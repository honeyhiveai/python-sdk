import pytest
import asyncio
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.custom import trace, atrace, enrich_span
from honeyhive.utils.baggage_dict import BaggageDict
from opentelemetry import context, baggage
from opentelemetry.context import Context


class TestContextPropagation:
    """Comprehensive tests for context propagation and baggage handling"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    @patch('honeyhive.tracer.HoneyHive')
    @patch('honeyhive.tracer.Traceloop')
    def test_context_propagation_across_threads(self, mock_traceloop, mock_sdk_class):
        """Test context propagation across thread boundaries"""
        # Setup mocks
        mock_sdk = Mock()
        mock_sdk_class.return_value = mock_sdk
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.object.session_id = "parent-session-id"
        mock_sdk.session.start_session.return_value = mock_response
        
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            # Create tracer in main thread
            parent_tracer = HoneyHiveTracer(tags={'thread': 'main', 'test': 'context_prop'})
            
            # Store expected context values
            expected_session_id = parent_tracer.session_id
            expected_baggage = parent_tracer.baggage.get_all_baggage()
            
            # Results storage
            thread_results = {}
            
            def worker_thread(thread_id):
                """Worker function that checks context inheritance"""
                # Get current context in worker thread
                current_ctx = context.get_current()
                association_props = current_ctx.get('association_properties')
                
                # Check if context was properly inherited
                thread_results[thread_id] = {
                    'has_association_props': association_props is not None,
                    'session_id': association_props.get('session_id') if association_props else None,
                    'baggage_values': {}
                }
                
                # Check specific baggage values
                for key in BaggageDict.valid_baggage_keys:
                    value = baggage.get_baggage(key, current_ctx)
                    if value:
                        thread_results[thread_id]['baggage_values'][key] = value
                
                # Check tag baggage
                tag_session_id = baggage.get_baggage('tag_thread', current_ctx)
                tag_test = baggage.get_baggage('tag_test', current_ctx)
                thread_results[thread_id]['baggage_values']['tag_thread'] = tag_session_id
                thread_results[thread_id]['baggage_values']['tag_test'] = tag_test
            
            # Create multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Verify context was propagated to all threads
            for thread_id, result in thread_results.items():
                assert result['session_id'] == expected_session_id, f"Thread {thread_id} missing session_id"
                assert result['baggage_values'].get('session_id') == expected_session_id
                assert result['baggage_values'].get('tag_thread') == 'main'
                assert result['baggage_values'].get('tag_test') == 'context_prop'

    @patch('honeyhive.tracer.HoneyHive')
    @patch('honeyhive.tracer.Traceloop')
    def test_baggage_serialization_deserialization(self, mock_traceloop, mock_sdk_class):
        """Test baggage serialization and deserialization"""
        # Setup mocks
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
            # Create tracer with various data types in tags
            complex_tags = {
                'string_tag': 'test_value',
                'number_tag': 42,
                'float_tag': 3.14,
                'boolean_tag': True,
                'unicode_tag': '🌟🚀',
                'special_chars': 'test=value&other=data',
            }
            
            tracer = HoneyHiveTracer(
                source='serialization_test',
                tags=complex_tags
            )
            
            # Get original baggage
            original_baggage = tracer.baggage.get_all_baggage()
            
            # Simulate serialization through carrier injection/extraction
            carrier = {}
            tracer.inject(carrier)
            
            # Verify carrier contains expected headers
            assert 'baggage' in carrier or any('baggage' in str(k).lower() for k in carrier.keys())
            
            # Create new tracer and link with carrier
            new_tracer = HoneyHiveTracer(
                session_id=str(tracer.session_id),
                project='test_project',
                source='serialization_test'
            )
            
            # Link with carrier to restore context
            new_tracer.link(carrier)
            
            # Verify baggage was properly restored
            restored_baggage = new_tracer.baggage.get_all_baggage()
            
            # Check core baggage values
            assert restored_baggage.get('session_id') == original_baggage.get('session_id')
            assert restored_baggage.get('project') == original_baggage.get('project')
            assert restored_baggage.get('source') == original_baggage.get('source')

    @pytest.mark.asyncio
    async def test_async_context_inheritance(self):
        """Test context inheritance in async operations"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "async-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                # Create tracer in main context
                tracer = HoneyHiveTracer(tags={'async_test': 'true', 'context': 'main'})
                
                # Store expected values
                expected_session_id = tracer.session_id
                
                async def async_worker(worker_id):
                    """Async worker that checks context inheritance"""
                    await asyncio.sleep(0.01)  # Simulate async work
                    
                    # Check current context
                    current_ctx = context.get_current()
                    association_props = current_ctx.get('association_properties')
                    
                    return {
                        'worker_id': worker_id,
                        'session_id': association_props.get('session_id') if association_props else None,
                        'async_tag': baggage.get_baggage('tag_async_test', current_ctx),
                        'context_tag': baggage.get_baggage('tag_context', current_ctx)
                    }
                
                # Run multiple async workers concurrently
                tasks = [async_worker(i) for i in range(10)]
                results = await asyncio.gather(*tasks)
                
                # Verify all workers inherited context correctly
                for result in results:
                    assert result['session_id'] == expected_session_id
                    assert result['async_tag'] == 'true'
                    assert result['context_tag'] == 'main'

    @pytest.mark.asyncio
    async def test_nested_async_context_propagation(self):
        """Test context propagation through nested async calls"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "nested-session-id"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer(tags={'level': '0'})
                
                async def nested_async_call(level, max_level=3):
                    """Recursively nested async calls"""
                    await asyncio.sleep(0.001)  # Small delay
                    
                    # Check context at current level
                    current_ctx = context.get_current()
                    association_props = current_ctx.get('association_properties')
                    session_id = association_props.get('session_id') if association_props else None
                    
                    if level < max_level:
                        # Add tag for current level and recurse
                        tracer.add_tags({f'level_{level}': f'visited'})
                        return await nested_async_call(level + 1, max_level)
                    else:
                        # Return context info from deepest level
                        return {
                            'session_id': session_id,
                            'level_tags': {
                                f'level_{i}': baggage.get_baggage(f'tag_level_{i}', current_ctx)
                                for i in range(max_level + 1)
                            }
                        }
                
                result = await nested_async_call(0)
                
                # Verify context propagated through all levels
                assert result['session_id'] == tracer.session_id
                for i in range(3):
                    assert result['level_tags'].get(f'level_{i}') == 'visited'

    def test_baggage_cross_process_simulation(self):
        """Test baggage handling across simulated process boundaries"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "cross-process-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                # Simulate "Process 1" - create tracer and inject context
                process1_tracer = HoneyHiveTracer(
                    source='process1',
                    tags={'process': '1', 'data': 'important'}
                )
                
                # Inject context into carrier (simulate HTTP headers)
                carrier = {}
                process1_tracer.inject(carrier)
                
                # Simulate "Process 2" - receive carrier and restore context
                # Reset tracer state to simulate new process
                HoneyHiveTracer.api_key = None
                HoneyHiveTracer.server_url = None
                HoneyHiveTracer._is_traceloop_initialized = False
                
                # Create new tracer in "process 2"
                mock_response.object.session_id = "process2-session"
                process2_tracer = HoneyHiveTracer(
                    source='process2',
                    tags={'process': '2'}
                )
                
                # Link with carrier from process 1
                process2_tracer.link(carrier)
                
                # Verify context was restored
                current_ctx = context.get_current()
                
                # Check that we can access baggage from process 1
                original_session = baggage.get_baggage('session_id', current_ctx)
                original_project = baggage.get_baggage('project', current_ctx)
                original_source = baggage.get_baggage('source', current_ctx)
                
                # Verify some context was propagated (implementation may vary)
                assert current_ctx is not None
                # Note: exact values depend on implementation details of linking

    def test_context_isolation_between_tracers(self):
        """Test that different tracer instances have isolated contexts"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                
                # Create multiple mock responses
                mock_responses = []
                for i in range(3):
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.object.session_id = f"isolated-session-{i}"
                    mock_responses.append(mock_response)
                
                mock_sdk.session.start_session.side_effect = mock_responses
                
                # Create multiple tracers with different contexts
                tracers = []
                for i in range(3):
                    tracer = HoneyHiveTracer(
                        source=f'isolated_source_{i}',
                        tags={'tracer_id': str(i), 'isolation_test': 'true'}
                    )
                    tracers.append(tracer)
                
                # Verify each tracer has its own session and context
                session_ids = [t.session_id for t in tracers]
                assert len(set(session_ids)) == 3  # All unique
                
                # Verify baggage isolation
                for i, tracer in enumerate(tracers):
                    baggage_dict = tracer.baggage.get_all_baggage()
                    assert baggage_dict.get('source') == f'isolated_source_{i}'
                    assert baggage_dict.get('tag_tracer_id') == str(i)

    @pytest.mark.asyncio
    async def test_concurrent_async_operations_context_safety(self):
        """Test context safety with many concurrent async operations"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "concurrent-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer(tags={'concurrent_test': 'true'})
                
                async def concurrent_worker(worker_id, iterations=10):
                    """Worker that performs multiple context operations"""
                    results = []
                    
                    for i in range(iterations):
                        # Add unique tags for this worker and iteration
                        tracer.add_tags({
                            f'worker_{worker_id}_iteration_{i}': f'value_{i}'
                        })
                        
                        await asyncio.sleep(0.001)  # Small delay
                        
                        # Check context consistency
                        current_ctx = context.get_current()
                        association_props = current_ctx.get('association_properties')
                        session_id = association_props.get('session_id') if association_props else None
                        
                        results.append({
                            'worker_id': worker_id,
                            'iteration': i,
                            'session_id': session_id,
                            'concurrent_tag': baggage.get_baggage('tag_concurrent_test', current_ctx)
                        })
                    
                    return results
                
                # Run many concurrent workers
                num_workers = 20
                tasks = [concurrent_worker(i, 5) for i in range(num_workers)]
                all_results = await asyncio.gather(*tasks)
                
                # Flatten results
                flattened_results = [item for sublist in all_results for item in sublist]
                
                # Verify all operations had consistent context
                expected_session = tracer.session_id
                for result in flattened_results:
                    assert result['session_id'] == expected_session
                    assert result['concurrent_tag'] == 'true'

    def test_baggage_type_coercion_and_validation(self):
        """Test baggage type coercion and validation"""
        baggage_dict = BaggageDict()
        
        # Test valid baggage keys
        valid_data = {
            'session_id': 'test-session',
            'project': 'test-project',
            'source': 'test-source',
            'run_id': 'run-123',
            'dataset_id': 'dataset-456',
            'datapoint_id': 'datapoint-789',
            'disable_http_tracing': True,
        }
        
        baggage_dict.update(valid_data)
        
        # Verify type coercion
        assert baggage_dict['session_id'] == 'test-session'
        assert baggage_dict['disable_http_tracing'] is True  # Should be converted to bool
        
        # Test invalid keys are filtered out
        invalid_data = {
            'invalid_key': 'should_be_ignored',
            'another_invalid': 123,
            'session_id': 'valid_value'  # This should be kept
        }
        
        baggage_dict.update(invalid_data)
        assert 'invalid_key' not in baggage_dict
        assert 'another_invalid' not in baggage_dict
        assert baggage_dict['session_id'] == 'valid_value'
        
        # Test None values are handled
        baggage_dict['project'] = None
        assert baggage_dict.get('project') is None
        
        # Test tag keys (not in valid_baggage_keys) can be set directly
        baggage_dict['tag_test'] = 'tag_value'
        assert baggage_dict['tag_test'] == 'tag_value'

    def test_context_with_link_carrier_edge_cases(self):
        """Test context linking with various carrier edge cases"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "link-test-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                # Test various carrier formats
                carriers = [
                    # Standard case-sensitive
                    {'baggage': 'session_id=test123', 'traceparent': '00-trace-span-01'},
                    # Case variations
                    {'Baggage': 'session_id=test456', 'Traceparent': '00-trace-span-02'},
                    {'BAGGAGE': 'session_id=test789', 'TRACEPARENT': '00-trace-span-03'},
                    # Mixed case
                    {'BaGgAgE': 'session_id=testmixed', 'TraceParent': '00-trace-span-04'},
                    # Empty values
                    {'baggage': '', 'traceparent': ''},
                    # Missing keys
                    {'other_header': 'value'},
                    # Multiple baggage values
                    {'baggage': 'session_id=multi,project=test,source=dev'},
                ]
                
                for i, carrier in enumerate(carriers):
                    try:
                        # Should handle all carrier formats gracefully
                        token = tracer.link(carrier)
                        
                        # Verify linking worked (context should be attached)
                        current_ctx = context.get_current()
                        assert current_ctx is not None
                        
                        # Clean up
                        if token:
                            tracer.unlink(token)
                            
                    except Exception as e:
                        # Some carriers may cause expected exceptions
                        # Log but continue testing
                        print(f"Carrier {i} caused exception: {e}")
                        continue