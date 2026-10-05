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

import uuid
from typing import Callable, Dict

import pytest

from honeyhive._generated.api_config import HTTPException
from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateChartRequest, UpdateChartRequest

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


# Keyed by operationId. A wrapped data plane operation missing here fails the
# unit guard; an entry for an operation the shim does not wrap fails it too.
OPERATIONS: Dict[str, Entry] = {
    "getCharts": get_charts,
    "getChart": get_chart,
    "createChart": create_chart,
    "updateChart": update_chart,
    "deleteChart": delete_chart,
}
