"""HoneyHive Evaluation Module

This module provides a comprehensive evaluation framework for LLM outputs,
including built-in evaluators, custom evaluator support, threading support,
and integration with the HoneyHive API for storing evaluation results.
"""

from .evaluators import (
    BaseEvaluator,
    EvaluationContext,
    EvaluationResult,
    ExactMatchEvaluator,
    F1ScoreEvaluator,
    LengthEvaluator,
    SemanticSimilarityEvaluator,
    aevaluator,
    create_evaluation_run,
    evaluate,
    evaluate_batch,  # New threading function
    evaluate_decorator,  # Main @evaluate decorator
    evaluate_with_evaluators,  # Enhanced with threading
    evaluator,
    get_evaluator,
)

__all__ = [
    # Core evaluation functions
    "evaluate",
    "evaluate_decorator",  # Main @evaluate decorator
    "evaluate_with_evaluators",  # Enhanced with threading
    "evaluate_batch",  # New threading function
    "evaluator",
    "aevaluator",
    # Data classes
    "EvaluationResult",
    "EvaluationContext",
    # Base evaluator class
    "BaseEvaluator",
    # Built-in evaluators
    "ExactMatchEvaluator",
    "F1ScoreEvaluator",
    "LengthEvaluator",
    "SemanticSimilarityEvaluator",
    # Utility functions
    "get_evaluator",
    "create_evaluation_run",
]
