"""Unit tests for HoneyHive OpenTelemetry tracer functionality."""

import json
import time
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanContext, SpanKind, Tracer
from opentelemetry.trace.span import TraceFlags

from honeyhive.tracer.otel_tracer import HoneyHiveTracer


class TestHoneyHiveTracer:
    """Test HoneyHiveTracer functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset the singleton before each test
        HoneyHiveTracer.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        # Reset the singleton after each test
        HoneyHiveTracer.reset()

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(api_key="test_key", project="test_project")
                assert tracer.api_key == "test_key"
                assert tracer.project == "test_project"
                assert tracer.source == "production"
                assert tracer.test_mode is False
                assert tracer.disable_http_tracing is True

    def test_init_test_mode(self) -> None:
        """Test initialization in test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = None
                mock_config.project = None

                tracer = HoneyHiveTracer(test_mode=True)
                assert tracer.test_mode is True
                assert tracer.api_key == "test-api-key"
                assert tracer.project == "default"

    def test_init_otel_not_available(self) -> None:
        """Test initialization when OpenTelemetry is not available."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", False):
            with pytest.raises(ImportError, match="OpenTelemetry is required"):
                HoneyHiveTracer()

    def test_init_no_api_key(self) -> None:
        """Test initialization without API key in non-test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = None
                mock_config.project = None

                with pytest.raises(ValueError, match="API key is required"):
                    HoneyHiveTracer(test_mode=False)

    def test_singleton_pattern(self) -> None:
        """Test singleton pattern implementation."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Reset instance
                HoneyHiveTracer.reset()

                tracer1 = HoneyHiveTracer(api_key="test_key", project="test_project")
                tracer2 = HoneyHiveTracer(
                    api_key="different_key", project="different_project"
                )

                # Should be the same instance
                assert tracer1 is tracer2
                assert tracer1.api_key == "test_key"  # First initialization values
                assert tracer1.project == "test_project"

    def test_reset_class_method(self) -> None:
        """Test reset class method."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Create instance
                tracer1 = HoneyHiveTracer(api_key="test_key", project="test_project")

                # Reset
                HoneyHiveTracer.reset()

                # Create new instance
                tracer2 = HoneyHiveTracer(api_key="new_key", project="new_project")

                # Should be different instances after reset
                assert tracer1 is not tracer2

    def test_http_tracing_disabled(self) -> None:
        """Test HTTP tracing disabled by default."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"

                    tracer = HoneyHiveTracer(api_key="test_key", project="test_project")

                    # Should set environment variable
                    assert mock_env["HH_DISABLE_HTTP_TRACING"] == "true"

    def test_http_tracing_enabled(self) -> None:
        """Test HTTP tracing enabled when specified."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"

                    tracer = HoneyHiveTracer(
                        api_key="test_key",
                        project="test_project",
                        disable_http_tracing=False,
                    )

                    # Should set environment variable
                    assert mock_env["HH_DISABLE_HTTP_TRACING"] == "false"

    def test_session_name_generation(self) -> None:
        """Test automatic session name generation."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(api_key="test_key", project="test_project")

                # Should generate session name based on the calling file name
                # The test file name is 'test_tracer_otel_tracer.py', so session name should be 'test_tracer_otel_tracer'
                assert tracer.session_name == "test_tracer_otel_tracer"

    def test_custom_session_name(self) -> None:
        """Test custom session name."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(
                    api_key="test_key",
                    project="test_project",
                    session_name="custom_session",
                )

                # Should use custom session name
                assert tracer.session_name == "custom_session"

    def test_instrumentors_integration(self) -> None:
        """Test instrumentors integration."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch.object(
                    HoneyHiveTracer, "_integrate_instrumentors"
                ) as mock_integrate:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"

                    instrumentors = ["test_instrumentor"]
                    tracer = HoneyHiveTracer(
                        api_key="test_key",
                        project="test_project",
                        instrumentors=instrumentors,
                    )

                    # Should call instrumentor integration
                    mock_integrate.assert_called_once_with(instrumentors)

    def test_initialization_flow(self) -> None:
        """Test complete initialization flow."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch.object(
                    HoneyHiveTracer, "_initialize_otel"
                ) as mock_init_otel:
                    with patch.object(
                        HoneyHiveTracer, "_initialize_session"
                    ) as mock_init_session:
                        with patch.object(
                            HoneyHiveTracer, "_setup_baggage_context"
                        ) as mock_setup_baggage:
                            mock_config.api_key = "test_key"
                            mock_config.project = "test_project"

                            tracer = HoneyHiveTracer(
                                api_key="test_key", project="test_project"
                            )

                            # Should call all initialization methods
                            mock_init_otel.assert_called_once()
                            mock_init_session.assert_called_once()
                            mock_setup_baggage.assert_called_once()

    def test_double_initialization(self) -> None:
        """Test that double initialization doesn't re-run setup."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch.object(
                    HoneyHiveTracer, "_initialize_otel"
                ) as mock_init_otel:
                    with patch.object(
                        HoneyHiveTracer, "_initialize_session"
                    ) as mock_init_session:
                        with patch.object(
                            HoneyHiveTracer, "_setup_baggage_context"
                        ) as mock_setup_baggage:
                            mock_config.api_key = "test_key"
                            mock_config.project = "test_project"

                            # First initialization
                            tracer1 = HoneyHiveTracer(
                                api_key="test_key", project="test_project"
                            )

                            # Second initialization on same instance
                            tracer2 = HoneyHiveTracer(
                                api_key="different_key", project="different_project"
                            )

                            # Should be same instance
                            assert tracer1 is tracer2

                            # Should only call initialization methods once
                            assert mock_init_otel.call_count == 1
                            assert mock_init_session.call_count == 1
                            assert mock_setup_baggage.call_count == 1

    def test_environment_variable_handling(self) -> None:
        """Test environment variable handling."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"

                    # Test with different disable_http_tracing values
                    test_cases = [
                        (True, "true"),
                        (False, "false"),
                        (None, "true"),  # Default value
                    ]

                    for disable_value, expected_env_value in test_cases:
                        HoneyHiveTracer.reset()
                        mock_env.clear()

                        if disable_value is None:
                            tracer = HoneyHiveTracer(
                                api_key="test_key", project="test_project"
                            )
                        else:
                            tracer = HoneyHiveTracer(
                                api_key="test_key",
                                project="test_project",
                                disable_http_tracing=disable_value,
                            )

                        assert mock_env["HH_DISABLE_HTTP_TRACING"] == expected_env_value

    def test_config_fallback_values(self) -> None:
        """Test config fallback values."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = None
                mock_config.project = None

                tracer = HoneyHiveTracer(test_mode=True)

                # Should use fallback values
                assert tracer.api_key == "test-api-key"
                assert tracer.project == "default"

    def test_source_parameter(self) -> None:
        """Test source parameter handling."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                test_sources = ["development", "staging", "production", "custom"]

                for source in test_sources:
                    HoneyHiveTracer.reset()

                    tracer = HoneyHiveTracer(
                        api_key="test_key", project="test_project", source=source
                    )

                    assert tracer.source == source

    def test_project_parameter_priority(self) -> None:
        """Test project parameter priority over config."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "config_project"

                tracer = HoneyHiveTracer(api_key="test_key", project="param_project")

                # Parameter should override config
                assert tracer.project == "param_project"

    def test_api_key_parameter_priority(self) -> None:
        """Test API key parameter priority over config."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "config_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(api_key="param_key", project="test_project")

                # Parameter should override config
                assert tracer.api_key == "param_key"

    def test_test_mode_api_key_handling(self) -> None:
        """Test API key handling in test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = None
                mock_config.project = None

                # Test mode with no API key
                tracer1 = HoneyHiveTracer(test_mode=True)
                assert tracer1.api_key == "test-api-key"

                # Test mode with custom API key
                HoneyHiveTracer.reset()
                tracer2 = HoneyHiveTracer(api_key="custom_test_key", test_mode=True)
                assert tracer2.api_key == "custom_test_key"

    def test_initialization_error_handling(self) -> None:
        """Test error handling during initialization."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = None  # No fallback API key
                mock_config.project = "test_project"

                # Test with invalid parameters
                with pytest.raises(ValueError):
                    HoneyHiveTracer(api_key="", project="test_project")

                with pytest.raises(ValueError):
                    HoneyHiveTracer(
                        api_key=None, project="test_project", test_mode=False
                    )

    def test_initialization_state_tracking(self) -> None:
        """Test initialization state tracking."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Reset to ensure clean state
                HoneyHiveTracer.reset()

                # Check initial state
                assert HoneyHiveTracer._instance is None
                assert HoneyHiveTracer._is_initialized is False

                # Initialize
                tracer = HoneyHiveTracer(api_key="test_key", project="test_project")

                # Check final state
                assert HoneyHiveTracer._instance is not None
                assert HoneyHiveTracer._is_initialized is True
                assert tracer._is_initialized is True

    def test_thread_safety(self) -> None:
        """Test thread safety of singleton pattern."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                import threading
                import time

                results = []

                def create_tracer(thread_id: int) -> None:
                    try:
                        tracer = HoneyHiveTracer(
                            api_key=f"key_{thread_id}", project=f"project_{thread_id}"
                        )
                        results.append((thread_id, tracer))
                    except Exception as e:
                        results.append((thread_id, e))

                # Reset instance
                HoneyHiveTracer.reset()

                # Create multiple threads
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=create_tracer, args=(i,))
                    threads.append(thread)
                    thread.start()

                # Wait for all threads
                for thread in threads:
                    thread.join()

                # All should have the same tracer instance
                tracers = [
                    result[1]
                    for result in results
                    if not isinstance(result[1], Exception)
                ]
                assert len(tracers) > 0

                first_tracer = tracers[0]
                for tracer in tracers:
                    assert tracer is first_tracer
