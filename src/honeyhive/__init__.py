"""
HoneyHive Python SDK - LLM Observability and Evaluation Platform
"""

# Version must be defined BEFORE imports to avoid circular import issues
__version__ = "1.0.0rc7"

from .api.client import HoneyHive

# Evaluation module (deprecated, for backward compatibility)
from .evaluation import (
    BaseEvaluator,
    EvaluationContext,
    EvaluationResult,
    aevaluator,
    evaluate,
    evaluator,
)

# Experiments module (new, recommended)
from .experiments import (
    AggregatedMetrics,
    EvalResult,
    EvalSettings,
    EvaluatorSettings,
    ExperimentContext,
    ExperimentResultSummary,
    ExperimentRun,
    ExperimentRunStatus,
    RunComparisonResult,
)
from .experiments import aevaluator as exp_aevaluator
from .experiments import (
    compare_runs,
)
from .experiments import evaluate as exp_evaluate  # Core functionality
from .experiments import evaluator as exp_evaluator
from .experiments import (
    get_run_metrics,
    get_run_result,
    run_experiment,
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

# pylint: disable=duplicate-code
# Intentional API export duplication between main __init__.py and tracer/__init__.py
# Both modules need to export the same public API symbols for user convenience
__all__ = [
    # Core client
    "HoneyHive",
    # Tracer
    "HoneyHiveTracer",
    "trace",
    "atrace",
    "trace_class",
    "enrich_session",
    "enrich_span",
    "flush",
    "set_default_tracer",
    # Experiments (new, recommended)
    "run_experiment",
    "ExperimentContext",
    "ExperimentRunStatus",
    "ExperimentResultSummary",
    "AggregatedMetrics",
    "RunComparisonResult",
    "ExperimentRun",
    "get_run_result",
    "get_run_metrics",
    "compare_runs",
    "EvalResult",
    "EvalSettings",
    "EvaluatorSettings",
    # Evaluation (deprecated, for backward compatibility)
    "evaluate",
    "evaluator",
    "aevaluator",
    "BaseEvaluator",
    "EvaluationResult",
    "EvaluationContext",
    # Utilities
    "DotDict",
    "get_logger",
    "HoneyHiveLogger",
]
