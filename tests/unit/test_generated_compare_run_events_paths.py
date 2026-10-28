"""Unit tests for the paths the generated compare-run-events services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)

COMPARISON: Dict[str, Any] = {"events": [], "totalEvents": 0}


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = COMPARISON
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


class TestSyncCompareRunEventsPaths:
    """Sync compare-events operations request their own paths."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_scoped_requests_the_project_path(self, client_cls: MagicMock) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentCompareEvents(
            APIConfig(), project_id="p1", new_run_id="r1", old_run_id="r2", limit=1
        )

        assert _requested(client) == (
            "get",
            "/v1/projects/p1/runs/r1/compare/r2/events",
        )
        assert result.totalEvents == 0

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_legacy_requests_the_flat_path(self, client_cls: MagicMock) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentCompareEventsLegacy(
            APIConfig(), new_run_id="r1", old_run_id="r2", limit=1
        )

        assert _requested(client) == ("get", "/v1/runs/r1/compare/r2/events")
        assert result.totalEvents == 0

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_query_id_legacy_requests_the_query_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentCompareEventsQueryIdLegacy(
            APIConfig(), run_id_1="r1", run_id_2="r2", limit=1
        )

        assert _requested(client) == ("get", "/v1/runs/compare/events")
        assert result.totalEvents == 0


class TestAsyncCompareRunEventsPaths:
    """Async compare-events operations request their own paths."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_scoped_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentCompareEvents(
            APIConfig(), project_id="p1", new_run_id="r1", old_run_id="r2", limit=1
        )

        assert _requested(client) == (
            "get",
            "/v1/projects/p1/runs/r1/compare/r2/events",
        )
        assert result.totalEvents == 0

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_legacy_requests_the_flat_path(self, client_cls: MagicMock) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentCompareEventsLegacy(
            APIConfig(), new_run_id="r1", old_run_id="r2", limit=1
        )

        assert _requested(client) == ("get", "/v1/runs/r1/compare/r2/events")
        assert result.totalEvents == 0

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_query_id_legacy_requests_the_query_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentCompareEventsQueryIdLegacy(
            APIConfig(), run_id_1="r1", run_id_2="r2", limit=1
        )

        assert _requested(client) == ("get", "/v1/runs/compare/events")
        assert result.totalEvents == 0
