#!/usr/bin/env python3
"""
HoneyHive Evaluation Framework Example

This comprehensive example demonstrates the HoneyHive evaluation framework
from basic usage to advanced features, including:

1. Basic Setup & Initialization
2. Simple Custom Evaluators
3. Built-in Evaluators
4. Advanced Custom Evaluators
5. The @evaluate_decorator
6. Async Evaluation
7. Threading & Parallel Processing
8. API Integration

This example progresses from simple concepts to advanced usage patterns.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional

from honeyhive import (
    # Core evaluation decorators
    evaluate_decorator,  # Main @evaluate decorator
    evaluator,
    aevaluator,
    
    # Evaluation utilities
    get_evaluator,
    BaseEvaluator,
    EvaluationResult,
    EvaluationContext,
    create_evaluation_run,
    evaluate_batch,
    evaluate_with_evaluators,
    
    # Tracer for initialization
    HoneyHiveTracer,
)

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "evaluation-demo"
os.environ["HH_SOURCE"] = "development"


def section_header(title: str, level: int = 1) -> None:
    """Print a formatted section header."""
    if level == 1:
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
    else:
        print(f"\n{level}. {title}")
        print("-" * (len(title) + 3))


def main():
    """Main evaluation example function with progressive complexity."""
    
    print("🚀 HoneyHive Evaluation Framework - Comprehensive Example")
    print("This example demonstrates evaluation features from basic to advanced")
    
    # ========================================================================
    # 1. BASIC SETUP & INITIALIZATION
    # ========================================================================
    section_header("Basic Setup & Initialization")
    
    # Initialize tracer using the recommended pattern
    tracer = HoneyHiveTracer.init(
        api_key="your-api-key-here",
        # project derived from API key,
        source="development"
    )
    
    print(f"✓ Tracer initialized for project: {tracer.project}")
    print(f"✓ Source environment: {tracer.source}")
    print(f"✓ Session ID: {tracer.session_id}")
    
    # ========================================================================
    # 2. SIMPLE CUSTOM EVALUATORS
    # ========================================================================
    section_header("Simple Custom Evaluators", 2)
    
    @evaluator(name="accuracy_check")
    def accuracy_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Simple accuracy evaluator - exact match."""
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")
        return {"accuracy": expected == actual}
    
    @evaluator(name="length_check")
    def length_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Length evaluator - measures response length."""
        response = outputs.get("response", "")
        return {"length": len(response)}
    
    # Test the simple evaluators
    test_inputs = {"expected": "Hello, World!"}
    test_outputs = {"response": "Hello, World!"}
    
    accuracy_result = accuracy_evaluator(test_inputs, test_outputs)
    length_result = length_evaluator(test_inputs, test_outputs)
    
    print(f"✓ Accuracy evaluator: {accuracy_result}")
    print(f"✓ Length evaluator: {length_result}")
    
    # ========================================================================
    # 3. BUILT-IN EVALUATORS
    # ========================================================================
    section_header("Built-in Evaluators", 3)
    
    # Get built-in evaluators
    exact_match_eval = get_evaluator("exact_match")
    f1_eval = get_evaluator("f1_score")
    length_eval = get_evaluator("length")
    semantic_eval = get_evaluator("semantic_similarity")
    
    # Test with slightly different inputs
    test_inputs_2 = {"expected": "Hello, world!"}
    test_outputs_2 = {"response": "Hello world"}
    
    # Run individual evaluators
    exact_result = exact_match_eval(test_inputs_2, test_outputs_2)
    f1_result = f1_eval(test_inputs_2, test_outputs_2)
    length_result = length_eval(test_inputs_2, test_outputs_2)
    semantic_result = semantic_eval(test_inputs_2, test_outputs_2)
    
    print(f"✓ Exact Match: {exact_result}")
    print(f"✓ F1 Score: {f1_result}")
    print(f"✓ Length Analysis: {length_result}")
    print(f"✓ Semantic Similarity: {semantic_result}")
    
    # ========================================================================
    # 4. ADVANCED CUSTOM EVALUATORS
    # ========================================================================
    section_header("Advanced Custom Evaluators", 4)
    
    class CustomAccuracyEvaluator(BaseEvaluator):
        """Custom evaluator for accuracy with tolerance."""
        
        def __init__(self, tolerance: float = 0.1, **kwargs: Any) -> None:
            """Initialize with tolerance for numeric comparisons."""
            super().__init__("custom_accuracy", **kwargs)
            self.tolerance = tolerance
        
        def evaluate(
            self, inputs: Dict[str, Any], outputs: Dict[str, Any], 
            ground_truth: Optional[Dict[str, Any]] = None, **kwargs: Any
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
    
    # Test the custom evaluator
    custom_eval = CustomAccuracyEvaluator(tolerance=0.2)
    custom_result = custom_eval(test_inputs_2, test_outputs_2)
    print(f"✓ Custom String Accuracy: {custom_result}")
    
    # Test with numeric values
    numeric_inputs = {"expected": 100}
    numeric_outputs = {"response": 95}
    numeric_result = custom_eval(numeric_inputs, numeric_outputs)
    print(f"✓ Custom Numeric Accuracy: {numeric_result}")
    
    # ========================================================================
    # 5. THE @evaluate_decorator
    # ========================================================================
    section_header("The @evaluate_decorator", 5)
    
    @evaluate_decorator(evaluators=[
        accuracy_evaluator, 
        length_evaluator
    ])
    def simple_function(inputs):
        """Simple function to evaluate with basic evaluators."""
        return {"response": "Hello, World!"}
    
    # Test the decorated function
    result = simple_function({"expected": "Hello, World!"})
    print(f"✓ Simple function result: {result}")
    
    # Check if evaluation was attached
    if "evaluation" in result:
        eval_result = result["evaluation"]["result"]
        print(f"✓ Evaluation score: {eval_result.score}")
        print(f"✓ Evaluation metrics: {eval_result.metrics}")
    
    # More advanced @evaluate_decorator usage
    @evaluate_decorator(evaluators=[
        "exact_match",
        "f1_score", 
        "length",
        custom_eval
    ])
    def advanced_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Function with advanced evaluation using built-ins and custom evaluators."""
        expected = inputs.get("expected", "")
        # Simulate some processing
        response = expected.replace(",", "").replace("!", "")
        return {"response": response}
    
    # Call the advanced function
    advanced_result = advanced_function({"expected": "Hello, world!"})
    print(f"✓ Advanced function result: {advanced_result}")
    
    # Check evaluation results
    if "evaluation" in advanced_result:
        eval_result = advanced_result["evaluation"]["result"]
        print(f"✓ Advanced evaluation score: {eval_result.score}")
        print(f"✓ Advanced evaluation metrics: {eval_result.metrics}")
        if hasattr(eval_result, 'feedback') and eval_result.feedback:
            print(f"✓ Evaluation feedback: {eval_result.feedback}")
    
    # ========================================================================
    # 6. ASYNC EVALUATION
    # ========================================================================
    section_header("Async Evaluation", 6)
    
    @aevaluator(name="async_accuracy")
    async def async_accuracy_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Async accuracy evaluator."""
        await asyncio.sleep(0.1)  # Simulate async work
        expected = inputs.get("expected", "")
        actual = outputs.get("response", "")
        return {"async_accuracy": expected == actual}
    
    @aevaluator(name="async_length")
    async def async_length_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Async length evaluator."""
        await asyncio.sleep(0.05)  # Simulate async work
        response = outputs.get("response", "")
        return {"async_length": len(response)}
    
    # Test async evaluators
    async def test_async_evaluators():
        accuracy_result = await async_accuracy_evaluator(test_inputs, test_outputs)
        length_result = await async_length_evaluator(test_inputs, test_outputs)
        return accuracy_result, length_result
    
    async_accuracy_result, async_length_result = asyncio.run(test_async_evaluators())
    print(f"✓ Async accuracy evaluator: {async_accuracy_result}")
    print(f"✓ Async length evaluator: {async_length_result}")
    
    # Async function evaluation
    @evaluate_decorator(evaluators=[async_accuracy_evaluator, async_length_evaluator])
    async def async_function(inputs):
        """Async function to evaluate."""
        await asyncio.sleep(0.1)
        return {"response": "Async Hello, World!"}
    
    async_result = asyncio.run(async_function({"expected": "Async Hello, World!"}))
    print(f"✓ Async function result: {async_result}")
    
    # ========================================================================
    # 7. EVALUATION RESULT MANAGEMENT
    # ========================================================================
    section_header("Evaluation Result Management", 7)
    
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
    
    print("\n🎉 Basic to Intermediate evaluation features completed!")
    print("\nNext: Advanced threading and parallel processing features...")


def demo_advanced_features():
    """Demonstrate advanced threading and parallel evaluation features."""
    
    section_header("ADVANCED FEATURES: Threading & Parallel Processing")
    
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
    
    # Define evaluators for batch processing
    class CustomAccuracyEvaluator(BaseEvaluator):
        """Custom evaluator for batch processing demo."""
        
        def __init__(self, tolerance: float = 0.1, **kwargs: Any) -> None:
            super().__init__("custom_accuracy", **kwargs)
            self.tolerance = tolerance
        
        def evaluate(
            self, inputs: Dict[str, Any], outputs: Dict[str, Any], 
            ground_truth: Optional[Dict[str, Any]] = None, **kwargs: Any
        ) -> Dict[str, Any]:
            expected = inputs.get("expected")
            actual = outputs.get("response")
            
            if isinstance(expected, str) and isinstance(actual, str):
                accuracy = 1.0 if expected.lower() in actual.lower() else 0.0
                return {"custom_accuracy": accuracy}
            return {"custom_accuracy": 0.0}
    
    evaluators = [
        "exact_match",
        "f1_score", 
        "length",
        CustomAccuracyEvaluator(tolerance=0.1)
    ]
    
    # ========================================================================
    # 8. SEQUENTIAL VS PARALLEL EVALUATION
    # ========================================================================
    section_header("Sequential vs Parallel Evaluation", 8)
    
    print("Sequential Evaluation (Single Thread)")
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
    
    print("\nParallel Evaluation (4 Threads)")
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
    if sequential_time > 0:
        print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    for i, result in enumerate(parallel_results):
        print(f"  Result {i+1}: Score {result.score:.3f}, Metrics: {len(result.metrics)}")
    
    # ========================================================================
    # 9. PARALLEL EVALUATOR EXECUTION
    # ========================================================================
    section_header("Parallel Evaluator Execution", 9)
    
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
    
    # ========================================================================
    # 10. CONTEXT-AWARE EVALUATION
    # ========================================================================
    section_header("Context-Aware Evaluation", 10)
    
    context = EvaluationContext(
        # project derived from API key,
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
    
    # ========================================================================
    # 11. API INTEGRATION (COMMENTED OUT)
    # ========================================================================
    section_header("API Integration", 11)
    
    print("✓ The create_evaluation_run function is available for creating evaluation runs")
    print("✓ It integrates with the HoneyHive API to store evaluation results")
    print("✓ Uncomment the code below to test it with a valid API key:")
    print()
    print("""
    # Uncomment to test evaluation run creation:
    # run = create_evaluation_run(
    #     name="comprehensive-evaluation-run",
    #     # project derived from API key,
    #     results=eval_results,
    #     metadata={"demo": True, "version": "2.0", "comprehensive": True}
    # )
    # if run:
    #     print(f"✓ Created evaluation run: {run.run_id}")
    """)


if __name__ == "__main__":
    # Run the main comprehensive example
    main()
    
    # Run advanced features demo
    demo_advanced_features()
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE EVALUATION EXAMPLE COMPLETED!")
    print("="*60)
    print("\nKey features demonstrated:")
    print("✅ Basic custom evaluators (@evaluator, @aevaluator)")
    print("✅ Built-in evaluators (exact_match, f1_score, length, semantic_similarity)")
    print("✅ Advanced custom evaluators (BaseEvaluator subclass)")
    print("✅ @evaluate_decorator with automatic evaluation")
    print("✅ Async evaluation patterns")
    print("✅ Evaluation result creation and management")
    print("✅ Sequential vs parallel evaluation")
    print("✅ Threading and concurrent processing")
    print("✅ Context-aware evaluation")
    print("✅ Integration with HoneyHive API")
    print("✅ Comprehensive evaluation pipeline")
    print("\nThis example progresses from basic concepts to advanced usage!")
