"""
Admin API routes for system management
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from database.database import get_db
from models.user import User, Organization, UsageRecord, APIKey
from auth.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics (organization owners only)"""
    
    # Get organization stats
    org_result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = org_result.scalar_one()
    
    # Get usage stats for this organization
    usage_stats = await db.execute(
        select(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.sum(UsageRecord.cost_usd).label("total_cost"),
            func.avg(UsageRecord.response_time_ms).label("avg_response_time")
        ).where(
            UsageRecord.organization_id == organization.id
        )
    )
    
    stats = usage_stats.first()
    
    return {
        "organization": {
            "name": organization.name,
            "plan": organization.plan_type.value,
            "created_at": organization.created_at.isoformat()
        },
        "usage": {
            "total_requests": stats.total_requests or 0,
            "total_tokens": stats.total_tokens or 0,
            "total_cost": float(stats.total_cost or 0),
            "avg_response_time": float(stats.avg_response_time or 0)
        }
    }


@router.get("/users")
async def list_organization_users(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """List users in organization (admin and above)"""
    
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db)
):
    """Update user role (owner only)"""
    
    # Validate role
    valid_roles = ["viewer", "member", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Get user
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    
    # Update role
    from models.user import UserRole
    user.role = UserRole(new_role)
    await db.commit()
    
    return {"message": "User role updated successfully"}


@router.delete("/users/{user_id}")
async def remove_user(
    user_id: str,
    current_user: User = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db)
):
    """Remove user from organization (owner only)"""
    
    # Get user
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    
    # Soft delete user
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    
    # Deactivate their API keys
    await db.execute(
        update(APIKey).where(
            APIKey.user_id == user.id
        ).values(is_active=False)
    )
    
    await db.commit()
    
    return {"message": "User removed successfully"}