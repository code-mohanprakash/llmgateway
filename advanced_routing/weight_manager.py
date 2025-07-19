"""
Dynamic Provider Weight Management System
Implements adaptive weight calculation based on performance with exponential moving averages
"""

import asyncio
import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class WeightMetrics:
    """Comprehensive metrics for weight calculation"""
    provider_name: str
    base_weight: float
    current_weight: float
    performance_score: float
    availability_score: float
    cost_efficiency_score: float
    response_time_score: float
    success_rate_score: float
    load_balance_score: float
    trend_score: float
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'provider_name': self.provider_name,
            'base_weight': self.base_weight,
            'current_weight': self.current_weight,
            'performance_score': self.performance_score,
            'availability_score': self.availability_score,
            'cost_efficiency_score': self.cost_efficiency_score,
            'response_time_score': self.response_time_score,
            'success_rate_score': self.success_rate_score,
            'load_balance_score': self.load_balance_score,
            'trend_score': self.trend_score,
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class WeightAdjustmentEvent:
    """Event representing a weight adjustment"""
    provider_name: str
    old_weight: float
    new_weight: float
    adjustment_type: str  # 'performance', 'availability', 'cost', 'manual'
    trigger_reason: str
    adjustment_magnitude: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ExponentialMovingAverage:
    """Exponential Moving Average calculator for smooth weight adjustments"""
    
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha  # Smoothing factor (0-1)
        self.values: Dict[str, float] = {}
        self.initialized: Dict[str, bool] = {}
    
    def update(self, key: str, value: float) -> float:
        """Update EMA for a key and return new value"""
        if key not in self.initialized or not self.initialized[key]:
            self.values[key] = value
            self.initialized[key] = True
            return value
        
        # EMA formula: new_value = alpha * current_value + (1 - alpha) * previous_ema
        self.values[key] = self.alpha * value + (1 - self.alpha) * self.values[key]
        return self.values[key]
    
    def get_value(self, key: str) -> Optional[float]:
        """Get current EMA value for a key"""
        return self.values.get(key)
    
    def get_all_values(self) -> Dict[str, float]:
        """Get all current EMA values"""
        return self.values.copy()


class WeightManager:
    """
    Advanced weight management system with adaptive calculations and automatic rebalancing
    
    Features:
    - Exponential moving averages for smooth weight adjustments
    - Multi-factor weight calculation (performance, cost, availability, etc.)
    - Automatic rebalancing based on performance trends
    - Configurable adjustment triggers and thresholds
    - Weight adjustment history and analytics
    """
    
    def __init__(self, adjustment_interval: int = 60):
        self.adjustment_interval = adjustment_interval  # seconds
        self.provider_weights: Dict[str, WeightMetrics] = {}
        self.adjustment_history: List[WeightAdjustmentEvent] = []
        self.max_history_size = 1000
        
        # Exponential moving averages for different metrics
        self.response_time_ema = ExponentialMovingAverage(alpha=0.2)
        self.success_rate_ema = ExponentialMovingAverage(alpha=0.3)
        self.cost_ema = ExponentialMovingAverage(alpha=0.1)
        self.availability_ema = ExponentialMovingAverage(alpha=0.4)
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.last_adjustment_time = datetime.utcnow()
        
        # Configuration
        self.config = {
            'min_weight': 0.1,
            'max_weight': 10.0,
            'adjustment_sensitivity': 0.5,
            'rebalance_threshold': 0.3,
            'trend_window': 20,  # Number of data points for trend calculation
            'performance_weight': 0.3,
            'availability_weight': 0.25,
            'cost_weight': 0.2,
            'response_time_weight': 0.15,
            'load_balance_weight': 0.1
        }
        
        # Weight adjustment triggers
        self.triggers = {
            'performance_degradation': {'threshold': 0.2, 'enabled': True},
            'availability_drop': {'threshold': 0.15, 'enabled': True},
            'cost_increase': {'threshold': 0.25, 'enabled': True},
            'response_time_spike': {'threshold': 0.3, 'enabled': True},
            'success_rate_drop': {'threshold': 0.1, 'enabled': True},
            'load_imbalance': {'threshold': 0.4, 'enabled': True}
        }
        
        # Background task
        self.adjustment_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def start(self):
        """Start the weight adjustment background task"""
        if self.running:
            return
        
        self.running = True
        self.adjustment_task = asyncio.create_task(self._adjustment_loop())
        logger.info("Weight manager started")
    
    async def stop(self):
        """Stop the weight adjustment background task"""
        self.running = False
        if self.adjustment_task:
            self.adjustment_task.cancel()
            try:
                await self.adjustment_task
            except asyncio.CancelledError:
                pass
        logger.info("Weight manager stopped")
    
    async def _adjustment_loop(self):
        """Main weight adjustment loop"""
        while self.running:
            try:
                await self._perform_weight_adjustment()
                await asyncio.sleep(self.adjustment_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in weight adjustment loop: {str(e)}")
                await asyncio.sleep(self.adjustment_interval)
    
    def register_provider(self, provider_name: str, base_weight: float = 1.0):
        """Register a provider with the weight manager"""
        self.provider_weights[provider_name] = WeightMetrics(
            provider_name=provider_name,
            base_weight=base_weight,
            current_weight=base_weight,
            performance_score=0.5,
            availability_score=0.5,
            cost_efficiency_score=0.5,
            response_time_score=0.5,
            success_rate_score=0.5,
            load_balance_score=0.5,
            trend_score=0.5
        )
        logger.info(f"Registered provider {provider_name} with base weight {base_weight}")
    
    def unregister_provider(self, provider_name: str):
        """Unregister a provider from weight management"""
        if provider_name in self.provider_weights:
            del self.provider_weights[provider_name]
            if provider_name in self.performance_history:
                del self.performance_history[provider_name]
            logger.info(f"Unregistered provider {provider_name}")
    
    def record_performance(self, provider_name: str, response_time: float, 
                         success: bool, cost: float = 0.0, availability: float = 1.0):
        """Record performance data for a provider"""
        if provider_name not in self.provider_weights:
            return
        
        # Record in performance history
        performance_data = {
            'timestamp': datetime.utcnow(),
            'response_time': response_time,
            'success': success,
            'cost': cost,
            'availability': availability
        }
        
        self.performance_history[provider_name].append(performance_data)
        
        # Update EMAs
        self.response_time_ema.update(provider_name, response_time)
        self.success_rate_ema.update(provider_name, float(success))
        self.cost_ema.update(provider_name, cost)
        self.availability_ema.update(provider_name, availability)
        
        # Check for immediate adjustment triggers
        asyncio.create_task(self._check_immediate_triggers(provider_name))
    
    async def _check_immediate_triggers(self, provider_name: str):
        """Check for immediate weight adjustment triggers"""
        if provider_name not in self.provider_weights:
            return
        
        metrics = self.provider_weights[provider_name]
        recent_data = list(self.performance_history[provider_name])[-10:]  # Last 10 requests
        
        if len(recent_data) < 5:  # Need minimum data
            return
        
        # Calculate recent performance metrics
        recent_success_rate = sum(1 for d in recent_data if d['success']) / len(recent_data)
        recent_response_time = sum(d['response_time'] for d in recent_data) / len(recent_data)
        recent_availability = sum(d['availability'] for d in recent_data) / len(recent_data)
        
        # Check triggers
        adjustments_made = []
        
        # Performance degradation trigger
        if (self.triggers['performance_degradation']['enabled'] and 
            recent_success_rate < metrics.success_rate_score - self.triggers['performance_degradation']['threshold']):
            await self._adjust_weight(provider_name, 'performance_degradation', 
                                    f"Success rate dropped to {recent_success_rate:.2%}")
            adjustments_made.append('performance_degradation')
        
        # Availability drop trigger
        if (self.triggers['availability_drop']['enabled'] and 
            recent_availability < metrics.availability_score - self.triggers['availability_drop']['threshold']):
            await self._adjust_weight(provider_name, 'availability_drop',
                                    f"Availability dropped to {recent_availability:.2%}")
            adjustments_made.append('availability_drop')
        
        # Response time spike trigger
        if (self.triggers['response_time_spike']['enabled'] and 
            recent_response_time > metrics.response_time_score * (1 + self.triggers['response_time_spike']['threshold'])):
            await self._adjust_weight(provider_name, 'response_time_spike',
                                    f"Response time spiked to {recent_response_time:.2f}s")
            adjustments_made.append('response_time_spike')
        
        if adjustments_made:
            logger.info(f"Immediate weight adjustments for {provider_name}: {adjustments_made}")
    
    async def _perform_weight_adjustment(self):
        """Perform comprehensive weight adjustment for all providers"""
        if not self.provider_weights:
            return
        
        logger.debug("Performing weight adjustment cycle")
        
        # Calculate scores for all providers
        for provider_name in self.provider_weights.keys():
            await self._calculate_provider_scores(provider_name)
        
        # Perform rebalancing if needed
        await self._rebalance_weights()
        
        self.last_adjustment_time = datetime.utcnow()
    
    async def _calculate_provider_scores(self, provider_name: str):
        """Calculate comprehensive scores for a provider"""
        if provider_name not in self.provider_weights:
            return
        
        metrics = self.provider_weights[provider_name]
        history = list(self.performance_history[provider_name])
        
        if len(history) < 3:  # Need minimum data
            return
        
        # Calculate individual scores
        response_time_score = self._calculate_response_time_score(provider_name, history)
        success_rate_score = self._calculate_success_rate_score(provider_name, history)
        availability_score = self._calculate_availability_score(provider_name, history)
        cost_efficiency_score = self._calculate_cost_efficiency_score(provider_name, history)
        load_balance_score = self._calculate_load_balance_score(provider_name)
        trend_score = self._calculate_trend_score(provider_name, history)
        
        # Calculate composite performance score
        performance_score = (
            response_time_score * self.config['response_time_weight'] +
            success_rate_score * self.config['performance_weight'] +
            availability_score * self.config['availability_weight'] +
            cost_efficiency_score * self.config['cost_weight'] +
            load_balance_score * self.config['load_balance_weight']
        )
        
        # Update metrics
        metrics.performance_score = performance_score
        metrics.response_time_score = response_time_score
        metrics.success_rate_score = success_rate_score
        metrics.availability_score = availability_score
        metrics.cost_efficiency_score = cost_efficiency_score
        metrics.load_balance_score = load_balance_score
        metrics.trend_score = trend_score
        
        # Calculate new weight
        old_weight = metrics.current_weight
        new_weight = self._calculate_new_weight(metrics, trend_score)
        
        # Apply weight with bounds checking
        new_weight = max(self.config['min_weight'], min(self.config['max_weight'], new_weight))
        
        # Update weight if significant change
        if abs(new_weight - old_weight) > 0.05:  # 5% threshold
            await self._update_provider_weight(provider_name, old_weight, new_weight, 'performance')
    
    def _calculate_response_time_score(self, provider_name: str, history: List[Dict]) -> float:
        """Calculate response time score (0-1, higher is better)"""
        if not history:
            return 0.5
        
        # Use EMA for smooth score calculation
        ema_response_time = self.response_time_ema.get_value(provider_name)
        if ema_response_time is None:
            return 0.5
        
        # Score inversely related to response time (lower time = higher score)
        # Normalize to reasonable range (0.5s - 10s)
        normalized_time = max(0.5, min(10.0, ema_response_time))
        score = 1.0 - ((normalized_time - 0.5) / 9.5)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_success_rate_score(self, provider_name: str, history: List[Dict]) -> float:
        """Calculate success rate score (0-1, higher is better)"""
        ema_success_rate = self.success_rate_ema.get_value(provider_name)
        if ema_success_rate is None:
            return 0.5
        
        return max(0.0, min(1.0, ema_success_rate))
    
    def _calculate_availability_score(self, provider_name: str, history: List[Dict]) -> float:
        """Calculate availability score (0-1, higher is better)"""
        ema_availability = self.availability_ema.get_value(provider_name)
        if ema_availability is None:
            return 0.5
        
        return max(0.0, min(1.0, ema_availability))
    
    def _calculate_cost_efficiency_score(self, provider_name: str, history: List[Dict]) -> float:
        """Calculate cost efficiency score (0-1, higher is better)"""
        ema_cost = self.cost_ema.get_value(provider_name)
        if ema_cost is None:
            return 0.5
        
        # All providers cost comparison
        all_costs = [self.cost_ema.get_value(p) for p in self.provider_weights.keys()]
        all_costs = [c for c in all_costs if c is not None]
        
        if len(all_costs) <= 1:
            return 0.5
        
        # Score inversely related to cost (lower cost = higher score)
        min_cost = min(all_costs)
        max_cost = max(all_costs)
        
        if max_cost == min_cost:
            return 0.5
        
        # Normalize cost to 0-1 range (inverted)
        normalized_cost = (ema_cost - min_cost) / (max_cost - min_cost)
        score = 1.0 - normalized_cost
        
        return max(0.0, min(1.0, score))
    
    def _calculate_load_balance_score(self, provider_name: str) -> float:
        """Calculate load balance score (0-1, higher is better for balanced load)"""
        if len(self.provider_weights) <= 1:
            return 1.0
        
        # Calculate request distribution
        total_requests = sum(len(self.performance_history[p]) for p in self.provider_weights.keys())
        if total_requests == 0:
            return 0.5
        
        provider_requests = len(self.performance_history[provider_name])
        expected_share = 1.0 / len(self.provider_weights)
        actual_share = provider_requests / total_requests
        
        # Score based on how close to expected share
        deviation = abs(actual_share - expected_share)
        score = max(0.0, 1.0 - (deviation / expected_share))
        
        return score
    
    def _calculate_trend_score(self, provider_name: str, history: List[Dict]) -> float:
        """Calculate trend score based on recent performance trend"""
        if len(history) < self.config['trend_window']:
            return 0.5
        
        # Use recent data for trend calculation
        recent_data = history[-self.config['trend_window']:]
        
        # Calculate trend for success rate
        success_rates = [float(d['success']) for d in recent_data]
        success_trend = self._calculate_linear_trend(success_rates)
        
        # Calculate trend for response time (inverted - lower is better)
        response_times = [d['response_time'] for d in recent_data]
        response_time_trend = -self._calculate_linear_trend(response_times)
        
        # Combine trends
        trend_score = 0.5 + (success_trend + response_time_trend) / 4.0
        
        return max(0.0, min(1.0, trend_score))
    
    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend (-1 to 1, positive means improving)"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate correlation coefficient
        mean_x = sum(x) / n
        mean_y = sum(values) / n
        
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denominator_y = sum((values[i] - mean_y) ** 2 for i in range(n))
        
        if denominator_x == 0 or denominator_y == 0:
            return 0.0
        
        correlation = numerator / (math.sqrt(denominator_x) * math.sqrt(denominator_y))
        
        return max(-1.0, min(1.0, correlation))
    
    def _calculate_new_weight(self, metrics: WeightMetrics, trend_score: float) -> float:
        """Calculate new weight based on all metrics"""
        # Base weight adjustment
        performance_factor = metrics.performance_score
        trend_factor = 0.8 + (trend_score * 0.4)  # 0.8 to 1.2 range
        
        # Calculate new weight
        new_weight = metrics.base_weight * performance_factor * trend_factor
        
        # Apply sensitivity
        adjustment = (new_weight - metrics.current_weight) * self.config['adjustment_sensitivity']
        final_weight = metrics.current_weight + adjustment
        
        return final_weight
    
    async def _update_provider_weight(self, provider_name: str, old_weight: float, 
                                    new_weight: float, adjustment_type: str):
        """Update provider weight and record the change"""
        if provider_name not in self.provider_weights:
            return
        
        metrics = self.provider_weights[provider_name]
        metrics.current_weight = new_weight
        metrics.last_updated = datetime.utcnow()
        
        # Record adjustment event
        event = WeightAdjustmentEvent(
            provider_name=provider_name,
            old_weight=old_weight,
            new_weight=new_weight,
            adjustment_type=adjustment_type,
            trigger_reason=f"Weight adjusted from {old_weight:.3f} to {new_weight:.3f}",
            adjustment_magnitude=abs(new_weight - old_weight)
        )
        
        self.adjustment_history.append(event)
        
        # Keep history size manageable
        if len(self.adjustment_history) > self.max_history_size:
            self.adjustment_history.pop(0)
        
        logger.info(f"Weight adjusted for {provider_name}: {old_weight:.3f} -> {new_weight:.3f} ({adjustment_type})")
    
    async def _adjust_weight(self, provider_name: str, trigger_type: str, reason: str):
        """Perform immediate weight adjustment based on trigger"""
        if provider_name not in self.provider_weights:
            return
        
        metrics = self.provider_weights[provider_name]
        old_weight = metrics.current_weight
        
        # Apply trigger-specific adjustment
        if trigger_type == 'performance_degradation':
            new_weight = old_weight * 0.8  # 20% reduction
        elif trigger_type == 'availability_drop':
            new_weight = old_weight * 0.7  # 30% reduction
        elif trigger_type == 'response_time_spike':
            new_weight = old_weight * 0.9  # 10% reduction
        else:
            new_weight = old_weight * 0.85  # Default 15% reduction
        
        new_weight = max(self.config['min_weight'], min(self.config['max_weight'], new_weight))
        
        await self._update_provider_weight(provider_name, old_weight, new_weight, trigger_type)
    
    async def _rebalance_weights(self):
        """Perform global weight rebalancing if needed"""
        if len(self.provider_weights) < 2:
            return
        
        # Calculate current weight distribution
        total_weight = sum(metrics.current_weight for metrics in self.provider_weights.values())
        weight_distribution = {
            name: metrics.current_weight / total_weight
            for name, metrics in self.provider_weights.items()
        }
        
        # Check if rebalancing is needed
        expected_weight = 1.0 / len(self.provider_weights)
        max_deviation = max(abs(weight - expected_weight) for weight in weight_distribution.values())
        
        if max_deviation > self.config['rebalance_threshold']:
            logger.info(f"Rebalancing weights - max deviation: {max_deviation:.3f}")
            
            # Perform gentle rebalancing
            for provider_name, metrics in self.provider_weights.items():
                current_share = weight_distribution[provider_name]
                adjustment_factor = 1.0 + (expected_weight - current_share) * 0.1  # 10% adjustment
                
                old_weight = metrics.current_weight
                new_weight = old_weight * adjustment_factor
                new_weight = max(self.config['min_weight'], min(self.config['max_weight'], new_weight))
                
                if abs(new_weight - old_weight) > 0.01:  # 1% threshold
                    await self._update_provider_weight(provider_name, old_weight, new_weight, 'rebalance')
    
    def get_provider_weights(self) -> Dict[str, WeightMetrics]:
        """Get all provider weight metrics"""
        return {name: metrics for name, metrics in self.provider_weights.items()}
    
    def get_weight_history(self, provider_name: Optional[str] = None) -> List[WeightAdjustmentEvent]:
        """Get weight adjustment history"""
        if provider_name:
            return [event for event in self.adjustment_history if event.provider_name == provider_name]
        return self.adjustment_history.copy()
    
    def get_weight_analytics(self) -> Dict[str, Any]:
        """Get comprehensive weight management analytics"""
        current_time = datetime.utcnow()
        
        # Calculate statistics
        total_adjustments = len(self.adjustment_history)
        recent_adjustments = [
            event for event in self.adjustment_history
            if (current_time - event.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        adjustment_types = {}
        for event in self.adjustment_history:
            adjustment_types[event.adjustment_type] = adjustment_types.get(event.adjustment_type, 0) + 1
        
        # Provider statistics
        provider_stats = {}
        for name, metrics in self.provider_weights.items():
            provider_stats[name] = {
                'current_weight': metrics.current_weight,
                'base_weight': metrics.base_weight,
                'weight_ratio': metrics.current_weight / metrics.base_weight,
                'performance_score': metrics.performance_score,
                'last_updated': metrics.last_updated.isoformat(),
                'adjustment_count': len([e for e in self.adjustment_history if e.provider_name == name])
            }
        
        return {
            'total_adjustments': total_adjustments,
            'recent_adjustments': len(recent_adjustments),
            'adjustment_types': adjustment_types,
            'provider_stats': provider_stats,
            'configuration': self.config.copy(),
            'triggers': self.triggers.copy(),
            'last_adjustment_time': self.last_adjustment_time.isoformat(),
            'ema_values': {
                'response_time': self.response_time_ema.get_all_values(),
                'success_rate': self.success_rate_ema.get_all_values(),
                'cost': self.cost_ema.get_all_values(),
                'availability': self.availability_ema.get_all_values()
            }
        }
    
    def update_configuration(self, new_config: Dict[str, Any]):
        """Update weight manager configuration"""
        self.config.update(new_config)
        logger.info(f"Weight manager configuration updated: {new_config}")
    
    def update_triggers(self, new_triggers: Dict[str, Dict[str, Any]]):
        """Update weight adjustment triggers"""
        self.triggers.update(new_triggers)
        logger.info(f"Weight adjustment triggers updated: {new_triggers}")
    
    def export_weights(self, filepath: str):
        """Export weight data to file"""
        try:
            export_data = {
                'provider_weights': {
                    name: metrics.to_dict() 
                    for name, metrics in self.provider_weights.items()
                },
                'adjustment_history': [
                    {
                        'provider_name': event.provider_name,
                        'old_weight': event.old_weight,
                        'new_weight': event.new_weight,
                        'adjustment_type': event.adjustment_type,
                        'trigger_reason': event.trigger_reason,
                        'adjustment_magnitude': event.adjustment_magnitude,
                        'timestamp': event.timestamp.isoformat()
                    }
                    for event in self.adjustment_history
                ],
                'configuration': self.config,
                'triggers': self.triggers,
                'export_timestamp': datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Weight data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting weight data: {str(e)}")


# Global weight manager instance
weight_manager = WeightManager()