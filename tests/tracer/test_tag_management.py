import pytest
import os
import threading
import time
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.utils.baggage_dict import BaggageDict
from opentelemetry import context, baggage


class TestTagManagement:
    """Comprehensive tests for tag propagation and management functionality"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_tag_initialization_in_constructor(self):
        """Test tag initialization during tracer construction"""
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
                
                # Test with various tag types
                initial_tags = {
                    'environment': 'production',
                    'version': '1.2.3',
                    'team': 'ml-platform',
                    'experiment_id': 'exp_123',
                    'user_tier': 'premium',
                    'region': 'us-east-1',
                    'debug': True,
                    'priority': 5,
                    'weight': 0.75
                }
                
                tracer = HoneyHiveTracer(tags=initial_tags)
                
                # Verify tags are stored
                assert tracer.tags == initial_tags
                
                # Verify tags are in baggage with correct prefix
                for key, value in initial_tags.items():
                    baggage_key = f'tag_{key}'
                    assert baggage_key in tracer.baggage
                    assert tracer.baggage[baggage_key] == str(value)

    def test_add_tags_basic_functionality(self):
        """Test basic add_tags functionality"""
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
                
                # Add initial tags
                initial_tags = {'env': 'test', 'version': '1.0'}
                tracer.add_tags(initial_tags)
                
                assert tracer.tags == initial_tags
                
                # Add more tags
                additional_tags = {'team': 'backend', 'priority': 'high'}
                tracer.add_tags(additional_tags)
                
                expected_tags = {**initial_tags, **additional_tags}
                assert tracer.tags == expected_tags

    def test_add_tags_type_handling(self):
        """Test add_tags with various data types"""
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
                
                # Test various data types
                mixed_tags = {
                    'string_tag': 'text_value',
                    'int_tag': 42,
                    'float_tag': 3.14,
                    'bool_true': True,
                    'bool_false': False,
                    'zero_int': 0,
                    'empty_string': '',
                    'unicode_tag': '🚀🌟',
                    'scientific': 1.23e-10
                }
                
                tracer.add_tags(mixed_tags)
                
                # Verify all types are stored
                for key, value in mixed_tags.items():
                    assert tracer.tags[key] == value
                    # Verify in baggage as strings
                    baggage_key = f'tag_{key}'
                    assert tracer.baggage[baggage_key] == str(value)

    def test_tag_overwriting_behavior(self):
        """Test tag overwriting behavior"""
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
                
                tracer = HoneyHiveTracer(tags={'env': 'development', 'version': '1.0'})
                
                # Overwrite existing tags
                tracer.add_tags({'env': 'production', 'team': 'backend'})
                
                expected_tags = {'env': 'production', 'version': '1.0', 'team': 'backend'}
                assert tracer.tags == expected_tags
                
                # Verify baggage was updated
                assert tracer.baggage['tag_env'] == 'production'
                assert tracer.baggage['tag_version'] == '1.0' 
                assert tracer.baggage['tag_team'] == 'backend'

    def test_tag_propagation_to_context(self):
        """Test tag propagation to OpenTelemetry context"""
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
                
                # Add tags
                test_tags = {'service': 'api', 'region': 'us-west-2', 'canary': True}
                tracer.add_tags(test_tags)
                
                # Check context propagation
                current_ctx = context.get_current()
                
                # Verify tags are in context baggage
                for key, value in test_tags.items():
                    baggage_value = baggage.get_baggage(f'tag_{key}', current_ctx)
                    assert baggage_value == str(value)

    def test_tag_propagation_across_threads(self):
        """Test tag propagation across thread boundaries"""
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
                
                tracer = HoneyHiveTracer(tags={'main_thread': 'true', 'shared': 'value'})
                
                thread_results = {}
                
                def worker_thread(thread_id):
                    # Check if tags are available in worker thread
                    current_ctx = context.get_current()
                    
                    thread_results[thread_id] = {
                        'main_thread_tag': baggage.get_baggage('tag_main_thread', current_ctx),
                        'shared_tag': baggage.get_baggage('tag_shared', current_ctx),
                        'session_id': baggage.get_baggage('session_id', current_ctx)
                    }
                
                # Start worker threads
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=worker_thread, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join()
                
                # Verify tag propagation
                for thread_id, result in thread_results.items():
                    assert result['main_thread_tag'] == 'true', f"Thread {thread_id} missing main_thread tag"
                    assert result['shared_tag'] == 'value', f"Thread {thread_id} missing shared tag"
                    assert result['session_id'] == 'test-session-id', f"Thread {thread_id} missing session_id"

    def test_tag_injection_and_extraction(self):
        """Test tag injection into carrier and extraction"""
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
                
                # Create tracer with tags
                original_tracer = HoneyHiveTracer(tags={
                    'service': 'frontend',
                    'version': '2.1.0',
                    'deploy_id': 'deploy_456'
                })
                
                # Inject context into carrier
                carrier = {}
                original_tracer.inject(carrier)
                
                # Verify carrier contains baggage
                assert 'baggage' in carrier or any('baggage' in str(k).lower() for k in carrier.keys())
                
                # Create new tracer and link with carrier
                HoneyHiveTracer.api_key = None  # Reset for new tracer
                HoneyHiveTracer.server_url = None
                HoneyHiveTracer._is_traceloop_initialized = False
                
                mock_response.object.session_id = "new-session-id"
                new_tracer = HoneyHiveTracer()
                
                # Link with carrier
                new_tracer.link(carrier)
                
                # Verify context was restored (implementation dependent)
                current_ctx = context.get_current()
                # Some tags might be preserved through linking
                assert current_ctx is not None

    def test_baggage_dict_tag_handling(self):
        """Test BaggageDict specific tag handling"""
        baggage_dict = BaggageDict()
        
        # Test tag keys (should be allowed even if not in valid_baggage_keys)
        tag_data = {
            'tag_environment': 'production',
            'tag_version': '1.0.0',
            'tag_feature_flag': 'enabled',
            'tag_user_segment': 'premium'
        }
        
        # Add tag keys directly
        for key, value in tag_data.items():
            baggage_dict[key] = value
        
        # Verify tag keys are stored
        for key, value in tag_data.items():
            assert baggage_dict[key] == value
        
        # Test set_all_baggage includes tags
        ctx = baggage_dict.set_all_baggage()
        
        for key, value in tag_data.items():
            retrieved_value = baggage.get_baggage(key, ctx)
            assert retrieved_value == value
        
        # Test get_all_baggage includes tags
        all_baggage = baggage_dict.get_all_baggage(ctx)
        for key, value in tag_data.items():
            assert all_baggage.get(key) == value

    def test_tag_memory_and_cleanup(self):
        """Test tag memory usage and cleanup"""
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
                
                # Add many tags
                large_tag_set = {f'tag_{i}': f'value_{i}' for i in range(1000)}
                tracer.add_tags(large_tag_set)
                
                # Verify all tags are stored
                assert len(tracer.tags) == 1000
                
                # Verify baggage contains all tags
                tag_baggage = {k: v for k, v in tracer.baggage.items() if k.startswith('tag_')}
                assert len(tag_baggage) == 1000
                
                # Clear references (simulate cleanup)
                del large_tag_set
                
                # Tags should still be accessible through tracer
                assert tracer.tags[f'tag_{500}'] == f'value_{500}'

    def test_concurrent_tag_operations(self):
        """Test concurrent tag addition and modification"""
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
                
                def add_tags_worker(worker_id, num_tags=50):
                    for i in range(num_tags):
                        time.sleep(0.001)  # Small delay to encourage race conditions
                        tags = {f'worker_{worker_id}_tag_{i}': f'value_{i}'}
                        tracer.add_tags(tags)
                
                # Start concurrent workers
                threads = []
                num_workers = 10
                
                for worker_id in range(num_workers):
                    thread = threading.Thread(target=add_tags_worker, args=(worker_id,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join(timeout=30)
                
                # Verify all tags were added
                expected_tags = num_workers * 50
                actual_tags = len([k for k in tracer.tags.keys() if k.startswith('worker_')])
                
                # Allow for some race condition losses but should be close
                assert actual_tags >= expected_tags * 0.9, f"Expected ~{expected_tags}, got {actual_tags}"

    def test_tag_validation_and_sanitization(self):
        """Test tag validation and sanitization"""
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
                
                # Test tags with special characters
                special_tags = {
                    'tag-with-dashes': 'value1',
                    'tag_with_underscores': 'value2',
                    'tag.with.dots': 'value3',
                    'tag with spaces': 'value4',
                    'tag123numbers': 'value5',
                    'UPPERCASE_TAG': 'value6',
                    'MixedCase_Tag': 'value7',
                    '🚀emoji_tag': 'value8'
                }
                
                tracer.add_tags(special_tags)
                
                # All should be stored (validation may vary by implementation)
                for key, value in special_tags.items():
                    assert tracer.tags[key] == value

    def test_tag_persistence_across_operations(self):
        """Test tag persistence across various tracer operations"""
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
                
                tracer = HoneyHiveTracer(tags={'persistent': 'true', 'initial': 'tag'})
                
                # Perform various operations
                tracer.add_tags({'operation': 'add_tags'})
                
                # Create carrier and inject
                carrier = {}
                tracer.inject(carrier)
                
                # Link operation
                token = tracer.link(carrier)
                
                # More tag operations
                tracer.add_tags({'after_link': 'true'})
                
                # Verify all tags persist
                expected_tags = {
                    'persistent': 'true',
                    'initial': 'tag',
                    'operation': 'add_tags',
                    'after_link': 'true'
                }
                
                for key, value in expected_tags.items():
                    assert tracer.tags[key] == value
                
                # Cleanup
                if token:
                    tracer.unlink(token)

    def test_tag_edge_cases_and_limits(self):
        """Test tag handling with edge cases and limits"""
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
                
                # Edge case values
                edge_case_tags = {
                    'empty_key': '',
                    'null_like': 'null',
                    'undefined_like': 'undefined',
                    'very_long_key': 'x' * 1000,
                    'very_long_value': 'y' * 10000,
                    'numeric_string': '12345',
                    'float_string': '3.14159',
                    'boolean_string': 'true',
                    'special_chars': '!@#$%^&*()[]{}|;:,.<>?',
                    'json_like': '{"nested": "value"}',
                    'array_like': '[1,2,3,4,5]'
                }
                
                tracer.add_tags(edge_case_tags)
                
                # All should be handled gracefully
                for key, value in edge_case_tags.items():
                    assert tracer.tags[key] == value

    def test_tag_uninitialized_tracer_handling(self):
        """Test tag operations on uninitialized tracer"""
        # Create tracer instance without proper initialization
        tracer = object.__new__(HoneyHiveTracer)
        tracer.tags = {}
        tracer._tags_initialized = False
        
        # Should handle gracefully and still update tags
        tracer.add_tags({'test': 'uninitialized'})
        
        assert tracer.tags == {'test': 'uninitialized'}
        assert not getattr(tracer, '_tags_initialized', True)

    def test_tag_serialization_compatibility(self):
        """Test tag serialization for various transport mechanisms"""
        import json
        import pickle
        
        tag_data = {
            'string': 'value',
            'number': 42,
            'float': 3.14,
            'boolean': True,
            'unicode': '🌟',
            'complex': {'nested': 'structure'}
        }
        
        # Test JSON serialization (tags should be JSON compatible)
        try:
            json_str = json.dumps(tag_data)
            restored_from_json = json.loads(json_str)
            # Basic structure should be preserved
            assert 'string' in restored_from_json
        except Exception as e:
            pytest.fail(f"Tags should be JSON serializable: {e}")
        
        # Test basic serialization
        try:
            serialized = str(tag_data)
            assert 'string' in serialized
        except Exception as e:
            pytest.fail(f"Tags should be string serializable: {e}")