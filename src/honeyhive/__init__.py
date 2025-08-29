"""HoneyHive Python SDK - LLM Observability and Evaluation Platform"""

from .api.client import HoneyHive
from .evaluation import aevaluator, evaluate, evaluator
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
    "evaluator",
    "aevaluator",
    "config",
    "DotDict",
    "get_logger",
    "HoneyHiveLogger",
]
