"""
Dashboard API routes for analytics and management
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract

from database.database import get_db
from models.user import User, Organization, UsageRecord, APIKey
from auth.dependencies import get_current_user

router = APIRouter()


class AnalyticsData(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost: float
    success_rate: float
    avg_response_time: float
    top_models: List[dict]
    usage_by_day: List[dict]
    cost_by_provider: List[dict]


class ModelUsage(BaseModel):
    model_id: str
    provider: str
    request_count: int
    token_count: int
    cost: float
    avg_response_time: float


@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics data for the dashboard"""
    
    # Date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get overall stats
    overall_stats = await db.execute(
        select(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("total_cost"),
            func.avg(UsageRecord.response_time_ms).label("avg_response_time"),
            func.sum(func.case((UsageRecord.success == True, 1), else_=0)).label("successful_requests")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date
        )
    )
    
    stats = overall_stats.first()
    total_requests = stats.total_requests or 0
    success_rate = (stats.successful_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Get top models
    top_models_query = await db.execute(
        select(
            UsageRecord.model_id,
            UsageRecord.provider,
            func.count(UsageRecord.id).label("request_count"),
            func.sum(UsageRecord.total_tokens).label("token_count"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date,
            UsageRecord.success == True
        ).group_by(
            UsageRecord.model_id, UsageRecord.provider
        ).order_by(
            desc("request_count")
        ).limit(10)
    )
    
    top_models = [
        {
            "model_id": row.model_id,
            "provider": row.provider,
            "request_count": row.request_count,
            "token_count": row.token_count,
            "cost": float(row.cost)
        }
        for row in top_models_query
    ]
    
    # Get usage by day
    usage_by_day_query = await db.execute(
        select(
            func.date(UsageRecord.created_at).label("date"),
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.total_tokens).label("tokens"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date,
            UsageRecord.success == True
        ).group_by(
            func.date(UsageRecord.created_at)
        ).order_by(
            "date"
        )
    )
    
    usage_by_day = [
        {
            "date": row.date.isoformat(),
            "requests": row.requests,
            "tokens": row.tokens,
            "cost": float(row.cost)
        }
        for row in usage_by_day_query
    ]
    
    # Get cost by provider
    cost_by_provider_query = await db.execute(
        select(
            UsageRecord.provider,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date,
            UsageRecord.success == True
        ).group_by(
            UsageRecord.provider
        ).order_by(
            desc("cost")
        )
    )
    
    cost_by_provider = [
        {
            "provider": row.provider,
            "requests": row.requests,
            "cost": float(row.cost)
        }
        for row in cost_by_provider_query
    ]
    
    return AnalyticsData(
        total_requests=total_requests,
        total_tokens=stats.total_tokens or 0,
        total_cost=float(stats.total_cost or 0),
        success_rate=success_rate,
        avg_response_time=float(stats.avg_response_time or 0),
        top_models=top_models,
        usage_by_day=usage_by_day,
        cost_by_provider=cost_by_provider
    )


@router.get("/recent-requests")
async def get_recent_requests(
    limit: int = Query(default=50, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent API requests"""
    
    result = await db.execute(
        select(UsageRecord).where(
            UsageRecord.organization_id == current_user.organization_id
        ).order_by(
            desc(UsageRecord.created_at)
        ).limit(limit)
    )
    
    requests = result.scalars().all()
    
    return [
        {
            "id": str(record.id),
            "request_id": record.request_id,
            "provider": record.provider,
            "model_id": record.model_id,
            "tokens": record.total_tokens,
            "cost": float(record.cost_usd + record.markup_usd),
            "response_time_ms": record.response_time_ms,
            "success": record.success,
            "error_message": record.error_message,
            "created_at": record.created_at.isoformat()
        }
        for record in requests
    ]


@router.get("/organization")
async def get_organization_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization information"""
    
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one()
    
    # Get member count
    members_result = await db.execute(
        select(func.count(User.id)).where(
            User.organization_id == organization.id,
            User.is_deleted == False
        )
    )
    member_count = members_result.scalar()
    
    # Get API key count
    api_keys_result = await db.execute(
        select(func.count(APIKey.id)).where(
            APIKey.organization_id == organization.id,
            APIKey.is_deleted == False
        )
    )
    api_key_count = api_keys_result.scalar()
    
    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "plan_type": organization.plan_type.value,
        "monthly_request_limit": organization.monthly_request_limit,
        "monthly_token_limit": organization.monthly_token_limit,
        "features": organization.features,
        "member_count": member_count,
        "api_key_count": api_key_count,
        "created_at": organization.created_at.isoformat()
    }


@router.get("/team-members")
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team members"""
    
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.is_deleted == False
        ).order_by(User.created_at)
    )
    
    members = result.scalars().all()
    
    return [
        {
            "id": str(member.id),
            "email": member.email,
            "full_name": member.full_name,
            "role": member.role.value,
            "is_active": member.is_active,
            "created_at": member.created_at.isoformat(),
            "last_login": member.updated_at.isoformat()
        }
        for member in members
    ]