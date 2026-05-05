"""HoneyHive OpenTelemetry tracer module.

This module provides the complete public API for HoneyHive tracing functionality.
Users should import from this module rather than internal submodules for stability.

Example:
    from honeyhive.tracer import HoneyHiveTracer, trace, enrich_span

    tracer = HoneyHiveTracer.init(api_key="...", project="...")

    @trace(tracer=tracer)
    def my_function():
        return "Hello, World!"
"""

from .core import HoneyHiveTracer
from .instrumentation.decorators import atrace, trace, trace_class
from .instrumentation.enrichment import enrich_span
from .integration.compatibility import enrich_session
from .integration.detection import get_global_provider, set_global_provider
from .lifecycle import graceful_shutdown_all, shutdown_tracer
from .lifecycle.flush import force_flush_tracer as flush
from .processing.span_processor import HoneyHiveSpanProcessor
from .registry import clear_registry, get_default_tracer, set_default_tracer

__all__ = [
    # Core tracer class
    "HoneyHiveTracer",
    # Decorators
    "trace",
    "atrace",
    "trace_class",
    # Span enrichment
    "enrich_session",
    "enrich_span",
    # Registry management
    "set_default_tracer",
    "get_default_tracer",
    "clear_registry",
    # Lifecycle management
    "shutdown_tracer",
    "graceful_shutdown_all",
    "flush",
    # OpenTelemetry provider management
    "set_global_provider",
    "get_global_provider",
    # Advanced components
    "HoneyHiveSpanProcessor",
]
