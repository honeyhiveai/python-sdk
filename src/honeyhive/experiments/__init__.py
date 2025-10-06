"""Experiments module for HoneyHive SDK.

This module provides experiment management functionality including:
- Experiment run creation and management
- External dataset support with EXT- prefix
- Result aggregation from backend
- Run comparison and analysis
- Evaluator framework integration

The experiments module replaces the legacy evaluation module while maintaining
backward compatibility through deprecation aliases.
"""

from honeyhive.experiments.core import (
    ExperimentContext,
    evaluate,
    run_experiment,
)
from honeyhive.experiments.evaluators import (
    EvalResult,
    EvalSettings,
    EvaluatorSettings,
    aevaluator,
    evaluator,
)
from honeyhive.experiments.models import (
    AggregatedMetrics,
    ExperimentResultSummary,
    ExperimentRunStatus,
    RunComparisonResult,
)
from honeyhive.experiments.results import (
    compare_runs,
    get_run_metrics,
    get_run_result,
)
from honeyhive.experiments.utils import (
    generate_external_datapoint_id,
    generate_external_dataset_id,
    prepare_external_dataset,
    prepare_run_request_data,
)

# Import generated models with experiment terminology aliases
from honeyhive.models.generated import EvaluationRun

# Type aliases for experiment terminology
ExperimentRun = EvaluationRun

__all__ = [
    # Extended models
    "ExperimentRunStatus",
    "AggregatedMetrics",
    "ExperimentResultSummary",
    "RunComparisonResult",
    # Core functionality
    "ExperimentContext",
    "run_experiment",
    "evaluate",
    # Utilities
    "generate_external_dataset_id",
    "generate_external_datapoint_id",
    "prepare_external_dataset",
    "prepare_run_request_data",
    # Results
    "get_run_result",
    "get_run_metrics",
    "compare_runs",
    # Evaluators
    "evaluator",
    "aevaluator",
    "EvalResult",
    "EvalSettings",
    "EvaluatorSettings",
    # Type aliases
    "ExperimentRun",
]
