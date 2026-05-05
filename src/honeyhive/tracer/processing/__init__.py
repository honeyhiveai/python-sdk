"""Processing pipeline for HoneyHive tracer spans and data transformation.

This module provides the complete data processing pipeline from span creation
to export, including context management, span processing, and OTLP export.
All components use dynamic logic patterns for flexible, extensible processing.
"""

# Context management
from .context import (
    extract_context_from_carrier,
    get_current_baggage,
    inject_context_into_carrier,
    setup_baggage_context,
    with_distributed_trace_context,
)

# OTLP export
from .otlp_exporter import HoneyHiveOTLPExporter

# Span processing
from .span_processor import HoneyHiveSpanProcessor

__all__ = [
    # Span processing
    "HoneyHiveSpanProcessor",
    # OTLP export
    "HoneyHiveOTLPExporter",
    # Context management
    "extract_context_from_carrier",
    "get_current_baggage",
    "inject_context_into_carrier",
    "setup_baggage_context",
    "with_distributed_trace_context",
]
