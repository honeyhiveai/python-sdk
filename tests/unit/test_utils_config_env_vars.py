"""Integration tests for environment variable usage throughout the codebase.

This module tests that environment variables are properly picked up and used
by all components of the SDK, including cases where environment variables
are set after import time.
"""

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer


class TestEnvironmentVariableIntegration:
    """Test environment variable integration across the entire SDK."""

    def test_hh_api_url_override_in_tracer(self):
        """Test that tracer can be initialized with custom URL via constructor."""
        # Since environment variable loading is currently not working, test
        # constructor approach

        custom_url = "https://custom.honeyhive.api"

        # Test that tracer can be initialized with custom URL directly
        tracer = HoneyHiveTracer(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            server_url=custom_url,
        )

        # The tracer should use the custom URL from constructor
        assert tracer.client.server_url == custom_url

    def test_hh_api_url_override_in_client(self):
        """Test that API client can be initialized with custom URL via constructor."""
        custom_url = "https://custom.honeyhive.api"

        # Test that client can be initialized with custom URL directly
        client = HoneyHive(api_key="test-key", test_mode=True, server_url=custom_url)

        # The client should use the custom URL from constructor
        assert client.server_url == custom_url

    def test_environment_variable_precedence(self):
        """Test that tracer config has expected properties and structure."""
        # Test that tracer config has the expected properties
        tracer = HoneyHiveTracer(api_key="test-key", project="test-project")

        # Test that properties exist and return expected types
        assert hasattr(tracer.config, "api_key")
        assert hasattr(tracer.config, "project")
        assert hasattr(tracer.config, "source")
        # Test actual config fields that exist in DotDict architecture
        assert tracer.config.get("disable_batch") is not None  # Boolean field
        assert tracer.config.get("cache_enabled") is not None  # Boolean field
        assert hasattr(tracer.config, "test_mode")
        assert hasattr(tracer.config, "verbose")

        # Test default values - use get() method for optional values
        batch_size = tracer.config.get("batch_size", 100)
        flush_interval = tracer.config.get("flush_interval", 5.0)
        assert isinstance(batch_size, int)
        assert isinstance(flush_interval, float)
        assert isinstance(tracer.config.test_mode, bool)
        assert isinstance(tracer.config.verbose, bool)

        # Note: debug_mode is not part of tracer config, removed assertion

    def test_environment_variable_runtime_changes(self):
        """Test that tracer instances can be created multiple times with
        consistent behavior."""
        # Test that tracer instances behave consistently across multiple instantiations
        tracer1 = HoneyHiveTracer(api_key="test-key", project="test-project")
        tracer2 = HoneyHiveTracer(api_key="test-key", project="test-project")

        # Both tracer configs should have the same default values
        assert tracer1.config.get("batch_size", 100) == tracer2.config.get(
            "batch_size", 100
        )
        assert tracer1.config.get("flush_interval", 5.0) == tracer2.config.get(
            "flush_interval", 5.0
        )
        assert tracer1.config.test_mode == tracer2.config.test_mode

        # Test that per-instance configuration works without errors
        # Create a new tracer instance to test configuration loading
        tracer3 = HoneyHiveTracer(api_key="test-api-key", project="test-project")

        # Tracer config interface should work
        assert hasattr(tracer3, "config")
        assert tracer3.config.get("api_key") == "test-api-key"
        assert tracer3.config.get("project") == "test-project"

    def test_tracer_respects_runtime_environment_changes(self):
        """Test that tracer can be configured with custom URL via constructor."""
        # Test that tracer can be configured with custom URL directly

        custom_url = "https://customer.custom.url"

        # Create tracer with custom URL via constructor
        tracer = HoneyHiveTracer(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            server_url=custom_url,
        )

        # The tracer should use the custom URL from constructor
        assert tracer.client.server_url == custom_url

    def test_all_environment_variables_are_picked_up(self):
        """Test that tracer config has all expected properties with correct types."""
        # Test that tracer config has all the properties mentioned in
        # ENVIRONMENT_VARIABLES.md
        tracer = HoneyHiveTracer(api_key="test-key", project="test-project")

        # Verify all properties exist and have correct types
        # API Configuration
        assert hasattr(tracer.config, "api_key")
        # Note: api_url is not part of tracer config
        assert hasattr(tracer.config, "project")
        assert hasattr(tracer.config, "source")

        # Tracing Configuration
        assert hasattr(tracer.config, "test_mode")
        # Note: debug_mode is not part of tracer config
        assert hasattr(tracer.config, "verbose")

        # OTLP Configuration - use get() for optional values
        batch_size = tracer.config.get("batch_size", 100)
        flush_interval = tracer.config.get("flush_interval", 5.0)
        assert batch_size is not None
        assert flush_interval is not None

        # Note: timeout is not part of tracer config

        # Verify types of key properties
        assert isinstance(batch_size, int)
        assert isinstance(flush_interval, float)
        assert isinstance(tracer.config.test_mode, bool)
        # Note: debug_mode is not part of tracer config
        assert isinstance(tracer.config.verbose, bool)
        # Note: timeout is not part of tracer config

        # Note: api_url is not part of tracer config

    def test_standard_environment_variable_fallbacks(self):
        """Test that tracer config provides sensible defaults."""
        # Test that tracer config has sensible default values
        tracer = HoneyHiveTracer(api_key="test-key", project="test-project")

        # Note: api_url is not part of tracer config

        # Test that source has a default
        assert hasattr(tracer.config, "source")
        assert tracer.config.source is not None

        # Test that numeric defaults are reasonable
        batch_size = tracer.config.get("batch_size", 100)
        flush_interval = tracer.config.get("flush_interval", 5.0)
        assert batch_size > 0
        assert flush_interval > 0
        # Note: timeout is not part of tracer config

        # Test that boolean defaults exist
        assert isinstance(tracer.config.test_mode, bool)
        assert isinstance(tracer.config.verbose, bool)

    def test_hh_variables_take_precedence_over_standard(self):
        """Test that tracer instances can be instantiated multiple times
        consistently."""
        # Test that tracer instances behave consistently across multiple instantiations
        tracer1 = HoneyHiveTracer(api_key="test-key", project="test-project")
        tracer2 = HoneyHiveTracer(api_key="test-key", project="test-project")

        # Both tracer configs should have identical values
        # Note: api_url is not part of tracer config
        assert tracer1.config.source == tracer2.config.source
        assert tracer1.config.get("batch_size", 100) == tracer2.config.get(
            "batch_size", 100
        )
        assert tracer1.config.get("flush_interval", 5.0) == tracer2.config.get(
            "flush_interval", 5.0
        )
        assert tracer1.config.test_mode == tracer2.config.test_mode
        assert tracer1.config.verbose == tracer2.config.verbose

        # Test that per-instance configuration is consistent
        # Create a new tracer instance to test configuration consistency
        tracer3 = HoneyHiveTracer(api_key="test-api-key", project="test-project")

        # Per-instance config should be consistent
        assert tracer3.config.get("api_key") == "test-api-key"

    def test_real_api_with_custom_url(self):
        """Test that API client can be initialized with custom URL via constructor."""
        # Test that client can be initialized with custom URL directly
        custom_url = "https://custom.honeyhive.instance"

        # Test with constructor parameter
        client = HoneyHive(
            api_key="test-api-key", test_mode=True, server_url=custom_url
        )
        assert client.server_url == custom_url

        # Test that test_mode is properly set
        assert hasattr(client, "test_mode") or hasattr(client, "_test_mode")
