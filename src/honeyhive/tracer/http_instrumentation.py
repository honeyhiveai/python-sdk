import logging
import time
from typing import Any, Dict, Optional, Callable
from urllib.parse import urlparse

import wrapt
import httpx
import requests

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode

logger = logging.getLogger(__name__)


class HTTPInstrumentor:
    """
    HTTP instrumentation using wrapt to trace HTTP requests.
    Replaces traceloop's HTTP tracing functionality.
    """
    
    def __init__(self):
        self.tracer = trace.get_tracer("honeyhive.http", "1.0.0")
        self._instrumented = False
    
    def instrument(self):
        """Instrument HTTP libraries"""
        if self._instrumented:
            return
            
        # Instrument requests
        self._instrument_requests()
        
        # Instrument httpx
        self._instrument_httpx()
        
        self._instrumented = True
    
    def uninstrument(self):
        """Uninstrument HTTP libraries"""
        if not self._instrumented:
            return
            
        # Note: wrapt doesn't provide a direct unwrap method
        # We'll need to re-import the modules to reset them
        # This is a limitation of the current approach
        try:
            import importlib
            import requests
            import httpx
            
            # Re-import to reset instrumentation
            importlib.reload(requests)
            importlib.reload(httpx)
        except Exception as e:
            # If we can't uninstrument, just mark as uninstrumented
            pass
        
        self._instrumented = False
    
    def _instrument_requests(self):
        """Instrument the requests library"""
        
        @wrapt.function_wrapper
        def requests_wrapper(wrapped, instance, args, kwargs):
            method = kwargs.get('method', 'GET')
            url = kwargs.get('url', '')
            
            # Check if HTTP tracing is disabled
            if self._is_http_tracing_disabled():
                return wrapped(*args, **kwargs)
            
            span_name = f"HTTP {method}"
            with self.tracer.start_as_current_span(
                span_name,
                kind=SpanKind.CLIENT,
                attributes={
                    "http.method": method,
                    "http.url": url,
                    "http.scheme": urlparse(url).scheme,
                    "http.target": urlparse(url).path,
                    "http.host": urlparse(url).netloc,
                }
            ) as span:
                start_time = time.time()
                
                try:
                    response = wrapped(*args, **kwargs)
                    
                    # Add response attributes
                    span.set_attributes({
                        "http.status_code": response.status_code,
                        "http.response_size": len(response.content) if response.content else 0,
                    })
                    
                    # Set span status based on HTTP status code
                    if 200 <= response.status_code < 400:
                        span.set_status(Status(StatusCode.OK))
                    elif 400 <= response.status_code < 500:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    else:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    
                    return response
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("http.duration", duration)
        
        # Apply the wrapper to requests.Session.request
        wrapt.wrap_function_wrapper(requests.Session, "request", requests_wrapper)
    
    def _instrument_httpx(self):
        """Instrument the httpx library"""
        
        @wrapt.function_wrapper
        def httpx_sync_wrapper(wrapped, instance, args, kwargs):
            method = kwargs.get('method', 'GET')
            url = kwargs.get('url', '')
            
            # Check if HTTP tracing is disabled
            if self._is_http_tracing_disabled():
                return wrapped(*args, **kwargs)
            
            span_name = f"HTTP {method}"
            with self.tracer.start_as_current_span(
                span_name,
                kind=SpanKind.CLIENT,
                attributes={
                    "http.method": method,
                    "http.url": str(url),
                    "http.scheme": urlparse(str(url)).scheme,
                    "http.target": urlparse(str(url)).path,
                    "http.host": urlparse(str(url)).netloc,
                }
            ) as span:
                start_time = time.time()
                
                try:
                    response = wrapped(*args, **kwargs)
                    
                    # Add response attributes
                    span.set_attributes({
                        "http.status_code": response.status_code,
                        "http.response_size": len(response.content) if response.content else 0,
                    })
                    
                    # Set span status based on HTTP status code
                    if 200 <= response.status_code < 400:
                        span.set_status(Status(StatusCode.OK))
                    elif 400 <= response.status_code < 500:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    else:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    
                    return response
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("http.duration", duration)
        
        @wrapt.function_wrapper
        async def httpx_async_wrapper(wrapped, instance, args, kwargs):
            method = kwargs.get('method', 'GET')
            url = kwargs.get('url', '')
            
            # Check if HTTP tracing is disabled
            if self._is_http_tracing_disabled():
                return await wrapped(*args, **kwargs)
            
            span_name = f"HTTP {method}"
            with self.tracer.start_as_current_span(
                span_name,
                kind=SpanKind.CLIENT,
                attributes={
                    "http.method": method,
                    "http.url": str(url),
                    "http.scheme": urlparse(str(url)).scheme,
                    "http.target": urlparse(str(url)).path,
                    "http.host": urlparse(str(url)).netloc,
                }
            ) as span:
                start_time = time.time()
                
                try:
                    response = await wrapped(*args, **kwargs)
                    
                    # Add response attributes
                    span.set_attributes({
                        "http.status_code": response.status_code,
                        "http.response_size": len(response.content) if response.content else 0,
                    })
                    
                    # Set span status based on HTTP status code
                    if 200 <= response.status_code < 400:
                        span.set_status(Status(StatusCode.OK))
                    elif 400 <= response.status_code < 500:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    else:
                        span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                    
                    return response
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("http.duration", duration)
        
        # Apply the wrappers to httpx clients
        wrapt.wrap_function_wrapper(httpx.Client, "request", httpx_sync_wrapper)
        wrapt.wrap_function_wrapper(httpx.AsyncClient, "request", httpx_async_wrapper)
    
    def _is_http_tracing_disabled(self) -> bool:
        """Check if HTTP tracing is disabled via context"""
        from opentelemetry import context
        from honeyhive.utils.baggage_dict import BaggageDict
        
        ctx = context.get_current()
        bags = BaggageDict().get_all_baggage(ctx)
        disable_http_tracing = bags.get('disable_http_tracing', 'false')
        return disable_http_tracing.lower() == 'true'


# Global instance
http_instrumentor = HTTPInstrumentor()


def instrument_http():
    """Instrument HTTP libraries"""
    http_instrumentor.instrument()


def uninstrument_http():
    """Uninstrument HTTP libraries"""
    http_instrumentor.uninstrument()
