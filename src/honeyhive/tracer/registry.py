"""Tracer registry for automatic tracer discovery via OpenTelemetry baggage.

This module provides a lightweight registry system that enables backward-compatible
@trace decorator usage by automatically discovering the appropriate HoneyHiveTracer
instance from OpenTelemetry baggage context.

The registry uses weak references to prevent memory leaks and automatically
cleans up when tracer instances are garbage collected.
"""

# pylint: disable=global-statement,not-callable
# Justification: This module implements a global tracer registry for multi-instance
# support. Global statements are necessary to manage registry state (_TRACER_REGISTRY,
# _DEFAULT_TRACER) and ensure thread-safe operations across the application lifecycle.
# _DEFAULT_TRACER is a weakref.ref object which is callable, but pylint doesn't
# recognize this. Calling _DEFAULT_TRACER() either returns the original tracer object
# or None if it was garbage collected.

import logging
import weakref
from typing import TYPE_CHECKING, Dict, List, Optional

from opentelemetry import baggage, context
from opentelemetry.context import Context

from ..utils.logger import safe_log

if TYPE_CHECKING:
    from .core import HoneyHiveTracer

# Global tracer registry using weak references for automatic cleanup
_TRACER_REGISTRY: "weakref.WeakValueDictionary[str, HoneyHiveTracer]" = (
    weakref.WeakValueDictionary()
)

# Default tracer for global fallback (backward compatibility)
_DEFAULT_TRACER: "Optional[weakref.ReferenceType[HoneyHiveTracer]]" = None

# PYTEST-XDIST COMPATIBLE: Disabled cross-process locks
# _registry_lock = threading.Lock()


def register_tracer(tracer: "HoneyHiveTracer") -> str:
    """Register a tracer instance and return its unique ID.

    Args:
        tracer: HoneyHiveTracer instance to register

    Returns:
        Unique tracer ID for use in baggage context

    Example:
        >>> tracer = HoneyHiveTracer(api_key="your-api-key")  # project from API key
        >>> tracer_id = register_tracer(tracer)
        >>> print(f"Registered tracer with ID: {tracer_id}")
    """
    tracer_id = str(id(tracer))
    # PYTEST-XDIST COMPATIBLE: No cross-process locks needed
    _TRACER_REGISTRY[tracer_id] = tracer
    return tracer_id


def unregister_tracer(tracer_id: str) -> bool:
    """Unregister a tracer instance by ID.

    Args:
        tracer_id: Unique tracer ID to unregister

    Returns:
        True if tracer was found and unregistered, False otherwise

    Note:
        This is typically not needed as the WeakValueDictionary
        automatically cleans up when tracers are garbage collected.
    """
    if tracer_id in _TRACER_REGISTRY:
        del _TRACER_REGISTRY[tracer_id]
        return True
    return False


def get_tracer_from_baggage(
    ctx: Optional["Context"] = None,
) -> "Optional[HoneyHiveTracer]":
    """Discover and return the HoneyHiveTracer instance from baggage context.

    This function looks up the tracer ID from OpenTelemetry baggage and
    returns the corresponding registered tracer instance.

    Args:
        ctx: OpenTelemetry context to read baggage from.
             If None, uses current context.

    Returns:
        HoneyHiveTracer instance if found in baggage and registry,
        None otherwise

    Example:
        >>> # Within a traced context:
        >>> tracer = get_tracer_from_baggage()
        >>> if tracer:
        ...     print(f"Found tracer for project: {tracer.project}")
    """

    try:
        ctx = ctx or context.get_current()
        tracer_id = baggage.get_baggage("honeyhive_tracer_id", ctx)

        if tracer_id:
            if isinstance(tracer_id, str) and tracer_id in _TRACER_REGISTRY:
                tracer = _TRACER_REGISTRY[tracer_id]
                # Debug logging for successful baggage discovery
                if hasattr(tracer, "logger"):
                    safe_log(
                        tracer,
                        "debug",
                        "Tracer discovered from baggage: tracer_id=%s, project=%s",
                        tracer_id,
                        getattr(tracer, "project", "unknown"),
                        honeyhive_data={
                            "tracer_id": tracer_id,
                            "discovery_method": "baggage",
                        },
                    )
                return tracer

    except Exception as e:
        # Log error for debugging but don't crash
        logging.debug("Baggage tracer discovery failed: %s", e)

    return None


def set_default_tracer(tracer: "Optional[HoneyHiveTracer]") -> None:
    """Set a global default tracer for backward compatibility.

    This tracer will be used as a fallback when no tracer is found
    in baggage context and no explicit tracer is provided.

    Args:
        tracer: HoneyHiveTracer instance to use as default,
                or None to clear the default

    Example:
        >>> default_tracer = HoneyHiveTracer(api_key="your-api-key")  # auto project
        >>> set_default_tracer(default_tracer)
        >>>
        >>> # Now @trace will use default_tracer when no context available
        >>> @trace
        ... def my_function():
        ...     pass
    """
    global _DEFAULT_TRACER

    # PYTEST-XDIST COMPATIBLE: No cross-process locks needed
    if tracer is None:
        _DEFAULT_TRACER = None
    else:
        # Register the tracer to ensure it's in the registry
        register_tracer(tracer)
        _DEFAULT_TRACER = weakref.ref(tracer)


def get_default_tracer() -> "Optional[HoneyHiveTracer]":
    """Get the global default tracer if set and still alive.

    Returns:
        Default HoneyHiveTracer instance if set and not garbage collected,
        None otherwise

    Example:
        >>> tracer = get_default_tracer()
        >>> if tracer:
        ...     print(f"Default tracer project: {tracer.project}")
    """
    global _DEFAULT_TRACER

    # PYTEST-XDIST COMPATIBLE: No cross-process locks needed
    if _DEFAULT_TRACER is not None:
        # Weak reference - check if still alive
        tracer = _DEFAULT_TRACER()
        if tracer is not None:
            return tracer
        # Tracer was garbage collected, clear the reference
        _DEFAULT_TRACER = None

    return None


def discover_tracer(
    explicit_tracer: "Optional[HoneyHiveTracer]" = None,
    ctx: Optional["Context"] = None,
) -> "Optional[HoneyHiveTracer]":
    """Discover the appropriate tracer using priority-based fallback.

    This is the main function used by decorators to find the right tracer
    instance using the following priority order:
    1. Explicit tracer parameter (highest priority)
    2. Baggage-discovered tracer (context-aware)
    3. Global default tracer (fallback)

    Args:
        explicit_tracer: Explicitly provided tracer (from decorator parameter)
        ctx: OpenTelemetry context to read baggage from

    Returns:
        HoneyHiveTracer instance using priority fallback, None if none found

    Example:
        >>> # In decorator implementation:
        >>> tracer = discover_tracer(
        ...     explicit_tracer=kwargs.get("tracer"),
        ...     ctx=context.get_current()
        ... )
        >>> if tracer:
        ...     # Use discovered tracer for tracing
        ...     with tracer.start_span("operation") as span:
        ...         # ... tracing logic
    """
    # Priority 1: Explicit tracer parameter
    if explicit_tracer is not None:
        return explicit_tracer

    # Priority 2: Baggage-discovered tracer (context-aware)
    baggage_tracer = get_tracer_from_baggage(ctx)
    if baggage_tracer is not None:
        return baggage_tracer

    # Priority 3: Global default tracer (fallback)
    default_tracer = get_default_tracer()
    if default_tracer is not None:
        return default_tracer

    # No tracer found
    return None


def get_all_tracers() -> List["HoneyHiveTracer"]:
    """Get all registered tracers.

    Returns:
        List of all registered HoneyHiveTracer instances

    Example:
        >>> tracers = get_all_tracers()
        >>> print(f"Found {len(tracers)} active tracers")
    """
    return list(_TRACER_REGISTRY.values())


def get_registry_stats() -> Dict[str, int]:
    """Get statistics about the tracer registry for debugging.

    Returns:
        Dictionary with registry statistics

    Example:
        >>> stats = get_registry_stats()
        >>> print(f"Active tracers: {stats['active_tracers']}")
        >>> print(f"Has default: {stats['has_default_tracer']}")
    """
    return {
        "active_tracers": len(_TRACER_REGISTRY),
        "has_default_tracer": 1 if get_default_tracer() is not None else 0,
    }


def clear_registry() -> None:
    """Clear all registered tracers and default tracer.

    This is primarily useful for testing and cleanup scenarios.

    Warning:
        This will break any ongoing tracing operations that depend
        on auto-discovery. Use with caution.

    Example:
        >>> # In test teardown:
        >>> clear_registry()
    """
    global _DEFAULT_TRACER
    _TRACER_REGISTRY.clear()
    _DEFAULT_TRACER = None
