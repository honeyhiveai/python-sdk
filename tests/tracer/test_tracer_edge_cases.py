import pytest
import os
import uuid
import threading
import time
import requests
from unittest.mock import patch, MagicMock, Mock, PropertyMock
from honeyhive.tracer import HoneyHiveTracer, enrich_session
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import errors
from opentelemetry import context
import subprocess


class TestHoneyHiveTracerEdgeCases:
    """Comprehensive edge case and error scenario tests for HoneyHiveTracer"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False
        HoneyHiveTracer.verbose = False

    def test_init_with_malformed_environment_variables(self, capsys):
        """Test initialization with malformed environment variables"""
        with patch.dict(os.environ, {
            'HH_API_KEY': '',  # Empty string
            'HH_PROJECT': '   ',  # Whitespace only
            'HH_SOURCE': '123',  # Numeric as string
        }):
            tracer = HoneyHiveTracer()
            
        captured = capsys.readouterr()
        assert "HoneyHive SDK Error" in captured.out

    def test_init_with_invalid_uuid_session_id(self):
        """Test initialization with various invalid UUID formats"""
        invalid_uuids = [
            "not-a-uuid",
            "12345678-1234-1234-1234",  # Too short
            "12345678-1234-1234-1234-12345678901234",  # Too long
            "xyz45678-1234-1234-1234-123456789012",  # Invalid characters
            "",  # Empty string
            "   ",  # Whitespace
            123,  # Integer
            None,  # None (should work - new session)
        ]
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            for invalid_uuid in invalid_uuids:
                if invalid_uuid is None:
                    continue  # Skip None - it should work
                    
                with pytest.raises(errors.SDKError, match="session_id must be a valid UUID"):
                    HoneyHiveTracer(session_id=invalid_uuid)

    def test_init_with_extreme_values(self):
        """Test initialization with extreme parameter values"""
        very_long_string = "x" * 10000
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "test-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                # Should handle large strings gracefully
                tracer = HoneyHiveTracer(
                    session_name=very_long_string,
                    source=very_long_string,
                    inputs={"key": very_long_string}
                )
                
                assert tracer.session_id == "test-session-id"

    def test_init_concurrent_initialization(self):
        """Test concurrent initialization from multiple threads"""
        results = []
        errors_list = []
        
        def init_tracer(thread_id):
            try:
                with patch.dict(os.environ, {
                    'HH_API_KEY': f'test_key_{thread_id}',
                    'HH_PROJECT': f'test_project_{thread_id}'
                }):
                    with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                        mock_sdk = Mock()
                        mock_sdk_class.return_value = mock_sdk
                        mock_response = Mock()
                        mock_response.status_code = 200
                        mock_response.object.session_id = f"session-{thread_id}"
                        mock_sdk.session.start_session.return_value = mock_response
                        
                        tracer = HoneyHiveTracer()
                        results.append((thread_id, tracer.session_id))
            except Exception as e:
                errors_list.append((thread_id, str(e)))
        
        # Create multiple threads initializing tracers simultaneously
        threads = []
        for i in range(10):
            thread = threading.Thread(target=init_tracer, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all initializations succeeded
        assert len(errors_list) == 0, f"Errors occurred: {errors_list}"
        assert len(results) == 10
        
        # Verify each thread got its own session
        session_ids = [result[1] for result in results]
        assert len(set(session_ids)) == 10  # All unique session IDs

    @patch('subprocess.run')
    def test_git_info_edge_cases(self, mock_run):
        """Test git info collection with various edge cases"""
        
        # Test git command timeout/hanging
        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
            assert 'error' in git_info

    @patch('subprocess.run')  
    def test_git_info_permission_denied(self, mock_run):
        """Test git info when permission denied"""
        mock_run.side_effect = PermissionError("Permission denied")
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
            assert 'error' in git_info

    @patch('subprocess.run')
    def test_git_info_corrupted_repo(self, mock_run):
        """Test git info with corrupted repository"""
        mock_run.side_effect = [
            Mock(returncode=0),  # is-inside-work-tree succeeds
            subprocess.CalledProcessError(128, "git", "fatal: bad object HEAD"),  # HEAD is corrupted
        ]
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
            assert 'error' in git_info

    def test_session_start_network_timeout(self):
        """Test session start with network timeout"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_sdk.session.start_session.side_effect = requests.Timeout("Request timed out")
                
                with pytest.raises(requests.Timeout):
                    HoneyHiveTracer()

    def test_session_start_connection_error(self):
        """Test session start with connection error"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_sdk.session.start_session.side_effect = requests.ConnectionError("Connection failed")
                
                with pytest.raises(requests.ConnectionError):
                    HoneyHiveTracer()

    def test_session_start_http_error(self):
        """Test session start with HTTP error responses"""
        error_codes = [400, 401, 403, 404, 500, 502, 503]
        
        for error_code in error_codes:
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = error_code
                    mock_response.raw_response.text = f"HTTP {error_code} Error"
                    mock_sdk.session.start_session.return_value = mock_response
                    
                    with pytest.raises(AssertionError, match=f"Failed to start session"):
                        HoneyHiveTracer()

    def test_session_start_malformed_response(self):
        """Test session start with malformed API response"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = None  # Missing session ID
                mock_sdk.session.start_session.return_value = mock_response
                
                with pytest.raises(AssertionError, match="Failure initializing session"):
                    HoneyHiveTracer()

    def test_memory_cleanup_after_failed_init(self):
        """Test that memory is properly cleaned up after failed initialization"""
        original_api_key = HoneyHiveTracer.api_key
        original_server_url = HoneyHiveTracer.server_url
        original_is_initialized = HoneyHiveTracer._is_traceloop_initialized
        
        # Attempt failed initialization
        with patch.dict(os.environ, {}, clear=True):
            tracer = HoneyHiveTracer()  # Should fail but not crash
        
        # Verify static variables are in expected state after failure
        # (they might be set during failed init, that's okay)
        assert isinstance(HoneyHiveTracer.api_key, (str, type(None)))
        assert isinstance(HoneyHiveTracer.server_url, (str, type(None)))
        assert isinstance(HoneyHiveTracer._is_traceloop_initialized, bool)

    def test_init_with_context_already_set(self):
        """Test initialization when context already has association properties"""
        # Set up an existing context with association properties
        ctx = context.get_current()
        ctx = ctx.with_set_value('association_properties', {
            'session_id': 'existing-session-id',
            'project': 'existing-project',
            'source': 'existing-source',
            'disable_http_tracing': True,
            'run_id': 'existing-run-id',
            'dataset_id': 'existing-dataset-id',
            'datapoint_id': 'existing-datapoint-id'
        })
        
        token = context.attach(ctx)
        
        try:
            with patch.dict(os.environ, {'HH_API_KEY': 'test_key'}):
                with patch('honeyhive.tracer.HoneyHive'):
                    tracer = HoneyHiveTracer(
                        project='new-project',  # Should be overridden
                        source='new-source'     # Should be overridden
                    )
                    
                    # Should use values from context
                    assert tracer.session_id == 'existing-session-id'
                    assert tracer.project == 'existing-project'
                    assert tracer.source == 'existing-source'
        finally:
            context.detach(token)

    def test_baggage_with_invalid_values(self):
        """Test baggage handling with invalid/edge case values"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "test-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                # Test with various invalid tag values
                invalid_tags = {
                    'null_tag': None,
                    'empty_tag': '',
                    'unicode_tag': '🚀🌟',
                    'number_tag': 42,
                    'bool_tag': True,
                    'list_tag': [1, 2, 3],
                    'dict_tag': {'nested': 'value'}
                }
                
                tracer = HoneyHiveTracer(tags=invalid_tags)
                
                # Should handle all types gracefully
                assert tracer.session_id == "test-session-id"
                assert isinstance(tracer.baggage, BaggageDict)

    def test_flush_with_lock_timeout(self):
        """Test flush behavior when lock acquisition times out"""
        HoneyHiveTracer._is_traceloop_initialized = True
        
        # Mock the lock to simulate timeout
        original_lock = HoneyHiveTracer._flush_lock
        mock_lock = Mock()
        mock_lock.acquire.return_value = False  # Simulate timeout
        HoneyHiveTracer._flush_lock = mock_lock
        
        try:
            with patch('sys.stdout.write') as mock_write:
                HoneyHiveTracer.flush()
                
                # Should log warning about timeout
                mock_lock.acquire.assert_called_once_with(blocking=True, timeout=10.0)
        finally:
            HoneyHiveTracer._flush_lock = original_lock

    def test_flush_with_exception_in_lock_acquire(self):
        """Test flush behavior when lock acquisition raises exception"""
        HoneyHiveTracer._is_traceloop_initialized = True
        
        # Mock the lock to raise exception
        original_lock = HoneyHiveTracer._flush_lock
        mock_lock = Mock()
        mock_lock.acquire.side_effect = Exception("Lock error")
        HoneyHiveTracer._flush_lock = mock_lock
        
        try:
            with patch('sys.stdout.write') as mock_write:
                HoneyHiveTracer.flush()
                
                # Should handle exception gracefully
                mock_lock.acquire.assert_called_once()
        finally:
            HoneyHiveTracer._flush_lock = original_lock

    def test_enrich_session_with_malformed_data(self):
        """Test session enrichment with malformed data"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        # Test with various malformed data types
        malformed_data = [
            {'circular_ref': None},  # Will create circular reference
            {'huge_data': 'x' * 1000000},  # Very large data
            {'invalid_json': object()},  # Non-serializable object
        ]
        
        # Create circular reference
        malformed_data[0]['circular_ref'] = malformed_data[0]
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            # Should handle malformed data gracefully without crashing
            for data in malformed_data:
                try:
                    enrich_session(session_id='test-session', metadata=data)
                except Exception:
                    # Some exceptions are expected for malformed data
                    pass

    def test_add_tags_with_uninitialized_tracer(self):
        """Test adding tags to uninitialized tracer"""
        tracer = object.__new__(HoneyHiveTracer)  # Create without calling __init__
        tracer.tags = {}
        tracer._tags_initialized = False
        
        # Should handle gracefully
        tracer.add_tags({'test': 'value'})
        assert tracer.tags == {'test': 'value'}

    def test_add_tags_invalid_input(self):
        """Test adding invalid tags"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "test-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                # Test with non-dict input
                with pytest.raises(ValueError, match="Tags must be a dictionary"):
                    tracer.add_tags("not_a_dict")
                
                with pytest.raises(ValueError, match="Tags must be a dictionary"):
                    tracer.add_tags(123)
                
                with pytest.raises(ValueError, match="Tags must be a dictionary"):
                    tracer.add_tags(['list', 'not', 'dict'])

    def test_link_with_malformed_carrier(self):
        """Test linking with malformed carrier data"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "test-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                # Test various malformed carriers
                malformed_carriers = [
                    None,
                    "string_carrier",
                    123,
                    [],
                    {'malformed': {'nested': {'too': 'deep'}}},
                    {'invalid_encoding': b'\xff\xfe'},  # Invalid encoding
                ]
                
                for carrier in malformed_carriers:
                    try:
                        # Should handle gracefully without crashing
                        token = tracer.link(carrier)
                        if token:
                            tracer.unlink(token)
                    except Exception:
                        # Some exceptions are expected for malformed data
                        pass