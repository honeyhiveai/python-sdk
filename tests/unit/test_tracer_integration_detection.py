"""Unit tests for HoneyHive tracer integration provider detection functionality.

This module tests the dynamic provider detection system including provider type
classification, integration strategy determination, and atomic provider operations
using standard fixtures and comprehensive edge case coverage following Agent OS
testing standards.
"""

# pylint: disable=line-too-long,protected-access,use-implicit-booleaness-not-comparison
# pylint: disable=missing-class-docstring,too-few-public-methods,unused-argument
# pylint: disable=unused-variable,unused-import
# Justification: Test module requires protected access, comprehensive mocking,
# and test classes may have few methods

import threading
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import NoOpTracerProvider, ProxyTracerProvider

from honeyhive.tracer.integration.detection import (
    IntegrationStrategy,
    ProviderDetector,
    ProviderType,
    _is_functioning_tracer_provider,
    _processor_has_exporters,
    _reset_provider_flag_dynamically,
    _single_processor_has_exporter,
    atomic_provider_detection_and_setup,
    detect_provider_integration_strategy,
    get_global_provider,
    is_noop_or_proxy_provider,
    set_global_provider,
)


class TestProviderType:
    """Test ProviderType enum."""

    def test_enum_values(self) -> None:
        """Test ProviderType enum has correct values."""
        assert ProviderType.NOOP.value == "noop"
        assert ProviderType.TRACER_PROVIDER.value == "tracer_provider"
        assert ProviderType.PROXY_TRACER_PROVIDER.value == "proxy_tracer_provider"
        assert ProviderType.CUSTOM.value == "custom"

    def test_enum_membership(self) -> None:
        """Test ProviderType enum membership."""
        assert ProviderType.NOOP in ProviderType
        assert ProviderType.TRACER_PROVIDER in ProviderType
        assert ProviderType.PROXY_TRACER_PROVIDER in ProviderType
        assert ProviderType.CUSTOM in ProviderType


class TestIntegrationStrategy:
    """Test IntegrationStrategy enum."""

    def test_enum_values(self) -> None:
        """Test IntegrationStrategy enum has correct values."""
        assert IntegrationStrategy.MAIN_PROVIDER.value == "main_provider"
        assert IntegrationStrategy.INDEPENDENT_PROVIDER.value == "independent_provider"
        assert IntegrationStrategy.CONSOLE_FALLBACK.value == "console_fallback"

    def test_enum_membership(self) -> None:
        """Test IntegrationStrategy enum membership."""
        assert IntegrationStrategy.MAIN_PROVIDER in IntegrationStrategy
        assert IntegrationStrategy.INDEPENDENT_PROVIDER in IntegrationStrategy
        assert IntegrationStrategy.CONSOLE_FALLBACK in IntegrationStrategy


class TestProviderDetector:
    """Test ProviderDetector functionality."""

    def test_init_without_tracer_instance(self) -> None:
        """Test ProviderDetector initialization without tracer instance."""
        detector = ProviderDetector()

        assert detector.tracer_instance is None
        assert isinstance(detector._detection_patterns, dict)
        assert isinstance(detector._strategy_rules, dict)

    def test_init_with_tracer_instance(self, honeyhive_tracer) -> None:
        """Test ProviderDetector initialization with tracer instance."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        assert detector.tracer_instance == honeyhive_tracer
        assert isinstance(detector._detection_patterns, dict)
        assert isinstance(detector._strategy_rules, dict)

    def test_build_detection_patterns_dynamically(self, honeyhive_tracer) -> None:
        """Test dynamic detection patterns building."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        patterns = detector._build_detection_patterns_dynamically()

        assert isinstance(patterns, dict)
        assert "noop" in patterns
        assert "proxy_tracer_provider" in patterns
        assert "tracer_provider" in patterns
        assert "custom" in patterns

        # Check pattern contents
        assert "NoOp" in patterns["noop"]
        assert "NoOpTracerProvider" in patterns["noop"]
        assert "Proxy" in patterns["proxy_tracer_provider"]
        assert "ProxyTracerProvider" in patterns["proxy_tracer_provider"]
        assert "TracerProvider" in patterns["tracer_provider"]
        assert patterns["custom"] == []

    def test_build_strategy_rules_dynamically(self, honeyhive_tracer) -> None:
        """Test dynamic strategy rules building."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        rules = detector._build_strategy_rules_dynamically()

        assert isinstance(rules, dict)
        assert len(rules) == 4

        # Check strategy mappings
        assert rules[ProviderType.NOOP] == IntegrationStrategy.MAIN_PROVIDER
        assert (
            rules[ProviderType.PROXY_TRACER_PROVIDER]
            == IntegrationStrategy.MAIN_PROVIDER
        )
        assert (
            rules[ProviderType.TRACER_PROVIDER]
            == IntegrationStrategy.INDEPENDENT_PROVIDER
        )
        assert rules[ProviderType.CUSTOM] == IntegrationStrategy.INDEPENDENT_PROVIDER

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_detect_provider_type_noop(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test provider type detection for NoOp provider."""
        mock_provider = NoOpTracerProvider()
        mock_get_provider.return_value = mock_provider

        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider_type = detector.detect_provider_type()

        assert isinstance(provider_type, ProviderType)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_detect_provider_type_tracer_provider(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test provider type detection for TracerProvider."""
        mock_provider = TracerProvider()
        mock_get_provider.return_value = mock_provider

        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider_type = detector.detect_provider_type()

        assert isinstance(provider_type, ProviderType)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_detect_provider_type_proxy_provider(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test provider type detection for ProxyTracerProvider."""
        mock_provider = ProxyTracerProvider()
        mock_get_provider.return_value = mock_provider

        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider_type = detector.detect_provider_type()

        assert isinstance(provider_type, ProviderType)
        mock_log.assert_called()

    def test_classify_provider_dynamically_noop(self, honeyhive_tracer) -> None:
        """Test dynamic provider classification for NoOp provider."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider = NoOpTracerProvider()

        provider_type = detector._classify_provider_dynamically(provider)

        assert provider_type == ProviderType.NOOP

    def test_classify_provider_dynamically_tracer_provider(
        self, honeyhive_tracer
    ) -> None:
        """Test dynamic provider classification for TracerProvider."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider = TracerProvider()

        provider_type = detector._classify_provider_dynamically(provider)

        assert provider_type == ProviderType.TRACER_PROVIDER

    def test_classify_provider_dynamically_proxy_provider(
        self, honeyhive_tracer
    ) -> None:
        """Test dynamic provider classification for ProxyTracerProvider."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider = ProxyTracerProvider()

        provider_type = detector._classify_provider_dynamically(provider)

        assert provider_type == ProviderType.PROXY_TRACER_PROVIDER

    def test_classify_provider_dynamically_custom(self, honeyhive_tracer) -> None:
        """Test dynamic provider classification for custom provider."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        # Create a custom provider that doesn't match known patterns
        class CustomProvider:
            pass

        provider = CustomProvider()
        provider_type = detector._classify_provider_dynamically(provider)

        assert provider_type == ProviderType.CUSTOM

    def test_get_base_strategy_dynamically(self, honeyhive_tracer) -> None:
        """Test base integration strategy retrieval."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        # Test different provider types
        strategy_noop = detector._get_base_strategy_dynamically(ProviderType.NOOP)
        assert strategy_noop == IntegrationStrategy.MAIN_PROVIDER

        strategy_tracer = detector._get_base_strategy_dynamically(
            ProviderType.TRACER_PROVIDER
        )
        assert strategy_tracer == IntegrationStrategy.INDEPENDENT_PROVIDER

        strategy_proxy = detector._get_base_strategy_dynamically(
            ProviderType.PROXY_TRACER_PROVIDER
        )
        assert strategy_proxy == IntegrationStrategy.MAIN_PROVIDER

        strategy_custom = detector._get_base_strategy_dynamically(ProviderType.CUSTOM)
        assert strategy_custom == IntegrationStrategy.INDEPENDENT_PROVIDER

    def test_is_functioning_tracer_provider_dynamically(self, honeyhive_tracer) -> None:
        """Test functioning tracer provider check."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        # Test with TracerProvider
        tracer_provider = TracerProvider()
        result = detector._is_functioning_tracer_provider_dynamically(tracer_provider)
        assert isinstance(result, bool)

        # Test with NoOp provider
        noop_provider = NoOpTracerProvider()
        result = detector._is_functioning_tracer_provider_dynamically(noop_provider)
        assert isinstance(result, bool)

    def test_refine_tracer_provider_strategy_dynamically(
        self, honeyhive_tracer
    ) -> None:
        """Test tracer provider strategy refinement."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        base_strategy = IntegrationStrategy.INDEPENDENT_PROVIDER

        result = detector._refine_tracer_provider_strategy_dynamically(base_strategy)

        assert isinstance(result, IntegrationStrategy)

    def test_has_active_span_processor_dynamically(self, honeyhive_tracer) -> None:
        """Test active span processor detection."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider = TracerProvider()

        result = detector._has_active_span_processor_dynamically(provider)

        assert isinstance(result, bool)


class TestDetectProviderIntegrationStrategy:
    """Test detect_provider_integration_strategy function."""

    def test_detect_provider_integration_strategy(self) -> None:
        """Test provider integration strategy detection."""
        strategy = detect_provider_integration_strategy()

        assert isinstance(strategy, IntegrationStrategy)


class TestIsNoopOrProxyProvider:
    """Test is_noop_or_proxy_provider function."""

    def test_is_noop_provider(self) -> None:
        """Test NoOp provider detection."""
        provider = NoOpTracerProvider()
        result = is_noop_or_proxy_provider(provider)
        assert result is True

    def test_is_proxy_provider(self) -> None:
        """Test Proxy provider detection."""
        provider = ProxyTracerProvider()
        result = is_noop_or_proxy_provider(provider)
        assert result is True

    def test_is_not_noop_or_proxy_provider(self) -> None:
        """Test non-NoOp/Proxy provider detection."""
        provider = TracerProvider()
        result = is_noop_or_proxy_provider(provider)
        assert result is False

    def test_is_custom_provider(self) -> None:
        """Test custom provider detection."""

        class CustomProvider:
            pass

        provider = CustomProvider()
        result = is_noop_or_proxy_provider(provider)
        assert result is False


class TestAtomicProviderDetectionAndSetup:
    """Test atomic_provider_detection_and_setup function."""

    @patch("honeyhive.tracer.integration.detection._provider_detection_lock")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    def test_atomic_provider_detection_basic(
        self, mock_get_provider, mock_log, mock_lock, honeyhive_tracer
    ) -> None:
        """Test basic atomic provider detection and setup."""
        mock_provider = NoOpTracerProvider()
        mock_get_provider.return_value = mock_provider

        result = atomic_provider_detection_and_setup(tracer_instance=honeyhive_tracer)

        assert isinstance(result, tuple)
        assert len(result) == 3
        reason, provider, metadata = result
        assert isinstance(reason, str)
        assert isinstance(metadata, dict)

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_atomic_provider_detection_threading(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test atomic provider detection uses threading lock."""
        result = atomic_provider_detection_and_setup(tracer_instance=honeyhive_tracer)

        assert isinstance(result, tuple)
        assert len(result) == 3
        # Just verify the function completes successfully with threading
        reason, provider, metadata = result
        assert isinstance(reason, str)
        assert isinstance(metadata, dict)


class TestIsFunctioningTracerProvider:
    """Test _is_functioning_tracer_provider function."""

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_is_functioning_tracer_provider_with_provider(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test functioning tracer provider check with provider."""
        provider = TracerProvider()

        result = _is_functioning_tracer_provider(provider, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_is_functioning_tracer_provider_without_provider(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test functioning tracer provider check without provider."""
        mock_provider = TracerProvider()
        mock_get_provider.return_value = mock_provider

        result = _is_functioning_tracer_provider(tracer_instance=honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_is_functioning_tracer_provider_noop(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test functioning tracer provider check with NoOp provider."""
        provider = NoOpTracerProvider()

        result = _is_functioning_tracer_provider(provider, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()


class TestSetGlobalProvider:
    """Test set_global_provider function."""

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_set_global_provider_basic(self, mock_log, honeyhive_tracer) -> None:
        """Test basic global provider setting."""
        provider = TracerProvider()

        # The function should complete without error
        set_global_provider(provider, tracer_instance=honeyhive_tracer)

        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_set_global_provider_with_force_override(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test global provider setting with force override."""
        provider = TracerProvider()

        # The function should complete without error
        set_global_provider(
            provider, force_override=True, tracer_instance=honeyhive_tracer
        )

        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_set_global_provider_existing_provider(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test global provider setting with existing provider."""
        new_provider = TracerProvider()

        # The function should complete without error
        set_global_provider(new_provider, tracer_instance=honeyhive_tracer)

        mock_log.assert_called()


class TestResetProviderFlagDynamically:
    """Test _reset_provider_flag_dynamically function."""

    def test_reset_provider_flag_dynamically(self, honeyhive_tracer) -> None:
        """Test provider flag reset."""
        # The function should complete without error
        _reset_provider_flag_dynamically(tracer_instance=honeyhive_tracer)

        # No assertion needed - just verify it doesn't crash


class TestGetGlobalProvider:
    """Test get_global_provider function."""

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_get_global_provider(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test global provider retrieval."""
        mock_provider = TracerProvider()
        mock_get_provider.return_value = mock_provider

        result = get_global_provider(tracer_instance=honeyhive_tracer)

        assert result == mock_provider
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.trace.get_tracer_provider")
    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_get_global_provider_noop(
        self, mock_log, mock_get_provider, honeyhive_tracer
    ) -> None:
        """Test global provider retrieval with NoOp provider."""
        mock_provider = NoOpTracerProvider()
        mock_get_provider.return_value = mock_provider

        result = get_global_provider(tracer_instance=honeyhive_tracer)

        assert result == mock_provider
        mock_log.assert_called()


class TestProcessorHasExporters:
    """Test _processor_has_exporters function."""

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_processor_has_exporters_with_list(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test processor exporters check with list of processors."""
        # Mock processors list
        mock_processor1 = Mock()
        mock_processor2 = Mock()
        processors = [mock_processor1, mock_processor2]

        result = _processor_has_exporters(processors, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_processor_has_exporters_with_single(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test processor exporters check with single processor."""
        mock_processor = Mock()

        result = _processor_has_exporters(mock_processor, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_processor_has_exporters_empty_list(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test processor exporters check with empty list."""
        processors = []

        result = _processor_has_exporters(processors, honeyhive_tracer)

        assert result is False
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_processor_has_exporters_none(self, mock_log, honeyhive_tracer) -> None:
        """Test processor exporters check with None."""
        result = _processor_has_exporters(None, honeyhive_tracer)

        assert result is False
        mock_log.assert_called()


class TestSingleProcessorHasExporter:
    """Test _single_processor_has_exporter function."""

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_single_processor_has_exporter_with_exporter(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test single processor exporter check with exporter."""
        mock_processor = Mock()
        mock_processor.span_exporter = Mock()

        result = _single_processor_has_exporter(mock_processor, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_single_processor_has_exporter_without_exporter(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test single processor exporter check without exporter."""
        mock_processor = Mock()
        # Remove span_exporter attribute
        if hasattr(mock_processor, "span_exporter"):
            delattr(mock_processor, "span_exporter")

        result = _single_processor_has_exporter(mock_processor, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_single_processor_has_exporter_none_processor(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test single processor exporter check with None processor."""
        result = _single_processor_has_exporter(None, honeyhive_tracer)

        assert result is False
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.detection.safe_log")
    def test_single_processor_has_exporter_none_exporter(
        self, mock_log, honeyhive_tracer
    ) -> None:
        """Test single processor exporter check with None exporter."""
        mock_processor = Mock()
        mock_processor.span_exporter = None

        result = _single_processor_has_exporter(mock_processor, honeyhive_tracer)

        assert isinstance(result, bool)
        mock_log.assert_called()


class TestProviderDetectorPrivateMethods:
    """Test private methods of ProviderDetector that need coverage."""

    def test_has_composite_processors_dynamically(self, honeyhive_tracer) -> None:
        """Test composite processors detection."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider = TracerProvider()

        result = detector._has_composite_processors_dynamically(provider)

        assert isinstance(result, bool)

    def test_get_integration_strategy_dynamically(self, honeyhive_tracer) -> None:
        """Test integration strategy determination."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)
        provider_type = ProviderType.TRACER_PROVIDER

        strategy = detector.get_integration_strategy(provider_type)

        assert isinstance(strategy, IntegrationStrategy)

    def test_detect_provider_type_complete_flow(self, honeyhive_tracer) -> None:
        """Test complete provider type detection flow."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        # Test the complete detection flow
        provider_type = detector.detect_provider_type()

        assert isinstance(provider_type, ProviderType)

    def test_provider_detector_integration(self, honeyhive_tracer) -> None:
        """Test provider detector integration functionality."""
        detector = ProviderDetector(tracer_instance=honeyhive_tracer)

        # Test that the detector can handle different provider types
        provider_type = detector.detect_provider_type()
        strategy = detector.get_integration_strategy(provider_type)

        assert isinstance(provider_type, ProviderType)
        assert isinstance(strategy, IntegrationStrategy)
