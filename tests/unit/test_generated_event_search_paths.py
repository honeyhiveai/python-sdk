"""Unit tests for the paths the generated event search services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.models import SearchEventsRequest
from honeyhive._generated.services import Events_service as events_svc
from honeyhive._generated.services import async_Events_service as events_svc_async

PAGE: Dict[str, Any] = {"events": [{"event_id": "e1"}], "count": 1}
REQUEST = SearchEventsRequest(limit=10, page=1)


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = PAGE
    return response


def _mock_client() -> MagicMock:
    client = MagicMock()
    client.request.return_value = _response()
    return client


def _mock_async_client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock(return_value=_response())
    return client


def _requested(client: MagicMock) -> tuple[str, str]:
    method, url = client.request.call_args.args[:2]
    return method, str(url)


class TestSyncEventSearchPaths:
    """Sync searchEvents posts to the project URL, searchEventsLegacy to the flat one."""

    @patch("honeyhive._generated.services.Events_service.httpx.Client")
    def test_search_events_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = events_svc.searchEvents(APIConfig(), project_id="p1", data=REQUEST)

        assert _requested(client) == ("post", "/v1/projects/p1/events/search")
        assert client.request.call_args.kwargs["json"] == {"limit": 10, "page": 1}
        assert result.count == 1

    @patch("honeyhive._generated.services.Events_service.httpx.Client")
    def test_search_events_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = events_svc.searchEventsLegacy(APIConfig(), data=REQUEST)

        assert _requested(client) == ("post", "/v1/events/search")
        assert result.count == 1


class TestAsyncEventSearchPaths:
    """Async searchEvents posts to the project URL, searchEventsLegacy to the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Events_service.httpx.AsyncClient")
    async def test_search_events_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await events_svc_async.searchEvents(
            APIConfig(), project_id="p1", data=REQUEST
        )

        assert _requested(client) == ("post", "/v1/projects/p1/events/search")
        assert result.count == 1

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Events_service.httpx.AsyncClient")
    async def test_search_events_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await events_svc_async.searchEventsLegacy(APIConfig(), data=REQUEST)

        assert _requested(client) == ("post", "/v1/events/search")
        assert result.count == 1
