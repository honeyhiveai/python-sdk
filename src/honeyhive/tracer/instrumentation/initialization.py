"""Tracer initialization and OpenTelemetry setup functionality.

This module handles the complex initialization process for HoneyHive tracers,
including OpenTelemetry provider detection, configuration, and session setup.
It implements the multi-instance architecture with proper provider integration.
"""

# pylint: disable=duplicate-code
# Agent OS graceful degradation error handling patterns are intentionally consistent

import inspect
import os
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

from ...api.client import HoneyHive
from ...api.session import SessionAPI

# Removed get_config import - using per-instance configuration instead
from ...utils.logger import get_tracer_logger, safe_log
from .. import registry
from ..integration.detection import (
    atomic_provider_detection_and_setup,
    set_global_provider,
)
from ..processing.context import setup_baggage_context
from ..processing.otlp_exporter import HoneyHiveOTLPExporter
from ..processing.otlp_profiles import get_environment_optimized_config
from ..processing.otlp_session import (
    OTLPSessionConfig,
    create_dynamic_otlp_config,
    get_default_otlp_config,
)
from ..processing.span_processor import HoneyHiveSpanProcessor

if TYPE_CHECKING:
    from ..core import HoneyHiveTracer
    from ..core.base import HoneyHiveTracerBase

# pylint: disable=protected-access,too-many-lines
# Protected access needed for tracer initialization and state management
# too-many-lines disabled due to extensive informative docstrings


# Dynamic logger - will be created per tracer instance
def _get_logger_for_tracer(tracer_instance: Any) -> Any:
    """Get a logger configured for the specific tracer instance."""
    return get_tracer_logger(tracer_instance, "honeyhive.tracer.initialization")


def _create_tracer_provider_with_resources(tracer_instance: Any) -> TracerProvider:
    """Create TracerProvider with dynamic resource detection and caching.

    Args:
        tracer_instance: The tracer instance to create provider for

    Returns:
        TracerProvider configured with detected resources
    """
    try:
        # Use cached resource detection if available
        if hasattr(tracer_instance, "_detect_resources_with_cache"):
            resource_attributes = tracer_instance._detect_resources_with_cache()
            safe_log(
                tracer_instance,
                "debug",
                f"Creating TracerProvider with {len(resource_attributes)} resources",
            )
        else:
            # Fallback to minimal resources if detection not available
            resource_attributes = {
                "service.name": getattr(
                    tracer_instance, "project", "honeyhive-service"
                ),
                "service.instance.id": str(id(tracer_instance)),
            }
            safe_log(
                tracer_instance,
                "debug",
                "Creating TracerProvider with minimal resources (no detection)",
            )

        # Create Resource from detected attributes
        resource = Resource.create(resource_attributes)

        # Create TracerProvider with resource (span limits already applied
        # via atomic detection)
        provider = TracerProvider(resource=resource)

        safe_log(
            tracer_instance,
            "debug",
            "TracerProvider created with resource detection",
            honeyhive_data={
                "resource_count": len(resource_attributes),
                "service_name": resource_attributes.get("service.name", "unknown"),
                "cached": hasattr(tracer_instance, "_detect_resources_with_cache"),
            },
        )

        return provider

    except Exception as e:
        # Graceful degradation - create provider without resources if detection fails
        safe_log(
            tracer_instance,
            "warning",
            f"Resource detection failed, creating provider without resources: {e}",
        )
        return TracerProvider()


# Config values accessed directly from tracer.config DotDict


def initialize_tracer_instance(tracer_instance: "HoneyHiveTracerBase") -> None:
    """Initialize a HoneyHiveTracer instance with full setup.

    This function handles the complete initialization process for a tracer
    instance, including OpenTelemetry setup, session creation, and provider
    configuration. It's called by the HoneyHiveTracer.init() class method.

    :param tracer_instance: The tracer instance to initialize
    :type tracer_instance: HoneyHiveTracer
    :note: Uses graceful degradation - never crashes host application
    :note: Missing configuration triggers degraded mode with warnings
    :note: API failures result in no-op mode with local fallback

    **Example:**

    .. code-block:: python

        tracer = HoneyHiveTracer(api_key="key", project="project")
        initialize_tracer_instance(tracer)
        # Tracer is now fully initialized and ready to use

    **Note:**

    This function modifies the tracer instance in-place and should only
    be called once per tracer instance during initialization.
    """
    # Multi-instance logging architecture uses safe_log utility
    # No need to attach logger directly to tracer instance

    # Enable debug logging if verbose mode is requested
    if getattr(tracer_instance, "verbose", False):
        # Verbose logging is handled by the tracer's logger.update_verbose_setting()
        # in the tracer initialization - no need for direct logging module calls here
        safe_log(
            tracer_instance,
            "debug",
            "Verbose logging enabled for HoneyHive tracer initialization",
        )

    safe_log(
        tracer_instance,
        "debug",
        "Starting tracer initialization",
        honeyhive_data={
            "project": tracer_instance.project_name,
            "source": tracer_instance.source_environment,
            "test_mode": tracer_instance.test_mode,
        },
    )

    # Configuration already loaded and validated during tracer init

    # Step 2: Initialize OpenTelemetry components
    _initialize_otel_components(tracer_instance)

    # Step 3: Initialize session management
    _initialize_session_management(tracer_instance)

    # Step 4: Register tracer for auto-discovery (assigns _tracer_id)
    _register_tracer_instance(tracer_instance)

    # Step 5: Setup baggage context (after registration so _tracer_id is available)
    _setup_baggage_context(tracer_instance)

    # Mark as initialized
    tracer_instance._initialized = True

    safe_log(
        tracer_instance,
        "info",
        "Tracer initialization completed successfully",
        honeyhive_data={
            "project": tracer_instance.project_name,
            "session_id": tracer_instance.session_id,
            "is_main_provider": tracer_instance.is_main_provider,
        },
    )

    # Clean up the temporary initialization logger
    # The tracer has its own logger (tracer_instance.logger) for runtime use
    if hasattr(tracer_instance, "logger"):
        delattr(tracer_instance, "logger")


def _load_configuration(tracer_instance: Any) -> None:
    """Load and validate tracer configuration from environment variables.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :note: Uses graceful degradation for missing configuration
    """
    # Configuration is available via tracer_instance.config DotDict
    # No need to flatten config values to tracer attributes

    # Validate configuration with graceful degradation
    _validate_configuration_gracefully(tracer_instance)

    # Enhanced configuration debug logging for troubleshooting

    # Collect all relevant configuration values (with safe access)
    config_debug = {
        # Core tracer settings
        "project": tracer_instance.project_name,
        "source": tracer_instance.source_environment,
        "server_url": tracer_instance.config.server_url,
        "has_api_key": bool(tracer_instance.config.api_key),
        "test_mode": tracer_instance.test_mode,
        "verbose": getattr(tracer_instance, "verbose", False),
        # Environment variables (critical for debugging)
        "env_HH_OTLP_ENABLED": os.getenv("HH_OTLP_ENABLED"),
        "env_HH_TEST_MODE": os.getenv("HH_TEST_MODE"),
        "env_HH_API_KEY": (
            f"{os.getenv('HH_API_KEY', '')[:10]}..."
            if os.getenv("HH_API_KEY")
            else None
        ),
        "env_HH_PROJECT": os.getenv("HH_PROJECT"),
        "env_HH_SOURCE": os.getenv("HH_SOURCE"),
        "env_HH_DISABLE_HTTP_TRACING": os.getenv("HH_DISABLE_HTTP_TRACING"),
        "env_HH_BATCH_SIZE": os.getenv("HH_BATCH_SIZE"),
        "env_HH_FLUSH_INTERVAL": os.getenv("HH_FLUSH_INTERVAL"),
        # Tracer instance settings
        "disable_batch": getattr(tracer_instance, "disable_batch", None),
        "disable_http_tracing": getattr(tracer_instance, "disable_http_tracing", None),
        "session_name": getattr(tracer_instance, "session_name", None),
    }

    # Safely access config values using dynamic logic (config and legacy attributes)
    # Debug logging removed - config already validated during init

    safe_log(
        tracer_instance,
        "debug",
        "Configuration loaded and validated",
        honeyhive_data=config_debug,
    )


def _initialize_otel_components(tracer_instance: Any) -> None:
    """Initialize OpenTelemetry components using atomic provider detection.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :note: Uses thread-safe atomic provider detection to prevent race conditions
    """
    # Get user-configured span limits from tracer config BEFORE provider creation
    max_attributes = getattr(tracer_instance.config, "max_attributes", 1024)
    max_events = getattr(tracer_instance.config, "max_events", 1024)
    max_links = getattr(tracer_instance.config, "max_links", 128)
    max_span_size = getattr(
        tracer_instance.config, "max_span_size", 10 * 1024 * 1024
    )  # 10MB

    # Store max_span_size on tracer instance for span processor access
    # (OTel doesn't support total span size limits natively)
    tracer_instance._max_span_size = max_span_size

    # Create SpanLimits to pass to provider creation
    # Note: max_span_size is NOT in SpanLimits - it's enforced separately
    # in span processor
    span_limits = SpanLimits(
        max_attributes=max_attributes,
        max_events=max_events,
        max_links=max_links,
    )

    # Use atomic provider detection to prevent race conditions
    # Pass span_limits so new providers are created with correct limits
    strategy_name, main_provider, provider_info = atomic_provider_detection_and_setup(
        tracer_instance=tracer_instance, span_limits=span_limits
    )

    safe_log(
        tracer_instance,
        "debug",
        "Atomic provider detection completed",
        honeyhive_data={
            "provider_class": provider_info["provider_class_name"],
            "strategy": strategy_name,
            "atomic_operation": True,
            "max_attributes": max_attributes,
        },
    )

    # Create OTLP exporter first (needed by HoneyHiveSpanProcessor)
    otlp_exporter = _create_otlp_exporter(tracer_instance)
    # Store on tracer instance for later access
    tracer_instance.otlp_exporter = otlp_exporter

    if strategy_name == "main_provider":
        # Provider already created and set as global in atomic operation
        tracer_instance.provider = main_provider
        tracer_instance.is_main_provider = True
        _setup_main_provider_components(tracer_instance, provider_info, otlp_exporter)
    else:  # "independent_provider"
        _setup_independent_provider(tracer_instance, provider_info, otlp_exporter)

    # Setup propagators
    _setup_propagators(tracer_instance)

    # Create tracer instance (no longer needs to set global provider)
    _create_tracer_instance(tracer_instance)


def _setup_main_provider_components(
    tracer_instance: Any,
    provider_info: Dict[str, Any],
    otlp_exporter: Optional[Any] = None,
) -> None:
    """Setup components for main provider (provider already created and set as global).

    This function is called when the atomic provider detection has already
    created and set the TracerProvider as global. We just need to add components.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :param provider_info: Provider detection information
    :type provider_info: Dict[str, Any]
    :param otlp_exporter: OTLP exporter instance
    :type otlp_exporter: Optional[Any]
    """
    safe_log(
        tracer_instance,
        "info",
        "Setting up components for main provider (already set as global)",
        honeyhive_data={
            "replaced_provider": provider_info.get(
                "original_provider_class", "Unknown"
            ),
            "reason": "atomic_provider_detection",
            "thread_safe": True,
        },
    )

    # Add span processor to the existing provider
    try:
        tracer_instance.span_processor = HoneyHiveSpanProcessor(
            client=getattr(tracer_instance, "client", None),
            disable_batch=getattr(tracer_instance, "disable_batch", False),
            otlp_exporter=otlp_exporter,
            tracer_instance=tracer_instance,
        )
        tracer_instance.provider.add_span_processor(tracer_instance.span_processor)
        safe_log(
            tracer_instance,
            "info",
            "Added HoneyHive span processor to main provider",
            honeyhive_data={
                "span_processor_type": type(tracer_instance.span_processor).__name__,
                "provider_type": type(tracer_instance.provider).__name__,
                "tracer_instance_id": id(tracer_instance),
                "span_processor_tracer_instance": (
                    id(tracer_instance.span_processor.tracer_instance)
                    if tracer_instance.span_processor.tracer_instance
                    else None
                ),
                "provider_processors_count": (
                    len(
                        tracer_instance.provider._active_span_processor._span_processors
                    )
                    if hasattr(tracer_instance.provider, "_active_span_processor")
                    else "unknown"
                ),
            },
        )

        safe_log(
            tracer_instance,
            "debug",
            "🔍 DEBUG: Main provider span processor registration details",
            honeyhive_data={
                "provider_id": id(tracer_instance.provider),
                "span_processor_id": id(tracer_instance.span_processor),
                "tracer_instance_session_id": getattr(
                    tracer_instance, "session_id", "not_set"
                ),
                "span_processor_has_tracer_instance": hasattr(
                    tracer_instance.span_processor, "tracer_instance"
                ),
                "span_processor_tracer_session_id": (
                    getattr(
                        tracer_instance.span_processor.tracer_instance,
                        "session_id",
                        "not_available",
                    )
                    if hasattr(tracer_instance.span_processor, "tracer_instance")
                    and tracer_instance.span_processor.tracer_instance
                    else "no_tracer_instance"
                ),
            },
        )
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Failed to integrate HoneyHive span processor: %s",
            str(e),
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "span_processor_integration",
                "error_details": str(e),
            },
        )


def _setup_main_provider(
    tracer_instance: Any,
    provider_info: Dict[str, Any],
    otlp_exporter: Optional[Any] = None,
) -> None:
    """Setup tracer as the main (global) OpenTelemetry provider.

    DEPRECATED: This function is kept for backward compatibility but should
    not be used with the new atomic provider detection system.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :param provider_info: Provider detection information
    :type provider_info: Dict[str, Any]
    """
    safe_log(
        tracer_instance,
        "warning",
        "Using deprecated _setup_main_provider - should use atomic detection",
        honeyhive_data={"deprecated_function": "_setup_main_provider"},
    )

    # Create new TracerProvider for this process with resource detection
    tracer_instance.provider = _create_tracer_provider_with_resources(tracer_instance)
    tracer_instance.is_main_provider = True

    safe_log(
        tracer_instance,
        "info",
        "Creating new TracerProvider as main (global) provider",
        honeyhive_data={
            "replaced_provider": provider_info["provider_class_name"],
            "reason": "no_functioning_provider",
            "thread_safe": True,
        },
    )

    # Add span processor with proper configuration
    try:
        tracer_instance.span_processor = HoneyHiveSpanProcessor(
            client=getattr(tracer_instance, "client", None),
            disable_batch=getattr(tracer_instance, "disable_batch", False),
            otlp_exporter=otlp_exporter,
            tracer_instance=tracer_instance,
        )
        tracer_instance.provider.add_span_processor(tracer_instance.span_processor)
        safe_log(
            tracer_instance, "info", "Added HoneyHive span processor to new provider"
        )
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "debug",
            "Integrating HoneyHive span processor",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "span_processor_integration",
            },
        )


def _setup_independent_provider(
    tracer_instance: Any,
    provider_info: Dict[str, Any],
    otlp_exporter: Optional[Any] = None,
) -> None:
    """Setup tracer as isolated instance with independent provider.

    Multi-Instance Architecture: HoneyHive creates its own TracerProvider
    with our processor and exporter, but doesn't become the global provider.
    This ensures complete isolation from other instrumentors while still
    capturing spans through our independent tracer instance.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :param provider_info: Provider detection information
    :type provider_info: Dict[str, Any]
    :param otlp_exporter: OTLP exporter instance
    :type otlp_exporter: Optional[Any]
    """
    # Create NEW isolated TracerProvider with resource detection (multi-instance arch)
    tracer_instance.provider = _create_tracer_provider_with_resources(tracer_instance)
    tracer_instance.is_main_provider = False  # Don't become global provider

    safe_log(
        tracer_instance,
        "info",
        "Creating isolated TracerProvider (multi-instance architecture)",
        honeyhive_data={
            "existing_provider": provider_info["provider_class_name"],
            "integration_mode": "isolated_instance",
            "is_functioning": provider_info.get("is_functioning", False),
        },
    )

    # Add span processor to OUR isolated provider with proper configuration
    try:
        tracer_instance.span_processor = HoneyHiveSpanProcessor(
            client=getattr(tracer_instance, "client", None),
            disable_batch=getattr(tracer_instance, "disable_batch", False),
            otlp_exporter=otlp_exporter,
            tracer_instance=tracer_instance,
        )
        tracer_instance.provider.add_span_processor(tracer_instance.span_processor)
        safe_log(
            tracer_instance,
            "info",
            "Added HoneyHive span processor to isolated provider",
            honeyhive_data={
                "span_processor_type": type(tracer_instance.span_processor).__name__,
                "provider_type": type(tracer_instance.provider).__name__,
                "tracer_instance_id": id(tracer_instance),
                "span_processor_tracer_instance": (
                    id(tracer_instance.span_processor.tracer_instance)
                    if tracer_instance.span_processor.tracer_instance
                    else None
                ),
                "provider_processors_count": (
                    len(
                        tracer_instance.provider._active_span_processor._span_processors
                    )
                    if hasattr(tracer_instance.provider, "_active_span_processor")
                    else "unknown"
                ),
            },
        )

        safe_log(
            tracer_instance,
            "debug",
            "🔍 DEBUG: Independent provider span processor registration details",
            honeyhive_data={
                "provider_id": id(tracer_instance.provider),
                "span_processor_id": id(tracer_instance.span_processor),
                "tracer_instance_session_id": getattr(
                    tracer_instance, "session_id", "not_set"
                ),
                "span_processor_has_tracer_instance": hasattr(
                    tracer_instance.span_processor, "tracer_instance"
                ),
                "span_processor_tracer_session_id": (
                    getattr(
                        tracer_instance.span_processor.tracer_instance,
                        "session_id",
                        "not_available",
                    )
                    if hasattr(tracer_instance.span_processor, "tracer_instance")
                    and tracer_instance.span_processor.tracer_instance
                    else "no_tracer_instance"
                ),
            },
        )
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "debug",
            "Integrating HoneyHive span processor",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "span_processor_integration",
            },
        )


def _setup_console_fallback(
    tracer_instance: Any,
    provider_info: Dict[str, Any],
    otlp_exporter: Optional[Any] = None,  # pylint: disable=unused-argument
) -> None:
    """Setup tracer with console fallback for incompatible providers.

    Used when the existing provider doesn't support span processors.
    HoneyHive operates in degraded mode with limited functionality.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :param provider_info: Provider detection information
    :type provider_info: Dict[str, Any]
    """
    # Provider incompatible - use existing provider but operate in degraded mode
    tracer_instance.provider = provider_info["provider_instance"]
    tracer_instance.is_main_provider = False

    safe_log(
        tracer_instance,
        "warning",
        "Provider doesn't support span processors, operating in degraded mode",
        honeyhive_data={
            "provider_class": provider_info["provider_class_name"],
            "fallback_mode": "console_logging",
            "supports_processors": provider_info.get("supports_span_processors", False),
        },
    )
    tracer_instance.span_processor = None


def _get_optimal_session_config(tracer_instance: Any) -> OTLPSessionConfig:
    """Determine optimal OTLP session configuration using dynamic analysis.

    This function uses dynamic logic to analyze the tracer's actual configuration,
    environment conditions, and usage patterns to create an optimal session
    configuration rather than selecting from predefined static configurations.

    Args:
        tracer_instance: The tracer instance to analyze

    Returns:
        Dynamically optimized OTLPSessionConfig for the tracer's use case
    """
    try:
        # Dynamic analysis of tracer configuration
        batch_size = getattr(tracer_instance.config, "batch_size", 100)
        disable_batch = getattr(tracer_instance, "disable_batch", False)
        verbose = getattr(tracer_instance, "verbose", False)

        # Determine scenario based on dynamic analysis
        scenario = "default"
        scenario_reasons = []

        # High-volume indicators
        if batch_size > 200:
            scenario = "high_volume"
            scenario_reasons.append(f"large_batch_size_{batch_size}")
        elif disable_batch and verbose:
            scenario = "high_volume"
            scenario_reasons.append("immediate_mode_with_verbose_logging")
        # Low-latency indicators
        elif disable_batch and not verbose:
            scenario = "low_latency"
            scenario_reasons.append("immediate_mode_optimized_for_speed")
        else:
            scenario_reasons.append("balanced_performance_requirements")

        # Additional dynamic adjustments based on environment
        env_adjustments = {}

        # Check for test environment
        test_mode = getattr(tracer_instance, "test_mode", False)
        if test_mode:
            env_adjustments.update(
                {
                    "pool_maxsize": 5,  # Smaller pools for testing
                    "timeout": 10.0,  # Shorter timeout for tests
                    "max_retries": 1,  # Fewer retries in tests
                }
            )
            scenario_reasons.append("test_mode_optimizations")

        # Check for high-frequency usage patterns
        session_name = getattr(tracer_instance, "session_name", "") or ""
        if "benchmark" in session_name.lower() or "load" in session_name.lower():
            scenario = "high_volume"
            scenario_reasons.append("performance_testing_detected")

        # Create environment-aware configuration (leverages existing resource detection)
        try:
            config = get_environment_optimized_config(tracer_instance)
            safe_log(
                tracer_instance,
                "info",
                "Using environment-aware OTLP configuration",
                honeyhive_data={
                    "config_source": "environment_profiles",
                    "final_config": config.to_dict(),
                },
            )
        except Exception as e:
            safe_log(
                tracer_instance,
                "warning",
                f"Environment-aware config failed, using dynamic fallback: {e}",
            )
            # Fallback to dynamic configuration
            config = create_dynamic_otlp_config(
                tracer_instance=tracer_instance, scenario=scenario, **env_adjustments
            )

        safe_log(
            tracer_instance,
            "info",
            f"Selected dynamic OTLP session configuration: {scenario}",
            honeyhive_data={
                "scenario": scenario,
                "scenario_reasons": scenario_reasons,
                "batch_size": batch_size,
                "disable_batch": disable_batch,
                "verbose": verbose,
                "test_mode": test_mode,
                "env_adjustments": env_adjustments,
                "final_config": config.to_dict(),
            },
        )

        return config

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            f"Failed to create dynamic session config, using fallback: {e}",
            honeyhive_data={"error_type": type(e).__name__},
        )
        # Fallback to basic dynamic configuration
        return get_default_otlp_config(tracer_instance)


def _create_otlp_exporter(tracer_instance: Any) -> Optional[Any]:
    """Create OTLP exporter for sending spans to HoneyHive backend.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :return: HoneyHiveOTLPExporter instance or None if disabled
    """
    # Get both environment and config values for debugging using dynamic logic
    env_otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true")
    config_otlp_enabled = getattr(tracer_instance.config, "otlp_enabled", None)

    # Use config object value for actual decision (not environment variable)
    otlp_enabled = config_otlp_enabled if config_otlp_enabled is not None else True

    # Enhanced debug logging to show all decision factors
    safe_log(
        tracer_instance,
        "debug",
        "OTLP exporter creation decision",
        honeyhive_data={
            "env_HH_OTLP_ENABLED": env_otlp_enabled,
            "config_otlp_enabled": config_otlp_enabled,
            "computed_otlp_enabled": otlp_enabled,
            "tracer_test_mode": tracer_instance.test_mode,
            "will_create_exporter": otlp_enabled and not tracer_instance.test_mode,
        },
    )

    if not otlp_enabled or tracer_instance.test_mode:
        safe_log(
            tracer_instance,
            "debug",
            "OTLP export disabled (test mode or HH_OTLP_ENABLED=false)",
        )
        return None

    try:
        # Configure custom OTLP exporter to send to backend service using dynamic logic
        server_url = getattr(
            tracer_instance.config, "server_url", "https://api.honeyhive.ai"
        )
        otlp_endpoint = f"{server_url}/opentelemetry/v1/traces"

        # Note: Using per-instance configuration (process-safe)

        # Determine optimal session configuration based on tracer settings
        session_config = _get_optimal_session_config(tracer_instance)

        # Get protocol from config or environment (defaults to http/protobuf)
        otlp_protocol = (
            getattr(tracer_instance.config, "otlp_protocol", None)
            or os.getenv("HH_OTLP_PROTOCOL")
            or os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL")
            or "http/protobuf"
        )

        safe_log(
            tracer_instance,
            "info",
            f"Creating OTLP exporter with protocol: {otlp_protocol}",
            honeyhive_data={
                "protocol": otlp_protocol,
                "endpoint": otlp_endpoint,
                "config_otlp_protocol": getattr(
                    tracer_instance.config, "otlp_protocol", None
                ),
                "env_HH_OTLP_PROTOCOL": os.getenv("HH_OTLP_PROTOCOL"),
                "env_OTEL_EXPORTER_OTLP_PROTOCOL": os.getenv(
                    "OTEL_EXPORTER_OTLP_PROTOCOL"
                ),
            },
        )

        # Use custom exporter with optimized connection pooling
        otlp_exporter = HoneyHiveOTLPExporter(
            tracer_instance=tracer_instance,
            session_config=session_config,
            use_optimized_session=True,
            protocol=otlp_protocol,
            endpoint=otlp_endpoint,
            headers={
                "Authorization": f"Bearer {tracer_instance.config.api_key}",
                "X-Project": tracer_instance.project_name,
                "X-Source": tracer_instance.source_environment,
            },
            timeout=30.0,  # 30 second timeout for exports
        )

        safe_log(tracer_instance, "info", "OTLP exporter created successfully")
        return otlp_exporter

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            None,
            "error",
            f"OTLP exporter initialization failed: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "otlp_exporter_initialization",
            },
        )
        return None


def _setup_propagators(tracer_instance: Any) -> None:
    """Setup OpenTelemetry propagators for context propagation.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    """
    try:
        tracer_instance.propagator = CompositePropagator(
            [
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator(),
            ]
        )
        safe_log(tracer_instance, "debug", "Propagators configured successfully")
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "warning",
            f"Failed to setup propagators: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "setup_propagators",
            },
        )
        tracer_instance.propagator = None


def _set_global_provider_thread_safe(tracer_instance: "HoneyHiveTracer") -> None:
    """Thread-safe global provider setup for multi-instance architecture.

    This function ensures that only ONE tracer instance becomes the global provider
    in a multi-threaded/multi-process environment (like pytest-xdist). Other instances
    will automatically become isolated secondary providers.

    :param tracer_instance: The tracer instance requesting to be the main provider
    :type tracer_instance: HoneyHiveTracer
    """
    # PYTEST-XDIST COMPATIBLE: Removed cross-process locks that cause deadlocks
    # Each pytest-xdist worker process has its own isolated OpenTelemetry state

    try:
        # Use the enhanced set_global_provider from integration module
        # Set as global provider - this handles the "set once" logic internally
        set_global_provider(tracer_instance.provider)

        safe_log(
            tracer_instance,
            "debug",
            "Set HoneyHive as global TracerProvider for this process",
            honeyhive_data={
                "process_isolated": True,
                "architecture": "multi-instance",
            },
        )

    except Exception as e:
        # If setting global provider fails, gracefully degrade to isolated instance
        tracer_instance.is_main_provider = False
        safe_log(
            tracer_instance,
            "warning",
            f"Failed to set global provider, running as isolated instance: {e}",
            honeyhive_data={
                "degradation_reason": "global_provider_setup_failed",
                "error_type": type(e).__name__,
                "error": str(e),
                "operation": "global_provider_setup",
            },
        )


def _create_tracer_instance(tracer_instance: Any) -> None:
    """Create the OpenTelemetry tracer instance.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :note: Global provider setting is now handled atomically during detection
    """
    # Global provider setup is now handled atomically during detection phase
    # No need to set global provider here - it's already done if needed

    if tracer_instance.is_main_provider:
        safe_log(
            tracer_instance,
            "debug",
            "Main provider tracer - global provider already set atomically",
            honeyhive_data={
                "architecture": "multi-instance",
                "provider_type": (
                    type(tracer_instance.provider).__name__
                    if tracer_instance.provider
                    else "None"
                ),
                "atomic_setup": True,
            },
        )
    else:
        safe_log(
            tracer_instance,
            "debug",
            "Independent provider tracer - functioning global provider exists",
            honeyhive_data={
                "architecture": "multi-instance",
                "provider_type": (
                    type(tracer_instance.provider).__name__
                    if tracer_instance.provider
                    else "None"
                ),
                "independent_instance": True,
            },
        )

    # Create tracer using our provider
    if tracer_instance.provider is not None:
        tracer_name = f"honeyhive.{id(tracer_instance)}"
        tracer_instance.tracer = tracer_instance.provider.get_tracer(tracer_name)
        safe_log(
            tracer_instance,
            "debug",
            "OpenTelemetry tracer created from instance provider",
            honeyhive_data={
                "provider_type": type(tracer_instance.provider).__name__,
                "tracer_instance_id": id(tracer_instance),
                "provider_id": id(tracer_instance.provider),
                "is_main_provider": tracer_instance.is_main_provider,
                "tracer_id": id(tracer_instance.tracer),
                "tracer_name": (
                    tracer_instance.tracer.name
                    if hasattr(tracer_instance.tracer, "name")
                    else "unknown"
                ),
            },
        )

        safe_log(
            tracer_instance,
            "debug",
            "🔍 DEBUG: Tracer-Provider relationship established",
            honeyhive_data={
                "tracer_uses_provider": (
                    tracer_instance.tracer._provider == tracer_instance.provider
                    if hasattr(tracer_instance.tracer, "_provider")
                    else "unknown"
                ),
                "provider_has_processors": (
                    len(
                        tracer_instance.provider._active_span_processor._span_processors
                    )
                    if hasattr(tracer_instance.provider, "_active_span_processor")
                    else "unknown"
                ),
                "session_id": getattr(tracer_instance, "session_id", "not_set"),
            },
        )
    else:
        # ARCHITECTURAL VIOLATION: This should never happen in proper initialization
        # Every tracer must have isolated provider - create emergency fallback
        safe_log(
            tracer_instance,
            "error",
            "ISOLATION VIOLATION: Missing provider - creating emergency provider",
            honeyhive_data={
                "tracer_instance_id": id(tracer_instance),
                "architectural_violation": True,
                "emergency_fallback": True,
            },
        )

        # Create emergency isolated TracerProvider with resources (never use global)
        tracer_instance.provider = _create_tracer_provider_with_resources(
            tracer_instance
        )
        tracer_instance.is_main_provider = False

        # Create tracer from emergency isolated provider
        tracer_name = f"honeyhive.{id(tracer_instance)}"
        tracer_instance.tracer = tracer_instance.provider.get_tracer(tracer_name)

        safe_log(
            tracer_instance,
            "warning",
            "Created emergency isolated provider - investigate initialization failure",
            honeyhive_data={
                "provider_type": type(tracer_instance.provider).__name__,
                "tracer_instance_id": id(tracer_instance),
                "provider_id": id(tracer_instance.provider),
                "is_main_provider": False,
            },
        )


def _initialize_session_management(tracer_instance: Any) -> None:
    """Initialize session management and HoneyHive client.

    :param tracer_instance: The tracer instance to configure
    :type tracer_instance: HoneyHiveTracer
    :note: Uses graceful degradation for API connection failures
    """
    try:
        # Create client and session API using dynamic configuration extraction

        # Extract configuration values dynamically (config object and legacy attributes)
        api_key = getattr(tracer_instance.config, "api_key", None)
        server_url = getattr(
            tracer_instance.config, "server_url", "https://api.honeyhive.ai"
        )
        test_mode = getattr(tracer_instance.config, "test_mode", False)
        verbose = getattr(tracer_instance.config, "verbose", False)

        tracer_instance.client = HoneyHive(
            api_key=api_key,
            server_url=server_url,
            test_mode=test_mode,
            verbose=verbose,
        )
        tracer_instance.session_api = SessionAPI(tracer_instance.client)

        # Handle session ID initialization
        # Always create/initialize session in backend, even if session_id is provided
        # This ensures the session exists and prevents backend from auto-populating
        # inputs/outputs from the first event
        provided_session_id = None
        if tracer_instance.session_id:
            # Store provided session_id for later use
            provided_session_id = tracer_instance.session_id
            # Validate UUID format first
            try:
                uuid.UUID(tracer_instance.session_id)
                tracer_instance.session_id = tracer_instance.session_id.lower()
                tracer_instance._session_id = tracer_instance.session_id
                safe_log(
                    tracer_instance,
                    "debug",
                    "Validated provided session_id, will initialize session in backend",
                    honeyhive_data={"session_id": tracer_instance.session_id},
                )
            except Exception as e:
                # Invalid UUID format - generate new one
                fallback_id = str(uuid.uuid4())
                tracer_instance.session_id = fallback_id
                tracer_instance._session_id = fallback_id
                tracer_instance._degraded_mode = True
                if not hasattr(tracer_instance, "_degradation_reasons"):
                    tracer_instance._degradation_reasons = []
                tracer_instance._degradation_reasons.append("invalid_session_id")
                safe_log(
                    tracer_instance,
                    "warning",
                    (
                        f"Invalid session_id format: {e}. "
                        "Generated new UUID for operation."
                    ),
                    honeyhive_data={
                        "session_id": tracer_instance.session_id,
                        "error_type": type(e).__name__,
                        "operation": "session_id_validation",
                    },
                )

        # Always create/initialize session in backend (even if session_id was provided)
        # This ensures session exists and prevents backend auto-population bug
        if provided_session_id:
            safe_log(
                tracer_instance,
                "debug",
                "Initializing session in backend with provided session_id",
                honeyhive_data={"session_id": provided_session_id},
            )
        _create_new_session(tracer_instance)

        safe_log(
            tracer_instance,
            "debug",
            "Session management initialized",
            honeyhive_data={
                "session_id": tracer_instance.session_id,
                "has_client": bool(tracer_instance.client),
            },
        )

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "warning",
            f"Failed to initialize session management: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "session_management_initialization",
            },
        )
        # Graceful degradation: Continue without session management
        tracer_instance.session_id = None
        tracer_instance._degraded_mode = True
        if not hasattr(tracer_instance, "_degradation_reasons"):
            tracer_instance._degradation_reasons = []
        tracer_instance._degradation_reasons.append("session_management_failed")

        # Consistent warning regardless of test_mode for debugging
        safe_log(
            tracer_instance,
            "warning",
            "Session management disabled due to API connection failure. "
            "Tracer will continue without session tracking.",
            honeyhive_data={"operation": "session_management_initialization"},
        )


def _validate_configuration_gracefully(tracer_instance: Any) -> None:
    """Validate configuration with graceful degradation.

    Following Agent OS graceful degradation standards:
    - Never crash the host application
    - Provide meaningful warnings for missing configuration
    - Continue operation in degraded mode when possible
    - Use sensible defaults where appropriate
    """
    degraded_mode = False
    degradation_reasons = []

    # Handle missing API key with graceful degradation
    if not tracer_instance.config.api_key:
        # Consistent warning regardless of test_mode for debugging
        safe_log(
            tracer_instance,
            "warning",
            "API key missing. Tracer will operate in no-op mode. "
            "Set HH_API_KEY environment variable for full functionality.",
            honeyhive_data={"operation": "api_key_validation"},
        )
        # Set degraded mode - spans will be created but not exported
        degraded_mode = True
        degradation_reasons.append("missing_api_key")
        # Set a placeholder to prevent further errors
        # No need to set api_key on tracer instance - config handles this

    # Handle missing project with graceful degradation
    if not tracer_instance.project_name:
        # Consistent warning regardless of test_mode for debugging
        safe_log(
            tracer_instance,
            "warning",
            "Project missing. Using default project 'unknown'. "
            "Set HH_PROJECT environment variable for proper categorization.",
            honeyhive_data={"operation": "project_validation"},
        )
        degraded_mode = True
        degradation_reasons.append("missing_project")

    # Store degradation state for runtime behavior
    tracer_instance._degraded_mode = degraded_mode
    tracer_instance._degradation_reasons = degradation_reasons

    if degraded_mode:
        safe_log(
            tracer_instance,
            "info",
            "Tracer initialized in degraded mode",
            honeyhive_data={
                "degradation_reasons": degradation_reasons,
                "test_mode": tracer_instance.test_mode,
            },
        )


def _validate_session_id(tracer_instance: Any) -> None:
    """Validate and normalize an existing session ID.

    :param tracer_instance: The tracer instance with session_id to validate
    :type tracer_instance: HoneyHiveTracer
    :note: Uses graceful degradation for invalid session IDs
    """
    try:
        # Validate that session_id is a valid UUID (backwards compatibility)
        uuid.UUID(tracer_instance.session_id)
        tracer_instance.session_id = tracer_instance.session_id.lower()
        # Update private attribute to match public attribute
        tracer_instance._session_id = tracer_instance.session_id

        safe_log(
            tracer_instance,
            "debug",
            "Using existing session ID",
            honeyhive_data={"session_id": tracer_instance.session_id},
        )
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        fallback_id = str(uuid.uuid4())
        tracer_instance.session_id = fallback_id
        tracer_instance._session_id = fallback_id  # Update private attribute
        tracer_instance._degraded_mode = True
        if not hasattr(tracer_instance, "_degradation_reasons"):
            tracer_instance._degradation_reasons = []
        tracer_instance._degradation_reasons.append("invalid_session_id")

        safe_log(
            tracer_instance,
            "warning",
            f"Invalid session_id format: {e}. Generated new UUID for operation.",
            honeyhive_data={
                "session_id": tracer_instance.session_id,
                "error_type": type(e).__name__,
                "operation": "session_id_validation",
            },
        )


def _create_new_session(tracer_instance: Any) -> None:
    """Create a new session in HoneyHive backend.

    :param tracer_instance: The tracer instance to create session for
    :type tracer_instance: HoneyHiveTracer
    """
    if tracer_instance.test_mode:
        # In test mode, just generate a UUID without backend call
        test_id = str(uuid.uuid4())
        tracer_instance.session_id = test_id
        tracer_instance._session_id = test_id  # Update private attribute
        safe_log(
            tracer_instance,
            "debug",
            "Generated session ID for test mode",
            honeyhive_data={"session_id": tracer_instance.session_id},
        )
        return

    try:
        # Determine session name
        session_name = tracer_instance.session_name
        if not session_name:
            # Auto-generate session name from filename

            frame = inspect.currentframe()
            while frame:
                filename = frame.f_code.co_filename
                if not filename.endswith(
                    ("tracer_initialization.py", "tracer_core.py", "otel_tracer.py")
                ):
                    session_name = os.path.basename(filename).replace(".py", "")
                    break
                frame = frame.f_back

        if not session_name:
            session_name = "unknown"  # Match original SDK fallback

        # Collect evaluation/experiment metadata if available
        # This ensures run_id, dataset_id, datapoint_id are included in session metadata
        session_metadata = {}

        if hasattr(tracer_instance, "run_id") and tracer_instance.run_id:
            session_metadata["run_id"] = str(tracer_instance.run_id)

        if hasattr(tracer_instance, "dataset_id") and tracer_instance.dataset_id:
            session_metadata["dataset_id"] = str(tracer_instance.dataset_id)

        if hasattr(tracer_instance, "datapoint_id") and tracer_instance.datapoint_id:
            session_metadata["datapoint_id"] = str(tracer_instance.datapoint_id)

        # Log metadata being added
        if session_metadata:
            safe_log(
                tracer_instance,
                "debug",
                "Including evaluation/experiment metadata in session",
                honeyhive_data={"metadata": session_metadata},
            )

        # Create session via API with metadata
        # If session_id is already set (explicitly provided), use it when creating
        # session. This ensures session exists in backend and prevents
        # auto-population bug
        session_response = tracer_instance.session_api.start_session(
            project=tracer_instance.project_name,
            session_name=session_name,
            source=tracer_instance.source_environment,
            session_id=tracer_instance.session_id,  # Use provided session_id if set
            inputs=tracer_instance.config.session.inputs,
            metadata=session_metadata if session_metadata else None,
        )

        if session_response and hasattr(session_response, "session_id"):
            # Preserve explicitly provided session_id if it was set
            # Otherwise use the session_id from the response
            provided_session_id = tracer_instance.session_id
            response_session_id = session_response.session_id

            # Use provided session_id if it matches response (session was created
            # with it). Otherwise use response session_id (new session was created)
            if (
                provided_session_id
                and provided_session_id.lower() == response_session_id.lower()
            ):
                # Session was created with the provided session_id - keep it
                tracer_instance.session_id = provided_session_id.lower()
                tracer_instance._session_id = provided_session_id.lower()
                safe_log(
                    tracer_instance,
                    "info",
                    "Initialized session with provided session_id",
                    honeyhive_data={
                        "session_id": tracer_instance.session_id,
                        "session_name": session_name,
                    },
                )
            else:
                # New session was created - use response session_id
                tracer_instance.session_id = response_session_id
                tracer_instance._session_id = response_session_id
                safe_log(
                    tracer_instance,
                    "info",
                    "Created new session",
                    honeyhive_data={
                        "session_id": tracer_instance.session_id,
                        "session_name": session_name,
                    },
                )

            tracer_instance.session_name = session_name
        else:
            # Fallback to UUID if session creation fails
            fallback_id = str(uuid.uuid4())
            tracer_instance.session_id = fallback_id
            tracer_instance._session_id = fallback_id  # Update private attribute
            safe_log(
                tracer_instance,
                "warning",
                "Session creation failed, using fallback UUID",
                honeyhive_data={"session_id": tracer_instance.session_id},
            )

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        # Fallback to UUID if session creation fails
        fallback_id = str(uuid.uuid4())
        tracer_instance.session_id = fallback_id
        tracer_instance._session_id = fallback_id  # Update private attribute
        safe_log(
            tracer_instance,
            "warning",
            f"Session creation failed ({e}), using fallback UUID",
            honeyhive_data={
                "session_id": tracer_instance.session_id,
                "error_type": type(e).__name__,
                "operation": "session_creation_fallback",
            },
        )


def _setup_baggage_context(tracer_instance: Any) -> None:
    """Setup baggage context for the tracer instance.

    :param tracer_instance: The tracer instance to configure baggage for
    :type tracer_instance: HoneyHiveTracer
    """
    setup_baggage_context(tracer_instance)


def _register_tracer_instance(tracer_instance: Any) -> None:
    """Register tracer instance for auto-discovery.

    Automatically sets this tracer as the global default if no default
    exists yet. This ensures @trace() decorator works in simple single-
    instance scenarios without requiring manual set_default_tracer() calls.

    :param tracer_instance: The tracer instance to register
    :type tracer_instance: HoneyHiveTracer
    """
    try:

        tracer_instance._tracer_id = registry.register_tracer(tracer_instance)

        # Auto-set as default if this is the first tracer
        # Users can override this later with set_default_tracer()
        if registry.get_default_tracer() is None:
            registry.set_default_tracer(tracer_instance)
            safe_log(
                tracer_instance,
                "info",
                "Automatically set as default tracer (first instance)",
                honeyhive_data={
                    "auto_default": True,
                    "tracer_id": tracer_instance._tracer_id,
                    "decorator_discovery": "enabled",
                },
            )

        safe_log(
            tracer_instance,
            "debug",
            "Tracer registered for auto-discovery",
            honeyhive_data={"tracer_id": tracer_instance._tracer_id},
        )
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "warning",
            f"Failed to register tracer for auto-discovery: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "operation": "tracer_registration",
            },
        )
        tracer_instance._tracer_id = None
