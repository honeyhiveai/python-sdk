"""HoneyHive OpenTelemetry tracer module."""

from .decorators import atrace, trace, trace_class
from .otel_tracer import HoneyHiveTracer, enrich_session, enrich_span
from .span_processor import HoneyHiveSpanProcessor

__all__ = [
    "HoneyHiveTracer",
    "HoneyHiveSpanProcessor",
    "enrich_session",
    "enrich_span",
    "trace",
    "atrace",
    "trace_class",
]
