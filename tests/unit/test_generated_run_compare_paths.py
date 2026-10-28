"""Unit tests for the paths the generated run comparison services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)

RUN = {
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
COMPARISON: Dict[str, Any] = {
    "metrics": [],
    "commonDatapoints": ["d1"],
    "event_details": [],
    "old_run": RUN,
    "new_run": RUN,
}
RUN_IDS = {"new_run_id": "r-new", "old_run_id": "r-old"}


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


class TestSyncRunComparePaths:
    """Sync getExperimentComparison reads at the project URL, the Legacy one at the flat."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_experiment_comparison_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentComparison(
            APIConfig(), project_id="p1", **RUN_IDS
        )

        assert _requested(client) == (
            "get",
            "/v1/projects/p1/runs/r-new/compare/r-old",
        )
        assert result.commonDatapoints == ["d1"]

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_experiment_comparison_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentComparisonLegacy(APIConfig(), **RUN_IDS)

        assert _requested(client) == ("get", "/v1/runs/r-new/compare/r-old")
        assert result.commonDatapoints == ["d1"]


class TestAsyncRunComparePaths:
    """Async getExperimentComparison reads at the project URL, the Legacy one at the flat."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_experiment_comparison_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentComparison(
            APIConfig(), project_id="p1", **RUN_IDS
        )

        assert _requested(client) == (
            "get",
            "/v1/projects/p1/runs/r-new/compare/r-old",
        )
        assert result.commonDatapoints == ["d1"]

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_experiment_comparison_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentComparisonLegacy(
            APIConfig(), **RUN_IDS
        )

        assert _requested(client) == ("get", "/v1/runs/r-new/compare/r-old")
        assert result.commonDatapoints == ["d1"]
