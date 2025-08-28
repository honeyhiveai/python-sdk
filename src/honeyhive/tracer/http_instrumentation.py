"""HTTP instrumentation for HoneyHive tracing."""

import os
import time
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlparse

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .otel_tracer import HoneyHiveTracer


class HTTPInstrumentation:
    """HTTP instrumentation for automatic request tracing."""
    
    def __init__(self):
        """Initialize HTTP instrumentation."""
        self._original_httpx_request = None
        self._original_requests_request = None
        self._is_instrumented = False
    
    def instrument(self):
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
    
    def uninstrument(self):
        """Remove HTTP instrumentation."""
        if not self._is_instrumented:
            return
        
        # Restore httpx
        if HTTPX_AVAILABLE and self._original_httpx_request:
            httpx.Client.request = self._original_httpx_request
            httpx.AsyncClient.request = self._original_httpx_request
        
        # Restore requests
        if REQUESTS_AVAILABLE and self._original_requests_request:
            requests.Session.request = self._original_requests_request
        
        self._is_instrumented = False
    
    def _instrument_httpx(self):
        """Instrument httpx for automatic tracing."""
        if not HTTPX_AVAILABLE:
            return
        
        # Store original methods
        self._original_httpx_request = httpx.Client.request
        
        # Create instrumented request method
        def instrumented_request(self, method, url, **kwargs):
            # Simple instrumentation that won't conflict with OTLP exporter
            try:
                # Get tracer instance
                tracer = HoneyHiveTracer._instance
                if tracer:
                    # Create a simple span for the request
                    with tracer.start_span(name=f"HTTP {method.upper()}", attributes={"http.method": method.upper(), "http.url": str(url)}):
                        return self._original_httpx_request(method, url, **kwargs)
                else:
                    return self._original_httpx_request(method, url, **kwargs)
            except Exception:
                # Fallback to original behavior
                return self._original_httpx_request(method, url, **kwargs)
        
        # Replace methods
        httpx.Client.request = instrumented_request
        httpx.AsyncClient.request = instrumented_request
    
    def _instrument_requests(self):
        """Instrument requests for automatic tracing."""
        if not REQUESTS_AVAILABLE:
            return
        
        # Store original method
        self._original_requests_request = requests.Session.request
        
        # Create instrumented request method
        def instrumented_request(self, method, url, **kwargs):
            try:
                # Check if we have the trace method available
                if hasattr(self, '_trace_request'):
                    return self._trace_request(method, url, **kwargs)
                else:
                    # Fallback to original behavior if tracing not available
                    return self._original_requests_request(method, url, **kwargs)
            except (AttributeError, Exception):
                # Graceful fallback to original behavior
                return self._original_requests_request(method, url, **kwargs)
        
        # Replace method
        requests.Session.request = instrumented_request
    
    def _trace_request(self, method: str, url: str, **kwargs):
        """Trace an HTTP request."""
        # Get tracer instance
        try:
            tracer = HoneyHiveTracer._instance
            if not tracer:
                return self._original_httpx_request(method, url, **kwargs)
        except:
            return self._original_httpx_request(method, url, **kwargs)
        
        # Parse URL
        parsed_url = urlparse(url)
        
        # Prepare span attributes
        attributes = {
            "http.method": method.upper(),
            "http.url": url,
            "http.scheme": parsed_url.scheme,
            "http.host": parsed_url.netloc,
            "http.path": parsed_url.path,
            "http.query": parsed_url.query,
        }
        
        # Add headers if available
        headers = kwargs.get('headers', {})
        if headers:
            attributes["http.request.header.content_type"] = headers.get('content-type')
            attributes["http.request.header.user_agent"] = headers.get('user-agent')
        
        # Start span
        with tracer.start_span(
            name=f"HTTP {method.upper()}",
            attributes=attributes,
        ):
            start_time = time.time()
            try:
                # Make the request
                response = self._original_httpx_request(method, url, **kwargs)
                
                # Add response attributes
                if hasattr(response, 'status_code'):
                    attributes["http.status_code"] = response.status_code
                    attributes["http.status_text"] = response.reason_phrase if hasattr(response, 'reason_phrase') else None
                
                if hasattr(response, 'headers'):
                    response_headers = dict(response.headers)
                    attributes["http.response.header.content_type"] = response_headers.get('content-type')
                    attributes["http.response.header.content_length"] = response_headers.get('content-length')
                
                return response
            
            except Exception as e:
                # Add error information
                attributes["honeyhive.error"] = str(e)
                attributes["honeyhive.error.type"] = type(e).__name__
                raise
            
            finally:
                # Add duration
                duration = (time.time() - start_time) * 1000
                attributes["honeyhive.duration"] = duration


# Global instrumentation instance
# Check if HTTP tracing is disabled at import time
if os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true":
    # Create a dummy instrumentation that does nothing
    class DummyInstrumentation:
        def instrument(self):
            pass
        def uninstrument(self):
            pass
        def _instrument_httpx(self):
            pass
        def _instrument_requests(self):
            pass
    _instrumentation = DummyInstrumentation()
else:
    # Only create the instrumentation if HTTP tracing is enabled
    _instrumentation = HTTPInstrumentation()


def instrument_http():
    """Instrument HTTP libraries for automatic tracing."""
    # Check if HTTP tracing is disabled
    if os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true":
        return
    
    _instrumentation.instrument()


def uninstrument_http():
    """Remove HTTP instrumentation."""
    _instrumentation.uninstrument()
