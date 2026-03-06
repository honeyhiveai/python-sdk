"""Unit tests for event export timeout configuration.

Verifies that export() and export_async() use an appropriate timeout
instead of httpx's default 5-second timeout, which causes ReadTimeout
errors on large result sets.
"""

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive.api.client import EXPORT_TIMEOUT, EventsAPI


@pytest.fixture
def api_config() -> APIConfig:
    """Create a test APIConfig."""
    return APIConfig(
        base_path="https://api.test.honeyhive.ai",
        access_token="test-api-key",
    )


@pytest.fixture
def events_api(api_config: APIConfig) -> EventsAPI:
    """Create an EventsAPI instance with test config."""
    return EventsAPI(api_config)


class TestExportTimeoutConstant:
    """Test the EXPORT_TIMEOUT constant."""

    def test_export_timeout_is_httpx_timeout(self) -> None:
        """EXPORT_TIMEOUT should be an httpx.Timeout instance."""
        assert isinstance(EXPORT_TIMEOUT, httpx.Timeout)

    def test_export_timeout_value(self) -> None:
        """EXPORT_TIMEOUT should use split values: short connect/pool, long read."""
        assert EXPORT_TIMEOUT.connect == 10.0
        assert EXPORT_TIMEOUT.read == 300.0
        assert EXPORT_TIMEOUT.write == 30.0
        assert EXPORT_TIMEOUT.pool == 10.0

    def test_export_timeout_exceeds_default(self) -> None:
        """EXPORT_TIMEOUT should be much larger than httpx default (5s)."""
        default_timeout = httpx.Timeout(5.0)
        assert EXPORT_TIMEOUT.read > default_timeout.read


class TestExportSyncTimeout:
    """Test that sync export() uses the correct timeout."""

    @patch("honeyhive.api.client.httpx.Client")
    @patch("honeyhive.api.client.RetryConfig")
    def test_export_creates_client_with_timeout(
        self,
        mock_retry_cls: Mock,
        mock_client_cls: Mock,
        events_api: EventsAPI,
    ) -> None:
        """export() should create httpx.Client with EXPORT_TIMEOUT."""
        # Set up the mock client context manager
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = Mock(return_value=False)

        # Set up retry to return a successful response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": [], "totalEvents": 0}
        mock_retry = Mock()
        mock_retry.execute.return_value = mock_response
        mock_retry_cls.default.return_value = mock_retry

        events_api.export(filters=[])

        # Verify httpx.Client was called with EXPORT_TIMEOUT
        mock_client_cls.assert_called_once_with(
            base_url="https://api.test.honeyhive.ai",
            verify=True,
            timeout=EXPORT_TIMEOUT,
        )

    @patch("honeyhive.api.client.httpx.Client")
    @patch("honeyhive.api.client.RetryConfig")
    def test_export_returns_events(
        self,
        mock_retry_cls: Mock,
        mock_client_cls: Mock,
        events_api: EventsAPI,
    ) -> None:
        """export() should return events from the response."""
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = Mock(return_value=False)

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [{"event_id": "e1"}, {"event_id": "e2"}],
            "totalEvents": 2,
        }
        mock_retry = Mock()
        mock_retry.execute.return_value = mock_response
        mock_retry_cls.default.return_value = mock_retry

        result = events_api.export(filters=[])

        assert len(result.events) == 2
        assert result.total_events == 2


class TestExportAsyncTimeout:
    """Test that async export_async() uses the correct timeout."""

    @patch("honeyhive.api.client.httpx.AsyncClient")
    @patch("honeyhive.api.client.RetryConfig")
    @pytest.mark.asyncio
    async def test_export_async_creates_client_with_timeout(
        self,
        mock_retry_cls: Mock,
        mock_async_client_cls: Mock,
        events_api: EventsAPI,
    ) -> None:
        """export_async() should create httpx.AsyncClient with EXPORT_TIMEOUT."""
        # Set up the mock async client context manager
        mock_client = AsyncMock()
        mock_async_client_cls.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_async_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Set up retry to return a successful response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": [], "totalEvents": 0}
        mock_retry = Mock()
        mock_retry.execute_async = AsyncMock(return_value=mock_response)
        mock_retry_cls.default.return_value = mock_retry

        await events_api.export_async(filters=[])

        # Verify httpx.AsyncClient was called with EXPORT_TIMEOUT
        mock_async_client_cls.assert_called_once_with(
            base_url="https://api.test.honeyhive.ai",
            verify=True,
            timeout=EXPORT_TIMEOUT,
        )

    @patch("honeyhive.api.client.httpx.AsyncClient")
    @patch("honeyhive.api.client.RetryConfig")
    @pytest.mark.asyncio
    async def test_export_async_returns_events(
        self,
        mock_retry_cls: Mock,
        mock_async_client_cls: Mock,
        events_api: EventsAPI,
    ) -> None:
        """export_async() should return events from the response."""
        mock_client = AsyncMock()
        mock_async_client_cls.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_async_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [{"event_id": "e1"}, {"event_id": "e2"}],
            "totalEvents": 2,
        }
        mock_retry = Mock()
        mock_retry.execute_async = AsyncMock(return_value=mock_response)
        mock_retry_cls.default.return_value = mock_retry

        result = await events_api.export_async(filters=[])

        assert len(result.events) == 2
        assert result.total_events == 2

    @patch("honeyhive.api.client.httpx.AsyncClient")
    @patch("honeyhive.api.client.RetryConfig")
    @pytest.mark.asyncio
    async def test_get_by_session_id_async_uses_export_timeout(
        self,
        mock_retry_cls: Mock,
        mock_async_client_cls: Mock,
        events_api: EventsAPI,
    ) -> None:
        """get_by_session_id_async() delegates to export_async() which uses EXPORT_TIMEOUT."""
        mock_client = AsyncMock()
        mock_async_client_cls.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_async_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [{"event_id": "e1", "session_id": "sess-123"}],
            "totalEvents": 1,
        }
        mock_retry = Mock()
        mock_retry.execute_async = AsyncMock(return_value=mock_response)
        mock_retry_cls.default.return_value = mock_retry

        await events_api.get_by_session_id_async("sess-123")

        # Verify the timeout was passed through to AsyncClient
        mock_async_client_cls.assert_called_once_with(
            base_url="https://api.test.honeyhive.ai",
            verify=True,
            timeout=EXPORT_TIMEOUT,
        )
