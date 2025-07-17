"""
Authentication API routes
"""
import hashlib
import secrets
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from database.database import get_db
from models.user import User, Organization, APIKey, UserRole, PlanType
from auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)
from auth.dependencies import get_current_user, require_role
from auth.rbac_middleware import require_permission
from utils.auth.email_service import email_service

router = APIRouter()

logger = logging.getLogger("auth")


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    role: str
    organization_name: str
    avatar_url: Optional[str] = None
    timezone: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserProfile


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    # Backend format
    full_name: Optional[str] = None
    organization_name: Optional[str] = None
    # Frontend format
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    organizationName: Optional[str] = None
    
    def model_post_init(self, __context):
        # Convert frontend field names to backend format
        if self.firstName and self.lastName and not self.full_name:
            self.full_name = f"{self.firstName} {self.lastName}"
        if self.organizationName and not self.organization_name:
            self.organization_name = self.organizationName
            
        # Validate required fields
        if not self.full_name:
            raise ValueError("full_name or firstName+lastName is required")
        if not self.organization_name:
            self.organization_name = "My Organization"
        if not self.organization_name:
            raise ValueError("organization_name or organizationName is required")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class APIKeyCreate(BaseModel):
    name: str
    scopes: list[str] = []
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    api_key: Optional[str] = None  # Only returned on creation
    scopes: list[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[str]
    usage_count: int


# User Management Models
class UserInvite(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan_type: str
    user_count: int
    created_at: datetime


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and organization"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create organization
    org_slug = user_data.organization_name.lower().replace(" ", "-").replace("_", "-")
    organization = Organization(
        name=user_data.organization_name,
        slug=org_slug,
        plan_type=PlanType.FREE
    )
    db.add(organization)
    await db.flush()  # Get the ID
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        organization_id=organization.id,
        role=UserRole.OWNER,
        is_verified=True  # Auto-verify for now
    )
    db.add(user)
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login user"""
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == form_data.username, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Login failed: user not found or inactive for email {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_verified:
            logger.warning(f"Login failed: user not verified for email {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please verify your email before logging in.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: incorrect password for email {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        logger.info(f"Login successful for user {form_data.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login error for {form_data.username}: {e}")
        raise


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    
    try:
        # Verify refresh token
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
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
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
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


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "organization_id": str(current_user.organization_id),
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }


# User Management Endpoints
@router.get("/users", response_model=list[UserResponse])
async def list_organization_users(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """List all users in the organization"""
    
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        for user in users
    ]


@router.post("/users/invite", response_model=UserResponse)
async def invite_user(
    invite_data: UserInvite,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Invite a new user to the organization"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == invite_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user with temporary password
    temp_password = secrets.token_urlsafe(12)
    hashed_password = get_password_hash(temp_password)
    
    user = User(
        email=invite_data.email,
        full_name=invite_data.full_name,
        hashed_password=hashed_password,
        organization_id=current_user.organization_id,
        role=invite_data.role,
        is_verified=False,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    
    # TODO: Send invitation email with temp password
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Update user information"""
    
    # Get user to update
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent changing owner role
    if user.role == UserRole.OWNER and user_data.role and user_data.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner role"
        )
    
    # Update user fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db.commit()
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )


@router.delete("/users/{user_id}")
async def remove_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Remove user from organization"""
    
    # Get user to remove
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent removing owner
    if user.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove organization owner"
        )
    
    # Soft delete user
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "User removed successfully"}


@router.get("/organization", response_model=OrganizationResponse)
async def get_organization_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization information"""
    
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Count users in organization
    user_count_result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    user_count = len(user_count_result.scalars().all())
    
    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        slug=organization.slug,
        plan_type=organization.plan_type.value,
        user_count=user_count,
        created_at=organization.created_at
    )


@router.post("/api-keys", response_model=APIKeyResponse)
@require_permission("api_key.create", "api_key")
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key"""
    
    # Generate API key
    key_bytes = secrets.token_bytes(32)
    key_string = key_bytes.hex()
    full_key = f"llm_{key_string}"
    
    # Hash for storage
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    key_prefix = f"llm_...{key_string[-8:]}"
    
    # Create API key record
    api_key = APIKey(
        name=key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=key_data.scopes,
        rate_limit_per_minute=key_data.rate_limit_per_minute,
        rate_limit_per_hour=key_data.rate_limit_per_hour,
        rate_limit_per_day=key_data.rate_limit_per_day,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    
    db.add(api_key)
    await db.commit()
    
    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        api_key=full_key,  # Only returned on creation
        scopes=api_key.scopes,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        usage_count=api_key.usage_count
    )


@router.get("/api-keys", response_model=list[APIKeyResponse])
@require_permission("api_key.read", "api_key")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's API keys"""
    
    result = await db.execute(
        select(APIKey).where(
            APIKey.user_id == current_user.id,
            APIKey.is_deleted == False
        )
    )
    api_keys = result.scalars().all()
    
    return [
        APIKeyResponse(
            id=str(key.id),
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=key.scopes,
            is_active=key.is_active,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            usage_count=key.usage_count
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}")
@require_permission("api_key.delete", "api_key")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id,
            APIKey.is_deleted == False
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Soft delete
    api_key.is_deleted = True
    api_key.deleted_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "API key deleted successfully"}


# Enhanced Authentication Endpoints

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email"""
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Forgot password: email not found {request.email}")
            return {"message": "If the email exists, a password reset link has been sent"}
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
            return {"message": "If the email exists, a password reset link has been sent"}
        else:
            logger.error(f"Failed to send password reset email to {user.email}")
            return {"message": "If the email exists, a password reset link has been sent"}
    except Exception as e:
        logger.error(f"Forgot password error for {request.email}: {e}")
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    
    # Find user by reset token
    result = await db.execute(
        select(User).where(User.reset_token == request.token)
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
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password for authenticated user"""
    
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/send-verification-email")
async def send_verification_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send email verification"""
    
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return {"message": "If the email exists, a verification email has been sent"}
    
    if user.is_verified:
        return {"message": "Email is already verified"}
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Store token in user record
    user.verification_token = verification_token
    user.verification_token_expires = (datetime.utcnow() + timedelta(hours=24)).isoformat()
    await db.commit()
    
    # Send verification email
    email_sent = email_service.send_verification_email(user.email, verification_token)
    
    if email_sent:
        return {"message": "Verification email sent"}
    else:
        return {"message": "Verification email sent"}


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with token"""
    
    # Find user by verification token
    result = await db.execute(
        select(User).where(User.verification_token == token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Check if token is expired
    if user.verification_token_expires:
        expires_at = datetime.fromisoformat(user.verification_token_expires)
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
    
    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    await db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/test-email")
async def test_email(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test email configuration (admin feature)"""
    
    # Check if user has admin privileges
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can test email configuration"
        )
    
    email = request.get("email", current_user.email)
    test_type = request.get("test_type", "password_reset")
    
    # Generate test token
    test_token = secrets.token_urlsafe(32)
    
    try:
        if test_type == "password_reset":
            success = email_service.send_password_reset_email(email, test_token)
        elif test_type == "verification":
            success = email_service.send_verification_email(email, test_token)
        elif test_type == "notification":
            # Send a generic test notification email
            success = email_service.send_email(
                email,
                "Test Notification - Model Bridge",
                f"""
                <html>
                <body>
                    <h2>Test Email Notification</h2>
                    <p>This is a test email to verify your email configuration is working properly.</p>
                    <p><strong>Test Token:</strong> {test_token}</p>
                    <p>If you received this email, your email service is configured correctly.</p>
                    <hr>
                    <p><em>Model Bridge Email Testing System</em></p>
                </body>
                </html>
                """
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid test type. Must be 'password_reset', 'verification', or 'notification'"
            )
        
        if success:
            return {"message": f"Test {test_type} email sent successfully to {email}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email. Please check your email configuration."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email test failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should clear tokens)"""
    
    # In a real implementation, you might want to blacklist the token
    # For now, just return success - client will clear tokens
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile"""
    
    # Get organization info
    org_result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = org_result.scalar_one()
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role=current_user.role.value,
        organization_name=organization.name,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        created_at=current_user.created_at,
        last_login_at=datetime.fromisoformat(current_user.last_login_at) if current_user.last_login_at else None
    )


@router.put("/profile")
async def update_profile(
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    
    # Update allowed fields
    allowed_fields = ['full_name', 'avatar_url', 'timezone']
    
    for field, value in updates.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    await db.commit()
    
    return {"message": "Profile updated successfully"}


@router.get("/health/email")
async def email_health():
    """Health check for email service"""
    try:
        # Try to send a test email to the configured FROM_EMAIL (in dev mode, just logs)
        test_result = email_service.send_email(
            to_email=email_service.from_email or "test@example.com",
            subject="Model Bridge Email Health Check",
            html_content="<p>This is a test email for health check.</p>"
        )
        if test_result:
            return {"status": "ok"}
        else:
            return {"status": "error", "detail": "Failed to send test email. Check SMTP config."}
    except Exception as e:
        logger.error(f"Email health check failed: {e}")
        return {"status": "error", "detail": str(e)}