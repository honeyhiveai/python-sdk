import inspect
import logging
import re
from functools import wraps
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_instruments = ()


class FunctionInstrumentor(BaseInstrumentor):
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

    def trace(self, config=None, metadata=None):
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

                    if config:
                        self._set_span_attributes(span, "honeyhive_config", config)
                    if metadata:
                        self._set_span_attributes(span, "honeyhive_metadata", metadata)

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
