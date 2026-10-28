"""Unit tests for each twin wrapper's choice of operation and key.

A twin wrapper is a public method that takes an optional ``project_id``. It
sends the project-scoped operation with the data plane key when it is given
``project_id``, and the unscoped operation with the project key, plus a
``DeprecationWarning``, when it is not. Its private core sends the same
operations without ever warning, because SDK code that cannot pass
``project_id`` calls the core. Each branch is refused before sending,
naming its key, when that key is not configured: the project key never stands
in for the data plane key, nor the data plane key for the project key. The
generated service functions are
patched, so these tests see which function each call reaches and the
configuration it carries without sending anything.

A wrapper is covered by adding its ``Case`` to ``CASES``, and nothing checks
that it was added: a wrapper without one still passes the spec guards and the
live suite, which test only that it exists and that its scoped branch sends the
data plane key. A missing case leaves the unscoped branch untested, which is
the call the wrapper made before it took ``project_id``, so code review holds
each new wrapper to its case rather than a guard. A wrapper whose unscoped
branch is new code, such as one that maps its arguments onto an older
operation, warrants that guard.
"""

import os
import warnings
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Dict, Optional, Tuple, Union
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from honeyhive import MissingApiKeyError
from honeyhive._generated.models import GetExperimentRunCompareResponse
from honeyhive._generated.models import UpdateDatasetRequest as UpdateDatasetBody
from honeyhive.api import client as client_module
from honeyhive.api.client import HoneyHive
from honeyhive.models import (
    AddDatapointsToDatasetRequest,
    BatchCreateDatapointsRequest,
    CreateChartRequest,
    CreateDatapointRequest,
    CreateDatasetRequest,
    DatapointMapping,
    PostExperimentRunRequest,
    PutExperimentRunRequest,
    UpdateChartRequest,
    UpdateDatapointRequest,
    UpdateDatasetRequest,
)

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32

BATCH_CREATE_DATAPOINTS_REQUEST = BatchCreateDatapointsRequest(checkState={"e1": True})
CREATE_CHART_REQUEST = CreateChartRequest(name="n", metric="event_count")
CREATE_DATAPOINT_REQUEST = CreateDatapointRequest(inputs={"q": "x"})
CREATE_DATASET_REQUEST = CreateDatasetRequest(name="n")
UPDATE_DATAPOINT_REQUEST = UpdateDatapointRequest(metadata={"k": "v"})
UPDATE_CHART_REQUEST = UpdateChartRequest(name="n")
UPDATE_DATASET_REQUEST = UpdateDatasetRequest(dataset_id="ds1", name="n")
UPDATE_DATASET_BODY = UpdateDatasetBody(name="n")
UNNAMED_DATASET_UPDATE = UpdateDatasetRequest(dataset_id="", name="n")
CREATE_RUN_REQUEST = PostExperimentRunRequest(name="n")
LIST_RUNS_KWARGS: Dict[str, Any] = {
    "dataset_id": "ds1",
    "page": 2,
    "limit": 10,
    "run_ids": ["r1"],
    "name": "n",
    "status": "completed",
    "dateRange": {"$gte": 1},
    "sort_by": "created_at",
    "sort_order": "asc",
}
LIST_RUNS_ARGS = tuple(LIST_RUNS_KWARGS.values())
UPDATE_RUN_REQUEST = PutExperimentRunRequest(name="n")
RUNS_SCHEMA_DATE_RANGE: Dict[str, Any] = {"$gte": 1}
RUN_SUMMARY_FILTERS = [{"field": "event_name", "operator": "is", "value": "x"}]
ADD_DATAPOINTS_REQUEST = AddDatapointsToDatasetRequest(
    data=[{"q": "x"}], mapping=DatapointMapping(inputs=["q"])
)

RUN_METRICS_DATE_RANGE = '{"$gte": 1}'
RUN_METRICS_FILTERS = '[{"field": "metrics.accuracy"}]'


COMPARED_RUN = {
    "id": "row-1",
    "run_id": "r1",
    "metadata": {},
    "results": {},
    "event_ids": [],
    "configuration": {},
    "is_active": True,
    "created_at": "2026-01-01T00:00:00.000Z",
    "scope_type": "project",
    "scope_id": "p1",
}
COMPARISON = GetExperimentRunCompareResponse.model_validate(
    {
        "metrics": [],
        "commonDatapoints": ["d1"],
        "event_details": [],
        "old_run": COMPARED_RUN,
        "new_run": COMPARED_RUN,
    }
)
COMPARE_RUNS_FILTERS = [{"field": "metadata.cost", "operator": "exists"}]
COMPARE_RUNS_KWARGS = {
    "new_run_id": "r-new",
    "old_run_id": "r-old",
    "aggregate_function": "median",
    "filters": COMPARE_RUNS_FILTERS,
}


@dataclass(frozen=True)
class Case:
    """One twin wrapper: its method and the two functions it dispatches to.

    ``namespace`` is both the ``HoneyHive`` attribute that holds the method and
    the stem of the service modules it calls, ``<namespace>_svc`` and
    ``<namespace>_svc_async`` in ``honeyhive.api.client``. ``legacy_namespace``
    names the legacy function's module stem when it differs. ``response`` is
    what the patched functions return, for a method that copies the response
    rather than returning it as is.
    """

    namespace: str
    method: str
    args: Tuple[Any, ...]
    scoped: str
    scoped_kwargs: Dict[str, Any]
    legacy: str
    legacy_kwargs: Dict[str, Any]
    legacy_namespace: Optional[str] = None
    # What the patched functions return: a dict a wrapper copies through, or
    # the model a wrapper answers as ``response.model_dump()``.
    response: Optional[Union[BaseModel, Dict[str, Any]]] = None


CASES = [
    Case(
        "charts", "list", (), "getCharts", {"project_id": "p1"}, "getChartsLegacy", {}
    ),
    Case(
        "charts",
        "get",
        ("c1",),
        "getChart",
        {"project_id": "p1", "chart_id": "c1"},
        "getChartLegacy",
        {"chart_id": "c1"},
    ),
    Case(
        "charts",
        "create",
        (CREATE_CHART_REQUEST,),
        "createChart",
        {"project_id": "p1", "data": CREATE_CHART_REQUEST},
        "createChartLegacy",
        {"data": CREATE_CHART_REQUEST},
    ),
    Case(
        "charts",
        "update",
        ("c1", UPDATE_CHART_REQUEST),
        "updateChart",
        {"project_id": "p1", "chart_id": "c1", "data": UPDATE_CHART_REQUEST},
        "updateChartLegacy",
        {"chart_id": "c1", "data": UPDATE_CHART_REQUEST},
    ),
    Case(
        "charts",
        "delete",
        ("c1",),
        "deleteChart",
        {"project_id": "p1", "chart_id": "c1"},
        "deleteChartLegacy",
        {"chart_id": "c1"},
    ),
    # Both positional filters are passed, so the keyword-only check's extra
    # positional cannot bind to `dataset_name`.
    Case(
        "datapoints",
        "list",
        (["d1"], "n1"),
        "getDatapoints",
        {"project_id": "p1", "datapoint_ids": ["d1"], "dataset_name": "n1"},
        "getDatapointsLegacy",
        {"datapoint_ids": ["d1"], "dataset_name": "n1"},
    ),
    Case(
        "datapoints",
        "get",
        ("d1",),
        "getDatapoint",
        {"project_id": "p1", "datapoint_id": "d1"},
        "getDatapointLegacy",
        {"datapoint_id": "d1"},
    ),
    Case(
        "datapoints",
        "create",
        (CREATE_DATAPOINT_REQUEST,),
        "createDatapoint",
        {"project_id": "p1", "data": CREATE_DATAPOINT_REQUEST},
        "createDatapointLegacy",
        {"data": CREATE_DATAPOINT_REQUEST},
    ),
    Case(
        "datapoints",
        "update",
        ("d1", UPDATE_DATAPOINT_REQUEST),
        "updateDatapoint",
        {"project_id": "p1", "datapoint_id": "d1", "data": UPDATE_DATAPOINT_REQUEST},
        "updateDatapointLegacy",
        {"datapoint_id": "d1", "data": UPDATE_DATAPOINT_REQUEST},
    ),
    Case(
        "datapoints",
        "delete",
        ("d1",),
        "deleteDatapoint",
        {"project_id": "p1", "datapoint_id": "d1"},
        "deleteDatapointLegacy",
        {"datapoint_id": "d1"},
    ),
    Case(
        "datapoints",
        "create_batch",
        (BATCH_CREATE_DATAPOINTS_REQUEST,),
        "batchCreateDatapoints",
        {"project_id": "p1", "data": BATCH_CREATE_DATAPOINTS_REQUEST},
        "batchCreateDatapointsLegacy",
        {"data": BATCH_CREATE_DATAPOINTS_REQUEST},
    ),
    # Both positional filters are passed, so the keyword-only check's extra
    # positional cannot bind to `name`.
    Case(
        "datasets",
        "list",
        ("ds1", "n1"),
        "getDatasets",
        {"project_id": "p1", "dataset_id": "ds1", "name": "n1"},
        "getDatasetsLegacy",
        {"dataset_id": "ds1", "name": "n1"},
    ),
    Case(
        "datasets",
        "create",
        (CREATE_DATASET_REQUEST,),
        "createDataset",
        {"project_id": "p1", "data": CREATE_DATASET_REQUEST},
        "createDatasetLegacy",
        {"data": CREATE_DATASET_REQUEST},
    ),
    Case(
        "datasets",
        "add_datapoints",
        ("ds1", ADD_DATAPOINTS_REQUEST),
        "addDatapoints",
        {"project_id": "p1", "dataset_id": "ds1", "data": ADD_DATAPOINTS_REQUEST},
        "addDatapointsLegacy",
        {"dataset_id": "ds1", "data": ADD_DATAPOINTS_REQUEST},
    ),
    # The unscoped branch sends the query-id operation, whose generated
    # signature matches the twin's flat arm, so a type check cannot tell the
    # two apart. This row is what catches a call moved onto the flat arm.
    Case(
        "datasets",
        "delete",
        ("ds1",),
        "deleteDataset",
        {"project_id": "p1", "dataset_id": "ds1"},
        "deleteDatasetQueryIdLegacy",
        {"dataset_id": "ds1"},
    ),
    # The scoped branch moves `dataset_id` from the request into the path; the
    # unscoped branch sends the body-id operation with the request whole.
    Case(
        "datasets",
        "update",
        (UPDATE_DATASET_REQUEST,),
        "updateDataset",
        {"project_id": "p1", "dataset_id": "ds1", "data": UPDATE_DATASET_BODY},
        "updateDatasetBodyIdLegacy",
        {"data": UPDATE_DATASET_REQUEST},
    ),
    # The unscoped branch sends the short-path operation, whose generated
    # signature matches the twin's flat arm, so a type check cannot tell the
    # two apart. This row is what catches a call moved onto the flat arm.
    Case(
        "datasets",
        "remove_datapoint",
        ("ds1", "dp1"),
        "removeDatapoint",
        {"project_id": "p1", "dataset_id": "ds1", "datapoint_id": "dp1"},
        "removeDatapointShortPathLegacy",
        {"dataset_id": "ds1", "datapoint_id": "dp1"},
    ),
    Case(
        "experiments",
        "create_run",
        (CREATE_RUN_REQUEST,),
        "createRun",
        {"project_id": "p1", "data": CREATE_RUN_REQUEST},
        "createRunLegacy",
        {"data": CREATE_RUN_REQUEST},
    ),
    Case(
        "experiments",
        "list_runs",
        LIST_RUNS_ARGS,
        "getRuns",
        {"project_id": "p1", **LIST_RUNS_KWARGS},
        "getRunsLegacy",
        LIST_RUNS_KWARGS,
    ),
    Case(
        "experiments",
        "get_run",
        ("r1",),
        "getRun",
        {"project_id": "p1", "run_id": "r1"},
        "getRunLegacy",
        {"run_id": "r1"},
    ),
    Case(
        "experiments",
        "update_run",
        ("r1", UPDATE_RUN_REQUEST),
        "updateRun",
        {"project_id": "p1", "run_id": "r1", "data": UPDATE_RUN_REQUEST},
        "updateRunLegacy",
        {"run_id": "r1", "data": UPDATE_RUN_REQUEST},
    ),
    Case(
        "experiments",
        "delete_run",
        ("r1",),
        "deleteRun",
        {"project_id": "p1", "run_id": "r1"},
        "deleteRunLegacy",
        {"run_id": "r1"},
    ),
    Case(
        "experiments",
        "get_run_metrics",
        ("r1", RUN_METRICS_DATE_RANGE, RUN_METRICS_FILTERS),
        "getExperimentRunMetrics",
        {
            "project_id": "p1",
            "run_id": "r1",
            "dateRange": RUN_METRICS_DATE_RANGE,
            "filters": RUN_METRICS_FILTERS,
        },
        "getExperimentRunMetricsLegacy",
        {
            "run_id": "r1",
            "dateRange": RUN_METRICS_DATE_RANGE,
            "filters": RUN_METRICS_FILTERS,
        },
    ),
    Case(
        "experiments",
        "get_schema",
        (RUNS_SCHEMA_DATE_RANGE, None),
        "getRunsSchema",
        {"project_id": "p1", "dateRange": RUNS_SCHEMA_DATE_RANGE},
        "getEventsSchemaLegacy",
        {"dateRange": RUNS_SCHEMA_DATE_RANGE, "evaluation_id": None},
        legacy_namespace="events",
    ),
    Case(
        "experiments",
        "get_schema",
        (RUNS_SCHEMA_DATE_RANGE, "r1"),
        "getRunSchema",
        {"project_id": "p1", "run_id": "r1", "dateRange": RUNS_SCHEMA_DATE_RANGE},
        "getEventsSchemaLegacy",
        {"dateRange": RUNS_SCHEMA_DATE_RANGE, "evaluation_id": "r1"},
        legacy_namespace="events",
    ),
    Case(
        "experiments",
        "get_result",
        ("r1", "max", RUN_SUMMARY_FILTERS),
        "getExperimentSummary",
        {
            "project_id": "p1",
            "run_id": "r1",
            "aggregate_function": "max",
            "filters": RUN_SUMMARY_FILTERS,
        },
        "getExperimentResultLegacy",
        {"run_id": "r1", "aggregate_function": "max", "filters": RUN_SUMMARY_FILTERS},
        response={"status": "completed"},
    ),
    Case(
        "experiments",
        "compare_runs",
        ("r-new", "r-old", "median", COMPARE_RUNS_FILTERS),
        "getExperimentComparison",
        {"project_id": "p1", **COMPARE_RUNS_KWARGS},
        "getExperimentComparisonCompareWithLegacy",
        COMPARE_RUNS_KWARGS,
        response=COMPARISON,
    ),
    Case(
        "experiments",
        "compare_run_events",
        ("r1", "r2", "llm", "model", {"k": "v"}, 10, 2),
        "getExperimentCompareEvents",
        {
            "project_id": "p1",
            "new_run_id": "r1",
            "old_run_id": "r2",
            "event_name": "llm",
            "event_type": "model",
            "filter": {"k": "v"},
            "limit": 10,
            "page": 2,
        },
        "getExperimentCompareEventsQueryIdLegacy",
        {
            "run_id_1": "r1",
            "run_id_2": "r2",
            "event_name": "llm",
            "event_type": "model",
            "filter": {"k": "v"},
            "limit": 10,
            "page": 2,
        },
    ),
]


def _case_id(case: Case) -> str:
    return f"{case.namespace}.{case.method}"


def _client(**keys: str) -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(**keys)


def _method(client: HoneyHive, case: Case, suffix: str = "") -> Callable[..., Any]:
    return getattr(getattr(client, case.namespace), f"{case.method}{suffix}")


def _core(client: HoneyHive, case: Case, suffix: str = "") -> Callable[..., Any]:
    """The private core behind a public method, which SDK code calls directly."""
    return getattr(getattr(client, case.namespace), f"_{case.method}{suffix}")


def _service(case: Case, suffix: str = "") -> ModuleType:
    service: ModuleType = getattr(client_module, f"{case.namespace}_svc{suffix}")
    return service


def _legacy_service(case: Case, suffix: str = "") -> ModuleType:
    namespace = case.legacy_namespace or case.namespace
    service: ModuleType = getattr(client_module, f"{namespace}_svc{suffix}")
    return service


def _returns(case: Case) -> Dict[str, Any]:
    """What a patched generated function returns, when the case names it."""
    return {} if case.response is None else {"return_value": case.response}


def _assert_answers(result: Any, case: Case, sent: MagicMock) -> None:
    """The wrapper answered what the generated function returned."""
    if case.response is None:
        assert result is sent.return_value
    else:
        expected = (
            case.response.model_dump()
            if isinstance(case.response, BaseModel)
            else case.response
        )
        assert result == expected


def _assert_sent(mock: MagicMock, key: str, kwargs: Dict[str, Any]) -> None:
    """The mock was called once, with a configuration carrying ``key``."""
    mock.assert_called_once()
    (api_config,), sent_kwargs = mock.call_args
    assert api_config.access_token == key
    assert sent_kwargs == kwargs


@pytest.mark.parametrize("case", CASES, ids=_case_id)
class TestSync:
    """The sync methods."""

    def test_project_id_sends_the_scoped_operation_with_the_data_plane_key(
        self, case: Case
    ) -> None:
        """With project_id the scoped function is called, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(_service(case), case.scoped, **_returns(case)) as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = _method(client, case)(*case.args, project_id="p1")

        _assert_answers(result, case, scoped)
        _assert_sent(scoped, DATA_PLANE_KEY, case.scoped_kwargs)

    def test_no_project_id_sends_the_legacy_operation_with_the_project_key(
        self, case: Case
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case), case.legacy, **_returns(case)
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = _method(client, case)(*case.args)

        _assert_answers(result, case, legacy)
        _assert_sent(legacy, PROJECT_KEY, case.legacy_kwargs)
        [warning] = caught
        assert str(warning.message) == (
            f"Calling {case.namespace}.{case.method}() without project_id is "
            "deprecated and will stop working in v2.0. Pass project_id, and "
            "configure a data plane API key with data_plane_api_key or the "
            "HH_DATA_PLANE_API_KEY environment variable."
        )
        # Attributed to the caller, so Python's default filters show it in a
        # script and hide it in a library that calls the SDK.
        assert warning.filename == __file__

    def test_core_sends_the_legacy_operation_without_warning(self, case: Case) -> None:
        """The core takes the legacy branch silently, for SDK code that cannot pass project_id."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case), case.legacy, **_returns(case)
        ) as legacy:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = _core(client, case)(*case.args)

        _assert_answers(result, case, legacy)
        _assert_sent(legacy, PROJECT_KEY, case.legacy_kwargs)

    def test_project_id_without_a_data_plane_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the project key, the scoped call is refused, naming the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(_service(case), case.scoped, **_returns(case)) as scoped:
            with pytest.raises(MissingApiKeyError) as exc_info:
                _method(client, case)(*case.args, project_id="p1")

        assert exc_info.value.key_kind == "data_plane"
        scoped.assert_not_called()

    def test_no_project_id_without_a_project_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the data plane key, the unscoped call is refused, naming the project key."""
        client = _client(data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case), case.legacy, **_returns(case)
        ) as legacy:
            with pytest.raises(MissingApiKeyError) as exc_info:
                _method(client, case)(*case.args)

        assert exc_info.value.key_kind == "project"
        legacy.assert_not_called()

    def test_project_id_is_keyword_only(self, case: Case) -> None:
        """An extra positional argument cannot be read as project_id."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)

        with pytest.raises(TypeError):
            _method(client, case)(*case.args, "p1")


@pytest.mark.parametrize("case", CASES, ids=_case_id)
class TestAsync:
    """The async methods, which dispatch exactly as their sync counterparts do."""

    @pytest.mark.asyncio
    async def test_project_id_sends_the_scoped_operation_with_the_data_plane_key(
        self, case: Case
    ) -> None:
        """With project_id the scoped function is awaited, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _service(case, "_async"),
            case.scoped,
            new_callable=AsyncMock,
            **_returns(case),
        ) as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await _method(client, case, "_async")(
                    *case.args, project_id="p1"
                )

        _assert_answers(result, case, scoped)
        _assert_sent(scoped, DATA_PLANE_KEY, case.scoped_kwargs)

    @pytest.mark.asyncio
    async def test_no_project_id_sends_the_legacy_operation_with_the_project_key(
        self, case: Case
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case, "_async"),
            case.legacy,
            new_callable=AsyncMock,
            **_returns(case),
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = await _method(client, case, "_async")(*case.args)

        _assert_answers(result, case, legacy)
        _assert_sent(legacy, PROJECT_KEY, case.legacy_kwargs)
        [warning] = caught
        assert f"{case.namespace}.{case.method}_async() without project_id" in str(
            warning.message
        )
        assert warning.filename == __file__

    @pytest.mark.asyncio
    async def test_core_sends_the_legacy_operation_without_warning(
        self, case: Case
    ) -> None:
        """The core takes the legacy branch silently, for SDK code that cannot pass project_id."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case, "_async"),
            case.legacy,
            new_callable=AsyncMock,
            **_returns(case),
        ) as legacy:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await _core(client, case, "_async")(*case.args)

        _assert_answers(result, case, legacy)
        _assert_sent(legacy, PROJECT_KEY, case.legacy_kwargs)

    @pytest.mark.asyncio
    async def test_project_id_without_a_data_plane_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the project key, the scoped call is refused, naming the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(
            _service(case, "_async"),
            case.scoped,
            new_callable=AsyncMock,
            **_returns(case),
        ) as scoped:
            with pytest.raises(MissingApiKeyError) as exc_info:
                await _method(client, case, "_async")(*case.args, project_id="p1")

        assert exc_info.value.key_kind == "data_plane"
        scoped.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_project_id_without_a_project_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the data plane key, the unscoped call is refused, naming the project key."""
        client = _client(data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _legacy_service(case, "_async"),
            case.legacy,
            new_callable=AsyncMock,
            **_returns(case),
        ) as legacy:
            with pytest.raises(MissingApiKeyError) as exc_info:
                await _method(client, case, "_async")(*case.args)

        assert exc_info.value.key_kind == "project"
        legacy.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_id_is_keyword_only(self, case: Case) -> None:
        """An extra positional argument cannot be read as project_id."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)

        with pytest.raises(TypeError):
            await _method(client, case, "_async")(*case.args, "p1")


class TestAliases:
    """Backwards compatible aliases, which dispatch as their method does and
    warn in their own name. They are sync only, so they have no ``CASES`` row."""

    def test_list_datapoints_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias lists the project's datapoints, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "getDatapoints") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datapoints.list_datapoints(["d1"], project_id="p1")

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {"project_id": "p1", "datapoint_ids": ["d1"], "dataset_name": None},
        )

    def test_list_datapoints_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datapoints_svc, "getDatapointsLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datapoints.list_datapoints(["d1"])

        assert result is legacy.return_value
        _assert_sent(
            legacy, PROJECT_KEY, {"datapoint_ids": ["d1"], "dataset_name": None}
        )
        [warning] = caught
        assert "datapoints.list_datapoints() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_get_datapoint_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "getDatapoint") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datapoints.get_datapoint("d1", project_id="p1")

        assert result is scoped.return_value
        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1", "datapoint_id": "d1"})

    def test_get_datapoint_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "getDatapointLegacy") as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datapoints.get_datapoint("d1")

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"datapoint_id": "d1"})
        [warning] = caught
        assert "datapoints.get_datapoint() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_create_datapoint_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "createDatapoint") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datapoints.create_datapoint(
                    CREATE_DATAPOINT_REQUEST, project_id="p1"
                )

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {"project_id": "p1", "data": CREATE_DATAPOINT_REQUEST},
        )

    def test_create_datapoint_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datapoints_svc, "createDatapointLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datapoints.create_datapoint(CREATE_DATAPOINT_REQUEST)

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"data": CREATE_DATAPOINT_REQUEST})
        [warning] = caught
        assert "datapoints.create_datapoint() without project_id" in str(
            warning.message
        )
        assert warning.filename == __file__

    def test_update_datapoint_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "updateDatapoint") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datapoints.update_datapoint(
                    "d1", UPDATE_DATAPOINT_REQUEST, project_id="p1"
                )

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {
                "project_id": "p1",
                "datapoint_id": "d1",
                "data": UPDATE_DATAPOINT_REQUEST,
            },
        )

    def test_update_datapoint_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datapoints_svc, "updateDatapointLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datapoints.update_datapoint(
                    "d1", UPDATE_DATAPOINT_REQUEST
                )

        assert result is legacy.return_value
        _assert_sent(
            legacy,
            PROJECT_KEY,
            {"datapoint_id": "d1", "data": UPDATE_DATAPOINT_REQUEST},
        )
        [warning] = caught
        assert "datapoints.update_datapoint() without project_id" in str(
            warning.message
        )
        assert warning.filename == __file__

    def test_delete_datapoint_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datapoints_svc, "deleteDatapoint") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datapoints.delete_datapoint("d1", project_id="p1")

        assert result is scoped.return_value
        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1", "datapoint_id": "d1"})

    def test_delete_datapoint_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datapoints_svc, "deleteDatapointLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datapoints.delete_datapoint("d1")

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"datapoint_id": "d1"})
        [warning] = caught
        assert "datapoints.delete_datapoint() without project_id" in str(
            warning.message
        )
        assert warning.filename == __file__

    def test_get_dataset_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias lists the one dataset in that project."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "getDatasets") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datasets.get_dataset("ds1", project_id="p1")

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {"project_id": "p1", "dataset_id": "ds1", "name": None},
        )

    def test_get_dataset_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "getDatasetsLegacy") as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datasets.get_dataset("ds1")

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"dataset_id": "ds1", "name": None})
        [warning] = caught
        assert "datasets.get_dataset() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_list_datasets_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "getDatasets") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datasets.list_datasets("ds1", "n1", project_id="p1")

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {"project_id": "p1", "dataset_id": "ds1", "name": "n1"},
        )

    def test_list_datasets_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "getDatasetsLegacy") as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datasets.list_datasets("ds1", "n1")

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"dataset_id": "ds1", "name": "n1"})
        [warning] = caught
        assert "datasets.list_datasets() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_create_dataset_with_project_id_sends_the_scoped_operation(self) -> None:
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "createDataset") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datasets.create_dataset(
                    CREATE_DATASET_REQUEST, project_id="p1"
                )

        assert result is scoped.return_value
        _assert_sent(
            scoped, DATA_PLANE_KEY, {"project_id": "p1", "data": CREATE_DATASET_REQUEST}
        )

    def test_create_dataset_without_project_id_warns_in_its_own_name(self) -> None:
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "createDatasetLegacy") as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datasets.create_dataset(CREATE_DATASET_REQUEST)

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"data": CREATE_DATASET_REQUEST})
        [warning] = caught
        assert "datasets.create_dataset() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_delete_dataset_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "deleteDataset") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datasets.delete_dataset("ds1", project_id="p1")

        assert result is scoped.return_value
        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1", "dataset_id": "ds1"})

    def test_delete_dataset_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datasets_svc, "deleteDatasetQueryIdLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datasets.delete_dataset("ds1")

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"dataset_id": "ds1"})
        [warning] = caught
        assert "datasets.delete_dataset() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_update_dataset_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias calls the scoped function, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "updateDataset") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.datasets.update_dataset(
                    UPDATE_DATASET_REQUEST, project_id="p1"
                )

        assert result is scoped.return_value
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {"project_id": "p1", "dataset_id": "ds1", "data": UPDATE_DATASET_BODY},
        )

    def test_update_dataset_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datasets_svc, "updateDatasetBodyIdLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = client.datasets.update_dataset(UPDATE_DATASET_REQUEST)

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, {"data": UPDATE_DATASET_REQUEST})
        [warning] = caught
        assert "datasets.update_dataset() without project_id" in str(warning.message)
        assert warning.filename == __file__

    def test_get_run_result_with_project_id_sends_the_scoped_operation(self) -> None:
        """With project_id the alias reads the project's run summary, and nothing warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.experiments_svc, "getExperimentSummary"
        ) as scoped:
            scoped.return_value = {"status": "completed"}
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.experiments.get_run_result("r1", project_id="p1")

        assert result == {"status": "completed"}
        _assert_sent(
            scoped,
            DATA_PLANE_KEY,
            {
                "project_id": "p1",
                "run_id": "r1",
                "aggregate_function": None,
                "filters": None,
            },
        )

    def test_get_run_result_without_project_id_warns_in_its_own_name(self) -> None:
        """Without project_id the alias calls the legacy function and names itself."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.experiments_svc, "getExperimentResultLegacy"
        ) as legacy:
            legacy.return_value = {"status": "completed"}
            with pytest.warns(DeprecationWarning) as caught:
                result = client.experiments.get_run_result("r1", "max")

        assert result == {"status": "completed"}
        _assert_sent(
            legacy,
            PROJECT_KEY,
            {"run_id": "r1", "aggregate_function": "max", "filters": None},
        )
        [warning] = caught
        assert "experiments.get_run_result() without project_id" in str(warning.message)
        assert warning.filename == __file__


class TestDatasetUpdateWithoutDatasetId:
    """The scoped update names the dataset in its path, so it refuses an empty
    ``dataset_id``."""

    def test_sync_update_refuses_before_sending(self) -> None:
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(client_module.datasets_svc, "updateDataset") as scoped:
            with pytest.raises(ValueError, match="dataset_id"):
                client.datasets.update(UNNAMED_DATASET_UPDATE, project_id="p1")

        scoped.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_update_refuses_before_sending(self) -> None:
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.datasets_svc_async, "updateDataset", new_callable=AsyncMock
        ) as scoped:
            with pytest.raises(ValueError, match="dataset_id"):
                await client.datasets.update_async(
                    UNNAMED_DATASET_UPDATE, project_id="p1"
                )

        scoped.assert_not_called()
