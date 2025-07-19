"""
Advanced Score Calculator for Provider Performance
Implements sophisticated scoring algorithms for provider evaluation
"""

import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoreComponents:
    """Individual score components for a provider"""
    latency_score: float = 0.0
    throughput_score: float = 0.0
    reliability_score: float = 0.0
    cost_score: float = 0.0
    quality_score: float = 0.0
    consistency_score: float = 0.0
    availability_score: float = 0.0
    trend_score: float = 0.0
    composite_score: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance metrics for score calculation"""
    response_times: List[float]
    success_rates: List[float]
    error_rates: List[float]
    costs: List[float]
    availabilities: List[float]
    timestamps: List[datetime]


class ScoreCalculator:
    """
    Advanced scoring system for provider performance evaluation
    
    Features:
    - Multi-dimensional scoring (latency, reliability, cost, quality, etc.)
    - Time-weighted scoring with decay
    - Percentile-based normalization
    - Trend analysis and momentum scoring
    - Statistical outlier detection and handling
    """
    
    def __init__(self):
        self.score_weights = {
            'latency': 0.25,
            'throughput': 0.15,
            'reliability': 0.20,
            'cost': 0.15,
            'quality': 0.10,
            'consistency': 0.10,
            'availability': 0.03,
            'trend': 0.02
        }
        
        # Time decay configuration
        self.time_decay_hours = 24  # Hours for full decay
        self.decay_factor = 0.1  # Minimum weight for old data
        
        # Normalization parameters
        self.normalization_percentiles = {
            'response_time': {'p10': 0.5, 'p90': 5.0},
            'success_rate': {'p10': 0.9, 'p90': 1.0},
            'cost': {'p10': 0.001, 'p90': 0.1},
            'availability': {'p10': 0.95, 'p90': 1.0}
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    def calculate_comprehensive_score(self, provider_name: str, 
                                    metrics: PerformanceMetrics,
                                    baseline_metrics: Optional[Dict[str, PerformanceMetrics]] = None) -> ScoreComponents:
        """
        Calculate comprehensive score for a provider
        
        Args:
            provider_name: Name of the provider
            metrics: Performance metrics for the provider
            baseline_metrics: Optional baseline metrics for comparison
            
        Returns:
            ScoreComponents with all individual and composite scores
        """
        if not metrics.response_times:
            logger.warning(f"No metrics available for {provider_name}")
            return ScoreComponents()
        
        # Calculate individual score components
        scores = ScoreComponents()
        
        # Latency score (lower is better)
        scores.latency_score = self._calculate_latency_score(metrics.response_times, metrics.timestamps)
        
        # Throughput score (higher is better)
        scores.throughput_score = self._calculate_throughput_score(metrics.response_times, metrics.timestamps)
        
        # Reliability score (higher success rate is better)
        scores.reliability_score = self._calculate_reliability_score(metrics.success_rates, metrics.timestamps)
        
        # Cost score (lower cost is better)
        scores.cost_score = self._calculate_cost_score(metrics.costs, metrics.timestamps, baseline_metrics)
        
        # Quality score (consistency and accuracy)
        scores.quality_score = self._calculate_quality_score(metrics, baseline_metrics)
        
        # Consistency score (lower variance is better)
        scores.consistency_score = self._calculate_consistency_score(metrics.response_times, metrics.success_rates)
        
        # Availability score
        scores.availability_score = self._calculate_availability_score(metrics.availabilities, metrics.timestamps)
        
        # Trend score (improving performance is better)
        scores.trend_score = self._calculate_trend_score(metrics)
        
        # Composite score
        scores.composite_score = self._calculate_composite_score(scores)
        
        return scores
    
    def _calculate_latency_score(self, response_times: List[float], timestamps: List[datetime]) -> float:
        """Calculate latency score with time decay"""
        if not response_times:
            return 0.0
        
        # Apply time decay weights
        weights = self._calculate_time_weights(timestamps)
        
        # Calculate weighted percentiles
        weighted_median = self._weighted_percentile(response_times, weights, 0.5)
        weighted_p95 = self._weighted_percentile(response_times, weights, 0.95)
        
        # Normalize to 0-1 scale (lower latency = higher score)
        median_score = self._normalize_inverse(weighted_median, 0.5, 5.0)
        p95_score = self._normalize_inverse(weighted_p95, 1.0, 10.0)
        
        # Combine median (70%) and p95 (30%)
        return median_score * 0.7 + p95_score * 0.3
    
    def _calculate_throughput_score(self, response_times: List[float], timestamps: List[datetime]) -> float:
        """Calculate throughput score based on request rate"""
        if len(timestamps) < 2:
            return 0.5
        
        # Calculate requests per second in recent time windows
        time_windows = self._create_time_windows(timestamps, window_minutes=5)
        
        throughput_rates = []
        for window_start, window_end, window_timestamps in time_windows:
            duration = (window_end - window_start).total_seconds()
            if duration > 0:
                rate = len(window_timestamps) / duration
                throughput_rates.append(rate)
        
        if not throughput_rates:
            return 0.5
        
        # Score based on average throughput
        avg_throughput = statistics.mean(throughput_rates)
        return self._normalize_direct(avg_throughput, 0.1, 10.0)
    
    def _calculate_reliability_score(self, success_rates: List[float], timestamps: List[datetime]) -> float:
        """Calculate reliability score with time decay"""
        if not success_rates:
            return 0.0
        
        # Apply time decay weights
        weights = self._calculate_time_weights(timestamps)
        
        # Calculate weighted average success rate
        weighted_avg = sum(rate * weight for rate, weight in zip(success_rates, weights)) / sum(weights)
        
        # Calculate consistency (lower variance is better)
        variance = sum(weight * (rate - weighted_avg) ** 2 for rate, weight in zip(success_rates, weights)) / sum(weights)
        consistency_factor = 1.0 - min(variance, 0.1) / 0.1
        
        # Combine success rate (80%) and consistency (20%)
        return weighted_avg * 0.8 + consistency_factor * 0.2
    
    def _calculate_cost_score(self, costs: List[float], timestamps: List[datetime], 
                            baseline_metrics: Optional[Dict[str, PerformanceMetrics]] = None) -> float:
        """Calculate cost efficiency score"""
        if not costs:
            return 0.5
        
        # Apply time decay weights
        weights = self._calculate_time_weights(timestamps)
        
        # Calculate weighted average cost
        weighted_avg_cost = sum(cost * weight for cost, weight in zip(costs, weights)) / sum(weights)
        
        # If baseline metrics available, calculate relative cost score
        if baseline_metrics:
            all_costs = []
            for provider_metrics in baseline_metrics.values():
                if provider_metrics.costs:
                    provider_weights = self._calculate_time_weights(provider_metrics.timestamps)
                    provider_avg = sum(c * w for c, w in zip(provider_metrics.costs, provider_weights)) / sum(provider_weights)
                    all_costs.append(provider_avg)
            
            if all_costs:
                min_cost = min(all_costs)
                max_cost = max(all_costs)
                
                if max_cost > min_cost:
                    # Normalize inversely (lower cost = higher score)
                    return 1.0 - (weighted_avg_cost - min_cost) / (max_cost - min_cost)
        
        # Fallback to absolute cost scoring
        return self._normalize_inverse(weighted_avg_cost, 0.001, 0.1)
    
    def _calculate_quality_score(self, metrics: PerformanceMetrics, 
                               baseline_metrics: Optional[Dict[str, PerformanceMetrics]] = None) -> float:
        """Calculate quality score based on multiple factors"""
        if not metrics.response_times:
            return 0.0
        
        quality_factors = []
        
        # Response time consistency
        response_time_cv = self._coefficient_of_variation(metrics.response_times)
        consistency_score = 1.0 - min(response_time_cv, 1.0)
        quality_factors.append(consistency_score)
        
        # Success rate stability
        if metrics.success_rates:
            success_rate_cv = self._coefficient_of_variation(metrics.success_rates)
            stability_score = 1.0 - min(success_rate_cv, 1.0)
            quality_factors.append(stability_score)
        
        # Error rate score
        if metrics.error_rates:
            avg_error_rate = statistics.mean(metrics.error_rates)
            error_score = 1.0 - min(avg_error_rate, 1.0)
            quality_factors.append(error_score)
        
        # Availability consistency
        if metrics.availabilities:
            availability_cv = self._coefficient_of_variation(metrics.availabilities)
            availability_consistency = 1.0 - min(availability_cv, 1.0)
            quality_factors.append(availability_consistency)
        
        return statistics.mean(quality_factors) if quality_factors else 0.5
    
    def _calculate_consistency_score(self, response_times: List[float], success_rates: List[float]) -> float:
        """Calculate consistency score based on variance"""
        consistency_scores = []
        
        # Response time consistency
        if response_times:
            rt_cv = self._coefficient_of_variation(response_times)
            rt_consistency = 1.0 - min(rt_cv, 1.0)
            consistency_scores.append(rt_consistency)
        
        # Success rate consistency
        if success_rates:
            sr_cv = self._coefficient_of_variation(success_rates)
            sr_consistency = 1.0 - min(sr_cv, 1.0)
            consistency_scores.append(sr_consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.5
    
    def _calculate_availability_score(self, availabilities: List[float], timestamps: List[datetime]) -> float:
        """Calculate availability score with time decay"""
        if not availabilities:
            return 0.5
        
        # Apply time decay weights
        weights = self._calculate_time_weights(timestamps)
        
        # Calculate weighted average availability
        weighted_avg = sum(avail * weight for avail, weight in zip(availabilities, weights)) / sum(weights)
        
        return weighted_avg
    
    def _calculate_trend_score(self, metrics: PerformanceMetrics) -> float:
        """Calculate trend score based on performance improvement/degradation"""
        if len(metrics.response_times) < 10:  # Need minimum data for trend
            return 0.5
        
        trend_scores = []
        
        # Response time trend (improving = lower response time)
        rt_trend = self._calculate_linear_trend(metrics.response_times)
        rt_trend_score = 0.5 - rt_trend * 0.5  # Invert because lower is better
        trend_scores.append(rt_trend_score)
        
        # Success rate trend (improving = higher success rate)
        if metrics.success_rates:
            sr_trend = self._calculate_linear_trend(metrics.success_rates)
            sr_trend_score = 0.5 + sr_trend * 0.5
            trend_scores.append(sr_trend_score)
        
        # Cost trend (improving = lower cost)
        if metrics.costs:
            cost_trend = self._calculate_linear_trend(metrics.costs)
            cost_trend_score = 0.5 - cost_trend * 0.5
            trend_scores.append(cost_trend_score)
        
        return statistics.mean(trend_scores) if trend_scores else 0.5
    
    def _calculate_composite_score(self, scores: ScoreComponents) -> float:
        """Calculate composite score from individual components"""
        weighted_score = (
            scores.latency_score * self.score_weights['latency'] +
            scores.throughput_score * self.score_weights['throughput'] +
            scores.reliability_score * self.score_weights['reliability'] +
            scores.cost_score * self.score_weights['cost'] +
            scores.quality_score * self.score_weights['quality'] +
            scores.consistency_score * self.score_weights['consistency'] +
            scores.availability_score * self.score_weights['availability'] +
            scores.trend_score * self.score_weights['trend']
        )
        
        return max(0.0, min(1.0, weighted_score))
    
    def _calculate_time_weights(self, timestamps: List[datetime]) -> List[float]:
        """Calculate time decay weights for data points"""
        if not timestamps:
            return []
        
        current_time = datetime.utcnow()
        weights = []
        
        for timestamp in timestamps:
            # Calculate hours since data point
            hours_ago = (current_time - timestamp).total_seconds() / 3600
            
            # Apply exponential decay
            decay_factor = math.exp(-hours_ago / self.time_decay_hours)
            weight = self.decay_factor + (1 - self.decay_factor) * decay_factor
            weights.append(weight)
        
        return weights
    
    def _weighted_percentile(self, values: List[float], weights: List[float], percentile: float) -> float:
        """Calculate weighted percentile"""
        if not values or not weights:
            return 0.0
        
        # Sort values with corresponding weights
        sorted_pairs = sorted(zip(values, weights))
        sorted_values, sorted_weights = zip(*sorted_pairs)
        
        # Calculate cumulative weights
        total_weight = sum(sorted_weights)
        cumulative_weights = []
        cumulative = 0
        
        for weight in sorted_weights:
            cumulative += weight
            cumulative_weights.append(cumulative / total_weight)
        
        # Find percentile
        for i, cum_weight in enumerate(cumulative_weights):
            if cum_weight >= percentile:
                return sorted_values[i]
        
        return sorted_values[-1]
    
    def _normalize_direct(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range (higher value = higher score)"""
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _normalize_inverse(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range (lower value = higher score)"""
        if max_val == min_val:
            return 0.5
        
        normalized = 1.0 - (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _coefficient_of_variation(self, values: List[float]) -> float:
        """Calculate coefficient of variation (std dev / mean)"""
        if not values or len(values) < 2:
            return 0.0
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0
        
        std_dev = statistics.stdev(values)
        return std_dev / mean_val
    
    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend (-1 to 1, positive means improving)"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate correlation coefficient
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(values)
        
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denominator_y = sum((values[i] - mean_y) ** 2 for i in range(n))
        
        if denominator_x == 0 or denominator_y == 0:
            return 0.0
        
        correlation = numerator / (math.sqrt(denominator_x) * math.sqrt(denominator_y))
        return max(-1.0, min(1.0, correlation))
    
    def _create_time_windows(self, timestamps: List[datetime], window_minutes: int = 5) -> List[Tuple[datetime, datetime, List[datetime]]]:
        """Create time windows for analysis"""
        if not timestamps:
            return []
        
        sorted_timestamps = sorted(timestamps)
        windows = []
        
        start_time = sorted_timestamps[0]
        end_time = sorted_timestamps[-1]
        
        current_time = start_time
        window_delta = timedelta(minutes=window_minutes)
        
        while current_time < end_time:
            window_end = current_time + window_delta
            window_timestamps = [
                ts for ts in sorted_timestamps
                if current_time <= ts < window_end
            ]
            
            if window_timestamps:
                windows.append((current_time, window_end, window_timestamps))
            
            current_time = window_end
        
        return windows
    
    def get_score_breakdown(self, scores: ScoreComponents) -> Dict[str, Any]:
        """Get detailed breakdown of score components"""
        return {
            'individual_scores': {
                'latency': scores.latency_score,
                'throughput': scores.throughput_score,
                'reliability': scores.reliability_score,
                'cost': scores.cost_score,
                'quality': scores.quality_score,
                'consistency': scores.consistency_score,
                'availability': scores.availability_score,
                'trend': scores.trend_score
            },
            'composite_score': scores.composite_score,
            'score_weights': self.score_weights.copy(),
            'weighted_contributions': {
                component: score * weight
                for component, (score, weight) in zip(
                    self.score_weights.keys(),
                    [
                        (scores.latency_score, self.score_weights['latency']),
                        (scores.throughput_score, self.score_weights['throughput']),
                        (scores.reliability_score, self.score_weights['reliability']),
                        (scores.cost_score, self.score_weights['cost']),
                        (scores.quality_score, self.score_weights['quality']),
                        (scores.consistency_score, self.score_weights['consistency']),
                        (scores.availability_score, self.score_weights['availability']),
                        (scores.trend_score, self.score_weights['trend'])
                    ]
                )
            }
        }
    
    def update_score_weights(self, new_weights: Dict[str, float]):
        """Update score component weights"""
        # Validate weights sum to 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Score weights sum to {total_weight}, normalizing to 1.0")
            new_weights = {k: v / total_weight for k, v in new_weights.items()}
        
        self.score_weights.update(new_weights)
        logger.info(f"Score weights updated: {new_weights}")


# Global score calculator instance
score_calculator = ScoreCalculator()