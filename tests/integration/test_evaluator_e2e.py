"""End-to-end integration test for server-side LLM evaluators (HHAI-4323).

Validates the federated golden path: create LLM metric -> ingest trace ->
async evaluation -> scores on event -> scores readable via DP event export
(``events.get_by_session_id``). Control Plane ``events.list`` is not used here
because project API keys authenticate the Data Plane; CP ``GET /events`` expects
a user/session token and returns 401 for API-key-only clients.

Requires a live stack and project-scoped API key. Defaults to the lightweight
``mock_llm`` provider backed by the mock-llm docker-compose service. Set
``HH_EVALUATOR_E2E_USE_OPENAI=1`` with ``OPENAI_API_KEY`` to use real cloud
OpenAI instead.

The created metric includes an ``event_name`` filter matching the test span so
evaluation does not run on every event in the shared integration project under
``pytest-xdist``.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateMetricRequest, CreateMetricResponse
from honeyhive.tracer import HoneyHiveTracer
from tests.integration._experiments_helpers import require_server_side_eval_creds


def _event_to_dict(event: Any) -> dict[str, Any]:
    """Normalize an event from export/list APIs to a dict."""
    if isinstance(event, dict):
        return event
    if hasattr(event, "model_dump"):
        return event.model_dump()
    return dict(event)


def _metrics_map(event: Any) -> dict[str, Any]:
    """Return the ``metrics`` bucket from an event, or {}."""
    raw = _event_to_dict(event).get("metrics")
    return raw if isinstance(raw, dict) else {}


def _poll_for_metric_score(
    client: HoneyHive,
    session_id: str,
    metric_name: str,
    *,
    poll_interval_sec: float = 3.0,
    max_wait_sec: float = 180.0,
) -> dict[str, Any]:
    """Poll ``get_by_session_id`` until ``metric_name`` appears in event metrics.

    Args:
        client: ``HoneyHive`` client.
        session_id: Session to load events for.
        metric_name: Evaluator name as stored on the event.
        poll_interval_sec: Sleep between attempts.
        max_wait_sec: Total wall time before failing.

    Returns:
        The first event dict that contains ``metric_name`` in ``metrics``.

    Raises:
        AssertionError: If the score never appears within the timeout.
    """
    deadline = time.monotonic() + max_wait_sec
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            export = client.events.get_by_session_id(session_id=session_id)
            events = getattr(export, "events", None) or []
            for ev in events:
                metrics = _metrics_map(ev)
                if metric_name in metrics:
                    return _event_to_dict(ev)
            last_error = f"no metric {metric_name!r} yet ({len(events)} events)"
        except Exception as exc:  # noqa: BLE001 - propagate after timeout only
            last_error = str(exc)
        time.sleep(poll_interval_sec)

    raise AssertionError(
        f"Timed out after {max_wait_sec}s waiting for metric {metric_name!r}. Last state: {last_error}"
    )


@pytest.mark.integration
@pytest.mark.xdist_group("server_side_eval")
class TestEvaluatorLlmE2E:
    """Server-side LLM evaluator pipeline via Python SDK (trace -> scores)."""

    def test_llm_evaluator_async_pipeline_end_to_end(
        self,
        integration_client: HoneyHive,
        real_api_key: str,
        real_project: str,
        real_source: str,
    ) -> None:
        """Create LLM metric, emit trace, wait for evaluator scores, verify APIs."""
        model_name, model_provider = require_server_side_eval_creds()

        if (
            not integration_client.api_key
            or integration_client.api_key == "test-api-key-12345"
        ):
            pytest.fail(
                "Real API credentials required — configure HH_API_KEY for integration"
            )

        test_id = uuid.uuid4().hex[:10]
        metric_name = f"e2e_llm_eval_{test_id}"
        # Per-run OTLP span name; metric filter matches stored ``event_name``.
        span_name = f"e2e_llm_eval_span_{test_id}"
        metric_id: str | None = None

        criteria = (
            "You evaluate a single HoneyHive trace event (inputs, outputs, metadata). "
            "Respond with exactly one score from 1 to 5 for overall trace usefulness. "
            "Use this exact format: [[3]] (replace 3 with your integer score)."
        )

        create_req = CreateMetricRequest(
            name=metric_name,
            type="LLM",
            description="E2E LLM evaluator integration test (HHAI-4323)",
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
                        "value": span_name,
                        "type": "string",
                    }
                ]
            },
        )

        try:
            created = integration_client.metrics.create(create_req)
            assert isinstance(created, CreateMetricResponse)
            assert created.inserted is True
            metric_id = created.metric_id

            session_name = f"e2e-llm-eval-session-{test_id}"
            tracer = HoneyHiveTracer.init(
                api_key=real_api_key,
                project=real_project,
                source=real_source,
                session_name=session_name,
                test_mode=False,
                disable_batch=True,
                verbose=False,
            )
            session_id = tracer.session_id
            assert session_id, "Tracer must produce a session_id"

            with tracer.start_span(span_name) as span:
                span.set_attribute("honeyhive.project", real_project)
                span.set_attribute(
                    "output",
                    "Integration test assistant output for LLM evaluation scoring.",
                )

            tracer.force_flush()
            tracer.shutdown()

            scored_event = _poll_for_metric_score(
                integration_client,
                session_id,
                metric_name,
            )
            metrics = _metrics_map(scored_event)
            raw_score = metrics[metric_name]
            assert isinstance(raw_score, (int, float)), (
                f"metric score must be numeric, got {type(raw_score)}: {raw_score!r}"
            )
            score = float(raw_score)
            assert 0.0 <= score <= 5.0, f"score out of range: {score}"

            explanation_key = f"{metric_name}_explanation"
            if explanation_key in metrics:
                assert isinstance(metrics[explanation_key], str)

            # Second export read proves scores stay queryable (same DP path as polling).
            export_again = integration_client.events.get_by_session_id(
                session_id=session_id
            )
            again_events = getattr(export_again, "events", None) or []
            found_again = False
            for ev in again_events:
                m = _metrics_map(ev)
                if metric_name in m and isinstance(m[metric_name], (int, float)):
                    found_again = True
                    break
            assert found_again, (
                f"Expected metric score on repeat get_by_session_id export (session_id={session_id})"
            )

        finally:
            if metric_id:
                try:
                    integration_client.metrics.delete(metric_id)
                except Exception:
                    pass
