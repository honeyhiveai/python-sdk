"""The data plane API key against every data plane operation the SDK exposes, live.

Each entry of ``OPERATIONS`` performs a public SDK operation with only a data
plane key configured. It verifies effects through a project-key route when
one exists, or through the data plane route otherwise. Coverage is checked by
``tests/unit/test_data_plane_operations_match_the_spec.py``, which runs where
the spec is reachable; this module runs the entries where the server is.

``evaluate()`` has a test of its own, because it is one call over several
operations and also sends traces, which take the ingestion key. The event
reads have one too, because ``events.export`` sends its request without a
generated function, and ``OPERATIONS`` holds only what a generated function
sends.

The data plane key comes from ``HH_DATA_PLANE_API_KEY`` and the id of the
project it acts on from ``HH_PROJECT_ID``. Without either, the tests here skip.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.experiments import evaluate
from honeyhive.models import (
    AddDatapointsToDatasetRequest,
    CreateDatasetRequest,
    DatapointMapping,
    GetEventsQuery,
    PostEventRequest,
)
from tests.integration._data_plane_operations import OPERATIONS
from tests.integration._spec_operations import data_plane_url

pytestmark = [pytest.mark.integration, pytest.mark.real_api, pytest.mark.slow]


@pytest.mark.parametrize("operation", sorted(OPERATIONS))
def test_operation_accepts_the_data_plane_key_alone(
    operation: str,
    real_api_key: str,
    real_data_plane_api_key: str,
    real_project_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The wrapper reaches the server on a data plane key with no project key in reach."""
    # Each client holds one key, so the data plane client's request can only
    # have travelled on the data plane key. Entries may use the project client
    # to verify effects on APIs that also expose a project-key route.
    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)
        env.delenv("HH_DATA_PLANE_API_KEY", raising=False)
        data_plane = HoneyHive(
            data_plane_api_key=real_data_plane_api_key, base_url=data_plane_url()
        )
        project_client = HoneyHive(api_key=real_api_key, base_url=data_plane_url())
        assert data_plane.api_key == ""
        assert project_client.data_plane_api_key == ""

        OPERATIONS[operation](data_plane, project_client, real_project_id)


# How long the event read test polls for its event to become searchable. The
# search reads an index that fills after the event is accepted.
_EVENT_SEARCHABLE_TIMEOUT_SECONDS = 60.0
_EVENT_SEARCHABLE_POLL_SECONDS = 1.0


def test_event_reads_accept_the_data_plane_key_alone(
    real_api_key: str,
    real_data_plane_api_key: str,
    real_project_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """export() and list() with project_id read events on the data plane key.

    The arguments are ones only the older export request accepts as given: a
    range with ``$gte`` alone, a limit above the search's maximum, and a query
    model whose bounds are named ``gte`` and ``lte``. So the test also checks
    the body the SDK sends against the route that validates it.
    """

    def timestamp(moment: datetime) -> str:
        return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

    now = datetime.now(timezone.utc)
    start = timestamp(now - timedelta(hours=1))
    end = timestamp(now + timedelta(hours=1))
    session_id = str(uuid.uuid4())
    session_filter = {
        "field": "session_id",
        "operator": "is",
        "value": session_id,
        "type": "string",
    }

    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)
        env.delenv("HH_DATA_PLANE_API_KEY", raising=False)
        data_plane = HoneyHive(
            data_plane_api_key=real_data_plane_api_key, base_url=data_plane_url()
        )
        project_client = HoneyHive(api_key=real_api_key, base_url=data_plane_url())
        assert data_plane.api_key == ""

        event = project_client.events.create(
            PostEventRequest(
                event={
                    "source": "data-plane-key",
                    "event_name": f"data-plane-key-{uuid.uuid4().hex[:8]}",
                    "event_type": "tool",
                    "inputs": {},
                    "outputs": {},
                    "session_id": session_id,
                    "duration": 1.0,
                }
            )
        )

        exported: List[str] = []
        deadline = time.monotonic() + _EVENT_SEARCHABLE_TIMEOUT_SECONDS
        while not exported and time.monotonic() < deadline:
            response = data_plane.events.export(
                filters=[session_filter],
                date_range={"$gte": start},
                limit=5000,
                project_id=real_project_id,
            )
            exported = [found.event_id for found in response.events]
            if not exported:
                time.sleep(_EVENT_SEARCHABLE_POLL_SECONDS)
        assert exported == [event.event_id]

        listed = data_plane.events.list(
            GetEventsQuery.model_validate(
                {
                    "filters": [session_filter],
                    "dateRange": {"$gte": start, "$lte": end},
                    "limit": 10,
                }
            ),
            project_id=real_project_id,
        )
        assert [found.event_id for found in listed.events] == [event.event_id]


def test_evaluate_runs_with_no_project_key_in_reach(
    real_data_plane_api_key: str,
    real_ingestion_api_key: str,
    real_project_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """evaluate() with project_id needs only the data plane and ingestion keys.

    The dataset is a stored one, because only that mode reads the dataset and
    its datapoints. Setup, read-back and cleanup use the data plane key too,
    so the test never holds a project key.
    """
    suffix = uuid.uuid4().hex[:8]

    def answer(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"answer": inputs.get("query")}

    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)
        data_plane = HoneyHive(
            data_plane_api_key=real_data_plane_api_key, base_url=data_plane_url()
        )
        assert data_plane.api_key == ""

        dataset_id = data_plane.datasets.create(
            CreateDatasetRequest(name=f"evaluate-data-plane-key-{suffix}"),
            project_id=real_project_id,
        ).result.insertedId
        run_id = None
        try:
            added = data_plane.datasets.add_datapoints(
                dataset_id,
                AddDatapointsToDatasetRequest(
                    data=[{"query": f"evaluate-{suffix}", "answer": "a"}],
                    mapping=DatapointMapping(inputs=["query"], ground_truth=["answer"]),
                ),
                project_id=real_project_id,
            )
            assert len(added.datapoint_ids) == 1

            result = evaluate(
                function=answer,
                dataset_id=dataset_id,
                project_id=real_project_id,
                data_plane_api_key=real_data_plane_api_key,
                ingestion_api_key=real_ingestion_api_key,
                server_url=data_plane_url(),
                name=f"evaluate-data-plane-key-{suffix}",
                max_workers=1,
                print_results=False,
            )
            run_id = result.run_id

            run = data_plane.experiments.get_run(
                run_id, project_id=real_project_id
            ).evaluation
            assert run.scope_id == real_project_id
            assert run.dataset_id == dataset_id
            assert run.status == "completed"
            # One session per datapoint, started on the ingestion key and
            # linked to the run by the data plane key's update.
            assert len(run.event_ids) == 1
        finally:
            if run_id is not None:
                data_plane.experiments.delete_run(run_id, project_id=real_project_id)
            data_plane.datasets.delete(dataset_id, project_id=real_project_id)
