"""Unit tests for utility functions."""

import os
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer import HoneyHiveTracer


class TestHoneyHiveTracerInitCompatibility:
    """Test that HoneyHiveTracer.init method is fully compatible with constructor."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset the singleton for each test
        HoneyHiveTracer.reset()

    def test_init_method_has_all_constructor_parameters(self) -> None:
        """Test that init method supports all constructor parameters."""
        # Mock OpenTelemetry availability
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            # Mock the _initialize_session method to prevent it from running
            with patch.object(HoneyHiveTracer, "_initialize_session"):
                # Test that init method supports all constructor parameters
                tracer = HoneyHiveTracer.init(
                    api_key="test-key",
                    project="test-project",
                    source="test",
                    test_mode=True,  # New parameter
                    session_name="test-session",
                    instrumentors=[],  # New parameter
                    disable_http_tracing=True,
                )

                # Verify all parameters are properly set
                assert tracer.api_key == "test-key"
                assert tracer.project == "test-project"
                assert tracer.source == "test"
                assert tracer.test_mode is True
                assert tracer.session_name == "test-session"
                assert tracer.disable_http_tracing is True

    def test_init_method_with_server_url(self) -> None:
        """Test that init method properly handles server_url parameter."""
        # Mock OpenTelemetry availability
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            # Mock the _initialize_session method to prevent it from running
            with patch.object(HoneyHiveTracer, "_initialize_session"):
                # Test server_url parameter
                tracer = HoneyHiveTracer.init(
                    api_key="test-key",
                    project="test-project",
                    source="test",
                    server_url="https://custom-server.com",
                    test_mode=True,
                    instrumentors=[],
                    disable_http_tracing=True,
                )

                # Verify parameters are properly set
                assert tracer.api_key == "test-key"
                assert tracer.project == "test-project"
                assert tracer.source == "test"
                assert tracer.test_mode is True
                assert tracer.disable_http_tracing is True

    def test_init_method_defaults_match_constructor(self) -> None:
        """Test that init method defaults are compatible with constructor."""
        # Mock OpenTelemetry availability
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            # Mock the _initialize_session method to prevent it from running
            with patch.object(HoneyHiveTracer, "_initialize_session"):
                # Test with minimal parameters
                tracer = HoneyHiveTracer.init(
                    api_key="test-key",
                    project="test-project",
                )

                # Verify defaults are set correctly
                assert tracer.api_key == "test-key"
                assert tracer.project == "test-project"
                assert tracer.source == "dev"  # Default from init method
                assert tracer.test_mode is False  # Default from init method
                assert tracer.disable_http_tracing is True  # Default from init method
