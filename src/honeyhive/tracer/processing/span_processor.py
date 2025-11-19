"""HoneyHive span processor for OpenTelemetry integration."""

# pylint: disable=duplicate-code,protected-access,too-many-lines,line-too-long,invalid-name,no-else-return
# Justification: Legitimate shared patterns with utils and decorators.
# Duplicate code represents common LLM attribute lists and model patterns
# shared across processing and utility modules for consistent event detection.
# protected-access: Accessing _config is the established pattern for tracer config
# too-many-lines: Comprehensive span processor with debugging requires additional code
# line-too-long: Complex OpenTelemetry attribute mappings exceed 88 char limit
# invalid-name: OPENINFERENCE_TO_HONEYHIVE is a constant mapping dict (acceptable)
# no-else-return: Early return pattern improves readability in complex conditionals

import json
from typing import Any, Optional

from opentelemetry import baggage, context
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

# Removed get_config import - using per-instance configuration instead
from ..utils import convert_enum_to_string
from ..utils.event_type import detect_event_type_from_patterns, extract_raw_attributes

# No module-level logger - use tracer instance logger


# Removed _get_config_value_dynamically_from_tracer - replaced by unified config
# Use tracer.config.get(key) instead


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
        :param tracer_instance: HoneyHive tracer instance for session isolation
        :type tracer_instance: Optional[Any]
        """
        self.client = client
        self.disable_batch = disable_batch
        self.otlp_exporter = otlp_exporter
        self.tracer_instance = tracer_instance

        # Multi-instance logging architecture uses safe_log utility
        # No need to store logger reference directly

        # Determine processing mode
        if client is not None:
            self.mode = "client"
            self._safe_log(
                "debug",
                "🚀 HoneyHiveSpanProcessor initialized in CLIENT mode (direct API)",
            )
        else:
            # Both disable_batch=True and False use OTLP exporter
            self.mode = "otlp"
            batch_mode = "immediate" if disable_batch else "batched"
            self._safe_log(
                "debug",
                "🚀 HoneyHiveSpanProcessor initialized in OTLP mode (%s)",
                batch_mode,
            )

        self._safe_log(
            "debug",
            "🔧 Span processor mode: %s, client: %s, disable_batch: %s",
            self.mode,
            client is not None,
            disable_batch,
        )

    def _safe_log(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        """Safely log using the centralized safe_log utility."""
        # pylint: disable=import-outside-toplevel  # Avoids circular
        # import: processor -> logger
        from ...utils.logger import safe_log

        # Format message with args if provided (maintain backward compatibility)
        if args:
            formatted_message = message % args
        else:
            formatted_message = message
        safe_log(self.tracer_instance, level, formatted_message, **kwargs)

    def _dump_raw_span_data(self, span: ReadableSpan) -> str:
        """Dump all raw span data for debugging.

        :param span: The span to dump
        :type span: ReadableSpan
        :return: Formatted string with all span properties
        :rtype: str
        """
        try:
            # Get span context
            span_context = span.context if hasattr(span, "context") else None

            # Build comprehensive span data dictionary
            span_data = {
                "name": span.name if hasattr(span, "name") else None,
                "context": (
                    {
                        "trace_id": (
                            f"{span_context.trace_id:032x}" if span_context else None
                        ),
                        "span_id": (
                            f"{span_context.span_id:016x}" if span_context else None
                        ),
                        "trace_flags": (
                            str(span_context.trace_flags) if span_context else None
                        ),
                        "trace_state": (
                            str(span_context.trace_state) if span_context else None
                        ),
                        "is_remote": span_context.is_remote if span_context else None,
                    }
                    if span_context
                    else None
                ),
                "parent": (
                    {
                        "trace_id": (
                            f"{span.parent.trace_id:032x}" if span.parent else None
                        ),
                        "span_id": (
                            f"{span.parent.span_id:016x}" if span.parent else None
                        ),
                    }
                    if hasattr(span, "parent") and span.parent
                    else None
                ),
                "kind": str(span.kind) if hasattr(span, "kind") else None,
                "start_time": span.start_time if hasattr(span, "start_time") else None,
                "end_time": span.end_time if hasattr(span, "end_time") else None,
                "status": (
                    {
                        "status_code": (
                            str(span.status.status_code)
                            if hasattr(span, "status") and span.status
                            else None
                        ),
                        "description": (
                            span.status.description
                            if hasattr(span, "status") and span.status
                            else None
                        ),
                    }
                    if hasattr(span, "status")
                    else None
                ),
                "attributes": (
                    dict(span.attributes)
                    if hasattr(span, "attributes") and span.attributes
                    else {}
                ),
                "events": [
                    {
                        "name": event.name if hasattr(event, "name") else None,
                        "timestamp": (
                            event.timestamp if hasattr(event, "timestamp") else None
                        ),
                        "attributes": (
                            dict(event.attributes)
                            if hasattr(event, "attributes") and event.attributes
                            else {}
                        ),
                    }
                    for event in (
                        span.events if hasattr(span, "events") and span.events else []
                    )
                ],
                "links": [
                    {
                        "context": {
                            "trace_id": (
                                f"{link.context.trace_id:032x}"
                                if hasattr(link, "context") and link.context
                                else None
                            ),
                            "span_id": (
                                f"{link.context.span_id:016x}"
                                if hasattr(link, "context") and link.context
                                else None
                            ),
                        },
                        "attributes": (
                            dict(link.attributes)
                            if hasattr(link, "attributes") and link.attributes
                            else {}
                        ),
                    }
                    for link in (
                        span.links if hasattr(span, "links") and span.links else []
                    )
                ],
                "resource": (
                    {
                        "attributes": (
                            dict(span.resource.attributes)
                            if hasattr(span, "resource")
                            and hasattr(span.resource, "attributes")
                            and span.resource.attributes
                            else {}
                        ),
                        "schema_url": (
                            span.resource.schema_url
                            if hasattr(span, "resource")
                            and hasattr(span.resource, "schema_url")
                            else None
                        ),
                    }
                    if hasattr(span, "resource") and span.resource
                    else None
                ),
                "instrumentation_info": (
                    {
                        "name": (
                            span.instrumentation_info.name
                            if hasattr(span, "instrumentation_info")
                            and hasattr(span.instrumentation_info, "name")
                            else None
                        ),
                        "version": (
                            span.instrumentation_info.version
                            if hasattr(span, "instrumentation_info")
                            and hasattr(span.instrumentation_info, "version")
                            else None
                        ),
                        "schema_url": (
                            span.instrumentation_info.schema_url
                            if hasattr(span, "instrumentation_info")
                            and hasattr(span.instrumentation_info, "schema_url")
                            else None
                        ),
                    }
                    if hasattr(span, "instrumentation_info")
                    and span.instrumentation_info
                    else None
                ),
            }

            # Return formatted JSON with proper indentation
            return json.dumps(span_data, indent=2, default=str)

        except Exception as e:
            return f"Error dumping span data: {e}"

    def _get_context(self, parent_context: Optional[Context]) -> Optional[Context]:
        """Get the appropriate context for baggage operations.

        :param parent_context: Parent context to use, or None to use current context
        :type parent_context: Optional[Context]
        :return: Context to use for baggage operations
        :rtype: Optional[Context]
        """
        return parent_context if parent_context is not None else context.get_current()

    def _get_basic_baggage_attributes(self, ctx: Context) -> dict:
        """Get basic baggage attributes (session_id, project, source, parent_id).

        :param ctx: OpenTelemetry context to extract baggage from
        :type ctx: Context
        :return: Dictionary of baggage attributes
        :rtype: dict
        """
        attributes = {}

        # Priority: baggage session_id (for distributed tracing),
        # then tracer instance
        # This ensures distributed traces use the propagated session_id from the client
        session_id = baggage.get_baggage("session_id", ctx)

        # Fallback to tracer instance session_id if baggage doesn't have it
        # (for local tracing scenarios)
        if not session_id:
            if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
                session_id = self.tracer_instance.session_id

        if session_id:
            attributes["honeyhive.session_id"] = session_id
            # Backend compatibility: also set Traceloop-style attribute
            attributes["traceloop.association.properties.session_id"] = session_id

        # Priority: baggage project (for distributed tracing), then tracer instance
        project = baggage.get_baggage("project", ctx)

        # Fallback to tracer instance project if baggage doesn't have it
        if not project:
            if self.tracer_instance and hasattr(self.tracer_instance, "project_name"):
                project = self.tracer_instance.project_name

        if project:
            attributes["honeyhive.project"] = project
            # Backend compatibility: also set Traceloop-style attribute
            attributes["traceloop.association.properties.project"] = project

        # Priority: baggage source (for distributed tracing), then tracer instance
        source = baggage.get_baggage("source", ctx)

        # Fallback to tracer instance source if baggage doesn't have it
        if not source:
            if self.tracer_instance and hasattr(
                self.tracer_instance, "source_environment"
            ):
                source = self.tracer_instance.source_environment

        if source:
            attributes["honeyhive.source"] = source
            # Backend compatibility: also set Traceloop-style attribute
            attributes["traceloop.association.properties.source"] = source

        parent_id = baggage.get_baggage("parent_id", ctx)
        if parent_id:
            attributes["honeyhive.parent_id"] = parent_id

        return attributes

    def _get_experiment_attributes(self) -> dict:
        """Get experiment configuration attributes.

        :return: Dictionary of experiment attributes
        :rtype: dict
        """
        attributes = {}

        try:
            # Use dynamic configuration extraction (config object and legacy attributes)
            experiment_attrs = [
                "experiment_id",
                "experiment_name",
                "experiment_variant",
                "experiment_group",
            ]

            for attr_name in experiment_attrs:
                if self.tracer_instance is not None:
                    value = self.tracer_instance.config.get(attr_name)
                    if value:
                        attributes[f"honeyhive.{attr_name}"] = value

            # Handle experiment metadata using nested config access
            experiment_metadata = None
            if self.tracer_instance is not None:
                experiment_metadata = getattr(
                    self.tracer_instance.config.experiment, "experiment_metadata", None
                )
            if experiment_metadata and isinstance(experiment_metadata, dict):
                # Add experiment metadata as individual attributes
                # for better observability
                for key, value in experiment_metadata.items():
                    attr_key = f"honeyhive.experiment_metadata.{key}"
                    attributes[attr_key] = str(value)

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            self._safe_log(
                "debug",
                "Error adding experiment attributes",
                honeyhive_data={"error_type": type(e).__name__},
            )

        return attributes

    def _process_association_properties(self, ctx: Context) -> dict:
        """Process legacy association_properties from context.

        :param ctx: OpenTelemetry context to extract association properties from
        :type ctx: Context
        :return: Dictionary of association properties attributes
        :rtype: dict
        """
        attributes = {}

        try:
            # Check if context has association_properties (legacy support)
            if hasattr(ctx, "get") and callable(getattr(ctx, "get", None)):
                association_properties = ctx.get("association_properties")
                if association_properties and isinstance(association_properties, dict):
                    # Found association_properties
                    for key, value in association_properties.items():
                        if value is not None and not baggage.get_baggage(key, ctx):
                            # Set traceloop.association.properties.* format
                            # for backend compatibility
                            attr_key = f"traceloop.association.properties.{key}"
                            attributes[attr_key] = str(value)
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            self._safe_log(
                "debug",
                "Error checking association_properties",
                honeyhive_data={"error_type": type(e).__name__},
            )

        return attributes

    def _get_traceloop_compatibility_attributes(self, ctx: Context) -> dict:
        """Get traceloop.association.properties.* attributes for backend compatibility.

        :param ctx: OpenTelemetry context to extract baggage from
        :type ctx: Context
        :return: Dictionary of traceloop compatibility attributes
        :rtype: dict
        """
        attributes = {}

        session_id = baggage.get_baggage("session_id", ctx)
        if session_id:
            attributes["traceloop.association.properties.session_id"] = session_id

        project = baggage.get_baggage("project", ctx)
        if project:
            attributes["traceloop.association.properties.project"] = project

        source = baggage.get_baggage("source", ctx)
        if source:
            attributes["traceloop.association.properties.source"] = source

        parent_id = baggage.get_baggage("parent_id", ctx)
        if parent_id:
            attributes["traceloop.association.properties.parent_id"] = parent_id

        return attributes

    def _get_evaluation_attributes_from_baggage(self, ctx: Context) -> dict:
        """Get evaluation metadata from baggage (run_id, dataset_id, datapoint_id).

        This method reads evaluation context that was set during evaluate() execution
        and ensures it propagates to all child spans created during
        # datapoint processing.

        :param ctx: OpenTelemetry context to extract baggage from
        :type ctx: Context
        :return: Dictionary of evaluation attributes
        :rtype: dict
        """
        attributes = {}

        # Read evaluation metadata from baggage
        run_id = baggage.get_baggage("run_id", ctx)
        if run_id:
            attributes["honeyhive_metadata.run_id"] = run_id

        dataset_id = baggage.get_baggage("dataset_id", ctx)
        if dataset_id:
            attributes["honeyhive_metadata.dataset_id"] = dataset_id

        datapoint_id = baggage.get_baggage("datapoint_id", ctx)
        if datapoint_id:
            attributes["honeyhive_metadata.datapoint_id"] = datapoint_id

        # Log if evaluation attributes were found
        if attributes:
            self._safe_log(
                "debug",
                "📊 Evaluation metadata from baggage",
                honeyhive_data={
                    "attributes": attributes,
                    "span_name": "will_be_set_on_span",
                },
            )

        return attributes

    def _get_all_baggage_attributes(self, ctx: Context) -> dict:
        """Get all baggage attributes from context, excluding already-processed keys.

        This method extracts ALL baggage items from the OpenTelemetry context and
        adds them as span attributes with a "baggage." prefix. This ensures that
        custom baggage items set by users are automatically propagated to spans.

        Excludes keys that are already handled by:
        - _get_basic_baggage_attributes (session_id, project, source, parent_id)
        - _get_evaluation_attributes_from_baggage (run_id, dataset_id, datapoint_id)

        :param ctx: OpenTelemetry context to extract baggage from
        :type ctx: Context
        :return: Dictionary of baggage attributes with "baggage." prefix
        :rtype: dict
        """
        attributes: dict[str, Any] = {}

        try:
            # Get all baggage items from context
            all_baggage = baggage.get_all(ctx)
            if not all_baggage:
                return attributes

            # Keys that are already processed by other methods
            excluded_keys = {
                "session_id",
                "project",
                "source",
                "parent_id",
                "run_id",
                "dataset_id",
                "datapoint_id",
                "honeyhive_tracer_id",  # Internal tracer discovery key
            }

            # Extract all other baggage items
            for key, value in all_baggage.items():
                if key not in excluded_keys and value is not None:
                    # Add baggage items with "baggage." prefix for clarity
                    attributes[f"baggage.{key}"] = str(value)

            if attributes:
                self._safe_log(
                    "debug",
                    "📦 Extracted custom baggage attributes",
                    honeyhive_data={
                        "baggage_keys": list(attributes.keys()),
                        "count": len(attributes),
                    },
                )

        except Exception as e:
            self._safe_log(
                "warning",
                "Failed to extract all baggage attributes: %s",
                e,
                honeyhive_data={"error_type": type(e).__name__},
            )

        return attributes

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span starts - enriches spans with HoneyHive attributes.

        :param span: The span that is starting
        :type span: Span
        :param parent_context: Parent context for baggage operations
        :type parent_context: Optional[Context]
        """
        self._safe_log(
            "debug",
            "🚀 SPAN PROCESSOR on_start called",
            honeyhive_data={
                "span_name": span.name,
                "span_id": span.get_span_context().span_id,
                "trace_id": span.get_span_context().trace_id,
                "tracer_instance_id": (
                    id(self.tracer_instance) if self.tracer_instance else None
                ),
                "tracer_instance_type": (
                    type(self.tracer_instance).__name__
                    if self.tracer_instance
                    else None
                ),
                "has_parent_context": parent_context is not None,
            },
        )

        try:
            ctx = self._get_context(parent_context)
            if ctx is None:
                self._safe_log(
                    "debug",
                    "⚠️ DEBUG: Context is None, exiting on_start early",
                    honeyhive_data={
                        "span_name": span.name,
                        "parent_context": parent_context,
                    },
                )
                return

            # Get session_id to determine if this span should be enriched
            # Priority: baggage session_id (distributed tracing), then
            # tracer instance. This ensures distributed traces use the
            # propagated session_id from the client
            session_id = baggage.get_baggage("session_id", ctx)

            if session_id:
                self._safe_log(
                    "debug",
                    "🔍 DEBUG: Using baggage session_id (distributed tracing)",
                    honeyhive_data={
                        "span_name": span.name,
                        "session_id": session_id,
                        "source": "baggage",
                    },
                )

            # Fallback to tracer instance session_id if baggage doesn't have it
            # (for local tracing scenarios)
            if not session_id:
                if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
                    session_id = self.tracer_instance.session_id
                    self._safe_log(
                        "debug",
                        "🔍 DEBUG: Using tracer instance session_id (local tracing)",
                        honeyhive_data={
                            "span_name": span.name,
                            "session_id": session_id,
                            "tracer_instance_id": id(self.tracer_instance),
                            "source": "tracer_instance",
                        },
                    )
                else:
                    self._safe_log(
                        "debug",
                        (
                            "⚠️ DEBUG: No session_id found in tracer "
                            "instance or baggage"
                        ),
                        honeyhive_data={
                            "span_name": span.name,
                            "tracer_instance_id": (
                                id(self.tracer_instance)
                                if self.tracer_instance
                                else None
                            ),
                            "has_tracer_instance": self.tracer_instance is not None,
                            "baggage_keys": (
                                list(baggage.get_all(ctx).keys()) if ctx else []
                            ),
                        },
                    )

            # Collect all attributes to set
            attributes_to_set = {}

            # Always process association_properties for legacy support
            attributes_to_set.update(self._process_association_properties(ctx))

            # Always add experiment attributes (they don't require session_id)
            attributes_to_set.update(self._get_experiment_attributes())

            if session_id:
                # Set session_id attributes directly (multi-instance isolation)
                attributes_to_set["honeyhive.session_id"] = session_id
                attributes_to_set["traceloop.association.properties.session_id"] = (
                    session_id
                )

                # Get other baggage attributes (project, source, etc.)
                other_baggage_attrs = self._get_basic_baggage_attributes(ctx)
                # Remove session_id from baggage attrs since we're setting it directly
                other_baggage_attrs.pop("honeyhive.session_id", None)
                other_baggage_attrs.pop(
                    "traceloop.association.properties.session_id", None
                )
                attributes_to_set.update(other_baggage_attrs)

                # Add traceloop compatibility attributes for backend
                attributes_to_set.update(
                    self._get_traceloop_compatibility_attributes(ctx)
                )

                # Add evaluation metadata from baggage (run_id, dataset_id,
                # datapoint_id)
                attributes_to_set.update(
                    self._get_evaluation_attributes_from_baggage(ctx)
                )

            # Add all custom baggage attributes (generalized baggage extraction)
            # This extracts ALL baggage items not already processed above
            attributes_to_set.update(self._get_all_baggage_attributes(ctx))

            # Apply all attributes to the span
            for key, value in attributes_to_set.items():
                if value is not None:
                    span.set_attribute(key, value)

            # Process all honeyhive attributes and map them to backend format
            self._process_honeyhive_attributes(span)

            # Detect and set event type using priority-based logic
            detected_event_type = self._detect_event_type(span)
            if detected_event_type:
                span.set_attribute("honeyhive_event_type", detected_event_type)
                span_context = span.get_span_context()
                self._safe_log(
                    "debug",
                    "🎯 Event type set on span: %s",
                    detected_event_type,
                    honeyhive_data={
                        "span_name": span.name,
                        "detected_event_type": detected_event_type,
                        "span_id": (
                            span_context.span_id
                            if span_context is not None
                            else "unknown"
                        ),
                    },
                )

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            self._safe_log(
                "debug",
                "Error in span enrichment",
                honeyhive_data={"error_type": type(e).__name__},
            )

    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends - send span data based on processor mode.

        :param span: The span that is ending
        :type span: ReadableSpan
        """
        try:
            self._safe_log("debug", f"🟦 ON_END CALLED for span: {span.name}")

            # Get span duration for performance metrics
            span_context = span.get_span_context()
            if span_context is None or span_context.span_id == 0:
                self._safe_log(
                    "warning",
                    f"❌ ON_END: Invalid span context for {span.name}, skipping",
                )
                return  # Skip invalid spans

            # Extract span attributes
            attributes = {}
            if hasattr(span, "attributes") and span.attributes:
                attributes = dict(span.attributes)

            # Get session information from span attributes (set in on_start)
            session_id_raw = attributes.get("honeyhive.session_id") or attributes.get(
                "traceloop.association.properties.session_id"
            )

            if not session_id_raw:
                # Span has no session_id, skipping HoneyHive export
                self._safe_log(
                    "warning",
                    (
                        f"⚠️ ON_END: Span {span.name} has no session_id, "
                        f"skipping HoneyHive export. Attributes: "
                        f"{list(attributes.keys())}"
                    ),
                )
                return

            # Convert session_id to string
            session_id = str(session_id_raw)

            # Dump raw span data for debugging
            raw_span_data = self._dump_raw_span_data(span)
            self._safe_log(
                "debug",
                "🚀 SPAN PROCESSOR on_end - mode: %s, span: %s\n📊 RAW DATA:\n%s",
                self.mode,
                span.name,
                raw_span_data,
            )

            # Process span based on mode
            if self.mode == "client" and self.client:
                self._send_via_client(span, attributes, session_id)
            elif self.mode == "otlp" and self.otlp_exporter:
                self._send_via_otlp(span, attributes, session_id)
            else:
                self._safe_log(
                    "warning",
                    (
                        "⚠️ No valid export method for mode: %s, "
                        "client: %s, exporter: %s"
                    ),
                    self.mode,
                    self.client is not None,
                    self.otlp_exporter is not None,
                )

        except Exception as e:
            # Error processing span end - continue without disrupting application
            self._safe_log("debug", "❌ Error in span processor on_end: %s", e)

    def _send_via_client(
        self, span: ReadableSpan, attributes: dict, session_id: str
    ) -> None:
        """Send span via HoneyHive SDK client (Events API).

        :param span: The span to send
        :type span: ReadableSpan
        :param attributes: Span attributes dictionary
        :type attributes: dict
        :param session_id: HoneyHive session ID
        :type session_id: str
        """
        try:
            self._safe_log("debug", "🚀 OTLP EXPORT CALLED - CLIENT MODE")

            # Convert span to HoneyHive event format
            event_data = self._convert_span_to_event(span, attributes, session_id)

            # Send via client Events API
            if (
                self.client is not None
                and hasattr(self.client, "events")
                and hasattr(self.client.events, "create")
            ):
                response = self.client.events.create(**event_data)
                self._safe_log("debug", "✅ Event sent via client: %s", response)
            else:
                self._safe_log("warning", "⚠️ Client missing events.create method")

        except Exception as e:
            self._safe_log("debug", "❌ Error sending via client: %s", e)

    def _send_via_otlp(
        self, span: ReadableSpan, _attributes: dict, _session_id: str
    ) -> None:
        """Send span via OTLP exporter - ALWAYS exports spans to ensure delivery.

        :param span: The span to send
        :type span: ReadableSpan
        :param attributes: Span attributes dictionary
        :type attributes: dict
        :param session_id: HoneyHive session ID
        :type session_id: str
        """
        try:
            batch_mode = "immediate" if self.disable_batch else "batched"
            self._safe_log(
                "debug", "🚀 OTLP EXPORT CALLED - %s MODE", batch_mode.upper()
            )

            if self.otlp_exporter:
                # ALWAYS export spans to ensure delivery to backend
                # The HoneyHiveOTLPExporter handles the actual OTLP protocol
                result = self.otlp_exporter.export([span])
                self._safe_log(
                    "debug", "✅ Span exported via OTLP exporter (%s mode)", batch_mode
                )

                # Log export result for debugging
                if hasattr(result, "name"):
                    self._safe_log("debug", "📊 OTLP export result: %s", result.name)
            else:
                self._safe_log("warning", "⚠️ No OTLP exporter available")

        except Exception as e:
            self._safe_log("error", "❌ Error sending via OTLP: %s", e)

    def _process_honeyhive_attributes(self, span: Span) -> None:
        """Process all honeyhive_* attributes and map them to backend-expected format.

        This method handles:
        1. Converting honeyhive_* attributes to backend format
        2. Processing _raw attributes if they exist
        3. Converting enums to strings
        4. Ensuring proper attribute naming for backend compatibility

        :param span: The span to process attributes for
        :type span: Span
        """
        try:
            # Get current span attributes
            attributes = (
                dict(span.attributes)
                if hasattr(span, "attributes") and span.attributes
                else {}
            )

            self._safe_log(
                "debug",
                "🔧 Processing honeyhive attributes for span: %s",
                span.name,
                honeyhive_data={
                    "span_name": span.name,
                    "total_attributes": len(attributes),
                    "honeyhive_attributes": [
                        k for k in attributes.keys() if k.startswith("honeyhive")
                    ],
                    "attribute_types": {
                        k: type(v).__name__
                        for k, v in attributes.items()
                        if k.startswith("honeyhive")
                    },
                },
            )

            # Define all honeyhive attributes that need processing
            honeyhive_basic_attrs = [
                "honeyhive_event_type",
                "honeyhive_event_name",
                "honeyhive_event_id",
                "honeyhive_source",
                "honeyhive_project",
                "honeyhive_session_id",
                "honeyhive_user_id",
                "honeyhive_session_name",
            ]

            honeyhive_complex_attrs = [
                "honeyhive_inputs",
                "honeyhive_config",
                "honeyhive_metadata",
                "honeyhive_metrics",
                "honeyhive_feedback",
                "honeyhive_outputs",
            ]

            # Process basic attributes
            for attr_name in honeyhive_basic_attrs:
                if attr_name in attributes:
                    value = attributes[attr_name]
                    # Convert enum to string if needed
                    processed_value = convert_enum_to_string(value)
                    if processed_value is not None:
                        # Set the processed value back to the span
                        span.set_attribute(attr_name, processed_value)
                        self._safe_log(
                            "debug",
                            "Processed basic attribute: %s = %s",
                            attr_name,
                            processed_value,
                        )

            # Process complex attributes (these might have nested structures)
            for attr_name in honeyhive_complex_attrs:
                if attr_name in attributes:
                    value = attributes[attr_name]
                    # Complex attributes processed by _set_span_attributes
                    # Just ensure they're properly formatted
                    self._safe_log("debug", "Found complex attribute: %s", attr_name)

            # Process attributes using centralized dynamic logic
            self._safe_log(
                "debug", "🔍 Processing attributes using dynamic extraction logic"
            )

            # Use the centralized dynamic logic from event_type utility
            processed_attributes = extract_raw_attributes(
                attributes, self.tracer_instance
            )

            # Set processed attributes on the span
            for attr_name, attr_value in processed_attributes.items():
                if attr_name not in attributes:  # Don't override existing attributes
                    span.set_attribute(attr_name, attr_value)
                    self._safe_log(
                        "debug",
                        "Set processed attribute: %s = %s",
                        attr_name,
                        attr_value,
                    )

        except Exception as e:
            self._safe_log("debug", "Error processing honeyhive attributes: %s", e)

    def _detect_event_type(self, span: Span) -> Optional[str]:
        """Dynamically detect event type using priority-based patterns.

        Priority Order:
        1. honeyhive_event_type_raw - Set by @trace decorator (highest priority)
        2. honeyhive_event_type - Alternative explicit format
        3. openinference.span.kind - Standard instrumentor convention
           (LLM/CHAIN/TOOL/AGENT)
        4. Span name inference - Pattern matching fallback
        5. Default to "tool" - Final fallback

        OpenInference span.kind mappings:
        - LLM → model (actual LLM invocations)
        - CHAIN → chain (multi-step workflows)
        - TOOL → tool (function/tool calls)
        - AGENT → chain (agent operations)
        - RETRIEVER → tool (retrieval operations)
        - EMBEDDING → tool (embedding generation)
        - RERANKER → tool (reranking operations)
        - GUARDRAIL → tool (guardrail checks)

        :param span: The span to analyze for event type
        :type span: Span
        :return: Detected event type or None if no detection possible
        :rtype: Optional[str]
        """
        try:
            attributes = (
                dict(span.attributes)
                if hasattr(span, "attributes") and span.attributes
                else {}
            )

            span_context = span.get_span_context()
            self._safe_log(
                "debug",
                "🔍 Starting event type detection for span: %s",
                span.name,
                honeyhive_data={
                    "span_name": span.name,
                    "available_attributes": list(attributes.keys()),
                    "span_id": (
                        span_context.span_id if span_context is not None else "unknown"
                    ),
                },
            )

            # Priority 1: Check if event type is already set
            existing_type = attributes.get("honeyhive_event_type")
            if (
                existing_type and existing_type != "tool"
            ):  # Don't return if it's just the default
                self._safe_log(
                    "debug", "✅ Event type already processed: %s", existing_type
                )
                return None  # Don't override existing processed value

            # Priority 2: Explicit _raw decorator attributes
            raw_type = attributes.get("honeyhive_event_type_raw")
            if raw_type:
                self._safe_log(
                    "debug", "✅ Event type from _raw decorator: %s", raw_type
                )
                return str(raw_type)

            # Priority 3: Direct decorator attributes
            direct_type = attributes.get("honeyhive_event_type")
            if direct_type and direct_type != "tool":
                (
                    self._safe_log(
                        "debug", "✅ Event type from decorator: %s", direct_type
                    )
                )
                return str(direct_type)

            # Priority 4: OpenInference span.kind attribute (standard
            # instrumentor convention)
            span_kind = attributes.get("openinference.span.kind")
            if span_kind:
                # Map OpenInference span kinds to HoneyHive event types
                # Complete OpenInference span.kind mapping
                span_kind_upper = str(span_kind).upper()

                # Deterministic mapping table
                OPENINFERENCE_TO_HONEYHIVE = {
                    "LLM": "model",  # LLM invocations
                    "CHAIN": "chain",  # Multi-step workflows
                    "TOOL": "tool",  # Tool/function calls
                    "AGENT": "chain",  # Agent operations (map to chain)
                    "RETRIEVER": "tool",  # Retrieval operations
                    "EMBEDDING": "tool",  # Embedding generation (map to tool)
                    "RERANKER": "tool",  # Reranking operations
                    "GUARDRAIL": "tool",  # Guardrail checks
                }

                event_type = OPENINFERENCE_TO_HONEYHIVE.get(span_kind_upper)
                if event_type:
                    self._safe_log(
                        "debug",
                        (
                            f"✅ Event type from openinference.span.kind: "
                            f"{event_type} ({span_kind_upper})"
                        ),
                    )
                    return event_type
                else:
                    # Unknown span.kind - log warning and default to tool
                    self._safe_log(
                        "warning",
                        (
                            f"⚠️ Unknown openinference.span.kind: "
                            f"{span_kind_upper}, defaulting to tool"
                        ),
                    )
                    return "tool"

            # Priority 5: Dynamic pattern matching using utility function
            self._safe_log(
                "debug", "🔍 Using dynamic pattern matching for span: '%s'", span.name
            )

            # Use the centralized dynamic logic from event_type utility
            detected_type = detect_event_type_from_patterns(
                span.name, attributes, self.tracer_instance
            )

            if detected_type:
                self._safe_log(
                    "debug",
                    "✅ Event type detected via dynamic patterns: '%s' for span '%s'",
                    detected_type,
                    span.name,
                )
                return detected_type

            # Priority 6: Default fallback
            self._safe_log(
                "debug",
                "⚠️ No event type pattern matched for '%s', defaulting to 'tool'",
                span.name,
            )
            return "tool"

        except Exception as e:
            self._safe_log("debug", "Error in event type detection: %s", e)
            return "tool"  # Safe fallback

    def _convert_span_to_event(
        self, span: ReadableSpan, attributes: dict, session_id: str
    ) -> dict:
        """Convert OpenTelemetry span to HoneyHive event format.

        :param span: The span to convert
        :type span: ReadableSpan
        :param attributes: Span attributes dictionary
        :type attributes: dict
        :param session_id: HoneyHive session ID
        :type session_id: str
        :return: Event data dictionary for HoneyHive Events API
        :rtype: dict
        """
        try:
            # Extract raw attributes from span for event type detection
            span_attributes = {}
            if hasattr(span, "attributes") and span.attributes:
                span_attributes = dict(span.attributes)

            raw_attributes = extract_raw_attributes(span_attributes)

            # Detect event type dynamically using patterns
            detected_event_type = detect_event_type_from_patterns(
                span.name, raw_attributes
            )

            # Basic event structure
            event_data = {
                "project": attributes.get("honeyhive.project", "Unknown"),
                "source": attributes.get("honeyhive.source", "python-sdk"),
                "session_id": session_id,
                "event_name": span.name,
                "event_type": attributes.get(
                    "honeyhive_event_type", detected_event_type
                ),
                "start_time": span.start_time,
                "end_time": span.end_time,
                "metadata": {},
                "inputs": {},
                "outputs": {},
            }

            # Add all attributes as inputs (for test compatibility)
            for key, value in attributes.items():
                if not key.startswith("honeyhive.") and not key.startswith(
                    "traceloop."
                ):
                    event_data["inputs"][key] = value

            # Add span attributes as inputs too
            for key, value in raw_attributes.items():
                if not key.startswith("honeyhive.") and not key.startswith(
                    "traceloop."
                ):
                    event_data["inputs"][key] = value

            # Add HoneyHive-specific attributes as metadata
            for key, value in attributes.items():
                if key.startswith("honeyhive.") and key not in [
                    "honeyhive.project",
                    "honeyhive.source",
                    "honeyhive.session_id",
                ]:
                    clean_key = key.replace("honeyhive.", "")
                    event_data["metadata"][clean_key] = value

            # Handle error status
            if span.status and hasattr(span.status, "status_code"):
                # pylint: disable=import-outside-toplevel  # Only needed when
                # span has error status
                from opentelemetry.trace import StatusCode

                if span.status.status_code == StatusCode.ERROR:
                    event_data["error"] = {
                        "message": getattr(span.status, "description", "Unknown error"),
                        "type": "span_error",
                    }

            return event_data

        except Exception as e:
            self._safe_log("debug", "❌ Error converting span to event: %s", e)
            return {}

    def shutdown(self) -> None:
        """Shutdown the span processor.

        Performs graceful shutdown of the OTLP exporter if available.
        """
        try:
            # Check if we have an OTLP exporter to shutdown
            if hasattr(self, "otlp_exporter") and self.otlp_exporter:
                if hasattr(self.otlp_exporter, "shutdown"):
                    self.otlp_exporter.shutdown()
        except Exception as e:
            self._safe_log("debug", "Error during shutdown: %s", e)
            # Graceful degradation - continue shutdown process

    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending spans.

        This HoneyHive span processor doesn't buffer spans, so this method
        performs validation and cleanup operations to ensure consistency.

        :param timeout_millis: Maximum time to wait for flush completion (ms).
                              Not used by this processor since it doesn't buffer spans.
        :type timeout_millis: float
        :return: True if flush operations completed successfully, False otherwise.
        :rtype: bool
        """
        try:
            # Check if we have an OTLP exporter to flush
            if hasattr(self, "otlp_exporter") and self.otlp_exporter:
                if hasattr(self.otlp_exporter, "force_flush"):
                    result = self.otlp_exporter.force_flush(timeout_millis)
                    return bool(result)

            # Since this processor doesn't buffer spans, we perform validation
            # and ensure any ongoing operations are completed

            # Validate processor state
            processor_healthy = True

            # Check if we can access required OpenTelemetry components
            try:
                _ = context.get_current()
                _ = baggage.get_baggage("session_id", context.get_current())
            except Exception as e:
                # Graceful degradation following Agent OS standards - never crash host
                self._safe_log(
                    "debug",
                    "Processor health check failed",
                    honeyhive_data={"error_type": type(e).__name__},
                )
                processor_healthy = False

            # Simulate flush completion for compatibility with OpenTelemetry patterns
            return bool(processor_healthy)

        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host
            self._safe_log(
                "debug",
                "HoneyHive span processor flush error",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return False
