"""Integration tests — external dataset × server-side evaluators (Cell 2).

Server-side evaluators (a.k.a. backend metrics) are configured in the
project rather than passed as Python callables to ``evaluate()``. They
fire asynchronously after OTLP ingest: the data plane's evaluator
service runs the metric against any event whose properties match the
metric's filter and re-emits the event with ``metrics[<metric_name>]``
populated.

This cell proves the wiring works when the trace producer is
``evaluate()`` (not raw tracer + start_span like
``test_evaluator_e2e.py``). The user function is auto-wrapped with
``@trace(event_type="chain", event_name=function.__name__, ...)``, so
filtering the metric on ``event_name=<function_name>`` scopes the
evaluator to exactly the chain spans this test produces — important to
avoid xdist cross-talk on the shared integration project.

Defaults to the lightweight ``mock_llm`` provider backed by the
mock-llm docker-compose service. Set ``HH_EVALUATOR_E2E_USE_OPENAI=1``
with ``OPENAI_API_KEY`` to use real cloud OpenAI instead.
"""

# pylint: disable=R0801
# Justification: shared metric-create / poll / cleanup pattern with
# managed-server-side cell and the standalone evaluator e2e test.

import os
import time
import uuid
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import evaluate
from honeyhive.models import CreateMetricRequest, CreateMetricResponse
from tests.integration._experiments_helpers import (
    assert_run_metadata_on_all_child_events,
    chain_events_for_function,
    event_metrics,
    export_events_for_run_polling,
    poll_for_server_side_score_on_chain,
    require_server_side_eval_creds,
)


def _build_llm_metric_request(
    metric_name: str, function_name: str, model_name: str, model_provider: str
) -> CreateMetricRequest:
    """LLM metric scoped to a single user-function chain span.

    ``filterArray`` matches our auto-traced chain span exactly so the
    backend evaluator pipeline only fires on this test's events; this is
    important under pytest-xdist where many tests share the integration
    project.
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
        description="E2E LLM evaluator (external dataset × server-side cell)",
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
@pytest.mark.xdist_group("server_side_eval")
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsExternalServerSide:
    """external dataset × server-side LLM evaluator."""

    def test_server_side_llm_evaluator_on_evaluate_run(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Create LLM metric → run evaluate() → wait for async scoring → assert."""
        del real_api_key  # only here for fixture wiring; client carries the key
        model_name, model_provider = require_server_side_eval_creds()

        test_id = uuid.uuid4().hex[:10]
        metric_name = f"e2e_external_server_{test_id}"
        # Per-run user-function name keeps the metric's event_name filter
        # tight even when this test runs alongside the managed cell.
        function_name = f"e2e_external_user_fn_{test_id}"
        run_name = f"e2e-external-server-side-{test_id}"

        # Two datapoints — assertion is "every chain span gets scored",
        # so we want >1 to prove the polling loop waits for ALL chains
        # rather than just the first.
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
            assert created.inserted is True, "metrics.create should report inserted"
            metric_id = created.metric_id

            # Build a user function whose ``__name__`` equals
            # ``function_name`` so the chain span's event_name lines up
            # with the metric's filterArray. ``def`` syntax doesn't
            # support runtime names, so create via a small factory.
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

            # Run with no client-side evaluators — the only metric scoring
            # this run is the server-side LLM metric we just created.
            result = evaluate(
                function=user_function,
                dataset=dataset,
                evaluators=None,
                api_key=integration_client.api_key,
                project=real_project,
                name=run_name,
                max_workers=2,
                verbose=False,
            )
            assert result is not None and result.run_id, (
                "evaluate() must return a run_id"
            )

            # Poll /events/export for chain spans tagged with our run_id
            # until all datapoints' chain spans are present AND every one
            # has metrics[metric_name]. The explicit count guards against
            # returning as soon as the first-landed chain span is scored.
            scored_event = poll_for_server_side_score_on_chain(
                integration_client,
                result.run_id,
                function_name,
                metric_name,
                expected_chain_span_count=len(dataset),
            )
            scored_metrics = event_metrics(scored_event)
            raw_score = scored_metrics[metric_name]
            assert isinstance(raw_score, (int, float)), (
                f"server-side metric must be numeric; got {type(raw_score).__name__}={raw_score!r}"
            )
            score = float(raw_score)
            assert 0.0 <= score <= 5.0, f"score out of range: {score}"

            explanation_key = f"{metric_name}_explanation"
            if explanation_key in scored_metrics:
                # When the LLM evaluator emits an explanation, it should
                # be a string (matches server-side
                # metric_update_service.js shape). If absent, that's also
                # OK — explanation is optional in the LLM eval pipeline.
                assert isinstance(scored_metrics[explanation_key], str), (
                    f"{explanation_key} should be str; got {type(scored_metrics[explanation_key]).__name__}"
                )

            # All chain spans (one per datapoint) ended up scored. Poll for
            # the full set so async OTLP ingest of the last chain span can't
            # race the assertion.
            events = export_events_for_run_polling(
                integration_client,
                result.run_id,
                function_name=function_name,
                expected_chain_span_count=len(dataset),
            )
            chains = chain_events_for_function(events, function_name)
            assert len(chains) == len(dataset), (
                f"Expected {len(dataset)} chain spans, got {len(chains)}"
            )
            for ev in chains:
                m = event_metrics(ev)
                assert metric_name in m and isinstance(m[metric_name], (int, float)), (
                    f"server-side metric {metric_name!r} missing or non-numeric on chain span; metrics={m}"
                )

            # Baggage IDs still propagate even when no client-side
            # evaluators run — the baggage injector lives in the tracer,
            # not in the eval pipeline.
            assert_run_metadata_on_all_child_events(events, result.run_id)

        finally:
            if metric_id:
                try:
                    integration_client.metrics.delete(metric_id)
                except Exception as exc:  # noqa: BLE001 — cleanup
                    print(f"⚠️  metric cleanup error for {metric_id}: {exc}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
