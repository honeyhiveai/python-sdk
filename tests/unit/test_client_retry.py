"""Unit tests for HoneyHive retry-config threading into events.export()."""

# pylint: disable=protected-access
# Justification: Tests inspect EventsAPI._retry_config to verify wiring.

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from honeyhive._generated.api_config import APIConfig
from honeyhive.api.client import EventsAPI, HoneyHive
from honeyhive.utils.error_handler import APIError
from honeyhive.utils.retry import BackoffStrategy, RetryConfig


class TestHoneyHiveRetryConfig:
    """HoneyHive() threads retry budget into EventsAPI."""

    def test_default_retry_budget(self) -> None:
        """With no retry config, export uses the default of 3 retries."""
        with patch.dict("os.environ", {}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.retry_config.max_retries == 3
        assert client.events._retry_config is client.retry_config

    def test_hh_max_retries_env_var(self) -> None:
        """HH_MAX_RETRIES sets the export retry budget."""
        with patch.dict("os.environ", {"HH_MAX_RETRIES": "5"}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.retry_config.max_retries == 5
        assert client.events._retry_config.max_retries == 5

    def test_explicit_retry_config_beats_env_var(self) -> None:
        """An explicit RetryConfig wins over HH_MAX_RETRIES."""
        explicit = RetryConfig(max_retries=9)
        with patch.dict("os.environ", {"HH_MAX_RETRIES": "5"}, clear=True):
            client = HoneyHive(api_key="k", retry_config=explicit)
        assert client.retry_config is explicit
        assert client.events._retry_config is explicit

    def test_invalid_env_var_falls_back_to_default(self) -> None:
        """Invalid HH_MAX_RETRIES keeps the default of 3."""
        with patch.dict("os.environ", {"HH_MAX_RETRIES": "nope"}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.retry_config.max_retries == 3


def _events_api(api_config: APIConfig, max_retries: int) -> EventsAPI:
    """Build an EventsAPI whose retries do not sleep."""
    return EventsAPI(
        api_config,
        retry_config=RetryConfig(
            max_retries=max_retries,
            backoff_strategy=BackoffStrategy(
                initial_delay=0.0, max_delay=0.0, jitter=0.0
            ),
        ),
    )


def _response(status_code: int) -> Mock:
    """Build an httpx.Response mock for the given status code."""
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    response.text = f"status {status_code}"
    if status_code == 200:
        response.json.return_value = {"events": [{"event_id": "e1"}], "totalEvents": 1}
    return response


class TestExportUsesRetryConfig:
    """events.export() uses the RetryConfig stored on EventsAPI."""

    @pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
    @patch("honeyhive.utils.retry.time.sleep")
    @patch("honeyhive.api.client.httpx.Client")
    def test_export_stops_at_the_configured_budget(
        self,
        mock_client_cls: Mock,
        mock_sleep: Mock,
        status: int,
        api_config: APIConfig,
    ) -> None:
        """A budget of 1 makes 2 attempts, then raises. Pins the budget.

        A hard-coded budget would keep retrying past the second attempt.
        """
        events_api = _events_api(api_config, max_retries=1)

        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = Mock(return_value=False)
        mock_client.request.return_value = _response(status)

        with pytest.raises(APIError):
            events_api.export(filters=[])

        assert mock_client.request.call_count == 2
        assert mock_sleep.call_count == 1

    @patch("honeyhive.utils.retry.time.sleep")
    @patch("honeyhive.api.client.httpx.Client")
    def test_export_returns_the_response_after_a_retry(
        self,
        mock_client_cls: Mock,
        mock_sleep: Mock,
        api_config: APIConfig,
    ) -> None:
        """A retried request that succeeds returns its events."""
        events_api = _events_api(api_config, max_retries=1)

        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = Mock(return_value=False)
        mock_client.request.side_effect = [_response(503), _response(200)]

        result = events_api.export(filters=[])

        assert len(result.events) == 1
        assert mock_client.request.call_count == 2
        mock_sleep.assert_called_once()
