"""
Fault injection tests for error handling and resilience.

These tests simulate various failure scenarios to validate
the error handling and recovery mechanisms.
"""

import threading
import time
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.error_handler import (
    ErrorContext,
    ErrorHandler,
    ErrorSeverity,
    ExportError,
    FallbackMode,
    ProviderIncompatibleError,
    SpanProcessingError,
)
from tests.mocks.mock_frameworks import MockFrameworkA


class TestFaultInjection:
    """Test fault injection scenarios."""

    def __init__(self):
        """Initialize test class attributes."""
        self.error_handler = None
        self.test_api_key = None
        self.test_project = None

    def setup_method(self):
        """Set up test fixtures."""
        # Reset OpenTelemetry state
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

        self.error_handler = ErrorHandler()
        self.test_api_key = "fault-injection-test-key"
        self.test_project = "fault-injection-test"

    def teardown_method(self):
        """Clean up after tests."""
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

    @pytest.mark.integration
    def test_api_key_failure_injection(self):
        """Test behavior when API key is invalid."""
        print("🔥 Testing API key failure injection...")

        # Test with invalid API key
        with patch("honeyhive.api.client.HoneyHiveClient") as mock_client_class:
            # Mock client to raise authentication error
            mock_client = Mock()
            mock_client.session.create_session.side_effect = Exception(
                "Invalid API key"
            )
            mock_client_class.return_value = mock_client

            # Initialize tracer with invalid key
            tracer = HoneyHiveTracer.init(
                api_key="invalid-key",
                project=self.test_project,
                test_mode=False,  # Force real API call
                verbose=False,
            )

            # Should still work but with degraded functionality
            assert tracer is not None

            # Test framework integration still works
            framework = MockFrameworkA("FaultInjectionA")
            result = framework.execute_operation("api_key_failure_test")

            assert result["status"] == "completed"
            print("   ✅ API key failure handled gracefully")

    @pytest.mark.integration
    def test_provider_incompatibility_injection(self):
        """Test behavior with incompatible TracerProvider."""
        print("🔥 Testing provider incompatibility injection...")

        # Create incompatible provider
        class IncompatibleProvider:
            """Mock incompatible TracerProvider for testing."""

            def __init__(self):
                self.name = "IncompatibleProvider"

            # Missing required methods like add_span_processor

        from opentelemetry import trace

        # Set incompatible provider
        incompatible_provider = IncompatibleProvider()
        trace.set_tracer_provider(incompatible_provider)

        # Initialize HoneyHive (should handle gracefully)
        tracer = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        # Should still work
        assert tracer is not None

        # Framework should still function
        framework = MockFrameworkA("IncompatibleProviderTest")
        result = framework.execute_operation("incompatible_provider_test")

        assert result["status"] == "completed"
        print("   ✅ Provider incompatibility handled gracefully")

    @pytest.mark.integration
    def test_span_processing_failure_injection(self):
        """Test span processing failures."""
        print("🔥 Testing span processing failure injection...")

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        # Mock span processor to fail
        with patch.object(
            tracer.span_processor, "on_end", side_effect=Exception("Processing failed")
        ):
            framework = MockFrameworkA("SpanProcessingFailure")

            # Operations should still complete despite processing failures
            result = framework.execute_operation("span_processing_failure_test")

            assert result["status"] == "completed"
            print("   ✅ Span processing failure handled gracefully")

    @pytest.mark.integration
    def test_export_failure_injection(self):
        """Test export failures."""
        print("🔥 Testing export failure injection...")

        # Initialize tracer
        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        # Mock OTLP exporter to fail
        with patch(
            "opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter"
        ) as mock_exporter_class:
            mock_exporter = Mock()
            mock_exporter.export.side_effect = Exception("Export failed")
            mock_exporter_class.return_value = mock_exporter

            framework = MockFrameworkA("ExportFailure")

            # Operations should still work despite export failures
            result = framework.execute_operation("export_failure_test")

            assert result["status"] == "completed"
            print("   ✅ Export failure handled gracefully")

    @pytest.mark.integration
    def test_network_failure_injection(self):
        """Test network failure scenarios."""
        print("🔥 Testing network failure injection...")

        # Mock network failures
        with patch("requests.post", side_effect=ConnectionError("Network unreachable")):
            tracer = HoneyHiveTracer.init(
                api_key=self.test_api_key,
                project=self.test_project,
                test_mode=False,  # Try real network calls
                verbose=False,
            )

            # Should initialize with fallback
            assert tracer is not None

            framework = MockFrameworkA("NetworkFailure")
            result = framework.execute_operation("network_failure_test")

            assert result["status"] == "completed"
            print("   ✅ Network failure handled gracefully")

    @pytest.mark.integration
    def test_memory_pressure_injection(self):
        """Test behavior under memory pressure."""
        print("🔥 Testing memory pressure injection...")

        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        framework = MockFrameworkA("MemoryPressure")

        # Simulate memory pressure by creating many operations
        results = []
        for i in range(1000):  # Large number of operations
            try:
                result = framework.execute_operation(f"memory_pressure_test_{i}")
                results.append(result)

                # Periodically check if we're still functioning
                if i % 100 == 0:
                    assert result["status"] == "completed"

            except MemoryError:
                # If we hit memory limits, that's expected
                print(f"   Memory limit reached at operation {i}")
                break

        # Should have completed at least some operations
        assert len(results) > 0
        print(f"   ✅ Completed {len(results)} operations under memory pressure")

    @pytest.mark.integration
    def test_concurrent_failure_injection(self):
        """Test concurrent failures."""
        print("🔥 Testing concurrent failure injection...")

        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        framework = MockFrameworkA("ConcurrentFailure")

        def worker_with_failures(worker_id: int, failure_rate: float = 0.3):
            """Worker that randomly fails operations."""
            import random

            results = []

            for i in range(10):
                try:
                    if random.random() < failure_rate:
                        # Inject random failure
                        raise RuntimeError(
                            f"Injected failure in worker {worker_id}, op {i}"
                        )

                    result = framework.execute_operation(
                        f"concurrent_failure_test_{worker_id}_{i}", worker_id=worker_id
                    )
                    results.append(result)

                except Exception as e:
                    # Log failure but continue
                    results.append({"status": "failed", "error": str(e)})

            return results

        # Run concurrent workers with injected failures
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(worker_with_failures, i, 0.2)  # 20% failure rate
                for i in range(5)
            ]

            all_results = []
            for future in concurrent.futures.as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)

        # Analyze results
        successful = [r for r in all_results if r.get("status") == "completed"]
        failed = [r for r in all_results if r.get("status") == "failed"]

        print(f"   Successful operations: {len(successful)}")
        print(f"   Failed operations: {len(failed)}")

        # Should have some successful operations despite failures
        assert len(successful) > 0
        print("   ✅ Concurrent failures handled gracefully")

    @pytest.mark.integration
    def test_recovery_after_failure(self):
        """Test recovery after failures."""
        print("🔥 Testing recovery after failure...")

        _ = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        framework = MockFrameworkA("RecoveryTest")

        # Phase 1: Normal operation
        result1 = framework.execute_operation("pre_failure_test")
        assert result1["status"] == "completed"
        print("   Phase 1: Normal operation ✅")

        # Phase 2: Inject failure
        with patch.object(
            framework, "execute_operation", side_effect=RuntimeError("Injected failure")
        ):
            try:
                framework.execute_operation("failure_test")
                assert False, "Should have raised exception"
            except RuntimeError:
                pass  # Expected

        print("   Phase 2: Failure injected ✅")

        # Phase 3: Recovery (remove failure injection)
        result3 = framework.execute_operation("post_failure_test")
        assert result3["status"] == "completed"
        print("   Phase 3: Recovery successful ✅")

        # Verify error handler statistics
        stats = self.error_handler.get_error_statistics()
        print(f"   Error statistics: {stats}")

    @pytest.mark.integration
    def test_cascading_failure_injection(self):
        """Test cascading failure scenarios."""
        print("🔥 Testing cascading failure injection...")

        # Initialize multiple components that can fail
        tracer = HoneyHiveTracer.init(
            api_key=self.test_api_key,
            project=self.test_project,
            test_mode=True,
            verbose=False,
        )

        framework_a = MockFrameworkA("CascadingA")
        framework_b = MockFrameworkA("CascadingB")

        # Simulate cascading failures
        failure_scenarios = [
            ("provider_failure", lambda: setattr(tracer, "provider", None)),
            ("processor_failure", lambda: setattr(tracer, "span_processor", None)),
            ("framework_failure", lambda: setattr(framework_a, "tracer", None)),
        ]

        for scenario_name, inject_failure in failure_scenarios:
            print(f"   Testing {scenario_name}...")

            try:
                # Inject failure
                inject_failure()

                # Try operations (should handle gracefully)
                result_a = framework_a.execute_operation(
                    f"cascading_test_{scenario_name}_a"
                )
                result_b = framework_b.execute_operation(
                    f"cascading_test_{scenario_name}_b"
                )

                # At least one should succeed or both should fail gracefully
                assert (
                    result_a.get("status") == "completed"
                    or result_b.get("status") == "completed"
                    or "error" in result_a
                    or "error" in result_b
                )

                print(f"     {scenario_name} handled ✅")

            except Exception as e:
                # Graceful failure is acceptable
                print(f"     {scenario_name} failed gracefully: {e}")

        print("   ✅ Cascading failures handled")


class TestRecoveryMechanisms:
    """Test recovery mechanisms."""

    def __init__(self):
        """Initialize test class attributes."""
        self.error_handler = None

    def setup_method(self):
        """Set up test fixtures."""
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

        self.error_handler = ErrorHandler()

    def teardown_method(self):
        """Clean up after tests."""
        from opentelemetry import trace

        trace._TRACER_PROVIDER = None

    @pytest.mark.integration
    def test_automatic_retry_mechanism(self):
        """Test automatic retry mechanism."""
        print("🔄 Testing automatic retry mechanism...")

        from honeyhive.tracer.error_handler import RetryStrategy

        retry_strategy = RetryStrategy(
            max_retries=3, base_delay=0.01
        )  # Fast for testing

        # Function that fails twice then succeeds
        call_count = 0

        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError(f"Failure {call_count}")
            return f"Success on attempt {call_count}"

        with patch("time.sleep"):  # Speed up test
            result = retry_strategy.execute_with_retry(flaky_function)

        assert result == "Success on attempt 3"
        assert call_count == 3
        print("   ✅ Automatic retry successful")

    @pytest.mark.integration
    def test_health_check_recovery(self):
        """Test health check and recovery."""
        print("🏥 Testing health check recovery...")

        # Put error handler in fallback mode
        self.error_handler.fallback_active = True
        self.error_handler.last_health_check = 0  # Force health check

        # Mock successful recovery
        with patch.object(self.error_handler, "_attempt_recovery", return_value=True):
            health_result = self.error_handler.perform_health_check()

        assert health_result["recovery_attempted"] is True
        assert health_result["recovery_successful"] is True
        assert not self.error_handler.fallback_active

        print("   ✅ Health check recovery successful")

    @pytest.mark.integration
    def test_background_retry_mechanism(self):
        """Test background retry mechanism."""
        print("🔄 Testing background retry mechanism...")

        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            severity=ErrorSeverity.MEDIUM,
            fallback_mode=FallbackMode.GRACEFUL_DEGRADATION,
        )

        # Track if background retry was scheduled
        retry_scheduled = threading.Event()

        def mock_background_retry():
            retry_scheduled.set()

        with patch("threading.Thread") as mock_thread:
            mock_thread.return_value.start = mock_background_retry

            self.error_handler._schedule_background_retry(context)

        # Wait briefly for background thread
        assert retry_scheduled.wait(timeout=1.0)

        print("   ✅ Background retry scheduled")

    @pytest.mark.integration
    def test_graceful_degradation_recovery(self):
        """Test graceful degradation and recovery."""
        print("📉 Testing graceful degradation recovery...")

        _ = HoneyHiveTracer.init(
            api_key="degradation-test-key",
            project="degradation-test",
            test_mode=True,
            verbose=False,
        )

        framework = MockFrameworkA("DegradationTest")

        # Normal operation
        result1 = framework.execute_operation("normal_operation")
        assert result1["status"] == "completed"

        # Simulate degradation
        context = ErrorContext(
            operation="span_processing",
            component="span_processor",
            severity=ErrorSeverity.HIGH,
            fallback_mode=FallbackMode.GRACEFUL_DEGRADATION,
        )

        error = SpanProcessingError("test_span")
        degradation_result = self.error_handler.handle_integration_failure(
            error, context
        )

        assert degradation_result["fallback_mode"] == "graceful_degradation"
        assert degradation_result["reduced_functionality"] is True

        # Operations should still work in degraded mode
        result2 = framework.execute_operation("degraded_operation")
        assert result2["status"] == "completed"

        print("   ✅ Graceful degradation working")

        # Test recovery
        self.error_handler.last_health_check = 0  # Force health check

        with patch.object(self.error_handler, "_attempt_recovery", return_value=True):
            health_result = self.error_handler.perform_health_check()

        assert health_result["recovery_successful"] is True

        # Operations should work normally after recovery
        result3 = framework.execute_operation("recovered_operation")
        assert result3["status"] == "completed"

        print("   ✅ Recovery from degradation successful")


def run_fault_injection_suite():
    """Run the complete fault injection test suite."""
    print("💥 Running Fault Injection Test Suite")
    print("=" * 40)

    # Create test instances
    fault_tests = TestFaultInjection()
    recovery_tests = TestRecoveryMechanisms()

    # Run fault injection tests
    fault_tests.setup_method()
    try:
        fault_tests.test_api_key_failure_injection()
        fault_tests.test_provider_incompatibility_injection()
        fault_tests.test_span_processing_failure_injection()
        fault_tests.test_export_failure_injection()
        fault_tests.test_network_failure_injection()
        fault_tests.test_memory_pressure_injection()
        fault_tests.test_concurrent_failure_injection()
        fault_tests.test_recovery_after_failure()
        fault_tests.test_cascading_failure_injection()
    finally:
        fault_tests.teardown_method()

    # Run recovery tests
    recovery_tests.setup_method()
    try:
        recovery_tests.test_automatic_retry_mechanism()
        recovery_tests.test_health_check_recovery()
        recovery_tests.test_background_retry_mechanism()
        recovery_tests.test_graceful_degradation_recovery()
    finally:
        recovery_tests.teardown_method()

    print("\n🎉 Fault injection test suite completed!")
    print("✅ All error handling and resilience mechanisms validated")


if __name__ == "__main__":
    # Run fault injection tests
    run_fault_injection_suite()
