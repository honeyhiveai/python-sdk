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

from typing import Any, Dict, Optional, Sequence

import requests

# Third-party imports
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

# Local imports
from ...utils.logger import safe_log
from .otlp_session import (
    OTLPSessionConfig,
    create_optimized_otlp_session,
    get_default_otlp_config,
    get_session_stats,
)


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
        **kwargs: Any,
    ) -> None:
        """Initialize the HoneyHive OTLP exporter with optional connection pooling.

        Args:
            tracer_instance: Optional tracer instance for logging context
            session_config: Optional configuration for optimized HTTP session
            use_optimized_session: Whether to use optimized session (default: True)
            **kwargs: Arguments passed to the underlying OTLPSpanExporter
        """
        self.tracer_instance = tracer_instance
        self.session_config = session_config or get_default_otlp_config(tracer_instance)
        self.use_optimized_session = use_optimized_session
        self._session: Optional[requests.Session] = None
        self._is_shutdown = False

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

        # Initialize the underlying OTLP exporter
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
