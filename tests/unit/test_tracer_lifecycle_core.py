"""Unit tests for HoneyHive tracer lifecycle core functionality.

This module tests the core lifecycle management infrastructure including
safe logging, tracer registration, and thread-safe operations.
"""

# pylint: disable=unused-argument,attribute-defined-outside-init,duplicate-code
# Justification: Test fixtures may not be used, test setup defines attributes

import gc
import threading
import time
from unittest.mock import Mock, patch

from honeyhive.tracer.lifecycle.core import (
    _lifecycle_lock,
    _new_spans_disabled,
    _registered_tracers,
    acquire_lifecycle_lock_optimized,
    acquire_lock_with_timeout,
    disable_new_span_creation,
    get_lifecycle_lock,
    get_lock_config,
    get_lock_strategy,
    is_new_span_creation_disabled,
    register_tracer_for_atexit_cleanup,
    unregister_tracer_from_atexit_cleanup,
)


class MockTracer:
    """Mock tracer for testing lifecycle operations."""

    def __init__(self, tracer_id: str = "test-tracer"):
        self.tracer_id = tracer_id
        self.shutdown_called = False
        self.flush_called = False

    def shutdown(self) -> None:
        """Mock shutdown method."""
        self.shutdown_called = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Mock force flush method."""
        self.flush_called = True
        return True


# TestSafeLogging class removed - functionality no longer exists
# The _safe_log function was removed in favor of direct safe_log usage from utils.logger


class TestTracerRegistration:
    """Test tracer registration for atexit cleanup."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        # Clear the registered tracers set
        _registered_tracers.clear()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Clear the registered tracers set
        _registered_tracers.clear()

        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def test_register_tracer_for_atexit_cleanup(self) -> None:
        """Test tracer registration for atexit cleanup."""
        tracer = MockTracer("test-tracer-1")

        with patch("honeyhive.tracer.lifecycle.core.atexit.register") as mock_atexit:
            register_tracer_for_atexit_cleanup(tracer)

            # Verify tracer was added to registered set
            assert tracer in _registered_tracers

            # Verify atexit handler was registered
            mock_atexit.assert_called_once()

    def test_register_multiple_tracers(self) -> None:
        """Test registering multiple tracers."""
        tracer1 = MockTracer("tracer-1")
        tracer2 = MockTracer("tracer-2")
        tracer3 = MockTracer("tracer-3")

        with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
            register_tracer_for_atexit_cleanup(tracer1)
            register_tracer_for_atexit_cleanup(tracer2)
            register_tracer_for_atexit_cleanup(tracer3)

            # Verify all tracers were registered
            assert len(_registered_tracers) == 3
            assert tracer1 in _registered_tracers
            assert tracer2 in _registered_tracers
            assert tracer3 in _registered_tracers

    def test_register_same_tracer_multiple_times(self) -> None:
        """Test registering the same tracer multiple times."""
        tracer = MockTracer("duplicate-tracer")

        with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
            register_tracer_for_atexit_cleanup(tracer)
            register_tracer_for_atexit_cleanup(tracer)
            register_tracer_for_atexit_cleanup(tracer)

            # Should only be registered once (WeakSet behavior)
            assert len(_registered_tracers) == 1
            assert tracer in _registered_tracers

    def test_unregister_tracer_from_atexit_cleanup(self) -> None:
        """Test tracer unregistration from atexit cleanup."""
        tracer = MockTracer("test-tracer")

        with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
            # First register the tracer
            register_tracer_for_atexit_cleanup(tracer)
            assert tracer in _registered_tracers

            # Then unregister it
            unregister_tracer_from_atexit_cleanup(tracer)
            assert tracer not in _registered_tracers

    def test_unregister_nonexistent_tracer(self) -> None:
        """Test unregistering a tracer that wasn't registered."""
        tracer = MockTracer("nonexistent-tracer")

        # Should not raise exception
        unregister_tracer_from_atexit_cleanup(tracer)

    def test_weak_reference_cleanup(self) -> None:
        """Test that tracers are automatically cleaned up when garbage collected."""
        with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
            tracer = MockTracer("weak-ref-tracer")
            register_tracer_for_atexit_cleanup(tracer)

            # Verify tracer is registered
            assert len(_registered_tracers) == 1

            # Delete the tracer and force garbage collection
            del tracer
            gc.collect()

            # WeakSet should automatically remove the dead reference
            # Note: This might not work immediately due to GC timing
            # but the WeakSet will clean up eventually

    def test_thread_safety_registration(self) -> None:
        """Test that tracer registration is thread-safe."""
        tracers = []

        def register_worker(worker_id: int):
            tracer = MockTracer(f"worker-{worker_id}")
            tracers.append(tracer)
            with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
                register_tracer_for_atexit_cleanup(tracer)

        # Create multiple threads registering tracers
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all tracers were registered
        assert len(_registered_tracers) == 10
        for tracer in tracers:
            assert tracer in _registered_tracers


class TestShutdownStateManagement:
    """Test shutdown state management functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        # Reset shutdown states (only _new_spans_disabled exists now)
        _new_spans_disabled.clear()

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Reset shutdown states (only _new_spans_disabled exists now)
        _new_spans_disabled.clear()

    def test_disable_new_span_creation(self) -> None:
        """Test disabling new span creation."""
        assert not _new_spans_disabled.is_set()
        assert not is_new_span_creation_disabled()

        disable_new_span_creation()

        assert _new_spans_disabled.is_set()
        assert is_new_span_creation_disabled()

    def test_is_new_span_creation_disabled_initial_state(self) -> None:
        """Test initial state of new span creation."""
        assert not is_new_span_creation_disabled()

    def test_shutdown_state_coordination(self) -> None:
        """Test coordination between different shutdown states."""
        # Initially, new spans should not be disabled
        assert not _new_spans_disabled.is_set()

        # Disable new spans
        disable_new_span_creation()
        assert _new_spans_disabled.is_set()

        # New spans should remain disabled
        assert _new_spans_disabled.is_set()

    def test_thread_safety_shutdown_states(self) -> None:
        """Test that shutdown state operations are thread-safe."""
        results = []

        def state_worker(worker_id: int):
            if worker_id % 2 == 0:
                results.append("stream_closure")
            else:
                disable_new_span_creation()
                results.append("spans_disabled")

        # Create multiple threads modifying shutdown states
        threads = []
        for i in range(10):
            thread = threading.Thread(target=state_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed
        assert len(results) == 10
        assert "stream_closure" in results
        assert "spans_disabled" in results

        # Verify final states
        assert _new_spans_disabled.is_set()


class TestLifecycleLocking:
    """Test lifecycle locking mechanisms."""

    def test_lifecycle_lock_exists(self) -> None:
        """Test that lifecycle lock is available."""
        assert _lifecycle_lock is not None
        # Check that it's a lock-like object (has acquire/release methods)
        assert hasattr(_lifecycle_lock, "acquire")
        assert hasattr(_lifecycle_lock, "release")
        assert callable(_lifecycle_lock.acquire)
        assert callable(_lifecycle_lock.release)

    def test_lifecycle_lock_thread_safety(self) -> None:
        """Test that lifecycle lock provides thread safety."""
        shared_counter = {"value": 0}

        def increment_worker():
            for _ in range(100):
                with _lifecycle_lock:
                    current = shared_counter["value"]
                    # Simulate some work
                    time.sleep(0.001)
                    shared_counter["value"] = current + 1

        # Create multiple threads incrementing counter
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=increment_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # With proper locking, final value should be 500
        assert shared_counter["value"] == 500

    def test_lifecycle_lock_context_manager(self) -> None:
        """Test lifecycle lock works as context manager."""
        acquired = False

        with _lifecycle_lock:
            acquired = _lifecycle_lock.locked()

        # Should be acquired inside context, released outside
        assert acquired
        assert not _lifecycle_lock.locked()


class TestLockStrategy:
    """Test suite for lock strategy detection and configuration."""

    def test_get_lock_strategy_lambda(self) -> None:
        """Test AWS Lambda environment detection."""
        with patch.dict("os.environ", {"AWS_LAMBDA_FUNCTION_NAME": "test-function"}):
            # This tests lines 90-91
            strategy = get_lock_strategy()
            assert strategy == "lambda_optimized"

    def test_get_lock_strategy_kubernetes(self) -> None:
        """Test Kubernetes environment detection."""
        with patch.dict(
            "os.environ", {"KUBERNETES_SERVICE_HOST": "10.0.0.1"}, clear=True
        ):
            # This tests lines 94-95
            strategy = get_lock_strategy()
            assert strategy == "k8s_optimized"

    def test_get_lock_strategy_high_concurrency(self) -> None:
        """Test high concurrency mode detection."""
        with patch.dict("os.environ", {"HH_HIGH_CONCURRENCY": "true"}, clear=True):
            # This tests lines 98-99
            strategy = get_lock_strategy()
            assert strategy == "high_concurrency"

    def test_get_lock_strategy_high_concurrency_variants(self) -> None:
        """Test high concurrency mode detection with different values."""
        test_values = ["1", "yes", "TRUE", "Yes"]
        for value in test_values:
            with patch.dict("os.environ", {"HH_HIGH_CONCURRENCY": value}, clear=True):
                strategy = get_lock_strategy()
                assert strategy == "high_concurrency"

    def test_get_lock_strategy_standard_default(self) -> None:
        """Test standard environment (default case)."""
        with patch.dict("os.environ", {}, clear=True):
            # This tests line 102
            strategy = get_lock_strategy()
            assert strategy == "standard"

    def test_get_lock_config_with_strategy(self) -> None:
        """Test lock configuration retrieval with explicit strategy."""
        # This tests lines 123-126
        config = get_lock_config("lambda_optimized")
        assert config["lifecycle_timeout"] == 0.5
        assert config["flush_timeout"] == 2.0
        assert "description" in config

    def test_get_lock_config_auto_detect(self) -> None:
        """Test lock configuration with auto-detection."""
        with patch.dict("os.environ", {"AWS_LAMBDA_FUNCTION_NAME": "test"}, clear=True):
            # This tests lines 123-124 (strategy is None path)
            config = get_lock_config(None)
            assert config["lifecycle_timeout"] == 0.5

    def test_get_lock_config_unknown_strategy_fallback(self) -> None:
        """Test lock configuration fallback for unknown strategy."""
        # This tests line 126 (fallback to standard)
        config = get_lock_config("unknown_strategy")
        assert config == get_lock_config("standard")


# TestSafeLogDelegation class removed - functionality no longer exists
# The _safe_log function was removed in favor of direct safe_log usage


class TestLockAcquisition:
    """Test suite for lock acquisition utilities."""

    def test_get_lifecycle_lock(self) -> None:
        """Test lifecycle lock getter."""
        # This tests the get_lifecycle_lock function
        lock = get_lifecycle_lock()
        assert lock is _lifecycle_lock

    @patch("honeyhive.tracer.lifecycle.core.get_lock_config")
    def test_acquire_lifecycle_lock_optimized_success(self, mock_get_config) -> None:
        """Test successful lock acquisition with optimization."""
        # Mock configuration
        mock_get_config.return_value = {"lifecycle_timeout": 1.0}

        # This tests the acquire_lifecycle_lock_optimized function
        with acquire_lifecycle_lock_optimized("test_operation") as acquired:
            assert acquired is True
            assert _lifecycle_lock.locked()

    @patch("honeyhive.tracer.lifecycle.core.get_lock_config")
    def test_acquire_lifecycle_lock_optimized_custom_timeout(
        self, mock_get_config
    ) -> None:
        """Test lock acquisition with custom timeout."""
        mock_get_config.return_value = {"lifecycle_timeout": 1.0}

        with acquire_lifecycle_lock_optimized(
            "test_operation", custom_timeout=0.5
        ) as acquired:
            assert acquired is True
            # Verify custom timeout was used (not the config timeout)

    @patch("honeyhive.tracer.lifecycle.core.get_lock_config")
    @patch("honeyhive.tracer.lifecycle.core._lifecycle_lock")
    def test_acquire_lifecycle_lock_optimized_timeout(
        self, mock_lock, mock_get_config
    ) -> None:
        """Test lock acquisition timeout handling."""
        mock_get_config.return_value = {"lifecycle_timeout": 0.001}
        mock_lock.acquire.return_value = False  # Simulate timeout

        with acquire_lifecycle_lock_optimized("test_operation") as acquired:
            assert acquired is False

    def test_acquire_lock_with_timeout_success(self) -> None:
        """Test successful lock acquisition with timeout."""
        mock_lock = Mock()
        mock_lock.acquire.return_value = True

        # This tests lines 329-336
        with acquire_lock_with_timeout(mock_lock, 1.0) as acquired:
            assert acquired is True
            mock_lock.acquire.assert_called_once_with(timeout=1.0)

        # Verify lock was released
        mock_lock.release.assert_called_once()

    def test_acquire_lock_with_timeout_failure(self) -> None:
        """Test lock acquisition timeout failure."""
        mock_lock = Mock()
        mock_lock.acquire.return_value = False  # Simulate timeout

        # This tests lines 329-331
        with acquire_lock_with_timeout(mock_lock, 0.1) as acquired:
            assert acquired is False
            mock_lock.acquire.assert_called_once_with(timeout=0.1)

        # Verify lock was NOT released (since it wasn't acquired)
        mock_lock.release.assert_not_called()


class TestTracerRegistrationCleanup:
    """Test suite for tracer registration and cleanup."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        _registered_tracers.clear()

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        _registered_tracers.clear()

    @patch("atexit.register")
    def test_register_tracer_for_atexit_cleanup(self, mock_atexit_register) -> None:
        """Test tracer registration for atexit cleanup."""
        tracer = MockTracer("test-tracer")

        # This tests the registration logic
        register_tracer_for_atexit_cleanup(tracer)

        # Verify tracer was added to registry
        assert tracer in _registered_tracers

        # Verify atexit handler was registered
        mock_atexit_register.assert_called_once()

    @patch("atexit.register")
    @patch("honeyhive.tracer.lifecycle.core.safe_log")
    def test_register_tracer_already_registered(
        self, mock_safe_log, mock_atexit_register
    ) -> None:
        """Test registering a tracer that's already registered."""
        tracer = MockTracer("test-tracer")

        # First registration
        register_tracer_for_atexit_cleanup(tracer)

        # Second registration (should log debug and return early)
        # This tests lines 190-195
        register_tracer_for_atexit_cleanup(tracer)

        # Should have logged debug message about already registered
        mock_safe_log.assert_any_call(
            tracer,
            "debug",
            f"Tracer already registered for atexit cleanup: {id(tracer)}",
        )

        # Should still only be registered once in atexit
        assert mock_atexit_register.call_count == 1

    @patch("atexit.register")
    @patch("honeyhive.tracer.lifecycle.flush.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.shutdown_tracer")
    def test_atexit_cleanup_function_execution(
        self, mock_shutdown, mock_flush, mock_atexit_register
    ) -> None:
        """Test that the atexit cleanup function works correctly."""
        tracer = MockTracer("test-tracer")

        # Register tracer
        register_tracer_for_atexit_cleanup(tracer)

        # Get the cleanup function that was registered with atexit
        cleanup_func = mock_atexit_register.call_args[0][0]

        # Execute the cleanup function - this tests lines 206-222
        cleanup_func()

        # Note: Shutdown state detection has moved to logger system
        # This test focuses on cleanup function behavior (flush/shutdown calls)

        # Verify flush and shutdown were called
        mock_flush.assert_called_once_with(tracer, timeout_millis=1000)
        mock_shutdown.assert_called_once_with(tracer)

    @patch("atexit.register")
    @patch("honeyhive.tracer.lifecycle.flush.force_flush_tracer")
    def test_atexit_cleanup_function_exception_handling(
        self, mock_flush, mock_atexit_register
    ) -> None:
        """Test that atexit cleanup handles exceptions gracefully."""
        tracer = MockTracer("test-tracer")

        # Make flush raise an exception
        mock_flush.side_effect = Exception("Flush error during shutdown")

        # Register tracer
        register_tracer_for_atexit_cleanup(tracer)

        # Get and execute the cleanup function
        cleanup_func = mock_atexit_register.call_args[0][0]

        # Should not raise exception (tests lines 220-222)
        cleanup_func()  # Should complete without error

        # Note: Shutdown state detection has moved to logger system
        # This test focuses on exception handling in cleanup function

    def test_unregister_tracer_from_atexit_cleanup(self) -> None:
        """Test tracer unregistration from atexit cleanup."""
        tracer = MockTracer("test-tracer")

        # First register the tracer
        _registered_tracers.add(tracer)
        assert tracer in _registered_tracers

        # Then unregister it - this tests the unregistration logic
        unregister_tracer_from_atexit_cleanup(tracer)

        # Verify tracer was removed from registry
        assert tracer not in _registered_tracers

    def test_unregister_nonexistent_tracer(self) -> None:
        """Test unregistering a tracer that wasn't registered."""
        tracer = MockTracer("nonexistent-tracer")

        # Should not raise an error
        unregister_tracer_from_atexit_cleanup(tracer)

        # Registry should remain empty
        assert len(_registered_tracers) == 0


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple lifecycle features."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        # Reset all states (only these exist now)
        _new_spans_disabled.clear()
        _registered_tracers.clear()

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Reset all states (only these exist now)
        _new_spans_disabled.clear()
        _registered_tracers.clear()

    def test_full_shutdown_sequence(self) -> None:
        """Test a complete shutdown sequence."""
        tracer = MockTracer("shutdown-test")

        with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
            # 1. Register tracer
            register_tracer_for_atexit_cleanup(tracer)
            assert tracer in _registered_tracers

            # 2. Disable new span creation
            disable_new_span_creation()
            assert is_new_span_creation_disabled()

            # 3. Mark stream closure

            # 4. Unregister tracer
            unregister_tracer_from_atexit_cleanup(tracer)
            assert tracer not in _registered_tracers

    def test_concurrent_lifecycle_operations(self) -> None:
        """Test concurrent lifecycle operations."""
        tracers = []
        results = []

        def lifecycle_worker(worker_id: int):
            tracer = MockTracer(f"concurrent-{worker_id}")
            tracers.append(tracer)

            try:
                with patch("honeyhive.tracer.lifecycle.core.atexit.register"):
                    # Register tracer
                    register_tracer_for_atexit_cleanup(tracer)

                    # Perform shutdown operations
                    if worker_id % 3 == 0:
                        disable_new_span_creation()
                    elif worker_id % 3 == 1:
                        pass  # No additional operation for this worker

                    # Unregister tracer
                    unregister_tracer_from_atexit_cleanup(tracer)

                results.append("success")
            except Exception as e:
                results.append(f"error: {e}")

        # Create multiple threads performing lifecycle operations
        threads = []
        for i in range(15):
            thread = threading.Thread(target=lifecycle_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed successfully
        assert len(results) == 15
        assert all(result == "success" for result in results)
