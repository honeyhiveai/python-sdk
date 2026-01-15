"""Example: Running evaluations with HoneyHive tracing.

This example demonstrates how to:
1. Initialize a HoneyHive tracer
2. Run evaluation functions with tracing
3. Enrich spans with custom metrics
4. Define evaluator functions to score outputs
"""

import os
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

from honeyhive import HoneyHiveTracer, trace, enrich_span

load_dotenv()

DATASET_NAME = "sample-honeyhive-evaluation"


def invoke_summary_agent(context: str) -> str:
    """Simulate an LLM summarization agent.
    
    In production, this would call an actual LLM API.
    """
    # Hardcoded response for demonstration
    return (
        "The American Shorthair is a pedigreed cat breed, originally known as "
        "the Domestic Shorthair, that was among the first CFA-registered breeds "
        "in 1906 and was renamed in 1966 to distinguish it from random-bred "
        "domestic short-haired cats while highlighting its American origins."
    )


# Dataset with inputs and ground_truth (standard structure)
dataset = [
    {
        "inputs": {
            "context": (
                "The Poodle, called the Pudel in German and the Caniche in French, "
                "is a breed of water dog. The breed is divided into four varieties "
                "based on size, the Standard Poodle, Medium Poodle, Miniature Poodle "
                "and Toy Poodle, although the Medium Poodle is not universally "
                "recognised. They have a distinctive thick, curly coat that comes "
                "in many colours and patterns, with only solid colours recognised "
                "by major breed registries. Poodles are active and intelligent, and "
                "are particularly able to learn from humans. Poodles tend to live "
                "10–18 years, with smaller varieties tending to live longer than "
                "larger ones."
            )
        },
        "ground_truth": {
            "answer": (
                "The Poodle is an intelligent water dog breed that comes in four "
                "size varieties with a distinctive curly coat, known for its "
                "trainability and relatively long lifespan of 10-18 years."
            )
        },
    },
    {
        "inputs": {
            "context": (
                "The American Shorthair is a pedigree cat breed, with a strict "
                "conformation standard, as set by cat fanciers of the breed and "
                "North American cat fancier associations such as The International "
                "Cat Association (TICA) and the CFA. The breed is accepted by all "
                "North American cat registries. Originally known as the Domestic "
                "Shorthair, in 1966 the breed was renamed the American Shorthair "
                'to better represent its "all-American" origins and to differentiate '
                "it from other short-haired breeds. The name American Shorthair also "
                "reinforces the breed's pedigreed status as distinct from the "
                "random-bred non-pedigreed domestic short-haired cats in North "
                "America, which may nevertheless resemble the American Shorthair. "
                "Both the American Shorthair breed and the random-bred cats from "
                "which the breed is derived are sometimes called working cats "
                "because they were used for controlling rodent populations, on ships "
                "and farms. The American Shorthair (then referred to as the Domestic "
                "Shorthair) was among the first five breeds that were registered by "
                "the CFA in 1906."
            )
        },
        "ground_truth": {
            "answer": (
                "The American Shorthair is a pedigreed cat breed, originally known "
                "as the Domestic Shorthair, that was among the first CFA-registered "
                "breeds in 1906 and was renamed in 1966 to distinguish it from "
                "random-bred domestic short-haired cats while highlighting its "
                "American origins."
            )
        },
    },
]


# Define evaluator functions to score outputs
def length_check(output: str, ground_truth: str) -> Dict[str, Any]:
    """Check if output has reasonable length (10-500 words)."""
    word_count = len(output.split())
    in_range = 10 <= word_count <= 500
    
    return {
        "score": 1.0 if in_range else 0.5,
        "word_count": word_count,
        "in_range": in_range,
    }


def has_content(output: str, ground_truth: str) -> Dict[str, Any]:
    """Check if output contains non-empty content."""
    has_text = len(output.strip()) > 0
    return {
        "score": 1.0 if has_text else 0.0,
        "has_content": has_text,
    }


@trace()
def run_evaluation(datapoint: Dict[str, Any]) -> Dict[str, Any]:
    """Run evaluation on a single datapoint with tracing.
    
    Args:
        datapoint: Contains 'inputs' and 'ground_truth' keys
    
    Returns:
        Dictionary with output and evaluation metrics
    """
    inputs = datapoint.get("inputs", {})
    ground_truth = datapoint.get("ground_truth", {})
    context = inputs.get("context", "")
    expected_answer = ground_truth.get("answer", "")
    
    # Enrich span with input metadata
    enrich_span(metadata={
        "input_length": len(context),
        "has_ground_truth": bool(expected_answer),
    })
    
    # Call your application logic
    answer = invoke_summary_agent(context)
    
    # Run evaluators
    length_result = length_check(answer, expected_answer)
    content_result = has_content(answer, expected_answer)
    
    # Enrich span with evaluation metrics
    enrich_span(metrics={
        "length_score": length_result["score"],
        "content_score": content_result["score"],
        "word_count": length_result["word_count"],
    })
    
    return {
        "answer": answer,
        "metrics": {
            "length_check": length_result,
            "has_content": content_result,
        }
    }


def run_all_evaluations(
    tracer: HoneyHiveTracer,
    dataset: List[Dict[str, Any]],
    verbose: bool = True
) -> List[Dict[str, Any]]:
    """Run evaluations on all datapoints in the dataset.
    
    Args:
        tracer: HoneyHiveTracer instance
        dataset: List of datapoints with 'inputs' and 'ground_truth'
        verbose: Whether to print progress
    
    Returns:
        List of evaluation results
    """
    results = []
    
    for i, datapoint in enumerate(dataset):
        if verbose:
            print(f"Processing datapoint {i + 1}/{len(dataset)}...")
        
        result = run_evaluation(datapoint)
        results.append(result)
        
        if verbose:
            metrics = result.get("metrics", {})
            length_score = metrics.get("length_check", {}).get("score", 0)
            content_score = metrics.get("has_content", {}).get("score", 0)
            print(f"  Length score: {length_score:.2f}, Content score: {content_score:.2f}")
    
    return results


def calculate_aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate aggregate metrics across all results."""
    if not results:
        return {}
    
    length_scores = []
    content_scores = []
    
    for result in results:
        metrics = result.get("metrics", {})
        length_scores.append(metrics.get("length_check", {}).get("score", 0))
        content_scores.append(metrics.get("has_content", {}).get("score", 0))
    
    return {
        "avg_length_score": sum(length_scores) / len(length_scores),
        "avg_content_score": sum(content_scores) / len(content_scores),
        "total_datapoints": len(results),
    }


if __name__ == "__main__":
    # Initialize tracer with explicit server URL from environment
    tracer = HoneyHiveTracer.init(
        api_key=os.environ.get("HH_API_KEY"),
        project=os.environ.get("HH_PROJECT", "evaluation-example"),
        session_name=f"{DATASET_NAME}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        source="eval-example",
        server_url=os.environ.get("HH_API_URL"),
    )
    
    print(f"\nStarting evaluation run: {DATASET_NAME}")
    print(f"Dataset size: {len(dataset)} datapoints")
    print("-" * 50)
    
    # Run evaluations
    results = run_all_evaluations(tracer, dataset, verbose=True)
    
    # Calculate and print aggregate metrics
    aggregate = calculate_aggregate_metrics(results)
    
    print("-" * 50)
    print("\nEvaluation Complete!")
    print(f"Total datapoints: {aggregate.get('total_datapoints', 0)}")
    print(f"Avg length score: {aggregate.get('avg_length_score', 0):.2f}")
    print(f"Avg content score: {aggregate.get('avg_content_score', 0):.2f}")
    
    # Flush traces to ensure they're sent
    tracer.force_flush()
    print("\nTraces flushed to HoneyHive.")
