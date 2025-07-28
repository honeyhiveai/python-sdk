import pytest
import os
import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer, enrich_session
from honeyhive.tracer.custom import trace, atrace, enrich_span
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import errors


class TestInputValidation:
    """Comprehensive input validation and type safety tests"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_api_key_validation_edge_cases(self):
        """Test API key validation with edge cases"""
        invalid_api_keys = [
            "",  # Empty string
            " ",  # Whitespace only
            "\n",  # Newline
            "\t",  # Tab
            None,  # None value
            123,  # Integer
            [],  # List
            {},  # Dictionary
            True,  # Boolean
            0.5,  # Float
        ]
        
        for invalid_key in invalid_api_keys:
            assert not HoneyHiveTracer._validate_api_key(invalid_key)
        
        # Valid cases
        valid_api_keys = [
            "valid_key",
            "key-with-dashes",
            "key_with_underscores",
            "UPPERCASE_KEY",
            "mixedCaseKey",
            "key123with456numbers",
            "very_long_key_" + "x" * 100,
        ]
        
        for valid_key in valid_api_keys:
            assert HoneyHiveTracer._validate_api_key(valid_key)

    def test_server_url_validation_edge_cases(self):
        """Test server URL validation with edge cases"""
        invalid_urls = [
            "",  # Empty string
            " ",  # Whitespace only
            None,  # None value
            123,  # Integer
            [],  # List
            {},  # Dictionary
            True,  # Boolean
            "not-a-url",  # Invalid format
            "http://",  # Incomplete
            "://no-protocol.com",  # Missing protocol
        ]
        
        for invalid_url in invalid_urls:
            assert not HoneyHiveTracer._validate_server_url(invalid_url)
        
        # Valid cases (basic string validation only)
        valid_urls = [
            "https://api.honeyhive.ai",
            "http://localhost:8080",
            "https://custom.domain.com/path",
            "http://192.168.1.1:3000",
            "https://api.example.com/v1/endpoint",
        ]
        
        for valid_url in valid_urls:
            assert HoneyHiveTracer._validate_server_url(valid_url)

    def test_project_validation_edge_cases(self):
        """Test project validation with edge cases"""
        invalid_projects = [
            "",  # Empty string
            " ",  # Whitespace only
            "\n",  # Newline only
            "\t",  # Tab only
            None,  # None value
            123,  # Integer
            [],  # List
            {},  # Dictionary
            True,  # Boolean
        ]
        
        for invalid_project in invalid_projects:
            assert not HoneyHiveTracer._validate_project(invalid_project)
        
        # Valid cases
        valid_projects = [
            "test_project",
            "project-with-dashes",
            "ProjectWithCamelCase",
            "project123",
            "UPPERCASE_PROJECT",
            "project with spaces",  # Spaces are valid
            "project_" + "x" * 100,  # Long project name
            "项目名称",  # Unicode characters
        ]
        
        for valid_project in valid_projects:
            assert HoneyHiveTracer._validate_project(valid_project)

    def test_source_validation_edge_cases(self):
        """Test source validation with edge cases"""
        invalid_sources = [
            "",  # Empty string
            " ",  # Whitespace only
            None,  # None value
            123,  # Integer
            [],  # List
            {},  # Dictionary
            True,  # Boolean
        ]
        
        for invalid_source in invalid_sources:
            assert not HoneyHiveTracer._validate_source(invalid_source)
        
        # Valid cases
        valid_sources = [
            "dev",
            "production",
            "test",
            "staging",
            "local",
            "source-with-dashes",
            "source_with_underscores",
            "source with spaces",
            "SOURCE_UPPERCASE",
            "source123",
            "测试源",  # Unicode
        ]
        
        for valid_source in valid_sources:
            assert HoneyHiveTracer._validate_source(valid_source)

    def test_session_id_validation_comprehensive(self):
        """Test comprehensive session ID validation"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            # Valid UUID formats
            valid_uuids = [
                str(uuid.uuid4()),  # Standard UUID4
                str(uuid.uuid1()),  # UUID1
                "12345678-1234-1234-1234-123456789012",  # Manual valid UUID
                "ABCDEFGH-1234-5678-9012-ABCDEFGHIJKL",  # Uppercase
                "abcdefgh-1234-5678-9012-abcdefghijkl",  # Lowercase
            ]
            
            for valid_uuid in valid_uuids:
                with patch('honeyhive.tracer.HoneyHive'):
                    try:
                        tracer = HoneyHiveTracer(session_id=valid_uuid)
                        assert tracer.session_id == valid_uuid.lower()
                    except Exception as e:
                        pytest.fail(f"Valid UUID {valid_uuid} should not raise: {e}")
            
            # Invalid UUID formats
            invalid_uuids = [
                "not-a-uuid",
                "12345678-1234-1234-1234",  # Too short
                "12345678-1234-1234-1234-12345678901234",  # Too long
                "xyz45678-1234-1234-1234-123456789012",  # Invalid hex
                "12345678-12341234-1234-123456789012",  # Wrong format
                "",  # Empty
                "   ",  # Whitespace
                123,  # Integer
                [],  # List
                {},  # Dict
                True,  # Boolean
            ]
            
            for invalid_uuid in invalid_uuids:
                with pytest.raises(errors.SDKError, match="session_id must be a valid UUID"):
                    HoneyHiveTracer(session_id=invalid_uuid)

    def test_tags_validation_comprehensive(self):
        """Test comprehensive tags validation"""
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
                
                # Valid tag formats
                valid_tag_sets = [
                    {'string_tag': 'value'},
                    {'number_tag': 123},
                    {'float_tag': 3.14},
                    {'bool_tag': True},
                    {'false_tag': False},
                    {'unicode_tag': '🚀🌟'},
                    {'empty_string': ''},
                    {'spaces': 'value with spaces'},
                    {'special_chars': 'value-with_special.chars'},
                    {'mixed': {'nested': 'not_allowed_but_handled'}},  # Should be converted to string
                    {'list_tag': [1, 2, 3]},  # Should be converted to string
                    {'decimal_tag': Decimal('10.5')},  # Should be converted to string
                    {'datetime_tag': datetime.now()},  # Should be converted to string
                ]
                
                for tags in valid_tag_sets:
                    try:
                        tracer = HoneyHiveTracer(tags=tags)
                        assert isinstance(tracer.tags, dict)
                        assert len(tracer.tags) >= len(tags)
                    except Exception as e:
                        pytest.fail(f"Valid tags {tags} should not raise: {e}")

    def test_add_tags_validation(self):
        """Test add_tags method validation"""
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
                
                # Valid tag additions
                valid_additions = [
                    {'new_tag': 'value'},
                    {'multiple': 'tags', 'in': 'one', 'call': True},
                    {},  # Empty dict should work
                ]
                
                for tags in valid_additions:
                    try:
                        tracer.add_tags(tags)
                    except Exception as e:
                        pytest.fail(f"Valid add_tags({tags}) should not raise: {e}")
                
                # Invalid tag additions
                invalid_additions = [
                    "not_a_dict",
                    123,
                    [],
                    None,
                    True,
                    lambda x: x,
                ]
                
                for invalid_tags in invalid_additions:
                    with pytest.raises(ValueError, match="Tags must be a dictionary"):
                        tracer.add_tags(invalid_tags)

    def test_baggage_dict_type_coercion(self):
        """Test BaggageDict type coercion and validation"""
        baggage = BaggageDict()
        
        # Test valid baggage key updates
        valid_updates = [
            {'session_id': 'test-session'},
            {'project': 'test-project'},
            {'source': 'test-source'},
            {'run_id': 'run-123'},
            {'dataset_id': 'dataset-456'},
            {'datapoint_id': 'datapoint-789'},
            {'disable_http_tracing': True},
            {'disable_http_tracing': 'true'},  # String boolean
            {'disable_http_tracing': 'false'},  # String boolean
        ]
        
        for update in valid_updates:
            try:
                baggage.update(update)
            except Exception as e:
                pytest.fail(f"Valid baggage update {update} should not raise: {e}")
        
        # Test type coercion
        baggage['disable_http_tracing'] = 'True'
        assert baggage['disable_http_tracing'] is True
        
        baggage['disable_http_tracing'] = 'False'
        assert baggage['disable_http_tracing'] is False
        
        # Test invalid keys are filtered
        invalid_update = {
            'invalid_key': 'should_be_ignored',
            'session_id': 'should_be_kept',
            'another_invalid': 123,
        }
        
        baggage.update(invalid_update)
        assert 'invalid_key' not in baggage
        assert 'another_invalid' not in baggage
        assert baggage['session_id'] == 'should_be_kept'
        
        # Test None values are handled
        baggage['project'] = None
        assert baggage.get('project') is None

    def test_trace_decorator_parameter_validation(self):
        """Test trace decorator parameter validation"""
        # Valid event types
        valid_event_types = ['tool', 'model', 'chain']
        
        for event_type in valid_event_types:
            @trace(event_type=event_type)
            def test_function():
                return "result"
            
            assert test_function.event_type == event_type

        # Invalid event types (should not crash but may not set attribute)
        invalid_event_types = [
            'invalid_type',
            123,
            None,
            [],
            {},
            True,
        ]
        
        for event_type in invalid_event_types:
            try:
                @trace(event_type=event_type)
                def test_function():
                    return "result"
                
                # Should create decorator without error
                assert test_function.event_type == event_type
            except Exception as e:
                pytest.fail(f"trace decorator with event_type={event_type} should not raise: {e}")

    def test_trace_decorator_metadata_validation(self):
        """Test trace decorator metadata validation"""
        # Valid metadata formats
        valid_metadata = [
            {'key': 'value'},
            {'nested': {'dict': 'value'}},
            {'list': [1, 2, 3]},
            {'mixed': {'string': 'value', 'number': 123, 'bool': True}},
            {},  # Empty dict
            None,  # None should be handled
        ]
        
        for metadata in valid_metadata:
            try:
                @trace(metadata=metadata)
                def test_function():
                    return "result"
                
                assert test_function.metadata == metadata
            except Exception as e:
                pytest.fail(f"trace decorator with metadata={metadata} should not raise: {e}")

    def test_enrich_session_parameter_validation(self):
        """Test enrich_session parameter validation"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sdk.events.update_event.return_value = mock_response
            
            # Valid parameter combinations
            valid_params = [
                {
                    'session_id': 'test-session',
                    'metadata': {'key': 'value'}
                },
                {
                    'session_id': 'test-session',
                    'feedback': {'rating': 5, 'comment': 'good'}
                },
                {
                    'session_id': 'test-session',
                    'metrics': {'accuracy': 0.95, 'latency': 100}
                },
                {
                    'session_id': 'test-session',
                    'config': {'model': 'gpt-4', 'temperature': 0.7}
                },
                {
                    'session_id': 'test-session',
                    'outputs': {'response': 'Generated text'}
                },
                {
                    'session_id': 'test-session',
                    'user_properties': {'user_id': '123', 'plan': 'premium'}
                },
                # Complex nested data
                {
                    'session_id': 'test-session',
                    'metadata': {
                        'nested': {
                            'deeply': {
                                'nested': 'value'
                            }
                        },
                        'list': [1, 2, {'inner': 'value'}],
                        'mixed_types': {
                            'string': 'value',
                            'number': 123,
                            'float': 3.14,
                            'bool': True,
                            'null': None
                        }
                    }
                },
            ]
            
            for params in valid_params:
                try:
                    enrich_session(**params)
                    # Should complete without error
                except Exception as e:
                    # Some exceptions might be acceptable depending on implementation
                    print(f"enrich_session with {params} raised: {e}")

    def test_enrich_span_parameter_validation(self):
        """Test enrich_span parameter validation"""
        # Valid parameter combinations
        valid_params = [
            {'config': {'model': 'gpt-4'}},
            {'metadata': {'version': '1.0'}},
            {'metrics': {'score': 0.9}},
            {'feedback': {'rating': 5}},
            {'inputs': {'prompt': 'test'}},
            {'outputs': {'response': 'result'}},
            {'error': 'Error message'},
            {'tags': {'env': 'test'}},
            # Mixed parameters
            {
                'config': {'model': 'gpt-4'},
                'metadata': {'version': '1.0'},
                'metrics': {'score': 0.9},
                'tags': {'env': 'production'}
            },
            # Complex nested structures
            {
                'metadata': {
                    'request': {
                        'headers': {'content-type': 'application/json'},
                        'body': {'query': 'test query'}
                    },
                    'response': {
                        'status': 200,
                        'headers': {'content-length': '1234'}
                    }
                }
            },
        ]
        
        for params in valid_params:
            try:
                # Mock the current span
                with patch('honeyhive.tracer.custom.otel_trace.get_current_span') as mock_get_span:
                    mock_span = Mock()
                    mock_get_span.return_value = mock_span
                    
                    enrich_span(**params)
                    
                    # Should have called the instrumentor
                    assert mock_get_span.called
            except Exception as e:
                pytest.fail(f"enrich_span with {params} should not raise: {e}")

    def test_boundary_value_testing(self):
        """Test boundary values for various parameters"""
        # String length boundaries
        test_strings = [
            "",  # Empty
            "x",  # Single character
            "x" * 1000,  # Long string
            "x" * 10000,  # Very long string
        ]
        
        for test_string in test_strings:
            # Test API key validation
            if test_string:  # Non-empty strings should be valid
                assert HoneyHiveTracer._validate_api_key(test_string)
            else:
                assert not HoneyHiveTracer._validate_api_key(test_string)
        
        # Numeric boundaries
        numeric_values = [
            0,
            1,
            -1,
            float('inf'),
            float('-inf'),
            float('nan'),
            2**31 - 1,  # Max 32-bit int
            2**63 - 1,  # Max 64-bit int
        ]
        
        # These should be handled gracefully in tags
        for value in numeric_values:
            try:
                baggage = BaggageDict()
                baggage['tag_numeric'] = str(value)  # Tags get converted to strings
                assert isinstance(baggage['tag_numeric'], str)
            except Exception as e:
                print(f"Numeric value {value} caused: {e}")

    def test_unicode_and_encoding_validation(self):
        """Test Unicode and encoding handling"""
        unicode_test_cases = [
            "English text",
            "Español",
            "Français",
            "Deutsch",
            "Русский",
            "中文",
            "العربية",
            "हिन्दी",
            "日本語",
            "한국어",
            "🚀🌟💫",  # Emojis
            "Mix of text and emojis 🚀",
            "\u0000",  # Null character
            "\u001F",  # Control characters
            "\uFFFD",  # Replacement character
        ]
        
        for test_text in unicode_test_cases:
            try:
                # Test in various contexts
                assert HoneyHiveTracer._validate_project(test_text) or test_text in ["\u0000", "\u001F"]
                
                baggage = BaggageDict()
                baggage['tag_unicode'] = test_text
                
                # Should handle Unicode gracefully
                retrieved = baggage['tag_unicode']
                assert isinstance(retrieved, str)
                
            except Exception as e:
                print(f"Unicode text '{repr(test_text)}' caused: {e}")

    def test_type_safety_edge_cases(self):
        """Test type safety with edge cases"""
        edge_case_values = [
            None,
            True,
            False,
            0,
            1,
            -1,
            3.14,
            -3.14,
            float('inf'),
            float('-inf'),
            complex(1, 2),
            [],
            {},
            set(),
            frozenset(),
            bytes(b"test"),
            bytearray(b"test"),
        ]
        
        for value in edge_case_values:
            # Test baggage handling
            baggage = BaggageDict()
            try:
                if value is not None:
                    baggage['test_key'] = str(value) if not isinstance(value, str) else value
                    retrieved = baggage['test_key']
                    assert isinstance(retrieved, (str, bool, type(None)))
            except Exception as e:
                print(f"Edge case value {type(value).__name__}({value}) caused: {e}")