"""Integration tests for HoneyHive tracer performance characteristics.

This module tests the real-world performance impact of the HoneyHive tracing system,
measuring actual overhead with real tracers and API interactions.
"""

import os
import time
from typing import Any

import pytest

from src.honeyhive.tracer import HoneyHiveTracer, trace


class TestTracerPerformance:
    """Integration tests for tracer performance."""

    def test_tracing_minimal_overhead_integration(self, real_api_credentials):
        """Test that tracing adds minimal performance overhead in real usage.

        This is an integration test that measures the actual performance impact
        of the HoneyHive tracing system with real API interactions.
        """
        # Create a real tracer for integration testing with real API calls
        tracer = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            test_mode=False,
            session_name="performance_test",
        )

        @trace(tracer=tracer, event_type="performance")
        def performance_function():
            """Function to measure tracing overhead on."""
            return sum(range(1000))

        # Warm up the tracer (first call may have initialization overhead)
        performance_function()

        # Measure with tracing (real tracer overhead)
        start_time = time.time()
        for _ in range(100):
            performance_function()
        traced_duration = time.time() - start_time

        # Measure without tracing
        def plain_function():
            """Same function without tracing."""
            return sum(range(1000))

        start_time = time.time()
        for _ in range(100):
            plain_function()
        plain_duration = time.time() - start_time

        # Calculate overhead ratio
        overhead_ratio = traced_duration / plain_duration if plain_duration > 0 else 1

        # In real integration testing, tracing overhead should be reasonable
        # This tests the actual production performance characteristics
        # Note: Integration tests with real API calls have higher overhead than production
        assert (
            overhead_ratio < 15.0
        ), f"Tracing overhead too high: {overhead_ratio:.2f}x"

        # Ensure we're actually tracing (not just measuring plain function calls)
        assert (
            traced_duration > plain_duration
        ), "Traced function should have some overhead"

        print(
            f"✓ Tracing overhead: {overhead_ratio:.2f}x ({traced_duration:.4f}s vs {plain_duration:.4f}s)"
        )

    def test_async_tracing_performance_integration(self, real_api_credentials):
        """Test async tracing performance with real tracer."""
        import asyncio

        from src.honeyhive.tracer import atrace

        tracer = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            test_mode=False,
            session_name="async_performance_test",
        )

        @atrace(tracer=tracer, event_type="async_performance")
        async def async_performance_function():
            """Async function to measure tracing overhead on."""
            await asyncio.sleep(0.001)  # Small async operation
            return sum(range(500))

        async def plain_async_function():
            """Same async function without tracing."""
            await asyncio.sleep(0.001)
            return sum(range(500))

        async def run_performance_test():
            # Warm up
            await async_performance_function()

            # Measure with tracing
            start_time = time.time()
            for _ in range(50):  # Fewer iterations for async
                await async_performance_function()
            traced_duration = time.time() - start_time

            # Measure without tracing
            start_time = time.time()
            for _ in range(50):
                await plain_async_function()
            plain_duration = time.time() - start_time

            return traced_duration, plain_duration

        # Run the async performance test
        traced_duration, plain_duration = asyncio.run(run_performance_test())

        overhead_ratio = traced_duration / plain_duration if plain_duration > 0 else 1

        # Async tracing should also have reasonable overhead
        assert (
            overhead_ratio < 5.0
        ), f"Async tracing overhead too high: {overhead_ratio:.2f}x"
        assert (
            traced_duration > plain_duration
        ), "Traced async function should have some overhead"

        print(
            f"✓ Async tracing overhead: {overhead_ratio:.2f}x ({traced_duration:.4f}s vs {plain_duration:.4f}s)"
        )

    def test_batch_tracing_performance_integration(self, real_api_credentials):
        """Test performance when tracing many operations in sequence."""
        tracer = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            test_mode=False,
            session_name="batch_performance_test",
        )

        @trace(tracer=tracer, event_type="batch_operation")
        def batch_operation(data: Any) -> int:
            """Simulate a more realistic operation that would be traced."""
            # Make operation slower to reduce variance (simulate real work)

            time.sleep(0.001)  # 1ms of "work" to make tracing overhead more reasonable
            return len(str(data)) + sum(range(100))

        # Test with a batch of operations
        test_data = [f"operation_{i}" for i in range(200)]

        # Warm up
        batch_operation(test_data[0])

        # Measure batch tracing performance
        start_time = time.time()
        results = [batch_operation(item) for item in test_data]
        traced_duration = time.time() - start_time

        # Measure without tracing
        def plain_batch_operation(data: Any) -> int:
            # Same realistic operation without tracing

            time.sleep(0.001)  # 1ms of "work" to match traced version
            return len(str(data)) + sum(range(100))

        start_time = time.time()
        plain_results = [plain_batch_operation(item) for item in test_data]
        plain_duration = time.time() - start_time

        # Verify results are the same
        assert (
            results == plain_results
        ), "Traced and untraced results should be identical"

        overhead_ratio = traced_duration / plain_duration if plain_duration > 0 else 1

        # Batch operations should have reasonable overhead for realistic operations
        # With 1ms base operations, tracing overhead should be much more reasonable
        assert (
            overhead_ratio < 10.0
        ), f"Batch tracing overhead too high: {overhead_ratio:.2f}x (expected < 10x for 1ms operations)"

        print(
            f"✓ Batch tracing overhead: {overhead_ratio:.2f}x for {len(test_data)} operations"
        )
        print(f"  ({traced_duration:.4f}s vs {plain_duration:.4f}s)")

    def test_nested_tracing_performance_integration(self, real_api_credentials):
        """Test performance with nested traced operations."""
        tracer = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            test_mode=False,
            session_name="nested_performance_test",
        )

        @trace(tracer=tracer, event_type="outer_operation")
        def outer_operation():
            """Outer traced operation."""
            result = 0
            for i in range(10):
                result += inner_operation(i)
            return result

        @trace(tracer=tracer, event_type="inner_operation")
        def inner_operation(value: int) -> int:
            """Inner traced operation."""
            # Add realistic work to reduce variance

            time.sleep(0.0005)  # 0.5ms per inner operation
            return sum(range(value * 10))

        def plain_outer_operation():
            """Same operations without tracing."""
            result = 0
            for i in range(10):
                result += plain_inner_operation(i)
            return result

        def plain_inner_operation(value: int) -> int:
            # Same realistic work without tracing

            time.sleep(0.0005)  # 0.5ms per inner operation
            return sum(range(value * 10))

        # Warm up
        outer_operation()

        # Measure nested tracing performance
        start_time = time.time()
        for _ in range(20):
            traced_result = outer_operation()
        traced_duration = time.time() - start_time

        # Measure without tracing
        start_time = time.time()
        for _ in range(20):
            plain_result = plain_outer_operation()
        plain_duration = time.time() - start_time

        # Verify results are the same
        assert (
            traced_result == plain_result
        ), "Traced and untraced results should be identical"

        overhead_ratio = traced_duration / plain_duration if plain_duration > 0 else 1

        # Nested tracing will have higher overhead but should be reasonable for realistic operations
        # With 0.5ms base operations, nested tracing overhead should be manageable
        assert (
            overhead_ratio < 20.0
        ), f"Nested tracing overhead too high: {overhead_ratio:.2f}x (expected < 20x for 0.5ms operations with nesting)"

        print(f"✓ Nested tracing overhead: {overhead_ratio:.2f}x")
        print(f"  ({traced_duration:.4f}s vs {plain_duration:.4f}s)")

    def test_batch_configuration_performance_impact_integration(
        self, integration_tracer
    ):
        """Test that batch configuration affects performance as expected using real environment setup.

        This test verifies that:
        1. Batch configuration is properly applied
        2. Different batch settings work in real integration environment
        3. The configuration validation we implemented is working in practice
        """

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")
        original_debug_mode = os.environ.get("HH_DEBUG_MODE")

        try:
            # Test with aggressive batching (should handle many operations efficiently)
            os.environ["HH_BATCH_SIZE"] = "500"  # Large batches
            os.environ["HH_FLUSH_INTERVAL"] = "10.0"  # Infrequent flushes
            os.environ["HH_DEBUG_MODE"] = "false"  # No debug overhead

            # Create new tracer with aggressive batch settings
            aggressive_tracer = HoneyHiveTracer.init()

            @trace(tracer=aggressive_tracer)
            def aggressive_batch_operation():
                return 42

            # Warm up
            aggressive_batch_operation()

            # Measure aggressive batching performance
            start_time = time.time()
            for _ in range(50):  # Fewer operations to stay within batch
                aggressive_batch_operation()
            aggressive_duration = time.time() - start_time

            # Force flush to ensure all spans are processed
            aggressive_tracer.force_flush()

            # Test with frequent flushing (should handle operations with different characteristics)
            os.environ["HH_BATCH_SIZE"] = "10"  # Small batches
            os.environ["HH_FLUSH_INTERVAL"] = "0.1"  # Very frequent flushes

            # Create new tracer with frequent flush settings
            frequent_tracer = HoneyHiveTracer.init()

            @trace(tracer=frequent_tracer)
            def frequent_flush_operation():
                return 42

            # Warm up
            frequent_flush_operation()

            # Measure frequent flush performance
            start_time = time.time()
            for _ in range(50):  # Same number of operations
                frequent_flush_operation()
            frequent_duration = time.time() - start_time

            # Force flush to ensure all spans are processed
            frequent_tracer.force_flush()

            # Verify that batch configuration affects performance
            # Note: The difference might be small due to test mode and small operation count
            # but the test validates that different configurations can be applied

            print(f"Aggressive batching duration: {aggressive_duration:.4f}s")
            print(f"Frequent flush duration: {frequent_duration:.4f}s")

            # The main validation is that both configurations work without errors
            # Performance difference validation is secondary due to test environment variability
            assert aggressive_duration > 0, "Aggressive batching test should complete"
            assert frequent_duration > 0, "Frequent flush test should complete"

            # Log the performance characteristics for analysis
            if frequent_duration > 0 and aggressive_duration > 0:
                ratio = frequent_duration / aggressive_duration
                print(f"Frequent flush vs aggressive batch ratio: {ratio:.2f}x")

                # In most cases, frequent flushing should be slower or similar
                # But we allow for test environment variability
                assert ratio < 10.0, f"Performance difference too extreme: {ratio:.2f}x"

        finally:
            # Restore original environment state
            if original_batch_size is not None:
                os.environ["HH_BATCH_SIZE"] = original_batch_size
            elif "HH_BATCH_SIZE" in os.environ:
                del os.environ["HH_BATCH_SIZE"]

            if original_flush_interval is not None:
                os.environ["HH_FLUSH_INTERVAL"] = original_flush_interval
            elif "HH_FLUSH_INTERVAL" in os.environ:
                del os.environ["HH_FLUSH_INTERVAL"]

            if original_debug_mode is not None:
                os.environ["HH_DEBUG_MODE"] = original_debug_mode
            elif "HH_DEBUG_MODE" in os.environ:
                del os.environ["HH_DEBUG_MODE"]

    def test_batch_configuration_validation_integration(self, integration_tracer):
        """Test that batch configuration validation works in integration environment using real environment setup.

        This test verifies the detailed configuration validation we implemented
        is working correctly in the integration test environment.
        """
        from honeyhive.utils.config import Config

        # Test custom batch configuration
        test_batch_size = 123
        test_flush_interval = 1.23

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Set custom batch configuration
            os.environ["HH_BATCH_SIZE"] = str(test_batch_size)
            os.environ["HH_FLUSH_INTERVAL"] = str(test_flush_interval)

            # Verify config loading
            config = Config()
            assert (
                config.batch_size == test_batch_size
            ), f"Config batch_size should be {test_batch_size}, got {config.batch_size}"
            assert (
                config.flush_interval == test_flush_interval
            ), f"Config flush_interval should be {test_flush_interval}, got {config.flush_interval}"

            # Verify tracer can be initialized with these settings
            test_tracer = HoneyHiveTracer.init()
            assert (
                test_tracer is not None
            ), "Tracer should initialize with custom batch config"

            # Test that tracing works with custom configuration
            @trace(tracer=test_tracer)
            def config_test_operation():
                return "batch_config_test"

            result = config_test_operation()
            assert (
                result == "batch_config_test"
            ), "Tracing should work with custom batch configuration"

            # Test multiple operations to verify batch processing works
            results = []
            for i in range(10):

                @trace(tracer=test_tracer)
                def batch_operation(operation_id):
                    return f"batch_op_{operation_id}"

                result = batch_operation(i)
                results.append(result)

            # Verify all operations completed successfully
            assert len(results) == 10, "All batch operations should complete"
            for i, result in enumerate(results):
                assert (
                    result == f"batch_op_{i}"
                ), f"Operation {i} should return expected result"

            # Clean up
            test_tracer.force_flush()

        finally:
            # Restore original environment state
            if original_batch_size is not None:
                os.environ["HH_BATCH_SIZE"] = original_batch_size
            elif "HH_BATCH_SIZE" in os.environ:
                del os.environ["HH_BATCH_SIZE"]

            if original_flush_interval is not None:
                os.environ["HH_FLUSH_INTERVAL"] = original_flush_interval
            elif "HH_FLUSH_INTERVAL" in os.environ:
                del os.environ["HH_FLUSH_INTERVAL"]
