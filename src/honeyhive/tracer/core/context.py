"""Context and baggage management for HoneyHive tracer.

This module provides dynamic context management, baggage operations, and
session enrichment capabilities. It uses dynamic logic for flexible
context handling and robust state management.
"""

# pylint: disable=duplicate-code
# Justification: Legitimate shared patterns with decorator and operations mixins.
# Duplicate code represents common session enrichment and parameter building
# patterns shared across core mixin classes for consistent behavior.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from opentelemetry import baggage, context, trace
from opentelemetry.context import Context

from ...utils.logger import safe_log
from ..lifecycle import force_flush_tracer, shutdown_tracer
from ..processing.context import get_current_baggage

# Context processing imports - handle potential circular imports gracefully
try:
    from ..processing.context import (
        extract_context_from_carrier,
        inject_context_into_carrier,
    )
except ImportError:
    # Fallback for circular import issues
    extract_context_from_carrier = None  # type: ignore[assignment]
    inject_context_into_carrier = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from . import HoneyHiveTracer


class TracerContextInterface(ABC):  # pylint: disable=too-few-public-methods
    """Abstract interface for tracer context operations.
    This ABC defines the required methods that must be implemented by any class
    that uses TracerContextMixin. Provides explicit type safety and clear contracts.

    Note: too-few-public-methods disabled - ABC interface defines only abstract methods,
    concrete implementations in TracerContextMixin provide public methods.
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


class TracerContextMixin(TracerContextInterface):
    """Mixin providing dynamic context and baggage management for HoneyHive tracer.

    This mixin uses dynamic logic for baggage operations, context propagation,
    and session enrichment with comprehensive error handling and thread safety.

    This mixin requires implementation of TracerContextInterface abstract methods.
    """

    # Type hint for mypy - these attributes will be provided by the composed class
    if TYPE_CHECKING:
        client: Optional[Any]
        session_api: Optional[Any]
        _session_id: Optional[str]
        _baggage_lock: Any

    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush tracer data with dynamic timeout handling.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            True if flush successful, False otherwise
        """
        return force_flush_tracer(self, timeout_millis)

    def shutdown(self) -> None:
        """Shutdown tracer with dynamic cleanup including cache management."""
        # Clean up cache manager first to prevent resource leaks
        if hasattr(self, "_cache_manager") and self._cache_manager:
            try:
                self._cache_manager.close_all()
                safe_log(self, "debug", "Cache manager closed successfully")
            except Exception as e:
                # Graceful degradation - cache cleanup should not break shutdown
                safe_log(
                    self, "warning", f"Error closing cache manager during shutdown: {e}"
                )

        # Proceed with standard tracer shutdown
        shutdown_tracer(self)

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # Justification: Session enrichment requires multiple optional parameters
    # for comprehensive session data (inputs, outputs, metadata, config, etc.).
    def enrich_session(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Enrich current session with dynamic metadata management.

        **PRIMARY PATTERN (v1.0+):** This instance method is the recommended way
        to enrich sessions. It provides explicit tracer reference and works seamlessly
        in multi-instance environments.

        This method uses dynamic logic to update session metadata with
        flexible parameter handling and automatic session detection. Use it to
        add user properties, feedback, metrics, or custom metadata to sessions.

        Args:
            session_id: Optional explicit session ID to enrich.
                        If not provided, uses tracer's current session ID.
                        (Provided for backwards compatibility)
            metadata: Additional metadata for the session
            inputs: Session input data (captured at session start)
            outputs: Session output data (captured at session end)
            config: Configuration data used during session
            feedback: User feedback or evaluation results
            metrics: Performance metrics (latency, token count, etc.)
            user_properties: User-specific properties (user_id, plan, etc.)
                             Automatically prefixed with 'user_properties.'
            **kwargs: Additional dynamic parameters

        Examples:
            Basic session enrichment::

                tracer = HoneyHiveTracer.init(api_key="...", project="...")

                # Enrich with user properties
                tracer.enrich_session(
                    user_properties={"user_id": "user-123", "plan": "premium"}
                )

            Enrichment with feedback and metrics::

                # After processing user request
                tracer.enrich_session(
                    inputs={"query": "What is AI?"},
                    outputs={"response": "AI is..."},
                    feedback={"rating": 5, "helpful": True},
                    metrics={"latency_ms": 250, "tokens": 150}
                )

            Multiple enrichments throughout session::

                # At session start
                tracer.enrich_session(
                    metadata={"source": "web-app"},
                    user_properties={"user_id": "user-456"}
                )

                # During processing
                tracer.enrich_session(
                    metrics={"api_calls": 3}
                )

                # At session end
                tracer.enrich_session(
                    outputs={"final_result": "success"},
                    feedback={"satisfaction": "high"}
                )

        Note:
            **Backwards Compatibility:** This method maintains compatibility
            with v0.2.x signature. The free function ``enrich_session()``
            is also available but will be deprecated in v2.0.
            See :func:`honeyhive.tracer.integration.compatibility.enrich_session`

        See Also:
            - :meth:`enrich_span` - Enrich individual spans with metadata
            - :meth:`session_start` - Start a new session
            - :meth:`session_end` - End current session

        .. versionadded:: 1.0
            Instance method pattern introduced as primary API.
        """
        if not self._can_enrich_session_dynamically():
            return

        try:
            # Build session update parameters dynamically
            # user_properties should be passed directly to API, not merged into metadata
            update_params = self._build_session_update_params_dynamically(
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                config=config,
                feedback=feedback,
                metrics=metrics,
                user_properties=user_properties,
                **kwargs,
            )

            # Get target session ID - use explicit session_id if provided
            # (backwards compat). Otherwise fall back to dynamic detection
            target_session_id: Optional[str]
            if session_id:
                target_session_id = session_id
            else:
                target_session_id = self._get_session_id_for_enrichment_dynamically()

            if target_session_id and update_params:
                # Update session via EventsAPI (sessions are events in the backend)
                # Import here to avoid circular dependency
                from ...api.events import (  # pylint: disable=import-outside-toplevel
                    UpdateEventRequest,
                )

                if self.client is not None and hasattr(self.client, "events"):
                    update_request = UpdateEventRequest(
                        event_id=target_session_id, **update_params
                    )
                    self.client.events.update_event(update_request)
                else:
                    safe_log(self, "warning", "Events API not available for update")

                safe_log(
                    self,
                    "debug",
                    "Session enriched successfully",
                    honeyhive_data={
                        "session_id": target_session_id,
                        "update_fields": list(update_params.keys()),
                    },
                )

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to enrich session: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )

    def session_start(self) -> Optional[str]:
        """Start a new session and return session ID.

        Creates a new session using the tracer's configuration and returns
        the session ID. This provides backward compatibility with the original
        SDK's session_start() method.

        Returns:
            Session ID if successful, None otherwise

        Example:
            >>> tracer = HoneyHiveTracer(api_key="...", project="...")
            >>> session_id = tracer.session_start()
            >>> print(f"Created session: {session_id}")
        """
        if not self.session_api:
            safe_log(self, "warning", "No session API available for session creation")
            return None

        try:
            # Use existing session creation logic from base class
            if hasattr(self, "_create_session_dynamically"):
                self._create_session_dynamically()  # type: ignore[attr-defined]
                return getattr(self, "_session_id", None)

            # Fallback: create session directly
            safe_log(self, "error", "Session creation method not available")
            return None
        except Exception as e:
            safe_log(
                self,
                "error",
                "Failed to start session",
                honeyhive_data={"error": str(e), "error_type": type(e).__name__},
            )
            return None

    def _can_enrich_session_dynamically(self) -> bool:
        """Dynamically check if session enrichment is possible."""
        # Check if client with events API is available (for session updates)
        if not self.client or not hasattr(self.client, "events"):
            safe_log(self, "debug", "No session API available for enrichment")
            return False

        if not self._get_session_id_for_enrichment_dynamically():
            safe_log(self, "debug", "No session ID available for enrichment")
            return False

        return True

    def _get_session_id_for_enrichment_dynamically(self) -> Optional[str]:
        """Dynamically get session ID for enrichment operations."""
        # Priority: explicit session_id, baggage session_id
        if self._session_id:
            return str(self._session_id)

        # Check baggage dynamically
        try:
            # Use dynamic baggage access
            current_baggage = get_current_baggage()
            baggage_session = current_baggage.get("session_id")
            if baggage_session:
                return baggage_session
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self,
                "debug",
                "Failed to get session from baggage",
                honeyhive_data={"error_type": type(e).__name__},
            )

        return None

    # pylint: disable=too-many-arguments
    # Justification: Session parameter building requires multiple optional parameters
    # for flexible session update configuration.
    def _build_session_update_params_dynamically(
        self,
        *,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dynamically build session update parameters.

        Maps parameters to UpdateEventRequest supported fields only.
        Unsupported fields (inputs, unrecognized kwargs) are merged into metadata.

        UpdateEventRequest supports: metadata, feedback, metrics, outputs,
        config, user_properties, duration (see src/honeyhive/api/events.py:45)
        """
        # Fields supported by UpdateEventRequest
        # pylint: disable=invalid-name  # SUPPORTED_FIELDS is semantically a constant
        SUPPORTED_FIELDS = {
            "metadata",
            "feedback",
            "metrics",
            "outputs",
            "config",
            "user_properties",
            "duration",
        }

        # Start with provided metadata (or empty dict)
        merged_metadata = dict(metadata) if metadata else {}

        # Map inputs to metadata (NOT supported by UpdateEventRequest)
        if inputs:
            merged_metadata["inputs"] = inputs
            safe_log(
                self,
                "debug",
                "Mapped 'inputs' to metadata (not supported by UpdateEventRequest)",
            )

        # Map unsupported kwargs to metadata
        unsupported_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in SUPPORTED_FIELDS and v is not None
        }
        if unsupported_kwargs:
            merged_metadata.update(unsupported_kwargs)
            safe_log(
                self,
                "debug",
                "Mapped unsupported kwargs to metadata: %s",
                list(unsupported_kwargs.keys()),
            )

        # Build update params with only supported fields
        update_params = {}

        if merged_metadata:
            update_params["metadata"] = merged_metadata

        if outputs:
            update_params["outputs"] = outputs

        if config:
            update_params["config"] = config

        if feedback:
            update_params["feedback"] = feedback

        if metrics:
            update_params["metrics"] = metrics

        if user_properties:
            update_params["user_properties"] = user_properties

        # Handle duration from kwargs if present (supported field)
        if "duration" in kwargs and kwargs["duration"] is not None:
            update_params["duration"] = kwargs["duration"]

        return update_params

    def enrich_span(
        self,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        event_id: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Enrich current span with dynamic attribute management.

        **PRIMARY PATTERN (v1.0+):** This instance method is the recommended way
        to enrich spans. It provides explicit tracer reference and works seamlessly
        in multi-instance environments.

        This method uses dynamic logic to add attributes to the current span
        with flexible parameter handling and automatic span detection. It enriches
        the currently active span with metadata, metrics, or custom attributes.

        Args:
            attributes: Span attributes to add directly (dict of key-value pairs)
            metadata: Metadata to add (automatically prefixed with
                'honeyhive_metadata.')
            metrics: Metrics to add (automatically prefixed with 'honeyhive_metrics.')
            feedback: Feedback to add (automatically prefixed with
                'honeyhive_feedback.')
            inputs: Inputs to add (automatically prefixed with 'honeyhive_inputs.')
            outputs: Outputs to add (automatically prefixed with 'honeyhive_outputs.')
            config: Config to add (automatically prefixed with 'honeyhive_config.')
            user_properties: User properties to add (automatically prefixed with
                'honeyhive_user_properties.' for spans)
            error: Error message (stored as 'honeyhive_error')
            event_id: Event ID (stored as 'honeyhive_event_id')
            **kwargs: Additional dynamic attributes (routed to metadata namespace)

        Returns:
            True if enrichment succeeded, False otherwise

        Examples:
            Basic enrichment with metadata::

                from honeyhive import trace
                tracer = HoneyHiveTracer.init(api_key="...", project="...")

                @trace(tracer=tracer, event_type="tool")
                def process_data(input_text):
                    result = transform(input_text)

                    # Enrich with metadata and metrics
                    tracer.enrich_span(
                        metadata={"input": input_text, "result": result},
                        metrics={"processing_time_ms": 150}
                    )

                    return result

            Enrichment with user_properties and metrics::

                tracer.enrich_span(
                    user_properties={"user_id": "user-123", "plan": "premium"},
                    metrics={"score": 0.95, "latency_ms": 150}
                )

        Note:
            For backward compatibility, the free function ``enrich_span()``
            is also available but will be deprecated in v2.0.
            See :func:`honeyhive.tracer.integration.compatibility.enrich_span`

        See Also:
            - :meth:`enrich_session` - Enrich session with metadata
            - :meth:`start_span` - Create and manage spans manually
            - :meth:`trace` - Decorator for automatic span creation

        .. versionadded:: 1.0
            Instance method pattern introduced as primary API.
        """
        try:
            # Get current span dynamically
            current_span = self._get_current_span_dynamically()
            if not current_span or not current_span.is_recording():
                safe_log(self, "debug", "No active recording span for enrichment")
                return False

            # Use the enrichment core logic which handles reserved parameters correctly
            # Import here to avoid circular dependency
            from ..instrumentation.enrichment import (  # pylint: disable=import-outside-toplevel
                enrich_span_core,
            )

            result = enrich_span_core(
                attributes=attributes,
                metadata=metadata,
                metrics=metrics,
                feedback=feedback,
                inputs=inputs,
                outputs=outputs,
                config=config,
                error=error,
                event_id=event_id,
                tracer_instance=self,
                verbose=False,
                # Handle user_properties specially - for spans, it goes to a namespace
                user_properties=user_properties,
                **kwargs,
            )

            if result.get("success"):
                safe_log(
                    self,
                    "debug",
                    "Span enriched successfully",
                    honeyhive_data={
                        "attribute_count": result.get("attribute_count", 0)
                    },
                )

            return bool(result.get("success", False))

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to enrich span: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return False

    def _get_current_span_dynamically(self) -> Any:
        """Dynamically get the current active span."""
        try:
            return trace.get_current_span()
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self,
                "debug",
                "Failed to get current span",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return None

    def _build_enrichment_attributes_dynamically(
        self,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dynamically build enrichment attributes from multiple sources."""
        enrichment_attrs = {}

        # Add direct attributes
        if attributes:
            enrichment_attrs.update(attributes)

        # Add metadata with prefix
        if metadata:
            for key, value in metadata.items():
                prefixed_key = f"honeyhive_metadata.{key}"
                enrichment_attrs[prefixed_key] = value

        # Add kwargs dynamically
        for key, value in kwargs.items():
            if value is not None:
                # Normalize key for OpenTelemetry
                normalized_key = self._normalize_attribute_key_dynamically(key)
                enrichment_attrs[normalized_key] = value

        return enrichment_attrs

    def _apply_attributes_to_span_dynamically(
        self, span: Any, attributes: Dict[str, Any]
    ) -> None:
        """Dynamically apply attributes to span with error handling."""
        for key, value in attributes.items():
            try:
                # Normalize value for OpenTelemetry compatibility
                normalized_value = self._normalize_attribute_value_dynamically(value)
                if normalized_value is not None:
                    span.set_attribute(key, normalized_value)
            except Exception as e:
                safe_log(
                    self,
                    "warning",
                    f"Failed to set span attribute '{key}': {e}",
                    honeyhive_data={"attribute_key": key},
                )

    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage value using dynamic context access.

        Args:
            key: Baggage key to retrieve

        Returns:
            Baggage value if found, None otherwise
        """
        try:
            # Use dynamic baggage access with error handling
            current_baggage = get_current_baggage()

            # Dynamic key lookup with normalization
            normalized_key = self._normalize_baggage_key_dynamically(key)

            # Try multiple key formats dynamically
            key_variants = [key, normalized_key, key.lower(), key.upper()]

            for variant in key_variants:
                if variant in current_baggage:
                    value = current_baggage[variant]
                    safe_log(
                        self,
                        "debug",
                        f"Retrieved baggage: {key}",
                        honeyhive_data={"key": key, "found_as": variant},
                    )
                    return value

            return None

        except Exception as e:
            safe_log(
                self,
                "warning",
                f"Failed to get baggage '{key}': {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return None

    def _normalize_baggage_key_dynamically(self, key: str) -> str:
        """Dynamically normalize baggage key for consistent access."""
        # Replace common separators with underscores
        normalized = key.replace("-", "_").replace(".", "_").replace(" ", "_")
        return normalized.lower()

    def set_baggage(self, key: str, value: str) -> None:
        """Set baggage value using dynamic context management.

        Args:
            key: Baggage key to set
            value: Baggage value to set
        """
        if not key or value is None:
            return

        try:
            with self._baggage_lock:
                # Dynamic baggage setting with context management
                current_ctx = context.get_current()

                # Normalize key and value dynamically
                normalized_key = self._normalize_baggage_key_dynamically(key)
                normalized_value = str(value) if value is not None else ""

                # Set baggage in current context
                new_ctx = baggage.set_baggage(
                    normalized_key, normalized_value, current_ctx
                )

                # Attach context (implementation depends on usage pattern)
                context.attach(new_ctx)

                safe_log(
                    self,
                    "debug",
                    f"Set baggage: {key}",
                    honeyhive_data={
                        "key": key,
                        "normalized_key": normalized_key,
                        "value_length": len(normalized_value),
                    },
                )

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to set baggage '{key}': {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )

    def inject_context(self, carrier: Dict[str, str]) -> None:
        """Inject current context into carrier using dynamic propagation.

        Args:
            carrier: Dictionary to inject context into
        """
        try:
            # Dynamic context injection with error handling
            if inject_context_into_carrier is not None:
                inject_context_into_carrier(carrier, cast("HoneyHiveTracer", self))
            else:
                safe_log(self, "warning", "Context injection not available")

            safe_log(
                self,
                "debug",
                "Context injected into carrier",
                honeyhive_data={
                    "carrier_keys": list(carrier.keys()),
                    "injection_count": len(carrier),
                },
            )

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to inject context: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )

    def extract_context(self, carrier: Dict[str, str]) -> Optional["Context"]:
        """Extract context from carrier using dynamic propagation.

        Args:
            carrier: Dictionary to extract context from

        Returns:
            Extracted context if successful, None otherwise
        """
        try:
            # Dynamic context extraction with validation
            if extract_context_from_carrier is not None:
                extracted_context = extract_context_from_carrier(
                    carrier, cast("HoneyHiveTracer", self)
                )
            else:
                extracted_context = None

            if extracted_context:
                safe_log(
                    self,
                    "debug",
                    "Context extracted from carrier",
                    honeyhive_data={
                        "carrier_keys": list(carrier.keys()),
                        "extraction_successful": True,
                    },
                )
                return extracted_context

            safe_log(
                self,
                "debug",
                "No context found in carrier",
                honeyhive_data={"carrier_keys": list(carrier.keys())},
            )
            return None

        except Exception as e:
            safe_log(
                self,
                "error",
                f"Failed to extract context: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return None
