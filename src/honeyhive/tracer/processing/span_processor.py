"""HoneyHive span processor for OpenTelemetry integration."""

import json
from typing import Any, Dict, Optional

from opentelemetry import baggage
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

from ...utils.logger import safe_log
from ..processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor
from ..utils.event_type import detect_event_type_from_patterns

# Note: Pre-end processing moved to span_interception.py


class HoneyHiveSpanProcessor(SpanProcessor):
    """HoneyHive span processor with two modes:

    1. Client mode: Use HoneyHive SDK client directly (Events API)
    2. OTLP mode: Use OTLP exporter for both immediate and batch processing
       - disable_batch=True: OTLP exporter sends spans immediately
       - disable_batch=False: OTLP exporter batches spans before sending
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        disable_batch: bool = False,
        otlp_exporter: Optional[Any] = None,
        tracer_instance: Optional[Any] = None,
    ) -> None:
        """Initialize the span processor.

        :param client: HoneyHive API client for direct Events API usage
        :type client: Optional[Any]
        :param disable_batch: If True, process spans immediately; if False, use batch
        :type disable_batch: bool
        :param otlp_exporter: OTLP exporter for batch mode (when disable_batch=False)
        :type otlp_exporter: Optional[Any]
        :param tracer_instance: Reference to the tracer instance for configuration
        :type tracer_instance: Optional[Any]
        """
        self.client = client
        self.disable_batch = disable_batch
        self.otlp_exporter = otlp_exporter
        self.tracer_instance = tracer_instance

        # Note: Pre-end processing is now handled via span interception
        # in the tracer's start_span method, not via on_end hooks
        # See span_interception.py for the correct implementation

        # Determine processing mode
        if client is not None:
            self.mode = "client"
            safe_log(
                self.tracer_instance,
                "debug",
                "HoneyHiveSpanProcessor initialized in CLIENT mode (direct API)",
            )
        else:
            self.mode = "otlp"
            batch_mode = "immediate" if disable_batch else "batch"
            safe_log(
                self.tracer_instance,
                "debug",
                "HoneyHiveSpanProcessor initialized in OTLP mode (%s)",
                batch_mode,
            )

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span starts - enrich with session and user context.

        :param span: The span that is starting
        :type span: Span
        :param parent_context: The parent context (optional)
        :type parent_context: Optional[Context]
        """
        try:
            span_context = span.get_span_context()
            safe_log(
                self.tracer_instance,
                "debug",
                "Span processor on_start called",
                honeyhive_data={
                    "span_name": span.name,
                    "span_id": span_context.span_id if span_context else None,
                    "trace_id": span_context.trace_id if span_context else None,
                },
            )

            # Process all spans to HoneyHive schema (add honeyhive.* attributes)
            # Note: Convention detection will happen in on_end when all attributes
            # are available

            # Extract session_id from multiple sources with priority order
            session_id = self._extract_session_id(parent_context)

            if session_id:
                # Set HoneyHive session_id for backend processing
                span.set_attribute("honeyhive.session_id", session_id)

                # Set Traceloop association for dual compatibility
                span.set_attribute(
                    "traceloop.association.properties.session_id", session_id
                )

                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Session ID extracted and set on span",
                    honeyhive_data={
                        "session_id": session_id,
                        "span_name": span.name,
                    },
                )

            # Extract user_id from context if available
            user_id = self._extract_user_id(parent_context)
            if user_id:
                span.set_attribute("honeyhive.user_id", user_id)
                span.set_attribute("traceloop.association.properties.user_id", user_id)

            # Extract project from tracer instance
            if self.tracer_instance and hasattr(self.tracer_instance, "project"):
                project = self.tracer_instance.project
                if project:
                    span.set_attribute("honeyhive.project", project)
                    span.set_attribute(
                        "traceloop.association.properties.project", project
                    )

            # Extract source from tracer instance
            if self.tracer_instance and hasattr(self.tracer_instance, "source"):
                source = self.tracer_instance.source
                if source:
                    span.set_attribute("honeyhive.source", source)
                    span.set_attribute(
                        "traceloop.association.properties.source", source
                    )

            # Set event type for better categorization
            event_type = self._determine_event_type(span)
            if event_type:
                span.set_attribute("honeyhive_event_type", event_type)

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                self.tracer_instance,
                "debug",
                "Error in span enrichment",
                honeyhive_data={
                    "error": str(e),
                    "span_name": span.name,
                    "error_type": type(e).__name__,
                },
            )

    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends - execute pre-end hooks then send span data.

        This method implements the pre-end hook system to process spans while
        they are still mutable, before sending them via the configured export method.

        :param span: The span that is ending
        :type span: ReadableSpan
        """

        try:
            # Skip invalid spans
            span_context = span.get_span_context()
            if span_context is None or span_context.span_id == 0:
                return

            # NOTE: Semantic convention processing now happens via span interception
            # in the tracer's start_span method, before span.end() is called.
            # This ensures processing happens while span is still mutable.
            # See span_interception.py for implementation details.

            # Extract attributes for processing (after hooks have run)
            attributes = dict(span.attributes) if span.attributes else {}

            # Extract session_id for export validation
            session_id_raw = attributes.get("honeyhive.session_id") or attributes.get(
                "traceloop.association.properties.session_id"
            )

            if not session_id_raw:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Span has no session_id, skipping HoneyHive export - "
                    "available attributes: %s",
                    list(attributes.keys())[:10],
                )
                return

            session_id = str(session_id_raw)

            safe_log(
                self.tracer_instance,
                "debug",
                "Span processor on_end called - mode: %s, span: %s, session_id: %s",
                self.mode,
                span.name,
                session_id,
            )

            # Process span based on mode
            if self.mode == "client" and self.client:
                self._send_via_client(span, attributes, session_id)
            elif self.mode == "otlp" and self.otlp_exporter:
                self._send_via_otlp(span, attributes, session_id)
            else:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "No valid export method for mode: %s, client: %s, exporter: %s",
                    self.mode,
                    self.client is not None,
                    self.otlp_exporter is not None,
                )

        except Exception as e:
            # Error processing span end - continue without disrupting application
            safe_log(
                self.tracer_instance, "debug", "Error in span processor on_end: %s", e
            )

    # NOTE: Pre-end hook methods removed - processing now happens via
    # span interception in tracer's start_span method.
    # See span_interception.py for the correct implementation.

    def _send_via_client(
        self, span: ReadableSpan, attributes: dict, session_id: str
    ) -> None:
        """Send span via HoneyHive SDK client (Events API).

        :param span: The span to send
        :type span: ReadableSpan
        :param attributes: Span attributes dictionary
        :type attributes: dict
        :param session_id: Session identifier
        :type session_id: str
        """
        try:
            safe_log(self.tracer_instance, "debug", "OTLP EXPORT CALLED - CLIENT MODE")

            # Convert span to event format
            event_data = self._convert_span_to_event(span, attributes, session_id)

            # Send via client
            if self.client and hasattr(self.client, "create_event"):
                response = self.client.create_event(event_data)
                safe_log(
                    self.tracer_instance, "debug", "Event sent via client: %s", response
                )
            else:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "Client not available or missing create_event method",
                )

        except Exception as e:
            safe_log(self.tracer_instance, "debug", "Error sending via client: %s", e)

    def _send_via_otlp(
        self,
        span: ReadableSpan,
        attributes: dict,  # pylint: disable=unused-argument
        session_id: str,  # pylint: disable=unused-argument
    ) -> None:
        """Send span via OTLP exporter.

        :param span: The span to send
        :type span: ReadableSpan
        :param attributes: Span attributes dictionary
        :type attributes: dict
        :param session_id: Session identifier
        :type session_id: str
        """
        try:
            batch_mode = "immediate" if self.disable_batch else "batch"
            safe_log(
                self.tracer_instance,
                "debug",
                "OTLP EXPORT: Sending span %s (%s mode) - semantic conventions "
                "already processed",
                span.name,
                batch_mode,
            )

            # Export via OTLP exporter
            if self.otlp_exporter and hasattr(self.otlp_exporter, "export"):
                result = self.otlp_exporter.export([span])
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Span exported via OTLP exporter (%s mode)",
                    batch_mode,
                )

                # Log result if available
                if hasattr(result, "name"):
                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "OTLP export result: %s",
                        result.name,
                    )
            else:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "OTLP exporter not available or missing export method",
                )

        except Exception as e:
            safe_log(self.tracer_instance, "error", "Error sending via OTLP: %s", e)

    def _apply_semantic_conventions_on_start(self, span: Span) -> None:
        """Apply semantic convention processing while span is mutable.

        Note: Convention detection happens in on_end when all attributes are available.

        :param span: The mutable span to process
        :type span: Span
        """
        try:
            # Early returns to reduce nesting
            current_attributes = dict(span.attributes) if span.attributes else {}
            if not current_attributes:
                return

            cache_manager = self._get_cache_manager()
            # Cache manager is optional for universal processor
            
            # Initialize universal processor (singleton per tracer instance)
            if not hasattr(self, '_universal_processor'):
                self._universal_processor = UniversalSemanticConventionProcessor(cache_manager)
            
            # Process semantic conventions using Universal LLM Discovery Engine v4.0
            self._process_span_semantic_conventions(
                span, self._universal_processor, current_attributes
            )

        except Exception as e:
            # Graceful degradation - never crash the host application
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to apply semantic conventions in on_start: %s",
                e,
            )

    def _get_cache_manager(self) -> Any:
        """Get cache manager from tracer instance."""
        return getattr(self.tracer_instance, "cache_manager", None) or getattr(
            self.tracer_instance, "_cache_manager", None
        )

    def _process_span_semantic_conventions(
        self, span: Any, universal_processor: Any, current_attributes: Dict[str, Any]
    ) -> None:
        """Process semantic conventions using Universal LLM Discovery Engine v4.0."""
        # Filter out HoneyHive attributes for provider detection
        filtered_attributes = {
            k: v
            for k, v in current_attributes.items()
            if not k.startswith(("honeyhive", "traceloop.association.properties"))
        }

        if not filtered_attributes:
            return

        # Process using Universal LLM Discovery Engine v4.0 (O(1) detection)
        event_data = universal_processor.processor.process_span_attributes(filtered_attributes)

        # Check if provider was detected
        detected_provider = event_data.get("metadata", {}).get("provider", "unknown")
        
        if detected_provider == "unknown":
            return

        # Apply event data to span
        self._apply_event_sections_to_span(span, event_data)

        # Set provider detection info
        span.set_attribute("honeyhive.detected_provider", detected_provider)
        span.set_attribute("honeyhive.universal_engine_version", "4.0")

        safe_log(
            self.tracer_instance,
            "info",
            "Applied %s provider conventions to span %s using Universal Engine v4.0",
            detected_provider,
            span.name,
        )

    def _apply_event_sections_to_span(
        self, span: Any, event_data: Dict[str, Any]
    ) -> None:
        """Apply all event data sections to span."""
        # Set nested attributes for inputs
        self._apply_section_to_span_attributes(
            span, event_data.get("inputs"), "honeyhive_inputs"
        )

        # Set nested attributes for outputs
        self._apply_section_to_span_attributes(
            span, event_data.get("outputs"), "honeyhive_outputs"
        )

        # Set nested attributes for config
        self._apply_section_to_span_attributes(
            span, event_data.get("config"), "honeyhive_config"
        )

        # Set nested attributes for metadata
        self._apply_section_to_span_attributes(
            span, event_data.get("metadata"), "honeyhive_metadata"
        )

    def _apply_section_to_span_attributes(
        self, span: Any, section_data: Any, prefix: str
    ) -> None:
        """Apply a section of data to span attributes."""
        if not section_data or not isinstance(section_data, dict):
            return

        for key, value in section_data.items():
            span.set_attribute(
                f"{prefix}.{key}",
                (json.dumps(value) if isinstance(value, (dict, list)) else str(value)),
            )

    def _extract_session_id(
        self, parent_context: Optional[Context] = None
    ) -> Optional[str]:
        """Extract session_id from multiple sources with priority order.

        :param parent_context: Optional parent context
        :type parent_context: Optional[Context]
        :return: Session ID if found
        :rtype: Optional[str]
        """
        # Priority 1: Tracer instance session_id (multi-instance architecture)
        if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
            session_id = self.tracer_instance.session_id
            if session_id:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Using tracer instance session_id for multi-instance",
                    honeyhive_data={"session_id": session_id},
                )
                return str(session_id)

        # Priority 2: OpenTelemetry baggage
        try:
            if parent_context:
                baggage_session_id = baggage.get_baggage("session_id", parent_context)
            else:
                baggage_session_id = baggage.get_baggage("session_id")

            if baggage_session_id:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Using baggage session_id (fallback)",
                    honeyhive_data={"session_id": baggage_session_id},
                )
                return str(baggage_session_id)
        except Exception:
            # Baggage access can fail in some contexts
            pass

        return None

    def _extract_user_id(
        self, parent_context: Optional[Context] = None
    ) -> Optional[str]:
        """Extract user_id from context.

        :param parent_context: Optional parent context
        :type parent_context: Optional[Context]
        :return: User ID if found
        :rtype: Optional[str]
        """
        try:
            if parent_context:
                user_id = baggage.get_baggage("user_id", parent_context)
            else:
                user_id = baggage.get_baggage("user_id")
            return str(user_id) if user_id else None
        except Exception:
            return None

    def _determine_event_type(self, span: Span) -> Optional[str]:
        """Determine event type from span characteristics.

        :param span: The span to analyze
        :type span: Span
        :return: Event type if determinable
        :rtype: Optional[str]
        """
        try:
            # Extract raw attributes for event type detection
            raw_attributes = dict(span.attributes) if span.attributes else {}

            # Use dynamic pattern matching for event type detection
            event_type = detect_event_type_from_patterns(
                span_name=span.name,
                attributes=raw_attributes,
            )

            return event_type if event_type != "unknown" else None

        except Exception:
            return None

    def _convert_span_to_event(
        self, span: ReadableSpan, attributes: dict, session_id: str
    ) -> dict:
        """Convert OpenTelemetry span to HoneyHive event format.

        :param span: The span to convert
        :type span: ReadableSpan
        :param attributes: Span attributes
        :type attributes: dict
        :param session_id: Session identifier
        :type session_id: str
        :return: Event data in HoneyHive format
        :rtype: dict
        """
        try:
            # Build basic event structure
            event_data = {
                "project": attributes.get("honeyhive.project", "default"),
                "source": attributes.get("honeyhive.source", "python-sdk"),
                "session_id": session_id,
                "event_name": span.name,
                "event_type": attributes.get("honeyhive_event_type", "unknown"),
                "start_time": (
                    int(span.start_time / 1_000_000) if span.start_time else None
                ),  # Convert to milliseconds
                "end_time": int(span.end_time / 1_000_000) if span.end_time else None,
                "inputs": {},
                "outputs": {},
                "error": None,
                "metadata": {},
                "config": {},
            }

            # Extract processed semantic convention data from span attributes
            for key, value in attributes.items():
                if key.startswith("honeyhive_inputs."):
                    field_name = key[len("honeyhive_inputs.") :]
                    event_data["inputs"][field_name] = self._parse_json_or_direct(value)
                elif key.startswith("honeyhive_outputs."):
                    field_name = key[len("honeyhive_outputs.") :]
                    event_data["outputs"][field_name] = self._parse_json_or_direct(
                        value
                    )
                elif key.startswith("honeyhive_config."):
                    field_name = key[len("honeyhive_config.") :]
                    event_data["config"][field_name] = self._parse_json_or_direct(value)
                elif key.startswith("honeyhive_metadata."):
                    field_name = key[len("honeyhive_metadata.") :]
                    event_data["metadata"][field_name] = self._parse_json_or_direct(
                        value
                    )

            # Add span context information
            span_context = span.get_span_context()
            if span_context:
                event_data["metadata"]["span_id"] = str(span_context.span_id)
                event_data["metadata"]["trace_id"] = str(span_context.trace_id)

            # Calculate duration if both timestamps are available
            if (
                span.start_time
                and span.end_time
                and span.start_time > 0
                and span.end_time > 0
            ):
                duration_ms = (span.end_time - span.start_time) / 1_000_000
                event_data["duration"] = duration_ms

            return event_data

        except Exception as e:
            safe_log(
                self.tracer_instance, "error", "Error converting span to event: %s", e
            )
            # Return minimal event structure on error
            return {
                "project": "default",
                "source": "python-sdk",
                "session_id": session_id,
                "event_name": span.name,
                "event_type": "unknown",
                "inputs": {},
                "outputs": {},
                "error": str(e),
                "metadata": {},
                "config": {},
            }

    def _parse_json_or_direct(self, value: Any) -> Any:
        """Parse JSON string or return value directly.

        :param value: Value to parse
        :type value: Any
        :return: Parsed value or original value
        :rtype: Any
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return value
        return value

    def shutdown(self) -> None:
        """Shutdown the span processor."""
        safe_log(
            self.tracer_instance, "debug", "HoneyHiveSpanProcessor shutdown called"
        )

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending spans.

        :param timeout_millis: Timeout in milliseconds
        :type timeout_millis: int
        :return: True if successful
        :rtype: bool
        """
        safe_log(
            self.tracer_instance, "debug", "HoneyHiveSpanProcessor force_flush called"
        )
        return True
