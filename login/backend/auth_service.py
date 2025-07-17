"""
Enterprise Authentication Service
Handles all authentication logic with proper error handling and validation
"""
import hashlib
import secrets
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import logging

from database.database import get_db
from models.user import User, Organization, UserRole, PlanType
from auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)
from utils.auth.email_service import email_service

logger = logging.getLogger("auth_service")


class AuthResponse(BaseModel):
    """Standardized authentication response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600
    user: Optional[Dict[str, Any]] = None


class UserData(BaseModel):
    """User data model for responses"""
    id: str
    email: str
    full_name: str
    role: str
    organization_id: str
    organization_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AuthService:
    """Enterprise Authentication Service"""
    
    @staticmethod
    async def login_user(email: str, password: str, db: AsyncSession) -> AuthResponse:
        """
        Authenticate user with email and password
        Returns standardized response with user data and tokens
        """
        try:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Login failed: user not found for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            if not user.is_verified:
                logger.warning(f"Login failed: user not verified for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not verified. Please verify your email before logging in."
                )
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Login failed: incorrect password for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Update last login
            user.last_login_at = datetime.utcnow().isoformat()
            await db.commit()
            
            # Get organization info
            org_result = await db.execute(
                select(Organization).where(Organization.id == user.organization_id)
            )
            organization = org_result.scalar_one()
            
            # Generate tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            # Prepare user data
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "organization_id": str(user.organization_id),
                "organization_name": organization.name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at
            }
            
            logger.info(f"Login successful for user {email}")
            
            return AuthResponse(
                success=True,
                message="Login successful",
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_data
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error for {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed due to server error"
            )
    
    @staticmethod
    async def register_user(user_data: dict, db: AsyncSession) -> AuthResponse:
        """
        Register new user with organization
        Returns standardized response with user data and tokens
        """
        try:
            email = user_data.get('email')
            password = user_data.get('password')
            first_name = user_data.get('firstName', '')
            last_name = user_data.get('lastName', '')
            organization_name = user_data.get('organizationName', 'My Organization')
            
            # Validate required fields
            if not email or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email and password are required"
                )
            
            if not first_name or not last_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="First name and last name are required"
                )
            
            full_name = f"{first_name} {last_name}"
            
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create organization
            org_slug = organization_name.lower().replace(" ", "-").replace("_", "-")
            organization = Organization(
                name=organization_name,
                slug=org_slug,
                plan_type=PlanType.FREE
            )
            db.add(organization)
            await db.flush()  # Get the ID
            
            # Create user
            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                organization_id=organization.id,
                role=UserRole.OWNER,
                is_verified=True,  # Auto-verify for now
                last_login_at=datetime.utcnow().isoformat()
            )
            db.add(user)
            await db.commit()
            
            # Generate tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            # Prepare user data
            user_response = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "organization_id": str(user.organization_id),
                "organization_name": organization.name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at
            }
            
            logger.info(f"Registration successful for user {email}")
            
            return AuthResponse(
                success=True,
                message="Registration successful",
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_response
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error for {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed due to server error"
            )
    
    @staticmethod
    async def forgot_password(email: str, db: AsyncSession) -> AuthResponse:
        """
        Send password reset email
        Returns standardized response
        """
        try:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Forgot password: email not found {email}")
                # Always return success to prevent email enumeration
                return AuthResponse(
                    success=True,
                    message="If the email exists, a password reset link has been sent"
                )
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store token in user record
            user.reset_token = reset_token
            user.reset_token_expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            await db.commit()
            
            # Send password reset email
            email_sent = email_service.send_password_reset_email(user.email, reset_token)
            
            if email_sent:
                logger.info(f"Password reset email sent to {user.email}")
            else:
                logger.error(f"Failed to send password reset email to {user.email}")
            
            return AuthResponse(
                success=True,
                message="If the email exists, a password reset link has been sent"
            )
            
        except Exception as e:
            logger.error(f"Forgot password error for {email}: {e}")
            return AuthResponse(
                success=True,
                message="If the email exists, a password reset link has been sent"
            )
    
    @staticmethod
    async def reset_password(token: str, new_password: str, db: AsyncSession) -> AuthResponse:
        """
        Reset password with token
        Returns standardized response
        """
        try:
            # Find user by reset token
            result = await db.execute(
                select(User).where(User.reset_token == token)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            
            # Check if token is expired
            if user.reset_token_expires:
                expires_at = datetime.fromisoformat(user.reset_token_expires)
                if datetime.utcnow() > expires_at:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid or expired reset token"
                    )
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expires = None
            await db.commit()
            
            logger.info(f"Password reset successful for user {user.email}")
            
            return AuthResponse(
                success=True,
                message="Password reset successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed due to server error"
            )
    
    @staticmethod
    async def refresh_token(refresh_token: str, db: AsyncSession) -> AuthResponse:
        """
        Refresh access token using refresh token
        Returns standardized response with new tokens
        """
        try:
            # Verify refresh token
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Generate new tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return AuthResponse(
                success=True,
                message="Token refreshed successfully",
                access_token=access_token,
                refresh_token=new_refresh_token
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed due to server error"
            )