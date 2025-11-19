"""Decorators for HoneyHive tracing.

This module provides decorators for adding tracing capabilities to functions and
classes.
Uses dynamic logic and reflection to minimize complexity and follow Agent OS standards.

The main :func:`trace` decorator automatically detects function type
or asynchronous and applies the appropriate wrapper. This eliminates the need for
separate sync/async decorators in most cases.

Key Features:
    - Unified :func:`trace` decorator that auto-detects sync/async functions
    - Dynamic attribute management using reflection and mapping
    - Graceful degradation when no tracer is available
    - Class-level tracing with :func:`trace_class`
    - Comprehensive span enrichment with OpenTelemetry integration

Example:
    Basic usage with auto-detection::

        from honeyhive.tracer.decorators import trace

        @trace(event_type="model", event_name="gpt_call")
        def sync_function(prompt: str) -> str:
            return "response"

        @trace(event_type="model", event_name="async_gpt_call")
        async def async_function(prompt: str) -> str:
            return "async response"

    Class-level tracing::

        @trace_class
        class MyService:
            def process_data(self, data):
                return data.upper()

Note:
    This module follows Agent OS standards for graceful degradation. If no tracer
    is available, functions execute normally without tracing rather than raising
    exceptions.

See Also:
    :mod:`honeyhive.tracer.core`: Core tracer implementation
    :mod:`honeyhive.tracer.enrichment_core`: Span enrichment functionality
"""

# pylint: disable=duplicate-code,R0801,import-outside-toplevel,too-many-branches,line-too-long
# Duplicate code patterns here are acceptable architectural patterns:
# 1. Agent OS graceful degradation error handling - consistent across modules
# import-outside-toplevel: Conditional imports avoid circular dependencies
# too-many-branches: Complex decorator logic requires comprehensive branching
# line-too-long: Complex decorator signatures and attribute mappings exceed 88 chars
# 2. Pydantic field validators for OTLP configs - domain-specific but identical logic
# 3. Standard exception logging patterns - architectural consistency for error handling
# 4. Dynamic attribute normalization patterns - shared across decorator and core mixins

import functools
import inspect
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar, Union

from opentelemetry import baggage, context

from ...models.tracing import TracingParams
from ...utils.logger import safe_log
from .. import registry
from ..processing.context import _add_experiment_attributes
from ..utils import convert_enum_to_string
from .enrichment import enrich_span_unified as otel_enrich_span
from .span_utils import _set_span_attributes

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer

T = TypeVar("T")
P = TypeVar("P")


# Dynamic attribute mappings - easily extensible
BASIC_ATTRIBUTES = {
    "event_type": "honeyhive_event_type",
    "event_name": "honeyhive_event_name",
    "event_id": "honeyhive_event_id",
    "source": "honeyhive_source",
    "project": "honeyhive_project",
    "session_id": "honeyhive_session_id",
    "user_id": "honeyhive_user_id",
    "session_name": "honeyhive_session_name",
}

COMPLEX_ATTRIBUTES = {
    "inputs": "honeyhive_inputs",
    "config": "honeyhive_config",
    "metadata": "honeyhive_metadata",
    "metrics": "honeyhive_metrics",
    "feedback": "honeyhive_feedback",
    "outputs": "honeyhive_outputs",
}


def _set_params_attributes(span: Any, params: TracingParams) -> None:
    """Dynamically set all TracingParams attributes using reflection.

    Args:
        span: OpenTelemetry span object to set attributes on
        params: TracingParams object containing attributes to set
    """
    if span is None:
        return

    # Set basic attributes dynamically
    try:
        for param_name, span_attr in BASIC_ATTRIBUTES.items():
            value = getattr(params, param_name, None)
            if value is not None:
                # Convert enum to string if needed (e.g., EventType.model -> "model")
                processed_value = convert_enum_to_string(value)
                if processed_value is not None:
                    span.set_attribute(span_attr, processed_value)
    except Exception:
        pass

    # Set complex attributes dynamically with _raw suffix
    for param_name, span_attr in COMPLEX_ATTRIBUTES.items():
        value = getattr(params, param_name, None)
        if value is not None:
            _set_span_attributes(span, span_attr, value)


def _set_experiment_attributes(span: Any) -> None:
    """Dynamically set experiment attributes from context.

    Args:
        span: OpenTelemetry span object to set attributes on
    """
    if span is None:
        return

    try:
        # Use existing context management functionality
        experiment_attrs: Dict[str, Any] = {}
        _add_experiment_attributes(experiment_attrs)

        # Dynamically set all discovered attributes
        for attr_name, attr_value in experiment_attrs.items():
            try:
                span.set_attribute(attr_name, attr_value)
            except Exception:
                pass
    except Exception:
        pass


def _set_kwargs_attributes(span: Any, **kwargs: Any) -> None:
    """Dynamically process kwargs, excluding reserved keywords.

    Args:
        span: OpenTelemetry span object to set attributes on
        **kwargs: Keyword arguments to process as span attributes
    """
    if span is None:
        return

    # Dynamic reserved keywords - easily extensible
    reserved_keys = {"tracer"}

    for key, value in kwargs.items():
        if key not in reserved_keys and value is not None:
            try:
                _set_span_attributes(span, f"honeyhive_{key}", value)
            except Exception:
                pass


def _capture_function_inputs(
    span: Any, func: Callable, args: tuple, kwargs: Dict[str, Any]
) -> None:
    """Capture function arguments as honeyhive_inputs.* attributes.

    Automatically captures function arguments and sets them as span attributes.
    Skips 'self' and 'cls' parameters.
    Handles serialization errors gracefully.

    Args:
        span: OpenTelemetry span object
        func: Function being traced
        args: Positional arguments
        kwargs: Keyword arguments
    """
    try:
        import json

        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Capture each argument
        for param_name, param_value in bound_args.arguments.items():
            # Skip self/cls parameters
            if param_name in ("self", "cls"):
                continue

            # Skip tracer parameter (to avoid recursion)
            if param_name == "tracer":
                continue

            try:
                # Serialize value safely
                if isinstance(param_value, (str, int, float, bool, type(None))):
                    # Simple types: set directly
                    span.set_attribute(f"honeyhive_inputs.{param_name}", param_value)
                elif isinstance(param_value, (dict, list)):
                    # Complex types: JSON serialize
                    serialized = json.dumps(param_value)
                    # Truncate if too long (prevent huge spans)
                    if len(serialized) > 1000:
                        serialized = serialized[:1000] + "... (truncated)"
                    span.set_attribute(f"honeyhive_inputs.{param_name}", serialized)
                else:
                    # Other types: use str() representation
                    str_value = str(param_value)
                    if len(str_value) > 500:
                        str_value = str_value[:500] + "... (truncated)"
                    span.set_attribute(f"honeyhive_inputs.{param_name}", str_value)
            except Exception:
                # Skip non-serializable values silently
                pass

    except Exception as e:
        # Graceful degradation - don't fail tracing if input capture fails
        safe_log(None, "debug", f"Failed to capture function inputs: {e}")


def _discover_tracer_safely(kwargs: Dict[str, Any], func: Callable) -> Optional[Any]:
    """Discover tracer using priority-based fallback with graceful degradation.

    Args:
        kwargs: Keyword arguments that may contain explicit tracer
        func: Function being decorated (for logging context)

    Returns:
        Discovered tracer instance or None if no tracer available
    """
    try:
        # Use current context for baggage-based tracer discovery
        current_ctx = context.get_current()
        tracer = registry.discover_tracer(
            explicit_tracer=kwargs.get("tracer"), ctx=current_ctx
        )

        if tracer is None:
            safe_log(
                None,  # No tracer available yet - use fallback logging
                "warning",
                "No tracer available for @trace decorator",
                honeyhive_data={
                    "function": f"{func.__module__}.{func.__name__}",
                    "usage_options": [
                        "Use @trace(tracer=my_tracer) with explicit tracer",
                        "Use tracer.start_span() context manager for auto-discovery",
                        "Set a global default with set_default_tracer()",
                    ],
                },
            )
        return tracer
    except Exception:
        return None


def _create_wrapper(
    func: Callable, params: TracingParams, is_async: bool = False, **kwargs: Any
) -> Callable:
    """Create a unified wrapper for both sync and async functions.

    Uses dynamic logic to reduce complexity and eliminate code duplication.

    Args:
        func: Function to be wrapped
        params: Tracing parameters to apply
        is_async: Whether the function is asynchronous
        **kwargs: Additional keyword arguments for tracing

    Returns:
        Wrapped function with tracing capabilities
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **func_kwargs: Any) -> Any:
        return _execute_with_tracing_sync(func, params, args, func_kwargs, kwargs)

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **func_kwargs: Any) -> Any:
        return await _execute_with_tracing(
            func, params, args, func_kwargs, kwargs, is_async=True
        )

    return async_wrapper if is_async else sync_wrapper


def _execute_with_tracing_sync(
    func: Callable,
    params: TracingParams,
    args: tuple,
    func_kwargs: Dict[str, Any],
    decorator_kwargs: Dict[str, Any],
) -> Any:
    """Execute sync function with tracing using dynamic attribute management.

    Synchronous execution logic for sync functions.

    Args:
        func: Function to execute
        params: Tracing parameters
        args: Positional arguments for the function
        func_kwargs: Keyword arguments for the function
        decorator_kwargs: Keyword arguments from the decorator

    Returns:
        Result from the executed function
    """
    # Discover tracer with graceful fallback
    tracer = _discover_tracer_safely(decorator_kwargs, func)
    if tracer is None:
        # Execute function without tracing
        return func(*args, **func_kwargs)

    # Start timing for duration calculation
    start_time = time.time()

    try:
        with tracer.start_span(
            params.event_name or f"{func.__module__}.{func.__name__}"
        ) as span:
            if span is not None:
                # Use dynamic attribute management
                _set_params_attributes(span, params)
                _set_experiment_attributes(span)
                _set_kwargs_attributes(span, **decorator_kwargs)

                # ✅ TASK 4: Auto-capture function inputs
                _capture_function_inputs(span, func, args, func_kwargs)

                # Set up baggage context for multi-instance tracer isolation
                _setup_decorator_baggage_context(tracer, span)

                # Use existing enrichment functionality
                try:
                    # NOTE: enrich_span_unified uses trace.get_current_span()
                    # internally. Do NOT pass span as first argument (would
                    # set honeyhive_metadata to span object)

                    # Build enrichment kwargs, filtering None (defense in depth)
                    # Prevents polluting spans with "null" from json.dumps(None)
                    enrich_kwargs: Dict[str, Any] = {}
                    if params.event_type is not None:
                        enrich_kwargs["event_type"] = params.event_type
                    if params.event_name is not None:
                        enrich_kwargs["event_name"] = params.event_name
                    if params.source is not None:
                        enrich_kwargs["source"] = params.source
                    if params.project is not None:
                        enrich_kwargs["project"] = params.project
                    if params.session_id is not None:
                        enrich_kwargs["session_id"] = params.session_id
                    if params.user_id is not None:
                        enrich_kwargs["user_id"] = params.user_id
                    if params.session_name is not None:
                        enrich_kwargs["session_name"] = params.session_name
                    if params.config is not None:
                        enrich_kwargs["config"] = params.config
                    if params.metadata is not None:
                        enrich_kwargs["metadata"] = params.metadata
                    if params.inputs is not None:
                        enrich_kwargs["inputs"] = params.inputs
                    if params.outputs is not None:
                        enrich_kwargs["outputs"] = params.outputs
                    if params.metrics is not None:
                        enrich_kwargs["metrics"] = params.metrics
                    if params.feedback is not None:
                        enrich_kwargs["feedback"] = params.feedback
                    if params.error is not None:
                        enrich_kwargs["error"] = str(params.error)

                    otel_enrich_span(**enrich_kwargs)
                except Exception:
                    pass

            # Execute the function (sync only)
            safe_log(
                tracer, "debug", f"🔴 DECORATOR: Executing function: {func.__name__}"
            )
            result = func(*args, **func_kwargs)
            safe_log(
                tracer,
                "debug",
                (
                    f"🟡 DECORATOR: Function completed: {func.__name__}, "
                    f"result type: {type(result).__name__}"
                ),
            )

            # Set outputs dynamically
            if span is not None:
                try:
                    if params.outputs:
                        _set_span_attributes(span, "honeyhive_outputs", params.outputs)
                    else:
                        # Use function result as output
                        _set_span_attributes(span, "honeyhive_outputs.result", result)
                except Exception:
                    pass

                # Set duration
                try:
                    duration = (time.time() - start_time) * 1000
                    span.set_attribute("honeyhive_duration_ms", duration)
                except Exception:
                    pass

            safe_log(
                tracer,
                "debug",
                f"🟣 DECORATOR: About to exit context manager for: {func.__name__}",
            )
            return result

    except Exception as e:
        # Graceful error handling
        if "Tracer error" in str(e):
            # Tracer failed, execute function without tracing
            return func(*args, **func_kwargs)

        # Create error span for actual function exceptions
        try:
            duration = (time.time() - start_time) * 1000
            with tracer.start_span(
                f"{params.event_name or func.__name__}_error"
            ) as error_span:
                if error_span is not None:
                    error_span.set_attribute("honeyhive_error", str(e))
                    error_span.set_attribute("honeyhive_error_type", type(e).__name__)
                    error_span.set_attribute("honeyhive_duration_ms", duration)
                    if params.error:
                        error_span.set_attribute("honeyhive_error", str(params.error))
                raise
        except Exception:  # pylint: disable=try-except-raise
            # If error span creation fails, just re-raise original exception
            raise


async def _execute_with_tracing(
    func: Callable,
    params: TracingParams,
    args: tuple,
    func_kwargs: Dict[str, Any],
    decorator_kwargs: Dict[str, Any],
    *,
    is_async: bool = False,
) -> Any:
    """Execute function with tracing using dynamic attribute management.

    Unified execution logic for both sync and async functions.

    Args:
        func: Function to execute
        params: Tracing parameters
        args: Positional arguments for the function
        func_kwargs: Keyword arguments for the function
        decorator_kwargs: Keyword arguments from the decorator
        is_async: Whether to execute as async function

    Returns:
        Result from the executed function
    """
    # Discover tracer with graceful fallback
    tracer = _discover_tracer_safely(decorator_kwargs, func)
    if tracer is None:
        # Execute function without tracing
        if is_async:
            return await func(*args, **func_kwargs)
        return func(*args, **func_kwargs)

    # Start timing for duration calculation
    start_time = time.time()

    try:
        with tracer.start_span(
            params.event_name or f"{func.__module__}.{func.__name__}"
        ) as span:
            if span is not None:
                # Use dynamic attribute management
                _set_params_attributes(span, params)
                _set_experiment_attributes(span)
                _set_kwargs_attributes(span, **decorator_kwargs)

                # ✅ TASK 4: Auto-capture function inputs
                _capture_function_inputs(span, func, args, func_kwargs)

                # Set up baggage context for multi-instance tracer isolation
                _setup_decorator_baggage_context(tracer, span)

                # Use existing enrichment functionality
                try:
                    # NOTE: enrich_span_unified uses trace.get_current_span()
                    # internally. Do NOT pass span as first argument (would
                    # set honeyhive_metadata to span object)

                    # Build enrichment kwargs, filtering None (defense in depth)
                    # Prevents polluting spans with "null" from json.dumps(None)
                    enrich_kwargs: Dict[str, Any] = {}
                    if params.event_type is not None:
                        enrich_kwargs["event_type"] = params.event_type
                    if params.event_name is not None:
                        enrich_kwargs["event_name"] = params.event_name
                    if params.source is not None:
                        enrich_kwargs["source"] = params.source
                    if params.project is not None:
                        enrich_kwargs["project"] = params.project
                    if params.session_id is not None:
                        enrich_kwargs["session_id"] = params.session_id
                    if params.user_id is not None:
                        enrich_kwargs["user_id"] = params.user_id
                    if params.session_name is not None:
                        enrich_kwargs["session_name"] = params.session_name
                    if params.config is not None:
                        enrich_kwargs["config"] = params.config
                    if params.metadata is not None:
                        enrich_kwargs["metadata"] = params.metadata
                    if params.inputs is not None:
                        enrich_kwargs["inputs"] = params.inputs
                    if params.outputs is not None:
                        enrich_kwargs["outputs"] = params.outputs
                    if params.metrics is not None:
                        enrich_kwargs["metrics"] = params.metrics
                    if params.feedback is not None:
                        enrich_kwargs["feedback"] = params.feedback
                    if params.error is not None:
                        enrich_kwargs["error"] = str(params.error)

                    otel_enrich_span(**enrich_kwargs)
                except Exception:
                    pass

            # Execute the function
            if is_async:
                result = await func(*args, **func_kwargs)
            else:
                result = func(*args, **func_kwargs)

            # Set outputs dynamically
            if span is not None:
                try:
                    if params.outputs:
                        _set_span_attributes(span, "honeyhive_outputs", params.outputs)
                    else:
                        # Use function result as output
                        _set_span_attributes(span, "honeyhive_outputs.result", result)
                except Exception:
                    pass

                # Set duration
                try:
                    duration = (time.time() - start_time) * 1000
                    span.set_attribute("honeyhive_duration_ms", duration)
                except Exception:
                    pass

            return result

    except Exception as e:
        # Graceful error handling
        if "Tracer error" in str(e):
            # Tracer failed, execute function without tracing
            if is_async:
                return await func(*args, **func_kwargs)
            return func(*args, **func_kwargs)

        # Create error span for actual function exceptions
        try:
            duration = (time.time() - start_time) * 1000
            with tracer.start_span(
                f"{params.event_name or func.__name__}_error"
            ) as error_span:
                if error_span is not None:
                    error_span.set_attribute("honeyhive_error", str(e))
                    error_span.set_attribute("honeyhive_error_type", type(e).__name__)
                    error_span.set_attribute("honeyhive_duration_ms", duration)
                    if params.error:
                        error_span.set_attribute("honeyhive_error", str(params.error))
                raise
        except Exception as exc:
            # If error tracing fails, just re-raise the original exception
            raise e from exc


def _create_tracing_params(  # pylint: disable=too-many-arguments
    *,
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    event_id: Optional[str] = None,
    source: Optional[str] = None,
    project: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_name: Optional[str] = None,
    span_config: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    tracer: Optional[Any] = None,
) -> TracingParams:
    """Create TracingParams with validation and graceful error handling.

    Args:
        event_type: Type of event being traced
        event_name: Name of the event
        event_id: Unique identifier for the event
        source: Source of the event
        project: Project name
        session_id: Session identifier
        user_id: User identifier
        session_name: Session name
        span_config: Configuration for the span
        metadata: Additional metadata
        inputs: Input parameters
        outputs: Output parameters
        metrics: Performance metrics
        feedback: User feedback
        error: Error information

    Returns:
        TracingParams object with validated parameters
    """
    try:
        return TracingParams(
            event_type=event_type,
            event_name=event_name,
            event_id=event_id,
            source=source,
            project=project,
            session_id=session_id,
            user_id=user_id,
            session_name=session_name,
            config=span_config,
            metadata=metadata,
            inputs=inputs,
            outputs=outputs,
            metrics=metrics,
            feedback=feedback,
            error=error,
            tracer=tracer,
        )
    except Exception as e:
        # Graceful fallback with minimal params
        safe_log(
            tracer, "warning", f"Failed to create TracingParams: {e}. Using defaults."
        )
        return TracingParams(
            event_type=event_type or "unknown",
            event_name=event_name or "unknown_event",
            tracer=tracer,
        )


def trace(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    **kwargs: Any,
) -> Union[Callable[[Callable[..., T]], Callable[..., T]], Callable[..., T]]:
    """Unified trace decorator that auto-detects sync/async functions.

    Automatically detects whether the decorated function is synchronous or
    asynchronous and applies the appropriate wrapper. This decorator can be
    used on both sync and async functions without needing separate decorators.

    Args:
        event_type: Type of event being traced (e.g., "model", "tool", "chain")
        event_name: Name of the event (defaults to function name)
        **kwargs: Additional tracing parameters (source, project, session_id, etc.)

    Returns:
        Decorated function with tracing capabilities

    Example:
        >>> @trace(event_type="model", event_name="gpt_call")
        ... def sync_function():
        ...     return "result"

        >>> @trace(event_type="model", event_name="async_gpt_call")
        ... async def async_function():
        ...     return "async result"
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Auto-detect if function is async
        is_async = inspect.iscoroutinefunction(func)

        # Filter out tracer argument for _create_tracing_params
        tracing_kwargs = {k: v for k, v in kwargs.items() if k != "tracer"}
        params = _create_tracing_params(
            event_type=event_type, event_name=event_name, **tracing_kwargs
        )
        return _create_wrapper(func, params, is_async=is_async, **kwargs)

    # Handle both @trace and @trace() usage patterns
    if event_type is not None and callable(event_type):
        # Used as @trace (without parentheses)
        func = event_type
        is_async = inspect.iscoroutinefunction(func)
        params = _create_tracing_params(event_type="tool")
        return _create_wrapper(func, params, is_async=is_async)

    # Used as @trace(...) (with parentheses)
    return decorator


def atrace(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    **kwargs: Any,
) -> Union[Callable[[Callable[..., Any]], Callable[..., Any]], Callable[..., Any]]:
    """Legacy async-specific trace decorator (deprecated).

    Note:
        This decorator is maintained for backwards compatibility.
        Use the unified :func:`trace` decorator instead, which auto-detects
        sync/async functions.

    Args:
        event_type: Type of event being traced (e.g., "model", "tool", "chain")
        event_name: Name of the event (defaults to function name)
        **kwargs: Additional tracing parameters (source, project, session_id, etc.)

    Returns:
        Decorated async function with tracing capabilities

    See Also:
        :func:`trace`: Unified decorator that handles both sync and async functions
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        params = _create_tracing_params(
            event_type=event_type, event_name=event_name, **kwargs
        )
        return _create_wrapper(func, params, is_async=True, **kwargs)

    # Handle both @atrace and @atrace() usage patterns
    if event_type is not None and callable(event_type):
        # Used as @atrace (without parentheses)
        func = event_type
        params = _create_tracing_params(event_type="tool")
        return _create_wrapper(func, params, is_async=True)

    # Used as @atrace(...) (with parentheses)
    return decorator


def trace_class(cls: type) -> type:
    """Class decorator to automatically trace all public methods.

    Uses dynamic reflection to discover and wrap all public methods of a class.
    Automatically detects sync/async methods and applies appropriate tracing.

    Args:
        cls: The class to be decorated

    Returns:
        The decorated class with all public methods traced

    Example:
        >>> @trace_class
        ... class MyService:
        ...     def process_data(self, data):
        ...         return data.upper()
        ...
        ...     async def async_process(self, data):
        ...         return await some_async_operation(data)
    """
    # Dynamically discover and wrap methods
    for attr_name in dir(cls):
        attr_value = getattr(cls, attr_name)

        # Dynamic method detection
        if (
            callable(attr_value)
            and not attr_name.startswith("_")
            and not isinstance(attr_value, (classmethod, staticmethod))
        ):
            # Determine if method is async
            is_async_method = inspect.iscoroutinefunction(attr_value)

            # Create tracing params for method
            params = _create_tracing_params(
                event_type="tool",
                event_name=f"{cls.__name__}.{attr_name}",
            )

            # Wrap method with appropriate wrapper
            wrapped_method = _create_wrapper(
                attr_value, params, is_async=is_async_method
            )
            setattr(cls, attr_name, wrapped_method)

    return cls


def _setup_decorator_baggage_context(tracer: Any, span: Any) -> None:
    """Set up baggage context for decorator spans to enable context propagation.

    This function sets baggage context within the span context so that
    child operations can access tracer-specific context like session_id.

    Args:
        tracer: HoneyHive tracer instance
        span: OpenTelemetry span to set context for
    """
    try:
        # Get current context
        current_ctx = context.get_current()

        # Set up baggage items from tracer
        baggage_items = {}

        # Add session_id if available
        if hasattr(tracer, "session_id") and tracer.session_id:
            baggage_items["session_id"] = str(tracer.session_id)

        # Add tracer_id if available
        if (
            hasattr(tracer, "_tracer_id")
            and tracer._tracer_id  # pylint: disable=protected-access
        ):
            baggage_items["honeyhive_tracer_id"] = str(
                tracer._tracer_id  # pylint: disable=protected-access
            )

        # Add project if available
        if hasattr(tracer, "project") and tracer.project:
            baggage_items["project"] = str(tracer.project)

        # Add source if available
        if hasattr(tracer, "source") and tracer.source:
            baggage_items["source"] = str(tracer.source)

        # Set baggage in current context, but preserve existing distributed
        # trace baggage
        # Priority: distributed trace context > local tracer defaults
        ctx = current_ctx
        preserved_keys = []
        overridden_keys = []

        for key, value in baggage_items.items():
            if value:
                # Check if key already exists in baggage (from distributed tracing)
                existing_value = baggage.get_baggage(key, ctx)
                if existing_value:
                    # Preserve distributed trace baggage
                    preserved_keys.append(f"{key}={existing_value}")
                else:
                    # Set tracer's value as default
                    ctx = baggage.set_baggage(key, value, ctx)
                    overridden_keys.append(f"{key}={value}")

        # Attach the context (only within the span scope)
        _token = context.attach(ctx)

        safe_log(
            tracer,
            "debug",
            "🔍 DEBUG: Set up decorator baggage context",
            honeyhive_data={
                "span_name": span.name if hasattr(span, "name") else "unknown",
                "baggage_items": baggage_items,
                "preserved_from_distributed_trace": preserved_keys,
                "set_from_tracer_defaults": overridden_keys,
                "tracer_id": id(tracer),
                "context_attached": True,
            },
        )

    except Exception as e:
        safe_log(tracer, "debug", f"Failed to set up decorator baggage context: {e}")
        # Don't fail the decorator if baggage setup fails
