"""Evaluation utilities for HoneyHive."""

# pylint: disable=duplicate-code
# This module contains legitimate code duplication with other modules:
# 1. API export lists (__all__) - intentionally duplicated for consistent public APIs
# 2. Pydantic field validators - shared validation logic across similar model classes
# 3. ErrorContext creation patterns - standard parameter structures for error handling

import asyncio
import contextvars
import functools
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from honeyhive.api.client import HoneyHive
from honeyhive.models.generated import (
    CreateRunRequest,
    EvaluationRun,
)

# Config import removed - not used in this module

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of an evaluation."""

    score: float
    metrics: Dict[str, Any]
    feedback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: Optional[str] = None


@dataclass
class EvaluationContext:
    """Context for evaluation runs."""

    project: str
    source: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseEvaluator:
    """Base class for custom evaluators."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize the evaluator."""
        self.name = name
        self.__name__ = name  # Add __name__ attribute for compatibility
        self.config = kwargs

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate the given inputs and outputs."""
        raise NotImplementedError("Subclasses must implement evaluate method")

    def __call__(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make the evaluator callable."""
        return self.evaluate(inputs, outputs, ground_truth, **kwargs)


class ExactMatchEvaluator(BaseEvaluator):  # pylint: disable=too-few-public-methods
    """Evaluator for exact string matching."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the exact match evaluator."""
        super().__init__("exact_match", **kwargs)

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate exact match between expected and actual outputs."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")

        # Handle different types
        if isinstance(expected, str) and isinstance(actual, str):
            score = float(expected.strip().lower() == actual.strip().lower())
        else:
            score = float(expected == actual)

        return {
            "exact_match": score,
            "expected": expected,
            "actual": actual,
        }


class F1ScoreEvaluator(BaseEvaluator):  # pylint: disable=too-few-public-methods
    """Evaluator for F1 score calculation."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the F1 score evaluator."""
        super().__init__("f1_score", **kwargs)

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate F1 score between expected and actual outputs."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")

        if not isinstance(expected, str) or not isinstance(actual, str):
            return {"f1_score": 0.0, "error": "Both inputs must be strings"}

        score = self._compute_f1_score(actual, expected)
        return {"f1_score": score}

    def _compute_f1_score(self, prediction: str, ground_truth: str) -> float:
        """Compute F1 score between prediction and ground truth."""
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


class LengthEvaluator(BaseEvaluator):  # pylint: disable=too-few-public-methods
    """Evaluator for response length analysis."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the length evaluator."""
        super().__init__("length", **kwargs)

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate response length metrics."""
        response = outputs.get("response", "")

        if isinstance(response, str):
            char_count = len(response)
            word_count = len(response.split())
            line_count = len(response.splitlines())
        else:
            char_count = len(str(response))
            word_count = 1
            line_count = 1

        return {
            "char_count": char_count,
            "word_count": word_count,
            "line_count": line_count,
        }


class SemanticSimilarityEvaluator(BaseEvaluator):
    # pylint: disable=too-few-public-methods
    """Evaluator for semantic similarity using basic heuristics."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the semantic similarity evaluator."""
        super().__init__("semantic_similarity", **kwargs)

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate semantic similarity between expected and actual outputs."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")

        if not isinstance(expected, str) or not isinstance(actual, str):
            return {"semantic_similarity": 0.0, "error": "Both inputs must be strings"}

        # Simple semantic similarity using word overlap and structure
        score = self._compute_semantic_similarity(actual, expected)
        return {"semantic_similarity": score}

    def _compute_semantic_similarity(self, prediction: str, ground_truth: str) -> float:
        """Compute semantic similarity score."""
        pred_words = set(prediction.lower().split())
        gt_words = set(ground_truth.lower().split())

        if not pred_words or not gt_words:
            return 0.0

        # Word overlap
        overlap = len(pred_words & gt_words)
        total_unique = len(pred_words | gt_words)

        # Structure similarity (simple heuristic)
        pred_sentences = len(prediction.split("."))
        gt_sentences = len(ground_truth.split("."))
        structure_similarity = 1.0 - abs(pred_sentences - gt_sentences) / max(
            pred_sentences, gt_sentences, 1
        )

        # Combined score
        word_similarity = overlap / total_unique if total_unique > 0 else 0.0
        final_score = (word_similarity * 0.7) + (structure_similarity * 0.3)

        return min(1.0, max(0.0, final_score))


# Built-in evaluators
BUILTIN_EVALUATORS = {
    "exact_match": ExactMatchEvaluator,
    "f1_score": F1ScoreEvaluator,
    "length": LengthEvaluator,
    "semantic_similarity": SemanticSimilarityEvaluator,
}


def get_evaluator(evaluator_name: str, **kwargs: Any) -> BaseEvaluator:
    """Get a built-in evaluator by name."""
    if evaluator_name not in BUILTIN_EVALUATORS:
        raise ValueError(f"Unknown evaluator: {evaluator_name}")

    return BUILTIN_EVALUATORS[evaluator_name](**kwargs)


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

    # Create inputs/outputs dict for evaluators
    inputs = {"expected": ground_truth}
    outputs = {"response": prediction}

    # Run each metric
    for metric in metrics:
        if metric in BUILTIN_EVALUATORS:
            eval_instance = BUILTIN_EVALUATORS[metric]()
            try:
                metric_result = eval_instance.evaluate(inputs, outputs)
                result_metrics.update(metric_result)
            except Exception as e:
                logger.warning("Failed to compute %s: %s", metric, e)
                result_metrics[metric] = 0.0

    # Compute overall score (average of numeric metrics)
    numeric_metrics = [
        v for v in result_metrics.values() if isinstance(v, (int, float))
    ]
    overall_score = (
        sum(numeric_metrics) / len(numeric_metrics) if numeric_metrics else 0.0
    )

    # Ensure score is in 0-1 range
    overall_score = max(0.0, min(1.0, overall_score))

    return EvaluationResult(score=overall_score, metrics=result_metrics, **kwargs)


def evaluate_decorator(
    evaluators: Optional[List[Union[str, BaseEvaluator, Callable]]] = None,
    **kwargs: Any,
) -> Callable[[Callable], Callable]:
    """Decorator for functions that should be evaluated.

    This is the main @evaluate decorator that can be used with evaluators.

    Args:
        evaluators: List of evaluators to apply
        **kwargs: Additional evaluation parameters
    """

    def decorator(func: Callable) -> Callable:
        # Check if function is async
        if asyncio.iscoroutinefunction(func):  # pylint: disable=no-else-return

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **func_kwargs: Any) -> Any:
                # Execute the async function first
                result = await func(*args, **func_kwargs)

                # If we have evaluators and the first argument is a dict (inputs)
                if evaluators and args and isinstance(args[0], dict):
                    inputs = args[0]

                    # Convert result to outputs format if it's not already
                    if isinstance(result, dict):
                        outputs = result
                    else:
                        outputs = {"response": result}

                    # Run evaluation
                    try:
                        eval_result = evaluate_with_evaluators(
                            evaluators=evaluators,
                            inputs=inputs,
                            outputs=outputs,
                            **kwargs,
                        )

                        # Store evaluation result in metadata if result is a dict
                        if isinstance(result, dict):
                            if "evaluation" not in result:
                                result["evaluation"] = {}
                            result["evaluation"]["result"] = eval_result
                        else:
                            # If result is not a dict, we can't easily attach evaluation
                            # but we could log it or store it elsewhere
                            logger.info("Evaluation result: %s", eval_result)

                    except Exception as e:
                        logger.warning("Evaluation failed: %s", e)

                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **func_kwargs: Any) -> Any:
                # Execute the function first
                result = func(*args, **func_kwargs)

                # If we have evaluators and the first argument is a dict (inputs)
                if evaluators and args and isinstance(args[0], dict):
                    inputs = args[0]

                    # Convert result to outputs format if it's not already
                    if isinstance(result, dict):
                        outputs = result
                    else:
                        outputs = {"response": result}

                    # Run evaluation
                    try:
                        eval_result = evaluate_with_evaluators(
                            evaluators=evaluators,
                            inputs=inputs,
                            outputs=outputs,
                            **kwargs,
                        )

                        # Store evaluation result in metadata if result is a dict
                        if isinstance(result, dict):
                            if "evaluation" not in result:
                                result["evaluation"] = {}
                            result["evaluation"]["result"] = eval_result
                        else:
                            # If result is not a dict, we can't easily attach evaluation
                            # but we could log it or store it elsewhere
                            logger.info("Evaluation result: %s", eval_result)

                    except Exception as e:
                        logger.warning("Evaluation failed: %s", e)

                return result

            return sync_wrapper

    return decorator


def evaluator(
    _name: Optional[str] = None, _session_id: Optional[str] = None, **_kwargs: Any
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
            # Execute evaluation
            result = func(*args, **kwargs)

            # Note: Event creation for evaluation functions is disabled to avoid \
            # type issues
            # The evaluation functionality works independently of event creation

            return result

        return wrapper

    return decorator


def aevaluator(
    _name: Optional[str] = None, _session_id: Optional[str] = None, **_kwargs: Any
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
            # Execute evaluation
            result = await func(*args, **kwargs)

            # Note: Event creation for evaluation functions is disabled to avoid \
            # type issues
            # The evaluation functionality works independently of event creation

            return result

        return wrapper

    return decorator


def evaluate_with_evaluators(
    # pylint: disable=too-many-arguments,too-many-branches
    evaluators: List[Union[str, BaseEvaluator, Callable]],
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    *,
    ground_truth: Optional[Dict[str, Any]] = None,
    context: Optional[EvaluationContext] = None,
    max_workers: int = 1,
    run_concurrently: bool = True,
) -> EvaluationResult:
    """Evaluate outputs using multiple evaluators with optional threading support.

    Args:
        evaluators: List of evaluators to apply
        inputs: Input data for evaluation
        outputs: Output data to evaluate
        ground_truth: Ground truth data for comparison
        context: Evaluation context
        max_workers: Maximum number of worker threads for parallel evaluation
        run_concurrently: Whether to run evaluators concurrently

    Returns:
        EvaluationResult with aggregated metrics
    """
    if not evaluators:
        return EvaluationResult(
            score=0.0,
            metrics={},
            metadata={
                "inputs": inputs,
                "outputs": outputs,
                "ground_truth": ground_truth,
                "context": context.__dict__ if context else None,
            },
        )

    metrics: Dict[str, Any] = {}

    if run_concurrently and max_workers > 1 and len(evaluators) > 1:
        # Run evaluators concurrently using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit evaluation tasks
            futures = []
            for eval_item in evaluators:
                eval_func = _get_evaluator_function(eval_item)

                # Create context for each thread
                ctx = contextvars.copy_context()
                future = executor.submit(
                    ctx.run,
                    functools.partial(
                        _run_single_evaluator, eval_func, inputs, outputs, ground_truth
                    ),
                )
                futures.append((eval_item, future))

            # Collect results
            for eval_item, future in futures:
                try:
                    result = future.result()
                    if isinstance(eval_item, str):
                        evaluator_name = eval_item
                    elif isinstance(eval_item, BaseEvaluator):
                        evaluator_name = eval_item.name
                    else:
                        evaluator_name = getattr(eval_item, "__name__", str(eval_item))

                    metrics[evaluator_name] = result
                except Exception as e:
                    logger.warning("Evaluator %s failed: %s", eval_item, e)
                    if isinstance(eval_item, str):
                        evaluator_name = eval_item
                    elif isinstance(eval_item, BaseEvaluator):
                        evaluator_name = eval_item.name
                    else:
                        evaluator_name = getattr(eval_item, "__name__", str(eval_item))
                    metrics[evaluator_name] = None
    else:
        # Run evaluators sequentially
        for eval_item in evaluators:
            try:
                eval_func = _get_evaluator_function(eval_item)

                if isinstance(eval_item, str):
                    evaluator_name = eval_item
                elif isinstance(eval_item, BaseEvaluator):
                    evaluator_name = eval_item.name
                else:
                    evaluator_name = getattr(eval_item, "__name__", str(eval_item))

                result = _run_single_evaluator(eval_func, inputs, outputs, ground_truth)
                metrics[evaluator_name] = result
            except Exception as e:
                logger.warning("Evaluator %s failed: %s", eval_item, e)
                if isinstance(eval_item, str):
                    evaluator_name = eval_item
                elif isinstance(eval_item, BaseEvaluator):
                    evaluator_name = eval_item.name
                else:
                    evaluator_name = getattr(eval_item, "__name__", str(eval_item))
                metrics[evaluator_name] = None

    # Calculate overall score
    valid_scores = []
    for metric_result in metrics.values():
        if metric_result is not None and isinstance(metric_result, dict):
            # Extract numeric scores from metric result dictionaries
            for value in metric_result.values():
                if isinstance(value, (int, float)) and value > 0:
                    valid_scores.append(value)
        elif isinstance(metric_result, (int, float)) and metric_result > 0:
            valid_scores.append(metric_result)

    if valid_scores:
        overall_score = sum(valid_scores) / len(valid_scores)
        # Normalize score to 0-1 range
        overall_score = max(0.0, min(1.0, overall_score))
    else:
        overall_score = 0.0

    return EvaluationResult(
        score=overall_score,
        metrics=metrics,
        metadata={
            "inputs": inputs,
            "outputs": outputs,
            "ground_truth": ground_truth,
            "context": context.__dict__ if context else None,
        },
    )


def _run_single_evaluator(
    evaluator_func: Callable,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    ground_truth: Optional[Dict[str, Any]] = None,
) -> Any:
    """Run a single evaluator function in a thread-safe manner.

    Args:
        evaluator_func: The evaluator function to run
        inputs: Input data
        outputs: Output data
        ground_truth: Ground truth data

    Returns:
        Evaluation result from the evaluator
    """
    try:
        if ground_truth is not None:
            return evaluator_func(inputs, outputs, ground_truth)
        return evaluator_func(inputs, outputs)
    except Exception as e:
        logger.error("Evaluator %s failed: %s", evaluator_func.__name__, e)
        raise


def _get_evaluator_function(eval_item: Union[str, BaseEvaluator, Callable]) -> Callable:
    """Get the evaluator function from different evaluator types.

    Args:
        evaluator: Evaluator (string name, BaseEvaluator instance, or callable)

    Returns:
        Callable evaluator function
    """
    if isinstance(eval_item, str):
        return get_evaluator(eval_item)
    if isinstance(eval_item, BaseEvaluator):
        return eval_item.evaluate
    return eval_item


def evaluate_batch(
    evaluators: List[Union[str, BaseEvaluator, Callable]],
    dataset: List[Dict[str, Any]],
    max_workers: int = 4,
    run_concurrently: bool = True,
    context: Optional[EvaluationContext] = None,
) -> List[EvaluationResult]:
    """Evaluate a batch of data points using multiple evaluators with threading support.

    Args:
        evaluators: List of evaluators to apply
        dataset: List of data points, each containing inputs, outputs, and \
        optional ground_truth
        max_workers: Maximum number of worker threads for parallel evaluation
        run_concurrently: Whether to run evaluations concurrently
        context: Evaluation context

    Returns:
        List of EvaluationResult objects
    """
    if not dataset:
        return []

    if run_concurrently and max_workers > 1 and len(dataset) > 1:
        # Run evaluations concurrently using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit evaluation tasks
            futures = []
            for data_point in dataset:
                inputs = data_point.get("inputs", {})
                outputs = data_point.get("outputs", {})
                ground_truth = data_point.get("ground_truth")

                # Create context for each thread
                ctx = contextvars.copy_context()
                future = executor.submit(
                    ctx.run,
                    functools.partial(
                        evaluate_with_evaluators,
                        evaluators=evaluators,
                        inputs=inputs,
                        outputs=outputs,
                        ground_truth=ground_truth,
                        context=context,
                        max_workers=1,  # Single evaluator per thread
                        run_concurrently=False,  # Sequential within thread
                    ),
                )
                futures.append(future)

            # Collect results
            results = []
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.warning("Batch evaluation failed: %s", e)
                    # Create empty result for failed evaluation
                    results.append(
                        EvaluationResult(
                            score=0.0,
                            metrics={},
                            metadata={
                                "inputs": {},
                                "outputs": {},
                                "ground_truth": {},
                                "context": context.__dict__ if context else None,
                            },
                        )
                    )

            return results
    else:
        # Run evaluations sequentially
        results = []
        for data_point in dataset:
            try:
                inputs = data_point.get("inputs", {})
                outputs = data_point.get("outputs", {})
                ground_truth = data_point.get("ground_truth")

                result = evaluate_with_evaluators(
                    evaluators=evaluators,
                    inputs=inputs,
                    outputs=outputs,
                    ground_truth=ground_truth,
                    context=context,
                    max_workers=1,
                    run_concurrently=False,
                )
                results.append(result)
            except Exception as e:
                logger.warning("Batch evaluation failed: %s", e)
                # Create empty result for failed evaluation
                results.append(
                    EvaluationResult(
                        score=0.0,
                        metrics={},
                        metadata={
                            "inputs": {},
                            "outputs": {},
                            "ground_truth": {},
                            "context": context.__dict__ if context else None,
                        },
                    )
                )

        return results


def create_evaluation_run(
    name: str,
    project: str,
    _results: List[EvaluationResult],
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[HoneyHive] = None,
) -> Optional[EvaluationRun]:
    """Create an evaluation run in HoneyHive.

    Args:
        name: Name of the evaluation run
        project: Project name
        results: List of evaluation results
        metadata: Additional metadata
        client: HoneyHive client instance

    Returns:
        Created evaluation run or None if failed
    """
    if client is None:
        try:
            client = HoneyHive()
        except Exception as e:
            logger.warning("Could not create HoneyHive client: %s", e)
            return None

    try:
        # Aggregate results (commented out for future use)
        # total_score = sum(r.score for r in results)

        # Prepare run data - CreateRunRequest expects specific fields
        # For now, we'll create a minimal request with required fields
        # Note: This is a simplified version - in production you'd want proper UUIDs
        try:
            # Create run request with minimal required data
            run_request = CreateRunRequest(
                name=name,
                project=project,  # This should be a valid UUID string
                event_ids=[],  # Empty list for now - in production you'd want \
                # actual event IDs
                dataset_id=None,
                datapoint_ids=None,
                configuration=None,
                status=None,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.warning("Could not create CreateRunRequest: %s", e)
            # Fallback: return None instead of crashing
            return None

        # Submit to API
        response = client.evaluations.create_run(run_request)

        logger.info(
            "Created evaluation run: %s",
            response.evaluation.run_id if response.evaluation else "unknown",
        )
        return response.evaluation

    except Exception as e:
        logger.error("Failed to create evaluation run: %s", e)
        return None


# Legacy function for backward compatibility
def _compute_f1_score(prediction: str, ground_truth: str) -> float:
    """Compute F1 score between prediction and ground truth.

    Args:
        prediction: Model prediction
        ground_truth: Ground truth value

    Returns:
        F1 score between 0 and 1
    """
    f1_evaluator = F1ScoreEvaluator()
    result = f1_evaluator.evaluate({"expected": ground_truth}, {"response": prediction})
    f1_score = result.get("f1_score", 0.0)
    if isinstance(f1_score, (int, float)):
        return float(f1_score)
    return 0.0
