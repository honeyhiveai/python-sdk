import inspect
import logging
import re
import functools
import asyncio
from typing import Callable, Optional, Dict, Any, TypeVar, cast, ParamSpec, Concatenate, Union

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_instruments = ()
P = ParamSpec('P')
R = TypeVar('R')

logger = logging.getLogger(__name__)


class SpanAttributeHandler:
    """Helper class for handling span attribute setting with different data types."""
    
    @staticmethod
    def set_span_attributes(span, prefix: str, value: Any) -> None:
        """Set span attributes, handling nested dictionaries, lists, and primitive types."""
        if isinstance(value, dict):
            SpanAttributeHandler._set_dict_attributes(span, prefix, value)
        elif isinstance(value, list):
            SpanAttributeHandler._set_list_attributes(span, prefix, value)
        elif SpanAttributeHandler._is_primitive_type(value):
            span.set_attribute(prefix, value)
        else:
            span.set_attribute(prefix, str(value))
    
    @staticmethod
    def _set_dict_attributes(span, prefix: str, value_dict: Dict[str, Any]) -> None:
        """Handle dictionary attributes recursively."""
        for key, val in value_dict.items():
            SpanAttributeHandler.set_span_attributes(span, f"{prefix}.{key}", val)
    
    @staticmethod
    def _set_list_attributes(span, prefix: str, value_list: list) -> None:
        """Handle list attributes by indexing."""
        for index, val in enumerate(value_list):
            SpanAttributeHandler.set_span_attributes(span, f"{prefix}.{index}", val)
    
    @staticmethod
    def _is_primitive_type(value: Any) -> bool:
        """Check if value is a primitive type supported by OpenTelemetry."""
        return isinstance(value, (int, bool, float, str))


class TemplateParser:
    """Helper class for parsing prompt templates."""
    
    @staticmethod
    def parse_and_match(template: str, text: str) -> Dict[str, str]:
        """Parse template placeholders and match against text.
        
        Args:
            template: Template string with {{placeholder}} format
            text: Text to match against template
            
        Returns:
            Dictionary mapping placeholder names to their values
            
        Raises:
            ValueError: If text doesn't match template pattern
        """
        # Extract placeholders from the template
        placeholders = re.findall(r"\{\{(.*?)\}\}", template)

        # Create a regex pattern from the template
        regex_pattern = re.escape(template)
        for placeholder in placeholders:
            regex_pattern = regex_pattern.replace(
                r"\{\{" + placeholder + r"\}\}", "(.*)"
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


class SpanEnricher:
    """Helper class for enriching spans with various metadata."""
    
    def __init__(self, attribute_handler: SpanAttributeHandler):
        self.attribute_handler = attribute_handler
    
    def enrich_span(
        self,
        span,
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Enrich span with various metadata attributes."""
        attribute_mappings = [
            (config, "honeyhive_config"),
            (metadata, "honeyhive_metadata"),
            (metrics, "honeyhive_metrics"),
            (feedback, "honeyhive_feedback"),
            (inputs, "honeyhive_inputs"),
            (outputs, "honeyhive_outputs"),
            (error, "honeyhive_error"),
            (tags, "honeyhive_tags"),
        ]
        
        for value, prefix in attribute_mappings:
            if value is not None:
                self.attribute_handler.set_span_attributes(span, prefix, value)
    
    def set_prompt_template(self, span, prompt_template: Dict[str, Any]) -> None:
        """Set prompt template attributes on span."""
        try:
            combined_template = "".join(
                [chat["content"] for chat in prompt_template["template"]]
            )
            combined_prompt = "".join(
                [chat["content"] for chat in prompt_template["prompt"]]
            )
            
            result = TemplateParser.parse_and_match(combined_template, combined_prompt)
            
            for param, value in result.items():
                self.attribute_handler.set_span_attributes(
                    span, f"honeyhive_prompt_template.inputs.{param}", value
                )
            
            template = prompt_template["template"]
            self.attribute_handler.set_span_attributes(
                span, "honeyhive_prompt_template.template", template
            )
            
            prompt = prompt_template["prompt"]
            self.attribute_handler.set_span_attributes(
                span, "honeyhive_prompt_template.prompt", prompt
            )
            
        except Exception as e:
            logger.warning(f"Failed to set prompt template: {e}")


class TracingDecorator:
    """Base class for tracing decorators with common functionality."""
    
    def __init__(
        self,
        func: Optional[Callable[P, R]] = None,
        event_type: Optional[str] = "tool",
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        instrumentor_instance=None,
    ):
        self.func = func
        self.event_type = event_type
        self.config = config
        self.metadata = metadata
        self.event_name = event_name
        self.tags = tags
        self._instrumentor = instrumentor_instance
        
        if func is not None:
            functools.update_wrapper(self, func)
    
    def __get__(self, instance, owner):
        """Implement descriptor protocol to handle method binding."""
        bound_method = functools.partial(self.__call__, instance)
        functools.update_wrapper(bound_method, self.func)
        return bound_method
    
    def _setup_span(self, span, args, kwargs) -> None:
        """Setup span with function parameters and decorator attributes."""
        try:
            # Extract function signature
            sig = inspect.signature(self.func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Log the function inputs with parameter names
            for param, value in bound_args.arguments.items():
                if param == "prompt_template":
                    self._instrumentor.span_enricher.set_prompt_template(span, value)
                else:
                    self._instrumentor.attribute_handler.set_span_attributes(
                        span, f"honeyhive_inputs._params_.{param}", value
                    )
            
            self._set_event_type(span)
            self._set_decorator_attributes(span)
            
        except Exception as e:
            logger.warning(f"Failed to setup span: {e}")
    
    def _set_event_type(self, span) -> None:
        """Set event type attribute if valid."""
        if self.event_type and isinstance(self.event_type, str):
            if self.event_type in ["tool", "model", "chain"]:
                self._instrumentor.attribute_handler.set_span_attributes(
                    span, "honeyhive_event_type", self.event_type
                )
            else:
                logger.warning(
                    "event_type could not be set. Must be 'tool', 'model', or 'chain'."
                )
    
    def _set_decorator_attributes(self, span) -> None:
        """Set attributes from decorator parameters."""
        attribute_mappings = [
            (self.config, "honeyhive_config"),
            (self.metadata, "honeyhive_metadata"),
            (self.tags, "honeyhive_tags"),
        ]
        
        for value, prefix in attribute_mappings:
            if value is not None:
                self._instrumentor.attribute_handler.set_span_attributes(span, prefix, value)
    
    def _handle_result(self, span, result: Any) -> Any:
        """Handle successful function result."""
        try:
            self._instrumentor.attribute_handler.set_span_attributes(
                span, "honeyhive_outputs.result", result
            )
        except Exception as e:
            logger.warning(f"Failed to set result attribute: {e}")
        return result
    
    def _handle_exception(self, span, exception: Exception) -> None:
        """Handle function exception."""
        try:
            self._instrumentor.attribute_handler.set_span_attributes(
                span, "honeyhive_error", str(exception)
            )
        except Exception as e:
            logger.warning(f"Failed to set error attribute: {e}")
        # Re-raise the exception to maintain normal error propagation
        raise exception


class FunctionInstrumentor(BaseInstrumentor):
    """Main instrumentor class that manages tracing functionality."""

    def __init__(self):
        super().__init__()
        self.attribute_handler = SpanAttributeHandler()
        self.span_enricher = SpanEnricher(self.attribute_handler)

    def _instrument(self, **kwargs):
        """Initialize the tracer."""
        tracer_provider = TracerProvider()
        otel_trace.set_tracer_provider(tracer_provider)
        self._tracer = otel_trace.get_tracer(__name__)

    def _uninstrument(self, **kwargs):
        """Clean up instrumentation."""
        pass

    def instrumentation_dependencies(self):
        """Return instrumentation dependencies."""
        return _instruments

    def _set_span_attributes(self, span, prefix: str, value: Any) -> None:
        """Legacy method for backward compatibility."""
        self.attribute_handler.set_span_attributes(span, prefix, value)

    def _parse_and_match(self, template: str, text: str) -> Dict[str, str]:
        """Legacy method for backward compatibility."""
        return TemplateParser.parse_and_match(template, text)

    def _set_prompt_template(self, span, prompt_template: Dict[str, Any]) -> None:
        """Legacy method for backward compatibility."""
        self.span_enricher.set_prompt_template(span, prompt_template)

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
        tags=None,
    ):
        """Legacy method for backward compatibility."""
        self.span_enricher.enrich_span(
            span, config, metadata, metrics, feedback, inputs, outputs, error, tags
        )

    def create_trace_decorator(self, is_async: bool = False):
        """Factory method to create trace decorators."""
        
        class TraceDecoratorImpl(TracingDecorator):
            def __init__(
                decorator_self,
                func: Optional[Callable[P, R]] = None,
                event_type: Optional[str] = "tool",
                config: Optional[Dict[str, Any]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                event_name: Optional[str] = None,
                tags: Optional[Dict[str, Any]] = None,
            ):
                super().__init__(func, event_type, config, metadata, event_name, tags, self)
                decorator_self.is_async = is_async
            
            def __new__(
                cls,
                func: Optional[Callable[P, R]] = None,
                event_type: Optional[str] = "tool",
                config: Optional[Dict[str, Any]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                event_name: Optional[str] = None,
                tags: Optional[Dict[str, Any]] = None,
            ):
                if func is None:
                    return lambda f: cls(f, event_type, config, metadata, event_name, tags)
                return super().__new__(cls)
            
            def __call__(decorator_self, *args: P.args, **kwargs: P.kwargs) -> R:
                if decorator_self.is_async:
                    # For async decorator, always return awaitable
                    return decorator_self.__acall__(*args, **kwargs)
                else:
                    # For sync decorator, check if function is async and raise error
                    if asyncio.iscoroutinefunction(decorator_self.func):
                        raise TypeError("please use @atrace for tracing async functions")
                    return decorator_self._sync_call(*args, **kwargs)
            
            async def __acall__(decorator_self, *args: P.args, **kwargs: P.kwargs) -> R:
                if asyncio.iscoroutinefunction(decorator_self.func):
                    return await decorator_self._async_call(*args, **kwargs)
                else:
                    return decorator_self._sync_call(*args, **kwargs)
            
            def _sync_call(decorator_self, *args, **kwargs):
                """Execute synchronous function with tracing."""
                with decorator_self._instrumentor._tracer.start_as_current_span(
                    decorator_self.event_name or decorator_self.func.__name__
                ) as span:
                    decorator_self._setup_span(span, args, kwargs)
                    try:
                        result = decorator_self.func(*args, **kwargs)
                        return decorator_self._handle_result(span, result)
                    except Exception as e:
                        decorator_self._handle_exception(span, e)
            
            async def _async_call(decorator_self, *args, **kwargs):
                """Execute asynchronous function with tracing."""
                with decorator_self._instrumentor._tracer.start_as_current_span(
                    decorator_self.event_name or decorator_self.func.__name__
                ) as span:
                    decorator_self._setup_span(span, args, kwargs)
                    try:
                        result = await decorator_self.func(*args, **kwargs)
                        return decorator_self._handle_result(span, result)
                    except Exception as e:
                        decorator_self._handle_exception(span, e)
        
        return TraceDecoratorImpl
    
    @property
    def trace(self):
        """Synchronous tracing decorator."""
        return self.create_trace_decorator(is_async=False)
    
    @property
    def atrace(self):
        """Asynchronous tracing decorator."""
        return self.create_trace_decorator(is_async=True)


# Instantiate and instrument the FunctionInstrumentor
instrumentor = FunctionInstrumentor()
instrumentor.instrument()

# Create the trace decorators for external use
trace = instrumentor.trace
atrace = instrumentor.atrace


# Enrich a span from within a traced function
def enrich_span(
    config: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None
):
    """Enrich the current span with additional attributes."""
    span = otel_trace.get_current_span()
    if span is None:
        logger.warning("Please use enrich_span inside a traced function.")
    else:
        # For backward compatibility, only pass tags if it's not None
        if tags is not None:
            instrumentor._enrich_span(span, config, metadata, metrics, feedback, inputs, outputs, error, tags)
        else:
            instrumentor._enrich_span(span, config, metadata, metrics, feedback, inputs, outputs, error)
