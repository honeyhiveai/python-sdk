"""
Concurrent performance benchmarks for HoneyHive non-instrumentor integration.

This module tests performance under concurrent load with:
- Thread safety validation
- Concurrent operation throughput
- Contention analysis
- Scalability testing
"""

# pylint: disable=R0401,R0801,R0902,R0903,R0913,R0914,R0915,C0301,W0621
# Justification: Performance benchmark with test patterns that trigger:
# - R0401 (cyclic-import): Test imports honeyhive package causing cycles
# - R0801 (duplicate-code): Shared test patterns with integration tests
# - W0621 (redefined-outer-name): Test function scoping
# - R0902-R0915, C0301: Comprehensive concurrent testing requirements

import queue
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from honeyhive import HoneyHiveTracer
from tests.mocks.mock_frameworks import MockFrameworkA, MockFrameworkB, MockFrameworkC


@dataclass
class ConcurrentTestResult:
    """Result of a concurrent performance test."""

    total_operations: int
    total_time: float
    operations_per_second: float
    average_latency: float
    min_latency: float
    max_latency: float
    p95_latency: float
    p99_latency: float
    thread_count: int
    success_rate: float
    errors: List[str]


class ConcurrentBenchmark:
    """Concurrent performance benchmark suite."""

    def __init__(self) -> None:
        self.results_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.error_queue: queue.Queue[str] = queue.Queue()

    def run_throughput_benchmark(
        self, num_threads: int = 10, operations_per_thread: int = 100
    ) -> ConcurrentTestResult:
        """Benchmark concurrent operation throughput."""
        print(
            "🚀 Running throughput benchmark: %s threads, %s ops/thread",
            num_threads,
            operations_per_thread,
        )

        # Initialize tracer
        _ = HoneyHiveTracer.init(
            api_key="concurrent-benchmark-key",
            project="concurrent-benchmark",
            source="throughput-test",
            test_mode=True,
        )

        def worker_task(worker_id: int) -> List[Dict[str, Any]]:
            """Worker task for throughput testing."""
            framework = MockFrameworkA(f"ThroughputWorker_{worker_id}")
            worker_results = []

            for i in range(operations_per_thread):
                start_time = time.perf_counter()

                try:
                    result = framework.execute_operation(
                        f"throughput_op_{worker_id}_{i}",
                        worker_id=worker_id,
                        operation_index=i,
                        thread_id=threading.get_ident(),
                    )

                    end_time = time.perf_counter()
                    latency = end_time - start_time

                    worker_results.append(
                        {
                            "worker_id": worker_id,
                            "operation_index": i,
                            "latency": latency,
                            "success": True,
                            "result": result,
                        }
                    )

                except Exception as e:
                    end_time = time.perf_counter()
                    latency = end_time - start_time

                    worker_results.append(
                        {
                            "worker_id": worker_id,
                            "operation_index": i,
                            "latency": latency,
                            "success": False,
                            "error": str(e),
                        }
                    )

            return worker_results

        # Execute concurrent operations
        start_time = time.perf_counter()
        all_results = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_task, worker_id)
                for worker_id in range(num_threads)
            ]

            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)

        end_time = time.perf_counter()

        # Analyze results
        return self._analyze_results(all_results, end_time - start_time, num_threads)

    def run_contention_benchmark(
        self, max_threads: int = 20, operations_per_thread: int = 50
    ) -> Dict[int, ConcurrentTestResult]:
        """Benchmark performance under increasing thread contention."""
        print(f"🔄 Running contention benchmark: 1 to {max_threads} threads")

        results = {}

        for thread_count in [1, 2, 4, 8, 12, 16, 20]:
            if thread_count > max_threads:
                break

            print(f"   Testing with {thread_count} threads...")
            result = self.run_throughput_benchmark(thread_count, operations_per_thread)
            results[thread_count] = result

            # Brief pause between tests
            time.sleep(0.1)

        return results

    def run_mixed_framework_benchmark(
        self, num_threads: int = 12, operations_per_thread: int = 50
    ) -> ConcurrentTestResult:
        """Benchmark concurrent operations across different framework types."""
        print(
            "🔀 Running mixed framework benchmark: %s threads, mixed frameworks",
            num_threads,
        )

        # Initialize tracer
        _ = HoneyHiveTracer.init(
            api_key="mixed-benchmark-key",
            project="mixed-benchmark",
            source="mixed-test",
            test_mode=True,
        )

        def mixed_worker_task(worker_id: int) -> List[Dict[str, Any]]:
            """Worker task using different framework types."""
            # Create different framework types for each worker
            framework_type = worker_id % 3

            framework: Union[MockFrameworkA, MockFrameworkB, MockFrameworkC]
            if framework_type == 0:
                framework = MockFrameworkA(f"MixedWorkerA_{worker_id}")
            elif framework_type == 1:
                framework = MockFrameworkB(
                    f"MixedWorkerB_{worker_id}", delay_provider_setup=False
                )
            else:
                framework = MockFrameworkC(f"MixedWorkerC_{worker_id}")

            worker_results = []

            for i in range(operations_per_thread):
                start_time = time.perf_counter()

                try:
                    if isinstance(framework, MockFrameworkA):
                        result = framework.execute_operation(
                            f"mixed_op_{worker_id}_{i}"
                        )
                    elif isinstance(framework, MockFrameworkB):
                        result = framework.process_data(
                            f"mixed_data_{worker_id}_{i}", "concurrent"
                        )
                    elif isinstance(framework, MockFrameworkC):
                        result = framework.analyze_content(
                            f"mixed content {worker_id} {i}", "concurrent"
                        )
                    else:
                        result = {
                            "status": "completed",
                            "message": "Unknown framework type",
                        }

                    end_time = time.perf_counter()
                    latency = end_time - start_time

                    worker_results.append(
                        {
                            "worker_id": worker_id,
                            "framework_type": type(framework).__name__,
                            "operation_index": i,
                            "latency": latency,
                            "success": True,
                            "result": result,
                        }
                    )

                except Exception as e:
                    end_time = time.perf_counter()
                    latency = end_time - start_time

                    worker_results.append(
                        {
                            "worker_id": worker_id,
                            "framework_type": type(framework).__name__,
                            "operation_index": i,
                            "latency": latency,
                            "success": False,
                            "error": str(e),
                        }
                    )

            return worker_results

        # Execute mixed concurrent operations
        start_time = time.perf_counter()
        all_results = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(mixed_worker_task, worker_id)
                for worker_id in range(num_threads)
            ]

            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)

        end_time = time.perf_counter()

        return self._analyze_results(all_results, end_time - start_time, num_threads)

    def run_burst_load_benchmark(
        self, burst_size: int = 50, burst_count: int = 10, burst_interval: float = 0.1
    ) -> List[ConcurrentTestResult]:
        """Benchmark performance under burst load patterns."""
        print(
            "💥 Running burst load benchmark: %s bursts of %s operations",
            burst_count,
            burst_size,
        )

        # Initialize tracer
        _ = HoneyHiveTracer.init(
            api_key="burst-benchmark-key",
            project="burst-benchmark",
            source="burst-test",
            test_mode=True,
        )

        burst_results = []

        for burst_idx in range(burst_count):
            print(f"   Executing burst {burst_idx + 1}/{burst_count}...")

            def burst_worker_task(
                worker_id: int, current_burst_idx: int
            ) -> Dict[str, Any]:
                """Single operation for burst testing."""
                framework = MockFrameworkA(
                    f"BurstWorker_{current_burst_idx}_{worker_id}"
                )

                start_time = time.perf_counter()

                try:
                    result = framework.execute_operation(
                        f"burst_op_{current_burst_idx}_{worker_id}",
                        burst_index=current_burst_idx,
                        worker_id=worker_id,
                    )

                    end_time = time.perf_counter()

                    return {
                        "burst_index": current_burst_idx,
                        "worker_id": worker_id,
                        "latency": end_time - start_time,
                        "success": True,
                        "result": result,
                    }

                except Exception as e:
                    end_time = time.perf_counter()

                    return {
                        "burst_index": current_burst_idx,
                        "worker_id": worker_id,
                        "latency": end_time - start_time,
                        "success": False,
                        "error": str(e),
                    }

            # Execute burst
            burst_start_time = time.perf_counter()
            burst_operation_results = []

            with ThreadPoolExecutor(max_workers=burst_size) as executor:
                futures = [
                    executor.submit(burst_worker_task, worker_id, burst_idx)
                    for worker_id in range(burst_size)
                ]

                for future in as_completed(futures):
                    result = future.result()
                    burst_operation_results.append(result)

            burst_end_time = time.perf_counter()

            # Analyze burst results
            burst_result = self._analyze_results(
                burst_operation_results, burst_end_time - burst_start_time, burst_size
            )
            burst_results.append(burst_result)

            # Wait before next burst
            if burst_idx < burst_count - 1:
                time.sleep(burst_interval)

        return burst_results

    def _analyze_results(
        self, results: List[Dict[str, Any]], total_time: float, thread_count: int
    ) -> ConcurrentTestResult:
        """Analyze concurrent test results."""
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        latencies = [r["latency"] for r in results if "latency" in r]

        if not latencies:
            # No latency data available
            return ConcurrentTestResult(
                total_operations=len(results),
                total_time=total_time,
                operations_per_second=0.0,
                average_latency=0.0,
                min_latency=0.0,
                max_latency=0.0,
                p95_latency=0.0,
                p99_latency=0.0,
                thread_count=thread_count,
                success_rate=0.0,
                errors=[r.get("error", "Unknown error") for r in failed_results],
            )

        # Calculate statistics
        latencies.sort()

        return ConcurrentTestResult(
            total_operations=len(results),
            total_time=total_time,
            operations_per_second=len(results) / total_time if total_time > 0 else 0.0,
            average_latency=statistics.mean(latencies),
            min_latency=min(latencies),
            max_latency=max(latencies),
            p95_latency=latencies[int(0.95 * len(latencies))] if latencies else 0.0,
            p99_latency=latencies[int(0.99 * len(latencies))] if latencies else 0.0,
            thread_count=thread_count,
            success_rate=(
                len(successful_results) / len(results) * 100 if results else 0.0
            ),
            errors=[r.get("error", "Unknown error") for r in failed_results],
        )


def run_concurrent_benchmark_suite() -> Dict[str, Any]:
    """Run the complete concurrent benchmark suite."""
    print("⚡ Running Concurrent Performance Benchmark Suite")
    print("=" * 60)

    benchmark = ConcurrentBenchmark()

    # Test 1: Throughput benchmark
    print("1. Throughput Benchmark")
    throughput_result = benchmark.run_throughput_benchmark(
        num_threads=10, operations_per_thread=100
    )
    print(f"   Operations/sec: {throughput_result.operations_per_second:.1f}")
    print(f"   Average latency: {throughput_result.average_latency * 1000:.2f}ms")
    print(f"   P95 latency: {throughput_result.p95_latency * 1000:.2f}ms")
    print(f"   Success rate: {throughput_result.success_rate:.1f}%")
    print()

    # Test 2: Contention benchmark
    print("2. Contention Analysis")
    contention_results = benchmark.run_contention_benchmark(
        max_threads=16, operations_per_thread=50
    )

    print("   Thread Count | Ops/Sec | Avg Latency | P95 Latency")
    print("   -------------|---------|-------------|------------")
    for thread_count, result in contention_results.items():
        print(
            f"   {thread_count:11d} | {result.operations_per_second:7.1f} | "
            f"{result.average_latency * 1000:9.2f}ms | {result.p95_latency * 1000:9.2f}ms"
        )
    print()

    # Test 3: Mixed framework benchmark
    print("3. Mixed Framework Benchmark")
    mixed_result = benchmark.run_mixed_framework_benchmark(
        num_threads=12, operations_per_thread=50
    )
    print(f"   Operations/sec: {mixed_result.operations_per_second:.1f}")
    print(f"   Average latency: {mixed_result.average_latency * 1000:.2f}ms")
    print(f"   Success rate: {mixed_result.success_rate:.1f}%")
    print()

    # Test 4: Burst load benchmark
    print("4. Burst Load Analysis")
    burst_results = benchmark.run_burst_load_benchmark(burst_size=30, burst_count=5)

    print("   Burst | Ops/Sec | Avg Latency | P95 Latency | Success Rate")
    print("   ------|---------|-------------|-------------|-------------")
    for i, result in enumerate(burst_results):
        print(
            f"   {i+1:4d}  | {result.operations_per_second:7.1f} | "
            f"{result.average_latency * 1000:9.2f}ms | {result.p95_latency * 1000:9.2f}ms | "
            f"{result.success_rate:10.1f}%"
        )
    print()

    # Performance analysis
    print("📊 Performance Analysis:")

    # Check throughput requirements (should handle at least 100 ops/sec)
    min_throughput = 100
    throughput_passed = throughput_result.operations_per_second >= min_throughput
    print(
        f"   Throughput: {throughput_result.operations_per_second:.1f} ops/sec "
        f"({'✅ PASS' if throughput_passed else '❌ FAIL'} - min: {min_throughput})"
    )

    # Check latency requirements (P95 should be <10ms)
    max_p95_latency = 0.010  # 10ms
    latency_passed = throughput_result.p95_latency < max_p95_latency
    print(
        f"   P95 Latency: {throughput_result.p95_latency * 1000:.2f}ms "
        f"({'✅ PASS' if latency_passed else '❌ FAIL'} - max: {max_p95_latency * 1000}ms)"
    )

    # Check success rate (should be >99%)
    min_success_rate = 99.0
    success_passed = throughput_result.success_rate >= min_success_rate
    print(
        f"   Success Rate: {throughput_result.success_rate:.1f}% "
        f"({'✅ PASS' if success_passed else '❌ FAIL'} - min: {min_success_rate}%)"
    )

    # Check scalability (performance shouldn't degrade too much with more threads)
    if len(contention_results) >= 2:
        single_thread_ops = contention_results[1].operations_per_second
        max_thread_ops = max(
            r.operations_per_second for r in contention_results.values()
        )
        scalability_ratio = max_thread_ops / single_thread_ops
        scalability_passed = (
            scalability_ratio > 2.0
        )  # Should at least double with more threads
        print(
            f"   Scalability: {scalability_ratio:.1f}x improvement "
            f"({'✅ PASS' if scalability_passed else '❌ FAIL'} - min: 2.0x)"
        )

    all_passed = all([throughput_passed, latency_passed, success_passed])

    print()
    if all_passed:
        print("🎉 All concurrent performance benchmarks passed!")
    else:
        print("⚠️  Some concurrent performance benchmarks failed requirements")

    return {
        "throughput": throughput_result,
        "contention": contention_results,
        "mixed_framework": mixed_result,
        "burst_load": burst_results,
        "all_passed": all_passed,
    }


if __name__ == "__main__":
    # Run concurrent benchmark suite
    results = run_concurrent_benchmark_suite()

    print("\n🔍 Detailed Analysis:")
    print(
        f"Peak throughput: {max(r.operations_per_second for r in results['contention'].values()):.1f} ops/sec"
    )
    print(
        f"Best P95 latency: {min(r.p95_latency for r in results['contention'].values()) * 1000:.2f}ms"
    )
    print(
        f"Thread scalability: Up to {max(results['contention'].keys())} concurrent threads tested"
    )
