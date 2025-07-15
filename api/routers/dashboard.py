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
from llm_gateway import enhanced_gateway

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


class IntelligentRoutingData(BaseModel):
    routing_recommendations: dict
    provider_performance: dict
    cost_optimization: dict
    performance_trends: dict


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
            func.count(UsageRecord.id).label("total_requests")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date
        )
    )
    stats = overall_stats.first()
    total_requests = stats.total_requests or 0
    total_tokens = stats.total_tokens or 0
    total_cost = float(stats.total_cost or 0)
    avg_response_time = float(stats.avg_response_time or 0)
    
    # Get successful requests count separately
    successful_stats = await db.execute(
        select(
            func.count(UsageRecord.id).label("successful_requests")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.created_at <= end_date,
            UsageRecord.success == True
        )
    )
    successful_requests = successful_stats.scalar() or 0
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0.0

    # Get top models
    try:
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
    except Exception:
        top_models = []

    # Get usage by day - simplified for SQLite compatibility
    try:
        usage_by_day_query = await db.execute(
            select(
                UsageRecord.created_at.label("date"),
                func.count(UsageRecord.id).label("requests"),
                func.sum(UsageRecord.total_tokens).label("tokens"),
                func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost")
            ).where(
                UsageRecord.organization_id == current_user.organization_id,
                UsageRecord.created_at >= start_date,
                UsageRecord.created_at <= end_date,
                UsageRecord.success == True
            ).group_by(
                UsageRecord.created_at
            ).order_by(
                UsageRecord.created_at
            )
        )
        usage_by_day = [
            {
                "date": row.date.strftime('%Y-%m-%d') if row.date else "2024-01-01",
                "requests": row.requests,
                "tokens": row.tokens or 0,
                "cost": float(row.cost or 0)
            }
            for row in usage_by_day_query
        ]
    except Exception as e:
        print(f"Error in usage_by_day query: {e}")
        usage_by_day = []

    # Get cost by provider
    try:
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
    except Exception:
        cost_by_provider = []

    return AnalyticsData(
        total_requests=total_requests,
        total_tokens=total_tokens,
        total_cost=total_cost,
        success_rate=success_rate,
        avg_response_time=avg_response_time,
        top_models=top_models,
        usage_by_day=usage_by_day,
        cost_by_provider=cost_by_provider
    )


@router.get("/intelligent-routing", response_model=IntelligentRoutingData)
async def get_intelligent_routing_data(
    current_user: User = Depends(get_current_user)
):
    """Get intelligent routing insights and recommendations"""
    
    # Get routing recommendations from the intelligent router
    routing_recommendations = enhanced_gateway.get_routing_recommendations()
    
    # Get provider performance data
    provider_performance = enhanced_gateway.get_performance_stats()
    
    # Calculate cost optimization insights
    cost_optimization = {
        "potential_savings": 0.0,
        "recommended_providers": [],
        "cost_trends": []
    }
    
    # Calculate potential savings by switching to cheaper providers
    if provider_performance:
        current_avg_cost = sum(
            perf.get("avg_cost", 0) * perf.get("total_requests", 0)
            for perf in provider_performance.values()
        )
        
        # Find cheapest providers
        cheapest_providers = sorted(
            provider_performance.items(),
            key=lambda x: x[1].get("avg_cost", float('inf'))
        )[:3]
        
        if cheapest_providers:
            cheapest_avg_cost = cheapest_providers[0][1].get("avg_cost", 0)
            potential_savings = max(0, current_avg_cost - cheapest_avg_cost)
            cost_optimization["potential_savings"] = potential_savings
            cost_optimization["recommended_providers"] = [
                {
                    "provider": name,
                    "avg_cost": perf.get("avg_cost", 0),
                    "success_rate": perf.get("success_rate", 0)
                }
                for name, perf in cheapest_providers
            ]
    
    # Calculate performance trends
    performance_trends = {
        "top_performers": [],
        "improving_providers": [],
        "declining_providers": []
    }
    
    if provider_performance:
        # Sort by success rate
        top_performers = sorted(
            provider_performance.items(),
            key=lambda x: x[1].get("success_rate", 0),
            reverse=True
        )[:5]
        
        performance_trends["top_performers"] = [
            {
                "provider": name,
                "success_rate": perf.get("success_rate", 0),
                "avg_response_time": perf.get("avg_response_time", 0),
                "avg_cost": perf.get("avg_cost", 0)
            }
            for name, perf in top_performers
        ]
    
    return IntelligentRoutingData(
        routing_recommendations=routing_recommendations,
        provider_performance=provider_performance,
        cost_optimization=cost_optimization,
        performance_trends=performance_trends
    )


@router.get("/provider-performance")
async def get_provider_performance(
    current_user: User = Depends(get_current_user)
):
    """Get detailed provider performance analysis"""
    
    performance_stats = enhanced_gateway.get_performance_stats()
    
    # Enhance with additional insights
    enhanced_stats = {}
    
    for provider_name, stats in performance_stats.items():
        enhanced_stats[provider_name] = {
            **stats,
            "efficiency_score": 0.0,
            "cost_efficiency": 0.0,
            "reliability_score": 0.0
        }
        
        # Calculate efficiency score (success rate * speed factor)
        success_rate = stats.get("success_rate", 0)
        avg_response_time = stats.get("avg_response_time", 5.0)
        speed_factor = max(0.1, 1.0 / (avg_response_time + 0.1))
        enhanced_stats[provider_name]["efficiency_score"] = success_rate * speed_factor
        
        # Calculate cost efficiency (success rate / cost)
        avg_cost = stats.get("avg_cost", 0.01)
        if avg_cost > 0:
            enhanced_stats[provider_name]["cost_efficiency"] = success_rate / avg_cost
        
        # Calculate reliability score
        total_requests = stats.get("total_requests", 0)
        if total_requests > 0:
            enhanced_stats[provider_name]["reliability_score"] = success_rate * min(1.0, total_requests / 100)
    
    return {
        "providers": enhanced_stats,
        "summary": {
            "total_providers": len(enhanced_stats),
            "best_performer": max(enhanced_stats.items(), key=lambda x: x[1]["efficiency_score"])[0] if enhanced_stats else None,
            "most_cost_efficient": max(enhanced_stats.items(), key=lambda x: x[1]["cost_efficiency"])[0] if enhanced_stats else None,
            "most_reliable": max(enhanced_stats.items(), key=lambda x: x[1]["reliability_score"])[0] if enhanced_stats else None
        }
    }


@router.get("/routing-insights")
async def get_routing_insights(
    current_user: User = Depends(get_current_user)
):
    """Get intelligent routing insights and recommendations"""
    
    # Get routing recommendations
    recommendations = enhanced_gateway.get_routing_recommendations()
    
    # Get provider health status
    health_status = recommendations.get("health_status", {})
    
    # Calculate routing insights
    insights = {
        "optimal_routing_strategy": "balanced",
        "recommended_providers": [],
        "health_alerts": [],
        "performance_insights": []
    }
    
    # Determine optimal routing strategy
    top_performers = recommendations.get("top_performers", [])
    cost_optimizers = recommendations.get("cost_optimizers", [])
    speed_optimizers = recommendations.get("speed_optimizers", [])
    
    if top_performers:
        insights["optimal_routing_strategy"] = "performance"
        insights["recommended_providers"] = top_performers[:3]
    elif cost_optimizers:
        insights["optimal_routing_strategy"] = "cost"
        insights["recommended_providers"] = cost_optimizers[:3]
    elif speed_optimizers:
        insights["optimal_routing_strategy"] = "speed"
        insights["recommended_providers"] = speed_optimizers[:3]
    
    # Check for health alerts
    for provider_name, health in health_status.items():
        if health.get("status") != "healthy":
            insights["health_alerts"].append({
                "provider": provider_name,
                "status": health.get("status"),
                "error": health.get("error", "Unknown error")
            })
    
    # Generate performance insights
    if top_performers:
        best_provider = top_performers[0]
        insights["performance_insights"].append({
            "type": "success",
            "message": f"{best_provider['provider']} is performing best with {best_provider.get('success_rate', 0):.1%} success rate"
        })
    
    if cost_optimizers:
        cheapest_provider = cost_optimizers[0]
        insights["performance_insights"].append({
            "type": "cost",
            "message": f"{cheapest_provider['provider']} offers best cost efficiency at ${cheapest_provider.get('avg_cost', 0):.4f} per request"
        })
    
    return insights


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
            "id": req.id,
            "request_id": req.request_id,
            "provider": req.provider,
            "model_id": req.model_id,
            "input_tokens": req.input_tokens,
            "output_tokens": req.output_tokens,
            "total_tokens": req.total_tokens,
            "cost_usd": float(req.cost_usd),
            "response_time_ms": req.response_time_ms,
            "success": req.success,
            "task_type": req.task_type,
            "complexity": req.complexity,
            "created_at": req.created_at.isoformat() if req.created_at else None
        }
        for req in requests
    ]


@router.get("/organization")
async def get_organization_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization information"""
    
    org = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = org.scalar_one_or_none()
    
    if not org:
        return {"error": "Organization not found"}
    
    return {
        "id": org.id,
        "name": org.name,
        "plan": org.plan,
        "created_at": org.created_at.isoformat() if org.created_at else None,
        "settings": org.settings
    }


@router.get("/team-members")
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team members for the organization"""
    
    members = await db.execute(
        select(User).where(User.organization_id == current_user.organization_id)
    )
    members = members.scalars().all()
    
    return [
        {
            "id": member.id,
            "email": member.email,
            "role": member.role,
            "created_at": member.created_at.isoformat() if member.created_at else None,
            "last_login": member.last_login.isoformat() if member.last_login else None
        }
        for member in members
    ]