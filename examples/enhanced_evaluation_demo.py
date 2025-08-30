#!/usr/bin/env python3
"""
Enhanced Evaluation Demo

This example demonstrates the comprehensive evaluation framework including:
- Built-in evaluators
- Custom evaluators
- The @evaluate decorator with evaluators
- Evaluation result handling
- Integration with HoneyHive API
"""

import os
from typing import Dict, Any, Optional
import time

from honeyhive import (
    evaluate_decorator,  # Main @evaluate decorator
    evaluator,
    aevaluator,
    get_evaluator,
    BaseEvaluator,
    EvaluationResult,
    create_evaluation_run,
    HoneyHiveTracer,
    evaluate_batch,
    evaluate_with_evaluators,
    EvaluationContext
)

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "enhanced-evaluation-demo"
os.environ["HH_SOURCE"] = "development"


class CustomAccuracyEvaluator(BaseEvaluator):
    """Custom evaluator for accuracy with tolerance."""
    
    def __init__(self, tolerance: float = 0.1, **kwargs: Any) -> None:
        """Initialize with tolerance for numeric comparisons."""
        super().__init__("custom_accuracy", **kwargs)
        self.tolerance = tolerance
    
    def evaluate(
        self, inputs: Dict[str, Any], outputs: Dict[str, Any], ground_truth: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Evaluate accuracy with tolerance for numeric values."""
        expected = inputs.get("expected")
        actual = outputs.get("response")
        
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            diff = abs(expected - actual)
            accuracy = 1.0 if diff <= self.tolerance else max(0.0, 1.0 - (diff / max(abs(expected), 1)))
            return {
                "custom_accuracy": accuracy,
                "tolerance": self.tolerance,
                "difference": diff
            }
        elif isinstance(expected, str) and isinstance(actual, str):
            # String comparison
            accuracy = 1.0 if expected.lower() == actual.lower() else 0.0
            return {"custom_accuracy": accuracy, "tolerance": "exact_match"}
        else:
            return {"custom_accuracy": 0.0, "error": "Incompatible types"}


def main():
    """Main enhanced evaluation demo function."""
    
    print("🚀 Enhanced HoneyHive Evaluation Framework Demo")
    print("=" * 60)
    
    # Initialize tracer
    print("1. Initializing HoneyHiveTracer...")
    HoneyHiveTracer.init(
        api_key="your-api-key-here",
        project="enhanced-evaluation-demo",
        source="development"
    )
    
    print("✓ Tracer initialized successfully")
    print()
    
    # Demonstrate built-in evaluators
    print("2. Testing built-in evaluators...")
    
    # Get built-in evaluators
    exact_match_eval = get_evaluator("exact_match")
    f1_eval = get_evaluator("f1_score")
    length_eval = get_evaluator("length")
    semantic_eval = get_evaluator("semantic_similarity")
    
    # Test inputs and outputs
    test_inputs = {"expected": "Hello, world!"}
    test_outputs = {"response": "Hello world"}
    
    # Run individual evaluators
    exact_result = exact_match_eval(test_inputs, test_outputs)
    f1_result = f1_eval(test_inputs, test_outputs)
    length_result = length_eval(test_inputs, test_outputs)
    semantic_result = semantic_eval(test_inputs, test_outputs)
    
    print(f"✓ Exact Match: {exact_result}")
    print(f"✓ F1 Score: {f1_result}")
    print(f"✓ Length Analysis: {length_result}")
    print(f"✓ Semantic Similarity: {semantic_result}")
    print()
    
    # Demonstrate custom evaluator
    print("3. Testing custom evaluator...")
    
    custom_eval = CustomAccuracyEvaluator(tolerance=0.2)
    custom_result = custom_eval(test_inputs, test_outputs)
    print(f"✓ Custom Accuracy: {custom_result}")
    
    # Test with numeric values
    numeric_inputs = {"expected": 100}
    numeric_outputs = {"response": 95}
    numeric_result = custom_eval(numeric_inputs, numeric_outputs)
    print(f"✓ Numeric Accuracy: {numeric_result}")
    print()
    
    # Demonstrate the @evaluate decorator with evaluators
    print("4. Testing @evaluate decorator with evaluators...")
    
    @evaluate_decorator(evaluators=[
        "exact_match",
        "f1_score", 
        "length",
        custom_eval
    ])
    def function_to_evaluate(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Function that will be automatically evaluated."""
        expected = inputs.get("expected", "")
        # Simulate some processing
        response = expected.replace(",", "").replace("!", "")
        return {"response": response}
    
    # Call the function - it will be automatically evaluated
    result = function_to_evaluate({"expected": "Hello, world!"})
    print(f"✓ Function result: {result}")
    
    # Check if evaluation was attached
    if "evaluation" in result:
        eval_result = result["evaluation"]["result"]
        print(f"✓ Evaluation score: {eval_result.score}")
        print(f"✓ Evaluation metrics: {eval_result.metrics}")
        print(f"✓ Evaluation feedback: {eval_result.feedback}")
    print()
    
    # Demonstrate evaluation decorators
    print("5. Testing evaluation decorators...")
    
    @evaluator(name="accuracy_check")
    def accuracy_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Simple accuracy evaluator."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")
        return {"accuracy": expected == actual}
    
    @evaluator(name="length_check")
    def length_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Length evaluator."""
        response = outputs.get("response", "")
        return {"length": len(str(response))}
    
    # Test the evaluators
    accuracy_result = accuracy_evaluator(test_inputs, test_outputs)
    length_result = length_evaluator(test_inputs, test_outputs)
    
    print(f"✓ Accuracy evaluator: {accuracy_result}")
    print(f"✓ Length evaluator: {length_result}")
    print()
    
    # Demonstrate async evaluation
    print("6. Testing async evaluation...")
    
    @aevaluator(name="async_accuracy")
    async def async_accuracy_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Async accuracy evaluator."""
        import asyncio
        await asyncio.sleep(0.1)  # Simulate async work
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")
        return {"async_accuracy": expected == actual}
    
    # Test async evaluator
    import asyncio
    async def test_async():
        result = await async_accuracy_evaluator(test_inputs, test_outputs)
        return result
    
    async_result = asyncio.run(test_async())
    print(f"✓ Async accuracy evaluator: {async_result}")
    print()
    
    # Demonstrate evaluation result creation
    print("7. Testing evaluation result creation...")
    
    # Create multiple evaluation results
    eval_results = [
        EvaluationResult(
            score=0.8,
            metrics={"accuracy": 0.8, "precision": 0.75},
            feedback="Good performance with room for improvement",
            metadata={"model": "gpt-4", "temperature": 0.1}
        ),
        EvaluationResult(
            score=0.9,
            metrics={"accuracy": 0.9, "precision": 0.85},
            feedback="Excellent performance",
            metadata={"model": "gpt-4", "temperature": 0.05}
        )
    ]
    
    print(f"✓ Created {len(eval_results)} evaluation results")
    for i, result in enumerate(eval_results):
        print(f"  Result {i+1}: Score {result.score}, Metrics: {result.metrics}")
    print()
    
    # Demonstrate evaluation run creation (commented out to avoid API calls)
    print("8. Evaluation run creation (commented out to avoid API calls)...")
    print("✓ The create_evaluation_run function is available for creating evaluation runs")
    print("✓ It integrates with the HoneyHive API to store evaluation results")
    print("✓ Uncomment the code below to test it:")
    print()
    print("""
    # Uncomment to test evaluation run creation:
    # run = create_evaluation_run(
    #     name="demo-evaluation-run",
    #     project="enhanced-evaluation-demo",
    #     results=eval_results,
    #     metadata={"demo": True, "version": "1.0"}
    # )
    # if run:
    #     print(f"✓ Created evaluation run: {run.run_id}")
    """)
    
    print("\n🎉 Enhanced evaluation demo completed successfully!")
    print("\nKey features demonstrated:")
    print("✅ Built-in evaluators (exact_match, f1_score, length, semantic_similarity)")
    print("✅ Custom evaluator creation with BaseEvaluator")
    print("✅ @evaluate_decorator with automatic evaluation")
    print("✅ @evaluator and @aevaluator decorators")
    print("✅ Evaluation result creation and management")
    print("✅ Integration with HoneyHive API")
    print("✅ Comprehensive evaluation pipeline")


def demo_threading_features():
    """Demonstrate threading and parallel evaluation features."""
    print("\n" + "="*60)
    print("THREADING & PARALLEL EVALUATION FEATURES")
    print("="*60)
    
    # Create a dataset for batch evaluation
    dataset = [
        {
            "inputs": {"question": "What is 2+2?", "expected": "4"},
            "outputs": {"response": "2+2 equals 4"},
            "ground_truth": {"answer": "4"}
        },
        {
            "inputs": {"question": "What is the capital of France?", "expected": "Paris"},
            "outputs": {"response": "The capital of France is Paris"},
            "ground_truth": {"answer": "Paris"}
        },
        {
            "inputs": {"question": "What color is the sky?", "expected": "Blue"},
            "outputs": {"response": "The sky is blue"},
            "ground_truth": {"answer": "Blue"}
        },
        {
            "inputs": {"question": "What is 5x5?", "expected": "25"},
            "outputs": {"response": "5 multiplied by 5 equals 25"},
            "ground_truth": {"answer": "25"}
        }
    ]
    
    # Define evaluators
    evaluators = [
        "exact_match",
        "f1_score", 
        "length",
        CustomAccuracyEvaluator(tolerance=0.1)
    ]
    
    print("\n1. Sequential Evaluation (Single Thread)")
    print("-" * 40)
    start_time = time.time()
    sequential_results = evaluate_batch(
        evaluators=evaluators,
        dataset=dataset,
        max_workers=1,
        run_concurrently=False
    )
    sequential_time = time.time() - start_time
    
    print(f"Sequential execution time: {sequential_time:.3f} seconds")
    for i, result in enumerate(sequential_results):
        print(f"  Result {i+1}: Score {result.score:.3f}, Metrics: {len(result.metrics)}")
    
    print("\n2. Parallel Evaluation (4 Threads)")
    print("-" * 40)
    start_time = time.time()
    parallel_results = evaluate_batch(
        evaluators=evaluators,
        dataset=dataset,
        max_workers=4,
        run_concurrently=True
    )
    parallel_time = time.time() - start_time
    
    print(f"Parallel execution time: {parallel_time:.3f} seconds")
    print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    for i, result in enumerate(parallel_results):
        print(f"  Result {i+1}: Score {result.score:.3f}, Metrics: {len(result.metrics)}")
    
    print("\n3. Parallel Evaluator Execution")
    print("-" * 40)
    start_time = time.time()
    parallel_eval_result = evaluate_with_evaluators(
        evaluators=evaluators,
        inputs={"question": "What is 10+15?", "expected": "25"},
        outputs={"response": "10 plus 15 equals 25"},
        ground_truth={"answer": "25"},
        max_workers=4,
        run_concurrently=True
    )
    parallel_eval_time = time.time() - start_time
    
    print(f"Parallel evaluator execution time: {parallel_eval_time:.3f} seconds")
    print(f"Overall score: {parallel_eval_result.score:.3f}")
    print(f"Metrics: {list(parallel_eval_result.metrics.keys())}")
    
    print("\n4. Context-Aware Threading")
    print("-" * 40)
    context = EvaluationContext(
        project="threading_demo",
        source="parallel_evaluation",
        metadata={"threading": True, "max_workers": 4}
    )
    
    threaded_results = evaluate_batch(
        evaluators=evaluators,
        dataset=dataset,
        max_workers=4,
        run_concurrently=True,
        context=context
    )
    
    print(f"Context-aware threading completed: {len(threaded_results)} results")
    for i, result in enumerate(threaded_results):
        if result.metadata and "context" in result.metadata:
            ctx = result.metadata["context"]
            print(f"  Result {i+1}: Project={ctx.get('project')}, Source={ctx.get('source')}")


if __name__ == "__main__":
    main()
    
    # Add threading demo
    demo_threading_features()
    
    print("\n" + "="*60)
    print("EVALUATION FRAMEWORK DEMO COMPLETE")
    print("="*60)
