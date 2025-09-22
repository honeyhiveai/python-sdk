"""Core lifecycle management infrastructure.

This module provides the foundational infrastructure for tracer lifecycle
management including safe logging, tracer registration, and thread-safe
lock management utilities.
"""

# pylint: disable=cyclic-import
# Justification: Cyclic imports are architecturally necessary in the lifecycle system.
# The core module provides shared infrastructure (logging, locking, state management)
# that both flush.py and shutdown.py depend on, while core.py needs to coordinate
# flush and shutdown operations in the correct sequence (flush → shutdown → cleanup).
# This creates an intentional cycle that ensures operational correctness while
# maintaining clean separation of concerns. The cycles are resolved safely at
# runtime through lazy imports.

import atexit
import os
import threading
import weakref
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

from ...utils.logger import safe_log

# No module-level logger - use tracer instance logger when available

# Global lock for thread-safe operations
_lifecycle_lock = threading.Lock()

# Thread-safe registry of tracers with atexit handlers
# Using WeakSet to avoid keeping tracers alive just for cleanup
_registered_tracers = weakref.WeakSet()  # type: ignore

# Shutdown state tracking moved to logger module to avoid circular imports

# New span creation control during shutdown
_new_spans_disabled = threading.Event()

# Environment-specific lock configuration
_LOCK_STRATEGIES = {
    "lambda_optimized": {
        "lifecycle_timeout": 0.5,  # Shorter timeout for Lambda constraints
        "flush_timeout": 2.0,  # Lambda execution time limits
        "description": "AWS Lambda optimized - fast timeouts",
    },
    "k8s_optimized": {
        "lifecycle_timeout": 2.0,  # Longer for graceful shutdown
        "flush_timeout": 5.0,  # K8s termination grace period
        "description": "Kubernetes optimized - graceful shutdown focus",
    },
    "standard": {
        "lifecycle_timeout": 1.0,  # Standard timeout
        "flush_timeout": 3.0,  # Standard flush timeout
        "description": "Standard threading environment",
    },
    "high_concurrency": {
        "lifecycle_timeout": 0.3,  # Very fast for high throughput
        "flush_timeout": 1.0,  # Quick flush for performance
        "description": "High concurrency optimized",
    },
}


def get_lock_strategy() -> str:
    """Detect deployment environment and return optimal lock strategy.

    Returns:
        Lock strategy name based on environment detection

    Environment Detection:
        - AWS Lambda: AWS_LAMBDA_FUNCTION_NAME environment variable
        - Kubernetes: KUBERNETES_SERVICE_HOST environment variable
        - High Concurrency: HH_HIGH_CONCURRENCY environment variable
        - Standard: Default fallback

    Examples:
        >>> # In AWS Lambda
        >>> strategy = get_lock_strategy()
        >>> print(strategy)  # 'lambda_optimized'

        >>> # In Kubernetes
        >>> strategy = get_lock_strategy()
        >>> print(strategy)  # 'k8s_optimized'
    """
    # AWS Lambda detection
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "lambda_optimized"

    # Kubernetes detection
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "k8s_optimized"

    # High concurrency mode (explicit opt-in)
    if os.environ.get("HH_HIGH_CONCURRENCY", "").lower() in ("true", "1", "yes"):
        return "high_concurrency"

    # Standard environment (default)
    return "standard"


def get_lock_config(strategy: Optional[str] = None) -> Dict[str, Any]:
    """Get lock configuration for the specified or detected strategy.

    Args:
        strategy: Optional strategy name. If None, auto-detects environment

    Returns:
        Dictionary containing timeout and configuration values

    Examples:
        >>> # Auto-detect environment
        >>> config = get_lock_config()
        >>> print(config['lifecycle_timeout'])  # 1.0 (standard)

        >>> # Explicit strategy
        >>> config = get_lock_config('lambda_optimized')
        >>> print(config['lifecycle_timeout'])  # 0.5 (Lambda optimized)
    """
    if strategy is None:
        strategy = get_lock_strategy()

    return _LOCK_STRATEGIES.get(strategy, _LOCK_STRATEGIES["standard"])


def register_tracer_for_atexit_cleanup(tracer_instance: Any) -> None:
    """Register a tracer instance for automatic cleanup on Python exit.

    This function provides thread-safe registration of tracer instances
    for automatic cleanup during Python interpreter shutdown. This prevents
    race conditions in pytest-xdist workers where logging streams are closed
    before fixture teardown runs.

    :param tracer_instance: The tracer instance to register for cleanup
    :type tracer_instance: HoneyHiveTracer

    **Thread Safety:**

    This function is thread-safe and supports the multi-instance architecture.
    Multiple tracer instances can be registered concurrently from different
    threads without conflicts.

    **Example:**

    .. code-block:: python

        # Register tracer for automatic cleanup
        tracer = HoneyHiveTracer.init(api_key="...", project="...")
        register_tracer_for_atexit_cleanup(tracer)

        # Tracer will be automatically cleaned up on Python exit
        # even if pytest-xdist closes logging streams early

    **Note:**

    Uses WeakSet to avoid keeping tracers alive just for cleanup.
    If a tracer is garbage collected, it's automatically removed
    from the cleanup registry.
    """
    with _lifecycle_lock:
        # Check if already registered to prevent duplicate atexit handlers
        if tracer_instance in _registered_tracers:
            safe_log(
                tracer_instance,
                "debug",
                f"Tracer already registered for atexit cleanup: {id(tracer_instance)}",
            )
            return

        # Add to registry using WeakSet (won't keep tracer alive)
        _registered_tracers.add(tracer_instance)

        # Create cleanup function that captures tracer by weak reference
        tracer_ref = weakref.ref(tracer_instance)

        def cleanup_tracer_on_exit() -> None:
            """Cleanup function that runs during Python shutdown."""
            # safe_log will automatically detect shutdown conditions

            tracer = tracer_ref()
            if tracer is not None:
                try:
                    # Import here to avoid circular imports
                    # pylint: disable=import-outside-toplevel
                    from .flush import force_flush_tracer
                    from .shutdown import shutdown_tracer

                    # Force flush first, then shutdown (no logging during shutdown)
                    force_flush_tracer(tracer, timeout_millis=1000)  # Shorter timeout
                    shutdown_tracer(tracer)

                except Exception as e:
                    # Graceful degradation following Agent OS standards
                    # Silent failure during shutdown is expected, but log for debugging
                    safe_log(
                        None,
                        "debug",
                        "Expected shutdown exception during cleanup",
                        honeyhive_data={"error_type": type(e).__name__},
                    )

        # Register the cleanup function with atexit
        atexit.register(cleanup_tracer_on_exit)

        safe_log(
            tracer_instance,
            "debug",
            f"Registered tracer for atexit cleanup: {id(tracer_instance)}",
            honeyhive_data={
                "tracer_id": id(tracer_instance),
                "registered_count": len(_registered_tracers),
                "architecture": "multi-instance",
            },
        )


def mark_stream_closure_detected() -> None:
    """Mark that stream closure has been detected during shutdown.

    This function should be called when stream closure is detected during
    shutdown to disable all logging and prevent race conditions with closed streams.
    This is useful in multiprocess environments, containers, and test frameworks.

    **Usage:**

    .. code-block:: python

        # In cleanup handlers
        try:
            tracer.shutdown()
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(None, "debug", "Shutdown exception during stream closure",
                    honeyhive_data={"error_type": type(e).__name__})
    """
    # safe_log will automatically detect stream closure and shutdown
    # No manual signaling needed - it handles everything internally


def disable_new_span_creation() -> None:
    """Disable creation of new spans during shutdown phase.

    This function prevents new spans from being created while allowing
    existing spans to complete naturally. This is part of the graceful
    shutdown process to prevent data loss.

    **Usage:**

    .. code-block:: python

        # Phase 1: Graceful drain
        disable_new_span_creation()
        time.sleep(0.1)  # Allow existing spans to complete

        # Phase 2: Force flush
        tracer.force_flush()
    """
    _new_spans_disabled.set()


def is_new_span_creation_disabled() -> bool:
    """Check if new span creation is disabled.

    Returns:
        bool: True if new span creation is disabled, False otherwise
    """
    return _new_spans_disabled.is_set()


def unregister_tracer_from_atexit_cleanup(tracer_instance: Any) -> None:
    """Unregister a tracer instance from automatic cleanup.

    This function removes a tracer from the atexit cleanup registry.
    Useful when manually shutting down a tracer before Python exit.

    :param tracer_instance: The tracer instance to unregister
    :type tracer_instance: HoneyHiveTracer

    **Thread Safety:**

    This function is thread-safe and supports concurrent access.

    **Example:**

    .. code-block:: python

        # Manual cleanup - unregister from atexit
        unregister_tracer_from_atexit_cleanup(tracer)
        tracer.force_flush()
        tracer.shutdown()
    """
    with _lifecycle_lock:
        if tracer_instance in _registered_tracers:
            _registered_tracers.discard(tracer_instance)
            safe_log(
                tracer_instance,
                "debug",
                f"Unregistered tracer from atexit cleanup: {id(tracer_instance)}",
                honeyhive_data={
                    "tracer_id": id(tracer_instance),
                    "remaining_count": len(_registered_tracers),
                },
            )


@contextmanager
def acquire_lock_with_timeout(lock: Any, timeout_seconds: float) -> Iterator[bool]:
    """Context manager for acquiring a lock with timeout."""
    acquired = lock.acquire(timeout=timeout_seconds)
    if not acquired:
        yield False
    else:
        try:
            yield True
        finally:
            lock.release()


@contextmanager
def acquire_lifecycle_lock_optimized(
    operation_type: str = "lifecycle", custom_timeout: Optional[float] = None
) -> Iterator[bool]:
    """Context manager for acquiring lifecycle lock with environment-optimized timeout.

    Args:
        operation_type: Type of operation ('lifecycle' or 'flush') for timeout selection
        custom_timeout: Optional custom timeout override

    Yields:
        bool: True if lock was acquired, False if timeout occurred

    Examples:
        >>> # Auto-optimized for environment
        >>> with acquire_lifecycle_lock_optimized('lifecycle') as acquired:
        ...     if acquired:
        ...         # Perform lifecycle operation
        ...         pass

        >>> # Custom timeout override
        >>> with acquire_lifecycle_lock_optimized('flush', custom_timeout=5.0) as acq:
        ...     if acq:
        ...         # Perform flush operation
        ...         pass
    """
    if custom_timeout is not None:
        timeout = custom_timeout
    else:
        config = get_lock_config()
        timeout_key = f"{operation_type}_timeout"
        timeout = config.get(timeout_key, config.get("lifecycle_timeout", 1.0))

    acquired = _lifecycle_lock.acquire(timeout=timeout)
    if not acquired:
        yield False
    else:
        try:
            yield True
        finally:
            _lifecycle_lock.release()


def get_lifecycle_lock() -> threading.Lock:
    """Get the global lifecycle lock for external use."""
    return _lifecycle_lock
