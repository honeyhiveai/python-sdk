"""Integration tests — managed dataset × server-side evaluators (Cell 4).

Same backend evaluator pipeline as Cell 2, but the ``evaluate()`` run
sources its datapoints from a HoneyHive-managed dataset (created via
``client.datasets.create_dataset`` + linked datapoints) rather than an
inline external list.

Defaults to the lightweight ``mock_llm`` provider backed by the
mock-llm docker-compose service. Set ``HH_EVALUATOR_E2E_USE_OPENAI=1``
with ``OPENAI_API_KEY`` to use real cloud OpenAI instead.
"""

# pylint: disable=R0801
# Justification: shared metric + dataset setup pattern with the other
# matrix cells.

import os
import uuid
from typing import Any, Dict, Optional

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import evaluate
from honeyhive.models import CreateMetricRequest, CreateMetricResponse
from tests.integration._experiments_helpers import (
    assert_run_metadata_on_all_child_events,
    chain_events_for_function,
    create_managed_dataset,
    event_field,
    event_metrics,
    export_events_for_run,
    poll_for_server_side_score_on_chain,
    require_server_side_eval_creds,
    safe_delete_dataset,
)


def _build_llm_metric_request(
    metric_name: str, function_name: str, model_name: str, model_provider: str
) -> CreateMetricRequest:
    """LLM metric scoped to a single user-function chain span."""
    criteria = (
        "You evaluate a single HoneyHive trace event (inputs, outputs, "
        "metadata). Respond with exactly one score from 1 to 5 for overall "
        "trace usefulness. Use this exact format: [[3]] (replace 3 with "
        "your integer score)."
    )
    return CreateMetricRequest(
        name=metric_name,
        type="LLM",
        description="E2E LLM evaluator (managed dataset × server-side cell)",
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


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsManagedServerSide:
    """managed dataset × server-side LLM evaluator."""

    def test_server_side_llm_evaluator_on_evaluate_run(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Create dataset + LLM metric, run evaluate(), poll for async scoring."""
        del real_api_key  # only here for fixture wiring; client carries the key
        model_name, model_provider = require_server_side_eval_creds()

        test_id = uuid.uuid4().hex[:10]
        metric_name = f"e2e_managed_server_{test_id}"
        function_name = f"e2e_managed_user_fn_{test_id}"
        dataset_name = f"managed-server-side-{test_id}"
        run_name = f"e2e-managed-server-side-{test_id}"

        datapoints = [
            {"inputs": {"prompt": "say one word"}, "ground_truth": None},
            {"inputs": {"prompt": "another short prompt"}, "ground_truth": None},
        ]

        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        metric_id: Optional[str] = None
        try:
            created = integration_client.metrics.create(
                _build_llm_metric_request(
                    metric_name, function_name, model_name, model_provider
                )
            )
            assert isinstance(created, CreateMetricResponse)
            assert created.inserted is True
            metric_id = created.metric_id

            def _make_user_fn():  # noqa: D401 — local helper
                def _user_fn(datapoint: Dict[str, Any]) -> Dict[str, Any]:
                    return {
                        "output": (
                            "Integration test response for prompt: "
                            + str(datapoint.get("inputs", {}).get("prompt", ""))
                        )
                    }

                _user_fn.__name__ = function_name
                _user_fn.__qualname__ = function_name
                return _user_fn

            user_function = _make_user_fn()

            result = evaluate(
                function=user_function,
                dataset_id=dataset_id,  # managed path
                evaluators=None,  # server-side scoring only
                api_key=integration_client.api_key,
                project=real_project,
                name=run_name,
                max_workers=2,
                verbose=False,
            )
            assert result is not None and result.run_id

            scored_event = poll_for_server_side_score_on_chain(
                integration_client,
                result.run_id,
                function_name,
                metric_name,
            )
            scored_metrics = event_metrics(scored_event)
            raw_score = scored_metrics[metric_name]
            assert isinstance(raw_score, (int, float)), (
                f"server-side metric must be numeric; got "
                f"{type(raw_score).__name__}={raw_score!r}"
            )
            score = float(raw_score)
            assert 0.0 <= score <= 5.0, f"score out of range: {score}"

            explanation_key = f"{metric_name}_explanation"
            if explanation_key in scored_metrics:
                assert isinstance(scored_metrics[explanation_key], str)

            # Verify dataset_id on every chain event matches the managed
            # dataset (no ``EXT-`` prefix) — same regression coverage as
            # Cell 3.
            events = export_events_for_run(integration_client, result.run_id)
            chains = chain_events_for_function(events, function_name)
            assert len(chains) == len(datapoints)
            for ev in chains:
                md = event_field(ev, "metadata") or {}
                if isinstance(md, dict):
                    md_ds = str(md.get("dataset_id", ""))
                    assert md_ds == str(dataset_id), (
                        f"chain {event_field(ev, 'event_id')} dataset_id "
                        f"{md_ds!r} != managed dataset_id {dataset_id!r}"
                    )
                    assert not md_ds.startswith("EXT-"), (
                        f"managed-server cell unexpectedly produced EXT- "
                        f"dataset_id {md_ds!r}"
                    )

                m = event_metrics(ev)
                assert metric_name in m and isinstance(m[metric_name], (int, float))

            assert_run_metadata_on_all_child_events(events, result.run_id)

        finally:
            if metric_id:
                try:
                    integration_client.metrics.delete(metric_id)
                except Exception as exc:  # noqa: BLE001 — cleanup
                    print(f"⚠️  metric cleanup error for {metric_id}: {exc}")
            safe_delete_dataset(integration_client, dataset_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
