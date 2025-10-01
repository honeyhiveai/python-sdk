"""
Unit tests for metrics calculator module.

Tests the MetricsCalculator class and its calculation methods.
"""

import pytest
from unittest.mock import Mock
from ..reporting.metrics_calculator import MetricsCalculator, NorthStarMetrics
from ..providers.base_provider import ProviderResponse
from ..core.metrics import PerformanceMetrics


class TestMetricsCalculator:
    """Test cases for MetricsCalculator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = MetricsCalculator()
    
    def test_initialization(self):
        """Test that MetricsCalculator initializes correctly."""
        assert self.calculator is not None
    
    def test_calculate_latency_statistics(self):
        """Test latency statistics calculation."""
        latencies = [100.0, 200.0, 300.0, 400.0, 500.0]
        stats = self.calculator.calculate_latency_statistics(latencies)
        
        assert stats['avg_latency'] == 300.0
        assert stats['min_latency'] == 100.0
        assert stats['max_latency'] == 500.0
        assert stats['p95_latency'] == 500.0  # For 5 items, P95 is the max
        assert stats['p99_latency'] == 500.0  # For 5 items, P99 is the max
    
    def test_calculate_latency_statistics_single_value(self):
        """Test latency statistics with single value."""
        latencies = [150.0]
        stats = self.calculator.calculate_latency_statistics(latencies)
        
        assert stats['avg_latency'] == 150.0
        assert stats['min_latency'] == 150.0
        assert stats['max_latency'] == 150.0
        assert stats['p95_latency'] == 150.0
        assert stats['p99_latency'] == 150.0
    
    def test_calculate_latency_statistics_empty_list(self):
        """Test latency statistics with empty list."""
        latencies = []
        stats = self.calculator.calculate_latency_statistics(latencies)
        
        assert stats['avg_latency'] == 0.0
        assert stats['min_latency'] == 0.0
        assert stats['max_latency'] == 0.0
        assert stats['p95_latency'] == 0.0
        assert stats['p99_latency'] == 0.0
    
    def test_calculate_throughput_metrics(self):
        """Test throughput metrics calculation."""
        operations = 100
        total_time = 50.0  # 50 seconds
        
        stats = self.calculator.calculate_throughput_metrics(operations, total_time)
        
        assert stats['operations_per_second'] == 2.0
        assert stats['total_operations'] == 100
        assert stats['total_time_seconds'] == 50.0
        assert stats['avg_time_per_operation'] == 0.5
    
    def test_calculate_throughput_metrics_zero_time(self):
        """Test throughput metrics with zero time."""
        operations = 100
        total_time = 0.0
        
        stats = self.calculator.calculate_throughput_metrics(operations, total_time)
        
        assert stats['operations_per_second'] == 0.0
        assert stats['total_operations'] == 100
        assert stats['total_time_seconds'] == 0.0
        assert stats['avg_time_per_operation'] == 0.0
    
    def test_calculate_memory_overhead(self):
        """Test memory overhead calculation."""
        baseline_mb = 100.0
        avg_mb = 120.0
        
        overhead_mb, overhead_percent = self.calculator.calculate_memory_overhead(baseline_mb, avg_mb)
        
        assert overhead_mb == 20.0
        assert overhead_percent == 20.0
    
    def test_calculate_memory_overhead_zero_baseline(self):
        """Test memory overhead with zero baseline."""
        baseline_mb = 0.0
        avg_mb = 120.0
        
        overhead_mb, overhead_percent = self.calculator.calculate_memory_overhead(baseline_mb, avg_mb)
        
        assert overhead_mb == 0.0
        assert overhead_percent == 0.0
    
    def test_calculate_memory_overhead_negative_baseline(self):
        """Test memory overhead with negative baseline."""
        baseline_mb = -10.0
        avg_mb = 120.0
        
        overhead_mb, overhead_percent = self.calculator.calculate_memory_overhead(baseline_mb, avg_mb)
        
        assert overhead_mb == 0.0
        assert overhead_percent == 0.0
    
    def test_calculate_dropped_span_rate(self):
        """Test dropped span rate calculation."""
        total_requests = 100
        successful_requests = 95
        
        rate = self.calculator.calculate_dropped_span_rate(total_requests, successful_requests)
        
        assert rate == 5.0  # 5% dropped
    
    def test_calculate_dropped_span_rate_all_successful(self):
        """Test dropped span rate with all successful requests."""
        total_requests = 100
        successful_requests = 100
        
        rate = self.calculator.calculate_dropped_span_rate(total_requests, successful_requests)
        
        assert rate == 0.0
    
    def test_calculate_dropped_span_rate_zero_total(self):
        """Test dropped span rate with zero total requests."""
        total_requests = 0
        successful_requests = 0
        
        rate = self.calculator.calculate_dropped_span_rate(total_requests, successful_requests)
        
        assert rate == 0.0
    
    def test_extract_north_star_metrics(self):
        """Test extraction of north-star metrics from PerformanceMetrics."""
        # Create a mock PerformanceMetrics object
        metrics = Mock(spec=PerformanceMetrics)
        metrics.tracer_overhead_percent = 2.5
        metrics.dropped_span_rate_percent = 1.0
        metrics.network_export_latency_ms = 150.0
        metrics.trace_coverage_percent = 98.0
        metrics.attribute_completeness_percent = 95.0
        metrics.memory_overhead_percent = 15.0
        
        north_star = self.calculator.extract_north_star_metrics(metrics)
        
        assert isinstance(north_star, NorthStarMetrics)
        assert north_star.overhead_latency_percent == 2.5
        assert north_star.dropped_span_rate_percent == 1.0
        assert north_star.export_latency_p95_ms == 150.0
        assert north_star.trace_coverage_percent == 98.0
        assert north_star.attribute_completeness_percent == 95.0
        assert north_star.memory_overhead_percent == 15.0
    
    def test_north_star_metrics_is_complete(self):
        """Test NorthStarMetrics completeness check."""
        # Complete metrics
        complete_metrics = NorthStarMetrics(
            overhead_latency_percent=2.5,
            dropped_span_rate_percent=1.0,
            export_latency_p95_ms=150.0,
            trace_coverage_percent=98.0,
            attribute_completeness_percent=95.0,
            memory_overhead_percent=15.0
        )
        assert complete_metrics.is_complete() is True
        
        # Incomplete metrics (negative value)
        incomplete_metrics = NorthStarMetrics(
            overhead_latency_percent=-1.0,  # Invalid negative value
            dropped_span_rate_percent=1.0,
            export_latency_p95_ms=150.0,
            trace_coverage_percent=98.0,
            attribute_completeness_percent=95.0,
            memory_overhead_percent=15.0
        )
        assert incomplete_metrics.is_complete() is False
    
    def test_north_star_metrics_get_summary(self):
        """Test NorthStarMetrics summary generation."""
        metrics = NorthStarMetrics(
            overhead_latency_percent=2.5,
            dropped_span_rate_percent=1.0,
            export_latency_p95_ms=150.0,
            trace_coverage_percent=98.0,
            attribute_completeness_percent=95.0,
            memory_overhead_percent=15.0
        )
        
        summary = metrics.get_summary()
        
        assert "Cost of Tracing" in summary
        assert "2.50% latency + 15.00% memory" in summary["Cost of Tracing"]
        assert "Fidelity of Data" in summary
        assert "98.0% coverage + 95.0% completeness" in summary["Fidelity of Data"]
        assert "Reliability of Pipeline" in summary
        assert "1.0% drops + 150.0ms P95 export" in summary["Reliability of Pipeline"]
