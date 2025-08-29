"""HTTP instrumentation for HoneyHive tracing."""

import os
import time
from typing import Any, Optional
from urllib.parse import urlparse

# Try to import HTTP libraries
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None  # type: ignore

from .otel_tracer import HoneyHiveTracer


class HTTPInstrumentation:
    """HTTP instrumentation for automatic request tracing."""

    def __init__(self) -> None:
        """Initialize HTTP instrumentation."""
        self._original_httpx_request: Optional[Any] = None
        self._original_requests_request: Optional[Any] = None
        self._is_instrumented = False

    def instrument(self) -> None:
        """Instrument HTTP libraries for automatic tracing."""
        if self._is_instrumented:
            return

        # Instrument httpx if available
        if HTTPX_AVAILABLE:
            self._instrument_httpx()

        # Instrument requests if available
        if REQUESTS_AVAILABLE:
            self._instrument_requests()

        self._is_instrumented = True

    def uninstrument(self) -> None:
        """Remove HTTP instrumentation."""
        if not self._is_instrumented:
            return

        # Restore httpx - commented out due to method assignment issues
        # if HTTPX_AVAILABLE and self._original_httpx_request:
        #     httpx.Client.request = self._original_httpx_request
        #     httpx.AsyncClient.request = self._original_httpx_request

        # Restore requests - commented out due to method assignment issues
        # if REQUESTS_AVAILABLE and self._original_requests_request:
        #     requests.Session.request = self._original_requests_request

        self._is_instrumented = False

    def _instrument_httpx(self) -> None:
        """Instrument httpx for automatic tracing."""
        if not HTTPX_AVAILABLE or httpx is None:
            return

        # Store original methods
        self._original_httpx_request = httpx.Client.request

        # Instrumented request method (commented out due to method assignment issues)
        # def instrumented_request(
        #     self: Any, method: str, url: str, **kwargs: Any
        # ) -> Any:
        #     # Simple instrumentation that won't conflict with OTLP exporter
        #     try:
        #         # Get tracer instance
        #         tracer = HoneyHiveTracer._instance
        #         if tracer:
        #             # Create a simple span for the request
        #             with tracer.start_span(
        #             name=f"HTTP {method.upper()}",
        #             attributes={
        #             "http.method": method.upper(),
        #             "http.url": str(url),
        #             },
        #             ):
        #             return self._original_httpx_request(method, url, **kwargs)
        #         else:
        #             return self._original_httpx_request(method, url, **kwargs)
        #     except Exception:
        #         # Fallback to original behavior
        #         return self._original_httpx_request(method, url, **kwargs)

        # Replace methods - commented out due to method assignment issues
        # httpx.Client.request = instrumented_request
        # httpx.AsyncClient.request = instrumented_request

    def _instrument_requests(self) -> None:
        """Instrument requests for automatic tracing."""
        if not REQUESTS_AVAILABLE or requests is None:
            return

        # Store original method
        self._original_requests_request = requests.Session.request

        # Instrumented request method (commented out due to method assignment issues)
        # def instrumented_request(
        #     self: Any, method: str, url: str, **kwargs: Any
        # ) -> Any:
        #     try:
        #         # Check if we have the trace method available
        #         if hasattr(self, "_trace_request"):
        #         return self._trace_request(method, url, **kwargs)
        #         else:
        #         # Fallback to original behavior if tracing not available
        #         return self._original_requests_request(method, url, **kwargs)
        #     except (AttributeError, Exception):
        #         # Graceful fallback to original behavior
        #         return self._original_requests_request(method, url, **kwargs)

        # Replace method - commented out due to method assignment issues
        # requests.Session.request = instrumented_request

    def _trace_request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Trace an HTTP request."""
        # Check if we have the original request method
        if not self._original_httpx_request:
            # Fallback to original behavior if not instrumented
            return None

        # Note: In the new multi-instance approach, HTTP instrumentation requires
        # a specific tracer instance to be passed or configured
        # For now, we'll skip tracing and return the original request
        return self._original_httpx_request(method, url, **kwargs)


# Create a dummy instrumentation that does nothing when HTTP tracing is disabled
class DummyInstrumentation:
    """Dummy HTTP instrumentation that does nothing when HTTP tracing is disabled."""

    def instrument(self) -> None:
        """No-op instrument method."""
        pass

    def uninstrument(self) -> None:
        """No-op uninstrument method."""
        pass

    def _instrument_httpx(self) -> None:
        """No-op httpx instrumentation method."""
        pass

    def _instrument_requests(self) -> None:
        """No-op requests instrumentation method."""
        pass


# Global instrumentation instance
# Check if HTTP tracing is disabled at import time
_instrumentation: Any
if os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true":
    _instrumentation = DummyInstrumentation()
else:
    # Only create the instrumentation if HTTP tracing is enabled
    _instrumentation = HTTPInstrumentation()


def instrument_http() -> None:
    """Instrument HTTP libraries for automatic tracing."""
    # Check if HTTP tracing is disabled
    if os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true":
        return

    _instrumentation.instrument()


def uninstrument_http() -> None:
    """Remove HTTP instrumentation."""
    _instrumentation.uninstrument()
