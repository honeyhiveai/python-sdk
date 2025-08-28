"""Tests for HoneyHive HTTP instrumentation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from honeyhive.tracer.http_instrumentation import HTTPInstrumentation
from honeyhive.tracer import HoneyHiveTracer


class TestHTTPInstrumentation:
    """Test HTTP instrumentation."""
    
    def test_http_instrumentation_initialization(self):
        """Test HTTP instrumentation initialization."""
        instrumentation = HTTPInstrumentation()
        
        assert instrumentation._is_instrumented is False
        assert instrumentation._original_httpx_request is None
        assert instrumentation._original_requests_request is None
    
    def test_http_instrumentation_instrument(self):
        """Test HTTP instrumentation enable."""
        instrumentation = HTTPInstrumentation()
        
        assert instrumentation._is_instrumented is False
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
    
    def test_http_instrumentation_uninstrument(self):
        """Test HTTP instrumentation disable."""
        instrumentation = HTTPInstrumentation()
        
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
        
        instrumentation.uninstrument()
        assert instrumentation._is_instrumented is False
    
    def test_http_instrumentation_double_instrument(self):
        """Test that double instrumentation doesn't cause issues."""
        instrumentation = HTTPInstrumentation()
        
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
        
        # Second call should not change state
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
    
    def test_http_instrumentation_double_uninstrument(self):
        """Test that double uninstrumentation doesn't cause issues."""
        instrumentation = HTTPInstrumentation()
        
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
        
        instrumentation.uninstrument()
        assert instrumentation._is_instrumented is False
        
        # Second call should not change state
        instrumentation.uninstrument()
        assert instrumentation._is_instrumented is False
    
    @patch('honeyhive.tracer.http_instrumentation.HTTPX_AVAILABLE', False)
    @patch('honeyhive.tracer.http_instrumentation.REQUESTS_AVAILABLE', False)
    def test_http_instrumentation_no_libraries(self):
        """Test HTTP instrumentation when no HTTP libraries are available."""
        instrumentation = HTTPInstrumentation()
        
        # Should not fail even when libraries are not available
        instrumentation.instrument()
        assert instrumentation._is_instrumented is True
        
        instrumentation.uninstrument()
        assert instrumentation._is_instrumented is False
    
    def test_http_instrumentation_instrument_uninstrument_cycle(self):
        """Test multiple instrument/uninstrument cycles."""
        instrumentation = HTTPInstrumentation()
        
        # Multiple cycles should work correctly
        for _ in range(5):
            instrumentation.instrument()
            assert instrumentation._is_instrumented is True
            
            instrumentation.uninstrument()
            assert instrumentation._is_instrumented is False
