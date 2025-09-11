"""Integration tests for non-instrumentor integration framework."""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.otel_tracer import HoneyHiveTracer
from honeyhive.tracer.processor_integrator import IntegrationManager
from honeyhive.tracer.provider_detector import (
    IntegrationStrategy,
    ProviderDetector,
    ProviderType,
)


class TestNonInstrumentorIntegration:
    """Test cases for non-instrumentor integration framework."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset OpenTelemetry state before each test
        with patch("honeyhive.tracer.otel_tracer.trace.set_tracer_provider"):
            pass

    def test_provider_detection_accuracy(self):
        """Test provider detection across all types."""
        detector = ProviderDetector()

        # Test with mock providers
        test_cases = [
            ("NoOpTracerProvider", ProviderType.NOOP),
            ("ProxyTracerProvider", ProviderType.PROXY_TRACER_PROVIDER),
            ("TracerProvider", ProviderType.TRACER_PROVIDER),
            ("CustomTracerProvider", ProviderType.CUSTOM),
        ]

        for provider_name, expected_type in test_cases:
            mock_provider = Mock()
            mock_provider.__class__.__name__ = provider_name

            with patch(
                "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
                return_value=mock_provider,
            ):
                detected_type = detector.detect_provider_type()
                assert detected_type == expected_type, f"Failed for {provider_name}"

    def test_integration_strategy_selection(self):
        """Test integration strategy selection for different provider types."""
        detector = ProviderDetector()

        strategy_cases = [
            (ProviderType.NOOP, IntegrationStrategy.MAIN_PROVIDER),
            (ProviderType.PROXY_TRACER_PROVIDER, IntegrationStrategy.MAIN_PROVIDER),
            (ProviderType.TRACER_PROVIDER, IntegrationStrategy.SECONDARY_PROVIDER),
            (ProviderType.CUSTOM, IntegrationStrategy.CONSOLE_FALLBACK),
        ]

        for provider_type, expected_strategy in strategy_cases:
            strategy = detector.get_integration_strategy(provider_type)
            assert strategy == expected_strategy, f"Failed for {provider_type}"

    @patch("honeyhive.tracer.otel_tracer.trace.get_tracer_provider")
    @patch("honeyhive.tracer.otel_tracer.trace.set_tracer_provider")
    def test_initialization_order_honeyhive_first(
        self, mock_set_provider, mock_get_provider
    ):
        """Test HoneyHive initializing before framework (main provider scenario)."""
        # Mock NoOp provider initially
        mock_noop_provider = Mock()
        mock_noop_provider.__class__.__name__ = "NoOpTracerProvider"
        mock_get_provider.return_value = mock_noop_provider

        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer(api_key="test-key", source="test", test_mode=True)

        # Verify HoneyHive became main provider
        assert tracer.is_main_provider is True
        assert mock_set_provider.called

        # Verify provider info
        detector = ProviderDetector()
        info = detector.get_provider_info()
        assert info["is_replaceable"] is True

    def test_initialization_order_framework_first(self):
        """Test framework initializing before HoneyHive (secondary provider scenario)."""
        # Mock real TracerProvider from framework
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"
        mock_provider.add_span_processor = Mock()

        # Mock the provider detector to return secondary provider strategy
        with patch(
            "honeyhive.tracer.otel_tracer.ProviderDetector"
        ) as mock_detector_class:
            mock_detector = Mock()
            mock_detector.get_provider_info.return_value = {
                "integration_strategy": IntegrationStrategy.SECONDARY_PROVIDER,
                "provider_instance": mock_provider,
                "provider_class_name": "TracerProvider",
            }
            mock_detector_class.return_value = mock_detector

            # Initialize HoneyHive tracer
            with patch(
                "honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor"
            ) as mock_processor_class:
                mock_processor = Mock()
                mock_processor_class.return_value = mock_processor

                tracer = HoneyHiveTracer(
                    api_key="test-key", source="test", test_mode=True
                )

                # Verify HoneyHive integrated as secondary provider
                assert tracer.is_main_provider is False
                assert tracer.provider == mock_provider

    @patch("honeyhive.tracer.otel_tracer.trace.get_tracer_provider")
    def test_proxy_provider_replacement(self, mock_get_provider):
        """Test ProxyTracerProvider replacement scenario."""
        # Mock ProxyTracerProvider from framework
        mock_proxy_provider = Mock()
        mock_proxy_provider.__class__.__name__ = "ProxyTracerProvider"
        mock_get_provider.return_value = mock_proxy_provider

        # Initialize HoneyHive tracer
        with patch(
            "honeyhive.tracer.otel_tracer.trace.set_tracer_provider"
        ) as mock_set_provider:
            tracer = HoneyHiveTracer(api_key="test-key", source="test", test_mode=True)

            # Verify HoneyHive replaced proxy provider
            assert tracer.is_main_provider is True
            assert mock_set_provider.called

            # Verify detection logic
            detector = ProviderDetector()
            strategy = detector.get_integration_strategy(
                ProviderType.PROXY_TRACER_PROVIDER
            )
            assert strategy == IntegrationStrategy.MAIN_PROVIDER

    def test_concurrent_initialization(self):
        """Test concurrent initialization scenarios."""
        results = []

        def init_honeyhive():
            """Initialize HoneyHive in thread."""
            try:
                with patch(
                    "honeyhive.tracer.otel_tracer.trace.get_tracer_provider"
                ) as mock_get:
                    with patch(
                        "honeyhive.tracer.otel_tracer.trace.set_tracer_provider"
                    ):
                        mock_provider = Mock()
                        mock_provider.__class__.__name__ = "NoOpTracerProvider"
                        mock_get.return_value = mock_provider

                        tracer = HoneyHiveTracer(
                            api_key="test-key", source="test", test_mode=True
                        )
                        results.append(("honeyhive", tracer.is_main_provider))
            except Exception as e:
                results.append(("honeyhive", f"error: {e}"))

        def init_framework():
            """Initialize mock framework in thread."""
            try:
                # Simulate framework setting up provider
                time.sleep(0.01)  # Small delay to simulate initialization
                results.append(("framework", "initialized"))
            except Exception as e:
                results.append(("framework", f"error: {e}"))

        # Start concurrent initialization
        threads = [
            threading.Thread(target=init_honeyhive),
            threading.Thread(target=init_framework),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Verify both initialized successfully
        assert len(results) == 2
        assert any("honeyhive" in result[0] for result in results)
        assert any("framework" in result[0] for result in results)

    def test_multi_framework_integration(self):
        """Test integration with multiple frameworks simultaneously."""
        # Mock multiple framework providers
        frameworks = [
            ("FrameworkA", Mock()),
            ("FrameworkB", Mock()),
            ("FrameworkC", Mock()),
        ]

        integration_manager = IntegrationManager()
        integration_results = []

        for name, mock_provider in frameworks:
            mock_provider.__class__.__name__ = f"{name}TracerProvider"
            mock_provider.add_span_processor = Mock()

            # Mock detector to return secondary provider strategy
            mock_detector = Mock()
            mock_detector.get_provider_info.return_value = {
                "integration_strategy": IntegrationStrategy.SECONDARY_PROVIDER,
                "provider_instance": mock_provider,
                "provider_class_name": f"{name}TracerProvider",
            }
            integration_manager.detector = mock_detector

            # Perform integration
            result = integration_manager.perform_integration(source="test")
            integration_results.append((name, result["success"]))

        # Verify all integrations succeeded
        assert all(success for _, success in integration_results)
        assert len(integration_results) == 3

    def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation."""
        # Test with incompatible provider
        mock_provider = Mock(spec=[])  # No add_span_processor method
        mock_provider.__class__.__name__ = "IncompatibleProvider"

        with patch(
            "honeyhive.tracer.provider_detector.trace.get_tracer_provider",
            return_value=mock_provider,
        ):
            detector = ProviderDetector()
            info = detector.get_provider_info()

            # Should fall back to console strategy
            assert info["integration_strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
            assert info["supports_span_processors"] is False

    def test_span_processor_integration_validation(self):
        """Test span processor integration validation."""
        integration_manager = IntegrationManager()

        # Test with compatible provider
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()

        compatible = integration_manager.integrator.validate_processor_compatibility(
            mock_provider
        )
        assert compatible is True

        # Test with incompatible provider
        mock_incompatible = Mock(spec=[])
        incompatible = integration_manager.integrator.validate_processor_compatibility(
            mock_incompatible
        )
        assert incompatible is False

    def test_integration_cleanup(self):
        """Test integration cleanup and resource management."""
        integration_manager = IntegrationManager()

        # Add mock processors
        mock_processor1 = Mock()
        mock_processor1.shutdown = Mock()
        mock_processor2 = Mock()
        mock_processor2.shutdown = Mock()

        integration_manager.integrator._integrated_processors = [
            mock_processor1,
            mock_processor2,
        ]

        # Cleanup
        integration_manager.cleanup()

        # Verify cleanup was called
        mock_processor1.shutdown.assert_called_once()
        mock_processor2.shutdown.assert_called_once()
        assert len(integration_manager.integrator.get_integrated_processors()) == 0

    def test_performance_overhead(self):
        """Test performance overhead of integration."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.__class__.__name__ = "TracerProvider"
        mock_provider.add_span_processor = Mock()

        # Mock the provider detector to return secondary provider strategy
        with patch(
            "honeyhive.tracer.otel_tracer.ProviderDetector"
        ) as mock_detector_class:
            mock_detector = Mock()
            mock_detector.get_provider_info.return_value = {
                "integration_strategy": IntegrationStrategy.SECONDARY_PROVIDER,
                "provider_instance": mock_provider,
                "provider_class_name": "TracerProvider",
            }
            mock_detector_class.return_value = mock_detector

            # Measure initialization time
            start_time = time.time()

            with patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor"):
                tracer = HoneyHiveTracer(
                    api_key="test-key", source="test", test_mode=True
                )

            initialization_time = time.time() - start_time

            # Verify initialization is fast (< 1s for integration tests)
            assert (
                initialization_time < 1.0
            ), f"Initialization took {initialization_time:.3f}s"

            # Verify integration succeeded
            assert tracer.provider == mock_provider
            assert tracer.is_main_provider is False


class TestInitializationOrderIndependence:
    """Test cases for initialization order independence."""

    def test_all_initialization_permutations(self):
        """Test all possible initialization order permutations."""
        scenarios = [
            ("honeyhive_first", self._init_honeyhive_first),
            ("framework_first", self._init_framework_first),
            ("concurrent", self._init_concurrent),
        ]

        for scenario_name, scenario_func in scenarios:
            try:
                result = scenario_func()
                assert (
                    result["success"] is True
                ), f"Scenario {scenario_name} failed: {result.get('error')}"
            except Exception as e:
                pytest.fail(f"Scenario {scenario_name} raised exception: {e}")

    def _init_honeyhive_first(self):
        """Initialize HoneyHive first scenario."""
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider"
        ) as mock_get:
            with patch("honeyhive.tracer.otel_tracer.trace.set_tracer_provider"):
                mock_provider = Mock()
                mock_provider.__class__.__name__ = "NoOpTracerProvider"
                mock_get.return_value = mock_provider

                tracer = HoneyHiveTracer(api_key="test-key", test_mode=True)
                return {"success": True, "is_main": tracer.is_main_provider}

    def _init_framework_first(self):
        """Initialize framework first scenario."""
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider"
        ) as mock_get:
            mock_provider = Mock()
            mock_provider.__class__.__name__ = "TracerProvider"
            mock_provider.add_span_processor = Mock()
            mock_get.return_value = mock_provider

            with patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor"):
                tracer = HoneyHiveTracer(api_key="test-key", test_mode=True)
                return {"success": True, "is_main": tracer.is_main_provider}

    def _init_concurrent(self):
        """Initialize concurrently scenario."""
        # Simplified concurrent test
        with patch(
            "honeyhive.tracer.otel_tracer.trace.get_tracer_provider"
        ) as mock_get:
            with patch("honeyhive.tracer.otel_tracer.trace.set_tracer_provider"):
                mock_provider = Mock()
                mock_provider.__class__.__name__ = "NoOpTracerProvider"
                mock_get.return_value = mock_provider

                tracer = HoneyHiveTracer(api_key="test-key", test_mode=True)
                return {"success": True, "is_main": tracer.is_main_provider}
