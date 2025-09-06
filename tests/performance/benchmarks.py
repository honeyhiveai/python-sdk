"""
Performance benchmarks for HoneyHive non-instrumentor integration.

This module provides comprehensive benchmarks for:
- Span processing overhead
- Provider detection speed
- Memory usage patterns
- Concurrent operation performance
"""

import gc
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

import psutil
import pytest

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.processor_integrator import ProcessorIntegrator
from honeyhive.tracer.provider_detector import IntegrationStrategy, ProviderDetector
from tests.mocks.mock_frameworks import MockFrameworkA, MockFrameworkB, MockFrameworkC


class PerformanceBenchmarks:
    """Comprehensive performance benchmark suite."""

    def __init__(self):
        """Initialize benchmark class attributes."""
        self.test_api_key = None
        self.test_project = None
        self.test_source = None
        self.max_span_processing_time = None
        self.max_provider_detection_time = None
        self.max_memory_overhead_percent = None
        self.benchmark_iterations = None
        self.concurrent_threads = None

    def setup_method(self):
        """Set up benchmark fixtures."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

        # Test configuration
        self.test_api_key = "benchmark-test-key"
        self.test_project = "benchmark-project"
        self.test_source = "benchmark-test"

        # Performance thresholds (from spec requirements)
        self.max_span_processing_time = 0.001  # 1ms per span
        self.max_provider_detection_time = 0.010  # 10ms
        self.max_memory_overhead_percent = 5.0  # 5% increase

        # Benchmark configuration
        self.benchmark_iterations = 1000
        self.concurrent_threads = 10

    def teardown_method(self):
        """Clean up after benchmarks."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

        # Force garbage collection
        gc.collect()

    @pytest.mark.benchmark
    def test_benchmark_span_processing_overhead(self, benchmark):
        """Benchmark span processing overhead."""
        # Initialize HoneyHive tracer
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            source=self.test_source,
            test_mode=True,
        )

        # Create framework for span generation
        framework = MockFrameworkA("BenchmarkFramework")

        def process_spans():
            """Process a batch of spans."""
            results = []
            for i in range(100):  # Process 100 spans per iteration
                result = framework.execute_operation(
                    f"benchmark_op_{i}", iteration=i, batch_size=100
                )
                results.append(result)
            return results

        # Benchmark the span processing
        result = benchmark(process_spans)

        # Verify results
        assert len(result) == 100
        assert all(r["status"] == "completed" for r in result)

        # Calculate per-span processing time
        per_span_time = benchmark.stats.mean / 100

        # Verify performance requirement: <1ms per span
        assert (
            per_span_time < self.max_span_processing_time
        ), f"Span processing too slow: {per_span_time:.4f}s per span (max: {self.max_span_processing_time}s)"

        print(f"✅ Span processing benchmark: {per_span_time:.4f}s per span")
        return per_span_time

    @pytest.mark.benchmark
    def test_benchmark_provider_detection_speed(self, benchmark):
        """Benchmark provider detection speed."""

        def detect_providers():
            """Detect providers multiple times."""
            detector = ProviderDetector()
            results = []

            for _ in range(50):  # 50 detections per iteration
                provider_info = detector.detect_current_provider()
                strategy = detector.determine_integration_strategy(provider_info)
                results.append((provider_info, strategy))

            return results

        # Benchmark provider detection
        result = benchmark(detect_providers)

        # Verify results
        assert len(result) == 50
        assert all(isinstance(strategy, IntegrationStrategy) for _, strategy in result)

        # Calculate per-detection time
        per_detection_time = benchmark.stats.mean / 50

        # Verify performance requirement: <10ms per detection
        assert (
            per_detection_time < self.max_provider_detection_time
        ), f"Provider detection too slow: {per_detection_time:.4f}s per detection (max: {self.max_provider_detection_time}s)"

        print(
            f"✅ Provider detection benchmark: {per_detection_time:.4f}s per detection"
        )
        return per_detection_time

    @pytest.mark.benchmark
    def test_benchmark_memory_usage_patterns(self, benchmark):
        """Benchmark memory usage patterns."""
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        def memory_intensive_operations():
            """Perform memory-intensive operations."""
            # Initialize tracer
            _ = HoneyHiveTracer.init(
                api_key=self.test_api_key,
                project=self.test_project,
                source=self.test_source,
                test_mode=True,
            )

            # Create multiple frameworks
            frameworks = (
                [MockFrameworkA(f"MemoryFrameworkA_{i}") for i in range(10)]
                + [
                    MockFrameworkB(f"MemoryFrameworkB_{i}", delay_provider_setup=False)
                    for i in range(10)
                ]
                + [MockFrameworkC(f"MemoryFrameworkC_{i}") for i in range(10)]
            )

            # Execute operations
            results = []
            for i, framework in enumerate(frameworks):
                if isinstance(framework, MockFrameworkA):
                    result = framework.execute_operation(
                        f"memory_test_{i}", data_size=1000
                    )
                elif isinstance(framework, MockFrameworkB):
                    result = framework.process_data(
                        f"memory_data_{i}" * 100, "memory_intensive"
                    )
                elif isinstance(framework, MockFrameworkC):
                    result = framework.analyze_content(
                        f"memory content {i}" * 50, "memory_analysis"
                    )
                else:
                    result = {
                        "status": "completed",
                        "message": "Unknown framework type",
                    }

                results.append(result)

            return results

        # Benchmark memory usage
        result = benchmark(memory_intensive_operations)

        # Get peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_overhead = ((peak_memory - baseline_memory) / baseline_memory) * 100

        # Verify results
        assert len(result) == 30  # 10 frameworks × 3 types
        assert all(r["status"] == "completed" for r in result)

        # Verify performance requirement: <5% memory overhead
        assert (
            memory_overhead < self.max_memory_overhead_percent
        ), f"Memory overhead too high: {memory_overhead:.2f}% (max: {self.max_memory_overhead_percent}%)"

        print(f"✅ Memory usage benchmark: {memory_overhead:.2f}% overhead")
        return memory_overhead

    @pytest.mark.benchmark
    def test_benchmark_concurrent_performance(self, benchmark):
        """Benchmark concurrent operation performance."""

        def concurrent_operations():
            """Execute operations concurrently."""
            # Initialize tracer
            _ = HoneyHiveTracer.init(
                api_key=self.test_api_key,
                project=self.test_project,
                source=self.test_source,
                test_mode=True,
            )

            # Create frameworks
            frameworks = [
                MockFrameworkA(f"ConcurrentA_{i}")
                for i in range(self.concurrent_threads)
            ]

            def worker_task(framework_index):
                """Worker task for concurrent execution."""
                framework = frameworks[framework_index]
                results = []

                for i in range(10):  # 10 operations per thread
                    result = framework.execute_operation(
                        f"concurrent_op_{framework_index}_{i}",
                        thread_id=threading.get_ident(),
                        operation_index=i,
                    )
                    results.append(result)

                return results

            # Execute concurrent operations
            all_results = []
            with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
                futures = [
                    executor.submit(worker_task, i)
                    for i in range(self.concurrent_threads)
                ]

                for future in as_completed(futures):
                    thread_results = future.result()
                    all_results.extend(thread_results)

            return all_results

        # Benchmark concurrent operations
        result = benchmark(concurrent_operations)

        # Verify results
        expected_operations = self.concurrent_threads * 10
        assert len(result) == expected_operations
        assert all(r["status"] == "completed" for r in result)

        # Calculate operations per second
        operations_per_second = expected_operations / benchmark.stats.mean

        # Verify reasonable concurrent performance (should handle at least 100 ops/sec)
        min_ops_per_second = 100
        assert (
            operations_per_second >= min_ops_per_second
        ), f"Concurrent performance too low: {operations_per_second:.1f} ops/sec (min: {min_ops_per_second})"

        print(
            f"✅ Concurrent performance benchmark: {operations_per_second:.1f} operations/second"
        )
        return operations_per_second

    @pytest.mark.benchmark
    def test_benchmark_initialization_overhead(self, benchmark):
        """Benchmark tracer initialization overhead."""

        def initialize_tracers():
            """Initialize multiple tracers."""
            tracers = []

            for i in range(10):  # Initialize 10 tracers per iteration
                # Reset state for clean initialization
                from opentelemetry import trace

                trace._TRACER_PROVIDER = None

                tracer = HoneyHiveTracer.init(
                    api_key=self.test_api_key,
                    project=f"{self.test_project}_{i}",
                    source=f"{self.test_source}_{i}",
                    test_mode=True,
                )
                tracers.append(tracer)

            return tracers

        # Benchmark initialization
        result = benchmark(initialize_tracers)

        # Verify results
        assert len(result) == 10
        assert all(isinstance(tracer, HoneyHiveTracer) for tracer in result)

        # Calculate per-initialization time
        per_init_time = benchmark.stats.mean / 10

        # Verify reasonable initialization time (<100ms per tracer)
        max_init_time = 0.1  # 100ms
        assert (
            per_init_time < max_init_time
        ), f"Initialization too slow: {per_init_time:.4f}s per tracer (max: {max_init_time}s)"

        print(f"✅ Initialization benchmark: {per_init_time:.4f}s per tracer")
        return per_init_time

    @pytest.mark.benchmark
    def test_benchmark_framework_switching_overhead(self, benchmark):
        """Benchmark overhead of switching between frameworks."""

        def framework_switching():
            """Switch between different frameworks rapidly."""
            # Initialize tracer
            _ = HoneyHiveTracer.init(
                api_key=self.test_api_key,
                project=self.test_project,
                source=self.test_source,
                test_mode=True,
            )

            # Create frameworks
            framework_a = MockFrameworkA("SwitchingA")
            framework_b = MockFrameworkB("SwitchingB", delay_provider_setup=False)
            framework_c = MockFrameworkC("SwitchingC")

            frameworks = [framework_a, framework_b, framework_c]
            results = []

            # Rapidly switch between frameworks
            for i in range(30):  # 30 operations, switching frameworks
                framework = frameworks[i % 3]

                if isinstance(framework, MockFrameworkA):
                    result = framework.execute_operation(f"switch_op_{i}")
                elif isinstance(framework, MockFrameworkB):
                    result = framework.process_data(f"switch_data_{i}", "switching")
                elif isinstance(framework, MockFrameworkC):
                    result = framework.analyze_content(
                        f"switch content {i}", "switching"
                    )
                else:
                    result = {
                        "status": "completed",
                        "message": "Unknown framework type",
                    }

                results.append(result)

            return results

        # Benchmark framework switching
        result = benchmark(framework_switching)

        # Verify results
        assert len(result) == 30
        assert all(r["status"] == "completed" for r in result)

        # Calculate per-operation time
        per_operation_time = benchmark.stats.mean / 30

        # Verify reasonable switching performance (<2ms per operation)
        max_operation_time = 0.002  # 2ms
        assert (
            per_operation_time < max_operation_time
        ), f"Framework switching too slow: {per_operation_time:.4f}s per operation (max: {max_operation_time}s)"

        print(
            f"✅ Framework switching benchmark: {per_operation_time:.4f}s per operation"
        )
        return per_operation_time


class MemoryProfiler:
    """Memory profiling utilities for performance testing."""

    @staticmethod
    def profile_memory_usage(func, *args, **kwargs):
        """Profile memory usage of a function."""
        process = psutil.Process(os.getpid())

        # Force garbage collection before measurement
        gc.collect()

        # Get baseline memory
        baseline_memory = process.memory_info().rss

        # Execute function
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        # Get peak memory
        peak_memory = process.memory_info().rss

        # Force garbage collection after measurement
        gc.collect()
        final_memory = process.memory_info().rss

        return {
            "result": result,
            "execution_time": end_time - start_time,
            "baseline_memory_mb": baseline_memory / 1024 / 1024,
            "peak_memory_mb": peak_memory / 1024 / 1024,
            "final_memory_mb": final_memory / 1024 / 1024,
            "memory_overhead_mb": (peak_memory - baseline_memory) / 1024 / 1024,
            "memory_overhead_percent": (
                (peak_memory - baseline_memory) / baseline_memory
            )
            * 100,
        }


class ConcurrentBenchmark:
    """Utilities for concurrent performance testing."""

    @staticmethod
    def run_concurrent_benchmark(
        worker_func, num_workers=10, operations_per_worker=100
    ):
        """Run a concurrent benchmark with multiple workers."""
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(worker_func, worker_id, operations_per_worker)
                for worker_id in range(num_workers)
            ]

            results = []
            for future in as_completed(futures):
                worker_results = future.result()
                results.extend(worker_results)

        end_time = time.perf_counter()

        total_operations = num_workers * operations_per_worker
        total_time = end_time - start_time
        operations_per_second = total_operations / total_time

        return {
            "results": results,
            "total_operations": total_operations,
            "total_time": total_time,
            "operations_per_second": operations_per_second,
            "average_time_per_operation": total_time / total_operations,
        }


# Standalone benchmark functions for manual testing
def benchmark_span_processing(iterations=1000):
    """Standalone span processing benchmark."""
    _ = HoneyHiveTracer.init(
        api_key="benchmark-key",
        project="benchmark-project",
        source="benchmark-test",
        test_mode=True,
    )

    framework = MockFrameworkA("StandaloneBenchmark")

    start_time = time.perf_counter()

    for i in range(iterations):
        framework.execute_operation(f"benchmark_op_{i}", iteration=i)

    end_time = time.perf_counter()

    total_time = end_time - start_time
    per_span_time = total_time / iterations

    print(f"Span Processing Benchmark:")
    print(f"  Total operations: {iterations}")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Time per span: {per_span_time:.6f}s")
    print(f"  Operations per second: {iterations / total_time:.1f}")

    return per_span_time


def benchmark_provider_detection(iterations=100):
    """Standalone provider detection benchmark."""
    detector = ProviderDetector()

    start_time = time.perf_counter()

    for _ in range(iterations):
        provider_info = detector.detect_current_provider()
        _ = detector.determine_integration_strategy(provider_info)  # strategy

    end_time = time.perf_counter()

    total_time = end_time - start_time
    per_detection_time = total_time / iterations

    print(f"Provider Detection Benchmark:")
    print(f"  Total detections: {iterations}")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Time per detection: {per_detection_time:.6f}s")
    print(f"  Detections per second: {iterations / total_time:.1f}")

    return per_detection_time


if __name__ == "__main__":
    # Run standalone benchmarks
    print("🚀 Running HoneyHive Performance Benchmarks")
    print("=" * 50)

    # Run span processing benchmark
    span_time = benchmark_span_processing(1000)

    print()

    # Run provider detection benchmark
    detection_time = benchmark_provider_detection(100)

    print()
    print("✅ Benchmark Summary:")
    print(f"  Span processing: {span_time:.6f}s per span")
    print(f"  Provider detection: {detection_time:.6f}s per detection")

    # Performance requirements check
    max_span_time = 0.001  # 1ms
    max_detection_time = 0.010  # 10ms

    if span_time < max_span_time:
        print(f"  ✅ Span processing meets requirement (<{max_span_time}s)")
    else:
        print(f"  ❌ Span processing exceeds requirement (>{max_span_time}s)")

    if detection_time < max_detection_time:
        print(f"  ✅ Provider detection meets requirement (<{max_detection_time}s)")
    else:
        print(f"  ❌ Provider detection exceeds requirement (>{max_detection_time}s)")
