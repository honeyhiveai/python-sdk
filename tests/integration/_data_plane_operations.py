"""The data plane key operations the SDK exposes, and how to call each on a data plane key.

The Data Plane OpenAPI spec declares which operations take a fine-grained data
plane key: those whose ``security`` names the ``DataPlaneApiKey`` scheme. Each
names a project in its path. The SDK exposes some of them through ``HoneyHive``
wrappers, and each wrapper passes the data plane configuration. ``OPERATIONS``
ties the two together: keyed by operationId, each value performs the operation
through the public wrapper on a client holding only a data plane key, and
checks its effect with a client holding only the project key.

Two tests consume it. ``tests/unit/test_data_plane_operations_match_the_spec.py``
asserts its keys equal the wrapped data plane operations (the spec's set,
intersected with the operations the shim calls a generated service function
for), so a new wrapper for a data plane route fails until it has an entry. It
runs in the unit job, where the ``openapi/dataplane.yaml`` symlink resolves.
``tests/integration/test_data_plane_api_key_endpoints.py`` runs every entry
live. Operations the spec declares but the SDK does not wrap are unsupported
and have no entry.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict

import pytest

from honeyhive._generated.api_config import HTTPException
from honeyhive.api.client import HoneyHive
from honeyhive.models import (
    AddDatapointsToDatasetRequest,
    BatchCreateDatapointsRequest,
    BatchCreateDatapointsResponse,
    ChartQueryRequest,
    CreateChartRequest,
    CreateDatapointRequest,
    CreateDatasetRequest,
    DatapointMapping,
    PostEventRequest,
    PostExperimentRunRequest,
    PutExperimentRunRequest,
    UpdateChartRequest,
    UpdateDatapointRequest,
    UpdateDatasetRequest,
)

DATA_PLANE_SCHEME = "DataPlaneApiKey"

# (client holding only a data plane key, client holding only the project key,
# the id of the project both keys act on) -> None. An entry asserts its own
# effect.
Entry = Callable[[HoneyHive, HoneyHive, str], None]


def _chart_name() -> str:
    return f"data-plane-key-{uuid.uuid4().hex[:8]}"


def _create_on_the_project_key(project_client: HoneyHive, name: str) -> str:
    """Create a chart through the unscoped route, for an entry to act on."""
    created = project_client.charts.create(
        CreateChartRequest(name=name, metric="event_count")
    )
    return created.data.id


def _delete_quietly(project_client: HoneyHive, chart_id: str) -> None:
    """Remove an entry's chart, so a run against a persistent project leaves nothing.

    It goes through the project key and the unscoped route, so the cleanup
    does not depend on the operation under test. A failure is printed rather
    than raised, so it cannot mask the entry's own result.
    """
    try:
        project_client.charts.delete(chart_id)
    except Exception as exc:  # noqa: BLE001 - cleanup must not raise
        print(f"Chart cleanup failed for {chart_id}: {exc}")


def get_charts(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.list``: a chart made on the project key is in the project's list."""
    chart_id = _create_on_the_project_key(project_client, _chart_name())
    try:
        listed = data_plane.charts.list(project_id=project_id)

        assert chart_id in {chart.id for chart in listed.data}
    finally:
        _delete_quietly(project_client, chart_id)


def get_chart(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.get``: a chart made on the project key is read back."""
    name = _chart_name()
    chart_id = _create_on_the_project_key(project_client, name)
    try:
        fetched = data_plane.charts.get(chart_id, project_id=project_id)

        assert fetched.data.name == name
    finally:
        _delete_quietly(project_client, chart_id)


def query_chart(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.query``: a scalar count over the last day succeeds."""
    del project_client
    now = datetime.now(timezone.utc)
    request = ChartQueryRequest.model_validate(
        {
            "date_range": {
                "start_time": (now - timedelta(days=1)).isoformat(),
                "end_time": now.isoformat(),
            },
            "filters": [
                {
                    "field": "event_type",
                    "operator": "is",
                    "value": "model",
                    "type": "string",
                }
            ],
            "query": {"kind": "scalar", "measure": {"metric": "event_count"}},
        }
    )

    result = data_plane.charts.query(request, project_id=project_id)

    assert result.success is True


def create_chart(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.create``: the chart is found on the project key afterwards."""
    name = _chart_name()

    created = data_plane.charts.create(
        CreateChartRequest(name=name, metric="event_count"), project_id=project_id
    )
    try:
        assert project_client.charts.get(created.data.id).data.name == name
    finally:
        _delete_quietly(project_client, created.data.id)


def update_chart(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.update``: the new name is read back on the project key."""
    chart_id = _create_on_the_project_key(project_client, _chart_name())
    try:
        renamed = _chart_name()
        data_plane.charts.update(
            chart_id, UpdateChartRequest(name=renamed), project_id=project_id
        )

        assert project_client.charts.get(chart_id).data.name == renamed
    finally:
        _delete_quietly(project_client, chart_id)


def delete_chart(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``charts.delete``: the chart is gone on the project key afterwards."""
    chart_id = _create_on_the_project_key(project_client, _chart_name())
    deleted = False
    try:
        data_plane.charts.delete(chart_id, project_id=project_id)
        deleted = True

        with pytest.raises(HTTPException) as exc_info:
            project_client.charts.get(chart_id)
        assert exc_info.value.status_code == 404
    finally:
        if not deleted:
            _delete_quietly(project_client, chart_id)


def _create_datapoint_on_the_project_key(project_client: HoneyHive) -> str:
    """Create a datapoint through the unscoped route, for an entry to act on."""
    created = project_client.datapoints.create(
        CreateDatapointRequest(
            inputs={"query": f"data-plane-key-{uuid.uuid4().hex[:8]}"}
        )
    )
    return created.result.insertedIds[0]


def _delete_datapoint_quietly(project_client: HoneyHive, datapoint_id: str) -> None:
    """Remove an entry's datapoint, as ``_delete_quietly`` does for a chart."""
    try:
        project_client.datapoints.delete(datapoint_id)
    except Exception as exc:  # noqa: BLE001 - cleanup must not raise
        print(f"Datapoint cleanup failed for {datapoint_id}: {exc}")


def get_datapoints(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datapoints.list``: a datapoint made on the project key is listed by its id."""
    datapoint_id = _create_datapoint_on_the_project_key(project_client)
    try:
        listed = data_plane.datapoints.list([datapoint_id], project_id=project_id)

        assert [datapoint.id for datapoint in listed.datapoints] == [datapoint_id]
    finally:
        _delete_datapoint_quietly(project_client, datapoint_id)


def get_datapoint(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datapoints.get``: a datapoint made on the project key is read back."""
    datapoint_id = _create_datapoint_on_the_project_key(project_client)
    try:
        fetched = data_plane.datapoints.get(datapoint_id, project_id=project_id)

        assert [datapoint.id for datapoint in fetched.datapoint] == [datapoint_id]
    finally:
        _delete_datapoint_quietly(project_client, datapoint_id)


def create_datapoint(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """Create with the data plane key and read the datapoint back on the project key."""
    query = f"data-plane-key-{uuid.uuid4().hex[:8]}"
    created = data_plane.datapoints.create(
        CreateDatapointRequest(inputs={"query": query}), project_id=project_id
    )
    [datapoint_id] = created.result.insertedIds
    try:
        assert created.inserted
        fetched = project_client.datapoints.get(datapoint_id)
        assert [
            (datapoint.id, datapoint.inputs) for datapoint in fetched.datapoint
        ] == [(datapoint_id, {"query": query})]
    finally:
        _delete_datapoint_quietly(project_client, datapoint_id)


# How long create_batch_datapoints polls for its event to reach object storage,
# which the batch route reads and the writer fills on its own flush interval.
_EVENT_STORED_TIMEOUT_SECONDS = 60.0
_EVENT_STORED_POLL_SECONDS = 1.0


def create_batch_datapoints(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """Batch-create from an event logged on the project key, and read the datapoint back.

    The batch route reads the checked events from object storage, which fills
    after the event is accepted. A call made before then finds no event and
    creates nothing, so the entry repeats the call until it creates one.
    """
    value = f"data-plane-key-{uuid.uuid4().hex[:8]}"
    event = project_client.events.create(
        PostEventRequest(
            event={
                "source": "data-plane-key",
                "event_name": value,
                "event_type": "tool",
                "inputs": {"value": value},
                "outputs": {"value": value},
                "session_id": str(uuid.uuid4()),
                "duration": 1.0,
            }
        )
    )
    request = BatchCreateDatapointsRequest(checkState={event.event_id: True})

    created = BatchCreateDatapointsResponse(inserted=False, insertedIds=[])
    deadline = time.monotonic() + _EVENT_STORED_TIMEOUT_SECONDS
    while not created.inserted and time.monotonic() < deadline:
        created = data_plane.datapoints.create_batch(request, project_id=project_id)
        if not created.inserted:
            time.sleep(_EVENT_STORED_POLL_SECONDS)

    try:
        assert created.inserted, f"event {event.event_id} never reached storage"
        [datapoint_id] = created.insertedIds
        fetched = project_client.datapoints.get(datapoint_id)
        assert [
            (datapoint.id, datapoint.inputs, datapoint.linked_event)
            for datapoint in fetched.datapoint
        ] == [(datapoint_id, {"value": value}, event.event_id)]
    finally:
        for datapoint_id in created.insertedIds:
            _delete_datapoint_quietly(project_client, datapoint_id)


def update_datapoint(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datapoints.update``: the data plane key's update reads back on the project key."""
    datapoint_id = _create_datapoint_on_the_project_key(project_client)
    marker = {"updated_by": f"data-plane-key-{uuid.uuid4().hex[:8]}"}
    try:
        updated = data_plane.datapoints.update(
            datapoint_id, UpdateDatapointRequest(metadata=marker), project_id=project_id
        )

        assert updated.updated
        fetched = project_client.datapoints.get(datapoint_id)
        assert [
            (datapoint.id, datapoint.metadata) for datapoint in fetched.datapoint
        ] == [(datapoint_id, marker)]
    finally:
        _delete_datapoint_quietly(project_client, datapoint_id)


def delete_datapoint(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datapoints.delete``: the datapoint is gone on the project key afterwards."""
    datapoint_id = _create_datapoint_on_the_project_key(project_client)
    deleted = False
    try:
        response = data_plane.datapoints.delete(datapoint_id, project_id=project_id)
        deleted = True

        assert response.deleted
        assert project_client.datapoints.get(datapoint_id).datapoint == []
    finally:
        if not deleted:
            _delete_datapoint_quietly(project_client, datapoint_id)


def _dataset_name() -> str:
    """A name the dataset validator accepts, unique per call because a
    project refuses a second dataset with the same name."""
    return f"data-plane-key-{uuid.uuid4().hex[:8]}"


def _create_dataset_on_the_project_key(project_client: HoneyHive, name: str) -> str:
    """Create a dataset through the unscoped route, for an entry to act on."""
    created = project_client.datasets.create(CreateDatasetRequest(name=name))
    return created.result.insertedId


def _delete_dataset_quietly(project_client: HoneyHive, dataset_id: str) -> None:
    """Remove an entry's dataset, as ``_delete_quietly`` does for a chart."""
    try:
        project_client.datasets.delete(dataset_id)
    except Exception as exc:  # noqa: BLE001 - cleanup must not raise
        print(f"Dataset cleanup failed for {dataset_id}: {exc}")


def get_datasets(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datasets.list``: a dataset made on the project key is listed by its id."""
    name = _dataset_name()
    dataset_id = _create_dataset_on_the_project_key(project_client, name)
    try:
        listed = data_plane.datasets.list(dataset_id, project_id=project_id)

        assert [(dataset.id, dataset.name) for dataset in listed.datasets] == [
            (dataset_id, name)
        ]
    finally:
        _delete_dataset_quietly(project_client, dataset_id)


def create_dataset(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """Create with the data plane key and verify the dataset with the project key."""
    name = _dataset_name()
    created = data_plane.datasets.create(
        CreateDatasetRequest(name=name), project_id=project_id
    )
    dataset_id = created.result.insertedId
    try:
        assert created.inserted
        listed = project_client.datasets.list(dataset_id=dataset_id)
        assert [(dataset.id, dataset.name) for dataset in listed.datasets] == [
            (dataset_id, name)
        ]
    finally:
        _delete_dataset_quietly(project_client, dataset_id)


def add_datapoints(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datasets.add_datapoints``: the returned ids are in the dataset on the project key."""
    dataset_id = _create_dataset_on_the_project_key(project_client, _dataset_name())
    try:
        added = data_plane.datasets.add_datapoints(
            dataset_id,
            AddDatapointsToDatasetRequest(
                data=[
                    {"query": f"data-plane-key-{uuid.uuid4().hex[:8]}", "answer": "a"}
                ],
                mapping=DatapointMapping(inputs=["query"], ground_truth=["answer"]),
            ),
            project_id=project_id,
        )

        assert added.datapoint_ids
        [dataset] = project_client.datasets.list(dataset_id=dataset_id).datasets
        assert set(added.datapoint_ids) <= set(dataset.datapoints)
    finally:
        _delete_dataset_quietly(project_client, dataset_id)


def update_dataset(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datasets.update``: the new name is read back on the project key."""
    dataset_id = _create_dataset_on_the_project_key(project_client, _dataset_name())
    try:
        renamed = _dataset_name()
        data_plane.datasets.update(
            UpdateDatasetRequest(dataset_id=dataset_id, name=renamed),
            project_id=project_id,
        )

        listed = project_client.datasets.list(dataset_id=dataset_id)
        assert [(dataset.id, dataset.name) for dataset in listed.datasets] == [
            (dataset_id, renamed)
        ]
    finally:
        _delete_dataset_quietly(project_client, dataset_id)


def delete_dataset(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datasets.delete``: the dataset is no longer listed on the project key afterwards."""
    dataset_id = _create_dataset_on_the_project_key(project_client, _dataset_name())
    deleted = False
    try:
        data_plane.datasets.delete(dataset_id, project_id=project_id)
        deleted = True

        # The list answers an empty list, not a 404, for an id it does not hold.
        assert project_client.datasets.list(dataset_id=dataset_id).datasets == []
    finally:
        if not deleted:
            _delete_dataset_quietly(project_client, dataset_id)


def remove_datapoint(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``datasets.remove_datapoint``: the dataset no longer lists the datapoint on the project key."""
    dataset_id = _create_dataset_on_the_project_key(project_client, _dataset_name())
    datapoint_ids: list[str] = []
    try:
        added = project_client.datasets.add_datapoints(
            dataset_id,
            AddDatapointsToDatasetRequest(
                data=[
                    {"query": f"data-plane-key-{uuid.uuid4().hex[:8]}", "answer": "a"}
                ],
                mapping=DatapointMapping(inputs=["query"], ground_truth=["answer"]),
            ),
        )
        datapoint_ids = added.datapoint_ids
        [datapoint_id] = datapoint_ids

        data_plane.datasets.remove_datapoint(
            dataset_id, datapoint_id, project_id=project_id
        )

        [dataset] = project_client.datasets.list(dataset_id=dataset_id).datasets
        assert datapoint_id not in dataset.datapoints
    finally:
        _delete_dataset_quietly(project_client, dataset_id)
        # A removed datapoint is unlinked, not deleted, so the dataset delete
        # leaves it behind.
        for datapoint_id in datapoint_ids:
            _delete_datapoint_quietly(project_client, datapoint_id)


def _run_name() -> str:
    return f"data-plane-key-{uuid.uuid4().hex[:8]}"


def _create_run_on_the_project_key(project_client: HoneyHive, name: str) -> str:
    """Create a run through the unscoped route, for an entry to act on."""
    return project_client.experiments.create_run(
        PostExperimentRunRequest(name=name)
    ).run_id


def _delete_run_quietly(project_client: HoneyHive, run_id: str) -> None:
    """Remove an entry's run through the project key.

    A failure is printed rather than raised, so it cannot mask the entry's own
    result.
    """
    try:
        project_client.experiments.delete_run(run_id)
    except Exception as exc:  # noqa: BLE001 - cleanup must not raise
        print(f"Run cleanup failed for {run_id}: {exc}")


def get_run(data_plane: HoneyHive, project_client: HoneyHive, project_id: str) -> None:
    """``experiments.get_run``: a run made on the project key is read back."""
    name = _run_name()
    run_id = _create_run_on_the_project_key(project_client, name)
    try:
        run = data_plane.experiments.get_run(run_id, project_id=project_id).evaluation

        assert (run.run_id, run.name, run.scope_id) == (run_id, name, project_id)
    finally:
        _delete_run_quietly(project_client, run_id)


def create_run(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.create_run``: the run is found on the project key afterwards."""
    name = _run_name()

    created = data_plane.experiments.create_run(
        PostExperimentRunRequest(name=name), project_id=project_id
    )
    try:
        run = project_client.experiments.get_run(created.run_id).evaluation
        assert (run.run_id, run.name, run.scope_id) == (
            created.run_id,
            name,
            project_id,
        )
    finally:
        _delete_run_quietly(project_client, created.run_id)


def get_runs(data_plane: HoneyHive, project_client: HoneyHive, project_id: str) -> None:
    """``experiments.list_runs``: the run created on the project key is listed."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        listed = data_plane.experiments.list_runs(
            run_ids=[run_id], project_id=project_id
        )
        assert [(run.run_id, run.scope_id) for run in listed.evaluations] == [
            (run_id, project_id)
        ]
    finally:
        _delete_run_quietly(project_client, run_id)


def update_run(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.update_run``: the new name is read back on the project key."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        renamed = _run_name()
        data_plane.experiments.update_run(
            run_id, PutExperimentRunRequest(name=renamed), project_id=project_id
        )

        assert project_client.experiments.get_run(run_id).evaluation.name == renamed
    finally:
        _delete_run_quietly(project_client, run_id)


def delete_run(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.delete_run``: the run is gone on the project key afterwards."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    deleted = False
    try:
        data_plane.experiments.delete_run(run_id, project_id=project_id)
        deleted = True

        with pytest.raises(HTTPException) as exc_info:
            project_client.experiments.get_run(run_id)
        assert exc_info.value.status_code == 404
    finally:
        if not deleted:
            _delete_run_quietly(project_client, run_id)


def get_runs_schema(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.get_schema``: the project's runs schema carries every part."""
    schema = data_plane.experiments.get_schema(project_id=project_id)
    assert isinstance(schema.fields, list)
    assert isinstance(schema.datasets, list)
    assert isinstance(schema.mappings, dict)


def get_run_schema(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.get_schema`` with ``evaluation_id``: the run's schema carries every part."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        schema = data_plane.experiments.get_schema(
            evaluation_id=run_id, project_id=project_id
        )
        assert isinstance(schema.fields, list)
        assert isinstance(schema.datasets, list)
        assert isinstance(schema.mappings, dict)
    finally:
        _delete_run_quietly(project_client, run_id)


def get_experiment_summary(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.get_result``: the summary of a run made on the project key."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        summary = data_plane.experiments.get_result(run_id, project_id=project_id)

        assert summary["run_object"]["run_id"] == run_id
    finally:
        _delete_run_quietly(project_client, run_id)


def get_run_metrics(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.get_run_metrics``: a new run's metrics hold no events."""
    run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        metrics = data_plane.experiments.get_run_metrics(run_id, project_id=project_id)

        assert (metrics.events, metrics.totalEvents) == ([], 0)
    finally:
        _delete_run_quietly(project_client, run_id)


def compare_runs(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.compare_runs``: two runs made on the project key are compared."""
    old_name = _run_name()
    old_run_id = _create_run_on_the_project_key(project_client, old_name)
    try:
        new_name = _run_name()
        new_run_id = _create_run_on_the_project_key(project_client, new_name)
        try:
            comparison = data_plane.experiments.compare_runs(
                new_run_id, old_run_id, project_id=project_id
            )

            assert [
                (run["run_id"], run["name"], run["scope_id"])
                for run in (comparison["old_run"], comparison["new_run"])
            ] == [
                (old_run_id, old_name, project_id),
                (new_run_id, new_name, project_id),
            ]
        finally:
            _delete_run_quietly(project_client, new_run_id)
    finally:
        _delete_run_quietly(project_client, old_run_id)


def compare_run_events(
    data_plane: HoneyHive, project_client: HoneyHive, project_id: str
) -> None:
    """``experiments.compare_run_events``: two runs with no events share no pairs."""
    new_run_id = _create_run_on_the_project_key(project_client, _run_name())
    try:
        old_run_id = _create_run_on_the_project_key(project_client, _run_name())
        try:
            comparison = data_plane.experiments.compare_run_events(
                new_run_id, old_run_id, limit=1, project_id=project_id
            )

            assert (comparison.events, comparison.totalEvents) == ([], 0)
        finally:
            _delete_run_quietly(project_client, old_run_id)
    finally:
        _delete_run_quietly(project_client, new_run_id)


# Keyed by operationId. A wrapped data plane operation missing here fails the
# unit guard; an entry for an operation the shim does not wrap fails it too.
OPERATIONS: Dict[str, Entry] = {
    "getCharts": get_charts,
    "getChart": get_chart,
    "createChart": create_chart,
    "updateChart": update_chart,
    "deleteChart": delete_chart,
    "getDatapoints": get_datapoints,
    "queryChart": query_chart,
    "getDatapoint": get_datapoint,
    "createDatapoint": create_datapoint,
    "updateDatapoint": update_datapoint,
    "deleteDatapoint": delete_datapoint,
    "batchCreateDatapoints": create_batch_datapoints,
    "getDatasets": get_datasets,
    "createDataset": create_dataset,
    "addDatapoints": add_datapoints,
    "updateDataset": update_dataset,
    "deleteDataset": delete_dataset,
    "removeDatapoint": remove_datapoint,
    "getRuns": get_runs,
    "getRun": get_run,
    "getRunsSchema": get_runs_schema,
    "getRunSchema": get_run_schema,
    "getExperimentRunMetrics": get_run_metrics,
    "createRun": create_run,
    "updateRun": update_run,
    "deleteRun": delete_run,
    "getExperimentSummary": get_experiment_summary,
    "getExperimentComparison": compare_runs,
    "getExperimentCompareEvents": compare_run_events,
}
