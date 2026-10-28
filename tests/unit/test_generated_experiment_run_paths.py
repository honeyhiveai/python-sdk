"""Unit tests for the paths the generated run services request."""

from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)

RUN: Dict[str, Any] = {
    "id": "id1",
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


DELETED: Dict[str, Any] = {"id": "r1", "deleted": True}


def _mock_client(body: Optional[Dict[str, Any]] = None) -> MagicMock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"evaluation": RUN} if body is None else body
    client = MagicMock()
    client.request.return_value = response
    return client


def _requested_path(client: MagicMock) -> str:
    return str(client.request.call_args.args[1])


def _requested_method(client: MagicMock) -> str:
    return str(client.request.call_args.args[0])


class TestSyncRunReadPaths:
    """Sync getRun reads at the project URL and getRunLegacy at the flat one."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_run_requests_the_project_path(self, client_cls: MagicMock) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getRun(APIConfig(), project_id="p1", run_id="r1")

        assert _requested_path(client) == "/v1/projects/p1/runs/r1"
        assert result.evaluation.run_id == "r1"

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_run_legacy_requests_the_flat_path(self, client_cls: MagicMock) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getRunLegacy(APIConfig(), run_id="r1")

        assert _requested_path(client) == "/v1/runs/r1"
        assert result.evaluation.run_id == "r1"


class TestAsyncRunReadPaths:
    """Async getRun reads at the project URL and getRunLegacy at the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_run_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client.request = AsyncMock(return_value=client.request.return_value)
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getRun(
            APIConfig(), project_id="p1", run_id="r1"
        )

        assert _requested_path(client) == "/v1/projects/p1/runs/r1"
        assert result.evaluation.run_id == "r1"

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_run_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client.request = AsyncMock(return_value=client.request.return_value)
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getRunLegacy(APIConfig(), run_id="r1")

        assert _requested_path(client) == "/v1/runs/r1"
        assert result.evaluation.run_id == "r1"


class TestSyncRunDeletePaths:
    """Sync deleteRun deletes at the project URL and deleteRunLegacy at the flat one."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_delete_run_requests_the_project_path(self, client_cls: MagicMock) -> None:
        client = _mock_client(DELETED)
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.deleteRun(APIConfig(), project_id="p1", run_id="r1")

        assert _requested_method(client) == "delete"
        assert _requested_path(client) == "/v1/projects/p1/runs/r1"
        assert result.deleted is True

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_delete_run_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client(DELETED)
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.deleteRunLegacy(APIConfig(), run_id="r1")

        assert _requested_method(client) == "delete"
        assert _requested_path(client) == "/v1/runs/r1"
        assert result.deleted is True


class TestAsyncRunDeletePaths:
    """Async deleteRun deletes at the project URL and deleteRunLegacy at the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_delete_run_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client(DELETED)
        client.request = AsyncMock(return_value=client.request.return_value)
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.deleteRun(
            APIConfig(), project_id="p1", run_id="r1"
        )

        assert _requested_method(client) == "delete"
        assert _requested_path(client) == "/v1/projects/p1/runs/r1"
        assert result.deleted is True

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_delete_run_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client(DELETED)
        client.request = AsyncMock(return_value=client.request.return_value)
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.deleteRunLegacy(APIConfig(), run_id="r1")

        assert _requested_method(client) == "delete"
        assert _requested_path(client) == "/v1/runs/r1"
        assert result.deleted is True
