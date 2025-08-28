"""HoneyHive Python SDK - LLM Observability and Evaluation Platform"""

from .api.client import HoneyHiveClient
from .tracer import HoneyHiveTracer, trace, atrace, trace_class, enrich_span
from .evaluation import evaluate, evaluator, aevaluator
from .utils.config import config
from .utils.dotdict import dotdict
from .utils.logger import get_logger, HoneyHiveLogger

__version__ = "0.1.0"

__all__ = [
    "HoneyHiveClient",
    "HoneyHiveTracer",
    "trace",
    "atrace",
    "trace_class",
    "enrich_span",
    "evaluate",
    "evaluator",
    "aevaluator",
    "config",
    "dotdict",
    "get_logger",
    "HoneyHiveLogger",
]
