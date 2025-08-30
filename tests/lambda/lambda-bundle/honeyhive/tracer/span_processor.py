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
            # DEBUG: Display span information before processing
            span_name = getattr(span, "name", "Unknown")
            span_kind = getattr(span, "kind", "Unknown")
            span_attributes = getattr(span, "attributes", {})
            print(f"🔍 SPAN INTERCEPTED: {span_name} (kind: {span_kind})")
            print(f"   Attributes: {span_attributes}")
            print(f"   Parent context: {parent_context}")

            # Get current context (use parent_context if provided, otherwise get_current)
            ctx = (
                parent_context if parent_context is not None else context.get_current()
            )
            if not ctx:
                print("   ❌ No context available")
                return

            print(f"   Context: {ctx}")

            # Compute attributes from baggage - no caching needed
            attributes_to_set = {}

            # Try to get session_id from baggage first
            session_id = baggage.get_baggage("session_id", ctx)
            print(f"   Session ID from baggage: {session_id}")

            # If no session_id in baggage, try to get it from the span name or attributes
            # This helps catch OpenInference spans that might not have explicit baggage
            if not session_id:
                # Check if this is an OpenAI-related span (OpenInference creates these)
                if any(
                    keyword in span_name.lower()
                    for keyword in ["openai", "chat", "completion", "gpt"]
                ):
                    print(f"   🔍 This looks like an OpenInference span: {span_name}")
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

                        print(
                            "✅ OpenInference span enriched with session context from baggage: "
                            f"{span_name}"
                        )
                        print(f"✅ Added attributes: {attributes_to_set}")
                    else:
                        print("ℹ️  No session context in baggage, skipping enrichment")
                else:
                    print("ℹ️  Not an OpenInference span")

            # Always process association_properties for legacy support
            # This ensures backward compatibility regardless of session_id status
            try:
                # Check if context has association_properties (legacy support)
                if hasattr(ctx, "get") and callable(getattr(ctx, "get", None)):
                    association_properties = ctx.get("association_properties")
                    if association_properties and isinstance(
                        association_properties, dict
                    ):
                        print(
                            f"   🔍 Found association_properties: {association_properties}"
                        )
                        for key, value in association_properties.items():
                            if value is not None and not baggage.get_baggage(key, ctx):
                                # Always set traceloop.association.properties.* format for backend compatibility
                                attr_key = f"traceloop.association.properties.{key}"
                                attributes_to_set[attr_key] = str(value)
                                print(
                                    f"   ✅ Set traceloop.association.properties.{key} = {value}"
                                )
            except Exception as e:
                print(f"   ❌ Error checking association_properties: {e}")

            # If we have session_id from baggage, process normally
            if session_id:
                # Set honeyhive.* attributes (primary format)
                attributes_to_set["honeyhive.session_id"] = session_id

                # Add project from baggage - early exit if missing
                project = baggage.get_baggage("project", ctx)
                if not project:
                    # No project means no HoneyHive context, skip processing
                    print(f"   ❌ No project in baggage, skipping processing")
                    return

                attributes_to_set["honeyhive.project"] = project

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
                        print(f"   ✅ Added experiment ID: {config.experiment_id}")

                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = (
                            config.experiment_name
                        )
                        print(f"   ✅ Added experiment name: {config.experiment_name}")

                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = (
                            config.experiment_variant
                        )
                        print(
                            "   ✅ Added experiment variant: "
                            f"{config.experiment_variant}"
                        )

                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = (
                            config.experiment_group
                        )
                        print(
                            "   ✅ Added experiment group: "
                            f"{config.experiment_group}"
                        )

                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        print(
                            "   ✅ Added experiment metadata: "
                            f"{len(config.experiment_metadata)} items"
                        )

                except Exception as e:
                    print(f"   ⚠️  Error adding experiment attributes: {e}")

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

                print(
                    "   ✅ Set both honeyhive.* and traceloop.association.properties.* "
                    "attributes for backend compatibility"
                )
            else:
                # No session_id, but we might have association_properties
                print(
                    "   ℹ️  No session_id in baggage, only processing "
                    "association_properties"
                )

                # Even without session_id, we can still add experiment attributes
                try:
                    if config.experiment_id:
                        attributes_to_set["honeyhive.experiment_id"] = (
                            config.experiment_id
                        )
                        print(
                            f"   ✅ Added experiment ID (no session): {config.experiment_id}"
                        )

                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = (
                            config.experiment_name
                        )
                        print(
                            f"   ✅ Added experiment name (no session): {config.experiment_name}"
                        )

                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = (
                            config.experiment_variant
                        )
                        print(
                            "   ✅ Added experiment variant (no session): "
                            f"{config.experiment_variant}"
                        )

                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = (
                            config.experiment_group
                        )
                        print(
                            "   ✅ Added experiment group (no session): "
                            f"{config.experiment_group}"
                        )

                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        print(
                            "   ✅ Added experiment metadata (no session): "
                            f"{len(config.experiment_metadata)} items"
                        )

                except Exception as e:
                    print(f"   ⚠️  Error adding experiment attributes (no session): {e}")

            print(f"   📝 Final attributes to set: {attributes_to_set}")

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

            print(f"   ✅ Span processing complete")

        except Exception as e:
            # Silently fail to avoid breaking the application
            print(f"   ❌ Error in span processor: {e}")

    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends."""
        if not OTEL_AVAILABLE:
            return

        try:
            # Get span duration for performance metrics
            span_context = span.get_span_context()
            if span_context.span_id == 0:
                return  # Skip invalid spans

            # Calculate duration if available
            if hasattr(span, "start_time") and hasattr(span, "end_time"):
                start_time = span.start_time
                end_time = span.end_time
                if start_time and end_time:
                    duration = end_time - start_time
                    # Set duration as attribute for monitoring
                    if hasattr(span, "set_attribute"):
                        span.set_attribute("honeyhive.span.duration", duration)

            # Log span completion
            span_name = getattr(span, "name", "Unknown")
            print(f"✅ Span completed: {span_name}")

        except Exception as e:
            print(f"❌ Error in span processor: {e}")

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
            if processor_healthy:
                print("✓ HoneyHive span processor flush: validated and ready")
                return True
            else:
                print("⚠️  HoneyHive span processor flush: validation issues detected")
                return False

        except Exception as e:
            print(f"❌ HoneyHive span processor flush error: {e}")
            return False
