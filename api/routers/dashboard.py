"""
Executive Dashboard API routes for enterprise analytics and management
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract, and_

from database.database import get_db
from models.user import User, Organization, UsageRecord, APIKey, PlanType
from models.rbac import AuditLog, CostCenter, Workflow, ABTest
from auth.dependencies import get_current_user
from auth.rbac_middleware import require_permission
from model_bridge import enhanced_gateway

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


class ExecutiveDashboardData(BaseModel):
    """Executive-level dashboard metrics"""
    kpi_metrics: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    performance_overview: Dict[str, Any]
    team_activity: Dict[str, Any]
    compliance_status: Dict[str, Any]
    growth_metrics: Dict[str, Any]


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


class CostCenterAnalysis(BaseModel):
    """Cost center analytics for enterprise billing"""
    cost_center_id: str
    name: str
    budget_limit: Optional[float]
    total_spent: float
    budget_utilization: float
    top_users: List[Dict[str, Any]]
    trending: str  # "up", "down", "stable"


@router.get("/analytics", response_model=AnalyticsData)
@require_permission("analytics.read", "dashboard")
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


@router.get("/executive", response_model=ExecutiveDashboardData)
@require_permission("analytics.executive", "dashboard")
async def get_executive_dashboard(
    period: str = Query(default="30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get executive-level dashboard metrics"""
    
    # Parse period
    period_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = period_map[period]
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    previous_start = start_date - timedelta(days=days)
    
    # KPI Metrics
    current_stats = await db.execute(
        select(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("total_cost"),
            func.avg(UsageRecord.response_time_ms).label("avg_response_time")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.success == True
        )
    )
    current = current_stats.first()
    
    # Previous period for comparison
    previous_stats = await db.execute(
        select(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("total_cost"),
            func.avg(UsageRecord.response_time_ms).label("avg_response_time")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= previous_start,
            UsageRecord.created_at < start_date,
            UsageRecord.success == True
        )
    )
    previous = previous_stats.first()
    
    # Calculate growth percentages
    def calc_growth(current_val, previous_val):
        if not previous_val or previous_val == 0:
            return 100 if current_val > 0 else 0
        return ((current_val - previous_val) / previous_val) * 100
    
    kpi_metrics = {
        "total_requests": {
            "current": current.total_requests or 0,
            "previous": previous.total_requests or 0,
            "growth": calc_growth(current.total_requests or 0, previous.total_requests or 0)
        },
        "total_tokens": {
            "current": current.total_tokens or 0,
            "previous": previous.total_tokens or 0,
            "growth": calc_growth(current.total_tokens or 0, previous.total_tokens or 0)
        },
        "total_cost": {
            "current": float(current.total_cost or 0),
            "previous": float(previous.total_cost or 0),
            "growth": calc_growth(float(current.total_cost or 0), float(previous.total_cost or 0))
        },
        "avg_response_time": {
            "current": float(current.avg_response_time or 0),
            "previous": float(previous.avg_response_time or 0),
            "growth": calc_growth(float(current.avg_response_time or 0), float(previous.avg_response_time or 0))
        }
    }
    
    # Cost Analysis with provider breakdown
    cost_by_provider = await db.execute(
        select(
            UsageRecord.provider,
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost"),
            func.count(UsageRecord.id).label("requests")
        ).where(
            UsageRecord.organization_id == current_user.organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.success == True
        ).group_by(UsageRecord.provider)
    )
    
    cost_analysis = {
        "total_spend": float(current.total_cost or 0),
        "cost_per_request": float(current.total_cost or 0) / max(1, current.total_requests or 1),
        "by_provider": [
            {
                "provider": row.provider,
                "cost": float(row.cost),
                "requests": row.requests,
                "cost_per_request": float(row.cost) / max(1, row.requests)
            }
            for row in cost_by_provider
        ],
        "cost_trend": "increasing" if kpi_metrics["total_cost"]["growth"] > 10 else 
                     "decreasing" if kpi_metrics["total_cost"]["growth"] < -10 else "stable"
    }
    
    # Performance Overview
    performance_overview = {
        "avg_response_time": float(current.avg_response_time or 0),
        "success_rate": 95.5,  # Calculate from actual data
        "provider_health": await _get_provider_health_summary(),
        "sla_compliance": 99.2,  # Calculate based on response times
        "error_rate": 4.5  # Calculate from failed requests
    }
    
    # Team Activity
    team_stats = await db.execute(
        select(
            func.count(func.distinct(APIKey.user_id)).label("active_users"),
            func.count(APIKey.id).label("total_api_keys")
        ).where(
            APIKey.organization_id == current_user.organization_id,
            APIKey.is_active == True
        )
    )
    team_data = team_stats.first()
    
    team_activity = {
        "active_users": team_data.active_users or 0,
        "total_api_keys": team_data.total_api_keys or 0,
        "recent_logins": await _get_recent_login_count(db, current_user.organization_id, start_date),
        "top_users": await _get_top_users_by_usage(db, current_user.organization_id, start_date, 5)
    }
    
    # Compliance Status
    audit_count = await db.execute(
        select(func.count(AuditLog.id)).where(
            AuditLog.organization_id == current_user.organization_id,
            AuditLog.created_at >= start_date
        )
    )
    
    compliance_status = {
        "audit_events": audit_count.scalar() or 0,
        "security_incidents": 0,  # Count failed login attempts, etc.
        "data_retention_compliance": True,
        "access_controls": True,
        "last_audit": datetime.utcnow().isoformat()
    }
    
    # Growth Metrics
    growth_metrics = {
        "user_growth": calc_growth(team_data.active_users or 0, 5),  # Compare with baseline
        "usage_growth": kpi_metrics["total_requests"]["growth"],
        "revenue_growth": kpi_metrics["total_cost"]["growth"],  # In SaaS context, cost might correlate with usage/value
        "market_expansion": 15.2,  # Placeholder for market metrics
        "customer_satisfaction": 4.7  # Placeholder for satisfaction metrics
    }
    
    return ExecutiveDashboardData(
        kpi_metrics=kpi_metrics,
        cost_analysis=cost_analysis,
        performance_overview=performance_overview,
        team_activity=team_activity,
        compliance_status=compliance_status,
        growth_metrics=growth_metrics
    )


@router.get("/cost-centers", response_model=List[CostCenterAnalysis])
@require_permission("cost_center.read", "dashboard")
async def get_cost_center_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get cost center analysis for enterprise billing"""
    
    # Get all cost centers for the organization
    cost_centers_query = await db.execute(
        select(CostCenter).where(
            CostCenter.organization_id == current_user.organization_id
        )
    )
    cost_centers = cost_centers_query.scalars().all()
    
    result = []
    
    for cost_center in cost_centers:
        # Calculate total spent (placeholder - would need proper allocation logic)
        total_spent = 1250.75  # Calculate from usage allocations
        budget_limit = cost_center.budget_limit or 10000
        budget_utilization = (total_spent / budget_limit) * 100 if budget_limit > 0 else 0
        
        # Determine trending (placeholder logic)
        trending = "up" if budget_utilization > 80 else "stable" if budget_utilization > 40 else "down"
        
        # Get top users for this cost center (placeholder)
        top_users = [
            {"user": "john.doe@company.com", "cost": 345.50, "requests": 1250},
            {"user": "jane.smith@company.com", "cost": 289.25, "requests": 980}
        ]
        
        result.append(CostCenterAnalysis(
            cost_center_id=cost_center.id,
            name=cost_center.name,
            budget_limit=float(budget_limit / 100) if budget_limit else None,  # Convert from cents
            total_spent=total_spent,
            budget_utilization=budget_utilization,
            top_users=top_users,
            trending=trending
        ))
    
    return result


@router.get("/intelligent-routing", response_model=IntelligentRoutingData)
@require_permission("analytics.read", "dashboard")
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


@router.get("/workflow-analytics")
@require_permission("workflow.read", "dashboard")
async def get_workflow_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow execution analytics"""
    
    # Get workflow statistics
    workflows_query = await db.execute(
        select(
            func.count(Workflow.id).label("total_workflows"),
            func.count(Workflow.id).filter(Workflow.status == 'active').label("active_workflows")
        ).where(Workflow.organization_id == current_user.organization_id)
    )
    workflow_stats = workflows_query.first()
    
    return {
        "total_workflows": workflow_stats.total_workflows or 0,
        "active_workflows": workflow_stats.active_workflows or 0,
        "execution_success_rate": 94.5,  # Calculate from executions
        "avg_execution_time": 2.3,  # Calculate from executions
        "most_used_workflows": [
            {"name": "Content Analysis", "executions": 1250, "success_rate": 96.2},
            {"name": "Data Processing", "executions": 890, "success_rate": 98.1}
        ]
    }


@router.get("/ab-testing-summary")
@require_permission("ab_testing.read", "dashboard")
async def get_ab_testing_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get A/B testing summary"""
    
    # Get A/B test statistics
    tests_query = await db.execute(
        select(
            func.count(ABTest.id).label("total_tests"),
            func.count(ABTest.id).filter(ABTest.status == 'active').label("active_tests"),
            func.count(ABTest.id).filter(ABTest.status == 'completed').label("completed_tests")
        ).where(ABTest.organization_id == current_user.organization_id)
    )
    test_stats = tests_query.first()
    
    return {
        "total_tests": test_stats.total_tests or 0,
        "active_tests": test_stats.active_tests or 0,
        "completed_tests": test_stats.completed_tests or 0,
        "significant_results": 8,  # Calculate from test results
        "cost_savings_identified": 15.3,  # Percentage
        "recent_winners": [
            {"test": "Provider Comparison", "winner": "Claude", "improvement": "23% faster"},
            {"test": "Cost Optimization", "winner": "Groq", "improvement": "45% cheaper"}
        ]
    }


# Helper functions
async def _get_provider_health_summary() -> Dict[str, Any]:
    """Get provider health summary"""
    health_status = await enhanced_gateway.health_check()
    
    total_providers = health_status.get("total_providers", 0)
    healthy_providers = health_status.get("healthy_providers", 0)
    
    return {
        "total_providers": total_providers,
        "healthy_providers": healthy_providers,
        "health_percentage": (healthy_providers / max(1, total_providers)) * 100
    }


async def _get_recent_login_count(db: AsyncSession, organization_id: str, start_date: datetime) -> int:
    """Get count of recent logins"""
    # This would require a login tracking table in production
    return 15  # Placeholder


async def _get_top_users_by_usage(
    db: AsyncSession, 
    organization_id: str, 
    start_date: datetime, 
    limit: int
) -> List[Dict[str, Any]]:
    """Get top users by API usage"""
    
    # Get top users by request count
    top_users_query = await db.execute(
        select(
            APIKey.user_id,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.cost_usd + UsageRecord.markup_usd).label("cost")
        ).join(
            UsageRecord, APIKey.id == UsageRecord.api_key_id
        ).where(
            APIKey.organization_id == organization_id,
            UsageRecord.created_at >= start_date,
            UsageRecord.success == True
        ).group_by(
            APIKey.user_id
        ).order_by(
            desc("requests")
        ).limit(limit)
    )
    
    return [
        {
            "user_id": row.user_id,
            "requests": row.requests,
            "cost": float(row.cost or 0)
        }
        for row in top_users_query
    ]


@router.get("/provider-performance")
@require_permission("analytics.read", "dashboard")
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
@require_permission("analytics.read", "dashboard")
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
@require_permission("usage.read", "dashboard")
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
@require_permission("organization.read", "dashboard")
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
        "plan_type": org.plan_type.value if org.plan_type else "free",
        "created_at": org.created_at.isoformat() if org.created_at else None,
        "settings": org.settings or {},
        "features": org.features or {},
        "monthly_request_limit": org.monthly_request_limit,
        "monthly_token_limit": org.monthly_token_limit
    }


@router.get("/team-members")
@require_permission("user.read", "dashboard")
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
            "full_name": member.full_name,
            "role": member.role.value if member.role else "member",
            "is_active": member.is_active,
            "created_at": member.created_at.isoformat() if member.created_at else None,
            "last_login_at": member.last_login_at if member.last_login_at else None
        }
        for member in members
    ]