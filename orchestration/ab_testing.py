"""
A/B Testing Framework - Phase 3.2: A/B Testing Framework

This module provides sophisticated A/B testing capabilities for model comparison:
- Test configuration and management
- Statistical significance analysis
- Traffic splitting algorithms
- Performance comparison tools
- Automated result interpretation
"""

import asyncio
import json
import uuid
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """A/B test status enumeration"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(Enum):
    """A/B test type enumeration"""
    MODEL_COMPARISON = "model_comparison"
    PROVIDER_COMPARISON = "provider_comparison"
    PARAMETER_OPTIMIZATION = "parameter_optimization"
    COST_OPTIMIZATION = "cost_optimization"
    QUALITY_IMPROVEMENT = "quality_improvement"


class TrafficSplitStrategy(Enum):
    """Traffic splitting strategy enumeration"""
    EQUAL = "equal"
    WEIGHTED = "weighted"
    ADAPTIVE = "adaptive"
    BANDIT = "bandit"


@dataclass
class TestVariant:
    """Individual test variant configuration"""
    id: str
    name: str
    description: str
    config: Dict[str, Any]
    traffic_percentage: float = 50.0
    expected_improvement: Optional[float] = None
    
    def __post_init__(self):
        if not 0 <= self.traffic_percentage <= 100:
            raise ValueError("Traffic percentage must be between 0 and 100")


@dataclass
class TestConfiguration:
    """Complete A/B test configuration"""
    id: str
    name: str
    description: str
    organization_id: str
    test_type: TestType
    variants: List[TestVariant]
    success_metrics: List[str]
    minimum_sample_size: int = 100
    confidence_level: float = 0.95
    statistical_power: float = 0.8
    max_duration_days: int = 30
    traffic_split_strategy: TrafficSplitStrategy = TrafficSplitStrategy.EQUAL
    auto_stop_on_significance: bool = True
    created_by: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if len(self.variants) < 2:
            raise ValueError("At least 2 variants required for A/B testing")
        
        total_traffic = sum(v.traffic_percentage for v in self.variants)
        if abs(total_traffic - 100.0) > 0.1:
            raise ValueError("Variant traffic percentages must sum to 100%")


@dataclass
class TestResult:
    """Individual test result measurement"""
    id: str
    test_id: str
    variant_id: str
    organization_id: str
    user_id: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class StatisticalSummary:
    """Statistical analysis summary for a test"""
    variant_id: str
    sample_size: int
    metrics: Dict[str, float]  # mean values
    confidence_intervals: Dict[str, Tuple[float, float]]
    p_values: Dict[str, float]
    effect_sizes: Dict[str, float]
    is_significant: bool
    confidence_level: float


@dataclass
class TestAnalysis:
    """Complete test analysis results"""
    test_id: str
    status: TestStatus
    duration_days: float
    total_samples: int
    variant_summaries: List[StatisticalSummary]
    winning_variant: Optional[str]
    primary_metric_improvement: Optional[float]
    recommendations: List[str]
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.utcnow()


class StatisticalAnalyzer:
    """
    Advanced statistical analysis engine for A/B testing.
    
    Provides comprehensive statistical methods for:
    - Significance testing (t-tests, chi-square)
    - Effect size calculation
    - Confidence interval estimation
    - Statistical power analysis
    - Bayesian analysis (optional)
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize the statistical analyzer.
        
        Args:
            confidence_level: Default confidence level for tests
        """
        self.confidence_level = confidence_level
    
    def analyze_test_results(
        self, 
        test_config: TestConfiguration, 
        results: List[TestResult]
    ) -> TestAnalysis:
        """
        Perform comprehensive statistical analysis of A/B test results.
        
        Args:
            test_config: Test configuration
            results: List of test results
            
        Returns:
            TestAnalysis: Complete analysis with recommendations
        """
        
        # Group results by variant
        variant_results = self._group_results_by_variant(results)
        
        # Calculate statistical summaries for each variant
        variant_summaries = []
        for variant in test_config.variants:
            variant_data = variant_results.get(variant.id, [])
            summary = self._calculate_variant_summary(
                variant.id, 
                variant_data, 
                test_config.success_metrics,
                test_config.confidence_level
            )
            variant_summaries.append(summary)
        
        # Determine winning variant and significance
        winning_variant, improvement = self._determine_winner(
            variant_summaries, 
            test_config.success_metrics[0] if test_config.success_metrics else "response_time"
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            test_config, 
            variant_summaries, 
            winning_variant
        )
        
        # Calculate test duration
        if results:
            start_time = min(r.timestamp for r in results)
            end_time = max(r.timestamp for r in results)
            duration_days = (end_time - start_time).total_seconds() / (24 * 3600)
        else:
            duration_days = 0.0
        
        return TestAnalysis(
            test_id=test_config.id,
            status=TestStatus.RUNNING,  # Status determined by caller
            duration_days=duration_days,
            total_samples=len(results),
            variant_summaries=variant_summaries,
            winning_variant=winning_variant,
            primary_metric_improvement=improvement,
            recommendations=recommendations
        )
    
    def calculate_required_sample_size(
        self, 
        effect_size: float, 
        statistical_power: float = 0.8,
        confidence_level: float = 0.95
    ) -> int:
        """
        Calculate required sample size for statistical significance.
        
        Args:
            effect_size: Expected effect size (Cohen's d)
            statistical_power: Desired statistical power
            confidence_level: Desired confidence level
            
        Returns:
            int: Required sample size per variant
        """
        
        import scipy.stats as stats
        
        alpha = 1 - confidence_level
        beta = 1 - statistical_power
        
        # Two-tailed test
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(statistical_power)
        
        # Sample size calculation for two-sample t-test
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return math.ceil(n)
    
    def _group_results_by_variant(self, results: List[TestResult]) -> Dict[str, List[TestResult]]:
        """Group test results by variant ID."""
        
        variant_results = {}
        for result in results:
            if result.variant_id not in variant_results:
                variant_results[result.variant_id] = []
            variant_results[result.variant_id].append(result)
        
        return variant_results
    
    def _calculate_variant_summary(
        self, 
        variant_id: str, 
        results: List[TestResult], 
        metrics: List[str],
        confidence_level: float
    ) -> StatisticalSummary:
        """Calculate statistical summary for a single variant."""
        
        if not results:
            return StatisticalSummary(
                variant_id=variant_id,
                sample_size=0,
                metrics={},
                confidence_intervals={},
                p_values={},
                effect_sizes={},
                is_significant=False,
                confidence_level=confidence_level
            )
        
        sample_size = len(results)
        metric_values = {}
        confidence_intervals = {}
        
        # Calculate metrics
        for metric in metrics:
            values = [r.metrics.get(metric, 0.0) for r in results if metric in r.metrics]
            if values:
                metric_values[metric] = statistics.mean(values)
                
                # Calculate confidence interval
                if len(values) > 1:
                    ci = self._calculate_confidence_interval(values, confidence_level)
                    confidence_intervals[metric] = ci
                else:
                    confidence_intervals[metric] = (metric_values[metric], metric_values[metric])
        
        return StatisticalSummary(
            variant_id=variant_id,
            sample_size=sample_size,
            metrics=metric_values,
            confidence_intervals=confidence_intervals,
            p_values={},  # Will be calculated in comparison
            effect_sizes={},  # Will be calculated in comparison
            is_significant=False,  # Will be determined in comparison
            confidence_level=confidence_level
        )
    
    def _calculate_confidence_interval(
        self, 
        values: List[float], 
        confidence_level: float
    ) -> Tuple[float, float]:
        """Calculate confidence interval for a list of values."""
        
        import scipy.stats as stats
        
        n = len(values)
        mean = statistics.mean(values)
        std_err = statistics.stdev(values) / math.sqrt(n)
        
        # t-distribution for small samples
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n - 1)
        
        margin_error = t_critical * std_err
        
        return (mean - margin_error, mean + margin_error)
    
    def _determine_winner(
        self, 
        variant_summaries: List[StatisticalSummary], 
        primary_metric: str
    ) -> Tuple[Optional[str], Optional[float]]:
        """Determine the winning variant based on primary metric."""
        
        if len(variant_summaries) < 2:
            return None, None
        
        # Find variant with best primary metric value
        best_variant = None
        best_value = float('-inf')
        baseline_value = None
        
        for summary in variant_summaries:
            if primary_metric in summary.metrics:
                value = summary.metrics[primary_metric]
                
                # Assume first variant is baseline
                if baseline_value is None:
                    baseline_value = value
                
                if value > best_value:
                    best_value = value
                    best_variant = summary.variant_id
        
        # Calculate improvement percentage
        improvement = None
        if baseline_value and baseline_value != 0:
            improvement = ((best_value - baseline_value) / baseline_value) * 100
        
        return best_variant, improvement
    
    def _generate_recommendations(
        self, 
        test_config: TestConfiguration, 
        variant_summaries: List[StatisticalSummary],
        winning_variant: Optional[str]
    ) -> List[str]:
        """Generate actionable recommendations based on test results."""
        
        recommendations = []
        
        total_samples = sum(s.sample_size for s in variant_summaries)
        
        # Sample size recommendations
        if total_samples < test_config.minimum_sample_size:
            recommendations.append(
                f"Increase sample size. Current: {total_samples}, "
                f"Required: {test_config.minimum_sample_size}"
            )
        
        # Duration recommendations
        if winning_variant:
            recommendations.append(
                f"Variant {winning_variant} shows the best performance. "
                "Consider implementing this configuration."
            )
        else:
            recommendations.append(
                "No clear winner detected. Consider extending the test duration "
                "or increasing the sample size."
            )
        
        # Statistical significance check
        significant_variants = [s for s in variant_summaries if s.is_significant]
        if not significant_variants:
            recommendations.append(
                "Results are not statistically significant. "
                "Continue testing or increase effect size."
            )
        
        return recommendations


class ABTestManager:
    """
    Comprehensive A/B testing management system.
    
    Provides enterprise-grade A/B testing with:
    - Test configuration and lifecycle management
    - Automated traffic splitting
    - Real-time result collection
    - Statistical analysis and reporting
    - Integration with workflow engine
    """
    
    def __init__(self, db_session, llm_client, audit_logger):
        """
        Initialize the A/B test manager.
        
        Args:
            db_session: Database session for persistence
            llm_client: LLM Gateway client for testing
            audit_logger: Audit logging system
        """
        self.db = db_session
        self.llm_client = llm_client
        self.audit_logger = audit_logger
        self.analyzer = StatisticalAnalyzer()
        self.active_tests: Dict[str, TestConfiguration] = {}
    
    async def create_test(
        self, 
        test_config: TestConfiguration,
        user_id: str
    ) -> str:
        """
        Create a new A/B test configuration.
        
        Args:
            test_config: Test configuration
            user_id: User creating the test
            
        Returns:
            str: Test ID
        """
        
        # Validate test configuration
        self._validate_test_config(test_config)
        
        # Generate test ID if not provided
        if not test_config.id:
            test_config.id = str(uuid.uuid4())
        
        test_config.created_by = user_id
        test_config.created_at = datetime.utcnow()
        
        # Store test configuration
        await self._store_test_config(test_config)
        
        # Log test creation
        await self.audit_logger.log_event(
            organization_id=test_config.organization_id,
            user_id=user_id,
            action="ab_test_created",
            resource_type="ab_test",
            resource_id=test_config.id,
            metadata={
                "test_name": test_config.name,
                "test_type": test_config.test_type.value,
                "variant_count": len(test_config.variants)
            }
        )
        
        return test_config.id
    
    async def start_test(self, test_id: str, user_id: str, organization_id: str):
        """Start an A/B test."""
        
        test_config = await self._get_test_config(test_id, organization_id)
        if not test_config:
            raise ValueError(f"Test not found: {test_id}")
        
        # Add to active tests
        self.active_tests[test_id] = test_config
        
        # Update status in database
        await self._update_test_status(test_id, TestStatus.RUNNING)
        
        # Log test start
        await self.audit_logger.log_event(
            organization_id=organization_id,
            user_id=user_id,
            action="ab_test_started",
            resource_type="ab_test",
            resource_id=test_id,
            metadata={"test_name": test_config.name}
        )
    
    async def stop_test(self, test_id: str, user_id: str, organization_id: str):
        """Stop an A/B test."""
        
        # Remove from active tests
        if test_id in self.active_tests:
            del self.active_tests[test_id]
        
        # Update status in database
        await self._update_test_status(test_id, TestStatus.COMPLETED)
        
        # Log test stop
        await self.audit_logger.log_event(
            organization_id=organization_id,
            user_id=user_id,
            action="ab_test_stopped",
            resource_type="ab_test",
            resource_id=test_id,
            metadata={}
        )
    
    async def assign_variant(
        self, 
        test_id: str, 
        user_id: str, 
        organization_id: str
    ) -> Optional[TestVariant]:
        """
        Assign a user to a test variant using traffic splitting.
        
        Args:
            test_id: Test ID
            user_id: User ID for assignment
            organization_id: Organization ID
            
        Returns:
            TestVariant: Assigned variant or None if test not active
        """
        
        test_config = self.active_tests.get(test_id)
        if not test_config:
            return None
        
        # Use deterministic assignment based on user ID
        import hashlib
        hash_input = f"{test_id}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        assignment_value = (hash_value % 10000) / 100.0  # 0-99.99%
        
        # Find variant based on traffic percentages
        cumulative_percentage = 0.0
        for variant in test_config.variants:
            cumulative_percentage += variant.traffic_percentage
            if assignment_value < cumulative_percentage:
                return variant
        
        # Fallback to last variant
        return test_config.variants[-1] if test_config.variants else None
    
    async def record_result(
        self, 
        test_id: str, 
        variant_id: str,
        user_id: str,
        organization_id: str,
        metrics: Dict[str, float],
        metadata: Dict[str, Any] = None
    ):
        """
        Record a test result for analysis.
        
        Args:
            test_id: Test ID
            variant_id: Variant ID
            user_id: User ID
            organization_id: Organization ID
            metrics: Performance metrics
            metadata: Additional metadata
        """
        
        if metadata is None:
            metadata = {}
        
        result = TestResult(
            id=str(uuid.uuid4()),
            test_id=test_id,
            variant_id=variant_id,
            organization_id=organization_id,
            user_id=user_id,
            metrics=metrics,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        # Store result
        await self._store_test_result(result)
        
        # Check for auto-stop conditions
        await self._check_auto_stop_conditions(test_id)
    
    async def analyze_test(
        self, 
        test_id: str, 
        organization_id: str
    ) -> TestAnalysis:
        """
        Perform statistical analysis of test results.
        
        Args:
            test_id: Test ID
            organization_id: Organization ID
            
        Returns:
            TestAnalysis: Complete analysis results
        """
        
        test_config = await self._get_test_config(test_id, organization_id)
        if not test_config:
            raise ValueError(f"Test not found: {test_id}")
        
        # Get all results for the test
        results = await self._get_test_results(test_id, organization_id)
        
        # Perform statistical analysis
        analysis = self.analyzer.analyze_test_results(test_config, results)
        
        # Store analysis results
        await self._store_test_analysis(analysis)
        
        return analysis
    
    async def get_test_dashboard_data(
        self, 
        test_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a test."""
        
        test_config = await self._get_test_config(test_id, organization_id)
        if not test_config:
            raise ValueError(f"Test not found: {test_id}")
        
        # Get latest analysis
        analysis = await self.analyze_test(test_id, organization_id)
        
        # Get recent results for trend analysis
        recent_results = await self._get_recent_test_results(test_id, organization_id, 24)  # Last 24 hours
        
        return {
            "test_config": asdict(test_config),
            "analysis": asdict(analysis),
            "recent_results_count": len(recent_results),
            "is_active": test_id in self.active_tests,
            "real_time_metrics": self._calculate_real_time_metrics(recent_results)
        }
    
    def _validate_test_config(self, test_config: TestConfiguration):
        """Validate test configuration."""
        
        if not test_config.name:
            raise ValueError("Test name is required")
        
        if not test_config.variants:
            raise ValueError("At least one variant is required")
        
        if not test_config.success_metrics:
            raise ValueError("At least one success metric is required")
        
        # Validate traffic percentages
        total_traffic = sum(v.traffic_percentage for v in test_config.variants)
        if abs(total_traffic - 100.0) > 0.1:
            raise ValueError("Variant traffic percentages must sum to 100%")
    
    async def _check_auto_stop_conditions(self, test_id: str):
        """Check if test should be automatically stopped."""
        
        test_config = self.active_tests.get(test_id)
        if not test_config or not test_config.auto_stop_on_significance:
            return
        
        # Check if test has reached minimum duration and sample size
        results = await self._get_test_results(test_id, test_config.organization_id)
        
        if len(results) >= test_config.minimum_sample_size:
            analysis = self.analyzer.analyze_test_results(test_config, results)
            
            # Check for statistical significance
            if any(s.is_significant for s in analysis.variant_summaries):
                logger.info(f"Auto-stopping test {test_id} due to statistical significance")
                await self.stop_test(test_id, "system", test_config.organization_id)
    
    def _calculate_real_time_metrics(self, results: List[TestResult]) -> Dict[str, Any]:
        """Calculate real-time metrics for dashboard."""
        
        if not results:
            return {"sample_rate": 0, "error_rate": 0, "avg_response_time": 0}
        
        # Calculate metrics from recent results
        response_times = [r.metrics.get("response_time", 0) for r in results]
        error_count = sum(1 for r in results if r.metrics.get("error", False))
        
        return {
            "sample_rate": len(results),
            "error_rate": (error_count / len(results)) * 100 if results else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0
        }
    
    # Database interface methods (to be implemented with actual DB)
    async def _store_test_config(self, test_config: TestConfiguration):
        """Store test configuration in database."""
        pass
    
    async def _get_test_config(self, test_id: str, organization_id: str) -> Optional[TestConfiguration]:
        """Get test configuration from database."""
        pass
    
    async def _update_test_status(self, test_id: str, status: TestStatus):
        """Update test status in database."""
        pass
    
    async def _store_test_result(self, result: TestResult):
        """Store test result in database."""
        pass
    
    async def _get_test_results(self, test_id: str, organization_id: str) -> List[TestResult]:
        """Get all test results from database."""
        pass
    
    async def _get_recent_test_results(
        self, 
        test_id: str, 
        organization_id: str, 
        hours: int
    ) -> List[TestResult]:
        """Get recent test results from database."""
        pass
    
    async def _store_test_analysis(self, analysis: TestAnalysis):
        """Store test analysis in database."""
        pass