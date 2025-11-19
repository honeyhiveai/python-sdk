"""Dynamic provider detection system for integration framework.

This module provides robust detection and classification of existing OpenTelemetry
TracerProviders using dynamic logic patterns to determine appropriate integration
strategies. All detection logic is extensible and configuration-driven.
"""

# pylint: disable=protected-access
# Justification: This module needs to inspect internal OpenTelemetry provider attributes
# for dynamic provider detection and integration strategy determination.

import threading
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import _set_tracer_provider

# Import shared logging utility
from ...utils.logger import safe_log

# Process-local lock for atomic provider detection and setting
# This prevents race conditions within a single process while being pytest-xdist
# compatible
_provider_detection_lock = threading.Lock()


class ProviderType(Enum):
    """Types of OpenTelemetry TracerProviders."""

    NOOP = "noop"
    TRACER_PROVIDER = "tracer_provider"
    PROXY_TRACER_PROVIDER = "proxy_tracer_provider"
    CUSTOM = "custom"


class IntegrationStrategy(Enum):
    """Integration strategies for different provider types."""

    MAIN_PROVIDER = "main_provider"
    INDEPENDENT_PROVIDER = "independent_provider"
    CONSOLE_FALLBACK = "console_fallback"


class ProviderDetector:
    """Dynamically detects and classifies existing OpenTelemetry TracerProviders."""

    def __init__(self, tracer_instance: Any = None) -> None:
        """Initialize the provider detector with dynamic detection patterns.

        Args:
            tracer_instance: Optional tracer instance for logging context
        """
        self.tracer_instance = tracer_instance
        self._detection_patterns = self._build_detection_patterns_dynamically()
        self._strategy_rules = self._build_strategy_rules_dynamically()

    def _build_detection_patterns_dynamically(self) -> Dict[str, List[str]]:
        """Dynamically build provider detection patterns.

        Returns:
            Dictionary mapping provider types to detection patterns
        """
        return {
            "noop": ["NoOp", "NoOpTracerProvider"],
            "proxy_tracer_provider": ["Proxy", "ProxyTracerProvider"],
            "tracer_provider": ["TracerProvider"],
            "custom": [],  # Fallback for unrecognized patterns
        }

    def _build_strategy_rules_dynamically(
        self,
    ) -> Dict[ProviderType, IntegrationStrategy]:
        """Dynamically build integration strategy rules.

        Returns:
            Dictionary mapping provider types to integration strategies
        """
        return {
            ProviderType.NOOP: IntegrationStrategy.MAIN_PROVIDER,
            ProviderType.PROXY_TRACER_PROVIDER: IntegrationStrategy.MAIN_PROVIDER,
            ProviderType.TRACER_PROVIDER: IntegrationStrategy.INDEPENDENT_PROVIDER,
            ProviderType.CUSTOM: IntegrationStrategy.INDEPENDENT_PROVIDER,
        }

    def detect_provider_type(self) -> ProviderType:
        """Dynamically detect the type of existing TracerProvider.

        Returns:
            ProviderType: The detected provider type
        """
        existing_provider = trace.get_tracer_provider()

        # Dynamic provider type detection
        provider_type = self._classify_provider_dynamically(existing_provider)

        safe_log(
            self.tracer_instance,
            "debug",
            "Provider type detected",
            honeyhive_data={
                "provider_class": type(existing_provider).__name__,
                "detected_type": provider_type.value,
            },
        )

        return provider_type

    def _classify_provider_dynamically(self, provider: Any) -> ProviderType:
        """Dynamically classify provider using pattern matching.

        Args:
            provider: The provider instance to classify

        Returns:
            ProviderType: The classified provider type
        """
        if provider is None:
            return ProviderType.NOOP

        provider_name = type(provider).__name__

        # Dynamic pattern matching
        for provider_type, patterns in self._detection_patterns.items():
            if self._matches_patterns_dynamically(provider_name, patterns):
                return ProviderType(provider_type)

        # Special case for TracerProvider - check for exclusions
        if self._is_tracer_provider_dynamically(provider_name):
            return ProviderType.TRACER_PROVIDER

        # Default to custom for unrecognized providers
        return ProviderType.CUSTOM

    def _matches_patterns_dynamically(
        self, provider_name: str, patterns: List[str]
    ) -> bool:
        """Dynamically match provider name against patterns.

        Args:
            provider_name: Name of the provider class
            patterns: List of patterns to match against

        Returns:
            bool: True if provider name matches any pattern
        """
        return any(pattern in provider_name for pattern in patterns)

    def _is_tracer_provider_dynamically(self, provider_name: str) -> bool:
        """Dynamically check if provider is a real TracerProvider.

        Args:
            provider_name: Name of the provider class

        Returns:
            bool: True if provider is a real TracerProvider
        """
        # Dynamic exclusion patterns
        exclusion_patterns = ["Proxy", "NoOp", "Custom"]

        # Check for TracerProvider with exclusions
        return provider_name == "TracerProvider" or (
            "TracerProvider" in provider_name
            and not any(exclusion in provider_name for exclusion in exclusion_patterns)
        )

    def get_integration_strategy(
        self, provider_type: Optional[ProviderType] = None
    ) -> IntegrationStrategy:
        """Dynamically determine integration strategy using Provider Intelligence.

        This implements the Agent OS Provider Strategy Intelligence:
        - Main Provider Strategy: Replace non-functioning providers (NoOp/Proxy/Empty)
        - Independent Provider Strategy: Coexist with functioning providers
        - Critical: Someone must process instrumentor spans - empty providers lose data

        Args:
            provider_type: Optional provider type. If None, will detect automatically.

        Returns:
            IntegrationStrategy: The recommended integration strategy
        """
        if provider_type is None:
            provider_type = self.detect_provider_type()

        # PROVIDER STRATEGY INTELLIGENCE: Check if current provider is functioning
        current_provider = trace.get_tracer_provider()
        is_functioning = _is_functioning_tracer_provider(
            current_provider, self.tracer_instance
        )

        if is_functioning:
            # Functioning provider exists - use Independent Provider Strategy
            # Coexist with existing observability systems
            strategy = IntegrationStrategy.INDEPENDENT_PROVIDER
            safe_log(
                self.tracer_instance,
                "debug",
                "Using Independent Provider Strategy - functioning provider detected",
                honeyhive_data={
                    "provider_type": provider_type.value,
                    "strategy": "independent_provider",
                    "reason": "functioning_provider_exists",
                },
            )
        else:
            # Non-functioning provider - use Main Provider Strategy
            # Replace empty providers to prevent instrumentor span loss
            strategy = IntegrationStrategy.MAIN_PROVIDER
            safe_log(
                self.tracer_instance,
                "debug",
                "Using Main Provider Strategy - non-functioning provider detected",
                honeyhive_data={
                    "provider_type": provider_type.value,
                    "strategy": "main_provider",
                    "reason": "non_functioning_provider",
                },
            )

        safe_log(
            self.tracer_instance,
            "debug",
            "Integration strategy determined",
            honeyhive_data={
                "provider_type": provider_type.value,
                "strategy": strategy.value,
            },
        )

        return strategy

    def _get_base_strategy_dynamically(
        self, provider_type: ProviderType
    ) -> IntegrationStrategy:
        """Dynamically get base integration strategy.

        Args:
            provider_type: The provider type

        Returns:
            IntegrationStrategy: Base integration strategy
        """
        return self._strategy_rules.get(
            provider_type, IntegrationStrategy.INDEPENDENT_PROVIDER
        )

    def _refine_tracer_provider_strategy_dynamically(
        self, _base_strategy: IntegrationStrategy
    ) -> IntegrationStrategy:
        """Dynamically refine strategy for TracerProvider based on functionality.

        Args:
            base_strategy: Base integration strategy

        Returns:
            IntegrationStrategy: Refined integration strategy
        """
        existing_provider = trace.get_tracer_provider()

        if self._is_functioning_tracer_provider_dynamically(existing_provider):
            # Functioning TracerProvider - maintain independence
            return IntegrationStrategy.INDEPENDENT_PROVIDER

        # Empty TracerProvider - become main provider to capture instrumentor spans
        return IntegrationStrategy.MAIN_PROVIDER

    def _is_functioning_tracer_provider_dynamically(self, provider: Any) -> bool:
        """Dynamically check if TracerProvider is functioning.

        Args:
            provider: The provider instance to check

        Returns:
            bool: True if provider has active processors/exporters
        """
        # Dynamic functionality detection patterns
        functionality_checks = [
            self._has_active_span_processor_dynamically,
            self._has_composite_processors_dynamically,
        ]

        # Apply functionality checks dynamically
        for check in functionality_checks:
            try:
                if check(provider):
                    return True
            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Functionality check failed",
                    honeyhive_data={
                        "check": check.__name__,
                        "error": str(e),
                    },
                )
                continue

        return False

    def _has_active_span_processor_dynamically(self, provider: Any) -> bool:
        """Dynamically check for active span processor.

        Args:
            provider: Provider to check

        Returns:
            bool: True if has active span processor
        """
        if not hasattr(provider, "_active_span_processor"):
            return False

        active_processor = getattr(provider, "_active_span_processor", None)
        return active_processor is not None

    def _has_composite_processors_dynamically(self, provider: Any) -> bool:
        """Dynamically check for composite processors.

        Args:
            provider: Provider to check

        Returns:
            bool: True if has composite processors
        """
        if not hasattr(provider, "_active_span_processor"):
            return False

        active_processor = getattr(provider, "_active_span_processor", None)
        if active_processor is None:
            return False

        if hasattr(active_processor, "_span_processors"):
            processors = getattr(active_processor, "_span_processors", [])
            return len(processors) > 0

        return False

    def can_add_span_processor(self) -> bool:
        """Dynamically check if the current provider supports adding span processors.

        Returns:
            bool: True if span processors can be added
        """
        existing_provider = trace.get_tracer_provider()

        # Dynamic capability detection
        capability_checks = [
            lambda p: hasattr(p, "add_span_processor"),
            lambda p: hasattr(p, "_active_span_processor"),
        ]

        return any(check(existing_provider) for check in capability_checks)

    def get_provider_info(self) -> Dict[str, Any]:
        """Dynamically gather comprehensive provider information.

        Returns:
            dict: Provider information including type, name, and capabilities
        """
        existing_provider = trace.get_tracer_provider()
        provider_type = self.detect_provider_type()
        integration_strategy = self.get_integration_strategy(provider_type)

        # Dynamic information gathering
        info = {
            "provider_instance": existing_provider,
            "provider_class_name": type(existing_provider).__name__,
            "provider_type": provider_type,
            "integration_strategy": integration_strategy,
            "supports_span_processors": self.can_add_span_processor(),
            "is_replaceable": self._is_replaceable_dynamically(provider_type),
            "is_functioning": _is_functioning_tracer_provider(
                existing_provider, self.tracer_instance
            ),
        }

        # Dynamic capability assessment
        info.update(self._assess_capabilities_dynamically(existing_provider))

        return info

    def _is_replaceable_dynamically(self, provider_type: ProviderType) -> bool:
        """Dynamically determine if provider is replaceable.

        Args:
            provider_type: The provider type

        Returns:
            bool: True if provider can be safely replaced
        """
        replaceable_types = {ProviderType.NOOP, ProviderType.PROXY_TRACER_PROVIDER}
        return provider_type in replaceable_types

    def _assess_capabilities_dynamically(self, provider: Any) -> Dict[str, Any]:
        """Dynamically assess provider capabilities.

        Args:
            provider: Provider to assess

        Returns:
            dict: Capability assessment results
        """
        capabilities = {}

        # Dynamic capability assessment patterns
        capability_assessments = [
            ("has_span_processors", lambda p: hasattr(p, "_active_span_processor")),
            ("has_resource", lambda p: hasattr(p, "resource")),
            ("has_sampler", lambda p: hasattr(p, "_sampler")),
            ("is_shutdown", lambda p: getattr(p, "_shutdown", False)),
        ]

        for capability_name, assessment_func in capability_assessments:
            try:
                capabilities[capability_name] = assessment_func(provider)
            except Exception:
                capabilities[capability_name] = False

        return capabilities


def detect_provider_integration_strategy() -> IntegrationStrategy:
    """Dynamically detect existing provider and determine integration strategy.

    This is a convenience function that combines provider detection
    and strategy selection in a single call using dynamic logic.

    Returns:
        IntegrationStrategy: The recommended integration strategy
    """
    detector = ProviderDetector()
    return detector.get_integration_strategy()


def is_noop_or_proxy_provider(provider: Any) -> bool:
    """Dynamically check if provider is NoOp, Proxy, or equivalent placeholder.

    Args:
        provider: The provider instance to check

    Returns:
        bool: True if provider is a placeholder that can be safely replaced
    """
    detector = ProviderDetector()
    provider_type = detector._classify_provider_dynamically(provider)
    return provider_type in {ProviderType.NOOP, ProviderType.PROXY_TRACER_PROVIDER}


def atomic_provider_detection_and_setup(
    tracer_instance: Any = None,
    span_limits: Optional[Any] = None,
) -> Tuple[str, Optional[Any], Dict[str, Any]]:
    """Atomically detect provider and set up new provider if needed.

    This function prevents race conditions by performing provider detection
    and provider creation/setting in a single atomic operation under a lock.

    Returns:
        Tuple containing:
        - strategy: "main_provider" or "independent_provider"
        - provider: New TracerProvider if main, None if independent
        - info: Provider information dictionary
    """
    with _provider_detection_lock:
        safe_log(
            tracer_instance,
            "debug",
            "Acquired provider detection lock for atomic operation",
        )

        # Step 1: Detect current provider state
        detector = ProviderDetector(tracer_instance=tracer_instance)
        provider_info = detector.get_provider_info()
        current_provider = provider_info["provider_instance"]

        # Step 2: Check if current provider is a real TracerProvider (not NoOp/Proxy)
        provider_type = provider_info["provider_type"]
        is_real_provider = provider_type not in {
            ProviderType.NOOP,
            ProviderType.PROXY_TRACER_PROVIDER,
        }

        if is_real_provider:
            # Functioning provider exists - use Independent Provider Strategy
            safe_log(
                tracer_instance,
                "debug",
                "Atomic detection: functioning provider exists, using independent",
                honeyhive_data={
                    "provider_type": provider_info["provider_class_name"],
                    "strategy": "independent_provider",
                    "is_real_provider": True,
                    "provider_id": id(current_provider),
                    "provider_details": str(current_provider)[:100],
                },
            )

            safe_log(
                tracer_instance,
                "debug",
                "🔍 DEBUG: Provider detection decision details",
                honeyhive_data={
                    "current_provider_type": provider_type,
                    "excluded_types": [
                        ProviderType.NOOP,
                        ProviderType.PROXY_TRACER_PROVIDER,
                    ],
                    "is_real_check": (
                        f"{provider_type} not in "
                        f"{[ProviderType.NOOP, ProviderType.PROXY_TRACER_PROVIDER]}"
                    ),
                    "decision": "independent_provider",
                },
            )
            return "independent_provider", None, provider_info

        # Non-functioning provider - create new provider and set as global
        safe_log(
            tracer_instance,
            "debug",
            "Atomic detection: non-functioning provider, creating new main",
            honeyhive_data={
                "provider_type": provider_info["provider_class_name"],
                "strategy": "main_provider",
                "is_real_provider": False,
            },
        )

        # Step 3: Create new TracerProvider with span limits
        if span_limits:
            new_provider = TracerProvider(span_limits=span_limits)
            safe_log(
                tracer_instance,
                "debug",
                "Creating TracerProvider with custom span limits",
                honeyhive_data={
                    "max_attributes": (
                        span_limits.max_attributes
                        if hasattr(span_limits, "max_attributes")
                        else "unknown"
                    ),
                },
            )
        else:
            new_provider = TracerProvider()
            safe_log(
                tracer_instance,
                "debug",
                "Creating TracerProvider with default span limits",
            )

        # Step 4: Immediately set as global provider (atomic with detection)
        try:
            # Use set_global_provider which handles SET_ONCE flag reset
            set_global_provider(new_provider, tracer_instance=tracer_instance)
            safe_log(
                tracer_instance,
                "info",
                "Atomically set new TracerProvider as global provider",
                honeyhive_data={
                    "replaced_provider": provider_info["provider_class_name"],
                    "new_provider": "TracerProvider",
                    "atomic_operation": True,
                },
            )

            # Update provider info to reflect the new state
            provider_info["provider_instance"] = new_provider
            provider_info["provider_class_name"] = "TracerProvider"
            provider_info["integration_strategy"] = IntegrationStrategy.MAIN_PROVIDER
            provider_info["is_functioning"] = True

            return "main_provider", new_provider, provider_info

        except Exception as e:
            safe_log(
                tracer_instance,
                "warning",
                "Failed to set global provider atomically, using independent",
                honeyhive_data={
                    "error": str(e),
                    "fallback_strategy": "independent_provider",
                },
            )
            return "independent_provider", None, provider_info


def _is_functioning_tracer_provider(
    provider: Any = None, tracer_instance: Any = None
) -> bool:
    """Check if TracerProvider is functioning (has active processors/exporters).

    This implements the Provider Strategy Intelligence from Agent OS decisions:
    - Functioning providers have span processors that can handle instrumentor spans
    - Non-functioning providers (NoOp/Proxy/Empty) will lose instrumentor spans
    - Critical: Someone must process instrumentor spans to prevent data loss

    Args:
        provider: TracerProvider to check, defaults to global provider

    Returns:
        True if provider is functioning (has processors), False otherwise
    """
    if provider is None:
        provider = trace.get_tracer_provider()

    try:
        # Check if provider has active span processor (OpenTelemetry SDK pattern)
        if hasattr(provider, "_active_span_processor"):
            processor = getattr(provider, "_active_span_processor", None)
            if processor is not None:
                # Check if processor has exporters (truly functioning)
                has_exporters = _processor_has_exporters(processor, tracer_instance)
                safe_log(
                    tracer_instance,
                    "debug",
                    f"Provider span processor check - has exporters: {has_exporters}",
                    honeyhive_data={
                        "provider_type": type(provider).__name__,
                        "processor_type": type(processor).__name__,
                        "has_exporters": has_exporters,
                        "strategy": (
                            "independent_provider" if has_exporters else "main_provider"
                        ),
                    },
                )
                return has_exporters

        # Check if provider has span processors list (alternative pattern)
        if hasattr(provider, "_span_processors"):
            processors = getattr(provider, "_span_processors", [])
            if processors:
                safe_log(
                    tracer_instance,
                    "debug",
                    "Provider is functioning - has span processors",
                    honeyhive_data={
                        "provider_type": type(provider).__name__,
                        "processor_count": len(processors),
                        "strategy": "independent_provider",
                    },
                )
                return True

        # Check if provider has add_span_processor method (can have processors)
        if hasattr(provider, "add_span_processor"):
            # If it has the method but no active processor, might be empty
            # We need to be more conservative here - only consider it functioning
            # if it actually has processors
            pass

        # Check for other indicators of functioning provider
        provider_type = type(provider).__name__
        if provider_type in ["NoOpTracerProvider", "ProxyTracerProvider"]:
            safe_log(
                tracer_instance,
                "debug",
                "Provider is non-functioning - placeholder provider",
                honeyhive_data={
                    "provider_type": provider_type,
                    "strategy": "main_provider",
                },
            )
            return False

        # If it's a real TracerProvider but no processors, it's empty (non-functioning)
        safe_log(
            tracer_instance,
            "debug",
            "Provider is non-functioning - no span processors",
            honeyhive_data={
                "provider_type": provider_type,
                "strategy": "main_provider",
            },
        )
        return False

    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            f"Error checking provider functionality: {e}",
            honeyhive_data={
                "provider_type": type(provider).__name__,
                "error": str(e),
                "strategy": "main_provider",  # Default to main provider on error
            },
        )
        return False


def set_global_provider(
    provider: Any, force_override: bool = False, tracer_instance: Any = None
) -> None:
    """Dynamically set the global OpenTelemetry tracer provider.

    This function properly handles OpenTelemetry's internal warnings when
    setting a tracer provider, using dynamic provider management techniques.

    Args:
        provider: The TracerProvider instance to set as global
        force_override: If True, allows overriding existing real providers
                       (intended for test utilities and clean state management)
        tracer_instance: Optional tracer instance for logging context

    Example:
        >>> from opentelemetry.sdk.trace import TracerProvider
        >>> from honeyhive.tracer.integration import set_global_provider
        >>> provider = TracerProvider()
        >>> set_global_provider(provider)

        # For test utilities - force override existing provider
        >>> set_global_provider(NoOpTracerProvider(), force_override=True)
    """
    try:
        # Check if a provider is already set to avoid the override warning
        current_provider = trace.get_tracer_provider()
        provider_type = type(current_provider).__name__

        # Determine if we should set the provider
        should_set = False
        reason = ""

        if provider_type in ["NoOpTracerProvider", "ProxyTracerProvider"]:
            # Safe to set as global provider - no real provider exists
            should_set = True
            reason = "no_real_provider_exists"
            # Reset SET_ONCE flag for both NoOp and Proxy providers
            # Both set the flag but should be replaceable
            _reset_provider_flag_dynamically(tracer_instance)
        elif force_override:
            # Force override requested (for test utilities)
            should_set = True
            reason = "force_override_requested"
            # Reset the SET_ONCE flag to allow clean override
            _reset_provider_flag_dynamically(tracer_instance)
        else:
            # Another real provider exists and no force override
            should_set = False
            reason = "real_provider_exists_no_force"

        if should_set:
            _set_tracer_provider(provider, log=False)
            safe_log(
                tracer_instance,
                "debug",
                "Global provider set successfully",
                honeyhive_data={
                    "provider_class": type(provider).__name__,
                    "replaced_provider": provider_type,
                    "reason": reason,
                    "force_override": force_override,
                },
            )
        else:
            # Another real provider is already set, don't override
            safe_log(
                tracer_instance,
                "debug",
                "Real TracerProvider already exists, skipping global provider set",
                honeyhive_data={
                    "existing_provider": provider_type,
                    "requested_provider": type(provider).__name__,
                    "reason": reason,
                    "force_override": force_override,
                },
            )

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to set global provider",
            honeyhive_data={
                "provider_class": type(provider).__name__,
                "error": str(e),
            },
        )
        raise


def _reset_provider_flag_dynamically(tracer_instance: Any = None) -> None:
    """Dynamically reset the provider SET_ONCE flag for testing scenarios."""
    try:
        # Reset the SET_ONCE flag to allow provider override
        if hasattr(trace, "_TRACER_PROVIDER_SET_ONCE"):
            trace._TRACER_PROVIDER_SET_ONCE._done = False
    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Could not reset provider flag",
            honeyhive_data={"error": str(e)},
        )


def get_global_provider(tracer_instance: Any = None) -> Any:
    """Dynamically get the current global OpenTelemetry tracer provider.

    Returns:
        The current global TracerProvider instance

    Example:
        >>> from honeyhive.tracer.integration import get_global_provider
        >>> provider = get_global_provider()
    """
    provider = trace.get_tracer_provider()

    safe_log(
        tracer_instance,
        "debug",
        "Retrieved global provider",
        honeyhive_data={
            "provider_class": type(provider).__name__,
        },
    )

    return provider


def _processor_has_exporters(processor: Any, tracer_instance: Any = None) -> bool:
    """Check if a span processor has exporters configured.

    A span processor without exporters is effectively non-functioning
    because spans have nowhere to go.

    Args:
        processor: Span processor to check

    Returns:
        True if processor has exporters, False otherwise
    """
    try:
        # Check for MultiSpanProcessor (has _span_processors list)
        if hasattr(processor, "_span_processors"):
            processors = getattr(processor, "_span_processors", [])
            safe_log(
                tracer_instance,
                "debug",
                f"🔍 DEBUG: MultiSpanProcessor has {len(processors)} processors",
                honeyhive_data={
                    "processor_type": type(processor).__name__,
                    "processor_count": len(processors),
                    "processor_types": [type(p).__name__ for p in processors],
                },
            )

            # Check each processor for exporters
            for sub_processor in processors:
                if _single_processor_has_exporter(sub_processor, tracer_instance):
                    return True
            return False

        # Check single processor
        return _single_processor_has_exporter(processor, tracer_instance)

    except Exception as e:
        safe_log(tracer_instance, "debug", f"Error checking processor exporters: {e}")
        return False


def _single_processor_has_exporter(processor: Any, tracer_instance: Any = None) -> bool:
    """Check if a single span processor has an exporter.

    Args:
        processor: Single span processor to check

    Returns:
        True if processor has an exporter, False otherwise
    """
    try:
        # Check for BatchSpanProcessor or SimpleSpanProcessor
        if hasattr(processor, "span_exporter"):
            exporter = getattr(processor, "span_exporter", None)
            has_exporter = exporter is not None
            safe_log(
                tracer_instance,
                "debug",
                "🔍 DEBUG: Processor exporter check",
                honeyhive_data={
                    "processor_type": type(processor).__name__,
                    "has_exporter": has_exporter,
                    "exporter_type": type(exporter).__name__ if exporter else None,
                },
            )
            return has_exporter

        # Check for _exporter attribute (alternative pattern)
        if hasattr(processor, "_exporter"):
            exporter = getattr(processor, "_exporter", None)
            has_exporter = exporter is not None
            safe_log(
                tracer_instance,
                "debug",
                "🔍 DEBUG: Processor _exporter check",
                honeyhive_data={
                    "processor_type": type(processor).__name__,
                    "has_exporter": has_exporter,
                    "exporter_type": type(exporter).__name__ if exporter else None,
                },
            )
            return has_exporter

        safe_log(
            tracer_instance,
            "debug",
            "🔍 DEBUG: No exporter attributes found on processor",
            honeyhive_data={
                "processor_type": type(processor).__name__,
                "processor_attrs": [
                    attr for attr in dir(processor) if not attr.startswith("__")
                ],
            },
        )
        return False

    except Exception as e:
        safe_log(
            tracer_instance, "debug", f"Error checking single processor exporter: {e}"
        )
        return False
