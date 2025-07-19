"""
Monitoring API Router - Phase 5: Enterprise Infrastructure

This module provides API endpoints for:
- System health monitoring
- Performance metrics tracking
- Alert management
- SLA compliance monitoring
- Incident management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import time

from auth.dependencies import get_current_user
from auth.rbac_middleware import require_permission
from models.user import User
from monitoring.monitoring_service import monitoring_service
from monitoring.performance_optimizer import performance_optimizer
from monitoring.scalability_manager import scalability_manager
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
security = HTTPBearer()


# Health Monitoring Endpoints

@router.get("/health")
@require_permission("monitoring.read", "monitoring")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current system health status"""
    
    try:
        # Collect current health data
        health_data = await monitoring_service.collect_system_health(
            db=db,
            organization_id=current_user.organization_id
        )
        
        return {
            "success": True,
            "health_data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


@router.get("/health/dashboard")
@require_permission("monitoring.read", "monitoring")
async def get_health_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive health dashboard data"""
    
    try:
        dashboard_data = await monitoring_service.get_health_dashboard(
            db=db,
            organization_id=current_user.organization_id
        )
        
        return {
            "success": True,
            "dashboard_data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error getting health dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get health dashboard")


@router.post("/health/collect")
@require_permission("monitoring.write", "monitoring")
async def collect_health_metrics(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger health metrics collection"""
    
    try:
        # Collect health metrics
        health_data = await monitoring_service.collect_system_health(
            db=db,
            organization_id=current_user.organization_id
        )
        
        return {
            "success": True,
            "message": "Health metrics collected successfully",
            "health_data": health_data
        }
        
    except Exception as e:
        logger.error(f"Error collecting health metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect health metrics")


# Performance Metrics Endpoints

@router.post("/metrics")
@require_permission("monitoring.write", "monitoring")
async def record_performance_metric(
    metric_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a performance metric"""
    
    try:
        # Validate required fields
        required_fields = ["metric_name", "value", "unit"]
        for field in required_fields:
            if field not in metric_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Record the metric
        await monitoring_service.record_performance_metric(
            metric_name=metric_data["metric_name"],
            value=metric_data["value"],
            unit=metric_data["unit"],
            endpoint=metric_data.get("endpoint"),
            method=metric_data.get("method"),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            db=db
        )
        
        return {
            "success": True,
            "message": "Performance metric recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error recording performance metric: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to record metric: {str(e)}")


@router.get("/metrics")
@require_permission("monitoring.read", "monitoring")
async def get_performance_metrics(
    metric_name: Optional[str] = Query(None),
    time_range_hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics"""
    
    try:
        from models.monitoring import PerformanceMetric
        from sqlalchemy import select, and_
        
        # Build query
        query = select(PerformanceMetric).where(
            and_(
                PerformanceMetric.organization_id == current_user.organization_id,
                PerformanceMetric.recorded_at >= datetime.utcnow() - timedelta(hours=time_range_hours)
            )
        )
        
        if metric_name:
            query = query.where(PerformanceMetric.metric_name == metric_name)
        
        query = query.order_by(PerformanceMetric.recorded_at.desc())
        
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        return {
            "success": True,
            "metrics": [
                {
                    "id": metric.id,
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "endpoint": metric.endpoint,
                    "method": metric.method,
                    "recorded_at": metric.recorded_at.isoformat()
                }
                for metric in metrics
            ],
            "total": len(metrics)
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


# Alert Management Endpoints

@router.get("/alerts")
@require_permission("monitoring.read", "monitoring")
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get alerts"""
    
    try:
        from models.monitoring import Alert
        from sqlalchemy import select, and_
        
        # Build query
        query = select(Alert).where(
            Alert.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.where(Alert.status == status)
        if severity:
            query = query.where(Alert.severity == severity)
        if alert_type:
            query = query.where(Alert.alert_type == alert_type)
        
        query = query.order_by(Alert.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return {
            "success": True,
            "alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "status": alert.status,
                    "source": alert.source,
                    "metric_name": alert.metric_name,
                    "threshold_value": alert.threshold_value,
                    "current_value": alert.current_value,
                    "created_at": alert.created_at.isoformat(),
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in alerts
            ],
            "total": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")


@router.post("/alerts/{alert_id}/acknowledge")
@require_permission("monitoring.write", "monitoring")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an alert"""
    
    try:
        from models.monitoring import Alert
        
        # Get alert
        result = await db.execute(
            select(Alert).where(
                and_(
                    Alert.id == alert_id,
                    Alert.organization_id == current_user.organization_id
                )
            )
        )
        
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.status = "acknowledged"
        alert.acknowledged_by = current_user.id
        alert.acknowledged_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Alert acknowledged successfully"
        }
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/alerts/{alert_id}/resolve")
@require_permission("monitoring.write", "monitoring")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resolve an alert"""
    
    try:
        from models.monitoring import Alert
        
        # Get alert
        result = await db.execute(
            select(Alert).where(
                and_(
                    Alert.id == alert_id,
                    Alert.organization_id == current_user.organization_id
                )
            )
        )
        
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Alert resolved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to resolve alert: {str(e)}")


# SLA Monitoring Endpoints

@router.get("/sla")
@require_permission("monitoring.read", "monitoring")
async def get_sla_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get SLA metrics"""
    
    try:
        from models.monitoring import SLAMetric
        
        result = await db.execute(
            select(SLAMetric)
            .where(SLAMetric.organization_id == current_user.organization_id)
            .order_by(SLAMetric.recorded_at.desc())
            .limit(10)
        )
        
        sla_metrics = result.scalars().all()
        
        return {
            "success": True,
            "sla_metrics": [
                {
                    "id": sla.id,
                    "sla_name": sla.sla_name,
                    "sla_target": sla.sla_target,
                    "current_value": sla.current_value,
                    "compliance_percentage": sla.compliance_percentage,
                    "status": sla.status,
                    "period_start": sla.period_start.isoformat(),
                    "period_end": sla.period_end.isoformat(),
                    "recorded_at": sla.recorded_at.isoformat()
                }
                for sla in sla_metrics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting SLA metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get SLA metrics")


# Incident Management Endpoints

@router.get("/incidents")
@require_permission("monitoring.read", "monitoring")
async def get_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get incidents"""
    
    try:
        from models.monitoring import Incident
        from sqlalchemy import select, and_
        
        # Build query
        query = select(Incident).where(
            Incident.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.where(Incident.status == status)
        if severity:
            query = query.where(Incident.severity == severity)
        
        query = query.order_by(Incident.detected_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        return {
            "success": True,
            "incidents": [
                {
                    "id": incident.id,
                    "incident_type": incident.incident_type,
                    "severity": incident.severity,
                    "title": incident.title,
                    "description": incident.description,
                    "status": incident.status,
                    "priority": incident.priority,
                    "affected_services": incident.affected_services,
                    "impact_level": incident.impact_level,
                    "detected_at": incident.detected_at.isoformat(),
                    "updated_at": incident.updated_at.isoformat(),
                    "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None
                }
                for incident in incidents
            ],
            "total": len(incidents)
        }
        
    except Exception as e:
        logger.error(f"Error getting incidents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get incidents")


@router.post("/incidents")
@require_permission("monitoring.write", "monitoring")
async def create_incident(
    incident_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new incident"""
    
    try:
        from models.monitoring import Incident
        
        # Validate required fields
        required_fields = ["incident_type", "severity", "title", "description", "priority", "impact_level"]
        for field in required_fields:
            if field not in incident_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create incident
        incident = Incident(
            incident_type=incident_data["incident_type"],
            severity=incident_data["severity"],
            title=incident_data["title"],
            description=incident_data["description"],
            priority=incident_data["priority"],
            impact_level=incident_data["impact_level"],
            affected_services=incident_data.get("affected_services", []),
            organization_id=current_user.organization_id
        )
        
        db.add(incident)
        await db.commit()
        
        return {
            "success": True,
            "incident_id": incident.id,
            "message": "Incident created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create incident: {str(e)}")


# Configuration Endpoints

@router.get("/config")
@require_permission("monitoring.read", "monitoring")
async def get_monitoring_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get monitoring configuration"""
    
    try:
        from models.monitoring import MonitoringConfig
        
        result = await db.execute(
            select(MonitoringConfig).where(MonitoringConfig.config_name == "default")
        )
        
        config = result.scalar_one_or_none()
        
        if config:
            return {
                "success": True,
                "config": {
                    "cpu_warning_threshold": config.cpu_warning_threshold,
                    "cpu_critical_threshold": config.cpu_critical_threshold,
                    "memory_warning_threshold": config.memory_warning_threshold,
                    "memory_critical_threshold": config.memory_critical_threshold,
                    "response_time_warning_threshold": config.response_time_warning_threshold,
                    "response_time_critical_threshold": config.response_time_critical_threshold,
                    "uptime_target": config.uptime_target,
                    "response_time_target": config.response_time_target,
                    "email_notifications": config.email_notifications,
                    "slack_notifications": config.slack_notifications,
                    "webhook_notifications": config.webhook_notifications,
                    "notification_recipients": config.notification_recipients
                }
            }
        else:
            # Return default configuration
            return {
                "success": True,
                "config": {
                    "cpu_warning_threshold": 80.0,
                    "cpu_critical_threshold": 95.0,
                    "memory_warning_threshold": 80.0,
                    "memory_critical_threshold": 95.0,
                    "response_time_warning_threshold": 1000.0,
                    "response_time_critical_threshold": 5000.0,
                    "uptime_target": 99.99,
                    "response_time_target": 100.0,
                    "email_notifications": True,
                    "slack_notifications": False,
                    "webhook_notifications": False,
                    "notification_recipients": []
                }
            }
        
    except Exception as e:
        logger.error(f"Error getting monitoring config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get monitoring config")


@router.put("/config")
@require_permission("monitoring.write", "monitoring")
async def update_monitoring_config(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update monitoring configuration"""
    
    try:
        from models.monitoring import MonitoringConfig
        
        # Get existing config or create new one
        result = await db.execute(
            select(MonitoringConfig).where(MonitoringConfig.config_name == "default")
        )
        
        config = result.scalar_one_or_none()
        
        if config:
            # Update existing config
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        else:
            # Create new config
            config = MonitoringConfig(
                config_name="default",
                config_type="alert",
                **config_data
            )
            db.add(config)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Monitoring configuration updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating monitoring config: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update config: {str(e)}")


# Performance Optimization Endpoints

@router.get("/performance/optimize")
@require_permission("monitoring.read", "monitoring")
async def optimize_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Optimize database queries and performance"""
    
    try:
        optimization_data = await performance_optimizer.optimize_database_queries(db)
        
        return {
            "success": True,
            "optimization_data": optimization_data
        }
        
    except Exception as e:
        logger.error(f"Error optimizing performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize performance")


@router.get("/performance/response-times")
@require_permission("monitoring.read", "monitoring")
async def optimize_response_times(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Optimize API response times"""
    
    try:
        response_data = await performance_optimizer.optimize_response_times(db)
        
        return {
            "success": True,
            "response_data": response_data
        }
        
    except Exception as e:
        logger.error(f"Error optimizing response times: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize response times")


@router.get("/performance/cache/stats")
@require_permission("monitoring.read", "monitoring")
async def get_cache_statistics():
    """Get cache statistics"""
    
    try:
        cache_stats = await performance_optimizer.get_cache_statistics()
        
        return {
            "success": True,
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")


@router.post("/performance/cache/clear")
@require_permission("monitoring.write", "monitoring")
async def clear_performance_cache():
    """Clear performance cache"""
    
    try:
        success = await performance_optimizer.clear_performance_cache()
        
        return {
            "success": success,
            "message": "Performance cache cleared successfully" if success else "Failed to clear cache"
        }
        
    except Exception as e:
        logger.error(f"Error clearing performance cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear performance cache")


@router.get("/performance/summary")
@require_permission("monitoring.read", "monitoring")
async def get_performance_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive performance summary"""
    
    try:
        summary = await performance_optimizer.get_performance_summary(db)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance summary")


# Scalability Management Endpoints

@router.get("/scalability/analyze")
@require_permission("monitoring.read", "monitoring")
async def analyze_scalability(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze scalability needs"""
    
    try:
        analysis = await scalability_manager.analyze_scalability_needs(db)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing scalability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze scalability")


@router.post("/scalability/auto-scaling")
@require_permission("monitoring.write", "monitoring")
async def toggle_auto_scaling(
    enabled: bool,
    current_user: User = Depends(get_current_user)
):
    """Enable or disable auto-scaling"""
    
    try:
        result = await scalability_manager.enable_auto_scaling(enabled)
        
        return {
            "success": result["success"],
            "message": result.get("message", "Auto-scaling status updated")
        }
        
    except Exception as e:
        logger.error(f"Error toggling auto-scaling: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle auto-scaling")


@router.put("/scalability/thresholds")
@require_permission("monitoring.write", "monitoring")
async def update_scaling_thresholds(
    thresholds: Dict[str, float],
    current_user: User = Depends(get_current_user)
):
    """Update scaling thresholds"""
    
    try:
        result = await scalability_manager.set_scaling_thresholds(thresholds)
        
        return {
            "success": result["success"],
            "message": result.get("message", "Scaling thresholds updated")
        }
        
    except Exception as e:
        logger.error(f"Error updating scaling thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update scaling thresholds")


@router.get("/scalability/config")
@require_permission("monitoring.read", "monitoring")
async def get_scaling_configuration(
    current_user: User = Depends(get_current_user)
):
    """Get scaling configuration"""
    
    try:
        config = await scalability_manager.get_scaling_configuration()
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Error getting scaling config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scaling config")


@router.post("/scalability/simulate")
@require_permission("monitoring.write", "monitoring")
async def simulate_scaling_event(
    event_type: str,
    instances: int,
    current_user: User = Depends(get_current_user)
):
    """Simulate a scaling event"""
    
    try:
        result = await scalability_manager.simulate_scaling_event(event_type, instances)
        
        return {
            "success": result["success"],
            "event": result.get("event"),
            "current_instances": result.get("current_instances")
        }
        
    except Exception as e:
        logger.error(f"Error simulating scaling event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate scaling event")


@router.get("/scalability/load-balancer")
@require_permission("monitoring.read", "monitoring")
async def get_load_balancer_status(
    current_user: User = Depends(get_current_user)
):
    """Get load balancer status"""
    
    try:
        status = await scalability_manager.get_load_balancer_status()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting load balancer status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get load balancer status")


@router.get("/scalability/database")
@require_permission("monitoring.read", "monitoring")
async def get_database_sharding_status(
    current_user: User = Depends(get_current_user)
):
    """Get database sharding status"""
    
    try:
        status = await scalability_manager.get_database_sharding_status()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting database sharding status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get database sharding status")


@router.get("/scalability/microservices")
@require_permission("monitoring.read", "monitoring")
async def get_microservices_status(
    current_user: User = Depends(get_current_user)
):
    """Get microservices status"""
    
    try:
        status = await scalability_manager.get_microservices_status()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting microservices status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get microservices status") 