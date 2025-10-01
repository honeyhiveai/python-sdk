"""
Load Testing Module

This module provides load testing capabilities for measuring tracer performance
under various QPS and concurrency levels. Identifies saturation points and
performance inflection curves for production capacity planning.
"""

import logging
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
import threading

from ..core.config import BenchmarkConfig
from ..scenarios.prompt_generator import PromptGenerator
from ..providers.base_provider import BaseProvider, ProviderResponse
from ..monitoring.memory_profiler import MemoryProfiler

logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load testing scenarios.
    
    :param name: Name of the load test
    :type name: str
    :param qps_levels: Queries per second levels to test
    :type qps_levels: List[float]
    :param concurrency_levels: Concurrency levels to test
    :type concurrency_levels: List[int]
    :param duration_seconds: Duration of each test phase
    :type duration_seconds: int
    :param warmup_seconds: Warmup period before measurements
    :type warmup_seconds: int
    :param ramp_up_seconds: Time to ramp up to target QPS
    :type ramp_up_seconds: int
    :param cooldown_seconds: Cooldown period between tests
    :type cooldown_seconds: int
    """
    name: str
    qps_levels: List[float] = field(default_factory=lambda: [1.0, 2.0, 5.0, 10.0, 20.0])
    concurrency_levels: List[int] = field(default_factory=lambda: [1, 2, 4, 8, 16])
    duration_seconds: int = 60
    warmup_seconds: int = 10
    ramp_up_seconds: int = 5
    cooldown_seconds: int = 5


@dataclass
class LoadTestResult:
    """Results from a single load test phase.
    
    :param test_name: Name of the test
    :type test_name: str
    :param target_qps: Target queries per second
    :type target_qps: float
    :param concurrency: Concurrency level used
    :type concurrency: int
    :param actual_qps: Actual achieved QPS
    :type actual_qps: float
    :param latencies: Response latencies in milliseconds
    :type latencies: List[float]
    :param success_rate: Percentage of successful requests
    :type success_rate: float
    :param memory_stats: Memory usage statistics
    :type memory_stats: Dict[str, float]
    :param saturation_detected: Whether saturation was detected
    :type saturation_detected: bool
    :param error_rate: Percentage of failed requests
    :type error_rate: float
    """
    test_name: str
    target_qps: float
    concurrency: int
    actual_qps: float
    latencies: List[float]
    success_rate: float
    memory_stats: Dict[str, float]
    saturation_detected: bool
    error_rate: float
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles.
        
        :return: Dictionary with P50, P95, P99 latencies
        :rtype: Dict[str, float]
        """
        if not self.latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            "p50": sorted_latencies[int(n * 0.5)],
            "p95": sorted_latencies[int(n * 0.95)],
            "p99": sorted_latencies[int(n * 0.99)]
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of load test results.
        
        :return: Dictionary with formatted results
        :rtype: Dict[str, Any]
        """
        percentiles = self.get_latency_percentiles()
        
        return {
            "Test": self.test_name,
            "Target QPS": f"{self.target_qps:.1f}",
            "Actual QPS": f"{self.actual_qps:.1f}",
            "Concurrency": self.concurrency,
            "Success Rate": f"{self.success_rate:.1f}%",
            "Error Rate": f"{self.error_rate:.1f}%",
            "P50 Latency": f"{percentiles['p50']:.0f}ms",
            "P95 Latency": f"{percentiles['p95']:.0f}ms",
            "P99 Latency": f"{percentiles['p99']:.0f}ms",
            "Memory Peak": f"{self.memory_stats.get('peak_memory_mb', 0):.1f}MB",
            "Saturated": "Yes" if self.saturation_detected else "No"
        }


class LoadTestRunner:
    """Load testing runner for measuring tracer performance under load.
    
    Executes systematic load tests across QPS and concurrency levels to
    identify performance characteristics and saturation points.
    
    :param config: Benchmark configuration
    :type config: BenchmarkConfig
    :param prompt_generator: Deterministic prompt generator
    :type prompt_generator: PromptGenerator
    
    Example:
        >>> runner = LoadTestRunner(config, prompt_generator)
        >>> results = runner.run_qps_sweep(
        ...     provider_factory=lambda: OpenAIProvider(),
        ...     load_config=LoadTestConfig("OpenAI Load Test")
        ... )
        >>> print(f"Saturation at {results.saturation_qps} QPS")
    """
    
    def __init__(self, config: BenchmarkConfig, prompt_generator: PromptGenerator) -> None:
        """Initialize load test runner.
        
        :param config: Benchmark configuration
        :type config: BenchmarkConfig
        :param prompt_generator: Deterministic prompt generator
        :type prompt_generator: PromptGenerator
        """
        self.config = config
        self.prompt_generator = prompt_generator
        self.memory_profiler = MemoryProfiler()
        self._stop_event = threading.Event()
        
        logger.info("🚀 Load Test Runner initialized")
    
    def run_qps_sweep(
        self,
        provider_factory: Callable[[], BaseProvider],
        load_config: LoadTestConfig
    ) -> Dict[str, Any]:
        """Run QPS sweep to find saturation point.
        
        :param provider_factory: Factory function to create provider instances
        :type provider_factory: Callable[[], BaseProvider]
        :param load_config: Load test configuration
        :type load_config: LoadTestConfig
        :return: QPS sweep results with saturation analysis
        :rtype: Dict[str, Any]
        """
        logger.info(f"🚀 Starting QPS sweep: {load_config.name}")
        
        results = []
        saturation_qps = None
        
        for qps in load_config.qps_levels:
            logger.info(f"📊 Testing QPS level: {qps}")
            
            # Use optimal concurrency for this QPS level
            concurrency = min(max(1, int(qps / 2)), 16)
            
            result = self._run_load_test_phase(
                provider_factory=provider_factory,
                target_qps=qps,
                concurrency=concurrency,
                load_config=load_config
            )
            
            results.append(result)
            
            # Check for saturation
            if result.saturation_detected and saturation_qps is None:
                saturation_qps = qps
                logger.warning(f"⚠️ Saturation detected at {qps} QPS")
            
            # Cooldown between tests
            if load_config.cooldown_seconds > 0:
                logger.debug(f"😴 Cooling down for {load_config.cooldown_seconds}s...")
                time.sleep(load_config.cooldown_seconds)
        
        return {
            "test_name": load_config.name,
            "test_type": "qps_sweep",
            "results": results,
            "saturation_qps": saturation_qps,
            "max_stable_qps": self._find_max_stable_qps(results),
            "performance_curve": self._analyze_performance_curve(results)
        }
    
    def run_concurrency_sweep(
        self,
        provider_factory: Callable[[], BaseProvider],
        load_config: LoadTestConfig,
        fixed_qps: float = 5.0
    ) -> Dict[str, Any]:
        """Run concurrency sweep at fixed QPS.
        
        :param provider_factory: Factory function to create provider instances
        :type provider_factory: Callable[[], BaseProvider]
        :param load_config: Load test configuration
        :type load_config: LoadTestConfig
        :param fixed_qps: Fixed QPS level for concurrency testing
        :type fixed_qps: float
        :return: Concurrency sweep results
        :rtype: Dict[str, Any]
        """
        logger.info(f"⚡ Starting concurrency sweep: {load_config.name} at {fixed_qps} QPS")
        
        results = []
        optimal_concurrency = None
        
        for concurrency in load_config.concurrency_levels:
            logger.info(f"📊 Testing concurrency level: {concurrency}")
            
            result = self._run_load_test_phase(
                provider_factory=provider_factory,
                target_qps=fixed_qps,
                concurrency=concurrency,
                load_config=load_config
            )
            
            results.append(result)
            
            # Track optimal concurrency (lowest latency without saturation)
            if not result.saturation_detected:
                if optimal_concurrency is None or result.get_latency_percentiles()["p95"] < results[optimal_concurrency].get_latency_percentiles()["p95"]:
                    optimal_concurrency = len(results) - 1
            
            # Cooldown between tests
            if load_config.cooldown_seconds > 0:
                time.sleep(load_config.cooldown_seconds)
        
        return {
            "test_name": load_config.name,
            "test_type": "concurrency_sweep",
            "fixed_qps": fixed_qps,
            "results": results,
            "optimal_concurrency": load_config.concurrency_levels[optimal_concurrency] if optimal_concurrency is not None else None,
            "concurrency_analysis": self._analyze_concurrency_impact(results)
        }
    
    def run_burst_test(
        self,
        provider_factory: Callable[[], BaseProvider],
        load_config: LoadTestConfig,
        burst_qps: float = 50.0,
        burst_duration: int = 10
    ) -> Dict[str, Any]:
        """Run burst load test to measure spike handling.
        
        :param provider_factory: Factory function to create provider instances
        :type provider_factory: Callable[[], BaseProvider]
        :param load_config: Load test configuration
        :type load_config: LoadTestConfig
        :param burst_qps: QPS level during burst
        :type burst_qps: float
        :param burst_duration: Duration of burst in seconds
        :type burst_duration: int
        :return: Burst test results
        :rtype: Dict[str, Any]
        """
        logger.info(f"💥 Starting burst test: {burst_qps} QPS for {burst_duration}s")
        
        # Baseline phase
        baseline_result = self._run_load_test_phase(
            provider_factory=provider_factory,
            target_qps=2.0,  # Low baseline
            concurrency=2,
            load_config=load_config
        )
        
        # Burst phase
        burst_result = self._run_load_test_phase(
            provider_factory=provider_factory,
            target_qps=burst_qps,
            concurrency=min(int(burst_qps / 2), 32),
            load_config=LoadTestConfig(
                name=f"{load_config.name}_burst",
                duration_seconds=burst_duration,
                warmup_seconds=2,
                ramp_up_seconds=1
            )
        )
        
        # Recovery phase
        recovery_result = self._run_load_test_phase(
            provider_factory=provider_factory,
            target_qps=2.0,  # Back to baseline
            concurrency=2,
            load_config=load_config
        )
        
        return {
            "test_name": f"{load_config.name}_burst",
            "test_type": "burst_test",
            "burst_qps": burst_qps,
            "burst_duration": burst_duration,
            "baseline_result": baseline_result,
            "burst_result": burst_result,
            "recovery_result": recovery_result,
            "burst_impact": self._analyze_burst_impact(baseline_result, burst_result, recovery_result)
        }
    
    def _run_load_test_phase(
        self,
        provider_factory: Callable[[], BaseProvider],
        target_qps: float,
        concurrency: int,
        load_config: LoadTestConfig
    ) -> LoadTestResult:
        """Run a single load test phase.
        
        :param provider_factory: Factory to create provider instance
        :type provider_factory: Callable[[], BaseProvider]
        :param target_qps: Target queries per second
        :type target_qps: float
        :param concurrency: Concurrency level
        :type concurrency: int
        :param load_config: Load test configuration
        :type load_config: LoadTestConfig
        :return: Load test results
        :rtype: LoadTestResult
        """
        # Create provider
        provider = provider_factory()
        provider.initialize_client()
        provider.initialize_instrumentor()
        
        # Generate prompts
        num_requests = int(target_qps * (load_config.duration_seconds + load_config.warmup_seconds))
        prompts = []
        for i in range(num_requests):
            prompt, scenario = self.prompt_generator.generate_prompt(40000 + i, self.config.span_size_mode)
            prompts.append(prompt)
        
        # Start memory monitoring
        self.memory_profiler.reset()
        self.memory_profiler.start_monitoring()
        
        # Initialize tracking
        self._stop_event.clear()
        responses = []
        latencies = []
        request_times = []
        
        # Rate limiting setup
        request_interval = 1.0 / target_qps
        
        def execute_request(prompt: str, operation_id: int) -> Tuple[float, ProviderResponse]:
            """Execute a single request with timing."""
            start_time = time.perf_counter()
            response = provider.make_call(prompt, operation_id)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            return latency_ms, response
        
        # Warmup phase
        if load_config.warmup_seconds > 0:
            logger.debug(f"🔥 Warming up for {load_config.warmup_seconds}s...")
            warmup_end = time.perf_counter() + load_config.warmup_seconds
            warmup_requests = 0
            
            while time.perf_counter() < warmup_end and not self._stop_event.is_set():
                if warmup_requests < len(prompts):
                    try:
                        execute_request(prompts[warmup_requests], 50000 + warmup_requests)
                        warmup_requests += 1
                    except Exception as e:
                        logger.debug(f"Warmup request failed: {e}")
                time.sleep(request_interval)
        
        # Main test phase
        logger.debug(f"📊 Running load test: {target_qps} QPS, {concurrency} threads, {load_config.duration_seconds}s")
        
        start_time = time.perf_counter()
        end_time = start_time + load_config.duration_seconds
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            request_count = 0
            
            while time.perf_counter() < end_time and not self._stop_event.is_set():
                if request_count < len(prompts):
                    # Submit request
                    future = executor.submit(execute_request, prompts[request_count], 60000 + request_count)
                    futures.append((future, time.perf_counter()))
                    request_count += 1
                    
                    # Rate limiting
                    time.sleep(request_interval)
                
                # Collect completed requests
                completed_futures = []
                for future, submit_time in futures:
                    if future.done():
                        try:
                            latency, response = future.result()
                            latencies.append(latency)
                            responses.append(response)
                            request_times.append(submit_time)
                            completed_futures.append((future, submit_time))
                        except Exception as e:
                            logger.debug(f"Request failed: {e}")
                
                # Remove completed futures
                for completed in completed_futures:
                    futures.remove(completed)
            
            # Wait for remaining requests to complete
            for future, submit_time in futures:
                try:
                    latency, response = future.result(timeout=30)
                    latencies.append(latency)
                    responses.append(response)
                    request_times.append(submit_time)
                except Exception as e:
                    logger.debug(f"Request timeout or failed: {e}")
        
        # Stop monitoring
        memory_stats = self.memory_profiler.stop_monitoring()
        
        # Calculate metrics
        actual_duration = time.perf_counter() - start_time
        actual_qps = len(responses) / actual_duration if actual_duration > 0 else 0
        success_count = sum(1 for r in responses if r.success)
        success_rate = (success_count / len(responses)) * 100 if responses else 0
        error_rate = 100 - success_rate
        
        # Detect saturation
        saturation_detected = self._detect_saturation(target_qps, actual_qps, latencies, error_rate)
        
        # Cleanup
        provider.cleanup_instrumentor()
        
        return LoadTestResult(
            test_name=load_config.name,
            target_qps=target_qps,
            concurrency=concurrency,
            actual_qps=actual_qps,
            latencies=latencies,
            success_rate=success_rate,
            memory_stats=memory_stats,
            saturation_detected=saturation_detected,
            error_rate=error_rate
        )
    
    def _detect_saturation(self, target_qps: float, actual_qps: float, latencies: List[float], error_rate: float) -> bool:
        """Detect if the system is saturated.
        
        :param target_qps: Target QPS
        :type target_qps: float
        :param actual_qps: Actual achieved QPS
        :type actual_qps: float
        :param latencies: Response latencies
        :type latencies: List[float]
        :param error_rate: Error rate percentage
        :type error_rate: float
        :return: True if saturation detected
        :rtype: bool
        """
        # QPS saturation: can't achieve target QPS
        qps_saturation = actual_qps < target_qps * 0.8
        
        # Latency saturation: P95 latency too high
        if latencies:
            sorted_latencies = sorted(latencies)
            p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            latency_saturation = p95_latency > 30000  # 30 seconds
        else:
            latency_saturation = False
        
        # Error saturation: too many errors
        error_saturation = error_rate > 10.0  # 10% error rate
        
        return qps_saturation or latency_saturation or error_saturation
    
    def _find_max_stable_qps(self, results: List[LoadTestResult]) -> Optional[float]:
        """Find maximum stable QPS from results.
        
        :param results: List of load test results
        :type results: List[LoadTestResult]
        :return: Maximum stable QPS or None
        :rtype: Optional[float]
        """
        for result in reversed(results):  # Start from highest QPS
            if not result.saturation_detected and result.success_rate > 95.0:
                return result.target_qps
        return None
    
    def _analyze_performance_curve(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze performance curve from QPS sweep results.
        
        :param results: List of load test results
        :type results: List[LoadTestResult]
        :return: Performance curve analysis
        :rtype: Dict[str, Any]
        """
        qps_values = [r.target_qps for r in results]
        latency_p95_values = [r.get_latency_percentiles()["p95"] for r in results]
        success_rates = [r.success_rate for r in results]
        
        # Find inflection point (where latency starts increasing rapidly)
        inflection_qps = None
        for i in range(1, len(results)):
            if latency_p95_values[i] > latency_p95_values[i-1] * 1.5:  # 50% increase
                inflection_qps = qps_values[i-1]
                break
        
        return {
            "qps_range": (min(qps_values), max(qps_values)),
            "latency_range": (min(latency_p95_values), max(latency_p95_values)),
            "inflection_qps": inflection_qps,
            "degradation_pattern": "linear" if inflection_qps is None else "exponential",
            "stable_region": qps_values[:qps_values.index(inflection_qps)] if inflection_qps else qps_values
        }
    
    def _analyze_concurrency_impact(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze impact of concurrency on performance.
        
        :param results: List of load test results
        :type results: List[LoadTestResult]
        :return: Concurrency impact analysis
        :rtype: Dict[str, Any]
        """
        concurrency_values = [r.concurrency for r in results]
        latency_p95_values = [r.get_latency_percentiles()["p95"] for r in results]
        
        # Find optimal concurrency (lowest P95 latency)
        min_latency_idx = latency_p95_values.index(min(latency_p95_values))
        optimal_concurrency = concurrency_values[min_latency_idx]
        
        return {
            "optimal_concurrency": optimal_concurrency,
            "latency_improvement": latency_p95_values[0] - min(latency_p95_values),
            "diminishing_returns_threshold": self._find_diminishing_returns(results),
            "concurrency_efficiency": min(latency_p95_values) / latency_p95_values[0]
        }
    
    def _find_diminishing_returns(self, results: List[LoadTestResult]) -> Optional[int]:
        """Find concurrency level where diminishing returns start.
        
        :param results: List of load test results
        :type results: List[LoadTestResult]
        :return: Concurrency level or None
        :rtype: Optional[int]
        """
        latency_improvements = []
        for i in range(1, len(results)):
            prev_latency = results[i-1].get_latency_percentiles()["p95"]
            curr_latency = results[i].get_latency_percentiles()["p95"]
            improvement = prev_latency - curr_latency
            latency_improvements.append(improvement)
        
        # Find where improvement drops significantly
        for i in range(1, len(latency_improvements)):
            if latency_improvements[i] < latency_improvements[i-1] * 0.5:  # 50% less improvement
                return results[i].concurrency
        
        return None
    
    def _analyze_burst_impact(
        self,
        baseline: LoadTestResult,
        burst: LoadTestResult,
        recovery: LoadTestResult
    ) -> Dict[str, Any]:
        """Analyze impact of burst load.
        
        :param baseline: Baseline test results
        :type baseline: LoadTestResult
        :param burst: Burst test results
        :type burst: LoadTestResult
        :param recovery: Recovery test results
        :type recovery: LoadTestResult
        :return: Burst impact analysis
        :rtype: Dict[str, Any]
        """
        baseline_p95 = baseline.get_latency_percentiles()["p95"]
        burst_p95 = burst.get_latency_percentiles()["p95"]
        recovery_p95 = recovery.get_latency_percentiles()["p95"]
        
        return {
            "burst_latency_impact": burst_p95 - baseline_p95,
            "recovery_time_estimate": "immediate" if recovery_p95 <= baseline_p95 * 1.1 else "delayed",
            "burst_success_rate": burst.success_rate,
            "system_resilience": "high" if burst.success_rate > 90 else "medium" if burst.success_rate > 70 else "low",
            "memory_spike": burst.memory_stats.get("peak_memory_mb", 0) - baseline.memory_stats.get("peak_memory_mb", 0)
        }
