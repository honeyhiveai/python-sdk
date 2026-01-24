"""
Evaluate Function Integration Tests

Tests the evaluate() function with real API calls.
Based on examples/eval_example.py and examples/evaluate_with_enrichment.py.

Requirements:
    pip install honeyhive

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
"""

import os
import pytest
from typing import Any, Dict, List


# Skip entire module if key not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.slow,
]


class TestEvaluateIntegration:
    """Test evaluate() function with real API calls."""

    def test_evaluate_basic_function(self):
        """Test basic evaluate() with inline dataset."""
        from honeyhive import evaluate, evaluator

        # Simple function to evaluate
        def simple_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Echo the input with processing."""
            text = inputs.get("text", "")
            return {"result": f"Processed: {text}", "length": len(text)}

        # Simple evaluator
        @evaluator()
        def length_check(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check if length is captured correctly."""
            return outputs.get("length", 0) == len(inputs.get("text", ""))

        # Dataset
        dataset = [
            {"inputs": {"text": "hello"}, "ground_truths": {"expected": "Processed: hello"}},
            {"inputs": {"text": "world"}, "ground_truths": {"expected": "Processed: world"}},
        ]

        # Run evaluation
        result = evaluate(
            function=simple_function,
            project=os.getenv("HH_PROJECT", "evaluate-integration-test"),
            name="test_evaluate_basic_function",
            dataset=dataset,
            evaluators=[length_check],
        )

        assert result is not None
        assert result.run_id is not None
        assert result.status in ["completed", "pending", "running"]

    def test_evaluate_with_enrichment(self):
        """Test evaluate() with span enrichment inside the function."""
        from honeyhive import evaluate, evaluator, trace, enrich_span

        @trace(event_type="chain")
        def function_with_enrichment(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Function that enriches spans during evaluation."""
            query = inputs.get("query", "")

            # Enrich with metadata
            enrich_span(metadata={"query_length": len(query)})

            # Simulate processing
            result = f"Answer to: {query}"

            # Enrich with output info
            enrich_span(
                metadata={"result_length": len(result)},
                metrics={"processing_score": 0.95},
            )

            return {"answer": result}

        @evaluator()
        def answer_exists(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check that answer exists and is non-empty."""
            return bool(outputs.get("answer"))

        dataset = [
            {"inputs": {"query": "What is AI?"}, "ground_truths": {}},
            {"inputs": {"query": "How does ML work?"}, "ground_truths": {}},
        ]

        result = evaluate(
            function=function_with_enrichment,
            project=os.getenv("HH_PROJECT", "evaluate-integration-test"),
            name="test_evaluate_with_enrichment",
            dataset=dataset,
            evaluators=[answer_exists],
        )

        assert result is not None
        assert result.run_id is not None
        assert result.status in ["completed", "pending", "running"]

    def test_evaluate_multiple_evaluators(self):
        """Test evaluate() with multiple evaluators."""
        from honeyhive import evaluate, evaluator

        def qa_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Simple Q&A function."""
            question = inputs.get("question", "")
            # Simulate answer generation
            return {"answer": f"The answer to '{question}' is 42.", "confidence": 0.9}

        @evaluator()
        def has_answer(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check answer exists."""
            return bool(outputs.get("answer"))

        @evaluator()
        def high_confidence(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check confidence is high."""
            return outputs.get("confidence", 0) >= 0.8

        @evaluator()
        def answer_mentions_question(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check answer references the question."""
            question = inputs.get("question", "")
            answer = outputs.get("answer", "")
            return question.lower() in answer.lower()

        dataset = [
            {"inputs": {"question": "what is the meaning of life"}, "ground_truths": {}},
        ]

        result = evaluate(
            function=qa_function,
            project=os.getenv("HH_PROJECT", "evaluate-integration-test"),
            name="test_evaluate_multiple_evaluators",
            dataset=dataset,
            evaluators=[has_answer, high_confidence, answer_mentions_question],
        )

        assert result is not None
        assert result.run_id is not None
        assert result.status in ["completed", "pending", "running"]

    def test_evaluate_with_ground_truths(self):
        """Test evaluate() with ground truth comparison."""
        from honeyhive import evaluate, evaluator

        def classification_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Simple classifier."""
            text = inputs.get("text", "").lower()
            if "happy" in text or "great" in text:
                sentiment = "positive"
            elif "sad" in text or "bad" in text:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            return {"sentiment": sentiment}

        @evaluator()
        def correct_sentiment(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check if sentiment matches ground truth."""
            return outputs.get("sentiment") == ground_truths.get("sentiment")

        dataset = [
            {
                "inputs": {"text": "I am so happy today!"},
                "ground_truths": {"sentiment": "positive"},
            },
            {
                "inputs": {"text": "This is a sad day."},
                "ground_truths": {"sentiment": "negative"},
            },
            {
                "inputs": {"text": "The sky is blue."},
                "ground_truths": {"sentiment": "neutral"},
            },
        ]

        result = evaluate(
            function=classification_function,
            project=os.getenv("HH_PROJECT", "evaluate-integration-test"),
            name="test_evaluate_with_ground_truths",
            dataset=dataset,
            evaluators=[correct_sentiment],
        )

        assert result is not None
        assert result.run_id is not None
        assert result.status in ["completed", "pending", "running"]

    def test_evaluate_async_function(self):
        """Test evaluate() with async function."""
        import asyncio
        from honeyhive import evaluate, evaluator

        async def async_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Async function to evaluate."""
            await asyncio.sleep(0.01)  # Simulate async work
            text = inputs.get("text", "")
            return {"processed": text.upper()}

        @evaluator()
        def is_uppercase(outputs: Dict, inputs: Dict, ground_truths: Dict) -> bool:
            """Check result is uppercase."""
            return outputs.get("processed", "").isupper()

        dataset = [
            {"inputs": {"text": "hello"}, "ground_truths": {}},
            {"inputs": {"text": "world"}, "ground_truths": {}},
        ]

        result = evaluate(
            function=async_function,
            project=os.getenv("HH_PROJECT", "evaluate-integration-test"),
            name="test_evaluate_async_function",
            dataset=dataset,
            evaluators=[is_uppercase],
        )

        assert result is not None
        assert result.run_id is not None
