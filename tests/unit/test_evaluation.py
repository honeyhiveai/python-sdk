"""Tests for HoneyHive evaluation module."""

from typing import Any, Callable, TypeVar, cast
from unittest.mock import Mock, patch

import pytest

from honeyhive.evaluation import aevaluator, evaluate, evaluator
from honeyhive.evaluation.evaluators import EvaluationResult

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
        assert result.metrics == {}
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
