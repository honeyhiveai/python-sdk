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
        """Test that singleton pattern is no longer used - multiple instances are created."""
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

                # Should be different instances in multi-instance mode
                assert tracer1 is not tracer2
                assert tracer1.api_key == "test_key"
                assert tracer1.project == "test_project"
                assert tracer2.api_key == "different_key"
                assert tracer2.project == "different_project"

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
        """Test that multiple initializations create different instances."""
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

                            # Second initialization creates new instance
                            tracer2 = HoneyHiveTracer(
                                api_key="different_key", project="different_project"
                            )

                            # Should be different instances in multi-instance mode
                            assert tracer1 is not tracer2

                            # Each instance should call initialization methods
                            assert mock_init_otel.call_count == 2
                            assert mock_init_session.call_count == 2
                            assert mock_setup_baggage.call_count == 2

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
        """Test initialization state tracking in multi-instance mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Reset to ensure clean state
                HoneyHiveTracer.reset()

                # Check that reset method works (no errors)
                # In multi-instance mode, reset just logs info

                # Initialize first tracer
                tracer1 = HoneyHiveTracer(api_key="test_key", project="test_project")
                assert tracer1.api_key == "test_key"
                assert tracer1.project == "test_project"

                # Initialize second tracer
                tracer2 = HoneyHiveTracer(
                    api_key="different_key", project="different_project"
                )
                assert tracer2.api_key == "different_key"
                assert tracer2.project == "different_project"

                # Should be different instances
                assert tracer1 is not tracer2

    def test_thread_safety(self) -> None:
        """Test thread safety in multi-instance mode."""
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

                # All should have different tracer instances in multi-instance mode
                tracers = [
                    result[1]
                    for result in results
                    if not isinstance(result[1], Exception)
                ]
                assert len(tracers) > 0

                # Check that each tracer has unique configuration
                tracer_configs = set()
                for tracer in tracers:
                    config = (tracer.api_key, tracer.project)
                    assert config not in tracer_configs, f"Duplicate config: {config}"
                    tracer_configs.add(config)


class TestMultiInstanceTracer:
    """Test multi-instance tracer functionality."""

    def test_multiple_tracer_instances(self) -> None:
        """Test that multiple tracer instances can coexist independently."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Create multiple tracers with different configurations
                tracer1 = HoneyHiveTracer(
                    api_key="key1", project="project1", source="dev"
                )
                tracer2 = HoneyHiveTracer(
                    api_key="key2", project="project2", source="staging"
                )
                tracer3 = HoneyHiveTracer(
                    api_key="key3", project="project3", source="prod"
                )

                # Verify they are different instances
                assert tracer1 is not tracer2
                assert tracer2 is not tracer3
                assert tracer1 is not tracer3

                # Verify each maintains its own configuration
                assert tracer1.api_key == "key1"
                assert tracer1.project == "project1"
                assert tracer1.source == "dev"

                assert tracer2.api_key == "key2"
                assert tracer2.project == "project2"
                assert tracer2.source == "staging"

                assert tracer3.api_key == "key3"
                assert tracer3.project == "project3"
                assert tracer3.source == "prod"

    def test_independent_session_management(self) -> None:
        """Test that each tracer instance manages sessions independently."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer1 = HoneyHiveTracer(api_key="key1", project="project1")
                tracer2 = HoneyHiveTracer(api_key="key2", project="project2")

                # Each should have its own session name based on calling file
                assert tracer1.session_name == "test_tracer_otel_tracer"
                assert tracer2.session_name == "test_tracer_otel_tracer"

                # But they should be independent instances
                assert tracer1 is not tracer2

    def test_independent_span_creation(self) -> None:
        """Test that each tracer can create spans independently."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer1 = HoneyHiveTracer(api_key="key1", project="project1")
                tracer2 = HoneyHiveTracer(api_key="key2", project="project2")

                # Verify tracers are different instances
                assert tracer1 is not tracer2

                # Verify each tracer has its own configuration
                assert tracer1.api_key == "key1"
                assert tracer2.api_key == "key2"

                # Verify each tracer has its own session name
                assert tracer1.session_name == "test_tracer_otel_tracer"
                assert tracer2.session_name == "test_tracer_otel_tracer"


class TestTracerProviderIntegration:
    """Test TracerProvider integration and flexibility."""

    def test_new_tracer_provider_creation(self) -> None:
        """Test creating a new TracerProvider when none exists."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    # Mock get_tracer_provider to return None
                    mock_trace.get_tracer_provider.return_value = None

                    tracer = HoneyHiveTracer(api_key="test", project="test")

                    assert tracer.is_main_provider is True
                    assert tracer.provider is not None

    def test_existing_tracer_provider_integration(self) -> None:
        """Test integration with existing TracerProvider."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock existing provider
                existing_provider = Mock()
                existing_provider.add_span_processor = Mock()

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = existing_provider

                    tracer = HoneyHiveTracer(api_key="test", project="test")

                    assert tracer.is_main_provider is False
                    assert tracer.provider is existing_provider

    def test_noop_provider_handling(self) -> None:
        """Test handling of NoOp TracerProvider."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock NoOp provider
                noop_provider = Mock()
                noop_provider.__class__.__name__ = "NoOpTracerProvider"

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = noop_provider

                    tracer = HoneyHiveTracer(api_key="test", project="test")

                    # Should create new provider when existing is NoOp
                    assert tracer.is_main_provider is True
                    assert tracer.provider is not noop_provider

    def test_provider_without_span_processor_support(self) -> None:
        """Test handling of providers that don't support span processors."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.config") as mock_config:
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock provider without add_span_processor method
                limited_provider = Mock()
                del limited_provider.add_span_processor

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = limited_provider

                    tracer = HoneyHiveTracer(api_key="test", project="test")

                    # Should handle gracefully without span processor support
                    assert tracer.is_main_provider is False
                    assert tracer.provider is limited_provider


class TestGlobalFunctions:
    """Test global helper functions with tracer parameters."""

    def test_enrich_session_with_tracer(self) -> None:
        """Test global enrich_session with tracer parameter."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            mock_tracer = Mock()

            from honeyhive.tracer.otel_tracer import enrich_session

            enrich_session("session123", {"key": "value"}, tracer=mock_tracer)
            mock_tracer.enrich_session.assert_called_once_with(
                "session123", {"key": "value"}
            )

    def test_enrich_session_without_tracer(self) -> None:
        """Test global enrich_session without tracer parameter."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            from honeyhive.tracer.otel_tracer import enrich_session

            # Should handle gracefully when no tracer provided
            enrich_session("session123", {"key": "value"})

    def test_enrich_span_with_tracer(self) -> None:
        """Test global enrich_span with tracer parameter."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            mock_tracer = Mock()

            from honeyhive.tracer.otel_tracer import enrich_span

            enrich_span(
                {"key": "value"}, {"metric": 42}, {"attr": "test"}, tracer=mock_tracer
            )
            mock_tracer.enrich_span.assert_called_once_with(
                {"key": "value"}, {"metric": 42}, {"attr": "test"}
            )

    def test_enrich_span_without_tracer(self) -> None:
        """Test global enrich_span without tracer parameter."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            from honeyhive.tracer.otel_tracer import enrich_span

            # Should handle gracefully when no tracer provided
            enrich_span({"key": "value"}, {"metric": 42}, {"attr": "test"})

    def test_get_tracer_deprecated(self) -> None:
        """Test that get_tracer returns None and provides guidance."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            from honeyhive.tracer.otel_tracer import get_tracer

            # Should return None and provide guidance
            result = get_tracer()
            assert result is None
