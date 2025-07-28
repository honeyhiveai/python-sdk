import pytest
import os
import uuid
import threading
import time
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.custom import trace, atrace, enrich_span
from honeyhive.utils.baggage_dict import BaggageDict
from opentelemetry import context, baggage


class TestHoneyHiveTracerIntegration:
    """Integration tests for HoneyHiveTracer with real-world scenarios"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    @patch('honeyhive.tracer.Traceloop')
    @patch('honeyhive.tracer.HoneyHive')
    @patch('honeyhive.tracer.HoneyHiveTracer._get_git_info')
    def test_complete_initialization_flow(self, mock_git_info, mock_sdk_class, mock_traceloop):
        """Test complete initialization flow with all parameters"""
        # Mock git info
        mock_git_info.return_value = {
            'commit_hash': 'abc123',
            'branch': 'main',
            'repo_url': 'https://github.com/test/repo'
        }
        
        # Mock SDK
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.object.session_id = "test-session-id"
        mock_sdk.session.start_session.return_value = mock_response
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project',
            'HH_SOURCE': 'test_source'
        }):
            tracer = HoneyHiveTracer(
                session_name="test_session",
                inputs={'test': 'input'},
                verbose=True,
                disable_batch=True,
                disable_http_tracing=True,
                tags={'env': 'test', 'version': '1.0'}
            )
            
        assert tracer.session_id == "test-session-id"
        assert tracer.project == "test_project"
        assert tracer.source == "test_source"
        assert tracer.tags == {'env': 'test', 'version': '1.0'}
        assert HoneyHiveTracer.api_key == "test_key"
        assert HoneyHiveTracer.verbose is True

    @patch('honeyhive.tracer.Traceloop')
    @patch('honeyhive.tracer.HoneyHive')
    def test_evaluation_mode_initialization(self, mock_sdk_class, mock_traceloop):
        """Test initialization in evaluation mode"""
        # Mock SDK
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.object.session_id = "eval-session-id"
        mock_sdk.session.start_session.return_value = mock_response
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            tracer = HoneyHiveTracer(
                is_evaluation=True,
                run_id="test-run-id",
                dataset_id="test-dataset-id",
                datapoint_id="test-datapoint-id"
            )
            
        # Check that evaluation properties are in baggage
        baggage_dict = tracer.baggage.get_all_baggage()
        assert baggage_dict['run_id'] == "test-run-id"
        assert baggage_dict['dataset_id'] == "test-dataset-id"
        assert baggage_dict['datapoint_id'] == "test-datapoint-id"

    def test_session_id_initialization(self):
        """Test initialization with existing session_id"""
        valid_uuid = str(uuid.uuid4())
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            tracer = HoneyHiveTracer(session_id=valid_uuid)
            
        assert tracer.session_id == valid_uuid.lower()
        assert tracer.project == "test_project"

    @patch('honeyhive.tracer.HoneyHive')
    def test_link_method_with_baggage(self, mock_sdk_class):
        """Test link method with baggage propagation"""
        # Setup tracer
        with patch('honeyhive.tracer.Traceloop'), patch('honeyhive.tracer.HoneyHiveTracer._get_git_info'):
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.object.session_id = "test-session-id"
            mock_sdk.session.start_session.return_value = mock_response
            
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                tracer = HoneyHiveTracer()
        
        # Test linking with carrier
        carrier = {
            'baggage': 'session_id=parent-session,project=parent-project',
            'traceparent': '00-1234567890abcdef-fedcba0987654321-01'
        }
        
        with patch('honeyhive.tracer.context.attach') as mock_attach:
            token = tracer.link(carrier)
            mock_attach.assert_called_once()

    @patch('honeyhive.tracer.HoneyHive')
    def test_inject_method(self, mock_sdk_class):
        """Test inject method for context propagation"""
        # Setup tracer
        with patch('honeyhive.tracer.Traceloop'), patch('honeyhive.tracer.HoneyHiveTracer._get_git_info'):
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.object.session_id = "test-session-id"
            mock_sdk.session.start_session.return_value = mock_response
            
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                tracer = HoneyHiveTracer()
        
        # Test injection
        carrier = {}
        result = tracer.inject(carrier)
        
        assert result is carrier  # Should return the same carrier object

    @patch('honeyhive.tracer.HoneyHive')
    def test_add_tags_method(self, mock_sdk_class):
        """Test add_tags method functionality"""
        # Setup tracer
        with patch('honeyhive.tracer.Traceloop'), patch('honeyhive.tracer.HoneyHiveTracer._get_git_info'):
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.object.session_id = "test-session-id"
            mock_sdk.session.start_session.return_value = mock_response
            
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                tracer = HoneyHiveTracer(tags={'initial': 'tag'})
        
        # Add more tags
        new_tags = {'env': 'production', 'version': '2.0'}
        
        with patch('honeyhive.tracer.context.attach') as mock_attach:
            tracer.add_tags(new_tags)
            
        # Verify tags were added
        assert tracer.tags['initial'] == 'tag'
        assert tracer.tags['env'] == 'production'
        assert tracer.tags['version'] == '2.0'
        
        # Verify baggage was updated
        baggage_dict = tracer.baggage.get_all_baggage()
        assert baggage_dict['tag_initial'] == 'tag'
        assert baggage_dict['tag_env'] == 'production'
        assert baggage_dict['tag_version'] == '2.0'

    def test_add_tags_invalid_input(self):
        """Test add_tags with invalid input"""
        tracer = Mock()
        tracer.tags = {}
        
        # Should raise ValueError for non-dict input
        with pytest.raises(ValueError, match="Tags must be a dictionary"):
            HoneyHiveTracer.add_tags(tracer, "invalid_tags")

    def test_threading_safety(self):
        """Test thread safety of static variables"""
        results = []
        
        def init_tracer(api_key):
            try:
                with patch('honeyhive.tracer.Traceloop'), patch('honeyhive.tracer.HoneyHive') as mock_sdk_class, patch('honeyhive.tracer.HoneyHiveTracer._get_git_info'):
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.object.session_id = f"session-{api_key}"
                    mock_sdk.session.start_session.return_value = mock_response
                    
                    with patch.dict(os.environ, {
                        'HH_API_KEY': api_key,
                        'HH_PROJECT': 'test_project'
                    }):
                        tracer = HoneyHiveTracer()
                        results.append((api_key, HoneyHiveTracer.api_key))
            except Exception as e:
                results.append((api_key, str(e)))
        
        # Reset static variables
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer._is_traceloop_initialized = False
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=init_tracer, args=(f'key_{i}',))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results - all should have the same API key (first one set)
        assert len(results) == 3
        # The first thread to set the API key wins
        first_set_key = results[0][1]
        for _, api_key in results:
            assert api_key == first_set_key

    @patch('honeyhive.tracer.TracerWrapper')
    def test_flush_with_concurrent_access(self, mock_tracer_wrapper):
        """Test flush method with concurrent access"""
        HoneyHiveTracer._is_traceloop_initialized = True
        mock_wrapper = Mock()
        mock_tracer_wrapper.return_value = mock_wrapper
        
        results = []
        
        def call_flush():
            HoneyHiveTracer.flush()
            results.append("flushed")
        
        # Create multiple threads calling flush
        threads = []
        for i in range(5):
            thread = threading.Thread(target=call_flush)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At least one flush should have been called
        assert len(results) >= 1
        mock_wrapper.flush.assert_called()

    @patch('honeyhive.tracer.HoneyHive')
    def test_context_propagation_with_decorators(self, mock_sdk_class):
        """Test context propagation through decorated functions"""
        # Setup tracer
        with patch('honeyhive.tracer.Traceloop'), patch('honeyhive.tracer.HoneyHiveTracer._get_git_info'):
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.object.session_id = "test-session-id"
            mock_sdk.session.start_session.return_value = mock_response
            
            with patch.dict(os.environ, {
                'HH_API_KEY': 'test_key',
                'HH_PROJECT': 'test_project'
            }):
                tracer = HoneyHiveTracer()
        
        # Test nested traced functions
        @trace(event_type="tool", tags={'tool': 'outer'})
        def outer_function(x):
            enrich_span(metadata={'step': 'outer'})
            return inner_function(x * 2)
        
        @trace(event_type="chain", tags={'tool': 'inner'})
        def inner_function(x):
            enrich_span(metadata={'step': 'inner'})
            return x + 1
        
        with patch('honeyhive.tracer.custom.instrumentor._tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = outer_function(5)
            
            assert result == 11  # (5 * 2) + 1
            # Both functions should create spans
            assert mock_tracer.start_as_current_span.call_count == 2

    def test_legacy_init_method(self):
        """Test legacy init static method"""
        with patch('honeyhive.tracer.HoneyHiveTracer.__init__') as mock_init:
            mock_init.return_value = None
            
            HoneyHiveTracer.init(
                api_key='test_key',
                project='test_project'
            )
            
            mock_init.assert_called_once_with(
                api_key='test_key',
                project='test_project'
            )

    @patch('subprocess.run')
    def test_git_info_with_uncommitted_changes(self, mock_run):
        """Test git info with uncommitted changes"""
        mock_run.side_effect = [
            Mock(returncode=0),  # is-inside-work-tree
            Mock(stdout="abc123\n", returncode=0),  # rev-parse HEAD
            Mock(stdout="main\n", returncode=0),  # rev-parse --abbrev-ref HEAD
            Mock(stdout="https://github.com/user/repo\n", returncode=0),  # remote origin url
            Mock(stdout="M file1.py\nA file2.py\n", returncode=0),  # status --porcelain (has changes)
            Mock(stdout="/path/to/repo\n", returncode=0),  # show-toplevel
        ]
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
        
        assert git_info['uncommitted_changes'] is True

    @patch('subprocess.run')
    @patch('sys.modules')
    def test_git_info_with_main_module_path(self, mock_modules, mock_run):
        """Test git info with main module relative path"""
        # Mock main module
        mock_main = Mock()
        mock_main.__file__ = '/path/to/repo/src/main.py'
        mock_modules.get.return_value = mock_main
        
        mock_run.side_effect = [
            Mock(returncode=0),  # is-inside-work-tree
            Mock(stdout="abc123\n", returncode=0),  # rev-parse HEAD
            Mock(stdout="main\n", returncode=0),  # rev-parse --abbrev-ref HEAD
            Mock(stdout="https://github.com/user/repo\n", returncode=0),  # remote origin url
            Mock(stdout="", returncode=0),  # status --porcelain
            Mock(stdout="/path/to/repo\n", returncode=0),  # show-toplevel
        ]
        
        with patch('os.path.abspath') as mock_abspath, \
             patch('os.path.relpath') as mock_relpath, \
             patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            
            mock_abspath.return_value = '/path/to/repo/src/main.py'
            mock_relpath.return_value = 'src/main.py'
            
            git_info = HoneyHiveTracer._get_git_info()
        
        assert git_info['relative_path'] == 'src/main.py'

    def test_sanitize_carrier_case_insensitive(self):
        """Test carrier sanitization with different cases"""
        carrier = {
            'BAGGAGE': 'session_id=123',
            'traceparent': '00-trace-span-01',
            'Baggage': 'should_not_override'  # Should be ignored since BAGGAGE already exists
        }
        getter = BaggageDict.DefaultGetter
        
        result = HoneyHiveTracer._sanitize_carrier(carrier, getter)
        
        assert 'baggage' in result
        assert 'traceparent' in result
        assert result['baggage'] == ['session_id=123']  # Should use BAGGAGE value
        assert result['traceparent'] == ['00-trace-span-01']