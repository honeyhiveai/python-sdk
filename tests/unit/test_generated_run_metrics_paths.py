"""Unit tests for the paths the generated run-metrics services request."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Experiments_service as experiments_svc
from honeyhive._generated.services import (
    async_Experiments_service as experiments_svc_async,
)

METRICS: Dict[str, Any] = {"events": [], "totalEvents": 0}
DATE_RANGE = '{"$gte": 1}'


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = METRICS
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


class TestSyncRunMetricsPaths:
    """Sync getExperimentRunMetrics reads at the project URL, its Legacy twin at the flat one."""

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_run_metrics_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentRunMetrics(
            APIConfig(), project_id="p1", run_id="r1", dateRange=DATE_RANGE
        )

        assert _requested(client) == ("get", "/v1/projects/p1/runs/r1/metrics")
        assert result.totalEvents == 0

    @patch("honeyhive._generated.services.Experiments_service.httpx.Client")
    def test_get_run_metrics_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_client()
        client_cls.return_value.__enter__.return_value = client

        result = experiments_svc.getExperimentRunMetricsLegacy(
            APIConfig(), run_id="r1", dateRange=DATE_RANGE
        )

        assert _requested(client) == ("get", "/v1/runs/r1/metrics")
        assert result.totalEvents == 0


class TestAsyncRunMetricsPaths:
    """Async getExperimentRunMetrics reads at the project URL, its Legacy twin at the flat one."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_run_metrics_requests_the_project_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentRunMetrics(
            APIConfig(), project_id="p1", run_id="r1", dateRange=DATE_RANGE
        )

        assert _requested(client) == ("get", "/v1/projects/p1/runs/r1/metrics")
        assert result.totalEvents == 0

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
    async def test_get_run_metrics_legacy_requests_the_flat_path(
        self, client_cls: MagicMock
    ) -> None:
        client = _mock_async_client()
        client_cls.return_value.__aenter__.return_value = client

        result = await experiments_svc_async.getExperimentRunMetricsLegacy(
            APIConfig(), run_id="r1", dateRange=DATE_RANGE
        )

        assert _requested(client) == ("get", "/v1/runs/r1/metrics")
        assert result.totalEvents == 0
