import pytest
import os
import uuid
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer, enrich_session
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import errors
from opentelemetry import context


class TestHoneyHiveTracer:
    """Test suite for HoneyHiveTracer initialization and static methods"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_validate_api_key(self):
        """Test API key validation"""
        assert HoneyHiveTracer._validate_api_key("valid_key") is True
        assert HoneyHiveTracer._validate_api_key("") is False
        assert HoneyHiveTracer._validate_api_key(None) is False
        assert HoneyHiveTracer._validate_api_key(123) is False

    def test_validate_server_url(self):
        """Test server URL validation"""
        assert HoneyHiveTracer._validate_server_url("https://api.honeyhive.ai") is True
        assert HoneyHiveTracer._validate_server_url("http://localhost:8080") is True
        assert HoneyHiveTracer._validate_server_url("") is False
        assert HoneyHiveTracer._validate_server_url(None) is False
        assert HoneyHiveTracer._validate_server_url(123) is False

    def test_validate_project(self):
        """Test project validation"""
        assert HoneyHiveTracer._validate_project("test_project") is True
        assert HoneyHiveTracer._validate_project("") is False
        assert HoneyHiveTracer._validate_project(None) is False
        assert HoneyHiveTracer._validate_project(123) is False

    def test_validate_source(self):
        """Test source validation"""
        assert HoneyHiveTracer._validate_source("dev") is True
        assert HoneyHiveTracer._validate_source("production") is True
        assert HoneyHiveTracer._validate_source("") is False
        assert HoneyHiveTracer._validate_source(None) is False
        assert HoneyHiveTracer._validate_source(123) is False

    def test_get_validated_api_key_from_env(self):
        """Test getting validated API key from environment"""
        with patch.dict(os.environ, {'HH_API_KEY': 'test_key'}):
            assert HoneyHiveTracer._get_validated_api_key() == 'test_key'

    def test_get_validated_api_key_explicit(self):
        """Test getting validated API key explicitly passed"""
        assert HoneyHiveTracer._get_validated_api_key("explicit_key") == "explicit_key"

    def test_get_validated_api_key_missing(self):
        """Test error when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="api_key must be specified"):
                HoneyHiveTracer._get_validated_api_key()

    def test_get_validated_server_url_default(self):
        """Test getting default server URL"""
        with patch.dict(os.environ, {}, clear=True):
            url = HoneyHiveTracer._get_validated_server_url()
            assert url == 'https://api.honeyhive.ai'

    def test_get_validated_server_url_from_env(self):
        """Test getting server URL from environment"""
        with patch.dict(os.environ, {'HH_API_URL': 'https://custom.api.com'}):
            url = HoneyHiveTracer._get_validated_server_url()
            assert url == 'https://custom.api.com'

    def test_get_validated_project_from_env(self):
        """Test getting project from environment"""
        with patch.dict(os.environ, {'HH_PROJECT': 'test_project'}):
            assert HoneyHiveTracer._get_validated_project() == 'test_project'

    def test_get_validated_project_missing(self):
        """Test error when project is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception, match="project must be specified"):
                HoneyHiveTracer._get_validated_project()

    def test_get_validated_source_default(self):
        """Test getting default source"""
        with patch.dict(os.environ, {}, clear=True):
            assert HoneyHiveTracer._get_validated_source() == 'dev'

    def test_get_validated_source_from_env(self):
        """Test getting source from environment"""
        with patch.dict(os.environ, {'HH_SOURCE': 'production'}):
            assert HoneyHiveTracer._get_validated_source() == 'production'

    @patch('subprocess.run')
    def test_get_git_info_success(self, mock_run):
        """Test successful git info retrieval"""
        # Mock subprocess calls
        mock_run.side_effect = [
            Mock(returncode=0),  # is-inside-work-tree
            Mock(stdout="abc123\n", returncode=0),  # rev-parse HEAD
            Mock(stdout="main\n", returncode=0),  # rev-parse --abbrev-ref HEAD
            Mock(stdout="https://github.com/user/repo\n", returncode=0),  # remote origin url
            Mock(stdout="", returncode=0),  # status --porcelain
            Mock(stdout="/path/to/repo\n", returncode=0),  # show-toplevel
        ]
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
            
        assert git_info['commit_hash'] == 'abc123'
        assert git_info['branch'] == 'main'
        assert git_info['repo_url'] == 'https://github.com/user/repo'
        assert git_info['uncommitted_changes'] is False

    @patch('subprocess.run')
    def test_get_git_info_not_git_repo(self, mock_run):
        """Test git info when not in a git repository"""
        mock_run.return_value = Mock(returncode=1)  # not a git repo
        
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'true'}):
            git_info = HoneyHiveTracer._get_git_info()
            
        assert 'error' in git_info
        assert 'Not a git repository' in git_info['error']

    def test_get_git_info_telemetry_disabled(self):
        """Test git info when telemetry is disabled"""
        with patch.dict(os.environ, {'HONEYHIVE_TELEMETRY': 'false'}):
            git_info = HoneyHiveTracer._get_git_info()
            
        assert 'error' in git_info
        assert 'Telemetry disabled' in git_info['error']

    @patch('honeyhive.tracer.HoneyHive')
    def test_start_session_success(self, mock_sdk_class):
        """Test successful session start"""
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.object.session_id = "test-session-id"
        mock_sdk.session.start_session.return_value = mock_response
        
        session_id = HoneyHiveTracer._HoneyHiveTracer__start_session(
            "api_key", "project", "session_name", "source", "server_url"
        )
        
        assert session_id == "test-session-id"
        mock_sdk.session.start_session.assert_called_once()

    @patch('honeyhive.tracer.HoneyHive')
    def test_start_session_failure(self, mock_sdk_class):
        """Test session start failure"""
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raw_response.text = "Bad request"
        mock_sdk.session.start_session.return_value = mock_response
        
        with pytest.raises(AssertionError, match="Failed to start session"):
            HoneyHiveTracer._HoneyHiveTracer__start_session(
                "api_key", "project", "session_name", "source", "server_url"
            )

    def test_sanitize_carrier(self):
        """Test carrier sanitization for link method"""
        carrier = {
            'baggage': 'session_id=123',
            'Traceparent': '00-trace-span-01'
        }
        getter = BaggageDict.DefaultGetter
        
        result = HoneyHiveTracer._sanitize_carrier(carrier, getter)
        
        assert 'baggage' in result
        assert 'traceparent' in result
        assert result['baggage'] == ['session_id=123']
        assert result['traceparent'] == ['00-trace-span-01']

    @patch('honeyhive.tracer.TracerWrapper')
    def test_flush_success(self, mock_tracer_wrapper):
        """Test successful flush"""
        HoneyHiveTracer._is_traceloop_initialized = True
        mock_wrapper = Mock()
        mock_tracer_wrapper.return_value = mock_wrapper
        
        HoneyHiveTracer.flush()
        
        mock_wrapper.flush.assert_called_once()

    def test_flush_not_initialized(self, capsys):
        """Test flush when tracer not initialized"""
        HoneyHiveTracer._is_traceloop_initialized = False
        
        HoneyHiveTracer.flush()
        
        captured = capsys.readouterr()
        assert "Could not flush: HoneyHiveTracer not initialized" in captured.out

    @patch('honeyhive.tracer.HoneyHive')
    @patch('honeyhive.tracer.context.get_current')
    def test_enrich_session_function_success(self, mock_get_current, mock_sdk_class):
        """Test standalone enrich_session function success"""
        # Mock context
        mock_ctx = Mock()
        mock_ctx.get.return_value = {'session_id': 'test-session-id'}
        mock_get_current.return_value = mock_ctx
        
        # Mock SDK
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_sdk.events.update_event.return_value = mock_response
        
        # Set up static variables
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        HoneyHiveTracer._is_traceloop_initialized = True
        
        enrich_session(metadata={'test': 'value'})
        
        mock_sdk.events.update_event.assert_called_once()

    def test_enrich_session_function_not_initialized(self, capsys):
        """Test standalone enrich_session function when not initialized"""
        HoneyHiveTracer._is_traceloop_initialized = False
        
        enrich_session(metadata={'test': 'value'})
        
        captured = capsys.readouterr()
        assert "Could not enrich session: HoneyHiveTracer not initialized" in captured.out

    @patch('honeyhive.tracer.Traceloop')
    @patch('honeyhive.tracer.HoneyHive')
    @patch('honeyhive.tracer.HoneyHiveTracer._get_git_info')
    def test_init_success(self, mock_git_info, mock_sdk_class, mock_traceloop):
        """Test successful HoneyHiveTracer initialization"""
        # Mock git info
        mock_git_info.return_value = {'commit_hash': 'abc123', 'branch': 'main'}
        
        # Mock SDK
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
            
        assert tracer.session_id == "test-session-id"
        assert tracer.project == "test_project"
        assert HoneyHiveTracer.api_key == "test_key"

    def test_init_invalid_session_id(self):
        """Test initialization with invalid session_id"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with pytest.raises(errors.SDKError, match="session_id must be a valid UUID"):
                HoneyHiveTracer(session_id="invalid-uuid")

    def test_init_missing_api_key(self, capsys):
        """Test initialization with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            HoneyHiveTracer()
            
        captured = capsys.readouterr()
        assert "HoneyHive SDK Error" in captured.out

    def test_init_missing_project(self, capsys):
        """Test initialization with missing project"""
        with patch.dict(os.environ, {'HH_API_KEY': 'test_key'}, clear=True):
            HoneyHiveTracer()
            
        captured = capsys.readouterr()
        assert "HoneyHive SDK Error" in captured.out

    @patch('honeyhive.tracer.HoneyHive')
    def test_enrich_session_method(self, mock_sdk_class):
        """Test HoneyHiveTracer.enrich_session method"""
        # Mock SDK
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_sdk.events.update_event.return_value = mock_response
        
        # Set up static variables
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        HoneyHiveTracer._is_traceloop_initialized = True
        
        # Create tracer instance
        tracer = Mock()
        tracer.session_id = 'test-session-id'
        
        # Call method
        HoneyHiveTracer.enrich_session(
            tracer,
            metadata={'test': 'value'},
            feedback={'rating': 5},
            metrics={'score': 0.9}
        )
        
        mock_sdk.events.update_event.assert_called_once()
        call_args = mock_sdk.events.update_event.call_args[1]['request']
        assert call_args.event_id == 'test-session-id'
        assert call_args.metadata == {'test': 'value'}
        assert call_args.feedback == {'rating': 5}
        assert call_args.metrics == {'score': 0.9}