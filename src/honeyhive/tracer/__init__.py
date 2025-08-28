"""HoneyHive OpenTelemetry tracer module."""

from .otel_tracer import HoneyHiveTracer, get_tracer, enrich_session, enrich_span
from .span_processor import HoneyHiveSpanProcessor
from .decorators import trace, atrace, trace_class

__all__ = [
    "HoneyHiveTracer",
    "get_tracer", 
    "HoneyHiveSpanProcessor",
    "enrich_session",
    "enrich_span",
    "trace",
    "atrace", 
    "trace_class"
]
