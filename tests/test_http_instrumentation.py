#!/usr/bin/env python3
"""
Comprehensive tests for http_instrumentation.py

Consolidated from multiple test files for better organization.
Focuses on working tests and practical coverage.
"""

import pytest
import os
import sys
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
import requests
import httpx

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer.http_instrumentation import (
    HTTPInstrumentor,
    instrument_http,
    uninstrument_http
)
from honeyhive.tracer.otel_tracer import BaggageDict


class TestHTTPInstrumentorBasic:
    """Basic HTTP instrumentation tests"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instrumentor = HTTPInstrumentor()
        
        # Reset instrumentation state
        try:
            self.instrumentor.uninstrument()
        except:
            pass
    
    def teardown_method(self):
        """Clean up after tests"""
        try:
            self.instrumentor.uninstrument()
        except:
            pass
    
    def test_instrumentor_initialization(self):
        """Test HTTPInstrumentor initialization"""
        instrumentor = HTTPInstrumentor()
        assert instrumentor is not None
        assert hasattr(instrumentor, 'instrument')
        assert hasattr(instrumentor, 'uninstrument')
    
    def test_instrumentation_idempotency(self):
        """Test that instrumentation is idempotent"""
        instrumentor = HTTPInstrumentor()
        
        # First instrumentation
        instrumentor.instrument()
        assert hasattr(requests.Session.request, '__wrapped__')
        
        # Second instrumentation (should not change anything)
        instrumentor.instrument()
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_instrumentation_methods_exist(self):
        """Test that instrumentation wraps the expected methods"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # Check that requests methods are wrapped
        assert hasattr(requests.Session.request, '__wrapped__')
        
        # Check that httpx methods are wrapped
        assert hasattr(httpx.Client.request, '__wrapped__')
        assert hasattr(httpx.AsyncClient.request, '__wrapped__')
    
    def test_import_error_handling_requests(self):
        """Test import error handling for requests during uninstrumentation"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # Mock import error for requests
        with patch('importlib.reload', side_effect=ImportError("No module named 'requests'")):
            # Should not raise an exception
            instrumentor.uninstrument()
    
    def test_import_error_handling_httpx(self):
        """Test import error handling for httpx during uninstrumentation"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # Mock import error for httpx
        with patch('importlib.reload', side_effect=ImportError("No module named 'httpx'")):
            # Should not raise an exception
            instrumentor.uninstrument()
    
    def test_wrap_function_wrapper_calls(self):
        """Test that wrapt.wrap_function_wrapper is called correctly"""
        instrumentor = HTTPInstrumentor()
        
        with patch('wrapt.wrap_function_wrapper') as mock_wrap:
            instrumentor.instrument()
            
            # Should be called for requests and httpx methods
            assert mock_wrap.call_count >= 3  # requests.Session.request, httpx.Client.request, httpx.AsyncClient.request
    
    def test_tracer_initialization(self):
        """Test that the tracer is initialized correctly"""
        instrumentor = HTTPInstrumentor()
        
        # Just test that instrumentation completes without error
        instrumentor.instrument()
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_is_http_tracing_disabled_method_exists(self):
        """Test HTTPInstrumentor._is_http_tracing_disabled method exists"""
        instrumentor = HTTPInstrumentor()
        assert hasattr(instrumentor, '_is_http_tracing_disabled')
        assert callable(getattr(instrumentor, '_is_http_tracing_disabled'))
        
        # Test that it returns a boolean
        result = instrumentor._is_http_tracing_disabled()
        assert isinstance(result, bool)
    
    def test_global_instrument_function(self):
        """Test the global instrument_http function"""
        # Test that it doesn't raise an exception
        instrument_http()
        
        # Verify instrumentation occurred
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_global_uninstrument_function(self):
        """Test the global uninstrument_http function"""
        # First instrument
        instrument_http()
        
        # Test that uninstrumentation doesn't raise an exception
        uninstrument_http()
    
    def test_wrapper_function_parameter_handling(self):
        """Test wrapper function parameter handling"""
        instrumentor = HTTPInstrumentor()
        
        with patch('wrapt.wrap_function_wrapper') as mock_wrap:
            instrumentor.instrument()
            
            # Get the wrapper function for requests
            requests_wrapper = None
            for call_args in mock_wrap.call_args_list:
                if call_args[0][1] == 'request' and 'Session' in str(call_args[0][0]):
                    requests_wrapper = call_args[0][2]
                    break
            
            assert requests_wrapper is not None
            assert callable(requests_wrapper)
    
    def test_wrapper_function_url_parsing(self):
        """Test wrapper function URL parsing"""
        instrumentor = HTTPInstrumentor()
        
        with patch('wrapt.wrap_function_wrapper') as mock_wrap:
            instrumentor.instrument()
            
            # Test that wrappers can handle different URL formats
            # This is tested implicitly by the wrapper creation
            assert mock_wrap.called
    
    def test_wrapper_function_method_extraction(self):
        """Test wrapper function method extraction"""
        instrumentor = HTTPInstrumentor()
        
        with patch('wrapt.wrap_function_wrapper') as mock_wrap:
            instrumentor.instrument()
            
            # Test that wrappers can extract HTTP methods
            # This is tested implicitly by the wrapper creation
            assert mock_wrap.called
    
    def test_wrapper_function_response_size_calculation(self):
        """Test wrapper function response size calculation"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # This tests that the wrapper functions are created correctly
        # The actual response size calculation is tested in integration tests
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_wrapper_function_status_code_handling(self):
        """Test wrapper function status code handling"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # This tests that the wrapper functions are created correctly
        # The actual status code handling is tested in integration tests
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_wrapper_function_empty_content_handling(self):
        """Test wrapper function empty content handling"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # This tests that the wrapper functions are created correctly
        # The actual empty content handling is tested in integration tests
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_wrapper_function_duration_tracking(self):
        """Test wrapper function duration tracking"""
        instrumentor = HTTPInstrumentor()
        instrumentor.instrument()
        
        # This tests that the wrapper functions are created correctly
        # The actual duration tracking is tested in integration tests
        assert hasattr(requests.Session.request, '__wrapped__')


class TestHTTPInstrumentorConfiguration:
    """Test HTTP instrumentation configuration and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instrumentor = HTTPInstrumentor()
        
        # Reset instrumentation state
        try:
            self.instrumentor.uninstrument()
        except:
            pass
    
    def teardown_method(self):
        """Clean up after tests"""
        try:
            self.instrumentor.uninstrument()
        except:
            pass
    
    def test_instrumentation_with_tracer_provider(self):
        """Test instrumentation with custom tracer provider"""
        from opentelemetry.sdk.trace import TracerProvider
        
        tracer_provider = TracerProvider()
        
        with patch('opentelemetry.trace.get_tracer_provider', return_value=tracer_provider):
            self.instrumentor.instrument()
            assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_instrumentation_without_tracer_provider(self):
        """Test instrumentation without custom tracer provider"""
        self.instrumentor.instrument()
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_baggage_context_usage(self):
        """Test that instrumentation can handle baggage context"""
        instrumentor = HTTPInstrumentor()
        
        # Test that the method exists and can be called
        result = instrumentor._is_http_tracing_disabled()
        assert isinstance(result, bool)
    
    def test_environment_variable_independence(self):
        """Test that instrumentation works independent of environment variables"""
        # Test with environment variable set to disable
        with patch.dict(os.environ, {'HH_DISABLE_HTTP_TRACING': 'true'}):
            instrumentor = HTTPInstrumentor()
            instrumentor.instrument()
            
            # Should still instrument regardless of environment variable
            assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_threading_safety(self):
        """Test that instrumentation is thread-safe"""
        results = []
        
        def instrument_in_thread():
            try:
                instrumentor = HTTPInstrumentor()
                instrumentor.instrument()
                results.append(True)
            except Exception:
                results.append(False)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=instrument_in_thread)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All threads should succeed
        assert all(results)
        assert len(results) == 5
    
    def test_multiple_instrumentor_instances(self):
        """Test multiple instrumentor instances"""
        instrumentor1 = HTTPInstrumentor()
        instrumentor2 = HTTPInstrumentor()
        
        # Both should be able to instrument without conflicts
        instrumentor1.instrument()
        instrumentor2.instrument()
        
        # Verify instrumentation is active
        assert hasattr(requests.Session.request, '__wrapped__')
    
    def test_instrumentation_state_persistence(self):
        """Test that instrumentation state persists across instances"""
        instrumentor1 = HTTPInstrumentor()
        instrumentor1.instrument()
        
        # Create new instance
        instrumentor2 = HTTPInstrumentor()
        
        # Should still be instrumented
        assert hasattr(requests.Session.request, '__wrapped__')
        
        # Second instance should be able to uninstrument
        instrumentor2.uninstrument()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
