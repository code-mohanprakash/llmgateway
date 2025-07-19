"""
Monitoring service for enterprise infrastructure
"""
import psutil
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from models.monitoring import (
    SystemHealth, PerformanceMetric, Alert, SLAMetric, 
    Incident, MonitoringConfig
)
from models.user import User, Organization


class MonitoringService:
    """Service for system monitoring and alerting"""
    
    def __init__(self):
        self.start_time = time.time()
        self.monitoring_active = True
    
    async def collect_system_health(self, db: AsyncSession, organization_id: str = None) -> Dict[str, Any]:
        """Collect current system health metrics"""
        
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate network latency (simplified)
            network_latency = 50.0  # ms - would be measured in production
            
            # Calculate response time (average from recent requests)
            response_time = await self._get_average_response_time(db)
            
            # Determine status
            status = self._determine_health_status(cpu_usage, memory.percent, disk.percent)
            
            # Calculate uptime
            uptime_seconds = int(time.time() - self.start_time)
            
            # Create health record
            health_data = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "network_latency": network_latency,
                "response_time": response_time,
                "status": status,
                "uptime_seconds": uptime_seconds,
                "active_connections": await self._get_active_connections(db),
                "error_rate": await self._get_error_rate(db),
                "throughput": await self._get_throughput(db),
                "organization_id": organization_id
            }
            
            # Save to database
            health_record = SystemHealth(**health_data)
            db.add(health_record)
            await db.commit()
            
            # Check for alerts
            await self._check_alerts(health_data, db, organization_id)
            
            return health_data
            
        except Exception as e:
            print(f"Error collecting system health: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_average_response_time(self, db: AsyncSession) -> float:
        """Get average response time from recent requests"""
        try:
            # Get recent performance metrics
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'api_response_time',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
            )
            
            metrics = result.scalars().all()
            if metrics:
                return sum(m.value for m in metrics) / len(metrics)
            return 100.0  # Default response time
            
        except Exception as e:
            print(f"Error getting response time: {e}")
            return 100.0
    
    async def _get_active_connections(self, db: AsyncSession) -> int:
        """Get number of active connections"""
        try:
            # This would be implemented with actual connection tracking
            return 10  # Placeholder
        except Exception as e:
            print(f"Error getting active connections: {e}")
            return 0
    
    async def _get_error_rate(self, db: AsyncSession) -> float:
        """Get current error rate"""
        try:
            # Calculate error rate from recent requests
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'api_errors',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
            )
            
            error_metrics = result.scalars().all()
            if error_metrics:
                total_errors = sum(m.value for m in error_metrics)
                return min(total_errors, 100.0)  # Cap at 100%
            return 0.0
            
        except Exception as e:
            print(f"Error getting error rate: {e}")
            return 0.0
    
    async def _get_throughput(self, db: AsyncSession) -> float:
        """Get current requests per second"""
        try:
            # Calculate throughput from recent requests
            recent_time = datetime.utcnow() - timedelta(minutes=1)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'requests_per_second',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
            )
            
            throughput_metrics = result.scalars().all()
            if throughput_metrics:
                return sum(m.value for m in throughput_metrics) / len(throughput_metrics)
            return 10.0  # Default throughput
            
        except Exception as e:
            print(f"Error getting throughput: {e}")
            return 10.0
    
    def _determine_health_status(self, cpu: float, memory: float, disk: float) -> str:
        """Determine system health status"""
        if cpu > 95 or memory > 95 or disk > 95:
            return "critical"
        elif cpu > 80 or memory > 80 or disk > 80:
            return "warning"
        else:
            return "healthy"
    
    async def _check_alerts(self, health_data: Dict[str, Any], db: AsyncSession, organization_id: str = None):
        """Check if any alerts should be triggered"""
        
        try:
            # Get monitoring configuration
            config = await self._get_monitoring_config(db, organization_id)
            
            # Check CPU alerts
            if health_data["cpu_usage"] > config["cpu_critical_threshold"]:
                await self._create_alert(
                    "system", "critical", "High CPU Usage",
                    f"CPU usage is {health_data['cpu_usage']:.1f}%",
                    "system_monitoring", "cpu_usage", config["cpu_critical_threshold"],
                    health_data["cpu_usage"], db, organization_id
                )
            elif health_data["cpu_usage"] > config["cpu_warning_threshold"]:
                await self._create_alert(
                    "system", "warning", "High CPU Usage",
                    f"CPU usage is {health_data['cpu_usage']:.1f}%",
                    "system_monitoring", "cpu_usage", config["cpu_warning_threshold"],
                    health_data["cpu_usage"], db, organization_id
                )
            
            # Check memory alerts
            if health_data["memory_usage"] > config["memory_critical_threshold"]:
                await self._create_alert(
                    "system", "critical", "High Memory Usage",
                    f"Memory usage is {health_data['memory_usage']:.1f}%",
                    "system_monitoring", "memory_usage", config["memory_critical_threshold"],
                    health_data["memory_usage"], db, organization_id
                )
            elif health_data["memory_usage"] > config["memory_warning_threshold"]:
                await self._create_alert(
                    "system", "warning", "High Memory Usage",
                    f"Memory usage is {health_data['memory_usage']:.1f}%",
                    "system_monitoring", "memory_usage", config["memory_warning_threshold"],
                    health_data["memory_usage"], db, organization_id
                )
            
            # Check response time alerts
            if health_data["response_time"] > config["response_time_critical_threshold"]:
                await self._create_alert(
                    "performance", "critical", "High Response Time",
                    f"Average response time is {health_data['response_time']:.1f}ms",
                    "performance_monitoring", "response_time", config["response_time_critical_threshold"],
                    health_data["response_time"], db, organization_id
                )
            elif health_data["response_time"] > config["response_time_warning_threshold"]:
                await self._create_alert(
                    "performance", "warning", "High Response Time",
                    f"Average response time is {health_data['response_time']:.1f}ms",
                    "performance_monitoring", "response_time", config["response_time_warning_threshold"],
                    health_data["response_time"], db, organization_id
                )
                
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    async def _get_monitoring_config(self, db: AsyncSession, organization_id: str = None) -> Dict[str, Any]:
        """Get monitoring configuration"""
        try:
            result = await db.execute(
                select(MonitoringConfig)
                .where(MonitoringConfig.config_name == "default")
            )
            
            config = result.scalar_one_or_none()
            if config:
                return {
                    "cpu_warning_threshold": config.cpu_warning_threshold,
                    "cpu_critical_threshold": config.cpu_critical_threshold,
                    "memory_warning_threshold": config.memory_warning_threshold,
                    "memory_critical_threshold": config.memory_critical_threshold,
                    "response_time_warning_threshold": config.response_time_warning_threshold,
                    "response_time_critical_threshold": config.response_time_critical_threshold,
                    "uptime_target": config.uptime_target,
                    "response_time_target": config.response_time_target
                }
            
            # Return default configuration
            return {
                "cpu_warning_threshold": 80.0,
                "cpu_critical_threshold": 95.0,
                "memory_warning_threshold": 80.0,
                "memory_critical_threshold": 95.0,
                "response_time_warning_threshold": 1000.0,
                "response_time_critical_threshold": 5000.0,
                "uptime_target": 99.99,
                "response_time_target": 100.0
            }
            
        except Exception as e:
            print(f"Error getting monitoring config: {e}")
            return {
                "cpu_warning_threshold": 80.0,
                "cpu_critical_threshold": 95.0,
                "memory_warning_threshold": 80.0,
                "memory_critical_threshold": 95.0,
                "response_time_warning_threshold": 1000.0,
                "response_time_critical_threshold": 5000.0,
                "uptime_target": 99.99,
                "response_time_target": 100.0
            }
    
    async def _create_alert(
        self, alert_type: str, severity: str, title: str, message: str,
        source: str, metric_name: str, threshold_value: float, current_value: float,
        db: AsyncSession, organization_id: str = None
    ):
        """Create a new alert"""
        
        try:
            # Check if similar alert already exists
            result = await db.execute(
                select(Alert)
                .where(
                    and_(
                        Alert.alert_type == alert_type,
                        Alert.severity == severity,
                        Alert.source == source,
                        Alert.status == 'active',
                        Alert.organization_id == organization_id
                    )
                )
            )
            
            existing_alert = result.scalar_one_or_none()
            if existing_alert:
                # Update existing alert
                existing_alert.current_value = current_value
                existing_alert.message = message
                await db.commit()
                return
            
            # Create new alert
            alert = Alert(
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                source=source,
                metric_name=metric_name,
                threshold_value=threshold_value,
                current_value=current_value,
                organization_id=organization_id,
                notification_channels=["email"]  # Default to email
            )
            
            db.add(alert)
            await db.commit()
            
            # TODO: Send notifications
            await self._send_notifications(alert, db)
            
        except Exception as e:
            print(f"Error creating alert: {e}")
    
    async def _send_notifications(self, alert: Alert, db: AsyncSession):
        """Send notifications for alerts"""
        try:
            # TODO: Implement actual notification sending
            # For now, just mark as sent
            alert.notification_sent = True
            await db.commit()
            
        except Exception as e:
            print(f"Error sending notifications: {e}")
    
    async def record_performance_metric(
        self, metric_name: str, value: float, unit: str,
        endpoint: str = None, method: str = None,
        user_id: str = None, organization_id: str = None,
        db: AsyncSession = None
    ):
        """Record a performance metric"""
        
        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                metric_type="gauge",  # Default type
                value=value,
                unit=unit,
                endpoint=endpoint,
                method=method,
                user_id=user_id,
                organization_id=organization_id
            )
            
            db.add(metric)
            await db.commit()
            
        except Exception as e:
            print(f"Error recording performance metric: {e}")
    
    async def get_health_dashboard(self, db: AsyncSession, organization_id: str = None) -> Dict[str, Any]:
        """Get health dashboard data"""
        
        try:
            # Get latest health data
            result = await db.execute(
                select(SystemHealth)
                .where(SystemHealth.organization_id == organization_id)
                .order_by(SystemHealth.recorded_at.desc())
                .limit(1)
            )
            
            latest_health = result.scalar_one_or_none()
            
            # Get recent alerts
            recent_time = datetime.utcnow() - timedelta(hours=24)
            result = await db.execute(
                select(Alert)
                .where(
                    and_(
                        Alert.organization_id == organization_id,
                        Alert.created_at >= recent_time
                    )
                )
                .order_by(Alert.created_at.desc())
                .limit(10)
            )
            
            recent_alerts = result.scalars().all()
            
            # Get SLA metrics
            result = await db.execute(
                select(SLAMetric)
                .where(SLAMetric.organization_id == organization_id)
                .order_by(SLAMetric.recorded_at.desc())
                .limit(5)
            )
            
            sla_metrics = result.scalars().all()
            
            # Get active incidents
            result = await db.execute(
                select(Incident)
                .where(
                    and_(
                        Incident.organization_id == organization_id,
                        Incident.status.in_(['open', 'investigating'])
                    )
                )
                .order_by(Incident.detected_at.desc())
                .limit(5)
            )
            
            active_incidents = result.scalars().all()
            
            return {
                "current_health": {
                    "status": latest_health.status if latest_health else "unknown",
                    "cpu_usage": latest_health.cpu_usage if latest_health else 0,
                    "memory_usage": latest_health.memory_usage if latest_health else 0,
                    "disk_usage": latest_health.disk_usage if latest_health else 0,
                    "response_time": latest_health.response_time if latest_health else 0,
                    "uptime_seconds": latest_health.uptime_seconds if latest_health else 0
                },
                "recent_alerts": [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "title": alert.title,
                        "message": alert.message,
                        "created_at": alert.created_at.isoformat(),
                        "status": alert.status
                    }
                    for alert in recent_alerts
                ],
                "sla_metrics": [
                    {
                        "name": sla.sla_name,
                        "target": sla.sla_target,
                        "current": sla.current_value,
                        "compliance": sla.compliance_percentage,
                        "status": sla.status
                    }
                    for sla in sla_metrics
                ],
                "active_incidents": [
                    {
                        "id": incident.id,
                        "type": incident.incident_type,
                        "severity": incident.severity,
                        "title": incident.title,
                        "status": incident.status,
                        "priority": incident.priority,
                        "detected_at": incident.detected_at.isoformat()
                    }
                    for incident in active_incidents
                ]
            }
            
        except Exception as e:
            print(f"Error getting health dashboard: {e}")
            return {
                "error": str(e),
                "current_health": {},
                "recent_alerts": [],
                "sla_metrics": [],
                "active_incidents": []
            }


# Global monitoring service instance
monitoring_service = MonitoringService() 