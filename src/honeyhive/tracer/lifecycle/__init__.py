"""Tracer lifecycle management for shutdown and cleanup operations.

This module provides comprehensive lifecycle management for HoneyHive tracer
instances, including graceful shutdown, resource cleanup, and proper handling
of multi-instance architectures.

The module is organized into sub-components but maintains a unified public API
for backward compatibility with existing usage patterns.
"""

# Import shutdown detection from logger module (moved to avoid circular imports)
from ...utils.logger import (
    is_shutdown_detected,
)

# Import all public functions to maintain the existing API
from .core import (
    disable_new_span_creation,
    is_new_span_creation_disabled,
    register_tracer_for_atexit_cleanup,
    unregister_tracer_from_atexit_cleanup,
)
from .flush import force_flush_tracer
from .shutdown import graceful_shutdown_all, shutdown_tracer, wait_for_pending_spans

# Maintain the original __all__ exports for backward compatibility
__all__ = [
    "shutdown_tracer",
    "force_flush_tracer",
    "graceful_shutdown_all",
    "register_tracer_for_atexit_cleanup",
    "unregister_tracer_from_atexit_cleanup",
    "is_shutdown_detected",
    "disable_new_span_creation",
    "is_new_span_creation_disabled",
    "wait_for_pending_spans",
]
