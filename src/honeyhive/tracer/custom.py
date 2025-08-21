import inspect
import logging
import re
import functools
import asyncio
from typing import Callable, Optional, Dict, Any, TypeVar, cast, ParamSpec, Concatenate

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_instruments = ()
P = ParamSpec('P')
R = TypeVar('R')

logger = logging.getLogger(__name__)

class FunctionInstrumentor(BaseInstrumentor):

    def _instrument(self, **kwargs):
        # Use the tracer from the main HoneyHiveOTelTracer if available
        from honeyhive.tracer.otel_tracer import HoneyHiveOTelTracer
        
        # Wait for the tracer to be available (with timeout)
        import time
        start_time = time.time()
        timeout = 5.0  # 5 second timeout
        
        while HoneyHiveOTelTracer.tracer is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if HoneyHiveOTelTracer.tracer is not None:
            self._tracer = HoneyHiveOTelTracer.tracer
            if HoneyHiveOTelTracer.verbose:
                print(f"🔗 FunctionInstrumentor using HoneyHiveOTelTracer.tracer")
        else:
            # Fallback to creating a new tracer provider
            if HoneyHiveOTelTracer.verbose:
                print(f"⚠️ FunctionInstrumentor creating fallback tracer provider")
            tracer_provider = TracerProvider()
            otel_trace.set_tracer_provider(tracer_provider)
            self._tracer = otel_trace.get_tracer(__name__)

    def _uninstrument(self, **kwargs):
        pass

    def instrumentation_dependencies(self):
        return _instruments

    def _set_span_attributes(self, span, prefix, value):
        if isinstance(value, dict):
            for k, v in value.items():
                self._set_span_attributes(span, f"{prefix}.{k}", v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                self._set_span_attributes(span, f"{prefix}.{i}", v)
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
                import json
                span.set_attribute(prefix, json.dumps(value, default=str))
            except (TypeError, ValueError):
                # Fallback to string representation if JSON serialization fails
                span.set_attribute(prefix, str(value))

    def _parse_and_match(self, template, text):
        # Extract placeholders from the template
        placeholders = re.findall(r"\{\{(.*?)\}\}", template)

        # Create a regex pattern from the template
        regex_pattern = re.escape(template)
        for placeholder in placeholders:
            regex_pattern = regex_pattern.replace(
                r"\{\{" + placeholder + r"\}\}", "(.*?)"
            )

        # Match the pattern against the text
        match = re.match(regex_pattern, text)

        if not match:
            raise ValueError("The text does not match the template.")

        # Extract the corresponding substrings
        matches = match.groups()

        # Create a dictionary of the results
        result = {
            placeholder: match for placeholder, match in zip(placeholders, matches)
        }

        return result

    def _set_prompt_template(self, span, prompt_template):
        combined_template = "".join(
            [chat["content"] for chat in prompt_template["template"]]
        )
        combined_prompt = "".join(
            [chat["content"] for chat in prompt_template["prompt"]]
        )
        result = self._parse_and_match(combined_template, combined_prompt)
        for param, value in result.items():
            self._set_span_attributes(
                span, f"honeyhive_prompt_template.inputs.{param}", value
            )

        template = prompt_template["template"]
        self._set_span_attributes(span, "honeyhive_prompt_template.template", template)
        prompt = prompt_template["prompt"]
        self._set_span_attributes(span, "honeyhive_prompt_template.prompt", prompt)

    def _enrich_span(
        self,
        span,
        config=None,
        metadata=None,
        metrics=None,
        feedback=None,
        inputs=None,
        outputs=None,
        error=None,
        # headers=None,
    ):
        if config:
            self._set_span_attributes(span, "honeyhive_config", config)
        if metadata:
            self._set_span_attributes(span, "honeyhive_metadata", metadata)
        if metrics:
            self._set_span_attributes(span, "honeyhive_metrics", metrics)
        if feedback:
            self._set_span_attributes(span, "honeyhive_feedback", feedback)
        if inputs:
            self._set_span_attributes(span, "honeyhive_inputs", inputs)
        if outputs:
            self._set_span_attributes(span, "honeyhive_outputs", outputs)
        if error:
            self._set_span_attributes(span, "honeyhive_error", error)


    class trace:
        """Decorator for tracing synchronous functions"""

        _func_instrumentor = None

        def __init__(
            self,
            func: Optional[Callable[P, R]] = None,
            event_type: Optional[str] = "tool",
            config: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            event_name: Optional[str] = None,
        ):
            self.func = func
            self.event_type = event_type
            self.config = config
            self.metadata = metadata
            self.event_name = event_name

            if func is not None:
                functools.update_wrapper(self, func)

        def __call__(self, *args, **kwargs):
            # If we have a function and this is being called with function arguments
            if self.func is not None:
                # Check if tracing is disabled at call time for maximum performance
                if hasattr(self._func_instrumentor, '_tracing_disabled') and self._func_instrumentor._tracing_disabled:
                    # Ultra-fast path: direct function call with zero overhead
                    return self.func(*args, **kwargs)
                return self.sync_call(*args, **kwargs)
            # If we don't have a function, this is being used as a decorator
            else:
                func = args[0]
                # Check if tracing is disabled when creating the decorator
                if hasattr(self._func_instrumentor, '_tracing_disabled') and self._func_instrumentor._tracing_disabled:
                    # Return a no-op decorator for maximum performance
                    return func
                return self.__class__(func, self.event_type, self.config, self.metadata, self.event_name)

        def __get__(self, instance, owner):
            # Implement descriptor protocol to handle method binding
            bound_method = functools.partial(self.__call__, instance)
            functools.update_wrapper(bound_method, self.func)
            return bound_method

        def _setup_span(self, span, args, kwargs):
            if self.func is None:
                return
                
            # Extract function signature
            sig = inspect.signature(self.func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Log the function inputs with parameter names
            for param, value in bound_args.arguments.items():
                if param == "prompt_template":
                    self._func_instrumentor._set_prompt_template(span, value)
                else:
                    self._func_instrumentor._set_span_attributes(
                        span, f"honeyhive_inputs._params_.{param}", value
                    )

            if self.event_type:
                if isinstance(self.event_type, str) and self.event_type in [
                    "tool",
                    "model",
                    "chain",
                ]:
                    self._func_instrumentor._set_span_attributes(
                        span, "honeyhive_event_type", self.event_type
                    )
                else:
                    logger.warning(
                        "event_type could not be set. Must be 'tool', 'model', or 'chain'."
                    )

            if self.config:
                self._func_instrumentor._set_span_attributes(
                    span, "honeyhive_config", self.config
                )
            if self.metadata:
                self._func_instrumentor._set_span_attributes(
                    span, "honeyhive_metadata", self.metadata
                )

        def _handle_result(self, span, result):
            # Log the function output
            self._func_instrumentor._set_span_attributes(
                span, "honeyhive_outputs.result", result
            )
            return result

        def _handle_exception(self, span, exception):
            # Capture exception in the span
            self._func_instrumentor._set_span_attributes(
                span, "honeyhive_error", str(exception)
            )
            # Re-raise the exception to maintain normal error propagation
            raise exception

        def sync_call(self, *args, **kwargs):
            # Performance optimization: check if tracing is globally disabled
            if hasattr(self._func_instrumentor, '_tracing_disabled') and self._func_instrumentor._tracing_disabled:
                # Ultra-fast path: direct function call with zero overhead
                return self.func(*args, **kwargs)
                
            # Check if tracer exists and is available
            if not hasattr(self._func_instrumentor, '_tracer') or self._func_instrumentor._tracer is None:
                return self.func(*args, **kwargs)
                
            # Create comprehensive span for better event tracking
            try:
                # Get current context and add session information
                from opentelemetry import context
                from honeyhive.tracer.otel_tracer import HoneyHiveOTelTracer
                
                current_ctx = context.get_current()
                
                # Add session context if available
                if hasattr(HoneyHiveOTelTracer, 'api_key') and HoneyHiveOTelTracer.api_key:
                    # Try to get session_id from context or create a new one
                    session_id = None
                    if current_ctx is not None:
                        association_properties = current_ctx.get('association_properties')
                        if association_properties and isinstance(association_properties, dict):
                            session_id = association_properties.get('session_id')
                    
                    # If no session_id in context, try to get from current tracer instance
                    if not session_id:
                        # This is a bit of a hack, but we need to get the session_id somehow
                        # For now, let's try to get it from the global context
                        pass
                
                # Get the current context with session information
                from opentelemetry import context
                current_ctx = context.get_current()
                
                # Create span with the current context
                span = self._func_instrumentor._tracer.start_span(
                    self.event_name or self.func.__name__,
                    context=current_ctx
                )
                
                # Set comprehensive attributes for better event tracking
                if self.event_type:
                    span.set_attribute("honeyhive_event_type", self.event_type)
                
                # Set up span context for enrichment
                with otel_trace.use_span(span):
                    # Execute function
                    result = self.func(*args, **kwargs)
                    
                    # Set result attribute using the proper method for complex types
                    if isinstance(result, (dict, list)) or not isinstance(result, (int, bool, float, str)):
                        # Convert complex types to JSON strings for OpenTelemetry compatibility
                        try:
                            import json
                            span.set_attribute("honeyhive_outputs.result", json.dumps(result, default=str))
                        except (TypeError, ValueError):
                            # Fallback to string representation if JSON serialization fails
                            span.set_attribute("honeyhive_outputs.result", str(result))
                    else:
                        # Simple types can be set directly
                        span.set_attribute("honeyhive_outputs.result", result)
                    
                    # End span
                    span.end()
                    return result
                
            except Exception as e:
                if 'span' in locals():
                    span.set_attribute("honeyhive_error", str(e))
                    span.end()
                raise

        async def async_call(self, *args, **kwargs):
            # Performance optimization: check if tracing is globally disabled
            if hasattr(self._func_instrumentor, '_tracing_disabled') and self._func_instrumentor._tracing_disabled:
                # Ultra-fast path: direct function call with zero overhead
                return await self.func(*args, **kwargs)
                
            # Check if tracer exists and is available
            if not hasattr(self._func_instrumentor, '_tracer') or self._func_instrumentor._tracer is None:
                return await self.func(*args, **kwargs)
                
            # Create comprehensive span for better event tracking
            try:
                span = self._func_instrumentor._tracer.start_span(
                    self.event_name or self.func.__name__
                )
                
                # Set comprehensive attributes for better event tracking
                if self.event_type:
                    span.set_attribute("honeyhive_event_type", self.event_type)
                
                # Set up span context for enrichment
                with otel_trace.use_span(span):
                    # Execute function
                    result = await self.func(*args, **kwargs)
                    
                    # Set result attribute using the proper method for complex types
                    if isinstance(result, (dict, list)) or not isinstance(result, (int, bool, float, str)):
                        # Convert complex types to JSON strings for OpenTelemetry compatibility
                        try:
                            import json
                            span.set_attribute("honeyhive_outputs.result", json.dumps(result, default=str))
                        except (TypeError, ValueError):
                            # Fallback to string representation if JSON serialization fails
                            span.set_attribute("honeyhive_outputs.result", str(result))
                    else:
                        # Simple types can be set directly
                        span.set_attribute("honeyhive_outputs.result", result)
                    
                    # End span
                    span.end()
                    return result
                
            except Exception as e:
                if 'span' in locals():
                    span.set_attribute("honeyhive_error", str(e))
                    span.end()
                raise

    class atrace(trace):
        """Decorator for tracing asynchronous functions"""
        
        def __init__(
            self,
            func: Optional[Callable[P, R]] = None,
            event_type: Optional[str] = "tool",
            config: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            event_name: Optional[str] = None,
        ):
            super().__init__(func, event_type, config, metadata, event_name)

        def __call__(self, *args, **kwargs):
            # If we have a function and this is being called with function arguments
            if self.func is not None:
                return self.async_call(*args, **kwargs)
            # If we don't have a function, this is being used as a decorator
            else:
                func = args[0]
                return self.__class__(func, self.event_type, self.config, self.metadata, self.event_name)

    def __init__(self):
        super().__init__()

        self.trace._func_instrumentor = self
        self._tracing_disabled = False

    def disable_tracing(self):
        """Disable tracing globally for performance optimization"""
        self._tracing_disabled = True

    def enable_tracing(self):
        """Enable tracing globally"""
        self._tracing_disabled = False


# Lazy initialization of FunctionInstrumentor
_instrumentor_instance = None

def _get_instrumentor():
    """Get or create the instrumentor instance"""
    global _instrumentor_instance
    if _instrumentor_instance is None:
        _instrumentor_instance = FunctionInstrumentor()
        _instrumentor_instance.instrument()
    return _instrumentor_instance

# Create dynamic decorators that check tracing state at runtime
def trace(*args, **kwargs):
    """Dynamic trace decorator that checks tracing state at runtime"""
    if len(args) == 1 and callable(args[0]):
        # Used as @trace
        func = args[0]
        
        # Create a proxy function that checks tracing state at call time
        def traced_function(*func_args, **func_kwargs):
            # Ultra-fast path: check tracing state with minimal overhead
            instrumentor = _get_instrumentor()
            if instrumentor._tracing_disabled:
                # Direct function call with zero overhead
                return func(*func_args, **func_kwargs)
            
            # Full tracing path - optimized for performance
            trace_instance = instrumentor.trace(func, **kwargs)
            return trace_instance.sync_call(*func_args, **func_kwargs)
        
        # Preserve function metadata
        functools.update_wrapper(traced_function, func)
        return traced_function
    else:
        # Used as @trace(...)
        def decorator(func):
            # Create a proxy function that checks tracing state at call time
            def traced_function(*func_args, **func_kwargs):
                # Ultra-fast path: check tracing state with minimal overhead
                instrumentor = _get_instrumentor()
                if instrumentor._tracing_disabled:
                    # Direct function call with zero overhead
                    return func(*func_args, **func_kwargs)
                
                # Full tracing path - optimized for performance
                trace_instance = instrumentor.trace(func, *args, **kwargs)
                return trace_instance.sync_call(*func_args, **func_kwargs)
            
            # Preserve function metadata
            functools.update_wrapper(traced_function, func)
            return traced_function
        return decorator

def atrace(*args, **kwargs):
    """Dynamic atrace decorator that checks tracing state at runtime"""
    if len(args) == 1 and callable(args[0]):
        # Used as @atrace
        func = args[0]
        
        # Create a proxy function that checks tracing state at call time
        async def traced_function(*func_args, **func_kwargs):
            # Ultra-fast path: check tracing state with minimal overhead
            instrumentor = _get_instrumentor()
            if instrumentor._tracing_disabled:
                # Direct function call with zero overhead
                return await func(*func_args, **func_kwargs)
            
            # Full tracing path - optimized for performance
            atrace_instance = instrumentor.atrace(func, **kwargs)
            return await atrace_instance.async_call(*func_args, **func_kwargs)
        
        # Preserve function metadata
        functools.update_wrapper(traced_function, func)
        return traced_function
    else:
        # Used as @atrace(...)
        def decorator(func):
            # Create a proxy function that checks tracing state at call time
            async def traced_function(*func_args, **func_kwargs):
                # Ultra-fast path: check tracing state with minimal overhead
                instrumentor = _get_instrumentor()
                if instrumentor._tracing_disabled:
                    # Direct function call with zero overhead
                    return await func(*func_args, **func_kwargs)
                
                # Full tracing path - optimized for performance
                atrace_instance = instrumentor.atrace(func, *args, **kwargs)
                return await atrace_instance.async_call(*func_args, **func_kwargs)
            
            # Preserve function metadata
            functools.update_wrapper(traced_function, func)
            return traced_function
        return decorator

# Global functions to control tracing
def disable_tracing():
    """Disable tracing globally for performance optimization"""
    _get_instrumentor().disable_tracing()

def enable_tracing():
    """Enable tracing globally"""
    _get_instrumentor().enable_tracing()


# Enrich a span from within a traced function
def enrich_span(
    config: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    span = otel_trace.get_current_span()
    if span is None:
        logger.warning("Please use enrich_span inside a traced function.")
    else:
        _get_instrumentor()._enrich_span(span, config, metadata, metrics, feedback, inputs, outputs, error)
