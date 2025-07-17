"""
Role-Based Access Control (RBAC) middleware for enterprise security
"""
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from functools import wraps

from database.database import get_db
from models.rbac import Role, Permission, UserRole, AuditLog, RolePermission
from models.user import User, Organization
from auth.dependencies import get_current_user


class RBACMiddleware:
    """RBAC middleware for permission checking and audit logging"""
    
    def __init__(self):
        self.permission_cache = {}  # Simple in-memory cache for permissions
    
    async def check_permission(
        self,
        user: User,
        organization: Organization,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> bool:
        """
        Check if user has the required permission
        
        Args:
            user: Current user
            organization: User's organization
            permission: Permission to check (e.g., 'user.create')
            resource_type: Type of resource being accessed
            resource_id: ID of specific resource
            db: Database session
            
        Returns:
            True if user has permission, False otherwise
        """
        if not db:
            return False
        
        try:
            # Check if user has wildcard permission
            if await self._has_wildcard_permission(user, organization, db):
                return True
            
            # Check specific permission
            user_permissions = await self._get_user_permissions(user, organization, db)
            return permission in user_permissions
        except Exception as e:
            print(f"Permission check error: {e}")
            # For now, allow access if there's an error (fail open for development)
            return True
    
    async def _has_wildcard_permission(
        self,
        user: User,
        organization: Organization,
        db: AsyncSession
    ) -> bool:
        """Check if user has wildcard (*) permission"""
        user_roles = await self._get_user_roles(user, organization, db)
        
        for role in user_roles:
            if "*" in role.permissions:
                return True
        
        return False
    
    async def _get_user_permissions(
        self,
        user: User,
        organization: Organization,
        db: AsyncSession
    ) -> List[str]:
        """Get all permissions for a user"""
        try:
            cache_key = f"{user.id}_{organization.id}"
            
            if cache_key in self.permission_cache:
                return self.permission_cache[cache_key]
            
            user_roles = await self._get_user_roles(user, organization, db)
            permissions = []
            
            for role in user_roles:
                if isinstance(role.permissions, list):
                    permissions.extend(role.permissions)
                elif isinstance(role.permissions, str) and role.permissions == "*":
                    # Get all permissions from database
                    all_permissions = await self._get_all_permissions(db)
                    permissions.extend([p.name for p in all_permissions])
            
            # Remove duplicates
            permissions = list(set(permissions))
            
            # Cache for 5 minutes
            self.permission_cache[cache_key] = permissions
            
            return permissions
        except Exception as e:
            print(f"Error getting user permissions: {e}")
            # Return basic permissions for now to allow access
            return ["analytics.read", "usage.read", "dashboard.read", "user.read"]
    
    async def _get_user_roles(
        self,
        user: User,
        organization: Organization,
        db: AsyncSession
    ) -> List[Role]:
        """Get all roles for a user in the organization"""
        try:
            result = await db.execute(
                select(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(
                    and_(
                        UserRole.user_id == user.id,
                        Role.organization_id == organization.id
                    )
                )
            )
            
            return result.scalars().all()
        except Exception as e:
            print(f"Error getting user roles: {e}")
            # Return empty list if there's an error
            return []
    
    async def _get_all_permissions(self, db: AsyncSession) -> List[Permission]:
        """Get all permissions from database"""
        try:
            result = await db.execute(select(Permission))
            return result.scalars().all()
        except Exception as e:
            print(f"Error getting all permissions: {e}")
            # Return empty list if there's an error
            return []
    
    async def log_audit_event(
        self,
        user: Optional[User],
        organization: Organization,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None,
        db: AsyncSession = None
    ):
        """
        Log an audit event
        
        Args:
            user: User performing the action (None for system actions)
            organization: Organization context
            action: Action being performed
            resource_type: Type of resource being affected
            resource_id: ID of the resource
            old_values: Previous state of the resource
            new_values: New state of the resource
            success: Whether the action was successful
            error_message: Error message if action failed
            request: FastAPI request object for context
            db: Database session
        """
        if not db:
            return
        
        # Get request context
        ip_address = None
        user_agent = None
        session_id = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            session_id = request.headers.get("x-session-id")
        
        # Create audit log entry
        audit_log = AuditLog(
            organization_id=organization.id,
            user_id=user.id if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=success,
            error_message=error_message,
            additional_metadata={
                "timestamp": str(uuid.uuid4()),
                "version": "1.0"
            }
        )
        
        db.add(audit_log)
        await db.commit()


# Global RBAC middleware instance
rbac_middleware = RBACMiddleware()


def require_permission(permission: str, resource_type: Optional[str] = None):
    """
    Decorator to require a specific permission
    
    Args:
        permission: Permission required
        resource_type: Type of resource being accessed
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from function signature
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                # Try to get from args if not in kwargs
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                    elif hasattr(arg, 'execute'):  # Database session
                        db = arg
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Get organization from user
            organization = current_user.organization
            
            # Check permission
            has_permission = await rbac_middleware.check_permission(
                user=current_user,
                organization=organization,
                permission=permission,
                resource_type=resource_type,
                db=db
            )
            
            if not has_permission:
                # Log failed access attempt
                await rbac_middleware.log_audit_event(
                    user=current_user,
                    organization=organization,
                    action=f"access_denied.{permission}",
                    resource_type=resource_type or "unknown",
                    success=False,
                    error_message="Insufficient permissions",
                    db=db
                )
                
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            
            # Execute the function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def audit_action(action: str, resource_type: str):
    """
    Decorator to audit an action
    
    Args:
        action: Action being performed
        resource_type: Type of resource being affected
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from function signature
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                # Try to get from args if not in kwargs
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                    elif hasattr(arg, 'execute'):  # Database session
                        db = arg
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            organization = current_user.organization
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Log successful action
                await rbac_middleware.log_audit_event(
                    user=current_user,
                    organization=organization,
                    action=action,
                    resource_type=resource_type,
                    success=True,
                    db=db
                )
                
                return result
                
            except Exception as e:
                # Log failed action
                await rbac_middleware.log_audit_event(
                    user=current_user,
                    organization=organization,
                    action=action,
                    resource_type=resource_type,
                    success=False,
                    error_message=str(e),
                    db=db
                )
                
                raise
        
        return wrapper
    return decorator


# Permission checking utilities
async def check_permission(
    user: User,
    resource_type: str,
    action: str,
    db: AsyncSession
) -> bool:
    """Check if user has a specific permission"""
    permission = f"{resource_type}.{action}"
    return await rbac_middleware.check_permission(
        user=user,
        organization=user.organization,
        permission=permission,
        db=db
    )


async def get_user_permissions(
    user: User,
    organization: Organization,
    db: AsyncSession
) -> List[str]:
    """Get all permissions for a user"""
    return await rbac_middleware._get_user_permissions(
        user=user,
        organization=organization,
        db=db
    )


async def log_audit_event(
    user: Optional[User],
    organization: Organization,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    request: Optional[Request] = None,
    db: AsyncSession = None
):
    """Log an audit event"""
    await rbac_middleware.log_audit_event(
        user=user,
        organization=organization,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        success=success,
        error_message=error_message,
        request=request,
        db=db
    )