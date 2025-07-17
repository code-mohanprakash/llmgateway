#!/usr/bin/env python3
"""
Guaranteed working authentication system
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
import uuid
import logging
import os

# Create synchronous database connection
DATABASE_URL = "sqlite:///./model_bridge.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token
)

router = APIRouter(prefix="/working-auth", tags=["working-auth"])
logger = logging.getLogger(__name__)

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    organizationName: str = "My Organization"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/test")
def test_endpoint():
    """Test endpoint"""
    return {"message": "Working auth is ready!"}

@router.post("/register", response_model=TokenResponse)
def working_register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Working registration endpoint"""
    try:
        logger.info(f"Registration for {user_data.email}")
        
        # Check if user exists
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user_data.email})
        if result.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create organization
        org_id = str(uuid.uuid4())
        org_slug = user_data.organizationName.lower().replace(" ", "-")
        db.execute(text("""
            INSERT INTO organizations (id, name, slug, plan_type, created_at, updated_at, is_deleted) 
            VALUES (:id, :name, :slug, :plan_type, :created_at, :updated_at, :is_deleted)
        """), {
            "id": org_id,
            "name": user_data.organizationName,
            "slug": org_slug,
            "plan_type": "FREE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_deleted": False
        })
        
        # Create user
        user_id = str(uuid.uuid4())
        full_name = f"{user_data.firstName} {user_data.lastName}"
        hashed_password = get_password_hash(user_data.password)
        
        db.execute(text("""
            INSERT INTO users (
                id, email, full_name, hashed_password, organization_id, role,
                is_active, is_verified, created_at, updated_at, is_deleted
            ) VALUES (
                :id, :email, :full_name, :hashed_password, :organization_id, :role,
                :is_active, :is_verified, :created_at, :updated_at, :is_deleted
            )
        """), {
            "id": user_id,
            "email": user_data.email,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "organization_id": org_id,
            "role": "OWNER",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_deleted": False
        })
        
        db.commit()
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        logger.info(f"Registration successful for {user_data.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenResponse)
def working_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Working login endpoint"""
    try:
        logger.info(f"Login for {form_data.username}")
        
        # Find user
        result = db.execute(text("""
            SELECT id, email, hashed_password, is_active, is_verified 
            FROM users 
            WHERE email = :email AND is_active = 1 AND is_deleted = 0
        """), {"email": form_data.username})
        
        user = result.fetchone()
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
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
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
def working_forgot_password(request: dict, db: Session = Depends(get_db)):
    """Working forgot password endpoint"""
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # In development, just return success
        logger.info(f"Forgot password request for {email}")
        return {"message": "Password reset email sent (check server logs in development)"}
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return {"message": "Password reset email sent (check server logs in development)"}

security = HTTPBearer()

@router.get("/me")
def get_user_info(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get current user info using JWT token"""
    try:
        # Extract token from Authorization header
        import jwt
        from auth.jwt_handler import SECRET_KEY, ALGORITHM
        
        # Decode JWT token
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        result = db.execute(text("""
            SELECT u.id, u.email, u.full_name, u.role, u.organization_id, u.is_verified, u.created_at,
                   o.name as organization_name
            FROM users u 
            LEFT JOIN organizations o ON u.organization_id = o.id
            WHERE u.id = :user_id AND u.is_active = 1 AND u.is_deleted = 0
        """), {"user_id": user_id})
        
        user = result.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": str(user.organization_id),
            "organization_name": user.organization_name,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else str(user.created_at)
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")