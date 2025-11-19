"""HoneyHive Evaluation Module (Deprecated)

⚠️ DEPRECATION WARNING: This module is deprecated and will be removed
in a future version.
Please migrate to the new `honeyhive.experiments` module.

Migration Guide:
    OLD: from honeyhive.evaluation import evaluate, evaluator
    NEW: from honeyhive.experiments import evaluate, evaluator

The experiments module provides:
- Same functionality with improved architecture
- Better tracer integration
- Backend aggregation support
- Enhanced performance with multi-instance tracer pattern

For more details, see:
https://docs.honeyhive.ai/sdk-reference/experiments
"""

# Import wrapper functions from _compat module (these show deprecation warnings)
from honeyhive.evaluation._compat import (
    BaseEvaluator,
    aevaluator,
    compare_runs,
    evaluate,
    evaluator,
    get_run_metrics,
    get_run_result,
    run_experiment,
)

# Import type aliases from experiments module (no warnings for type aliases)
from honeyhive.experiments import AggregatedMetrics as _AggregatedMetrics
from honeyhive.experiments import EvalResult as _EvalResult
from honeyhive.experiments import EvalSettings as _EvalSettings
from honeyhive.experiments import EvaluatorSettings as _EvaluatorSettings
from honeyhive.experiments import ExperimentContext as _ExperimentContext
from honeyhive.experiments import ExperimentResultSummary as _ExperimentResultSummary
from honeyhive.experiments import evaluators as _evaluators_module

# Create backward compatibility aliases (no warnings for simple imports)
EvaluationContext = _ExperimentContext
EvaluationResult = _ExperimentResultSummary
EvaluationRun = _ExperimentResultSummary
EvalResult = _EvalResult
EvalSettings = _EvalSettings
EvaluatorSettings = _EvaluatorSettings

# For backward compatibility with: from honeyhive.evaluation.evaluators import X
evaluators = _evaluators_module


__all__ = [
    # Core evaluation functions
    "evaluate",
    "evaluator",
    "aevaluator",
    "run_experiment",
    # Results
    "get_run_result",
    "get_run_metrics",
    "compare_runs",
    # Data classes (aliases)
    "EvaluationResult",
    "EvaluationContext",
    "EvaluationRun",
    "EvalResult",
    "EvalSettings",
    "EvaluatorSettings",
    # Legacy
    "BaseEvaluator",
    # Sub-module
    "evaluators",
]
