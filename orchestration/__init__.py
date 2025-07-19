"""
Phase 3: Orchestration & Evaluation Module

This module provides enterprise-grade orchestration and evaluation capabilities
including workflow management, A/B testing, and model performance evaluation.

Components:
- Workflow Builder: Visual workflow designer and execution engine
- A/B Testing: Statistical testing framework for model comparison
- Model Evaluation: Automated benchmarking and performance analysis
"""

from .workflow_engine import WorkflowEngine, WorkflowExecutor
from .ab_testing import ABTestManager, StatisticalAnalyzer
from .model_evaluator import ModelEvaluator, BenchmarkRunner
from .workflow_builder import WorkflowBuilder, WorkflowValidator

__all__ = [
    'WorkflowEngine',
    'WorkflowExecutor', 
    'ABTestManager',
    'StatisticalAnalyzer',
    'ModelEvaluator',
    'BenchmarkRunner',
    'WorkflowBuilder',
    'WorkflowValidator'
]

__version__ = "1.0.0"