"""
Memory profiling tests for HoneyHive non-instrumentor integration.

This module provides detailed memory profiling for:
- Memory allocation patterns
- Memory leak detection
- Peak memory usage analysis
- Garbage collection impact
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,import-error
# Justification: Performance memory test file with comprehensive profiling requiring protected member access and optional memory_profiler

import gc
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import psutil  # type: ignore[import-untyped]
from memory_profiler import profile  # type: ignore[import-untyped]
from opentelemetry import trace

from honeyhive import HoneyHiveTracer
from tests.mocks.mock_frameworks import MockFrameworkA, MockFrameworkB, MockFrameworkC


class MemoryProfiler:
    """Advanced memory profiling for HoneyHive integration."""

    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = None
        self.peak_memory = None
        self.memory_samples: List[Dict[str, Any]] = []

    def start_profiling(self) -> None:
        """Start memory profiling."""
        gc.collect()  # Clean up before baseline
        self.baseline_memory = self.process.memory_info().rss
        self.memory_samples = []
        if self.baseline_memory is not None:
            print(
                f"🔍 Memory profiling started - Baseline: {self.baseline_memory / 1024 / 1024:.2f} MB"
            )

    def sample_memory(self, label: str = "") -> Dict[str, Any]:
        """Take a memory sample."""
        current_memory = self.process.memory_info().rss
        sample = {
            "timestamp": time.time(),
            "memory_rss": current_memory,
            "memory_mb": current_memory / 1024 / 1024,
            "label": label,
        }
        self.memory_samples.append(sample)

        if self.peak_memory is None or current_memory > self.peak_memory:
            self.peak_memory = current_memory

        return sample

    def stop_profiling(self) -> Dict[str, Any]:
        """Stop profiling and return analysis."""
        gc.collect()  # Clean up after profiling
        final_memory = self.process.memory_info().rss

        if (
            not self.memory_samples
            or self.baseline_memory is None
            or self.peak_memory is None
        ):
            return {"error": "No memory samples collected or profiling not started"}

        analysis = {
            "baseline_mb": self.baseline_memory / 1024 / 1024,
            "peak_mb": self.peak_memory / 1024 / 1024,
            "final_mb": final_memory / 1024 / 1024,
            "peak_overhead_mb": (self.peak_memory - self.baseline_memory) / 1024 / 1024,
            "final_overhead_mb": (final_memory - self.baseline_memory) / 1024 / 1024,
            "peak_overhead_percent": (
                (self.peak_memory - self.baseline_memory) / self.baseline_memory
            )
            * 100,
            "final_overhead_percent": (
                (final_memory - self.baseline_memory) / self.baseline_memory
            )
            * 100,
            "samples_count": len(self.memory_samples),
            "samples": self.memory_samples,
        }

        print("📊 Memory profiling completed:")
        print(f"   Baseline: {analysis['baseline_mb']:.2f} MB")
        print(
            "   Peak: %.2f MB (+%.2f MB, +%.1f%%)",
            analysis["peak_mb"],
            analysis["peak_overhead_mb"],
            analysis["peak_overhead_percent"],
        )
        print(
            "   Final: %.2f MB (+%.2f MB, +%.1f%%)",
            analysis["final_mb"],
            analysis["final_overhead_mb"],
            analysis["final_overhead_percent"],
        )

        return analysis


def test_memory_usage_single_framework() -> Dict[str, Any]:
    """Test memory usage with a single framework."""
    profiler = MemoryProfiler()
    profiler.start_profiling()

    # Initialize tracer
    profiler.sample_memory("before_tracer_init")
    _ = HoneyHiveTracer.init(
        api_key="memory-test-key",
        project="memory-test-project",
        source="memory-test",
        test_mode=True,
    )
    profiler.sample_memory("after_tracer_init")

    # Create framework
    framework = MockFrameworkA("MemoryTestFramework")
    profiler.sample_memory("after_framework_creation")

    # Execute operations
    for i in range(100):
        framework.execute_operation(f"memory_op_{i}", data_size=1000)
        if i % 20 == 0:
            profiler.sample_memory(f"after_{i}_operations")

    profiler.sample_memory("after_all_operations")

    # Get operations (potential memory accumulation)
    _ = framework.get_operations()  # operations
    profiler.sample_memory("after_get_operations")

    analysis = profiler.stop_profiling()

    # Verify memory usage is reasonable
    assert (
        analysis["peak_overhead_percent"] < 10.0
    ), f"Memory overhead too high: {analysis['peak_overhead_percent']:.1f}%"

    return analysis


def test_memory_usage_multiple_frameworks() -> Dict[str, Any]:
    """Test memory usage with multiple frameworks."""
    profiler = MemoryProfiler()
    profiler.start_profiling()

    # Initialize tracer
    _ = HoneyHiveTracer.init(
        api_key="memory-test-key",
        project="memory-test-project",
        source="memory-test",
        test_mode=True,
    )
    profiler.sample_memory("after_tracer_init")

    # Create multiple frameworks
    frameworks = []
    for i in range(10):
        framework_a = MockFrameworkA(f"MemoryA_{i}")
        framework_b = MockFrameworkB(f"MemoryB_{i}", delay_provider_setup=False)
        framework_c = MockFrameworkC(f"MemoryC_{i}")
        frameworks.extend([framework_a, framework_b, framework_c])

    profiler.sample_memory("after_framework_creation")

    # Execute operations on all frameworks
    for i, framework in enumerate(frameworks):
        if isinstance(framework, MockFrameworkA):
            framework.execute_operation(f"multi_op_{i}", batch_size=50)
        elif isinstance(framework, MockFrameworkB):
            framework.process_data(f"multi_data_{i}", "memory_test")
        elif isinstance(framework, MockFrameworkC):
            framework.analyze_content(f"multi content {i}", "memory_analysis")

        if i % 10 == 0:
            profiler.sample_memory(f"after_framework_{i}")

    profiler.sample_memory("after_all_frameworks")

    analysis = profiler.stop_profiling()

    # Verify memory usage scales reasonably
    assert (
        analysis["peak_overhead_percent"] < 15.0
    ), f"Memory overhead too high for multiple frameworks: {analysis['peak_overhead_percent']:.1f}%"

    return analysis


def test_memory_leak_detection() -> Dict[str, Any]:
    """Test for memory leaks over repeated operations."""
    profiler = MemoryProfiler()
    profiler.start_profiling()

    # Initialize tracer
    _ = HoneyHiveTracer.init(
        api_key="leak-test-key",
        project="leak-test-project",
        source="leak-test",
        test_mode=True,
    )

    framework = MockFrameworkA("LeakTestFramework")
    profiler.sample_memory("initial_state")

    # Run multiple cycles to detect leaks
    for cycle in range(5):
        # Execute many operations
        for i in range(200):
            framework.execute_operation(f"leak_test_cycle_{cycle}_op_{i}")

        # Force garbage collection
        gc.collect()
        profiler.sample_memory(f"after_cycle_{cycle}")

        # Reset framework state
        framework.reset()

    analysis = profiler.stop_profiling()

    # Check for memory leaks by comparing first and last cycles
    samples = analysis["samples"]
    cycle_samples = [s for s in samples if "after_cycle_" in s["label"]]

    if len(cycle_samples) >= 2:
        first_cycle_memory = cycle_samples[0]["memory_mb"]
        last_cycle_memory = cycle_samples[-1]["memory_mb"]
        memory_growth = last_cycle_memory - first_cycle_memory
        growth_percent = (memory_growth / first_cycle_memory) * 100

        print("🔍 Memory leak analysis:")
        print(f"   First cycle: {first_cycle_memory:.2f} MB")
        print(f"   Last cycle: {last_cycle_memory:.2f} MB")
        print(f"   Growth: {memory_growth:.2f} MB ({growth_percent:.1f}%)")

        # Verify no significant memory leaks (allow 2% growth for normal variance)
        assert (
            growth_percent < 2.0
        ), f"Potential memory leak detected: {growth_percent:.1f}% growth over cycles"

    return analysis


def test_concurrent_memory_usage() -> Dict[str, Any]:
    """Test memory usage under concurrent load."""
    profiler = MemoryProfiler()
    profiler.start_profiling()

    # Initialize tracer
    _ = HoneyHiveTracer.init(
        api_key="concurrent-memory-test-key",
        project="concurrent-memory-test",
        source="concurrent-test",
        test_mode=True,
    )
    profiler.sample_memory("after_tracer_init")

    def worker_task(worker_id: int, operations_count: int) -> List[Any]:
        """Worker task for concurrent execution."""
        framework = MockFrameworkA(f"ConcurrentWorker_{worker_id}")
        results = []

        for i in range(operations_count):
            result = framework.execute_operation(
                f"concurrent_op_{worker_id}_{i}", worker_id=worker_id, operation_index=i
            )
            results.append(result)

        return results

    # Execute concurrent operations
    num_workers = 8
    operations_per_worker = 50

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(worker_task, worker_id, operations_per_worker)
            for worker_id in range(num_workers)
        ]

        # Sample memory during execution
        for i, future in enumerate(futures):
            future.result()  # Wait for completion
            profiler.sample_memory(f"after_worker_{i}")

    profiler.sample_memory("after_all_workers")

    analysis = profiler.stop_profiling()

    # Verify concurrent memory usage is reasonable
    assert (
        analysis["peak_overhead_percent"] < 20.0
    ), f"Concurrent memory overhead too high: {analysis['peak_overhead_percent']:.1f}%"

    return analysis


@profile  # type: ignore[misc]
def memory_intensive_tracer_operations() -> List[Any]:
    """Memory-intensive operations for line-by-line profiling."""
    # Initialize multiple tracers
    tracers = []
    for i in range(5):
        trace._TRACER_PROVIDER = None  # Reset for clean initialization

        tracer = HoneyHiveTracer.init(
            api_key=f"profile-key-{i}",
            project=f"profile-project-{i}",
            source=f"profile-source-{i}",
            test_mode=True,
        )
        tracers.append(tracer)

    # Create frameworks
    frameworks = []
    for i in range(10):
        framework_a = MockFrameworkA(f"ProfileA_{i}")
        framework_b = MockFrameworkB(f"ProfileB_{i}", delay_provider_setup=False)
        frameworks.extend([framework_a, framework_b])

    # Execute operations
    results = []
    for i, framework in enumerate(frameworks):
        if isinstance(framework, MockFrameworkA):
            result = framework.execute_operation(f"profile_op_{i}", data_size=500)
        elif isinstance(framework, MockFrameworkB):
            result = framework.process_data(f"profile_data_{i}" * 10, "profiling")
        else:
            result = {"status": "completed", "message": "Unknown framework type"}

        results.append(result)

    return results


def run_memory_profiling_suite() -> Dict[str, Any]:
    """Run the complete memory profiling suite."""
    print("🧠 Running Memory Profiling Suite")
    print("=" * 50)

    # Test 1: Single framework memory usage
    print("1. Single Framework Memory Usage")
    single_analysis = test_memory_usage_single_framework()
    print(f"   Result: {single_analysis['peak_overhead_percent']:.1f}% peak overhead")
    print()

    # Test 2: Multiple frameworks memory usage
    print("2. Multiple Frameworks Memory Usage")
    multi_analysis = test_memory_usage_multiple_frameworks()
    print(f"   Result: {multi_analysis['peak_overhead_percent']:.1f}% peak overhead")
    print()

    # Test 3: Memory leak detection
    print("3. Memory Leak Detection")
    _ = test_memory_leak_detection()  # leak_analysis
    print("   Result: No significant leaks detected")
    print()

    # Test 4: Concurrent memory usage
    print("4. Concurrent Memory Usage")
    concurrent_analysis = test_concurrent_memory_usage()
    print(
        f"   Result: {concurrent_analysis['peak_overhead_percent']:.1f}% peak overhead"
    )
    print()

    # Summary
    print("📊 Memory Profiling Summary:")
    print(
        f"   Single framework: {single_analysis['peak_overhead_percent']:.1f}% overhead"
    )
    print(
        f"   Multiple frameworks: {multi_analysis['peak_overhead_percent']:.1f}% overhead"
    )
    print(
        f"   Concurrent usage: {concurrent_analysis['peak_overhead_percent']:.1f}% overhead"
    )

    # Check if all tests meet requirements (<5% overhead)
    max_overhead = 5.0
    all_passed = all(
        [
            single_analysis["peak_overhead_percent"] < max_overhead,
            multi_analysis["peak_overhead_percent"]
            < max_overhead * 2,  # Allow higher for multiple frameworks
            concurrent_analysis["peak_overhead_percent"]
            < max_overhead * 3,  # Allow higher for concurrent
        ]
    )

    if all_passed:
        print("✅ All memory profiling tests passed!")
    else:
        print("❌ Some memory profiling tests exceeded thresholds")

    return {
        "single_framework": single_analysis,
        "multiple_frameworks": multi_analysis,
        "concurrent": concurrent_analysis,
        "all_passed": all_passed,
    }


if __name__ == "__main__":
    # Run memory profiling suite
    results = run_memory_profiling_suite()

    print("\n🔬 Running detailed line-by-line memory profiling...")
    print("(This will show memory usage for each line of code)")
    memory_intensive_tracer_operations()
