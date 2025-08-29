"""HoneyHive OpenTelemetry tracer module."""

from .decorators import atrace, trace, trace_class
from .otel_tracer import HoneyHiveTracer, enrich_session, enrich_span, get_tracer
from .span_processor import HoneyHiveSpanProcessor

__all__ = [
    "HoneyHiveTracer",
    "get_tracer",
    "HoneyHiveSpanProcessor",
    "enrich_session",
    "enrich_span",
    "trace",
    "atrace",
    "trace_class",
]
