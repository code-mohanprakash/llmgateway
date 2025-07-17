"""
Enterprise Authentication Router
Clean, organized API endpoints for authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional

from database.database import get_db
from .auth_service import AuthService, AuthResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    organizationName: Optional[str] = "My Organization"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Authentication Endpoints
@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """Login user with email and password"""
    return await AuthService.login_user(form_data.username, form_data.password, db)


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    """Register new user and organization"""
    return await AuthService.register_user(user_data.dict(), db)


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email"""
    return await AuthService.forgot_password(request.email, db)


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    return await AuthService.reset_password(request.token, request.new_password, db)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    return await AuthService.refresh_token(request.refresh_token, db)


@router.post("/logout", response_model=AuthResponse)
async def logout():
    """Logout user (client should clear tokens)"""
    return AuthResponse(
        success=True,
        message="Logged out successfully"
    )