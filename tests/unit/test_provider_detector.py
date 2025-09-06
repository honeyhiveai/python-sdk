"""Unit tests for provider detection system."""

from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.provider_detector import (
    IntegrationStrategy,
    ProviderDetector,
    ProviderType,
    detect_provider_integration_strategy,
    is_noop_or_proxy_provider,
)


class TestProviderDetector:
    """Test cases for ProviderDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ProviderDetector()

    def test_detect_noop_provider(self):
        """Test detection of NoOpTracerProvider."""
        # Mock NoOp provider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "NoOpTracerProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            provider_type = self.detector.detect_provider_type()
            assert provider_type == ProviderType.NOOP

    def test_detect_proxy_provider(self):
        """Test detection of ProxyTracerProvider."""
        # Mock Proxy provider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "ProxyTracerProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            provider_type = self.detector.detect_provider_type()
            assert provider_type == ProviderType.PROXY_TRACER_PROVIDER

    def test_detect_tracer_provider(self):
        """Test detection of real TracerProvider."""
        # Mock real TracerProvider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            provider_type = self.detector.detect_provider_type()
            assert provider_type == ProviderType.TRACER_PROVIDER

    def test_detect_custom_provider(self):
        """Test detection of custom provider."""
        # Mock custom provider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "CustomTracerProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            provider_type = self.detector.detect_provider_type()
            assert provider_type == ProviderType.CUSTOM

    def test_integration_strategy_main_provider_noop(self):
        """Test main provider strategy for NoOp provider."""
        strategy = self.detector.get_integration_strategy(ProviderType.NOOP)
        assert strategy == IntegrationStrategy.MAIN_PROVIDER

    def test_integration_strategy_main_provider_proxy(self):
        """Test main provider strategy for Proxy provider."""
        strategy = self.detector.get_integration_strategy(
            ProviderType.PROXY_TRACER_PROVIDER
        )
        assert strategy == IntegrationStrategy.MAIN_PROVIDER

    def test_integration_strategy_secondary_provider(self):
        """Test secondary provider strategy for real TracerProvider."""
        strategy = self.detector.get_integration_strategy(ProviderType.TRACER_PROVIDER)
        assert strategy == IntegrationStrategy.SECONDARY_PROVIDER

    def test_integration_strategy_console_fallback(self):
        """Test console fallback strategy for custom provider."""
        strategy = self.detector.get_integration_strategy(ProviderType.CUSTOM)
        assert strategy == IntegrationStrategy.CONSOLE_FALLBACK

    def test_can_add_span_processor_true(self):
        """Test span processor capability detection - positive case."""
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            can_add = self.detector.can_add_span_processor()
            assert can_add is True

    def test_can_add_span_processor_false(self):
        """Test span processor capability detection - negative case."""
        mock_provider = Mock(spec=[])  # No add_span_processor method

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            can_add = self.detector.can_add_span_processor()
            assert can_add is False

    def test_get_provider_info(self):
        """Test comprehensive provider information gathering."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"
        mock_provider.add_span_processor = Mock()

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            info = self.detector.get_provider_info()

            assert info["provider_instance"] == mock_provider
            assert info["provider_class_name"] == "TracerProvider"
            assert info["provider_type"] == ProviderType.TRACER_PROVIDER
            assert (
                info["integration_strategy"] == IntegrationStrategy.SECONDARY_PROVIDER
            )
            assert info["supports_span_processors"] is True
            assert info["is_replaceable"] is False

    def test_is_noop_provider_none(self):
        """Test NoOp detection with None provider."""
        assert self.detector._is_noop_provider(None) is True

    def test_is_noop_provider_noop_class(self):
        """Test NoOp detection with NoOp class name."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "NoOpTracerProvider"
        assert self.detector._is_noop_provider(mock_provider) is True

    def test_is_noop_provider_contains_noop(self):
        """Test NoOp detection with class name containing NoOp."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "SomeNoOpProvider"
        assert self.detector._is_noop_provider(mock_provider) is True

    def test_is_proxy_provider_proxy_class(self):
        """Test Proxy detection with Proxy class name."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "ProxyTracerProvider"
        assert self.detector._is_proxy_provider(mock_provider) is True

    def test_is_proxy_provider_contains_proxy(self):
        """Test Proxy detection with class name containing Proxy."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "SomeProxyProvider"
        assert self.detector._is_proxy_provider(mock_provider) is True

    def test_is_tracer_provider_real(self):
        """Test TracerProvider detection with real provider."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"
        assert self.detector._is_tracer_provider(mock_provider) is True

    def test_is_tracer_provider_excludes_proxy(self):
        """Test TracerProvider detection excludes Proxy variants."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "ProxyTracerProvider"
        assert self.detector._is_tracer_provider(mock_provider) is False

    def test_is_tracer_provider_excludes_noop(self):
        """Test TracerProvider detection excludes NoOp variants."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "NoOpTracerProvider"
        assert self.detector._is_tracer_provider(mock_provider) is False


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_detect_provider_integration_strategy(self):
        """Test convenience function for strategy detection."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            strategy = detect_provider_integration_strategy()
            assert strategy == IntegrationStrategy.SECONDARY_PROVIDER

    def test_is_noop_or_proxy_provider_noop(self):
        """Test convenience function for NoOp provider."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "NoOpTracerProvider"

        result = is_noop_or_proxy_provider(mock_provider)
        assert result is True

    def test_is_noop_or_proxy_provider_proxy(self):
        """Test convenience function for Proxy provider."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "ProxyTracerProvider"

        result = is_noop_or_proxy_provider(mock_provider)
        assert result is True

    def test_is_noop_or_proxy_provider_real(self):
        """Test convenience function for real provider."""
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"

        result = is_noop_or_proxy_provider(mock_provider)
        assert result is False

    @patch("honeyhive.tracer.provider_detector.OTEL_AVAILABLE", False)
    def test_detect_strategy_no_otel(self):
        """Test strategy detection when OpenTelemetry not available."""
        strategy = detect_provider_integration_strategy()
        assert strategy == IntegrationStrategy.CONSOLE_FALLBACK

    @patch("honeyhive.tracer.provider_detector.OTEL_AVAILABLE", False)
    def test_is_noop_or_proxy_no_otel(self):
        """Test provider check when OpenTelemetry not available."""
        result = is_noop_or_proxy_provider(Mock())
        assert result is True


class TestProviderDetectorInitialization:
    """Test cases for ProviderDetector initialization."""

    @patch("honeyhive.tracer.provider_detector.OTEL_AVAILABLE", False)
    def test_init_without_otel(self):
        """Test initialization fails without OpenTelemetry."""
        with pytest.raises(ImportError, match="OpenTelemetry is required"):
            ProviderDetector()

    def test_init_with_otel(self):
        """Test successful initialization with OpenTelemetry."""
        detector = ProviderDetector()
        assert detector is not None
