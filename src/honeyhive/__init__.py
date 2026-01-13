"""
HoneyHive Python SDK - LLM Observability and Evaluation Platform
"""

# Version must be defined BEFORE imports to avoid circular import issues
__version__ = "1.0.0rc8"

# Main API client
from .api import HoneyHive

# Tracer (if available - may have additional dependencies)
try:
    from .tracer import (
        HoneyHiveTracer,
        atrace,
        enrich_session,
        enrich_span,
        flush,
        set_default_tracer,
        trace,
        trace_class,
    )

    _TRACER_AVAILABLE = True
except ImportError:
    _TRACER_AVAILABLE = False

__all__ = [
    # Core client
    "HoneyHive",
]

# Add tracer exports if available
if _TRACER_AVAILABLE:
    __all__.extend(
        [
            "HoneyHiveTracer",
            "trace",
            "atrace",
            "trace_class",
            "enrich_session",
            "enrich_span",
            "flush",
            "set_default_tracer",
        ]
    )
