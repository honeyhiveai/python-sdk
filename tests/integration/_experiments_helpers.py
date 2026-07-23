"""Shared helpers for the experiments integration test matrix.

The leading underscore keeps pytest from collecting this file as a test
module. Imported by the per-cell test files in the same directory.

The matrix the tests cover is:

::

    +----------------+--------------------+--------------------+
    |                | client-side evals  | server-side evals  |
    +----------------+--------------------+--------------------+
    | external dataset|       Cell 1      |       Cell 2       |
    | managed dataset |       Cell 3      |       Cell 4       |
    +----------------+--------------------+--------------------+

Cells 1 + 3 attach scores via the inline ``enrich_span(metrics=…)`` path
inside ``evaluate()``. Cells 2 + 4 attach scores asynchronously via the
backend evaluator pipeline against a metric whose ``event_name`` filter
matches the user-function chain span.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import pytest

from honeyhive import HoneyHive
from honeyhive.models import CreateDatapointRequest, CreateDatasetRequest, EventFilter

# --- Generic event helpers ---------------------------------------------------


def event_field(event: Any, name: str) -> Any:
    """Read ``event.<name>`` whether the response model exposes attrs or dict.

    Events come back from /events/export either as Pydantic instances or
    as plain dicts depending on response shape. Tests don't care which.
    """
    if isinstance(event, dict):
        return event.get(name)
    return getattr(event, name, None)


def event_metadata(event: Any) -> Dict[str, Any]:
    """Read ``event.metadata`` defensively (typed object or dict)."""
    md = event_field(event, "metadata")
    return md if isinstance(md, dict) else {}


def event_metrics(event: Any) -> Dict[str, Any]:
    """Read ``event.metrics`` defensively (typed object or dict)."""
    m = event_field(event, "metrics")
    return m if isinstance(m, dict) else {}


# --- Run-scoped event fetchers -----------------------------------------------


def export_events_for_run(
    client: HoneyHive,
    run_id: str,
    *,
    limit: int = 100,
) -> List[Any]:
    """Fetch every event tagged with ``metadata.run_id == run_id``.

    Uses the /events/export endpoint with a single equality filter on the
    baggage-injected run_id (see _baggage_injector in the SDK tracer).
    """
    response = client.events.export(
        filters=[
            EventFilter(
                field="metadata.run_id",
                operator="is",
                value=run_id,
                type="string",
            )
        ],
        limit=limit,
    )
    return list(getattr(response, "events", None) or [])


def export_events_for_run_polling(
    client: HoneyHive,
    run_id: str,
    *,
    function_name: str,
    expected_chain_span_count: int,
    poll_interval_sec: float = 1.0,
    max_wait_sec: float = 30.0,
    limit: int = 100,
) -> List[Any]:
    """Poll ``events.export`` until ``expected_chain_span_count`` chain spans appear.

    OTLP ingest is async; ``evaluate()`` returns as soon as the run-level
    write completes, but the per-datapoint chain spans flow through the
    OTLP pipeline and may take a beat to materialize via the legacy
    /events/export endpoint. Tests assert on chain-span shape, so they
    care that all expected spans are present before fetching — not just
    "at least one event."

    ``function_name`` is the user-function ``__name__`` (== chain-span
    ``event_name``). Returns the full event list once the count is
    satisfied; raises AssertionError on timeout with the last-seen state
    in the message.
    """
    deadline = time.monotonic() + max_wait_sec
    last_count = 0
    last_events: List[Any] = []
    while time.monotonic() < deadline:
        events = export_events_for_run(client, run_id, limit=limit)
        chains = [e for e in events if event_field(e, "event_name") == function_name]
        last_count = len(chains)
        last_events = events
        if last_count >= expected_chain_span_count:
            return events
        time.sleep(poll_interval_sec)

    raise AssertionError(
        f"Timed out after {max_wait_sec}s waiting for "
        f"{expected_chain_span_count} chain spans named {function_name!r} "
        f"on run {run_id}; last saw {last_count}. "
        f"Total events seen: {len(last_events)}."
    )


def chain_events_for_function(
    events: Iterable[Any],
    function_name: str,
) -> List[Any]:
    """Pick out the user-function chain spans from a flat event list.

    The chain span is named after the user function (``@trace`` uses
    ``event_name=function.__name__`` when ``evaluate()`` auto-wraps it).
    """
    return [e for e in events if event_field(e, "event_name") == function_name]


# --- Chain-span metric assertions --------------------------------------------


def assert_run_metadata_on_all_child_events(events: Iterable[Any], run_id: str) -> None:
    """Every chain/tool/model event must carry the three baggage IDs.

    The ingestion-side baggage injector stamps ``run_id``, ``dataset_id``,
    and ``datapoint_id`` onto each non-session event's metadata. This is
    the assertion HHAI-5269 unblocks; if it regresses, downstream
    comparison endpoints break silently.
    """
    for ev in events:
        if event_field(ev, "event_type") not in ("chain", "tool", "model"):
            continue
        md = event_metadata(ev)
        ev_id = event_field(ev, "event_id")
        ev_name = event_field(ev, "event_name")
        assert md.get("run_id") == run_id, (
            f"event {ev_id} ({ev_name}) missing run_id; metadata={md}"
        )
        assert md.get("dataset_id"), f"event {ev_id} ({ev_name}) missing dataset_id"
        assert md.get("datapoint_id"), f"event {ev_id} ({ev_name}) missing datapoint_id"


def assert_metric_present_on_chain_spans(
    events: Iterable[Any],
    function_name: str,
    metric_name: str,
    *,
    expected_value: Any = None,
) -> None:
    """Assert ``metric_name`` lands on every ``function_name`` chain span.

    If ``expected_value`` is provided, asserts equality; otherwise just
    checks the key is present and not None.
    """
    chains = chain_events_for_function(events, function_name)
    assert chains, f"Expected at least one chain span named {function_name!r}"
    for ev in chains:
        m = event_metrics(ev)
        ev_id = event_field(ev, "event_id")
        if expected_value is None:
            assert metric_name in m and m[metric_name] is not None, (
                f"chain span {ev_id} missing metric {metric_name!r}; metrics={m}"
            )
        else:
            assert m.get(metric_name) == expected_value, (
                f"chain span {ev_id} expected {metric_name}={expected_value!r}, got {m.get(metric_name)!r}; metrics={m}"
            )


def assert_metric_absent_on_chain_spans(
    events: Iterable[Any],
    function_name: str,
    metric_name: str,
) -> None:
    """Assert ``metric_name`` does NOT appear on any ``function_name`` chain span.

    Used to verify negative paths — e.g. evaluator that raised, or a
    nested ``@trace`` helper that should not receive evaluator metrics.
    """
    chains = chain_events_for_function(events, function_name)
    assert chains, f"Expected at least one chain span named {function_name!r}"
    for ev in chains:
        m = event_metrics(ev)
        assert metric_name not in m, (
            f"metric {metric_name!r} unexpectedly on chain span {event_field(ev, 'event_id')}; metrics={m}"
        )


# --- Server-side evaluator polling -------------------------------------------


def require_server_side_eval_creds() -> Tuple[str, str]:
    """Return ``(model_name, model_provider)`` for server-side evaluator tests.

    Defaults to the lightweight ``mock_llm`` provider backed by the
    mock-llm docker-compose service.  ``OPENAI_API_KEY`` alone is **not**
    enough — set ``HH_EVALUATOR_E2E_USE_OPENAI=1`` together with
    ``OPENAI_API_KEY`` to opt in to real cloud OpenAI.

    Returns:
        ``(model_name, model_provider)`` — caller passes both into
        ``CreateMetricRequest``.
    """
    use_openai = os.environ.get("HH_EVALUATOR_E2E_USE_OPENAI", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if use_openai:
        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("HH_EVALUATOR_E2E_USE_OPENAI=1 but OPENAI_API_KEY is not set.")
        return "gpt-4o-mini", "openai"

    # deterministic/default/default has no latency and error_rate=0, so
    # evaluator calls are instant.  See mock_provider_config.yaml.
    return "deterministic/default/default", "mock_llm"


def poll_for_server_side_score_on_chain(
    client: HoneyHive,
    run_id: str,
    function_name: str,
    metric_name: str,
    *,
    expected_chain_span_count: Optional[int] = None,
    poll_interval_sec: float = 3.0,
    max_wait_sec: float = 180.0,
) -> Any:
    """Poll until ``metric_name`` appears on every chain span for ``run_id``.

    The server-side evaluator pipeline is async — once the chain span is
    ingested, the backend's evaluator service computes the metric and
    re-emits the event with ``metrics[metric_name]`` populated. We poll
    /events/export filtered by run_id until we see the metric on every
    chain span (or time out).

    ``expected_chain_span_count`` guards against a subtle early-return
    race: OTLP ingest is async and per-datapoint chain spans materialize
    independently, so at any poll only a subset may be visible. Without
    an expected count the "all visible chains are scored" condition is
    trivially satisfied the instant the *first* chain span lands scored,
    and a caller that then re-fetches events sees fewer chains than
    datapoints (the ``assert 1 == 2`` flake). When set, we require both
    that all ``expected_chain_span_count`` chain spans are present *and*
    that every one is scored before returning.

    Returns the first chain event with the metric attached (so the caller
    can read additional fields like ``{metric}_explanation``).
    """
    deadline = time.monotonic() + max_wait_sec
    last_state = "<no events>"
    while time.monotonic() < deadline:
        events = export_events_for_run(client, run_id)
        chains = chain_events_for_function(events, function_name)
        if chains:
            scored = [c for c in chains if metric_name in event_metrics(c)]
            count_ready = (
                expected_chain_span_count is None
                or len(chains) >= expected_chain_span_count
            )
            all_scored = bool(scored) and len(scored) == len(chains)
            if count_ready and all_scored:
                return scored[0]
            waiting = (
                f"; need {expected_chain_span_count} chain spans"
                if expected_chain_span_count is not None
                else ""
            )
            last_state = (
                f"{len(scored)}/{len(chains)} chain spans scored "
                f"(waiting on {len(chains) - len(scored)}){waiting}"
            )
        else:
            last_state = "no chain spans yet"
        time.sleep(poll_interval_sec)

    raise AssertionError(
        f"Timed out after {max_wait_sec}s waiting for server-side metric "
        f"{metric_name!r} on every chain span of run {run_id}. "
        f"Last state: {last_state}"
    )


# --- Convenience constructors used across cells ------------------------------


def passing_failing_dataset() -> List[Dict[str, Any]]:
    """Two-datapoint external dataset where one passes and one fails.

    Used by inline-attachment tests so we can assert behavior on both
    branches of ground-truth-comparing evaluators.
    """
    return [
        {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},  # pass
        {"inputs": {"value": 8}, "ground_truth": {"expected": 99}},  # fail
    ]


def double_value_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
    """Reference user function: doubles the input value into ``result``.

    Many cells share this — keeping it factored prevents drift on the
    chain span name (``__name__ == 'double_value_function'``).
    """
    return {"result": datapoint["inputs"]["value"] * 2}


# --- Evaluator factory exercising every accepted return shape ----------------


def standard_evaluator_suite() -> List[Callable]:
    """Four evaluators covering scalar / bool / dict-with-explanation / dict-with-extras.

    Returned as a list so tests can pass it directly to
    ``evaluate(evaluators=...)``. Each evaluator is named so its score
    surfaces under that key on the chain span.
    """

    # Scalar float — bare ``metrics[name]``.
    def chain_eval(
        outputs: Dict[str, Any],
        _inputs: Dict[str, Any],
        ground_truth: Dict[str, Any],
    ) -> float:
        return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

    # Scalar bool — pass-through; compare-runs aggregates booleans.
    def is_positive(
        outputs: Dict[str, Any],
        _inputs: Dict[str, Any],
        _ground_truth: Dict[str, Any],
    ) -> bool:
        return outputs["result"] > 0

    # Dict with score + explanation — adds ``{name}_explanation``.
    def confidence_eval(
        _outputs: Dict[str, Any],
        _inputs: Dict[str, Any],
        _ground_truth: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {"score": 0.75, "explanation": "moderate confidence"}

    # Dict with extras (scalar) — flattened to ``{name}_{key}``.
    def judge_eval(
        outputs: Dict[str, Any],
        _inputs: Dict[str, Any],
        ground_truth: Dict[str, Any],
    ) -> Dict[str, Any]:
        passed = outputs["result"] == ground_truth["expected"]
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "exact match" if passed else "mismatch",
            "passed": passed,
            "category": "exact" if passed else "off",
        }

    return [chain_eval, is_positive, confidence_eval, judge_eval]


# --- Managed dataset CRUD helpers --------------------------------------------


def _get_id_from_object(obj: Any) -> Optional[str]:
    """Extract the inserted-document id from a CreateDataset/Datapoint response.

    The HoneyHive API exposes the new id under several different keys
    depending on endpoint version (``insertedId`` / ``inserted_id`` /
    ``_id`` / ``id``) and may return a list under ``insertedIds``. Walk
    them in order; return the first non-empty value as a string.
    """
    for key in ("insertedId", "inserted_id", "_id", "id"):
        if isinstance(obj, dict):
            id_value = obj.get(key)
        else:
            id_value = getattr(obj, key, None)
        if id_value:
            return str(id_value)
    ids_list = (
        obj.get("insertedIds")
        if isinstance(obj, dict)
        else getattr(obj, "insertedIds", None)
    )
    if ids_list:
        return str(ids_list[0])
    return None


def create_managed_dataset(
    client: HoneyHive,
    project: str,
    name: str,
    datapoints: List[Dict[str, Any]],
    *,
    description: str = "Integration test dataset",
) -> str:
    """Create a managed dataset + linked datapoints; return the dataset_id."""
    created_dataset = client.datasets.create_dataset(
        CreateDatasetRequest(project=project, name=name, description=description)
    )
    dataset_id = _get_id_from_object(getattr(created_dataset, "result", None))
    assert dataset_id, f"Could not extract dataset_id for {name}"

    for dp in datapoints:
        client.datapoints.create_datapoint(
            CreateDatapointRequest(
                inputs=dp["inputs"],
                ground_truth=dp.get("ground_truth"),
                linked_datasets=[dataset_id],
                project=project,
                history=None,
                linked_event=None,
                metadata=None,
            )
        )
    return dataset_id


def safe_delete_dataset(client: HoneyHive, dataset_id: str) -> None:
    """Best-effort dataset cleanup — log-and-continue on failure."""
    try:
        client.datasets.delete_dataset(dataset_id)
    except Exception as exc:  # noqa: BLE001 - cleanup must not raise
        print(f"⚠️  Dataset cleanup error for {dataset_id}: {exc}")


def assert_standard_suite_attached_to_chain_spans(
    events: Iterable[Any],
    function_name: str,
    *,
    expected_dataset_size: int,
) -> None:
    """Verify the four ``standard_evaluator_suite`` shapes survive end-to-end.

    Asserts that every chain span carries:
    * scalar-float ``chain_eval`` (one pass + one fail across the run)
    * scalar-bool ``is_positive`` (always True for our positive inputs)
    * dict ``confidence_eval`` + ``confidence_eval_explanation``
    * dict-with-extras ``judge_eval`` + ``_explanation`` + ``_passed`` + ``_category``
    * judge_eval + chain_eval encode the same pass/fail outcome per datapoint
    """
    chains = chain_events_for_function(events, function_name)
    assert len(chains) == expected_dataset_size, (
        f"Expected {expected_dataset_size} chain spans named {function_name!r}, got {len(chains)}"
    )

    seen_chain_eval_values: List[Any] = []
    for ev in chains:
        metrics = event_metrics(ev)
        ev_id = event_field(ev, "event_id")

        assert metrics.get("is_positive") is True, (
            f"is_positive (bool return) missing/wrong on event_id={ev_id}; metrics={metrics}"
        )
        assert metrics.get("confidence_eval") == 0.75, (
            f"confidence_eval (dict return) missing/wrong; metrics={metrics}"
        )
        assert metrics.get("confidence_eval_explanation") == "moderate confidence", (
            f"confidence_eval_explanation missing/wrong; metrics={metrics}"
        )

        chain_score = metrics.get("chain_eval")
        assert chain_score in (
            0.0,
            1.0,
        ), f"chain_eval should be 0.0 or 1.0; got {chain_score!r}"
        seen_chain_eval_values.append(chain_score)

        judge_score = metrics.get("judge_eval")
        assert judge_score == chain_score, (
            "judge_eval and chain_eval encode the same passed/failed outcome "
            "and must agree on this datapoint; "
            f"got chain_eval={chain_score!r}, judge_eval={judge_score!r}"
        )
        judge_passed = metrics.get("judge_eval_passed")
        assert isinstance(judge_passed, bool), (
            f"judge_eval_passed (extras flattened, bool) should be a native "
            f"bool; got {type(judge_passed).__name__} value={judge_passed!r}"
        )
        assert judge_passed == (chain_score == 1.0), (
            f"judge_eval_passed inconsistent with chain_eval (chain={chain_score!r}, passed={judge_passed!r})"
        )
        if judge_passed:
            assert metrics.get("judge_eval_explanation") == "exact match"
            assert metrics.get("judge_eval_category") == "exact"
        else:
            assert metrics.get("judge_eval_explanation") == "mismatch"
            assert metrics.get("judge_eval_category") == "off"

    # Sanity: with the standard pass+fail dataset we exercise both branches.
    if expected_dataset_size == 2:
        assert sorted(seen_chain_eval_values) == [
            0.0,
            1.0,
        ], (
            f"Expected one passing and one failing chain span; got chain_eval values={seen_chain_eval_values}"
        )
