"""Instrumentation framework for HoneyHive tracing.

This module provides user-facing instrumentation capabilities including
decorators, enrichment, and tracer initialization. All components use
dynamic logic patterns for flexible, configuration-driven instrumentation.
"""

# Decorators
from .decorators import atrace, trace, trace_class

# Enrichment
from .enrichment import enrich_span, enrich_span_core, enrich_span_unified

# Initialization
from .initialization import initialize_tracer_instance

__all__ = [
    # Decorators
    "atrace",
    "trace",
    "trace_class",
    # Enrichment
    "enrich_span",
    "enrich_span_core",
    "enrich_span_unified",
    # Initialization
    "initialize_tracer_instance",
]
