"""Core span enrichment logic with dynamic pattern detection.

This module implements the unified enrichment architecture that supports
multiple invocation patterns while maintaining a single core logic implementation.
Follows Agent OS dynamic logic standards for configuration-driven, extensible systems.
"""

from contextlib import _GeneratorContextManager, contextmanager
from typing import Any, Dict, Iterator, Optional, Union

# Third-party imports
from opentelemetry import trace

# Local imports
from ...utils.logger import safe_log


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


def enrich_span_core(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Core span enrichment logic - unified implementation for all patterns.

    This function implements the core span enrichment logic that is shared
    across all invocation patterns. It follows Agent OS dynamic logic standards
    by providing a single, extensible implementation.

    :param attributes: Attributes to add to the current span
    :type attributes: Optional[Dict[str, Any]]
    :param tracer_instance: Optional tracer instance for logging context
    :type tracer_instance: Optional[Any]
    :param verbose: Whether to log debug information
    :type verbose: bool
    :param kwargs: Additional attributes as keyword arguments
    :type kwargs: Any
    :return: Enrichment result with success status and span reference
    :rtype: Dict[str, Any]
    """
    # Combine attributes and kwargs dynamically
    all_attributes = attributes.copy() if attributes else {}
    all_attributes.update(kwargs)

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

        # Apply attributes to the span
        attribute_count = 0
        for key, value in all_attributes.items():
            try:
                current_span.set_attribute(key, value)
                attribute_count += 1
            except Exception as attr_error:
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Failed to set attribute {key}: {attr_error}",
                )

        # Log success if verbose mode is enabled
        if verbose:
            safe_log(
                tracer_instance,
                "debug",
                "Span enriched with attributes",
                honeyhive_data={
                    "attribute_count": attribute_count,
                    "attributes": list(all_attributes.keys()),
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
            "warning",
            f"Failed to enrich span: {e}",
            honeyhive_data={"error_type": type(e).__name__, "caller": "enrich_span"},
        )
        return {"success": False, "span": NoOpSpan(), "error": str(e)}


class UnifiedEnrichSpan:
    """Unified enrich_span that auto-detects invocation pattern.

    This class provides a single entry point for span enrichment that automatically
    detects whether it's being used as a context manager (with statement) or as a
    direct call, eliminating the need for multiple entry points.

    Usage patterns:
    - Context manager: `with enrich_span({'key': 'value'}) as span:`
    - Direct call: `success = enrich_span({'key': 'value'})`
    - Boolean evaluation: `if enrich_span({'key': 'value'}):`
    """

    def __init__(self) -> None:
        self._context_manager: Optional[Any] = None
        self._direct_result: Optional[Any] = None
        self._attributes: Optional[Dict[str, Any]] = None
        self._tracer: Optional[Any] = None
        self._kwargs: Optional[Dict[str, Any]] = None

    def __call__(
        self,
        attributes: Optional[Dict[str, Any]] = None,
        tracer: Optional[Any] = None,
        **kwargs: Any,
    ) -> "UnifiedEnrichSpan":
        """Called when enrich_span() is invoked.

        Returns self to enable both context manager and direct call patterns.
        """
        # Store arguments for later use
        self._attributes = attributes
        self._tracer = tracer
        self._kwargs = kwargs
        self._context_manager = None
        self._direct_result = None

        return self

    def __enter__(self) -> Any:
        """Context manager entry - delegates to unified function."""
        self._context_manager = enrich_span_unified(
            attributes=self._attributes,
            tracer_instance=self._tracer,
            caller="context_manager",
            **(self._kwargs or {}),
        )
        if hasattr(self._context_manager, "__enter__"):
            return self._context_manager.__enter__()
        return self._context_manager

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self._context_manager and hasattr(self._context_manager, "__exit__"):
            self._context_manager.__exit__(exc_type, exc_val, exc_tb)

    def __bool__(self) -> bool:
        """Direct call evaluation - delegates to unified function."""
        if self._direct_result is None:
            self._direct_result = enrich_span_unified(
                attributes=self._attributes,
                tracer_instance=self._tracer,
                caller="direct_call",
                **(self._kwargs or {}),
            )
        return bool(self._direct_result)


def enrich_span_unified(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    caller: str = "direct_call",
    **kwargs: Any,
) -> Union[bool, _GeneratorContextManager[Any, None, None]]:  # type: ignore[type-arg]
    """Unified enrich_span implementation with simple caller identification.

    This function implements the unified enrichment architecture with a simple
    caller parameter approach. Each caller explicitly identifies itself, making
    the behavior predictable and following Agent OS dynamic logic standards.

    :param attributes: Attributes to add to the current span
    :type attributes: Optional[Dict[str, Any]]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param caller: Caller identification ('context_manager' or 'direct_call')
    :type caller: str
    :param kwargs: Additional attributes as keyword arguments
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
    safe_log(
        tracer_instance,
        "debug",
        f"Enriching span via {caller}",
        honeyhive_data={"caller": caller, "has_attributes": bool(attributes)},
    )

    if caller == "context_manager":
        # Return context manager for 'with' statement usage
        return _enrich_span_context_manager(attributes, tracer_instance, **kwargs)
    # Return boolean for direct call and other patterns
    return _enrich_span_direct_call(attributes, tracer_instance, **kwargs)


@contextmanager
def _enrich_span_context_manager(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> Iterator[Any]:
    """Context manager implementation for enrich_span.

    :param attributes: Attributes to add to the current span
    :type attributes: Optional[Dict[str, Any]]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param kwargs: Additional attributes as keyword arguments
    :type kwargs: Any
    :yield: The current span or NoOpSpan
    :rtype: Iterator[Any]
    """
    # Remove verbose from kwargs if it exists (it's not relevant to span enrichment)
    kwargs_clean = {k: v for k, v in kwargs.items() if k != "verbose"}

    # Execute core enrichment logic (verbose=False since it's not used in enrichment)
    result = enrich_span_core(attributes, tracer_instance, False, **kwargs_clean)

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


def _enrich_span_direct_call(
    attributes: Optional[Dict[str, Any]] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> bool:
    """Direct call implementation for enrich_span.

    :param attributes: Attributes to add to the current span
    :type attributes: Optional[Dict[str, Any]]
    :param tracer_instance: Optional tracer instance for context
    :type tracer_instance: Optional[Any]
    :param kwargs: Additional attributes as keyword arguments
    :type kwargs: Any
    :return: True if enrichment succeeded, False otherwise
    :rtype: bool
    """
    # Remove verbose from kwargs if it exists (it's not relevant to span enrichment)
    kwargs_clean = {k: v for k, v in kwargs.items() if k != "verbose"}

    # Execute core enrichment logic (verbose=False since it's not used in enrichment)
    result = enrich_span_core(attributes, tracer_instance, False, **kwargs_clean)

    # Return boolean success status
    return bool(result["success"])


# Create the unified enrich_span instance
enrich_span = UnifiedEnrichSpan()
