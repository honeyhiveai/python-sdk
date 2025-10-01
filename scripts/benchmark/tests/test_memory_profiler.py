"""
Unit tests for memory profiler module.

Tests the MemoryProfiler class for memory usage monitoring.
"""

import pytest
from unittest.mock import Mock, patch
from ..monitoring.memory_profiler import MemoryProfiler


class TestMemoryProfiler:
    """Test cases for MemoryProfiler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('psutil.Process') as mock_process:
            # Mock the process and memory info
            mock_memory_info = Mock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100MB in bytes
            mock_memory_info.vms = 200 * 1024 * 1024  # 200MB in bytes
            
            mock_process.return_value.memory_info.return_value = mock_memory_info
            
            self.profiler = MemoryProfiler()
            self.mock_process = mock_process.return_value
            self.mock_memory_info = mock_memory_info
    
    def test_initialization(self):
        """Test that MemoryProfiler initializes correctly."""
        assert self.profiler is not None
        assert self.profiler.monitoring_active is False
        assert self.profiler.samples == []
        assert self.profiler.baseline_memory is None
        assert self.profiler.peak_memory == 0.0
        assert self.profiler.start_time is None
    
    def test_start_monitoring(self):
        """Test starting memory monitoring."""
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        assert self.profiler.monitoring_active is True
        assert self.profiler.baseline_memory == 100.0  # 100MB
        assert self.profiler.peak_memory == 100.0
        assert self.profiler.start_time == 1000.0
        assert len(self.profiler.samples) == 0
    
    def test_start_monitoring_already_active(self):
        """Test starting monitoring when already active."""
        self.profiler.monitoring_active = True
        
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        # Should not change the start time if already active
        assert self.profiler.start_time is None
    
    def test_sample_memory(self):
        """Test memory sampling."""
        # Start monitoring first
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        # Sample memory
        with patch('time.perf_counter', return_value=1001.0):
            memory = self.profiler.sample_memory("test_operation")
        
        assert memory == 100.0  # 100MB
        assert len(self.profiler.samples) == 1
        
        sample = self.profiler.samples[0]
        assert sample['memory_mb'] == 100.0
        assert sample['operation'] == "test_operation"
        assert sample['timestamp'] == 1001.0
        assert sample['rss_bytes'] == 100 * 1024 * 1024
        assert sample['vms_bytes'] == 200 * 1024 * 1024
    
    def test_sample_memory_not_monitoring(self):
        """Test memory sampling when not monitoring (should auto-start)."""
        with patch('time.perf_counter', return_value=1000.0):
            memory = self.profiler.sample_memory("test_operation")
        
        assert memory == 100.0
        assert self.profiler.monitoring_active is True
        assert len(self.profiler.samples) == 1
    
    def test_sample_memory_updates_peak(self):
        """Test that memory sampling updates peak memory."""
        # Start monitoring
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        # Mock higher memory usage
        self.mock_memory_info.rss = 150 * 1024 * 1024  # 150MB
        
        with patch('time.perf_counter', return_value=1001.0):
            memory = self.profiler.sample_memory("high_memory_operation")
        
        assert memory == 150.0
        assert self.profiler.peak_memory == 150.0
    
    def test_stop_monitoring(self):
        """Test stopping memory monitoring."""
        # Start monitoring and add some samples
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        with patch('time.perf_counter', return_value=1001.0):
            self.profiler.sample_memory("operation1")
        
        # Mock higher memory for peak
        self.mock_memory_info.rss = 120 * 1024 * 1024  # 120MB
        with patch('time.perf_counter', return_value=1002.0):
            self.profiler.sample_memory("operation2")
        
        # Stop monitoring
        with patch('time.perf_counter', return_value=1010.0):
            stats = self.profiler.stop_monitoring()
        
        assert self.profiler.monitoring_active is False
        assert stats['baseline_memory_mb'] == 100.0
        assert stats['peak_memory_mb'] == 120.0
        assert stats['memory_overhead_mb'] == 20.0
        assert stats['memory_overhead_percent'] == 20.0
        assert stats['avg_memory_mb'] == 110.0  # (100 + 120) / 2
        assert stats['min_memory_mb'] == 100.0
        assert stats['max_memory_mb'] == 120.0
        assert stats['total_samples'] == 2
        assert stats['monitoring_duration_s'] == 10.0
    
    def test_stop_monitoring_not_active(self):
        """Test stopping monitoring when not active."""
        stats = self.profiler.stop_monitoring()
        
        # Should return empty stats
        assert stats['baseline_memory_mb'] == 0.0
        assert stats['peak_memory_mb'] == 0.0
        assert stats['memory_overhead_mb'] == 0.0
        assert stats['memory_overhead_percent'] == 0.0
        assert stats['total_samples'] == 0
    
    def test_stop_monitoring_no_samples(self):
        """Test stopping monitoring with no samples."""
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        # Stop immediately without sampling
        stats = self.profiler.stop_monitoring()
        
        # Should return empty stats
        assert stats['baseline_memory_mb'] == 0.0
        assert stats['total_samples'] == 0
    
    def test_get_current_memory(self):
        """Test getting current memory without sampling."""
        memory = self.profiler.get_current_memory()
        assert memory == 100.0
        
        # Should not add to samples
        assert len(self.profiler.samples) == 0
    
    def test_reset(self):
        """Test resetting profiler state."""
        # Set up some state
        self.profiler.monitoring_active = True
        self.profiler.samples = [{'test': 'data'}]
        self.profiler.baseline_memory = 100.0
        self.profiler.peak_memory = 150.0
        self.profiler.start_time = 1000.0
        
        self.profiler.reset()
        
        assert self.profiler.monitoring_active is False
        assert self.profiler.samples == []
        assert self.profiler.baseline_memory is None
        assert self.profiler.peak_memory == 0.0
        assert self.profiler.start_time is None
    
    @patch('psutil.Process')
    def test_process_error_handling(self, mock_process_class):
        """Test error handling when process operations fail."""
        # Mock process to raise exception
        mock_process_class.side_effect = Exception("Process error")
        
        # Should handle the error gracefully
        with pytest.raises(Exception):
            MemoryProfiler()
    
    def test_sample_memory_process_error(self):
        """Test error handling during memory sampling."""
        with patch('time.perf_counter', return_value=1000.0):
            self.profiler.start_monitoring()
        
        # Mock memory_info to raise exception
        self.mock_process.memory_info.side_effect = Exception("Memory error")
        
        memory = self.profiler.sample_memory("error_operation")
        
        # Should return 0.0 on error
        assert memory == 0.0
        assert len(self.profiler.samples) == 0
