"""Unit tests for tracer lifecycle shutdown functionality.

This module tests the shutdown and cleanup operations for tracer lifecycle management,
including graceful shutdown, provider cleanup, resource management, timeout protection,
and graceful degradation patterns.

Test Coverage:
- shutdown_tracer() with all branches and error conditions
- graceful_shutdown_all() with multiple tracers and failures
- wait_for_pending_spans() with timeout and completion scenarios
- Private helper functions for comprehensive coverage
- Lock acquisition timeout and graceful degradation
- Provider shutdown with timeout protection
- Registry cleanup and state management
- Error handling and logging verification

Following Agent OS testing standards with proper fixtures and isolation.
Generated using enhanced comprehensive analysis framework for 90%+ coverage.
"""

# pylint: disable=too-many-lines,line-too-long,redefined-outer-name,protected-access
# pylint: disable=too-few-public-methods,R0917
# Reason: Comprehensive testing file requires extensive test coverage for 90%+ target
# Line length disabled for test readability and comprehensive assertions
# Redefined outer name disabled for pytest fixture usage pattern
# Protected access needed for testing internal tracer state
# Too few public methods acceptable for test helper classes

from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.lifecycle.shutdown import (
    _check_processor_pending_spans,
    _cleanup_secondary_provider,
    _cleanup_tracer_state,
    _has_pending_spans,
    _shutdown_main_provider,
    _shutdown_without_lock,
    graceful_shutdown_all,
    shutdown_tracer,
    wait_for_pending_spans,
)


class TestShutdownTracer:
    """Test cases for shutdown_tracer function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock tracer instance for testing."""
        tracer = Mock()
        tracer.test_mode = False
        tracer.is_main_provider = True
        tracer.provider = Mock()
        tracer.provider.shutdown = Mock()
        tracer._instance_shutdown = False
        tracer._tracer_id = "test-tracer-123"
        tracer._initialized = True
        tracer.tracer = Mock()
        tracer.span_processor = Mock()
        tracer.propagator = Mock()
        return tracer

    @pytest.fixture
    def mock_secondary_tracer(self) -> Mock:
        """Create a mock secondary tracer instance for testing."""
        tracer = Mock()
        tracer.test_mode = False
        tracer.is_main_provider = False
        tracer.provider = Mock()
        tracer.provider.shutdown = Mock()
        tracer._instance_shutdown = False
        tracer._tracer_id = "test-tracer-456"
        tracer._initialized = True
        tracer.tracer = Mock()
        tracer.span_processor = Mock()
        tracer.propagator = Mock()
        return tracer

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.disable_new_span_creation")
    @patch("honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized")
    @patch("honeyhive.tracer.lifecycle.shutdown._shutdown_main_provider")
    @patch("honeyhive.tracer.lifecycle.shutdown._cleanup_tracer_state")
    def test_shutdown_tracer_success_main_provider(
        self,
        mock_cleanup_state: Mock,
        mock_shutdown_main: Mock,
        mock_acquire_lock: Mock,
        mock_disable_spans: Mock,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful shutdown of main provider tracer."""
        # Setup
        mock_force_flush.return_value = True
        mock_acquire_lock.return_value.__enter__.return_value = True
        mock_acquire_lock.return_value.__exit__.return_value = None

        # Execute
        shutdown_tracer(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer, "debug", "shutdown_tracer: Starting data loss prevention phase"
        )
        mock_disable_spans.assert_called_once()
        assert mock_tracer._instance_shutdown is True
        mock_force_flush.assert_called_once_with(mock_tracer, timeout_millis=5000)
        mock_acquire_lock.assert_called_once_with("lifecycle")
        mock_shutdown_main.assert_called_once_with(mock_tracer)
        mock_cleanup_state.assert_called_once_with(mock_tracer)

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized")
    @patch("honeyhive.tracer.lifecycle.shutdown._cleanup_secondary_provider")
    @patch("honeyhive.tracer.lifecycle.shutdown._cleanup_tracer_state")
    def test_shutdown_tracer_success_secondary_provider(
        self,
        mock_cleanup_state: Mock,
        mock_cleanup_secondary: Mock,
        mock_acquire_lock: Mock,
        mock_force_flush: Mock,
        _mock_safe_log: Mock,
        mock_secondary_tracer: Mock,
    ) -> None:
        """Test successful shutdown of secondary provider tracer."""
        # Setup
        mock_force_flush.return_value = True
        mock_acquire_lock.return_value.__enter__.return_value = True
        mock_acquire_lock.return_value.__exit__.return_value = None

        # Execute
        shutdown_tracer(mock_secondary_tracer)

        # Verify
        mock_cleanup_secondary.assert_called_once_with(mock_secondary_tracer)
        mock_cleanup_state.assert_called_once_with(mock_secondary_tracer)

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    def test_shutdown_tracer_test_mode_skips_flush(
        self,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test that test mode skips pre-lock flush to prevent conflicts."""
        # Setup
        mock_tracer.test_mode = True

        with patch(
            "honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized"
        ) as mock_lock:
            mock_lock.return_value.__enter__.return_value = True
            mock_lock.return_value.__exit__.return_value = None

            # Execute
            shutdown_tracer(mock_tracer)

            # Verify
            mock_safe_log.assert_any_call(
                mock_tracer,
                "debug",
                "Skipping pre-lock flush in test mode to prevent conflicts",
            )
            mock_force_flush.assert_not_called()

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized")
    def test_shutdown_tracer_flush_retry_success(
        self,
        mock_acquire_lock: Mock,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful flush on retry after initial failure."""
        # Setup
        mock_force_flush.side_effect = [False, True]  # Fail first, succeed on retry
        mock_acquire_lock.return_value.__enter__.return_value = True
        mock_acquire_lock.return_value.__exit__.return_value = None

        # Execute
        shutdown_tracer(mock_tracer)

        # Verify
        assert mock_force_flush.call_count == 2
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Pre-lock flush failed (timeout: 5000ms), retrying",
        )
        mock_safe_log.assert_any_call(
            mock_tracer,
            "info",
            "Pre-lock flush succeeded on retry (10000ms)",
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized")
    def test_shutdown_tracer_flush_retry_failure(
        self,
        mock_acquire_lock: Mock,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test flush failure on both initial attempt and retry."""
        # Setup
        mock_force_flush.return_value = False
        mock_acquire_lock.return_value.__enter__.return_value = True
        mock_acquire_lock.return_value.__exit__.return_value = None

        # Execute
        shutdown_tracer(mock_tracer)

        # Verify
        assert mock_force_flush.call_count == 2
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Pre-lock flush failed after retry (10000ms), continuing with shutdown - potential data loss",
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized")
    @patch("honeyhive.tracer.lifecycle.shutdown.get_lock_config")
    @patch("honeyhive.tracer.lifecycle.shutdown._shutdown_without_lock")
    def test_shutdown_tracer_lock_timeout(
        self,
        mock_shutdown_without_lock: Mock,
        mock_get_lock_config: Mock,
        mock_acquire_lock: Mock,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test graceful degradation when lock acquisition times out."""
        # Setup
        mock_force_flush.return_value = True
        mock_acquire_lock.return_value.__enter__.return_value = False
        mock_acquire_lock.return_value.__exit__.return_value = None
        mock_get_lock_config.return_value = {
            "lifecycle_timeout": 2.0,
            "description": "test config",
        }

        # Execute
        shutdown_tracer(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Failed to acquire _lifecycle_lock within 2.0s, proceeding without lock",
            honeyhive_data={
                "lock_timeout": 2.0,
                "lock_strategy": "test config",
                "degradation_reason": "lock_acquisition_timeout",
                "data_flush_completed": True,
            },
        )
        mock_shutdown_without_lock.assert_called_once_with(mock_tracer)

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    def test_shutdown_tracer_exception_handling(
        self,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test exception handling during shutdown process."""
        # Setup - Remove provider to cause AttributeError in shutdown logic
        mock_tracer.provider = None

        with patch(
            "honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized"
        ) as mock_lock:
            mock_lock.return_value.__enter__.return_value = True
            mock_lock.return_value.__exit__.return_value = None

            # Execute - this should not crash despite the error
            shutdown_tracer(mock_tracer)

            # Verify - function completed without crashing
            assert mock_safe_log.called  # Some logging should have occurred

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    def test_shutdown_tracer_no_provider(
        self,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test shutdown when tracer has no provider."""
        # Setup
        mock_tracer.provider = None

        with patch(
            "honeyhive.tracer.lifecycle.shutdown.acquire_lifecycle_lock_optimized"
        ) as mock_lock:
            mock_lock.return_value.__enter__.return_value = True
            mock_lock.return_value.__exit__.return_value = None

            # Execute
            shutdown_tracer(mock_tracer)

            # Verify - should not crash and should clean up state
            mock_safe_log.assert_any_call(
                mock_tracer,
                "debug",
                "Starting tracer shutdown",
                honeyhive_data={
                    "is_main_provider": True,
                    "has_provider": False,
                },
            )


class TestShutdownWithoutLock:
    """Test cases for _shutdown_without_lock function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock tracer instance for testing."""
        tracer = Mock()
        tracer.test_mode = False
        tracer.is_main_provider = True
        tracer.provider = Mock()
        tracer.provider.shutdown = Mock()
        tracer._instance_shutdown = False
        return tracer

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    @patch("honeyhive.tracer.lifecycle.shutdown.disable_new_span_creation")
    @patch("honeyhive.tracer.lifecycle.shutdown._shutdown_main_provider")
    @patch("honeyhive.tracer.lifecycle.shutdown._cleanup_tracer_state")
    def test_shutdown_without_lock_success(
        self,
        mock_cleanup_state: Mock,
        mock_shutdown_main: Mock,
        mock_disable_spans: Mock,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful shutdown without lock."""
        # Setup
        mock_force_flush.return_value = True

        # Execute
        _shutdown_without_lock(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Starting tracer shutdown WITHOUT LOCK (graceful degradation)",
            honeyhive_data={
                "is_main_provider": True,
                "has_provider": True,
            },
        )
        mock_disable_spans.assert_called_once()
        assert mock_tracer._instance_shutdown is True
        mock_force_flush.assert_called_once_with(mock_tracer, timeout_millis=5000)
        mock_shutdown_main.assert_called_once_with(mock_tracer)
        mock_cleanup_state.assert_called_once_with(mock_tracer)

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    def test_shutdown_without_lock_test_mode(
        self,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test shutdown without lock in test mode skips flush."""
        # Setup
        mock_tracer.test_mode = True

        # Execute
        _shutdown_without_lock(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Skipping flush in test mode to prevent conflicts",
        )
        mock_force_flush.assert_not_called()

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.force_flush_tracer")
    def test_shutdown_without_lock_flush_retry(
        self,
        mock_force_flush: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test flush retry logic in shutdown without lock."""
        # Setup
        mock_force_flush.side_effect = [False, True]  # Fail first, succeed on retry

        # Execute
        _shutdown_without_lock(mock_tracer)

        # Verify
        assert mock_force_flush.call_count == 2
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Initial flush failed (timeout: 5000ms), retrying",
        )
        mock_safe_log.assert_any_call(
            mock_tracer,
            "info",
            "Flush succeeded on retry (timeout: 10000ms)",
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown._cleanup_tracer_state")
    def test_shutdown_without_lock_exception_handling(
        self,
        mock_cleanup_state: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test exception handling in shutdown without lock."""
        # Setup - cause an exception during cleanup
        mock_cleanup_state.side_effect = Exception("Cleanup error")

        # Execute
        _shutdown_without_lock(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Error during tracer shutdown (without lock)",
            honeyhive_data={
                "error": "Cleanup error",
                "error_type": "Exception",
                "operation": "tracer_shutdown_without_lock",
            },
        )


class TestShutdownMainProvider:
    """Test cases for _shutdown_main_provider function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock tracer instance for testing."""
        tracer = Mock()
        tracer.test_mode = False
        tracer.provider = Mock()
        tracer.provider.shutdown = Mock()
        return tracer

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.ThreadPoolExecutor")
    def test_shutdown_main_provider_success(
        self,
        mock_executor_class: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful main provider shutdown."""
        # Setup
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__.return_value = None
        mock_future = Mock()
        mock_executor.submit.return_value = mock_future
        mock_future.result.return_value = None

        # Execute
        _shutdown_main_provider(mock_tracer)

        # Verify
        mock_executor.submit.assert_called_once_with(mock_tracer.provider.shutdown)
        mock_future.result.assert_called_once_with(timeout=5.0)
        mock_safe_log.assert_any_call(
            mock_tracer,
            "info",
            "Main tracer provider shut down successfully",
            honeyhive_data={
                "provider_type": "main",
                "timeout_seconds": 5.0,
            },
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.ThreadPoolExecutor")
    def test_shutdown_main_provider_test_mode_timeout(
        self,
        mock_executor_class: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test main provider shutdown with test mode timeout."""
        # Setup
        mock_tracer.test_mode = True
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__.return_value = None
        mock_future = Mock()
        mock_executor.submit.return_value = mock_future
        mock_future.result.return_value = None

        # Execute
        _shutdown_main_provider(mock_tracer)

        # Verify
        mock_future.result.assert_called_once_with(timeout=1.0)

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.ThreadPoolExecutor")
    def test_shutdown_main_provider_timeout(
        self,
        mock_executor_class: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test main provider shutdown timeout handling."""
        # Setup
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__.return_value = None
        mock_future = Mock()
        mock_executor.submit.return_value = mock_future
        mock_future.result.side_effect = Exception("Timeout")

        # Execute
        _shutdown_main_provider(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Provider shutdown timed out after 5.0s, proceeding anyway (graceful degradation)",
            honeyhive_data={
                "provider_type": "main",
                "timeout_seconds": 5.0,
                "degradation_reason": "shutdown_timeout",
                "error_type": "Exception",
            },
        )
        mock_future.cancel.assert_called_once()

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.ThreadPoolExecutor")
    def test_shutdown_main_provider_with_proxy_reset(
        self,
        mock_executor_class: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test main provider shutdown with proxy provider reset."""
        # Setup
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        mock_executor_class.return_value.__exit__.return_value = None
        mock_future = Mock()
        mock_executor.submit.return_value = mock_future
        mock_future.result.return_value = None

        with patch("opentelemetry.trace.ProxyTracerProvider") as mock_proxy:
            with patch(
                "honeyhive.tracer.integration.detection.set_global_provider"
            ) as mock_set_global:
                mock_proxy_instance = Mock()
                mock_proxy.return_value = mock_proxy_instance

                # Execute
                _shutdown_main_provider(mock_tracer)

                # Verify
                mock_proxy.assert_called_once()
                mock_set_global.assert_called_once_with(
                    mock_proxy_instance, force_override=True
                )
                mock_safe_log.assert_any_call(
                    mock_tracer,
                    "debug",
                    "Reset global TracerProvider to ProxyTracerProvider",
                    honeyhive_data={
                        "reason": "main_provider_shutdown_cleanup",
                        "allows_new_main_providers": True,
                    },
                )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    def test_shutdown_main_provider_exception(
        self,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test exception handling in main provider shutdown."""
        # Setup - cause an exception
        mock_tracer.provider = None

        # Execute
        _shutdown_main_provider(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Error shutting down main provider",
            honeyhive_data={
                "error": "'NoneType' object has no attribute 'shutdown'",
                "error_type": "AttributeError",
                "operation": "shutdown_main_provider",
            },
        )


class TestCleanupSecondaryProvider:
    """Test cases for _cleanup_secondary_provider function."""

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    def test_cleanup_secondary_provider(self, mock_safe_log: Mock) -> None:
        """Test cleanup of secondary provider."""
        # Setup
        mock_tracer = Mock()

        # Execute
        _cleanup_secondary_provider(mock_tracer)

        # Verify
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "info",
            "Tracer instance closed (secondary provider)",
            honeyhive_data={
                "provider_type": "secondary",
                "note": "Provider left running for other instances",
            },
        )


class TestCleanupTracerState:
    """Test cases for _cleanup_tracer_state function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock tracer instance for testing."""
        tracer = Mock()
        tracer.is_main_provider = True
        tracer._tracer_id = "test-tracer-123"
        tracer._initialized = True
        tracer.tracer = Mock()
        tracer.span_processor = Mock()
        tracer.propagator = Mock()
        tracer.provider = Mock()
        return tracer

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_cleanup_tracer_state_success(
        self,
        mock_registry: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful tracer state cleanup."""
        # Setup
        mock_registry.unregister_tracer.return_value = True

        # Execute
        _cleanup_tracer_state(mock_tracer)

        # Verify
        mock_registry.unregister_tracer.assert_called_once_with("test-tracer-123")
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Tracer unregistered from auto-discovery",
            honeyhive_data={"tracer_id": "test-tracer-123"},
        )
        mock_safe_log.assert_any_call(
            mock_tracer, "debug", "Tracer instance state cleaned up"
        )

        # Verify state cleanup
        assert mock_tracer.tracer is None
        assert mock_tracer.span_processor is None
        assert mock_tracer.propagator is None
        assert mock_tracer._initialized is False
        assert mock_tracer.provider is None  # Main provider clears provider

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_cleanup_tracer_state_secondary_provider(
        self,
        _mock_registry: Mock,
        _mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test tracer state cleanup for secondary provider."""
        # Setup
        mock_tracer.is_main_provider = False
        original_provider = mock_tracer.provider

        # Execute
        _cleanup_tracer_state(mock_tracer)

        # Verify
        # Secondary provider should not clear provider reference
        assert mock_tracer.provider is original_provider

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_cleanup_tracer_state_no_tracer_id(
        self,
        mock_registry: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test tracer state cleanup when no tracer ID is present."""
        # Setup
        mock_tracer._tracer_id = None

        # Execute
        _cleanup_tracer_state(mock_tracer)

        # Verify
        mock_registry.unregister_tracer.assert_not_called()
        mock_safe_log.assert_any_call(
            mock_tracer, "debug", "Tracer instance state cleaned up"
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_cleanup_tracer_state_unregister_failure(
        self,
        mock_registry: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test tracer state cleanup when unregister fails."""
        # Setup
        mock_registry.unregister_tracer.side_effect = Exception("Unregister failed")

        # Execute
        _cleanup_tracer_state(mock_tracer)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Failed to unregister tracer: Unregister failed",
            honeyhive_data={
                "error_type": "Exception",
                "operation": "unregister_tracer",
            },
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    def test_cleanup_tracer_state_exception(
        self,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test exception handling in tracer state cleanup."""
        # Setup - Remove required attributes to cause exceptions
        del mock_tracer._tracer_id
        del mock_tracer._initialized

        # Execute - should not crash despite missing attributes
        _cleanup_tracer_state(mock_tracer)

        # Verify - function completed without crashing
        assert mock_safe_log.called  # Some logging should have occurred


class TestGracefulShutdownAll:
    """Test cases for graceful_shutdown_all function."""

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    @patch("honeyhive.tracer.lifecycle.shutdown.shutdown_tracer")
    def test_graceful_shutdown_all_success(
        self,
        mock_shutdown_tracer: Mock,
        mock_registry: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test successful graceful shutdown of all tracers."""
        # Setup
        mock_tracer1 = Mock()
        mock_tracer1._tracer_id = "tracer-1"
        mock_tracer2 = Mock()
        mock_tracer2._tracer_id = "tracer-2"
        mock_registry.get_all_tracers.return_value = [mock_tracer1, mock_tracer2]

        # Execute
        graceful_shutdown_all()

        # Verify
        mock_safe_log.assert_any_call(
            None,
            "info",
            "Starting graceful shutdown of all tracers",
            honeyhive_data={"tracer_count": 2},
        )
        assert mock_shutdown_tracer.call_count == 2
        mock_shutdown_tracer.assert_any_call(mock_tracer1)
        mock_shutdown_tracer.assert_any_call(mock_tracer2)
        mock_safe_log.assert_any_call(
            None,
            "info",
            "Graceful shutdown completed",
            honeyhive_data={
                "total_tracers": 2,
                "successful_shutdowns": 2,
                "failed_shutdowns": 0,
            },
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_graceful_shutdown_all_no_tracers(
        self,
        mock_registry: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test graceful shutdown when no tracers are active."""
        # Setup
        mock_registry.get_all_tracers.return_value = []

        # Execute
        graceful_shutdown_all()

        # Verify
        mock_safe_log.assert_called_once_with(
            None, "debug", "No active tracers found for shutdown"
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    @patch("honeyhive.tracer.lifecycle.shutdown.shutdown_tracer")
    def test_graceful_shutdown_all_partial_failure(
        self,
        mock_shutdown_tracer: Mock,
        mock_registry: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test graceful shutdown with some tracer failures."""
        # Setup
        mock_tracer1 = Mock()
        mock_tracer1._tracer_id = "tracer-1"
        mock_tracer2 = Mock()
        mock_tracer2._tracer_id = "tracer-2"
        mock_registry.get_all_tracers.return_value = [mock_tracer1, mock_tracer2]

        def shutdown_side_effect(tracer: Mock) -> None:
            if tracer._tracer_id == "tracer-2":
                raise Exception("Shutdown failed")

        mock_shutdown_tracer.side_effect = shutdown_side_effect

        # Execute
        graceful_shutdown_all()

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer2,
            "error",
            "Tracer shutdown failed",
            honeyhive_data={
                "tracer_id": "tracer-2",
                "error": "Shutdown failed",
                "error_type": "Exception",
                "operation": "graceful_shutdown_single_tracer",
            },
        )
        mock_safe_log.assert_any_call(
            None,
            "info",
            "Graceful shutdown completed",
            honeyhive_data={
                "total_tracers": 2,
                "successful_shutdowns": 1,
                "failed_shutdowns": 1,
            },
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown.registry")
    def test_graceful_shutdown_all_exception(
        self,
        mock_registry: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test exception handling in graceful shutdown all."""
        # Setup
        mock_registry.get_all_tracers.side_effect = Exception("Registry error")

        # Execute
        graceful_shutdown_all()

        # Verify
        mock_safe_log.assert_any_call(
            None,
            "error",
            "Error during graceful shutdown of all tracers",
            honeyhive_data={
                "error": "Registry error",
                "error_type": "Exception",
                "operation": "graceful_shutdown_all",
            },
        )


class TestPendingSpansHelpers:
    """Test cases for pending spans helper functions."""

    def test_check_processor_pending_spans_with_spans_list(self) -> None:
        """Test _check_processor_pending_spans with spans_list."""
        # Setup
        processor = Mock()
        processor._exporter = Mock()
        processor._spans_list = ["span1", "span2"]

        # Execute
        result = _check_processor_pending_spans(processor)

        # Verify
        assert result is True

    def test_check_processor_pending_spans_empty_spans_list(self) -> None:
        """Test _check_processor_pending_spans with empty spans_list."""
        # Setup
        processor = Mock()
        processor._exporter = Mock()
        processor._spans_list = []

        # Execute
        result = _check_processor_pending_spans(processor)

        # Verify
        assert result is False

    def test_check_processor_pending_spans_with_pending_spans(self) -> None:
        """Test _check_processor_pending_spans with _pending_spans."""
        # Setup
        processor = Mock()
        del processor._exporter  # Remove _exporter attribute
        processor._pending_spans = ["span1"]

        # Execute
        result = _check_processor_pending_spans(processor)

        # Verify
        assert result is True

    def test_check_processor_pending_spans_no_pending_work(self) -> None:
        """Test _check_processor_pending_spans with no pending work."""
        # Setup
        processor = Mock()
        del processor._exporter
        del processor._spans_list
        del processor._pending_spans

        # Execute
        result = _check_processor_pending_spans(processor)

        # Verify
        assert result is False

    def test_has_pending_spans_true(self) -> None:
        """Test _has_pending_spans returns True when spans are pending."""
        # Setup
        tracer = Mock()
        processor1 = Mock()
        processor1._spans_list = []
        processor2 = Mock()
        processor2._spans_list = ["span1"]
        tracer.provider._span_processors = [processor1, processor2]

        # Execute
        result = _has_pending_spans(tracer)

        # Verify
        assert result is True

    def test_has_pending_spans_false(self) -> None:
        """Test _has_pending_spans returns False when no spans are pending."""
        # Setup
        tracer = Mock()
        processor = Mock()
        processor._spans_list = []
        del processor._pending_spans
        tracer.provider._span_processors = [processor]

        # Execute
        result = _has_pending_spans(tracer)

        # Verify
        assert result is False

    def test_has_pending_spans_no_processors(self) -> None:
        """Test _has_pending_spans when provider has no _span_processors."""
        # Setup
        tracer = Mock()
        del tracer.provider._span_processors

        # Execute
        result = _has_pending_spans(tracer)

        # Verify
        assert result is False


class TestWaitForPendingSpans:
    """Test cases for wait_for_pending_spans function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock tracer instance for testing."""
        tracer = Mock()
        tracer.provider = Mock()
        return tracer

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown._has_pending_spans")
    @patch("honeyhive.tracer.lifecycle.shutdown.time")
    def test_wait_for_pending_spans_success(
        self,
        mock_time: Mock,
        mock_has_pending: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test successful wait for pending spans completion."""
        # Setup
        mock_time.time.return_value = 1.0  # Fixed time for wait calculation
        mock_has_pending.return_value = False

        # Execute
        result = wait_for_pending_spans(mock_tracer, max_wait_seconds=5.0)

        # Verify
        assert result is True
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "debug",
            "No pending spans detected",
            honeyhive_data={"wait_time": 0.0},
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown._has_pending_spans")
    @patch("honeyhive.tracer.lifecycle.shutdown.time")
    def test_wait_for_pending_spans_timeout(
        self,
        mock_time: Mock,
        mock_has_pending: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test wait for pending spans timeout."""
        # Setup
        mock_time.time.side_effect = [0.0, 6.0]  # Exceed timeout
        mock_has_pending.return_value = True
        mock_time.sleep = Mock()

        # Execute
        result = wait_for_pending_spans(mock_tracer, max_wait_seconds=5.0)

        # Verify
        assert result is False
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "warning",
            "Timeout waiting for pending spans",
            honeyhive_data={"max_wait_seconds": 5.0},
        )

    def test_wait_for_pending_spans_no_provider(self, mock_tracer: Mock) -> None:
        """Test wait for pending spans when tracer has no provider."""
        # Setup
        mock_tracer.provider = None

        # Execute
        result = wait_for_pending_spans(mock_tracer)

        # Verify
        assert result is True

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown._has_pending_spans")
    @patch("honeyhive.tracer.lifecycle.shutdown.time")
    def test_wait_for_pending_spans_exception(
        self,
        mock_time: Mock,
        mock_has_pending: Mock,
        mock_safe_log: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test exception handling in wait for pending spans."""
        # Setup
        mock_time.time.return_value = 1.0  # Fixed time for wait calculation
        mock_has_pending.side_effect = Exception("Check failed")

        # Execute
        result = wait_for_pending_spans(mock_tracer, max_wait_seconds=1.0)

        # Verify
        assert result is False
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Error checking for pending spans: Check failed",
            honeyhive_data={
                "wait_time": 0.0,
                "error_type": "Exception",
                "operation": "wait_for_pending_spans",
            },
        )

    @patch("honeyhive.tracer.lifecycle.shutdown.safe_log")
    @patch("honeyhive.tracer.lifecycle.shutdown._has_pending_spans")
    @patch("honeyhive.tracer.lifecycle.shutdown.time")
    def test_wait_for_pending_spans_with_sleep_cycles(
        self,
        mock_time: Mock,
        mock_has_pending: Mock,
        mock_tracer: Mock,
    ) -> None:
        """Test wait for pending spans with multiple sleep cycles."""
        # Setup
        mock_time.time.return_value = 0.3  # Fixed time for wait calculation
        mock_has_pending.side_effect = [True, True, False]  # Pending, then complete
        mock_time.sleep = Mock()

        # Execute
        result = wait_for_pending_spans(mock_tracer, max_wait_seconds=5.0)

        # Verify
        assert result is True
        assert mock_time.sleep.call_count == 2  # Called twice before completion
        mock_time.sleep.assert_called_with(0.1)
