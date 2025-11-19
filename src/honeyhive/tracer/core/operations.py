"""Tracer operations for span creation and event management.

This module provides dynamic span creation, event management, and tracing
operations. It uses dynamic logic for flexible span handling, attribute
processing, and event creation with comprehensive error handling.
"""

# pylint: disable=duplicate-code,too-many-lines
# Justification for duplicate-code: Legitimate shared patterns with decorator
# and base mixins. Duplicate code represents common dynamic attribute
# normalization and event creation patterns shared across core mixin classes
# for consistent behavior.
# Justification for too-many-lines: Comprehensive operations mixin providing
# span creation, event management, enrichment, and finalization. Core module
# with 1006 lines (6 lines over limit) - acceptable for central operations.

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, contextmanager
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

from opentelemetry import trace
from opentelemetry.baggage import get_baggage
from opentelemetry.trace import SpanKind, Status, StatusCode

from ...api.events import CreateEventRequest
from ...models.generated import EventType1
from ...utils.logger import is_shutdown_detected, safe_log
from ..lifecycle.core import (
    is_new_span_creation_disabled,
)
from .base import NoOpSpan

if TYPE_CHECKING:
    # Import for type checking only to avoid circular imports
    from . import HoneyHiveTracer


class TracerOperationsInterface(ABC):  # pylint: disable=too-few-public-methods
    """Abstract interface for tracer operations.

    This ABC defines the required methods that must be implemented by any class
    that uses TracerOperationsMixin. Provides explicit type safety and clear contracts.

    Note: too-few-public-methods disabled - ABC interface defines only abstract methods,
    concrete implementations in TracerOperationsMixin provide public methods.
    """

    @abstractmethod
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage value by key.

        Args:
            key: The baggage key to retrieve

        Returns:
            Baggage value or None if not found
        """

    @abstractmethod
    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Normalize attribute key dynamically for OpenTelemetry compatibility.

        Args:
            key: The attribute key to normalize

        Returns:
            Normalized key string
        """

    @abstractmethod
    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Normalize attribute value dynamically for OpenTelemetry compatibility.

        Args:
            value: The attribute value to normalize

        Returns:
            Normalized value
        """


class TracerOperationsMixin(TracerOperationsInterface):
    """Mixin providing dynamic span and event operations for HoneyHive tracer.

    This mixin uses dynamic logic for span creation, attribute processing,
    and event management, providing flexible and robust tracing operations.

    This mixin requires implementation of TracerOperationsInterface abstract methods.
    """

    # Type hint for mypy - this will be provided by the composed class
    if TYPE_CHECKING:
        # These attributes will be available when this mixin is composed
        # Note: is_initialized and project_name are properties in base class
        tracer: Optional[Any]
        client: Optional[Any]
        session_api: Optional[Any]
        config: Any  # TracerConfig provided by base class
        _session_id: Optional[str]
        _baggage_lock: Any

        @property
        def is_initialized(
            self,
        ) -> bool:
            """Check if tracer is initialized."""

        @property
        def project_name(
            self,
        ) -> Optional[str]:
            """Get project name."""

    def trace(
        self,
        name: str,
        event_type: Optional[str] = None,
        **kwargs: Any,
    ) -> AbstractContextManager[Any]:
        """Create and return a new span for direct programmatic tracing.

        This method creates a span directly without using decorators, allowing for
        programmatic control over span lifecycle. The span should be used as a
        context manager.

        Args:
            name: Human-readable name for the operation being traced
            event_type: Event type for categorization. Must be one of: "model", "tool",
                or "chain"
            **kwargs: Additional span attributes to set on creation

        Returns:
            Context manager yielding an OpenTelemetry Span object

        Example:
            >>> tracer = HoneyHiveTracer(api_key="...", project="...")
            >>>
            >>> # Direct span creation
            >>> with tracer.trace("my_operation", event_type="tool") as span:
            ...     span.set_attribute("input", "some data")
            ...     result = do_work()
            ...     span.set_attribute("output", result)
            >>>
            >>> # Nested spans (automatic context propagation)
            >>> with tracer.trace("parent_operation") as parent:
            ...     parent.set_attribute("operation.level", "parent")
            ...     with tracer.trace("child_operation") as child:
            ...         child.set_attribute("operation.level", "child")
        """
        # Prepare attributes including event_type if provided
        attributes = kwargs.copy()
        if event_type is not None:
            attributes["honeyhive.event_type"] = event_type
        # Use the tracer's start_span method which handles all the HoneyHive logic
        return self.start_span(name=name, attributes=attributes if attributes else None)

    @contextmanager
    # pylint: disable=too-many-arguments
    # Justification: Dynamic span creation requires multiple optional parameters
    # for flexible attribute handling, timing, and error management.
    def start_span(
        self,
        name: str,
        *,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Dict[str, Any]] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
    ) -> Iterator[Any]:
        """Create and manage a span using dynamic span creation logic.

        This method uses dynamic patterns to create spans with flexible
        attribute handling, automatic error management, and graceful degradation.

        Args:
            name: Span name
            kind: Span kind (defaults to INTERNAL)
            attributes: Initial span attributes
            links: Span links
            start_time: Custom start time
            record_exception: Whether to record exceptions automatically
            set_status_on_exception: Whether to set error status on exceptions

        Yields:
            Active span object with dynamic attribute management
        """
        # Dynamic span creation with graceful degradation
        span = self._create_span_dynamically(
            name=name,
            kind=kind,
            attributes=attributes,
            links=links,
            start_time=start_time,
        )

        try:
            # Dynamic span context management
            with self._manage_span_context_dynamically(span):
                yield span

        except Exception as e:
            # Dynamic exception handling
            self._handle_span_exception_dynamically(
                span=span,
                exception=e,
                record_exception=record_exception,
                set_status_on_exception=set_status_on_exception,
            )
            raise
        finally:
            # Dynamic span finalization
            safe_log(
                self, "debug", f"⭐ START_SPAN: Finalize span in finally block: {name}"
            )
            self._finalize_span_dynamically(span)
            safe_log(self, "debug", f"✅ START_SPAN: Span finalized: {name}")

    # pylint: disable=too-many-arguments
    # Justification: Internal span creation method needs multiple parameters
    # for comprehensive dynamic span configuration.
    def _create_span_dynamically(
        self,
        name: str,
        *,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Dict[str, Any]] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
    ) -> Any:
        """Dynamically create a span with comprehensive error handling."""
        # Check for shutdown conditions (instance-specific for multi-instance)
        if (hasattr(self, "_instance_shutdown") and self._instance_shutdown) or (
            is_shutdown_detected() and getattr(self, "is_main_provider", False)
        ):
            safe_log(self, "debug", "Span creation skipped - shutdown in progress")
            return NoOpSpan()

        # Check if new span creation is disabled
        if self._is_span_creation_disabled_dynamically():
            safe_log(self, "debug", "Span creation disabled during shutdown")
            return NoOpSpan()

        # Graceful degradation if not initialized
        if not self.is_initialized or not self.tracer:
            safe_log(
                self,
                "warning",
                "🔍 DEBUG: Tracer not initialized - using NoOp span",
                honeyhive_data={
                    "span_name": name,
                    "is_initialized": self.is_initialized,
                    "has_tracer": self.tracer is not None,
                    "tracer_type": type(self.tracer).__name__ if self.tracer else None,
                    "has_provider": hasattr(self, "provider")
                    and self.provider is not None,
                    "provider_type": (
                        type(self.provider).__name__
                        if hasattr(self, "provider") and self.provider
                        else None
                    ),
                    "is_main_provider": getattr(self, "is_main_provider", "unknown"),
                    "tracer_instance_id": id(self),
                },
            )
            return NoOpSpan()

        try:
            # Dynamic span creation parameters
            span_params = self._build_span_parameters_dynamically(
                name=name,
                kind=kind,
                attributes=attributes,
                links=links,
                start_time=start_time,
            )

            # Create span using OpenTelemetry tracer
            span = self.tracer.start_span(**span_params)

            # Dynamic attribute processing
            self._process_span_attributes_dynamically(span, attributes)

            safe_log(
                self,
                "debug",
                f"Created span: {name}",
                honeyhive_data={
                    "span_name": name,
                    "span_kind": str(kind) if kind else "INTERNAL",
                    "has_attributes": bool(attributes),
                },
            )

            return span

        except Exception as e:
            safe_log(
                self,
                "warning",
                f"Failed to create span '{name}': {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            # Graceful degradation
            return NoOpSpan()

    # pylint: disable=too-many-arguments
    # Justification: Parameter building method needs multiple optional parameters
    # for flexible span configuration.
    def _build_span_parameters_dynamically(
        self,
        name: str,
        *,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Dict[str, Any]] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Dynamically build span creation parameters."""
        # Build parameters with proper types for OpenTelemetry start_span
        params: Dict[str, Any] = {"name": name}

        # Add optional parameters dynamically with correct types
        if kind is not None:
            params["kind"] = kind
        else:
            params["kind"] = SpanKind.INTERNAL

        if attributes:
            params["attributes"] = attributes

        if links is not None:
            params["links"] = links

        if start_time is not None:
            params["start_time"] = start_time

        return params

    def _process_span_attributes_dynamically(
        self, span: Any, attributes: Optional[Dict[str, Any]]
    ) -> None:
        """Dynamically process and set span attributes."""
        if not attributes:
            return

        try:
            # Process attributes using dynamic logic
            processed_attributes = self._normalize_attributes_dynamically(attributes)

            # Set attributes on span
            for key, value in processed_attributes.items():
                if value is not None:
                    span.set_attribute(key, value)

        except Exception as e:
            safe_log(
                self,
                "warning",
                f"Failed to process span attributes: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )

    def _normalize_attributes_dynamically(
        self, attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dynamically normalize attributes for OpenTelemetry compatibility."""
        normalized = {}

        for key, value in attributes.items():
            # Dynamic key normalization
            normalized_key = self._normalize_attribute_key_dynamically(key)

            # Dynamic value normalization
            normalized_value = self._normalize_attribute_value_dynamically(value)

            if normalized_value is not None:
                normalized[normalized_key] = normalized_value

        return normalized

    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Dynamically normalize attribute keys."""
        if not isinstance(key, str):
            key = str(key)

        # Replace invalid characters dynamically
        normalized = key.replace(".", "_").replace("-", "_").replace(" ", "_")

        # Ensure valid identifier
        if not normalized or normalized[0].isdigit():
            normalized = f"attr_{normalized}"

        return normalized

    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Dynamically normalize attribute values for OpenTelemetry."""
        # Handle None values
        if value is None:
            return None

        # Handle enum values dynamically
        if hasattr(value, "value"):
            return value.value

        # Handle basic types that OpenTelemetry accepts
        if isinstance(value, (str, int, float, bool)):
            return value

        # Convert complex types to strings
        try:
            return str(value)
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self,
                "debug",
                "Failed to serialize attribute value",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return "<unserializable>"

    def _is_span_creation_disabled_dynamically(self) -> bool:
        """Dynamically check if span creation is disabled."""
        try:
            # For multi-instance architecture: only check global flag if main provider
            if getattr(self, "is_main_provider", False):
                return is_new_span_creation_disabled()
            # Independent providers not affected by global span creation disabling
            return False
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self,
                "warning",
                f"Span creation state check failed: {e}",
                honeyhive_data={
                    "error_type": type(e).__name__,
                    "operation": "span_creation_check",
                    "fallback": "disabled_check_false",
                },
            )
            # Continue without crashing - return safe default
            return False

    @contextmanager
    def _manage_span_context_dynamically(self, span: Any) -> Iterator[None]:
        """Dynamically manage span context and activation."""
        if isinstance(span, NoOpSpan):
            # No context management needed for NoOp spans
            yield
            return

        # Use OpenTelemetry's proper context management
        with trace.use_span(  # pylint: disable=not-context-manager
            span, end_on_exit=False
        ):
            yield

    def _handle_span_exception_dynamically(
        self,
        span: Any,
        exception: Exception,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
    ) -> None:
        """Dynamically handle exceptions in span context."""
        if isinstance(span, NoOpSpan):
            return

        try:
            if record_exception:
                # Record exception with dynamic attribute extraction
                exception_attributes = self._extract_exception_attributes_dynamically(
                    exception
                )
                span.record_exception(exception, attributes=exception_attributes)

            if set_status_on_exception:
                # Set error status dynamically
                error_description = self._generate_error_description_dynamically(
                    exception
                )
                span.set_status(Status(StatusCode.ERROR, error_description))

        except Exception as e:
            safe_log(
                self,
                "warning",
                f"Failed to handle span exception: {e}",
                honeyhive_data={"original_error": str(exception)},
            )

    def _extract_exception_attributes_dynamically(
        self, exception: Exception
    ) -> Dict[str, Any]:
        """Dynamically extract attributes from exception."""
        attributes = {
            "exception.type": type(exception).__name__,
            "exception.message": str(exception),
        }

        # Add module information if available
        if hasattr(exception, "__module__"):
            attributes["exception.module"] = exception.__module__

        return attributes

    def _generate_error_description_dynamically(self, exception: Exception) -> str:
        """Dynamically generate error description from exception."""
        return f"{type(exception).__name__}: {str(exception)}"

    def _preserve_core_attributes_inline(self, span: Any) -> None:
        """Re-set core attributes inline to ensure they survive FIFO eviction.

        Called just before span.end() for spans approaching the attribute limit.
        By setting core attributes LAST, they become the NEWEST attributes and
        survive OpenTelemetry's FIFO eviction policy.

        Args:
            span: The span to preserve core attributes on (must be mutable)
        """
        try:
            # 1. CRITICAL: Session ID (required for backend ingestion)
            session_id = None
            baggage_session_id = get_baggage("honeyhive.session_id")
            if baggage_session_id:
                session_id = str(baggage_session_id)
            if not session_id:
                config_session_id = getattr(self.config, "session_id", None)
                if config_session_id:
                    session_id = str(config_session_id)
            if session_id:
                span.set_attribute("honeyhive.session_id", session_id)

            # 2. CRITICAL: Source (required for backend routing)
            source = getattr(self, "source", None) or getattr(
                self.config, "source", "unknown"
            )
            span.set_attribute("honeyhive.source", source)

            # 3-6: Event type, name, project, config (if already set)
            if hasattr(span, "attributes") and span.attributes:
                event_type = span.attributes.get(
                    "honeyhive_event_type"
                ) or span.attributes.get("honeyhive.event_type")
                if event_type:
                    span.set_attribute("honeyhive.event_type", event_type)

                event_name = span.attributes.get(
                    "honeyhive_event_name"
                ) or span.attributes.get("honeyhive.event_name")
                if event_name:
                    span.set_attribute("honeyhive.event_name", event_name)

                project = getattr(self, "project", None) or getattr(
                    self.config, "project", None
                )
                if project:
                    span.set_attribute("honeyhive.project", project)

                config_name = span.attributes.get("honeyhive_config")
                if config_name:
                    span.set_attribute("honeyhive.config", config_name)
        except Exception:
            # Best-effort optimization - don't fail span finalization
            pass

    def _finalize_span_dynamically(self, span: Any) -> None:
        """Dynamically finalize span with proper cleanup.

        This method is called in the finally block of start_span() and is
        guaranteed to run for every span. If core attribute preservation is
        enabled and the span is approaching the attribute limit (95% threshold),
        this method will re-set core attributes just before span.end() to ensure
        they survive FIFO eviction.

        Args:
            span: The span to finalize (must be mutable, not yet ReadableSpan)
        """
        if isinstance(span, NoOpSpan):
            safe_log(self, "debug", "Skipping finalize for NoOpSpan")
            return

        try:
            # 🎯 LAZY ACTIVATION: Only preserve core if approaching limit
            if getattr(self.config, "preserve_core_attributes", True):
                max_attributes = getattr(self.config, "max_attributes", 1024)
                threshold = int(max_attributes * 0.95)  # 95% of limit

                # Check current attribute count (minimal overhead: ~0.001ms)
                current_count = (
                    len(span.attributes) if hasattr(span, "attributes") else 0
                )

                if current_count >= threshold:
                    # Span is approaching limit - preserve core attributes
                    # by re-setting them LAST to survive FIFO eviction
                    self._preserve_core_attributes_inline(span)

            # NOW end the span (converts to ReadableSpan and calls on_end)
            span.end()
        except Exception as e:
            safe_log(
                self,
                "error",
                "Failed to finalize span",
                honeyhive_data={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )

    # pylint: disable=too-many-arguments
    # Justification: Event creation requires many optional parameters for comprehensive
    # event data (inputs, outputs, metadata, config, feedback, metrics, etc.).
    def create_event(
        self,
        event_name_or_dict: Union[str, Dict[str, Any]],
        *,
        event_type: str = "tool",
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """Create an event using dynamic API interaction and error handling.

        This method uses dynamic logic to create events with flexible parameter
        handling, automatic session management, and comprehensive error recovery.

        Args:
            event_name: Name of the event
            event_type: Type of event (model, tool, chain, session)
            inputs: Event input data
            outputs: Event output data
            error: Error message if applicable
            duration: Event duration in seconds
            metadata: Additional metadata
            config: Configuration data
            feedback: Feedback data
            metrics: Metrics data
            **kwargs: Additional dynamic parameters

        Returns:
            Event ID if successful, None otherwise
        """
        # Dynamic event creation with graceful degradation
        if not self._can_create_event_dynamically():
            return None

        try:
            # Parse parameters dynamically - handle both dict and individual params
            if isinstance(event_name_or_dict, dict):
                # Dictionary-based call: extract all parameters from dict
                event_dict = event_name_or_dict
                event_name = event_dict.get("event_name", "unknown_event")
                event_type = event_dict.get("event_type", event_type)
                inputs = event_dict.get("inputs", inputs)
                outputs = event_dict.get("outputs", outputs)
                error = event_dict.get("error", error)
                duration = event_dict.get("duration", duration)
                metadata = event_dict.get("metadata", metadata)
                config = event_dict.get("config", config)
                feedback = event_dict.get("feedback", feedback)
                metrics = event_dict.get("metrics", metrics)
                # Merge any additional kwargs from the dict
                for key, value in event_dict.items():
                    if key not in [
                        "event_name",
                        "event_type",
                        "inputs",
                        "outputs",
                        "error",
                        "duration",
                        "metadata",
                        "config",
                        "feedback",
                        "metrics",
                    ]:
                        kwargs[key] = value
            else:
                # Individual parameter call: use event_name_or_dict as event_name
                event_name = str(event_name_or_dict)

            # Build event request dynamically
            event_request = self._build_event_request_dynamically(
                event_name=event_name,
                event_type=event_type,
                inputs=inputs,
                outputs=outputs,
                error=error,
                duration=duration,
                metadata=metadata,
                config=config,
                feedback=feedback,
                metrics=metrics,
                **kwargs,
            )

            # Create event via API
            if self.client is not None:
                response = self.client.events.create_event(event_request)
                safe_log(
                    self,
                    "debug",
                    "🔍 DEBUG: API response received for event creation",
                    honeyhive_data={
                        "event_name": event_name,
                        "response_type": type(response).__name__,
                        "response_content": str(response)[:200] if response else "None",
                        "has_response": response is not None,
                    },
                )
            else:
                raise RuntimeError("Client not initialized")

            # Dynamic response processing
            event_id = self._extract_event_id_dynamically(response)
            safe_log(
                self,
                "debug",
                "🔍 DEBUG: Event ID extraction result",
                honeyhive_data={
                    "event_name": event_name,
                    "extracted_event_id": event_id,
                    "event_id_type": type(event_id).__name__ if event_id else "None",
                    "response_type": type(response).__name__ if response else "None",
                },
            )

            if event_id:
                safe_log(
                    self,
                    "debug",
                    f"Created event: {event_name}",
                    honeyhive_data={
                        "event_id": event_id,
                        "event_type": event_type,
                        "session_id": self._session_id,
                    },
                )
            else:
                safe_log(
                    self,
                    "warning",
                    "⚠️ DEBUG: Event creation returned no event_id",
                    honeyhive_data={
                        "event_name": event_name,
                        "response": str(response)[:500] if response else "None",
                        "response_type": (
                            type(response).__name__ if response else "None"
                        ),
                    },
                )

            return event_id

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to create event '{event_name}': {e}",
                honeyhive_data={
                    "event_type": event_type,
                    "error_type": type(e).__name__,
                },
            )
            return None

    def _can_create_event_dynamically(self) -> bool:
        """Dynamically check if event creation is possible."""
        # Check required components
        if not self.client:
            safe_log(self, "debug", "No API client available for event creation")
            return False

        # Check session availability
        target_session_id = self._get_target_session_id_dynamically()
        if not target_session_id:
            safe_log(self, "warning", "No session ID available for event creation")
            return False

        return True

    def _get_target_session_id_dynamically(self) -> Optional[str]:
        """Dynamically determine target session ID for event creation."""
        # Priority order: explicit session_id, current baggage session
        # Check both _session_id and session_id for backwards compatibility
        session_id = getattr(self, "_session_id", None) or getattr(
            self, "session_id", None
        )
        if session_id:
            safe_log(
                self,
                "debug",
                "🔍 DEBUG: Found session ID for event creation",
                honeyhive_data={
                    "session_id": session_id,
                    "source": (
                        "_session_id"
                        if hasattr(self, "_session_id") and self._session_id
                        else "session_id"
                    ),
                },
            )
            return str(session_id)

        # Check baggage for session ID
        try:
            baggage_session = (
                self.get_baggage(  # pylint: disable=assignment-from-no-return
                    "session_id"
                )
            )
            if baggage_session:
                return str(baggage_session)
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self,
                "debug",
                "Failed to get baggage session",
                honeyhive_data={"error_type": type(e).__name__},
            )

        return None

    # pylint: disable=too-many-arguments
    # Justification: Event request building requires many optional parameters
    # to support comprehensive event data structure.
    def _build_event_request_dynamically(
        self,
        event_name: str,
        event_type: str,
        *,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> CreateEventRequest:
        """Dynamically build event request with flexible parameter handling."""
        # Get target session ID
        target_session_id = self._get_target_session_id_dynamically()

        # Convert string event_type to EventType1 enum dynamically
        event_type_enum = self._convert_event_type_dynamically(event_type)

        # Build base request parameters with proper types using dynamic methods
        request_params: Dict[str, Any] = {
            "project": str(self.project_name) if self.project_name else "",
            "source": self._get_source_dynamically(),
            "session_id": str(target_session_id) if target_session_id else None,
            "event_name": str(event_name),
            "event_type": event_type_enum,
            "config": self._get_config_dynamically(config),
            "inputs": self._get_inputs_dynamically(inputs),
            "duration": self._get_duration_dynamically(duration),
        }

        # Add optional parameters dynamically
        optional_params = {
            "outputs": outputs,
            "error": error,
            "metadata": metadata,
            "feedback": feedback,
            "metrics": metrics,
        }

        for param_name, param_value in optional_params.items():
            if param_value is not None:
                # Ensure proper type conversion for each parameter
                if param_name in ["error"] and isinstance(param_value, str):
                    request_params[param_name] = param_value
                elif param_name in ["duration"] and isinstance(
                    param_value, (int, float)
                ):
                    request_params[param_name] = float(param_value)
                elif param_name in [
                    "inputs",
                    "outputs",
                    "metadata",
                    "config",
                    "feedback",
                    "metrics",
                ] and isinstance(param_value, dict):
                    request_params[param_name] = param_value
                else:
                    # For other types, convert to appropriate type or skip
                    request_params[param_name] = param_value

        # Add any additional kwargs dynamically
        for key, value in kwargs.items():
            if value is not None and key not in request_params:
                request_params[key] = value

        return CreateEventRequest(**request_params)

    def _convert_event_type_dynamically(self, event_type: str) -> EventType1:
        """Dynamically convert string event type to enum."""
        # Dynamic mapping with fallback
        type_mapping = {
            "model": EventType1.model,
            "tool": EventType1.tool,
            "chain": EventType1.chain,
        }

        # Handle session type - fallback to tool if not available
        if event_type.lower() == "session":
            # Check if session type exists, otherwise use tool
            return getattr(EventType1, "session", EventType1.tool)

        return type_mapping.get(event_type.lower(), EventType1.tool)

    def _extract_event_id_dynamically(self, response: Any) -> Optional[str]:
        """Dynamically extract event ID from API response."""
        safe_log(
            self,
            "debug",
            "🔍 DEBUG: Starting event ID extraction",
            honeyhive_data={
                "response_type": type(response).__name__,
                "response_str": str(response)[:300] if response else "None",
                "has_response": response is not None,
                "response_attrs": dir(response) if response else [],
            },
        )

        # Try different response formats dynamically
        id_attributes = ["event_id", "id", "uuid"]

        for attr in id_attributes:
            if hasattr(response, attr):
                event_id = getattr(response, attr)
                safe_log(
                    self,
                    "debug",
                    f"🔍 DEBUG: Found attribute {attr}",
                    honeyhive_data={
                        "attribute": attr,
                        "value": event_id,
                        "value_type": type(event_id).__name__ if event_id else "None",
                        "is_truthy": bool(event_id),
                    },
                )
                if event_id:
                    return str(event_id)

        # Try dictionary access if response is dict-like
        if hasattr(response, "get"):
            safe_log(
                self,
                "debug",
                "🔍 DEBUG: Trying dictionary access",
                honeyhive_data={
                    "response_keys": (
                        list(response.keys())
                        if hasattr(response, "keys")
                        else "no_keys_method"
                    )
                },
            )
            for attr in id_attributes:
                event_id = response.get(attr)
                safe_log(
                    self,
                    "debug",
                    f"🔍 DEBUG: Dictionary get for {attr}",
                    honeyhive_data={
                        "attribute": attr,
                        "value": event_id,
                        "value_type": type(event_id).__name__ if event_id else "None",
                        "is_truthy": bool(event_id),
                    },
                )
                if event_id:
                    return str(event_id)

        safe_log(
            self,
            "warning",
            "⚠️ DEBUG: No event ID found in response",
            honeyhive_data={
                "response_type": type(response).__name__,
                "tried_attributes": id_attributes,
                "response_content": str(response)[:500] if response else "None",
            },
        )
        return None

    def _get_source_dynamically(self) -> str:
        """Dynamically get source value with intelligent fallback."""
        # Try to get from tracer instance
        if hasattr(self, "source") and self.source:
            return str(self.source)

        # Try to get from config
        if hasattr(self, "config") and self.config:
            source = getattr(self.config, "source", None)
            if source:
                return str(source)

        # Intelligent fallback based on context
        if hasattr(self, "is_evaluation") and self.is_evaluation:
            return "evaluation"
        if hasattr(self, "test_mode") and getattr(self, "test_mode", False):
            return "test"
        return "dev"

    def _get_config_dynamically(
        self, config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Dynamically get config with intelligent defaults."""
        if config is not None:
            return config

        # Try to extract from current context or span
        if hasattr(self, "_current_span") and self._current_span:
            span_config = getattr(self._current_span, "config", None)
            if span_config:
                return dict(span_config)

        # Return empty dict as safe default
        return {}

    def _get_inputs_dynamically(
        self, inputs: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Dynamically get inputs with intelligent defaults."""
        if inputs is not None:
            return inputs

        # Try to extract from current context or span
        if hasattr(self, "_current_span") and self._current_span:
            span_inputs = getattr(self._current_span, "inputs", None)
            if span_inputs:
                return dict(span_inputs)

        # Return empty dict as safe default
        return {}

    def _get_duration_dynamically(self, duration: Optional[float]) -> float:
        """Dynamically get duration with intelligent calculation."""
        if duration is not None:
            return float(duration)

        # Try to calculate from current span timing
        if hasattr(self, "_current_span") and self._current_span:
            start_time = getattr(self._current_span, "start_time", None)
            end_time = getattr(self._current_span, "end_time", None)
            if start_time and end_time:
                calculated_duration = end_time - start_time
                if calculated_duration > 0:
                    return float(calculated_duration)

        # Return minimal duration as safe default
        return 0.0
