import inspect
import logging
import re
from functools import wraps
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_instruments = ()

logger = logging.getLogger(__name__)

class SpanProxy:
    def _enrich_span(self, *args, **kwargs): 
        logger.warning('Please use enrich_span inside a traced function.')

class FunctionInstrumentor(BaseInstrumentor):
    def __init__(self):
        super().__init__()
        self._span_proxy = SpanProxy()

    def _instrument(self, **kwargs):
        tracer_provider = TracerProvider()
        trace.set_tracer_provider(tracer_provider)

        self._tracer = trace.get_tracer(__name__)

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
            
    @contextmanager
    def _span_context(self, span):
        # save the current span attributes
        current_enrich_span = self._span_proxy._enrich_span
        
        # call _enrich_span with the current span
        self._span_proxy._enrich_span = \
            lambda *args, **kwargs: self._enrich_span(span, *args, **kwargs)
        
        try:
            yield
        finally:
            # restore the original enrich_span
            self._span_proxy._enrich_span = current_enrich_span
        
    def trace(
        self, 
        event_type=None,
        config=None, 
        metadata=None, 
    ):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self._tracer.start_as_current_span(func.__name__) as span:
                    # Extract function signature
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    # Log the function inputs with parameter names
                    for param, value in bound_args.arguments.items():
                        if param == "prompt_template":
                            self._set_prompt_template(span, value)
                        else:
                            self._set_span_attributes(
                                span, f"honeyhive_inputs._params_.{param}", value
                            )

                    if event_type:
                        if isinstance(event_type, str) and event_type in ['tool', 'model', 'chain']:
                            self._set_span_attributes(span, "honeyhive_event_type", event_type)
                        else:
                            logger.warning("event_type could not be set. Must be 'tool', 'model', or 'chain'.")
                    
                    if config:
                        self._set_span_attributes(span, "honeyhive_config", config)
                    if metadata:
                        self._set_span_attributes(span, "honeyhive_metadata", metadata)
                                        
                    # This context allows us to enrich the span from within the decorated function
                    with self._span_context(span):
                        result = func(*args, **kwargs)
                    
                    # Log the function output
                    self._set_span_attributes(span, "honeyhive_outputs.result", result)

                    return result

            return wrapper

        return decorator


# Instantiate and instrument the FunctionInstrumentor
instrumentor = FunctionInstrumentor()
instrumentor.instrument()

# Create the log_and_trace decorator for external use
trace = instrumentor.trace

# Enrich a span from within a traced function
def enrich_span(*args, **kwargs):
    return instrumentor._span_proxy._enrich_span(*args, **kwargs)