"""Tests for HTTP client configuration models."""

# pylint: disable=import-outside-toplevel,unused-import,reimported,redefined-outer-name
# Justification: Test isolation requires dynamic imports and mock redefinition

import os
from unittest.mock import patch

from honeyhive.config.models.http_client import HTTPClientConfig


class TestHTTPClientConfig:
    """Test HTTP client configuration model."""

    def test_http_client_config_initialization(self) -> None:
        """Test HTTP client config initialization with default values."""

        # Clear environment to test defaults
        with patch.dict(os.environ, {}, clear=True):
            config = HTTPClientConfig()
            assert config.timeout == 30.0
            assert config.max_connections == 10
            assert config.max_keepalive_connections == 20
            assert config.keepalive_expiry == 30.0
            assert config.pool_timeout == 10.0
            assert config.rate_limit_calls == 100
            assert config.rate_limit_window == 60.0
            assert config.max_retries == 3
            assert config.http_proxy is None
            assert config.https_proxy is None
            assert config.no_proxy is None
            assert config.verify_ssl is True
            assert config.follow_redirects is True

    def test_http_client_config_with_environment_variables(self) -> None:
        """Test HTTP client config with environment variables."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        env_vars = {
            "HH_TIMEOUT": "60.0",
            "HH_MAX_CONNECTIONS": "50",
            "HH_MAX_KEEPALIVE_CONNECTIONS": "100",
            "HH_KEEPALIVE_EXPIRY": "120.0",
            "HH_POOL_TIMEOUT": "20.0",
            "HH_RATE_LIMIT_CALLS": "200",
            "HH_RATE_LIMIT_WINDOW": "300.0",
            "HH_MAX_RETRIES": "5",
            "HH_HTTP_PROXY": "http://proxy.company.com:8080",
            "HH_HTTPS_PROXY": "https://proxy.company.com:8080",
            "HH_NO_PROXY": "localhost,127.0.0.1",
            "HH_VERIFY_SSL": "false",
            "HH_FOLLOW_REDIRECTS": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = HTTPClientConfig()
            assert config.timeout == 60.0
            assert config.max_connections == 50
            assert config.max_keepalive_connections == 100
            assert config.keepalive_expiry == 120.0
            assert config.pool_timeout == 20.0
            assert config.rate_limit_calls == 200
            assert config.rate_limit_window == 300.0
            assert config.max_retries == 5
            assert config.http_proxy == "http://proxy.company.com:8080"
            assert config.https_proxy == "https://proxy.company.com:8080"
            assert config.no_proxy == "localhost,127.0.0.1"
            assert config.verify_ssl is False
            assert config.follow_redirects is False

    def test_env_bool_true_values(self) -> None:
        """Test environment boolean parsing for true values (line 25)."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch.dict(os.environ, {"HH_VERIFY_SSL": "true"}, clear=True):
            config = HTTPClientConfig()
            assert config.verify_ssl is True

    def test_env_bool_false_values(self) -> None:
        """Test environment boolean parsing for false values (line 27)."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch.dict(os.environ, {"HH_VERIFY_SSL": "false"}, clear=True):
            config = HTTPClientConfig()
            assert config.verify_ssl is False

    def test_env_int_invalid_values(self) -> None:
        """Test environment int parsing for invalid values (lines 35-36)."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch.dict(os.environ, {"HH_MAX_CONNECTIONS": "invalid"}, clear=True):
            config = HTTPClientConfig()
            assert config.max_connections == 10  # Should fall back to default

    def test_env_float_invalid_values(self) -> None:
        """Test environment float parsing for invalid values (lines 43-44)."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch.dict(os.environ, {"HH_TIMEOUT": "invalid"}, clear=True):
            config = HTTPClientConfig()
            assert config.timeout == 30.0  # Should fall back to default

    def test_positive_float_validation_invalid_values(self) -> None:
        """Test positive float validation with invalid values (lines 239-245)."""
        import logging
        from unittest.mock import patch

        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch(
            "honeyhive.config.models.http_client.logging.getLogger"
        ) as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            # Test negative timeout
            config = HTTPClientConfig(timeout=-5.0)
            assert config.timeout == 30.0  # Default for invalid value
            mock_logger.warning.assert_called()

    def test_positive_float_validation_none_values(self) -> None:
        """Test positive float validation with None values."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        config = HTTPClientConfig(timeout=None)
        assert config.timeout == 30.0  # Default for None

    def test_positive_float_validation_invalid_types(self) -> None:
        """Test positive float validation with invalid types."""
        import logging
        from unittest.mock import patch

        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch(
            "honeyhive.config.models.http_client.logging.getLogger"
        ) as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            config = HTTPClientConfig(timeout="not-a-number")
            assert config.timeout == 30.0  # Default for invalid type
            mock_logger.warning.assert_called()

    def test_positive_int_validation_invalid_values(self) -> None:
        """Test positive int validation with invalid values (lines 271-277)."""
        import logging
        from unittest.mock import patch

        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch(
            "honeyhive.config.models.http_client.logging.getLogger"
        ) as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            # Test negative max_connections
            config = HTTPClientConfig(max_connections=-5)
            assert config.max_connections == 100  # Default for invalid value
            mock_logger.warning.assert_called()

    def test_positive_int_validation_none_values(self) -> None:
        """Test positive int validation with None values."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        config = HTTPClientConfig(max_connections=None)
        assert config.max_connections == 100  # Default for None

    def test_positive_int_validation_invalid_types(self) -> None:
        """Test positive int validation with invalid types."""
        import logging
        from unittest.mock import patch

        from honeyhive.config.models.http_client import HTTPClientConfig

        with patch(
            "honeyhive.config.models.http_client.logging.getLogger"
        ) as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            config = HTTPClientConfig(max_connections="not-a-number")
            assert config.max_connections == 100  # Default for invalid type
            mock_logger.warning.assert_called()

    def test_proxy_url_validation(self) -> None:
        """Test proxy URL validation with graceful degradation."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        # Test with invalid URL
        config = HTTPClientConfig(http_proxy="not-a-url")
        assert config.http_proxy is None  # Should gracefully degrade

        # Test with valid URL
        config_valid = HTTPClientConfig(http_proxy="http://proxy.company.com:8080")
        assert config_valid.http_proxy == "http://proxy.company.com:8080"

    def test_graceful_degradation_invalid_values(self) -> None:
        """Test graceful degradation with various invalid values."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        # Should not crash with invalid values
        config = HTTPClientConfig(
            timeout=-1.0,  # Invalid negative
            max_connections=0,  # Invalid zero
            keepalive_expiry=-5.0,  # Invalid negative
            max_retries=-1,  # Invalid negative
        )

        # Should use safe defaults
        assert config.timeout == 30.0  # Default
        assert config.max_connections == 100  # Default
        assert config.keepalive_expiry == 30.0  # Default
        assert config.max_retries == 100  # Default

    def test_fallback_environment_variables(self) -> None:
        """Test fallback to standard HTTP_* environment variables."""
        from honeyhive.config.models.http_client import HTTPClientConfig

        env_vars = {
            "HTTP_MAX_CONNECTIONS": "25",
            "HTTP_PROXY": "http://fallback.proxy.com:8080",
            "HTTPS_PROXY": "https://fallback.proxy.com:8080",
            "NO_PROXY": "fallback.local",
            "VERIFY_SSL": "false",
            "FOLLOW_REDIRECTS": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = HTTPClientConfig()
            assert config.max_connections == 25
            assert config.http_proxy == "http://fallback.proxy.com:8080"
            assert config.https_proxy == "https://fallback.proxy.com:8080"
            assert config.no_proxy == "fallback.local"
            assert config.verify_ssl is False
            assert config.follow_redirects is False
