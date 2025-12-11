"""HoneyHive OTLP exporter with optimized connection pooling.

This module provides the OTLP exporter for HoneyHive tracers. It's an enhanced
wrapper around the standard OpenTelemetry OTLP exporter that includes:

- Optimized HTTP session with connection pooling for better performance
- Enhanced retry strategies for reliable span delivery
- Session statistics and monitoring capabilities
- Graceful fallback to standard sessions if optimization fails

All span processing should be completed by the HoneyHiveSpanProcessor before
spans reach this exporter, as ReadableSpan objects are immutable.
"""

import json
from typing import Any, Dict, Optional, Sequence, Union

import requests

# Third-party imports
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import StatusCode

# Local imports
from ...utils.logger import safe_log
from .otlp_session import (
    OTLPSessionConfig,
    create_optimized_otlp_session,
    get_default_otlp_config,
    get_session_stats,
)


class OTLPJSONExporter(SpanExporter):
    """OTLP JSON exporter that sends spans in JSON format over HTTP.

    This exporter serializes spans to OTLP JSON format and sends them via HTTP POST
    with Content-Type: application/json. It implements the SpanExporter interface
    and can be used as a drop-in replacement for OTLPSpanExporter when JSON format
    is required.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        timeout: Optional[float] = None,
        tracer_instance: Any = None,
    ) -> None:
        """Initialize the OTLP JSON exporter.

        Args:
            endpoint: OTLP endpoint URL
                (e.g., "https://api.honeyhive.ai/opentelemetry/v1/traces")
            headers: Optional HTTP headers to include in requests
            session: Optional requests.Session to use for HTTP requests
            timeout: Optional timeout in seconds for HTTP requests
            tracer_instance: Optional tracer instance for logging context
        """
        self.endpoint = endpoint.rstrip("/")
        # Copy headers to avoid modifying the original dict
        self.headers = dict(headers) if headers else {}
        self.session = session or requests.Session()
        self.timeout = timeout
        self.tracer_instance = tracer_instance
        self._is_shutdown = False

        # Always set Content-Type header for JSON (override any existing value)
        self.headers["Content-Type"] = "application/json"

        safe_log(
            tracer_instance,
            "info",
            "OTLPJSONExporter initialized",
            honeyhive_data={
                "endpoint": self.endpoint,
                "content_type": self.headers.get("Content-Type"),
                "has_session": self.session is not None,
            },
        )

    def _span_to_otlp_json(self, span: ReadableSpan) -> Dict[str, Any]:
        """Convert a ReadableSpan to OTLP JSON format.

        Args:
            span: ReadableSpan to convert

        Returns:
            Dictionary representing the span in OTLP JSON format
        """
        # Convert trace_id and span_id to hex strings
        trace_id = format(span.context.trace_id, "032x")
        span_id = format(span.context.span_id, "016x")
        parent_span_id = None
        if span.parent and hasattr(span.parent, "span_id") and span.parent.span_id:
            parent_span_id = format(span.parent.span_id, "016x")

        # Convert attributes - use string values, let backend handle type conversion
        attributes = []
        if span.attributes:
            for key, value in span.attributes.items():
                attr = {
                    "key": key,
                    "value": {"stringValue": str(value)},
                }
                attributes.append(attr)

        # Convert events
        events = []
        if span.events:
            for event in span.events:
                event_attrs = []
                if event.attributes:
                    for key, value in event.attributes.items():
                        event_attrs.append(
                            {
                                "key": key,
                                "value": {"stringValue": str(value)},
                            }
                        )
                events.append(
                    {
                        # uint64 - nanoseconds since Unix epoch
                        "timeUnixNano": event.timestamp,
                        "name": event.name,
                        "attributes": event_attrs,
                    }
                )

        # Convert status
        status_code_map = {
            StatusCode.OK: "STATUS_CODE_OK",
            StatusCode.ERROR: "STATUS_CODE_ERROR",
        }
        status = {
            "code": status_code_map.get(span.status.status_code, "STATUS_CODE_UNSET")
        }
        if span.status.description:
            status["message"] = span.status.description

        # Convert kind - use span.kind.name directly (already in correct format)
        span_kind = (
            f"SPAN_KIND_{span.kind.name}"
            if not span.kind.name.startswith("SPAN_KIND_")
            else span.kind.name
        )

        span_json = {
            "traceId": trace_id,
            "spanId": span_id,
            "parentSpanId": parent_span_id,
            "name": span.name,
            "kind": span_kind,
            # uint64 - nanoseconds since Unix epoch
            "startTimeUnixNano": span.start_time,
            "endTimeUnixNano": span.end_time,
            "attributes": attributes,
            "events": events,
            "status": status,
        }

        return span_json

    def _spans_to_otlp_json_payload(
        self, spans: Sequence[ReadableSpan]
    ) -> Dict[str, Any]:
        """Convert spans to OTLP JSON payload format.

        Args:
            spans: Sequence of ReadableSpan objects

        Returns:
            Dictionary in OTLP JSON format ready for HTTP POST
        """
        if not spans:
            return {"resourceSpans": []}

        # Simplified: use first span's resource, put all spans in one scope
        first_span = spans[0]
        resource_attrs = []
        if first_span.resource and first_span.resource.attributes:
            resource_attrs = [
                {"key": k, "value": {"stringValue": str(v)}}
                for k, v in first_span.resource.attributes.items()
            ]

        # Get scope info from first span (simplified - all spans in one scope)
        scope_info = {}
        if (
            hasattr(first_span, "instrumentation_scope")
            and first_span.instrumentation_scope
        ):
            scope_info["name"] = first_span.instrumentation_scope.name or "unknown"
            if first_span.instrumentation_scope.version:
                scope_info["version"] = first_span.instrumentation_scope.version

        # Convert all spans
        span_jsons = [self._span_to_otlp_json(span) for span in spans]

        resource_span = {
            "resource": {"attributes": resource_attrs} if resource_attrs else {},
            "scopeSpans": [{"scope": scope_info, "spans": span_jsons}],
        }

        return {"resourceSpans": [resource_span]}

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to HoneyHive via OTLP JSON format.

        Args:
            spans: Sequence of ReadableSpan objects to export

        Returns:
            SpanExportResult indicating success or failure
        """
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "JSON exporter already shutdown, skipping export",
            )
            return SpanExportResult.FAILURE

        if not spans:
            return SpanExportResult.SUCCESS

        try:
            # Convert spans to OTLP JSON format
            payload = self._spans_to_otlp_json_payload(spans)
            json_data = json.dumps(payload)

            # Log the JSON payload for debugging
            safe_log(
                self.tracer_instance,
                "debug",
                f"Exporting {len(spans)} spans via OTLP JSON",
                honeyhive_data={
                    "span_count": len(spans),
                    "endpoint": self.endpoint,
                    "payload_size_bytes": len(json_data),
                    "json_payload": json.dumps(
                        payload, indent=2
                    ),  # Pretty-printed for debugging
                },
            )

            # Send HTTP POST request
            response = self.session.post(
                self.endpoint,
                data=json_data,
                headers=self.headers,
                timeout=self.timeout,
            )

            # Check response status
            if response.status_code == 200:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    f"Successfully exported {len(spans)} spans via OTLP JSON",
                    honeyhive_data={
                        "span_count": len(spans),
                        "status_code": response.status_code,
                    },
                )
                return SpanExportResult.SUCCESS

            safe_log(
                self.tracer_instance,
                "error",
                f"OTLP JSON export failed with status {response.status_code}",
                honeyhive_data={
                    "status_code": response.status_code,
                    "response_body": response.text[:500] if response.text else None,
                    "span_count": len(spans),
                },
            )
            return SpanExportResult.FAILURE

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                f"Error in OTLP JSON export: {e}",
                honeyhive_data={
                    "error_type": type(e).__name__,
                    "span_count": len(spans),
                },
            )
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans (no-op for this exporter)."""
        return True

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        if self._is_shutdown:
            return
        self._is_shutdown = True
        if self.session:
            self.session.close()


class HoneyHiveOTLPExporter(SpanExporter):
    """HoneyHive OTLP exporter with optimized connection pooling.

    This exporter is an enhanced wrapper around the standard OpenTelemetry OTLP
    exporter that includes optimized HTTP session with connection pooling for
    better performance and reliability. All span processing should have been
    completed by the HoneyHiveSpanProcessor before spans reach this exporter.

    Features:
    - Optimized HTTP session with connection pooling
    - Enhanced retry strategies for reliable span delivery
    - Session statistics and monitoring capabilities
    - Graceful fallback to standard sessions if optimization fails
    """

    def __init__(
        self,
        tracer_instance: Any = None,
        session_config: Optional[OTLPSessionConfig] = None,
        use_optimized_session: bool = True,
        protocol: str = "http/protobuf",
        **kwargs: Any,
    ) -> None:
        """Initialize the HoneyHive OTLP exporter with optional connection pooling.

        Args:
            tracer_instance: Optional tracer instance for logging context
            session_config: Optional configuration for optimized HTTP session
            use_optimized_session: Whether to use optimized session (default: True)
            protocol: OTLP protocol format
                - "http/protobuf" (default) or "http/json"
            **kwargs: Arguments passed to underlying OTLPSpanExporter or
                OTLPJSONExporter
        """
        self.tracer_instance = tracer_instance
        self.session_config = session_config or get_default_otlp_config(tracer_instance)
        self.use_optimized_session = use_optimized_session
        self.protocol = protocol.lower()
        self._session: Optional[requests.Session] = None
        self._is_shutdown = False
        self._use_json = self.protocol == "http/json"
        self._otlp_exporter: Union[OTLPSpanExporter, OTLPJSONExporter]

        # Create optimized session if requested and not already provided
        if use_optimized_session and "session" not in kwargs:
            try:
                self._session = create_optimized_otlp_session(
                    config=self.session_config, tracer_instance=tracer_instance
                )
                kwargs["session"] = self._session

                safe_log(
                    tracer_instance,
                    "info",
                    "HoneyHiveOTLPExporter initialized with optimized pooling",
                    honeyhive_data=self.session_config.to_dict(),
                )

            except Exception as e:
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Failed to create optimized session, using default: {e}",
                    honeyhive_data={"error_type": type(e).__name__},
                )
                # Continue with default session
        else:
            # Store reference to provided session or None
            self._session = kwargs.get("session")

        # Initialize the appropriate exporter based on protocol
        if self._use_json:
            # Use JSON exporter
            endpoint = kwargs.get("endpoint")
            if not endpoint:
                raise ValueError("endpoint is required for OTLP exporter")
            headers = kwargs.get("headers", {})
            timeout = kwargs.get("timeout")
            self._otlp_exporter = OTLPJSONExporter(
                endpoint=endpoint,
                headers=headers,
                session=self._session,
                timeout=timeout,
                tracer_instance=tracer_instance,
            )
            safe_log(
                tracer_instance,
                "info",
                "HoneyHiveOTLPExporter initialized with JSON format",
                honeyhive_data={"protocol": "http/json", "endpoint": endpoint},
            )
        else:
            # Use standard Protobuf exporter
            self._otlp_exporter = OTLPSpanExporter(**kwargs)

        # Log initialization details
        session_type = (
            "optimized" if self._session and use_optimized_session else "default"
        )
        safe_log(
            tracer_instance,
            "debug",
            f"HoneyHiveOTLPExporter initialized with {session_type} session",
            honeyhive_data={
                "session_type": session_type,
                "use_optimized_session": use_optimized_session,
                "has_custom_session": "session" in kwargs,
            },
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to HoneyHive via OTLP.

        This method exports spans that have already been processed by the
        HoneyHiveSpanProcessor. All attribute processing should have been
        completed before reaching this exporter.

        Args:
            spans: Sequence of ReadableSpan objects to export

        Returns:
            SpanExportResult indicating success or failure
        """
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, skipping export",
            )
            return SpanExportResult.FAILURE

        safe_log(
            self.tracer_instance,
            "debug",
            f"Exporting {len(spans)} processed spans to HoneyHive",
            honeyhive_data={"span_count": len(spans)},
        )

        try:
            # All span processing completed by HoneyHiveSpanProcessor
            # This exporter simply passes the spans to the underlying OTLP exporter
            return self._otlp_exporter.export(spans)

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                f"Error in OTLP export: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans."""
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, skipping force_flush",
            )
            return True
        return self._otlp_exporter.force_flush(timeout_millis)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics from the HTTP session.

        Returns:
            Dictionary containing session and connection pool statistics
        """
        if not self._session:
            return {"error": "No session available", "session_type": "default"}

        try:
            stats = get_session_stats(self._session)
            stats.update(
                {
                    "session_type": (
                        "optimized" if self.use_optimized_session else "custom"
                    ),
                    "session_config": (
                        self.session_config.to_dict() if self.session_config else None
                    ),
                }
            )
            return stats
        except Exception as e:
            return {
                "error": f"Failed to get session stats: {e}",
                "session_type": "optimized" if self.use_optimized_session else "custom",
            }

    def log_session_stats(self) -> None:
        """Log current session statistics for monitoring."""
        stats = self.get_session_stats()
        safe_log(
            self.tracer_instance,
            "debug",
            "OTLP exporter session statistics",
            honeyhive_data={"session_stats": stats},
        )

    def shutdown(self) -> None:
        """Shutdown the exporter and log final statistics."""
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, ignoring call",
            )
            return

        # Log final session statistics before shutdown
        if self._session and self.tracer_instance:
            try:
                final_stats = self.get_session_stats()
                safe_log(
                    self.tracer_instance,
                    "info",
                    "OTLP exporter final session statistics",
                    honeyhive_data={"final_session_stats": final_stats},
                )
            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    f"Could not get final session stats: {e}",
                )

        self._is_shutdown = True
        self._otlp_exporter.shutdown()
        safe_log(
            self.tracer_instance, "debug", "HoneyHiveOTLPExporter shutdown completed"
        )
