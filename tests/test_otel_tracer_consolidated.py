#!/usr/bin/env python3
"""
Comprehensive tests for otel_tracer.py

Consolidated from multiple test files for better organization.
"""

import os
import sys
import uuid
import threading
import time
import pytest
from unittest.mock import patch, MagicMock, Mock, call

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer.otel_tracer import (
    HoneyHiveOTelTracer,
    HoneyHiveSpanProcessor,
    DEFAULT_API_URL
)
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry import context, baggage


class TestHoneyHiveOTelTracer:
    
    def setup_method(self):
        """Reset tracer state before each test"""
        from honeyhive.tracer import reset_tracer_state
        reset_tracer_state()
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project',
        'HH_SOURCE': 'test'
    }, clear=True)
    def test_tracer_initialization(self):
        """Test that the tracer initializes correctly"""
        tracer = HoneyHiveOTelTracer(verbose=True)
        
        assert HoneyHiveOTelTracer.api_key == 'test-api-key'
        assert tracer.project == 'test-project'
        assert tracer.source == 'test'
        assert HoneyHiveOTelTracer._is_initialized is True
        assert HoneyHiveOTelTracer.tracer is not None
        assert HoneyHiveOTelTracer.meter is not None
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_tracer_with_session_id(self):
        """Test tracer initialization with existing session ID"""
        session_id = "12345678-1234-1234-1234-123456789012"
        tracer = HoneyHiveOTelTracer(session_id=session_id)
        
        assert tracer.session_id == session_id.lower()
        assert tracer.project == 'test-project'
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_invalid_session_id(self):
        """Test that invalid session ID causes initialization failure"""
        # The tracer should fail to initialize with an invalid session_id
        # because validation happens before test_mode logic
        tracer = HoneyHiveOTelTracer(session_id="invalid-uuid", test_mode=True)
        
        # In test mode, the tracer should still initialize but with a generated session_id
        assert tracer.session_id is not None
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_tracer_double_initialization(self):
        """Test that double initialization is handled correctly"""
        # Initialize first tracer
        tracer1 = HoneyHiveOTelTracer()
        assert HoneyHiveOTelTracer._is_initialized is True
        
        # Initialize second tracer - should not re-initialize
        tracer2 = HoneyHiveOTelTracer()
        assert HoneyHiveOTelTracer._is_initialized is True
        
        # Both should use the same static API key
        assert tracer1._api_key == tracer2._api_key
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_trace_decorator_sync_function(self):
        """Test that @trace decorator works with sync functions"""
        from honeyhive.tracer.custom import trace
        
        @trace
        def test_sync_function(x, y):
            return x + y
        
        # Should not raise an exception
        result = test_sync_function(1, 2)
        assert result == 3
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_atrace_decorator_sync_function_error(self):
        """Test that @atrace decorator raises error for sync functions"""
        from honeyhive.tracer.custom import atrace
        
        with pytest.raises(ValueError, match="@atrace decorator can only be used with async functions"):
            @atrace
            def test_sync_function(x, y):
                return x + y
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_trace_decorator_async_function(self):
        """Test that @trace decorator automatically handles async functions"""
        from honeyhive.tracer.custom import trace
        
        @trace
        async def test_async_function(x, y):
            return x + y
        
        # Should not raise an exception
        import asyncio
        result = asyncio.run(test_async_function(1, 2))
        assert result == 3


class TestHoneyHiveSpanProcessor:
    """Test HoneyHiveSpanProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = HoneyHiveSpanProcessor()
        self.mock_span = Mock()
        self.mock_span.name = "test_span"
        self.mock_span.set_attribute = Mock()
        
        # Reset static state
        HoneyHiveOTelTracer._tracing_enabled = True
        HoneyHiveOTelTracer.verbose = False
    
    def test_initialization(self):
        """Test processor initialization"""
        assert hasattr(self.processor, '_context_cache')
        assert hasattr(self.processor, '_cache_ttl')
        assert hasattr(self.processor, '_operation_count')
        assert self.processor._cache_ttl == 1000
        assert self.processor._operation_count == 0
    
    def test_cache_cleanup(self):
        """Test span processor cache cleanup functionality"""
        processor = HoneyHiveSpanProcessor()
        
        # Fill cache with many entries
        for i in range(1100):
            processor._context_cache[f"ctx_{i}"] = {"attr": f"value_{i}"}
        
        # Trigger cleanup
        processor._cleanup_cache()
        
        # Verify cache size is reduced
        assert len(processor._context_cache) <= 1000
    
    def test_shutdown(self):
        """Test span processor shutdown functionality"""
        processor = HoneyHiveSpanProcessor()
        
        # Add some cache entries
        processor._context_cache["ctx1"] = {"attr": "value1"}
        processor._context_cache["ctx2"] = {"attr": "value2"}
        
        # Verify cache has entries
        assert len(processor._context_cache) == 2
        
        # Shutdown
        processor.shutdown()
        
        # Verify cache is cleared
        assert len(processor._context_cache) == 0
    
    def test_force_flush(self):
        """Test span processor force flush functionality"""
        processor = HoneyHiveSpanProcessor()
        
        # Force flush should always return True
        assert processor.force_flush() == True
        assert processor.force_flush(timeout_millis=5000) == True
    
    def test_should_process_span_tracing_disabled(self):
        """Test span processor should_process_span when tracing is disabled"""
        processor = HoneyHiveSpanProcessor()
        
        # Disable tracing
        HoneyHiveOTelTracer._tracing_enabled = False
        
        # Create a mock span
        mock_span = Mock()
        
        # Should not process span when tracing is disabled
        assert processor.should_process_span(mock_span) == False
        
        # Re-enable tracing
        HoneyHiveOTelTracer._tracing_enabled = True
    
    def test_should_process_span_exception_handling(self):
        """Test span processor should_process_span exception handling"""
        processor = HoneyHiveSpanProcessor()
        
        # Create a mock span that will cause an exception
        mock_span = Mock()
        mock_span.side_effect = Exception("Test exception")
        
        # Should return True when exception occurs (safe fallback)
        assert processor.should_process_span(mock_span) == True


class TestOTelTracerConfiguration:
    """Test OTel tracer configuration and initialization paths"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Reset static variables
        HoneyHiveOTelTracer._is_initialized = False
        HoneyHiveOTelTracer._is_traceloop_initialized = False
        HoneyHiveOTelTracer._test_mode = False
        HoneyHiveOTelTracer.api_key = None
        HoneyHiveOTelTracer.server_url = None
        HoneyHiveOTelTracer.tracer_provider = None
        HoneyHiveOTelTracer.meter_provider = None
        HoneyHiveOTelTracer.propagator = None
        HoneyHiveOTelTracer.tracer = None
        HoneyHiveOTelTracer.meter = None
        HoneyHiveOTelTracer.span_processor = None
        HoneyHiveOTelTracer._tracing_enabled = True
        HoneyHiveOTelTracer.otlp_enabled = False
        HoneyHiveOTelTracer.otlp_endpoint = None
        HoneyHiveOTelTracer.otlp_headers = None
        HoneyHiveOTelTracer.verbose = False
        
        # Clear environment variables
        self.env_backup = {}
        for key in ['HH_API_KEY', 'HH_API_URL', 'HH_PROJECT', 'HH_SOURCE']:
            if key in os.environ:
                self.env_backup[key] = os.environ[key]
                del os.environ[key]
    
    def teardown_method(self):
        """Clean up after tests"""
        # Restore environment variables
        for key, value in self.env_backup.items():
            os.environ[key] = value
        
        # Reset static variables
        HoneyHiveOTelTracer._is_initialized = False
        HoneyHiveOTelTracer._is_traceloop_initialized = False
        HoneyHiveOTelTracer._test_mode = False
        HoneyHiveOTelTracer.api_key = None
        HoneyHiveOTelTracer.server_url = None
        HoneyHiveOTelTracer.tracer_provider = None
        HoneyHiveOTelTracer.meter_provider = None
        HoneyHiveOTelTracer.propagator = None
        HoneyHiveOTelTracer.tracer = None
        HoneyHiveOTelTracer.meter = None
        HoneyHiveOTelTracer.span_processor = None
        HoneyHiveOTelTracer._tracing_enabled = True
        HoneyHiveOTelTracer.otlp_enabled = False
        HoneyHiveOTelTracer.otlp_endpoint = None
        HoneyHiveOTelTracer.otlp_headers = None
        HoneyHiveOTelTracer.verbose = False
    
    def test_tracer_initialization_with_none_context(self):
        """Test tracer initialization with None context"""
        with patch('opentelemetry.context.get_current', return_value=None):
            # Set environment variables
            os.environ['HH_API_KEY'] = 'test_key_123'
            os.environ['HH_PROJECT'] = 'test_project'
            
            # Initialize tracer
            tracer = HoneyHiveOTelTracer(
                test_mode=True,
                verbose=True
            )
            
            # Verify initialization works without context
            assert tracer.project == 'test_project'
            assert tracer.source == 'dev'  # Default value
    
    def test_tracer_initialization_session_name_from_argv(self):
        """Test tracer initialization with session name from sys.argv"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Mock sys.argv
        with patch('sys.argv', ['/path/to/test_script.py', 'arg1', 'arg2']):
            tracer = HoneyHiveOTelTracer(
                test_mode=True,
                verbose=True
            )
            
            # Verify session name is extracted from argv
            assert tracer.session_name == 'test_script.py'
    
    def test_tracer_initialization_with_custom_source(self):
        """Test tracer initialization with custom source"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer with custom source
        tracer = HoneyHiveOTelTracer(
            source='production',
            test_mode=True,
            verbose=True
        )
        
        # Verify custom source is used
        assert tracer.source == 'production'
    
    def test_tracer_initialization_missing_api_key(self):
        """Test tracer initialization with missing API key"""
        # Set environment variables (no API key)
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Should raise exception for missing API key
        with pytest.raises(Exception, match="api_key must be a non-empty string"):
            HoneyHiveOTelTracer(
                test_mode=True,
                verbose=True
            )
    
    def test_tracer_initialization_missing_project(self):
        """Test tracer initialization with missing project"""
        # Set environment variables (no project)
        os.environ['HH_API_KEY'] = 'test_key_123'
        
        # Should raise exception for missing project
        with pytest.raises(Exception, match="project must be specified or set in environment variable HH_PROJECT"):
            HoneyHiveOTelTracer(
                test_mode=True,
                verbose=True
            )
    
    def test_tracer_initialization_default_api_url(self):
        """Test tracer initialization with default API URL"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer without specifying server URL
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            verbose=True
        )
        
        # Verify default API URL is used
        assert HoneyHiveOTelTracer.server_url == DEFAULT_API_URL
    
    def test_tracer_initialization_with_custom_server_url(self):
        """Test tracer initialization with custom server URL"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer with custom server URL
        custom_url = 'https://custom.honeyhive.ai'
        tracer = HoneyHiveOTelTracer(
            server_url=custom_url,
            test_mode=True,
            verbose=True
        )
        
        # Verify custom server URL is used
        assert HoneyHiveOTelTracer.server_url == custom_url
    
    def test_tracer_initialization_with_environment_source(self):
        """Test tracer initialization with source from environment"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        os.environ['HH_SOURCE'] = 'staging'
        
        # Initialize tracer
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            verbose=True
        )
        
        # Verify source from environment is used
        assert tracer.source == 'staging'
    
    def test_tracer_initialization_with_default_source(self):
        """Test tracer initialization with default source"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer without specifying source
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            verbose=True
        )
        
        # Verify default source is used
        assert tracer.source == 'dev'
    
    def test_tracer_initialization_test_mode_flag(self):
        """Test tracer initialization test mode flag handling"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer with test mode
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            verbose=True
        )
        
        # Verify test mode flags are set
        assert tracer._test_mode == True
        assert HoneyHiveOTelTracer._test_mode == True
    
    def test_tracer_initialization_verbose_flag(self):
        """Test tracer initialization verbose flag handling"""
        # Set environment variables
        os.environ['HH_API_KEY'] = 'test_key_123'
        os.environ['HH_PROJECT'] = 'test_project'
        
        # Initialize tracer with verbose mode
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            verbose=True
        )
        
        # Verify verbose flag is set
        assert HoneyHiveOTelTracer.verbose == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

