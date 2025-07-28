import pytest
import threading
import time
import os
import queue
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.custom import trace, atrace
from honeyhive.utils.baggage_dict import BaggageDict


class TestThreadSafety:
    """Comprehensive thread safety tests for tracer functionality"""

    def setup_method(self):
        """Reset HoneyHiveTracer static variables before each test"""
        HoneyHiveTracer.api_key = None
        HoneyHiveTracer.server_url = None
        HoneyHiveTracer._is_traceloop_initialized = False

    def test_concurrent_tracer_initialization(self):
        """Test multiple threads initializing tracers simultaneously"""
        results = queue.Queue()
        errors = queue.Queue()
        num_threads = 20
        
        def init_tracer_thread(thread_id):
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
                        
                        # Add small random delay to increase race condition chances
                        time.sleep(random.uniform(0.001, 0.01))
                        
                        tracer = HoneyHiveTracer(
                            session_name=f"session_{thread_id}",
                            tags={'thread_id': str(thread_id)}
                        )
                        
                        results.put({
                            'thread_id': thread_id,
                            'session_id': tracer.session_id,
                            'success': True
                        })
                        
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start all threads simultaneously
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=init_tracer_thread, args=(i,))
            threads.append(thread)
        
        # Start all threads at roughly the same time
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # Generous timeout
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no errors occurred
        assert len(all_errors) == 0, f"Errors in concurrent init: {all_errors}"
        
        # Verify all threads succeeded
        assert len(all_results) == num_threads
        
        # Verify all sessions are unique
        session_ids = [r['session_id'] for r in all_results]
        assert len(set(session_ids)) == num_threads

    def test_concurrent_tag_operations(self):
        """Test concurrent tag addition operations"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "concurrent-tags-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                results = queue.Queue()
                errors = queue.Queue()
                num_threads = 15
                tags_per_thread = 10
                
                def add_tags_thread(thread_id):
                    try:
                        for i in range(tags_per_thread):
                            # Add random delay to increase race conditions
                            time.sleep(random.uniform(0.001, 0.005))
                            
                            tags = {
                                f'thread_{thread_id}_tag_{i}': f'value_{i}',
                                f'shared_counter': str(thread_id * tags_per_thread + i)
                            }
                            
                            tracer.add_tags(tags)
                        
                        results.put({
                            'thread_id': thread_id,
                            'final_tags': dict(tracer.tags),
                            'success': True
                        })
                        
                    except Exception as e:
                        errors.put({
                            'thread_id': thread_id,
                            'error': str(e),
                            'type': type(e).__name__
                        })
                
                # Start all threads
                threads = []
                for i in range(num_threads):
                    thread = threading.Thread(target=add_tags_thread, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join(timeout=30)
                
                # Check results
                all_results = []
                while not results.empty():
                    all_results.append(results.get())
                
                all_errors = []
                while not errors.empty():
                    all_errors.append(errors.get())
                
                # Verify no errors
                assert len(all_errors) == 0, f"Errors in concurrent tag ops: {all_errors}"
                assert len(all_results) == num_threads
                
                # Verify final state consistency
                final_tags = tracer.tags
                
                # Check that tags from all threads are present
                for thread_id in range(num_threads):
                    for tag_id in range(tags_per_thread):
                        expected_key = f'thread_{thread_id}_tag_{tag_id}'
                        assert expected_key in final_tags, f"Missing {expected_key}"
                        assert final_tags[expected_key] == f'value_{tag_id}'

    def test_concurrent_flush_operations(self):
        """Test concurrent flush operations for thread safety"""
        HoneyHiveTracer._is_traceloop_initialized = True
        
        results = queue.Queue() 
        errors = queue.Queue()
        num_threads = 10
        
        def flush_thread(thread_id):
            try:
                # Multiple flush attempts per thread
                for i in range(3):
                    time.sleep(random.uniform(0.001, 0.01))
                    
                    with patch('honeyhive.tracer.TracerWrapper') as mock_wrapper_class:
                        mock_wrapper = Mock()
                        mock_wrapper_class.return_value = mock_wrapper
                        
                        HoneyHiveTracer.flush()
                        
                results.put({
                    'thread_id': thread_id,
                    'success': True
                })
                
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start concurrent flush operations
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=flush_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no deadlocks or errors occurred
        assert len(all_errors) == 0, f"Errors in concurrent flush: {all_errors}"
        assert len(all_results) == num_threads

    def test_concurrent_session_enrichment(self):
        """Test concurrent session enrichment operations"""
        HoneyHiveTracer._is_traceloop_initialized = True
        HoneyHiveTracer.api_key = 'test_key'
        HoneyHiveTracer.server_url = 'https://api.honeyhive.ai'
        
        results = queue.Queue()
        errors = queue.Queue()
        num_threads = 8
        
        def enrich_session_thread(thread_id):
            try:
                with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                    mock_sdk = Mock()
                    mock_sdk_class.return_value = mock_sdk
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_sdk.events.update_event.return_value = mock_response
                    
                    # Perform multiple enrichment operations
                    for i in range(5):
                        time.sleep(random.uniform(0.001, 0.01))
                        
                        from honeyhive.tracer import enrich_session
                        enrich_session(
                            session_id=f'test-session-{thread_id}',
                            metadata={
                                f'thread_{thread_id}_update_{i}': f'value_{i}',
                                'timestamp': time.time()
                            },
                            feedback={'rating': thread_id % 5 + 1}
                        )
                
                results.put({
                    'thread_id': thread_id,
                    'success': True
                })
                
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start concurrent enrichment operations
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=enrich_session_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no errors
        assert len(all_errors) == 0, f"Errors in concurrent enrichment: {all_errors}"
        assert len(all_results) == num_threads

    def test_static_variable_access_thread_safety(self):
        """Test thread-safe access to static variables"""
        num_threads = 20
        results = queue.Queue()
        errors = queue.Queue()
        
        def access_static_vars_thread(thread_id):
            try:
                # Multiple operations accessing/modifying static variables
                for i in range(10):
                    time.sleep(random.uniform(0.0001, 0.001))
                    
                    # Read operations
                    api_key = HoneyHiveTracer.api_key
                    server_url = HoneyHiveTracer.server_url
                    is_initialized = HoneyHiveTracer._is_traceloop_initialized
                    verbose = HoneyHiveTracer.verbose
                    
                    # Write operations (simulate what init does)
                    if i % 3 == 0:
                        HoneyHiveTracer.api_key = f'key_{thread_id}_{i}'
                    if i % 4 == 0:
                        HoneyHiveTracer.server_url = f'url_{thread_id}_{i}'
                    if i % 5 == 0:
                        HoneyHiveTracer.verbose = (thread_id % 2 == 0)
                
                results.put({
                    'thread_id': thread_id,
                    'final_api_key': HoneyHiveTracer.api_key,
                    'final_server_url': HoneyHiveTracer.server_url,
                    'final_verbose': HoneyHiveTracer.verbose,
                    'success': True
                })
                
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start all threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=access_static_vars_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no errors (race conditions might occur but shouldn't crash)
        assert len(all_errors) == 0, f"Errors in static var access: {all_errors}"
        assert len(all_results) == num_threads

    def test_trace_decorator_thread_safety(self):
        """Test thread safety of trace decorators"""
        call_results = queue.Queue()
        errors = queue.Queue()
        num_threads = 15
        
        @trace(event_type="tool", metadata={'thread_test': 'true'})
        def threaded_function(thread_id, call_id):
            """Function to be called from multiple threads"""
            time.sleep(random.uniform(0.001, 0.01))  # Simulate work
            return f"result_{thread_id}_{call_id}"
        
        def worker_thread(thread_id):
            try:
                # Multiple calls per thread
                for call_id in range(5):
                    with patch('honeyhive.tracer.custom.instrumentor._tracer') as mock_tracer:
                        mock_span = Mock()
                        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
                        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
                        
                        result = threaded_function(thread_id, call_id)
                        
                        call_results.put({
                            'thread_id': thread_id,
                            'call_id': call_id,
                            'result': result,
                            'success': True
                        })
                        
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start worker threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not call_results.empty():
            all_results.append(call_results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no errors
        assert len(all_errors) == 0, f"Errors in trace decorator: {all_errors}"
        assert len(all_results) == num_threads * 5  # 5 calls per thread
        
        # Verify all calls completed correctly
        for result in all_results:
            expected = f"result_{result['thread_id']}_{result['call_id']}"
            assert result['result'] == expected

    def test_baggage_dict_thread_safety(self):
        """Test thread safety of BaggageDict operations"""
        baggage = BaggageDict()
        results = queue.Queue()
        errors = queue.Queue()
        num_threads = 12
        
        def baggage_operations_thread(thread_id):
            try:
                # Perform various operations on shared baggage dict
                for i in range(20):
                    time.sleep(random.uniform(0.0001, 0.001))
                    
                    # Update operations
                    update_data = {
                        'session_id': f'session_{thread_id}_{i}',
                        'project': f'project_{thread_id}',
                        'source': f'source_{thread_id}_{i}',
                    }
                    baggage.update(update_data)
                    
                    # Set operations
                    baggage[f'tag_thread_{thread_id}'] = f'value_{i}'
                    
                    # Get operations
                    session_id = baggage.get('session_id')
                    project = baggage.get('project')
                    
                    # Context operations
                    if i % 5 == 0:
                        ctx = baggage.set_all_baggage()
                        all_baggage = baggage.get_all_baggage(ctx)
                
                results.put({
                    'thread_id': thread_id,
                    'final_session_id': baggage.get('session_id'),
                    'final_project': baggage.get('project'),
                    'success': True
                })
                
            except Exception as e:
                errors.put({
                    'thread_id': thread_id,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        # Start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=baggage_operations_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())
        
        # Verify no errors (some race conditions expected but no crashes)
        assert len(all_errors) == 0, f"Errors in baggage operations: {all_errors}"
        assert len(all_results) == num_threads

    def test_linking_operations_thread_safety(self):
        """Test thread safety of link/unlink operations"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "linking-test-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                tracer = HoneyHiveTracer()
                
                results = queue.Queue()
                errors = queue.Queue()
                num_threads = 10
                
                def linking_operations_thread(thread_id):
                    try:
                        for i in range(10):
                            time.sleep(random.uniform(0.001, 0.01))
                            
                            # Create carrier
                            carrier = {
                                'baggage': f'session_id=thread_{thread_id}_session_{i}',
                                'traceparent': f'00-{thread_id:032d}-{i:016d}-01'
                            }
                            
                            # Link operation
                            token = tracer.link(carrier)
                            
                            # Some operations while linked
                            tracer.add_tags({f'linked_thread_{thread_id}': f'iteration_{i}'})
                            
                            # Inject operation
                            inject_carrier = {}
                            tracer.inject(inject_carrier)
                            
                            # Unlink operation
                            if token:
                                tracer.unlink(token)
                        
                        results.put({
                            'thread_id': thread_id,
                            'success': True
                        })
                        
                    except Exception as e:
                        errors.put({
                            'thread_id': thread_id,
                            'error': str(e),
                            'type': type(e).__name__
                        })
                
                # Start threads
                threads = []
                for i in range(num_threads):
                    thread = threading.Thread(target=linking_operations_thread, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join(timeout=30)
                
                # Check results
                all_results = []
                while not results.empty():
                    all_results.append(results.get())
                
                all_errors = []
                while not errors.empty():
                    all_errors.append(errors.get())
                
                # Verify no errors
                assert len(all_errors) == 0, f"Errors in linking operations: {all_errors}"
                assert len(all_results) == num_threads

    def test_memory_consistency_under_load(self):
        """Test memory consistency under high concurrent load"""
        with patch.dict(os.environ, {
            'HH_API_KEY': 'test_key',
            'HH_PROJECT': 'test_project'
        }):
            with patch('honeyhive.tracer.HoneyHive') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.object.session_id = "memory-test-session"
                mock_sdk.session.start_session.return_value = mock_response
                
                # Create tracer
                tracer = HoneyHiveTracer()
                
                # Track memory consistency
                consistency_results = queue.Queue()
                errors = queue.Queue()
                num_threads = 25
                
                def memory_stress_thread(thread_id):
                    try:
                        local_inconsistencies = 0
                        
                        for i in range(50):
                            # Rapid operations that might cause inconsistencies
                            tracer.add_tags({f'stress_{thread_id}_{i}': str(i)})
                            
                            # Check consistency
                            expected_tag = f'stress_{thread_id}_{i}'
                            if expected_tag not in tracer.tags:
                                local_inconsistencies += 1
                            
                            # Baggage operations
                            baggage_snapshot = tracer.baggage.get_all_baggage()
                            if 'session_id' not in baggage_snapshot:
                                local_inconsistencies += 1
                            
                            # Very small delay to increase race chances
                            if i % 10 == 0:
                                time.sleep(0.0001)
                        
                        consistency_results.put({
                            'thread_id': thread_id,
                            'inconsistencies': local_inconsistencies,
                            'success': True
                        })
                        
                    except Exception as e:
                        errors.put({
                            'thread_id': thread_id,
                            'error': str(e),
                            'type': type(e).__name__
                        })
                
                # Start high-load threads
                threads = []
                for i in range(num_threads):
                    thread = threading.Thread(target=memory_stress_thread, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join(timeout=60)  # Longer timeout for stress test
                
                # Check results
                all_results = []
                while not consistency_results.empty():
                    all_results.append(consistency_results.get())
                
                all_errors = []
                while not errors.empty():
                    all_errors.append(errors.get())
                
                # Verify no errors
                assert len(all_errors) == 0, f"Errors under memory stress: {all_errors}"
                assert len(all_results) == num_threads
                
                # Check for major inconsistencies (some minor ones might be acceptable)
                total_inconsistencies = sum(r['inconsistencies'] for r in all_results)
                # Allow some inconsistencies but not too many
                assert total_inconsistencies < num_threads * 5, f"Too many inconsistencies: {total_inconsistencies}"