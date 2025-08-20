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
from honeyhive.tracer.custom import trace, atrace, disable_tracing, enable_tracing

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
    'atrace',
    'disable_tracing',
    'enable_tracing',
    'reset_tracer_state'
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
    # Create a temporary tracer instance to call enrich_session
    try:
        from honeyhive.tracer.otel_tracer import HoneyHiveOTelTracer
        if HoneyHiveOTelTracer._is_initialized:
            print(f"enrich_session: Creating temporary tracer for session {session_id}")
            print(f"enrich_session: Metrics: {metrics}")
            
            # Create a temporary tracer instance
            temp_tracer = HoneyHiveOTelTracer(
                api_key=HoneyHiveOTelTracer.api_key,
                project=getattr(HoneyHiveOTelTracer, 'project', None) or "unknown",
                source="enrich_session",
                test_mode=False  # Don't use test mode to ensure API calls work
            )
            
            print(f"enrich_session: Calling temp_tracer.enrich_session")
            result = temp_tracer.enrich_session(
                session_id=session_id,
                metadata=metadata,
                feedback=feedback,
                metrics=metrics,
                config=config,
                inputs=inputs,
                outputs=outputs,
                user_properties=user_properties
            )
            print(f"enrich_session: Successfully called temp_tracer.enrich_session")
            return result
        else:
            print("Warning: HoneyHiveOTelTracer not initialized, skipping enrich_session")
            return None
    except Exception as e:
        print(f"Warning: enrich_session failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# Global function to reset tracer state for testing
def reset_tracer_state():
    """Reset tracer static state for testing purposes"""
    HoneyHiveTracer._reset_static_state()

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