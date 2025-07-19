"""
Cache Optimizer - Phase 2.3: Cost-aware Caching
Optimizes cache settings and policies based on usage patterns and cost analysis.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics
from collections import defaultdict

from .cost_cache import CostCache, CacheEntry, CacheMetrics, CacheStrategy

logger = logging.getLogger(__name__)


class OptimizationGoal(Enum):
    """Optimization goals for cache tuning."""
    MAXIMIZE_SAVINGS = "maximize_savings"
    MINIMIZE_STORAGE = "minimize_storage"
    BALANCE_COST_STORAGE = "balance_cost_storage"
    MAXIMIZE_HIT_RATE = "maximize_hit_rate"
    MAXIMIZE_QUALITY = "maximize_quality"


@dataclass
class OptimizationRecommendation:
    """Recommendation for cache optimization."""
    parameter: str
    current_value: Any
    recommended_value: Any
    expected_improvement: float
    confidence: float
    reasoning: str
    impact_estimate: Dict[str, float]


@dataclass
class CacheAnalysis:
    """Analysis of cache performance."""
    hit_rate: float
    cost_savings: float
    storage_efficiency: float
    quality_score: float
    access_patterns: Dict[str, Any]
    model_performance: Dict[str, Any]
    provider_performance: Dict[str, Any]
    recommendations: List[OptimizationRecommendation]


@dataclass
class AccessPattern:
    """Pattern analysis for cache access."""
    model_id: str
    provider: str
    access_frequency: float
    average_cost: float
    quality_score: float
    cache_hit_rate: float
    time_distribution: Dict[str, float]  # Hour -> access percentage
    seasonal_patterns: Dict[str, float]  # Day -> access multiplier


class CacheOptimizer:
    """
    Advanced cache optimization with machine learning insights.
    
    Chain of thought:
    1. Analyze cache access patterns and performance
    2. Identify optimization opportunities
    3. Recommend parameter adjustments
    4. Predict impact of changes
    5. Implement adaptive tuning
    """
    
    def __init__(self, cache: CostCache):
        """Initialize cache optimizer."""
        self.logger = logging.getLogger(__name__)
        self.cache = cache
        
        # Analysis history
        self.analysis_history: List[CacheAnalysis] = []
        
        # Pattern tracking
        self.access_patterns: Dict[str, AccessPattern] = {}
        self.optimization_history: List[OptimizationRecommendation] = []
        
        # Optimization settings
        self.optimization_interval = 3600  # Optimize every hour
        self.min_data_points = 100  # Minimum requests for analysis
        
        # Performance targets
        self.target_hit_rate = 0.6
        self.target_storage_efficiency = 0.8
        self.target_quality_score = 0.85
        
        self.logger.info("CacheOptimizer initialized")
    
    async def analyze_cache_performance(self) -> CacheAnalysis:
        """
        Analyze current cache performance and generate recommendations.
        
        Returns:
            CacheAnalysis with performance metrics and recommendations
        """
        try:
            # Get current metrics
            metrics = self.cache.get_cache_stats()
            
            # Analyze access patterns
            access_patterns = self._analyze_access_patterns()
            
            # Analyze model performance
            model_performance = self._analyze_model_performance()
            
            # Analyze provider performance
            provider_performance = self._analyze_provider_performance()
            
            # Calculate quality score
            quality_score = self._calculate_overall_quality_score()
            
            # Calculate storage efficiency
            storage_efficiency = self._calculate_storage_efficiency(metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                metrics, access_patterns, model_performance, provider_performance
            )
            
            analysis = CacheAnalysis(
                hit_rate=metrics.hit_rate,
                cost_savings=metrics.net_savings,
                storage_efficiency=storage_efficiency,
                quality_score=quality_score,
                access_patterns=access_patterns,
                model_performance=model_performance,
                provider_performance=provider_performance,
                recommendations=recommendations
            )
            
            # Store in history
            self.analysis_history.append(analysis)
            
            self.logger.info(f"Cache analysis complete: hit_rate={metrics.hit_rate:.2%}, savings=${metrics.net_savings:.2f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing cache performance: {str(e)}")
            raise
    
    def _analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns across models and providers."""
        patterns = {
            "hourly_distribution": defaultdict(int),
            "model_distribution": defaultdict(int),
            "provider_distribution": defaultdict(int),
            "cost_distribution": defaultdict(list),
            "quality_distribution": defaultdict(list)
        }
        
        for entry in self.cache.cache.values():
            # Hourly distribution
            hour = entry.last_accessed.hour
            patterns["hourly_distribution"][hour] += entry.access_count
            
            # Model distribution
            patterns["model_distribution"][entry.model_id] += entry.access_count
            
            # Provider distribution
            patterns["provider_distribution"][entry.provider] += entry.access_count
            
            # Cost distribution
            patterns["cost_distribution"][entry.model_id].append(entry.original_cost)
            
            # Quality distribution
            patterns["quality_distribution"][entry.model_id].append(entry.quality_score)
        
        # Calculate averages
        for model_id, costs in patterns["cost_distribution"].items():
            if costs:
                patterns["cost_distribution"][model_id] = statistics.mean(costs)
        
        for model_id, qualities in patterns["quality_distribution"].items():
            if qualities:
                patterns["quality_distribution"][model_id] = statistics.mean(qualities)
        
        return dict(patterns)
    
    def _analyze_model_performance(self) -> Dict[str, Any]:
        """Analyze performance by model."""
        model_stats = defaultdict(lambda: {
            "requests": 0,
            "hits": 0,
            "total_cost": 0.0,
            "total_savings": 0.0,
            "avg_quality": 0.0,
            "quality_samples": []
        })
        
        for entry in self.cache.cache.values():
            stats = model_stats[entry.model_id]
            stats["requests"] += entry.access_count
            stats["hits"] += entry.access_count
            stats["total_cost"] += entry.original_cost
            stats["total_savings"] += entry.cumulative_savings
            stats["quality_samples"].append(entry.quality_score)
        
        # Calculate averages and metrics
        for model_id, stats in model_stats.items():
            if stats["quality_samples"]:
                stats["avg_quality"] = statistics.mean(stats["quality_samples"])
                del stats["quality_samples"]
            
            if stats["requests"] > 0:
                stats["hit_rate"] = stats["hits"] / stats["requests"]
                stats["avg_cost"] = stats["total_cost"] / stats["requests"]
                stats["savings_per_request"] = stats["total_savings"] / stats["requests"]
            else:
                stats["hit_rate"] = 0.0
                stats["avg_cost"] = 0.0
                stats["savings_per_request"] = 0.0
        
        return dict(model_stats)
    
    def _analyze_provider_performance(self) -> Dict[str, Any]:
        """Analyze performance by provider."""
        provider_stats = defaultdict(lambda: {
            "requests": 0,
            "hits": 0,
            "total_cost": 0.0,
            "total_savings": 0.0,
            "avg_quality": 0.0,
            "quality_samples": []
        })
        
        for entry in self.cache.cache.values():
            stats = provider_stats[entry.provider]
            stats["requests"] += entry.access_count
            stats["hits"] += entry.access_count
            stats["total_cost"] += entry.original_cost
            stats["total_savings"] += entry.cumulative_savings
            stats["quality_samples"].append(entry.quality_score)
        
        # Calculate averages and metrics
        for provider, stats in provider_stats.items():
            if stats["quality_samples"]:
                stats["avg_quality"] = statistics.mean(stats["quality_samples"])
                del stats["quality_samples"]
            
            if stats["requests"] > 0:
                stats["hit_rate"] = stats["hits"] / stats["requests"]
                stats["avg_cost"] = stats["total_cost"] / stats["requests"]
                stats["savings_per_request"] = stats["total_savings"] / stats["requests"]
            else:
                stats["hit_rate"] = 0.0
                stats["avg_cost"] = 0.0
                stats["savings_per_request"] = 0.0
        
        return dict(provider_stats)
    
    def _calculate_overall_quality_score(self) -> float:
        """Calculate overall quality score of cached responses."""
        if not self.cache.cache:
            return 0.0
        
        quality_scores = [entry.quality_score for entry in self.cache.cache.values()]
        return statistics.mean(quality_scores)
    
    def _calculate_storage_efficiency(self, metrics: CacheMetrics) -> float:
        """Calculate storage efficiency (savings per unit of storage cost)."""
        if metrics.storage_cost == 0:
            return 1.0
        
        return metrics.net_savings / metrics.storage_cost if metrics.storage_cost > 0 else 0.0
    
    async def _generate_recommendations(
        self,
        metrics: CacheMetrics,
        access_patterns: Dict[str, Any],
        model_performance: Dict[str, Any],
        provider_performance: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # 1. Cache size optimization
        size_rec = self._recommend_cache_size(metrics, access_patterns)
        if size_rec:
            recommendations.append(size_rec)
        
        # 2. Eviction policy optimization
        eviction_rec = self._recommend_eviction_policy(metrics, access_patterns)
        if eviction_rec:
            recommendations.append(eviction_rec)
        
        # 3. Quality threshold optimization
        quality_rec = self._recommend_quality_threshold(model_performance)
        if quality_rec:
            recommendations.append(quality_rec)
        
        # 4. Cost threshold optimization
        cost_rec = self._recommend_cost_threshold(metrics, model_performance)
        if cost_rec:
            recommendations.append(cost_rec)
        
        # 5. TTL optimization
        ttl_rec = self._recommend_ttl_settings(access_patterns)
        if ttl_rec:
            recommendations.append(ttl_rec)
        
        # 6. Strategy optimization
        strategy_rec = self._recommend_cache_strategy(metrics, access_patterns)
        if strategy_rec:
            recommendations.append(strategy_rec)
        
        return recommendations
    
    def _recommend_cache_size(self, metrics: CacheMetrics, access_patterns: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend optimal cache size."""
        current_size = len(self.cache.cache)
        max_size = self.cache.max_size
        
        # Calculate size utilization
        utilization = current_size / max_size if max_size > 0 else 0.0
        
        # Recommend size adjustment based on utilization and performance
        if utilization > 0.9 and metrics.hit_rate < self.target_hit_rate:
            # High utilization, low hit rate - increase size
            recommended_size = int(max_size * 1.5)
            expected_improvement = 0.1  # 10% improvement in hit rate
            
            return OptimizationRecommendation(
                parameter="max_size",
                current_value=max_size,
                recommended_value=recommended_size,
                expected_improvement=expected_improvement,
                confidence=0.7,
                reasoning="High cache utilization with low hit rate indicates insufficient cache size",
                impact_estimate={"hit_rate_improvement": 0.1, "storage_cost_increase": 0.5}
            )
        
        elif utilization < 0.5 and metrics.storage_cost > metrics.total_cost_savings * 0.3:
            # Low utilization, high storage cost - decrease size
            recommended_size = int(max_size * 0.7)
            expected_improvement = 0.2  # 20% reduction in storage cost
            
            return OptimizationRecommendation(
                parameter="max_size",
                current_value=max_size,
                recommended_value=recommended_size,
                expected_improvement=expected_improvement,
                confidence=0.8,
                reasoning="Low cache utilization with high storage cost indicates oversized cache",
                impact_estimate={"storage_cost_reduction": 0.2, "hit_rate_impact": -0.05}
            )
        
        return None
    
    def _recommend_eviction_policy(self, metrics: CacheMetrics, access_patterns: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend eviction policy optimizations."""
        # Analyze access patterns to recommend eviction batch size
        avg_access_count = statistics.mean([entry.access_count for entry in self.cache.cache.values()])
        
        if avg_access_count > 10 and self.cache.eviction_batch_size < 200:
            # High access frequency - increase batch size for efficiency
            recommended_batch = min(200, int(self.cache.eviction_batch_size * 1.5))
            
            return OptimizationRecommendation(
                parameter="eviction_batch_size",
                current_value=self.cache.eviction_batch_size,
                recommended_value=recommended_batch,
                expected_improvement=0.05,
                confidence=0.6,
                reasoning="High access frequency suggests larger eviction batches for better efficiency",
                impact_estimate={"eviction_efficiency": 0.05, "memory_usage": 0.1}
            )
        
        return None
    
    def _recommend_quality_threshold(self, model_performance: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend quality threshold adjustments."""
        # Calculate average quality across all models
        avg_qualities = [stats["avg_quality"] for stats in model_performance.values() if stats["avg_quality"] > 0]
        
        if not avg_qualities:
            return None
        
        overall_avg_quality = statistics.mean(avg_qualities)
        current_threshold = self.cache.min_quality_score
        
        # If overall quality is high, we can raise the threshold
        if overall_avg_quality > 0.9 and current_threshold < 0.8:
            recommended_threshold = min(0.8, current_threshold + 0.1)
            
            return OptimizationRecommendation(
                parameter="min_quality_score",
                current_value=current_threshold,
                recommended_value=recommended_threshold,
                expected_improvement=0.05,
                confidence=0.7,
                reasoning="High overall quality allows for stricter quality threshold",
                impact_estimate={"quality_improvement": 0.05, "cache_size_reduction": 0.1}
            )
        
        # If overall quality is low, we should lower the threshold
        elif overall_avg_quality < 0.6 and current_threshold > 0.5:
            recommended_threshold = max(0.5, current_threshold - 0.1)
            
            return OptimizationRecommendation(
                parameter="min_quality_score",
                current_value=current_threshold,
                recommended_value=recommended_threshold,
                expected_improvement=0.1,
                confidence=0.6,
                reasoning="Low overall quality suggests lowering quality threshold for better hit rate",
                impact_estimate={"hit_rate_improvement": 0.1, "quality_impact": -0.05}
            )
        
        return None
    
    def _recommend_cost_threshold(self, metrics: CacheMetrics, model_performance: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend cost threshold adjustments."""
        # Calculate average cost across all models
        avg_costs = [stats["avg_cost"] for stats in model_performance.values() if stats["avg_cost"] > 0]
        
        if not avg_costs:
            return None
        
        overall_avg_cost = statistics.mean(avg_costs)
        current_threshold = self.cache.min_cost_threshold
        
        # If average cost is much higher than threshold, we can raise it
        if overall_avg_cost > current_threshold * 5:
            recommended_threshold = min(overall_avg_cost * 0.1, current_threshold * 2)
            
            return OptimizationRecommendation(
                parameter="min_cost_threshold",
                current_value=current_threshold,
                recommended_value=recommended_threshold,
                expected_improvement=0.1,
                confidence=0.7,
                reasoning="High average cost allows for higher cost threshold, focusing on expensive requests",
                impact_estimate={"storage_savings": 0.1, "hit_rate_impact": -0.05}
            )
        
        return None
    
    def _recommend_ttl_settings(self, access_patterns: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend TTL settings based on access patterns."""
        # Analyze hourly distribution to recommend TTL
        hourly_dist = access_patterns.get("hourly_distribution", {})
        
        if not hourly_dist:
            return None
        
        # Calculate peak hours
        max_hour_accesses = max(hourly_dist.values()) if hourly_dist else 0
        peak_hours = [hour for hour, accesses in hourly_dist.items() if accesses > max_hour_accesses * 0.7]
        
        if len(peak_hours) <= 6:  # Concentrated usage
            recommended_ttl = 3600 * 4  # 4 hours
            
            return OptimizationRecommendation(
                parameter="default_ttl",
                current_value=3600,  # Assume 1 hour default
                recommended_value=recommended_ttl,
                expected_improvement=0.08,
                confidence=0.6,
                reasoning="Concentrated usage patterns suggest longer TTL for better cache utilization",
                impact_estimate={"hit_rate_improvement": 0.08, "storage_cost_increase": 0.05}
            )
        
        return None
    
    def _recommend_cache_strategy(self, metrics: CacheMetrics, access_patterns: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Recommend cache strategy based on performance."""
        current_strategy = self.cache.strategy
        
        # Analyze if strategy change would be beneficial
        if metrics.hit_rate < self.target_hit_rate and current_strategy != CacheStrategy.HYBRID:
            return OptimizationRecommendation(
                parameter="strategy",
                current_value=current_strategy.value,
                recommended_value=CacheStrategy.HYBRID.value,
                expected_improvement=0.1,
                confidence=0.6,
                reasoning="Low hit rate suggests hybrid strategy might be more effective",
                impact_estimate={"hit_rate_improvement": 0.1, "complexity_increase": 0.1}
            )
        
        return None
    
    async def apply_recommendations(self, recommendations: List[OptimizationRecommendation], confidence_threshold: float = 0.7):
        """Apply optimization recommendations with sufficient confidence."""
        applied_count = 0
        
        for rec in recommendations:
            if rec.confidence >= confidence_threshold:
                try:
                    await self._apply_recommendation(rec)
                    applied_count += 1
                    self.optimization_history.append(rec)
                    self.logger.info(f"Applied recommendation: {rec.parameter} = {rec.recommended_value}")
                except Exception as e:
                    self.logger.error(f"Error applying recommendation {rec.parameter}: {str(e)}")
        
        self.logger.info(f"Applied {applied_count} of {len(recommendations)} recommendations")
    
    async def _apply_recommendation(self, rec: OptimizationRecommendation):
        """Apply a single recommendation."""
        if rec.parameter == "max_size":
            self.cache.max_size = rec.recommended_value
        elif rec.parameter == "eviction_batch_size":
            self.cache.eviction_batch_size = rec.recommended_value
        elif rec.parameter == "min_quality_score":
            self.cache.min_quality_score = rec.recommended_value
        elif rec.parameter == "min_cost_threshold":
            self.cache.min_cost_threshold = rec.recommended_value
        elif rec.parameter == "strategy":
            self.cache.strategy = CacheStrategy(rec.recommended_value)
        # Add other parameters as needed
    
    def get_optimization_history(self) -> List[OptimizationRecommendation]:
        """Get history of applied optimizations."""
        return self.optimization_history
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time."""
        if len(self.analysis_history) < 2:
            return {"insufficient_data": True}
        
        recent = self.analysis_history[-1]
        previous = self.analysis_history[-2]
        
        trends = {
            "hit_rate_trend": recent.hit_rate - previous.hit_rate,
            "cost_savings_trend": recent.cost_savings - previous.cost_savings,
            "storage_efficiency_trend": recent.storage_efficiency - previous.storage_efficiency,
            "quality_trend": recent.quality_score - previous.quality_score,
            "analysis_count": len(self.analysis_history)
        }
        
        return trends
    
    def export_optimization_report(self) -> Dict[str, Any]:
        """Export comprehensive optimization report."""
        if not self.analysis_history:
            return {"error": "No analysis data available"}
        
        latest_analysis = self.analysis_history[-1]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_performance": {
                "hit_rate": latest_analysis.hit_rate,
                "cost_savings": latest_analysis.cost_savings,
                "storage_efficiency": latest_analysis.storage_efficiency,
                "quality_score": latest_analysis.quality_score
            },
            "recommendations": [
                {
                    "parameter": rec.parameter,
                    "current_value": rec.current_value,
                    "recommended_value": rec.recommended_value,
                    "expected_improvement": rec.expected_improvement,
                    "confidence": rec.confidence,
                    "reasoning": rec.reasoning
                }
                for rec in latest_analysis.recommendations
            ],
            "trends": self.get_performance_trends(),
            "optimization_history": len(self.optimization_history),
            "analysis_history": len(self.analysis_history)
        }