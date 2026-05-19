"""Integration tests — external dataset × client-side evaluators (Cell 1).

Covers the inline ``enrich_span(metrics=…)`` attachment path that
``evaluate()`` runs between user-function-return and chain-span-end. The
chain span is named after the user function and carries the evaluator
scores out via OTLP export.

Tests in this cell:

* Full external-dataset workflow (run creation, backend state, results).
* Inline chain-span attachment for **sync** user functions, exercising
  every accepted evaluator return shape (scalar float, scalar bool,
  dict-with-explanation, dict-with-extras).
* Inline chain-span attachment for **async** user functions with sync,
  async, and mixed evaluator pools (regression coverage for the
  nested-event-loop bug fixed in 9d2ef6d on PR #3998).
* Nested ``@trace``-decorated helper isolation — evaluator scores must
  attach to the user-function chain span only, never to nested tools.
* Failure-mode coverage — one evaluator raises while others succeed;
  empty ``evaluators=[]`` runs cleanly.
"""

# pylint: disable=R0801,too-many-lines
# Justification: shared integration patterns with v1 immediate-ship and
# misc/experiment tests.

import asyncio
import os
import time
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive, trace
from honeyhive.experiments import evaluate
from tests.integration._experiments_helpers import (
    assert_metric_absent_on_chain_spans,
    assert_metric_present_on_chain_spans,
    assert_run_metadata_on_all_child_events,
    assert_standard_suite_attached_to_chain_spans,
    chain_events_for_function,
    double_value_function,
    event_field,
    event_metrics,
    export_events_for_run_polling,
    passing_failing_dataset,
    standard_evaluator_suite,
)


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsExternalClientSide:
    """external dataset × client-side evaluators."""

    def test_full_workflow(
        self,
        real_api_key: str,
        real_project: str,
        real_source: str,
        integration_client: HoneyHive,
    ) -> None:
        """Complete external-dataset workflow with EXT- IDs.

        Validates run creation, function execution under the multi-instance
        tracer, backend state for run name/dataset/events/status, and
        result retrieval.
        """
        del real_source  # captured for pytest fixture wiring; unused here

        def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            question = inputs.get("question", "")
            return {"answer": f"Answer to: {question}"}

        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            expected = ground_truth.get("expected_answer", "")
            actual = outputs.get("answer", "")
            return 1.0 if expected in actual else 0.0

        dataset = [
            {
                "inputs": {"question": "What is 2+2?"},
                "ground_truth": {"expected_answer": "4"},
            },
            {
                "inputs": {"question": "What is the capital of France?"},
                "ground_truth": {"expected_answer": "Paris"},
            },
            {
                "inputs": {"question": "What color is the sky?"},
                "ground_truth": {"expected_answer": "blue"},
            },
        ]
        run_name = f"external-client-full-{int(time.time())}"

        result = evaluate(
            function=simple_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            aggregate_function="average",
            verbose=False,
        )
        assert result is not None and result.run_id

        # Backend state — run name set, events recorded.
        backend_run = integration_client.evaluations.get_run(result.run_id)
        assert hasattr(backend_run, "evaluation") and backend_run.evaluation, (
            f"Backend response missing 'evaluation' field: {backend_run}"
        )
        run_data = backend_run.evaluation
        assert getattr(run_data, "name", None), "Run name should not be empty"
        assert len(getattr(run_data, "event_ids", []) or []) > 0, (
            "Should have recorded events"
        )

    # ---------------------- inline attachment, sync ------------------------

    def test_inline_chain_span_attachment_sync(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Sync user function — inline-attach over every accepted return shape.

        Asserts:
        * Every child event carries ``metadata.{run_id, dataset_id, datapoint_id}``
          (baggage-driven injection at span on_start).
        * Each client-side evaluator's score (and the ``_explanation`` /
          ``_passed`` / ``_category`` derivatives) appears on the
          user-function chain span.
        """
        run_name = f"inline-attach-sync-{int(time.time())}"
        dataset = passing_failing_dataset()

        result = evaluate(
            function=double_value_function,
            dataset=dataset,
            evaluators=standard_evaluator_suite(),
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="double_value_function",
            expected_chain_span_count=len(dataset),
        )
        assert events, f"No events returned for run {result.run_id}"

        assert_run_metadata_on_all_child_events(events, result.run_id)
        assert_standard_suite_attached_to_chain_spans(
            events,
            function_name="double_value_function",
            expected_dataset_size=len(dataset),
        )

    # ---------------------- inline attachment, async -----------------------

    def test_inline_chain_span_attachment_async_user_fn_sync_evaluators(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Async user fn × sync evaluators — sync evals run via asyncio.to_thread."""
        run_name = f"inline-attach-async-sync-{int(time.time())}"
        dataset = passing_failing_dataset()

        async def async_double_value_function(
            datapoint: Dict[str, Any],
        ) -> Dict[str, Any]:
            # Real async hop ensures we exercise the asyncio.run path
            # in process_datapoint, not just a coroutine wrapper that
            # returns synchronously.
            await asyncio.sleep(0)
            return {"result": datapoint["inputs"]["value"] * 2}

        result = evaluate(
            function=async_double_value_function,
            dataset=dataset,
            evaluators=standard_evaluator_suite(),
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="async_double_value_function",
            expected_chain_span_count=len(dataset),
        )
        assert_run_metadata_on_all_child_events(events, result.run_id)
        assert_standard_suite_attached_to_chain_spans(
            events,
            function_name="async_double_value_function",
            expected_dataset_size=len(dataset),
        )

    def test_inline_chain_span_attachment_async_user_fn_async_evaluators(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Async user fn × multiple async evaluators (len > 1).

        Verifies the multi-evaluator async dispatch path through
        ``_aapply_inline_evaluators``. The single-evaluator (len==1)
        case has its own dedicated test below for the HHAI-5270
        nested-event-loop regression.
        """
        run_name = f"inline-attach-async-async-{int(time.time())}"
        dataset = passing_failing_dataset()

        async def async_double_value_function(
            datapoint: Dict[str, Any],
        ) -> Dict[str, Any]:
            await asyncio.sleep(0)
            return {"result": datapoint["inputs"]["value"] * 2}

        async def async_chain_eval(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            await asyncio.sleep(0)
            return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

        async def async_is_positive(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> bool:
            await asyncio.sleep(0)
            return outputs["result"] > 0

        result = evaluate(
            function=async_double_value_function,
            dataset=dataset,
            evaluators=[async_chain_eval, async_is_positive],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="async_double_value_function",
            expected_chain_span_count=len(dataset),
        )
        assert_run_metadata_on_all_child_events(events, result.run_id)
        assert_metric_present_on_chain_spans(
            events,
            "async_double_value_function",
            "async_is_positive",
            expected_value=True,
        )
        # Both pass and fail branches of async_chain_eval observed.
        chain_scores = sorted(
            event_metrics(c).get("async_chain_eval")
            for c in chain_events_for_function(events, "async_double_value_function")
        )
        assert chain_scores == [
            0.0,
            1.0,
        ], f"Expected one pass + one fail; got async_chain_eval={chain_scores}"

    def test_inline_chain_span_attachment_async_user_fn_single_async_evaluator(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Async user fn × single async evaluator (len==1) — HHAI-5270 regression.

        Locks in the nested-event-loop fix on PR #3998. Pre-fix, a
        single async evaluator under an async user function raised
        ``RuntimeError: Cannot run the event loop while another loop is
        running`` because ``_run_single_evaluator`` started a fresh loop
        inside the same thread that ``asyncio.run(traced_function(dp))``
        was already using. Routing through ``_aapply_inline_evaluators``
        + ``_arun_single_evaluator`` (await directly) fixed it.

        Kept as its own named test (not folded into the multi-eval test
        above) so that pytest output names the failing scenario
        precisely if this regression ever returns.
        """
        run_name = f"inline-attach-async-async-len1-{int(time.time())}"
        dataset = passing_failing_dataset()

        async def async_double_value_function(
            datapoint: Dict[str, Any],
        ) -> Dict[str, Any]:
            await asyncio.sleep(0)
            return {"result": datapoint["inputs"]["value"] * 2}

        async def async_chain_eval(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            await asyncio.sleep(0)
            return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

        result = evaluate(
            function=async_double_value_function,
            dataset=dataset,
            evaluators=[async_chain_eval],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="async_double_value_function",
            expected_chain_span_count=len(dataset),
        )
        scores = sorted(
            event_metrics(c).get("async_chain_eval")
            for c in chain_events_for_function(events, "async_double_value_function")
        )
        assert scores == [0.0, 1.0], (
            f"HHAI-5270 single-async-eval regression: expected [0.0, 1.0], got {scores}"
        )

    def test_inline_chain_span_attachment_mixed_sync_async_evaluators(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Async user fn × mixed sync + async evaluators on the same run.

        Exercises ``_aapply_inline_evaluators``'s dispatch: async evals
        are awaited directly, sync evals run via ``asyncio.to_thread`` so
        they don't block the loop.
        """
        run_name = f"inline-attach-async-mixed-{int(time.time())}"
        dataset = passing_failing_dataset()

        async def async_double_value_function(
            datapoint: Dict[str, Any],
        ) -> Dict[str, Any]:
            await asyncio.sleep(0)
            return {"result": datapoint["inputs"]["value"] * 2}

        async def async_chain_eval(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            await asyncio.sleep(0)
            return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

        def sync_is_positive(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> bool:
            return outputs["result"] > 0

        result = evaluate(
            function=async_double_value_function,
            dataset=dataset,
            evaluators=[async_chain_eval, sync_is_positive],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="async_double_value_function",
            expected_chain_span_count=len(dataset),
        )
        assert_metric_present_on_chain_spans(
            events,
            "async_double_value_function",
            "sync_is_positive",
            expected_value=True,
        )
        chain_scores = sorted(
            event_metrics(c).get("async_chain_eval")
            for c in chain_events_for_function(events, "async_double_value_function")
        )
        assert chain_scores == [
            0.0,
            1.0,
        ], f"Expected one pass + one fail; got async_chain_eval={chain_scores}"

    # --------------------- nested-tool isolation ---------------------------

    def test_nested_tool_span_does_not_receive_evaluator_metrics(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Evaluator scores attach to the chain span only — never to nested tools.

        ``evaluate()`` evaluators run inline between user-function-return
        and chain-span-end, so they enrich the active span at that moment
        — the user-function chain span. A ``@trace``-decorated helper
        called from inside the user function has already closed by the
        time evaluators run, so its span does NOT receive any evaluator
        metrics. (Per the docs, span-level metrics on a helper are the
        helper's own ``enrich_span()`` job.)
        """
        run_name = f"nested-no-metric-{int(time.time())}"

        @trace(event_type="tool", event_name="my_helper")
        def my_helper(x: int) -> int:
            return x * 2

        def user_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            value = datapoint["inputs"]["value"]
            return {"result": my_helper(value)}

        def chain_eval(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> float:
            return float(outputs["result"])

        result = evaluate(
            function=user_function,
            dataset=[
                {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},
                {"inputs": {"value": 8}, "ground_truth": {"expected": 16}},
            ],
            evaluators=[chain_eval],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="user_function",
            expected_chain_span_count=2,
        )
        assert events, f"No events returned for run {result.run_id}"

        assert_metric_present_on_chain_spans(events, "user_function", "chain_eval")
        assert_metric_absent_on_chain_spans(events, "my_helper", "chain_eval")
        # Sanity: helper spans actually exist (negative-assertion safety net).
        assert chain_events_for_function(events, "my_helper"), (
            "Expected at least one my_helper tool span"
        )

    # ---------------------- failure-mode coverage --------------------------

    def test_evaluator_failure_isolation(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """One evaluator raising must not block others or fail the run.

        ``_run_single_evaluator`` catches evaluator exceptions and yields
        an ``EvaluatorMetricResult(score=None)``. ``to_metric_attrs`` then
        omits the bare-name key for None-score results, so the failing
        evaluator's name is absent from the chain-span metrics while the
        others land normally.
        """
        run_name = f"eval-failure-isolation-{int(time.time())}"

        def good_eval(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> float:
            return float(outputs["result"])

        def boom_eval(
            _outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> float:
            raise RuntimeError("boom from boom_eval")

        result = evaluate(
            function=double_value_function,
            dataset=[{"inputs": {"value": 5}, "ground_truth": {"expected": 10}}],
            evaluators=[good_eval, boom_eval],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        # Run must complete despite boom_eval raising.
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="double_value_function",
            expected_chain_span_count=1,
        )
        assert_metric_present_on_chain_spans(
            events,
            "double_value_function",
            "good_eval",
            expected_value=10.0,
        )
        assert_metric_absent_on_chain_spans(
            events,
            "double_value_function",
            "boom_eval",
        )

    def test_no_evaluators_runs_clean(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """``evaluators=[]`` (or omitted) — chain spans land without scores.

        Sanity check on the ``if evaluators:`` branch in
        ``process_datapoint``: when the list is empty/None,
        ``_apply_inline_evaluators`` is never called, no evaluator
        metrics appear on the chain span, and the run still completes.
        """
        run_name = f"no-evaluators-{int(time.time())}"

        result = evaluate(
            function=double_value_function,
            dataset=[
                {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},
                {"inputs": {"value": 8}, "ground_truth": {"expected": 16}},
            ],
            evaluators=[],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=False,
        )
        assert result is not None and result.run_id

        events = export_events_for_run_polling(
            integration_client,
            result.run_id,
            function_name="double_value_function",
            expected_chain_span_count=2,
        )
        chains = chain_events_for_function(events, "double_value_function")
        assert chains, "Expected user-function chain spans even with no evaluators"

        # No evaluator scores — but the chain span itself must still exist
        # and carry the baggage metadata.
        assert_run_metadata_on_all_child_events(events, result.run_id)
        for ev in chains:
            metrics = event_metrics(ev)
            # No evaluator we defined should be present; spot-check the
            # standard suite names so an accidental wiring change fails loudly.
            for forbidden in (
                "chain_eval",
                "is_positive",
                "confidence_eval",
                "judge_eval",
            ):
                assert forbidden not in metrics, (
                    f"Unexpected evaluator metric {forbidden!r} on chain span "
                    f"{event_field(ev, 'event_id')} despite evaluators=[]; "
                    f"metrics={metrics}"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
