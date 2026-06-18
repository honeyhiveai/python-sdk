"""Unit tests verifying the generated services pass APIConfig.timeout to httpx.

The generated service functions create an httpx client per request. These tests
confirm the configured ``timeout`` (5.0s by default) is forwarded to both the
sync ``httpx.Client`` and async ``httpx.AsyncClient`` constructors. getDatasets
is used as the representative operation (the customer's reported use case).
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive._generated.services import Datasets_service as datasets_svc
from honeyhive._generated.services import async_Datasets_service as datasets_svc_async


def _mock_response() -> Mock:
    """A 200 response whose body satisfies GetDatasetsResponse."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"datasets": []}
    return response


class TestSyncServiceTimeout:
    """Sync generated services forward api_config.timeout to httpx.Client."""

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_explicit_timeout_is_passed(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.request.return_value = _mock_response()
        mock_client_cls.return_value.__enter__.return_value = mock_client

        datasets_svc.getDatasets(api_config_override=APIConfig(timeout=2.5))

        assert mock_client_cls.call_args.kwargs["timeout"] == 2.5

    @patch("honeyhive._generated.services.Datasets_service.httpx.Client")
    def test_default_timeout_is_passed(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.request.return_value = _mock_response()
        mock_client_cls.return_value.__enter__.return_value = mock_client

        datasets_svc.getDatasets(api_config_override=APIConfig())

        assert mock_client_cls.call_args.kwargs["timeout"] == 5.0


class TestAsyncServiceTimeout:
    """Async generated services forward api_config.timeout to httpx.AsyncClient."""

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Datasets_service.httpx.AsyncClient")
    async def test_explicit_timeout_is_passed(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.request = AsyncMock(return_value=_mock_response())
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        await datasets_svc_async.getDatasets(api_config_override=APIConfig(timeout=2.5))

        assert mock_client_cls.call_args.kwargs["timeout"] == 2.5

    @pytest.mark.asyncio
    @patch("honeyhive._generated.services.async_Datasets_service.httpx.AsyncClient")
    async def test_default_timeout_is_passed(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.request = AsyncMock(return_value=_mock_response())
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        await datasets_svc_async.getDatasets(api_config_override=APIConfig())

        assert mock_client_cls.call_args.kwargs["timeout"] == 5.0
