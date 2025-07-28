import pytest
import asyncio
import time
import concurrent.futures
from unittest.mock import patch, MagicMock, Mock
from honeyhive.tracer.custom import trace, atrace, enrich_span, instrumentor


class TestAsyncDecorators:
    """Comprehensive tests for async decorator functionality with real async operations"""

    @pytest.mark.asyncio
    async def test_atrace_basic_functionality(self):
        """Test basic atrace decorator functionality"""
        @atrace(event_type="tool", metadata={'test': 'basic'})
        async def async_function(x, y=10):
            await asyncio.sleep(0.01)
            return x + y
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await async_function(5, y=15)
            
            assert result == 20
            mock_tracer.start_as_current_span.assert_called_once_with('async_function')
            # Verify span attributes were set
            mock_span.set_attribute.assert_any_call('honeyhive_event_type', 'tool')
            mock_span.set_attribute.assert_any_call('honeyhive_metadata.test', 'basic')

    @pytest.mark.asyncio
    async def test_atrace_with_exception_handling(self):
        """Test atrace decorator exception handling"""
        @atrace(event_type="tool")
        async def failing_async_function():
            await asyncio.sleep(0.01)
            raise ValueError("Async test error")
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            with pytest.raises(ValueError, match="Async test error"):
                await failing_async_function()
            
            # Verify error was captured
            mock_span.set_attribute.assert_any_call('honeyhive_error', 'Async test error')

    @pytest.mark.asyncio
    async def test_atrace_with_concurrent_execution(self):
        """Test atrace decorator with concurrent async operations"""
        call_count = 0
        
        @atrace(event_type="chain", tags={'concurrent': 'true'})
        async def concurrent_async_function(worker_id, delay=0.01):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(delay)
            return f"worker_{worker_id}_result"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Execute 10 concurrent operations
            tasks = [concurrent_async_function(i, 0.01) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # Verify all operations completed
            assert len(results) == 10
            assert call_count == 10
            
            # Verify each result is correct
            for i, result in enumerate(results):
                assert result == f"worker_{i}_result"
            
            # Verify tracer was called for each operation
            assert mock_tracer.start_as_current_span.call_count == 10

    @pytest.mark.asyncio
    async def test_atrace_with_nested_async_calls(self):
        """Test atrace decorator with nested async calls"""
        @atrace(event_type="tool", event_name="outer_function")
        async def outer_async_function(depth):
            await asyncio.sleep(0.001)
            if depth > 0:
                return await inner_async_function(depth - 1)
            return f"depth_{depth}"
        
        @atrace(event_type="tool", event_name="inner_function")
        async def inner_async_function(depth):
            await asyncio.sleep(0.001)
            if depth > 0:
                return await outer_async_function(depth - 1)
            return f"inner_depth_{depth}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await outer_async_function(3)
            
            # Should complete successfully
            assert "depth_0" in result or "inner_depth_0" in result
            
            # Should have traced multiple function calls
            assert mock_tracer.start_as_current_span.call_count >= 3

    @pytest.mark.asyncio
    async def test_atrace_with_real_io_operations(self):
        """Test atrace decorator with real I/O operations"""
        @atrace(event_type="tool", metadata={'io': 'file'})
        async def async_file_operation(filename, content):
            # Simulate async file I/O
            await asyncio.sleep(0.01)  # Simulate I/O delay
            
            # Mock file operations
            return f"wrote_{len(content)}_bytes_to_{filename}"
        
        @atrace(event_type="tool", metadata={'io': 'network'})
        async def async_network_operation(url, timeout=1.0):
            # Simulate async network I/O
            await asyncio.sleep(min(timeout, 0.05))  # Simulate network delay
            
            return f"fetched_data_from_{url}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Execute I/O operations concurrently
            file_task = async_file_operation("test.txt", "hello world")
            network_task = async_network_operation("https://example.com", 0.02)
            
            file_result, network_result = await asyncio.gather(file_task, network_task)
            
            assert "wrote_11_bytes_to_test.txt" == file_result
            assert "fetched_data_from_https://example.com" == network_result
            
            # Verify both operations were traced
            assert mock_tracer.start_as_current_span.call_count == 2

    @pytest.mark.asyncio
    async def test_atrace_with_asyncio_primitives(self):
        """Test atrace decorator with asyncio primitives (locks, queues, etc.)"""
        lock = asyncio.Lock()
        queue = asyncio.Queue()
        event = asyncio.Event()
        
        @atrace(event_type="tool", tags={'primitive': 'lock'})
        async def locked_operation(worker_id):
            async with lock:
                await asyncio.sleep(0.01)  # Critical section
                return f"worker_{worker_id}_completed"
        
        @atrace(event_type="tool", tags={'primitive': 'queue'})
        async def queue_producer(items):
            for item in items:
                await queue.put(item)
                await asyncio.sleep(0.001)
            await queue.put(None)  # Sentinel
            return len(items)
        
        @atrace(event_type="tool", tags={'primitive': 'queue'})
        async def queue_consumer():
            results = []
            while True:
                item = await queue.get()
                if item is None:
                    break
                results.append(item)
                queue.task_done()
            return results
        
        @atrace(event_type="tool", tags={'primitive': 'event'})
        async def event_waiter():
            await event.wait()
            return "event_received"
        
        @atrace(event_type="tool", tags={'primitive': 'event'})
        async def event_setter():
            await asyncio.sleep(0.02)
            event.set()
            return "event_set"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Test locked operations
            lock_tasks = [locked_operation(i) for i in range(3)]
            lock_results = await asyncio.gather(*lock_tasks)
            assert len(lock_results) == 3
            
            # Test queue operations
            producer_task = queue_producer(['item1', 'item2', 'item3'])
            consumer_task = queue_consumer()
            
            produced_count, consumed_items = await asyncio.gather(producer_task, consumer_task)
            assert produced_count == 3
            assert consumed_items == ['item1', 'item2', 'item3']
            
            # Test event operations
            waiter_task = event_waiter()
            setter_task = event_setter()
            
            wait_result, set_result = await asyncio.gather(waiter_task, setter_task)
            assert wait_result == "event_received"
            assert set_result == "event_set"
            
            # Verify all operations were traced
            expected_calls = 3 + 2 + 2  # lock + queue + event operations
            assert mock_tracer.start_as_current_span.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_atrace_performance_under_load(self):
        """Test atrace decorator performance under high load"""
        @atrace(event_type="tool", metadata={'load_test': 'true'})
        async def high_load_function(batch_id, item_id):
            # Minimal async work to test overhead
            await asyncio.sleep(0.001)
            return f"batch_{batch_id}_item_{item_id}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            start_time = time.time()
            
            # Create many concurrent tasks
            batch_size = 50
            num_batches = 4
            all_tasks = []
            
            for batch_id in range(num_batches):
                batch_tasks = [
                    high_load_function(batch_id, item_id) 
                    for item_id in range(batch_size)
                ]
                all_tasks.extend(batch_tasks)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*all_tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify all operations completed
            assert len(results) == batch_size * num_batches
            
            # Verify performance is reasonable (should complete in under 5 seconds)
            assert total_time < 5.0, f"Operations took too long: {total_time}s"
            
            # Verify all operations were traced
            expected_calls = batch_size * num_batches
            assert mock_tracer.start_as_current_span.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_atrace_with_context_variables(self):
        """Test atrace decorator with context variables"""
        import contextvars
        
        # Create context variable
        request_id = contextvars.ContextVar('request_id')
        
        @atrace(event_type="tool", metadata={'context_test': 'true'})
        async def context_aware_function():
            req_id = request_id.get('unknown')
            await asyncio.sleep(0.01)
            return f"processed_request_{req_id}"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Set context variable and run function
            request_id.set('12345')
            result = await context_aware_function()
            
            assert result == "processed_request_12345"
            mock_tracer.start_as_current_span.assert_called_once()

    @pytest.mark.asyncio
    async def test_atrace_with_cancellation(self):
        """Test atrace decorator with task cancellation"""
        @atrace(event_type="tool", tags={'cancellable': 'true'})
        async def cancellable_function():
            try:
                await asyncio.sleep(10)  # Long operation
                return "completed"
            except asyncio.CancelledError:
                return "cancelled"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Start task and cancel it
            task = asyncio.create_task(cancellable_function())
            await asyncio.sleep(0.01)  # Let it start
            task.cancel()
            
            try:
                result = await task
                # If we get here, cancellation was handled gracefully
                assert result == "cancelled"
            except asyncio.CancelledError:
                # Cancellation propagated (also acceptable)
                pass
            
            # Verify tracer was called
            mock_tracer.start_as_current_span.assert_called_once()

    @pytest.mark.asyncio
    async def test_mixed_sync_async_tracing(self):
        """Test mixing sync and async traced functions"""
        @trace(event_type="tool", metadata={'type': 'sync'})
        def sync_function(x):
            time.sleep(0.01)  # Simulate work
            return x * 2
        
        @atrace(event_type="tool", metadata={'type': 'async'})
        async def async_function(x):
            await asyncio.sleep(0.01)  # Simulate async work
            # Call sync function from async context
            sync_result = sync_function(x)
            return sync_result + 1
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await async_function(5)
            
            assert result == 11  # (5 * 2) + 1
            
            # Both sync and async functions should be traced
            assert mock_tracer.start_as_current_span.call_count == 2

    @pytest.mark.asyncio
    async def test_atrace_with_thread_pool_executor(self):
        """Test atrace decorator with thread pool executor"""
        @atrace(event_type="tool", metadata={'executor': 'thread_pool'})
        async def thread_pool_operation(numbers):
            loop = asyncio.get_event_loop()
            
            def cpu_bound_task(n):
                # Simulate CPU-bound work
                result = sum(i * i for i in range(n))
                return result
            
            # Execute CPU-bound tasks in thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                tasks = [
                    loop.run_in_executor(executor, cpu_bound_task, n)
                    for n in numbers
                ]
                results = await asyncio.gather(*tasks)
            
            return sum(results)
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            result = await thread_pool_operation([100, 200, 300])
            
            # Verify calculation is correct
            expected = sum(sum(i * i for i in range(n)) for n in [100, 200, 300])
            assert result == expected
            
            # Verify tracing occurred
            mock_tracer.start_as_current_span.assert_called_once()

    @pytest.mark.asyncio
    async def test_atrace_with_enrich_span(self):
        """Test atrace decorator combined with enrich_span"""
        @atrace(event_type="model", metadata={'enrichment_test': 'true'})
        async def enriched_async_function(prompt, temperature=0.7):
            await asyncio.sleep(0.01)
            
            # Enrich span with additional data during execution
            enrich_span(
                inputs={'prompt': prompt, 'temperature': temperature},
                metadata={'processing_stage': 'tokenization'}
            )
            
            await asyncio.sleep(0.01)
            
            # More enrichment
            enrich_span(
                metadata={'processing_stage': 'generation'},
                metrics={'tokens_generated': 150}
            )
            
            result = f"Generated response for: {prompt[:20]}..."
            
            # Final enrichment
            enrich_span(
                outputs={'response': result},
                metrics={'completion_time': 0.02}
            )
            
            return result
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            with patch('honeyhive.tracer.custom.otel_trace.get_current_span', return_value=mock_span):
                result = await enriched_async_function("Test prompt for enrichment", 0.8)
            
            assert "Generated response for: Test prompt for enr..." == result
            
            # Verify span was enriched multiple times
            mock_tracer.start_as_current_span.assert_called_once()
            # enrich_span calls should have set additional attributes
            assert mock_span.set_attribute.call_count > 5  # Initial + enrichments

    @pytest.mark.asyncio
    async def test_atrace_error_boundary_behavior(self):
        """Test atrace decorator error boundary behavior"""
        @atrace(event_type="tool", metadata={'error_boundary': 'true'})
        async def error_boundary_function(should_fail=False):
            await asyncio.sleep(0.01)
            
            if should_fail:
                raise RuntimeError("Intentional failure")
            
            return "success"
        
        with patch.object(instrumentor, '_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
            
            # Test successful case
            success_result = await error_boundary_function(False)
            assert success_result == "success"
            
            # Test failure case
            with pytest.raises(RuntimeError, match="Intentional failure"):
                await error_boundary_function(True)
            
            # Verify both cases were traced
            assert mock_tracer.start_as_current_span.call_count == 2
            
            # Verify error was captured in the failing case
            error_calls = [call for call in mock_span.set_attribute.call_args_list 
                          if 'honeyhive_error' in str(call)]
            assert len(error_calls) >= 1