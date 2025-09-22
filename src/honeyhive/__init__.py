"""HoneyHive Python SDK - LLM Observability and Evaluation Platform"""

from .api.client import HoneyHive

# Global config removed - use per-instance configuration instead
from .evaluation import evaluate_batch  # New threading function
from .evaluation import evaluate_decorator  # Main @evaluate decorator
from .evaluation import evaluate_with_evaluators  # Enhanced with threading
from .evaluation import (
    BaseEvaluator,
    EvaluationContext,
    EvaluationResult,
    aevaluator,
    create_evaluation_run,
    evaluate,
    evaluator,
    get_evaluator,
)
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

# Global config removed - use per-instance configuration:
# HoneyHiveTracer(api_key="...", project="...") or
# HoneyHiveTracer(config=TracerConfig(...))
from .utils.dotdict import DotDict
from .utils.logger import HoneyHiveLogger, get_logger

__version__ = "0.1.0rc2"

# pylint: disable=duplicate-code
# Intentional API export duplication between main __init__.py and tracer/__init__.py
# Both modules need to export the same public API symbols for user convenience
__all__ = [
    "HoneyHive",
    "HoneyHiveTracer",
    "trace",
    "atrace",
    "trace_class",
    "enrich_session",
    "enrich_span",
    "flush",
    "set_default_tracer",
    "evaluate",
    "evaluate_batch",  # New threading function
    "evaluate_decorator",  # Main @evaluate decorator
    "evaluate_with_evaluators",  # Enhanced with threading
    "evaluator",
    "aevaluator",
    "get_evaluator",
    "BaseEvaluator",
    "EvaluationResult",
    "EvaluationContext",
    "create_evaluation_run",
    # "config" removed - use per-instance configuration instead
    "DotDict",
    "get_logger",
    "HoneyHiveLogger",
]
