"""Backward compatibility layer for deprecated evaluation module.

This module contains wrapper functions and classes that provide
backward compatibility with the old evaluation module API.

⚠️ DEPRECATION WARNING: This entire module is deprecated.
Please migrate to honeyhive.experiments instead.
"""

import warnings
from typing import Any

# Import actual implementations from experiments module
from honeyhive.experiments import aevaluator as _aevaluator
from honeyhive.experiments import compare_runs as _compare_runs
from honeyhive.experiments import evaluate as _evaluate
from honeyhive.experiments import evaluator as _evaluator
from honeyhive.experiments import get_run_metrics as _get_run_metrics
from honeyhive.experiments import get_run_result as _get_run_result
from honeyhive.experiments import run_experiment as _run_experiment


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Show deprecation warning for old evaluation module usage."""
    warnings.warn(
        f"\n{'='*70}\n"
        f"DEPRECATION WARNING: honeyhive.evaluation.{old_name}\n"
        f"{'='*70}\n"
        f"The 'honeyhive.evaluation' module is deprecated.\n"
        f"Please use 'honeyhive.experiments.{new_name}' instead.\n\n"
        f"Migration:\n"
        f"  OLD: from honeyhive.evaluation import {old_name}\n"
        f"  NEW: from honeyhive.experiments import {new_name}\n\n"
        f"The evaluation module will be removed in version 2.0.0.\n"
        f"{'='*70}",
        DeprecationWarning,
        stacklevel=3,
    )


# Wrap functions with deprecation warnings
def evaluate(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.evaluate instead."""
    _deprecation_warning("evaluate", "evaluate")
    return _evaluate(*args, **kwargs)


def evaluator(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.evaluator instead."""
    if args and callable(args[0]):
        # Used as @evaluator (no parens) - warn only once
        func = args[0]
        _deprecation_warning("evaluator", "evaluator")
        return _evaluator(func)

    # Used as @evaluator(...) - return wrapper
    def wrapper(func: Any) -> Any:
        _deprecation_warning("evaluator", "evaluator")
        return _evaluator(*args, **kwargs)(func)

    return wrapper


def aevaluator(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.aevaluator instead."""
    if args and callable(args[0]):
        # Used as @aevaluator (no parens)
        func = args[0]
        _deprecation_warning("aevaluator", "aevaluator")
        return _aevaluator(func)

    # Used as @aevaluator(...)
    def wrapper(func: Any) -> Any:
        _deprecation_warning("aevaluator", "aevaluator")
        return _aevaluator(*args, **kwargs)(func)

    return wrapper


def run_experiment(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.run_experiment instead."""
    _deprecation_warning("run_experiment", "run_experiment")
    return _run_experiment(*args, **kwargs)


def get_run_result(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.get_run_result instead."""
    _deprecation_warning("get_run_result", "get_run_result")
    return _get_run_result(*args, **kwargs)


def get_run_metrics(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.get_run_metrics instead."""
    _deprecation_warning("get_run_metrics", "get_run_metrics")
    return _get_run_metrics(*args, **kwargs)


def compare_runs(*args: Any, **kwargs: Any) -> Any:
    """Deprecated: Use honeyhive.experiments.compare_runs instead."""
    _deprecation_warning("compare_runs", "compare_runs")
    return _compare_runs(*args, **kwargs)


# Legacy class names (keep for imports but don't actively use)
class BaseEvaluator:  # pylint: disable=too-few-public-methods
    """Deprecated: Legacy evaluator base class. Use @evaluator decorator instead."""

    def __init__(self, *args: Any, **kwargs: Any):  # pylint: disable=unused-argument
        """Initialize deprecated BaseEvaluator (shows warning)."""
        warnings.warn(
            "BaseEvaluator is deprecated. Use @evaluator decorator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
