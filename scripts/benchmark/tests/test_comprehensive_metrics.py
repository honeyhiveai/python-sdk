"""
Unit tests for comprehensive metrics framework module.

Tests the ComprehensiveMetricsCalculator and related classes.
"""

import pytest
from unittest.mock import Mock
from ..testing.comprehensive_metrics import (
    ComprehensiveMetricsCalculator, ComprehensiveMetricsReport,
    CoreEfficiencyMetrics, AccuracyFidelityMetrics, ReliabilityLossMetrics,
    ContextCorrelationMetrics, CostPayloadMetrics
)
from ..core.metrics import PerformanceMetrics
from ..reporting.metrics_calculator import NorthStarMetrics


class TestCoreEfficiencyMetrics:
    """Test cases for CoreEfficiencyMetrics dataclass."""
    
    def test_initialization(self):
        """Test CoreEfficiencyMetrics initialization."""
        metrics = CoreEfficiencyMetrics(
            cpu_overhead_percent=5.0,
            memory_overhead_percent=15.0,
            throughput_degradation_percent=3.0,
            latency_overhead_ms=50.0,
            resource_utilization_score=85.0
        )
        
        assert metrics.cpu_overhead_percent == 5.0
        assert metrics.memory_overhead_percent == 15.0
        assert metrics.resource_utilization_score == 85.0
    
    def test_get_efficiency_grade(self):
        """Test efficiency grade calculation."""
        # Grade A
        metrics_a = CoreEfficiencyMetrics(5.0, 10.0, 2.0, 30.0, 95.0)
        assert metrics_a.get_efficiency_grade() == "A"
        
        # Grade B
        metrics_b = CoreEfficiencyMetrics(10.0, 15.0, 5.0, 50.0, 85.0)
        assert metrics_b.get_efficiency_grade() == "B"
        
        # Grade C
        metrics_c = CoreEfficiencyMetrics(15.0, 20.0, 8.0, 80.0, 75.0)
        assert metrics_c.get_efficiency_grade() == "C"
        
        # Grade D
        metrics_d = CoreEfficiencyMetrics(20.0, 25.0, 12.0, 100.0, 65.0)
        assert metrics_d.get_efficiency_grade() == "D"
        
        # Grade F
        metrics_f = CoreEfficiencyMetrics(30.0, 35.0, 20.0, 150.0, 45.0)
        assert metrics_f.get_efficiency_grade() == "F"


class TestAccuracyFidelityMetrics:
    """Test cases for AccuracyFidelityMetrics dataclass."""
    
    def test_initialization(self):
        """Test AccuracyFidelityMetrics initialization."""
        metrics = AccuracyFidelityMetrics(
            trace_coverage_percent=98.0,
            attribute_completeness_percent=95.0,
            semantic_accuracy_percent=90.0,
            span_hierarchy_correctness=92.0,
            timing_accuracy_percent=96.0,
            data_fidelity_score=94.2
        )
        
        assert metrics.trace_coverage_percent == 98.0
        assert metrics.data_fidelity_score == 94.2
    
    def test_get_fidelity_grade(self):
        """Test fidelity grade calculation."""
        # Grade A
        metrics_a = AccuracyFidelityMetrics(99.0, 98.0, 97.0, 96.0, 98.0, 97.6)
        assert metrics_a.get_fidelity_grade() == "A"
        
        # Grade B
        metrics_b = AccuracyFidelityMetrics(95.0, 93.0, 92.0, 91.0, 94.0, 93.0)
        assert metrics_b.get_fidelity_grade() == "B"
        
        # Grade F
        metrics_f = AccuracyFidelityMetrics(70.0, 65.0, 60.0, 55.0, 70.0, 64.0)
        assert metrics_f.get_fidelity_grade() == "F"


class TestReliabilityLossMetrics:
    """Test cases for ReliabilityLossMetrics dataclass."""
    
    def test_initialization(self):
        """Test ReliabilityLossMetrics initialization."""
        metrics = ReliabilityLossMetrics(
            dropped_span_rate_percent=0.5,
            export_failure_rate_percent=0.1,
            data_loss_rate_percent=0.5,
            system_stability_score=99.4,
            error_recovery_time_ms=500.0,
            uptime_percentage=99.9
        )
        
        assert metrics.dropped_span_rate_percent == 0.5
        assert metrics.system_stability_score == 99.4
    
    def test_get_reliability_grade(self):
        """Test reliability grade calculation."""
        # Grade A
        metrics_a = ReliabilityLossMetrics(0.1, 0.05, 0.1, 99.8, 200.0, 99.99)
        assert metrics_a.get_reliability_grade() == "A"
        
        # Grade B
        metrics_b = ReliabilityLossMetrics(1.0, 0.5, 1.0, 98.5, 800.0, 99.5)
        assert metrics_b.get_reliability_grade() == "B"
        
        # Grade F
        metrics_f = ReliabilityLossMetrics(10.0, 5.0, 10.0, 80.0, 5000.0, 95.0)
        assert metrics_f.get_reliability_grade() == "F"


class TestContextCorrelationMetrics:
    """Test cases for ContextCorrelationMetrics dataclass."""
    
    def test_initialization(self):
        """Test ContextCorrelationMetrics initialization."""
        metrics = ContextCorrelationMetrics(
            session_correlation_accuracy=96.0,
            conversation_continuity_score=94.0,
            cross_service_correlation=88.0,
            context_propagation_success=97.0,
            distributed_trace_completeness=91.0,
            correlation_quality_score=93.2
        )
        
        assert metrics.session_correlation_accuracy == 96.0
        assert metrics.correlation_quality_score == 93.2
    
    def test_get_correlation_grade(self):
        """Test correlation grade calculation."""
        # Grade A
        metrics_a = ContextCorrelationMetrics(98.0, 97.0, 96.0, 98.0, 95.0, 96.8)
        assert metrics_a.get_correlation_grade() == "A"
        
        # Grade F
        metrics_f = ContextCorrelationMetrics(70.0, 65.0, 60.0, 70.0, 65.0, 66.0)
        assert metrics_f.get_correlation_grade() == "F"


class TestCostPayloadMetrics:
    """Test cases for CostPayloadMetrics dataclass."""
    
    def test_initialization(self):
        """Test CostPayloadMetrics initialization."""
        metrics = CostPayloadMetrics(
            network_overhead_bytes=1024.0,
            storage_overhead_bytes=512.0,
            export_payload_size_bytes=2048.0,
            bandwidth_utilization_percent=8.0,
            storage_efficiency_score=85.0,
            cost_efficiency_score=87.0
        )
        
        assert metrics.network_overhead_bytes == 1024.0
        assert metrics.cost_efficiency_score == 87.0
    
    def test_get_cost_grade(self):
        """Test cost grade calculation."""
        # Grade A
        metrics_a = CostPayloadMetrics(500.0, 256.0, 1024.0, 3.0, 95.0, 92.0)
        assert metrics_a.get_cost_grade() == "A"
        
        # Grade F
        metrics_f = CostPayloadMetrics(5000.0, 2000.0, 10000.0, 25.0, 40.0, 45.0)
        assert metrics_f.get_cost_grade() == "F"


class TestComprehensiveMetricsReport:
    """Test cases for ComprehensiveMetricsReport dataclass."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.north_star = NorthStarMetrics(
            overhead_latency_percent=2.5,
            dropped_span_rate_percent=0.5,
            export_latency_p95_ms=120.0,
            trace_coverage_percent=98.0,
            attribute_completeness_percent=95.0,
            memory_overhead_percent=18.0
        )
        
        self.core_efficiency = CoreEfficiencyMetrics(2.5, 18.0, 2.0, 25.0, 88.0)
        self.accuracy_fidelity = AccuracyFidelityMetrics(98.0, 95.0, 92.0, 94.0, 96.0, 95.0)
        self.reliability_loss = ReliabilityLossMetrics(0.5, 0.1, 0.5, 99.4, 300.0, 99.9)
        self.context_correlation = ContextCorrelationMetrics(96.0, 94.0, 88.0, 97.0, 91.0, 93.2)
        self.cost_payload = CostPayloadMetrics(1024.0, 512.0, 2048.0, 5.0, 90.0, 88.0)
        
        self.report = ComprehensiveMetricsReport(
            test_name="Test Report",
            north_star_metrics=self.north_star,
            core_efficiency=self.core_efficiency,
            accuracy_fidelity=self.accuracy_fidelity,
            reliability_loss=self.reliability_loss,
            context_correlation=self.context_correlation,
            cost_payload=self.cost_payload,
            overall_score=92.5,
            recommendations=["Optimize memory usage", "Improve correlation"]
        )
    
    def test_initialization(self):
        """Test ComprehensiveMetricsReport initialization."""
        assert self.report.test_name == "Test Report"
        assert self.report.overall_score == 92.5
        assert len(self.report.recommendations) == 2
    
    def test_get_overall_grade(self):
        """Test overall grade calculation."""
        assert self.report.get_overall_grade() == "A"  # 92.5 >= 90
        
        # Test other grades
        report_b = ComprehensiveMetricsReport(
            "Test B", self.north_star, self.core_efficiency, self.accuracy_fidelity,
            self.reliability_loss, self.context_correlation, self.cost_payload, 85.0
        )
        assert report_b.get_overall_grade() == "B"
    
    def test_get_category_grades(self):
        """Test category grades calculation."""
        grades = self.report.get_category_grades()
        
        assert "Core Efficiency" in grades
        assert "Accuracy & Fidelity" in grades
        assert "Reliability & Loss" in grades
        assert "Context & Correlation" in grades
        assert "Cost & Payload" in grades
        assert "Overall" in grades
        
        assert grades["Overall"] == "A"
        assert grades["Accuracy & Fidelity"] == "A"  # 95.0 >= 95
        assert grades["Reliability & Loss"] == "A"   # 99.4 >= 99


class TestComprehensiveMetricsCalculator:
    """Test cases for ComprehensiveMetricsCalculator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ComprehensiveMetricsCalculator()
        
        # Mock performance metrics
        self.performance_metrics = Mock(spec=PerformanceMetrics)
        self.performance_metrics.tracer_overhead_percent = 2.5
        self.performance_metrics.dropped_span_rate_percent = 0.5
        self.performance_metrics.network_export_latency_ms = 120.0
        self.performance_metrics.trace_coverage_percent = 98.0
        self.performance_metrics.attribute_completeness_percent = 95.0
        self.performance_metrics.memory_overhead_percent = 18.0
        self.performance_metrics.provider = "test_provider"
        
        # Mock trace data
        self.trace_data = {
            "semantic_accuracy_percent": 92.0,
            "hierarchy_correctness_percent": 94.0,
            "timing_accuracy_percent": 96.0,
            "session_correlation_accuracy": 96.0,
            "conversation_continuity_score": 94.0,
            "cross_service_correlation": 88.0,
            "context_propagation_success": 97.0,
            "distributed_trace_completeness": 91.0
        }
        
        # Mock system data
        self.system_data = {
            "avg_latency_ms": 1000.0,
            "export_failure_rate_percent": 0.1,
            "error_recovery_time_ms": 300.0,
            "uptime_percentage": 99.9,
            "network_overhead_bytes": 1024.0,
            "storage_overhead_bytes": 512.0,
            "export_payload_size_bytes": 2048.0,
            "bandwidth_utilization_percent": 5.0
        }
    
    def test_initialization(self):
        """Test ComprehensiveMetricsCalculator initialization."""
        assert self.calculator is not None
    
    def test_calculate_core_efficiency(self):
        """Test core efficiency metrics calculation."""
        metrics = self.calculator._calculate_core_efficiency(
            self.performance_metrics, self.system_data, None
        )
        
        assert isinstance(metrics, CoreEfficiencyMetrics)
        assert metrics.cpu_overhead_percent == 2.5
        assert metrics.memory_overhead_percent == 18.0
        assert metrics.throughput_degradation_percent <= 50.0  # Should be reasonable
        assert metrics.latency_overhead_ms > 0
        assert metrics.resource_utilization_score > 0
    
    def test_calculate_accuracy_fidelity(self):
        """Test accuracy and fidelity metrics calculation."""
        metrics = self.calculator._calculate_accuracy_fidelity(
            self.performance_metrics, self.trace_data
        )
        
        assert isinstance(metrics, AccuracyFidelityMetrics)
        assert metrics.trace_coverage_percent == 98.0
        assert metrics.attribute_completeness_percent == 95.0
        assert metrics.semantic_accuracy_percent == 92.0
        assert metrics.span_hierarchy_correctness == 94.0
        assert metrics.timing_accuracy_percent == 96.0
        assert metrics.data_fidelity_score > 0
    
    def test_calculate_reliability_loss(self):
        """Test reliability and loss metrics calculation."""
        metrics = self.calculator._calculate_reliability_loss(
            self.performance_metrics, self.system_data
        )
        
        assert isinstance(metrics, ReliabilityLossMetrics)
        assert metrics.dropped_span_rate_percent == 0.5
        assert metrics.export_failure_rate_percent == 0.1
        assert metrics.data_loss_rate_percent >= max(0.5, 0.1)
        assert metrics.system_stability_score > 0
        assert metrics.error_recovery_time_ms == 300.0
        assert metrics.uptime_percentage == 99.9
    
    def test_calculate_context_correlation(self):
        """Test context and correlation metrics calculation."""
        metrics = self.calculator._calculate_context_correlation(self.trace_data)
        
        assert isinstance(metrics, ContextCorrelationMetrics)
        assert metrics.session_correlation_accuracy == 96.0
        assert metrics.conversation_continuity_score == 94.0
        assert metrics.cross_service_correlation == 88.0
        assert metrics.context_propagation_success == 97.0
        assert metrics.distributed_trace_completeness == 91.0
        assert metrics.correlation_quality_score > 0
    
    def test_calculate_cost_payload(self):
        """Test cost and payload metrics calculation."""
        metrics = self.calculator._calculate_cost_payload(
            self.performance_metrics, self.system_data
        )
        
        assert isinstance(metrics, CostPayloadMetrics)
        assert metrics.network_overhead_bytes == 1024.0
        assert metrics.storage_overhead_bytes == 512.0
        assert metrics.export_payload_size_bytes == 2048.0
        assert metrics.bandwidth_utilization_percent == 5.0
        assert metrics.storage_efficiency_score > 0
        assert metrics.cost_efficiency_score > 0
    
    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        core_efficiency = CoreEfficiencyMetrics(2.5, 18.0, 2.0, 25.0, 88.0)
        accuracy_fidelity = AccuracyFidelityMetrics(98.0, 95.0, 92.0, 94.0, 96.0, 95.0)
        reliability_loss = ReliabilityLossMetrics(0.5, 0.1, 0.5, 99.4, 300.0, 99.9)
        context_correlation = ContextCorrelationMetrics(96.0, 94.0, 88.0, 97.0, 91.0, 93.2)
        cost_payload = CostPayloadMetrics(1024.0, 512.0, 2048.0, 5.0, 90.0, 88.0)
        
        overall_score = self.calculator._calculate_overall_score(
            core_efficiency, accuracy_fidelity, reliability_loss,
            context_correlation, cost_payload
        )
        
        assert isinstance(overall_score, float)
        assert 0 <= overall_score <= 100
        
        # Should be weighted average with fidelity having highest weight (30%)
        expected_approx = (
            88.0 * 0.25 +    # efficiency
            95.0 * 0.30 +    # fidelity (highest weight)
            99.4 * 0.25 +    # reliability
            93.2 * 0.15 +    # correlation
            88.0 * 0.05      # cost
        )
        
        assert abs(overall_score - expected_approx) < 1.0  # Within 1 point
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # High overhead scenarios
        high_cpu = CoreEfficiencyMetrics(10.0, 15.0, 8.0, 100.0, 75.0)
        high_both = CoreEfficiencyMetrics(10.0, 25.0, 8.0, 100.0, 75.0)  # High CPU and memory
        low_coverage = AccuracyFidelityMetrics(90.0, 85.0, 92.0, 94.0, 96.0, 91.4)
        high_drops = ReliabilityLossMetrics(2.0, 0.8, 2.0, 97.2, 300.0, 99.9)
        low_correlation = ContextCorrelationMetrics(85.0, 80.0, 75.0, 88.0, 82.0, 82.0)
        low_cost = CostPayloadMetrics(5000.0, 2000.0, 10000.0, 20.0, 60.0, 65.0)
        
        recommendations = self.calculator._generate_recommendations(
            high_both, low_coverage, high_drops, low_correlation, low_cost
        )
        
        assert len(recommendations) > 0
        assert any("CPU overhead" in rec for rec in recommendations)
        assert any("memory" in rec.lower() or "pooling" in rec.lower() for rec in recommendations)
        assert any("coverage" in rec for rec in recommendations)
        assert any("span buffering" in rec for rec in recommendations)
        assert any("context propagation" in rec for rec in recommendations)
        assert any("cost efficiency" in rec for rec in recommendations)
    
    def test_calculate_comprehensive_report(self):
        """Test complete comprehensive report calculation."""
        report = self.calculator.calculate_comprehensive_report(
            performance_metrics=self.performance_metrics,
            trace_data=self.trace_data,
            system_data=self.system_data,
            baseline_data=None
        )
        
        assert isinstance(report, ComprehensiveMetricsReport)
        assert report.test_name == "test_provider"
        assert isinstance(report.north_star_metrics, NorthStarMetrics)
        assert isinstance(report.core_efficiency, CoreEfficiencyMetrics)
        assert isinstance(report.accuracy_fidelity, AccuracyFidelityMetrics)
        assert isinstance(report.reliability_loss, ReliabilityLossMetrics)
        assert isinstance(report.context_correlation, ContextCorrelationMetrics)
        assert isinstance(report.cost_payload, CostPayloadMetrics)
        assert 0 <= report.overall_score <= 100
        assert len(report.recommendations) > 0
