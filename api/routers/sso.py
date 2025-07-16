"""
SSO (Single Sign-On) API endpoints for enterprise authentication
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database.database import get_db
from models.user import User
from auth.sso import authenticate_sso, setup_mfa, verify_mfa, get_current_user_sso
from auth.rbac_middleware import log_audit_event, check_permission

router = APIRouter(prefix="/sso", tags=["SSO"])


class SSOLoginRequest(BaseModel):
    provider_type: str  # "saml", "oauth", "ad"
    credentials: Dict[str, Any]


class MFASetupRequest(BaseModel):
    user_id: str


class MFAVerifyRequest(BaseModel):
    user_id: str
    code: str


class SSOConfigRequest(BaseModel):
    provider_type: str
    config: Dict[str, Any]


@router.post("/login")
async def sso_login(
    request: SSOLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with SSO provider"""
    try:
        result = await authenticate_sso(
            provider_type=request.provider_type,
            credentials=request.credentials,
            db=db
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/setup-mfa")
async def setup_user_mfa(
    request: MFASetupRequest,
    current_user: User = Depends(get_current_user_sso),
    db: AsyncSession = Depends(get_db)
):
    """Setup MFA for user"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="mfa",
            action="setup",
            db=db
        )
        
        mfa_data = await setup_mfa(request.user_id, db)
        
        # Log audit event
        await log_audit_event(
            user=current_user,
            organization=current_user.organization,
            action="mfa.setup",
            resource_type="user",
            resource_id=request.user_id,
            success=True,
            db=db
        )
        
        return {
            "success": True,
            "data": mfa_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-mfa")
async def verify_user_mfa(
    request: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify MFA code"""
    try:
        is_valid = await verify_mfa(request.user_id, request.code, db)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid MFA code")
        
        return {
            "success": True,
            "message": "MFA verification successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/providers")
async def get_sso_providers(
    current_user: User = Depends(get_current_user_sso),
    db: AsyncSession = Depends(get_db)
):
    """Get available SSO providers"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="sso",
            action="read",
            db=db
        )
        
        providers = [
            {
                "type": "saml",
                "name": "SAML 2.0",
                "description": "Enterprise SAML authentication",
                "configurable": True
            },
            {
                "type": "oauth",
                "name": "OAuth 2.0 / OpenID Connect",
                "description": "OAuth 2.0 and OpenID Connect authentication",
                "configurable": True
            },
            {
                "type": "ad",
                "name": "Active Directory",
                "description": "Microsoft Active Directory integration",
                "configurable": True
            }
        ]
        
        return {
            "success": True,
            "data": providers
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config")
async def configure_sso_provider(
    request: SSOConfigRequest,
    current_user: User = Depends(get_current_user_sso),
    db: AsyncSession = Depends(get_db)
):
    """Configure SSO provider"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="sso",
            action="configure",
            db=db
        )
        
        # Store SSO configuration
        # In production, store in secure configuration management
        
        # Log audit event
        await log_audit_event(
            user=current_user,
            organization=current_user.organization,
            action="sso.configure",
            resource_type="sso_provider",
            resource_id=request.provider_type,
            new_values={"config": request.config},
            success=True,
            db=db
        )
        
        return {
            "success": True,
            "message": f"SSO provider {request.provider_type} configured successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_sso_status(
    current_user: User = Depends(get_current_user_sso),
    db: AsyncSession = Depends(get_db)
):
    """Get SSO status for organization"""
    try:
        # Check permission
        await check_permission(
            user=current_user,
            resource_type="sso",
            action="read",
            db=db
        )
        
        # Get SSO status from configuration
        # In production, retrieve from configuration management
        
        status = {
            "enabled": True,
            "providers": ["saml", "oauth"],
            "mfa_required": True,
            "session_timeout": 28800,  # 8 hours in seconds
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def sso_logout(
    current_user: User = Depends(get_current_user_sso),
    db: AsyncSession = Depends(get_db)
):
    """Logout from SSO session"""
    try:
        # Log audit event
        await log_audit_event(
            user=current_user,
            organization=current_user.organization,
            action="sso.logout",
            resource_type="user",
            resource_id=current_user.id,
            success=True,
            db=db
        )
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 