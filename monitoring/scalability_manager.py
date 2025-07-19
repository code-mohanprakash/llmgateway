"""
Scalability manager for enterprise infrastructure
"""
import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import json

from models.monitoring import SystemHealth, PerformanceMetric
from models.user import User, Organization


class ScalabilityManager:
    """Service for managing scalability and auto-scaling"""
    
    def __init__(self):
        self.scaling_thresholds = {
            "cpu_high": 80.0,
            "cpu_critical": 95.0,
            "memory_high": 80.0,
            "memory_critical": 95.0,
            "response_time_high": 1000.0,
            "response_time_critical": 5000.0,
            "concurrent_users_high": 1000,
            "concurrent_users_critical": 5000
        }
        self.auto_scaling_enabled = True
        self.scaling_history = []
        self.current_instances = 1
        self.max_instances = 10
    
    async def analyze_scalability_needs(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze current scalability needs"""
        
        try:
            # Get current system metrics
            current_metrics = await self._get_current_metrics(db)
            
            # Calculate scaling recommendations
            scaling_recommendations = await self._calculate_scaling_recommendations(current_metrics)
            
            # Get historical scaling data
            scaling_history = await self._get_scaling_history(db)
            
            return {
                "current_metrics": current_metrics,
                "scaling_recommendations": scaling_recommendations,
                "scaling_history": scaling_history,
                "auto_scaling_status": {
                    "enabled": self.auto_scaling_enabled,
                    "current_instances": self.current_instances,
                    "max_instances": self.max_instances
                }
            }
            
        except Exception as e:
            print(f"Error analyzing scalability needs: {e}")
            return {
                "error": str(e),
                "current_metrics": {},
                "scaling_recommendations": [],
                "scaling_history": [],
                "auto_scaling_status": {}
            }
    
    async def _get_current_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get current system metrics"""
        
        try:
            # Get latest health data
            result = await db.execute(
                select(SystemHealth)
                .order_by(SystemHealth.recorded_at.desc())
                .limit(1)
            )
            
            latest_health = result.scalar_one_or_none()
            
            if latest_health:
                return {
                    "cpu_usage": latest_health.cpu_usage,
                    "memory_usage": latest_health.memory_usage,
                    "response_time": latest_health.response_time,
                    "active_connections": latest_health.active_connections,
                    "throughput": latest_health.throughput,
                    "recorded_at": latest_health.recorded_at.isoformat()
                }
            
            # Fallback to system metrics
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "response_time": 100.0,  # Default
                "active_connections": 10,  # Default
                "throughput": 10.0,  # Default
                "recorded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting current metrics: {e}")
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "response_time": 0,
                "active_connections": 0,
                "throughput": 0,
                "recorded_at": datetime.utcnow().isoformat()
            }
    
    async def _calculate_scaling_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate scaling recommendations based on metrics"""
        
        recommendations = []
        
        # CPU-based scaling
        if metrics["cpu_usage"] > self.scaling_thresholds["cpu_critical"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "critical",
                "reason": "CPU usage critical",
                "current_value": metrics["cpu_usage"],
                "threshold": self.scaling_thresholds["cpu_critical"],
                "action": "Scale up immediately - add more instances",
                "estimated_instances": min(self.current_instances + 2, self.max_instances)
            })
        elif metrics["cpu_usage"] > self.scaling_thresholds["cpu_high"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "high",
                "reason": "CPU usage high",
                "current_value": metrics["cpu_usage"],
                "threshold": self.scaling_thresholds["cpu_high"],
                "action": "Scale up - add one more instance",
                "estimated_instances": min(self.current_instances + 1, self.max_instances)
            })
        
        # Memory-based scaling
        if metrics["memory_usage"] > self.scaling_thresholds["memory_critical"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "critical",
                "reason": "Memory usage critical",
                "current_value": metrics["memory_usage"],
                "threshold": self.scaling_thresholds["memory_critical"],
                "action": "Scale up immediately - add more instances",
                "estimated_instances": min(self.current_instances + 2, self.max_instances)
            })
        elif metrics["memory_usage"] > self.scaling_thresholds["memory_high"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "high",
                "reason": "Memory usage high",
                "current_value": metrics["memory_usage"],
                "threshold": self.scaling_thresholds["memory_high"],
                "action": "Scale up - add one more instance",
                "estimated_instances": min(self.current_instances + 1, self.max_instances)
            })
        
        # Response time-based scaling
        if metrics["response_time"] > self.scaling_thresholds["response_time_critical"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "critical",
                "reason": "Response time critical",
                "current_value": metrics["response_time"],
                "threshold": self.scaling_thresholds["response_time_critical"],
                "action": "Scale up immediately - add more instances",
                "estimated_instances": min(self.current_instances + 2, self.max_instances)
            })
        elif metrics["response_time"] > self.scaling_thresholds["response_time_high"]:
            recommendations.append({
                "type": "scale_up",
                "priority": "high",
                "reason": "Response time high",
                "current_value": metrics["response_time"],
                "threshold": self.scaling_thresholds["response_time_high"],
                "action": "Scale up - add one more instance",
                "estimated_instances": min(self.current_instances + 1, self.max_instances)
            })
        
        # Scale down recommendations
        if (metrics["cpu_usage"] < 30 and 
            metrics["memory_usage"] < 30 and 
            metrics["response_time"] < 200 and
            self.current_instances > 1):
            recommendations.append({
                "type": "scale_down",
                "priority": "medium",
                "reason": "Low resource usage",
                "current_value": f"CPU: {metrics['cpu_usage']}%, Memory: {metrics['memory_usage']}%",
                "threshold": "Low usage",
                "action": "Scale down - remove one instance",
                "estimated_instances": max(self.current_instances - 1, 1)
            })
        
        return recommendations
    
    async def _get_scaling_history(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get scaling history"""
        
        try:
            # Get recent scaling events from performance metrics
            recent_time = datetime.utcnow() - timedelta(days=7)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'scaling_event',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
                .order_by(PerformanceMetric.recorded_at.desc())
                .limit(10)
            )
            
            scaling_events = result.scalars().all()
            
            return [
                {
                    "event_type": event.value,  # scale_up, scale_down
                    "timestamp": event.recorded_at.isoformat(),
                    "details": event.endpoint  # Additional details stored in endpoint field
                }
                for event in scaling_events
            ]
            
        except Exception as e:
            print(f"Error getting scaling history: {e}")
            return []
    
    async def enable_auto_scaling(self, enabled: bool = True) -> Dict[str, Any]:
        """Enable or disable auto-scaling"""
        
        try:
            self.auto_scaling_enabled = enabled
            
            return {
                "success": True,
                "auto_scaling_enabled": self.auto_scaling_enabled,
                "message": f"Auto-scaling {'enabled' if enabled else 'disabled'}"
            }
            
        except Exception as e:
            print(f"Error enabling auto-scaling: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_scaling_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Set scaling thresholds"""
        
        try:
            # Update thresholds
            for key, value in thresholds.items():
                if key in self.scaling_thresholds:
                    self.scaling_thresholds[key] = value
            
            return {
                "success": True,
                "thresholds": self.scaling_thresholds,
                "message": "Scaling thresholds updated"
            }
            
        except Exception as e:
            print(f"Error setting scaling thresholds: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_scaling_configuration(self) -> Dict[str, Any]:
        """Get current scaling configuration"""
        
        return {
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "current_instances": self.current_instances,
            "max_instances": self.max_instances,
            "scaling_thresholds": self.scaling_thresholds,
            "scaling_history": self.scaling_history[-10:]  # Last 10 events
        }
    
    async def simulate_scaling_event(self, event_type: str, instances: int) -> Dict[str, Any]:
        """Simulate a scaling event for testing"""
        
        try:
            if event_type == "scale_up":
                self.current_instances = min(self.current_instances + instances, self.max_instances)
            elif event_type == "scale_down":
                self.current_instances = max(self.current_instances - instances, 1)
            
            # Record scaling event
            scaling_event = {
                "event_type": event_type,
                "instances": instances,
                "new_total": self.current_instances,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.scaling_history.append(scaling_event)
            
            return {
                "success": True,
                "event": scaling_event,
                "current_instances": self.current_instances
            }
            
        except Exception as e:
            print(f"Error simulating scaling event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_load_balancer_status(self) -> Dict[str, Any]:
        """Get load balancer status"""
        
        try:
            # Simulate load balancer status
            return {
                "status": "healthy",
                "active_instances": self.current_instances,
                "health_checks": {
                    "instance_1": "healthy",
                    "instance_2": "healthy" if self.current_instances > 1 else "not_active",
                    "instance_3": "healthy" if self.current_instances > 2 else "not_active"
                },
                "traffic_distribution": {
                    "instance_1": 100 if self.current_instances == 1 else 50,
                    "instance_2": 50 if self.current_instances > 1 else 0,
                    "instance_3": 33 if self.current_instances > 2 else 0
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting load balancer status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_database_sharding_status(self) -> Dict[str, Any]:
        """Get database sharding status"""
        
        try:
            # Simulate database sharding status
            return {
                "sharding_enabled": False,
                "shards": [
                    {
                        "id": "shard_1",
                        "status": "active",
                        "connections": 50,
                        "load_percentage": 100
                    }
                ],
                "replication": {
                    "enabled": False,
                    "replicas": 0
                },
                "backup_status": "healthy",
                "last_backup": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting database sharding status: {e}")
            return {
                "sharding_enabled": False,
                "error": str(e)
            }
    
    async def get_microservices_status(self) -> Dict[str, Any]:
        """Get microservices status"""
        
        try:
            # Simulate microservices status
            return {
                "architecture": "monolithic",  # Currently monolithic
                "services": [
                    {
                        "name": "api_gateway",
                        "status": "healthy",
                        "instances": 1,
                        "response_time": 50
                    },
                    {
                        "name": "auth_service",
                        "status": "healthy",
                        "instances": 1,
                        "response_time": 30
                    },
                    {
                        "name": "llm_service",
                        "status": "healthy",
                        "instances": 1,
                        "response_time": 200
                    },
                    {
                        "name": "monitoring_service",
                        "status": "healthy",
                        "instances": 1,
                        "response_time": 20
                    }
                ],
                "service_mesh": "not_implemented",
                "container_orchestration": "not_implemented"
            }
            
        except Exception as e:
            print(f"Error getting microservices status: {e}")
            return {
                "architecture": "unknown",
                "error": str(e)
            }


# Global scalability manager instance
scalability_manager = ScalabilityManager() 