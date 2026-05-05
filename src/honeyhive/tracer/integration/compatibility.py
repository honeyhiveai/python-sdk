"""Dynamic backward compatibility functions for the refactored tracer module.

This module provides global functions that maintain backward compatibility
with the original API while using the new modular tracer architecture.
All compatibility functions use dynamic discovery and fallback patterns.
"""

from typing import Any, Dict, Optional

from opentelemetry import baggage, context, trace

# Import shared logging utility
from ...utils.logger import safe_log
from ..registry import get_default_tracer


def enrich_session(
    session_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    tracer: Optional[Any] = None,
    tracer_instance: Optional[Any] = None,
) -> None:
    """**LEGACY (v1.0+):** Dynamically enrich session with metadata.

    .. deprecated:: 1.0
       This free function pattern is provided for backward compatibility only.
       **Use instance methods instead:** ``tracer.enrich_session()``
       This pattern will be removed in v2.0.

    **Recommended Pattern (v1.0+):**
    Use the tracer instance method for explicit tracer reference::

        tracer = HoneyHiveTracer.init(api_key="...", project="...")
        tracer.enrich_session(
            metadata={"user_id": "user-456"},
            user_properties={"plan": "premium"}
        )

    This function provides backward compatibility for the global enrich_session
    function using dynamic tracer discovery and flexible metadata handling.

    Args:
        session_id: The session ID to enrich
        metadata: Metadata dictionary to add to the session
        tracer: Optional tracer instance to use
        tracer_instance: Optional tracer instance for logging context

    Legacy Example:
        >>> # Using default tracer (backward compatibility)
        >>> enrich_session("session-123", {"user_id": "user-456"})
        >>>
        >>> # Using specific tracer (backward compatibility)
        >>> enrich_session("session-123", {"user_id": "user-456"}, tracer=my_tracer)

    See Also:
        - :meth:`HoneyHiveTracer.enrich_session` - Primary pattern (v1.0+)
        - :meth:`HoneyHiveTracer.enrich_span` - Span enrichment
    """
    # Dynamic tracer discovery
    active_tracer = _discover_tracer_dynamically(tracer, tracer_instance)

    if active_tracer is None:
        safe_log(
            tracer_instance,
            "warning",
            "No tracer available for session enrichment",
            honeyhive_data={
                "session_id": session_id,
                "metadata_keys": list(metadata.keys()) if metadata else [],
            },
        )
        return

    # Dynamic session enrichment
    try:
        _enrich_session_dynamically(
            active_tracer, session_id, metadata, tracer_instance
        )

        safe_log(
            tracer_instance,
            "debug",
            "Session enriched successfully",
            honeyhive_data={
                "session_id": session_id,
                "tracer_type": type(active_tracer).__name__,
                "metadata_count": len(metadata) if metadata else 0,
            },
        )

    except Exception as e:
        safe_log(
            tracer_instance,
            "error",
            "Failed to enrich session",
            honeyhive_data={
                "session_id": session_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
    return


def _discover_tracer_dynamically(
    explicit_tracer: Optional[Any], tracer_instance: Optional[Any] = None
) -> Optional[Any]:
    """Dynamically discover appropriate tracer using fallback strategy.

    Args:
        explicit_tracer: Explicitly provided tracer

    Returns:
        Discovered tracer instance or None
    """
    # Dynamic tracer discovery strategies
    discovery_strategies = [
        explicit_tracer,  # Explicit tracer (highest priority)
        get_default_tracer,  # Default tracer from registry
        lambda: _discover_from_context_dynamically(
            tracer_instance
        ),  # Context-based discovery
    ]

    # Apply discovery strategies dynamically
    for strategy in discovery_strategies:
        try:
            if callable(strategy):
                tracer = strategy()
            else:
                tracer = strategy
            if tracer is not None:
                return tracer
        except Exception as e:
            safe_log(
                tracer_instance,
                "debug",
                "Tracer discovery strategy failed",
                honeyhive_data={
                    "strategy": getattr(strategy, "__name__", "unknown"),
                    "error": str(e),
                },
            )
            continue

    return None


# pylint: disable=useless-return
def _discover_from_context_dynamically(
    tracer_instance: Optional[Any] = None, ctx: Optional[Any] = None
) -> Optional[Any]:
    """Dynamically discover tracer from OpenTelemetry context.

    Args:
        tracer_instance: Optional tracer instance for logging
        ctx: Optional context to use, defaults to current context

    Returns:
        Tracer from context or None
    """
    try:
        # Dynamic context-based discovery patterns
        # Check for tracer ID in baggage - use provided context or current
        current_context = ctx if ctx is not None else context.get_current()
        tracer_id = baggage.get_baggage("honeyhive_tracer_id", current_context)

        if tracer_id:
            # Try to resolve tracer from registry (not implemented yet)
            safe_log(
                tracer_instance,
                "debug",
                "Found tracer ID in baggage but registry lookup not implemented",
                honeyhive_data={"tracer_id": tracer_id},
            )

    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Context-based tracer discovery failed",
            honeyhive_data={"error": str(e)},
        )

    return None


def _enrich_session_dynamically(
    _tracer: Any,
    session_id: str,
    metadata: Optional[Dict[str, Any]],
    tracer_instance: Optional[Any] = None,
) -> None:
    """Dynamically enrich session using available tracer methods.

    Args:
        _tracer: Tracer instance to use
        session_id: Session ID to enrich
        metadata: Metadata to add
        tracer_instance: Optional tracer instance for logging
    """
    if metadata is None:
        metadata = {}

    # Try direct method first with backwards compatible signature
    try:
        if hasattr(_tracer, "enrich_session"):
            # Call with session_id and metadata parameters for backwards compatibility
            _tracer.enrich_session(session_id=session_id, metadata=metadata)
            return
    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Direct session enrichment failed",
            honeyhive_data={"error": str(e)},
        )

    # Try baggage method
    try:
        _enrich_via_baggage_dynamically(_tracer, session_id, metadata, tracer_instance)
        return
    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Baggage session enrichment failed",
            honeyhive_data={"error": str(e)},
        )

    # Try attributes method
    try:
        _enrich_via_attributes_dynamically(
            _tracer, session_id, metadata, tracer_instance
        )
        return
    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Attributes session enrichment failed",
            honeyhive_data={"error": str(e)},
        )

    # If all methods failed, log warning
    safe_log(
        tracer_instance,
        "warning",
        "All session enrichment methods failed",
        honeyhive_data={
            "session_id": session_id,
            "tracer_type": type(_tracer).__name__,
            "available_methods": [
                attr
                for attr in dir(_tracer)
                if "session" in attr.lower() or "enrich" in attr.lower()
            ],
        },
    )


def _enrich_via_baggage_dynamically(
    _tracer: Any,
    session_id: str,
    metadata: Dict[str, Any],
    _tracer_instance: Optional[Any] = None,
    ctx: Optional[Any] = None,
) -> None:
    """Dynamically enrich session via OpenTelemetry baggage.

    Args:
        tracer: Tracer instance
        session_id: Session ID
        metadata: Metadata to add
        tracer_instance: Optional tracer instance for logging
        ctx: Optional context to use, defaults to current context
    """
    # Set session metadata in baggage - use provided context or current
    current_context = ctx if ctx is not None else context.get_current()

    # Dynamic baggage key generation
    baggage_updates = {
        "honeyhive_session_id": session_id,
    }

    # Add metadata with prefixes
    for key, value in metadata.items():
        baggage_key = f"honeyhive_session_{key}"
        baggage_updates[baggage_key] = str(value)

    # Apply baggage updates dynamically
    updated_context = current_context
    for key, value in baggage_updates.items():
        updated_context = baggage.set_baggage(key, value, updated_context)

    # Attach updated context
    context.attach(updated_context)


def _enrich_via_attributes_dynamically(
    _tracer: Any,
    session_id: str,
    metadata: Dict[str, Any],
    tracer_instance: Optional[Any] = None,
) -> None:
    """Dynamically enrich session via span attributes.

    Args:
        tracer: Tracer instance
        session_id: Session ID
        metadata: Metadata to add
    """
    # Get current span
    current_span = trace.get_current_span()

    if current_span and hasattr(current_span, "set_attribute"):
        # Dynamic attribute setting
        attribute_updates = {
            "honeyhive.session_id": session_id,
        }

        # Add metadata as attributes
        for key, value in metadata.items():
            attribute_key = f"honeyhive.session.{key}"
            attribute_updates[attribute_key] = str(value)

        # Apply attribute updates dynamically
        for key, value in attribute_updates.items():
            try:
                current_span.set_attribute(key, value)
            except Exception as e:
                safe_log(
                    tracer_instance,
                    "debug",
                    "Failed to set span attribute",
                    honeyhive_data={
                        "attribute_key": key,
                        "error": str(e),
                    },
                )


def get_compatibility_info() -> Dict[str, Any]:
    """Get dynamic compatibility information.

    Returns:
        Dictionary with compatibility status and available features
    """
    # Dynamic compatibility assessment
    compatibility_info = {
        "backward_compatibility": True,
        "available_functions": ["enrich_session"],
        "tracer_discovery": {
            "explicit_tracer": True,
            "default_tracer": True,
            "context_based": True,
        },
        "enrichment_methods": {
            "direct_method": True,
            "baggage_method": True,
            "attribute_method": True,
        },
    }

    # Dynamic feature detection
    try:
        default_tracer = get_default_tracer()
        compatibility_info["default_tracer_available"] = default_tracer is not None

        if default_tracer:
            compatibility_info["default_tracer_type"] = type(default_tracer).__name__
            compatibility_info["default_tracer_methods"] = [
                method
                for method in dir(default_tracer)
                if not method.startswith("_")
                and callable(getattr(default_tracer, method))
            ]
    except Exception as e:
        compatibility_info["default_tracer_available"] = False
        compatibility_info["default_tracer_error"] = str(e)

    return compatibility_info
