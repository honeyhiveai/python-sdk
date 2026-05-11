"""Integration test — manual ``enrich_span()`` inside ``evaluate()``.

Different surface from the matrix cells: instead of letting
``evaluate()`` auto-attach evaluator scores via the inline path, the
user function (and a nested ``@trace``-decorated helper) call
``enrich_span()`` themselves to attach metadata, metrics, config, and
feedback. This is the documented pattern for span-level enrichment on
nested helpers.

We verify those manual enrichments survive the OTLP export and land on
the corresponding events fetched via /events/export.
"""

# pylint: disable=R0801

import os
import time
from typing import Any, Dict, List, Tuple

import pytest

from honeyhive import HoneyHive, enrich_span, trace
from honeyhive.experiments import evaluate
from honeyhive.models import EventFilter


def _fetch_all_session_events(client: HoneyHive, session_ids: List[Any]) -> List[Any]:
    """Fetch all events across the given session IDs via /events/export."""
    all_events: List[Any] = []
    for session_id in session_ids:
        try:
            session_id_str = str(session_id)
            response = client.events.export(
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value=session_id_str,
                        type="string",
                    )
                ],
                limit=1000,
            )
            session_events = list(getattr(response, "events", []) or [])
            all_events.extend(session_events)
        except Exception as exc:  # noqa: BLE001 - best-effort fetch
            print(f"⚠️  Could not fetch events for session {session_id}: {exc}")
    return all_events


def _validate_enrichments(events: List[Any]) -> Tuple[bool, bool]:
    """Walk events, return (found_eval_function, found_helper_function)."""
    found_eval = False
    found_helper = False
    for event in events:
        metadata = getattr(event, "metadata", {}) or {}
        if isinstance(metadata, dict):
            if metadata.get("evaluation_function") == "text_evaluator":
                found_eval = True
            if metadata.get("helper_function") == "text_processor":
                found_helper = True

        # Numeric-metric sanity check on whatever events carry metrics.
        metrics = getattr(event, "metrics", {}) or {}
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                assert isinstance(value, (int, float, bool)), (
                    f"Metric {key!r} on event must be scalar; "
                    f"got {type(value).__name__}={value!r}"
                )
    return found_eval, found_helper


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsManualEnrichSpan:
    """Manual ``enrich_span()`` integration with ``evaluate()``."""

    @pytest.mark.slow
    def test_evaluate_with_nested_enrich_span_backend_validation(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Nested enrichment from parent + child @trace functions reaches the backend.

        Validates:
        1. Nested function calls (``evaluation_function`` →
           ``helper_function``) each create their own span.
        2. ``enrich_span()`` calls in both parent and child attach
           metadata, metrics, config, feedback to the right span.
        3. Backend events fetched via /events/export carry the enriched
           properties (not just the events' existence).
        """
        calls: List[str] = []

        @trace(event_type="tool", event_name="helper_function")
        def helper_function(text: str, multiplier: int) -> str:
            calls.append("helper_called")
            enrich_span(
                metadata={
                    "helper_function": "text_processor",
                    "text_length": len(text),
                    "multiplier": multiplier,
                    "nested_level": "1",
                },
                metrics={
                    "processing_complexity": len(text) * multiplier,
                    "helper_call_count": len(
                        [c for c in calls if c == "helper_called"]
                    ),
                },
            )
            return text.upper() * multiplier

        @trace(event_type="chain", event_name="evaluation_function")
        def evaluation_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            calls.append("eval_called")
            inputs = datapoint.get("inputs", {})
            text = inputs.get("text", "")
            multiplier = inputs.get("multiplier", 1)

            enrich_span(
                metadata={
                    "evaluation_function": "text_evaluator",
                    "input_text": text,
                    "input_multiplier": multiplier,
                },
                metrics={
                    "eval_call_count": len([c for c in calls if c == "eval_called"]),
                    "total_call_count": len(calls),
                },
                config={
                    "model": "test-model-v1",
                    "temperature": 0.7,
                    "max_tokens": 100,
                },
            )

            processed_text = helper_function(text, multiplier)

            enrich_span(
                metrics={"output_length": len(processed_text)},
                feedback={"quality": "high", "nested_processing": "successful"},
            )

            return {"result": processed_text, "status": "completed"}

        dataset = [
            {"inputs": {"text": "hello", "multiplier": 2}},
            {"inputs": {"text": "world", "multiplier": 3}},
        ]
        run_name = f"nested-enrich-{int(time.time())}"

        result = evaluate(
            function=evaluation_function,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=1,  # serial for clearer trace hierarchy
            verbose=False,
        )
        assert result is not None and result.run_id

        # Backend processing window for OTLP → event materialization.
        time.sleep(5)

        backend_run = integration_client.evaluations.get_run(result.run_id)
        assert (
            hasattr(backend_run, "evaluation") and backend_run.evaluation
        ), "Backend response missing 'evaluation' field"
        run_data = backend_run.evaluation
        session_ids = getattr(run_data, "event_ids", []) or []
        assert session_ids, "Should have recorded session events"

        all_events = _fetch_all_session_events(integration_client, session_ids)
        assert all_events, "Backend returned no events for these sessions"

        found_eval, found_helper = _validate_enrichments(all_events)
        assert found_eval, (
            "evaluation_function enrichment NOT FOUND in backend — "
            "parent @trace + enrich_span() did not persist"
        )
        assert found_helper, (
            "helper_function enrichment NOT FOUND in backend — "
            "nested @trace + enrich_span() did not persist"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
