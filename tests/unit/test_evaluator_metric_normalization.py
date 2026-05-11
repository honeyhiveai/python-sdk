"""Unit tests for client-side evaluator score normalization.

Client-side evaluator scores attach to the user-function chain span
inline via ``enrich_span(metrics=…)`` (see ``_apply_inline_evaluators``
in ``honeyhive.experiments.core``). The wire shape — what becomes
``metrics[eval_name]`` vs ``metrics[f"{eval_name}_explanation"]`` vs
extras — is decided by ``EvaluatorMetricResult.from_raw``, which mirrors
the canonical server-side evaluator output shape from
``services/data_plane/dp_evaluation_service/app/services/metric_update_service.js``.

This file exercises ``from_raw`` plus the ``to_metric_attrs`` flattener
and the per-datapoint runner ``_run_evaluators_for_datapoint``.
"""

# pylint: disable=protected-access,redefined-outer-name,too-few-public-methods
# Justification: testing internal helpers; mock fixtures need shared setup.

import asyncio
import logging
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from honeyhive.experiments.core import (
    EvaluatorMetricResult,
    _aapply_inline_evaluators,
    _apply_inline_evaluators,
    _run_evaluators_for_datapoint,
    _run_single_evaluator,
)


@pytest.fixture(autouse=True)
def _capture_module_logs(caplog: pytest.LogCaptureFixture):
    """Pipe ``honeyhive.experiments.core`` logs into ``caplog``.

    The HoneyHive logger sets ``propagate=False`` (utils/logger.py:177),
    so pytest's default caplog setup never sees its records. Attach
    caplog's handler directly to the module logger for the duration of
    each test.
    """
    module_logger = logging.getLogger("honeyhive.experiments.core")
    module_logger.addHandler(caplog.handler)
    module_logger.setLevel(logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="honeyhive.experiments.core")
    try:
        yield
    finally:
        module_logger.removeHandler(caplog.handler)


class TestEvaluatorMetricResultFromRaw:
    """Parsing rules for evaluator return values into the canonical metrics shape."""

    def test_scalar_float(self) -> None:
        result = EvaluatorMetricResult.from_raw("accuracy", 0.95)
        assert result.eval_name == "accuracy"
        assert result.score == 0.95
        assert result.explanation is None
        assert result.extras == {}

    def test_scalar_bool(self) -> None:
        result = EvaluatorMetricResult.from_raw("passed", True)
        assert result.score is True

    def test_scalar_str(self) -> None:
        result = EvaluatorMetricResult.from_raw("verdict", "good")
        assert result.score == "good"

    def test_scalar_int(self) -> None:
        # ints are scalars too — accepted as score.
        result = EvaluatorMetricResult.from_raw("count", 7)
        assert result.score == 7

    def test_list_of_one_coerced_to_element(self) -> None:
        # Preserves legacy list/tuple-of-one coercion behavior.
        result = EvaluatorMetricResult.from_raw("acc", [0.5])
        assert result.score == 0.5

    def test_tuple_of_one_coerced_to_element(self) -> None:
        result = EvaluatorMetricResult.from_raw("acc", (0.5,))
        assert result.score == 0.5

    def test_dict_with_score_and_explanation(self) -> None:
        result = EvaluatorMetricResult.from_raw(
            "accuracy",
            {"score": 0.95, "explanation": "Good match"},
        )
        assert result.score == 0.95
        assert result.explanation == "Good match"
        assert result.extras == {}

    def test_dict_extras_flattened_when_scalar(self) -> None:
        result = EvaluatorMetricResult.from_raw(
            "judge",
            {
                "score": 4,
                "explanation": "Pretty close",
                "passed": True,
                "category": "ok",
            },
        )
        assert result.score == 4
        assert result.explanation == "Pretty close"
        assert result.extras == {"passed": True, "category": "ok"}

    def test_dict_extras_non_scalar_dropped_with_warning(self, caplog) -> None:
        result = EvaluatorMetricResult.from_raw(
            "judge",
            {"score": 1.0, "extra_obj": {"nested": 1}, "extra_list": [1, 2]},
        )
        assert result.score == 1.0
        assert result.extras == {}  # both extras dropped
        assert any(
            "extra_obj" in rec.message and "non-scalar" in rec.message.lower()
            for rec in caplog.records
        )

    def test_dict_non_scalar_score_rejected(self, caplog) -> None:
        result = EvaluatorMetricResult.from_raw(
            "judge",
            {"score": {"nested": 1}, "explanation": "x"},
        )
        # Non-scalar score must not pollute compare-runs (it only diffs
        # numeric/boolean values; nested dicts would silently disappear
        # from diffing but appear in the metric list — explicit reject
        # is safer).
        assert result.score is None
        assert result.explanation == "x"
        assert any(
            "non-scalar" in rec.message.lower() and "score" in rec.message.lower()
            for rec in caplog.records
        )

    def test_dict_without_score_key_warns(self, caplog) -> None:
        result = EvaluatorMetricResult.from_raw("judge", {"foo": 1, "bar": 2})
        assert result.score is None
        # Defensive: extras still flattened so no data is lost outright.
        assert result.extras == {"foo": 1, "bar": 2}
        assert any("missing 'score' key" in rec.message for rec in caplog.records)

    def test_none_score_passes_through(self) -> None:
        # Failing evaluator returns None today; preserve that path.
        result = EvaluatorMetricResult.from_raw("acc", None)
        assert result.score is None
        assert result.extras == {}

    def test_to_metric_attrs_score_only(self) -> None:
        result = EvaluatorMetricResult(eval_name="accuracy", score=0.95)
        assert result.to_metric_attrs() == {"accuracy": 0.95}

    def test_to_metric_attrs_with_explanation(self) -> None:
        result = EvaluatorMetricResult(
            eval_name="accuracy",
            score=0.95,
            explanation="Good match",
        )
        assert result.to_metric_attrs() == {
            "accuracy": 0.95,
            "accuracy_explanation": "Good match",
        }

    def test_to_metric_attrs_with_extras(self) -> None:
        result = EvaluatorMetricResult(
            eval_name="judge",
            score=1.0,
            explanation="ok",
            extras={"passed": True, "category": "good"},
        )
        assert result.to_metric_attrs() == {
            "judge": 1.0,
            "judge_explanation": "ok",
            "judge_passed": True,
            "judge_category": "good",
        }

    def test_to_metric_attrs_omits_none_score(self) -> None:
        # Evaluator failed; we still want any extras visible but no
        # None-valued bare score key.
        result = EvaluatorMetricResult(
            eval_name="judge", score=None, extras={"category": "fail"}
        )
        assert result.to_metric_attrs() == {"judge_category": "fail"}


class TestRunSingleEvaluator:
    """Behavior of the single-evaluator runner used inside the per-datapoint pool."""

    def test_sync_evaluator_returns_normalized_result(self) -> None:
        def my_eval(outputs, inputs, ground_truth):
            return outputs.get("v", 0) * 2.0

        result = _run_single_evaluator(
            my_eval,
            inputs={"q": "x"},
            outputs={"v": 5},
            ground_truth={"expected": 10},
            verbose=False,
        )
        assert result.eval_name == "my_eval"
        assert result.score == 10.0

    def test_evaluator_without_ground_truth_uses_two_arg_signature(self) -> None:
        # Legacy "evaluator(outputs, inputs)" signature path: when the
        # datapoint has no ground_truth, the runner calls the evaluator
        # with just (outputs, inputs).
        def fluency(outputs, inputs):
            return 0.9

        result = _run_single_evaluator(
            fluency,
            inputs={},
            outputs={},
            ground_truth=None,
            verbose=False,
        )
        assert result.score == 0.9

    def test_evaluator_exception_returns_none_score(self, caplog) -> None:
        def failing(outputs, inputs, ground_truth):
            raise ValueError("evaluator boom")

        result = _run_single_evaluator(
            failing,
            inputs={},
            outputs={},
            ground_truth={"x": 1},
            verbose=True,
        )
        assert result.eval_name == "failing"
        assert result.score is None
        assert any("evaluator boom" in rec.message for rec in caplog.records)


class TestRunEvaluatorsForDatapoint:
    """Per-datapoint orchestration of N evaluators."""

    def test_empty_evaluator_list_returns_empty(self) -> None:
        assert (
            _run_evaluators_for_datapoint([], inputs={}, outputs={}, ground_truth=None)
            == []
        )

    def test_single_evaluator_single_call(self) -> None:
        def acc(outputs, inputs, ground_truth):
            return 0.5

        results = _run_evaluators_for_datapoint(
            [acc], inputs={}, outputs={}, ground_truth={}
        )
        assert len(results) == 1
        assert results[0].eval_name == "acc"
        assert results[0].score == 0.5

    def test_multiple_evaluators_all_returned(self) -> None:
        def a(outputs, inputs, ground_truth):
            return 0.1

        def b(outputs, inputs, ground_truth):
            return 0.2

        def c(outputs, inputs, ground_truth):
            return 0.3

        results = _run_evaluators_for_datapoint(
            [a, b, c],
            inputs={},
            outputs={},
            ground_truth={},
            max_workers=4,
        )
        names_to_scores = {r.eval_name: r.score for r in results}
        assert names_to_scores == {"a": 0.1, "b": 0.2, "c": 0.3}

    def test_one_evaluator_failure_does_not_block_others(self) -> None:
        def good(outputs, inputs, ground_truth):
            return 1.0

        def bad(outputs, inputs, ground_truth):
            raise RuntimeError("nope")

        results = _run_evaluators_for_datapoint(
            [good, bad],
            inputs={},
            outputs={},
            ground_truth={},
            verbose=False,
        )
        names_to_scores = {r.eval_name: r.score for r in results}
        assert names_to_scores == {"good": 1.0, "bad": None}


class TestApplyInlineEvaluators:
    """Inline-enrichment of the active chain span with evaluator scores."""

    def test_attaches_flattened_metrics_to_chain_span(self) -> None:
        def acc(outputs, inputs, ground_truth):
            return {"score": 0.9, "explanation": "decent"}

        tracer = MagicMock()
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span"
        ) as mock_enrich:
            results = _apply_inline_evaluators(
                [acc],
                inputs={},
                outputs={"x": 1},
                ground_truth={"x": 1},
                tracer=tracer,
                max_workers=2,
                verbose=False,
            )

        assert len(results) == 1
        mock_enrich.assert_called_once()
        call = mock_enrich.call_args
        assert call.kwargs["tracer"] is tracer
        assert call.kwargs["metrics"] == {
            "acc": 0.9,
            "acc_explanation": "decent",
        }

    def test_no_metrics_skips_enrich_call(self) -> None:
        # All evaluators failed → score None, no extras → metric dict empty.
        def bad(outputs, inputs, ground_truth):
            raise ValueError("boom")

        tracer = MagicMock()
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span"
        ) as mock_enrich:
            _apply_inline_evaluators(
                [bad],
                inputs={},
                outputs={},
                ground_truth={},
                tracer=tracer,
                max_workers=1,
                verbose=False,
            )
        mock_enrich.assert_not_called()

    def test_enrich_span_failure_does_not_raise(self, caplog) -> None:
        def acc(outputs, inputs, ground_truth):
            return 0.5

        tracer = MagicMock()
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span",
            side_effect=RuntimeError("span gone"),
        ):
            # Must not raise.
            results = _apply_inline_evaluators(
                [acc],
                inputs={},
                outputs={},
                ground_truth={},
                tracer=tracer,
                max_workers=1,
                verbose=False,
            )

        assert len(results) == 1
        assert results[0].score == 0.5
        assert any(
            "Failed to attach evaluator metrics" in rec.message
            for rec in caplog.records
        )

    def test_multiple_evaluators_metrics_merge(self) -> None:
        def a(outputs, inputs, ground_truth):
            return 1.0

        def b(outputs, inputs, ground_truth):
            return {"score": 2.0, "explanation": "B"}

        tracer = MagicMock()
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span"
        ) as mock_enrich:
            _apply_inline_evaluators(
                [a, b],
                inputs={},
                outputs={},
                ground_truth={},
                tracer=tracer,
                max_workers=2,
                verbose=False,
            )

        sent_metrics: Dict[str, Any] = mock_enrich.call_args.kwargs["metrics"]
        assert sent_metrics == {
            "a": 1.0,
            "b": 2.0,
            "b_explanation": "B",
        }


class TestAapplyInlineEvaluatorsAsyncPath:
    """Async-eval × async-user-fn regression coverage.

    Reproduces the pre-fix bug: ``_apply_inline_evaluators`` (sync)
    called from inside an active event loop with a single async
    evaluator raised ``RuntimeError: Cannot run the event loop while
    another loop is running`` because ``_run_single_evaluator``'s
    ``loop.run_until_complete`` cannot start a nested loop in the same
    thread. The async-user-fn path now routes through
    ``_aapply_inline_evaluators`` which awaits the evaluator directly.
    """

    def test_single_async_evaluator_inside_running_loop(self) -> None:
        async def acc(outputs, inputs, ground_truth):
            await asyncio.sleep(0)
            return {"score": 0.42, "explanation": "ok"}

        tracer = MagicMock()
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span"
        ) as mock_enrich:
            results = asyncio.run(
                _aapply_inline_evaluators(
                    [acc],
                    inputs={},
                    outputs={"x": 1},
                    ground_truth={"x": 1},
                    tracer=tracer,
                    verbose=False,
                )
            )

        assert len(results) == 1
        assert results[0].eval_name == "acc"
        assert results[0].score == 0.42
        mock_enrich.assert_called_once()
        assert mock_enrich.call_args.kwargs["metrics"] == {
            "acc": 0.42,
            "acc_explanation": "ok",
        }

    def test_mixed_sync_and_async_evaluators_inside_running_loop(self) -> None:
        # Sync evaluators must still work on the async path — they get
        # dispatched to a worker thread by ``_arun_single_evaluator``.
        def fast(outputs, inputs, ground_truth):
            return 1.0

        async def slow(outputs, inputs, ground_truth):
            await asyncio.sleep(0)
            return 2.0

        tracer = MagicMock()
        with patch("honeyhive.tracer.instrumentation.enrichment.enrich_span"):
            results = asyncio.run(
                _aapply_inline_evaluators(
                    [fast, slow],
                    inputs={},
                    outputs={},
                    ground_truth={},
                    tracer=tracer,
                    verbose=False,
                )
            )

        names_to_scores = {r.eval_name: r.score for r in results}
        assert names_to_scores == {"fast": 1.0, "slow": 2.0}

    def test_async_evaluator_exception_does_not_break_path(self) -> None:
        async def boom(outputs, inputs, ground_truth):
            raise ValueError("nope")

        tracer = MagicMock()
        with patch("honeyhive.tracer.instrumentation.enrichment.enrich_span"):
            results = asyncio.run(
                _aapply_inline_evaluators(
                    [boom],
                    inputs={},
                    outputs={},
                    ground_truth={},
                    tracer=tracer,
                    verbose=False,
                )
            )

        assert len(results) == 1
        assert results[0].eval_name == "boom"
        assert results[0].score is None
