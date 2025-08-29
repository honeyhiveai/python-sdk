"""HoneyHive Python SDK - LLM Observability and Evaluation Platform"""

from .api.client import HoneyHive
from .evaluation import (
    aevaluator,
    evaluate,
    evaluate_batch,  # New threading function
    evaluate_decorator,  # Main @evaluate decorator
    evaluate_with_evaluators,  # Enhanced with threading
    evaluator,
    get_evaluator,
    BaseEvaluator,
    EvaluationResult,
    EvaluationContext,
    create_evaluation_run,
)
from .tracer import HoneyHiveTracer, atrace, enrich_span, trace, trace_class
from .utils.config import config
from .utils.dotdict import DotDict
from .utils.logger import HoneyHiveLogger, get_logger

__version__ = "0.1.0"

__all__ = [
    "HoneyHive",
    "HoneyHiveTracer",
    "trace",
    "atrace",
    "trace_class",
    "enrich_span",
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
    "config",
    "DotDict",
    "get_logger",
    "HoneyHiveLogger",
]
