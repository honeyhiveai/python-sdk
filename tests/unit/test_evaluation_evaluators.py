"""Tests for HoneyHive evaluation module."""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-few-public-methods
# pylint: disable=missing-class-docstring,import-outside-toplevel,broad-exception-raised
# pylint: disable=unused-argument,unused-import,unused-variable
# Justification: Comprehensive test coverage requires extensive test cases, testing
# private methods requires protected access, pytest fixtures redefine outer names by
# design, test classes may have few methods, test helper classes don't need docstrings,
# dynamic imports needed for testing, test exceptions can be broad, and test helper
# functions may not use all arguments. This file will be dramatically changed in future.

from typing import Any, Callable, TypeVar, cast
from unittest.mock import Mock, patch

import pytest

from honeyhive.evaluation import (
    BaseEvaluator,
    EvaluationContext,
    aevaluator,
    create_evaluation_run,
    evaluate,
    evaluate_batch,
    evaluate_decorator,
    evaluate_with_evaluators,
    evaluator,
    get_evaluator,
)
from honeyhive.evaluation.evaluators import (
    BUILTIN_EVALUATORS,
    EvaluationResult,
    ExactMatchEvaluator,
    F1ScoreEvaluator,
    LengthEvaluator,
    SemanticSimilarityEvaluator,
)

# Type variable for function return types
T = TypeVar("T")

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestEvaluationFunctions:
    """Test the core evaluation functions."""

    def test_evaluate_basic(self) -> None:
        """Test basic evaluation functionality."""
        result = evaluate("hello world", "hello world")

        assert isinstance(result, EvaluationResult)
        assert result.score == 1.0
        assert result.metrics["exact_match"] == 1.0
        assert result.metrics["f1_score"] == 1.0

    def test_evaluate_different_strings(self) -> None:
        """Test evaluation with different strings."""
        result = evaluate("hello world", "goodbye world")

        assert isinstance(result, EvaluationResult)
        # F1 score is 0.5 because they share "world" word
        assert result.score == 0.25  # (0.0 + 0.5) / 2
        assert result.metrics["exact_match"] == 0.0
        assert result.metrics["f1_score"] == 0.5

    def test_evaluate_case_insensitive(self) -> None:
        """Test evaluation is case insensitive."""
        result = evaluate("Hello World", "hello world")

        assert isinstance(result, EvaluationResult)
        assert result.score == 1.0
        assert result.metrics["exact_match"] == 1.0

    def test_evaluate_whitespace_insensitive(self) -> None:
        """Test evaluation is whitespace insensitive."""
        result = evaluate("  hello world  ", "hello world")

        assert isinstance(result, EvaluationResult)
        assert result.score == 1.0
        assert result.metrics["exact_match"] == 1.0

    def test_evaluate_custom_metrics(self) -> None:
        """Test evaluation with custom metrics."""
        result = evaluate("hello world", "hello world", metrics=["exact_match"])

        assert isinstance(result, EvaluationResult)
        assert result.score == 1.0
        assert "exact_match" in result.metrics
        assert "f1_score" not in result.metrics

    def test_evaluate_with_metadata(self) -> None:
        """Test evaluation with metadata."""
        result = evaluate(
            "hello world", "hello world", metadata={"model": "test-model"}
        )

        assert isinstance(result, EvaluationResult)
        assert result.metadata is not None
        assert result.metadata["model"] == "test-model"

    def test_evaluate_with_feedback(self) -> None:
        """Test evaluation with feedback."""
        result = evaluate("hello world", "hello world", feedback="Good match")

        assert isinstance(result, EvaluationResult)
        assert result.feedback == "Good match"


class TestBuiltinEvaluators:
    """Test the built-in evaluators."""

    def test_exact_match_evaluator(self) -> None:
        """Test ExactMatchEvaluator."""
        evaluator = ExactMatchEvaluator()

        # Test exact match
        result = evaluator.evaluate(
            {"expected": "Hello, world!"}, {"response": "Hello, world!"}
        )
        assert result["exact_match"] == 1.0

        # Test case insensitive
        result = evaluator.evaluate(
            {"expected": "Hello, world!"}, {"response": "hello, world!"}
        )
        assert result["exact_match"] == 1.0

        # Test different strings
        result = evaluator.evaluate(
            {"expected": "Hello, world!"}, {"response": "Goodbye, world!"}
        )
        assert result["exact_match"] == 0.0

    def test_f1_score_evaluator(self) -> None:
        """Test F1ScoreEvaluator."""
        evaluator = F1ScoreEvaluator()

        # Test perfect match
        result = evaluator.evaluate(
            {"expected": "hello world"}, {"response": "hello world"}
        )
        assert result["f1_score"] == 1.0

        # Test partial match
        result = evaluator.evaluate({"expected": "hello world"}, {"response": "hello"})
        assert 0.0 < result["f1_score"] < 1.0

        # Test no match
        result = evaluator.evaluate(
            {"expected": "hello world"}, {"response": "goodbye"}
        )
        assert result["f1_score"] == 0.0

    def test_length_evaluator(self) -> None:
        """Test LengthEvaluator."""
        evaluator = LengthEvaluator()

        result = evaluator.evaluate({"expected": "hello"}, {"response": "hello world"})

        assert result["char_count"] == 11
        assert result["word_count"] == 2
        assert result["line_count"] == 1

    def test_semantic_similarity_evaluator(self) -> None:
        """Test SemanticSimilarityEvaluator."""
        evaluator = SemanticSimilarityEvaluator()

        # Test similar content
        result = evaluator.evaluate(
            {"expected": "The cat is on the mat."},
            {"response": "A cat sits on the mat."},
        )
        assert result["semantic_similarity"] > 0.5

        # Test very different content
        result = evaluator.evaluate(
            {"expected": "The cat is on the mat."},
            {"response": "The weather is sunny today."},
        )
        assert result["semantic_similarity"] < 0.5


class TestBuiltinEvaluatorsRegistry:
    """Test the built-in evaluators registry."""

    def test_builtin_evaluators_available(self) -> None:
        """Test that all built-in evaluators are available."""
        expected_evaluators = [
            "exact_match",
            "f1_score",
            "length",
            "semantic_similarity",
        ]

        for name in expected_evaluators:
            assert name in BUILTIN_EVALUATORS
            evaluator_class = BUILTIN_EVALUATORS[name]
            assert issubclass(evaluator_class, BaseEvaluator)

    def test_get_evaluator(self) -> None:
        """Test get_evaluator function."""
        # Test valid evaluator
        evaluator = get_evaluator("exact_match")
        assert isinstance(evaluator, ExactMatchEvaluator)

        # Test invalid evaluator
        with pytest.raises(ValueError, match="Unknown evaluator"):
            get_evaluator("nonexistent")


class TestBaseEvaluator:
    """Test the BaseEvaluator class."""

    def test_base_evaluator_initialization(self) -> None:
        """Test BaseEvaluator initialization."""
        evaluator = BaseEvaluator("test_name", param1="value1", param2="value2")

        assert evaluator.name == "test_name"
        assert evaluator.config["param1"] == "value1"
        assert evaluator.config["param2"] == "value2"

    def test_base_evaluator_callable(self) -> None:
        """Test that BaseEvaluator is callable."""
        evaluator = BaseEvaluator("test_name")

        # Should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            evaluator.evaluate({}, {})


class TestCustomEvaluator:
    """Test custom evaluator functionality."""

    class CustomEvaluatorImpl(BaseEvaluator):
        """Custom evaluator implementation for testing."""

        def evaluate(
            self, inputs: dict, outputs: dict, ground_truth=None, **kwargs: Any
        ) -> dict:
            """Simple test evaluation."""
            expected = inputs.get("expected", "")
            actual = outputs.get("response", "")
            return {"custom_score": float(expected == actual)}

    def test_custom_evaluator_usage(self) -> None:
        """Test using a custom evaluator."""
        evaluator = self.CustomEvaluatorImpl("custom_test")

        result = evaluator.evaluate({"expected": "hello"}, {"response": "hello"})

        assert result["custom_score"] == 1.0
        assert evaluator.name == "custom_test"


class TestEvaluateDecorator:
    """Test the @evaluate decorator functionality."""

    def test_evaluate_decorator_with_string_evaluators(self) -> None:
        """Test @evaluate decorator with string evaluator names."""

        @evaluate_decorator(evaluators=["exact_match", "length"])
        def test_function(inputs):
            return {"response": "Hello, world!"}

        result = test_function({"expected": "Hello, world!"})

        assert "evaluation" in result
        eval_result = result["evaluation"]["result"]
        assert eval_result.score > 0
        assert "exact_match" in eval_result.metrics
        assert "length" in eval_result.metrics
        assert "char_count" in eval_result.metrics["length"]

    def test_evaluate_decorator_with_evaluator_instances(self) -> None:
        """Test @evaluate decorator with evaluator instances."""
        evaluator_instance = ExactMatchEvaluator()

        @evaluate_decorator(evaluators=[evaluator_instance])
        def test_function(inputs):
            return {"response": "Hello, world!"}

        result = test_function({"expected": "Hello, world!"})

        assert "evaluation" in result
        eval_result = result["evaluation"]["result"]
        assert eval_result.score == 1.0

    def test_evaluate_decorator_with_callable_evaluators(self) -> None:
        """Test @evaluate decorator with callable evaluators."""

        def custom_evaluator(inputs, outputs, **kwargs):
            return {"custom_metric": 0.8}

        @evaluate_decorator(evaluators=[custom_evaluator])
        def test_function(inputs):
            return {"response": "Hello, world!"}

        result = test_function({"expected": "Hello, world!"})

        assert "evaluation" in result
        eval_result = result["evaluation"]["result"]
        # The custom evaluator function gets named by its function name
        assert "custom_evaluator" in eval_result.metrics
        assert eval_result.metrics["custom_evaluator"]["custom_metric"] == 0.8

    def test_evaluate_decorator_no_evaluators(self) -> None:
        """Test @evaluate decorator with no evaluators."""

        @evaluate_decorator()
        def test_function(inputs):
            return {"response": "Hello, world!"}

        result = test_function({"expected": "Hello, world!"})

        # Should not have evaluation attached
        assert "evaluation" not in result

    def test_evaluate_decorator_non_dict_inputs(self) -> None:
        """Test @evaluate decorator with non-dict inputs."""

        @evaluate_decorator(evaluators=["exact_match"])
        def test_function(inputs):
            return {"response": "Hello, world!"}

        result = test_function("not a dict")

        # Should not have evaluation attached
        assert "evaluation" not in result

    def test_evaluate_decorator_dict_result(self) -> None:
        """Test @evaluate decorator with dict result."""

        @evaluate_decorator(evaluators=["exact_match"])
        def test_function(inputs):
            return {"response": "Hello, world!", "extra": "data"}

        result = test_function({"expected": "Hello, world!"})

        assert "evaluation" in result
        assert result["extra"] == "data"

    def test_evaluate_decorator_non_dict_result(self) -> None:
        """Test @evaluate decorator with non-dict result."""

        @evaluate_decorator(evaluators=["exact_match"])
        def test_function(inputs):
            return "Hello, world!"

        result = test_function({"expected": "Hello, world!"})

        # Should still work but evaluation won't be attached
        assert result == "Hello, world!"


class TestEvaluateWithEvaluators:
    """Test the evaluate_with_evaluators function."""

    def test_evaluate_with_evaluators_basic(self) -> None:
        """Test basic evaluate_with_evaluators functionality."""
        inputs = {"expected": "Hello, world!"}
        outputs = {"response": "Hello, world!"}

        result = evaluate_with_evaluators(
            evaluators=["exact_match", "length"], inputs=inputs, outputs=outputs
        )

        assert isinstance(result, EvaluationResult)
        assert result.score > 0
        assert "exact_match" in result.metrics
        assert "length" in result.metrics
        assert "char_count" in result.metrics["length"]

    def test_evaluate_with_evaluators_with_context(self) -> None:
        """Test evaluate_with_evaluators with custom context."""
        context = EvaluationContext(
            project="test-project", source="test-source", session_id="test-session"
        )

        inputs = {"expected": "Hello, world!"}
        outputs = {"response": "Hello, world!"}

        result = evaluate_with_evaluators(
            evaluators=["exact_match"], inputs=inputs, outputs=outputs, context=context
        )

        assert result.metadata is not None
        assert "context" in result.metadata
        assert result.metadata["context"]["project"] == "test-project"
        assert result.metadata["context"]["source"] == "test-source"
        assert result.metadata["context"]["session_id"] == "test-session"

    def test_evaluate_with_evaluators_mixed_types(self) -> None:
        """Test evaluate_with_evaluators with mixed evaluator types."""
        inputs = {"expected": "Hello, world!"}
        outputs = {"response": "Hello, world!"}

        def custom_evaluator(inputs, outputs, **kwargs):
            return {"custom": 0.9}

        result = evaluate_with_evaluators(
            evaluators=["exact_match", custom_evaluator, LengthEvaluator()],
            inputs=inputs,
            outputs=outputs,
        )

        assert "exact_match" in result.metrics
        assert "custom_evaluator" in result.metrics
        assert "custom" in result.metrics["custom_evaluator"]
        assert "length" in result.metrics
        assert "char_count" in result.metrics["length"]

    def test_evaluate_with_evaluators_error_handling(self) -> None:
        """Test evaluate_with_evaluators error handling."""
        inputs = {"expected": "Hello, world!"}
        outputs = {"response": "Hello, world!"}

        def failing_evaluator(inputs, outputs, **kwargs):
            raise Exception("Test error")

        # Should not crash, should log error and continue
        result = evaluate_with_evaluators(
            evaluators=["exact_match", failing_evaluator],
            inputs=inputs,
            outputs=outputs,
        )

        assert isinstance(result, EvaluationResult)
        assert "exact_match" in result.metrics
        # Failing evaluator should be skipped


class TestEvaluationContext:
    """Test the EvaluationContext class."""

    def test_evaluation_context_creation(self) -> None:
        """Test EvaluationContext creation."""
        context = EvaluationContext(
            project="test-project",
            source="test-source",
            session_id="test-session",
            metadata={"test": "data"},
        )

        assert context.project == "test-project"
        assert context.source == "test-source"
        assert context.session_id == "test-session"
        assert context.metadata is not None
        assert context.metadata["test"] == "data"

    def test_evaluation_context_defaults(self) -> None:
        """Test EvaluationContext default values."""
        context = EvaluationContext(project="test-project", source="test-source")

        assert context.session_id is None
        assert context.metadata is None


class TestCreateEvaluationRun:
    """Test the create_evaluation_run function."""

    @patch("honeyhive.evaluation.evaluators.HoneyHive")
    def test_create_evaluation_run_success(self, mock_honeyhive_class):
        """Test successful evaluation run creation."""
        # Mock the HoneyHive client
        mock_client = Mock()
        mock_honeyhive_class.return_value = mock_client

        # Mock the API response
        mock_response = Mock()
        mock_evaluation_run = Mock()
        mock_evaluation_run.id = "test-run-id"
        mock_response.evaluation = mock_evaluation_run
        mock_client.evaluations.create_run.return_value = mock_response

        # Create test results
        results = [
            EvaluationResult(score=0.8, metrics={"accuracy": 0.8}),
            EvaluationResult(score=0.9, metrics={"accuracy": 0.9}),
        ]

        # Test the function
        result = create_evaluation_run(
            name="test-run", project="test-project", _results=results
        )

        assert result is not None
        assert result.id == "test-run-id"

        # Verify API was called
        mock_client.evaluations.create_run.assert_called_once()

    @patch("honeyhive.evaluation.evaluators.HoneyHive")
    def test_create_evaluation_run_client_creation_failure(self, mock_honeyhive_class):
        """Test evaluation run creation when client creation fails."""
        mock_honeyhive_class.side_effect = Exception("Client creation failed")

        results = [EvaluationResult(score=0.8, metrics={"accuracy": 0.8})]

        result = create_evaluation_run(
            name="test-run", project="test-project", _results=results
        )

        assert result is None

    @patch("honeyhive.evaluation.evaluators.HoneyHive")
    def test_create_evaluation_run_api_failure(self, mock_honeyhive_class):
        """Test evaluation run creation when API call fails."""
        mock_client = Mock()
        mock_honeyhive_class.return_value = mock_client
        mock_client.evaluations.create_run.side_effect = Exception("API call failed")

        results = [EvaluationResult(score=0.8, metrics={"accuracy": 0.8})]

        result = create_evaluation_run(
            name="test-run", project="test-project", _results=results
        )

        assert result is None


class TestEvaluatorDecorator:
    """Test the evaluator decorator."""

    @patch("honeyhive.tracer.HoneyHiveTracer")
    def test_evaluator_decorator(self, mock_tracer: Any) -> None:
        """Test the evaluator decorator functionality."""
        mock_tracer._instance = Mock()
        mock_tracer._instance.project = "test-project"
        mock_tracer._instance.source = "test-source"
        mock_tracer._instance.api_key = "test-key"
        mock_tracer._instance.test_mode = True

        @evaluator(name="test_eval")
        def test_function() -> str:
            return "test result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], str] = cast(Callable[[], str], test_function)
        result: str = decorated_function()

        assert result == "test result"

    @patch("honeyhive.tracer.HoneyHiveTracer")
    def test_evaluator_decorator_with_session(self, mock_tracer: Any) -> None:
        """Test the evaluator decorator with session ID."""
        mock_tracer._instance = Mock()
        mock_tracer._instance.project = "test-project"
        mock_tracer._instance.source = "test-source"
        mock_tracer._instance.api_key = "test-key"
        mock_tracer._instance.test_mode = True

        @evaluator(name="test_eval", session_id="test-session")
        def test_function() -> str:
            return "test result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], str] = cast(Callable[[], str], test_function)
        result: str = decorated_function()

        assert result == "test result"

    def test_evaluator_decorator_no_tracer(self) -> None:
        """Test the evaluator decorator when no tracer is available."""

        @evaluator(name="test_eval")
        def test_function() -> str:
            return "test result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], str] = cast(Callable[[], str], test_function)
        result: str = decorated_function()

        assert result == "test result"


class TestAsyncEvaluatorDecorator:
    """Test the async evaluator decorator."""

    @pytest_mark_asyncio  # type: ignore
    @patch("honeyhive.tracer.HoneyHiveTracer")
    async def test_aevaluator_decorator(self, mock_tracer: Any) -> None:
        """Test the async evaluator decorator functionality."""
        mock_tracer._instance = Mock()
        mock_tracer._instance.project = "test-project"
        mock_tracer._instance.source = "test-source"
        mock_tracer._instance.api_key = "test-key"
        mock_tracer._instance.test_mode = True

        @aevaluator(name="test_async_eval")
        async def test_async_function() -> str:
            return "test async result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], Any] = cast(
            Callable[[], Any], test_async_function
        )
        result: str = await decorated_function()

        assert result == "test async result"

    @pytest_mark_asyncio  # type: ignore
    @patch("honeyhive.tracer.HoneyHiveTracer")
    async def test_aevaluator_decorator_with_session(self, mock_tracer: Any) -> None:
        """Test the async evaluator decorator with session ID."""
        mock_tracer._instance = Mock()
        mock_tracer._instance.project = "test-project"
        mock_tracer._instance.source = "test-source"
        mock_tracer._instance.api_key = "test-key"
        mock_tracer._instance.test_mode = True

        @aevaluator(name="test_async_eval", session_id="test-session")
        async def test_async_function() -> str:
            return "test async result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], Any] = cast(
            Callable[[], Any], test_async_function
        )
        result: str = await decorated_function()

        assert result == "test async result"

    @pytest_mark_asyncio  # type: ignore
    async def test_aevaluator_decorator_no_tracer(self) -> None:
        """Test the async evaluator decorator when no tracer is available."""

        @aevaluator(name="test_async_eval")
        async def test_async_function() -> str:
            return "test async result"

        # Cast the decorated function to its expected type
        decorated_function: Callable[[], Any] = cast(
            Callable[[], Any], test_async_function
        )
        result: str = await decorated_function()

        assert result == "test async result"


class TestEvaluationResult:
    """Test the EvaluationResult dataclass."""

    def test_evaluation_result_creation(self) -> None:
        """Test creating an EvaluationResult instance."""
        result = EvaluationResult(
            score=0.85,
            metrics={"accuracy": 0.9, "precision": 0.8},
            feedback="Good performance",
            metadata={"model": "gpt-4"},
        )

        assert result.score == 0.85
        assert result.metrics["accuracy"] == 0.9
        assert result.metrics["precision"] == 0.8
        assert result.feedback == "Good performance"
        assert result.metadata is not None
        assert result.metadata["model"] == "gpt-4"

    def test_evaluation_result_defaults(self) -> None:
        """Test EvaluationResult with default values."""
        result = EvaluationResult(score=0.5, metrics={})

        assert result.score == 0.5
        assert not result.metrics
        assert result.feedback is None
        assert result.metadata is None

    def test_evaluation_result_immutable(self) -> None:
        """Test that EvaluationResult attributes can be accessed."""
        result = EvaluationResult(score=0.8, metrics={"test": 1.0})

        # Test attribute access
        assert result.score == 0.8
        assert result.metrics["test"] == 1.0

        # Test that we can access the dict representation
        result_dict = result.__dict__
        assert result_dict["score"] == 0.8

    def test_evaluation_result_unique_id(self) -> None:
        """Test that each EvaluationResult gets a unique ID."""
        result1 = EvaluationResult(score=0.8, metrics={})
        result2 = EvaluationResult(score=0.9, metrics={})

        assert result1.evaluation_id != result2.evaluation_id
        assert len(result1.evaluation_id) > 0
        assert len(result2.evaluation_id) > 0


class TestEvaluationFrameworkIntegration:
    """Test the evaluation framework as a complete system."""

    def test_complete_evaluation_pipeline(self) -> None:
        """Test a complete evaluation pipeline from start to finish."""

        @evaluate_decorator(evaluators=["exact_match", "f1_score", "length"])
        def process_text(inputs):
            text = inputs.get("input_text", "")
            processed = text.lower().strip()
            return {"response": processed}

        result = process_text(
            {"input_text": "Hello, World!", "expected": "hello, world!"}
        )

        assert "evaluation" in result
        eval_result = result["evaluation"]["result"]
        assert "exact_match" in eval_result.metrics
        assert "f1_score" in eval_result.metrics
        assert "length" in eval_result.metrics
        assert "char_count" in eval_result.metrics["length"]
        assert 0.0 <= eval_result.score <= 1.0

    def test_custom_evaluator_integration(self) -> None:
        """Test integration of custom evaluators with the framework."""

        class SentimentEvaluator(BaseEvaluator):
            def __init__(self):
                super().__init__("sentiment")

            def evaluate(self, inputs, outputs, ground_truth=None, **kwargs):
                text = outputs.get("response", "")
                positive_words = ["good", "great", "excellent", "happy", "love"]
                negative_words = ["bad", "terrible", "awful", "sad", "hate"]

                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)

                if positive_count > negative_count:
                    sentiment = "positive"
                    score = min(1.0, positive_count / 2.0)
                elif negative_count > positive_count:
                    sentiment = "negative"
                    score = min(1.0, negative_count / 2.0)
                else:
                    sentiment = "neutral"
                    score = 0.5

                return {
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                }

        @evaluate_decorator(evaluators=["exact_match", "length", SentimentEvaluator()])
        def analyze_text(inputs):
            return {"response": inputs.get("text", "")}

        result = analyze_text(
            {
                "text": "I love this product, it's great!",
                "expected": "positive feedback",
            }
        )

        eval_result = result["evaluation"]["result"]
        assert "sentiment" in eval_result.metrics
        assert eval_result.metrics["sentiment"]["sentiment"] == "positive"


class TestEdgeCaseHandling:
    """Test edge cases and boundary conditions."""

    def test_empty_strings_evaluation(self) -> None:
        """Test evaluation with empty strings."""

        @evaluate_decorator(evaluators=["exact_match", "f1_score", "length"])
        def test_function(inputs):
            return {"response": inputs.get("response", "")}

        result = test_function({"expected": "", "response": ""})
        eval_result = result["evaluation"]["result"]

        assert eval_result.metrics["exact_match"]["exact_match"] == 1.0
        assert eval_result.metrics["f1_score"]["f1_score"] == 0.0
        assert eval_result.metrics["length"]["char_count"] == 0
        assert eval_result.metrics["length"]["word_count"] == 0

    def test_very_long_strings_evaluation(self) -> None:
        """Test evaluation with very long strings."""
        long_text = "word " * 1000

        @evaluate_decorator(evaluators=["length", "f1_score"])
        def test_function(inputs):
            return {"response": long_text}

        result = test_function({"expected": long_text})
        eval_result = result["evaluation"]["result"]

        assert eval_result.metrics["length"]["char_count"] > 1000
        assert eval_result.metrics["length"]["word_count"] == 1000
        assert eval_result.metrics["f1_score"]["f1_score"] == 1.0

    def test_error_handling_integration(self) -> None:
        """Test error handling throughout the evaluation pipeline."""

        class FailingEvaluator(BaseEvaluator):
            def __init__(self):
                super().__init__("failing")

            def evaluate(self, inputs, outputs, ground_truth=None, **kwargs):
                raise RuntimeError("Simulated failure")

        @evaluate_decorator(evaluators=["exact_match", FailingEvaluator(), "length"])
        def test_function(inputs):
            return {"response": "test"}

        result = test_function({"expected": "test"})
        assert "evaluation" in result
        eval_result = result["evaluation"]["result"]
        assert "exact_match" in eval_result.metrics
        assert "length" in eval_result.metrics
        assert "char_count" in eval_result.metrics["length"]
        assert eval_result.score > 0


class TestThreadingFeatures:
    """Test threading and parallel evaluation features."""

    def test_evaluate_with_evaluators_threading(self):
        """Test parallel evaluator execution with threading."""
        evaluators = [
            "exact_match",
            "f1_score",
            "length",
            TestCustomEvaluator.CustomEvaluatorImpl("custom"),
        ]

        inputs = {"question": "What is 2+2?", "expected": "4"}
        outputs = {"response": "2+2 equals 4"}
        ground_truth = {"answer": "4"}

        # Test sequential execution
        sequential_result = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            ground_truth=ground_truth,
            max_workers=1,
            run_concurrently=False,
        )

        assert sequential_result.score > 0
        assert len(sequential_result.metrics) == 4

        # Test parallel execution
        parallel_result = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            ground_truth=ground_truth,
            max_workers=4,
            run_concurrently=True,
        )

        assert parallel_result.score > 0
        assert len(parallel_result.metrics) == 4
        assert (
            parallel_result.score == sequential_result.score
        )  # Results should be identical

    def test_evaluate_batch_threading(self):
        """Test batch evaluation with threading support."""
        evaluators = ["exact_match", "length"]

        dataset = [
            {
                "inputs": {"question": "What is 2+2?", "expected": "4"},
                "outputs": {"response": "2+2 equals 4"},
                "ground_truth": {"answer": "4"},
            },
            {
                "inputs": {"question": "What is 3+3?", "expected": "6"},
                "outputs": {"response": "3+3 equals 6"},
                "ground_truth": {"answer": "6"},
            },
        ]

        # Test sequential batch execution
        sequential_results = evaluate_batch(
            evaluators=evaluators,
            dataset=dataset,
            max_workers=1,
            run_concurrently=False,
        )

        assert len(sequential_results) == 2
        assert all(isinstance(r, EvaluationResult) for r in sequential_results)

        # Test parallel batch execution
        parallel_results = evaluate_batch(
            evaluators=evaluators, dataset=dataset, max_workers=2, run_concurrently=True
        )

        assert len(parallel_results) == 2
        assert all(isinstance(r, EvaluationResult) for r in parallel_results)

        # Results should be identical
        for seq, par in zip(sequential_results, parallel_results):
            assert seq.score == par.score
            assert seq.metrics == par.metrics

    def test_context_propagation_threading(self):
        """Test that context is properly propagated across threads."""
        context = EvaluationContext(
            project="threading_test",
            source="parallel_evaluation",
            metadata={"test": True},
        )

        evaluators = ["exact_match"]
        dataset = [
            {
                "inputs": {"expected": "test"},
                "outputs": {"response": "test"},
                "ground_truth": {"answer": "test"},
            }
        ]

        results = evaluate_batch(
            evaluators=evaluators,
            dataset=dataset,
            max_workers=2,
            run_concurrently=True,
            context=context,
        )

        assert len(results) == 1
        result = results[0]
        assert result.metadata is not None
        assert "context" in result.metadata

        ctx = result.metadata["context"]
        assert ctx["project"] == "threading_test"
        assert ctx["source"] == "parallel_evaluation"
        assert ctx["metadata"]["test"] is True

    def test_thread_safety(self):
        """Test that evaluation is thread-safe."""
        import threading
        import time

        # Create a shared counter to test thread safety
        counter = {"value": 0}
        lock = threading.Lock()

        def thread_safe_evaluator(inputs, outputs, ground_truth=None):
            """Thread-safe evaluator that increments a counter."""
            with lock:
                counter["value"] += 1
                import time

                time.sleep(0.01)  # Simulate some work
                return counter["value"]

        evaluators = [thread_safe_evaluator]
        inputs = {"test": "data"}
        outputs = {"response": "test"}

        # Run multiple evaluations concurrently
        results = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            max_workers=4,
            run_concurrently=True,
        )

        # The counter should be incremented exactly once per evaluator call
        assert results.metrics["thread_safe_evaluator"] == 1

    def test_max_workers_respect(self):
        """Test that max_workers parameter is respected."""
        import threading

        thread_ids = set()
        lock = threading.Lock()

        def track_thread_evaluator(inputs, outputs, ground_truth):
            """Track which thread is executing this evaluator."""
            with lock:
                thread_ids.add(threading.current_thread().ident)
            import time

            time.sleep(0.01)  # Simulate work
            return 1.0

        evaluators = [track_thread_evaluator] * 8  # 8 evaluators

        inputs = {"test": "data"}
        outputs = {"response": "test"}

        # Test with max_workers=2
        _results = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            max_workers=2,
            run_concurrently=True,
        )

        # Should use at most 2 threads
        assert len(thread_ids) <= 2

        # Test with max_workers=4
        thread_ids.clear()
        results = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            max_workers=4,
            run_concurrently=True,
        )

        # Should use at most 4 threads
        assert len(thread_ids) <= 4

    def test_error_handling_threading(self):
        """Test error handling in threaded evaluation."""

        def failing_evaluator(inputs, outputs, ground_truth=None):
            """Evaluator that always fails."""
            raise ValueError("Intentional failure")

        def working_evaluator(inputs, outputs, ground_truth=None):
            """Evaluator that works correctly."""
            return 1.0

        evaluators = [failing_evaluator, working_evaluator]
        inputs = {"test": "data"}
        outputs = {"response": "test"}

        # Test that one failing evaluator doesn't break the others
        result = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            max_workers=2,
            run_concurrently=True,
        )

        assert "failing_evaluator" in result.metrics
        assert result.metrics["failing_evaluator"] is None
        assert "working_evaluator" in result.metrics
        assert result.metrics["working_evaluator"] == 1.0

        # Overall score should still be calculated from working evaluators
        assert result.score > 0

    def test_empty_dataset_threading(self):
        """Test threading with empty dataset."""
        evaluators = ["exact_match"]
        dataset = []

        results = evaluate_batch(
            evaluators=evaluators, dataset=dataset, max_workers=4, run_concurrently=True
        )

        assert not results

    def test_single_item_dataset_threading(self):
        """Test threading with single item dataset (should not use threading)."""
        evaluators = ["exact_match"]
        dataset = [
            {
                "inputs": {"expected": "test"},
                "outputs": {"response": "test"},
                "ground_truth": {"answer": "test"},
            }
        ]

        results = evaluate_batch(
            evaluators=evaluators, dataset=dataset, max_workers=4, run_concurrently=True
        )

        assert len(results) == 1
        assert isinstance(results[0], EvaluationResult)

    def test_mixed_evaluator_types_threading(self):
        """Test threading with mixed evaluator types (string, class, callable)."""
        evaluators = [
            "exact_match",  # String
            LengthEvaluator(),  # Class instance
            lambda i, o, g: 0.5,  # Callable
        ]

        inputs = {"expected": "test"}
        outputs = {"response": "test"}

        result = evaluate_with_evaluators(
            evaluators=evaluators,
            inputs=inputs,
            outputs=outputs,
            max_workers=3,
            run_concurrently=True,
        )

        assert len(result.metrics) == 3
        assert "exact_match" in result.metrics
        assert "length" in result.metrics
        assert "<lambda>" in result.metrics  # Function name for lambda
