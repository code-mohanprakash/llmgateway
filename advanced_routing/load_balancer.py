"""
Advanced Load Balancer with Real-time Health Monitoring
Implements weighted round-robin with real-time performance adjustment
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from providers.base import BaseModelProvider, GenerationRequest, GenerationResponse
from .health_monitor import HealthMonitor, HealthStatus

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    INTELLIGENT = "intelligent"


@dataclass
class ProviderWeight:
    """Weight configuration for a provider"""
    provider_name: str
    base_weight: float = 1.0
    current_weight: float = 1.0
    performance_multiplier: float = 1.0
    health_multiplier: float = 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConnectionPool:
    """Connection pool metrics for a provider"""
    active_connections: int = 0
    total_connections: int = 0
    max_connections: int = 100
    
    def can_accept_connection(self) -> bool:
        """Check if provider can accept a new connection"""
        return self.active_connections < self.max_connections
    
    def acquire_connection(self) -> bool:
        """Acquire a connection from the pool"""
        if self.can_accept_connection():
            self.active_connections += 1
            return True
        return False
    
    def release_connection(self):
        """Release a connection back to the pool"""
        if self.active_connections > 0:
            self.active_connections -= 1


class LoadBalancer:
    """
    Advanced load balancer with real-time health monitoring and performance optimization
    
    Features:
    - Weighted round-robin with dynamic weight adjustment
    - Real-time performance-based routing
    - Connection pooling management
    - Health-aware request distribution
    - Intelligent fallback strategies
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT):
        self.strategy = strategy
        self.providers: Dict[str, BaseModelProvider] = {}
        self.provider_weights: Dict[str, ProviderWeight] = {}
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.health_monitor = HealthMonitor()
        
        # Round-robin state
        self.round_robin_index = 0
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.weight_adjustment_interval = 60  # seconds
        self.last_weight_adjustment = datetime.utcnow()
        
        # Connection management
        self.max_connections_per_provider = 100
        self.connection_timeout = 30.0
        
        # Intelligent routing parameters
        self.response_time_weight = 0.3
        self.success_rate_weight = 0.4
        self.cost_weight = 0.2
        self.availability_weight = 0.1
    
    async def initialize(self):
        """Initialize the load balancer"""
        await self.health_monitor.start_monitoring()
        logger.info("Load balancer initialized")
    
    async def shutdown(self):
        """Shutdown the load balancer"""
        await self.health_monitor.stop_monitoring()
        logger.info("Load balancer shutdown")
    
    def register_provider(self, name: str, provider: BaseModelProvider, base_weight: float = 1.0):
        """Register a provider with the load balancer"""
        self.providers[name] = provider
        self.provider_weights[name] = ProviderWeight(
            provider_name=name,
            base_weight=base_weight,
            current_weight=base_weight
        )
        self.connection_pools[name] = ConnectionPool(max_connections=self.max_connections_per_provider)
        self.performance_history[name] = []
        
        # Register with health monitor
        self.health_monitor.register_provider(name, provider)
        
        logger.info(f"Registered provider {name} with base weight {base_weight}")
    
    def unregister_provider(self, name: str):
        """Unregister a provider from the load balancer"""
        if name in self.providers:
            del self.providers[name]
            del self.provider_weights[name]
            del self.connection_pools[name]
            del self.performance_history[name]
            
            # Unregister from health monitor
            self.health_monitor.unregister_provider(name)
            
            logger.info(f"Unregistered provider {name}")
    
    async def select_provider(self, request_characteristics: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Select the optimal provider based on the configured strategy
        
        Args:
            request_characteristics: Optional request characteristics for intelligent routing
            
        Returns:
            Provider name or None if no providers available
        """
        available_providers = self._get_available_providers()
        if not available_providers:
            logger.warning("No available providers for request")
            return None
        
        # Update weights if needed
        await self._update_weights_if_needed()
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_providers)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_providers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_providers)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_selection(available_providers)
        elif self.strategy == LoadBalancingStrategy.INTELLIGENT:
            return self._intelligent_selection(available_providers, request_characteristics)
        else:
            # Default to weighted round-robin
            return self._weighted_round_robin_selection(available_providers)
    
    def _get_available_providers(self) -> List[str]:
        """Get list of available providers based on health status"""
        available = []
        for provider_name in self.providers.keys():
            # Check health status
            if self.health_monitor.is_provider_available(provider_name):
                # Check connection pool availability
                if self.connection_pools[provider_name].can_accept_connection():
                    available.append(provider_name)
        
        return available
    
    def _round_robin_selection(self, available_providers: List[str]) -> str:
        """Simple round-robin selection"""
        if not available_providers:
            return None
        
        # Ensure index is within bounds
        self.round_robin_index = self.round_robin_index % len(available_providers)
        selected = available_providers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(available_providers)
        
        return selected
    
    def _weighted_round_robin_selection(self, available_providers: List[str]) -> str:
        """Weighted round-robin selection based on current weights"""
        if not available_providers:
            return None
        
        # Calculate total weight
        total_weight = sum(
            self.provider_weights[name].current_weight 
            for name in available_providers
        )
        
        if total_weight <= 0:
            # Fallback to simple round-robin
            return self._round_robin_selection(available_providers)
        
        # Generate random number and select based on weight
        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for provider_name in available_providers:
            cumulative_weight += self.provider_weights[provider_name].current_weight
            if random_value <= cumulative_weight:
                return provider_name
        
        # Fallback to last provider
        return available_providers[-1]
    
    def _least_connections_selection(self, available_providers: List[str]) -> str:
        """Select provider with least active connections"""
        if not available_providers:
            return None
        
        min_connections = float('inf')
        selected_provider = None
        
        for provider_name in available_providers:
            connections = self.connection_pools[provider_name].active_connections
            if connections < min_connections:
                min_connections = connections
                selected_provider = provider_name
        
        return selected_provider
    
    def _response_time_selection(self, available_providers: List[str]) -> str:
        """Select provider with best average response time"""
        if not available_providers:
            return None
        
        best_response_time = float('inf')
        selected_provider = None
        
        for provider_name in available_providers:
            health_metrics = self.health_monitor.get_provider_health(provider_name)
            if health_metrics and health_metrics.response_time < best_response_time:
                best_response_time = health_metrics.response_time
                selected_provider = provider_name
        
        return selected_provider or available_providers[0]
    
    def _intelligent_selection(self, available_providers: List[str], characteristics: Optional[Dict[str, Any]]) -> str:
        """Intelligent provider selection based on multiple factors"""
        if not available_providers:
            return None
        
        provider_scores = {}
        
        for provider_name in available_providers:
            score = self._calculate_provider_score(provider_name, characteristics)
            provider_scores[provider_name] = score
        
        # Select provider with highest score
        best_provider = max(provider_scores.items(), key=lambda x: x[1])
        return best_provider[0]
    
    def _calculate_provider_score(self, provider_name: str, characteristics: Optional[Dict[str, Any]]) -> float:
        """Calculate composite score for a provider based on multiple factors"""
        score = 0.0
        
        # Health metrics
        health_metrics = self.health_monitor.get_provider_health(provider_name)
        if health_metrics:
            # Response time score (lower is better)
            response_time_score = max(0, 100 - health_metrics.response_time * 10)
            score += response_time_score * self.response_time_weight
            
            # Success rate score
            success_rate_score = health_metrics.success_rate * 100
            score += success_rate_score * self.success_rate_weight
            
            # Availability score
            if health_metrics.status == HealthStatus.HEALTHY:
                availability_score = 100
            elif health_metrics.status == HealthStatus.DEGRADED:
                availability_score = 70
            else:
                availability_score = 0
            score += availability_score * self.availability_weight
        
        # Connection pool availability
        pool = self.connection_pools[provider_name]
        pool_utilization = pool.active_connections / pool.max_connections
        pool_score = max(0, 100 - pool_utilization * 100)
        score += pool_score * 0.1
        
        # Performance weight multiplier
        weight = self.provider_weights[provider_name]
        score *= weight.performance_multiplier * weight.health_multiplier
        
        # Request characteristics adjustment
        if characteristics:
            score = self._adjust_score_for_characteristics(score, provider_name, characteristics)
        
        return score
    
    def _adjust_score_for_characteristics(self, base_score: float, provider_name: str, characteristics: Dict[str, Any]) -> float:
        """Adjust provider score based on request characteristics"""
        adjusted_score = base_score
        
        # Complexity-based adjustments
        complexity = characteristics.get("complexity", "medium")
        if complexity == "simple":
            # Prefer faster, cheaper providers for simple tasks
            if provider_name in ["groq", "google"]:
                adjusted_score *= 1.2
        elif complexity == "complex":
            # Prefer high-quality providers for complex tasks
            if provider_name in ["anthropic", "openai"]:
                adjusted_score *= 1.3
        
        # Cost sensitivity adjustments
        cost_sensitivity = characteristics.get("cost_sensitivity", "medium")
        if cost_sensitivity == "high":
            # Prefer cheaper providers
            if provider_name in ["ollama", "groq"]:
                adjusted_score *= 1.4
        elif cost_sensitivity == "low":
            # Quality over cost
            if provider_name in ["anthropic", "openai"]:
                adjusted_score *= 1.2
        
        # Urgency adjustments
        urgency = characteristics.get("urgency", "normal")
        if urgency == "high":
            # Prefer fastest providers
            health_metrics = self.health_monitor.get_provider_health(provider_name)
            if health_metrics and health_metrics.response_time < 2.0:
                adjusted_score *= 1.3
        
        return adjusted_score
    
    async def _update_weights_if_needed(self):
        """Update provider weights based on performance if enough time has passed"""
        now = datetime.utcnow()
        if (now - self.last_weight_adjustment).total_seconds() < self.weight_adjustment_interval:
            return
        
        self.last_weight_adjustment = now
        
        for provider_name in self.providers.keys():
            await self._update_provider_weight(provider_name)
    
    async def _update_provider_weight(self, provider_name: str):
        """Update weight for a specific provider based on performance"""
        weight = self.provider_weights[provider_name]
        health_metrics = self.health_monitor.get_provider_health(provider_name)
        
        if not health_metrics:
            return
        
        # Calculate performance multiplier based on success rate and response time
        success_rate_factor = health_metrics.success_rate
        response_time_factor = max(0.1, min(2.0, 2.0 / max(1.0, health_metrics.response_time)))
        
        weight.performance_multiplier = (success_rate_factor + response_time_factor) / 2
        
        # Calculate health multiplier
        if health_metrics.status == HealthStatus.HEALTHY:
            weight.health_multiplier = 1.0
        elif health_metrics.status == HealthStatus.DEGRADED:
            weight.health_multiplier = 0.7
        else:
            weight.health_multiplier = 0.1
        
        # Update current weight
        weight.current_weight = (
            weight.base_weight * 
            weight.performance_multiplier * 
            weight.health_multiplier
        )
        
        weight.last_updated = datetime.utcnow()
        
        logger.debug(f"Updated weight for {provider_name}: {weight.current_weight:.2f}")
    
    async def execute_request(self, provider_name: str, request: GenerationRequest, model_id: str, method_name: str) -> GenerationResponse:
        """Execute a request through the selected provider with connection management"""
        pool = self.connection_pools[provider_name]
        
        # Acquire connection
        if not pool.acquire_connection():
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=provider_name,
                error="Provider connection pool exhausted"
            )
        
        try:
            provider = self.providers[provider_name]
            method = getattr(provider, method_name)
            
            # Execute request
            start_time = time.time()
            response = await method(request, model_id)
            execution_time = time.time() - start_time
            
            # Record performance data
            self._record_performance_data(provider_name, execution_time, not response.error)
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing request on {provider_name}: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=provider_name,
                error=str(e)
            )
        finally:
            # Always release connection
            pool.release_connection()
    
    def _record_performance_data(self, provider_name: str, execution_time: float, success: bool):
        """Record performance data for analytics"""
        performance_record = {
            "timestamp": datetime.utcnow(),
            "execution_time": execution_time,
            "success": success
        }
        
        # Keep only recent records (last 100)
        history = self.performance_history[provider_name]
        history.append(performance_record)
        if len(history) > 100:
            history.pop(0)
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        stats = {
            "strategy": self.strategy.value,
            "total_providers": len(self.providers),
            "available_providers": len(self._get_available_providers()),
            "provider_weights": {
                name: {
                    "base_weight": weight.base_weight,
                    "current_weight": weight.current_weight,
                    "performance_multiplier": weight.performance_multiplier,
                    "health_multiplier": weight.health_multiplier
                }
                for name, weight in self.provider_weights.items()
            },
            "connection_pools": {
                name: {
                    "active_connections": pool.active_connections,
                    "max_connections": pool.max_connections,
                    "utilization": pool.active_connections / pool.max_connections
                }
                for name, pool in self.connection_pools.items()
            },
            "health_summary": self.health_monitor.get_health_summary()
        }
        
        return stats
    
    def get_provider_performance_history(self, provider_name: str) -> List[Dict[str, Any]]:
        """Get performance history for a specific provider"""
        return self.performance_history.get(provider_name, []).copy()
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """Change the load balancing strategy"""
        self.strategy = strategy
        logger.info(f"Load balancing strategy changed to {strategy.value}")
    
    def update_provider_weight(self, provider_name: str, new_weight: float):
        """Manually update a provider's base weight"""
        if provider_name in self.provider_weights:
            weight = self.provider_weights[provider_name]
            weight.base_weight = new_weight
            weight.current_weight = new_weight * weight.performance_multiplier * weight.health_multiplier
            weight.last_updated = datetime.utcnow()
            logger.info(f"Updated base weight for {provider_name} to {new_weight}")