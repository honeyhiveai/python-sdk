"""
Performance Metrics Module

This module provides dataclasses for capturing and analyzing tracer
performance metrics, following Agent OS production code standards.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for tracer benchmarks.
    
    This dataclass captures all performance-related measurements including
    latency, throughput, memory usage, network I/O, and trace quality metrics.
    Implements the six north-star metrics framework from teammate feedback.
    
    :param provider: LLM provider name (openai, anthropic)
    :type provider: str
    :param mode: Benchmark mode (sequential, concurrent)
    :type mode: str
    :param total_operations: Total number of operations performed
    :type total_operations: int
    :param total_time: Total execution time in seconds
    :type total_time: float
    :param operations_per_second: Throughput metric
    :type operations_per_second: float
    :param avg_latency: Average latency per operation in milliseconds
    :type avg_latency: float
    :param min_latency: Minimum observed latency in milliseconds
    :type min_latency: float
    :param max_latency: Maximum observed latency in milliseconds
    :type max_latency: float
    :param p95_latency: 95th percentile latency in milliseconds
    :type p95_latency: float
    :param p99_latency: 99th percentile latency in milliseconds
    :type p99_latency: float
    :param tracer_overhead: Tracer overhead in milliseconds
    :type tracer_overhead: float
    :param tracer_overhead_percent: Tracer overhead as percentage
    :type tracer_overhead_percent: float
    :param span_processing_time_ms: Span processing time in milliseconds
    :type span_processing_time_ms: float
    :param network_requests_count: Number of telemetry export requests
    :type network_requests_count: int
    :param network_bytes_sent: Total bytes sent for telemetry
    :type network_bytes_sent: int
    :param network_bytes_received: Total bytes received from telemetry service
    :type network_bytes_received: int
    :param network_export_latency_ms: Average export latency in milliseconds
    :type network_export_latency_ms: float
    :param network_bytes_per_operation: Average bytes per operation
    :type network_bytes_per_operation: float
    :param memory_baseline_mb: Baseline memory usage in MB
    :type memory_baseline_mb: float
    :param memory_peak_mb: Peak memory usage in MB
    :type memory_peak_mb: float
    :param memory_overhead_mb: Memory overhead in MB
    :type memory_overhead_mb: float
    :param memory_overhead_percent: Memory overhead as percentage
    :type memory_overhead_percent: float
    :param success_rate: Success rate as percentage (0-100)
    :type success_rate: float
    :param error_count: Number of failed operations
    :type error_count: int
    :param trace_coverage_percent: Percentage of requests with complete root span
    :type trace_coverage_percent: Optional[float]
    :param attribute_completeness_percent: Percentage of spans with required fields
    :type attribute_completeness_percent: Optional[float]
    :param dropped_span_rate_percent: Percentage of spans dropped before storage
    :type dropped_span_rate_percent: Optional[float]
    
    Example:
        >>> metrics = PerformanceMetrics(
        ...     provider="openai",
        ...     mode="sequential",
        ...     total_operations=50,
        ...     avg_latency=1009.5,
        ...     success_rate=100.0
        ... )
        >>> print(f"{metrics.provider} {metrics.mode}: {metrics.avg_latency:.1f}ms avg")
        openai sequential: 1009.5ms avg
    """
    
    # Core identification
    provider: str
    mode: str
    
    # Basic performance metrics
    total_operations: int
    total_time: float
    operations_per_second: float
    
    # Latency metrics
    avg_latency: float
    min_latency: float
    max_latency: float
    p95_latency: float
    p99_latency: float
    
    # North-Star Metric 1: Overhead Latency
    tracer_overhead: float
    tracer_overhead_percent: float
    span_processing_time_ms: float
    
    # North-Star Metric 3: Export Latency
    network_requests_count: int
    network_bytes_sent: int
    network_bytes_received: int
    network_export_latency_ms: float
    network_bytes_per_operation: float
    
    # North-Star Metric 6: Memory Overhead
    memory_baseline_mb: float
    memory_peak_mb: float
    memory_overhead_mb: float
    memory_overhead_percent: float
    
    # North-Star Metric 2: Dropped Span Rate (via success rate)
    success_rate: float
    error_count: int
    
    # North-Star Metric 4: Trace Coverage (NEW)
    trace_coverage_percent: Optional[float] = None
    
    # North-Star Metric 5: Attribute Completeness (NEW)
    attribute_completeness_percent: Optional[float] = None
    
    # Additional reliability metrics
    dropped_span_rate_percent: Optional[float] = None
    
    # Detailed Network I/O Analysis
    llm_request_avg_kb: float = 0.0
    llm_response_avg_kb: float = 0.0
    llm_latency_avg_ms: float = 0.0
    tracer_export_avg_kb: float = 0.0
    tracer_export_latency_avg_ms: float = 0.0
    total_llm_traffic_kb: float = 0.0
    total_tracer_traffic_kb: float = 0.0
    tracer_traffic_percent: float = 0.0
    
    def __post_init__(self) -> None:
        """Validate metrics after initialization.
        
        :raises ValueError: If any metric value is invalid
        """
        if self.total_operations <= 0:
            raise ValueError("total_operations must be positive")
        if self.total_time <= 0:
            raise ValueError("total_time must be positive")
        if not 0.0 <= self.success_rate <= 100.0:
            raise ValueError("success_rate must be between 0.0 and 100.0")
        if self.error_count < 0:
            raise ValueError("error_count must be non-negative")
        
        # Validate optional percentages
        for field_name, value in [
            ("trace_coverage_percent", self.trace_coverage_percent),
            ("attribute_completeness_percent", self.attribute_completeness_percent),
            ("dropped_span_rate_percent", self.dropped_span_rate_percent)
        ]:
            if value is not None and not 0.0 <= value <= 100.0:
                raise ValueError(f"{field_name} must be between 0.0 and 100.0")
    
    def get_north_star_summary(self) -> dict[str, Optional[float]]:
        """Get the six north-star metrics in a structured format.
        
        Returns the six critical metrics identified by teammate feedback
        for quick tracer capability assessment.
        
        :return: Dictionary with north-star metric values
        :rtype: dict[str, Optional[float]]
        
        Example:
            >>> metrics = PerformanceMetrics(...)
            >>> summary = metrics.get_north_star_summary()
            >>> print(f"Overhead: {summary['overhead_latency_percent']:.1f}%")
        """
        return {
            "overhead_latency_percent": self.tracer_overhead_percent,
            "dropped_span_rate_percent": (100.0 - self.success_rate) if self.success_rate else None,
            "export_latency_ms": self.network_export_latency_ms,
            "trace_coverage_percent": self.trace_coverage_percent,
            "attribute_completeness_percent": self.attribute_completeness_percent,
            "memory_overhead_percent": self.memory_overhead_percent,
        }
    
    def is_north_star_complete(self) -> bool:
        """Check if all six north-star metrics are available.
        
        :return: True if all north-star metrics have values
        :rtype: bool
        """
        summary = self.get_north_star_summary()
        return all(value is not None for value in summary.values())
