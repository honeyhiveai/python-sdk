import pytest
import asyncio
import time
from unittest.mock import patch, Mock, MagicMock
from honeyhive.tracer.performance import (
    PerformanceMetrics,
    PerformanceMonitor,
    performance_trace,
    perf_trace,
    performance_monitor,
    monitor,
    get_performance_summary,
    reset_performance_metrics
)


class TestPerformanceMetrics:
    """Test suite for PerformanceMetrics class"""

    def test_performance_metrics_initialization(self):
        """Test PerformanceMetrics initialization with default values"""
        metrics = PerformanceMetrics()
        
        assert metrics.execution_times == []
        assert metrics.memory_usage == []
        assert metrics.cpu_usage == []
        assert metrics.call_count == 0
        assert metrics.total_time == 0.0
        assert metrics.min_time == float('inf')
        assert metrics.max_time == 0.0
        assert metrics.avg_time == 0.0
        assert metrics.last_called is None

    def test_add_execution_single_measurement(self):
        """Test adding a single execution measurement"""
        metrics = PerformanceMetrics()
        
        metrics.add_execution(0.5, 10.0, 15.0)
        
        assert len(metrics.execution_times) == 1
        assert metrics.execution_times[0] == 0.5
        assert metrics.memory_usage[0] == 10.0
        assert metrics.cpu_usage[0] == 15.0
        assert metrics.call_count == 1
        assert metrics.total_time == 0.5
        assert metrics.min_time == 0.5
        assert metrics.max_time == 0.5
        assert metrics.avg_time == 0.5
        assert metrics.last_called is not None

    def test_add_execution_multiple_measurements(self):
        """Test adding multiple execution measurements"""
        metrics = PerformanceMetrics()
        
        metrics.add_execution(0.5, 10.0, 15.0)
        metrics.add_execution(1.0, 20.0, 25.0)
        metrics.add_execution(0.3, 5.0, 10.0)
        
        assert len(metrics.execution_times) == 3
        assert metrics.call_count == 3
        assert metrics.total_time == 1.8
        assert metrics.min_time == 0.3
        assert metrics.max_time == 1.0
        assert metrics.avg_time == 0.6

    def test_add_execution_memory_limit(self):
        """Test that execution lists don't grow beyond 1000 items"""
        metrics = PerformanceMetrics()
        
        # Add 1001 measurements
        for i in range(1001):
            metrics.add_execution(i * 0.001, i * 0.1, i * 0.01)
        
        # Should only keep last 1000 measurements
        assert len(metrics.execution_times) == 1000
        assert len(metrics.memory_usage) == 1000
        assert len(metrics.cpu_usage) == 1000
        assert metrics.call_count == 1001  # Call count should still be accurate
        
        # First measurement should be removed, last should be present
        assert 0.0 not in metrics.execution_times
        assert 1.0 in metrics.execution_times

    def test_get_percentile_time(self):
        """Test percentile calculation for execution times"""
        metrics = PerformanceMetrics()
        
        # Add measurements: 0.1, 0.2, 0.3, 0.4, 0.5
        for i in range(1, 6):
            metrics.add_execution(i * 0.1, 0, 0)
        
        assert abs(metrics.get_percentile(50, 'time') - 0.3) < 1e-10  # Median (handle floating point precision)
        assert metrics.get_percentile(100, 'time') == 0.5  # Max
        assert metrics.get_percentile(0, 'time') == 0.1   # Min

    def test_get_percentile_memory(self):
        """Test percentile calculation for memory usage"""
        metrics = PerformanceMetrics()
        
        # Add measurements with different memory values
        for i in range(1, 6):
            metrics.add_execution(0.1, i * 10.0, 0)
        
        assert metrics.get_percentile(50, 'memory') == 30.0  # Median
        assert metrics.get_percentile(100, 'memory') == 50.0  # Max

    def test_get_percentile_cpu(self):
        """Test percentile calculation for CPU usage"""
        metrics = PerformanceMetrics()
        
        # Add measurements with different CPU values
        for i in range(1, 6):
            metrics.add_execution(0.1, 0, i * 5.0)
        
        assert metrics.get_percentile(50, 'cpu') == 15.0  # Median
        assert metrics.get_percentile(100, 'cpu') == 25.0  # Max

    def test_get_percentile_empty_data(self):
        """Test percentile calculation with empty data"""
        metrics = PerformanceMetrics()
        
        assert metrics.get_percentile(50, 'time') == 0.0
        assert metrics.get_percentile(50, 'memory') == 0.0
        assert metrics.get_percentile(50, 'cpu') == 0.0

    def test_get_percentile_invalid_metric_type(self):
        """Test percentile calculation with invalid metric type"""
        metrics = PerformanceMetrics()
        metrics.add_execution(0.5, 10.0, 15.0)
        
        with pytest.raises(ValueError, match="metric_type must be"):
            metrics.get_percentile(50, 'invalid')

    def test_get_summary_with_data(self):
        """Test get_summary with performance data"""
        metrics = PerformanceMetrics()
        
        metrics.add_execution(0.5, 10.0, 15.0)
        metrics.add_execution(1.0, 20.0, 25.0)
        
        summary = metrics.get_summary()
        
        assert summary['call_count'] == 2
        assert summary['total_time'] == 1.5
        assert summary['avg_time'] == 0.75
        assert summary['min_time'] == 0.5
        assert summary['max_time'] == 1.0
        assert summary['median_time'] == 0.75
        assert summary['avg_memory_mb'] == 15.0
        assert summary['avg_cpu_percent'] == 20.0
        assert 'p95_time' in summary
        assert 'p99_time' in summary
        assert 'last_called' in summary

    def test_get_summary_empty_data(self):
        """Test get_summary with no performance data"""
        metrics = PerformanceMetrics()
        
        summary = metrics.get_summary()
        
        assert summary == {}


class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor class"""

    def setup_method(self):
        """Reset performance monitor before each test"""
        # Reset the singleton instance and clear its state
        if hasattr(PerformanceMonitor, '_instance') and PerformanceMonitor._instance is not None:
            PerformanceMonitor._instance._metrics.clear()
            PerformanceMonitor._instance._active_timers.clear()
        else:
            PerformanceMonitor._instance = None

    def test_performance_monitor_singleton(self):
        """Test that PerformanceMonitor is a singleton"""
        monitor1 = PerformanceMonitor()
        monitor2 = PerformanceMonitor()
        
        assert monitor1 is monitor2

    def test_start_and_end_timing(self):
        """Test basic timing functionality"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_operation")
        time.sleep(0.01)  # Small delay
        duration = monitor.end_timing("test_operation")
        
        assert duration > 0
        assert duration >= 0.01
        
        # Check that metrics were recorded
        metrics = monitor.get_metrics("test_operation")
        assert metrics.call_count == 1
        assert len(metrics.execution_times) == 1

    def test_end_timing_without_start(self):
        """Test ending timing without starting it"""
        monitor = PerformanceMonitor()
        
        duration = monitor.end_timing("nonexistent_operation")
        
        assert duration == 0.0

    def test_multiple_operations(self):
        """Test tracking multiple operations"""
        monitor = PerformanceMonitor()
        
        # Track two different operations
        monitor.start_timing("op1")
        time.sleep(0.01)
        monitor.end_timing("op1")
        
        monitor.start_timing("op2")
        time.sleep(0.01)
        monitor.end_timing("op2")
        
        # Both operations should be tracked
        assert monitor.get_metrics("op1").call_count == 1
        assert monitor.get_metrics("op2").call_count == 1
        
        all_metrics = monitor.get_all_metrics()
        assert "op1" in all_metrics
        assert "op2" in all_metrics

    def test_reset_metrics_single_operation(self):
        """Test resetting metrics for a single operation"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        monitor.end_timing("test_op")
        
        assert monitor.get_metrics("test_op").call_count == 1
        
        monitor.reset_metrics("test_op")
        
        assert monitor.get_metrics("test_op").call_count == 0

    def test_reset_metrics_all_operations(self):
        """Test resetting all metrics"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("op1")
        monitor.end_timing("op1")
        monitor.start_timing("op2")
        monitor.end_timing("op2")
        
        assert len(monitor.get_all_metrics()) == 2
        
        monitor.reset_metrics()
        
        assert len(monitor.get_all_metrics()) == 0

    def test_context_manager(self):
        """Test performance monitoring using context manager"""
        monitor = PerformanceMonitor()
        
        with monitor.track("context_test") as perf:
            time.sleep(0.01)
            assert perf is monitor
        
        metrics = monitor.get_metrics("context_test")
        assert metrics.call_count == 1
        assert len(metrics.execution_times) == 1

    @patch('honeyhive.tracer.performance.psutil.Process')
    def test_resource_tracking_disabled(self, mock_process):
        """Test timing without resource tracking"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        duration = monitor.end_timing("test_op", track_resources=False)
        
        assert duration > 0
        # psutil.Process should not be called when resource tracking is disabled
        mock_process.assert_not_called()

    @patch('honeyhive.tracer.performance.psutil.Process')
    def test_resource_tracking_enabled(self, mock_process):
        """Test timing with resource tracking"""
        # Reset singleton to ensure clean state
        PerformanceMonitor._instance = None
        
        # Mock the process and its methods
        mock_process_instance = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100 MB in bytes
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process_instance.cpu_percent.return_value = 15.5
        mock_process.return_value = mock_process_instance
        
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        duration = monitor.end_timing("test_op", track_resources=True)
        
        assert duration > 0
        
        # Verify process was created in constructor and resource tracking was attempted
        mock_process.assert_called()
        mock_process_instance.memory_info.assert_called()
        mock_process_instance.cpu_percent.assert_called()


class TestPerformanceTrace:
    """Test suite for performance_trace decorator"""

    def setup_method(self):
        """Reset performance monitor before each test"""
        # Reset the singleton instance and clear its state
        if hasattr(PerformanceMonitor, '_instance') and PerformanceMonitor._instance is not None:
            PerformanceMonitor._instance._metrics.clear()
            PerformanceMonitor._instance._active_timers.clear()
        else:
            PerformanceMonitor._instance = None

    @patch('honeyhive.tracer.performance.enrich_span')
    @patch('honeyhive.tracer.performance.trace')
    def test_performance_trace_sync_function(self, mock_trace_decorator, mock_enrich_span):
        """Test performance_trace decorator on synchronous function"""
        # Mock the trace decorator to return the original function
        mock_trace_decorator.return_value = lambda func: func
        
        @performance_trace(operation_name="test_sync_func")
        def test_function(x, y=10):
            time.sleep(0.01)
            return x + y
        
        result = test_function(5, y=15)
        
        assert result == 20
        
        # Verify trace decorator was called
        mock_trace_decorator.assert_called_once()
        
        # Verify span was enriched with performance data
        mock_enrich_span.assert_called_once()
        call_args = mock_enrich_span.call_args
        assert 'metadata' in call_args.kwargs
        assert 'performance' in call_args.kwargs['metadata']
        
        # Check performance data structure
        perf_data = call_args.kwargs['metadata']['performance']
        assert 'duration_seconds' in perf_data
        assert 'call_count' in perf_data
        assert 'avg_duration' in perf_data

    @pytest.mark.asyncio
    @patch('honeyhive.tracer.performance.enrich_span')
    @patch('honeyhive.tracer.performance.atrace')
    async def test_performance_trace_async_function(self, mock_atrace_decorator, mock_enrich_span):
        """Test performance_trace decorator on asynchronous function"""
        # Mock the atrace decorator to return the original function
        mock_atrace_decorator.return_value = lambda func: func
        
        @performance_trace(operation_name="test_async_func")
        async def async_test_function(x, y=10):
            await asyncio.sleep(0.01)
            return x + y
        
        result = await async_test_function(5, y=15)
        
        assert result == 20
        
        # Verify atrace decorator was called
        mock_atrace_decorator.assert_called_once()
        
        # Verify span was enriched with performance data
        mock_enrich_span.assert_called_once()

    @patch('honeyhive.tracer.performance.enrich_span')
    @patch('honeyhive.tracer.performance.trace')
    def test_performance_trace_with_thresholds(self, mock_trace_decorator, mock_enrich_span):
        """Test performance_trace decorator with threshold alerting"""
        mock_trace_decorator.return_value = lambda func: func
        
        with patch('honeyhive.tracer.performance.logger') as mock_logger:
            @performance_trace(
                time_threshold=0.001,  # Very low threshold
                alert_on_threshold=True
            )
            def slow_function():
                time.sleep(0.01)  # This should exceed threshold
                return "result"
            
            result = slow_function()
            
            assert result == "result"
            
            # Verify warning was logged for threshold violation
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "exceeded time threshold" in warning_call

    @patch('honeyhive.tracer.performance.enrich_span')
    @patch('honeyhive.tracer.performance.trace')
    def test_performance_trace_with_exception(self, mock_trace_decorator, mock_enrich_span):
        """Test performance_trace decorator with function that raises exception"""
        mock_trace_decorator.return_value = lambda func: func
        
        @performance_trace()
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_function()
        
        # Verify span was enriched with performance data even on failure
        mock_enrich_span.assert_called()
        call_args = mock_enrich_span.call_args
        assert 'metadata' in call_args.kwargs
        assert 'performance' in call_args.kwargs['metadata']
        assert call_args.kwargs['metadata']['performance']['failed'] is True
        assert 'error' in call_args.kwargs

    def test_performance_trace_default_operation_name(self):
        """Test that operation name defaults to function name"""
        monitor = PerformanceMonitor()
        
        @performance_trace()
        def my_test_function():
            time.sleep(0.01)
            return "result"
        
        result = my_test_function()
        
        assert result == "result"
        
        # Check that metrics were recorded with function name
        metrics = monitor.get_metrics("my_test_function")
        assert metrics.call_count == 1

    @patch('honeyhive.tracer.performance.psutil.Process')
    def test_performance_trace_memory_tracking(self, mock_process):
        """Test performance_trace decorator with memory tracking"""
        # Mock process and memory info
        mock_process_instance = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 50  # 50 MB initially, 60 MB after
        mock_process_instance.memory_info.side_effect = [
            Mock(rss=1024 * 1024 * 50),  # Start: 50 MB
            Mock(rss=1024 * 1024 * 60)   # End: 60 MB
        ]
        mock_process_instance.cpu_percent.return_value = 25.0
        mock_process.return_value = mock_process_instance
        
        with patch('honeyhive.tracer.performance.enrich_span') as mock_enrich_span, \
             patch('honeyhive.tracer.performance.trace') as mock_trace_decorator:
            
            mock_trace_decorator.return_value = lambda func: func
            
            @performance_trace(track_memory=True, track_cpu=True)
            def memory_function():
                return "result"
            
            result = memory_function()
            
            assert result == "result"
            
            # Verify span was enriched with memory data
            mock_enrich_span.assert_called()
            call_args = mock_enrich_span.call_args
            perf_data = call_args.kwargs['metadata']['performance']
            assert 'memory_used_mb' in perf_data
            assert 'cpu_percent' in perf_data


class TestConvenienceFunctions:
    """Test suite for convenience functions"""

    def setup_method(self):
        """Reset performance monitor before each test"""
        # Reset the singleton instance and clear its state
        if hasattr(PerformanceMonitor, '_instance') and PerformanceMonitor._instance is not None:
            PerformanceMonitor._instance._metrics.clear()
            PerformanceMonitor._instance._active_timers.clear()
        else:
            PerformanceMonitor._instance = None

    def test_get_performance_summary_single_operation(self):
        """Test get_performance_summary for single operation"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        time.sleep(0.01)
        monitor.end_timing("test_op")
        
        summary = get_performance_summary("test_op")
        
        assert 'call_count' in summary
        assert summary['call_count'] == 1

    def test_get_performance_summary_all_operations(self):
        """Test get_performance_summary for all operations"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("op1")
        monitor.end_timing("op1")
        monitor.start_timing("op2")
        monitor.end_timing("op2")
        
        summary = get_performance_summary()
        
        assert "op1" in summary
        assert "op2" in summary

    def test_reset_performance_metrics_function(self):
        """Test reset_performance_metrics function"""
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        monitor.end_timing("test_op")
        
        assert len(monitor.get_all_metrics()) == 1
        
        reset_performance_metrics()
        
        assert len(monitor.get_all_metrics()) == 0

    def test_perf_trace_alias(self):
        """Test that perf_trace is an alias for performance_trace"""
        from honeyhive.tracer.performance import perf_trace, performance_trace
        
        assert perf_trace is performance_trace

    def test_monitor_alias(self):
        """Test that monitor is an alias for performance_monitor.track"""
        monitor = PerformanceMonitor()
        
        with monitor.track("alias_test") as perf:
            time.sleep(0.01)
        
        metrics = monitor.get_metrics("alias_test")
        assert metrics.call_count == 1


class TestEdgeCases:
    """Test suite for edge cases and error conditions"""

    def setup_method(self):
        """Reset performance monitor before each test"""
        # Reset the singleton instance and clear its state
        if hasattr(PerformanceMonitor, '_instance') and PerformanceMonitor._instance is not None:
            PerformanceMonitor._instance._metrics.clear()
            PerformanceMonitor._instance._active_timers.clear()
        else:
            PerformanceMonitor._instance = None

    @patch('honeyhive.tracer.performance.psutil.Process')
    def test_resource_tracking_failure(self, mock_process):
        """Test graceful handling of resource tracking failures"""
        # Mock process to raise exception
        mock_process.side_effect = Exception("psutil error")
        
        monitor = PerformanceMonitor()
        
        monitor.start_timing("test_op")
        # Should not raise exception even if resource tracking fails
        duration = monitor.end_timing("test_op", track_resources=True)
        
        assert duration > 0
        
        # Metrics should still be recorded
        metrics = monitor.get_metrics("test_op")
        assert metrics.call_count == 1

    def test_concurrent_access(self):
        """Test thread safety of performance monitor"""
        import threading
        
        monitor = PerformanceMonitor()
        results = []
        
        def worker(operation_id):
            op_name = f"op_{operation_id}"
            monitor.start_timing(op_name)
            time.sleep(0.01)
            duration = monitor.end_timing(op_name)
            results.append((operation_id, duration))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should be recorded
        assert len(results) == 5
        all_metrics = monitor.get_all_metrics()
        assert len(all_metrics) == 5
        
        # Each operation should have been called once
        for i in range(5):
            assert f"op_{i}" in all_metrics
            assert all_metrics[f"op_{i}"]['call_count'] == 1