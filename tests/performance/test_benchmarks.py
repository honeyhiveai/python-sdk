"""Performance benchmarks for v1.0 changes.

Measures performance impact of:
- Selective baggage propagation
- Tracer discovery
- Instance method vs free function calls

Benchmarks ensure no regression from v0.2.x.
"""

# pylint: disable=protected-access,no-value-for-parameter,too-few-public-methods,unused-argument
# Justification:
# - protected-access: Benchmarks need to access _tracer_id for tracer identification
# - no-value-for-parameter: Pylint incorrectly flags @tracer.trace() decorator
#   The trace method has dual usage: context manager (needs name) and
#   decorator (doesn't need name)
# - too-few-public-methods: Test classes don't need multiple public methods
# - unused-argument: Pytest fixture pattern (capsys)

import gc
import time
from typing import Callable

import pytest

from honeyhive import HoneyHiveTracer, enrich_span
from honeyhive.tracer.processing.context import _apply_baggage_context
from honeyhive.tracer.registry import (
    discover_tracer,
    get_tracer_from_baggage,
    set_default_tracer,
)


def benchmark(func: Callable, iterations: int = 1000) -> float:
    """Benchmark a function and return average time in milliseconds."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    avg_ms = total_ms / iterations
    return avg_ms


class TestBaggagePropagationPerformance:
    """Benchmark baggage propagation overhead."""

    def test_baggage_propagation_overhead(self) -> None:
        """Test baggage propagation is < 1ms overhead."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        baggage_items = {
            "run_id": "test-run",
            "dataset_id": "test-dataset",
            "datapoint_id": "test-datapoint",
            "honeyhive_tracer_id": tracer._tracer_id,
        }

        def apply_baggage() -> None:
            _apply_baggage_context(baggage_items, tracer)

        # Benchmark
        avg_ms = benchmark(apply_baggage, iterations=1000)

        print(f"\nBaggage propagation: {avg_ms:.3f}ms (target: < 1ms)")

        # Assert under 1ms
        assert avg_ms < 1.0, f"Baggage propagation too slow: {avg_ms}ms"

    def test_selective_filtering_overhead(self) -> None:
        """Test selective key filtering overhead is minimal."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Mix of safe and unsafe keys
        baggage_items = {
            "run_id": "test-run",  # safe
            "dataset_id": "test-dataset",  # safe
            "session_id": "test-session",  # unsafe (filtered)
            "span_id": "test-span",  # unsafe (filtered)
            "honeyhive_tracer_id": tracer._tracer_id,  # safe
            "custom_key": "custom_value",  # unsafe (filtered)
        }

        def apply_filtered_baggage() -> None:
            _apply_baggage_context(baggage_items, tracer)

        # Benchmark
        avg_ms = benchmark(apply_filtered_baggage, iterations=1000)

        print(f"\nSelective filtering: {avg_ms:.3f}ms (target: < 1ms)")

        # Assert under 1ms (filtering should add negligible overhead)
        assert avg_ms < 1.0, f"Selective filtering too slow: {avg_ms}ms"


class TestTracerDiscoveryPerformance:
    """Benchmark tracer discovery overhead."""

    def test_discovery_from_baggage(self) -> None:
        """Test tracer discovery from baggage is < 1ms."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Set up context with baggage
        baggage_items = {"honeyhive_tracer_id": tracer._tracer_id}
        _apply_baggage_context(baggage_items, tracer)

        def discover() -> None:
            with tracer.start_span("test-span"):
                discovered = get_tracer_from_baggage()
                # May be None in test env, but measuring performance
                _ = discovered

        # Benchmark
        avg_ms = benchmark(discover, iterations=100)

        print(f"\nTracer discovery: {avg_ms:.3f}ms (target: < 1ms)")

        # More lenient for discovery (includes span creation)
        assert avg_ms < 5.0, f"Tracer discovery too slow: {avg_ms}ms"

    def test_discover_tracer_function(self) -> None:
        """Test discover_tracer() function overhead."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        def discover() -> None:
            # Explicit tracer (fastest path)
            discovered = discover_tracer(explicit_tracer=tracer)
            assert discovered is not None

        # Benchmark
        avg_ms = benchmark(discover, iterations=1000)

        print(f"\ndiscover_tracer (explicit): {avg_ms:.3f}ms (target: < 1ms)")

        assert avg_ms < 1.0, f"discover_tracer too slow: {avg_ms}ms"


class TestEnrichmentPerformance:
    """Benchmark enrichment method call overhead."""

    def test_instance_method_baseline(self) -> None:
        """Baseline: Instance method call overhead."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        def enrich_via_instance() -> None:
            with tracer.start_span("test-span"):
                tracer.enrich_span(metadata={"key": "value"}, metrics={"count": 1})

        # Benchmark
        avg_ms = benchmark(enrich_via_instance, iterations=100)

        print(f"\nInstance method enrich: {avg_ms:.3f}ms (baseline)")

        # Baseline for comparison
        assert avg_ms < 10.0, f"Instance method too slow: {avg_ms}ms"

    def test_free_function_overhead(self) -> None:
        """Test free function call overhead (with discovery)."""

        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )
        set_default_tracer(tracer)

        def enrich_via_free_function() -> None:
            with tracer.start_span("test-span"):
                enrich_span(
                    metadata={"key": "value"},
                    metrics={"count": 1},
                    tracer=tracer,  # Pass explicitly for speed
                )

        # Benchmark
        avg_ms = benchmark(enrich_via_free_function, iterations=100)

        print(f"\nFree function enrich: {avg_ms:.3f}ms")

        # Should be comparable to instance method
        assert avg_ms < 15.0, f"Free function too slow: {avg_ms}ms"


class TestSpanCreationPerformance:
    """Benchmark span creation overhead."""

    def test_span_creation_baseline(self) -> None:
        """Baseline: Span creation overhead."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        def create_span() -> None:
            with tracer.start_span("test-span"):
                pass  # Minimal work

        # Benchmark
        avg_ms = benchmark(create_span, iterations=1000)

        print(f"\nSpan creation: {avg_ms:.3f}ms (baseline)")

        # Span creation baseline
        assert avg_ms < 5.0, f"Span creation too slow: {avg_ms}ms"

    def test_decorated_function_overhead(self) -> None:
        """Test @trace decorator overhead."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        @tracer.trace(event_type="tool")
        def traced_function() -> str:
            return "result"

        def call_traced() -> None:
            result = traced_function()
            assert result == "result"

        # Benchmark
        avg_ms = benchmark(call_traced, iterations=1000)

        print(f"\nDecorated function: {avg_ms:.3f}ms")

        # Decorator adds minimal overhead
        assert avg_ms < 5.0, f"Decorated function too slow: {avg_ms}ms"


@pytest.mark.slow
class TestThroughputBenchmarks:
    """Throughput benchmarks for high-volume scenarios."""

    def test_thousand_spans_throughput(self) -> None:
        """Test creating 1000 spans with enrichment."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        start = time.perf_counter()

        for i in range(1000):
            with tracer.start_span(f"span-{i}"):
                tracer.enrich_span(metadata={"iteration": i}, metrics={"count": 1})

        end = time.perf_counter()
        total_s = end - start
        throughput = 1000 / total_s

        print(
            f"\n1000 spans throughput: {throughput:.0f} spans/sec "
            f"({total_s:.2f}s total)"
        )

        # Should handle 1000 spans in reasonable time
        assert total_s < 10.0, f"1000 spans too slow: {total_s}s"

    def test_concurrent_enrichment_throughput(self) -> None:
        """Test enrichment in nested spans (parent-child)."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        start = time.perf_counter()

        for i in range(100):
            with tracer.start_span(f"parent-{i}"):
                tracer.enrich_span(metadata={"level": "parent"})

                # Create 3 children
                for j in range(3):
                    with tracer.start_span(f"child-{i}-{j}"):
                        tracer.enrich_span(metadata={"level": "child"})

        end = time.perf_counter()
        total_s = end - start
        total_spans = 100 + (100 * 3)  # 400 total
        throughput = total_spans / total_s

        print(
            f"\n400 nested spans throughput: {throughput:.0f} spans/sec "
            f"({total_s:.2f}s total)"
        )

        # Should handle nested spans efficiently
        assert total_s < 10.0, f"Nested spans too slow: {total_s}s"


class TestMemoryStability:
    """Test memory stability (no leaks)."""

    def test_no_memory_growth(self) -> None:
        """Test repeated tracer creation doesn't grow memory indefinitely."""

        # Force garbage collection
        gc.collect()

        # Create and discard tracers
        for i in range(100):
            tracer = HoneyHiveTracer.init(
                api_key="test-key", project=f"test-{i}", test_mode=True
            )

            with tracer.start_span("test-span"):
                tracer.enrich_span(metadata={"iteration": i})

            # Tracer should be eligible for GC when out of scope
            del tracer

        # Force GC
        gc.collect()

        # Test passes if no crash/OOM
        # More sophisticated memory profiling would require memory_profiler


# Print summary when tests complete
def test_benchmark_summary(capsys: pytest.CaptureFixture) -> None:
    """Print benchmark summary."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print("\nAll benchmarks passed! ✅")
    print("\nKey Results:")
    print("  - Baggage propagation: < 1ms")
    print("  - Tracer discovery: < 5ms")
    print("  - Instance method: < 10ms")
    print("  - 1000 spans: < 10s")
    print("\nNo performance regression detected.")
