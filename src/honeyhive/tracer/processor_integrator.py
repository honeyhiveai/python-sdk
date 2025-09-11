"""Span processor integration framework for non-instrumentor integrations.

This module provides a flexible system for adding HoneyHive span processors
to any existing TracerProvider without disrupting existing functionality.
"""

import threading
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

try:
    from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

from ..utils.logger import get_logger
from .provider_detector import IntegrationStrategy, ProviderDetector
from .span_processor import HoneyHiveSpanProcessor


class ProcessorIntegrationError(Exception):
    """Base exception for processor integration errors."""

    pass


class ProviderIncompatibleError(ProcessorIntegrationError):
    """Provider doesn't support required operations."""

    pass


class ProcessorIntegrator:
    """Manages integration of HoneyHive processors with existing providers."""

    def __init__(self) -> None:
        """Initialize the processor integrator."""
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for ProcessorIntegrator")

        self.logger = get_logger(f"honeyhive.tracer.{self.__class__.__name__}")
        self._lock = threading.Lock()
        self._integrated_processors: List["SpanProcessor"] = []

    def integrate_with_provider(
        self,
        provider: "TracerProvider",
        source: str = "dev",
        project: Optional[str] = None,
    ) -> bool:
        """Add HoneyHive processor to existing provider.

        Args:
            provider: The TracerProvider to integrate with
            source: Source environment for span enrichment
            project: Optional project for span enrichment

        Returns:
            bool: True if integration successful, False otherwise

        Raises:
            ProviderIncompatibleError: If provider doesn't support span processors
        """
        with self._lock:
            try:
                # Validate provider compatibility
                if not self.validate_processor_compatibility(provider):
                    self.logger.warning(
                        "Provider doesn't support span processors",
                        honeyhive_data={"provider_class": type(provider).__name__},
                    )
                    return False

                # Create HoneyHive span processor directly (processors can't be batched, only exporters can)
                honeyhive_processor = HoneyHiveSpanProcessor()
                provider.add_span_processor(honeyhive_processor)

                # Track integrated processor
                self._integrated_processors.append(honeyhive_processor)

                self.logger.info(
                    "Successfully integrated HoneyHive span processor",
                    honeyhive_data={"provider_class": type(provider).__name__},
                )
                return True

            except Exception as e:
                self.logger.error(
                    "Failed to integrate with provider",
                    honeyhive_data={
                        "provider_class": type(provider).__name__,
                        "error": str(e),
                    },
                )
                return False

    def validate_processor_compatibility(self, provider: "TracerProvider") -> bool:
        """Check if provider supports span processor integration.

        Args:
            provider: The TracerProvider to check

        Returns:
            bool: True if provider supports span processors
        """
        return hasattr(provider, "add_span_processor") and callable(
            getattr(provider, "add_span_processor")
        )

    def get_processor_insertion_point(self, provider: "TracerProvider") -> int:
        """Determine optimal position for HoneyHive processor.

        For now, we append to the end of the processor chain.
        Future versions could implement more sophisticated ordering.

        Args:
            provider: The TracerProvider to analyze

        Returns:
            int: Index where processor should be inserted (-1 for append)
        """
        # For now, always append to end
        # Future enhancement: analyze existing processors and determine optimal position
        return -1

    def get_integrated_processors(self) -> List["SpanProcessor"]:
        """Get list of processors that have been integrated.

        Returns:
            List[SpanProcessor]: List of integrated HoneyHive processors
        """
        with self._lock:
            return self._integrated_processors.copy()

    def cleanup_processors(self) -> None:
        """Clean up integrated processors.

        This should be called during shutdown to ensure proper cleanup.
        """
        with self._lock:
            for processor in self._integrated_processors:
                try:
                    if hasattr(processor, "shutdown"):
                        processor.shutdown()
                except Exception as e:
                    self.logger.warning(
                        "Error shutting down processor",
                        honeyhive_data={"error": str(e)},
                    )

            self._integrated_processors.clear()
            self.logger.info("Cleaned up integrated processors")


class IntegrationManager:
    """High-level manager for non-instrumentor integrations."""

    def __init__(self) -> None:
        """Initialize the integration manager."""
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for IntegrationManager")

        self.detector = ProviderDetector()
        self.integrator = ProcessorIntegrator()

    def perform_integration(
        self, source: str = "dev", project: Optional[str] = None
    ) -> dict[str, Any]:
        """Perform complete integration based on detected provider.

        Args:
            source: Source environment for span enrichment
            project: Optional project for span enrichment

        Returns:
            dict: Integration result with status and details
        """
        try:
            # Get provider information
            provider_info = self.detector.get_provider_info()
            strategy = provider_info["integration_strategy"]

            result = {
                "success": False,
                "strategy": strategy,
                "provider_info": provider_info,
                "message": "",
            }

            if strategy == IntegrationStrategy.MAIN_PROVIDER:
                # Provider is replaceable (NoOp/Proxy) - this should be handled by caller
                result["message"] = (
                    "Provider is replaceable - caller should create new TracerProvider"
                )
                result["success"] = True

            elif strategy == IntegrationStrategy.SECONDARY_PROVIDER:
                # Add processors to existing provider
                provider = provider_info["provider_instance"]
                success = self.integrator.integrate_with_provider(
                    provider, source=source, project=project
                )
                result["success"] = success
                result["message"] = (
                    "Successfully integrated with existing provider"
                    if success
                    else "Failed to integrate with existing provider"
                )

            elif strategy == IntegrationStrategy.CONSOLE_FALLBACK:
                # Fallback to console logging
                result["message"] = (
                    "Provider incompatible - falling back to console logging"
                )
                result["success"] = True  # Console fallback is considered successful

            return result

        except Exception as e:
            return {
                "success": False,
                "strategy": IntegrationStrategy.CONSOLE_FALLBACK,
                "provider_info": {},
                "message": f"Integration failed: {e}",
                "error": str(e),
            }

    def cleanup(self) -> None:
        """Clean up integration resources."""
        self.integrator.cleanup_processors()


# Convenience functions for backward compatibility
def integrate_with_existing_provider(
    source: str = "dev", project: Optional[str] = None
) -> dict[str, Any]:
    """Integrate HoneyHive with existing OpenTelemetry provider.

    This is a convenience function that handles the complete integration process.

    Args:
        source: Source environment for span enrichment
        project: Optional project for span enrichment

    Returns:
        dict: Integration result with status and details
    """
    if not OTEL_AVAILABLE:
        return {
            "success": False,
            "strategy": IntegrationStrategy.CONSOLE_FALLBACK,
            "message": "OpenTelemetry not available",
        }

    manager = IntegrationManager()
    return manager.perform_integration(source=source, project=project)
