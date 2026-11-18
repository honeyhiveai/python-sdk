"""Unit tests for the experiment result functions.

``get_run_result``, ``get_run_metrics`` and ``compare_runs`` each choose
between two requests. With ``project_id`` and a client that holds a data plane
API key, they send the project-scoped request. Otherwise they send the request
the project API key takes, and warn. They accepted and ignored ``project_id``
before data plane keys existed, so ``project_id`` with only a project key must
keep working, which is the difference from the client's own methods. With
neither key there is nothing to keep working, so ``project_id`` is honored and
the request is refused for its missing data plane key.

The client is a mock, so these tests see which request each call asks the
client for without sending anything. Every warning test checks the file the
warning is attributed to, because pytest shows every warning whatever its
``stacklevel`` and Python shows a ``DeprecationWarning`` only when it lands on
the caller's code.
"""

# pylint: disable=protected-access,redefined-outer-name
# Justification: the result functions call the client's private cores, and
# pytest fixtures are passed by name.

import warnings
from typing import Any, Callable, Dict, List, Tuple
from unittest.mock import Mock

import pytest

from honeyhive.experiments import results as results_module
from honeyhive.experiments.models import (
    AggregatedMetrics,
    ExperimentResultSummary,
    RunComparisonResult,
)
from honeyhive.experiments.results import compare_runs, get_run_metrics, get_run_result
from tests.integration._spec_operations import require_spec, spec_parameter_enum

PROJECT_ID = "project-123"

RESULT_RESPONSE: Dict[str, Any] = {
    "status": "completed",
    "success": True,
    "passed": ["dp-1", "dp-2"],
    "failed": ["dp-3"],
    "metrics": {
        "aggregation_function": "average",
        "accuracy": {"aggregate": 0.85, "values": [0.8, 0.9]},
    },
    "datapoints": [
        {"datapoint_id": "dp-1", "session_id": "session-1", "passed": True},
        {"datapoint_id": "dp-3", "session_id": "session-3", "passed": False},
    ],
}

COMPARE_RESPONSE: Dict[str, Any] = {
    "commonDatapoints": ["dp-1", "dp-2", "dp-3"],
    "metrics": [
        {
            "metric_name": "accuracy",
            "old_aggregate": 0.80,
            "new_aggregate": 0.85,
            "found_count": 3,
            "improved_count": 2,
            "degraded_count": 0,
            "improved": ["dp-1", "dp-2"],
            "degraded": [],
        },
        {
            "metric_name": "latency",
            "old_aggregate": 1.5,
            "new_aggregate": 1.8,
            "found_count": 3,
            "improved_count": 0,
            "degraded_count": 1,
            "improved": [],
            "degraded": ["dp-3"],
        },
    ],
    "old_run": {"run_id": "run-old"},
    "new_run": {"run_id": "run-new"},
}


def make_client(*, data_plane_api_key: str, api_key: str) -> Mock:
    """A client whose cores answer with the canned responses.

    Both keys are set explicitly, because an attribute a ``Mock`` was never
    given is itself a truthy ``Mock``.
    """
    client = Mock()
    client.data_plane_api_key = data_plane_api_key
    client.api_key = api_key
    client.experiments._get_result.return_value = RESULT_RESPONSE
    client.experiments._compare_runs.return_value = COMPARE_RESPONSE
    return client


@pytest.fixture
def project_key_client() -> Mock:
    """A client that holds a project API key and no data plane API key."""
    return make_client(data_plane_api_key="", api_key="hh_test")


@pytest.fixture
def data_plane_client() -> Mock:
    """A client that holds a data plane API key and no project API key."""
    return make_client(data_plane_api_key="hh_fgdp_test", api_key="")


@pytest.fixture
def keyless_client() -> Mock:
    """A client that holds neither key."""
    return make_client(data_plane_api_key="", api_key="")


def _result_core(client: Mock) -> Mock:
    return client.experiments._get_result


def _compare_core(client: Mock) -> Mock:
    return client.experiments._compare_runs


# One row per result function: its name, a call with only the required
# arguments plus `project_id`, the core that call reaches, and the arguments
# the core receives beside `project_id`.
HELPERS: List[
    Tuple[str, Callable[..., Any], Callable[[Mock], Mock], Dict[str, Any]]
] = [
    (
        "get_run_result",
        lambda client, **kwargs: get_run_result(client, "run-123", **kwargs),
        _result_core,
        {"run_id": "run-123", "aggregate_function": "average"},
    ),
    (
        "get_run_metrics",
        lambda client, **kwargs: get_run_metrics(client, "run-123", **kwargs),
        _result_core,
        {"run_id": "run-123"},
    ),
    (
        "compare_runs",
        lambda client, **kwargs: compare_runs(client, "run-new", "run-old", **kwargs),
        _compare_core,
        {
            "new_run_id": "run-new",
            "old_run_id": "run-old",
            "aggregate_function": "average",
        },
    ),
]
HELPER_IDS = [name for name, _, _, _ in HELPERS]


@pytest.mark.parametrize("name, call, core, core_kwargs", HELPERS, ids=HELPER_IDS)
class TestProjectSelection:
    """Which request each result function sends, and what it tells the caller."""

    def test_project_id_with_a_data_plane_key_sends_the_scoped_request(
        self,
        data_plane_client: Mock,
        name: str,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
        core_kwargs: Dict[str, Any],
    ) -> None:
        """The core receives the project, and nothing is deprecated."""
        del name
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            call(data_plane_client, project_id=PROJECT_ID)

        core(data_plane_client).assert_called_once_with(
            **core_kwargs, project_id=PROJECT_ID
        )
        assert not caught

    def test_no_project_id_sends_the_project_key_request_and_warns(
        self,
        data_plane_client: Mock,
        name: str,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
        core_kwargs: Dict[str, Any],
    ) -> None:
        """Without ``project_id`` the call is deprecated, whatever keys exist."""
        with pytest.warns(DeprecationWarning) as caught:
            call(data_plane_client)

        core(data_plane_client).assert_called_once_with(**core_kwargs, project_id=None)
        assert len(caught) == 1
        message = str(caught[0].message)
        assert f"experiments.{name}() without project_id" in message
        assert "HH_DATA_PLANE_API_KEY" in message
        assert caught[0].filename == __file__

    def test_project_id_without_a_data_plane_key_is_ignored_with_a_warning(
        self,
        project_key_client: Mock,
        name: str,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
        core_kwargs: Dict[str, Any],
    ) -> None:
        """The call keeps working on the project key and names what is missing."""
        with pytest.warns(DeprecationWarning) as caught:
            call(project_key_client, project_id=PROJECT_ID)

        core(project_key_client).assert_called_once_with(**core_kwargs, project_id=None)
        assert len(caught) == 1
        message = str(caught[0].message)
        assert f"'project_id' argument to {name}()" in message
        assert "ignored" in message
        assert "HH_DATA_PLANE_API_KEY" in message
        assert caught[0].filename == __file__

    def test_project_id_with_neither_key_is_kept(
        self,
        keyless_client: Mock,
        name: str,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
        core_kwargs: Dict[str, Any],
    ) -> None:
        """With no project key to fall back to, the scoped request is asked for.

        The core then refuses it naming the data plane key, which is the key a
        caller who passes ``project_id`` is missing.
        """
        del name
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            call(keyless_client, project_id=PROJECT_ID)

        core(keyless_client).assert_called_once_with(
            **core_kwargs, project_id=PROJECT_ID
        )
        assert not caught


# The two functions that take `aggregate_function`, each as a call that passes
# it and the core that receives it.
AGGREGATING: List[Tuple[Callable[..., Any], Callable[[Mock], Mock]]] = [
    (
        lambda client, **kwargs: get_run_result(client, "run-123", **kwargs),
        _result_core,
    ),
    (
        lambda client, **kwargs: compare_runs(client, "run-new", "run-old", **kwargs),
        _compare_core,
    ),
]
AGGREGATING_IDS = ["get_run_result", "compare_runs"]


@pytest.mark.parametrize("call, core", AGGREGATING, ids=AGGREGATING_IDS)
class TestAggregateFunction:
    """An ``aggregate_function`` the scoped operations refuse becomes "average"."""

    def test_scoped_request_sends_an_accepted_value_as_given(
        self,
        data_plane_client: Mock,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
    ) -> None:
        """A value in the scoped enum reaches the core without a warning."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            call(data_plane_client, project_id=PROJECT_ID, aggregate_function="median")

        assert (
            core(data_plane_client).call_args.kwargs["aggregate_function"] == "median"
        )
        assert not caught

    def test_scoped_request_replaces_a_refused_value_and_warns(
        self,
        data_plane_client: Mock,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
    ) -> None:
        """The caller is told which value was dropped and which are accepted."""
        with pytest.warns(UserWarning) as caught:
            call(data_plane_client, project_id=PROJECT_ID, aggregate_function="mean")

        assert (
            core(data_plane_client).call_args.kwargs["aggregate_function"] == "average"
        )
        assert len(caught) == 1
        message = str(caught[0].message)
        assert "'mean'" in message
        assert "median" in message
        assert caught[0].filename == __file__

    def test_project_key_request_sends_a_refused_value_as_given(
        self,
        project_key_client: Mock,
        call: Callable[..., Any],
        core: Callable[[Mock], Mock],
    ) -> None:
        """The project key's operations do their own fallback, so nothing changes."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            call(project_key_client, aggregate_function="mean")

        assert core(project_key_client).call_args.kwargs["aggregate_function"] == "mean"
        assert not [w for w in caught if issubclass(w.category, UserWarning)]


@pytest.mark.parametrize(
    "operation_id", ["getExperimentSummary", "getExperimentComparison"]
)
def test_scoped_aggregate_functions_match_the_spec(operation_id: str) -> None:
    """The SDK's copy of the accepted values equals the spec's enum.

    A value the spec gains and this copy lacks would be replaced by "average"
    on the scoped requests, so the copy must move with the spec.
    """
    require_spec()

    assert set(results_module._SCOPED_AGGREGATE_FUNCTIONS) == spec_parameter_enum(
        operation_id, "aggregate_function"
    )


class TestGetRunResultParsing:
    """``get_run_result`` turns the response into an ``ExperimentResultSummary``."""

    def test_parses_the_summary(self, data_plane_client: Mock) -> None:
        """Status, pass and fail lists, metrics and datapoints are all carried."""
        result = get_run_result(data_plane_client, "run-123", PROJECT_ID)

        assert isinstance(result, ExperimentResultSummary)
        assert result.run_id == "run-123"
        assert result.status == "completed"
        assert result.success is True
        assert result.passed == ["dp-1", "dp-2"]
        assert result.failed == ["dp-3"]
        assert isinstance(result.metrics, AggregatedMetrics)
        assert result.metrics.get_metric("accuracy") == {
            "aggregate": 0.85,
            "values": [0.8, 0.9],
        }
        assert [dp.datapoint_id for dp in result.datapoints] == ["dp-1", "dp-3"]

    def test_parses_a_response_with_no_metrics(self, data_plane_client: Mock) -> None:
        """A run with nothing aggregated yields empty metrics, not an error."""
        data_plane_client.experiments._get_result.return_value = {
            "status": "completed",
            "success": False,
            "metrics": {},
        }

        result = get_run_result(data_plane_client, "run-123", PROJECT_ID)

        assert result.success is False
        assert result.metrics.list_metrics() == []
        assert result.datapoints == []


class TestGetRunMetrics:
    """``get_run_metrics`` returns the run result as the client gives it."""

    def test_returns_the_response_unparsed(self, data_plane_client: Mock) -> None:
        """The dict the core answers with is the dict the caller gets."""
        assert get_run_metrics(data_plane_client, "run-123", PROJECT_ID) == (
            RESULT_RESPONSE
        )


class TestCompareRunsParsing:
    """``compare_runs`` turns the response into a ``RunComparisonResult``."""

    def test_parses_the_comparison(self, data_plane_client: Mock) -> None:
        """Common datapoints are counted and each metric's delta is kept."""
        result = compare_runs(data_plane_client, "run-new", "run-old", PROJECT_ID)

        assert isinstance(result, RunComparisonResult)
        assert result.new_run_id == "run-new"
        assert result.old_run_id == "run-old"
        assert result.common_datapoints == 3
        accuracy = result.get_metric_delta("accuracy")
        assert accuracy is not None
        assert accuracy["old_aggregate"] == 0.80
        assert accuracy["new_aggregate"] == 0.85
        assert accuracy["improved"] == ["dp-1", "dp-2"]
        assert result.list_improved_metrics() == ["accuracy"]
        assert result.list_degraded_metrics() == ["latency"]

    def test_parses_a_comparison_with_nothing_in_common(
        self, data_plane_client: Mock
    ) -> None:
        """Runs that share no datapoints compare to an empty result."""
        data_plane_client.experiments._compare_runs.return_value = {
            "commonDatapoints": [],
            "metrics": [],
        }

        result = compare_runs(data_plane_client, "run-new", "run-old", PROJECT_ID)

        assert result.common_datapoints == 0
        assert result.metric_deltas == {}
