"""The ingestion API key against every ingestion operation the SDK exposes, live.

Each entry of ``OPERATIONS`` (see ``_ingestion_operations``) performs one
wrapped ingestion operation through the public wrapper on a client holding
only an ingestion key, and what it wrote is read back with the project key.
That the dictionary covers exactly the wrapped ingestion operations is asserted
by ``tests/unit/test_ingestion_operations_match_the_spec.py``, which runs where
the spec is reachable; this module runs the entries where the server is.

The tracer's OTLP export is not in the spec; ``test_ingestion_api_key_otlp.py``
covers it by hand. The ingestion key comes from ``HH_INGESTION_API_KEY``, and
without it the tests here skip.
"""

from typing import Any, Callable, List

import pytest

from honeyhive.api.client import HoneyHive
from tests.integration._ingestion_operations import OPERATIONS, data_plane_url

pytestmark = [pytest.mark.integration, pytest.mark.real_api, pytest.mark.slow]


@pytest.mark.parametrize("operation", sorted(OPERATIONS))
def test_operation_accepts_the_ingestion_key_alone(
    operation: str,
    real_ingestion_api_key: str,
    real_project: str,
    real_source: str,
    fetch_events: Callable[..., List[Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The wrapper reaches the server on an ingestion key with no project key in reach."""
    # The project key is out of reach while the client runs, so the request can
    # only have travelled on the ingestion key.
    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)
        client = HoneyHive(
            ingestion_api_key=real_ingestion_api_key, base_url=data_plane_url()
        )
        assert client.api_key == ""
        outcome = OPERATIONS[operation](client, real_project, real_source)

    # Reading back is a Data Plane operation, so it runs after the project key
    # returns with the environment.
    if outcome.landed is not None:
        events = fetch_events(
            outcome.session_id,
            project=real_project,
            min_events=1,
            predicate=outcome.landed,
        )
        names = [getattr(event, "event_name", None) for event in events]
        assert outcome.landed(events), f"{operation}: not ingested; saw {names}"
