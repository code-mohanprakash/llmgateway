"""
RBAC API endpoints for enterprise role and permission management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from database.database import get_db
from models.user import User, Organization
from models.rbac import Role, Permission, UserRole, AuditLog, RolePermission
from auth.dependencies import get_current_user
from auth.rbac_middleware import require_permission, audit_action, rbac_middleware

router = APIRouter()


# Pydantic models for API requests/responses
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]
    parent_role_id: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    parent_role_id: Optional[str] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    permissions: List[str]
    is_system_role: bool
    parent_role_id: Optional[str]
    created_at: str
    updated_at: str


class UserRoleAssign(BaseModel):
    user_id: str
    role_id: str
    expires_at: Optional[str] = None


class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    resource_type: str
    action: str
    conditions: Optional[Dict[str, Any]]


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    success: bool
    error_message: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: str
    metadata: Optional[Dict[str, Any]]


# Role management endpoints
@router.post("/roles", response_model=RoleResponse)
@require_permission("role.create", "role")
@audit_action("role.create", "role")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new role"""
    organization = current_user.organization
    
    # Check if role name already exists in organization
    existing_role = await db.execute(
        select(Role).where(
            and_(
                Role.name == role_data.name,
                Role.organization_id == organization.id
            )
        )
    )
    
    if existing_role.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Role with this name already exists in the organization"
        )
    
    # Validate permissions
    valid_permissions = await _get_valid_permissions(db)
    invalid_permissions = [p for p in role_data.permissions if p not in valid_permissions]
    
    if invalid_permissions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid permissions: {invalid_permissions}"
        )
    
    # Create role
    role = Role(
        name=role_data.name,
        description=role_data.description,
        organization_id=organization.id,
        permissions=role_data.permissions,
        parent_role_id=role_data.parent_role_id
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        is_system_role=role.is_system_role,
        parent_role_id=role.parent_role_id,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.get("/roles", response_model=List[RoleResponse])
@require_permission("role.read", "role")
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all roles in the organization"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Role).where(Role.organization_id == organization.id)
    )
    
    roles = result.scalars().all()
    
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions,
            is_system_role=role.is_system_role,
            parent_role_id=role.parent_role_id,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        for role in roles
    ]


@router.get("/roles/{role_id}", response_model=RoleResponse)
@require_permission("role.read", "role")
async def get_role(
    role_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific role"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.organization_id == organization.id
            )
        )
    )
    
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        is_system_role=role.is_system_role,
        parent_role_id=role.parent_role_id,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.put("/roles/{role_id}", response_model=RoleResponse)
@require_permission("role.update", "role")
@audit_action("role.update", "role")
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a role"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.organization_id == organization.id
            )
        )
    )
    
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.is_system_role:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify system roles"
        )
    
    # Update fields
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permissions is not None:
        # Validate permissions
        valid_permissions = await _get_valid_permissions(db)
        invalid_permissions = [p for p in role_data.permissions if p not in valid_permissions]
        
        if invalid_permissions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid permissions: {invalid_permissions}"
            )
        
        role.permissions = role_data.permissions
    if role_data.parent_role_id is not None:
        role.parent_role_id = role_data.parent_role_id
    
    await db.commit()
    await db.refresh(role)
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        is_system_role=role.is_system_role,
        parent_role_id=role.parent_role_id,
        created_at=role.created_at,
        updated_at=role.updated_at
    )


@router.delete("/roles/{role_id}")
@require_permission("role.delete", "role")
@audit_action("role.delete", "role")
async def delete_role(
    role_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a role"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Role).where(
            and_(
                Role.id == role_id,
                Role.organization_id == organization.id
            )
        )
    )
    
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.is_system_role:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete system roles"
        )
    
    # Check if role is assigned to any users
    user_roles = await db.execute(
        select(UserRole).where(UserRole.role_id == role_id)
    )
    
    if user_roles.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete role that is assigned to users"
        )
    
    await db.delete(role)
    await db.commit()
    
    return {"message": "Role deleted successfully"}


# User role assignment endpoints
@router.post("/user-roles")
@require_permission("role.assign", "role")
@audit_action("role.assign", "user_role")
async def assign_role_to_user(
    assignment: UserRoleAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a role to a user"""
    organization = current_user.organization
    
    # Verify user exists in organization
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == assignment.user_id,
                User.organization_id == organization.id
            )
        )
    )
    
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify role exists in organization
    role_result = await db.execute(
        select(Role).where(
            and_(
                Role.id == assignment.role_id,
                Role.organization_id == organization.id
            )
        )
    )
    
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if assignment already exists
    existing_assignment = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == assignment.user_id,
                UserRole.role_id == assignment.role_id
            )
        )
    )
    
    if existing_assignment.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User already has this role"
        )
    
    # Parse expiration date
    expires_at = None
    if assignment.expires_at:
        try:
            expires_at = datetime.fromisoformat(assignment.expires_at.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid expiration date format"
            )
    
    # Create assignment
    user_role = UserRole(
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        assigned_by=current_user.id,
        expires_at=expires_at
    )
    
    db.add(user_role)
    await db.commit()
    
    return {"message": "Role assigned successfully"}


@router.delete("/user-roles/{user_id}/{role_id}")
@require_permission("role.assign", "role")
@audit_action("role.unassign", "user_role")
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a role from a user"""
    organization = current_user.organization
    
    # Verify user exists in organization
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id
            )
        )
    )
    
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find and delete assignment
    assignment_result = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        )
    )
    
    assignment = assignment_result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Role assignment not found"
        )
    
    await db.delete(assignment)
    await db.commit()
    
    return {"message": "Role removed successfully"}


# Permission management endpoints
@router.get("/permissions", response_model=List[PermissionResponse])
@require_permission("role.read", "permission")
async def list_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all available permissions"""
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    
    return [
        PermissionResponse(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            resource_type=permission.resource_type,
            action=permission.action,
            conditions=permission.conditions
        )
        for permission in permissions
    ]


# Audit log endpoints
@router.get("/audit-logs", response_model=List[AuditLogResponse])
@require_permission("audit_log.read", "audit_log")
async def list_audit_logs(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List audit logs with filtering"""
    organization = current_user.organization
    
    # Build query
    query = select(AuditLog).where(AuditLog.organization_id == organization.id)
    
    if action:
        query = query.where(AuditLog.action.contains(action))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if success is not None:
        query = query.where(AuditLog.success == success)
    
    # Order by created_at descending
    query = query.order_by(AuditLog.created_at.desc())
    
    # Add pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            success=log.success,
            error_message=log.error_message,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            created_at=log.created_at,
            metadata=log.metadata
        )
        for log in audit_logs
    ]


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
@require_permission("audit_log.read", "audit_log")
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific audit log entry"""
    organization = current_user.organization
    
    result = await db.execute(
        select(AuditLog).where(
            and_(
                AuditLog.id == log_id,
                AuditLog.organization_id == organization.id
            )
        )
    )
    
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        action=log.action,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        success=log.success,
        error_message=log.error_message,
        ip_address=str(log.ip_address) if log.ip_address else None,
        user_agent=log.user_agent,
        created_at=log.created_at,
        metadata=log.metadata
    )


# Utility functions
async def _get_valid_permissions(db: AsyncSession) -> List[str]:
    """Get all valid permission names"""
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    return [p.name for p in permissions]


# Initialize system permissions and roles
async def initialize_rbac_system(db: AsyncSession):
    """Initialize the RBAC system with default permissions and roles"""
    from models.rbac import SYSTEM_PERMISSIONS, SYSTEM_ROLES
    
    # Create permissions
    for perm_data in SYSTEM_PERMISSIONS:
        existing_perm = await db.execute(
            select(Permission).where(Permission.name == perm_data["name"])
        )
        
        if not existing_perm.scalar_one_or_none():
            permission = Permission(**perm_data)
            db.add(permission)
    
    await db.commit()
    
    # Create system roles (these will be created per organization when needed)
    # This is handled in the organization creation process 