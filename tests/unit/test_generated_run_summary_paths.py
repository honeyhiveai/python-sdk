"""Unit tests for the paths the generated run-summary services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)

SUMMARY: Dict[str, Any] = {
    "status": "completed",
    "success": True,
    "passed": [],
    "failed": [],
    "metrics": {"aggregation_function": "max"},
    "datapoints": [],
    "event_details": [],
    "run_object": {
        "id": "o1",
        "run_id": "r1",
        "metadata": {},
        "results": {},
        "event_ids": [],
        "configuration": {},
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "scope_type": "project",
        "scope_id": "p1",
    },
}


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = SUMMARY
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


class TestSyncRunSummaryPaths:
    """Sync getExperimentSummary reads at the project URL, the legacy one at the flat one."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_experiment_summary_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        experiments_svc.getExperimentSummary(
            APIConfig(), project_id="p1", run_id="r1", aggregate_function="max"
        )

        assert _requested(client) == ("get", "/v1/projects/p1/runs/r1/summary")

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_experiment_summary_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        experiments_svc.getExperimentSummaryLegacy(
            APIConfig(), run_id="r1", aggregate_function="max"
        )

        assert _requested(client) == ("get", "/v1/runs/r1/summary")


class TestAsyncRunSummaryPaths:
    """Async getExperimentSummary reads at the project URL, the legacy one at the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_experiment_summary_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        await experiments_svc_async.getExperimentSummary(
            APIConfig(), project_id="p1", run_id="r1", aggregate_function="max"
        )

        assert _requested(client) == ("get", "/v1/projects/p1/runs/r1/summary")

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_experiment_summary_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        await experiments_svc_async.getExperimentSummaryLegacy(
            APIConfig(), run_id="r1", aggregate_function="max"
        )

        assert _requested(client) == ("get", "/v1/runs/r1/summary")
