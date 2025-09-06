"""Unit tests for processor integration system."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive.tracer.processor_integrator import (
    IntegrationManager,
    ProcessorIntegrationError,
    ProcessorIntegrator,
    ProviderIncompatibleError,
    integrate_with_existing_provider,
)
from honeyhive.tracer.provider_detector import IntegrationStrategy


class TestProcessorIntegrator:
    """Test cases for ProcessorIntegrator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.integrator = ProcessorIntegrator()

    def test_validate_processor_compatibility_true(self):
        """Test processor compatibility validation - positive case."""
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()

        result = self.integrator.validate_processor_compatibility(mock_provider)
        assert result is True

    def test_validate_processor_compatibility_false(self):
        """Test processor compatibility validation - negative case."""
        mock_provider = Mock(spec=[])  # No add_span_processor method

        result = self.integrator.validate_processor_compatibility(mock_provider)
        assert result is False

    def test_validate_processor_compatibility_not_callable(self):
        """Test processor compatibility validation - attribute not callable."""
        mock_provider = Mock()
        mock_provider.add_span_processor = "not_callable"

        result = self.integrator.validate_processor_compatibility(mock_provider)
        assert result is False

    @patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor")
    def test_integrate_with_provider_success(self, mock_processor_class):
        """Test successful integration with provider."""
        # Setup mocks
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        # Test integration
        result = self.integrator.integrate_with_provider(mock_provider)

        assert result is True
        mock_provider.add_span_processor.assert_called_once_with(mock_processor)
        assert mock_processor in self.integrator.get_integrated_processors()

    def test_integrate_with_provider_incompatible(self):
        """Test integration with incompatible provider."""
        mock_provider = Mock(spec=[])  # No add_span_processor method

        # Should return False, not raise exception
        result = self.integrator.integrate_with_provider(mock_provider)
        assert result is False

    @patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor")
    def test_integrate_with_provider_exception(self, mock_processor_class):
        """Test integration handling exceptions."""
        # Setup mocks
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock(side_effect=Exception("Test error"))
        mock_processor_class.return_value = Mock()

        # Test integration
        result = self.integrator.integrate_with_provider(mock_provider)

        assert result is False

    def test_get_processor_insertion_point(self):
        """Test processor insertion point determination."""
        mock_provider = Mock()

        insertion_point = self.integrator.get_processor_insertion_point(mock_provider)
        assert insertion_point == -1  # Always append for now

    def test_get_integrated_processors_empty(self):
        """Test getting integrated processors when none exist."""
        processors = self.integrator.get_integrated_processors()
        assert processors == []

    @patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor")
    def test_get_integrated_processors_with_processors(self, mock_processor_class):
        """Test getting integrated processors when some exist."""
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        # Add a processor
        self.integrator.integrate_with_provider(mock_provider)

        processors = self.integrator.get_integrated_processors()
        assert len(processors) == 1
        assert mock_processor in processors

    @patch("honeyhive.tracer.processor_integrator.HoneyHiveSpanProcessor")
    def test_cleanup_processors(self, mock_processor_class):
        """Test processor cleanup."""
        # Setup mock processor with shutdown method
        mock_processor = Mock()
        mock_processor.shutdown = Mock()
        mock_processor_class.return_value = mock_processor

        # Setup mock provider
        mock_provider = Mock()
        mock_provider.add_span_processor = Mock()

        # Add processor
        self.integrator.integrate_with_provider(mock_provider)

        # Cleanup
        self.integrator.cleanup_processors()

        mock_processor.shutdown.assert_called_once()
        assert len(self.integrator.get_integrated_processors()) == 0

    def test_cleanup_processors_no_shutdown(self):
        """Test processor cleanup when processor has no shutdown method."""
        # Add a mock processor without shutdown method
        mock_processor = Mock(spec=[])
        self.integrator._integrated_processors.append(mock_processor)

        # Should not raise exception
        self.integrator.cleanup_processors()
        assert len(self.integrator.get_integrated_processors()) == 0

    def test_cleanup_processors_shutdown_exception(self):
        """Test processor cleanup when shutdown raises exception."""
        # Setup mock processor with failing shutdown
        mock_processor = Mock()
        mock_processor.shutdown = Mock(side_effect=Exception("Shutdown error"))
        self.integrator._integrated_processors.append(mock_processor)

        # Should not raise exception
        self.integrator.cleanup_processors()
        assert len(self.integrator.get_integrated_processors()) == 0


class TestIntegrationManager:
    """Test cases for IntegrationManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = IntegrationManager()

    def test_perform_integration_main_provider(self):
        """Test integration with main provider strategy."""
        # Setup mock detector
        mock_detector = Mock()
        mock_detector.get_provider_info.return_value = {
            "integration_strategy": IntegrationStrategy.MAIN_PROVIDER,
            "provider_instance": Mock(),
            "provider_class_name": "NoOpTracerProvider",
        }
        self.manager.detector = mock_detector

        result = self.manager.perform_integration()

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.MAIN_PROVIDER
        assert "replaceable" in result["message"]

    def test_perform_integration_secondary_provider_success(self):
        """Test integration with secondary provider strategy - success."""
        # Setup mock detector
        mock_provider = Mock()
        mock_detector = Mock()
        mock_detector.get_provider_info.return_value = {
            "integration_strategy": IntegrationStrategy.SECONDARY_PROVIDER,
            "provider_instance": mock_provider,
            "provider_class_name": "TracerProvider",
        }
        self.manager.detector = mock_detector

        # Setup mock integrator
        mock_integrator = Mock()
        mock_integrator.integrate_with_provider.return_value = True
        mock_integrator.get_integrated_processors.return_value = [Mock()]
        self.manager.integrator = mock_integrator

        result = self.manager.perform_integration()

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.SECONDARY_PROVIDER
        assert "Successfully integrated" in result["message"]

    def test_perform_integration_secondary_provider_failure(self):
        """Test integration with secondary provider strategy - failure."""
        # Setup mock detector
        mock_provider = Mock()
        mock_detector = Mock()
        mock_detector.get_provider_info.return_value = {
            "integration_strategy": IntegrationStrategy.SECONDARY_PROVIDER,
            "provider_instance": mock_provider,
            "provider_class_name": "TracerProvider",
        }
        self.manager.detector = mock_detector

        # Setup mock integrator
        mock_integrator = Mock()
        mock_integrator.integrate_with_provider.return_value = False
        self.manager.integrator = mock_integrator

        result = self.manager.perform_integration()

        assert result["success"] is False
        assert result["strategy"] == IntegrationStrategy.SECONDARY_PROVIDER
        assert "Failed to integrate" in result["message"]

    def test_perform_integration_console_fallback(self):
        """Test integration with console fallback strategy."""
        # Setup mock detector
        mock_detector = Mock()
        mock_detector.get_provider_info.return_value = {
            "integration_strategy": IntegrationStrategy.CONSOLE_FALLBACK,
            "provider_instance": Mock(),
            "provider_class_name": "CustomProvider",
        }
        self.manager.detector = mock_detector

        result = self.manager.perform_integration()

        assert result["success"] is True
        assert result["strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
        assert "console logging" in result["message"]

    def test_perform_integration_exception(self):
        """Test integration handling exceptions."""
        # Setup mock detector to raise exception
        mock_detector = Mock()
        mock_detector.get_provider_info.side_effect = Exception("Test error")
        self.manager.detector = mock_detector

        result = self.manager.perform_integration()

        assert result["success"] is False
        assert result["strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
        assert "Integration failed" in result["message"]
        assert "error" in result

    @patch("honeyhive.tracer.processor_integrator.ProcessorIntegrator")
    def test_cleanup(self, mock_integrator_class):
        """Test integration manager cleanup."""
        mock_integrator = Mock()
        mock_integrator_class.return_value = mock_integrator

        manager = IntegrationManager()
        manager.cleanup()

        mock_integrator.cleanup_processors.assert_called_once()


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @patch("honeyhive.tracer.processor_integrator.IntegrationManager")
    def test_integrate_with_existing_provider_success(self, mock_manager_class):
        """Test convenience function for successful integration."""
        mock_manager = Mock()
        mock_manager.perform_integration.return_value = {
            "success": True,
            "strategy": IntegrationStrategy.SECONDARY_PROVIDER,
            "message": "Success",
        }
        mock_manager_class.return_value = mock_manager

        result = integrate_with_existing_provider(source="test", project="test-project")

        assert result["success"] is True
        mock_manager.perform_integration.assert_called_once_with(
            source="test", project="test-project"
        )

    @patch("honeyhive.tracer.processor_integrator.OTEL_AVAILABLE", False)
    def test_integrate_with_existing_provider_no_otel(self):
        """Test convenience function when OpenTelemetry not available."""
        result = integrate_with_existing_provider()

        assert result["success"] is False
        assert result["strategy"] == IntegrationStrategy.CONSOLE_FALLBACK
        assert "OpenTelemetry not available" in result["message"]


class TestProcessorIntegratorInitialization:
    """Test cases for ProcessorIntegrator initialization."""

    @patch("honeyhive.tracer.processor_integrator.OTEL_AVAILABLE", False)
    def test_init_without_otel(self):
        """Test initialization fails without OpenTelemetry."""
        with pytest.raises(ImportError, match="OpenTelemetry is required"):
            ProcessorIntegrator()

    def test_init_with_otel(self):
        """Test successful initialization with OpenTelemetry."""
        integrator = ProcessorIntegrator()
        assert integrator is not None
        assert integrator._integrated_processors == []


class TestIntegrationManagerInitialization:
    """Test cases for IntegrationManager initialization."""

    @patch("honeyhive.tracer.processor_integrator.OTEL_AVAILABLE", False)
    def test_init_without_otel(self):
        """Test initialization fails without OpenTelemetry."""
        with pytest.raises(ImportError, match="OpenTelemetry is required"):
            IntegrationManager()

    def test_init_with_otel(self):
        """Test successful initialization with OpenTelemetry."""
        manager = IntegrationManager()
        assert manager is not None
        assert manager.detector is not None
        assert manager.integrator is not None
