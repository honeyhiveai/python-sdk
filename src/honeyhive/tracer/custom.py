import logging
from functools import wraps
import inspect
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
        elif isinstance(value, int) or isinstance(value, bool) or isinstance(value, float) or isinstance(value, str):
            span.set_attribute(prefix, value)
        else:
            span.set_attribute(prefix, str(value))

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
                        self._set_span_attributes(span, f"honeyhive_inputs._params_.{param}", value)
                    
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
