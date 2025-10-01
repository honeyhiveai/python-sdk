"""
Comprehensive Metrics Framework Module

This module implements the full metrics framework covering all aspects of
tracer performance evaluation as requested by teammate feedback:
- Core Efficiency
- Accuracy & Fidelity  
- Reliability & Loss
- Context & Correlation
- Cost & Payload
"""

import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from ..core.metrics import PerformanceMetrics
from ..reporting.metrics_calculator import NorthStarMetrics

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of comprehensive metrics."""
    CORE_EFFICIENCY = "core_efficiency"
    ACCURACY_FIDELITY = "accuracy_fidelity"
    RELIABILITY_LOSS = "reliability_loss"
    CONTEXT_CORRELATION = "context_correlation"
    COST_PAYLOAD = "cost_payload"


@dataclass
class CoreEfficiencyMetrics:
    """Core efficiency metrics measuring fundamental tracer performance.
    
    :param cpu_overhead_percent: CPU processing overhead (%)
    :type cpu_overhead_percent: float
    :param memory_overhead_percent: Memory overhead (%)
    :type memory_overhead_percent: float
    :param throughput_degradation_percent: Throughput reduction (%)
    :type throughput_degradation_percent: float
    :param latency_overhead_ms: Additional latency in milliseconds
    :type latency_overhead_ms: float
    :param resource_utilization_score: Resource efficiency score (0-100)
    :type resource_utilization_score: float
    """
    cpu_overhead_percent: float
    memory_overhead_percent: float
    throughput_degradation_percent: float
    latency_overhead_ms: float
    resource_utilization_score: float
    
    def get_efficiency_grade(self) -> str:
        """Get letter grade for overall efficiency.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        score = self.resource_utilization_score
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"


@dataclass
class AccuracyFidelityMetrics:
    """Accuracy and fidelity metrics measuring data quality.
    
    :param trace_coverage_percent: Percentage of complete traces
    :type trace_coverage_percent: float
    :param attribute_completeness_percent: Percentage of complete attributes
    :type attribute_completeness_percent: float
    :param semantic_accuracy_percent: Semantic convention accuracy
    :type semantic_accuracy_percent: float
    :param span_hierarchy_correctness: Span parent-child relationships accuracy
    :type span_hierarchy_correctness: float
    :param timing_accuracy_percent: Timing measurement accuracy
    :type timing_accuracy_percent: float
    :param data_fidelity_score: Overall data fidelity score (0-100)
    :type data_fidelity_score: float
    """
    trace_coverage_percent: float
    attribute_completeness_percent: float
    semantic_accuracy_percent: float
    span_hierarchy_correctness: float
    timing_accuracy_percent: float
    data_fidelity_score: float
    
    def get_fidelity_grade(self) -> str:
        """Get letter grade for data fidelity.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        score = self.data_fidelity_score
        if score >= 95: return "A"
        elif score >= 90: return "B"
        elif score >= 85: return "C"
        elif score >= 80: return "D"
        else: return "F"


@dataclass
class ReliabilityLossMetrics:
    """Reliability and loss metrics measuring system stability.
    
    :param dropped_span_rate_percent: Percentage of dropped spans
    :type dropped_span_rate_percent: float
    :param export_failure_rate_percent: Export failure rate
    :type export_failure_rate_percent: float
    :param data_loss_rate_percent: Overall data loss rate
    :type data_loss_rate_percent: float
    :param system_stability_score: System stability score (0-100)
    :type system_stability_score: float
    :param error_recovery_time_ms: Time to recover from errors
    :type error_recovery_time_ms: float
    :param uptime_percentage: System uptime percentage
    :type uptime_percentage: float
    """
    dropped_span_rate_percent: float
    export_failure_rate_percent: float
    data_loss_rate_percent: float
    system_stability_score: float
    error_recovery_time_ms: float
    uptime_percentage: float
    
    def get_reliability_grade(self) -> str:
        """Get letter grade for reliability.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        score = self.system_stability_score
        if score >= 99: return "A"
        elif score >= 95: return "B"
        elif score >= 90: return "C"
        elif score >= 85: return "D"
        else: return "F"


@dataclass
class ContextCorrelationMetrics:
    """Context and correlation metrics measuring trace relationships.
    
    :param session_correlation_accuracy: Session correlation accuracy (%)
    :type session_correlation_accuracy: float
    :param conversation_continuity_score: Conversation flow tracking score
    :type conversation_continuity_score: float
    :param cross_service_correlation: Cross-service trace correlation accuracy
    :type cross_service_correlation: float
    :param context_propagation_success: Context propagation success rate
    :type context_propagation_success: float
    :param distributed_trace_completeness: Distributed trace completeness
    :type distributed_trace_completeness: float
    :param correlation_quality_score: Overall correlation quality (0-100)
    :type correlation_quality_score: float
    """
    session_correlation_accuracy: float
    conversation_continuity_score: float
    cross_service_correlation: float
    context_propagation_success: float
    distributed_trace_completeness: float
    correlation_quality_score: float
    
    def get_correlation_grade(self) -> str:
        """Get letter grade for correlation quality.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        score = self.correlation_quality_score
        if score >= 95: return "A"
        elif score >= 90: return "B"
        elif score >= 85: return "C"
        elif score >= 80: return "D"
        else: return "F"


@dataclass
class CostPayloadMetrics:
    """Cost and payload metrics measuring resource consumption.
    
    :param network_overhead_bytes: Additional network bytes per request
    :type network_overhead_bytes: float
    :param storage_overhead_bytes: Additional storage bytes per span
    :type storage_overhead_bytes: float
    :param export_payload_size_bytes: Average export payload size
    :type export_payload_size_bytes: float
    :param bandwidth_utilization_percent: Network bandwidth utilization
    :type bandwidth_utilization_percent: float
    :param storage_efficiency_score: Storage efficiency score (0-100)
    :type storage_efficiency_score: float
    :param cost_efficiency_score: Overall cost efficiency score (0-100)
    :type cost_efficiency_score: float
    """
    network_overhead_bytes: float
    storage_overhead_bytes: float
    export_payload_size_bytes: float
    bandwidth_utilization_percent: float
    storage_efficiency_score: float
    cost_efficiency_score: float
    
    def get_cost_grade(self) -> str:
        """Get letter grade for cost efficiency.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        score = self.cost_efficiency_score
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"


@dataclass
class ComprehensiveMetricsReport:
    """Complete comprehensive metrics report.
    
    :param test_name: Name of the test
    :type test_name: str
    :param north_star_metrics: Six north-star metrics
    :type north_star_metrics: NorthStarMetrics
    :param core_efficiency: Core efficiency metrics
    :type core_efficiency: CoreEfficiencyMetrics
    :param accuracy_fidelity: Accuracy and fidelity metrics
    :type accuracy_fidelity: AccuracyFidelityMetrics
    :param reliability_loss: Reliability and loss metrics
    :type reliability_loss: ReliabilityLossMetrics
    :param context_correlation: Context and correlation metrics
    :type context_correlation: ContextCorrelationMetrics
    :param cost_payload: Cost and payload metrics
    :type cost_payload: CostPayloadMetrics
    :param overall_score: Overall composite score (0-100)
    :type overall_score: float
    :param recommendations: Performance improvement recommendations
    :type recommendations: List[str]
    """
    test_name: str
    north_star_metrics: NorthStarMetrics
    core_efficiency: CoreEfficiencyMetrics
    accuracy_fidelity: AccuracyFidelityMetrics
    reliability_loss: ReliabilityLossMetrics
    context_correlation: ContextCorrelationMetrics
    cost_payload: CostPayloadMetrics
    overall_score: float
    recommendations: List[str] = field(default_factory=list)
    
    def get_overall_grade(self) -> str:
        """Get overall letter grade.
        
        :return: Letter grade (A-F)
        :rtype: str
        """
        if self.overall_score >= 90: return "A"
        elif self.overall_score >= 80: return "B"
        elif self.overall_score >= 70: return "C"
        elif self.overall_score >= 60: return "D"
        else: return "F"
    
    def get_category_grades(self) -> Dict[str, str]:
        """Get grades for all metric categories.
        
        :return: Dictionary of category grades
        :rtype: Dict[str, str]
        """
        return {
            "Core Efficiency": self.core_efficiency.get_efficiency_grade(),
            "Accuracy & Fidelity": self.accuracy_fidelity.get_fidelity_grade(),
            "Reliability & Loss": self.reliability_loss.get_reliability_grade(),
            "Context & Correlation": self.context_correlation.get_correlation_grade(),
            "Cost & Payload": self.cost_payload.get_cost_grade(),
            "Overall": self.get_overall_grade()
        }


class ComprehensiveMetricsCalculator:
    """Calculator for comprehensive tracer performance metrics.
    
    Implements the full metrics framework covering all aspects of tracer
    performance evaluation as specified in teammate feedback.
    
    Example:
        >>> calculator = ComprehensiveMetricsCalculator()
        >>> report = calculator.calculate_comprehensive_report(
        ...     performance_metrics=metrics,
        ...     trace_data=traces,
        ...     system_data=system_stats
        ... )
        >>> print(f"Overall Grade: {report.get_overall_grade()}")
    """
    
    def __init__(self) -> None:
        """Initialize comprehensive metrics calculator."""
        logger.info("📊 Comprehensive Metrics Calculator initialized")
    
    def calculate_comprehensive_report(
        self,
        performance_metrics: PerformanceMetrics,
        trace_data: Dict[str, Any],
        system_data: Dict[str, Any],
        baseline_data: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveMetricsReport:
        """Calculate comprehensive metrics report.
        
        :param performance_metrics: Basic performance metrics
        :type performance_metrics: PerformanceMetrics
        :param trace_data: Trace analysis data
        :type trace_data: Dict[str, Any]
        :param system_data: System performance data
        :type system_data: Dict[str, Any]
        :param baseline_data: Baseline comparison data
        :type baseline_data: Optional[Dict[str, Any]]
        :return: Comprehensive metrics report
        :rtype: ComprehensiveMetricsReport
        """
        logger.info("📊 Calculating comprehensive metrics report...")
        
        # Extract north-star metrics
        north_star = NorthStarMetrics(
            overhead_latency_percent=performance_metrics.tracer_overhead_percent,
            dropped_span_rate_percent=performance_metrics.dropped_span_rate_percent,
            export_latency_p95_ms=performance_metrics.network_export_latency_ms,
            trace_coverage_percent=performance_metrics.trace_coverage_percent,
            attribute_completeness_percent=performance_metrics.attribute_completeness_percent,
            memory_overhead_percent=performance_metrics.memory_overhead_percent
        )
        
        # Calculate category metrics
        core_efficiency = self._calculate_core_efficiency(performance_metrics, system_data, baseline_data)
        accuracy_fidelity = self._calculate_accuracy_fidelity(performance_metrics, trace_data)
        reliability_loss = self._calculate_reliability_loss(performance_metrics, system_data)
        context_correlation = self._calculate_context_correlation(trace_data)
        cost_payload = self._calculate_cost_payload(performance_metrics, system_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            core_efficiency, accuracy_fidelity, reliability_loss,
            context_correlation, cost_payload
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            core_efficiency, accuracy_fidelity, reliability_loss,
            context_correlation, cost_payload
        )
        
        return ComprehensiveMetricsReport(
            test_name=getattr(performance_metrics, 'provider', 'Unknown Test'),
            north_star_metrics=north_star,
            core_efficiency=core_efficiency,
            accuracy_fidelity=accuracy_fidelity,
            reliability_loss=reliability_loss,
            context_correlation=context_correlation,
            cost_payload=cost_payload,
            overall_score=overall_score,
            recommendations=recommendations
        )
    
    def _calculate_core_efficiency(
        self,
        metrics: PerformanceMetrics,
        system_data: Dict[str, Any],
        baseline_data: Optional[Dict[str, Any]]
    ) -> CoreEfficiencyMetrics:
        """Calculate core efficiency metrics."""
        # CPU overhead (from tracer processing)
        cpu_overhead = metrics.tracer_overhead_percent
        
        # Memory overhead
        memory_overhead = metrics.memory_overhead_percent
        
        # Throughput degradation (estimated from latency overhead)
        throughput_degradation = min(cpu_overhead * 0.8, 50.0)  # Conservative estimate
        
        # Latency overhead in milliseconds
        latency_overhead_ms = system_data.get('avg_latency_ms', 0) * (cpu_overhead / 100)
        
        # Resource utilization score (inverse of overhead)
        resource_score = max(0, 100 - (cpu_overhead + memory_overhead) / 2)
        
        return CoreEfficiencyMetrics(
            cpu_overhead_percent=cpu_overhead,
            memory_overhead_percent=memory_overhead,
            throughput_degradation_percent=throughput_degradation,
            latency_overhead_ms=latency_overhead_ms,
            resource_utilization_score=resource_score
        )
    
    def _calculate_accuracy_fidelity(
        self,
        metrics: PerformanceMetrics,
        trace_data: Dict[str, Any]
    ) -> AccuracyFidelityMetrics:
        """Calculate accuracy and fidelity metrics."""
        # Trace coverage
        trace_coverage = metrics.trace_coverage_percent
        
        # Attribute completeness
        attribute_completeness = metrics.attribute_completeness_percent
        
        # Semantic accuracy (from trace validation)
        semantic_accuracy = trace_data.get('semantic_accuracy_percent', 85.0)
        
        # Span hierarchy correctness
        hierarchy_correctness = trace_data.get('hierarchy_correctness_percent', 90.0)
        
        # Timing accuracy (estimated from span duration consistency)
        timing_accuracy = trace_data.get('timing_accuracy_percent', 95.0)
        
        # Overall data fidelity score
        fidelity_score = statistics.mean([
            trace_coverage, attribute_completeness, semantic_accuracy,
            hierarchy_correctness, timing_accuracy
        ])
        
        return AccuracyFidelityMetrics(
            trace_coverage_percent=trace_coverage,
            attribute_completeness_percent=attribute_completeness,
            semantic_accuracy_percent=semantic_accuracy,
            span_hierarchy_correctness=hierarchy_correctness,
            timing_accuracy_percent=timing_accuracy,
            data_fidelity_score=fidelity_score
        )
    
    def _calculate_reliability_loss(
        self,
        metrics: PerformanceMetrics,
        system_data: Dict[str, Any]
    ) -> ReliabilityLossMetrics:
        """Calculate reliability and loss metrics."""
        # Dropped span rate
        dropped_spans = metrics.dropped_span_rate_percent
        
        # Export failure rate (estimated from system data)
        export_failures = system_data.get('export_failure_rate_percent', 0.0)
        
        # Overall data loss rate
        data_loss = max(dropped_spans, export_failures)
        
        # System stability score (inverse of failure rates)
        stability_score = max(0, 100 - (dropped_spans + export_failures))
        
        # Error recovery time
        recovery_time = system_data.get('error_recovery_time_ms', 1000.0)
        
        # Uptime percentage
        uptime = system_data.get('uptime_percentage', 99.9)
        
        return ReliabilityLossMetrics(
            dropped_span_rate_percent=dropped_spans,
            export_failure_rate_percent=export_failures,
            data_loss_rate_percent=data_loss,
            system_stability_score=stability_score,
            error_recovery_time_ms=recovery_time,
            uptime_percentage=uptime
        )
    
    def _calculate_context_correlation(self, trace_data: Dict[str, Any]) -> ContextCorrelationMetrics:
        """Calculate context and correlation metrics."""
        # Session correlation accuracy
        session_correlation = trace_data.get('session_correlation_accuracy', 95.0)
        
        # Conversation continuity
        conversation_continuity = trace_data.get('conversation_continuity_score', 90.0)
        
        # Cross-service correlation
        cross_service = trace_data.get('cross_service_correlation', 85.0)
        
        # Context propagation success
        context_propagation = trace_data.get('context_propagation_success', 95.0)
        
        # Distributed trace completeness
        distributed_completeness = trace_data.get('distributed_trace_completeness', 90.0)
        
        # Overall correlation quality
        correlation_quality = statistics.mean([
            session_correlation, conversation_continuity, cross_service,
            context_propagation, distributed_completeness
        ])
        
        return ContextCorrelationMetrics(
            session_correlation_accuracy=session_correlation,
            conversation_continuity_score=conversation_continuity,
            cross_service_correlation=cross_service,
            context_propagation_success=context_propagation,
            distributed_trace_completeness=distributed_completeness,
            correlation_quality_score=correlation_quality
        )
    
    def _calculate_cost_payload(
        self,
        metrics: PerformanceMetrics,
        system_data: Dict[str, Any]
    ) -> CostPayloadMetrics:
        """Calculate cost and payload metrics."""
        # Network overhead (estimated from export data)
        network_overhead = system_data.get('network_overhead_bytes', 1024.0)
        
        # Storage overhead per span
        storage_overhead = system_data.get('storage_overhead_bytes', 512.0)
        
        # Export payload size
        payload_size = system_data.get('export_payload_size_bytes', 2048.0)
        
        # Bandwidth utilization
        bandwidth_util = system_data.get('bandwidth_utilization_percent', 5.0)
        
        # Storage efficiency (inverse of overhead)
        storage_efficiency = max(0, 100 - min(storage_overhead / 100, 50))
        
        # Cost efficiency (composite score)
        cost_efficiency = max(0, 100 - (bandwidth_util + storage_overhead / 100))
        
        return CostPayloadMetrics(
            network_overhead_bytes=network_overhead,
            storage_overhead_bytes=storage_overhead,
            export_payload_size_bytes=payload_size,
            bandwidth_utilization_percent=bandwidth_util,
            storage_efficiency_score=storage_efficiency,
            cost_efficiency_score=cost_efficiency
        )
    
    def _calculate_overall_score(
        self,
        core_efficiency: CoreEfficiencyMetrics,
        accuracy_fidelity: AccuracyFidelityMetrics,
        reliability_loss: ReliabilityLossMetrics,
        context_correlation: ContextCorrelationMetrics,
        cost_payload: CostPayloadMetrics
    ) -> float:
        """Calculate overall composite score."""
        # Weighted average of category scores
        weights = {
            'efficiency': 0.25,      # 25% - Core performance
            'fidelity': 0.30,        # 30% - Data quality (most important)
            'reliability': 0.25,     # 25% - System stability
            'correlation': 0.15,     # 15% - Context tracking
            'cost': 0.05            # 5% - Resource efficiency
        }
        
        weighted_score = (
            core_efficiency.resource_utilization_score * weights['efficiency'] +
            accuracy_fidelity.data_fidelity_score * weights['fidelity'] +
            reliability_loss.system_stability_score * weights['reliability'] +
            context_correlation.correlation_quality_score * weights['correlation'] +
            cost_payload.cost_efficiency_score * weights['cost']
        )
        
        return round(weighted_score, 2)
    
    def _generate_recommendations(
        self,
        core_efficiency: CoreEfficiencyMetrics,
        accuracy_fidelity: AccuracyFidelityMetrics,
        reliability_loss: ReliabilityLossMetrics,
        context_correlation: ContextCorrelationMetrics,
        cost_payload: CostPayloadMetrics
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Core efficiency recommendations
        if core_efficiency.cpu_overhead_percent > 5.0:
            recommendations.append("🔧 Optimize span processing to reduce CPU overhead")
        if core_efficiency.memory_overhead_percent > 20.0:
            recommendations.append("💾 Implement memory pooling to reduce memory overhead")
        
        # Accuracy & fidelity recommendations
        if accuracy_fidelity.trace_coverage_percent < 95.0:
            recommendations.append("📊 Improve instrumentation coverage for complete traces")
        if accuracy_fidelity.attribute_completeness_percent < 90.0:
            recommendations.append("🏷️ Enhance attribute collection for better observability")
        
        # Reliability recommendations
        if reliability_loss.dropped_span_rate_percent > 1.0:
            recommendations.append("🛡️ Implement span buffering to reduce data loss")
        if reliability_loss.export_failure_rate_percent > 0.5:
            recommendations.append("🔄 Add export retry logic with exponential backoff")
        
        # Context correlation recommendations
        if context_correlation.correlation_quality_score < 90.0:
            recommendations.append("🔗 Improve context propagation across service boundaries")
        
        # Cost optimization recommendations
        if cost_payload.cost_efficiency_score < 80.0:
            recommendations.append("💰 Optimize payload size and compression for cost efficiency")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ Performance is excellent - consider advanced optimizations")
        
        return recommendations
