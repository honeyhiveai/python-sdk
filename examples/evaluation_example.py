"""Evaluation example for HoneyHive Python SDK."""

import asyncio
from honeyhive import evaluate, evaluator, aevaluator, HoneyHiveTracer
from honeyhive.evaluation.evaluators import EvaluationResult


# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key", project="Evaluation Example", source="example"
)


def basic_evaluation():
    """Basic evaluation example."""
    print("=== Basic Evaluation ===")

    # Simple evaluation
    result = evaluate(
        prediction="The weather is sunny today",
        ground_truth="It's sunny today",
        metrics=["exact_match", "f1_score"],
    )

    print(f"Prediction: The weather is sunny today")
    print(f"Ground Truth: It's sunny today")
    print(f"Overall Score: {result.score:.3f}")
    print(f"Metrics: {result.metrics}")
    print()


def custom_evaluation():
    """Custom evaluation example."""
    print("=== Custom Evaluation ===")

    @evaluator(name="custom-evaluator", session_id="example-session")
    def custom_eval(prediction, ground_truth):
        """Custom evaluation function."""
        # Simple word overlap metric
        pred_words = set(prediction.lower().split())
        gt_words = set(ground_truth.lower().split())

        if not pred_words or not gt_words:
            return EvaluationResult(
                score=0.0, metrics={"word_overlap": 0.0}, feedback="No words to compare"
            )

        overlap = len(pred_words & gt_words)
        total = len(pred_words | gt_words)
        word_overlap = overlap / total if total > 0 else 0.0

        return EvaluationResult(
            score=word_overlap,
            metrics={"word_overlap": word_overlap},
            feedback="Custom word overlap evaluation",
        )

    # Use custom evaluator
    result = custom_eval(
        "The weather is sunny and warm today", "It's sunny and warm outside"
    )

    print(f"Custom evaluation result:")
    print(f"Score: {result.score:.3f}")
    print(f"Metrics: {result.metrics}")
    print(f"Feedback: {result.feedback}")
    print()


async def async_evaluation():
    """Async evaluation example."""
    print("=== Async Evaluation ===")

    @aevaluator(name="async-evaluator", session_id="example-session")
    async def async_eval(prediction, ground_truth):
        """Async evaluation function."""
        # Simulate async processing
        await asyncio.sleep(0.1)

        # Calculate similarity score
        pred_words = set(prediction.lower().split())
        gt_words = set(ground_truth.lower().split())

        if not pred_words or not gt_words:
            return EvaluationResult(
                score=0.0, metrics={"similarity": 0.0}, feedback="No words to compare"
            )

        intersection = len(pred_words & gt_words)
        union = len(pred_words | gt_words)
        similarity = intersection / union if union > 0 else 0.0

        return EvaluationResult(
            score=similarity,
            metrics={"similarity": similarity},
            feedback="Async similarity evaluation",
        )

    # Use async evaluator
    result = await async_eval(
        "The temperature is 25 degrees Celsius", "It's 25°C outside"
    )

    print(f"Async evaluation result:")
    print(f"Score: {result.score:.3f}")
    print(f"Metrics: {result.metrics}")
    print(f"Feedback: {result.feedback}")
    print()


def batch_evaluation():
    """Batch evaluation example."""
    print("=== Batch Evaluation ===")

    # Test data
    test_cases = [
        ("The weather is sunny", "It's sunny today"),
        ("The temperature is 20°C", "It's 20 degrees Celsius"),
        ("There are 5 apples", "There are five apples"),
        ("The sky is blue", "The sky is red"),  # Different
    ]

    results = []
    for i, (prediction, ground_truth) in enumerate(test_cases):
        result = evaluate(
            prediction=prediction,
            ground_truth=ground_truth,
            metrics=["exact_match", "f1_score"],
        )
        results.append(result)

        print(f"Case {i+1}:")
        print(f"  Prediction: {prediction}")
        print(f"  Ground Truth: {ground_truth}")
        print(f"  Score: {result.score:.3f}")
        print(f"  Exact Match: {result.metrics['exact_match']:.3f}")
        print(f"  F1 Score: {result.metrics['f1_score']:.3f}")
        print()

    # Calculate average score
    avg_score = sum(r.score for r in results) / len(results)
    print(f"Average Score: {avg_score:.3f}")


async def main():
    """Run all evaluation examples."""
    print("=== HoneyHive Evaluation Examples ===\n")

    # Basic evaluation
    basic_evaluation()

    # Custom evaluation
    custom_evaluation()

    # Async evaluation
    await async_evaluation()

    # Batch evaluation
    batch_evaluation()

    print("All evaluation examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
