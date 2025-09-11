"""Integration tests for environment variable usage throughout the codebase.

This module tests that environment variables are properly picked up and used
by all components of the SDK, including cases where environment variables
are set after import time.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.tracer.otel_tracer import HoneyHiveTracer
from honeyhive.utils.config import Config, reload_config


class TestEnvironmentVariableIntegration:
    """Test environment variable integration across the entire SDK."""

    def test_hh_api_url_override_in_tracer(self):
        """Test that HH_API_URL is properly used by the tracer when set after import."""
        # This test demonstrates the current issue where HH_API_URL set after import
        # is not picked up by the tracer

        custom_url = "https://custom.honeyhive.api"

        with patch.dict(os.environ, {"HH_API_URL": custom_url}, clear=False):
            # Reload config to pick up the new environment variable
            reload_config()

            # Create a tracer with test mode to avoid actual API calls
            tracer = HoneyHiveTracer(
                api_key="test-key", project="test-project", test_mode=True
            )

            # The tracer should use the custom URL from environment
            # Currently this may fail due to the config being loaded at import time
            assert tracer.client.base_url == custom_url

    def test_hh_api_url_override_in_client(self):
        """Test that HH_API_URL is properly used by the API client."""
        custom_url = "https://custom.honeyhive.api"

        with patch.dict(os.environ, {"HH_API_URL": custom_url}, clear=False):
            # Reload config to pick up the new environment variable
            reload_config()

            # Create a client
            client = HoneyHive(api_key="test-key", test_mode=True)

            # The client should use the custom URL from environment
            assert client.base_url == custom_url

    def test_environment_variable_precedence(self):
        """Test that environment variables have proper precedence over defaults."""
        env_vars = {
            "HH_API_KEY": "env-api-key",
            "HH_API_URL": "https://env.api.url",
            "HH_PROJECT": "env-project",
            "HH_SOURCE": "env-source",
            "HH_TIMEOUT": "45.0",
            "HH_MAX_RETRIES": "5",
            "HH_BATCH_SIZE": "200",
            "HH_FLUSH_INTERVAL": "2.5",
            "HH_MAX_CONNECTIONS": "25",
            "HH_TEST_MODE": "true",
            "HH_DEBUG_MODE": "true",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Reload config to pick up all environment variables
            reload_config()

            # Create config and verify all values are loaded
            config = Config()

            assert config.api_key == "env-api-key"
            assert config.api_url == "https://env.api.url"
            assert config.project == "env-project"
            assert config.source == "env-source"
            assert config.timeout == 45.0
            assert config.max_retries == 5
            assert config.batch_size == 200
            assert config.flush_interval == 2.5
            assert config.max_connections == 25
            assert config.test_mode is True
            assert config.debug_mode is True

    def test_environment_variable_runtime_changes(self):
        """Test that environment variables can be changed at runtime."""
        # Set initial values
        initial_env = {
            "HH_API_KEY": "initial-key",
            "HH_API_URL": "https://initial.api.url",
            "HH_PROJECT": "initial-project",
        }

        with patch.dict(os.environ, initial_env, clear=False):
            reload_config()
            config1 = Config()

            assert config1.api_key == "initial-key"
            assert config1.api_url == "https://initial.api.url"
            assert config1.project == "initial-project"

            # Change environment variables at runtime
            updated_env = {
                "HH_API_KEY": "updated-key",
                "HH_API_URL": "https://updated.api.url",
                "HH_PROJECT": "updated-project",
            }

            with patch.dict(os.environ, updated_env, clear=False):
                # Reload config to pick up changes
                reload_config()
                config2 = Config()

                assert config2.api_key == "updated-key"
                assert config2.api_url == "https://updated.api.url"
                assert config2.project == "updated-project"

    def test_tracer_respects_runtime_environment_changes(self):
        """Test that tracer respects environment variable changes at runtime."""
        # This is the key test that demonstrates the customer's issue

        # Start with default URL
        with patch.dict(os.environ, {}, clear=True):
            reload_config()

            # Set custom URL at runtime (after imports)
            os.environ["HH_API_URL"] = "https://customer.custom.url"
            os.environ["HH_API_KEY"] = "test-key"
            os.environ["HH_PROJECT"] = "test-project"

            # Reload config to pick up the runtime changes
            reload_config()

            # Create tracer - it should use the custom URL
            tracer = HoneyHiveTracer(test_mode=True)

            # This should pass - the tracer should use the custom URL
            assert tracer.client.base_url == "https://customer.custom.url"

    def test_all_environment_variables_are_picked_up(self):
        """Test that all documented environment variables are properly loaded."""
        # Test all HH_ prefixed environment variables from ENVIRONMENT_VARIABLES.md
        all_env_vars = {
            # API Configuration
            "HH_API_KEY": "test-api-key",
            "HH_API_URL": "https://test.api.url",
            "HH_PROJECT": "test-project",
            "HH_SOURCE": "test-source",
            # Tracing Configuration
            "HH_DISABLE_TRACING": "true",
            "HH_DISABLE_HTTP_TRACING": "true",
            "HH_TEST_MODE": "true",
            "HH_DEBUG_MODE": "true",
            # OTLP Configuration
            "HH_OTLP_ENABLED": "false",
            "HH_OTLP_ENDPOINT": "https://test.otlp.endpoint",
            "HH_OTLP_HEADERS": '{"test": "header"}',
            "HH_BATCH_SIZE": "150",
            "HH_FLUSH_INTERVAL": "3.0",
            # HTTP Client Configuration
            "HH_MAX_CONNECTIONS": "25",
            "HH_MAX_KEEPALIVE_CONNECTIONS": "35",
            "HH_KEEPALIVE_EXPIRY": "45.0",
            "HH_POOL_TIMEOUT": "15.0",
            "HH_RATE_LIMIT_CALLS": "200",
            "HH_RATE_LIMIT_WINDOW": "30.0",
            "HH_HTTP_PROXY": "http://test.proxy.com:8080",
            "HH_HTTPS_PROXY": "https://test.proxy.com:8443",
            "HH_NO_PROXY": "localhost,127.0.0.1",
            "HH_VERIFY_SSL": "false",
            "HH_FOLLOW_REDIRECTS": "false",
            # Experiment Configuration
            "HH_EXPERIMENT_ID": "test-exp-123",
            "HH_EXPERIMENT_NAME": "test-experiment",
            "HH_EXPERIMENT_VARIANT": "test-variant",
            "HH_EXPERIMENT_GROUP": "test-group",
            "HH_EXPERIMENT_METADATA": '{"test": "metadata"}',
            # SDK Configuration
            "HH_TIMEOUT": "45.0",
            "HH_MAX_RETRIES": "5",
        }

        with patch.dict(os.environ, all_env_vars, clear=False):
            reload_config()
            config = Config()

            # Verify all values are loaded correctly
            assert config.api_key == "test-api-key"
            assert config.api_url == "https://test.api.url"
            assert config.project == "test-project"
            assert config.source == "test-source"

            assert config.disable_tracing is True
            assert config.disable_http_tracing is True
            assert config.test_mode is True
            assert config.debug_mode is True

            assert config.otlp_enabled is False
            assert config.otlp_endpoint == "https://test.otlp.endpoint"
            assert config.otlp_headers == {"test": "header"}
            assert config.batch_size == 150
            assert config.flush_interval == 3.0

            assert config.max_connections == 25
            assert config.max_keepalive_connections == 35
            assert config.keepalive_expiry == 45.0
            assert config.pool_timeout == 15.0
            assert config.rate_limit_calls == 200
            assert config.rate_limit_window == 30.0
            assert config.http_proxy == "http://test.proxy.com:8080"
            assert config.https_proxy == "https://test.proxy.com:8443"
            assert config.no_proxy == "localhost,127.0.0.1"
            assert config.verify_ssl is False
            assert config.follow_redirects is False

            assert config.experiment_id == "test-exp-123"
            assert config.experiment_name == "test-experiment"
            assert config.experiment_variant == "test-variant"
            assert config.experiment_group == "test-group"
            assert config.experiment_metadata == {"test": "metadata"}

            assert config.timeout == 45.0
            assert config.max_retries == 5

    def test_standard_environment_variable_fallbacks(self):
        """Test that standard environment variables work as fallbacks."""
        # Test that standard environment variables are used when HH_ versions are not set
        standard_env_vars = {
            "API_URL": "https://standard.api.url",
            "SOURCE": "standard-source",
            "ENVIRONMENT": "standard-environment",
            "HTTP_PROXY": "http://standard.proxy.com:8080",
            "HTTPS_PROXY": "https://standard.proxy.com:8443",
            "NO_PROXY": "standard.localhost",
            "EXPERIMENT_ID": "standard-exp-123",
            "EXPERIMENT_NAME": "standard-experiment",
        }

        with patch.dict(os.environ, standard_env_vars, clear=True):
            reload_config()
            config = Config()

            # Verify standard variables are used as fallbacks
            assert config.api_url == "https://standard.api.url"
            assert (
                config.source == "standard-source"
            )  # SOURCE takes precedence over ENVIRONMENT
            assert config.http_proxy == "http://standard.proxy.com:8080"
            assert config.https_proxy == "https://standard.proxy.com:8443"
            assert config.no_proxy == "standard.localhost"
            assert config.experiment_id == "standard-exp-123"
            assert config.experiment_name == "standard-experiment"

    def test_hh_variables_take_precedence_over_standard(self):
        """Test that HH_ prefixed variables take precedence over standard ones."""
        mixed_env_vars = {
            # Both HH_ and standard versions
            "HH_API_URL": "https://hh.api.url",
            "API_URL": "https://standard.api.url",
            "HH_SOURCE": "hh-source",
            "SOURCE": "standard-source",
            "HH_HTTP_PROXY": "http://hh.proxy.com:8080",
            "HTTP_PROXY": "http://standard.proxy.com:8080",
            "HH_EXPERIMENT_ID": "hh-exp-123",
            "EXPERIMENT_ID": "standard-exp-123",
        }

        with patch.dict(os.environ, mixed_env_vars, clear=False):
            reload_config()
            config = Config()

            # Verify HH_ prefixed variables take precedence
            assert config.api_url == "https://hh.api.url"
            assert config.source == "hh-source"
            assert config.http_proxy == "http://hh.proxy.com:8080"
            assert config.experiment_id == "hh-exp-123"

    @pytest.mark.skipif(
        not os.getenv("HH_API_KEY"),
        reason="Requires HH_API_KEY environment variable for real API testing",
    )
    def test_real_api_with_custom_url(self):
        """Test that custom API URL works with real API calls (if API key is available)."""
        # This test only runs if HH_API_KEY is set in the environment
        # It tests the actual end-to-end flow with a custom URL

        # Note: This would need a real custom HoneyHive instance to test properly
        # For now, we'll just verify the URL is set correctly
        custom_url = "https://custom.honeyhive.instance"

        with patch.dict(os.environ, {"HH_API_URL": custom_url}, clear=False):
            reload_config()

            client = HoneyHive(api_key=os.getenv("HH_API_KEY"))
            assert client.base_url == custom_url
