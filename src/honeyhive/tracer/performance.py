import time
import threading
import functools
import psutil
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from statistics import mean, median
from contextlib import contextmanager

from opentelemetry import trace as otel_trace
from honeyhive.tracer.custom import enrich_span, trace, atrace

logger = logging.getLogger(__name__)

P = TypeVar('P')
R = TypeVar('R')

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    execution_times: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_called: Optional[float] = None
    
    def add_execution(self, duration: float, memory_mb: float = 0.0, cpu_percent: float = 0.0):
        """Add a new execution measurement"""
        self.execution_times.append(duration)
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.avg_time = self.total_time / self.call_count
        self.last_called = time.time()
        
        # Keep only last 1000 measurements to prevent memory bloat
        if len(self.execution_times) > 1000:
            self.execution_times.pop(0)
            self.memory_usage.pop(0)
            self.cpu_usage.pop(0)
    
    def get_percentile(self, percentile: int, metric_type: str = 'time') -> float:
        """Get percentile of execution times"""
        if metric_type == 'time':
            data = sorted(self.execution_times)
        elif metric_type == 'memory':
            data = sorted(self.memory_usage)
        elif metric_type == 'cpu':
            data = sorted(self.cpu_usage)
        else:
            raise ValueError("metric_type must be 'time', 'memory', or 'cpu'")
            
        if not data:
            return 0.0
            
        index = (percentile / 100.0) * (len(data) - 1)
        if index.is_integer():
            return data[int(index)]
        else:
            lower = data[int(index)]
            upper = data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.execution_times:
            return {}
            
        return {
            'call_count': self.call_count,
            'total_time': self.total_time,
            'avg_time': self.avg_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'median_time': median(self.execution_times) if self.execution_times else 0,
            'p95_time': self.get_percentile(95, 'time'),
            'p99_time': self.get_percentile(99, 'time'),
            'avg_memory_mb': mean(self.memory_usage) if self.memory_usage else 0,
            'avg_cpu_percent': mean(self.cpu_usage) if self.cpu_usage else 0,
            'last_called': self.last_called
        }


class PerformanceMonitor:
    """Global performance monitoring utility"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
            self._active_timers: Dict[str, float] = {}
            self._lock = threading.Lock()
            try:
                self._process = psutil.Process()
            except Exception as e:
                logger.debug(f"Failed to initialize psutil Process: {e}")
                self._process = None
            self._initialized = True
    
    def start_timing(self, operation_name: str) -> None:
        """Start timing an operation"""
        self._active_timers[operation_name] = time.perf_counter()
    
    def end_timing(self, operation_name: str, track_resources: bool = True) -> float:
        """End timing an operation and record metrics"""
        if operation_name not in self._active_timers:
            logger.warning(f"No active timer found for operation: {operation_name}")
            return 0.0
        
        duration = time.perf_counter() - self._active_timers.pop(operation_name)
        
        # Collect resource metrics
        memory_mb = 0.0
        cpu_percent = 0.0
        
        if track_resources and self._process is not None:
            try:
                memory_info = self._process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                cpu_percent = self._process.cpu_percent()
            except Exception as e:
                logger.debug(f"Failed to collect resource metrics: {e}")
        
        # Record metrics
        with self._lock:
            self._metrics[operation_name].add_execution(duration, memory_mb, cpu_percent)
        
        return duration
    
    def get_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Get metrics for a specific operation"""
        return self._metrics.get(operation_name, PerformanceMetrics())
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all tracked operations"""
        return {name: metrics.get_summary() for name, metrics in self._metrics.items()}
    
    def reset_metrics(self, operation_name: Optional[str] = None) -> None:
        """Reset metrics for a specific operation or all operations"""
        with self._lock:
            if operation_name:
                if operation_name in self._metrics:
                    del self._metrics[operation_name]
            else:
                self._metrics.clear()
    
    @contextmanager
    def track(self, operation_name: str, track_resources: bool = True):
        """Context manager for tracking performance"""
        self.start_timing(operation_name)
        try:
            yield self
        finally:
            self.end_timing(operation_name, track_resources)


# Global instance
performance_monitor = PerformanceMonitor()


def performance_trace(
    func: Optional[Callable] = None,
    *,
    operation_name: Optional[str] = None,
    track_memory: bool = True,
    track_cpu: bool = True,
    time_threshold: Optional[float] = None,
    memory_threshold: Optional[float] = None,
    alert_on_threshold: bool = False,
    event_type: str = "tool",
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, Any]] = None
):
    """
    Decorator that combines performance monitoring with tracing.
    
    Args:
        func: Function to decorate
        operation_name: Name for the operation (defaults to function name)
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
        time_threshold: Alert if execution time exceeds this (seconds)
        memory_threshold: Alert if memory usage exceeds this (MB)
        alert_on_threshold: Whether to log alerts when thresholds are exceeded
        event_type: OpenTelemetry event type
        metadata: Additional metadata for the trace
        tags: Tags for the trace
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        if asyncio.iscoroutinefunction(func):
            @atrace(event_type=event_type, metadata=metadata, tags=tags)
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                start_memory = 0.0
                start_cpu = 0.0
                
                # Collect baseline metrics
                process = None
                if track_memory or track_cpu:
                    try:
                        process = psutil.Process()
                        if track_memory:
                            start_memory = process.memory_info().rss / 1024 / 1024
                        if track_cpu:
                            start_cpu = process.cpu_percent()
                    except Exception as e:
                        logger.debug(f"Failed to collect baseline metrics: {e}")
                        process = None
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Calculate performance metrics
                    duration = time.perf_counter() - start_time
                    end_memory = start_memory
                    cpu_usage = 0.0
                    
                    if track_memory or track_cpu and process is not None:
                        try:
                            if track_memory:
                                end_memory = process.memory_info().rss / 1024 / 1024
                            if track_cpu:
                                cpu_usage = process.cpu_percent()
                        except Exception as e:
                            logger.debug(f"Failed to collect end metrics: {e}")
                    
                    memory_used = end_memory - start_memory if track_memory else 0.0
                    
                    # Record metrics
                    performance_monitor._metrics[op_name].add_execution(
                        duration, memory_used, cpu_usage
                    )
                    
                    # Check thresholds and alert if needed
                    if alert_on_threshold:
                        if time_threshold and duration > time_threshold:
                            logger.warning(f"Function {op_name} exceeded time threshold: {duration:.3f}s > {time_threshold}s")
                        if memory_threshold and memory_used > memory_threshold:
                            logger.warning(f"Function {op_name} exceeded memory threshold: {memory_used:.1f}MB > {memory_threshold}MB")
                    
                    # Enrich span with performance data
                    perf_data = {
                        'duration_seconds': duration,
                        'call_count': performance_monitor._metrics[op_name].call_count,
                        'avg_duration': performance_monitor._metrics[op_name].avg_time
                    }
                    
                    if track_memory:
                        perf_data['memory_used_mb'] = memory_used
                    if track_cpu:
                        perf_data['cpu_percent'] = cpu_usage
                    
                    enrich_span(metadata={'performance': perf_data})
                    
                    return result
                    
                except Exception as e:
                    # Still record the execution time even on failure
                    duration = time.perf_counter() - start_time
                    performance_monitor._metrics[op_name].add_execution(duration)
                    
                    enrich_span(
                        metadata={'performance': {'duration_seconds': duration, 'failed': True}},
                        error=str(e)
                    )
                    raise
            
            return async_wrapper
        else:
            @trace(event_type=event_type, metadata=metadata, tags=tags)
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                start_memory = 0.0
                start_cpu = 0.0
                
                # Collect baseline metrics
                process = None
                if track_memory or track_cpu:
                    try:
                        process = psutil.Process()
                        if track_memory:
                            start_memory = process.memory_info().rss / 1024 / 1024
                        if track_cpu:
                            start_cpu = process.cpu_percent()
                    except Exception as e:
                        logger.debug(f"Failed to collect baseline metrics: {e}")
                        process = None
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Calculate performance metrics
                    duration = time.perf_counter() - start_time
                    end_memory = start_memory
                    cpu_usage = 0.0
                    
                    if track_memory or track_cpu and process is not None:
                        try:
                            if track_memory:
                                end_memory = process.memory_info().rss / 1024 / 1024
                            if track_cpu:
                                cpu_usage = process.cpu_percent()
                        except Exception as e:
                            logger.debug(f"Failed to collect end metrics: {e}")
                    
                    memory_used = end_memory - start_memory if track_memory else 0.0
                    
                    # Record metrics
                    performance_monitor._metrics[op_name].add_execution(
                        duration, memory_used, cpu_usage
                    )
                    
                    # Check thresholds and alert if needed
                    if alert_on_threshold:
                        if time_threshold and duration > time_threshold:
                            logger.warning(f"Function {op_name} exceeded time threshold: {duration:.3f}s > {time_threshold}s")
                        if memory_threshold and memory_used > memory_threshold:
                            logger.warning(f"Function {op_name} exceeded memory threshold: {memory_used:.1f}MB > {memory_threshold}MB")
                    
                    # Enrich span with performance data
                    perf_data = {
                        'duration_seconds': duration,
                        'call_count': performance_monitor._metrics[op_name].call_count,
                        'avg_duration': performance_monitor._metrics[op_name].avg_time
                    }
                    
                    if track_memory:
                        perf_data['memory_used_mb'] = memory_used
                    if track_cpu:
                        perf_data['cpu_percent'] = cpu_usage
                    
                    enrich_span(metadata={'performance': perf_data})
                    
                    return result
                    
                except Exception as e:
                    # Still record the execution time even on failure
                    duration = time.perf_counter() - start_time
                    performance_monitor._metrics[op_name].add_execution(duration)
                    
                    enrich_span(
                        metadata={'performance': {'duration_seconds': duration, 'failed': True}},
                        error=str(e)
                    )
                    raise
            
            return sync_wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def get_performance_summary(operation_name: Optional[str] = None) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """
    Get performance summary for a specific operation or all operations.
    
    Args:
        operation_name: Name of operation to get summary for, or None for all operations
        
    Returns:
        Performance summary data
    """
    if operation_name:
        return performance_monitor.get_metrics(operation_name).get_summary()
    else:
        return performance_monitor.get_all_metrics()


def reset_performance_metrics(operation_name: Optional[str] = None) -> None:
    """
    Reset performance metrics for a specific operation or all operations.
    
    Args:
        operation_name: Name of operation to reset, or None to reset all
    """
    performance_monitor.reset_metrics(operation_name)


# Convenience aliases
perf_trace = performance_trace
monitor = performance_monitor.track