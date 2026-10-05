"""Unit tests for each twin wrapper's choice of operation and key.

A twin wrapper is a public method that takes an optional ``project_id``. It
sends the project-scoped operation with the data plane key when it is given
``project_id``, and the unscoped operation with the project key, plus a
``DeprecationWarning``, when it is not. Each branch is refused before sending,
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
from typing import Any, Callable, Dict, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from honeyhive import MissingApiKeyError
from honeyhive.api import client as client_module
from honeyhive.api.client import HoneyHive
from honeyhive.models import CreateChartRequest, UpdateChartRequest

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32

CREATE_CHART_REQUEST = CreateChartRequest(name="n", metric="event_count")
UPDATE_CHART_REQUEST = UpdateChartRequest(name="n")


@dataclass(frozen=True)
class Case:
    """One twin wrapper: its method and the two functions it dispatches to.

    ``namespace`` is both the ``HoneyHive`` attribute that holds the method and
    the stem of the service modules it calls, ``<namespace>_svc`` and
    ``<namespace>_svc_async`` in ``honeyhive.api.client``.
    """

    namespace: str
    method: str
    args: Tuple[Any, ...]
    scoped: str
    scoped_kwargs: Dict[str, Any]
    legacy: str
    legacy_kwargs: Dict[str, Any]


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
]


def _case_id(case: Case) -> str:
    return f"{case.namespace}.{case.method}"


def _client(**keys: str) -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(**keys)


def _method(client: HoneyHive, case: Case, suffix: str = "") -> Callable[..., Any]:
    return getattr(getattr(client, case.namespace), f"{case.method}{suffix}")


def _service(case: Case, suffix: str = "") -> ModuleType:
    service: ModuleType = getattr(client_module, f"{case.namespace}_svc{suffix}")
    return service


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
        with patch.object(_service(case), case.scoped) as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = _method(client, case)(*case.args, project_id="p1")

        assert result is scoped.return_value
        _assert_sent(scoped, DATA_PLANE_KEY, case.scoped_kwargs)

    def test_no_project_id_sends_the_legacy_operation_with_the_project_key(
        self, case: Case
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(_service(case), case.legacy) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = _method(client, case)(*case.args)

        assert result is legacy.return_value
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

    def test_project_id_without_a_data_plane_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the project key, the scoped call is refused, naming the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(_service(case), case.scoped) as scoped:
            with pytest.raises(MissingApiKeyError) as exc_info:
                _method(client, case)(*case.args, project_id="p1")

        assert exc_info.value.key_kind == "data_plane"
        scoped.assert_not_called()

    def test_no_project_id_without_a_project_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the data plane key, the unscoped call is refused, naming the project key."""
        client = _client(data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(_service(case), case.legacy) as legacy:
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
            _service(case, "_async"), case.scoped, new_callable=AsyncMock
        ) as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await _method(client, case, "_async")(
                    *case.args, project_id="p1"
                )

        assert result is scoped.return_value
        _assert_sent(scoped, DATA_PLANE_KEY, case.scoped_kwargs)

    @pytest.mark.asyncio
    async def test_no_project_id_sends_the_legacy_operation_with_the_project_key(
        self, case: Case
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            _service(case, "_async"), case.legacy, new_callable=AsyncMock
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = await _method(client, case, "_async")(*case.args)

        assert result is legacy.return_value
        _assert_sent(legacy, PROJECT_KEY, case.legacy_kwargs)
        [warning] = caught
        assert f"{case.namespace}.{case.method}_async() without project_id" in str(
            warning.message
        )
        assert warning.filename == __file__

    @pytest.mark.asyncio
    async def test_project_id_without_a_data_plane_key_sends_nothing(
        self, case: Case
    ) -> None:
        """With only the project key, the scoped call is refused, naming the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(
            _service(case, "_async"), case.scoped, new_callable=AsyncMock
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
            _service(case, "_async"), case.legacy, new_callable=AsyncMock
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
