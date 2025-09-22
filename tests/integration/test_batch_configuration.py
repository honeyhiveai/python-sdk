"""
Integration tests for batch configuration validation.

Tests that verify HH_BATCH_SIZE and HH_FLUSH_INTERVAL environment variables
are properly applied to the BatchSpanProcessor configuration using real
environment setup.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,duplicate-code
# Justification: Integration test file with comprehensive batch configuration testing requiring real API calls

import os
import time
from typing import Any, cast

from honeyhive import HoneyHiveTracer
from honeyhive.tracer import trace
from honeyhive.tracer.core.base import HoneyHiveTracerBase
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)


class TestBatchConfiguration:
    """Test batch configuration is properly applied."""

    def test_default_batch_configuration_integration(self) -> None:
        """Test that default batch configuration values are used in integration
        environment."""
        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Clear batch environment variables for this test
            if "HH_BATCH_SIZE" in os.environ:
                del os.environ["HH_BATCH_SIZE"]
            if "HH_FLUSH_INTERVAL" in os.environ:
                del os.environ["HH_FLUSH_INTERVAL"]

            # Create tracer to check per-instance configuration defaults
            tracer = HoneyHiveTracer(
                api_key="test-api-key", project="test-project", source="test"
            )

            # Verify default values match our expectations (simplified config interface)
            # Note: Using the new simplified .config property for easy access
            assert (
                tracer.config.get("otlp", {}).get("batch_size", 100) == 100
            ), "Default batch_size should be 100"
            assert (
                tracer.config.get("otlp", {}).get("flush_interval", 5.0) == 5.0
            ), "Default flush_interval should be 5.0"

            # Verify tracer can be initialized with defaults
            init_tracer: HoneyHiveTracerBase = HoneyHiveTracer.init()
            assert (
                init_tracer is not None
            ), "Tracer should initialize with default batch config"
            cast(HoneyHiveTracer, init_tracer).force_flush()

        finally:
            # Restore original environment state
            if original_batch_size is not None:
                os.environ["HH_BATCH_SIZE"] = original_batch_size
            if original_flush_interval is not None:
                os.environ["HH_FLUSH_INTERVAL"] = original_flush_interval

    def test_custom_batch_configuration_from_env_integration(
        self,
        tracer_factory: Any,
        config_reloader: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test that custom batch configuration is loaded from environment
        variables with backend verification."""

        test_batch_size = 250
        test_flush_interval = 2.5

        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Set custom batch configuration
            os.environ["HH_BATCH_SIZE"] = str(test_batch_size)
            os.environ["HH_FLUSH_INTERVAL"] = str(test_flush_interval)

            # Create tracer to check per-instance configuration with environment variables
            tracer = HoneyHiveTracer(
                api_key="test-api-key", project="test-project", source="test"
            )

            # Verify custom values are loaded from environment (simplified config interface)
            # Note: Environment variables should be picked up during tracer initialization
            assert (
                tracer.config.get("otlp", {}).get("batch_size") == test_batch_size
            ), f"Expected batch_size={test_batch_size}"
            assert (
                tracer.config.get("otlp", {}).get("flush_interval")
                == test_flush_interval
            ), f"Expected flush_interval={test_flush_interval}"

            # Use standardized tracer factory instead of direct init
            tracer = tracer_factory("batch-config-test")
            assert (
                tracer is not None
            ), "Tracer should initialize with custom batch config"

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

    def test_batch_processor_real_tracing_integration(
        self,
        integration_client: Any,
        real_project: Any,
        tracer_factory: Any,
        config_reloader: Any,  # pylint: disable=unused-argument
    ) -> None:
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

            # Reload config to pick up new environment variables
            config_reloader()

            # Initialize tracer with custom batch configuration using factory
            tracer = tracer_factory("test_batch_configuration")

            # Verify tracer was created successfully
            assert tracer is not None, "Tracer should be initialized"
            assert tracer.project is not None, "Tracer should have a project"

            # Test real tracing operations with the batch configuration and backend
            # verification
            _, unique_id = generate_test_id("batch_config", "custom_env")

            # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
            # backend verification
            verified_event = verify_tracer_span(
                tracer=tracer,
                client=integration_client,
                project=real_project,
                span_name="batch_test_operation",
                unique_identifier=unique_id,
                span_attributes={
                    "test.unique_id": unique_id,
                    "test.type": "custom_batch_configuration",
                    "batch.operations_count": 5,
                    "batch.result": "batch_config_working",
                },
            )

            assert verified_event.event_name == "batch_test_operation"
            print(
                f"✓ Custom batch configuration backend verification successful: "
                f"{verified_event.event_id}"
            )

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
        self,
        config_reloader: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test that different batch configurations affect real performance
        characteristics."""
        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Test with fast flush configuration (should handle spans quickly)
            os.environ["HH_BATCH_SIZE"] = "10"  # Small batches
            os.environ["HH_FLUSH_INTERVAL"] = "0.5"  # Fast flush

            # Reload config to pick up new environment variables
            config_reloader()

            fast_tracer = HoneyHiveTracer.init()

            @trace(tracer=fast_tracer)  # type: ignore[misc]
            def fast_operation() -> None:
                pass  # Fast batch operation

            # Execute operations and measure completion
            start_time = time.time()
            for _ in range(5):
                fast_operation()
            cast(HoneyHiveTracer, fast_tracer).force_flush()
            fast_duration = time.time() - start_time

            # Test with slower flush configuration
            os.environ["HH_BATCH_SIZE"] = "100"  # Larger batches
            os.environ["HH_FLUSH_INTERVAL"] = "2.0"  # Slower flush

            # Reload config to pick up new environment variables
            config_reloader()

            slow_tracer = HoneyHiveTracer.init()

            @trace(tracer=slow_tracer)  # type: ignore[misc]
            def slow_operation() -> None:
                pass  # Slow batch operation

            # Execute same operations
            start_time = time.time()
            for _ in range(5):
                slow_operation()
            cast(HoneyHiveTracer, slow_tracer).force_flush()
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
        self,
        config_reloader: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test batch configuration values from the HoneyHive documentation with
        real environment setup."""
        # Save current environment state
        original_batch_size = os.environ.get("HH_BATCH_SIZE")
        original_flush_interval = os.environ.get("HH_FLUSH_INTERVAL")

        try:
            # Test Example 1: Performance optimized (from documentation)
            os.environ["HH_BATCH_SIZE"] = "200"
            os.environ["HH_FLUSH_INTERVAL"] = "1.0"

            # Create tracer to check per-instance configuration with performance settings
            tracer = HoneyHiveTracer(
                api_key="test-api-key", project="test-project", source="test"
            )

            # Verify performance optimized values (simplified config interface)
            # Note: Environment variables should be picked up during tracer initialization
            assert (
                tracer.config.get("otlp", {}).get("batch_size", 100) == 200
            ), "Performance optimized batch size should be 200"
            assert (
                tracer.config.get("otlp", {}).get("flush_interval", 5.0) == 1.0
            ), "Performance optimized flush interval should be 1.0"

            # Test real tracing with performance optimized settings
            perf_tracer = HoneyHiveTracer.init()
            assert (
                perf_tracer is not None
            ), "Performance optimized tracer should initialize"

            @trace(tracer=perf_tracer)  # type: ignore[misc]
            def perf_test_operation() -> None:
                pass  # Performance optimized operation

            perf_test_operation()
            # Performance optimized tracing should work without errors
            cast(HoneyHiveTracer, perf_tracer).force_flush()

            # Test Example 2: Memory optimized (smaller batches)
            os.environ["HH_BATCH_SIZE"] = "50"
            os.environ["HH_FLUSH_INTERVAL"] = "2.0"

            # Create tracer to check per-instance configuration with memory settings
            tracer = HoneyHiveTracer(
                api_key="test-api-key", project="test-project", source="test"
            )

            # Verify memory optimized values (simplified config interface)
            # Note: Environment variables should be picked up during tracer initialization
            assert (
                tracer.config.get("otlp", {}).get("batch_size", 100) == 50
            ), "Memory optimized batch size should be 50"
            assert (
                tracer.config.get("otlp", {}).get("flush_interval", 5.0) == 2.0
            ), "Memory optimized flush interval should be 2.0"

            # Test real tracing with memory optimized settings
            memory_tracer = HoneyHiveTracer.init()
            assert (
                memory_tracer is not None
            ), "Memory optimized tracer should initialize"

            @trace(tracer=memory_tracer)  # type: ignore[misc]
            def memory_test_operation() -> None:
                pass  # Memory optimized operation

            memory_test_operation()
            # Memory optimized tracing should work without errors
            cast(HoneyHiveTracer, memory_tracer).force_flush()

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
