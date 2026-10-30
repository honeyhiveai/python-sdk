"""Unit tests for the paths the generated event get services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Events_service as events_svc
from honeyhive._generated.services import async_Events_service as events_svc_async

EVENT_ID = "7f22137a-6911-4ed3-bc36-110f1dde6b66"
BODY: Dict[str, Any] = {"event": {"event_id": EVENT_ID, "project_id": "p1"}}


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = BODY
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


class TestSyncEventGetPaths:
    """Sync getEvent requests the project URL, getEventLegacy the flat one."""

    @patch("honeyhive._generated.services.Events_service.httpx.Client")
    def test_get_event_requests_the_project_path(self, client_cls: MagicMock) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = events_svc.getEvent(APIConfig(), project_id="p1", event_id=EVENT_ID)

        assert _requested(client) == ("get", f"/v1/projects/p1/events/{EVENT_ID}")
        assert result.event.event_id == EVENT_ID

    @patch("honeyhive._generated.services.Events_service.httpx.Client")
    def test_get_event_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = events_svc.getEventLegacy(APIConfig(), event_id=EVENT_ID)

        assert _requested(client) == ("get", f"/v1/events/{EVENT_ID}")
        assert result.event.event_id == EVENT_ID


class TestAsyncEventGetPaths:
    """Async getEvent requests the project URL, getEventLegacy the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Events_service.httpx.AsyncClient")
    async def test_get_event_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await events_svc_async.getEvent(
            APIConfig(), project_id="p1", event_id=EVENT_ID
        )

        assert _requested(client) == ("get", f"/v1/projects/p1/events/{EVENT_ID}")
        assert result.event.event_id == EVENT_ID

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Events_service.httpx.AsyncClient")
    async def test_get_event_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await events_svc_async.getEventLegacy(APIConfig(), event_id=EVENT_ID)

        assert _requested(client) == ("get", f"/v1/events/{EVENT_ID}")
        assert result.event.event_id == EVENT_ID
