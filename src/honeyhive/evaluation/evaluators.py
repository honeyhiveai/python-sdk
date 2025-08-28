"""Evaluation utilities for HoneyHive."""

import asyncio
import functools
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass

from ..api.client import HoneyHiveClient
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
    **kwargs
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
        result_metrics["exact_match"] = float(prediction.strip().lower() == ground_truth.strip().lower())
    
    # Compute F1 score (simplified)
    if "f1_score" in metrics:
        result_metrics["f1_score"] = _compute_f1_score(prediction, ground_truth)
    
    # Compute overall score (average of all metrics)
    overall_score = sum(result_metrics.values()) / len(result_metrics) if result_metrics else 0.0
    
    return EvaluationResult(
        score=overall_score,
        metrics=result_metrics,
        **kwargs
    )


def evaluator(
    name: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
):
    """Decorator for synchronous evaluation functions.
    
    Args:
        name: Evaluation name
        session_id: Session ID for tracing
        **kwargs: Additional evaluation parameters
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get evaluation name
            eval_name = name or f"{func.__module__}.{func.__qualname__}"
            
            # Execute evaluation
            result = func(*args, **kwargs)
            
            # Send evaluation event if tracer is available
            try:
                from ..tracer import HoneyHiveTracer
                if HoneyHiveTracer._instance:
                    tracer = HoneyHiveTracer._instance
                    
                    # Create evaluation event
                    event = CreateEventRequest(
                        project=tracer.project,
                        source=tracer.source,
                        event_name=eval_name,
                        event_type="evaluation",
                        session_id=session_id,
                        inputs={"args": args, "kwargs": kwargs},
                        outputs={"result": result.__dict__ if hasattr(result, '__dict__') else result},
                        metrics=getattr(result, 'metrics', {}),
                        feedback=getattr(result, 'feedback', None),
                        metadata=getattr(result, 'metadata', {}),
                    )
                    
                    # Send event
                    if not tracer.test_mode:
                        client = HoneyHiveClient(api_key=tracer.api_key)
                        client.events.create_event(event)
            
            except Exception as e:
                # Silently fail to avoid breaking evaluation
                pass
            
            return result
        
        return wrapper
    
    return decorator


def aevaluator(
    name: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
):
    """Decorator for asynchronous evaluation functions.
    
    Args:
        name: Evaluation name
        session_id: Session ID for tracing
        **kwargs: Additional evaluation parameters
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get evaluation name
            eval_name = name or f"{func.__module__}.{func.__qualname__}"
            
            # Execute evaluation
            result = await func(*args, **kwargs)
            
            # Send evaluation event if tracer is available
            try:
                from ..tracer import HoneyHiveTracer
                if HoneyHiveTracer._instance:
                    tracer = HoneyHiveTracer._instance
                    
                    # Create evaluation event
                    event = CreateEventRequest(
                        project=tracer.project,
                        source=tracer.source,
                        event_name=eval_name,
                        event_type="evaluation",
                        session_id=session_id,
                        inputs={"args": args, "kwargs": kwargs},
                        outputs={"result": result.__dict__ if hasattr(result, '__dict__') else result},
                        metrics=getattr(result, 'metrics', {}),
                        feedback=getattr(result, 'feedback', None),
                        metadata=getattr(result, 'metadata', {}),
                    )
                    
                    # Send event
                    if not tracer.test_mode:
                        client = HoneyHiveClient(api_key=tracer.api_key)
                        await client.events.create_event_async(event)
            
            except Exception as e:
                # Silently fail to avoid breaking evaluation
                pass
            
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
