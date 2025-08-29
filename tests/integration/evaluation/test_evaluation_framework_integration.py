"""Integration tests for the HoneyHive evaluation framework.

This module tests the comprehensive evaluation framework including:
- Threading and parallel processing
- Custom evaluators
- Decorator patterns
- API integration
- Performance and scalability

These tests use REAL API credentials from the .env file to test actual
HoneyHive API integration.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

import psutil
import pytest

from honeyhive import HoneyHive
from honeyhive.evaluation.evaluators import (
    BaseEvaluator,
    EvaluationResult,
    ExactMatchEvaluator,
    F1ScoreEvaluator,
    LengthEvaluator,
    SemanticSimilarityEvaluator,
    aevaluator,
    create_evaluation_run,
    evaluate,
    evaluate_batch,
    evaluate_decorator,
    evaluate_with_evaluators,
    evaluator,
)


class TestCustomEvaluator(BaseEvaluator):
    """Custom evaluator for integration testing."""

    def __init__(self, name: str = "test_custom", tolerance: float = 0.1):
        super().__init__(name)
        self.tolerance = tolerance

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Custom evaluation logic for testing."""
        if not ground_truth:
            return {"score": 0.0, "error": "No ground truth"}

        predicted = outputs.get("response", "")
        expected = ground_truth.get("expected", "")

        # Simple similarity scoring
        if predicted == expected:
            score = 1.0
        elif predicted.lower() == expected.lower():
            score = 0.8
        elif len(predicted) > 0 and len(expected) > 0:
            # Calculate basic similarity
            common_chars = sum(1 for c in predicted if c in expected)
            score = min(1.0, common_chars / max(len(predicted), len(expected)))
        else:
            score = 0.0

        return {
            "score": score,
            "tolerance": self.tolerance,
            "predicted": predicted,
            "expected": expected,
            "similarity_score": score,
        }


class TestPerformanceEvaluator(BaseEvaluator):
    """Performance-focused evaluator for testing threading."""

    def __init__(self, name: str = "performance_test"):
        super().__init__(name)

    def evaluate(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        ground_truth: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Simulate some processing time to test threading."""
        time.sleep(0.01)  # Small delay to simulate processing

        response = outputs.get("response", "")
        score = min(1.0, len(response) / 100.0)  # Score based on length

        return {
            "score": score,
            "response_length": len(response),
            "processing_time": 0.01,
            "performance_score": score,
        }


@pytest.mark.integration
@pytest.mark.evaluation
class TestEvaluationFrameworkIntegration:
    """Integration tests for the evaluation framework."""

    def test_basic_evaluation_integration(self):
        """Test basic evaluation functionality integration."""
        # Test with built-in evaluators using the correct function signature
        result = evaluate(
            prediction="The answer is 4",
            ground_truth="4",
            metrics=["exact_match", "length"],
        )

        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "metrics")
        # The evaluate function flattens metrics, so they're not nested under evaluator names
        assert "exact_match" in result.metrics
        assert (
            "char_count" in result.metrics
        )  # Length evaluator adds char_count directly

    def test_custom_evaluator_integration(self):
        """Test custom evaluator integration."""
        custom_evaluator = TestCustomEvaluator(tolerance=0.2)

        result = evaluate_with_evaluators(
            evaluators=[custom_evaluator],
            inputs={"prompt": "Hello"},
            outputs={"response": "Hi there!"},
            ground_truth={"expected": "Hi there!"},
        )

        assert result is not None
        # The score calculation depends on the scoring logic in evaluate_with_evaluators
        # Let's check that we get a reasonable score and the metrics are correct
        assert result.score > 0.0  # Should have some score
        assert "test_custom" in result.metrics
        assert (
            result.metrics["test_custom"]["similarity_score"] > 0.8
        )  # Custom logic should give high score
        assert result.metrics["test_custom"]["tolerance"] == 0.2

    def test_threading_integration_basic(self):
        """Test basic threading integration."""
        # Small dataset to test threading
        inputs = {"prompt": "Question"}
        outputs = {"response": "Answer"}

        result = evaluate_with_evaluators(
            evaluators=["exact_match", "length"],
            inputs=inputs,
            outputs=outputs,
            max_workers=2,
        )

        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "metrics")
        assert "exact_match" in result.metrics
        assert "length" in result.metrics

    def test_threading_integration_large_dataset(self):
        """Test threading integration with larger dataset."""
        # Test with multiple evaluators to exercise threading
        inputs = {"prompt": "Question"}
        outputs = {"response": "Answer"}

        start_time = time.time()
        result = evaluate_with_evaluators(
            evaluators=["exact_match", "length", "f1_score"],
            inputs=inputs,
            outputs=outputs,
            max_workers=4,
        )
        end_time = time.time()

        processing_time = end_time - start_time

        # Should be reasonably fast with threading
        assert processing_time < 5.0  # Should complete in under 5 seconds

        # Verify result is valid
        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "metrics")

    def test_batch_evaluation_integration(self):
        """Test batch evaluation integration."""
        dataset = [
            {"inputs": {"prompt": "Hello"}, "outputs": {"response": "Hi"}},
            {"inputs": {"prompt": "World"}, "outputs": {"response": "Earth"}},
            {
                "inputs": {"prompt": "Python"},
                "outputs": {"response": "Programming language"},
            },
            {
                "inputs": {"prompt": "AI"},
                "outputs": {"response": "Artificial Intelligence"},
            },
        ]

        results = evaluate_batch(
            dataset=dataset, evaluators=["exact_match", "length"], max_workers=2
        )

        assert len(results) == 4
        for result in results:
            assert result is not None
            assert hasattr(result, "score")
            assert hasattr(result, "metrics")

    def test_decorator_integration(self):
        """Test decorator pattern integration."""

        @evaluate_decorator(evaluators=["exact_match", "length"])
        def test_function(prompt: str) -> str:
            return f"Response to: {prompt}"

        # Function should be automatically evaluated
        result = test_function("Hello")

        # The decorator should return the function result, not evaluation result
        assert isinstance(result, str)
        assert "Response to: Hello" in result

    def test_tracing_evaluator_decorator_integration(self):
        """Test tracing evaluator decorator integration."""

        @evaluator(evaluators=["exact_match", "length"])
        def traced_function(prompt: str) -> str:
            return f"Traced response: {prompt}"

        # Function should be automatically evaluated and traced
        result = traced_function("Test prompt")

        # Should return the function result
        assert isinstance(result, str)
        assert "Traced response: Test prompt" in result

    def test_async_evaluator_decorator_integration(self):
        """Test async evaluator decorator integration."""

        @aevaluator(evaluators=["exact_match", "length"])
        async def async_function(prompt: str) -> str:
            return f"Async response: {prompt}"

        # Test async function (we'll run it in sync context for testing)
        import asyncio

        result = asyncio.run(async_function("Async test"))

        assert isinstance(result, str)
        assert "Async response: Async test" in result

    def test_mixed_evaluator_types_integration(self):
        """Test integration with mixed evaluator types."""
        custom_evaluator = TestCustomEvaluator()

        result = evaluate_with_evaluators(
            evaluators=[
                "exact_match",  # String identifier
                LengthEvaluator(),  # Evaluator instance
                custom_evaluator,  # Custom evaluator
                lambda x, y, z: {"score": 0.8, "lambda_score": 0.8},  # Lambda function
            ],
            inputs={"prompt": "Hello"},
            outputs={"response": "Hi there!"},
            ground_truth={
                "expected": "Hi there!"
            },  # Add ground truth for custom evaluator
            max_workers=2,
        )

        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "metrics")

        # Should have results from all evaluators
        assert "exact_match" in result.metrics
        assert "length" in result.metrics
        assert "test_custom" in result.metrics
        # Lambda function key is "<lambda>" not "lambda"
        assert "<lambda>" in result.metrics

    def test_context_propagation_integration(self):
        """Test context propagation in threaded evaluation."""
        from honeyhive.evaluation.evaluators import EvaluationContext

        context = EvaluationContext(
            project="test-project",
            source="test-source",
            metadata={
                "model": "gpt-4",
                "temperature": 0.7,
                "batch_size": 10,
                "test_mode": True,
            },
        )

        result = evaluate_with_evaluators(
            evaluators=["exact_match", "length"],
            inputs={"prompt": "Hello"},
            outputs={"response": "Hi"},
            context=context,
            max_workers=2,
        )

        assert result is not None

        # Context should be preserved
        metadata = result.metadata
        if metadata and "context" in metadata:
            context_data = metadata["context"]
            if context_data is not None:
                assert context_data["project"] == "test-project"
                assert context_data["source"] == "test-source"
                assert context_data["metadata"]["test_mode"] is True

    def test_error_handling_integration(self):
        """Test error handling integration in threaded evaluation."""

        class FailingEvaluator(BaseEvaluator):
            """Test evaluator that always fails for error handling tests."""

            def __init__(self, name: str = "failing"):
                super().__init__(name)

            def evaluate(self, inputs, outputs, ground_truth=None, **kwargs):
                raise Exception("Simulated evaluator failure")

        failing_evaluator = FailingEvaluator()

        # Should not crash, should handle errors gracefully
        result = evaluate_with_evaluators(
            evaluators=["exact_match", failing_evaluator],
            inputs={"prompt": "Hello"},
            outputs={"response": "Hi"},
            max_workers=2,
        )

        assert result is not None

        # Should still have results from working evaluators
        assert "exact_match" in result.metrics

        # Failed evaluator should be logged but not crash the process
        # The exact error handling behavior depends on implementation
        assert result is not None

    def test_performance_evaluator_threading(self):
        """Test performance evaluator with threading."""
        # Test with performance evaluator that has small delays
        performance_evaluator = TestPerformanceEvaluator()

        start_time = time.time()
        result = evaluate_with_evaluators(
            evaluators=[performance_evaluator],
            inputs={"prompt": "Q"},
            outputs={"response": "A" * 50},  # Longer response
            max_workers=4,
        )
        end_time = time.time()

        processing_time = end_time - start_time

        assert result is not None
        assert processing_time < 2.0  # Should be much faster with threading

        # Verify result
        assert "performance_test" in result.metrics
        assert result.metrics["performance_test"]["response_length"] > 0

    def test_memory_efficient_batch_processing(self):
        """Test memory-efficient batch processing integration."""
        # Large dataset to test memory management
        dataset_size = 100
        dataset = [
            {"inputs": {"prompt": f"Q{i}"}, "outputs": {"response": f"A{i}" * 100}}
            for i in range(dataset_size)
        ]

        # Process in chunks to manage memory
        chunk_size = 25
        all_results = []

        for i in range(0, dataset_size, chunk_size):
            chunk = dataset[i : i + chunk_size]

            chunk_results = evaluate_batch(
                dataset=chunk, evaluators=["length"], max_workers=2
            )

            all_results.extend(chunk_results)

            # Clear chunk data
            del chunk

        assert len(all_results) == dataset_size

        # Verify all results
        for result in all_results:
            assert result is not None
            assert "length" in result.metrics

    def test_evaluator_registry_integration(self):
        """Test evaluator registry and discovery integration."""
        from honeyhive.evaluation.evaluators import get_evaluator

        # Test getting built-in evaluators
        exact_match = get_evaluator("exact_match")
        assert exact_match is not None
        assert hasattr(exact_match, "evaluate")

        length_evaluator = get_evaluator("length")
        assert length_evaluator is not None
        assert hasattr(length_evaluator, "evaluate")

        # Test getting custom evaluator
        # Note: Custom evaluators need to be registered or passed directly
        # This test verifies the basic registry functionality
        TestCustomEvaluator()  # Instantiate to test it works

    def test_score_normalization_integration(self):
        """Test score normalization integration."""
        # Test that scores are properly normalized to 0.0-1.0 range
        result = evaluate_with_evaluators(
            evaluators=["exact_match", "length"],
            inputs={"prompt": "Test"},
            outputs={"response": "Test response"},
            max_workers=1,
        )

        assert result is not None

        # Overall score should be normalized
        assert 0.0 <= result.score <= 1.0

        # Individual evaluator scores should also be normalized
        if "exact_match" in result.metrics:
            exact_score = result.metrics["exact_match"].get("score", 0.0)
            assert 0.0 <= exact_score <= 1.0

        if "length" in result.metrics:
            length_score = result.metrics["length"].get("score", 0.0)
            assert 0.0 <= length_score <= 1.0


@pytest.mark.integration
@pytest.mark.evaluation
@pytest.mark.api
class TestEvaluationAPIIntegration:
    """Integration tests for evaluation API functionality."""

    def test_create_evaluation_run_integration(
        self, integration_client, integration_project_name, skip_if_no_real_credentials
    ):
        """Test evaluation run creation integration with REAL API."""
        # Create evaluation results
        results = [
            EvaluationResult(score=0.8, metrics={"accuracy": 0.8, "precision": 0.75}),
            EvaluationResult(score=0.9, metrics={"accuracy": 0.9, "precision": 0.85}),
        ]

        # Test REAL API integration
        run = create_evaluation_run(
            name="integration-test-run",
            project=integration_project_name,
            results=results,
            metadata={"test_mode": True, "integration_test": True},
            client=integration_client,
        )

        # Verify the API call succeeded
        assert run is not None
        assert hasattr(run, "run_id")
        # Note: The actual run_id will be generated by the real API

    def test_evaluation_workflow_end_to_end(
        self, integration_client, integration_project_name, skip_if_no_real_credentials
    ):
        """Test complete evaluation workflow end-to-end with REAL API."""
        # Step 1: Create evaluation dataset
        dataset = [
            {
                "inputs": {"prompt": "What is 2+2?"},
                "outputs": {"response": "The answer is 4"},
            },
            {
                "inputs": {"prompt": "What is 3+3?"},
                "outputs": {"response": "The answer is 6"},
            },
            {
                "inputs": {"prompt": "What is 4+4?"},
                "outputs": {"response": "The answer is 8"},
            },
        ]

        # Step 2: Evaluate dataset with threading
        results = evaluate_batch(
            dataset=dataset,
            evaluators=["exact_match", "length"],
            max_workers=2,
            context=None,
        )

        assert len(results) == 3

        # Step 3: Store results via REAL API
        run = create_evaluation_run(
            name="end-to-end-test",
            project=integration_project_name,
            results=results,
            metadata={"workflow_test": True, "integration_test": True},
            client=integration_client,
        )

        # Verify the API call succeeded
        assert run is not None
        assert hasattr(run, "run_id")
        # Note: The actual run_id will be generated by the real API

    def test_large_dataset_api_integration(
        self, integration_client, integration_project_name, skip_if_no_real_credentials
    ):
        """Test large dataset evaluation with REAL API integration."""
        # Create larger dataset
        dataset_size = 50
        dataset = [
            {
                "inputs": {"prompt": f"Question {i}"},
                "outputs": {"response": f"Answer {i}"},
            }
            for i in range(dataset_size)
        ]

        # Evaluate with threading
        start_time = time.time()
        results = evaluate_batch(
            dataset=dataset,
            evaluators=["exact_match", "length"],
            max_workers=4,
            context=None,
        )
        evaluation_time = time.time() - start_time

        assert len(results) == dataset_size
        assert evaluation_time < 10.0  # Should complete reasonably quickly

        # Store results via REAL API
        run = create_evaluation_run(
            name="large-dataset-test",
            project=integration_project_name,
            results=results,
            metadata={
                "dataset_size": dataset_size,
                "evaluation_time": evaluation_time,
                "integration_test": True,
            },
            client=integration_client,
        )

        # Verify the API call succeeded
        assert run is not None
        assert hasattr(run, "run_id")
        # Note: The actual run_id will be generated by the real API


@pytest.mark.integration
@pytest.mark.evaluation
@pytest.mark.performance
class TestEvaluationPerformanceIntegration:
    """Performance integration tests for the evaluation framework."""

    def test_threading_scalability_integration(self):
        """Test threading scalability with real workloads."""
        # Test different worker configurations
        worker_configs = [1, 2, 4, 8]
        dataset_size = 100

        performance_results = {}

        for workers in worker_configs:
            dataset = [
                {"inputs": {"prompt": f"Q{i}"}, "outputs": {"response": f"A{i}" * 50}}
                for i in range(dataset_size)
            ]

            start_time = time.time()
            results = evaluate_batch(
                dataset=dataset, evaluators=["length"], max_workers=workers
            )
            end_time = time.time()

            processing_time = end_time - start_time
            items_per_second = dataset_size / processing_time

            performance_results[workers] = {
                "time": processing_time,
                "rate": items_per_second,
                "results_count": len(results),
            }

            # Verify results
            assert len(results) == dataset_size
            for result in results:
                assert result is not None
                assert "length" in result.metrics

        # For small datasets, threading overhead might make single-threaded faster
        # But we should still verify that all configurations work without crashing
        assert performance_results[1]["results_count"] == dataset_size
        assert performance_results[2]["results_count"] == dataset_size
        assert performance_results[4]["results_count"] == dataset_size
        assert performance_results[8]["results_count"] == dataset_size

        # Verify that threading doesn't crash and produces valid results
        # Performance improvements are not guaranteed for small datasets due to overhead
        print(f"Performance results: {performance_results}")

    def test_memory_usage_integration(self):
        """Test memory usage in real evaluation scenarios."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process large dataset
        dataset_size = 200
        dataset = [
            {"inputs": {"prompt": f"Q{i}"}, "outputs": {"response": f"A{i}" * 100}}
            for i in range(dataset_size)
        ]

        # Process in chunks to manage memory
        chunk_size = 50
        all_results = []

        for i in range(0, dataset_size, chunk_size):
            chunk = dataset[i : i + chunk_size]

            chunk_results = evaluate_batch(
                dataset=chunk, evaluators=["length"], max_workers=2
            )

            all_results.extend(chunk_results)

            # Clear chunk data
            del chunk

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert len(all_results) == dataset_size

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100.0

        # Verify all results
        for result in all_results:
            assert result is not None
            assert "length" in result.metrics

    def test_concurrent_evaluation_integration(self):
        """Test concurrent evaluation scenarios."""
        import queue
        import threading

        # Test concurrent evaluation from multiple threads
        results_queue = queue.Queue()
        num_threads = 4
        items_per_thread = 25

        def evaluate_thread(thread_id: int):
            """Evaluation function for each thread."""
            dataset = [
                {
                    "inputs": {"prompt": f"T{thread_id}-Q{i}"},
                    "outputs": {"response": f"T{thread_id}-A{i}"},
                }
                for i in range(items_per_thread)
            ]

            thread_results = evaluate_batch(
                dataset=dataset, evaluators=["exact_match", "length"], max_workers=2
            )

            results_queue.put((thread_id, thread_results))

        # Start concurrent evaluation threads
        threads = []
        start_time = time.time()

        for i in range(num_threads):
            thread = threading.Thread(target=evaluate_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Collect results
        all_results = []
        for _ in range(num_threads):
            _, thread_results = results_queue.get()
            all_results.extend(thread_results)

        # Verify results
        expected_total = num_threads * items_per_thread
        assert len(all_results) == expected_total

        # Should complete in reasonable time
        assert total_time < 30.0

        # All results should be valid
        for result in all_results:
            assert result is not None
            assert hasattr(result, "score")
            assert hasattr(result, "metrics")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
