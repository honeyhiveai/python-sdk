"""Provider detection system for non-instrumentor integration framework.

This module provides robust detection and classification of existing OpenTelemetry
TracerProviders to determine the appropriate integration strategy.
"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from opentelemetry import trace

try:
    from opentelemetry import trace

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class ProviderType(Enum):
    """Types of OpenTelemetry TracerProviders."""

    NOOP = "noop"
    TRACER_PROVIDER = "tracer_provider"
    PROXY_TRACER_PROVIDER = "proxy_tracer_provider"
    CUSTOM = "custom"


class IntegrationStrategy(Enum):
    """Integration strategies for different provider types."""

    MAIN_PROVIDER = "main_provider"
    SECONDARY_PROVIDER = "secondary_provider"
    CONSOLE_FALLBACK = "console_fallback"


class ProviderDetector:
    """Detects and classifies existing OpenTelemetry TracerProviders."""

    def __init__(self) -> None:
        """Initialize the provider detector."""
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for ProviderDetector")

    def detect_provider_type(self) -> ProviderType:
        """Detect the type of existing TracerProvider.

        Returns:
            ProviderType: The detected provider type
        """
        existing_provider = trace.get_tracer_provider()

        if self._is_noop_provider(existing_provider):
            return ProviderType.NOOP
        elif self._is_proxy_provider(existing_provider):
            return ProviderType.PROXY_TRACER_PROVIDER
        elif self._is_tracer_provider(existing_provider):
            return ProviderType.TRACER_PROVIDER
        else:
            return ProviderType.CUSTOM

    def get_integration_strategy(
        self, provider_type: Optional[ProviderType] = None
    ) -> IntegrationStrategy:
        """Determine integration strategy based on provider type.

        Args:
            provider_type: Optional provider type. If None, will detect automatically.

        Returns:
            IntegrationStrategy: The recommended integration strategy
        """
        if provider_type is None:
            provider_type = self.detect_provider_type()

        if provider_type in (ProviderType.NOOP, ProviderType.PROXY_TRACER_PROVIDER):
            # NoOp and Proxy providers are safe to replace
            return IntegrationStrategy.MAIN_PROVIDER
        elif provider_type == ProviderType.TRACER_PROVIDER:
            # Real TracerProvider - add processors to existing provider
            return IntegrationStrategy.SECONDARY_PROVIDER
        else:
            # Custom or unknown provider - fallback to console
            return IntegrationStrategy.CONSOLE_FALLBACK

    def can_add_span_processor(self) -> bool:
        """Check if the current provider supports adding span processors.

        Returns:
            bool: True if span processors can be added
        """
        existing_provider = trace.get_tracer_provider()
        return hasattr(existing_provider, "add_span_processor")

    def get_provider_info(self) -> dict[str, Any]:
        """Get detailed information about the current provider.

        Returns:
            dict: Provider information including type, name, and capabilities
        """
        existing_provider = trace.get_tracer_provider()
        provider_type = self.detect_provider_type()
        integration_strategy = self.get_integration_strategy(provider_type)

        return {
            "provider_instance": existing_provider,
            "provider_class_name": type(existing_provider).__name__,
            "provider_type": provider_type,
            "integration_strategy": integration_strategy,
            "supports_span_processors": self.can_add_span_processor(),
            "is_replaceable": provider_type
            in (ProviderType.NOOP, ProviderType.PROXY_TRACER_PROVIDER),
        }

    def _is_noop_provider(self, provider: Any) -> bool:
        """Check if provider is NoOp or equivalent.

        Args:
            provider: The provider instance to check

        Returns:
            bool: True if provider is NoOp
        """
        if provider is None:
            return True

        provider_name = type(provider).__name__
        return "NoOp" in provider_name or provider_name == "NoOpTracerProvider"

    def _is_proxy_provider(self, provider: Any) -> bool:
        """Check if provider is ProxyTracerProvider.

        Args:
            provider: The provider instance to check

        Returns:
            bool: True if provider is ProxyTracerProvider
        """
        if provider is None:
            return False

        provider_name = type(provider).__name__
        return "Proxy" in provider_name or provider_name == "ProxyTracerProvider"

    def _is_tracer_provider(self, provider: Any) -> bool:
        """Check if provider is a real TracerProvider.

        Args:
            provider: The provider instance to check

        Returns:
            bool: True if provider is a real TracerProvider
        """
        if provider is None:
            return False

        provider_name = type(provider).__name__
        # Check for exact TracerProvider match, excluding variants
        return provider_name == "TracerProvider" or (
            "TracerProvider" in provider_name
            and "Proxy" not in provider_name
            and "NoOp" not in provider_name
            and "Custom" not in provider_name
        )


def detect_provider_integration_strategy() -> IntegrationStrategy:
    """Detect existing provider and determine integration strategy.

    This is a convenience function that combines provider detection
    and strategy selection in a single call.

    Returns:
        IntegrationStrategy: The recommended integration strategy
    """
    if not OTEL_AVAILABLE:
        return IntegrationStrategy.CONSOLE_FALLBACK

    detector = ProviderDetector()
    return detector.get_integration_strategy()


def is_noop_or_proxy_provider(provider: Any) -> bool:
    """Check if provider is NoOp, Proxy, or equivalent placeholder.

    Args:
        provider: The provider instance to check

    Returns:
        bool: True if provider is a placeholder that can be safely replaced
    """
    if not OTEL_AVAILABLE:
        return True

    detector = ProviderDetector()
    return detector._is_noop_provider(provider) or detector._is_proxy_provider(provider)
