import inspect
import logging
import re
import functools
import asyncio

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_instruments = ()

logger = logging.getLogger(__name__)

class FunctionInstrumentor(BaseInstrumentor):

    def _instrument(self, **kwargs):
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
        headers=None,
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

        def __init__(self, func, event_type=None, config=None, metadata=None, eval=None):
            self.func = func
            self.event_type = event_type
            self.config = config
            self.metadata = metadata
            self.eval = eval

            if func is not None:
                functools.update_wrapper(self, func)

        def __new__(
            cls,
            func=None,
            event_type=None,
            config=None,
            metadata=None,
            eval=None,
        ):
            if func is None:
                return lambda f: cls(f, event_type, config, metadata, eval)
            return super().__new__(cls)

        def __get__(self, instance, owner):
            # Implement descriptor protocol to handle method binding
            bound_method = functools.partial(self.__call__, instance)
            functools.update_wrapper(bound_method, self.func)
            return bound_method

        def __call__(self, *args, **kwargs):
            if asyncio.iscoroutinefunction(self.func):
                raise TypeError("please use @atrace for tracing async functions")
            ret = self.sync_call(*args, **kwargs)
            return ret
        
        async def __acall__(self, *args, **kwargs):
            if asyncio.iscoroutinefunction(self.func):
                return await self.async_call(*args, **kwargs)
            else:
                return self.sync_call(*args, **kwargs)

        def sync_call(self, *args, **kwargs):

            with self._func_instrumentor._tracer.start_as_current_span(
                self.func.__name__
            ) as span:

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

                result = self.func(*args, **kwargs)

                # Log the function output
                self._func_instrumentor._set_span_attributes(
                    span, "honeyhive_outputs.result", result
                )

                return result

        async def async_call(self, *args, **kwargs):

            with self._func_instrumentor._tracer.start_as_current_span(
                self.func.__name__
            ) as span:

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

                result = await self.func(*args, **kwargs)

                # Log the function output
                self._func_instrumentor._set_span_attributes(
                    span, "honeyhive_outputs.result", result
                )

                return result

    class atrace(trace):
        """Decorator for tracing asynchronous functions"""

        async def __call__(self, *args, **kwargs):
            return await self.__acall__(*args, **kwargs)

    def __init__(self):
        super().__init__()

        self.trace._func_instrumentor = self


# Instantiate and instrument the FunctionInstrumentor
instrumentor = FunctionInstrumentor()
instrumentor.instrument()

# Create the log_and_trace decorator for external use
trace = instrumentor.trace
atrace = instrumentor.atrace


# Enrich a span from within a traced function
def enrich_span(**properties):
    span = otel_trace.get_current_span()
    if span is None:
        logger.warning("Please use enrich_span inside a traced function.")
    else:
        instrumentor._enrich_span(span, **properties)
