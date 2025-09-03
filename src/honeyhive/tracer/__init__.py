"""HoneyHive OpenTelemetry tracer module."""

from .decorators import atrace, trace, trace_class
from .otel_tracer import HoneyHiveTracer, enrich_session, enrich_span
from .registry import clear_registry, get_default_tracer, set_default_tracer
from .span_processor import HoneyHiveSpanProcessor

__all__ = [
    "HoneyHiveTracer",
    "HoneyHiveSpanProcessor",
    "enrich_session",
    "enrich_span",
    "trace",
    "atrace",
    "trace_class",
    "set_default_tracer",
    "get_default_tracer",
    "clear_registry",
]
