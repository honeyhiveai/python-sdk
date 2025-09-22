"""Context management and baggage operations for HoneyHive tracers.

This module handles OpenTelemetry context propagation, baggage management,
and span enrichment functionality. It provides dynamic baggage discovery
and context-aware operations following the multi-instance architecture.
"""

import json
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from opentelemetry import baggage, context, trace
from opentelemetry.context import Context
from opentelemetry.trace import Status, StatusCode

from ...utils.logger import safe_log

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer

# Removed get_config import - using per-instance configuration instead
# No module-level logger - use tracer instance logger


# Config values accessed directly from tracer.config DotDict


def _get_dynamic_experiment_patterns() -> List[str]:
    """Get dynamic experiment patterns that can be extended at runtime.

    :return: List of experiment patterns to search for
    :rtype: List[str]
    """
    # Base patterns - can be extended via configuration
    base_patterns = ["experiment_"]

    # Note: Custom experiment patterns would need to be passed via tracer instance
    # For now, using base patterns only (per-instance configuration approach)
    # This ensures thread safety and avoids global config dependency

    return base_patterns


# Shared logging utility imported at top


def _matches_experiment_pattern(attr_name: str, patterns: List[str]) -> bool:
    """Check if an attribute name matches any experiment pattern.

    :param attr_name: Attribute name to check
    :type attr_name: str
    :param patterns: List of patterns to match against
    :type patterns: List[str]
    :return: True if attribute matches any pattern
    :rtype: bool
    """
    return any(attr_name.startswith(pattern) for pattern in patterns)


def setup_baggage_context(tracer_instance: "HoneyHiveTracer") -> None:
    """Set up baggage with session context for OpenInference integration.

    This function dynamically discovers and sets up baggage items from the
    tracer configuration and environment. It supports experiment harness
    integration and evaluation context propagation.

    :param tracer_instance: The tracer instance to setup baggage for
    :type tracer_instance: HoneyHiveTracer

    **Example:**

    .. code-block:: python

        tracer = HoneyHiveTracer(api_key="key", project="project")
        setup_baggage_context(tracer)
        # Baggage is now available to all spans created by this tracer

    **Note:**

    This function uses dynamic discovery to find all relevant context
    information and automatically sets up baggage for downstream spans.
    It gracefully handles missing or invalid configuration.
    """
    try:
        # Dynamically discover baggage items
        baggage_items = _discover_baggage_items(tracer_instance)

        # Set up baggage context
        _apply_baggage_context(baggage_items, tracer_instance)

        safe_log(
            tracer_instance,
            "debug",
            "Baggage context set up successfully",
            honeyhive_data={
                "baggage_items": list(baggage_items.keys()),
                "item_count": len(baggage_items),
            },
        )

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to set up baggage context",
            honeyhive_data={"error": str(e)},
        )
        # Continue without baggage context - spans will still be processed


def _discover_baggage_items(tracer_instance: "HoneyHiveTracer") -> Dict[str, str]:
    """Dynamically discover all baggage items from tracer and environment.

    :param tracer_instance: The tracer instance to discover baggage from
    :type tracer_instance: HoneyHiveTracer
    :return: Dictionary of baggage key-value pairs
    :rtype: Dict[str, str]
    """
    baggage_items: Dict[str, str] = {}

    # Core tracer context
    _add_core_context(baggage_items, tracer_instance)

    # Evaluation context (backward compatibility)
    _add_evaluation_context(baggage_items, tracer_instance)

    # Experiment harness context
    _add_experiment_context(baggage_items, tracer_instance)

    # Auto-discovery context
    _add_discovery_context(baggage_items, tracer_instance)

    safe_log(
        tracer_instance,
        "debug",
        "Baggage items discovered",
        honeyhive_data={
            "total_items": len(baggage_items),
            "categories": {
                "core": bool(baggage_items.get("project")),
                "evaluation": bool(baggage_items.get("run_id")),
                "experiment": bool(baggage_items.get("experiment_id")),
                "discovery": bool(baggage_items.get("honeyhive_tracer_id")),
            },
        },
    )

    return baggage_items


def _add_core_context(
    baggage_items: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> None:
    """Add core tracer context to baggage items.

    :param baggage_items: Dictionary to add items to
    :type baggage_items: Dict[str, str]
    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    # Session context
    if tracer_instance.session_id:
        baggage_items["session_id"] = tracer_instance.session_id
        safe_log(
            tracer_instance,
            "debug",
            "Session context added to baggage",
            honeyhive_data={"session_id": tracer_instance.session_id},
        )
    else:
        safe_log(tracer_instance, "debug", "No session ID available for baggage")

    # Always set project and source in baggage
    if tracer_instance.project_name:
        baggage_items["project"] = tracer_instance.project_name
    if tracer_instance.source_environment:
        baggage_items["source"] = tracer_instance.source_environment

    safe_log(
        tracer_instance,
        "debug",
        "Core context added to baggage",
        honeyhive_data={
            "project": tracer_instance.project_name,
            "source": tracer_instance.source_environment,
        },
    )


def _add_evaluation_context(
    baggage_items: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> None:
    """Add evaluation-specific context to baggage items (backward compatibility).

    :param baggage_items: Dictionary to add items to
    :type baggage_items: Dict[str, str]
    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    if not tracer_instance.is_evaluation:
        return

    evaluation_items = {}

    if tracer_instance.run_id:
        evaluation_items["run_id"] = tracer_instance.run_id
        baggage_items["run_id"] = tracer_instance.run_id

    if tracer_instance.dataset_id:
        evaluation_items["dataset_id"] = tracer_instance.dataset_id
        baggage_items["dataset_id"] = tracer_instance.dataset_id

    if tracer_instance.datapoint_id:
        evaluation_items["datapoint_id"] = tracer_instance.datapoint_id
        baggage_items["datapoint_id"] = tracer_instance.datapoint_id

    if evaluation_items:
        safe_log(
            tracer_instance,
            "debug",
            "Evaluation context added to baggage",
            honeyhive_data=evaluation_items,
        )


def _add_experiment_context(
    baggage_items: Dict[str, str], tracer_instance: Any = None
) -> None:
    """Add experiment harness context to baggage items using dynamic logic.

    :param baggage_items: Dictionary to add items to
    :type baggage_items: Dict[str, str]
    :param tracer_instance: The tracer instance (for per-instance configuration)
    :type tracer_instance: Optional[HoneyHiveTracer]
    """
    experiment_items = {}

    # Use dynamic configuration extraction for experiment attributes
    experiment_attrs = [
        "experiment_id",
        "experiment_name",
        "experiment_variant",
        "experiment_group",
    ]

    # Handle None tracer instance gracefully
    if not tracer_instance:
        return

    for attr_name in experiment_attrs:
        # Use unified config - direct access to flattened config
        value = tracer_instance.config.get(attr_name)
        if value is not None:
            baggage_items[attr_name] = str(value)
            experiment_items[attr_name] = value

    # Handle experiment metadata using unified config
    experiment_metadata = getattr(
        tracer_instance.config.experiment, "experiment_metadata", None
    )
    if experiment_metadata and isinstance(experiment_metadata, dict):
        for key, value in experiment_metadata.items():
            attr_name = f"experiment_metadata_{key}"
            baggage_items[attr_name] = str(value)
            experiment_items[attr_name] = value

    # Handle experiment metadata JSON serialization using dynamic logic
    if experiment_metadata and isinstance(experiment_metadata, dict):
        try:
            baggage_items["experiment_metadata"] = json.dumps(experiment_metadata)
            experiment_items["experiment_metadata"] = (
                f"JSON({len(experiment_metadata)} items)"
            )
        except Exception:
            # Fallback to string representation
            baggage_items["experiment_metadata"] = str(experiment_metadata)
            experiment_items["experiment_metadata"] = "string format"

    if experiment_items:
        safe_log(
            tracer_instance,
            "debug",
            "Experiment context added to baggage",
            honeyhive_data=experiment_items,
        )


def _add_discovery_context(baggage_items: Dict[str, str], tracer_instance: Any) -> None:
    """Add auto-discovery context to baggage items.

    :param baggage_items: Dictionary to add items to
    :type baggage_items: Dict[str, str]
    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    """
    # Add tracer ID for auto-discovery (backward compatibility)
    tracer_id = getattr(tracer_instance, "_tracer_id", None)
    if tracer_id:
        baggage_items["honeyhive_tracer_id"] = str(tracer_id)
        safe_log(
            tracer_instance,
            "debug",
            "Auto-discovery context added to baggage",
            honeyhive_data={"tracer_id": tracer_id},
        )


def _apply_baggage_context(
    baggage_items: Dict[str, str], tracer_instance: Any = None
) -> None:
    """Apply baggage items to the current OpenTelemetry context.

    DEPRECATED: Use dynamic_baggage_manager.managed_baggage_context() instead
    for better extensibility and context-aware baggage management.

    :param baggage_items: Dictionary of baggage key-value pairs
    :type baggage_items: Dict[str, str]
    """
    if not baggage_items:
        safe_log(tracer_instance, "debug", "No baggage items to apply")
        return

    try:
        # Get current context and apply baggage
        ctx = context.get_current()

        safe_log(
            tracer_instance,
            "debug",
            "🔍 DEBUG: Applying baggage context",
            honeyhive_data={
                "baggage_items": baggage_items,
                "current_context_id": id(ctx),
                "baggage_count": len(baggage_items),
            },
        )

        for key, value in baggage_items.items():
            if value:  # Only set non-empty values
                ctx = baggage.set_baggage(key, str(value), ctx)
                safe_log(
                    tracer_instance,
                    "debug",
                    "🔍 DEBUG: Set baggage %s=%s",
                    key,
                    value,
                    honeyhive_data={
                        "key": key,
                        "value": str(value),
                        "context_id": id(ctx),
                    },
                )

        # Activate the context (disabled for multi-instance architecture)
        # Multi-instance tracers should not set global baggage context
        # as it causes session ID conflicts between tracer instances
        # context.attach(ctx)  # DISABLED: Use tracer-specific session IDs instead

        safe_log(
            tracer_instance,
            "debug",
            "Baggage context applied successfully",
            honeyhive_data={"applied_items": len(baggage_items)},
        )

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to apply baggage context: %s. Continuing without baggage.",
            e,
            honeyhive_data={"baggage_items": list(baggage_items.keys())},
        )
        # Graceful degradation: Continue without baggage context


@contextmanager
def enrich_span_context(  # pylint: disable=too-many-arguments
    span_name: str,
    *,
    attributes: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    project: Optional[str] = None,
    source: Optional[str] = None,
    tracer_instance: Any = None,
) -> Iterator[Any]:
    """Create an enriched span with HoneyHive-specific attributes.

    Note: Multiple positional arguments are required to maintain backward
    compatibility with existing API usage patterns and provide flexibility
    for span enrichment configuration.

    This context manager creates a span with automatic HoneyHive attribute
    enrichment, including session context, experiment information, and
    dynamic attribute discovery.

    :param span_name: Human-readable name for the operation being traced
    :type span_name: str
    :param attributes: Initial attributes to set on the span
    :type attributes: Optional[Dict[str, Any]]
    :param session_id: Optional session ID for the span
    :type session_id: Optional[str]
    :param project: Optional project name for the span
    :type project: Optional[str]
    :param source: Optional source environment for the span
    :type source: Optional[str]
    :return: Context manager yielding the enriched span
    :rtype: Iterator[Any]

    **Example:**

    .. code-block:: python

        with enrich_span_context("user_lookup",
                               attributes={"user.id": "12345"}) as span:
            user = get_user_by_id("12345")
            span.set_attribute("user.found", user is not None)

    **Note:**

    This function automatically adds HoneyHive-specific attributes and
    experiment context to the span. It's used internally by the tracer
    but can also be used directly for custom span creation.
    """
    # Get tracer from tracer instance if available, otherwise use global fallback
    if (
        tracer_instance
        and hasattr(tracer_instance, "tracer")
        and tracer_instance.tracer
    ):
        tracer = tracer_instance.tracer
    else:
        # Fallback for cases where no tracer instance is provided
        tracer = trace.get_tracer("honeyhive.fallback")

    # Prepare enriched attributes
    enriched_attributes = _prepare_enriched_attributes(
        attributes, session_id, project, source, tracer_instance
    )

    # Create and yield span
    with tracer.start_span(span_name, attributes=enriched_attributes) as span:
        try:
            yield span
        except Exception as e:
            # Record exception and re-raise
            if hasattr(span, "record_exception"):
                span.record_exception(e)
            if hasattr(span, "set_status"):
                span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def _prepare_enriched_attributes(
    attributes: Optional[Dict[str, Any]],
    session_id: Optional[str],
    project: Optional[str],
    source: Optional[str],
    tracer_instance: Any = None,
) -> Dict[str, Any]:
    """Prepare enriched attributes for span creation.

    :param attributes: Base attributes to enrich
    :type attributes: Optional[Dict[str, Any]]
    :param session_id: Optional session ID
    :type session_id: Optional[str]
    :param project: Optional project name
    :type project: Optional[str]
    :param source: Optional source environment
    :type source: Optional[str]
    :return: Enriched attributes dictionary
    :rtype: Dict[str, Any]
    """
    enriched_attributes = attributes.copy() if attributes else {}

    # Add HoneyHive core attributes
    if session_id:
        enriched_attributes["honeyhive.session_id"] = session_id
    if project:
        enriched_attributes["honeyhive.project"] = project
    if source:
        enriched_attributes["honeyhive.source"] = source

    # Add tracer version
    enriched_attributes["honeyhive.tracer_version"] = "0.1.0rc2"

    # Add experiment context dynamically
    _add_experiment_attributes(enriched_attributes, tracer_instance)

    safe_log(
        tracer_instance,
        "debug",
        "Span attributes enriched",
        honeyhive_data={
            "base_attributes": len(attributes) if attributes else 0,
            "enriched_attributes": len(enriched_attributes),
            "has_session": bool(session_id),
            "has_experiment": bool(enriched_attributes.get("honeyhive.experiment_id")),
        },
    )

    return enriched_attributes


def _add_experiment_attributes(
    _attributes: Dict[str, Any], tracer_instance: Any = None
) -> None:
    """Add experiment harness attributes to span attributes.

    :param attributes: Attributes dictionary to modify
    :type attributes: Dict[str, Any]
    """
    # Note: Experiment attributes now handled via per-tracer instance baggage context
    # This function is deprecated in favor of baggage-based experiment context
    # For GA: returning empty to avoid global config dependency
    added_attrs: Dict[str, Any] = {}

    # Experiment metadata is now handled via baggage context in per-tracer instances
    # This ensures thread safety and proper isolation

    if added_attrs:
        safe_log(
            tracer_instance,
            "debug",
            "Experiment attributes added to span",
            honeyhive_data=added_attrs,
        )


def get_current_baggage() -> Dict[str, str]:
    """Get all baggage items from the current OpenTelemetry context.

    This function dynamically discovers and returns all baggage items
    from the current context, providing a way to inspect what context
    information is available to spans.

    :return: Dictionary of all baggage key-value pairs
    :rtype: Dict[str, str]

    **Example:**

    .. code-block:: python

        current_baggage = get_current_baggage()
        print(f"Session ID: {current_baggage.get('session_id')}")
        print(f"Project: {current_baggage.get('project')}")

    **Note:**

    This function provides read-only access to the current baggage.
    To modify baggage, use the tracer's baggage management methods.
    """
    try:
        current_baggage = {}
        ctx = context.get_current()

        # Get all baggage items dynamically
        baggage_dict = baggage.get_all(ctx)

        for key, value in baggage_dict.items():
            current_baggage[key] = str(value)

        # Baggage retrieved successfully (removed logging from utility function)

        return current_baggage

    except Exception:
        # Error getting baggage (removed logging from utility function)
        return {}


def inject_context_into_carrier(
    carrier: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> None:
    """Inject OpenTelemetry context into a carrier dictionary.

    This function injects the current OpenTelemetry context (including
    trace context and baggage) into a carrier dictionary for cross-service
    or cross-process propagation.

    :param carrier: Dictionary to inject context into
    :type carrier: Dict[str, str]
    :param tracer_instance: The tracer instance for propagator access
    :type tracer_instance: HoneyHiveTracer

    **Example:**

    .. code-block:: python

        headers = {}
        inject_context_into_carrier(headers, tracer)
        # headers now contains trace context and baggage

        # Use headers in HTTP request
        response = requests.get(url, headers=headers)

    **Note:**

    The carrier dictionary will be modified in-place with context
    information. This is typically used for HTTP headers or message
    metadata in distributed systems.
    """

    try:
        if not tracer_instance.propagator:
            safe_log(
                tracer_instance,
                "warning",
                "No propagator available for context injection",
            )
            return

        # Inject current context into carrier
        tracer_instance.propagator.inject(carrier)

        safe_log(
            tracer_instance,
            "debug",
            "Context injected into carrier",
            honeyhive_data={
                "carrier_keys": list(carrier.keys()),
                "injected_items": len(carrier),
            },
        )

    except Exception as e:
        safe_log(
            tracer_instance,
            "error",
            "Failed to inject context into carrier: %s",
            e,
            honeyhive_data={"carrier_keys": list(carrier.keys())},
        )


def extract_context_from_carrier(
    carrier: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> Optional["Context"]:
    """Extract OpenTelemetry context from a carrier dictionary.

    This function extracts OpenTelemetry context (including trace context
    and baggage) from a carrier dictionary, typically received from another
    service or process.

    :param carrier: Dictionary containing context information
    :type carrier: Dict[str, str]
    :param tracer_instance: The tracer instance for propagator access
    :type tracer_instance: HoneyHiveTracer
    :return: Extracted OpenTelemetry context or None if extraction fails
    :rtype: Optional[Context]

    **Example:**

    .. code-block:: python

        # Extract context from HTTP headers
        extracted_context = extract_context_from_carrier(request.headers, tracer)

        # Use extracted context as parent for new spans
        with tracer.start_span("operation", context=extracted_context) as span:
            # This span will be a child of the remote span
            pass

    **Note:**

    This function is typically used in service endpoints to continue
    distributed traces from upstream services. The extracted context
    can be used as a parent context for new spans.
    """

    try:
        if not tracer_instance.propagator:
            safe_log(
                tracer_instance,
                "warning",
                "No propagator available for context extraction",
            )
            return None

        # Extract context from carrier
        extracted_context: Optional["Context"] = tracer_instance.propagator.extract(
            carrier
        )

        safe_log(
            tracer_instance,
            "debug",
            "Context extracted from carrier",
            honeyhive_data={
                "carrier_keys": list(carrier.keys()),
                "has_context": extracted_context is not None,
            },
        )

        return extracted_context

    except Exception as e:
        safe_log(
            tracer_instance,
            "error",
            "Failed to extract context from carrier: %s",
            e,
            honeyhive_data={"carrier_keys": list(carrier.keys())},
        )
        return None
