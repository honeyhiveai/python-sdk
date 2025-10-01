"""
Memory Profiler Module

This module provides memory usage monitoring and analysis for tracer
performance benchmarks, following Agent OS production code standards.
"""

import logging
import psutil
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MemoryProfiler:
    """Memory usage profiler for tracer performance analysis.
    
    Monitors memory consumption patterns during benchmark execution to measure
    tracer memory overhead and detect potential memory leaks. Implements
    north-star metric #6 (Memory Overhead).
    
    :param process_pid: Process ID to monitor (defaults to current process)
    :type process_pid: Optional[int]
    
    Example:
        >>> profiler = MemoryProfiler()
        >>> profiler.start_monitoring()
        >>> # ... perform operations ...
        >>> stats = profiler.stop_monitoring()
        >>> print(f"Peak memory: {stats['peak_memory_mb']:.1f}MB")
    """
    
    def __init__(self, process_pid: Optional[int] = None) -> None:
        """Initialize memory profiler.
        
        :param process_pid: Process ID to monitor, defaults to current process
        :type process_pid: Optional[int]
        """
        self.process = psutil.Process(process_pid)
        self.monitoring_active: bool = False
        self.samples: List[Dict[str, Any]] = []
        self.baseline_memory: Optional[float] = None
        self.peak_memory: float = 0.0
        self.start_time: Optional[float] = None
        
    def start_monitoring(self) -> None:
        """Start memory monitoring.
        
        Records baseline memory usage and begins periodic sampling.
        """
        if self.monitoring_active:
            logger.warning("Memory monitoring already active")
            return
            
        self.monitoring_active = True
        self.samples = []
        self.start_time = time.perf_counter()
        
        # Record baseline memory
        memory_info = self.process.memory_info()
        self.baseline_memory = memory_info.rss / (1024 * 1024)  # Convert to MB
        self.peak_memory = self.baseline_memory
        
        logger.debug(f"🧠 Memory monitoring started - baseline: {self.baseline_memory:.1f}MB")
        
    def sample_memory(self, operation_label: str) -> float:
        """Sample current memory usage with a label.
        
        :param operation_label: Label for this memory sample
        :type operation_label: str
        :return: Current memory usage in MB
        :rtype: float
        
        Example:
            >>> profiler = MemoryProfiler()
            >>> memory = profiler.sample_memory("before_api_call")
            >>> print(f"Memory usage: {memory:.1f}MB")
        """
        if not self.monitoring_active:
            logger.warning("Memory monitoring not active, starting automatically")
            self.start_monitoring()
            
        try:
            memory_info = self.process.memory_info()
            current_memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
            
            # Update peak memory
            if current_memory_mb > self.peak_memory:
                self.peak_memory = current_memory_mb
                
            # Record sample
            sample = {
                'timestamp': time.perf_counter(),
                'memory_mb': current_memory_mb,
                'operation': operation_label,
                'rss_bytes': memory_info.rss,
                'vms_bytes': memory_info.vms,
            }
            self.samples.append(sample)
            
            logger.debug(f"🧠 Memory sample '{operation_label}': {current_memory_mb:.1f}MB")
            return current_memory_mb
            
        except psutil.NoSuchProcess:
            logger.error("Process no longer exists for memory monitoring")
            return 0.0
        except Exception as e:
            logger.error(f"Error sampling memory: {e}")
            return 0.0
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop memory monitoring and return analysis.
        
        :return: Dictionary containing memory usage analysis
        :rtype: Dict[str, Any]
        
        Example:
            >>> profiler = MemoryProfiler()
            >>> profiler.start_monitoring()
            >>> # ... operations ...
            >>> stats = profiler.stop_monitoring()
            >>> overhead = stats['memory_overhead_percent']
        """
        if not self.monitoring_active:
            logger.warning("Memory monitoring not active")
            return self._empty_stats()
            
        self.monitoring_active = False
        
        if not self.samples or self.baseline_memory is None:
            logger.debug("No memory samples collected (expected for fast concurrent operations)")
            return self._empty_stats()
            
        # Calculate statistics
        memory_values = [sample['memory_mb'] for sample in self.samples]
        
        # Memory overhead calculations
        memory_overhead_mb = self.peak_memory - self.baseline_memory
        memory_overhead_percent = (memory_overhead_mb / self.baseline_memory) * 100 if self.baseline_memory > 0 else 0.0
        
        # Additional statistics
        avg_memory = sum(memory_values) / len(memory_values)
        min_memory = min(memory_values)
        max_memory = max(memory_values)
        
        stats = {
            'baseline_memory_mb': self.baseline_memory,
            'peak_memory_mb': self.peak_memory,
            'memory_overhead_mb': memory_overhead_mb,
            'memory_overhead_percent': memory_overhead_percent,
            'avg_memory_mb': avg_memory,
            'min_memory_mb': min_memory,
            'max_memory_mb': max_memory,
            'total_samples': len(self.samples),
            'monitoring_duration_s': time.perf_counter() - (self.start_time or 0),
            'samples': self.samples,
        }
        
        logger.debug(
            f"🧠 Memory monitoring stopped - "
            f"baseline: {self.baseline_memory:.1f}MB, "
            f"peak: {self.peak_memory:.1f}MB, "
            f"overhead: {memory_overhead_percent:.1f}%"
        )
        
        return stats
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics when monitoring fails.
        
        :return: Dictionary with zero/None values for all statistics
        :rtype: Dict[str, Any]
        """
        return {
            'baseline_memory_mb': 0.0,
            'peak_memory_mb': 0.0,
            'memory_overhead_mb': 0.0,
            'memory_overhead_percent': 0.0,
            'avg_memory_mb': 0.0,
            'min_memory_mb': 0.0,
            'max_memory_mb': 0.0,
            'total_samples': 0,
            'monitoring_duration_s': 0.0,
            'samples': [],
        }
    
    def get_current_memory(self) -> float:
        """Get current memory usage without recording a sample.
        
        :return: Current memory usage in MB
        :rtype: float
        """
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Error getting current memory: {e}")
            return 0.0
    
    def reset(self) -> None:
        """Reset profiler state for new monitoring session."""
        self.monitoring_active = False
        self.samples = []
        self.baseline_memory = None
        self.peak_memory = 0.0
        self.start_time = None
        logger.debug("🧠 Memory profiler reset")
