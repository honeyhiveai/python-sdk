import uuid
from traceback import print_exc
import os
import sys
import threading
import io
from contextlib import redirect_stdout
import subprocess

# from honeyhive.utils.telemetry import Telemetry
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import operations, components, errors
from honeyhive.sdk import HoneyHive

# Import the new OpenTelemetry tracer
from honeyhive.tracer.otel_tracer import HoneyHiveOTelTracer as HoneyHiveTracer
from honeyhive.tracer.http_instrumentation import instrument_http, uninstrument_http
from honeyhive.tracer.custom import trace, atrace

from opentelemetry import context, baggage
from opentelemetry.context import Context
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

DEFAULT_API_URL = "https://api.honeyhive.ai"

# Re-export the main tracer class for backward compatibility
__all__ = [
    'HoneyHiveTracer',
    'enrich_session',
    'instrument_http',
    'uninstrument_http',
    'trace',
    'atrace'
]

# Global function to enrich a session (re-exported from otel_tracer)
def enrich_session(
    session_id=None,
    metadata=None,
    feedback=None,
    metrics=None,
    config=None,
    inputs=None,
    outputs=None,
    user_properties=None
):
    """Global function to enrich a session"""
    from honeyhive.tracer.otel_tracer import enrich_session as _enrich_session
    return _enrich_session(
        session_id=session_id,
        metadata=metadata,
        feedback=feedback,
        metrics=metrics,
        config=config,
        inputs=inputs,
        outputs=outputs,
        user_properties=user_properties
    )

# Initialize HTTP instrumentation when the module is imported
def _initialize_http_instrumentation():
    """Initialize HTTP instrumentation if not disabled"""
    try:
        # Check if HTTP tracing is disabled via environment variable
        disable_http = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        if not disable_http:
            instrument_http()
    except Exception as e:
        # Silently fail if HTTP instrumentation fails
        pass

# Initialize HTTP instrumentation
_initialize_http_instrumentation()