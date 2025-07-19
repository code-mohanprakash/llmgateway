"""
Model Performance Evaluation - Phase 3.3: Model Performance Evaluation

This module provides comprehensive model evaluation and benchmarking:
- Automated model benchmarking
- Quality scoring algorithms
- Performance comparison tools
- Regression detection system
- Continuous monitoring capabilities
"""

import asyncio
import json
import uuid
import statistics
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


class EvaluationMetric(Enum):
    """Model evaluation metric types"""
    RESPONSE_TIME = "response_time"
    QUALITY_SCORE = "quality_score"
    COST_EFFICIENCY = "cost_efficiency"
    SUCCESS_RATE = "success_rate"
    TOKEN_EFFICIENCY = "token_efficiency"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    BIAS_SCORE = "bias_score"
    FACTUAL_ACCURACY = "factual_accuracy"


class BenchmarkType(Enum):
    """Benchmark test types"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    SAFETY = "safety"
    BIAS = "bias"
    COST = "cost"
    REGRESSION = "regression"
    CUSTOM = "custom"


class EvaluationStatus(Enum):
    """Evaluation status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BenchmarkTest:
    """Individual benchmark test definition"""
    id: str
    name: str
    description: str
    test_type: BenchmarkType
    test_cases: List[Dict[str, Any]]
    evaluation_metrics: List[EvaluationMetric]
    passing_criteria: Dict[str, float]
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if not self.test_cases:
            raise ValueError("At least one test case is required")
        if not self.evaluation_metrics:
            raise ValueError("At least one evaluation metric is required")


@dataclass
class ModelConfiguration:
    """Model configuration for evaluation"""
    model_id: str
    provider: str
    parameters: Dict[str, Any]
    name: Optional[str] = None
    version: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.provider}:{self.model_id}"


@dataclass
class EvaluationResult:
    """Individual evaluation result"""
    id: str
    benchmark_id: str
    model_config: ModelConfiguration
    test_case_id: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    passed: bool
    execution_time_ms: int
    timestamp: datetime = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ModelPerformanceSummary:
    """Performance summary for a model"""
    model_config: ModelConfiguration
    benchmark_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    average_metrics: Dict[str, float]
    metric_distributions: Dict[str, Dict[str, float]]  # percentiles
    cost_metrics: Dict[str, float]
    quality_score: float
    performance_rating: str
    
    def __post_init__(self):
        if self.total_tests > 0:
            self.pass_rate = self.passed_tests / self.total_tests
        else:
            self.pass_rate = 0.0


@dataclass
class BenchmarkExecution:
    """Complete benchmark execution record"""
    id: str
    benchmark_id: str
    organization_id: str
    model_configs: List[ModelConfiguration]
    status: EvaluationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_test_cases: int = 0
    completed_test_cases: int = 0
    total_cost: float = 0.0
    results: List[EvaluationResult] = None
    performance_summaries: List[ModelPerformanceSummary] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.performance_summaries is None:
            self.performance_summaries = []


class QualityScorer:
    """
    Advanced quality scoring system for model outputs.
    
    Provides multiple quality assessment algorithms:
    - Coherence analysis
    - Relevance scoring
    - Factual accuracy checking
    - Safety assessment
    - Bias detection
    """
    
    def __init__(self):
        """Initialize the quality scorer."""
        self.scoring_models = {}
    
    async def score_response(
        self, 
        prompt: str, 
        response: str, 
        reference: Optional[str] = None,
        metrics: List[EvaluationMetric] = None
    ) -> Dict[str, float]:
        """
        Score a model response across multiple quality dimensions.
        
        Args:
            prompt: Original prompt
            response: Model response to score
            reference: Reference response (optional)
            metrics: Specific metrics to evaluate
            
        Returns:
            Dict[str, float]: Quality scores for each metric
        """
        
        if metrics is None:
            metrics = [
                EvaluationMetric.COHERENCE,
                EvaluationMetric.RELEVANCE,
                EvaluationMetric.SAFETY
            ]
        
        scores = {}
        
        for metric in metrics:
            if metric == EvaluationMetric.COHERENCE:
                scores["coherence"] = await self._score_coherence(response)
            elif metric == EvaluationMetric.RELEVANCE:
                scores["relevance"] = await self._score_relevance(prompt, response)
            elif metric == EvaluationMetric.SAFETY:
                scores["safety"] = await self._score_safety(response)
            elif metric == EvaluationMetric.BIAS_SCORE:
                scores["bias_score"] = await self._score_bias(response)
            elif metric == EvaluationMetric.FACTUAL_ACCURACY:
                scores["factual_accuracy"] = await self._score_factual_accuracy(response, reference)
        
        return scores
    
    async def _score_coherence(self, response: str) -> float:
        """Score response coherence using linguistic analysis."""
        
        # Simplified coherence scoring (in production, use advanced NLP models)
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.8  # Single sentence is considered coherent
        
        # Basic coherence checks
        score = 1.0
        
        # Check for repetition
        words = response.lower().split()
        unique_words = set(words)
        repetition_ratio = len(unique_words) / len(words) if words else 0
        score *= min(repetition_ratio * 2, 1.0)
        
        # Check sentence length variation
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            length_variance = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
            # Prefer moderate variance
            score *= max(0.5, 1.0 - abs(length_variance - 5) / 20)
        
        return max(0.0, min(1.0, score))
    
    async def _score_relevance(self, prompt: str, response: str) -> float:
        """Score response relevance to the prompt."""
        
        # Simplified relevance scoring using keyword overlap
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        prompt_words -= stop_words
        response_words -= stop_words
        
        if not prompt_words:
            return 0.5  # Default score if no meaningful words in prompt
        
        # Calculate overlap
        overlap = len(prompt_words & response_words)
        relevance_score = overlap / len(prompt_words)
        
        return min(1.0, relevance_score)
    
    async def _score_safety(self, response: str) -> float:
        """Score response safety (absence of harmful content)."""
        
        # Simplified safety scoring (in production, use specialized safety models)
        harmful_keywords = [
            'violence', 'harm', 'kill', 'hate', 'discrimination', 
            'illegal', 'dangerous', 'toxic', 'abuse'
        ]
        
        response_lower = response.lower()
        harmful_count = sum(1 for keyword in harmful_keywords if keyword in response_lower)
        
        # Base safety score
        safety_score = 1.0 - (harmful_count * 0.2)
        
        return max(0.0, min(1.0, safety_score))
    
    async def _score_bias(self, response: str) -> float:
        """Score response for potential bias."""
        
        # Simplified bias detection (in production, use sophisticated bias detection models)
        bias_indicators = [
            'always', 'never', 'all', 'none', 'every', 'typical', 'naturally',
            'obviously', 'clearly', 'definitely'
        ]
        
        response_lower = response.lower()
        bias_count = sum(1 for indicator in bias_indicators if indicator in response_lower)
        
        # Calculate bias score (lower is better, so invert)
        bias_score = 1.0 - (bias_count * 0.1)
        
        return max(0.0, min(1.0, bias_score))
    
    async def _score_factual_accuracy(self, response: str, reference: Optional[str] = None) -> float:
        """Score factual accuracy of response."""
        
        if not reference:
            # Without reference, use basic fact-checking heuristics
            return await self._basic_fact_check(response)
        
        # Compare against reference
        return await self._compare_factual_content(response, reference)
    
    async def _basic_fact_check(self, response: str) -> float:
        """Basic fact-checking without reference."""
        
        # Look for factual claim indicators
        factual_indicators = ['according to', 'studies show', 'research indicates', 'data suggests']
        speculative_indicators = ['might', 'could', 'possibly', 'perhaps', 'may']
        
        response_lower = response.lower()
        
        factual_count = sum(1 for indicator in factual_indicators if indicator in response_lower)
        speculative_count = sum(1 for indicator in speculative_indicators if indicator in response_lower)
        
        # Prefer responses that acknowledge uncertainty for unverifiable claims
        if factual_count > 0 and speculative_count == 0:
            return 0.7  # Claims without uncertainty markers
        elif speculative_count > 0:
            return 0.9  # Acknowledges uncertainty
        else:
            return 0.8  # Default score
    
    async def _compare_factual_content(self, response: str, reference: str) -> float:
        """Compare factual content against reference."""
        
        # Extract key facts from both responses (simplified)
        response_facts = self._extract_facts(response)
        reference_facts = self._extract_facts(reference)
        
        if not reference_facts:
            return 0.5  # Can't compare without reference facts
        
        # Calculate fact overlap
        matching_facts = len(response_facts & reference_facts)
        total_facts = len(reference_facts)
        
        accuracy_score = matching_facts / total_facts if total_facts > 0 else 0.5
        
        return min(1.0, accuracy_score)
    
    def _extract_facts(self, text: str) -> Set[str]:
        """Extract factual statements from text (simplified)."""
        
        # Very basic fact extraction (in production, use NER and fact extraction models)
        sentences = text.split('.')
        facts = set()
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if any(indicator in sentence for indicator in ['is', 'are', 'was', 'were', 'has', 'have']):
                # Extract key noun phrases (simplified)
                words = sentence.split()
                if len(words) > 3:
                    facts.add(' '.join(words[:4]))  # First 4 words as fact key
        
        return facts


class BenchmarkRunner:
    """
    Automated benchmark execution engine.
    
    Provides comprehensive benchmarking capabilities:
    - Parallel test execution
    - Progress monitoring
    - Error handling and retry logic
    - Cost tracking
    - Performance optimization
    """
    
    def __init__(self, llm_client, audit_logger, quality_scorer: QualityScorer = None):
        """
        Initialize the benchmark runner.
        
        Args:
            llm_client: LLM Gateway client
            audit_logger: Audit logging system
            quality_scorer: Quality scoring system
        """
        self.llm_client = llm_client
        self.audit_logger = audit_logger
        self.quality_scorer = quality_scorer or QualityScorer()
        self.active_executions: Dict[str, BenchmarkExecution] = {}
    
    async def execute_benchmark(
        self, 
        benchmark: BenchmarkTest,
        model_configs: List[ModelConfiguration],
        organization_id: str,
        user_id: str,
        parallel_models: int = 3
    ) -> BenchmarkExecution:
        """
        Execute a benchmark test across multiple models.
        
        Args:
            benchmark: Benchmark test definition
            model_configs: Models to test
            organization_id: Organization ID
            user_id: User executing the benchmark
            parallel_models: Number of models to test in parallel
            
        Returns:
            BenchmarkExecution: Complete execution record
        """
        
        execution_id = str(uuid.uuid4())
        
        execution = BenchmarkExecution(
            id=execution_id,
            benchmark_id=benchmark.id,
            organization_id=organization_id,
            model_configs=model_configs,
            status=EvaluationStatus.PENDING,
            started_at=datetime.utcnow(),
            total_test_cases=len(benchmark.test_cases) * len(model_configs)
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            await self._audit_log(execution, "benchmark_started", {
                "benchmark_name": benchmark.name,
                "model_count": len(model_configs),
                "test_case_count": len(benchmark.test_cases)
            })
            
            execution.status = EvaluationStatus.RUNNING
            
            # Execute benchmark for all models
            await self._execute_benchmark_for_models(
                benchmark, 
                model_configs, 
                execution,
                parallel_models
            )
            
            # Generate performance summaries
            execution.performance_summaries = await self._generate_performance_summaries(
                benchmark, 
                execution.results
            )
            
            execution.status = EvaluationStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            
            await self._audit_log(execution, "benchmark_completed", {
                "total_results": len(execution.results),
                "total_cost": execution.total_cost,
                "execution_time_ms": int((execution.completed_at - execution.started_at).total_seconds() * 1000)
            })
            
        except Exception as e:
            execution.status = EvaluationStatus.FAILED
            execution.completed_at = datetime.utcnow()
            
            logger.error(f"Benchmark execution failed: {execution_id}", exc_info=True)
            
            await self._audit_log(execution, "benchmark_failed", {
                "error_message": str(e)
            })
            
        finally:
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
        
        return execution
    
    async def _execute_benchmark_for_models(
        self,
        benchmark: BenchmarkTest,
        model_configs: List[ModelConfiguration],
        execution: BenchmarkExecution,
        parallel_models: int
    ):
        """Execute benchmark tests for all models."""
        
        # Create semaphore for limiting parallel executions
        semaphore = asyncio.Semaphore(parallel_models)
        
        # Create tasks for all model-test case combinations
        tasks = []
        for model_config in model_configs:
            task = self._execute_model_benchmark(
                benchmark, 
                model_config, 
                execution, 
                semaphore
            )
            tasks.append(task)
        
        # Execute all tasks
        await asyncio.gather(*tasks)
    
    async def _execute_model_benchmark(
        self,
        benchmark: BenchmarkTest,
        model_config: ModelConfiguration,
        execution: BenchmarkExecution,
        semaphore: asyncio.Semaphore
    ):
        """Execute benchmark for a single model."""
        
        async with semaphore:
            for test_case in benchmark.test_cases:
                try:
                    result = await self._execute_single_test_case(
                        benchmark,
                        model_config,
                        test_case,
                        execution
                    )
                    
                    execution.results.append(result)
                    execution.completed_test_cases += 1
                    execution.total_cost += result.metadata.get("cost", 0.0)
                    
                except Exception as e:
                    logger.error(f"Test case failed for model {model_config.name}: {str(e)}")
                    
                    # Create failed result
                    failed_result = EvaluationResult(
                        id=str(uuid.uuid4()),
                        benchmark_id=benchmark.id,
                        model_config=model_config,
                        test_case_id=test_case.get("id", "unknown"),
                        metrics={},
                        metadata={"error": str(e)},
                        passed=False,
                        execution_time_ms=0,
                        error_message=str(e)
                    )
                    
                    execution.results.append(failed_result)
                    execution.completed_test_cases += 1
    
    async def _execute_single_test_case(
        self,
        benchmark: BenchmarkTest,
        model_config: ModelConfiguration,
        test_case: Dict[str, Any],
        execution: BenchmarkExecution
    ) -> EvaluationResult:
        """Execute a single test case for a model."""
        
        start_time = datetime.utcnow()
        
        try:
            # Extract test case data
            prompt = test_case.get("prompt", "")
            expected_output = test_case.get("expected_output")
            test_parameters = test_case.get("parameters", {})
            
            # Merge model parameters with test parameters
            final_parameters = {**model_config.parameters, **test_parameters}
            
            # Make LLM call
            response = await self.llm_client.chat_completion(
                prompt=prompt,
                model=model_config.model_id,
                provider=model_config.provider,
                **final_parameters
            )
            
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Calculate quality scores
            quality_scores = await self.quality_scorer.score_response(
                prompt=prompt,
                response=response.get("response", ""),
                reference=expected_output,
                metrics=benchmark.evaluation_metrics
            )
            
            # Calculate performance metrics
            metrics = {
                "response_time": execution_time_ms,
                "token_count": response.get("tokens", {}).get("total", 0),
                "cost": response.get("cost", 0.0),
                **quality_scores
            }
            
            # Check passing criteria
            passed = self._check_passing_criteria(metrics, benchmark.passing_criteria)
            
            return EvaluationResult(
                id=str(uuid.uuid4()),
                benchmark_id=benchmark.id,
                model_config=model_config,
                test_case_id=test_case.get("id", str(uuid.uuid4())),
                metrics=metrics,
                metadata={
                    "prompt": prompt,
                    "response": response.get("response", ""),
                    "expected_output": expected_output,
                    "model_response": response
                },
                passed=passed,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            raise Exception(f"Test case execution failed: {str(e)}")
    
    def _check_passing_criteria(
        self, 
        metrics: Dict[str, float], 
        criteria: Dict[str, float]
    ) -> bool:
        """Check if test result meets passing criteria."""
        
        for metric_name, threshold in criteria.items():
            if metric_name in metrics:
                if metrics[metric_name] < threshold:
                    return False
        
        return True
    
    async def _generate_performance_summaries(
        self,
        benchmark: BenchmarkTest,
        results: List[EvaluationResult]
    ) -> List[ModelPerformanceSummary]:
        """Generate performance summaries for each model."""
        
        # Group results by model
        model_results = {}
        for result in results:
            model_key = f"{result.model_config.provider}:{result.model_config.model_id}"
            if model_key not in model_results:
                model_results[model_key] = {
                    "config": result.model_config,
                    "results": []
                }
            model_results[model_key]["results"].append(result)
        
        summaries = []
        for model_key, data in model_results.items():
            summary = await self._create_model_summary(
                benchmark,
                data["config"],
                data["results"]
            )
            summaries.append(summary)
        
        return summaries
    
    async def _create_model_summary(
        self,
        benchmark: BenchmarkTest,
        model_config: ModelConfiguration,
        results: List[EvaluationResult]
    ) -> ModelPerformanceSummary:
        """Create performance summary for a single model."""
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Calculate average metrics
        average_metrics = {}
        metric_distributions = {}
        
        if results:
            # Get all metric names
            all_metrics = set()
            for result in results:
                all_metrics.update(result.metrics.keys())
            
            # Calculate averages and distributions
            for metric in all_metrics:
                values = [r.metrics.get(metric, 0.0) for r in results if metric in r.metrics]
                if values:
                    average_metrics[metric] = statistics.mean(values)
                    
                    # Calculate percentiles
                    metric_distributions[metric] = {
                        "p25": np.percentile(values, 25),
                        "p50": np.percentile(values, 50),
                        "p75": np.percentile(values, 75),
                        "p90": np.percentile(values, 90),
                        "p95": np.percentile(values, 95)
                    }
        
        # Calculate cost metrics
        cost_metrics = {
            "total_cost": sum(r.metrics.get("cost", 0.0) for r in results),
            "avg_cost_per_request": average_metrics.get("cost", 0.0),
            "cost_efficiency": self._calculate_cost_efficiency(results)
        }
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(average_metrics)
        
        # Determine performance rating
        performance_rating = self._determine_performance_rating(
            passed_tests / total_tests if total_tests > 0 else 0,
            quality_score,
            average_metrics.get("response_time", 0)
        )
        
        return ModelPerformanceSummary(
            model_config=model_config,
            benchmark_id=benchmark.id,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            pass_rate=passed_tests / total_tests if total_tests > 0 else 0.0,
            average_metrics=average_metrics,
            metric_distributions=metric_distributions,
            cost_metrics=cost_metrics,
            quality_score=quality_score,
            performance_rating=performance_rating
        )
    
    def _calculate_cost_efficiency(self, results: List[EvaluationResult]) -> float:
        """Calculate cost efficiency score."""
        
        if not results:
            return 0.0
        
        # Cost efficiency = quality / cost ratio
        total_quality = sum(
            sum(r.metrics.get(metric, 0.0) for metric in ["coherence", "relevance", "safety"])
            for r in results
        )
        total_cost = sum(r.metrics.get("cost", 0.0) for r in results)
        
        if total_cost > 0:
            return total_quality / total_cost
        
        return 0.0
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from metrics."""
        
        quality_metrics = ["coherence", "relevance", "safety", "factual_accuracy"]
        quality_values = [metrics.get(metric, 0.0) for metric in quality_metrics if metric in metrics]
        
        if quality_values:
            return statistics.mean(quality_values)
        
        return 0.0
    
    def _determine_performance_rating(
        self, 
        pass_rate: float, 
        quality_score: float, 
        avg_response_time: float
    ) -> str:
        """Determine overall performance rating."""
        
        # Normalize response time (assume 1000ms is baseline)
        time_score = max(0, 1 - (avg_response_time / 1000))
        
        # Combined score
        combined_score = (pass_rate * 0.4) + (quality_score * 0.4) + (time_score * 0.2)
        
        if combined_score >= 0.9:
            return "Excellent"
        elif combined_score >= 0.8:
            return "Good"
        elif combined_score >= 0.7:
            return "Fair"
        else:
            return "Poor"
    
    async def _audit_log(
        self, 
        execution: BenchmarkExecution, 
        action: str, 
        metadata: Dict[str, Any]
    ):
        """Log audit events for benchmark execution."""
        
        if self.audit_logger:
            await self.audit_logger.log_event(
                organization_id=execution.organization_id,
                user_id="system",  # System-generated events
                action=action,
                resource_type="benchmark_execution",
                resource_id=execution.id,
                metadata={
                    "benchmark_id": execution.benchmark_id,
                    **metadata
                }
            )


class ModelEvaluator:
    """
    High-level model evaluation system with enterprise capabilities.
    
    Provides comprehensive model evaluation including:
    - Automated benchmarking
    - Performance monitoring
    - Regression detection
    - Comparative analysis
    - Enterprise reporting
    """
    
    def __init__(self, db_session, llm_client, audit_logger):
        """
        Initialize the model evaluator.
        
        Args:
            db_session: Database session
            llm_client: LLM Gateway client
            audit_logger: Audit logging system
        """
        self.db = db_session
        self.llm_client = llm_client
        self.audit_logger = audit_logger
        self.quality_scorer = QualityScorer()
        self.benchmark_runner = BenchmarkRunner(llm_client, audit_logger, self.quality_scorer)
    
    async def create_benchmark(
        self,
        benchmark: BenchmarkTest,
        organization_id: str,
        user_id: str
    ) -> str:
        """Create a new benchmark test."""
        
        # Store benchmark in database
        await self._store_benchmark(benchmark, organization_id, user_id)
        
        # Log benchmark creation
        await self.audit_logger.log_event(
            organization_id=organization_id,
            user_id=user_id,
            action="benchmark_created",
            resource_type="benchmark",
            resource_id=benchmark.id,
            metadata={
                "benchmark_name": benchmark.name,
                "test_type": benchmark.test_type.value,
                "test_case_count": len(benchmark.test_cases)
            }
        )
        
        return benchmark.id
    
    async def run_evaluation(
        self,
        benchmark_id: str,
        model_configs: List[ModelConfiguration],
        organization_id: str,
        user_id: str
    ) -> str:
        """Run a complete model evaluation."""
        
        # Get benchmark configuration
        benchmark = await self._get_benchmark(benchmark_id, organization_id)
        if not benchmark:
            raise ValueError(f"Benchmark not found: {benchmark_id}")
        
        # Execute benchmark
        execution = await self.benchmark_runner.execute_benchmark(
            benchmark,
            model_configs,
            organization_id,
            user_id
        )
        
        # Store execution results
        await self._store_execution(execution)
        
        return execution.id
    
    async def get_evaluation_results(
        self,
        execution_id: str,
        organization_id: str
    ) -> BenchmarkExecution:
        """Get evaluation results."""
        
        execution = await self._get_execution(execution_id, organization_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")
        
        return execution
    
    async def compare_models(
        self,
        model_configs: List[ModelConfiguration],
        benchmark_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Compare multiple models using a benchmark."""
        
        # Get recent executions for these models
        model_summaries = []
        for model_config in model_configs:
            summary = await self._get_latest_model_summary(
                model_config,
                benchmark_id,
                organization_id
            )
            if summary:
                model_summaries.append(summary)
        
        # Generate comparison analysis
        comparison = self._generate_model_comparison(model_summaries)
        
        return comparison
    
    async def detect_performance_regression(
        self,
        model_config: ModelConfiguration,
        benchmark_id: str,
        organization_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """Detect performance regression for a model."""
        
        # Get historical performance data
        historical_data = await self._get_historical_performance(
            model_config,
            benchmark_id,
            organization_id,
            lookback_days
        )
        
        if len(historical_data) < 2:
            return {"regression_detected": False, "reason": "Insufficient historical data"}
        
        # Analyze for regression
        regression_analysis = self._analyze_regression(historical_data)
        
        return regression_analysis
    
    async def get_evaluation_dashboard_data(
        self,
        organization_id: str,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive evaluation dashboard data."""
        
        # Get recent evaluations
        recent_evaluations = await self._get_recent_evaluations(organization_id, time_range_days)
        
        # Get model performance trends
        performance_trends = await self._get_performance_trends(organization_id, time_range_days)
        
        # Get cost analysis
        cost_analysis = await self._get_cost_analysis(organization_id, time_range_days)
        
        return {
            "recent_evaluations": recent_evaluations,
            "performance_trends": performance_trends,
            "cost_analysis": cost_analysis,
            "evaluation_summary": self._generate_evaluation_summary(recent_evaluations)
        }
    
    def _generate_model_comparison(
        self,
        summaries: List[ModelPerformanceSummary]
    ) -> Dict[str, Any]:
        """Generate model comparison analysis."""
        
        if len(summaries) < 2:
            return {"error": "At least 2 models required for comparison"}
        
        # Find best performing model for each metric
        best_models = {}
        for metric in summaries[0].average_metrics.keys():
            best_model = max(summaries, key=lambda s: s.average_metrics.get(metric, 0))
            best_models[metric] = {
                "model": best_model.model_config.name,
                "value": best_model.average_metrics.get(metric, 0)
            }
        
        # Calculate relative performance
        baseline = summaries[0]  # Use first model as baseline
        relative_performance = []
        
        for summary in summaries[1:]:
            relative = {}
            for metric, baseline_value in baseline.average_metrics.items():
                if metric in summary.average_metrics and baseline_value > 0:
                    improvement = ((summary.average_metrics[metric] - baseline_value) / baseline_value) * 100
                    relative[metric] = improvement
            
            relative_performance.append({
                "model": summary.model_config.name,
                "improvements": relative
            })
        
        return {
            "best_models_by_metric": best_models,
            "relative_performance": relative_performance,
            "summary_statistics": self._calculate_comparison_statistics(summaries)
        }
    
    def _analyze_regression(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance data for regression."""
        
        # Sort by timestamp
        historical_data.sort(key=lambda x: x["timestamp"])
        
        # Check for significant degradation in key metrics
        regression_metrics = []
        
        for metric in ["quality_score", "pass_rate", "response_time"]:
            values = [d.get(metric, 0) for d in historical_data if metric in d]
            if len(values) >= 2:
                recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
                historical_avg = statistics.mean(values[:-3]) if len(values) >= 6 else statistics.mean(values[:-1])
                
                # Check for significant degradation (>5% for quality metrics, <5% improvement for response time)
                if metric == "response_time":
                    if recent_avg > historical_avg * 1.1:  # 10% slower is considered regression
                        regression_metrics.append({
                            "metric": metric,
                            "degradation": ((recent_avg - historical_avg) / historical_avg) * 100,
                            "current_value": recent_avg,
                            "historical_average": historical_avg
                        })
                else:
                    if recent_avg < historical_avg * 0.95:  # 5% degradation
                        regression_metrics.append({
                            "metric": metric,
                            "degradation": ((historical_avg - recent_avg) / historical_avg) * 100,
                            "current_value": recent_avg,
                            "historical_average": historical_avg
                        })
        
        return {
            "regression_detected": len(regression_metrics) > 0,
            "regression_metrics": regression_metrics,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_comparison_statistics(
        self,
        summaries: List[ModelPerformanceSummary]
    ) -> Dict[str, Any]:
        """Calculate comparison statistics across models."""
        
        stats = {}
        
        # Aggregate metrics across all models
        all_metrics = set()
        for summary in summaries:
            all_metrics.update(summary.average_metrics.keys())
        
        for metric in all_metrics:
            values = [s.average_metrics.get(metric, 0) for s in summaries if metric in s.average_metrics]
            if values:
                stats[metric] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values)
                }
        
        return stats
    
    def _generate_evaluation_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of recent evaluations."""
        
        if not evaluations:
            return {"total_evaluations": 0}
        
        total_evaluations = len(evaluations)
        successful_evaluations = sum(1 for e in evaluations if e.get("status") == "completed")
        
        return {
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0,
            "avg_execution_time": statistics.mean([e.get("execution_time_ms", 0) for e in evaluations]) if evaluations else 0
        }
    
    # Database interface methods (to be implemented with actual DB)
    async def _store_benchmark(
        self, 
        benchmark: BenchmarkTest, 
        organization_id: str, 
        user_id: str
    ):
        """Store benchmark in database."""
        pass
    
    async def _get_benchmark(
        self, 
        benchmark_id: str, 
        organization_id: str
    ) -> Optional[BenchmarkTest]:
        """Get benchmark from database."""
        pass
    
    async def _store_execution(self, execution: BenchmarkExecution):
        """Store execution in database."""
        pass
    
    async def _get_execution(
        self, 
        execution_id: str, 
        organization_id: str
    ) -> Optional[BenchmarkExecution]:
        """Get execution from database."""
        pass
    
    async def _get_latest_model_summary(
        self,
        model_config: ModelConfiguration,
        benchmark_id: str,
        organization_id: str
    ) -> Optional[ModelPerformanceSummary]:
        """Get latest performance summary for a model."""
        pass
    
    async def _get_historical_performance(
        self,
        model_config: ModelConfiguration,
        benchmark_id: str,
        organization_id: str,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Get historical performance data."""
        pass
    
    async def _get_recent_evaluations(
        self, 
        organization_id: str, 
        time_range_days: int
    ) -> List[Dict[str, Any]]:
        """Get recent evaluations."""
        pass
    
    async def _get_performance_trends(
        self, 
        organization_id: str, 
        time_range_days: int
    ) -> Dict[str, Any]:
        """Get performance trends."""
        pass
    
    async def _get_cost_analysis(
        self, 
        organization_id: str, 
        time_range_days: int
    ) -> Dict[str, Any]:
        """Get cost analysis."""
        pass