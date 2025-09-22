"""Integration framework for HoneyHive tracer with external systems.

This module provides dynamic integration capabilities for OpenTelemetry providers,
error handling, compatibility layers, and HTTP instrumentation. All components
use dynamic logic patterns for flexible, extensible integration strategies.
"""

# Compatibility layer
from .compatibility import enrich_session

# Provider detection and integration
from .detection import (
    IntegrationStrategy,
    ProviderDetector,
    ProviderType,
    get_global_provider,
    set_global_provider,
)

# Error handling and resilience
from .error_handling import (
    ErrorHandler,
    IntegrationError,
)
from .error_handling import ProviderIncompatibleError as ErrorProviderIncompatibleError
from .error_handling import (
    ResilienceLevel,
    with_error_handling,
)

# HTTP instrumentation
from .http import HTTPInstrumentation

# Processor integration
from .processor import (
    ProcessorIntegrationError,
    ProcessorIntegrator,
    ProviderIncompatibleError,
)

__all__ = [
    # Detection
    "IntegrationStrategy",
    "ProviderDetector",
    "ProviderType",
    "get_global_provider",
    "set_global_provider",
    # Processor integration
    "ProcessorIntegrationError",
    "ProcessorIntegrator",
    "ProviderIncompatibleError",
    # Error handling
    "ErrorHandler",
    "IntegrationError",
    "ErrorProviderIncompatibleError",
    "ResilienceLevel",
    "with_error_handling",
    # Compatibility
    "enrich_session",
    # HTTP instrumentation
    "HTTPInstrumentation",
]
