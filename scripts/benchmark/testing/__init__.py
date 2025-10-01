"""
Advanced testing components for A/B testing, synthetic spans, and load testing.

This module provides specialized testing frameworks for comprehensive tracer
evaluation beyond basic performance benchmarks.
"""

from .ab_testing_harness import ABTestingHarness, ABTestResult
from .synthetic_spans import SyntheticSpanGenerator, SyntheticSpanDAG
from .load_testing import LoadTestRunner, LoadTestConfig
from .comprehensive_metrics import (
    ComprehensiveMetricsCalculator, 
    ComprehensiveMetricsReport,
    CoreEfficiencyMetrics,
    AccuracyFidelityMetrics,
    ReliabilityLossMetrics,
    ContextCorrelationMetrics,
    CostPayloadMetrics
)

__all__ = [
    "ABTestingHarness", 
    "ABTestResult",
    "SyntheticSpanGenerator", 
    "SyntheticSpanDAG",
    "LoadTestRunner", 
    "LoadTestConfig",
    "ComprehensiveMetricsCalculator",
    "ComprehensiveMetricsReport",
    "CoreEfficiencyMetrics",
    "AccuracyFidelityMetrics",
    "ReliabilityLossMetrics",
    "ContextCorrelationMetrics",
    "CostPayloadMetrics"
]
