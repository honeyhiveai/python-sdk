"""
Real Export Latency Monitor Module

This module provides real OTLP export latency measurement by intercepting actual
HoneyHive tracer exports. Replaces simulated NetworkIOMonitor with real performance
data from the tracer pipeline.
"""

import logging
import statistics
import time
from typing import Dict, List, Any, Optional, Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

logger = logging.getLogger(__name__)


class RealExportLatencyMonitor:
    """Monitor real OTLP export latency by intercepting actual tracer exports.
    
    This class wraps the HoneyHive OTLP exporter to measure actual export times
    instead of using simulated/estimated values. Provides real performance data
    for north-star metric #3 (Export Latency).
    
    Example:
        >>> monitor = RealExportLatencyMonitor()
        >>> # Wrap the tracer's OTLP exporter
        >>> monitor.wrap_exporter(tracer.otlp_exporter)
        >>> # ... perform traced operations ...
        >>> stats = monitor.get_export_stats()
        >>> print(f"Real export P95: {stats['export_latency_p95_ms']:.1f}ms")
    """
    
    def __init__(self) -> None:
        """Initialize real export latency monitoring."""
        self.export_latency_samples: List[float] = []  # Real OTLP export times
        self.benchmark_overhead_samples: List[float] = []  # Our measurement overhead
        self.export_count: int = 0
        self.total_spans_exported: int = 0
        self.failed_exports: int = 0
        self.monitoring_active: bool = False
        self.wrapped_exporters: List[Any] = []
        self.start_time: Optional[float] = None
        self.total_benchmark_overhead_ms: float = 0.0
        
        logger.debug("🌐 RealExportLatencyMonitor initialized")
    
    def start_monitoring(self) -> None:
        """Start monitoring real export latency."""
        if self.monitoring_active:
            logger.warning("Real export monitoring already active")
            return
            
        self.monitoring_active = True
        self.start_time = time.perf_counter()
        self.export_latency_samples.clear()
        self.benchmark_overhead_samples.clear()
        self.export_count = 0
        self.total_spans_exported = 0
        self.failed_exports = 0
        self.total_benchmark_overhead_ms = 0.0
        
        logger.debug("🌐 Started real export latency monitoring")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return real export statistics.
        
        :return: Dictionary of real export statistics
        :rtype: Dict[str, Any]
        """
        if not self.monitoring_active:
            logger.warning("Real export monitoring not active")
            return self._empty_stats()
            
        self.monitoring_active = False
        
        if not self.export_latency_samples:
            logger.warning("No real export samples collected")
            return self._empty_stats()
            
        # Calculate real export latency statistics (actual tracer performance)
        latencies_ms = [sample * 1000 for sample in self.export_latency_samples]  # Convert to ms
        
        # Calculate benchmark overhead statistics (our measurement overhead)
        benchmark_overhead_ms = [sample * 1000 for sample in self.benchmark_overhead_samples]
        
        stats = {
            # Real export latency (actual tracer performance)
            'total_requests': self.export_count,
            'total_spans_exported': self.total_spans_exported,
            'failed_exports': self.failed_exports,
            'success_rate': ((self.export_count - self.failed_exports) / self.export_count * 100) if self.export_count > 0 else 0.0,
            'export_latency_samples': self.export_latency_samples,  # Keep in seconds for compatibility
            'avg_export_latency_ms': statistics.mean(latencies_ms),
            'min_export_latency_ms': min(latencies_ms),
            'max_export_latency_ms': max(latencies_ms),
            'p50_export_latency_ms': statistics.median(latencies_ms),
            'p95_export_latency_ms': self._calculate_percentile(latencies_ms, 0.95),
            'p99_export_latency_ms': self._calculate_percentile(latencies_ms, 0.99),
            
            # Benchmark measurement overhead (separate from tracer performance)
            'benchmark_overhead_samples': self.benchmark_overhead_samples,
            'avg_benchmark_overhead_ms': statistics.mean(benchmark_overhead_ms) if benchmark_overhead_ms else 0.0,
            'total_benchmark_overhead_ms': self.total_benchmark_overhead_ms,
            'benchmark_overhead_percent': (self.total_benchmark_overhead_ms / sum(latencies_ms) * 100) if latencies_ms else 0.0,
            
            # General stats
            'monitoring_duration_s': time.perf_counter() - self.start_time if self.start_time else 0.0,
        }
        
        logger.info(
            f"🌐 Real export monitoring completed: {self.export_count} exports, "
            f"P95: {stats['p95_export_latency_ms']:.1f}ms, "
            f"success rate: {stats['success_rate']:.1f}%"
        )
        
        return stats
    
    def wrap_exporter(self, exporter: Any) -> None:
        """Wrap an OTLP exporter to intercept real export calls.
        
        :param exporter: The OTLP exporter to wrap
        :type exporter: Any
        """
        if not exporter:
            logger.warning("Cannot wrap None exporter")
            return
            
        if hasattr(exporter, '_original_export'):
            logger.warning("Exporter already wrapped, skipping")
            return
            
        # Store original export method
        exporter._original_export = exporter.export
        exporter._export_monitor = self
        
        # Replace with our intercepting method
        def intercepting_export(spans: Sequence[ReadableSpan]) -> SpanExportResult:
            return self._intercept_export(exporter, spans)
        
        exporter.export = intercepting_export
        self.wrapped_exporters.append(exporter)
        
        logger.debug(f"🌐 Wrapped exporter: {type(exporter).__name__}")
    
    def unwrap_exporter(self, exporter: Any) -> None:
        """Unwrap an OTLP exporter to restore original export method.
        
        :param exporter: The OTLP exporter to unwrap
        :type exporter: Any
        """
        if not exporter or not hasattr(exporter, '_original_export'):
            return
            
        # Restore original export method
        exporter.export = exporter._original_export
        delattr(exporter, '_original_export')
        delattr(exporter, '_export_monitor')
        
        if exporter in self.wrapped_exporters:
            self.wrapped_exporters.remove(exporter)
            
        logger.debug(f"🌐 Unwrapped exporter: {type(exporter).__name__}")
    
    def _intercept_export(self, exporter: Any, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Intercept and measure real export latency with separate benchmark overhead tracking.
        
        :param exporter: The wrapped exporter
        :type exporter: Any
        :param spans: Spans to export
        :type spans: Sequence[ReadableSpan]
        :return: Export result
        :rtype: SpanExportResult
        """
        if not self.monitoring_active:
            # If monitoring not active, just pass through
            return exporter._original_export(spans)
        
        # Start measuring our benchmark overhead
        benchmark_start = time.perf_counter()
        
        # Measure real export latency (actual tracer performance)
        export_start = time.perf_counter()
        
        try:
            # Call original export method - this is the REAL tracer work
            result = exporter._original_export(spans)
            
            # End of real export measurement
            export_end = time.perf_counter()
            real_export_latency = export_end - export_start
            
            # Record the real export latency (actual tracer performance)
            self.export_latency_samples.append(real_export_latency)
            self.export_count += 1
            self.total_spans_exported += len(spans)
            
            if result != SpanExportResult.SUCCESS:
                self.failed_exports += 1
                logger.debug(f"🌐 Export failed with result: {result}")
            
            # Measure our benchmark overhead (time spent in this method)
            benchmark_end = time.perf_counter()
            benchmark_overhead = benchmark_end - benchmark_start
            benchmark_overhead_ms = benchmark_overhead * 1000
            
            self.benchmark_overhead_samples.append(benchmark_overhead)
            self.total_benchmark_overhead_ms += benchmark_overhead_ms
            
            logger.debug(
                f"🌐 Real export: {real_export_latency*1000:.1f}ms, "
                f"benchmark overhead: {benchmark_overhead_ms:.3f}ms "
                f"for {len(spans)} spans (result: {result})"
            )
            
            return result
            
        except Exception as e:
            # End of real export measurement (even for failures)
            export_end = time.perf_counter()
            real_export_latency = export_end - export_start
            
            # Record the real export latency and failure
            self.export_latency_samples.append(real_export_latency)
            self.export_count += 1
            self.failed_exports += 1
            
            # Measure our benchmark overhead
            benchmark_end = time.perf_counter()
            benchmark_overhead = benchmark_end - benchmark_start
            benchmark_overhead_ms = benchmark_overhead * 1000
            
            self.benchmark_overhead_samples.append(benchmark_overhead)
            self.total_benchmark_overhead_ms += benchmark_overhead_ms
            
            logger.debug(
                f"🌐 Export exception after {real_export_latency*1000:.1f}ms "
                f"(benchmark overhead: {benchmark_overhead_ms:.3f}ms): {e}"
            )
            
            # Re-raise the exception
            raise
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile from a list of values.
        
        :param values: List of values
        :type values: List[float]
        :param percentile: Percentile to calculate (0.0 to 1.0)
        :type percentile: float
        :return: Percentile value
        :rtype: float
        """
        if not values:
            return 0.0
            
        sorted_values = sorted(values)
        index = max(0, min(len(sorted_values) - 1, int(percentile * len(sorted_values))))
        return sorted_values[index]
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics for error cases.
        
        :return: Empty statistics dictionary
        :rtype: Dict[str, Any]
        """
        return {
            # Real export latency (actual tracer performance)
            'total_requests': 0,
            'total_spans_exported': 0,
            'failed_exports': 0,
            'success_rate': 0.0,
            'export_latency_samples': [],
            'avg_export_latency_ms': 0.0,
            'min_export_latency_ms': 0.0,
            'max_export_latency_ms': 0.0,
            'p50_export_latency_ms': 0.0,
            'p95_export_latency_ms': 0.0,
            'p99_export_latency_ms': 0.0,
            
            # Benchmark measurement overhead
            'benchmark_overhead_samples': [],
            'avg_benchmark_overhead_ms': 0.0,
            'total_benchmark_overhead_ms': 0.0,
            'benchmark_overhead_percent': 0.0,
            
            # General stats
            'monitoring_duration_s': 0.0,
        }
    
    def get_export_stats(self) -> Dict[str, Any]:
        """Get current export statistics without stopping monitoring.
        
        :return: Current export statistics
        :rtype: Dict[str, Any]
        """
        if not self.export_latency_samples:
            return self._empty_stats()
            
        latencies_ms = [sample * 1000 for sample in self.export_latency_samples]
        benchmark_overhead_ms = [sample * 1000 for sample in self.benchmark_overhead_samples]
        
        return {
            # Real export latency (actual tracer performance)
            'total_requests': self.export_count,
            'total_spans_exported': self.total_spans_exported,
            'failed_exports': self.failed_exports,
            'success_rate': ((self.export_count - self.failed_exports) / self.export_count * 100) if self.export_count > 0 else 0.0,
            'export_latency_samples': self.export_latency_samples,
            'avg_export_latency_ms': statistics.mean(latencies_ms),
            'min_export_latency_ms': min(latencies_ms),
            'max_export_latency_ms': max(latencies_ms),
            'p50_export_latency_ms': statistics.median(latencies_ms),
            'p95_export_latency_ms': self._calculate_percentile(latencies_ms, 0.95),
            'p99_export_latency_ms': self._calculate_percentile(latencies_ms, 0.99),
            
            # Benchmark measurement overhead (separate from tracer performance)
            'benchmark_overhead_samples': self.benchmark_overhead_samples,
            'avg_benchmark_overhead_ms': statistics.mean(benchmark_overhead_ms) if benchmark_overhead_ms else 0.0,
            'total_benchmark_overhead_ms': self.total_benchmark_overhead_ms,
            'benchmark_overhead_percent': (self.total_benchmark_overhead_ms / sum(latencies_ms) * 100) if latencies_ms else 0.0,
            
            # General stats
            'monitoring_duration_s': time.perf_counter() - self.start_time if self.start_time else 0.0,
        }
    
    def cleanup(self) -> None:
        """Clean up by unwrapping all exporters."""
        for exporter in self.wrapped_exporters.copy():
            self.unwrap_exporter(exporter)
        
        self.monitoring_active = False
        logger.debug("🌐 RealExportLatencyMonitor cleanup completed")
