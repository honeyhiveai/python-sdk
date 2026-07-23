"""Integration tests — ``compare_runs()`` / event-level comparison.

Three layers of coverage:

1. **Datapoint pairing** — explicit regression coverage for HHAI-3934
   (`compare_runs` returning 0 common datapoints for the same external
   dataset). The same external-dataset list across two runs must
   produce the same ``EXT-`` content-hashed datapoint IDs, and the
   comparison endpoint must pair them. The managed-dataset path uses
   the real Mongo IDs assigned at create time.

2. **Metric deltas + event-level pairing** — ``compare_runs`` and
   ``compare_run_events`` must surface evaluator scores from the chain
   spans that PR #3998 emits to. Pre-HHAI-5272 these returned empty
   ``metric_deltas`` because pairing was keyed on
   ``metric_name|event_name`` and the user-function-named chain span
   never matched across two runs.

3. **Matrix coverage** — exercises all four quadrants of (external,
   managed) × (client-side, server-side) for ``compare_runs``. The
   server-side cells default to the lightweight ``mock_llm`` provider
   (mock-llm docker-compose service); set
   ``HH_EVALUATOR_E2E_USE_OPENAI=1`` with ``OPENAI_API_KEY`` to opt into
   real cloud OpenAI scoring.
"""

# pylint: disable=R0801

import os
import time
import uuid
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import compare_runs, evaluate
from honeyhive.models import CreateMetricRequest, CreateMetricResponse
from tests.integration._experiments_helpers import (
    create_managed_dataset,
    export_events_for_run_polling,
    poll_for_server_side_score_on_chain,
    require_server_side_eval_creds,
    safe_delete_dataset,
)


def _build_llm_metric_request(
    metric_name: str, function_name: str, model_name: str, model_provider: str
) -> CreateMetricRequest:
    """LLM metric scoped to a single user-function chain span.

    Mirrors the helper in ``test_experiments_external_server_side.py``
    so server-side comparison cells exercise the same evaluator pipeline
    as the dedicated server-side cells.
    """
    criteria = (
        "You evaluate a single HoneyHive trace event (inputs, outputs, "
        "metadata). Respond with exactly one score from 1 to 5 for overall "
        "trace usefulness. Use this exact format: [[3]] (replace 3 with "
        "your integer score)."
    )
    return CreateMetricRequest(
        name=metric_name,
        type="LLM",
        description="E2E LLM evaluator (run-comparison matrix coverage)",
        criteria=criteria,
        return_type="float",
        scale=5,
        threshold={"min": 1, "max": 5},
        model_provider=model_provider,
        model_name=model_name,
        enabled_in_prod=True,
        sampling_percentage=100.0,
        needs_ground_truth=False,
        filters={
            "filterArray": [
                {
                    "field": "event_name",
                    "operator": "is",
                    "value": function_name,
                    "type": "string",
                }
            ]
        },
    )


def _make_named_user_fn(function_name: str):
    """Build a user function whose ``__name__`` matches the given name.

    The chain span's event_name comes from ``function.__name__``, and
    server-side metric filterArrays target that. Lambda/``def`` syntax
    doesn't accept runtime names, so we synthesize via a local factory.
    """

    def _user_fn(datapoint: Dict[str, Any]) -> Dict[str, Any]:
        prompt = str(datapoint.get("inputs", {}).get("prompt", ""))
        return {"output": f"Integration test response for prompt: {prompt}"}

    _user_fn.__name__ = function_name
    _user_fn.__qualname__ = function_name
    return _user_fn


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.xdist_group("server_side_eval")
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsRunComparison:
    """Multi-run comparison via compare_runs() and /runs/compare/events."""

    # --------------- HHAI-3934 datapoint-pairing regression ---------------

    def test_compare_runs_datapoint_pairing_for_same_external_dataset(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """HHAI-3934 regression: same external dataset → same EXT- IDs → paired.

        ``evaluate(dataset=…)`` generates content-hashed ``EXT-`` IDs for
        each datapoint. Two runs against the same Python list must
        produce the same IDs so the comparison endpoint can match them.
        Pre-fix this returned ``common_datapoints == 0``.

        Asserts only the datapoint-pairing guarantee — not the metric
        deltas (HHAI-5272 dependency, covered by the skiplisted
        ``test_compare_runs_with_metric_improvements_and_regressions``
        below).
        """
        dataset = [
            {"inputs": {"value": 1}, "ground_truth": {"expected": 2}},
            {"inputs": {"value": 2}, "ground_truth": {"expected": 4}},
            {"inputs": {"value": 3}, "ground_truth": {"expected": 6}},
        ]

        def doubler(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": datapoint["inputs"]["value"] * 2}

        timestamp = int(time.time())
        run_a = evaluate(
            function=doubler,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=f"hhai3934-external-a-{timestamp}",
            max_workers=2,
            verbose=False,
        )
        run_b = evaluate(
            function=doubler,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=f"hhai3934-external-b-{timestamp}",
            max_workers=2,
            verbose=False,
        )
        assert run_a and run_a.run_id and run_b and run_b.run_id

        # Wait for ClickHouse to materialize all chain spans for both runs
        # before comparing. compare_runs builds each run's datapoints list
        # from ClickHouse session events; if the newer run's events haven't
        # propagated yet, common_datapoints comes back short and the
        # assertion below flakes.
        for run_id in (run_a.run_id, run_b.run_id):
            export_events_for_run_polling(
                integration_client,
                run_id,
                function_name="doubler",
                expected_chain_span_count=len(dataset),
            )

        comparison = compare_runs(
            client=integration_client,
            new_run_id=run_b.run_id,
            old_run_id=run_a.run_id,
            project_id=real_project,
            aggregate_function="average",
        )
        assert comparison is not None
        assert comparison.new_run_id == run_b.run_id
        assert comparison.old_run_id == run_a.run_id

        # The HHAI-3934 root-cause assertions:
        assert comparison.common_datapoints == len(dataset), (
            f"HHAI-3934 regression: same external dataset across two "
            f"evaluate() runs must produce {len(dataset)} common "
            f"datapoints (content-hashed EXT- IDs); got "
            f"{comparison.common_datapoints}"
        )
        assert comparison.new_only_datapoints == 0, (
            f"Same external dataset must yield zero new-only datapoints; got {comparison.new_only_datapoints}"
        )
        assert comparison.old_only_datapoints == 0, (
            f"Same external dataset must yield zero old-only datapoints; got {comparison.old_only_datapoints}"
        )

    def test_compare_runs_datapoint_pairing_for_same_managed_dataset(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """HHAI-3934 regression: same managed dataset → same Mongo IDs → paired.

        Managed datasets identify each datapoint by the Mongo ID assigned
        at create time, not by content hash. Two ``evaluate()`` runs
        against the same ``dataset_id`` must therefore see exactly the
        same datapoint IDs and pair every datapoint in
        ``compare_runs``.
        """
        timestamp = int(time.time())
        dataset_name = f"hhai3934-managed-{timestamp}"
        datapoints = [
            {"inputs": {"value": 1}, "ground_truth": {"expected": 2}},
            {"inputs": {"value": 2}, "ground_truth": {"expected": 4}},
            {"inputs": {"value": 3}, "ground_truth": {"expected": 6}},
        ]
        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        try:

            def doubler(datapoint: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": datapoint["inputs"]["value"] * 2}

            run_a = evaluate(
                function=doubler,
                dataset_id=dataset_id,
                api_key=real_api_key,
                project=real_project,
                name=f"hhai3934-managed-a-{timestamp}",
                max_workers=2,
                verbose=False,
            )
            run_b = evaluate(
                function=doubler,
                dataset_id=dataset_id,
                api_key=real_api_key,
                project=real_project,
                name=f"hhai3934-managed-b-{timestamp}",
                max_workers=2,
                verbose=False,
            )
            assert run_a and run_a.run_id and run_b and run_b.run_id

            # Wait for ClickHouse to materialize all chain spans for both
            # runs before comparing — see external-dataset variant above
            # for the rationale (common_datapoints flake).
            for run_id in (run_a.run_id, run_b.run_id):
                export_events_for_run_polling(
                    integration_client,
                    run_id,
                    function_name="doubler",
                    expected_chain_span_count=len(datapoints),
                )

            comparison = compare_runs(
                client=integration_client,
                new_run_id=run_b.run_id,
                old_run_id=run_a.run_id,
                project_id=real_project,
                aggregate_function="average",
            )
            assert comparison is not None
            assert comparison.common_datapoints == len(datapoints), (
                f"HHAI-3934 regression (managed path): same managed "
                f"dataset across two evaluate() runs must produce "
                f"{len(datapoints)} common datapoints; got "
                f"{comparison.common_datapoints}"
            )
            assert comparison.new_only_datapoints == 0, (
                f"Same managed dataset must yield zero new-only datapoints; got {comparison.new_only_datapoints}"
            )
            assert comparison.old_only_datapoints == 0, (
                f"Same managed dataset must yield zero old-only datapoints; got {comparison.old_only_datapoints}"
            )
        finally:
            safe_delete_dataset(integration_client, dataset_id)

    # ------- Metric-deltas + event-level (HHAI-5272 skiplisted) ----------

    def test_compare_runs_with_metric_improvements_and_regressions(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Detect improved + regressed metrics across two runs on the same dataset."""
        # Shared dataset for both runs — same content → same EXT- IDs →
        # comparable datapoint pairing.
        dataset = [
            {
                "inputs": {"value": 10, "task": "double"},
                "ground_truth": {"expected": 20},
            },
            {
                "inputs": {"value": 15, "task": "triple"},
                "ground_truth": {"expected": 45},
            },
            {
                "inputs": {"value": 8, "task": "quadruple"},
                "ground_truth": {"expected": 32},
            },
        ]

        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            return 1.0 if actual == expected else 0.0

        def error_rate_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            if expected == 0:
                return 0.0
            error = abs(actual - expected) / abs(expected)
            return max(0.0, 1.0 - error)

        # IMPORTANT: both runs use the SAME target function name (`predictor`).
        # Cross-run pairing keys on metric_name|event_name; chain-span
        # event_name comes from `function.__name__`. Renaming the target
        # between runs is documented anti-pattern — it intentionally splits
        # the metric across two event_name buckets in compare output. We
        # mimic the realistic "edit the function in-place" workflow by
        # building two implementations and assigning the same __name__.
        def _baseline_impl(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            task = inputs.get("task", "")
            if task == "double":
                result = value * 2
            elif task == "triple":
                result = value * 2  # intentionally wrong
            elif task == "quadruple":
                result = value * 3  # intentionally wrong
            else:
                result = 0
            return {"result": result, "method": "baseline"}

        def _improved_impl(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            task = inputs.get("task", "")
            if task == "double":
                result = value * 2
            elif task == "triple":
                result = value * 3  # fixed
            elif task == "quadruple":
                result = value * 3  # still wrong
            else:
                result = 0
            return {"result": result, "method": "improved"}

        _baseline_impl.__name__ = "predictor"
        _baseline_impl.__qualname__ = "predictor"
        _improved_impl.__name__ = "predictor"
        _improved_impl.__qualname__ = "predictor"

        baseline = evaluate(
            function=_baseline_impl,
            dataset=dataset,
            evaluators=[accuracy_evaluator, error_rate_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"comparison-baseline-{int(time.time())}",
            max_workers=2,
            verbose=False,
        )
        assert baseline and baseline.run_id

        improved = evaluate(
            function=_improved_impl,
            dataset=dataset,
            evaluators=[accuracy_evaluator, error_rate_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"comparison-improved-{int(time.time())}",
            max_workers=2,
            verbose=False,
        )
        assert improved and improved.run_id

        # Wait for ClickHouse to materialize chain spans for both runs;
        # otherwise compare_runs reads a partial set and metric_deltas /
        # common_datapoints assertions flake.
        for run_id in (baseline.run_id, improved.run_id):
            export_events_for_run_polling(
                integration_client,
                run_id,
                function_name="predictor",
                expected_chain_span_count=len(dataset),
            )

        comparison = compare_runs(
            client=integration_client,
            new_run_id=improved.run_id,
            old_run_id=baseline.run_id,
            project_id=real_project,
            aggregate_function="average",
        )

        assert comparison is not None
        assert comparison.new_run_id == improved.run_id
        assert comparison.old_run_id == baseline.run_id
        assert comparison.common_datapoints == 3
        assert comparison.new_only_datapoints == 0
        assert comparison.old_only_datapoints == 0
        assert (
            comparison.metric_deltas is not None and len(comparison.metric_deltas) > 0
        )
        # Encode the fixture's intent: _improved_impl fixes the `triple`
        # datapoint (returns value*3 vs baseline's value*2), so accuracy
        # must surface as improved — not just "non-empty deltas". This
        # catches a future regression where pairing direction flips or
        # the metric is silently lost.
        improved_metrics = comparison.list_improved_metrics()
        assert "accuracy_evaluator" in improved_metrics, (
            f"accuracy_evaluator should improve baseline→improved on the "
            f"triple datapoint; got improved metrics: {improved_metrics}"
        )

    def test_event_level_comparison(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """/runs/compare/events returns paired events keyed by datapoint_id."""
        dataset = [
            {"inputs": {"value": 10}, "ground_truth": {"expected": 20}},
            {"inputs": {"value": 15}, "ground_truth": {"expected": 30}},
            {"inputs": {"value": 8}, "ground_truth": {"expected": 16}},
        ]

        def baseline_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": datapoint["inputs"]["value"] * 2}

        def modified_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            value = datapoint["inputs"]["value"]
            multiplier = 2.5 if value > 12 else 2.0
            return {"result": value * multiplier}

        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

        baseline = evaluate(
            function=baseline_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"event-comparison-baseline-{int(time.time())}",
            max_workers=2,
            verbose=False,
        )
        assert baseline and baseline.run_id

        modified = evaluate(
            function=modified_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"event-comparison-modified-{int(time.time())}",
            max_workers=2,
            verbose=False,
        )
        assert modified and modified.run_id

        # Wait for ClickHouse to materialize chain spans for each run
        # before the event-level comparison query. Each run uses a
        # distinct function name (anti-pattern by design — the comparison
        # endpoint pairs by datapoint_id, not event_name).
        export_events_for_run_polling(
            integration_client,
            baseline.run_id,
            function_name="baseline_function",
            expected_chain_span_count=len(dataset),
        )
        export_events_for_run_polling(
            integration_client,
            modified.run_id,
            function_name="modified_function",
            expected_chain_span_count=len(dataset),
        )

        comparison_response = integration_client.evaluations.compare_run_events(
            new_run_id=modified.run_id,
            old_run_id=baseline.run_id,
            event_type="session",
            limit=100,
        )
        assert comparison_response is not None

        events = comparison_response.events
        assert len(events) == len(dataset)
        for event_pair in events:
            datapoint_id = event_pair.datapoint_id
            event_1 = event_pair.event_1
            event_2 = event_pair.event_2
            assert event_1["metadata"]["datapoint_id"] == datapoint_id
            assert event_2["metadata"]["datapoint_id"] == datapoint_id

    # ----------- Matrix coverage: managed × client-side -----------------

    def test_compare_runs_with_metric_improvements_managed_dataset(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Managed dataset variant of the metric_deltas regression test.

        Mirrors ``test_compare_runs_with_metric_improvements_and_regressions``
        but routes through a managed dataset so the (managed × client-side)
        quadrant of the comparison matrix has explicit coverage.
        """
        timestamp = int(time.time())
        dataset_name = f"compare-managed-clientside-{timestamp}"
        datapoints = [
            {"inputs": {"value": 10}, "ground_truth": {"expected": 20}},
            {"inputs": {"value": 15}, "ground_truth": {"expected": 45}},
            {"inputs": {"value": 8}, "ground_truth": {"expected": 32}},
        ]
        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        try:

            def accuracy_evaluator(
                outputs: Dict[str, Any],
                _inputs: Dict[str, Any],
                ground_truth: Dict[str, Any],
            ) -> float:
                return (
                    1.0
                    if outputs.get("result") == ground_truth.get("expected")
                    else 0.0
                )

            # Both runs share the same target function name (`predictor`)
            # so chain-span event_name aligns and metric_deltas pair across
            # runs. Renaming the target between runs is documented anti-
            # pattern; the canonical case is "edit the function in-place,
            # re-run, compare".
            def _baseline_impl(datapoint: Dict[str, Any]) -> Dict[str, Any]:
                # Always doubles — wrong for the value=15 (expected 45) and
                # value=8 (expected 32) datapoints; right for value=10.
                return {"result": datapoint["inputs"]["value"] * 2}

            def _improved_impl(datapoint: Dict[str, Any]) -> Dict[str, Any]:
                # Returns the expected value directly so accuracy diverges
                # from baseline, producing a non-empty metric_delta.
                value = datapoint["inputs"]["value"]
                if value == 10:
                    return {"result": 20}
                if value == 15:
                    return {"result": 45}
                return {"result": 32}

            _baseline_impl.__name__ = "predictor"
            _baseline_impl.__qualname__ = "predictor"
            _improved_impl.__name__ = "predictor"
            _improved_impl.__qualname__ = "predictor"

            baseline = evaluate(
                function=_baseline_impl,
                dataset_id=dataset_id,
                evaluators=[accuracy_evaluator],
                api_key=real_api_key,
                project=real_project,
                name=f"compare-managed-baseline-{timestamp}",
                max_workers=2,
                verbose=False,
            )
            improved = evaluate(
                function=_improved_impl,
                dataset_id=dataset_id,
                evaluators=[accuracy_evaluator],
                api_key=real_api_key,
                project=real_project,
                name=f"compare-managed-improved-{timestamp}",
                max_workers=2,
                verbose=False,
            )
            assert baseline and baseline.run_id and improved and improved.run_id

            # Wait for ClickHouse to materialize chain spans for both
            # runs before comparing — see external variant for rationale.
            for run_id in (baseline.run_id, improved.run_id):
                export_events_for_run_polling(
                    integration_client,
                    run_id,
                    function_name="predictor",
                    expected_chain_span_count=len(datapoints),
                )

            comparison = compare_runs(
                client=integration_client,
                new_run_id=improved.run_id,
                old_run_id=baseline.run_id,
                project_id=real_project,
                aggregate_function="average",
            )
            assert comparison is not None
            assert comparison.common_datapoints == len(datapoints)
            assert (
                comparison.metric_deltas is not None
                and len(comparison.metric_deltas) > 0
            ), (
                "managed × client-side run comparison must surface at least one metric delta"
            )
        finally:
            safe_delete_dataset(integration_client, dataset_id)

    # ----------- Matrix coverage: external × server-side ----------------

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "HHAI-5662: metric_deltas can come back empty when the evaluation "
            "pipeline is cold — scores land on chain spans but aren't yet "
            "visible to compare_runs"
        ),
    )
    def test_compare_runs_with_server_side_metric_external_dataset(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Server-side LLM metric scored across two runs on an external dataset.

        Creates a project-scoped LLM metric, runs ``evaluate()`` twice (no
        client-side evaluators), polls until both runs' chain spans are
        scored, then asserts ``compare_runs`` surfaces the metric in
        ``metric_deltas``.
        """
        del real_api_key  # client carries the key
        model_name, model_provider = require_server_side_eval_creds()

        test_id = uuid.uuid4().hex[:10]
        metric_name = f"e2e_compare_external_server_{test_id}"
        function_name = f"e2e_compare_external_user_fn_{test_id}"
        dataset = [
            {"inputs": {"prompt": "say one word"}, "ground_truth": None},
            {"inputs": {"prompt": "another short prompt"}, "ground_truth": None},
        ]

        metric_id: str | None = None
        try:
            created = integration_client.metrics.create(
                _build_llm_metric_request(
                    metric_name, function_name, model_name, model_provider
                )
            )
            assert isinstance(created, CreateMetricResponse)
            assert created.inserted is True
            metric_id = created.metric_id

            user_function = _make_named_user_fn(function_name)
            baseline = evaluate(
                function=user_function,
                dataset=dataset,
                evaluators=None,
                api_key=integration_client.api_key,
                project=real_project,
                name=f"compare-external-server-baseline-{test_id}",
                max_workers=2,
                verbose=False,
            )
            improved = evaluate(
                function=user_function,
                dataset=dataset,
                evaluators=None,
                api_key=integration_client.api_key,
                project=real_project,
                name=f"compare-external-server-improved-{test_id}",
                max_workers=2,
                verbose=False,
            )
            assert baseline and baseline.run_id and improved and improved.run_id

            poll_for_server_side_score_on_chain(
                integration_client,
                baseline.run_id,
                function_name,
                metric_name,
                expected_chain_span_count=len(dataset),
            )
            poll_for_server_side_score_on_chain(
                integration_client,
                improved.run_id,
                function_name,
                metric_name,
                expected_chain_span_count=len(dataset),
            )

            comparison = compare_runs(
                client=integration_client,
                new_run_id=improved.run_id,
                old_run_id=baseline.run_id,
                project_id=real_project,
                aggregate_function="average",
            )
            assert comparison is not None
            assert comparison.common_datapoints == len(dataset)
            assert (
                comparison.metric_deltas is not None
                and len(comparison.metric_deltas) > 0
            ), (
                f"external × server-side comparison must surface at least one metric delta; expected {metric_name!r}"
            )
        finally:
            if metric_id:
                try:
                    integration_client.metrics.delete(metric_id)
                except Exception as exc:  # noqa: BLE001 — cleanup
                    print(f"⚠️  metric cleanup error for {metric_id}: {exc}")

    # ----------- Matrix coverage: managed × server-side -----------------

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "HHAI-5662: metric_deltas can come back empty when the evaluation "
            "pipeline is cold — scores land on chain spans but aren't yet "
            "visible to compare_runs"
        ),
    )
    def test_compare_runs_with_server_side_metric_managed_dataset(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Managed dataset variant of the server-side comparison matrix cell."""
        del real_api_key  # client carries the key
        model_name, model_provider = require_server_side_eval_creds()

        test_id = uuid.uuid4().hex[:10]
        metric_name = f"e2e_compare_managed_server_{test_id}"
        function_name = f"e2e_compare_managed_user_fn_{test_id}"
        dataset_name = f"compare-managed-server-{test_id}"
        datapoints = [
            {"inputs": {"prompt": "say one word"}, "ground_truth": None},
            {"inputs": {"prompt": "another short prompt"}, "ground_truth": None},
        ]
        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        metric_id: str | None = None
        try:
            created = integration_client.metrics.create(
                _build_llm_metric_request(
                    metric_name, function_name, model_name, model_provider
                )
            )
            assert isinstance(created, CreateMetricResponse)
            assert created.inserted is True
            metric_id = created.metric_id

            user_function = _make_named_user_fn(function_name)
            baseline = evaluate(
                function=user_function,
                dataset_id=dataset_id,
                evaluators=None,
                api_key=integration_client.api_key,
                project=real_project,
                name=f"compare-managed-server-baseline-{test_id}",
                max_workers=2,
                verbose=False,
            )
            improved = evaluate(
                function=user_function,
                dataset_id=dataset_id,
                evaluators=None,
                api_key=integration_client.api_key,
                project=real_project,
                name=f"compare-managed-server-improved-{test_id}",
                max_workers=2,
                verbose=False,
            )
            assert baseline and baseline.run_id and improved and improved.run_id

            poll_for_server_side_score_on_chain(
                integration_client,
                baseline.run_id,
                function_name,
                metric_name,
                expected_chain_span_count=len(datapoints),
            )
            poll_for_server_side_score_on_chain(
                integration_client,
                improved.run_id,
                function_name,
                metric_name,
                expected_chain_span_count=len(datapoints),
            )

            comparison = compare_runs(
                client=integration_client,
                new_run_id=improved.run_id,
                old_run_id=baseline.run_id,
                project_id=real_project,
                aggregate_function="average",
            )
            assert comparison is not None
            assert comparison.common_datapoints == len(datapoints)
            assert (
                comparison.metric_deltas is not None
                and len(comparison.metric_deltas) > 0
            ), (
                f"managed × server-side comparison must surface at least one metric delta; expected {metric_name!r}"
            )
        finally:
            if metric_id:
                try:
                    integration_client.metrics.delete(metric_id)
                except Exception as exc:  # noqa: BLE001 — cleanup
                    print(f"⚠️  metric cleanup error for {metric_id}: {exc}")
            safe_delete_dataset(integration_client, dataset_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
