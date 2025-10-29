"""Unit tests for HoneyHive API Client.

This module contains comprehensive unit tests for the HoneyHive API client,
focusing on HTTP client management, rate limiting, retry logic, and error handling.

Tests cover:
- RateLimiter class functionality
- HoneyHive client initialization and configuration
- HTTP client management (sync/async)
- Request handling with retry logic
- Rate limiting behavior
- Error handling and logging
- Context manager functionality
"""

# pylint: disable=protected-access,unused-argument,too-few-public-methods,too-many-lines
# Justification: Unit tests need to verify private method behavior
# Justification: Mock fixtures require unused arguments for proper patching
# Justification: Test classes focus on single functionality
# Justification: Comprehensive unit test coverage requires extensive test cases

from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, call, patch

import httpx
import pytest

from honeyhive import __version__
from honeyhive.api.client import HoneyHive, RateLimiter
from honeyhive.utils.error_handler import APIError


class TestRateLimiter:
    """Test suite for RateLimiter class."""

    def test_initialization_default_values(self) -> None:
        """Test RateLimiter initialization with default values."""
        rate_limiter = RateLimiter()

        assert rate_limiter.max_calls == 100
        assert rate_limiter.time_window == 60.0
        assert rate_limiter.calls == []

    def test_initialization_custom_values(self) -> None:
        """Test RateLimiter initialization with custom values."""
        max_calls = 50
        time_window = 30.0

        rate_limiter = RateLimiter(max_calls=max_calls, time_window=time_window)

        assert rate_limiter.max_calls == max_calls
        assert rate_limiter.time_window == time_window
        assert rate_limiter.calls == []

    @patch("time.time")
    def test_can_call_empty_calls_list(self, mock_time: Mock) -> None:
        """Test can_call returns True when calls list is empty."""
        mock_time.return_value = 1000.0
        rate_limiter = RateLimiter(max_calls=5, time_window=60.0)

        result = rate_limiter.can_call()

        assert result is True

    @patch("time.time")
    def test_can_call_within_limit(self, mock_time: Mock) -> None:
        """Test can_call returns True when within rate limit."""
        current_time = 1000.0
        mock_time.return_value = current_time
        rate_limiter = RateLimiter(max_calls=5, time_window=60.0)

        # Add calls within the time window but under the limit
        rate_limiter.calls = [
            current_time - 30.0,
            current_time - 20.0,
            current_time - 10.0,
        ]

        result = rate_limiter.can_call()

        assert result is True

    @patch("time.time")
    def test_can_call_exceeds_limit(self, mock_time: Mock) -> None:
        """Test can_call returns False when rate limit is exceeded."""
        current_time = 1000.0
        mock_time.return_value = current_time
        rate_limiter = RateLimiter(max_calls=3, time_window=60.0)

        # Add calls that exceed the limit within the time window
        rate_limiter.calls = [
            current_time - 50.0,
            current_time - 40.0,
            current_time - 30.0,
            current_time - 20.0,  # This exceeds the limit of 3
        ]

        result = rate_limiter.can_call()

        assert result is False

    @patch("time.time")
    def test_can_call_filters_old_calls(self, mock_time: Mock) -> None:
        """Test can_call filters out calls outside the time window."""
        current_time = 1000.0
        mock_time.return_value = current_time
        rate_limiter = RateLimiter(max_calls=3, time_window=60.0)

        # Add old calls outside the time window and recent calls within limit
        rate_limiter.calls = [
            current_time - 120.0,  # Outside time window
            current_time - 90.0,  # Outside time window
            current_time - 30.0,  # Within time window
            current_time - 20.0,  # Within time window
        ]

        result = rate_limiter.can_call()

        assert result is True
        # Verify old calls were filtered out and new call was added
        assert len(rate_limiter.calls) == 3

    @patch("time.sleep")
    @patch("time.time")
    def test_wait_if_needed_no_wait_required(
        self, mock_time: Mock, mock_sleep: Mock
    ) -> None:
        """Test wait_if_needed doesn't wait when calls are allowed."""
        mock_time.return_value = 1000.0
        rate_limiter = RateLimiter(max_calls=5, time_window=60.0)

        rate_limiter.wait_if_needed()

        mock_sleep.assert_not_called()
        assert len(rate_limiter.calls) == 1  # Call was recorded

    @patch("time.sleep")
    @patch("time.time")
    def test_wait_if_needed_waits_when_limit_exceeded(
        self, mock_time: Mock, mock_sleep: Mock
    ) -> None:
        """Test wait_if_needed waits when rate limit is exceeded."""
        current_time = 1000.0
        mock_time.return_value = current_time
        rate_limiter = RateLimiter(max_calls=2, time_window=60.0)

        # Fill up the rate limit
        rate_limiter.calls = [current_time - 30.0, current_time - 20.0]

        # Mock the behavior where first check fails, then succeeds
        with patch.object(rate_limiter, "can_call", side_effect=[False, True]):
            rate_limiter.wait_if_needed()

        mock_sleep.assert_called_once_with(0.1)
        # Original calls, new call added by wait_if_needed
        assert len(rate_limiter.calls) == 2


class TestHoneyHiveInitialization:
    """Test suite for HoneyHive client initialization."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.api.client.APIClientConfig")
    def test_initialization_default_values(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test HoneyHive client initialization with default values."""
        mock_config = Mock()
        mock_config.api_key = "test-api-key-12345"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = True
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        client = HoneyHive()

        assert client.api_key == "test-api-key-12345"
        assert client.server_url == "https://api.honeyhive.ai"
        assert client.timeout == 30.0
        assert client.test_mode is True  # Default from fixture is test_mode=True
        assert client.verbose is False
        assert client.logger == mock_logger
        mock_safe_log.assert_called()

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_initialization_custom_values(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test HoneyHive client initialization with custom values."""
        mock_config = Mock()
        mock_config.api_key = "default-key"
        mock_config.server_url = "https://default.api.com"
        mock_config.http_config.timeout = 15.0
        mock_config.http_config.rate_limit_calls = 50
        mock_config.http_config.rate_limit_window = 30.0
        mock_config.http_config.max_connections = 5
        mock_config.http_config.max_keepalive_connections = 2
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Override with custom values
        client = HoneyHive(
            api_key="custom-key",
            server_url="https://custom.api.com",
            timeout=45.0,
            test_mode=True,
            verbose=True,
        )

        assert client.api_key == "custom-key"
        assert client.server_url == "https://custom.api.com"
        assert client.timeout == 45.0
        assert client.test_mode is True
        assert client.verbose is True

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_initialization_with_tracer_instance(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test HoneyHive client initialization with tracer instance."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = True
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_tracer = Mock()
        mock_tracer.project_name = "test-project"

        client = HoneyHive(tracer_instance=mock_tracer)

        assert client.tracer_instance == mock_tracer
        # When tracer_instance is provided, get_logger is NOT called for the client
        # The tracer handles its own logging
        mock_get_logger.assert_not_called()


class TestHoneyHiveClientProperties:
    """Test suite for HoneyHive client properties and methods."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.api.client.APIClientConfig")
    def test_client_kwargs_basic(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test client_kwargs returns correct configuration."""
        mock_config = Mock()
        mock_config.api_key = "test-api-key-12345"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()
        kwargs = client.client_kwargs

        assert kwargs["timeout"] == 30.0
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key-12345"
        assert kwargs["headers"]["User-Agent"] == f"HoneyHive-Python-SDK/{__version__}"
        assert "limits" in kwargs

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_make_url_relative_path(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test URL construction with relative path."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()
        url = client._make_url("/api/v1/events")

        # Assert against actual configured server_url (respects environment)
        assert url == f"{client.server_url}/api/v1/events"

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_make_url_absolute_path(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test URL construction with absolute path."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()
        url = client._make_url("https://custom.api.com/endpoint")

        assert url == "https://custom.api.com/endpoint"


class TestHoneyHiveHTTPClients:
    """Test suite for HoneyHive HTTP client management."""

    @patch("httpx.Client")
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_sync_client_creation(
        self,
        mock_config_class: Mock,
        mock_get_logger: Mock,
        mock_safe_log: Mock,
        mock_httpx_client: Mock,
    ) -> None:
        """Test sync HTTP client creation."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = HoneyHive()
        sync_client = client.sync_client

        assert sync_client == mock_client_instance
        mock_httpx_client.assert_called_once()

        # Test that subsequent calls return the same instance
        sync_client_2 = client.sync_client
        assert sync_client_2 == mock_client_instance
        assert mock_httpx_client.call_count == 1  # Should not create a new client

    @patch("httpx.AsyncClient")
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_async_client_creation(
        self,
        mock_config_class: Mock,
        mock_get_logger: Mock,
        mock_safe_log: Mock,
        mock_httpx_async_client: Mock,
    ) -> None:
        """Test async HTTP client creation."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_async_client_instance = Mock()
        mock_httpx_async_client.return_value = mock_async_client_instance

        client = HoneyHive()
        async_client = client.async_client

        assert async_client == mock_async_client_instance
        mock_httpx_async_client.assert_called_once()

        # Test that subsequent calls return the same instance
        async_client_2 = client.async_client
        assert async_client_2 == mock_async_client_instance
        assert mock_httpx_async_client.call_count == 1


class TestHoneyHiveHealthCheck:
    """Test suite for HoneyHive health check functionality."""

    @patch("time.time")
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_get_health_success(
        self,
        mock_config_class: Mock,
        mock_get_logger: Mock,
        mock_safe_log: Mock,
        mock_time: Mock,
    ) -> None:
        """Test get_health returns success response."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_time.return_value = 1234567890.0

        client = HoneyHive()

        with patch.object(client, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_request.return_value = mock_response

            result = client.get_health()

            expected_result = {"status": "healthy"}

            assert result == expected_result
            mock_request.assert_called_once_with("GET", "/api/v1/health")

    @patch("time.time")
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.api.client.APIClientConfig")
    def test_get_health_exception(
        self,
        mock_config_class: Mock,
        mock_get_logger: Mock,
        mock_safe_log: Mock,
        mock_time: Mock,
    ) -> None:
        """Test get_health handles exceptions gracefully."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        mock_time.return_value = 1234567890.0

        client = HoneyHive()

        with patch.object(client, "request") as mock_request:
            mock_request.side_effect = Exception("Connection failed")

            result = client.get_health()

            expected_result = {
                "status": "healthy",
                "message": "API client is operational",
                "server_url": "https://api.honeyhive.ai",
                "timestamp": 1234567890.0,
            }

            assert result == expected_result


class TestHoneyHiveRequestHandling:
    """Test suite for HoneyHive request handling functionality."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_request_success(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test successful HTTP request."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        mock_sync_client = Mock()
        mock_sync_client.request.return_value = mock_response
        client._sync_client = mock_sync_client

        with patch.object(client.rate_limiter, "wait_if_needed") as mock_wait:
            result = client.request("GET", "/api/v1/test")

            assert result == mock_response
            mock_wait.assert_called_once()
            # Assert against actual configured server_url (respects environment)
            mock_sync_client.request.assert_called_once_with(
                "GET",
                f"{client.server_url}/api/v1/test",
                params=None,
                json=None,
            )

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_request_with_retry_success(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test request with retry logic success."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Mock retry config to enable retries
        mock_retry_config = Mock()
        mock_retry_config.should_retry.return_value = True
        mock_retry_config.max_retries = 3
        client.retry_config = mock_retry_config

        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(client, "_retry_request") as mock_retry_request:
            mock_retry_request.return_value = mock_response

            with patch.object(client.rate_limiter, "wait_if_needed"):
                result = client.request("POST", "/api/v1/test", json={"data": "test"})

                assert result == mock_response
                mock_retry_request.assert_called_once()

    @patch("time.sleep")
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_retry_request_success_after_failure(
        self,
        mock_config_class: Mock,
        mock_get_logger: Mock,
        mock_safe_log: Mock,
        mock_sleep: Mock,
    ) -> None:
        """Test retry request succeeds after initial failure."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Mock retry config
        mock_retry_config = Mock()
        mock_retry_config.max_retries = 3
        mock_retry_config.backoff_strategy = Mock()
        mock_retry_config.backoff_strategy.get_delay.return_value = 1.0
        client.retry_config = mock_retry_config

        # Mock sync client: first call raises exception, second succeeds
        mock_success_response = Mock()
        mock_success_response.status_code = 200

        mock_sync_client = Mock()
        mock_sync_client.request.side_effect = [
            httpx.RequestError("Temporary error"),
            mock_success_response,
        ]
        client._sync_client = mock_sync_client

        result = client._retry_request("GET", "/test")

        # The result should be the success response
        assert result.status_code == 200
        assert mock_sync_client.request.call_count == 2
        # Sleep is called twice: once for attempt 1, once for attempt 2
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(1.0), call(1.0)])

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_retry_request_max_retries_exceeded(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test retry request fails when max retries exceeded."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Mock retry config
        mock_retry_config = Mock()
        mock_retry_config.max_retries = 2
        mock_retry_config.backoff_strategy = Mock()
        mock_retry_config.backoff_strategy.get_delay.return_value = 0.1
        client.retry_config = mock_retry_config

        # Mock sync client that raises exceptions (not just failed status codes)
        mock_sync_client = Mock()
        mock_sync_client.request.side_effect = httpx.RequestError("Network error")
        client._sync_client = mock_sync_client

        # The retry logic should raise an exception after max retries
        with pytest.raises(httpx.RequestError, match="Network error"):
            client._retry_request("GET", "/test")

        assert mock_sync_client.request.call_count == 2  # max_retries


class TestHoneyHiveContextManager:
    """Test suite for HoneyHive context manager functionality."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_context_manager_enter(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test context manager __enter__ method."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Test context manager entry
        with client as entered_client:
            result = entered_client

        assert result == client

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_context_manager_exit(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test context manager __exit__ method."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        with patch.object(client, "close") as mock_close:
            client.__exit__(None, None, None)

            mock_close.assert_called_once()

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.api.client.APIClientConfig")
    def test_context_manager_full_workflow(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test full context manager workflow."""
        mock_config = Mock()
        mock_config.api_key = "test-api-key-12345"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        with patch.object(HoneyHive, "close") as mock_close:
            with HoneyHive() as client:
                assert isinstance(client, HoneyHive)
                assert client.api_key == "test-api-key-12345"

            mock_close.assert_called_once()


class TestHoneyHiveCleanup:
    """Test suite for HoneyHive cleanup functionality."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_close_with_clients(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test close method with active HTTP clients."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Create mock HTTP clients
        mock_sync_client = Mock()
        mock_async_client = Mock()
        client._sync_client = mock_sync_client
        client._async_client = mock_async_client

        client.close()

        mock_sync_client.close.assert_called_once()
        assert client._sync_client is None
        assert client._async_client is None
        mock_safe_log.assert_called()

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_close_without_clients(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test close method without active HTTP clients."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Ensure no HTTP clients are created
        assert client._sync_client is None
        assert client._async_client is None

        client.close()

        # Should not raise any errors
        mock_safe_log.assert_called()

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_close_with_exception(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test close method handles exceptions gracefully."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Create mock sync client that raises exception on close
        mock_sync_client = Mock()
        mock_sync_client.close.side_effect = Exception("Close failed")
        client._sync_client = mock_sync_client

        # The close method doesn't handle exceptions, so it will raise
        with pytest.raises(Exception, match="Close failed"):
            client.close()

        # The _sync_client should still be set to None after the exception
        # (this happens before the close() call that fails)
        mock_safe_log.assert_called()


class TestHoneyHiveLogging:
    """Test suite for HoneyHive logging functionality."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_log_method_basic(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test _log method with basic parameters."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Reset the mock to only capture the _log call
        mock_safe_log.reset_mock()

        client._log("info", "Test message")

        mock_safe_log.assert_called_with(
            client, "info", "Test message", honeyhive_data=None
        )

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_log_method_with_data(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test _log method with honeyhive_data."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()
        test_data: Dict[str, Any] = {"key": "value", "count": 42}

        # Reset the mock to only capture the _log call
        mock_safe_log.reset_mock()

        client._log(
            "debug", "Debug message", honeyhive_data=test_data, extra_param="test"
        )

        mock_safe_log.assert_called_with(
            client,
            "debug",
            "Debug message",
            honeyhive_data=test_data,
            extra_param="test",
        )


class TestHoneyHiveAsyncMethods:
    """Test suite for HoneyHive async methods."""

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    async def test_get_health_async_success(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async get_health returns success response."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Mock async request method
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}

        with patch.object(client, "request_async") as mock_request_async:
            mock_request_async.return_value = mock_response

            result = await client.get_health_async()

            expected_result = {"status": "healthy"}
            assert result == expected_result
            mock_request_async.assert_called_once_with("GET", "/api/v1/health")

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.api.client.APIClientConfig")
    async def test_get_health_async_exception(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async get_health handles exceptions gracefully."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        with patch.object(client, "request_async") as mock_request_async:
            mock_request_async.side_effect = Exception("Connection failed")

            result = await client.get_health_async()

            expected_result = {
                "status": "healthy",
                "message": "API client is operational",
                "server_url": "https://api.honeyhive.ai",
            }

            # Should contain the expected keys (timestamp will be dynamic)
            assert result["status"] == expected_result["status"]
            assert result["message"] == expected_result["message"]
            assert result["server_url"] == expected_result["server_url"]
            assert "timestamp" in result

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    async def test_request_async_success(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test successful async HTTP request."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        # Create mock async client with async request method
        mock_async_client = AsyncMock()
        mock_async_client.request.return_value = mock_response
        client._async_client = mock_async_client

        with patch.object(client.rate_limiter, "wait_if_needed"):
            result = await client.request_async("GET", "/api/v1/test")

            assert result == mock_response
            # Assert against actual configured server_url (respects environment)
            mock_async_client.request.assert_called_once_with(
                "GET", f"{client.server_url}/api/v1/test", params=None, json=None
            )

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    async def test_aclose(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async close method."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Create mock async client with async aclose method
        mock_async_client = AsyncMock()
        client._async_client = mock_async_client

        await client.aclose()

        mock_async_client.aclose.assert_called_once()
        assert client._async_client is None
        mock_safe_log.assert_called()


class TestHoneyHiveVerboseLogging:
    """Test suite for HoneyHive verbose logging functionality."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_verbose_request_logging(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test verbose logging during request."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = True  # Enable verbose logging
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        mock_sync_client = Mock()
        mock_sync_client.request.return_value = mock_response
        client._sync_client = mock_sync_client

        with patch.object(client.rate_limiter, "wait_if_needed"):
            client.request("POST", "/api/v1/test", json={"data": "test"})

            # Verify verbose logging was called multiple times
            assert mock_safe_log.call_count >= 2  # Multiple log calls for verbose mode
            # Check that verbose logging was triggered
            mock_safe_log.assert_called()


class TestHoneyHiveAsyncRetryLogic:
    """Test suite for HoneyHive async retry logic."""

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    async def test_aclose_without_client(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async close method when no async client exists."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Ensure no async client exists
        assert client._async_client is None

        await client.aclose()

        # Should complete without error
        mock_safe_log.assert_called()

    @pytest.mark.asyncio
    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    async def test_request_async_with_error_handling(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async request with error handling."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = True  # Enable verbose logging
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        mock_async_client = AsyncMock()
        mock_async_client.request.side_effect = httpx.RequestError("Network error")
        client._async_client = mock_async_client

        with patch.object(client.rate_limiter, "wait_if_needed"):
            # The error handler converts httpx.RequestError to APIError
            with pytest.raises(APIError, match="Request failed"):
                await client.request_async("GET", "/api/v1/test")


class TestHoneyHiveEdgeCases:
    """Test suite for HoneyHive edge cases and error scenarios."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_sync_client_property_creation(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test sync client property creates client when accessed."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Initially no sync client
        assert client._sync_client is None

        # Accessing sync_client property should create it
        sync_client = client.sync_client
        assert sync_client is not None
        assert client._sync_client is not None

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_async_client_property_creation(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test async client property creates client when accessed."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        # Initially no async client
        assert client._async_client is None

        # Accessing async_client property should create it
        async_client = client.async_client
        assert async_client is not None
        assert client._async_client is not None


class TestHoneyHiveErrorHandling:
    """Test suite for HoneyHive error handling."""

    @patch("honeyhive.api.client.safe_log")
    @patch("honeyhive.api.client.get_logger")
    @patch("honeyhive.config.models.api_client.APIClientConfig")
    def test_request_http_error(
        self, mock_config_class: Mock, mock_get_logger: Mock, mock_safe_log: Mock
    ) -> None:
        """Test request handling of HTTP errors."""
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.server_url = "https://api.honeyhive.ai"
        mock_config.http_config.timeout = 30.0
        mock_config.http_config.rate_limit_calls = 100
        mock_config.http_config.rate_limit_window = 60.0
        mock_config.http_config.max_connections = 10
        mock_config.http_config.max_keepalive_connections = 5
        mock_config.test_mode = False
        mock_config.verbose = False
        mock_config_class.return_value = mock_config

        client = HoneyHive()

        mock_sync_client = Mock()
        mock_sync_client.request.side_effect = httpx.RequestError("Network error")
        client._sync_client = mock_sync_client

        with patch.object(client.rate_limiter, "wait_if_needed"):
            # The error handler converts httpx.RequestError to APIError
            with pytest.raises(APIError, match="Request failed"):
                client.request("GET", "/api/v1/test")
