"""
Multi-LLM Tracer Performance Benchmark Package

This package provides a comprehensive, modular benchmark suite for HoneyHive
tracer performance testing across multiple LLM providers. Implements teammate
feedback requirements including north-star metrics, conversation simulation,
and A/B testing harness.

Main Components:
- Core: Configuration, metrics, and benchmark runner
- Providers: LLM provider implementations (OpenAI, Anthropic)
- Monitoring: Memory, network, and trace validation
- Scenarios: Conversation templates and prompt generation
- Reporting: Metrics calculation and report formatting

Example:
    >>> from benchmark.core.config import BenchmarkConfig
    >>> from benchmark.core.benchmark_runner import TracerBenchmark
    >>> 
    >>> config = BenchmarkConfig(operations=50)
    >>> benchmark = TracerBenchmark(config)
    >>> results = benchmark.run_full_benchmark()
"""

from .core.config import BenchmarkConfig
from .core.metrics import PerformanceMetrics
from .core.benchmark_runner import TracerBenchmark
from .reporting.metrics_calculator import MetricsCalculator, NorthStarMetrics
from .reporting.formatter import ReportFormatter
from .testing.ab_testing_harness import ABTestingHarness, ABTestResult
from .testing.synthetic_spans import SyntheticSpanGenerator, SyntheticSpanDAG
from .testing.load_testing import LoadTestRunner, LoadTestConfig
from .testing.comprehensive_metrics import ComprehensiveMetricsCalculator, ComprehensiveMetricsReport

# Version information
__version__ = "1.0.0"
__author__ = "HoneyHive AI"
__description__ = "Multi-LLM Tracer Performance Benchmark Suite"

# Main exports
__all__ = [
    # Core components
    "BenchmarkConfig",
    "PerformanceMetrics", 
    "TracerBenchmark",
    
    # Reporting components
    "MetricsCalculator",
    "NorthStarMetrics",
    "ReportFormatter",
    
    # Advanced testing components
    "ABTestingHarness",
    "ABTestResult",
    "SyntheticSpanGenerator",
    "SyntheticSpanDAG",
    "LoadTestRunner",
    "LoadTestConfig",
    "ComprehensiveMetricsCalculator",
    "ComprehensiveMetricsReport",
    
    # Package metadata
    "__version__",
    "__author__",
    "__description__",
]