"""
Health Monitor for Provider Health Checking
Implements real-time provider health monitoring with 30-second intervals
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from providers.base import BaseModelProvider, GenerationRequest

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthMetrics:
    """Health metrics for a provider"""
    status: HealthStatus
    response_time: float
    success_rate: float
    error_count: int
    last_check: datetime
    consecutive_failures: int
    last_error: Optional[str] = None


class HealthMonitor:
    """
    Advanced health monitoring system for providers
    
    Features:
    - Real-time health checks every 30 seconds
    - Response time tracking
    - Success rate calculation
    - Automatic provider degradation detection
    - Circuit breaker pattern implementation
    """
    
    def __init__(self, check_interval: int = 30, failure_threshold: int = 3):
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.providers: Dict[str, BaseModelProvider] = {}
        self.health_metrics: Dict[str, HealthMetrics] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Circuit breaker settings
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    def register_provider(self, name: str, provider: BaseModelProvider):
        """Register a provider for health monitoring"""
        self.providers[name] = provider
        self.health_metrics[name] = HealthMetrics(
            status=HealthStatus.UNKNOWN,
            response_time=0.0,
            success_rate=0.0,
            error_count=0,
            last_check=datetime.utcnow(),
            consecutive_failures=0
        )
        self.circuit_breakers[name] = {
            "state": "closed",  # closed, open, half_open
            "failure_count": 0,
            "last_failure": None,
            "next_attempt": None
        }
        
        logger.info(f"Registered provider {name} for health monitoring")
    
    def unregister_provider(self, name: str):
        """Unregister a provider from health monitoring"""
        if name in self.providers:
            del self.providers[name]
            del self.health_metrics[name]
            del self.circuit_breakers[name]
            logger.info(f"Unregistered provider {name} from health monitoring")
    
    async def start_monitoring(self):
        """Start the health monitoring background task"""
        if self._running:
            return
        
        self._running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop the health monitoring background task"""
        self._running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop that runs health checks"""
        while self._running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all registered providers"""
        check_tasks = []
        
        for provider_name in self.providers.keys():
            task = asyncio.create_task(
                self._check_provider_health(provider_name),
                name=f"health_check_{provider_name}"
            )
            check_tasks.append(task)
        
        # Run all health checks concurrently
        if check_tasks:
            await asyncio.gather(*check_tasks, return_exceptions=True)
    
    async def _check_provider_health(self, provider_name: str):
        """Check health of a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return
        
        # Check circuit breaker state
        circuit_breaker = self.circuit_breakers[provider_name]
        if circuit_breaker["state"] == "open":
            # Check if it's time to attempt a half-open state
            if (circuit_breaker["next_attempt"] and 
                datetime.utcnow() >= circuit_breaker["next_attempt"]):
                circuit_breaker["state"] = "half_open"
                logger.info(f"Circuit breaker for {provider_name} moving to half-open state")
            else:
                # Still in open state, mark as unhealthy
                self._update_health_metrics(
                    provider_name, 
                    success=False, 
                    response_time=0.0, 
                    error="Circuit breaker open"
                )
                return
        
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            # Simple health check using the provider's health_check method
            if hasattr(provider, 'health_check'):
                health_result = await provider.health_check()
                success = health_result.get("status") == "healthy"
                if not success:
                    error_message = health_result.get("error", "Health check failed")
            else:
                # Fallback: try a simple test request
                test_request = GenerationRequest(
                    prompt="Test",
                    max_tokens=1,
                    temperature=0.0
                )
                
                # Get the first available model for this provider
                models = provider.get_available_models()
                if models:
                    test_model = models[0].model_id
                    response = await provider.generate_text(test_request, test_model)
                    success = not response.error
                    if not success:
                        error_message = response.error
                else:
                    success = False
                    error_message = "No models available"
        
        except asyncio.TimeoutError:
            error_message = "Health check timeout"
        except Exception as e:
            error_message = str(e)
        
        response_time = time.time() - start_time
        
        # Update circuit breaker state
        self._update_circuit_breaker(provider_name, success)
        
        # Update health metrics
        self._update_health_metrics(provider_name, success, response_time, error_message)
    
    def _update_circuit_breaker(self, provider_name: str, success: bool):
        """Update circuit breaker state for a provider"""
        circuit_breaker = self.circuit_breakers[provider_name]
        
        if success:
            if circuit_breaker["state"] == "half_open":
                # Success in half-open state, close the circuit
                circuit_breaker["state"] = "closed"
                circuit_breaker["failure_count"] = 0
                logger.info(f"Circuit breaker for {provider_name} closed")
            elif circuit_breaker["state"] == "closed":
                # Reset failure count on success
                circuit_breaker["failure_count"] = 0
        else:
            circuit_breaker["failure_count"] += 1
            circuit_breaker["last_failure"] = datetime.utcnow()
            
            if (circuit_breaker["state"] in ["closed", "half_open"] and 
                circuit_breaker["failure_count"] >= self.circuit_breaker_threshold):
                # Open the circuit breaker
                circuit_breaker["state"] = "open"
                circuit_breaker["next_attempt"] = (
                    datetime.utcnow() + timedelta(seconds=self.circuit_breaker_timeout)
                )
                logger.warning(f"Circuit breaker for {provider_name} opened due to {circuit_breaker['failure_count']} failures")
    
    def _update_health_metrics(self, provider_name: str, success: bool, response_time: float, error: Optional[str]):
        """Update health metrics for a provider"""
        metrics = self.health_metrics[provider_name]
        
        # Update basic metrics
        metrics.last_check = datetime.utcnow()
        metrics.response_time = response_time
        
        if success:
            metrics.consecutive_failures = 0
            metrics.last_error = None
        else:
            metrics.consecutive_failures += 1
            metrics.error_count += 1
            metrics.last_error = error
        
        # Determine health status
        if self.circuit_breakers[provider_name]["state"] == "open":
            metrics.status = HealthStatus.UNHEALTHY
        elif metrics.consecutive_failures == 0:
            if response_time <= 2.0:
                metrics.status = HealthStatus.HEALTHY
            elif response_time <= 10.0:
                metrics.status = HealthStatus.DEGRADED
            else:
                metrics.status = HealthStatus.DEGRADED
        elif metrics.consecutive_failures < self.failure_threshold:
            metrics.status = HealthStatus.DEGRADED
        else:
            metrics.status = HealthStatus.UNHEALTHY
        
        # Calculate success rate (over last 10 checks)
        # This is a simplified calculation - in production, you'd want to store a rolling window
        if metrics.consecutive_failures == 0:
            metrics.success_rate = min(1.0, metrics.success_rate + 0.1)
        else:
            metrics.success_rate = max(0.0, metrics.success_rate - 0.1)
        
        logger.debug(f"Updated health metrics for {provider_name}: {metrics.status.value}, {response_time:.2f}s")
    
    def get_provider_health(self, provider_name: str) -> Optional[HealthMetrics]:
        """Get health metrics for a specific provider"""
        return self.health_metrics.get(provider_name)
    
    def get_all_health_metrics(self) -> Dict[str, HealthMetrics]:
        """Get health metrics for all providers"""
        return self.health_metrics.copy()
    
    def get_healthy_providers(self) -> List[str]:
        """Get list of healthy provider names"""
        return [
            name for name, metrics in self.health_metrics.items()
            if metrics.status == HealthStatus.HEALTHY
        ]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available (healthy or degraded) provider names"""
        return [
            name for name, metrics in self.health_metrics.items()
            if metrics.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        ]
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available (not unhealthy)"""
        metrics = self.health_metrics.get(provider_name)
        if not metrics:
            return False
        
        return metrics.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    def get_circuit_breaker_status(self, provider_name: str) -> Dict[str, Any]:
        """Get circuit breaker status for a provider"""
        return self.circuit_breakers.get(provider_name, {}).copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health status across all providers"""
        total_providers = len(self.health_metrics)
        healthy_count = len([m for m in self.health_metrics.values() if m.status == HealthStatus.HEALTHY])
        degraded_count = len([m for m in self.health_metrics.values() if m.status == HealthStatus.DEGRADED])
        unhealthy_count = len([m for m in self.health_metrics.values() if m.status == HealthStatus.UNHEALTHY])
        
        avg_response_time = 0.0
        if self.health_metrics:
            avg_response_time = sum(m.response_time for m in self.health_metrics.values()) / len(self.health_metrics)
        
        return {
            "total_providers": total_providers,
            "healthy_providers": healthy_count,
            "degraded_providers": degraded_count,
            "unhealthy_providers": unhealthy_count,
            "availability_percentage": (healthy_count + degraded_count) / max(total_providers, 1) * 100,
            "avg_response_time": avg_response_time,
            "monitoring_active": self._running
        }