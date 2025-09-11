"""HoneyHive span processor for OpenTelemetry integration."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from opentelemetry import baggage, context
    from opentelemetry.context import Context
    from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

try:
    from opentelemetry import baggage, context
    from opentelemetry.context import Context
    from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

from ..utils.config import config


class HoneyHiveSpanProcessor(SpanProcessor):
    """HoneyHive span processor using baggage for context information."""

    def __init__(self) -> None:
        """Initialize the span processor."""
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for HoneyHiveSpanProcessor")

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span starts - enriches spans with HoneyHive attributes from baggage."""
        if not OTEL_AVAILABLE:
            return

        try:
            # Get current context (use parent_context if provided, otherwise get_current)
            ctx = (
                parent_context if parent_context is not None else context.get_current()
            )
            if not ctx:
                return

            # Compute attributes from baggage - no caching needed
            attributes_to_set = {}

            # Try to get session_id from baggage first
            session_id = baggage.get_baggage("session_id", ctx)

            # If no session_id in baggage, try to get it from the span name or attributes
            # This helps catch OpenInference spans that might not have explicit baggage
            if not session_id:
                # Check if this is an OpenAI-related span (OpenInference creates these)
                if any(
                    keyword in span.name.lower()
                    for keyword in ["openai", "chat", "completion", "gpt"]
                ):
                    # This looks like an OpenInference span
                    # Try to get session context from baggage instead of global state
                    session_id = baggage.get_baggage("session_id", ctx)
                    if session_id:
                        # Add session context to this span
                        attributes_to_set["honeyhive.session_id"] = session_id

                        # Get project and source from baggage
                        project = baggage.get_baggage("project", ctx)
                        if project:
                            attributes_to_set["honeyhive.project"] = project

                        source = baggage.get_baggage("source", ctx)
                        if source:
                            attributes_to_set["honeyhive.source"] = source

                        # OpenInference span enriched with session context from baggage
                        pass
                    # else: No session context in baggage, skipping enrichment
                # else: Not an OpenInference span

            # Always process association_properties for legacy support
            # This ensures backward compatibility regardless of session_id status
            try:
                # Check if context has association_properties (legacy support)
                if hasattr(ctx, "get") and callable(getattr(ctx, "get", None)):
                    association_properties = ctx.get("association_properties")
                    if association_properties and isinstance(
                        association_properties, dict
                    ):
                        # Found association_properties
                        for key, value in association_properties.items():
                            if value is not None and not baggage.get_baggage(key, ctx):
                                # Always set traceloop.association.properties.* format for backend compatibility
                                attr_key = f"traceloop.association.properties.{key}"
                                attributes_to_set[attr_key] = str(value)
                                # Set traceloop.association.properties attribute
            except Exception:
                # Error checking association_properties
                pass

            # If we have session_id from baggage, process normally
            if session_id:
                # Set honeyhive.* attributes (primary format)
                attributes_to_set["honeyhive.session_id"] = session_id

                # Add project from baggage (backend will handle if missing)
                project = baggage.get_baggage("project", ctx)
                if project:
                    attributes_to_set["honeyhive.project"] = project
                else:
                    # No project in baggage - backend will derive from API key
                    pass

                # Add source from baggage
                source = baggage.get_baggage("source", ctx)
                if source:
                    attributes_to_set["honeyhive.source"] = source

                # Add parent_id from baggage
                parent_id = baggage.get_baggage("parent_id", ctx)
                if parent_id:
                    attributes_to_set["honeyhive.parent_id"] = parent_id

                # Add experiment harness information from configuration
                try:
                    if config.experiment_id:
                        attributes_to_set["honeyhive.experiment_id"] = (
                            config.experiment_id
                        )
                        # Added experiment ID

                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = (
                            config.experiment_name
                        )
                        # Added experiment name

                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = (
                            config.experiment_variant
                        )
                        # Added experiment variant

                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = (
                            config.experiment_group
                        )
                        # Added experiment group

                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        # Added experiment metadata

                except Exception:
                    # Error adding experiment attributes
                    pass

                # Set traceloop.association.properties.* attributes for backend compatibility
                # BUT avoid duplicates with what's already set from association_properties
                attributes_to_set["traceloop.association.properties.session_id"] = (
                    session_id
                )
                attributes_to_set["traceloop.association.properties.project"] = project
                if source:
                    attributes_to_set["traceloop.association.properties.source"] = (
                        source
                    )
                if parent_id:
                    attributes_to_set["traceloop.association.properties.parent_id"] = (
                        parent_id
                    )

                # Set both honeyhive.* and traceloop.association.properties.* attributes for backend compatibility
            else:
                # No session_id, but we might have association_properties
                # No session_id in baggage, only processing association_properties
                pass

                # Even without session_id, we can still add experiment attributes
                try:
                    if config.experiment_id:
                        attributes_to_set["honeyhive.experiment_id"] = (
                            config.experiment_id
                        )
                        # Added experiment ID (no session)

                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = (
                            config.experiment_name
                        )
                        # Added experiment name (no session)

                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = (
                            config.experiment_variant
                        )
                        # Added experiment variant (no session)

                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = (
                            config.experiment_group
                        )
                        # Added experiment group (no session)

                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        # Added experiment metadata (no session)

                except Exception:
                    # Error adding experiment attributes (no session)
                    pass

            # Final attributes to set

            # Set all attributes at once (more efficient)
            for key, value in attributes_to_set.items():
                # Ensure value is of the expected type for OpenTelemetry
                if isinstance(value, (str, bool, int, float)):
                    span.set_attribute(key, value)
                elif isinstance(value, (list, tuple)):
                    # Convert sequences to the expected type
                    if all(isinstance(v, str) for v in value):
                        span.set_attribute(key, list(value))
                    elif all(isinstance(v, bool) for v in value):
                        span.set_attribute(key, list(value))
                    elif all(isinstance(v, int) for v in value):
                        span.set_attribute(key, list(value))
                    elif all(isinstance(v, float) for v in value):
                        span.set_attribute(key, list(value))
                    else:
                        # Convert to string if mixed types
                        span.set_attribute(key, str(value))
                else:
                    # Convert to string for any other type
                    span.set_attribute(key, str(value))

            # Span processing complete

        except Exception:
            # Silently fail to avoid breaking the application
            # Error in span processor - silently continue
            pass

    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends - send span data to HoneyHive Events API."""
        if not OTEL_AVAILABLE:
            return

        try:
            # Get span duration for performance metrics
            span_context = span.get_span_context()
            if span_context.span_id == 0:
                return  # Skip invalid spans

            # Extract span attributes
            attributes = {}
            if hasattr(span, "attributes") and span.attributes:
                attributes = dict(span.attributes)

            # Get session information from span attributes
            session_id = attributes.get("honeyhive.session_id") or attributes.get(
                "traceloop.association.properties.session_id"
            )
            # Project and source are handled by OTLP export

            if not session_id:
                # Span has no session_id, skipping HoneyHive export
                return

            # Duration calculation is handled by OTLP export

            # Log span completion (OTLP export handles actual sending)
            # Span processed

        except Exception:
            # Error processing span end
            pass

    def shutdown(self) -> None:
        """Shutdown the span processor."""
        if not OTEL_AVAILABLE:
            return

        # No cleanup needed when using baggage-only approach
        pass

    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending spans.

        This HoneyHive span processor doesn't buffer spans, so this method
        performs validation and cleanup operations to ensure consistency.

        Args:
            timeout_millis: Maximum time to wait for flush completion in milliseconds.
                          Not used by this processor since it doesn't buffer spans.

        Returns:
            bool: True if flush operations completed successfully, False otherwise.
        """
        if not OTEL_AVAILABLE:
            return True

        try:
            # Since this processor doesn't buffer spans, we perform validation
            # and ensure any ongoing operations are completed

            # Validate processor state
            processor_healthy = True

            # Check if we can access required OpenTelemetry components
            try:
                _ = context.get_current()
                _ = baggage.get_baggage("session_id", context.get_current())
            except Exception:
                processor_healthy = False

            # Simulate flush completion for compatibility with OpenTelemetry patterns
            # HoneyHive span processor flush: validated and ready
            return bool(processor_healthy)

        except Exception:
            # HoneyHive span processor flush error
            return False
