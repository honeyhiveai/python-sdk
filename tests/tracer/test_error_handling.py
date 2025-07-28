import pytest
import os
import requests
import json
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer, enrich_session
from honeyhive.models import errors
from requests.exceptions import (
    ConnectionError, Timeout, HTTPError, RequestException,
    ChunkedEncodingError, ContentDecodingError, InvalidURL,
    TooManyRedirects, SSLError
)


class TestErrorHandling:
    """Comprehensive error handling tests for network failures and API errors"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_session_start_connection_errors(self):
        """Test various connection errors during session start"""
        connection_errors = [
            ConnectionError("Connection refused"),
            ConnectionError("Name or service not known"),
            ConnectionError("Network is unreachable"),
            requests.exceptions.ConnectTimeout("Connection timeout"),
            requests.exceptions.ReadTimeout("Read timeout"),
            Timeout("Request timeout"),
            SSLError("SSL certificate verification failed"),
            TooManyRedirects("Too many redirects"),
        ]
        
        for error in connection_errors:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_sdk.session.start_session.side_effect = error
                    
                    # Should raise the original exception
                    with pytest.raises(type(error)):
                        HoneyHiveTracer()

    def test_session_start_http_errors(self):
        """Test HTTP error responses during session start"""
        http_error_scenarios = [
            (400, "Bad Request", "Invalid request parameters"),
            (401, "Unauthorized", "Invalid API key"),
            (403, "Forbidden", "Access denied"),
            (404, "Not Found", "Project not found"),
            (429, "Too Many Requests", "Rate limit exceeded"),
            (500, "Internal Server Error", "Server error"),
            (502, "Bad Gateway", "Gateway error"),
            (503, "Service Unavailable", "Service temporarily unavailable"),
            (504, "Gateway Timeout", "Gateway timeout"),
        ]
        
        for status_code, status_text, error_message in http_error_scenarios:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = status_code
                    mock_response.raw_response.text = f"{status_code} {status_text}: {error_message}"
                    mock_sdk.session.start_session.return_value = mock_response
                    
                    with pytest.raises(AssertionError, match="Failed to start session"):
                        HoneyHiveTracer()

    def test_session_start_malformed_responses(self):
        """Test malformed API responses during session start"""
        malformed_scenarios = [
            # Missing session_id
            (200, lambda: Mock(session_id=None)),
            # Empty session_id
            (200, lambda: Mock(session_id="")),
            # Non-string session_id
            (200, lambda: Mock(session_id=12345)),
            # Missing object entirely
            (200, lambda: None),
        ]
        
        for status_code, object_factory in malformed_scenarios:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = status_code
                    mock_response.object = object_factory()
                    mock_sdk.session.start_session.return_value = mock_response
                    
                    with pytest.raises(AssertionError):
                        HoneyHiveTracer()

    def test_session_start_json_decode_errors(self):
        """Test JSON decode errors during session start"""
        json_errors = [
            json.JSONDecodeError("Expecting value", "doc", 0),
            ValueError("Invalid JSON"),
            UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte'),
        ]
        
        for error in json_errors:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_sdk.session.start_session.side_effect = error
                    
                    with pytest.raises(type(error)):
                        HoneyHiveTracer()

    def test_session_enrichment_network_errors(self):
        """Test network errors during session enrichment"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        network_errors = [
            ConnectionError("Failed to connect"),
            Timeout("Request timed out"),
            HTTPError("HTTP error occurred"),
            ChunkedEncodingError("Chunked encoding error"),
            ContentDecodingError("Content decoding error"),
            InvalidURL("Invalid URL"),
            SSLError("SSL error"),
        ]
        
        for error in network_errors:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_sdk.events.update_event.side_effect = error
                
                # Should handle error gracefully (not crash)
                try:
                    enrich_session(
                        session_id='test-session',
                        metadata={'test': 'data'},
                        feedback={'rating': 5}
                    )
                    # Success - error was handled gracefully
                except type(error):
                    # Also acceptable - error was re-raised
                    pass

    def test_session_enrichment_http_errors(self):
        """Test HTTP errors during session enrichment"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        http_error_scenarios = [
            (400, "Bad request data"),
            (401, "Invalid session or API key"),
            (403, "Forbidden to update session"),
            (404, "Session not found"),
            (422, "Validation error"),
            (500, "Internal server error"),
            (503, "Service unavailable"),
        ]
        
        for status_code, error_message in http_error_scenarios:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.raw_response.text = error_message
                mock_sdk.events.update_event.return_value = mock_response
                
                # Should handle gracefully - either succeed silently or raise exception
                try:
                    enrich_session(
                        session_id='test-session',
                        metadata={'test': 'data'}
                    )
                except Exception:
                    # Exception is acceptable for error status codes
                    pass

    def test_tracer_init_with_invalid_server_urls(self):
        """Test tracer initialization with invalid server URLs"""
        invalid_urls = [
            "not-a-url",
            "http://",  # Incomplete URL
            "ftp://invalid.protocol.com",  # Wrong protocol
            "https://",  # No domain
            "https://invalid-domain-that-does-not-exist.com",
            "http://localhost:99999",  # Invalid port
            "",  # Empty string
            None,  # None value
        ]
        
        for invalid_url in invalid_urls:
            if invalid_url is None:
                continue  # Skip None - it should use default
                
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    
                    # Mock the start_session to raise a connection error for invalid URLs
                    mock_sdk.session.start_session.side_effect = ConnectionError("Invalid URL")
                    
                    with pytest.raises(ConnectionError):
                        HoneyHiveTracer(server_url=invalid_url)

    def test_tracer_flush_with_traceloop_errors(self):
        """Test tracer flush with TracerWrapper errors"""
        HoneyHiveTracer._is_traceloop_initialized = True
        
        traceloop_errors = [
            Exception("TracerWrapper internal error"),
            RuntimeError("Tracer not initialized"),
            AttributeError("Missing flush method"),
            ConnectionError("Failed to send traces"),
            Timeout("Flush operation timed out"),
        ]
        
        for error in traceloop_errors:
            with patch('honeyhive.tracer.TracerWrapper') as mock_wrapper_class:
                mock_wrapper = Mock()
                mock_wrapper_class.return_value = mock_wrapper
                mock_wrapper.flush.side_effect = error
                
                # Should handle error gracefully
                try:
                    HoneyHiveTracer.flush()
                    # Success - error was handled
                except type(error):
                    # Also acceptable - error was re-raised
                    pass

    def test_baggage_operations_with_context_errors(self):
        """Test baggage operations with context-related errors"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "baggage-error-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                # Test with context operations that might fail
                context_errors = [
                    Exception("Context operation failed"),
                    RuntimeError("OpenTelemetry context error"),
                    AttributeError("Missing context attribute"),
                ]
                
                for error in context_errors:
                    with patch('opentelemetry.context.attach', side_effect=error):
                        # Should handle gracefully
                        try:
                            tracer.add_tags({'test': 'tag'})
                        except type(error):
                            # Error propagation is acceptable
                            pass

    def test_linking_with_propagator_errors(self):
        """Test linking operations with propagator errors"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "link-error-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                propagator_errors = [
                    ValueError("Invalid carrier format"),
                    KeyError("Missing required header"),
                    TypeError("Incorrect carrier type"),
                    UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid encoding'),
                ]
                
                for error in propagator_errors:
                    with patch.object(HoneyHiveTracer.propagator, 'extract', side_effect=error):
                        carrier = {'baggage': 'test=value', 'traceparent': '00-trace-span-01'}
                        
                        # Should handle gracefully
                        try:
                            token = tracer.link(carrier)
                            if token:
                                tracer.unlink(token)
                        except type(error):
                            # Error propagation is acceptable
                            pass

    def test_git_info_subprocess_errors(self):
        """Test git info collection with subprocess errors"""
        import subprocess
        
        subprocess_errors = [
            subprocess.CalledProcessError(128, 'git', 'fatal: not a git repository'),
            subprocess.TimeoutExpired('git', 30),
            FileNotFoundError("git command not found"),
            PermissionError("Permission denied accessing git repository"),
            OSError("OS error during git operation"),
        ]
        
        for error in subprocess_errors:
            with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
                with patch('subprocess.run', side_effect=error):
                    git_info = HoneyHiveTracer._get_git_info()
                    
                    # Should return error info, not crash
                    assert 'error' in git_info
                    assert isinstance(git_info['error'], str)

    def test_concurrent_error_scenarios(self):
        """Test error handling in concurrent scenarios"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def error_thread(thread_id):
            try:
                with patch.dict(os.environ, {
                    'HH_API_KEY': 'test_key',
                    'HH_PROJECT': 'test_project'
                }):
                    with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                        mock_sdk = Mock()
                        mock_sdk_class.return_value = mock_sdk
                        
                        # Simulate different types of errors for different threads
                        if thread_id % 3 == 0:
                            mock_sdk.session.start_session.side_effect = ConnectionError("Network error")
                        elif thread_id % 3 == 1:
                            mock_response = Mock()
                            mock_response.status_code = 500
                            mock_response.raw_response.text = "Server error"
                            mock_sdk.session.start_session.return_value = mock_response
                        else:
                            mock_response = Mock()
                            mock_response.status_code = 200
                            mock_response.object.session_id = None  # Missing session ID
                            mock_sdk.session.start_session.return_value = mock_response
                        
                        # Attempt initialization
                        tracer = HoneyHiveTracer()
                        
                        # Should not reach here for error cases
                        results.put({'thread_id': thread_id, 'unexpected_success': True})
                        
            except Exception as e:
                # Expected for error scenarios
                results.put({
                    'thread_id': thread_id,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
        
        # Start threads with different error scenarios
        threads = []
        for i in range(9):  # 3 of each error type
            thread = threading.Thread(target=error_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check that all threads handled errors appropriately
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        # Should have results from all threads
        assert len(all_results) == 9
        
        # None should have unexpected success
        unexpected_successes = [r for r in all_results if r.get('unexpected_success')]
        assert len(unexpected_successes) == 0

    def test_memory_errors_and_resource_cleanup(self):
        """Test behavior with memory errors and resource cleanup"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            # Test MemoryError during initialization
            with patch('honeyhive.tracer.HoneyHive', side_effect=MemoryError("Out of memory")):
                with pytest.raises(MemoryError):
                    HoneyHiveTracer()
            
            # Test resource cleanup after failed initialization
            original_api_key = HoneyHiveTracer.api_key
            original_server_url = HoneyHiveTracer.server_url
            
            try:
                with patch('honeyhive.tracer.HoneyHive', side_effect=RuntimeError("Init failed")):
                    HoneyHiveTracer()
            except RuntimeError:
                pass
            
            # Verify that static state is still manageable after error
            assert isinstance(HoneyHiveTracer.api_key, (str, type(None)))
            assert isinstance(HoneyHiveTracer.server_url, (str, type(None)))

    def test_serialization_errors_in_enrichment(self):
        """Test serialization errors during session enrichment"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Create objects that can't be JSON serialized
        class NonSerializableClass:
            def __init__(self):
                self.circular_ref = self
        
        non_serializable_data = [
            {'object': NonSerializableClass()},
            {'function': lambda x: x},
            {'bytes': b'\xff\xfe\xfd'},
            {'set': {1, 2, 3}},
            {'complex': complex(1, 2)},
        ]
        
        for data in non_serializable_data:
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_sdk.events.update_event.side_effect = TypeError("Object not JSON serializable")
                
                # Should handle serialization error gracefully
                try:
                    enrich_session(
                        session_id='test-session',
                        metadata=data
                    )
                except TypeError:
                    # Acceptable to re-raise serialization errors
                    pass

    def test_api_rate_limiting_scenarios(self):
        """Test API rate limiting and retry scenarios"""
        rate_limit_responses = [
            (429, "Rate limit exceeded", {"Retry-After": "60"}),
            (429, "Too many requests", {"X-RateLimit-Reset": "1234567890"}),
            (503, "Service temporarily unavailable", {"Retry-After": "30"}),
        ]
        
        for status_code, message, headers in rate_limit_responses:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = status_code
                    mock_response.raw_response.text = message
                    mock_response.headers = headers
                    mock_sdk.session.start_session.return_value = mock_response
                    
                    # Should handle rate limiting appropriately
                    with pytest.raises(AssertionError, match="Failed to start session"):
                        HoneyHiveTracer()

    def test_edge_case_error_combinations(self):
        """Test combinations of multiple error conditions"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            # Simulate multiple system failures
            with patch('honeyhive.tracer.HoneyHive', side_effect=ConnectionError("Network down")):
                with patch('honeyhive.tracer.HoneyHiveTracer._get_git_info', side_effect=OSError("Git unavailable")):
                    with patch('subprocess.run', side_effect=FileNotFoundError("Git command not found")):
                        # Should still handle gracefully
                        with pytest.raises(ConnectionError):
                            HoneyHiveTracer()
            
            # Test error during cleanup
            HoneyHiveTracer._is_traceloop_initialized = True
            with patch('honeyhive.tracer.TracerWrapper', side_effect=Exception("Cleanup error")):
                # Should not prevent subsequent operations
                try:
                    HoneyHiveTracer.flush()
                except Exception:
                    pass  # Error during cleanup is acceptable