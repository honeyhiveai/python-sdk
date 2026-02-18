"""
HoneyHive Python SDK - LLM Observability and Evaluation Platform
"""

# Version must be defined BEFORE imports to avoid circular import issues
__version__ = "1.0.0rc9.post2"

# Bundled package version (used by honeyhive-bundled PyPI package)
__version_bundled__ = "1.1.0a1"

# Main API client
from .api import HoneyHive

# Tracer (if available - may have additional dependencies)
try:
    from .tracer import (
        HoneyHiveTracer,
        atrace,
        clear_baggage_context,
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

# Config module (per-instance configuration)
try:
    from .config import TracerConfig as config  # backwards-compat alias

    _CONFIG_AVAILABLE = True
except ImportError:
    _CONFIG_AVAILABLE = False

# Evaluation/experiments module (if available)
try:
    from .evaluation._compat import aevaluator, evaluator
    from .evaluation.evaluators import BaseEvaluator
    from .experiments import evaluate

    _EVALUATION_AVAILABLE = True
except ImportError:
    _EVALUATION_AVAILABLE = False

# Utility imports (backwards compatibility)
try:
    from .utils.dotdict import DotDict
    from .utils.logger import get_logger

    _UTILS_AVAILABLE = True
except ImportError:
    _UTILS_AVAILABLE = False

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
            "clear_baggage_context",
            "enrich_session",
            "enrich_span",
            "flush",
            "set_default_tracer",
        ]
    )

# Add config export if available
if _CONFIG_AVAILABLE:
    __all__.append("config")

# Add evaluation exports if available
if _EVALUATION_AVAILABLE:
    __all__.extend(
        [
            "evaluate",
            "evaluator",
            "aevaluator",
            "BaseEvaluator",
        ]
    )

# Add utility exports if available
if _UTILS_AVAILABLE:
    __all__.extend(
        [
            "DotDict",
            "get_logger",
        ]
    )
