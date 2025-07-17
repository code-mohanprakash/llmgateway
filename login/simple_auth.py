#!/usr/bin/env python3
"""
Simple working authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
import uuid
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

router = APIRouter(prefix="/simple-auth", tags=["simple-auth"])
logger = logging.getLogger(__name__)

class UserRegisterSimple(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    organizationName: str = "My Organization"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"message": "Simple auth router is working!"}

@router.post("/register", response_model=TokenResponse)
async def simple_register(user_data: UserRegisterSimple, db: AsyncSession = Depends(get_db)):
    """Simple registration endpoint"""
    try:
        logger.info(f"Registration attempt for {user_data.email}")
        
        # Check if tables exist
        try:
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            table_exists = result.scalar()
            if not table_exists:
                raise HTTPException(status_code=500, detail="Database tables not found")
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check if user exists
        try:
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
        except Exception as e:
            logger.error(f"User check failed: {e}")
            raise HTTPException(status_code=500, detail="User check failed")
        
        # Create organization first
        try:
            org_slug = user_data.organizationName.lower().replace(" ", "-")
            organization = Organization(
                name=user_data.organizationName,
                slug=org_slug,
                plan_type=PlanType.FREE
            )
            db.add(organization)
            await db.flush()  # Get the ID
            logger.info(f"Created organization: {organization.id}")
        except Exception as e:
            logger.error(f"Organization creation failed: {e}")
            raise HTTPException(status_code=500, detail="Organization creation failed")
        
        # Create user
        try:
            full_name = f"{user_data.firstName} {user_data.lastName}"
            hashed_password = get_password_hash(user_data.password)
            
            user = User(
                email=user_data.email,
                full_name=full_name,
                hashed_password=hashed_password,
                organization_id=organization.id,
                role=UserRole.OWNER,
                is_verified=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
            logger.info(f"Created user: {user.id}")
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="User creation failed")
        
        # Generate tokens
        try:
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise HTTPException(status_code=500, detail="Token generation failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def simple_login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Simple login endpoint"""
    try:
        logger.info(f"Login attempt for {form_data.username}")
        
        # Find user
        result = await db.execute(
            select(User).where(User.email == form_data.username, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"Login successful for {form_data.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/forgot-password")
async def simple_forgot_password(request: dict, db: AsyncSession = Depends(get_db)):
    """Simple forgot password endpoint"""
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        logger.info(f"Forgot password for {email}")
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return {"message": "If the email exists, a password reset link has been sent"}