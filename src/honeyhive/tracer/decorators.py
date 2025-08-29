"""Decorators for HoneyHive tracing."""

import functools
import inspect
import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from opentelemetry import trace as otel_trace

from ..models.tracing import TracingParams
from ..utils.config import config
from .otel_tracer import get_tracer

T = TypeVar("T")
P = TypeVar("P")


def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    """Set span attributes with proper type handling and JSON serialization.

    Recursively sets span attributes for complex data structures, handling
    different data types appropriately for OpenTelemetry compatibility.

    Args:
        span: OpenTelemetry span object
        prefix: Attribute name prefix
        value: Value to set as attribute
    """
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _set_span_attributes(span, f"{prefix}.{i}", v)
    elif isinstance(value, (bool, float, int, str)):
        span.set_attribute(prefix, value)
    else:
        # Convert complex types to JSON strings for OpenTelemetry compatibility
        try:
            span.set_attribute(prefix, json.dumps(value, default=str))
        except (TypeError, ValueError):
            # Fallback to string representation if JSON serialization fails
            span.set_attribute(prefix, str(value))


def _create_sync_wrapper(
    func: Callable[..., T], params: TracingParams, **kwargs: Any
) -> Callable[..., T]:
    """Create a synchronous wrapper for the trace decorator.

    Wraps a synchronous function with tracing capabilities, creating spans
    and setting attributes based on the provided parameters.

    Args:
        func: Function to wrap
        params: Tracing parameters and configuration
        **kwargs: Additional tracing options

    Returns:
        Wrapped function with tracing capabilities
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **func_kwargs: Any) -> T:
        """Wrapper function that adds tracing capabilities to the decorated function.

        Args:
            *args: Positional arguments passed to the function
            **func_kwargs: Keyword arguments passed to the function

        Returns:
            The result of the decorated function execution
        """
        # Get tracer instance
        try:
            tracer = get_tracer()
            if tracer is None:
                # If no tracer is available, just call the function
                return func(*args, **func_kwargs)
        except Exception:
            # If tracer is not available, just call the function
            return func(*args, **func_kwargs)

        # Start timing for duration calculation
        start_time = time.time()

        try:
            with tracer.start_span(
                params.event_name or f"{func.__module__}.{func.__name__}"
            ) as span:
                if span is not None:
                    # Set comprehensive attributes
                    if params.event_type:
                        span.set_attribute("honeyhive_event_type", params.event_type)

                    if params.event_name:
                        span.set_attribute("honeyhive_event_name", params.event_name)

                    if params.event_id:
                        span.set_attribute("honeyhive_event_id", params.event_id)

                    # Set inputs if provided
                    if params.inputs:
                        _set_span_attributes(span, "honeyhive_inputs", params.inputs)

                    # Set config if provided
                    if params.config:
                        _set_span_attributes(span, "honeyhive_config", params.config)

                    # Set metadata if provided
                    if params.metadata:
                        _set_span_attributes(
                            span, "honeyhive_metadata", params.metadata
                        )

                    # Set metrics if provided
                    if params.metrics:
                        _set_span_attributes(span, "honeyhive_metrics", params.metrics)

                    # Set feedback if provided
                    if params.feedback:
                        _set_span_attributes(
                            span, "honeyhive_feedback", params.feedback
                        )

                    # Add experiment harness information if available
                    try:
                        if config.experiment_id:
                            span.set_attribute(
                                "honeyhive_experiment_id", config.experiment_id
                            )

                        if config.experiment_name:
                            span.set_attribute(
                                "honeyhive_experiment_name",
                                config.experiment_name,
                            )

                        if config.experiment_variant:
                            span.set_attribute(
                                "honeyhive_experiment_variant",
                                config.experiment_variant,
                            )

                        if config.experiment_group:
                            span.set_attribute(
                                "honeyhive_experiment_group",
                                config.experiment_group,
                            )

                        # Extract experiment metadata if available
                        if config.experiment_metadata and isinstance(
                            config.experiment_metadata, dict
                        ):
                            experiment_id = config.experiment_metadata.get(
                                "experiment_id"
                            )
                            if experiment_id:
                                span.set_attribute(
                                    "honeyhive.experiment.id", experiment_id
                                )

                            experiment_name = config.experiment_metadata.get(
                                "experiment_name"
                            )
                            if experiment_name:
                                span.set_attribute(
                                    "honeyhive.experiment.name", experiment_name
                                )

                            experiment_variant = config.experiment_metadata.get(
                                "experiment_variant"
                            )
                            if experiment_variant:
                                span.set_attribute(
                                    "honeyhive.experiment.variant", experiment_variant
                                )
                    except Exception:
                        # Silently handle any exceptions when setting experiment attributes
                        pass

                    # Set additional kwargs as attributes
                    for key, value in kwargs.items():
                        span.set_attribute(f"honeyhive_{key}", value)

                # Execute the function
                result = func(*args, **func_kwargs)

                # Set outputs if provided or use function result
                if span is not None and params.outputs:
                    try:
                        _set_span_attributes(span, "honeyhive_outputs", params.outputs)
                    except Exception:
                        # Silently handle any exceptions when setting span attributes
                        pass
                elif span is not None:
                    # Try to set function result as output, handle all exceptions silently
                    try:
                        span.set_attribute(
                            "honeyhive_outputs.result", json.dumps(result, default=str)
                        )
                    except Exception:
                        try:
                            span.set_attribute("honeyhive_outputs.result", str(result))
                        except Exception:
                            # Silently handle any exceptions when setting span attributes
                            pass

                return result

        except Exception as e:
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Create error span
            try:
                with tracer.start_span(
                    f"{params.event_name or f'{func.__module__}.{func.__name__}'}_error"
                ) as error_span:
                    if error_span is not None:
                        error_span.set_attribute("honeyhive_error", str(e))
                        error_span.set_attribute(
                            "honeyhive_error_type", type(e).__name__
                        )
                        error_span.set_attribute("honeyhive_duration_ms", duration)

                        # Set error context
                        if params.error:
                            error_span.set_attribute(
                                "honeyhive_error", str(params.error)
                            )
                        else:
                            error_span.set_attribute("honeyhive_error", str(e))

                    # Re-raise the exception
                    raise
            except Exception:
                # If error tracing fails, just re-raise the original exception
                raise e

    return wrapper


def _create_async_wrapper(
    func: Callable[..., Any], params: TracingParams, **kwargs: Any
) -> Callable[..., Any]:
    """Create an asynchronous wrapper for the trace decorator."""

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **func_kwargs: Any) -> Any:
        """Async wrapper function that adds tracing capabilities to the decorated async function.

        Args:
            *args: Positional arguments passed to the function
            **func_kwargs: Keyword arguments passed to the function

        Returns:
            The result of the decorated async function execution
        """
        # Get tracer instance
        try:
            tracer = get_tracer()
            if tracer is None:
                # If no tracer is available, just call the function
                return await func(*args, **func_kwargs)
        except Exception:
            # If tracer is not available, just call the function
            return await func(*args, **func_kwargs)

        # Start timing for duration calculation
        start_time = time.time()

        try:
            with tracer.start_span(
                params.event_name or f"{func.__module__}.{func.__name__}"
            ) as span:
                if span is not None:
                    # Set comprehensive attributes
                    if params.event_type:
                        span.set_attribute("honeyhive_event_type", params.event_type)

                    if params.event_name:
                        span.set_attribute("honeyhive_event_name", params.event_name)

                    if params.event_id:
                        span.set_attribute("honeyhive_event_id", params.event_id)

                    # Set inputs if provided
                    if params.inputs:
                        _set_span_attributes(span, "honeyhive_inputs", params.inputs)

                    # Set config if provided
                    if params.config:
                        _set_span_attributes(span, "honeyhive_config", params.config)

                    # Set metadata if provided
                    if params.metadata:
                        _set_span_attributes(
                            span, "honeyhive_metadata", params.metadata
                        )

                    # Set metrics if provided
                    if params.metrics:
                        _set_span_attributes(span, "honeyhive_metrics", params.metrics)

                    # Set feedback if provided
                    if params.feedback:
                        _set_span_attributes(
                            span, "honeyhive_feedback", params.feedback
                        )

                    # Add experiment harness information if available
                    try:
                        if config.experiment_id:
                            span.set_attribute(
                                "honeyhive_experiment_id", config.experiment_id
                            )

                        if config.experiment_name:
                            span.set_attribute(
                                "honeyhive_experiment_name",
                                config.experiment_name,
                            )

                        if config.experiment_variant:
                            span.set_attribute(
                                "honeyhive_experiment_variant",
                                config.experiment_variant,
                            )

                        if config.experiment_group:
                            span.set_attribute(
                                "honeyhive_experiment_group",
                                config.experiment_group,
                            )

                        # Extract experiment metadata if available
                        if config.experiment_metadata and isinstance(
                            config.experiment_metadata, dict
                        ):
                            experiment_id = config.experiment_metadata.get(
                                "experiment_id"
                            )
                            if experiment_id:
                                span.set_attribute(
                                    "honeyhive.experiment.id", experiment_id
                                )

                            experiment_name = config.experiment_metadata.get(
                                "experiment_name"
                            )
                            if experiment_name:
                                span.set_attribute(
                                    "honeyhive.experiment.name", experiment_name
                                )

                            experiment_variant = config.experiment_metadata.get(
                                "experiment_variant"
                            )
                            if experiment_variant:
                                span.set_attribute(
                                    "honeyhive.experiment.variant", experiment_variant
                                )
                    except Exception:
                        # Silently handle any exceptions when setting experiment attributes
                        pass

                    # Set additional kwargs as attributes
                    for key, value in kwargs.items():
                        span.set_attribute(f"honeyhive_{key}", value)

                # Execute the async function
                result = await func(*args, **func_kwargs)

                # Set outputs if provided or use function result
                if span is not None and params.outputs:
                    try:
                        _set_span_attributes(span, "honeyhive_outputs", params.outputs)
                    except Exception:
                        # Silently handle any exceptions when setting span attributes
                        pass
                elif span is not None:
                    # Try to set function result as output, handle all exceptions silently
                    try:
                        span.set_attribute(
                            "honeyhive_outputs.result", json.dumps(result, default=str)
                        )
                    except Exception:
                        try:
                            span.set_attribute("honeyhive_outputs.result", str(result))
                        except Exception:
                            # Silently handle any exceptions when setting span attributes
                            pass

                return result

        except Exception as e:
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Create error span
            try:
                with tracer.start_span(
                    f"{params.event_name or f'{func.__module__}.{func.__name__}'}_error"
                ) as error_span:
                    if error_span is not None:
                        error_span.set_attribute("honeyhive_error", str(e))
                        error_span.set_attribute(
                            "honeyhive_error_type", type(e).__name__
                        )
                        error_span.set_attribute("honeyhive_duration_ms", duration)

                        # Set error context
                        if params.error:
                            error_span.set_attribute(
                                "honeyhive_error", str(params.error)
                            )
                        else:
                            error_span.set_attribute("honeyhive_error", str(e))

                    # Re-raise the exception
                    raise
            except Exception:
                # If error tracing fails, just re-raise the original exception
                raise e

    return async_wrapper


def trace(
    event_type: Union[Optional[str], Callable] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Enhanced trace decorator with comprehensive attribute support.

    Args:
        event_type: Type of traced event (e.g., 'model', 'tool', 'chain')
        event_name: Name of the traced event
        inputs: Input data for the event
        outputs: Output data for the event
        metadata: Additional metadata
        config: Configuration data
        metrics: Performance metrics
        feedback: User feedback
        error: Error information
        event_id: Unique event identifier
        **kwargs: Additional attributes to set on the span
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Validate parameters using Pydantic model
        try:
            params = TracingParams(
                event_type=(
                    event_type if isinstance(event_type, (str, type(None))) else None
                ),
                event_name=event_name,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                config=config,
                metrics=metrics,
                feedback=feedback,
                error=error,
                event_id=event_id,
            )
        except Exception as e:
            # If validation fails, log the error but continue with default values
            logging.warning(f"Tracing parameter validation failed: {e}")
            params = TracingParams()

        return _create_sync_wrapper(func, params, **kwargs)

    # Handle both @trace and @trace(...) usage
    if callable(event_type):
        # Used as @trace
        return decorator(event_type)
    else:
        # Used as @trace(...)
        return decorator


def atrace(
    event_type: Union[Optional[str], Callable] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Enhanced async trace decorator with comprehensive attribute support.

    Args:
        event_type: Type of traced event (e.g., 'model', 'tool', 'chain')
        event_name: Name of the traced event
        inputs: Input data for the event
        outputs: Output data for the event
        metadata: Additional metadata
        config: Configuration data
        metrics: Performance metrics
        feedback: User feedback
        error: Error information
        event_id: Unique event identifier
        **kwargs: Additional attributes to set on the span
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Validate parameters using Pydantic model
        try:
            params = TracingParams(
                event_type=(
                    event_type if isinstance(event_type, (str, type(None))) else None
                ),
                event_name=event_name,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                config=config,
                metrics=metrics,
                feedback=feedback,
                error=error,
                event_id=event_id,
            )
        except Exception as e:
            # If validation fails, log the error but continue with default values
            logging.warning(f"Tracing parameter validation failed: {e}")
            params = TracingParams()

        return _create_async_wrapper(func, params, **kwargs)

    # Handle both @atrace and @atrace(...) usage
    if callable(event_type):
        # Used as @atrace
        return decorator(event_type)
    else:
        # Used as @atrace(...)
        return decorator


def trace_class(
    event_type: Optional[str] = None, event_name: Optional[str] = None, **kwargs: Any
) -> Callable[[type], type]:
    """
    Enhanced class decorator for tracing all methods of a class.

    Args:
        event_type: Type of traced events
        event_name: Name prefix for traced events
        **kwargs: Additional attributes to set on all spans
    """

    def decorator(cls: type) -> type:
        # Get all methods of the class
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)

            # Only trace methods (not properties, class methods, etc.)
            if (
                inspect.isfunction(attr_value)
                and not attr_name.startswith("_")
                and attr_name not in ["__init__", "__new__"]
            ):

                # Create a traced version of the method
                if inspect.iscoroutinefunction(attr_value):
                    # Async method
                    traced_method = atrace(
                        event_type=event_type,
                        event_name=f"{event_name or cls.__name__}.{attr_name}",
                        **kwargs,
                    )(attr_value)
                else:
                    # Sync method
                    traced_method = trace(
                        event_type=event_type,
                        event_name=f"{event_name or cls.__name__}.{attr_name}",
                        **kwargs,
                    )(attr_value)

                # Replace the method with the traced version
                setattr(cls, attr_name, traced_method)

        return cls

    return decorator


def enrich_span(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config_data: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Context manager for enriching existing spans with additional attributes.

    Args:
        event_type: Type of traced event
        event_name: Name of the traced event
        inputs: Input data for the event
        outputs: Output data for the event
        metadata: Additional metadata
        config: Configuration data
        metrics: Performance metrics
        feedback: User feedback
        error: Error information
        event_id: Unique event identifier
        **kwargs: Additional attributes to set on the span
    """

    @contextmanager
    def span_enricher() -> Any:
        """Context manager that enriches the current span with HoneyHive attributes.

        Yields:
            None: The context manager yields control to the wrapped code block
        """
        try:
            # Get current span from OpenTelemetry context
            current_span = otel_trace.get_current_span()

            if current_span and current_span.is_recording():
                # Set comprehensive attributes on the current span
                if event_type:
                    current_span.set_attribute("honeyhive_event_type", event_type)

                if event_name:
                    current_span.set_attribute("honeyhive_event_name", event_name)

                if event_id:
                    current_span.set_attribute("honeyhive_event_id", event_id)

                # Set inputs if provided
                if inputs:
                    _set_span_attributes(current_span, "honeyhive_inputs", inputs)

                # Set config if provided
                if config_data:
                    _set_span_attributes(current_span, "honeyhive_config", config_data)

                # Set metadata if provided
                if metadata:
                    _set_span_attributes(current_span, "honeyhive_metadata", metadata)

                # Set metrics if provided
                if metrics:
                    _set_span_attributes(current_span, "honeyhive_metrics", metrics)

                # Set feedback if provided
                if feedback:
                    _set_span_attributes(current_span, "honeyhive_feedback", feedback)

                # Set additional kwargs as attributes
                for key, value in kwargs.items():
                    current_span.set_attribute(f"honeyhive_{key}", value)

                # Add experiment harness information if available
                try:
                    if config_data and config_data.get("experiment_id"):
                        current_span.set_attribute(
                            "honeyhive_experiment_id", config_data["experiment_id"]
                        )

                    if config_data and config_data.get("experiment_name"):
                        current_span.set_attribute(
                            "honeyhive_experiment_name", config_data["experiment_name"]
                        )

                    if config_data and config_data.get("experiment_variant"):
                        current_span.set_attribute(
                            "honeyhive_experiment_variant",
                            config_data["experiment_variant"],
                        )

                    if config_data and config_data.get("experiment_group"):
                        current_span.set_attribute(
                            "honeyhive_experiment_group",
                            config_data["experiment_group"],
                        )

                    if config_data and config_data.get("experiment_metadata"):
                        # Add experiment metadata as individual attributes
                        for key, value in config_data["experiment_metadata"].items():
                            current_span.set_attribute(
                                f"honeyhive_experiment_metadata_{key}", str(value)
                            )
                except Exception:
                    # Silently handle any exceptions when setting experiment attributes
                    pass

            yield current_span

        except Exception:
            # If enrichment fails, just yield None
            yield None

    return span_enricher()
