"""The ingestion API key on the tracer's OTLP export, and on a whole ``evaluate()``.

The OTLP export routes are served by the ingestion endpoints but are not in
the Data Plane OpenAPI spec, so the spec-driven suite
(``test_ingestion_api_key_endpoints.py``) cannot list them. This module is
hand-maintained for that reason. It proves that a tracer holding only an
ingestion key exports spans the server accepts, and that the supported pair,
ingestion key for traces and project key for everything else, completes a
whole ``evaluate()`` run.

The ingestion key comes from ``HH_INGESTION_API_KEY``. Without it every test
here skips, so an environment that provisions only ``HH_API_KEY`` still runs
the rest of the suite.
"""

import os
import uuid
from typing import Any, Callable, List

import pytest

from honeyhive import HoneyHiveTracer, evaluate, trace
from honeyhive.api.client import HoneyHive
from tests.integration._experiments_helpers import (
    double_value_function,
    export_events_for_run_polling,
    passing_failing_dataset,
)

pytestmark = [pytest.mark.integration, pytest.mark.real_api, pytest.mark.slow]


def _data_plane_url() -> str:
    return os.environ.get("HH_API_URL", "https://api.dp1.us.honeyhive.ai")


def _names(events: List[Any]) -> List[Any]:
    return [getattr(event, "event_name", None) for event in events]


def _has_span(events: List[Any], function_name: str) -> bool:
    # `@trace` names a span after the decorated function's module and name.
    return any(str(name).endswith(f".{function_name}") for name in _names(events))


def test_span_export_travels_on_the_ingestion_key(
    real_ingestion_api_key: str,
    real_project: str,
    real_source: str,
    fetch_events: Callable[..., List[Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tracer holding only an ingestion key exports spans the server accepts."""
    session_name = f"ingestion-key-otlp-{uuid.uuid4().hex[:8]}"

    # The project key is out of reach while the client and tracer run, so the
    # session start and the export can only have travelled on the ingestion key.
    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)

        client = HoneyHive(
            ingestion_api_key=real_ingestion_api_key, base_url=_data_plane_url()
        )
        started = client.sessions.start(
            {
                "session": {
                    "project": real_project,
                    "session_name": session_name,
                    "source": real_source,
                }
            }
        )
        assert started.session_id

        tracer = HoneyHiveTracer(
            ingestion_api_key=real_ingestion_api_key,
            session_id=started.session_id,
            source=real_source,
            test_mode=False,
            disable_http_tracing=True,
        )
        try:
            assert tracer.api_key is None
            assert tracer.ingestion_api_key == real_ingestion_api_key

            @trace(event_type="tool")
            def double(value: int) -> int:
                return value * 2

            assert double(21) == 42
            tracer.force_flush()
        finally:
            tracer.shutdown()

    # Reading back is a Data Plane operation, which the ingestion key cannot
    # do, so it runs after the project key returns with the environment.
    events = fetch_events(
        started.session_id,
        project=real_project,
        min_events=1,
        predicate=lambda found: _has_span(found, "double"),
    )
    assert _has_span(events, "double"), f"span not ingested; saw {_names(events)}"


def test_evaluate_creates_the_run_and_lands_its_traces(
    real_api_key: str, real_ingestion_api_key: str
) -> None:
    """The supported pair: run creation on the project key, traces on the ingestion key."""
    dataset = passing_failing_dataset()
    result = evaluate(
        function=double_value_function,
        dataset=dataset,
        name=f"ingestion-key-evaluate-{uuid.uuid4().hex[:8]}",
        api_key=real_api_key,
        ingestion_api_key=real_ingestion_api_key,
        server_url=_data_plane_url(),
        print_results=False,
    )
    # Run creation is a Data Plane operation and went on the project key.
    assert result.run_id

    # The per-datapoint traces went to ingestion on the ingestion key. Read
    # them back with the project key; a wrong routing on either side would
    # have left the run without its chain spans.
    client = HoneyHive(api_key=real_api_key, base_url=_data_plane_url())
    events = export_events_for_run_polling(
        client,
        result.run_id,
        function_name=double_value_function.__name__,
        expected_chain_span_count=len(dataset),
    )
    chain_spans = [
        event
        for event in events
        if getattr(event, "event_name", None) == double_value_function.__name__
    ]
    assert len(chain_spans) == len(dataset), f"saw {_names(events)}"
