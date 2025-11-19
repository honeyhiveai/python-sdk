"""Shutdown and cleanup operations for tracer lifecycle management.

This module handles tracer shutdown, provider cleanup, and resource management
with comprehensive error handling, timeout protection, and graceful degradation.
"""

# pylint: disable=cyclic-import,duplicate-code
# Justification: This module completes the necessary architectural cycle.
# shutdown.py depends on both core.py (for shared infrastructure) and flush.py
# (for required flush-before-shutdown operations), while core.py coordinates
# Agent OS graceful degradation error handling patterns are intentionally consistent
# shutdown operations. This cycle is essential for correct shutdown sequencing:
# flush → shutdown → cleanup. The alternative would be a monolithic module
# or complex dependency injection, both of which would be worse architecturally.

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ...utils.logger import safe_log
from .. import registry
from .core import (
    acquire_lifecycle_lock_optimized,
    disable_new_span_creation,
    get_lock_config,
)
from .flush import force_flush_tracer


def shutdown_tracer(tracer_instance: Any) -> None:
    """Shutdown a tracer instance and clean up its resources.

    This function performs a graceful shutdown of a tracer instance,
    including flushing pending data, shutting down providers, and
    cleaning up resources. It handles both main and secondary providers
    appropriately.

    :param tracer_instance: The tracer instance to shutdown
    :type tracer_instance: HoneyHiveTracer

    **Example:**

    .. code-block:: python

        # Graceful shutdown
        shutdown_tracer(tracer)

        # In a try/finally block
        try:
            # Use tracer
            with tracer.start_span("operation") as span:
                pass
        finally:
            shutdown_tracer(tracer)

    **Note:**

    This function only shuts down the OpenTelemetry provider if the
    tracer instance is the main provider. Secondary providers are
    left running to avoid disrupting other tracer instances.
    """
    # Check if logging is still available (pytest-xdist workers may have closed streams)
    safe_log(
        tracer_instance, "debug", "shutdown_tracer: Starting data loss prevention phase"
    )

    # Phase 1: Data loss prevention - optimized for parallel execution
    # This ensures we attempt to preserve data even if locking fails
    test_mode = getattr(tracer_instance, "test_mode", False)

    # Skip data loss prevention in test mode to prevent worker conflicts
    # In production, this is critical for data preservation
    if not test_mode:
        # Graceful drain phase (production only)
        # For multi-instance architecture: only disable globally if main provider
        if getattr(tracer_instance, "is_main_provider", False):
            disable_new_span_creation()

        # Always set instance-specific shutdown flag for this tracer
        # Protected access required for multi-instance lifecycle management
        tracer_instance._instance_shutdown = True  # pylint: disable=protected-access

        # Brief grace period for existing spans to complete naturally
        time.sleep(0.1)

        # Force flush with extended timeout and retry logic (before lock acquisition)
        timeout_ms = 5000  # Extended timeout for production

        safe_log(
            tracer_instance,
            "debug",
            "Starting pre-lock force flush for data loss prevention",
            honeyhive_data={
                "timeout_ms": timeout_ms,
                "test_mode": test_mode,
                "phase": "pre_lock_data_preservation",
            },
        )

        flush_success = force_flush_tracer(tracer_instance, timeout_millis=timeout_ms)

        # Retry logic for critical data preservation (production only)
        if not flush_success:
            safe_log(
                tracer_instance,
                "warning",
                f"Pre-lock flush failed (timeout: {timeout_ms}ms), retrying",
            )

            retry_timeout_ms = timeout_ms * 2
            flush_success = force_flush_tracer(
                tracer_instance, timeout_millis=retry_timeout_ms
            )

            if flush_success:
                safe_log(
                    tracer_instance,
                    "info",
                    f"Pre-lock flush succeeded on retry ({retry_timeout_ms}ms)",
                )
            else:
                safe_log(
                    tracer_instance,
                    "error",
                    f"Pre-lock flush failed after retry ({retry_timeout_ms}ms), "
                    "continuing with shutdown - potential data loss",
                )
    else:
        # Test mode: skip pre-lock flush to prevent pytest-xdist worker conflicts
        safe_log(
            tracer_instance,
            "debug",
            "Skipping pre-lock flush in test mode to prevent conflicts",
        )
        flush_success = True  # Assume success for test mode

    safe_log(
        tracer_instance,
        "debug",
        "shutdown_tracer: Acquiring _lifecycle_lock for shutdown",
    )

    # Use environment-optimized lock timeout for better performance
    # Automatically detects Lambda, K8s, high-concurrency environments
    with acquire_lifecycle_lock_optimized("lifecycle") as lock_acquired:
        if not lock_acquired:
            # Graceful degradation: Try to log timeout but don't crash
            config = get_lock_config()
            timeout_used = config.get("lifecycle_timeout", 1.0)
            safe_log(
                tracer_instance,
                "warning",
                f"Failed to acquire _lifecycle_lock within {timeout_used}s, "
                "proceeding without lock",
                honeyhive_data={
                    "lock_timeout": timeout_used,
                    "lock_strategy": config.get("description", "unknown"),
                    "degradation_reason": "lock_acquisition_timeout",
                    "data_flush_completed": flush_success,
                },
            )
            # Continue without the lock - better than hanging indefinitely
            _shutdown_without_lock(tracer_instance)
            return

        try:
            safe_log(
                tracer_instance,
                "debug",
                "Starting tracer shutdown",
                honeyhive_data={
                    "is_main_provider": tracer_instance.is_main_provider,
                    "has_provider": bool(tracer_instance.provider),
                },
            )

            # Skip force_flush during shutdown to prevent recursive deadlock
            # The force_flush_tracer also tries to acquire _lifecycle_lock,
            # causing deadlock
            safe_log(
                tracer_instance,
                "debug",
                "Skipping force_flush during shutdown to prevent recursive deadlock",
            )

            # Only shutdown if we're the main provider
            if (
                tracer_instance.is_main_provider
                and tracer_instance.provider
                and hasattr(tracer_instance.provider, "shutdown")
            ):
                _shutdown_main_provider(tracer_instance)
            else:
                _cleanup_secondary_provider(tracer_instance)

            # Clean up instance state
            _cleanup_tracer_state(tracer_instance)

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                tracer_instance,
                "error",
                "Error during tracer shutdown",
                honeyhive_data={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "operation": "tracer_shutdown",
                },
            )


def _shutdown_without_lock(tracer_instance: Any) -> None:
    """Shutdown tracer without acquiring the lifecycle lock.

    This function performs the same shutdown operations as shutdown_tracer
    but without lock protection. Used for graceful degradation when lock
    acquisition times out.

    :param tracer_instance: The tracer instance to shutdown
    :type tracer_instance: HoneyHiveTracer
    """
    try:
        safe_log(
            tracer_instance,
            "debug",
            "Starting tracer shutdown WITHOUT LOCK (graceful degradation)",
            honeyhive_data={
                "is_main_provider": tracer_instance.is_main_provider,
                "has_provider": bool(tracer_instance.provider),
            },
        )

        # Phase 1: Data loss prevention - optimized for parallel execution
        test_mode = getattr(tracer_instance, "test_mode", False)

        # Skip data loss prevention in test mode to prevent worker conflicts
        # In production, this is critical for data preservation
        if not test_mode:
            # Graceful drain phase (production only)
            # For multi-instance architecture: only disable globally if main provider
            if getattr(tracer_instance, "is_main_provider", False):
                disable_new_span_creation()

            # Always set instance-specific shutdown flag for this tracer
            # Protected access required for multi-instance lifecycle management
            tracer_instance._instance_shutdown = (  # pylint: disable=protected-access
                True
            )

            # Brief grace period for existing spans to complete naturally
            time.sleep(0.1)

            # Phase 2: Force flush with extended timeout and retry logic
            timeout_ms = 5000  # Extended timeout for production

            safe_log(
                tracer_instance,
                "debug",
                "Starting force flush with data loss prevention (without lock)",
                honeyhive_data={
                    "timeout_ms": timeout_ms,
                    "test_mode": test_mode,
                    "phase": "graceful_drain_complete",
                },
            )

            flush_success = force_flush_tracer(
                tracer_instance, timeout_millis=timeout_ms
            )

            # Retry logic for critical data preservation (production only)
            if not flush_success:
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Initial flush failed (timeout: {timeout_ms}ms), retrying",
                )

                # Retry with double timeout
                retry_timeout_ms = timeout_ms * 2
                flush_success = force_flush_tracer(
                    tracer_instance, timeout_millis=retry_timeout_ms
                )

                if flush_success:
                    safe_log(
                        tracer_instance,
                        "info",
                        f"Flush succeeded on retry (timeout: {retry_timeout_ms}ms)",
                    )
                else:
                    safe_log(
                        tracer_instance,
                        "error",
                        f"Flush failed after retry (timeout: {retry_timeout_ms}ms), "
                        "proceeding with shutdown - potential data loss",
                    )
        else:
            # Test mode: skip flush to prevent pytest-xdist worker conflicts
            safe_log(
                tracer_instance,
                "debug",
                "Skipping flush in test mode to prevent conflicts",
            )

        # Only shutdown if we're the main provider
        if (
            tracer_instance.is_main_provider
            and tracer_instance.provider
            and hasattr(tracer_instance.provider, "shutdown")
        ):
            _shutdown_main_provider(tracer_instance)
        else:
            _cleanup_secondary_provider(tracer_instance)

        # Clean up instance state
        _cleanup_tracer_state(tracer_instance)

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Error during tracer shutdown (without lock)",
            honeyhive_data={
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "tracer_shutdown_without_lock",
            },
        )


def _shutdown_main_provider(tracer_instance: Any) -> None:
    """Shutdown the main OpenTelemetry provider with timeout protection.

    This function implements OpenTelemetry best practices for shutdown in
    production environments. The official OTel Python SDK's TracerProvider.shutdown()
    and BatchSpanProcessor.shutdown() methods do NOT accept timeout parameters
    and can hang indefinitely if exporters can't connect. This is a known issue
    in serverless environments like AWS Lambda.

    Our solution follows OTel community recommendations:
    1. Call force_flush() with timeout first (has timeout support)
    2. Use ThreadPoolExecutor timeout wrapper for shutdown() calls
    3. Graceful degradation - never crash the host application

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    try:
        # Use shorter timeout for test environments, extended for production
        timeout_seconds = (
            1.0 if getattr(tracer_instance, "test_mode", False) else 5.0
        )  # Extended from 3.0s

        # Use ThreadPoolExecutor to implement timeout for provider shutdown
        with ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="provider-shutdown"
        ) as executor:
            future = executor.submit(tracer_instance.provider.shutdown)
            try:
                future.result(timeout=timeout_seconds)
                safe_log(
                    tracer_instance,
                    "info",
                    "Main tracer provider shut down successfully",
                    honeyhive_data={
                        "provider_type": "main",
                        "timeout_seconds": timeout_seconds,
                    },
                )

                # Always reset global TracerProvider to ProxyTracerProvider when main
                # provider shuts down
                # This ensures new tracers can become the main provider
                try:
                    # Import inside try block for graceful degradation
                    from opentelemetry.trace import (  # pylint: disable=import-outside-toplevel
                        ProxyTracerProvider,
                    )

                    from ..integration.detection import (  # pylint: disable=import-outside-toplevel
                        set_global_provider,
                    )

                    proxy_provider = ProxyTracerProvider()
                    set_global_provider(proxy_provider, force_override=True)
                    safe_log(
                        tracer_instance,
                        "debug",
                        "Reset global TracerProvider to ProxyTracerProvider",
                        honeyhive_data={
                            "reason": "main_provider_shutdown_cleanup",
                            "allows_new_main_providers": True,
                        },
                    )
                except Exception as reset_error:
                    # Graceful degradation following Agent OS standards
                    safe_log(
                        tracer_instance,
                        "warning",
                        "Failed to reset TracerProvider to ProxyTracerProvider",
                        honeyhive_data={
                            "error": str(reset_error),
                            "error_type": type(reset_error).__name__,
                            "operation": "reset_tracer_provider",
                        },
                    )
            except Exception as timeout_error:
                # Graceful degradation: Log timeout but don't crash the application
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Provider shutdown timed out after {timeout_seconds}s, "
                    "proceeding anyway (graceful degradation)",
                    honeyhive_data={
                        "provider_type": "main",
                        "timeout_seconds": timeout_seconds,
                        "degradation_reason": "shutdown_timeout",
                        "error_type": type(timeout_error).__name__,
                    },
                )
                # Cancel the future to clean up the thread
                future.cancel()

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Error shutting down main provider",
            honeyhive_data={
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "shutdown_main_provider",
            },
        )


def _cleanup_secondary_provider(_tracer_instance: Any) -> None:
    """Clean up secondary provider resources without shutting down the provider.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    safe_log(
        _tracer_instance,
        "info",
        "Tracer instance closed (secondary provider)",
        honeyhive_data={
            "provider_type": "secondary",
            "note": "Provider left running for other instances",
        },
    )


def _cleanup_tracer_state(tracer_instance: Any) -> None:
    """Clean up tracer instance state after shutdown.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    try:
        # Unregister from auto-discovery if registered
        # pylint: disable=protected-access
        # Justification: Lifecycle management requires access to tracer internal state
        # (_tracer_id, _initialized) for proper cleanup and registry management.
        if hasattr(tracer_instance, "_tracer_id") and tracer_instance._tracer_id:
            try:
                registry.unregister_tracer(tracer_instance._tracer_id)
                safe_log(
                    tracer_instance,
                    "debug",
                    "Tracer unregistered from auto-discovery",
                    honeyhive_data={"tracer_id": tracer_instance._tracer_id},
                )
            except Exception as e:
                # Graceful degradation following Agent OS standards - never crash host
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Failed to unregister tracer: {e}",
                    honeyhive_data={
                        "error_type": type(e).__name__,
                        "operation": "unregister_tracer",
                    },
                )

        # Clear instance references
        tracer_instance.tracer = None
        tracer_instance.span_processor = None
        tracer_instance.propagator = None
        tracer_instance._initialized = False

        # Don't clear provider reference for secondary providers
        # as it might be shared with other instances
        if tracer_instance.is_main_provider:
            tracer_instance.provider = None

        safe_log(tracer_instance, "debug", "Tracer instance state cleaned up")

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "warning",
            f"Error during state cleanup: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "cleanup_tracer_state",
            },
        )


def graceful_shutdown_all() -> None:
    """Gracefully shutdown all registered tracer instances.

    This function attempts to find and shutdown all active HoneyHive
    tracer instances. It's useful for application shutdown or cleanup
    scenarios where multiple tracers might be active.

    **Example:**

    .. code-block:: python

        # Application shutdown
        import atexit
        atexit.register(graceful_shutdown_all)

        # Or explicit cleanup
        graceful_shutdown_all()

    **Note:**

    This function uses the tracer registry to find active instances.
    It attempts graceful shutdown but continues even if some instances
    fail to shutdown properly.
    """
    try:
        active_tracers = registry.get_all_tracers()

        if not active_tracers:
            safe_log(None, "debug", "No active tracers found for shutdown")
            return

        safe_log(
            None,
            "info",
            "Starting graceful shutdown of all tracers",
            honeyhive_data={"tracer_count": len(active_tracers)},
        )

        shutdown_results = []

        for tracer_instance in active_tracers:
            try:
                shutdown_tracer(tracer_instance)
                shutdown_results.append(
                    (getattr(tracer_instance, "_tracer_id", "unknown"), True)
                )
                safe_log(
                    tracer_instance,
                    "debug",
                    "Tracer shutdown successful",
                    honeyhive_data={
                        "tracer_id": getattr(tracer_instance, "_tracer_id", "unknown")
                    },
                )
            except Exception as e:
                shutdown_results.append(
                    (getattr(tracer_instance, "_tracer_id", "unknown"), False)
                )
                # Graceful degradation following Agent OS standards - never crash host
                safe_log(
                    tracer_instance,
                    "error",
                    "Tracer shutdown failed",
                    honeyhive_data={
                        "tracer_id": getattr(tracer_instance, "_tracer_id", "unknown"),
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "operation": "graceful_shutdown_single_tracer",
                    },
                )

        # Log summary
        successful_shutdowns = sum(1 for _, success in shutdown_results if success)
        safe_log(
            None,
            "info",
            "Graceful shutdown completed",
            honeyhive_data={
                "total_tracers": len(active_tracers),
                "successful_shutdowns": successful_shutdowns,
                "failed_shutdowns": len(active_tracers) - successful_shutdowns,
            },
        )

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            None,
            "error",
            "Error during graceful shutdown of all tracers",
            honeyhive_data={
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "graceful_shutdown_all",
            },
        )


def _check_processor_pending_spans(processor: Any) -> bool:
    """Check if a processor has pending spans."""
    # Check for batch processor with pending spans
    if hasattr(processor, "_exporter") and hasattr(processor, "_spans_list"):
        spans_list = getattr(processor, "_spans_list", [])
        return bool(spans_list)

    # Check for other processor types with pending work
    if hasattr(processor, "_pending_spans"):
        pending_spans = getattr(processor, "_pending_spans", [])
        return bool(pending_spans)

    return False


def _has_pending_spans(tracer_instance: Any) -> bool:
    """Check if tracer instance has any pending spans."""
    if not hasattr(tracer_instance.provider, "_span_processors"):
        return False

    for processor in getattr(tracer_instance.provider, "_span_processors", []):
        if _check_processor_pending_spans(processor):
            return True

    return False


def wait_for_pending_spans(
    tracer_instance: Any, max_wait_seconds: float = 10.0
) -> bool:
    """Wait for pending spans to complete processing.

    This function waits for any pending spans in the tracer's processors
    to complete processing. It's useful before shutdown to ensure all
    data is properly sent.

    :param tracer_instance: The tracer instance to wait for
    :type tracer_instance: HoneyHiveTracer
    :param max_wait_seconds: Maximum time to wait in seconds
    :type max_wait_seconds: float
    :return: True if all spans completed within timeout, False otherwise
    :rtype: bool

    **Example:**

    .. code-block:: python

        # Wait for spans before shutdown
        if wait_for_pending_spans(tracer, max_wait_seconds=5.0):
            print("All spans completed")
        else:
            print("Timeout waiting for spans")

    **Note:**

    This function polls the span processors to check for pending work.
    It's a best-effort operation and may not catch all edge cases.
    """
    if not tracer_instance.provider:
        return True

    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        try:
            if not _has_pending_spans(tracer_instance):
                safe_log(
                    tracer_instance,
                    "debug",
                    "No pending spans detected",
                    honeyhive_data={"wait_time": time.time() - start_time},
                )
                return True

            # Wait a bit before checking again
            time.sleep(0.1)

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                tracer_instance,
                "warning",
                f"Error checking for pending spans: {e}",
                honeyhive_data={
                    "wait_time": time.time() - start_time,
                    "error_type": type(e).__name__,
                    "operation": "wait_for_pending_spans",
                },
            )
            break

    safe_log(
        tracer_instance,
        "warning",
        "Timeout waiting for pending spans",
        honeyhive_data={"max_wait_seconds": max_wait_seconds},
    )
    return False
