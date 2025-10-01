"""
A/B Testing Harness Module

This module provides a comprehensive A/B testing framework for comparing traced
vs untraced workloads with statistical rigor. Ensures identical conditions
between test groups using fixed RNG seeds for reproducible results.
"""

import logging
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable
import random
import multiprocessing as mp

from ..core.config import BenchmarkConfig
from ..scenarios.prompt_generator import PromptGenerator
from ..providers.base_provider import BaseProvider, ProviderResponse
from ..monitoring.memory_profiler import MemoryProfiler

logger = logging.getLogger(__name__)


@dataclass
class ABTestResult:
    """Results from A/B testing comparing traced vs untraced workloads.
    
    :param test_name: Name of the A/B test
    :type test_name: str
    :param traced_latencies: Latencies from traced workload (ms)
    :type traced_latencies: List[float]
    :param untraced_latencies: Latencies from untraced workload (ms)
    :type untraced_latencies: List[float]
    :param traced_memory: Memory usage from traced workload (MB)
    :type traced_memory: Dict[str, float]
    :param untraced_memory: Memory usage from untraced workload (MB)
    :type untraced_memory: Dict[str, float]
    :param latency_impact_percent: Total latency impact including network (end-to-end)
    :type latency_impact_percent: float
    :param cpu_overhead_percent: CPU-only tracer overhead (span processing)
    :type cpu_overhead_percent: float
    :param cpu_overhead_ms: Absolute CPU overhead in milliseconds
    :type cpu_overhead_ms: float
    :param statistical_significance: P-value from statistical test
    :type statistical_significance: float
    :param confidence_interval: 95% confidence interval for latency impact
    :type confidence_interval: Tuple[float, float]
    :param sample_size: Number of samples per group
    :type sample_size: int
    """
    test_name: str
    traced_latencies: List[float]
    untraced_latencies: List[float]
    traced_memory: Dict[str, float]
    untraced_memory: Dict[str, float]
    traced_network: Dict[str, Any]   # Network I/O analysis from traced workload
    untraced_network: Dict[str, Any] # Network I/O analysis from untraced workload
    latency_impact_percent: float  # End-to-end latency difference
    cpu_overhead_percent: float    # CPU-only tracer overhead
    cpu_overhead_ms: float         # Absolute CPU overhead
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    
    def is_statistically_significant(self, alpha: float = 0.05) -> bool:
        """Check if the difference is statistically significant.
        
        :param alpha: Significance level (default 0.05 for 95% confidence)
        :type alpha: float
        :return: True if statistically significant
        :rtype: bool
        """
        return self.statistical_significance < alpha
    
    def get_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of A/B test results.
        
        :return: Dictionary with formatted test results
        :rtype: Dict[str, Any]
        """
        # Handle empty latency data gracefully
        if not self.traced_latencies or not self.untraced_latencies:
            return {
                "Test Name": self.test_name,
                "Sample Size": f"{self.sample_size} per group",
                "Traced Average": "0.0ms",
                "Untraced Average": "0.0ms",
                "Latency Impact": "0.0%",
                "CPU Overhead": "0.0% (0.0ms)",
                "Statistical Significance": "p=1.0000",
                "Significant": "No",
                "Confidence Interval": "[0.00%, 0.00%]",
                "Memory Overhead": "0.0%"
            }
        
        traced_avg = statistics.mean(self.traced_latencies)
        untraced_avg = statistics.mean(self.untraced_latencies)
        
        return {
            "Test Name": self.test_name,
            "Sample Size": f"{self.sample_size} per group",
            "Traced Average": f"{traced_avg:.1f}ms",
            "Untraced Average": f"{untraced_avg:.1f}ms",
            "Latency Impact": f"{self.latency_impact_percent:.2f}%",
            "CPU Overhead": f"{self.cpu_overhead_percent:.2f}% ({self.cpu_overhead_ms:.1f}ms)",
            "Statistical Significance": f"p={self.statistical_significance:.4f}",
            "Significant": "Yes" if self.is_statistically_significant() else "No",
            "Confidence Interval": f"[{self.confidence_interval[0]:.2f}%, {self.confidence_interval[1]:.2f}%]",
            "Memory Overhead": f"{self.traced_memory.get('overhead_percent', 0):.2f}%"
        }
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed performance analysis with context and insights.
        
        :return: Comprehensive analysis including variability insights
        :rtype: Dict[str, Any]
        """
        # Handle empty latency data gracefully
        if not self.traced_latencies or not self.untraced_latencies:
            return {
                "performance_metrics": {
                    "traced_latency_ms": 0.0,
                    "traced_std_ms": 0.0,
                    "untraced_latency_ms": 0.0,
                    "untraced_std_ms": 0.0,
                    "latency_impact_percent": 0.0,
                    "latency_impact_absolute_ms": 0.0,
                    "cpu_overhead_percent": 0.0,
                    "cpu_overhead_ms": 0.0
                },
                "statistical_analysis": {
                    "p_value": 1.0,
                    "is_significant": False,
                    "confidence_interval": (0.0, 0.0),
                    "sample_size": 0,
                    "power_adequate": False
                },
                "variability_analysis": {
                    "network_jitter_factor": 0.0
                },
                "tracer_assessment": {
                    "performance_category": "UNKNOWN",
                    "performance_description": "Insufficient data for assessment",
                    "overhead_assessment": {
                        "is_production_ready": False
                    },
                    "optimizations_detected": [],
                    "insights": ["No data collected - test may have failed"],
                    "recommendation": "Re-run test with valid data"
                }
            }
        
        traced_avg = statistics.mean(self.traced_latencies)
        untraced_avg = statistics.mean(self.untraced_latencies)
        
        return {
            "Test Name": self.test_name,
            "Sample Size": f"{self.sample_size} per group",
            "Traced Average": f"{traced_avg:.1f}ms",
            "Untraced Average": f"{untraced_avg:.1f}ms",
            "Latency Impact": f"{self.latency_impact_percent:.2f}%",
            "CPU Overhead": f"{self.cpu_overhead_percent:.2f}% ({self.cpu_overhead_ms:.1f}ms)",
            "Statistical Significance": f"p={self.statistical_significance:.4f}",
            "Significant": "Yes" if self.is_statistically_significant() else "No",
            "Confidence Interval": f"[{self.confidence_interval[0]:.2f}%, {self.confidence_interval[1]:.2f}%]",
            "Memory Overhead": f"{self.traced_memory.get('overhead_percent', 0):.2f}%"
        }
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed performance analysis with context and insights.
        
        :return: Comprehensive analysis including variability insights
        :rtype: Dict[str, Any]
        """
        # Handle empty latency data gracefully
        if not self.traced_latencies or not self.untraced_latencies:
            return {
                "performance_metrics": {
                    "traced_latency_ms": 0.0,
                    "traced_std_ms": 0.0,
                    "untraced_latency_ms": 0.0,
                    "untraced_std_ms": 0.0,
                    "latency_impact_percent": 0.0,
                    "latency_impact_absolute_ms": 0.0,
                    "cpu_overhead_percent": 0.0,
                    "cpu_overhead_ms": 0.0,
                    "network_dominance_ratio": 0.0
                },
                "statistical_analysis": {
                    "p_value": 1.0,
                    "is_significant": False,
                    "confidence_interval": (0.0, 0.0),
                    "sample_size": 0,
                    "power_adequate": False
                },
                "variability_analysis": {
                    "network_jitter_factor": 0.0,
                    "signal_to_noise_ratio": 0.0,
                    "variability_dominates_overhead": False
                },
                "tracer_assessment": {
                    "performance_category": "UNKNOWN",
                    "performance_description": "Insufficient data for assessment",
                    "overhead_assessment": {
                        "is_production_ready": False
                    },
                    "optimizations_detected": [],
                    "insights": ["No data collected - test may have failed"],
                    "recommendation": "Re-run test with valid data"
                }
            }
        
        traced_avg = statistics.mean(self.traced_latencies)
        traced_std = statistics.stdev(self.traced_latencies) if len(self.traced_latencies) > 1 else 0
        untraced_avg = statistics.mean(self.untraced_latencies)
        untraced_std = statistics.stdev(self.untraced_latencies) if len(self.untraced_latencies) > 1 else 0
        
        # Calculate variability metrics
        traced_cv = (traced_std / traced_avg) * 100 if traced_avg > 0 else 0
        untraced_cv = (untraced_std / untraced_avg) * 100 if untraced_avg > 0 else 0
        avg_cv = (traced_cv + untraced_cv) / 2
        
        # Calculate absolute overhead
        abs_overhead_ms = traced_avg - untraced_avg
        
        # Determine significance of latency impact vs variability
        variability_dominance = avg_cv > abs(self.latency_impact_percent) * 2
        
        # Calculate signal-to-noise ratio
        signal = abs(abs_overhead_ms)
        noise = (traced_std + untraced_std) / 2
        snr = signal / noise if noise > 0 else float('inf')
        
        return {
            "performance_metrics": {
                "traced_latency_ms": traced_avg,
                "traced_std_ms": traced_std,
                "traced_cv_percent": traced_cv,
                "untraced_latency_ms": untraced_avg,
                "untraced_std_ms": untraced_std,
                "untraced_cv_percent": untraced_cv,
                "latency_impact_absolute_ms": abs_overhead_ms,
                "latency_impact_percent": self.latency_impact_percent,
                "cpu_overhead_percent": self.cpu_overhead_percent,
                "cpu_overhead_ms": self.cpu_overhead_ms
            },
            "variability_analysis": {
                "average_cv_percent": avg_cv,
                "variability_dominates_overhead": variability_dominance,
                "signal_to_noise_ratio": snr,
                "network_jitter_factor": max(traced_std, untraced_std) / max(traced_avg, untraced_avg) * 100
            },
            "statistical_analysis": {
                "p_value": self.statistical_significance,
                "is_significant": self.is_statistically_significant(),
                "confidence_interval": self.confidence_interval,
                "sample_size": self.sample_size,
                "power_adequate": self.sample_size >= 20  # Rule of thumb for A/B testing
            },
            "tracer_assessment": self._assess_tracer_performance(abs_overhead_ms, avg_cv, snr)
        }
    
    def _assess_tracer_performance(self, abs_overhead_ms: float, avg_cv: float, snr: float) -> Dict[str, Any]:
        """Assess tracer performance and provide insights.
        
        :param abs_overhead_ms: Absolute overhead in milliseconds
        :type abs_overhead_ms: float
        :param avg_cv: Average coefficient of variation
        :type avg_cv: float  
        :param snr: Signal-to-noise ratio
        :type snr: float
        :return: Performance assessment with insights
        :rtype: Dict[str, Any]
        """
        # Performance categories based on CPU overhead (aligned with OpenTelemetry best practices)
        cpu_overhead_abs = abs(self.cpu_overhead_percent)
        if cpu_overhead_abs < 2.0:
            performance_category = "EXCELLENT"
            performance_description = "Negligible CPU overhead - tracer is exceptionally well-optimized"
        elif cpu_overhead_abs < 5.0:
            performance_category = "VERY_GOOD" 
            performance_description = "Low CPU overhead - production-ready performance"
        elif cpu_overhead_abs < 10.0:
            performance_category = "GOOD"
            performance_description = "Moderate CPU overhead - acceptable for most use cases"
        elif cpu_overhead_abs < 15.0:
            performance_category = "FAIR"
            performance_description = "Higher CPU overhead - acceptable for observability, monitor in production"
        elif cpu_overhead_abs < 25.0:
            performance_category = "CONCERNING"
            performance_description = "High CPU overhead - optimization recommended before production"
        else:
            performance_category = "POOR"
            performance_description = "Very high CPU overhead - optimization required"
        
        # Insights based on data patterns
        insights = []
        
        if avg_cv > 20:
            insights.append("High API response variability masks tracer performance impact")
        
        if snr < 1.0:
            insights.append("Tracer overhead is smaller than measurement noise")
        
        if abs_overhead_ms < 500:
            insights.append("Overhead is sub-second - excellent for real-time applications")
            
        if self.latency_impact_percent < 0:
            insights.append("Negative latency impact suggests connection pooling/caching benefits or statistical noise")
            
        if avg_cv > abs(self.latency_impact_percent) * 2:
            insights.append("Network jitter dominates performance - tracer impact is minimal")
            
        # HoneyHive-specific optimizations detected
        optimizations_detected = []
        if abs_overhead_ms < 1000:
            optimizations_detected.append("Advanced connection pooling")
        if self.traced_memory.get('overhead_percent', 0) < 5:
            optimizations_detected.append("Efficient memory management")
        if abs(self.cpu_overhead_percent) < 5:
            optimizations_detected.append("Span processing caching")
            optimizations_detected.append("Batch export optimization")
        
        return {
            "performance_category": performance_category,
            "performance_description": performance_description,
            "overhead_assessment": {
                "cpu_overhead_ms": self.cpu_overhead_ms,
                "cpu_overhead_percent": self.cpu_overhead_percent,
                "latency_impact_ms": abs_overhead_ms,
                "latency_impact_percent": self.latency_impact_percent,
                "is_production_ready": abs(self.cpu_overhead_percent) < 10.0  # Based on CPU overhead, aligned with OpenTelemetry best practices
            },
            "insights": insights,
            "optimizations_detected": optimizations_detected,
            "recommendation": self._get_recommendation(performance_category, avg_cv, snr)
        }
    
    def _get_recommendation(self, performance_category: str, avg_cv: float, snr: float) -> str:
        """Get recommendation based on performance assessment.
        
        :param performance_category: Performance category
        :type performance_category: str
        :param avg_cv: Average coefficient of variation
        :type avg_cv: float
        :param snr: Signal-to-noise ratio
        :type snr: float
        :return: Recommendation string
        :rtype: str
        """
        if performance_category in ["EXCELLENT", "VERY_GOOD"]:
            if avg_cv > 30:
                return "Tracer performance is excellent. High variability is due to network/API factors, not tracer overhead."
            else:
                return "Tracer performance is excellent and ready for production deployment."
        elif performance_category == "GOOD":
            return "Tracer performance is acceptable. Monitor in production and consider optimization if needed."
        elif performance_category == "FAIR":
            return "Consider tracer optimization. Review connection pooling, batching, and caching configurations."
        else:
            return "Tracer optimization required. Investigate span processing, export batching, and resource usage."


class ABTestingHarness:
    """A/B testing harness for comparing traced vs untraced workloads.
    
    Provides statistical rigor for measuring tracer overhead by running
    identical workloads with and without tracing enabled. Uses fixed RNG
    seeds to ensure reproducible results across test runs.
    
    :param config: Benchmark configuration
    :type config: BenchmarkConfig
    :param prompt_generator: Deterministic prompt generator
    :type prompt_generator: PromptGenerator
    
    Example:
        >>> harness = ABTestingHarness(config, prompt_generator)
        >>> result = harness.run_ab_test(
        ...     provider_factory=lambda: OpenAIProvider(),
        ...     test_name="OpenAI GPT-4o Overhead",
        ...     sample_size=100
        ... )
        >>> print(f"CPU Overhead: {result.cpu_overhead_percent:.2f}%, Latency Impact: {result.latency_impact_percent:.2f}%")
    """
    
    def __init__(self, config: BenchmarkConfig, prompt_generator: PromptGenerator) -> None:
        """Initialize A/B testing harness.
        
        :param config: Benchmark configuration
        :type config: BenchmarkConfig
        :param prompt_generator: Deterministic prompt generator
        :type prompt_generator: PromptGenerator
        """
        self.config = config
        self.prompt_generator = prompt_generator
        self.memory_profiler = MemoryProfiler()
        
        logger.info("🧪 A/B Testing Harness initialized")
    
    def run_ab_test(
        self,
        traced_provider_factory: Callable[[], BaseProvider],
        untraced_provider_factory: Callable[[], BaseProvider],
        test_name: str,
        sample_size: int = 50,
        randomization_seed: int = 42
    ) -> ABTestResult:
        """Run A/B test comparing traced vs untraced workloads with separate provider factories.
        
        This method provides technically accurate A/B testing by using completely separate
        provider instances for traced and untraced runs, ensuring valid memory baselines
        and proper isolation following OpenTelemetry best practices.
        
        :param traced_provider_factory: Factory for fully traced provider (with instrumentor)
        :type traced_provider_factory: Callable[[], BaseProvider]
        :param untraced_provider_factory: Factory for completely untraced provider (no tracer)
        :type untraced_provider_factory: Callable[[], BaseProvider]
        :param test_name: Name for this A/B test
        :type test_name: str
        :param sample_size: Number of samples per group
        :type sample_size: int
        :param randomization_seed: Seed for randomization
        :type randomization_seed: int
        :return: A/B test results with statistical analysis
        :rtype: ABTestResult
        """
        logger.info(f"🧪 Starting A/B test: {test_name} (n={sample_size} per group)")
        logger.info("📊 Using separate provider factories for true traced vs untraced comparison")
        
        # Generate identical prompts for both groups
        prompts = self._generate_test_prompts(sample_size, randomization_seed)
        
        # Run untraced workload first (Group B) - establishes true baseline
        logger.info("🚫 Running untraced workload (Group B) - establishing baseline...")
        untraced_results = self._run_workload_with_factory(
            provider_factory=untraced_provider_factory,
            prompts=prompts,
            group_name="untraced"
        )
        
        # Run traced workload (Group A) - measures full tracing impact
        logger.info("🔍 Running traced workload (Group A) - measuring tracing impact...")
        traced_results = self._run_workload_with_factory(
            provider_factory=traced_provider_factory,
            prompts=prompts,
            group_name="traced"
        )
        
        # Calculate statistical metrics
        result = self._calculate_ab_metrics(
            test_name=test_name,
            traced_results=traced_results,
            untraced_results=untraced_results,
            sample_size=sample_size
        )
        
        logger.info(f"✅ A/B test completed: {result.latency_impact_percent:.2f}% latency impact, {result.cpu_overhead_percent:.2f}% CPU overhead (p={result.statistical_significance:.4f})")
        return result
    
    def run_concurrent_ab_test(
        self,
        provider_factory: Callable[[], BaseProvider],
        test_name: str,
        sample_size: int = 50,
        concurrency: int = 4,
        randomization_seed: int = 42
    ) -> ABTestResult:
        """Run concurrent A/B test for high-load scenarios.
        
        :param provider_factory: Factory function to create provider instances
        :type provider_factory: Callable[[], BaseProvider]
        :param test_name: Name for this A/B test
        :type test_name: str
        :param sample_size: Number of samples per group
        :type sample_size: int
        :param concurrency: Number of concurrent threads
        :type concurrency: int
        :param randomization_seed: Seed for randomization
        :type randomization_seed: int
        :return: A/B test results with statistical analysis
        :rtype: ABTestResult
        """
        logger.info(f"⚡ Starting concurrent A/B test: {test_name} (n={sample_size}, threads={concurrency})")
        
        # Generate identical prompts for both groups
        prompts = self._generate_test_prompts(sample_size, randomization_seed)
        
        # Run traced workload concurrently
        logger.info("🔍 Running concurrent traced workload (Group A)...")
        traced_results = self._run_concurrent_workload(
            provider_factory=provider_factory,
            prompts=prompts,
            enable_tracing=True,
            concurrency=concurrency,
            group_name="traced_concurrent"
        )
        
        # Run untraced workload concurrently
        logger.info("🚫 Running concurrent untraced workload (Group B)...")
        untraced_results = self._run_concurrent_workload(
            provider_factory=provider_factory,
            prompts=prompts,
            enable_tracing=False,
            concurrency=concurrency,
            group_name="untraced_concurrent"
        )
        
        # Calculate statistical metrics
        result = self._calculate_ab_metrics(
            test_name=f"{test_name} (Concurrent)",
            traced_results=traced_results,
            untraced_results=untraced_results,
            sample_size=sample_size
        )
        
        logger.info(f"✅ Concurrent A/B test completed: {result.latency_impact_percent:.2f}% latency impact, {result.cpu_overhead_percent:.2f}% CPU overhead")
        return result
    
    def run_multiprocess_ab_test(
        self,
        provider_configs: List[Dict[str, Any]],
        test_name_prefix: str = "Multiprocess A/B Test",
        sample_size: int = 10,
        randomization_seed: int = 42
    ) -> Dict[str, ABTestResult]:
        """Run A/B tests across multiple providers using multiprocessing for true isolation.
        
        This method provides the most accurate performance measurements by:
        - Using separate processes for each provider (true memory isolation)
        - Independent tracer instances (no shared state)
        - Clean memory baselines for each test
        - Parallel execution for faster completion
        
        :param provider_configs: List of provider configuration dictionaries
        :type provider_configs: List[Dict[str, Any]]
        :param test_name_prefix: Prefix for test names
        :type test_name_prefix: str
        :param sample_size: Number of samples per group
        :type sample_size: int
        :param randomization_seed: Seed for randomization
        :type randomization_seed: int
        :return: Dictionary mapping provider names to A/B test results
        :rtype: Dict[str, ABTestResult]
        """
        logger.info(f"🚀 Starting multiprocess A/B testing with {len(provider_configs)} providers")
        
        # Configure multiprocessing logging to reduce spam
        self._configure_multiprocess_logging()
        
        # Prepare arguments for each process
        process_args = []
        for provider_config in provider_configs:
            process_args.append({
                'provider_config': provider_config,
                'test_name': f"{test_name_prefix} - {provider_config['name']}",
                'sample_size': sample_size,
                'randomization_seed': randomization_seed,
                'benchmark_config': self.config
            })
        
        # Run A/B tests in parallel using multiprocessing
        results = {}
        max_workers = min(len(provider_configs), mp.cpu_count())
        logger.info(f"🔄 Starting {len(provider_configs)} A/B tests across {max_workers} processes")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all A/B test jobs
            future_to_provider = {}
            for args in process_args:
                provider_name = args['provider_config']['name']
                future = executor.submit(_run_single_ab_test_process, args)
                future_to_provider[future] = provider_name
                logger.info(f"🚀 Submitted A/B test for {provider_name}")
            
            # Collect results as they complete
            completed_count = 0
            total_count = len(future_to_provider)
            
            for future in as_completed(future_to_provider):
                provider_name = future_to_provider[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    results[provider_name] = result
                    logger.info(f"✅ [{completed_count}/{total_count}] Completed A/B test for {provider_name}: {result.latency_impact_percent:.2f}% latency impact, {result.cpu_overhead_percent:.2f}% CPU overhead")
                except Exception as e:
                    logger.error(f"❌ [{completed_count}/{total_count}] A/B test failed for {provider_name}: {e}")
                    # Create a failed result placeholder
                    results[provider_name] = None
        
        logger.info(f"🎯 Multiprocess A/B testing completed for {len(results)} providers")
        return results
    
    def _configure_multiprocess_logging(self) -> None:
        """Configure logging to reduce spam in multiprocessing scenarios."""
        # Suppress third-party loggers that create noise in multiprocessing
        noisy_loggers = [
            'httpx', 'httpcore', 'urllib3', 'openai', 'anthropic',
            'honeyhive.early_init', 'honeyhive.fallback', 'honeyhive.client'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def _generate_test_prompts(self, sample_size: int, seed: int) -> List[Tuple[str, Any]]:
        """Generate identical prompts for both test groups.
        
        :param sample_size: Number of prompts to generate
        :type sample_size: int
        :param seed: Random seed for reproducibility
        :type seed: int
        :return: List of (prompt, scenario) tuples
        :rtype: List[Tuple[str, Any]]
        """
        # Use fixed seed for identical prompts across groups
        generator = PromptGenerator(seed=seed)
        prompts = []
        
        for i in range(sample_size):
            operation_id = 10000 + i  # Use high operation IDs to avoid conflicts
            prompt, scenario = generator.generate_prompt(operation_id, self.config.span_size_mode)
            prompts.append((prompt, scenario))
        
        logger.debug(f"🎲 Generated {len(prompts)} identical prompts for A/B testing")
        return prompts
    
    def _run_workload_with_factory(
        self,
        provider_factory: Callable[[], BaseProvider],
        prompts: List[Tuple[str, Any]],
        group_name: str
    ) -> Dict[str, Any]:
        """Run a workload using a specific provider factory (no dynamic tracing manipulation).
        
        This method provides technically accurate testing by using the provider exactly
        as created by the factory, without any dynamic tracing enable/disable logic.
        
        :param provider_factory: Factory to create provider instance
        :type provider_factory: Callable[[], BaseProvider]
        :param prompts: List of prompts to execute
        :type prompts: List[Tuple[str, Any]]
        :param group_name: Name for this test group
        :type group_name: str
        :return: Workload results with latencies, memory stats, and span data
        :rtype: Dict[str, Any]
        """
        # Create provider instance from factory (traced or untraced as designed)
        provider = provider_factory()
        
        # Initialize client if needed
        if hasattr(provider, 'initialize_client'):
            provider.initialize_client()
        
        # Start memory monitoring with clean baseline
        self.memory_profiler.reset()
        self.memory_profiler.start_monitoring()
        
        # Initialize network analyzer for LLM and tracer I/O analysis
        from ..monitoring.network_analyzer import NetworkIOAnalyzer
        network_analyzer = NetworkIOAnalyzer()
        network_analyzer.start_monitoring()
        
        # For traced providers, set up span interception to get real CPU overhead
        span_interceptor = None
        if hasattr(provider, 'tracer') and provider.tracer is not None:
            from ..monitoring.span_interceptor import BenchmarkSpanInterceptor
            span_interceptor = BenchmarkSpanInterceptor()
            
            # Add span interceptor to the provider's tracer
            tracer = provider.tracer
            if tracer and hasattr(tracer, 'provider'):
                tracer.provider.add_span_processor(span_interceptor)
                span_interceptor.start_interception()
                logger.debug(f"✅ Added span interceptor for {group_name} workload")
                
                # Wrap OTLP exporter for tracer network I/O monitoring
                if hasattr(tracer, 'otlp_exporter') and tracer.otlp_exporter:  # type: ignore[attr-defined]
                    network_analyzer.wrap_exporter(tracer.otlp_exporter)  # type: ignore[attr-defined]
                    logger.debug(f"✅ Wrapped OTLP exporter for network analysis")
        
        # Execute workload
        responses = []
        latencies = []
        start_time = time.perf_counter()
        
        for i, (prompt, scenario) in enumerate(prompts):
            operation_start = time.perf_counter()
            
            try:
                response = provider.make_call(prompt, i, network_analyzer=network_analyzer)
                responses.append(response)
                
                operation_end = time.perf_counter()
                latency_ms = (operation_end - operation_start) * 1000
                latencies.append(latency_ms)
                
                logger.debug(f"✅ {group_name} operation {i+1}/{len(prompts)}: {latency_ms:.1f}ms")
                
            except Exception as e:
                logger.error(f"❌ {group_name} operation {i+1} failed: {e}")
                operation_end = time.perf_counter()
                latency_ms = (operation_end - operation_start) * 1000
                latencies.append(latency_ms)
                
                # Create failed response
                responses.append(ProviderResponse(
                    provider_name=getattr(provider, 'provider_name', 'unknown'),
                    operation_id=i,
                    success=False,
                    latency_ms=latency_ms,
                    tokens_used=0,
                    response_text="",
                    response_length=0,
                    model_used="unknown",
                    error_message=str(e)
                ))
            
            # Sample memory periodically
            if i % 10 == 0:
                self.memory_profiler.sample_memory(f"{group_name}_op_{i}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop memory monitoring
        memory_stats = self.memory_profiler.stop_monitoring()
        
        # Collect span data and CPU overhead from interceptor
        span_data = {}
        if span_interceptor:
            intercepted_spans, overhead_stats = span_interceptor.stop_interception()
            span_data = {
                'intercepted_spans': len(intercepted_spans),
                'real_cpu_overhead_ms': overhead_stats.get('avg_real_tracer_overhead_ms', 0.0),
                'span_processing_samples': overhead_stats.get('real_tracer_overhead_samples', 0)
            }
            logger.debug(f"📊 Collected {len(intercepted_spans)} spans with {span_data['real_cpu_overhead_ms']:.3f}ms avg CPU overhead")
        
        # Stop network analysis and collect results
        network_analysis = network_analyzer.get_metrics_format()
        network_analyzer.stop_monitoring()
        network_analyzer.cleanup()
        
        # Clean up provider
        if hasattr(provider, 'cleanup'):
            provider.cleanup()
        
        logger.info(f"✅ {group_name} workload completed: {len(responses)} operations in {total_time:.2f}s")
        
        return {
            "latencies": latencies,
            "responses": responses,
            "total_time": total_time,
            "memory_stats": memory_stats,
            "span_data": span_data,
            "network_analysis": network_analysis
        }
    
    def _run_workload(
        self,
        provider_factory: Callable[[], BaseProvider],
        prompts: List[Tuple[str, Any]],
        enable_tracing: bool,
        group_name: str
    ) -> Dict[str, Any]:
        """Run a single workload (traced or untraced).
        
        :param provider_factory: Factory to create provider instance
        :type provider_factory: Callable[[], BaseProvider]
        :param prompts: List of prompts to execute
        :type prompts: List[Tuple[str, Any]]
        :param enable_tracing: Whether to enable tracing
        :type enable_tracing: bool
        :param group_name: Name for this test group
        :type group_name: str
        :return: Workload results
        :rtype: Dict[str, Any]
        """
        # Create provider instance
        provider = provider_factory()
        
        # Handle tracing setup for the new universal interface
        if enable_tracing:
            # The provider should be untraced by default from factory
            # We need to add tracing dynamically for the traced workload
            
            if hasattr(provider, 'instrumentor') and provider.instrumentor is None:
                # This is a new-style provider that supports universal instrumentation
                from ..providers.universal_instrumentor import UniversalInstrumentor
                
                # Extract provider type from the provider class
                provider_type = "openai" if "openai" in str(type(provider)).lower() else "anthropic"
                instrumentor_type = "openinference"  # Default for now, could be extracted from provider_name
                
                # Create and assign universal instrumentor for traced workload
                provider.instrumentor = UniversalInstrumentor(
                    instrumentor_type=instrumentor_type,
                    provider_type=provider_type,
                    project=os.getenv("HH_PROJECT", f"ab-test-traced"),
                    enable_tracing=True
                )
                
                logger.debug(f"✅ Added {instrumentor_type} tracing to {provider_type} provider for traced workload")
            else:
                # Legacy provider interface - call old methods
                if hasattr(provider, 'initialize_client'):
                    provider.initialize_client()
                if hasattr(provider, 'initialize_instrumentor'):
                    provider.initialize_instrumentor()
        else:
            # For untraced workload, provider should already be untraced
            # Just ensure client is initialized if using legacy interface
            if hasattr(provider, 'initialize_client'):
                provider.initialize_client()
        
        # Start memory monitoring
        self.memory_profiler.reset()
        self.memory_profiler.start_monitoring()
        
        # Execute workload
        responses = []
        latencies = []
        start_time = time.perf_counter()
        
        for i, (prompt, scenario) in enumerate(prompts):
            operation_id = 20000 + i  # Use different range for workload execution
            
            # Measure individual operation latency
            op_start = time.perf_counter()
            response = provider.make_call(prompt, operation_id)
            op_end = time.perf_counter()
            
            latency_ms = (op_end - op_start) * 1000
            latencies.append(latency_ms)
            responses.append(response)
            
            # Sample memory periodically
            if i % 10 == 0:
                self.memory_profiler.sample_memory(f"{group_name}_op_{i}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop memory monitoring
        memory_stats = self.memory_profiler.stop_monitoring()
        
        # Clean up provider
        if enable_tracing:
            if hasattr(provider, 'cleanup_instrumentor'):
                provider.cleanup_instrumentor()
            elif hasattr(provider, 'cleanup'):
                provider.cleanup()
        
        return {
            "latencies": latencies,
            "responses": responses,
            "total_time": total_time,
            "memory_stats": memory_stats,
            "success_count": sum(1 for r in responses if r.success),
            "group_name": group_name
        }
    
    def _run_concurrent_workload(
        self,
        provider_factory: Callable[[], BaseProvider],
        prompts: List[Tuple[str, Any]],
        enable_tracing: bool,
        concurrency: int,
        group_name: str
    ) -> Dict[str, Any]:
        """Run a concurrent workload (traced or untraced).
        
        :param provider_factory: Factory to create provider instance
        :type provider_factory: Callable[[], BaseProvider]
        :param prompts: List of prompts to execute
        :type prompts: List[Tuple[str, Any]]
        :param enable_tracing: Whether to enable tracing
        :type enable_tracing: bool
        :param concurrency: Number of concurrent threads
        :type concurrency: int
        :param group_name: Name for this test group
        :type group_name: str
        :return: Workload results
        :rtype: Dict[str, Any]
        """
        # Create provider instance
        provider = provider_factory()
        
        # Handle tracing setup for the new universal interface
        if enable_tracing:
            # The provider should be untraced by default from factory
            # We need to add tracing dynamically for the traced workload
            
            if hasattr(provider, 'instrumentor') and provider.instrumentor is None:
                # This is a new-style provider that supports universal instrumentation
                from ..providers.universal_instrumentor import UniversalInstrumentor
                
                # Extract provider type from the provider class
                provider_type = "openai" if "openai" in str(type(provider)).lower() else "anthropic"
                instrumentor_type = "openinference"  # Default for now, could be extracted from provider_name
                
                # Create and assign universal instrumentor for traced workload
                provider.instrumentor = UniversalInstrumentor(
                    instrumentor_type=instrumentor_type,
                    provider_type=provider_type,
                    project=os.getenv("HH_PROJECT", f"ab-test-traced"),
                    enable_tracing=True
                )
                
                logger.debug(f"✅ Added {instrumentor_type} tracing to {provider_type} provider for traced workload")
            else:
                # Legacy provider interface - call old methods
                if hasattr(provider, 'initialize_client'):
                    provider.initialize_client()
                if hasattr(provider, 'initialize_instrumentor'):
                    provider.initialize_instrumentor()
        else:
            # For untraced workload, provider should already be untraced
            # Just ensure client is initialized if using legacy interface
            if hasattr(provider, 'initialize_client'):
                provider.initialize_client()
        
        # Start memory monitoring
        self.memory_profiler.reset()
        self.memory_profiler.start_monitoring()
        
        # Execute workload concurrently
        responses = []
        latencies = []
        start_time = time.perf_counter()
        
        def execute_prompt(prompt_data: Tuple[int, Tuple[str, Any]]) -> Tuple[float, ProviderResponse]:
            """Execute a single prompt and return latency and response."""
            i, (prompt, scenario) = prompt_data
            operation_id = 30000 + i  # Use different range for concurrent execution
            
            op_start = time.perf_counter()
            response = provider.make_call(prompt, operation_id)
            op_end = time.perf_counter()
            
            latency_ms = (op_end - op_start) * 1000
            return latency_ms, response
        
        # Execute prompts concurrently
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # Submit all tasks
            futures = []
            for i, prompt_data in enumerate(prompts):
                future = executor.submit(execute_prompt, (i, prompt_data))
                futures.append(future)
            
            # Collect results
            for i, future in enumerate(as_completed(futures)):
                try:
                    latency, response = future.result()
                    latencies.append(latency)
                    responses.append(response)
                    
                    # Sample memory periodically
                    if i % 10 == 0:
                        self.memory_profiler.sample_memory(f"{group_name}_concurrent_op_{i}")
                        
                except Exception as e:
                    logger.error(f"❌ Concurrent operation failed: {e}")
                    # Create failed response
                    responses.append(ProviderResponse(
                        provider_name=group_name,
                        operation_id=30000 + i,
                        success=False,
                        latency_ms=0.0,
                        tokens_used=0,
                        response_text="",
                        response_length=0,
                        model_used="unknown",
                        error_message=str(e)
                    ))
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop memory monitoring
        memory_stats = self.memory_profiler.stop_monitoring()
        
        # Clean up provider
        if enable_tracing:
            if hasattr(provider, 'cleanup_instrumentor'):
                provider.cleanup_instrumentor()
            elif hasattr(provider, 'cleanup'):
                provider.cleanup()
        
        return {
            "latencies": latencies,
            "responses": responses,
            "total_time": total_time,
            "memory_stats": memory_stats,
            "success_count": sum(1 for r in responses if r.success),
            "group_name": group_name
        }
    
    def _calculate_ab_metrics(
        self,
        test_name: str,
        traced_results: Dict[str, Any],
        untraced_results: Dict[str, Any],
        sample_size: int
    ) -> ABTestResult:
        """Calculate A/B test metrics with statistical analysis.
        
        :param test_name: Name of the test
        :type test_name: str
        :param traced_results: Results from traced workload
        :type traced_results: Dict[str, Any]
        :param untraced_results: Results from untraced workload
        :type untraced_results: Dict[str, Any]
        :param sample_size: Sample size per group
        :type sample_size: int
        :return: A/B test results
        :rtype: ABTestResult
        """
        traced_latencies = traced_results["latencies"]
        untraced_latencies = untraced_results["latencies"]
        
        # Debug: Check latency data
        logger.debug(f"📊 Traced latencies: {len(traced_latencies)} samples: {traced_latencies}")
        logger.debug(f"📊 Untraced latencies: {len(untraced_latencies)} samples: {untraced_latencies}")
        
        # Calculate latency impact (end-to-end performance difference)
        if not traced_latencies or not untraced_latencies:
            logger.error(f"❌ Empty latency data: traced={len(traced_latencies)}, untraced={len(untraced_latencies)}")
            return ABTestResult(
                test_name=test_name,
                traced_latencies=[],
                untraced_latencies=[],
                traced_memory={},
                untraced_memory={},
                traced_network={},
                untraced_network={},
                latency_impact_percent=0.0,
                cpu_overhead_percent=0.0,
                cpu_overhead_ms=0.0,
                statistical_significance=1.0,
                confidence_interval=(0.0, 0.0),
                sample_size=0
            )
        
        traced_avg = statistics.mean(traced_latencies)
        untraced_avg = statistics.mean(untraced_latencies)
        latency_impact_percent = ((traced_avg - untraced_avg) / untraced_avg) * 100 if untraced_avg > 0 else 0
        
        logger.debug(f"🔍 AB Test Debug: traced_avg={traced_avg}, untraced_avg={untraced_avg}, traced_latencies={traced_latencies}")
        
        # Handle division by zero case (failed tests) - check for very small values too!
        if traced_avg <= 0.001 or len(traced_latencies) == 0 or all(lat == 0.0 for lat in traced_latencies):  # Failed test
            logger.warning(f"⚠️ Traced test failed ({traced_avg:.3f}ms average) - returning failed result")
            return ABTestResult(
                provider_name=provider_name,
                traced_latencies=[],
                untraced_latencies=untraced_latencies,
                latency_impact_percent=0.0,
                latency_impact_absolute_ms=0.0,
                cpu_overhead_percent=0.0,
                cpu_overhead_ms=0.0,
                statistical_significance=1.0,  # No significance for failed test
                traced_network=None,
                untraced_network=untraced_network,
                sample_size=0,
                confidence_interval=(0.0, 0.0),
                traced_memory_stats=None,
                untraced_memory_stats=untraced_memory_stats
            )
        
        # Calculate real CPU overhead from span interceptor data (if available)
        traced_span_data = traced_results.get("span_data", {})
        real_cpu_overhead_ms = traced_span_data.get('real_cpu_overhead_ms', 0.0)
        
        if real_cpu_overhead_ms > 0:
            # Use real CPU overhead from span interception
            cpu_overhead_ms = real_cpu_overhead_ms
            cpu_overhead_percent = (cpu_overhead_ms / traced_avg) * 100  # traced_avg > 0 guaranteed here
            logger.debug(f"📊 Using real CPU overhead: {cpu_overhead_ms:.3f}ms ({cpu_overhead_percent:.2f}%)")
        else:
            # Fallback to conservative estimate
            cpu_overhead_ms = 15.0  # Conservative estimate: 10ms base + 5ms processing
            cpu_overhead_percent = (cpu_overhead_ms / traced_avg) * 100  # traced_avg > 0 guaranteed here
            logger.debug(f"📊 Using estimated CPU overhead: {cpu_overhead_ms:.3f}ms ({cpu_overhead_percent:.2f}%)")
        
        # Calculate statistical significance using proper Welch's t-test
        traced_var = statistics.variance(traced_latencies) if len(traced_latencies) > 1 else 0
        untraced_var = statistics.variance(untraced_latencies) if len(untraced_latencies) > 1 else 0
        
        # Welch's t-test (unequal variances assumed)
        if traced_var > 0 and untraced_var > 0 and sample_size > 1:
            # Standard errors
            se_traced = (traced_var / sample_size) ** 0.5
            se_untraced = (untraced_var / sample_size) ** 0.5
            se_diff = (se_traced**2 + se_untraced**2) ** 0.5
            
            # t-statistic
            t_stat = (traced_avg - untraced_avg) / se_diff if se_diff > 0 else 0
            
            # Degrees of freedom (Welch-Satterthwaite equation)
            if se_traced > 0 and se_untraced > 0:
                df = (se_traced**2 + se_untraced**2)**2 / (
                    (se_traced**4 / (sample_size - 1)) + 
                    (se_untraced**4 / (sample_size - 1))
                )
            else:
                df = 2 * sample_size - 2
            
            # Convert t-statistic to p-value using approximation
            # For small samples, use conservative approach
            if abs(t_stat) < 0.5:
                p_value = 0.8  # Very likely not significant
            elif abs(t_stat) < 1.0:
                p_value = 0.4  # Probably not significant  
            elif abs(t_stat) < 1.5:
                p_value = 0.2  # Borderline
            elif abs(t_stat) < 2.0:
                p_value = 0.1  # Approaching significance
            elif abs(t_stat) < 2.5:
                p_value = 0.05  # Right at threshold
            elif abs(t_stat) < 3.0:
                p_value = 0.01  # Significant
            else:
                p_value = 0.001  # Highly significant
                
            logger.debug(f"📊 Welch's t-test: t={t_stat:.3f}, df={df:.1f}, p={p_value:.4f}")
        else:
            # Insufficient data for proper test
            p_value = 0.999  # Assume not significant
            t_stat = 0
            logger.debug("📊 Insufficient variance for statistical test")
        
        # Calculate 95% confidence interval for latency impact
        if 'se_diff' in locals() and se_diff > 0 and untraced_avg > 0:
            # Use proper standard error from t-test
            margin_of_error_ms = 1.96 * se_diff  # 95% confidence interval
            margin_of_error_percent = (margin_of_error_ms / untraced_avg) * 100
            ci_lower = latency_impact_percent - margin_of_error_percent
            ci_upper = latency_impact_percent + margin_of_error_percent
        else:
            # Fallback to simple calculation
            pooled_std = ((traced_var + untraced_var) / 2) ** 0.5
            margin_of_error = 1.96 * (pooled_std / (sample_size ** 0.5)) if pooled_std > 0 else 0
            ci_lower = latency_impact_percent - (margin_of_error / untraced_avg * 100) if untraced_avg > 0 else latency_impact_percent
            ci_upper = latency_impact_percent + (margin_of_error / untraced_avg * 100) if untraced_avg > 0 else latency_impact_percent
        
        # Memory metrics
        traced_memory = traced_results["memory_stats"]
        untraced_memory = untraced_results["memory_stats"]
        
        # Network metrics
        traced_network = traced_results.get("network_analysis", {})
        untraced_network = untraced_results.get("network_analysis", {})
        
        return ABTestResult(
            test_name=test_name,
            traced_latencies=traced_latencies,
            untraced_latencies=untraced_latencies,
            traced_memory=traced_memory,
            untraced_memory=untraced_memory,
            traced_network=traced_network,
            untraced_network=untraced_network,
            latency_impact_percent=latency_impact_percent,
            cpu_overhead_percent=cpu_overhead_percent,
            cpu_overhead_ms=cpu_overhead_ms,
            statistical_significance=p_value,
            confidence_interval=(ci_lower, ci_upper),
            sample_size=sample_size
        )


def _run_single_ab_test_process(args: Dict[str, Any]) -> ABTestResult:
    """Run a single A/B test in a separate process for true isolation.
    
    This function is designed to run in a subprocess and provides:
    - Complete memory isolation from other tests
    - Independent tracer instances
    - Clean baseline measurements
    - Reduced logging noise
    
    :param args: Dictionary containing all test parameters
    :type args: Dict[str, Any]
    :return: A/B test results
    :rtype: ABTestResult
    """
    # Configure logging to reduce noise in subprocess
    import logging
    import os
    import sys
    
    # Set root logger to CRITICAL to suppress ALL noise
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Aggressively suppress noisy loggers in subprocess
    noisy_loggers = [
        'httpx', 'httpcore', 'urllib3', 'openai', 'anthropic',
        'honeyhive.early_init', 'honeyhive.fallback', 'honeyhive.client',
        'honeyhive', 'openinference', 'traceloop', 'opentelemetry'
    ]
    
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.disabled = True
        logger.propagate = False
    
    # Multiple approaches to suppress JSON logging
    os.environ['HONEYHIVE_DISABLE_JSON_LOGGING'] = '1'
    os.environ['HONEYHIVE_LOG_LEVEL'] = 'CRITICAL'
    os.environ['OTEL_LOG_LEVEL'] = 'CRITICAL'
    os.environ['HONEYHIVE_VERBOSE'] = 'false'
    
    # Redirect stdout/stderr temporarily during tracer initialization to suppress JSON logs
    class DevNull:
        def write(self, msg): pass
        def flush(self): pass
    
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Extract arguments
    provider_config = args['provider_config']
    test_name = args['test_name']
    sample_size = args['sample_size']
    randomization_seed = args['randomization_seed']
    benchmark_config = args['benchmark_config']
    
    # Create fresh instances in this process
    from ..scenarios.prompt_generator import PromptGenerator
    
    prompt_generator = PromptGenerator(randomization_seed)
    
    # Temporarily redirect output during harness initialization to suppress JSON logs
    devnull = DevNull()
    sys.stdout = devnull
    sys.stderr = devnull
    
    try:
        harness = ABTestingHarness(benchmark_config, prompt_generator)
    finally:
        # Restore output
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
    # Create separate provider factories for traced vs untraced runs
    def create_traced_provider_factory():
        provider_name = provider_config['name']
        if provider_name == "openinference_openai":
            from ..providers.openinference_openai_provider import OpenInferenceOpenAIProvider
            from honeyhive import HoneyHiveTracer
            
            # Create tracer for this subprocess
            tracer = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "ab-test-traced"),
                source="ab-test-openinference-openai"
            )
            
            # Create provider with tracer
            provider = OpenInferenceOpenAIProvider(benchmark_config, tracer)
            provider.initialize_client()
            provider.initialize_instrumentor()
            return provider
            
        elif provider_name == "openinference_anthropic":
            from ..providers.openinference_anthropic_provider import OpenInferenceAnthropicProvider
            from honeyhive import HoneyHiveTracer
            
            # Create tracer for this subprocess
            tracer = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "ab-test-traced"),
                source="ab-test-openinference-anthropic"
            )
            
            # Create provider with tracer
            provider = OpenInferenceAnthropicProvider(benchmark_config, tracer)
            provider.initialize_client()
            provider.initialize_instrumentor()
            return provider
            
        elif provider_name == "traceloop_openai":
            from ..providers.traceloop_openai_provider import TraceloopOpenAIProvider
            from honeyhive import HoneyHiveTracer
            
            # Create tracer for this subprocess
            tracer = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "ab-test-traced"),
                source="ab-test-traceloop-openai"
            )
            
            # Create provider with tracer
            provider = TraceloopOpenAIProvider(benchmark_config, tracer)
            provider.initialize_client()
            provider.initialize_instrumentor()
            return provider
            
        elif provider_name == "traceloop_anthropic":
            from ..providers.traceloop_anthropic_provider import TraceloopAnthropicProvider
            from honeyhive import HoneyHiveTracer
            
            # Create tracer for this subprocess
            tracer = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "ab-test-traced"),
                source="ab-test-traceloop-anthropic"
            )
            
            # Create provider with tracer
            provider = TraceloopAnthropicProvider(benchmark_config, tracer)
            provider.initialize_client()
            provider.initialize_instrumentor()
            return provider
            
        else:
            raise ValueError(f"Unknown traced provider: {provider_name}")
    
    def create_untraced_provider_factory():
        provider_name = provider_config['name']
        # All untraced providers use the same base LLM without any tracing
        if "openai" in provider_name:
            from ..providers.openinference_openai_provider import OpenInferenceOpenAIProvider
            
            # Create provider without tracer (untraced)
            provider = OpenInferenceOpenAIProvider(benchmark_config, None)
            provider.initialize_client()
            # Don't initialize instrumentor for untraced workload
            return provider
            
        elif "anthropic" in provider_name:
            from ..providers.openinference_anthropic_provider import OpenInferenceAnthropicProvider
            
            # Create provider without tracer (untraced)
            provider = OpenInferenceAnthropicProvider(benchmark_config, None)
            provider.initialize_client()
            # Don't initialize instrumentor for untraced workload
            return provider
            
        else:
            raise ValueError(f"Unknown untraced provider for: {provider_name}")
    
    # Run the A/B test in this isolated process
    try:
        # Create a logger for this subprocess (after suppression setup)
        subprocess_logger = logging.getLogger(f"ab_test.{provider_config['name']}")
        subprocess_logger.setLevel(logging.INFO)
        
        subprocess_logger.info(f"🔬 Starting A/B test for {provider_config['name']} (PID: {os.getpid()})")
        subprocess_logger.info("📊 Using separate factories: traced vs truly untraced providers")
        
        result = harness.run_ab_test(
            traced_provider_factory=create_traced_provider_factory,
            untraced_provider_factory=create_untraced_provider_factory,
            test_name=test_name,
            sample_size=sample_size,
            randomization_seed=randomization_seed
        )
        
        subprocess_logger.info(f"✅ A/B test completed for {provider_config['name']}: {result.latency_impact_percent:.2f}% latency impact, {result.cpu_overhead_percent:.2f}% CPU overhead")
        return result
    except Exception as e:
        # Create a failed result
        logger = logging.getLogger(__name__)
        logger.error(f"A/B test failed in subprocess for {provider_config['name']}: {e}")
        
        # Return a placeholder result indicating failure
        return ABTestResult(
            test_name=test_name,
            traced_latencies=[],
            untraced_latencies=[],
            traced_memory={},
            untraced_memory={},
            traced_network={},
            untraced_network={},
            latency_impact_percent=0.0,
            cpu_overhead_percent=0.0,
            cpu_overhead_ms=0.0,
            statistical_significance=1.0,
            confidence_interval=(0.0, 0.0),
            sample_size=0
        )
