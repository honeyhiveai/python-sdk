"""Core span enrichment logic with dynamic pattern detection.

This module implements the unified enrichment architecture that supports
multiple invocation patterns while maintaining a single core logic implementation.
Follows Agent OS dynamic logic standards for configuration-driven, extensible systems.

**Backwards Compatibility:**
This module maintains full backwards compatibility with the main branch interface
while adding new functionality. All main branch usage patterns are supported.
"""

# pylint: disable=R0801
# Justification: Shared patterns with test_tracer_instrumentation_enrichment.py
# for parameter normalization and enrichment logic

# Standard library imports
from contextlib import _GeneratorContextManager, contextmanager
from typing import Any, Dict, Iterator, Optional, Union

# Third-party imports
from opentelemetry import context, trace

from ...utils.logger import safe_log
from ..registry import discover_tracer

# Local imports
from .span_utils import _set_span_attributes


# Create a minimal NoOpSpan for graceful degradation
class NoOpSpan:
    """No-op span implementation for graceful degradation."""

    def set_attribute(self, key: str, value: Any) -> None:
        """No-op set_attribute method."""

    def is_recording(self) -> bool:
        """Always returns False for no-op spans."""
        return False


# Removed complex EnrichmentPatternDetector class
# Using simple caller parameter approach instead


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-branches
# Justification: Enrichment requires multiple optional parameters for comprehensive
# span metadata (metadata, metrics, feedback, inputs, outputs, config, etc.).
# Many branches are needed to handle reserved parameters correctly.
def enrich_span_core(  # pylint: disable=too-many-locals
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    user_properties: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Core enrichment logic with namespace support and backwards compatibility.

    This function implements the unified enrichment architecture that supports
    multiple invocation patterns while maintaining backwards compatibility with
    the main branch interface. It routes parameters to proper attribute
    namespaces and handles arbitrary kwargs.

    **Backwards Compatibility:**
    Supports the main branch reserved parameter interface (metadata, metrics,
    feedback, inputs, outputs, config, error, event_id).

    **New Features:**
    - Simple dict via attributes parameter routes to metadata namespace
    - Arbitrary kwargs route to metadata namespace for convenience
    - user_properties routes to honeyhive_user_properties.* namespace

    **Parameter Precedence:**
    When the same key appears in multiple places, merge/override with this order:
    1. Reserved parameters (metadata, metrics, etc.) - Applied first
    2. attributes dict - Applied second
    3. **kwargs - Applied last (wins conflicts)

    :param attributes: Simple dict that routes to metadata namespace
    :type attributes: Optional[Dict[str, Any]]
    :param metadata: Metadata namespace (honeyhive_metadata.*)
    :type metadata: Optional[Dict[str, Any]]
    :param metrics: Metrics namespace (honeyhive_metrics.*)
    :type metrics: Optional[Dict[str, Any]]
    :param feedback: Feedback namespace (honeyhive_feedback.*)
    :type feedback: Optional[Dict[str, Any]]
    :param inputs: Inputs namespace (honeyhive_inputs.*)
    :type inputs: Optional[Dict[str, Any]]
    :param outputs: Outputs namespace (honeyhive_outputs.*)
    :type outputs: Optional[Dict[str, Any]]
    :param config: Config namespace (honeyhive_config.*)
    :type config: Optional[Dict[str, Any]]
    :param user_properties: User properties namespace (honeyhive_user_properties.*)
    :type user_properties: Optional[Dict[str, Any]]
    :param error: Error string (honeyhive_error, non-namespaced)
    :type error: Optional[str]
    :param event_id: Event ID (honeyhive_event_id, non-namespaced)
    :type event_id: Optional[str]
    :param tracer_instance: Optional tracer instance for logging
    :type tracer_instance: Optional[Any]
    :param verbose: Whether to log debug information
    :type verbose: bool
    :param kwargs: Arbitrary kwargs that route to metadata namespace
    :type kwargs: Any
    :return: Enrichment result with success status and span reference
    :rtype: Dict[str, Any]

    **Example:**

    .. code-block:: python

        # Main branch backwards compatible usage
        result = enrich_span_core(
            metadata={"user_id": "123"},
            metrics={"score": 0.95}
        )

        # New simplified usage
        result = enrich_span_core(
            user_id="123",  # Routes to metadata
            feature="chat"  # Routes to metadata
        )

        # User properties usage
        result = enrich_span_core(
            user_properties={"user_id": "user-123", "plan": "premium"},
            metrics={"score": 0.95}
        )

    **Note:**

    This function is thread-safe and uses OpenTelemetry's context
    propagation to access the current span automatically.
    """
    try:
        # Get current span from OpenTelemetry context
        current_span = trace.get_current_span()

        if not current_span or not hasattr(current_span, "set_attribute"):
            safe_log(
                tracer_instance,
                "debug",
                "No active span found or span doesn't support attributes",
            )
            return {"success": False, "span": NoOpSpan(), "error": "No active span"}

        attribute_count: int = 0

        # STEP 1: Apply reserved namespaces first (highest priority)
        # These use _set_span_attributes for recursive dict/list handling
        if metadata:
            _set_span_attributes(current_span, "honeyhive_metadata", metadata)
            attribute_count += len(metadata)

        if metrics:
            _set_span_attributes(current_span, "honeyhive_metrics", metrics)
            attribute_count += len(metrics)

        if feedback:
            _set_span_attributes(current_span, "honeyhive_feedback", feedback)
            attribute_count += len(feedback)

        if inputs:
            safe_log(
                tracer_instance,
                "debug",
                f"Setting inputs on span: {getattr(current_span, 'name', 'unknown')}",
                honeyhive_data={
                    "span_name": getattr(current_span, "name", "unknown"),
                    "inputs": inputs,
                    "span_is_recording": (
                        current_span.is_recording()
                        if hasattr(current_span, "is_recording")
                        else None
                    ),
                },
            )
            _set_span_attributes(current_span, "honeyhive_inputs", inputs)
            attribute_count += len(inputs)
            # Verify attributes were set
            if verbose and hasattr(current_span, "attributes"):
                span_attrs = getattr(current_span, "attributes", {})
                input_attrs = {
                    k: v
                    for k, v in span_attrs.items()
                    if k.startswith("honeyhive_inputs")
                }
                safe_log(
                    tracer_instance,
                    "debug",
                    f"Inputs attributes after setting: {list(input_attrs.keys())}",
                    honeyhive_data={"input_attrs": input_attrs},
                )

        if outputs:
            _set_span_attributes(current_span, "honeyhive_outputs", outputs)
            attribute_count += len(outputs)

        if config:
            _set_span_attributes(current_span, "honeyhive_config", config)
            attribute_count += len(config)

        if user_properties:
            _set_span_attributes(
                current_span, "honeyhive_user_properties", user_properties
            )
            attribute_count += len(user_properties)

        # STEP 2: Apply simple attributes dict → metadata (overwrites conflicts)
        if attributes:
            _set_span_attributes(current_span, "honeyhive_metadata", attributes)
            attribute_count += len(attributes)

        # STEP 3: Apply arbitrary kwargs → metadata (lowest priority, wins conflicts)
        # But exclude reserved parameter names from kwargs
        # Also extract reserved parameters from kwargs if not passed explicitly
        reserved_params = {
            "metadata",
            "metrics",
            "feedback",
            "inputs",
            "outputs",
            "config",
            "user_properties",
            "error",
            "event_id",
            "tracer_instance",
            "verbose",
        }

        # Extract reserved parameters from kwargs if present and not already handled
        # This handles cases where they're passed as kwargs (e.g., from instance method)
        if not metrics and "metrics" in kwargs:
            metrics_from_kwargs = kwargs.pop("metrics")
            if metrics_from_kwargs:
                _set_span_attributes(
                    current_span, "honeyhive_metrics", metrics_from_kwargs
                )
                attribute_count += len(metrics_from_kwargs)

        if not user_properties and "user_properties" in kwargs:
            user_properties_from_kwargs = kwargs.pop("user_properties")
            if user_properties_from_kwargs:
                _set_span_attributes(
                    current_span,
                    "honeyhive_user_properties",
                    user_properties_from_kwargs,
                )
                attribute_count += len(user_properties_from_kwargs)

        if not feedback and "feedback" in kwargs:
            feedback_from_kwargs = kwargs.pop("feedback")
            if feedback_from_kwargs:
                _set_span_attributes(
                    current_span, "honeyhive_feedback", feedback_from_kwargs
                )
                attribute_count += len(feedback_from_kwargs)

        if not inputs and "inputs" in kwargs:
            inputs_from_kwargs = kwargs.pop("inputs")
            if inputs_from_kwargs:
                _set_span_attributes(
                    current_span, "honeyhive_inputs", inputs_from_kwargs
                )
                attribute_count += len(inputs_from_kwargs)

        if not outputs and "outputs" in kwargs:
            outputs_from_kwargs = kwargs.pop("outputs")
            if outputs_from_kwargs:
                _set_span_attributes(
                    current_span, "honeyhive_outputs", outputs_from_kwargs
                )
                attribute_count += len(outputs_from_kwargs)

        if not config and "config" in kwargs:
            config_from_kwargs = kwargs.pop("config")
            if config_from_kwargs:
                _set_span_attributes(
                    current_span, "honeyhive_config", config_from_kwargs
                )
                attribute_count += len(config_from_kwargs)

        kwargs_filtered = {k: v for k, v in kwargs.items() if k not in reserved_params}
        if kwargs_filtered:
            _set_span_attributes(current_span, "honeyhive_metadata", kwargs_filtered)
            attribute_count += len(kwargs_filtered)

        # Handle special non-namespaced attributes
        if error:
            current_span.set_attribute("honeyhive_error", error)
            attribute_count += 1

        if event_id:
            current_span.set_attribute("honeyhive_event_id", event_id)
            attribute_count += 1

        # Log success if verbose mode is enabled
        if verbose:
            safe_log(
                tracer_instance,
                "debug",
                "Span enriched with attributes",
                honeyhive_data={
                    "attribute_count": attribute_count,
                    "span_name": getattr(current_span, "name", "unknown"),
                },
            )

        return {
            "success": True,
            "span": current_span,
            "attribute_count": attribute_count,
        }

    except Exception as e:
        safe_log(
            tracer_instance,
            "error",
            f"Failed to enrich span: {e}",
            honeyhive_data={"error_type": type(e).__name__, "caller": "enrich_span"},
            exc_info=True,
        )
        return {"success": False, "span": NoOpSpan(), "error": str(e)}


class UnifiedEnrichSpan:
    """**LEGACY (v1.0+):** Unified enrich_span that auto-detects invocation pattern.

    .. deprecated:: 1.0
       This free function pattern is provided for backward compatibility only.
       **Use instance methods instead:** ``tracer.enrich_span()``
       This pattern will be removed in v2.0.

    **Recommended Pattern (v1.0+):**
    Use the tracer instance method for explicit tracer reference::

        tracer = HoneyHiveTracer.init(api_key="...", project="...")
        tracer.enrich_span(metadata={'key': 'value'}, metrics={'time_ms': 100})

    This class provides a single entry point for span enrichment that automatically
    detects whether it's being used as a context manager (with statement) or as a
    direct call. It dynamically discovers the active tracer via baggage propagation.

    **Backwards Compatibility:**
    Supports all main branch reserved parameters (metadata, metrics, feedback, etc.)
    Works with evaluate() pattern via baggage-based tracer discovery (v1.0 fix).

    **Legacy Usage Patterns:**
    - Context manager: `with enrich_span(metadata={'key': 'value'}) as span:`
    - Direct call: `success = enrich_span(metadata={'key': 'value'})`
    - Boolean evaluation: `if enrich_span(user_id="123"):`

    See Also:
        - :meth:`HoneyHiveTracer.enrich_span` - Primary pattern (v1.0+)
        - :meth:`HoneyHiveTracer.enrich_session` - Session enrichment
    """

    def __init__(self) -> None:
        """Initialize unified enrich_span instance."""
        self._context_manager: Optional[Any] = None
        self._direct_result: Optional[Any] = None
        self._attributes: Optional[Dict[str, Any]] = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._metrics: Optional[Dict[str, Any]] = None
        self._feedback: Optional[Dict[str, Any]] = None
        self._inputs: Optional[Dict[str, Any]] = None
        self._outputs: Optional[Dict[str, Any]] = None
        self._config: Optional[Dict[str, Any]] = None
        self._error: Optional[str] = None
        self._event_id: Optional[str] = None
        self._tracer: Optional[Any] = None
        self._kwargs: Optional[Dict[str, Any]] = None

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # Justification: Enrichment requires multiple optional parameters for comprehensive
    # span metadata (metadata, metrics, feedback, inputs, outputs, config, etc.).
    def __call__(
        self,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        event_id: Optional[str] = None,
        tracer: Optional[Any] = None,
        **kwargs: Any,
    ) -> "UnifiedEnrichSpan":
        """Called when enrich_span() is invoked.

        Accepts all backwards-compatible parameters and new convenience parameters.
        Returns self to enable both context manager and direct call patterns.

        **IMMEDIATE EXECUTION (v1.0+ fix):**
        The enrichment executes immediately on call to match user expectations:
        ``enrich_span(metadata={'key': 'value'})`` works without explicit evaluation.

        :param attributes: Simple dict that routes to metadata namespace
        :type attributes: Optional[Dict[str, Any]]
        :param metadata: Metadata namespace
        :type metadata: Optional[Dict[str, Any]]
        :param metrics: Metrics namespace
        :type metrics: Optional[Dict[str, Any]]
        :param feedback: Feedback namespace
        :type feedback: Optional[Dict[str, Any]]
        :param inputs: Inputs namespace
        :type inputs: Optional[Dict[str, Any]]
        :param outputs: Outputs namespace
        :type outputs: Optional[Dict[str, Any]]
        :param config: Config namespace
        :type config: Optional[Dict[str, Any]]
        :param error: Error string
        :type error: Optional[str]
        :param event_id: Event ID
        :type event_id: Optional[str]
        :param tracer: Optional tracer instance
        :type tracer: Optional[Any]
        :param kwargs: Arbitrary kwargs routing to metadata
        :type kwargs: Any
        :return: Self for chaining
        :rtype: UnifiedEnrichSpan
        """
        # Store all arguments for later use
        self._attributes = attributes
        self._metadata = metadata
        self._metrics = metrics
        self._feedback = feedback
        self._inputs = inputs
        self._outputs = outputs
        self._config = config
        self._error = error
        self._event_id = event_id
        self._tracer = tracer
        self._kwargs = kwargs
        self._context_manager = None
        self._direct_result = None

        # IMMEDIATE EXECUTION (v1.0+ fix):
        # Execute enrichment immediately to match user expectations
        # Users expect: enrich_span(metadata={...}) to work immediately
        # Not: bool(enrich_span(metadata={...})) or with enrich_span(...):
        self._direct_result = enrich_span_unified(
            attributes=self._attributes,
            metadata=self._metadata,
            metrics=self._metrics,
            feedback=self._feedback,
            inputs=self._inputs,
            outputs=self._outputs,
            config=self._config,
            error=self._error,
            event_id=self._event_id,
            tracer_instance=self._tracer,
            caller="direct_call",
            **(self._kwargs or {}),
        )

        return self

    def __enter__(self) -> Any:
        """Context manager entry - delegates to unified function.

        :return: The span from the context manager
        :rtype: Any
        """
        self._context_manager = enrich_span_unified(
            attributes=self._attributes,
            metadata=self._metadata,
            metrics=self._metrics,
            feedback=self._feedback,
            inputs=self._inputs,
            outputs=self._outputs,
            config=self._config,
            error=self._error,
            event_id=self._event_id,
            tracer_instance=self._tracer,
            caller="context_manager",
            **(self._kwargs or {}),
        )
        if hasattr(self._context_manager, "__enter__"):
            return self._context_manager.__enter__()
        return self._context_manager

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit.

        :param exc_type: Exception type if raised
        :type exc_type: Optional[type]
        :param exc_val: Exception value if raised
        :type exc_val: Optional[BaseException]
        :param exc_tb: Exception traceback if raised
        :type exc_tb: Optional[Any]
        """
        if self._context_manager and hasattr(self._context_manager, "__exit__"):
            self._context_manager.__exit__(exc_type, exc_val, exc_tb)

    def __bool__(self) -> bool:
        """Direct call evaluation - delegates to unified function.

        :return: True if enrichment succeeded
        :rtype: bool
        """
        if self._direct_result is None:
            self._direct_result = enrich_span_unified(
                attributes=self._attributes,
                metadata=self._metadata,
                metrics=self._metrics,
                feedback=self._feedback,
                inputs=self._inputs,
                outputs=self._outputs,
                config=self._config,
                error=self._error,
                event_id=self._event_id,
                tracer_instance=self._tracer,
                caller="direct_call",
                **(self._kwargs or {}),
            )
        return bool(self._direct_result)


# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: Enrichment requires multiple optional parameters for comprehensive
# span metadata (metadata, metrics, feedback, inputs, outputs, config, etc.).
def enrich_span_unified(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    caller: str = "direct_call",
    **kwargs: Any,
) -> Union[bool, _GeneratorContextManager[Any, None, None]]:  # type: ignore[type-arg]
    """Unified enrich_span implementation with backwards compatibility.

    This function implements the unified enrichment architecture with a simple
    caller parameter approach. Each caller explicitly identifies itself, making
    the behavior predictable and following Agent OS dynamic logic standards.

    **Backwards Compatibility:**
    Supports all main branch reserved parameters (metadata, metrics, etc.)

    **Tracer Discovery:**
    If no tracer_instance is provided, automatically discovers tracer using:
    1. Baggage-discovered tracer (context-aware)
    2. Global default tracer (fallback)

    :param attributes: Simple dict that routes to metadata namespace
    :type attributes: Optional[Dict[str, Any]]
    :param metadata: Metadata namespace
    :type metadata: Optional[Dict[str, Any]]
    :param metrics: Metrics namespace
    :type metrics: Optional[Dict[str, Any]]
    :param feedback: Feedback namespace
    :type feedback: Optional[Dict[str, Any]]
    :param inputs: Inputs namespace
    :type inputs: Optional[Dict[str, Any]]
    :param outputs: Outputs namespace
    :type outputs: Optional[Dict[str, Any]]
    :param config: Config namespace
    :type config: Optional[Dict[str, Any]]
    :param error: Error string
    :type error: Optional[str]
    :param event_id: Event ID
    :type event_id: Optional[str]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param caller: Caller identification ('context_manager' or 'direct_call')
    :type caller: str
    :param kwargs: Arbitrary kwargs routing to metadata
    :type kwargs: Any
    :return: Context manager (Iterator) or boolean based on caller
    :rtype: Union[bool, Iterator[Any]]

    **Usage Patterns:**

    .. code-block:: python

        # Context manager pattern - returns Iterator[Any]
        enrich_span_unified(attrs, tracer, caller="context_manager")

        # Direct call pattern - returns bool
        enrich_span_unified(attrs, tracer, caller="direct_call")
    """
    # Discover tracer if not provided (same pattern as trace decorator)
    if tracer_instance is None:
        try:
            current_ctx = context.get_current()
            tracer_instance = discover_tracer(explicit_tracer=None, ctx=current_ctx)
        except Exception as e:
            # Graceful degradation - log but continue
            safe_log(
                None,
                "debug",
                f"Failed to discover tracer: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )

    safe_log(
        tracer_instance,
        "debug",
        f"Enriching span via {caller}",
        honeyhive_data={"caller": caller, "has_attributes": bool(attributes)},
    )

    if caller == "context_manager":
        # Return context manager for 'with' statement usage
        return _enrich_span_context_manager(
            attributes=attributes,
            metadata=metadata,
            metrics=metrics,
            feedback=feedback,
            inputs=inputs,
            outputs=outputs,
            config=config,
            error=error,
            event_id=event_id,
            tracer_instance=tracer_instance,
            **kwargs,
        )
    # Return boolean for direct call and other patterns
    return _enrich_span_direct_call(
        attributes=attributes,
        metadata=metadata,
        metrics=metrics,
        feedback=feedback,
        inputs=inputs,
        outputs=outputs,
        config=config,
        error=error,
        event_id=event_id,
        tracer_instance=tracer_instance,
        **kwargs,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: Enrichment requires multiple optional parameters for comprehensive
# span metadata (metadata, metrics, feedback, inputs, outputs, config, etc.).
@contextmanager
def _enrich_span_context_manager(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> Iterator[Any]:
    """Context manager implementation for enrich_span with backwards compatibility.

    :param attributes: Simple dict that routes to metadata namespace
    :type attributes: Optional[Dict[str, Any]]
    :param metadata: Metadata namespace
    :type metadata: Optional[Dict[str, Any]]
    :param metrics: Metrics namespace
    :type metrics: Optional[Dict[str, Any]]
    :param feedback: Feedback namespace
    :type feedback: Optional[Dict[str, Any]]
    :param inputs: Inputs namespace
    :type inputs: Optional[Dict[str, Any]]
    :param outputs: Outputs namespace
    :type outputs: Optional[Dict[str, Any]]
    :param config: Config namespace
    :type config: Optional[Dict[str, Any]]
    :param error: Error string
    :type error: Optional[str]
    :param event_id: Event ID
    :type event_id: Optional[str]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param kwargs: Arbitrary kwargs routing to metadata
    :type kwargs: Any
    :yield: The current span or NoOpSpan
    :rtype: Iterator[Any]
    """
    # Remove verbose from kwargs if it exists (it's not relevant to span enrichment)
    kwargs_clean = {k: v for k, v in kwargs.items() if k != "verbose"}

    # Execute core enrichment logic with all parameters
    result = enrich_span_core(
        attributes=attributes,
        metadata=metadata,
        metrics=metrics,
        feedback=feedback,
        inputs=inputs,
        outputs=outputs,
        config=config,
        error=error,
        event_id=event_id,
        tracer_instance=tracer_instance,
        verbose=False,
        **kwargs_clean,
    )

    try:
        # Yield the span for context manager usage
        yield result["span"]
    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            f"Error in enrich_span context manager: {e}",
            honeyhive_data={"error_type": type(e).__name__},
        )
        # Don't yield again - just let the exception propagate
        raise


# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: Enrichment requires multiple optional parameters for comprehensive
# span metadata (metadata, metrics, feedback, inputs, outputs, config, etc.).
def _enrich_span_direct_call(
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> bool:
    """Direct call implementation for enrich_span with backwards compatibility.

    :param attributes: Simple dict that routes to metadata namespace
    :type attributes: Optional[Dict[str, Any]]
    :param metadata: Metadata namespace
    :type metadata: Optional[Dict[str, Any]]
    :param metrics: Metrics namespace
    :type metrics: Optional[Dict[str, Any]]
    :param feedback: Feedback namespace
    :type feedback: Optional[Dict[str, Any]]
    :param inputs: Inputs namespace
    :type inputs: Optional[Dict[str, Any]]
    :param outputs: Outputs namespace
    :type outputs: Optional[Dict[str, Any]]
    :param config: Config namespace
    :type config: Optional[Dict[str, Any]]
    :param error: Error string
    :type error: Optional[str]
    :param event_id: Event ID
    :type event_id: Optional[str]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param kwargs: Arbitrary kwargs routing to metadata
    :type kwargs: Any
    :return: True if enrichment succeeded, False otherwise
    :rtype: bool
    """
    # Remove verbose from kwargs if it exists (it's not relevant to span enrichment)
    kwargs_clean = {k: v for k, v in kwargs.items() if k != "verbose"}

    # Execute core enrichment logic with all parameters
    result = enrich_span_core(
        attributes=attributes,
        metadata=metadata,
        metrics=metrics,
        feedback=feedback,
        inputs=inputs,
        outputs=outputs,
        config=config,
        error=error,
        event_id=event_id,
        tracer_instance=tracer_instance,
        verbose=False,
        **kwargs_clean,
    )

    # Return boolean success status
    return bool(result["success"])


# Create the unified enrich_span instance
enrich_span = UnifiedEnrichSpan()
