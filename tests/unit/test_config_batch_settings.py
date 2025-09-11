"""
Unit tests for batch configuration in the Config class.

Tests the loading and validation of HH_BATCH_SIZE and HH_FLUSH_INTERVAL
environment variables without requiring full tracer initialization.
"""

import os
from unittest.mock import patch

import pytest

from honeyhive.utils.config import Config, OTLPConfig


class TestConfigBatchSettings:
    """Test batch configuration loading in Config and OTLPConfig classes."""

    def test_otlp_config_default_batch_settings(self):
        """Test that OTLPConfig has correct default batch settings."""
        with patch.dict(os.environ, {}, clear=False):
            # Clear batch-related env vars
            for var in ["HH_BATCH_SIZE", "HH_FLUSH_INTERVAL"]:
                os.environ.pop(var, None)

            otlp_config = OTLPConfig()

            assert (
                otlp_config.batch_size == 100
            ), f"Expected default batch_size=100, got {otlp_config.batch_size}"
            assert (
                otlp_config.flush_interval == 5.0
            ), f"Expected default flush_interval=5.0, got {otlp_config.flush_interval}"

    def test_otlp_config_loads_batch_settings_from_env(self):
        """Test that OTLPConfig loads batch settings from environment variables."""
        test_batch_size = 256
        test_flush_interval = 3.5

        with patch.dict(
            os.environ,
            {
                "HH_BATCH_SIZE": str(test_batch_size),
                "HH_FLUSH_INTERVAL": str(test_flush_interval),
            },
        ):
            otlp_config = OTLPConfig()

            assert otlp_config.batch_size == test_batch_size
            assert otlp_config.flush_interval == test_flush_interval

    def test_config_batch_property_accessors(self):
        """Test that Config class properly exposes batch settings through properties."""
        test_batch_size = 128
        test_flush_interval = 1.25

        with patch.dict(
            os.environ,
            {
                "HH_BATCH_SIZE": str(test_batch_size),
                "HH_FLUSH_INTERVAL": str(test_flush_interval),
            },
        ):
            config = Config()

            # Test property accessors
            assert config.batch_size == test_batch_size
            assert config.flush_interval == test_flush_interval

            # Verify they're accessing the OTLP config
            assert config.batch_size == config.otlp.batch_size
            assert config.flush_interval == config.otlp.flush_interval

    def test_config_batch_properties_with_no_otlp_config(self):
        """Test that Config batch properties return defaults when OTLP config is None."""
        config = Config()
        config.otlp = None  # Simulate missing OTLP config

        # Should return defaults
        assert config.batch_size == 100
        assert config.flush_interval == 5.0

    def test_batch_settings_type_validation(self):
        """Test that batch settings are properly converted to correct types."""
        with patch.dict(
            os.environ,
            {
                "HH_BATCH_SIZE": "512",  # String -> int
                "HH_FLUSH_INTERVAL": "2.75",  # String -> float
            },
        ):
            otlp_config = OTLPConfig()

            assert isinstance(otlp_config.batch_size, int)
            assert isinstance(otlp_config.flush_interval, float)
            assert otlp_config.batch_size == 512
            assert otlp_config.flush_interval == 2.75

    def test_invalid_batch_settings_fallback_to_defaults(self):
        """Test that invalid batch settings fall back to defaults."""
        with patch.dict(
            os.environ,
            {"HH_BATCH_SIZE": "not_a_number", "HH_FLUSH_INTERVAL": "invalid_float"},
        ):
            otlp_config = OTLPConfig()

            # Should fall back to defaults
            assert otlp_config.batch_size == 100
            assert otlp_config.flush_interval == 5.0

    @pytest.mark.parametrize(
        "batch_size_str,expected_batch_size",
        [
            ("1", 1),
            ("100", 100),
            ("1000", 1000),
            ("0", 0),  # Edge case: zero batch size
        ],
    )
    def test_batch_size_parsing(self, batch_size_str, expected_batch_size):
        """Test various batch size values are parsed correctly."""
        with patch.dict(os.environ, {"HH_BATCH_SIZE": batch_size_str}):
            otlp_config = OTLPConfig()
            assert otlp_config.batch_size == expected_batch_size

    @pytest.mark.parametrize(
        "flush_interval_str,expected_flush_interval",
        [
            ("0.1", 0.1),
            ("1.0", 1.0),
            ("5.5", 5.5),
            ("30.0", 30.0),
            ("0", 0.0),  # Edge case: zero flush interval
        ],
    )
    def test_flush_interval_parsing(self, flush_interval_str, expected_flush_interval):
        """Test various flush interval values are parsed correctly."""
        with patch.dict(os.environ, {"HH_FLUSH_INTERVAL": flush_interval_str}):
            otlp_config = OTLPConfig()
            assert otlp_config.flush_interval == expected_flush_interval

    def test_batch_settings_independent_of_other_otlp_settings(self):
        """Test that batch settings work independently of other OTLP configuration."""
        with patch.dict(
            os.environ,
            {
                "HH_BATCH_SIZE": "64",
                "HH_FLUSH_INTERVAL": "0.5",
                "HH_OTLP_ENABLED": "false",
                "HH_OTLP_ENDPOINT": "http://custom-endpoint:4318/v1/traces",
            },
        ):
            otlp_config = OTLPConfig()

            # Batch settings should be loaded regardless of other OTLP settings
            assert otlp_config.batch_size == 64
            assert otlp_config.flush_interval == 0.5

            # Other settings should also be loaded
            assert otlp_config.otlp_enabled is False
            assert otlp_config.otlp_endpoint == "http://custom-endpoint:4318/v1/traces"

    def test_batch_settings_in_config_reload(self):
        """Test that batch settings are reloaded when Config is recreated."""
        # Initial configuration
        with patch.dict(
            os.environ, {"HH_BATCH_SIZE": "200", "HH_FLUSH_INTERVAL": "2.0"}
        ):
            config1 = Config()
            assert config1.batch_size == 200
            assert config1.flush_interval == 2.0

        # Changed configuration
        with patch.dict(
            os.environ, {"HH_BATCH_SIZE": "400", "HH_FLUSH_INTERVAL": "4.0"}
        ):
            config2 = Config()
            assert config2.batch_size == 400
            assert config2.flush_interval == 4.0

    def test_batch_settings_documentation_compliance(self):
        """Test that our batch settings match the documented behavior."""
        # Test the specific values mentioned in the HoneyHive documentation

        # Default values should match documentation
        with patch.dict(os.environ, {}, clear=False):
            for var in ["HH_BATCH_SIZE", "HH_FLUSH_INTERVAL"]:
                os.environ.pop(var, None)

            config = Config()
            assert config.batch_size == 100  # Documented default
            assert config.flush_interval == 5.0  # Documented default

        # Custom values should override defaults
        with patch.dict(
            os.environ, {"HH_BATCH_SIZE": "150", "HH_FLUSH_INTERVAL": "1.5"}
        ):
            config = Config()
            assert config.batch_size == 150
            assert config.flush_interval == 1.5
