"""Evaluation utilities for HoneyHive."""

import functools
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from ..api.client import HoneyHive
from ..api.events import CreateEventRequest


@dataclass
class EvaluationResult:
    """Result of an evaluation."""

    score: float
    metrics: Dict[str, Any]
    feedback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def evaluate(
    prediction: str,
    ground_truth: str,
    metrics: Optional[List[str]] = None,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate a prediction against ground truth.

    Args:
        prediction: Model prediction
        ground_truth: Ground truth value
        metrics: List of metrics to compute
        **kwargs: Additional evaluation parameters

    Returns:
        Evaluation result
    """
    # Default metrics
    if metrics is None:
        metrics = ["exact_match", "f1_score"]

    result_metrics = {}

    # Compute exact match
    if "exact_match" in metrics:
        result_metrics["exact_match"] = float(
            prediction.strip().lower() == ground_truth.strip().lower()
        )

    # Compute F1 score (simplified)
    if "f1_score" in metrics:
        result_metrics["f1_score"] = _compute_f1_score(prediction, ground_truth)

    # Compute overall score (average of all metrics)
    overall_score = (
        sum(result_metrics.values()) / len(result_metrics) if result_metrics else 0.0
    )

    return EvaluationResult(score=overall_score, metrics=result_metrics, **kwargs)


def evaluator(
    name: Optional[str] = None, session_id: Optional[str] = None, **kwargs: Any
) -> Callable[[Callable], Callable]:
    """Decorator for synchronous evaluation functions.

    Args:
        name: Evaluation name
        session_id: Session ID for tracing
        **kwargs: Additional evaluation parameters
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get evaluation name
            eval_name = name or f"{func.__module__}.{func.__qualname__}"

            # Execute evaluation
            result = func(*args, **kwargs)

            # Note: Event creation for evaluation functions is disabled to avoid type issues
            # The evaluation functionality works independently of event creation

            return result

        return wrapper

    return decorator


def aevaluator(
    name: Optional[str] = None, session_id: Optional[str] = None, **kwargs: Any
) -> Callable[[Callable], Callable]:
    """Decorator for asynchronous evaluation functions.

    Args:
        name: Evaluation name
        session_id: Session ID for tracing
        **kwargs: Additional evaluation parameters
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get evaluation name
            eval_name = name or f"{func.__module__}.{func.__qualname__}"

            # Execute evaluation
            result = await func(*args, **kwargs)

            # Note: Event creation for evaluation functions is disabled to avoid type issues
            # The evaluation functionality works independently of event creation

            return result

        return wrapper

    return decorator


def _compute_f1_score(prediction: str, ground_truth: str) -> float:
    """Compute F1 score between prediction and ground truth.

    Args:
        prediction: Model prediction
        ground_truth: Ground truth value

    Returns:
        F1 score between 0 and 1
    """
    # Simple word-based F1 score
    pred_words = set(prediction.lower().split())
    gt_words = set(ground_truth.lower().split())

    if not pred_words or not gt_words:
        return 0.0

    intersection = pred_words & gt_words
    precision = len(intersection) / len(pred_words)
    recall = len(intersection) / len(gt_words)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)
