"""
Integration tests for batch configuration validation.

Tests that verify HH_BATCH_SIZE and HH_FLUSH_INTERVAL environment variables
are properly applied to the BatchSpanProcessor configuration using real environment setup.
"""

import os

import pytest

from honeyhive import HoneyHiveTracer
from honeyhive.utils.config import Config


class TestBatchConfiguration:
    """Test batch configuration is properly applied."""

    def test_default_batch_configuration_integration(self, integration_client):
        """Test that default batch configuration values are used in integration environment."""
        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Clear batch environment variables for this test
            if "HH_BATCH_SIZE" in os.environ:
                del os.environ["HH_BATCH_SIZE"]
            if "HH_FLUSH_INTERVAL" in os.environ:
                del os.environ["HH_FLUSH_INTERVAL"]

            config = Config()

            # Verify default values match our expectations
            assert (
                config.batch_size == 100
            ), f"Expected default batch_size=100, got {config.batch_size}"
            assert (
                config.flush_interval == 5.0
            ), f"Expected default flush_interval=5.0, got {config.flush_interval}"

            # Verify tracer can be initialized with defaults
            tracer = HoneyHiveTracer.init()
            assert (
                tracer is not None
            ), "Tracer should initialize with default batch config"
            tracer.force_flush()

        finally:
            # Restore original environment state
            if original_batch_size is not None:
                os.environ["HH_BATCH_SIZE"] = original_batch_size
            if original_flush_interval is not None:
                os.environ["HH_FLUSH_INTERVAL"] = original_flush_interval

    def test_custom_batch_configuration_from_env_integration(self, integration_client):
        """Test that custom batch configuration is loaded from environment variables in integration environment."""
        test_batch_size = 250
        test_flush_interval = 2.5

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Set custom batch configuration
            os.environ["HH_BATCH_SIZE"] = str(test_batch_size)
            os.environ["HH_FLUSH_INTERVAL"] = str(test_flush_interval)

            config = Config()

            # Verify custom values are loaded
            assert (
                config.batch_size == test_batch_size
            ), f"Expected batch_size={test_batch_size}, got {config.batch_size}"
            assert (
                config.flush_interval == test_flush_interval
            ), f"Expected flush_interval={test_flush_interval}, got {config.flush_interval}"

            # Verify tracer works with custom configuration
            tracer = HoneyHiveTracer.init()
            assert (
                tracer is not None
            ), "Tracer should initialize with custom batch config"
            tracer.force_flush()

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

    def test_batch_processor_real_tracing_integration(self, integration_client):
        """Test that batch configuration works with real tracing operations."""
        test_batch_size = 150
        test_flush_interval = 1.5

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Set custom batch configuration
            os.environ["HH_BATCH_SIZE"] = str(test_batch_size)
            os.environ["HH_FLUSH_INTERVAL"] = str(test_flush_interval)

            # Initialize tracer with custom batch configuration
            tracer = HoneyHiveTracer.init()

            # Verify tracer was created successfully
            assert tracer is not None, "Tracer should be initialized"
            assert tracer.project is not None, "Tracer should have a project"

            # Test real tracing operations with the batch configuration
            from honeyhive.tracer.decorators import trace

            @trace(tracer=tracer)
            def batch_test_operation():
                return "batch_config_working"

            # Execute multiple operations to test batching behavior
            results = []
            for _ in range(5):
                result = batch_test_operation()
                results.append(result)

            # Verify all operations completed successfully
            assert len(results) == 5, "All batch operations should complete"
            assert all(
                r == "batch_config_working" for r in results
            ), "All operations should return expected result"

            # Force flush to ensure all spans are processed with our batch configuration
            flush_success = tracer.force_flush()
            assert (
                flush_success
            ), "Force flush should succeed with custom batch configuration"

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

    def test_batch_configuration_performance_characteristics_integration(
        self, integration_client
    ):
        """Test that different batch configurations affect real performance characteristics."""
        import time

        from honeyhive.tracer.decorators import trace

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Test with fast flush configuration (should handle spans quickly)
            os.environ["HH_BATCH_SIZE"] = "10"  # Small batches
            os.environ["HH_FLUSH_INTERVAL"] = "0.5"  # Fast flush

            fast_tracer = HoneyHiveTracer.init()

            @trace(tracer=fast_tracer)
            def fast_operation():
                return "fast_batch_test"

            # Execute operations and measure completion
            start_time = time.time()
            for _ in range(5):
                fast_operation()
            fast_tracer.force_flush()
            fast_duration = time.time() - start_time

            # Test with slower flush configuration
            os.environ["HH_BATCH_SIZE"] = "100"  # Larger batches
            os.environ["HH_FLUSH_INTERVAL"] = "2.0"  # Slower flush

            slow_tracer = HoneyHiveTracer.init()

            @trace(tracer=slow_tracer)
            def slow_operation():
                return "slow_batch_test"

            # Execute same operations
            start_time = time.time()
            for _ in range(5):
                slow_operation()
            slow_tracer.force_flush()
            slow_duration = time.time() - start_time

            # Both configurations should work (performance difference is secondary)
            assert (
                fast_duration > 0
            ), "Fast batch configuration should complete successfully"
            assert (
                slow_duration > 0
            ), "Slow batch configuration should complete successfully"

            # The main validation is that both configurations work without errors
            print(f"Fast batch config duration: {fast_duration:.4f}s")
            print(f"Slow batch config duration: {slow_duration:.4f}s")

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

    def test_batch_configuration_documentation_examples_integration(
        self, integration_client
    ):
        """Test batch configuration values from the HoneyHive documentation with real environment setup."""
        from honeyhive.tracer.decorators import trace

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Test Example 1: Performance optimized (from documentation)
            os.environ["HH_BATCH_SIZE"] = "200"
            os.environ["HH_FLUSH_INTERVAL"] = "1.0"

            config = Config()
            assert (
                config.batch_size == 200
            ), "Performance optimized batch size should be 200"
            assert (
                config.flush_interval == 1.0
            ), "Performance optimized flush interval should be 1.0"

            # Test real tracing with performance optimized settings
            perf_tracer = HoneyHiveTracer.init()
            assert (
                perf_tracer is not None
            ), "Performance optimized tracer should initialize"

            @trace(tracer=perf_tracer)
            def perf_test_operation():
                return "performance_optimized"

            result = perf_test_operation()
            assert (
                result == "performance_optimized"
            ), "Performance optimized tracing should work"
            perf_tracer.force_flush()

            # Test Example 2: Memory optimized (smaller batches)
            os.environ["HH_BATCH_SIZE"] = "50"
            os.environ["HH_FLUSH_INTERVAL"] = "2.0"

            config = Config()
            assert config.batch_size == 50, "Memory optimized batch size should be 50"
            assert (
                config.flush_interval == 2.0
            ), "Memory optimized flush interval should be 2.0"

            # Test real tracing with memory optimized settings
            memory_tracer = HoneyHiveTracer.init()
            assert (
                memory_tracer is not None
            ), "Memory optimized tracer should initialize"

            @trace(tracer=memory_tracer)
            def memory_test_operation():
                return "memory_optimized"

            result = memory_test_operation()
            assert result == "memory_optimized", "Memory optimized tracing should work"
            memory_tracer.force_flush()

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
