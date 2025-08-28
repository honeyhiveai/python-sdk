"""Decorators for HoneyHive tracing with enhanced attribute support."""

import functools
import inspect
import json
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from contextlib import contextmanager

from .otel_tracer import get_tracer

T = TypeVar('T')
P = TypeVar('P')


def _set_span_attributes(span, prefix: str, value: Any) -> None:
    """Set span attributes with proper type handling and JSON serialization."""
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _set_span_attributes(span, f"{prefix}.{i}", v)
    elif (
        isinstance(value, int)
        or isinstance(value, bool)
        or isinstance(value, float)
        or isinstance(value, str)
    ):
        span.set_attribute(prefix, value)
    else:
        # Convert complex types to JSON strings for OpenTelemetry compatibility
        try:
            span.set_attribute(prefix, json.dumps(value, default=str))
        except (TypeError, ValueError):
            # Fallback to string representation if JSON serialization fails
            span.set_attribute(prefix, str(value))


def trace(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs
):
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
        @functools.wraps(func)
        def wrapper(*args, **func_kwargs) -> T:
            # Get tracer instance
            try:
                tracer = get_tracer()
            except Exception:
                # If tracer is not available, just call the function
                return func(*args, **func_kwargs)
            
            # Create span name from function
            span_name = event_name or f"{func.__module__}.{func.__name__}"
            
            # Start timing for duration calculation
            start_time = time.time()
            
            try:
                with tracer.start_span(span_name) as span:
                    # Set comprehensive attributes
                    if event_type:
                        span.set_attribute("honeyhive_event_type", event_type)
                    
                    if event_name:
                        span.set_attribute("honeyhive_event_name", event_name)
                    
                    if event_id:
                        span.set_attribute("honeyhive_event_id", event_id)
                    
                    # Set inputs if provided
                    if inputs:
                        _set_span_attributes(span, "honeyhive_inputs", inputs)
                    
                    # Set config if provided
                    if config:
                        _set_span_attributes(span, "honeyhive_config", config)
                    
                    # Set metadata if provided
                    if metadata:
                        _set_span_attributes(span, "honeyhive_metadata", metadata)
                    
                    # Set metrics if provided
                    if metrics:
                        _set_span_attributes(span, "honeyhive_metrics", metrics)
                    
                    # Set feedback if provided
                    if feedback:
                        _set_span_attributes(span, "honeyhive_feedback", feedback)
                    
                    # Set additional kwargs as attributes
                    for key, value in kwargs.items():
                        span.set_attribute(f"honeyhive_{key}", value)
                    
                    # Execute the function
                    result = func(*args, **func_kwargs)
                    
                    # Set outputs if provided or use function result
                    if outputs:
                        try:
                            _set_span_attributes(span, "honeyhive_outputs", outputs)
                        except Exception:
                            # Silently handle any exceptions when setting span attributes
                            pass
                    else:
                        # Try to set function result as output, handle all exceptions silently
                        try:
                            span.set_attribute("honeyhive_outputs.result", json.dumps(result, default=str))
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
                    with tracer.start_span(f"{span_name}_error") as error_span:
                        error_span.set_attribute("honeyhive_error", str(e))
                        error_span.set_attribute("honeyhive_error_type", type(e).__name__)
                        error_span.set_attribute("honeyhive_duration_ms", duration)
                        
                        # Set error context
                        if error:
                            error_span.set_attribute("honeyhive_error", str(error))
                        else:
                            error_span.set_attribute("honeyhive_error", str(e))
                        
                        # Re-raise the exception
                        raise
                except Exception:
                    # If error tracing fails, just re-raise the original exception
                    raise e
        
        return wrapper
    
    # Handle both @trace and @trace(...) usage
    if callable(event_type):
        # Used as @trace
        return decorator(event_type)
    else:
        # Used as @trace(...)
        return decorator


def atrace(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs
):
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
        @functools.wraps(func)
        async def async_wrapper(*args, **func_kwargs) -> Any:
            # Get tracer instance
            try:
                tracer = get_tracer()
            except Exception:
                # If tracer is not available, just call the function
                return await func(*args, **func_kwargs)
            
            # Create span name from function
            span_name = event_name or f"{func.__module__}.{func.__name__}"
            
            # Start timing for duration calculation
            start_time = time.time()
            
            try:
                with tracer.start_span(span_name) as span:
                    # Set comprehensive attributes
                    if event_type:
                        span.set_attribute("honeyhive_event_type", event_type)
                    
                    if event_name:
                        span.set_attribute("honeyhive_event_name", event_name)
                    
                    if event_id:
                        span.set_attribute("honeyhive_event_id", event_id)
                    
                    # Set inputs if provided
                    if inputs:
                        _set_span_attributes(span, "honeyhive_inputs", inputs)
                    
                    # Set config if provided
                    if config:
                        _set_span_attributes(span, "honeyhive_config", config)
                    
                    # Set metadata if provided
                    if metadata:
                        _set_span_attributes(span, "honeyhive_metadata", metadata)
                    
                    # Set metrics if provided
                    if metrics:
                        _set_span_attributes(span, "honeyhive_metrics", metrics)
                    
                    # Set feedback if provided
                    if feedback:
                        _set_span_attributes(span, "honeyhive_feedback", feedback)
                    
                    # Set additional kwargs as attributes
                    for key, value in kwargs.items():
                        span.set_attribute(f"honeyhive_{key}", value)
                    
                    # Execute the async function
                    result = await func(*args, **func_kwargs)
                    
                    # Set outputs if provided or use function result
                    if outputs:
                        try:
                            _set_span_attributes(span, "honeyhive_outputs", outputs)
                        except Exception:
                            # Silently handle any exceptions when setting span attributes
                            pass
                    else:
                        # Try to set function result as output, handle all exceptions silently
                        try:
                            span.set_attribute("honeyhive_outputs.result", json.dumps(result, default=str))
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
                    with tracer.start_span(f"{span_name}_error") as error_span:
                        error_span.set_attribute("honeyhive_error", str(e))
                        error_span.set_attribute("honeyhive_error_type", type(e).__name__)
                        error_span.set_attribute("honeyhive_duration_ms", duration)
                        
                        # Set error context
                        if error:
                            error_span.set_attribute("honeyhive_error", str(error))
                        else:
                            error_span.set_attribute("honeyhive_error", str(e))
                        
                        # Re-raise the exception
                        raise
                except Exception:
                    # If error tracing fails, just re-raise the original exception
                    raise e
        
        return async_wrapper
    
    # Handle both @atrace and @atrace(...) usage
    if callable(event_type):
        # Used as @atrace
        return decorator(event_type)
    else:
        # Used as @atrace(...)
        return decorator


def trace_class(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    **kwargs
):
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
            if (inspect.isfunction(attr_value) and 
                not attr_name.startswith('_') and
                attr_name not in ['__init__', '__new__']):
                
                # Create a traced version of the method
                if inspect.iscoroutinefunction(attr_value):
                    # Async method
                    traced_method = atrace(
                        event_type=event_type,
                        event_name=f"{event_name or cls.__name__}.{attr_name}",
                        **kwargs
                    )(attr_value)
                else:
                    # Sync method
                    traced_method = trace(
                        event_type=event_type,
                        event_name=f"{event_name or cls.__name__}.{attr_name}",
                        **kwargs
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
    config: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    **kwargs
):
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
    def span_enricher():
        try:
            # Get current span from OpenTelemetry context
            from opentelemetry import trace
            current_span = trace.get_current_span()
            
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
                if config:
                    _set_span_attributes(current_span, "honeyhive_config", config)
                
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
            
            yield current_span
            
        except Exception:
            # If enrichment fails, just yield None
            yield None
    
    return span_enricher()
