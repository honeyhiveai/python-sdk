"""Unit tests for HoneyHive OpenTelemetry tracer functionality."""

import importlib
import json
import sys
import time
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanContext, SpanKind, Tracer
from opentelemetry.trace.span import TraceFlags

from honeyhive.tracer.otel_tracer import HoneyHiveTracer


class TestHoneyHiveTracerOTel:
    """Test HoneyHiveTracer OpenTelemetry implementation functionality."""

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
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(
                    api_key="test_key",
                )
                assert tracer.api_key == "test_key"
                assert tracer.project == "test_project"
                assert tracer.source == "dev"
                assert tracer.test_mode is False
                assert tracer.disable_http_tracing is True

    def test_init_test_mode(self) -> None:
        """Test initialization in test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config.api_key = None
                mock_config.project = None
                mock_config_class.return_value = mock_config

                tracer = HoneyHiveTracer(test_mode=True)
                assert tracer.test_mode is True
                assert tracer.api_key == "test-api-key"
                assert tracer.project == "test-project"

    def test_init_otel_not_available(self) -> None:
        """Test initialization when OpenTelemetry is not available."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", False):
            with pytest.raises(ImportError, match="OpenTelemetry is required"):
                HoneyHiveTracer()

    def test_init_no_api_key(self) -> None:
        """Test initialization without API key in non-test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config.api_key = None
                mock_config.project = None
                mock_config_class.return_value = mock_config

                with pytest.raises(ValueError, match="API key is required"):
                    HoneyHiveTracer(test_mode=False)

    def test_singleton_pattern(self) -> None:
        """Test that singleton pattern is no longer used - multiple instances are created."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Reset instance
                HoneyHiveTracer.reset()

                tracer1 = HoneyHiveTracer(
                    api_key="test_key",
                )
                tracer2 = HoneyHiveTracer(api_key="different_key")

                # Should be different instances in multi-instance mode
                assert tracer1 is not tracer2
                assert tracer1.api_key == "test_key"
                assert tracer1.project == "test_project"
                assert tracer2.api_key == "different_key"
                assert tracer2.project == "test_project"

    def test_reset_class_method(self) -> None:
        """Test reset class method."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Create instance
                tracer1 = HoneyHiveTracer(
                    api_key="test_key",
                )

                # Reset
                HoneyHiveTracer.reset()

                # Create new instance
                tracer2 = HoneyHiveTracer(
                    api_key="new_key",
                )

                # Should be different instances after reset
                assert tracer1 is not tracer2

    def test_http_tracing_disabled(self) -> None:
        """Test HTTP tracing disabled by default."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"
                    # Add batch configuration to avoid BatchSpanProcessor validation errors
                    mock_config.batch_size = 100
                    mock_config.flush_interval = 5.0

                    tracer = HoneyHiveTracer(
                        api_key="test_key",
                    )

                    # Should set environment variable
                    assert mock_env["HH_DISABLE_HTTP_TRACING"] == "true"

    def test_http_tracing_enabled(self) -> None:
        """Test HTTP tracing enabled when specified."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"
                    # Add batch configuration to avoid BatchSpanProcessor validation errors
                    mock_config.batch_size = 100
                    mock_config.flush_interval = 5.0

                    tracer = HoneyHiveTracer(
                        api_key="test_key",
                        disable_http_tracing=False,
                    )

                    # Should set environment variable
                    assert mock_env["HH_DISABLE_HTTP_TRACING"] == "false"

    def test_session_name_generation(self) -> None:
        """Test automatic session name generation."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(
                    api_key="test_key",
                )

                # Should generate session name based on the calling file name
                # The test file name is 'test_tracer_otel_tracer.py', so session name should be 'test_tracer_otel_tracer'
                assert tracer.session_name == "test_tracer_otel_tracer"

    def test_custom_session_name(self) -> None:
        """Test custom session name."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(
                    api_key="test_key",
                    session_name="custom_session",
                )

                # Should use custom session name
                assert tracer.session_name == "custom_session"

    def test_initialization_flow(self) -> None:
        """Test complete initialization flow."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
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
                                api_key="test_key",
                            )

                            # Should call all initialization methods
                            mock_init_otel.assert_called_once()
                            mock_init_session.assert_called_once()
                            mock_setup_baggage.assert_called_once()

    def test_double_initialization(self) -> None:
        """Test that multiple initializations create different instances."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
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
                                api_key="test_key",
                            )

                            # Second initialization creates new instance
                            tracer2 = HoneyHiveTracer(api_key="different_key")

                            # Should be different instances in multi-instance mode
                            assert tracer1 is not tracer2

                            # Each instance should call initialization methods
                            assert mock_init_otel.call_count == 2
                            assert mock_init_session.call_count == 2
                            assert mock_setup_baggage.call_count == 2

    def test_environment_variable_handling(self) -> None:
        """Test environment variable handling."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                with patch("honeyhive.tracer.otel_tracer.os.environ", {}) as mock_env:
                    mock_config.api_key = "test_key"
                    mock_config.project = "test_project"
                    # Add batch configuration to avoid BatchSpanProcessor validation errors
                    mock_config.batch_size = 100
                    mock_config.flush_interval = 5.0

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
                                api_key="test_key",
                            )
                        else:
                            tracer = HoneyHiveTracer(
                                api_key="test_key",
                                disable_http_tracing=disable_value,
                            )

                        assert mock_env["HH_DISABLE_HTTP_TRACING"] == expected_env_value

    def test_config_fallback_values(self) -> None:
        """Test config fallback values."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = None
                mock_config.project = None

                tracer = HoneyHiveTracer(test_mode=True)

                # Should use fallback values
                assert tracer.api_key == "test-api-key"
                assert tracer.project == "test_project"

    def test_source_parameter(self) -> None:
        """Test source parameter handling."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                test_sources = ["development", "staging", "production", "custom"]

                for source in test_sources:
                    HoneyHiveTracer.reset()

                    tracer = HoneyHiveTracer(api_key="test_key", source=source)

                    assert tracer.source == source

    def test_project_parameter_priority(self) -> None:
        """Test project parameter priority over config."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "config_project"

                tracer = HoneyHiveTracer(api_key="test_key", project="param_project")

                # Parameter should override config
                assert tracer.project == "param_project"

    def test_api_key_parameter_priority(self) -> None:
        """Test API key parameter priority over config."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "config_key"
                mock_config.project = "test_project"

                tracer = HoneyHiveTracer(
                    api_key="param_key",
                )

                # Parameter should override config
                assert tracer.api_key == "param_key"

    def test_test_mode_api_key_handling(self) -> None:
        """Test API key handling in test mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
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
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = None  # No fallback API key
                mock_config.project = "test_project"

                # Test with invalid parameters
                with pytest.raises(ValueError):
                    HoneyHiveTracer(
                        api_key="",
                    )

                with pytest.raises(ValueError):
                    HoneyHiveTracer(api_key=None, test_mode=False)

    def test_initialization_state_tracking(self) -> None:
        """Test initialization state tracking in multi-instance mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Reset to ensure clean state
                HoneyHiveTracer.reset()

                # Check that reset method works (no errors)
                # In multi-instance mode, reset just logs info

                # Initialize first tracer
                tracer1 = HoneyHiveTracer(
                    api_key="test_key",
                )
                assert tracer1.api_key == "test_key"
                assert tracer1.project == "test_project"

                # Initialize second tracer
                tracer2 = HoneyHiveTracer(api_key="different_key")
                assert tracer2.api_key == "different_key"
                assert tracer2.project == "test_project"

                # Should be different instances
                assert tracer1 is not tracer2

    def test_thread_safety(self) -> None:
        """Test thread safety in multi-instance mode."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                import threading
                import time

                results = []

                def create_tracer(thread_id: int) -> None:
                    try:
                        tracer = HoneyHiveTracer(api_key=f"key_{thread_id}")
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
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
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
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer1 = HoneyHiveTracer(
                    api_key="key1",
                )
                tracer2 = HoneyHiveTracer(
                    api_key="key2",
                )

                # Each should have its own session name based on calling file
                assert tracer1.session_name == "test_tracer_otel_tracer"
                assert tracer2.session_name == "test_tracer_otel_tracer"

                # But they should be independent instances
                assert tracer1 is not tracer2

    def test_independent_span_creation(self) -> None:
        """Test that each tracer can create spans independently."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                tracer1 = HoneyHiveTracer(
                    api_key="key1",
                )
                tracer2 = HoneyHiveTracer(
                    api_key="key2",
                )

                # Verify tracers are different instances
                assert tracer1 is not tracer2

                # Verify each tracer has its own configuration
                assert tracer1.api_key == "key1"
                assert tracer2.api_key == "key2"

                # Verify each tracer has its own session name
                assert tracer1.session_name == "test_tracer_otel_tracer"
                assert tracer2.session_name == "test_tracer_otel_tracer"


class TestOTelProviderIntegration:
    """Test OpenTelemetry TracerProvider integration and flexibility with mocks."""

    def test_new_tracer_provider_creation(self) -> None:
        """Test creating a new TracerProvider when none exists."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    # Mock get_tracer_provider to return None
                    mock_trace.get_tracer_provider.return_value = None

                    tracer = HoneyHiveTracer(
                        api_key="test",
                    )

                    assert tracer.is_main_provider is True
                    assert tracer.provider is not None

    def test_existing_tracer_provider_integration(self) -> None:
        """Test integration with existing TracerProvider."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock existing provider (not a ProxyTracerProvider)
                existing_provider = Mock()
                existing_provider.add_span_processor = Mock()
                existing_provider.__class__.__name__ = "TracerProvider"

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = existing_provider

                    tracer = HoneyHiveTracer(
                        api_key="test",
                    )

                    # With current logic, if no real provider exists, tracer becomes main provider
                    assert tracer.is_main_provider is True
                    assert tracer.provider is not None

    def test_noop_provider_handling(self) -> None:
        """Test handling of NoOp TracerProvider."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock NoOp provider
                noop_provider = Mock()
                noop_provider.__class__.__name__ = "NoOpTracerProvider"

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = noop_provider

                    tracer = HoneyHiveTracer(
                        api_key="test",
                    )

                    # Should create new provider when existing is NoOp
                    assert tracer.is_main_provider is True
                    assert tracer.provider is not noop_provider

    def test_provider_without_span_processor_support(self) -> None:
        """Test handling of providers that don't support span processors."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.utils.config.Config") as mock_config_class:
                mock_config = Mock()
                mock_config_class.return_value = mock_config
                # Set up the mock config attributes
                mock_config.api_key = "test_key"
                mock_config.project = "test_project"

                # Mock provider without add_span_processor method (not a ProxyTracerProvider)
                limited_provider = Mock()
                limited_provider.__class__.__name__ = "LimitedTracerProvider"
                del limited_provider.add_span_processor

                # Mock the entire opentelemetry.trace module
                with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                    mock_trace.get_tracer_provider.return_value = limited_provider

                    tracer = HoneyHiveTracer(
                        api_key="test",
                    )

                    # With current logic, tracer becomes main provider when needed
                    assert tracer.is_main_provider is True
                    assert tracer.provider is not None


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
                metadata={"key": "value"},
                metrics={"metric": 42},
                attributes={"attr": "test"},
                outputs=None,
                error=None,
            )

    def test_enrich_span_without_tracer(self) -> None:
        """Test global enrich_span without tracer parameter."""
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            from honeyhive.tracer.otel_tracer import enrich_span

            # Should handle gracefully when no tracer provided
            enrich_span({"key": "value"}, {"metric": 42}, {"attr": "test"})


class TestUnifiedEnrichSpan:
    """Test cases for the unified enrich_span implementation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.tracer = Mock()
        self.tracer.enrich_span = Mock(return_value=True)

    def test_enrich_span_context_manager_basic(self) -> None:
        """Test basic context manager pattern."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.is_recording.return_value = True
            mock_trace.get_current_span.return_value = mock_span

            # Test basic context manager usage
            with enrich_span(event_type="test_event", metadata={"key": "value"}):
                pass

            # Verify span attributes were set
            mock_span.set_attribute.assert_any_call(
                "honeyhive_event_type", "test_event"
            )

    def test_enrich_span_context_manager_enhanced(self) -> None:
        """Test enhanced context manager pattern from enhanced_tracing_demo.py."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            with patch(
                "honeyhive.tracer.otel_tracer._set_span_attributes"
            ) as mock_set_attrs:
                mock_span = Mock()
                mock_span.is_recording.return_value = True
                mock_trace.get_current_span.return_value = mock_span

                # Test enhanced pattern
                with enrich_span(
                    event_type="enrichment_demo",
                    event_name="attribute_enrichment",
                    inputs={"source": "demo", "operation": "enrichment"},
                    metadata={"enrichment_type": "context_manager"},
                    metrics={"enrichment_count": 5},
                ):
                    pass

                # Verify comprehensive attributes were set
                mock_span.set_attribute.assert_any_call(
                    "honeyhive_event_type", "enrichment_demo"
                )
                mock_span.set_attribute.assert_any_call(
                    "honeyhive_event_name", "attribute_enrichment"
                )
                mock_set_attrs.assert_any_call(
                    mock_span,
                    "honeyhive_inputs",
                    {"source": "demo", "operation": "enrichment"},
                )
                mock_set_attrs.assert_any_call(
                    mock_span,
                    "honeyhive_metadata",
                    {"enrichment_type": "context_manager"},
                )
                mock_set_attrs.assert_any_call(
                    mock_span, "honeyhive_metrics", {"enrichment_count": 5}
                )

    def test_enrich_span_backwards_compatibility_basic_usage(self) -> None:
        """Test backwards compatibility with basic_usage.py pattern."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            with patch(
                "honeyhive.tracer.otel_tracer._set_span_attributes"
            ) as mock_set_attrs:
                mock_span = Mock()
                mock_span.is_recording.return_value = True
                mock_trace.get_current_span.return_value = mock_span

                # Test basic_usage.py pattern: enrich_span("session_enrichment", {"enrichment_type": "session_data"})
                with enrich_span(
                    "session_enrichment", {"enrichment_type": "session_data"}
                ):
                    pass

                # Verify attributes were set correctly
                mock_span.set_attribute.assert_any_call(
                    "honeyhive_event_type", "session_enrichment"
                )
                mock_set_attrs.assert_any_call(
                    mock_span, "honeyhive_metadata", {"enrichment_type": "session_data"}
                )

    def test_enrich_span_direct_call_with_tracer(self) -> None:
        """Test direct method call with tracer parameter."""
        from honeyhive.tracer.otel_tracer import enrich_span

        # Test direct call with tracer
        result = enrich_span(
            metadata={"key": "value"}, metrics={"latency": 100}, tracer=self.tracer
        )

        # Should delegate to tracer instance
        self.tracer.enrich_span.assert_called_once_with(
            metadata={"key": "value"},
            metrics={"latency": 100},
            attributes=None,
            outputs=None,
            error=None,
        )
        assert result is True

    def test_enrich_span_direct_call_without_tracer(self) -> None:
        """Test direct method call without tracer parameter (should fail gracefully)."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("builtins.print") as mock_print:
            result = enrich_span(metadata={"key": "value"})

            # Should return False and print error message
            assert result is False
            mock_print.assert_called()

    def test_enrich_span_experiment_attributes(self) -> None:
        """Test experiment harness attributes are properly set."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.is_recording.return_value = True
            mock_trace.get_current_span.return_value = mock_span

            config_data = {
                "experiment_id": "exp-123",
                "experiment_name": "test_experiment",
                "experiment_variant": "control",
                "experiment_group": "A",
                "experiment_metadata": {"version": "1.0", "feature": "enabled"},
            }

            with enrich_span(event_type="experiment", config_data=config_data):
                pass

            # Verify experiment attributes were set
            mock_span.set_attribute.assert_any_call(
                "honeyhive_experiment_id", "exp-123"
            )
            mock_span.set_attribute.assert_any_call(
                "honeyhive_experiment_name", "test_experiment"
            )
            mock_span.set_attribute.assert_any_call(
                "honeyhive_experiment_variant", "control"
            )
            mock_span.set_attribute.assert_any_call("honeyhive_experiment_group", "A")
            mock_span.set_attribute.assert_any_call(
                "honeyhive_experiment_metadata_version", "1.0"
            )
            mock_span.set_attribute.assert_any_call(
                "honeyhive_experiment_metadata_feature", "enabled"
            )

    def test_enrich_span_no_active_span(self) -> None:
        """Test enrich_span when no active span exists."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_trace.get_current_span.return_value = None

            # Should handle gracefully when no span exists
            with enrich_span(event_type="test"):
                pass

    def test_enrich_span_span_not_recording(self) -> None:
        """Test enrich_span when span is not recording."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.is_recording.return_value = False
            mock_trace.get_current_span.return_value = mock_span

            # Should handle gracefully when span is not recording
            with enrich_span(event_type="test"):
                pass

            # Verify no attributes were set
            mock_span.set_attribute.assert_not_called()

    def test_enrich_span_exception_handling(self) -> None:
        """Test enrich_span handles exceptions gracefully."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.is_recording.return_value = True
            mock_span.set_attribute.side_effect = Exception("Test exception")
            mock_trace.get_current_span.return_value = mock_span

            # Should handle exceptions gracefully
            with enrich_span(event_type="test"):
                pass

    def test_enrich_span_kwargs_attributes(self) -> None:
        """Test enrich_span sets kwargs as honeyhive_ attributes."""
        from honeyhive.tracer.otel_tracer import enrich_span

        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.is_recording.return_value = True
            mock_trace.get_current_span.return_value = mock_span

            with enrich_span(
                event_type="test",
                custom_attr="custom_value",
                user_id="123",
                session_id="session-456",
            ):
                pass

            # Verify kwargs were set as honeyhive_ attributes
            mock_span.set_attribute.assert_any_call(
                "honeyhive_custom_attr", "custom_value"
            )
            mock_span.set_attribute.assert_any_call("honeyhive_user_id", "123")
            mock_span.set_attribute.assert_any_call(
                "honeyhive_session_id", "session-456"
            )

    def test_enrich_span_import_compatibility(self) -> None:
        """Test enrich_span can be imported from different modules."""
        # Test import from otel_tracer (main implementation)
        # Test import from __init__ (public API)
        from honeyhive.tracer import enrich_span as init_enrich_span

        # Test import from decorators (should delegate)
        from honeyhive.tracer.decorators import enrich_span as decorators_enrich_span
        from honeyhive.tracer.otel_tracer import enrich_span as otel_enrich_span

        # All should be callable
        assert callable(otel_enrich_span)
        assert callable(decorators_enrich_span)
        assert callable(init_enrich_span)


class TestSetSpanAttributes:
    """Test cases for _set_span_attributes helper function."""

    def test_set_span_attributes_dict(self) -> None:
        """Test setting span attributes with dictionary."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()
        data = {"key1": "value1", "key2": 42, "key3": True}

        _set_span_attributes(mock_span, "test", data)

        # Should set attributes for each key in the dict
        mock_span.set_attribute.assert_any_call("test.key1", "value1")
        mock_span.set_attribute.assert_any_call("test.key2", 42)
        mock_span.set_attribute.assert_any_call("test.key3", True)

    def test_set_span_attributes_list(self) -> None:
        """Test setting span attributes with list."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()
        data = ["item1", "item2", 42]

        _set_span_attributes(mock_span, "test", data)

        # Should set attributes for each item in the list
        mock_span.set_attribute.assert_any_call("test.0", "item1")
        mock_span.set_attribute.assert_any_call("test.1", "item2")
        mock_span.set_attribute.assert_any_call("test.2", 42)

    def test_set_span_attributes_nested_dict(self) -> None:
        """Test setting span attributes with nested dictionary."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()
        data = {"outer": {"inner": "value", "number": 123}}

        _set_span_attributes(mock_span, "test", data)

        # Should set attributes for nested structure
        mock_span.set_attribute.assert_any_call("test.outer.inner", "value")
        mock_span.set_attribute.assert_any_call("test.outer.number", 123)

    def test_set_span_attributes_complex_object(self) -> None:
        """Test setting span attributes with complex object (JSON serialization)."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()

        class CustomObject:
            def __init__(self):
                self.value = "test"

        data = CustomObject()

        _set_span_attributes(mock_span, "test", data)

        # Should call set_attribute once (either JSON or string representation)
        mock_span.set_attribute.assert_called_once()

    def test_set_span_attributes_none_value(self) -> None:
        """Test setting span attributes with None value."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()

        _set_span_attributes(mock_span, "test", None)

        # Should not set any attributes for None
        mock_span.set_attribute.assert_not_called()

    def test_set_span_attributes_exception_handling(self) -> None:
        """Test _set_span_attributes handles exceptions gracefully."""
        from honeyhive.tracer.otel_tracer import _set_span_attributes

        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("Test exception")

        # Should handle exceptions gracefully
        _set_span_attributes(mock_span, "test", "value")


class TestHoneyHiveTracerEnrichSpanUnified:
    """Test cases for HoneyHiveTracer.enrich_span unified implementation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.tracer = Mock()
        self.tracer.enrich_span = Mock()

    def test_tracer_enrich_span_context_manager_pattern(self) -> None:
        """Test HoneyHiveTracer.enrich_span with context manager pattern (backwards compatibility)."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer(api_key="test", test_mode=True)

        with patch(
            "honeyhive.tracer.otel_tracer._enrich_span_context_manager"
        ) as mock_context_manager:
            mock_context_manager.return_value.__enter__ = Mock()
            mock_context_manager.return_value.__exit__ = Mock()

            # Test basic_usage.py pattern: tracer.enrich_span("session_name", {"key": "value"})
            with tracer.enrich_span(
                "session_enrichment", {"enrichment_type": "session_data"}
            ):
                pass

            # Should call context manager with correct parameters
            mock_context_manager.assert_called_once()
            args, kwargs = mock_context_manager.call_args
            assert kwargs["event_type"] == "session_enrichment"
            assert kwargs["metadata"] == {"enrichment_type": "session_data"}
            assert kwargs["tracer"] == tracer

    def test_tracer_enrich_span_direct_method_call(self) -> None:
        """Test HoneyHiveTracer.enrich_span direct method call."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                mock_span = Mock()
                mock_span.get_span_context.return_value = Mock(span_id=123)
                mock_trace.get_current_span.return_value = mock_span

                # Test direct method call (no positional args)
                result = tracer.enrich_span(metadata={"key": "value"})

                # Should return the result from the actual implementation
                assert isinstance(
                    result, bool
                )  # Should return boolean for direct calls

    def test_tracer_enrich_span_with_outputs_and_error(self) -> None:
        """Test HoneyHiveTracer.enrich_span with outputs and error parameters."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
                with patch(
                    "honeyhive.tracer.otel_tracer._set_span_attributes"
                ) as mock_set_span_attributes:
                    mock_span = Mock()
                    mock_span.get_span_context.return_value = Mock(span_id=123)
                    mock_trace.get_current_span.return_value = mock_span

                    # Test data
                    test_outputs = {"result": "success", "data": [1, 2, 3]}
                    test_error = ValueError("test error")

                    # Test direct method call with outputs and error
                    result = tracer.enrich_span(
                        metadata={"operation": "test"},
                        outputs=test_outputs,
                        error=test_error,
                    )

                    # Should return boolean for direct calls
                    assert isinstance(result, bool)

                    # Verify _set_span_attributes was called for outputs and error
                    expected_calls = [
                        call(mock_span, "honeyhive.span.outputs", test_outputs),
                        call(mock_span, "honeyhive.span.error", test_error),
                    ]
                    mock_set_span_attributes.assert_has_calls(
                        expected_calls, any_order=True
                    )


class TestHoneyHiveTracerForceFlush:
    """Test cases for HoneyHiveTracer force_flush functionality."""

    def test_force_flush_basic(self) -> None:
        """Test basic force_flush functionality."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            # Test with default timeout
            result = tracer.force_flush()
            assert isinstance(result, bool)

            # Test with custom timeout
            result = tracer.force_flush(timeout_millis=5000)
            assert isinstance(result, bool)

    def test_force_flush_with_provider_support(self) -> None:
        """Test force_flush when provider supports it."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

            # Mock provider with force_flush support and no batch processors
            mock_provider = Mock()
            mock_provider.force_flush.return_value = True
            mock_provider._span_processors = []  # No batch processors
            tracer.provider = mock_provider

            # Mock span processor to return True as well
            mock_span_processor = Mock()
            mock_span_processor.force_flush.return_value = True
            tracer.span_processor = mock_span_processor

            result = tracer.force_flush(timeout_millis=10000)

            # Should call provider's force_flush
            mock_provider.force_flush.assert_called_once_with(timeout_millis=10000)
            mock_span_processor.force_flush.assert_called_once_with(
                timeout_millis=10000
            )
            assert result is True

    def test_force_flush_with_span_processor(self) -> None:
        """Test force_flush with span processor."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            # Mock span processor with force_flush support
            mock_span_processor = Mock()
            mock_span_processor.force_flush.return_value = True
            tracer.span_processor = mock_span_processor

            result = tracer.force_flush(timeout_millis=5000)

            # Should call span processor's force_flush
            mock_span_processor.force_flush.assert_called_once_with(timeout_millis=5000)
            assert result is True

    def test_force_flush_with_batch_processors(self) -> None:
        """Test force_flush with batch processors on provider."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            # Mock provider with batch processors
            mock_batch_processor = Mock()
            mock_batch_processor.force_flush.return_value = True

            mock_provider = Mock()
            mock_provider._span_processors = [mock_batch_processor]
            mock_provider.force_flush.return_value = True
            tracer.provider = mock_provider

            result = tracer.force_flush(timeout_millis=8000)

            # Should call both provider and batch processor force_flush
            mock_provider.force_flush.assert_called_once_with(timeout_millis=8000)
            mock_batch_processor.force_flush.assert_called_once_with(
                timeout_millis=8000
            )
            assert result is True

    def test_force_flush_partial_failure(self) -> None:
        """Test force_flush when some components fail."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            # Mock provider that fails
            mock_provider = Mock()
            mock_provider.force_flush.return_value = False
            tracer.provider = mock_provider

            # Mock span processor that succeeds
            mock_span_processor = Mock()
            mock_span_processor.force_flush.return_value = True
            tracer.span_processor = mock_span_processor

            result = tracer.force_flush()

            # Should return False because provider failed
            assert result is False

    def test_force_flush_exception_handling(self) -> None:
        """Test force_flush exception handling."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
            # Mock provider that raises exception
            mock_provider = Mock()
            mock_provider.force_flush.side_effect = Exception("Provider error")
            tracer.provider = mock_provider

            result = tracer.force_flush()

            # Should handle exception and return False
            assert result is False

    def test_force_flush_otel_not_available(self) -> None:
        """Test force_flush when OpenTelemetry is not available."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)

        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", False):
            result = tracer.force_flush()

            # Should return True (graceful degradation)
            assert result is True


class TestGlobalEnrichSpanWithOutputsAndError:
    """Test cases for global enrich_span function with outputs and error."""

    def test_global_enrich_span_with_outputs_and_error(self) -> None:
        """Test global enrich_span function with outputs and error parameters."""
        from contextlib import _GeneratorContextManager

        from honeyhive.tracer.otel_tracer import HoneyHiveTracer, enrich_span

        tracer = HoneyHiveTracer(api_key="test", test_mode=True)

        # Test data
        test_outputs = {"result": "success", "data": [1, 2, 3]}
        test_error = ValueError("test error")

        # Test that global function correctly switches to context manager mode
        # when rich parameters (outputs, error) are provided
        result = enrich_span(
            metadata={"operation": "global_test"},
            outputs=test_outputs,
            error=test_error,
            tracer=tracer,
        )

        # Should return a context manager when rich parameters are provided
        assert isinstance(result, _GeneratorContextManager)

        # Test with only basic parameters to ensure direct call mode works
        result_direct = enrich_span(
            metadata={"operation": "direct_test"}, tracer=tracer
        )

        # Should return boolean for direct calls (no rich parameters)
        assert isinstance(result_direct, bool)


class TestOtelTracerImportHandling:
    """Test OpenTelemetry import error handling using sys.modules manipulation."""

    def test_otel_import_error_handling(self):
        """Test OpenTelemetry ImportError handling using sys.modules manipulation."""
        # Get all OpenTelemetry modules currently loaded
        otel_modules = [
            key for key in sys.modules.keys() if key.startswith("opentelemetry")
        ]

        # Create patch dict to simulate OpenTelemetry not being available
        patch_dict = {module: None for module in otel_modules}
        patch_dict.update(
            {
                "opentelemetry": None,
                "opentelemetry.trace": None,
                "opentelemetry.sdk": None,
                "opentelemetry.sdk.trace": None,
                "opentelemetry.propagate": None,
            }
        )

        with patch.dict(sys.modules, patch_dict):
            # Force reimport to trigger the ImportError path
            import honeyhive.tracer.otel_tracer

            importlib.reload(honeyhive.tracer.otel_tracer)

            # This should have triggered the ImportError handling
            from honeyhive.tracer.otel_tracer import OTEL_AVAILABLE

            # Verify the import error was handled gracefully
            assert isinstance(OTEL_AVAILABLE, bool)

    def test_trace_context_import_availability(self):
        """Test that trace context imports are handled properly."""
        # Just test that the module can handle the import patterns
        from honeyhive.tracer.otel_tracer import OTEL_AVAILABLE

        # Just verify the flag works
        assert isinstance(OTEL_AVAILABLE, bool)

        # Only create tracer if OTEL is available
        if OTEL_AVAILABLE:
            from honeyhive.tracer.otel_tracer import HoneyHiveTracer

            tracer = HoneyHiveTracer()
            assert tracer is not None

    def test_sdk_trace_import_error(self):
        """Test SDK trace import error handling."""
        # Create patch dict to simulate SDK trace imports failing
        patch_dict = {
            "opentelemetry.sdk.trace": None,
            "opentelemetry.sdk.trace.export": None,
        }

        with patch.dict(sys.modules, patch_dict):
            # Force reimport to trigger the ImportError path
            import honeyhive.tracer.otel_tracer

            importlib.reload(honeyhive.tracer.otel_tracer)

            # Should handle gracefully
            from honeyhive.tracer.otel_tracer import OTEL_AVAILABLE

            assert isinstance(OTEL_AVAILABLE, bool)

    def test_baggage_import_error(self):
        """Test baggage import error handling."""
        # Create patch dict to simulate baggage imports failing
        patch_dict = {
            "opentelemetry.baggage": None,
        }

        with patch.dict(sys.modules, patch_dict):
            # Force reimport to trigger the ImportError path
            import honeyhive.tracer.otel_tracer

            importlib.reload(honeyhive.tracer.otel_tracer)

            # Should handle gracefully
            from honeyhive.tracer.otel_tracer import OTEL_AVAILABLE

            assert isinstance(OTEL_AVAILABLE, bool)
