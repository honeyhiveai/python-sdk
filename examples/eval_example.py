"""Example: Running evaluations with HoneyHive evaluate() harness.

This example demonstrates how to:
1. Define a function to evaluate per datapoint
2. Create evaluator functions that score outputs
3. Run experiments using the evaluate() harness
4. View aggregated results
"""

import os
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv

from honeyhive.experiments import evaluate

load_dotenv()


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


# =============================================================================
# Evaluation Function
# =============================================================================

def summarize(inputs: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    """Run summarization on a single datapoint.
    
    This is the function that gets executed for each datapoint in the dataset.
    It receives the inputs and ground_truth, and should return the outputs.
    
    Args:
        inputs: The inputs from the datapoint (e.g., {"context": "..."})
        ground_truth: The expected output (e.g., {"answer": "..."})
    
    Returns:
        Dictionary containing the outputs to be evaluated
    """
    context = inputs.get("context", "")
    
    # Call your application logic
    answer = invoke_summary_agent(context)
    
    return {"answer": answer}


# =============================================================================
# Evaluator Functions
# =============================================================================
# Evaluators have signature: evaluator(outputs, inputs, ground_truth) -> float
# They receive the function outputs, original inputs, and ground_truth,
# and should return a numeric score.

def length_score(outputs: Dict[str, Any], inputs: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
    """Check if output has reasonable length (10-500 words).
    
    Returns 1.0 if word count is in range, 0.5 otherwise.
    """
    answer = outputs.get("answer", "")
    word_count = len(answer.split())
    in_range = 10 <= word_count <= 500
    return 1.0 if in_range else 0.5


def content_score(outputs: Dict[str, Any], inputs: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
    """Check if output contains non-empty content.
    
    Returns 1.0 if output has content, 0.0 otherwise.
    """
    answer = outputs.get("answer", "")
    has_content = len(answer.strip()) > 0
    return 1.0 if has_content else 0.0


def keyword_overlap(outputs: Dict[str, Any], inputs: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
    """Calculate keyword overlap between output and ground truth.
    
    Returns a score between 0.0 and 1.0 based on word overlap.
    """
    answer = outputs.get("answer", "").lower()
    expected = ground_truth.get("answer", "").lower()
    
    if not expected:
        return 1.0  # No ground truth to compare
    
    answer_words = set(answer.split())
    expected_words = set(expected.split())
    
    if not expected_words:
        return 1.0
    
    overlap = len(answer_words & expected_words)
    return overlap / len(expected_words)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HoneyHive Evaluation Example")
    print("=" * 60)
    
    # Run the evaluation using the evaluate() harness
    result = evaluate(
        function=summarize,
        dataset=dataset,
        evaluators=[length_score, content_score, keyword_overlap],
        api_key=os.environ.get("HH_API_KEY"),
        project=os.environ.get("HH_PROJECT", "evaluation-example"),
        name=f"summarization-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        verbose=True,
        print_results=True,  # Prints formatted table of results
    )
    
    # Access result summary
    print("\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")
    print(f"Success: {result.success}")
    print(f"Passed: {len(result.passed)} datapoints")
    print(f"Failed: {len(result.failed)} datapoints")
    
    # Access individual metrics
    print("\nAggregated Metrics:")
    for metric_name in result.metrics.list_metrics():
        metric = result.metrics.get_metric(metric_name)
        if hasattr(metric, "aggregate"):
            print(f"  {metric_name}: {metric.aggregate:.4f}")
        else:
            print(f"  {metric_name}: {metric}")
