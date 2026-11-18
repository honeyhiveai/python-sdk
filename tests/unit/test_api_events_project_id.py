"""Unit tests for event reads that name a project.

``events.export``, ``events.list`` and their aliases take ``project_id``. With
it they send the project-scoped search with the data plane key. Without it
they send the older export request with the project key and warn. The search
refuses arguments the export operation corrects, so the scoped body follows
that operation's rules, and the tables here state them.

Every warning is checked for the file it is attributed to. Pytest shows a
warning at any ``stacklevel``, and Python's default filter hides a
``DeprecationWarning`` that is attributed to the SDK.
"""

# pylint: disable=protected-access,redefined-outer-name

import os
import warnings
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterator, List, NamedTuple, Optional
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from honeyhive import MissingApiKeyError
from honeyhive._generated.api_config import APIConfig
from honeyhive.api.client import (
    EXPORT_TIMEOUT,
    EventsAPI,
    HoneyHive,
    _scoped_search_body,
)
from honeyhive.models import (
    EventExportResponse,
    EventFilter,
    GetEventsQuery,
    GetEventsResponse,
)

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32
PROJECT_ID = "project-123"
BASE_URL = "https://api.test.honeyhive.ai"
SCOPED_PATH = f"/v1/projects/{PROJECT_ID}/events/search"
FLAT_PATH = "/v1/events/export"

START = "2024-01-01T00:00:00Z"
END = "2024-01-31T23:59:59Z"
EARLIEST = "1970-01-01T00:00:00.000Z"
LATEST = "2099-12-31T23:59:59.999Z"

SESSION_FILTER = {
    "field": "session_id",
    "operator": "is",
    "value": "session-1",
    "type": "string",
}

SYNC_EXPORTS = ["export", "list_events", "get_events"]
ASYNC_EXPORTS = ["export_async", "list_events_async", "get_events_async"]

PROJECT_ARGUMENT_WARNING = (
    "The 'project' parameter is ignored. It is deprecated and will be removed "
    "in v2.0. Name the project with project_id, which takes the project's ID."
)


def missing_project_id_warning(method: str) -> str:
    """The warning ``events.<method>()`` gives when called without project_id."""
    return (
        f"Calling events.{method}() without project_id is deprecated and will "
        "stop working in v2.0. Pass project_id, and configure a data plane API "
        "key with data_plane_api_key or the HH_DATA_PLANE_API_KEY environment "
        "variable."
    )


class Transport(NamedTuple):
    """The patched HTTP client class and the request method of its instance."""

    client_cls: Mock
    request: Mock

    @property
    def path(self) -> str:
        """The path of the one request sent."""
        self.request.assert_called_once()
        return str(self.request.call_args.args[1])

    @property
    def body(self) -> Dict[str, Any]:
        """The JSON body of the one request sent."""
        self.request.assert_called_once()
        return dict(self.request.call_args.kwargs["json"])

    @property
    def bearer(self) -> str:
        """The Authorization header of the one request sent."""
        self.request.assert_called_once()
        return str(self.request.call_args.kwargs["headers"]["Authorization"])


def _response(events: Optional[List[Dict[str, Any]]] = None) -> Mock:
    """A 200 response in the shape the project-scoped search answers with."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    events = events if events is not None else [{"event_id": "e1"}]
    response.json.return_value = {"events": events, "count": len(events)}
    return response


@pytest.fixture
def events(api_config: APIConfig) -> EventsAPI:
    """An events namespace that holds a project key and a data plane key."""
    return EventsAPI(api_config, data_plane_api_key=DATA_PLANE_KEY)


@pytest.fixture
def sync_transport() -> Iterator[Transport]:
    """The transport the sync methods send through."""
    with patch("honeyhive.api.client.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.request.return_value = _response()
        yield Transport(client_cls, client.request)


@pytest.fixture
def async_transport() -> Iterator[Transport]:
    """The transport the async methods send through."""
    with patch("honeyhive.api.client.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
        client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        client.request = AsyncMock(return_value=_response())
        yield Transport(client_cls, client.request)


class TestScopedSearchBody:
    """The body the project-scoped search is sent, rule by rule."""

    @pytest.mark.parametrize(
        "date_range, expected",
        [
            ({"$gte": START, "$lte": END}, {"start_time": START, "end_time": END}),
            ({"gte": START, "lte": END}, {"start_time": START, "end_time": END}),
            (
                {"$gte": START, "gte": "unused", "lte": END},
                {"start_time": START, "end_time": END},
            ),
            ({"$gte": START}, {"start_time": START, "end_time": LATEST}),
            ({"lte": END}, {"start_time": EARLIEST, "end_time": END}),
            # A bound that is not a string is absent.
            (
                {"$gte": 1704067200000, "$lte": END},
                {"start_time": EARLIEST, "end_time": END},
            ),
            ({"$gte": 1704067200000, "$lte": 1706745599000}, None),
            ({"$gte": "", "$lte": ""}, None),
            ({"relative": "7d"}, None),
            ({}, None),
            (None, None),
            (
                f'{{"$gte": "{START}", "$lte": "{END}"}}',
                {"start_time": START, "end_time": END},
            ),
            ("not json", None),
            ("[1, 2]", None),
        ],
    )
    def test_date_range(
        self, date_range: Any, expected: Optional[Dict[str, str]]
    ) -> None:
        """The range takes the search's keys, and one missing bound is filled."""
        body = _scoped_search_body([], date_range, 1000, 1)

        assert body.get("dateRange") == expected

    @pytest.mark.parametrize(
        "date_range, key",
        [
            ({"$gte": datetime(2024, 1, 1, tzinfo=timezone.utc), "$lte": END}, "$gte"),
            ({"$gte": START, "$lte": datetime(2024, 1, 31)}, "$lte"),
            ({"gte": date(2024, 1, 1)}, "gte"),
            ({"lte": True}, "lte"),
        ],
    )
    def test_a_bound_of_another_type_is_refused(
        self, date_range: Dict[str, Any], key: str
    ) -> None:
        """A bound the export request cannot encode does not widen the range."""
        with pytest.raises(TypeError) as exc_info:
            _scoped_search_body([], date_range, 1000, 1)

        assert f"date_range[{key!r}]" in str(exc_info.value)

    @pytest.mark.parametrize(
        "timestamp",
        ["2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00", "2024-01-01"],
    )
    def test_timestamps_are_sent_as_given(self, timestamp: str) -> None:
        """A timestamp the API refuses is not rewritten into one it accepts."""
        body = _scoped_search_body([], {"$gte": timestamp, "$lte": timestamp}, 1000, 1)

        assert body["dateRange"] == {"start_time": timestamp, "end_time": timestamp}

    @pytest.mark.parametrize(
        "limit, expected",
        [
            (25, 25),
            (1000, 1000),
            (5000, 1000),
            (0, 1000),
            (-3, 1000),
            (None, 1000),
            ("25", 25),
            ("5000", 1000),
            (" 7", 7),
            ("12abc", 12),
            ("abc", 1000),
            ("", 1000),
            (True, 1000),
            (float("nan"), 1000),
            (float("inf"), 1000),
            (2.5, 2.5),
        ],
    )
    def test_limit(self, limit: Any, expected: Any) -> None:
        """A limit the search refuses becomes the one the export operation uses."""
        assert _scoped_search_body([], None, limit, 1)["limit"] == expected

    @pytest.mark.parametrize(
        "page, expected",
        [
            (3, 3),
            (5000, 5000),
            (0, 1),
            (-1, 1),
            (None, 1),
            ("4", 4),
            ("4th", 4),
            ("x", 1),
            (True, 1),
        ],
    )
    def test_page(self, page: Any, expected: Any) -> None:
        """A page the search refuses becomes the first page, with no cap."""
        assert _scoped_search_body([], None, 1000, page)["page"] == expected

    def test_carries_only_what_the_search_accepts(self) -> None:
        """Filters pass through, and no other key is added."""
        filters = [SESSION_FILTER]

        body = _scoped_search_body(filters, None, 10, 2)

        assert body == {"filters": filters, "limit": 10, "page": 2}


class TestExport:
    """``export`` and ``export_async``, request by request."""

    ARGUMENTS: Dict[str, Any] = {
        "filters": [EventFilter(**SESSION_FILTER), SESSION_FILTER],
        "date_range": {"$gte": START},
        "projections": ["event_name"],
        "limit": 5000,
        "page": 2,
    }
    SCOPED_BODY = {
        "filters": [SESSION_FILTER, SESSION_FILTER],
        "limit": 1000,
        "page": 2,
        "dateRange": {"start_time": START, "end_time": LATEST},
    }
    FLAT_BODY = {
        "filters": [SESSION_FILTER, SESSION_FILTER],
        "limit": 5000,
        "page": 2,
        "dateRange": {"$gte": START},
        "projections": ["event_name"],
    }

    def test_project_id_sends_the_scoped_search(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """With project_id the search is sent on export's transport, silently."""
        retry = events._retry_config
        with patch.object(retry, "execute", wraps=retry.execute) as execute:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = events.export(**self.ARGUMENTS, project_id=PROJECT_ID)

        sync_transport.client_cls.assert_called_once_with(
            base_url=BASE_URL, verify=True, timeout=EXPORT_TIMEOUT
        )
        execute.assert_called_once()
        assert execute.call_args.kwargs == {"operation": "export()"}
        assert sync_transport.request.call_args.args == ("POST", SCOPED_PATH)
        assert sync_transport.bearer == f"Bearer {DATA_PLANE_KEY}"
        assert sync_transport.body == self.SCOPED_BODY
        assert isinstance(result, EventExportResponse)
        assert [event.event_id for event in result.events] == ["e1"]
        assert result.total_events == 1

    @pytest.mark.asyncio
    async def test_async_project_id_sends_the_scoped_search(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """``export_async`` sends the same request as ``export``."""
        retry = events._retry_config
        with patch.object(retry, "execute_async", wraps=retry.execute_async) as execute:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await events.export_async(
                    **self.ARGUMENTS, project_id=PROJECT_ID
                )

        async_transport.client_cls.assert_called_once_with(
            base_url=BASE_URL, verify=True, timeout=EXPORT_TIMEOUT
        )
        execute.assert_called_once()
        assert execute.call_args.kwargs == {"operation": "export_async()"}
        assert async_transport.request.call_args.args == ("POST", SCOPED_PATH)
        assert async_transport.bearer == f"Bearer {DATA_PLANE_KEY}"
        assert async_transport.body == self.SCOPED_BODY
        assert [event.event_id for event in result.events] == ["e1"]
        assert result.total_events == 1

    def test_no_project_id_sends_the_export_request_unchanged(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """Without project_id the body is the caller's, on the project key."""
        with pytest.warns(DeprecationWarning):
            events.export(**self.ARGUMENTS)

        assert sync_transport.path == FLAT_PATH
        assert sync_transport.bearer == "Bearer test-api-key"
        assert sync_transport.body == self.FLAT_BODY

    @pytest.mark.asyncio
    async def test_async_no_project_id_sends_the_export_request_unchanged(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """``export_async`` without project_id sends the same flat request."""
        with pytest.warns(DeprecationWarning):
            await events.export_async(**self.ARGUMENTS)

        assert async_transport.path == FLAT_PATH
        assert async_transport.bearer == "Bearer test-api-key"
        assert async_transport.body == self.FLAT_BODY

    def test_project_id_without_a_data_plane_key_sends_nothing(
        self, api_config: APIConfig, sync_transport: Transport
    ) -> None:
        """The project key never stands in for the data plane key."""
        events = EventsAPI(api_config)

        with pytest.raises(MissingApiKeyError) as exc_info:
            events.export(project_id=PROJECT_ID)

        assert exc_info.value.key_kind == "data_plane"
        sync_transport.client_cls.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_project_id_without_a_data_plane_key_sends_nothing(
        self, api_config: APIConfig, async_transport: Transport
    ) -> None:
        """``export_async`` refuses the same call before sending."""
        events = EventsAPI(api_config)

        with pytest.raises(MissingApiKeyError) as exc_info:
            await events.export_async(project_id=PROJECT_ID)

        assert exc_info.value.key_kind == "data_plane"
        async_transport.client_cls.assert_not_called()

    def test_a_datetime_bound_sends_nothing_on_either_path(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """Both paths refuse the bound with the same error type."""
        date_range: Any = {"$gte": datetime(2024, 1, 1, tzinfo=timezone.utc)}

        with pytest.raises(TypeError):
            events.export(date_range=date_range, project_id=PROJECT_ID)
        sync_transport.client_cls.assert_not_called()

    def test_the_client_gives_the_namespace_its_data_plane_key(
        self, sync_transport: Transport
    ) -> None:
        """A client built with only a data plane key exports with project_id."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(data_plane_api_key=DATA_PLANE_KEY)

        client.events.export(project_id=PROJECT_ID)
        assert sync_transport.bearer == f"Bearer {DATA_PLANE_KEY}"

        with pytest.warns(DeprecationWarning):
            with pytest.raises(MissingApiKeyError) as exc_info:
                client.events.export()
        assert exc_info.value.key_kind == "project"


class TestEveryExportMethod:
    """``export`` and its aliases each take ``project_id`` and warn by name."""

    @pytest.mark.parametrize("method", SYNC_EXPORTS)
    def test_project_id_sends_the_scoped_search(
        self, method: str, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """With project_id the method reaches the scoped search and is silent."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            getattr(events, method)(filters=[SESSION_FILTER], project_id=PROJECT_ID)

        assert sync_transport.path == SCOPED_PATH
        assert sync_transport.bearer == f"Bearer {DATA_PLANE_KEY}"

    @pytest.mark.parametrize("method", ASYNC_EXPORTS)
    @pytest.mark.asyncio
    async def test_async_project_id_sends_the_scoped_search(
        self, method: str, events: EventsAPI, async_transport: Transport
    ) -> None:
        """Each async method does the same."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            await getattr(events, method)(
                filters=[SESSION_FILTER], project_id=PROJECT_ID
            )

        assert async_transport.path == SCOPED_PATH
        assert async_transport.bearer == f"Bearer {DATA_PLANE_KEY}"

    @pytest.mark.parametrize("method", SYNC_EXPORTS)
    def test_no_project_id_warns_once_under_its_own_name(
        self, method: str, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """Without project_id the caller gets one warning that names the method."""
        with pytest.warns(DeprecationWarning) as caught:
            getattr(events, method)(filters=[SESSION_FILTER])

        [warning] = caught
        assert str(warning.message) == missing_project_id_warning(method)
        assert warning.filename == __file__
        assert sync_transport.path == FLAT_PATH

    @pytest.mark.parametrize("method", ASYNC_EXPORTS)
    @pytest.mark.asyncio
    async def test_async_no_project_id_warns_once_under_its_own_name(
        self, method: str, events: EventsAPI, async_transport: Transport
    ) -> None:
        """Each async method warns under its own name too."""
        with pytest.warns(DeprecationWarning) as caught:
            await getattr(events, method)(filters=[SESSION_FILTER])

        [warning] = caught
        assert str(warning.message) == missing_project_id_warning(method)
        assert warning.filename == __file__
        assert async_transport.path == FLAT_PATH

    @pytest.mark.parametrize("method", SYNC_EXPORTS)
    def test_project_argument_warns_and_stays_out_of_the_search(
        self, method: str, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """``project`` beside project_id warns once and is not sent."""
        with pytest.warns(DeprecationWarning) as caught:
            getattr(events, method)(project="my-project", project_id=PROJECT_ID)

        [warning] = caught
        assert str(warning.message) == PROJECT_ARGUMENT_WARNING
        assert warning.filename == __file__
        assert "project" not in sync_transport.body

    @pytest.mark.parametrize("method", ASYNC_EXPORTS)
    @pytest.mark.asyncio
    async def test_async_project_argument_warns_and_stays_out_of_the_search(
        self, method: str, events: EventsAPI, async_transport: Transport
    ) -> None:
        """Each async method gives the ``project`` warning itself."""
        with pytest.warns(DeprecationWarning) as caught:
            await getattr(events, method)(project="my-project", project_id=PROJECT_ID)

        [warning] = caught
        assert str(warning.message) == PROJECT_ARGUMENT_WARNING
        assert warning.filename == __file__
        assert "project" not in async_transport.body

    @pytest.mark.parametrize("method", SYNC_EXPORTS)
    def test_project_argument_without_project_id_gives_both_warnings(
        self, method: str, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """The flat request still carries ``project``, as it does today."""
        with pytest.warns(DeprecationWarning) as caught:
            getattr(events, method)(project="my-project")

        assert [str(warning.message) for warning in caught] == [
            PROJECT_ARGUMENT_WARNING,
            missing_project_id_warning(method),
        ]
        assert {warning.filename for warning in caught} == {__file__}
        assert sync_transport.body["project"] == "my-project"


class TestList:
    """``list`` and ``list_async`` over the same request."""

    QUERY: Dict[str, Any] = {
        "filters": [SESSION_FILTER],
        "dateRange": {"$gte": START, "$lte": END},
        "projections": ["event_name"],
        "limit": 10,
        "page": 2,
        "evaluation_id": "run-1",
        "ignore_order": True,
    }
    SCOPED_BODY = {
        "filters": [SESSION_FILTER],
        "limit": 10,
        "page": 2,
        "dateRange": {"start_time": START, "end_time": END},
    }

    def test_project_id_sends_the_scoped_search(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """With project_id the query becomes the search body, silently."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = events.list(self.QUERY, project_id=PROJECT_ID)

        assert sync_transport.path == SCOPED_PATH
        assert sync_transport.bearer == f"Bearer {DATA_PLANE_KEY}"
        assert sync_transport.body == self.SCOPED_BODY
        assert isinstance(result, GetEventsResponse)
        assert result.totalEvents == 1

    @pytest.mark.asyncio
    async def test_async_project_id_sends_the_scoped_search(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """``list_async`` sends the same request as ``list``."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = await events.list_async(self.QUERY, project_id=PROJECT_ID)

        assert async_transport.path == SCOPED_PATH
        assert async_transport.body == self.SCOPED_BODY
        assert result.totalEvents == 1

    def test_a_query_model_date_range_reaches_the_search(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """The model names its bounds ``gte`` and ``lte``, which the body reads."""
        query = GetEventsQuery.model_validate(
            {"dateRange": {"$gte": START, "$lte": END}}
        )
        assert set(query.model_dump(exclude_none=True)["dateRange"]) == {"gte", "lte"}

        events.list(query, project_id=PROJECT_ID)

        assert sync_transport.body["dateRange"] == {
            "start_time": START,
            "end_time": END,
        }

    def test_no_project_id_warns_once_under_its_own_name(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """``list`` warns as ``events.list()``, not as ``export``."""
        with pytest.warns(DeprecationWarning) as caught:
            events.list(self.QUERY)

        [warning] = caught
        assert str(warning.message) == missing_project_id_warning("list")
        assert warning.filename == __file__
        assert sync_transport.path == FLAT_PATH
        assert sync_transport.bearer == "Bearer test-api-key"

    @pytest.mark.asyncio
    async def test_async_no_project_id_warns_once_under_its_own_name(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """``list_async`` warns as ``events.list_async()``."""
        with pytest.warns(DeprecationWarning) as caught:
            await events.list_async(self.QUERY)

        [warning] = caught
        assert str(warning.message) == missing_project_id_warning("list_async")
        assert warning.filename == __file__
        assert async_transport.path == FLAT_PATH

    def test_project_id_is_keyword_only(self, events: EventsAPI) -> None:
        """A second positional argument is not taken for project_id."""
        with pytest.raises(TypeError):
            getattr(events, "list")(self.QUERY, PROJECT_ID)


class TestGetBySessionId:
    """``get_by_session_id`` stays on the project key and its own warning."""

    EVENTS = [
        {"event_id": "e2", "start_time": 2000.0},
        {"event_id": "e1", "start_time": 1000.0},
    ]

    def test_sends_the_export_request_with_one_warning(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """A client that holds a data plane key still sends the flat request."""
        sync_transport.request.return_value = _response(self.EVENTS)

        with pytest.warns(DeprecationWarning) as caught:
            result = events.get_by_session_id("session-1")

        [warning] = caught
        assert "events.get_by_session_id() is deprecated" in str(warning.message)
        assert warning.filename == __file__
        assert sync_transport.path == FLAT_PATH
        assert sync_transport.bearer == "Bearer test-api-key"
        assert sync_transport.body == {
            "filters": [SESSION_FILTER],
            "limit": 1000,
            "page": 1,
        }
        assert [event.event_id for event in result.events] == ["e1", "e2"]

    @pytest.mark.asyncio
    async def test_async_sends_the_export_request_with_one_warning(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """``get_by_session_id_async`` does the same."""
        async_transport.request.return_value = _response(self.EVENTS)

        with pytest.warns(DeprecationWarning) as caught:
            result = await events.get_by_session_id_async("session-1")

        [warning] = caught
        assert "events.get_by_session_id_async() is deprecated" in str(warning.message)
        assert warning.filename == __file__
        assert async_transport.path == FLAT_PATH
        assert [event.event_id for event in result.events] == ["e1", "e2"]

    def test_project_argument_adds_one_warning(
        self, events: EventsAPI, sync_transport: Transport
    ) -> None:
        """``project`` warns once more, and both warnings reach the caller."""
        with pytest.warns(DeprecationWarning) as caught:
            events.get_by_session_id("session-1", "my-project")

        deprecation, project = caught
        assert "events.get_by_session_id() is deprecated" in str(deprecation.message)
        assert "The project comes from the API key." in str(project.message)
        assert {deprecation.filename, project.filename} == {__file__}
        assert sync_transport.body["project"] == "my-project"

    @pytest.mark.asyncio
    async def test_async_project_argument_adds_one_warning(
        self, events: EventsAPI, async_transport: Transport
    ) -> None:
        """The async method attributes both warnings to its caller too."""
        with pytest.warns(DeprecationWarning) as caught:
            await events.get_by_session_id_async("session-1", "my-project")

        deprecation, project = caught
        assert "The project comes from the API key." in str(project.message)
        assert {deprecation.filename, project.filename} == {__file__}
        assert async_transport.body["project"] == "my-project"
