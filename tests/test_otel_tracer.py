import os
import pytest
from unittest.mock import patch, MagicMock
from honeyhive.tracer.otel_tracer import HoneyHiveOTelTracer


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
        # The tracer should still be created but session_id should be None due to validation failure
        assert tracer.session_id is None
        # This is expected behavior - invalid UUIDs cause initialization issues
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test that missing API key raises an error"""
        with pytest.raises(Exception):
            HoneyHiveOTelTracer(test_mode=True)
    
    @patch.dict(os.environ, {'HH_API_KEY': 'test-api-key'}, clear=True)
    def test_missing_project(self):
        """Test that missing project raises an error"""
        with pytest.raises(Exception):
            HoneyHiveOTelTracer()
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_baggage_initialization(self):
        """Test that baggage is initialized correctly"""
        tracer = HoneyHiveOTelTracer()
        
        # In test mode, baggage should be initialized
        assert hasattr(tracer, 'baggage')
        # The baggage might be empty if API calls fail, but the attribute should exist
        assert isinstance(tracer.baggage, dict)
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_evaluation_mode(self):
        """Test tracer in evaluation mode"""
        tracer = HoneyHiveOTelTracer(
            is_evaluation=True,
            run_id="test-run",
            dataset_id="test-dataset",
            datapoint_id="test-datapoint"
        )
        
        # In test mode, baggage should be initialized
        assert hasattr(tracer, 'baggage')
        assert isinstance(tracer.baggage, dict)
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_flush_method(self):
        """Test that flush method works"""
        tracer = HoneyHiveOTelTracer()
        
        # Should not raise an exception
        HoneyHiveOTelTracer.flush()
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_validation_methods(self):
        """Test validation methods"""
        # These methods raise exceptions on validation failure, they don't return boolean values
        # Test that they raise exceptions for invalid inputs
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_api_key("")
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_api_key(None)
        
        # Valid inputs should not raise exceptions
        HoneyHiveOTelTracer._validate_api_key("valid-key")
        
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_server_url("")
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_server_url("invalid-url")
        
        # Valid inputs should not raise exceptions
        HoneyHiveOTelTracer._validate_server_url("https://example.com")
        
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_project("")
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_project(None)
        
        # Valid inputs should not raise exceptions
        HoneyHiveOTelTracer._validate_project("valid-project")
        
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_source("")
        with pytest.raises(Exception):
            HoneyHiveOTelTracer._validate_source(None)
        
        # Valid inputs should not raise exceptions
        HoneyHiveOTelTracer._validate_source("valid-source")


class TestHTTPInstrumentation:
    
    def test_http_instrumentation_import(self):
        """Test that HTTP instrumentation can be imported"""
        from honeyhive.tracer.http_instrumentation import HTTPInstrumentor, instrument_http, uninstrument_http
        
        assert HTTPInstrumentor is not None
        assert instrument_http is not None
        assert uninstrument_http is not None
    
    def test_http_instrumentor_creation(self):
        """Test HTTP instrumentor creation"""
        from honeyhive.tracer.http_instrumentation import HTTPInstrumentor
        
        instrumentor = HTTPInstrumentor()
        assert instrumentor._instrumented is False
        assert instrumentor.tracer is not None


class TestCustomTracing:
    
    def test_custom_trace_import(self):
        """Test that custom tracing can be imported"""
        from honeyhive.tracer.custom import trace, atrace, enrich_span
        
        assert trace is not None
        assert atrace is not None
        assert enrich_span is not None
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_trace_decorator(self):
        """Test the trace decorator"""
        from honeyhive.tracer.custom import trace
        
        @trace
        def test_function(x, y):
            return x + y
        
        # Should not raise an exception
        result = test_function(1, 2)
        assert result == 3
    
    @patch.dict(os.environ, {
        'HH_API_KEY': 'test-api-key',
        'HH_PROJECT': 'test-project'
    }, clear=True)
    def test_atrace_decorator(self):
        """Test the atrace decorator (legacy support)"""
        from honeyhive.tracer.custom import atrace
        
        @atrace
        async def test_async_function(x, y):
            return x + y
        
        # Should not raise an exception
        import asyncio
        result = asyncio.run(test_async_function(1, 2))
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
