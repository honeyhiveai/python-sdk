"""Integration tests for async evaluator pipeline.

Tests validate that both @aevaluator and @evaluator work correctly
through the async execution path (async_call / __acall__), specifically
verifying that the non-repeat branch properly assigns `results` before
passing it to aggregation.

Regression test for: UnboundLocalError on `results` in async_call
when final_settings.repeat is falsy.
"""

import asyncio

import pytest

from honeyhive.experiments.evaluators import aevaluator, evaluator, EvalResult


@pytest.mark.integration
class TestAsyncEvaluatorPath:
    """Tests for the async evaluator execution path."""

    @pytest.mark.asyncio
    async def test_aevaluator_no_repeat_returns_score(self) -> None:
        """Async evaluator without repeat should not raise UnboundLocalError.

        Regression: async_call else-branch did not assign `results`,
        causing UnboundLocalError at the aggregation step.
        """

        @aevaluator
        async def async_accuracy(output: str, expected: str) -> float:
            return 1.0 if output == expected else 0.0

        score = await async_accuracy("hello", "hello")
        assert score is not None

    @pytest.mark.asyncio
    async def test_aevaluator_no_repeat_correct_value(self) -> None:
        """Async evaluator returns the correct numeric score."""

        @aevaluator
        async def async_match(a: int, b: int) -> float:
            return 1.0 if a == b else 0.0

        perfect = await async_match(42, 42)
        assert perfect == (1.0,)

        mismatch = await async_match(1, 2)
        assert mismatch == (0.0,)

    @pytest.mark.asyncio
    async def test_sync_evaluator_called_via_acall(self) -> None:
        """Sync evaluator invoked through __acall__ uses sync_call path."""

        @evaluator
        def sync_length(text: str) -> int:
            return len(text)

        result = await sync_length.__acall__("hello")
        assert result is not None

    @pytest.mark.asyncio
    async def test_aevaluator_with_repeat(self) -> None:
        """Async evaluator with repeat should gather results correctly."""

        @aevaluator(repeat=3)
        async def async_constant(_x: int) -> float:
            return 0.5

        score = await async_constant(1)
        assert score is not None

    @pytest.mark.asyncio
    async def test_aevaluator_result_is_tuple_in_acall(self) -> None:
        """Verify async_call returns (results_tuple, scores_tuple) structure."""

        @aevaluator
        async def async_score(val: float) -> float:
            return val * 2.0

        result_tuple = await async_score.async_call(0.25)
        assert isinstance(result_tuple, tuple)
        assert len(result_tuple) == 2
        results_tuple, scores_tuple = result_tuple
        assert isinstance(results_tuple, tuple)
        assert len(results_tuple) == 1
        assert isinstance(results_tuple[0], EvalResult)
        assert scores_tuple == (0.5,)
