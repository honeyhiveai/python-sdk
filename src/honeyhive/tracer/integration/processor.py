"""Dynamic span processor integration framework.

This module provides a flexible system for adding HoneyHive span processors
to any existing TracerProvider using dynamic integration strategies and
extensible processor management patterns.
"""

# pylint: disable=duplicate-code
# Standard exception logging patterns are intentionally consistent for error handling

import threading
from typing import Any, Dict, List, Optional

from opentelemetry import baggage, context
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

# Import shared logging utility
from ...utils.logger import safe_log
from .detection import IntegrationStrategy, ProviderDetector


class ProcessorIntegrationError(Exception):
    """Base exception for processor integration errors."""


class ProviderIncompatibleError(ProcessorIntegrationError):
    """Provider doesn't support required operations."""


class ProcessorIntegrator:
    """Dynamically manages integration of HoneyHive processors with providers."""

    def __init__(self, tracer_instance: Any = None) -> None:
        """Initialize the processor integrator with dynamic configuration.

        Args:
            tracer_instance: Optional tracer instance for logging context
        """
        self.tracer_instance = tracer_instance
        self._lock = threading.Lock()
        self._integrated_processors: List["SpanProcessor"] = []
        self._integration_strategies = self._build_integration_strategies_dynamically()

    def _build_integration_strategies_dynamically(self) -> Dict[str, Any]:
        """Dynamically build integration strategies.

        Returns:
            Dictionary of integration strategies and their configurations
        """
        return {
            "processor_validation": {
                "required_methods": ["add_span_processor"],
                "optional_methods": ["remove_span_processor", "get_span_processors"],
            },
            "context_enrichment": {
                "baggage_keys": ["source", "project", "honeyhive_tracer_id"],
                "context_timeout": 30.0,
            },
            "processor_ordering": {
                "default_position": -1,  # Append to end
                "priority_processors": [],  # Future: priority-based ordering
            },
        }

    def integrate_with_provider(
        self,
        provider: "TracerProvider",
        source: str = "dev",
        project: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Dynamically add HoneyHive processor to existing provider.

        Args:
            provider: The TracerProvider to integrate with
            source: Source environment for span enrichment
            project: Optional project for span enrichment
            **kwargs: Additional integration parameters

        Returns:
            bool: True if integration successful, False otherwise

        Raises:
            ProviderIncompatibleError: If provider doesn't support span processors
        """
        with self._lock:
            try:
                # Dynamic compatibility validation
                if not self._validate_provider_compatibility_dynamically(provider):
                    safe_log(
                        self.tracer_instance,
                        "warning",
                        "Provider doesn't support span processors",
                        honeyhive_data={
                            "provider_class": type(provider).__name__,
                            "missing_capabilities": (
                                self._get_missing_capabilities_dynamically(provider)
                            ),
                        },
                    )
                    return False

                # Dynamic context setup
                self._setup_integration_context_dynamically(source, project, **kwargs)

                # Dynamic processor creation and integration
                processor = self._create_processor_dynamically(provider, **kwargs)
                integration_success = self._integrate_processor_dynamically(
                    provider, processor
                )

                if integration_success:
                    self._integrated_processors.append(processor)
                    self._log_integration_success_dynamically(provider, source, project)

                return integration_success

            except Exception as e:
                self._log_integration_failure_dynamically(provider, e)
                return False

    def _validate_provider_compatibility_dynamically(
        self, provider: "TracerProvider"
    ) -> bool:
        """Dynamically validate provider compatibility.

        Args:
            provider: The TracerProvider to check

        Returns:
            bool: True if provider supports required operations
        """
        required_methods = self._integration_strategies["processor_validation"][
            "required_methods"
        ]

        # Dynamic method validation
        for method_name in required_methods:
            if not self._has_callable_method_dynamically(provider, method_name):
                return False

        return True

    def _has_callable_method_dynamically(self, obj: Any, method_name: str) -> bool:
        """Dynamically check if object has callable method.

        Args:
            obj: Object to check
            method_name: Name of method to check

        Returns:
            bool: True if object has callable method
        """
        return hasattr(obj, method_name) and callable(getattr(obj, method_name))

    def _get_missing_capabilities_dynamically(
        self, provider: "TracerProvider"
    ) -> List[str]:
        """Dynamically identify missing provider capabilities.

        Args:
            provider: Provider to analyze

        Returns:
            List of missing capability names
        """
        required_methods = self._integration_strategies["processor_validation"][
            "required_methods"
        ]

        missing = []
        for method_name in required_methods:
            if not self._has_callable_method_dynamically(provider, method_name):
                missing.append(method_name)

        return missing

    def _setup_integration_context_dynamically(
        self, source: str, project: Optional[str], **kwargs: Any
    ) -> None:
        """Dynamically set up integration context with baggage.

        Args:
            source: Source environment for span enrichment
            project: Optional project for span enrichment
            **kwargs: Additional context parameters
        """
        ctx = context.get_current()

        # Dynamic baggage setup
        _baggage_config = self._integration_strategies["context_enrichment"]
        baggage_mappings = {
            "source": source,
            "project": project,
        }

        # Add additional baggage from kwargs
        for key, value in kwargs.items():
            if key.startswith("honeyhive_") and value is not None:
                baggage_mappings[key] = value

        # Apply baggage dynamically
        for key, value in baggage_mappings.items():
            if value is not None:
                ctx = baggage.set_baggage(key, str(value), ctx)

        # Attach the updated context
        context.attach(ctx)

        safe_log(
            self.tracer_instance,
            "debug",
            "Integration context set up",
            honeyhive_data={
                "baggage_keys": list(baggage_mappings.keys()),
                "source": source,
                "project": project,
            },
        )

    def _create_processor_dynamically(
        self, _provider: "TracerProvider", **kwargs: Any
    ) -> "SpanProcessor":
        """Dynamically create HoneyHive span processor.

        Args:
            provider: The TracerProvider for context
            **kwargs: Additional processor configuration

        Returns:
            SpanProcessor: Configured HoneyHive span processor
        """
        # Import here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from ..processing.span_processor import HoneyHiveSpanProcessor

        # Dynamic processor configuration
        processor_config = {
            "client": kwargs.get("client"),
            "disable_batch": kwargs.get("disable_batch", False),
            "otlp_exporter": kwargs.get("otlp_exporter"),
            "tracer_instance": kwargs.get("tracer_instance"),
        }

        # Filter out None values
        processor_config = {k: v for k, v in processor_config.items() if v is not None}

        return HoneyHiveSpanProcessor(**processor_config)

    def _integrate_processor_dynamically(
        self, provider: "TracerProvider", processor: "SpanProcessor"
    ) -> bool:
        """Dynamically integrate processor with provider.

        Args:
            provider: Provider to integrate with
            processor: Processor to integrate

        Returns:
            bool: True if integration successful
        """
        try:
            # Dynamic insertion point determination
            insertion_point = self._get_processor_insertion_point_dynamically(provider)

            # Add processor to provider
            if insertion_point == -1:
                # Append to end (default)
                provider.add_span_processor(processor)
            else:
                # Future: Support for specific insertion points
                provider.add_span_processor(processor)

            return True

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to integrate processor",
                honeyhive_data={
                    "provider_class": type(provider).__name__,
                    "processor_class": type(processor).__name__,
                    "error": str(e),
                },
            )
            return False

    def _get_processor_insertion_point_dynamically(
        self, _provider: "TracerProvider"
    ) -> int:
        """Dynamically determine optimal processor insertion point.

        Args:
            provider: The TracerProvider to analyze

        Returns:
            int: Index where processor should be inserted (-1 for append)
        """
        # Dynamic insertion point strategies
        ordering_config = self._integration_strategies["processor_ordering"]

        # For now, use default position
        # Future: Implement sophisticated ordering based on existing processors
        return int(ordering_config["default_position"])

    def _log_integration_success_dynamically(
        self, provider: "TracerProvider", source: str, project: Optional[str]
    ) -> None:
        """Dynamically log successful integration.

        Args:
            provider: Integrated provider
            source: Source environment
            project: Project name
        """
        safe_log(
            self.tracer_instance,
            "info",
            "Successfully integrated HoneyHive span processor",
            honeyhive_data={
                "provider_class": type(provider).__name__,
                "source": source,
                "project": project,
                "total_processors": len(self._integrated_processors) + 1,
            },
        )

    def _log_integration_failure_dynamically(
        self, provider: "TracerProvider", error: Exception
    ) -> None:
        """Dynamically log integration failure.

        Args:
            provider: Provider that failed integration
            error: Exception that occurred
        """
        safe_log(
            self.tracer_instance,
            "error",
            "Failed to integrate with provider",
            honeyhive_data={
                "provider_class": type(provider).__name__,
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    def get_integrated_processors(self) -> List["SpanProcessor"]:
        """Get list of processors that have been integrated.

        Returns:
            List[SpanProcessor]: List of integrated HoneyHive processors
        """
        with self._lock:
            return self._integrated_processors.copy()

    def cleanup_processors(self) -> None:
        """Dynamically clean up integrated processors.

        This should be called during shutdown to ensure proper cleanup.
        """
        with self._lock:
            cleanup_results = self._cleanup_processors_dynamically()

            self._integrated_processors.clear()

            safe_log(
                self.tracer_instance,
                "info",
                "Cleaned up integrated processors",
                honeyhive_data={
                    "total_cleaned": cleanup_results["total_cleaned"],
                    "cleanup_errors": cleanup_results["cleanup_errors"],
                },
            )

    def _cleanup_processors_dynamically(self) -> Dict[str, int]:
        """Dynamically clean up all integrated processors.

        Returns:
            Dictionary with cleanup statistics
        """
        cleanup_stats = {"total_cleaned": 0, "cleanup_errors": 0}

        for processor in self._integrated_processors:
            try:
                if hasattr(processor, "shutdown"):
                    processor.shutdown()
                cleanup_stats["total_cleaned"] += 1
            except Exception as e:
                cleanup_stats["cleanup_errors"] += 1
                safe_log(
                    self.tracer_instance,
                    "warning",
                    "Error shutting down processor",
                    honeyhive_data={
                        "processor_class": type(processor).__name__,
                        "error": str(e),
                    },
                )

        return cleanup_stats


class IntegrationManager:
    """High-level manager for dynamic non-instrumentor integrations."""

    def __init__(self) -> None:
        """Initialize the integration manager with dynamic components."""
        self.detector = ProviderDetector()
        self.integrator = ProcessorIntegrator()
        self._integration_handlers = self._build_integration_handlers_dynamically()

    def _build_integration_handlers_dynamically(self) -> Dict[IntegrationStrategy, Any]:
        """Dynamically build integration strategy handlers.

        Returns:
            Dictionary mapping strategies to handler functions
        """
        return {
            IntegrationStrategy.MAIN_PROVIDER: self._handle_main_provider_strategy,
            IntegrationStrategy.INDEPENDENT_PROVIDER: (
                self._handle_independent_provider_strategy
            ),
            IntegrationStrategy.CONSOLE_FALLBACK: (
                self._handle_console_fallback_strategy
            ),
        }

    def perform_integration(
        self, source: str = "dev", project: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Dynamically perform complete integration based on detected provider.

        Args:
            source: Source environment for span enrichment
            project: Optional project for span enrichment
            **kwargs: Additional integration parameters

        Returns:
            dict: Integration result with status and details
        """
        try:
            # Dynamic provider analysis
            provider_info = self.detector.get_provider_info()
            strategy = provider_info["integration_strategy"]

            # Dynamic integration execution
            result = self._execute_integration_strategy_dynamically(
                strategy, provider_info, source, project, **kwargs
            )

            return result

        except Exception as e:
            return self._create_error_result_dynamically(e)

    def _execute_integration_strategy_dynamically(
        self,
        strategy: IntegrationStrategy,
        provider_info: Dict[str, Any],
        source: str,
        project: Optional[str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dynamically execute integration strategy.

        Args:
            strategy: Integration strategy to execute
            provider_info: Provider information
            source: Source environment
            project: Project name
            **kwargs: Additional parameters

        Returns:
            Integration result dictionary
        """
        # Get handler for strategy
        handler = self._integration_handlers.get(strategy)

        if handler:
            result = handler(provider_info, source, project, **kwargs)
            return dict(result) if result else {}

        return self._create_unknown_strategy_result_dynamically(strategy)

    def _handle_main_provider_strategy(
        self,
        provider_info: Dict[str, Any],
        source: str,
        project: Optional[str],
        **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Handle main provider integration strategy.

        Args:
            provider_info: Provider information
            source: Source environment
            project: Project name
            **kwargs: Additional parameters

        Returns:
            Integration result
        """
        return {
            "success": True,
            "strategy": IntegrationStrategy.MAIN_PROVIDER,
            "provider_info": provider_info,
            "message": "Provider is replaceable - create new TracerProvider",
            "source": source,
            "project": project,
            "action_required": "create_new_provider",
        }

    def _handle_independent_provider_strategy(
        self,
        provider_info: Dict[str, Any],
        source: str,
        project: Optional[str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Handle independent provider integration strategy.

        Args:
            provider_info: Provider information
            source: Source environment
            project: Project name
            **kwargs: Additional parameters

        Returns:
            Integration result
        """
        provider = provider_info["provider_instance"]
        success = self.integrator.integrate_with_provider(
            provider, source=source, project=project, **kwargs
        )

        return {
            "success": success,
            "strategy": IntegrationStrategy.INDEPENDENT_PROVIDER,
            "provider_info": provider_info,
            "message": (
                "Successfully integrated with existing provider"
                if success
                else "Failed to integrate with existing provider"
            ),
            "source": source,
            "project": project,
            "action_required": None,
        }

    def _handle_console_fallback_strategy(
        self,
        provider_info: Dict[str, Any],
        source: str,
        project: Optional[str],
        **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Handle console fallback integration strategy.

        Args:
            provider_info: Provider information
            source: Source environment
            project: Project name
            **kwargs: Additional parameters

        Returns:
            Integration result
        """
        return {
            "success": True,
            "strategy": IntegrationStrategy.CONSOLE_FALLBACK,
            "provider_info": provider_info,
            "message": "Provider incompatible - falling back to console logging",
            "source": source,
            "project": project,
            "action_required": "setup_console_fallback",
        }

    def _create_error_result_dynamically(self, error: Exception) -> Dict[str, Any]:
        """Dynamically create error result.

        Args:
            error: Exception that occurred

        Returns:
            Error result dictionary
        """
        return {
            "success": False,
            "strategy": IntegrationStrategy.CONSOLE_FALLBACK,
            "provider_info": {},
            "message": f"Integration failed: {error}",
            "error": str(error),
            "error_type": type(error).__name__,
            "action_required": "handle_integration_error",
        }

    def _create_unknown_strategy_result_dynamically(
        self, strategy: IntegrationStrategy
    ) -> Dict[str, Any]:
        """Dynamically create result for unknown strategy.

        Args:
            strategy: Unknown integration strategy

        Returns:
            Unknown strategy result dictionary
        """
        return {
            "success": False,
            "strategy": strategy,
            "provider_info": {},
            "message": f"Unknown integration strategy: {strategy}",
            "action_required": "handle_unknown_strategy",
        }

    def cleanup(self) -> None:
        """Clean up integration resources."""
        self.integrator.cleanup_processors()


# Convenience functions for backward compatibility
def integrate_with_existing_provider(
    source: str = "dev", project: Optional[str] = None, **kwargs: Any
) -> Dict[str, Any]:
    """Dynamically integrate HoneyHive with existing OpenTelemetry provider.

    This is a convenience function that handles the complete integration process
    using dynamic strategies and extensible configuration.

    Args:
        source: Source environment for span enrichment
        project: Optional project for span enrichment
        **kwargs: Additional integration parameters

    Returns:
        dict: Integration result with status and details
    """
    manager = IntegrationManager()
    return manager.perform_integration(source=source, project=project, **kwargs)
