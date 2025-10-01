"""
Report Formatter Module

This module provides enhanced report formatting and visualization for tracer
performance benchmarks. Includes north-star metrics display, comparison tables,
and comprehensive analysis. Follows Agent OS production code standards.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..core.metrics import PerformanceMetrics
from .metrics_calculator import NorthStarMetrics, MetricsCalculator

logger = logging.getLogger(__name__)


class ReportFormatter:
    """Enhanced report formatter for benchmark results visualization.
    
    Provides comprehensive formatting for benchmark results including north-star
    metrics, detailed analysis, comparison tables, and actionable recommendations.
    Supports both console output and structured data export.
    
    Example:
        >>> formatter = ReportFormatter()
        >>> report = formatter.generate_comprehensive_report(
        ...     metrics_list=[openai_metrics, anthropic_metrics],
        ...     config=benchmark_config
        ... )
        >>> print(report)
    """
    
    def __init__(self) -> None:
        """Initialize report formatter."""
        self.calculator = MetricsCalculator()
        logger.debug("📊 ReportFormatter initialized")
    
    def generate_comprehensive_report(
        self,
        metrics_list: List[PerformanceMetrics],
        config: Any,
        additional_stats: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate comprehensive benchmark report with all metrics and analysis.
        
        :param metrics_list: List of performance metrics for all providers/modes
        :type metrics_list: List[PerformanceMetrics]
        :param config: Benchmark configuration used
        :type config: Any
        :param additional_stats: Additional statistics to include
        :type additional_stats: Optional[Dict[str, Any]]
        :return: Formatted report string
        :rtype: str
        
        Example:
            >>> formatter = ReportFormatter()
            >>> metrics = [openai_sequential, anthropic_sequential, ...]
            >>> report = formatter.generate_comprehensive_report(
            ...     metrics_list=metrics,
            ...     config=benchmark_config
            ... )
        """
        report_lines = []
        
        # Header
        report_lines.extend(self._generate_header())
        
        # Configuration summary
        report_lines.extend(self._generate_configuration_summary(config))
        
        # North-star metrics table
        report_lines.append(self.generate_north_star_table(metrics_list))
        
        # Detailed analysis for each metric
        report_lines.extend(self._generate_detailed_analysis(metrics_list))
        
        # Performance assessment
        report_lines.extend(self._generate_performance_assessment(metrics_list))
        
        # Recommendations
        report_lines.extend(self._generate_recommendations(metrics_list))
        
        # Additional statistics
        if additional_stats:
            report_lines.extend(self._generate_additional_stats(additional_stats))
        
        # Footer
        report_lines.extend(self._generate_footer())
        
        report = "\n".join(report_lines)
        logger.debug("📊 Comprehensive report generated")
        return report
    
    def _generate_header(self) -> List[str]:
        """Generate report header.
        
        :return: List of header lines
        :rtype: List[str]
        """
        return [
            "🎯 Multi-LLM Tracer Performance Benchmark Report",
            "=" * 60,
            "",
        ]
    
    def _generate_configuration_summary(self, config: Any) -> List[str]:
        """Generate configuration summary section.
        
        :param config: Benchmark configuration
        :type config: Any
        :return: List of configuration lines
        :rtype: List[str]
        """
        lines = [
            "📋 Configuration:",
            f"   Operations per provider: {getattr(config, 'operations', 'N/A')}",
            f"   Concurrent threads: {getattr(config, 'concurrent_threads', 'N/A')}",
            f"   OpenAI model: {getattr(config, 'openai_model', 'N/A')}",
            f"   Anthropic model: {getattr(config, 'anthropic_model', 'N/A')}",
            f"   Max tokens: {getattr(config, 'max_tokens', 'N/A')}",
            f"   Span size mode: {getattr(config, 'span_size_mode', 'mixed')}",
            f"   Conversation mode: {getattr(config, 'conversation_mode', True)}",
            "",
        ]
        return lines
    
    def _generate_north_star_summary(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate north-star metrics summary.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: List of north-star summary lines
        :rtype: List[str]
        """
        lines = [
            "⭐ North-Star Metrics Summary:",
            "",
        ]
        
        # Extract north-star metrics for each provider/mode
        for metrics in metrics_list:
            north_star = self.calculator.extract_north_star_metrics(metrics)
            
            lines.extend([
                f"🎯 {metrics.provider.upper()} - {metrics.mode.title()}:",
                f"   Cost of Tracing: {north_star.overhead_latency_percent:.2f}% latency + {north_star.memory_overhead_percent:.2f}% memory",
                f"   Fidelity of Data: {north_star.trace_coverage_percent:.1f}% coverage + {north_star.attribute_completeness_percent:.1f}% completeness",
                f"   Pipeline Reliability: {north_star.dropped_span_rate_percent:.1f}% drops + {north_star.export_latency_p95_ms:.1f}ms P95 export",
                "",
            ])
        
        return lines
    
    def _generate_performance_table(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate performance results table.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: List of table lines
        :rtype: List[str]
        """
        lines = [
            "📊 Performance Results:",
            "",
            "Provider    | Mode       | Ops/Sec | Avg Lat | P95 Lat | Tracer OH | Net I/O | Success",
            "------------|------------|---------|---------|---------|-----------|---------|--------",
        ]
        
        for metrics in metrics_list:
            # Format values for display
            ops_per_sec = f"{metrics.operations_per_second:.1f}"
            avg_lat = f"{metrics.avg_latency:.0f}ms"
            p95_lat = f"{metrics.p95_latency:.0f}ms"
            tracer_oh = f"{metrics.tracer_overhead_percent:.2f}%"
            net_io = f"{metrics.network_bytes_per_operation/1024:.1f}KB"
            success = f"{metrics.success_rate:.1f}%"
            
            line = f"{metrics.provider:<12}| {metrics.mode:<11}| {ops_per_sec:>7} | {avg_lat:>7} | {p95_lat:>7} | {tracer_oh:>9} | {net_io:>7} | {success:>7}"
            lines.append(line)
        
        lines.append("")
        return lines
    
    def _generate_detailed_analysis(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate detailed analysis for each provider/mode.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: List of detailed analysis lines
        :rtype: List[str]
        """
        lines = [
            "🔍 Detailed Analysis:",
            "",
        ]
        
        for metrics in metrics_list:
            lines.extend([
                f"📈 {metrics.provider.upper()} - {metrics.mode.title()}:",
                f"   Total Operations: {metrics.total_operations}",
                f"   Total Time: {metrics.total_time:.2f}s",
                f"   Operations/Second: {metrics.operations_per_second:.1f}",
                f"   Latency (avg/min/max): {metrics.avg_latency:.0f}/{metrics.min_latency:.0f}/{metrics.max_latency:.0f}ms",
                f"   Latency (P95/P99): {metrics.p95_latency:.0f}/{metrics.p99_latency:.0f}ms",
            f"   Real Tracer Overhead: {metrics.tracer_overhead:.2f}ms ({metrics.tracer_overhead_percent:.2f}%)",
            f"   Span Processing: {metrics.span_processing_time_ms:.2f}ms per operation",
                f"   Network I/O: {metrics.network_bytes_per_operation:.0f} bytes/op, {metrics.network_export_latency_ms:.1f}ms export latency",
                f"   Telemetry Requests: {metrics.network_requests_count} ({metrics.network_bytes_sent + metrics.network_bytes_received} bytes total)",
                f"   Memory (baseline/peak): {metrics.memory_baseline_mb:.1f}/{metrics.memory_peak_mb:.1f}MB",
                f"   Memory Overhead: {metrics.memory_overhead_mb:.2f}MB ({metrics.memory_overhead_percent:.2f}%)",
                f"   Success Rate: {metrics.success_rate:.1f}%",
                f"   Errors: {metrics.error_count}",
            ])
            
            # Add trace validation metrics if available
            if metrics.trace_coverage_percent is not None:
                lines.append(f"   Trace Coverage: {metrics.trace_coverage_percent:.1f}%")
            if metrics.attribute_completeness_percent is not None:
                lines.append(f"   Attribute Completeness: {metrics.attribute_completeness_percent:.1f}%")
            
            lines.append("")
        
        return lines
    
    def _generate_performance_assessment(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate performance assessment with pass/fail criteria.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: List of assessment lines
        :rtype: List[str]
        """
        lines = [
            "🎯 Performance Assessment:",
            "",
        ]
        
        all_passed = True
        
        for metrics in metrics_list:
            provider_mode = f"{metrics.provider.upper()} {metrics.mode.title()}"
            
            # Success rate assessment
            success_status = "✅" if metrics.success_rate >= 99.0 else "⚠️" if metrics.success_rate >= 95.0 else "❌"
            lines.append(f"{success_status} {provider_mode} Success Rate: {metrics.success_rate:.1f}%")
            
            # Latency assessment
            latency_status = "✅" if metrics.p95_latency <= 5000 else "⚠️" if metrics.p95_latency <= 10000 else "❌"
            lines.append(f"{latency_status} {provider_mode} P95 Latency: {metrics.p95_latency:.0f}ms")
            
            # Memory overhead assessment
            memory_status = "✅" if metrics.memory_overhead_percent <= 5.0 else "⚠️" if metrics.memory_overhead_percent <= 10.0 else "❌"
            lines.append(f"{memory_status} {provider_mode} Memory Overhead: {metrics.memory_overhead_percent:.2f}%")
            
            # Tracer overhead assessment
            tracer_status = "✅" if metrics.tracer_overhead_percent <= 2.0 else "⚠️" if metrics.tracer_overhead_percent <= 5.0 else "❌"
            lines.append(f"{tracer_status} {provider_mode} Tracer Overhead: {metrics.tracer_overhead_percent:.2f}%")
            
            # Check if any failed
            if any(status == "❌" for status in [success_status, latency_status, memory_status, tracer_status]):
                all_passed = False
        
        lines.extend([
            "",
            f"🎉 All performance tests {'PASSED' if all_passed else 'FAILED'}!" if all_passed else "⚠️ Some performance tests failed - see details above",
            "",
        ])
        
        return lines
    
    def _generate_recommendations(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate actionable recommendations based on results.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: List of recommendation lines
        :rtype: List[str]
        """
        lines = [
            "📝 Recommendations:",
            "",
        ]
        
        # Analyze metrics for recommendations
        high_latency_providers = [m for m in metrics_list if m.p95_latency > 3000]
        high_memory_providers = [m for m in metrics_list if m.memory_overhead_percent > 5.0]
        low_success_providers = [m for m in metrics_list if m.success_rate < 99.0]
        
        # General recommendations
        lines.extend([
            "• Monitor P95 latency for production workloads",
            "• Consider connection pooling for high-throughput scenarios",
            "• Implement circuit breakers for API resilience",
            "• Use async patterns for concurrent operations",
            "• Monitor memory usage in long-running applications",
        ])
        
        # Specific recommendations based on results
        if high_latency_providers:
            providers = ", ".join([f"{m.provider} {m.mode}" for m in high_latency_providers])
            lines.append(f"• High latency detected in {providers} - consider optimization")
        
        if high_memory_providers:
            providers = ", ".join([f"{m.provider} {m.mode}" for m in high_memory_providers])
            lines.append(f"• High memory overhead in {providers} - investigate memory leaks")
        
        if low_success_providers:
            providers = ", ".join([f"{m.provider} {m.mode}" for m in low_success_providers])
            lines.append(f"• Low success rate in {providers} - check error handling")
        
        # Performance optimization suggestions
        concurrent_metrics = [m for m in metrics_list if m.mode == "concurrent"]
        sequential_metrics = [m for m in metrics_list if m.mode == "sequential"]
        
        if concurrent_metrics and sequential_metrics:
            lines.append("• Concurrent mode shows improved throughput - consider for production")
        
        lines.append("")
        return lines
    
    def _generate_additional_stats(self, additional_stats: Dict[str, Any]) -> List[str]:
        """Generate additional statistics section.
        
        :param additional_stats: Additional statistics to display
        :type additional_stats: Dict[str, Any]
        :return: List of additional stats lines
        :rtype: List[str]
        """
        lines = [
            "📈 Additional Statistics:",
            "",
        ]
        
        for key, value in additional_stats.items():
            lines.append(f"   {key}: {value}")
        
        lines.append("")
        return lines
    
    def _generate_footer(self) -> List[str]:
        """Generate report footer.
        
        :return: List of footer lines
        :rtype: List[str]
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        return [
            f"Generated at: {timestamp}",
            "",
        ]
    
    def generate_north_star_table(self, metrics_list: List[PerformanceMetrics]) -> str:
        """Generate a focused table with just the six north-star metrics.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: Formatted north-star metrics table
        :rtype: str
        
        Example:
            >>> formatter = ReportFormatter()
            >>> table = formatter.generate_north_star_table(metrics_list)
            >>> print(table)
        """
        lines = [
            "",
            "=" * 120,
            "📊 NORTH-STAR METRICS SUMMARY",
            "=" * 120,
            "",
            self._generate_benchmark_context_summary(),
            "",
            f"{'Instrumentor':<15} {'Provider':<10} {'Mode':<12} {'Overhead':<11} {'Drops':<8} {'Export':<10} {'Coverage':<10} {'Complete':<10} {'Memory':<9}",
            "-" * 122,
        ]
        
        # Sort metrics by instrumentor, provider, then mode for consistent ordering
        def sort_key(metrics):
            provider_parts = metrics.provider.split('_', 1)
            if len(provider_parts) == 2:
                instrumentor = provider_parts[0]  # openinference, traceloop
                provider = provider_parts[1]     # openai, anthropic
            else:
                instrumentor = metrics.provider
                provider = "unknown"
            
            # Sort order: instrumentor (alphabetical), provider (alphabetical), mode (sequential first)
            mode_priority = 0 if metrics.mode == "sequential" else 1
            return (instrumentor, provider, mode_priority)
        
        sorted_metrics = sorted(metrics_list, key=sort_key)
        
        for metrics in sorted_metrics:
            north_star = self.calculator.extract_north_star_metrics(metrics)
            
            # Parse provider name to separate instrumentor and provider
            provider_parts = metrics.provider.split('_', 1)
            if len(provider_parts) == 2:
                instrumentor = provider_parts[0].title()  # openinference -> Openinference
                provider = provider_parts[1].upper()     # openai -> OPENAI
            else:
                instrumentor = metrics.provider
                provider = "Unknown"
            
            # Format values with better spacing (increased precision for overhead to show variance)
            overhead = f"{north_star.overhead_latency_percent:.2f}%"
            drops = f"{north_star.dropped_span_rate_percent:.1f}%"
            export = f"{north_star.export_latency_p95_ms:.0f}ms"
            coverage = f"{north_star.trace_coverage_percent:.1f}%"
            complete = f"{north_star.attribute_completeness_percent:.1f}%"
            memory = f"{north_star.memory_overhead_percent:.2f}%"
            
            line = f"{instrumentor:<15} {provider:<10} {metrics.mode:<12} {overhead:<11} {drops:<8} {export:<10} {coverage:<10} {complete:<10} {memory:<9}"
            lines.append(line)
        
        lines.extend([
            "-" * 122,
            "",
            "📋 Legend:",
            "  • Overhead: Additional CPU processing time added by tracing (lower is better)",
            "  • Drops: Percentage of spans lost before storage (0% is ideal)",
            "  • Export: P95 latency for span export to backend (lower is better)",
            "  • Coverage: Percentage of requests with complete traces (100% is ideal)",
            "  • Complete: Percentage of spans with all required attributes (100% is ideal)",
            "  • Memory: Additional memory overhead from tracing (lower is better)",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_benchmark_context_summary(self) -> str:
        """Generate a summary of the benchmark context and conversation simulation setup.
        
        :return: Formatted context summary
        :rtype: str
        """
        context_lines = [
            "🎯 BENCHMARK CONTEXT:",
            "",
            "📋 What We're Testing:",
            "  • Multi-instrumentor tracer performance comparison (OpenInference vs Traceloop)",
            "  • Real-world conversation simulation with varied complexity and span sizes",
            "  • True process isolation using multiprocessing for accurate memory measurement",
            "  • Both sequential and concurrent execution patterns",
            "  • Flexible provider selection for targeted performance analysis",
            "",
            "🎛️ Provider Selection:",
            "  • Default: All available instrumentor/provider pairings",
            "  • Targeted: Use --include for specific combinations",
            "  • Available: openinference_openai, openinference_anthropic, traceloop_openai, traceloop_anthropic",
            "  • Future-ready: Easy expansion for new instrumentors (LangSmith, OpenLIT, etc.)",
            "",
            "💬 Conversation Simulation Setup:",
            "  • 9 realistic conversation scenarios across 5 domains:",
            "    - Technical: Architecture explanations, how-to guides, system design",
            "    - Creative: Story writing, content generation",
            "    - Factual: Knowledge queries, information retrieval", 
            "    - Analytical: Comparative analysis, research synthesis",
            "    - Troubleshooting: Problem diagnosis, error resolution",
            "",
            "📏 Span Size Categories:",
            "  • Small (50-200 tokens): Quick questions, brief responses",
            "  • Medium (200-500 tokens): Detailed explanations, multi-step guidance", 
            "  • Large (500+ tokens): Comprehensive analysis, long-form content",
            "",
            "🔬 Testing Methodology:",
            "  • Deterministic prompt generation using seeded randomness for reproducibility",
            "  • Process-isolated execution for true memory overhead measurement",
            "  • Real API calls to OpenAI (GPT-4o) and Anthropic (Claude Sonnet 4)",
            "  • Real OTLP export latency measurement (no simulation)",
            "  • Comprehensive span interception for attribute completeness validation",
            "  • OpenTelemetry best practices: RSS_traced vs RSS_untraced baseline comparison",
            "  • CPU-only overhead measurement: excludes network I/O from processing time",
            "  • Sustained memory usage: average memory vs peak spikes for realistic overhead",
            "  • 2-decimal precision metrics to reveal performance variance",
            "",
        ]
        return "\n".join(context_lines)
    
    def generate_comparison_report(self, metrics_list: List[PerformanceMetrics]) -> str:
        """Generate provider comparison report.
        
        :param metrics_list: List of performance metrics to compare
        :type metrics_list: List[PerformanceMetrics]
        :return: Formatted comparison report
        :rtype: str
        """
        if len(metrics_list) < 2:
            return "Need at least 2 providers for comparison"
        
        comparison = self.calculator.compare_providers(metrics_list)
        
        lines = [
            "🔄 Provider Comparison Report:",
            "=" * 40,
            "",
            f"Best Latency: {comparison.get('best_latency_provider', 'N/A')}",
            f"Best Throughput: {comparison.get('best_throughput_provider', 'N/A')}",
            f"Lowest Overhead: {comparison.get('lowest_overhead_provider', 'N/A')}",
            f"Highest Reliability: {comparison.get('highest_reliability_provider', 'N/A')}",
            "",
        ]
        
        return "\n".join(lines)
    
    def export_structured_data(self, metrics_list: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Export metrics as structured data for further analysis.
        
        :param metrics_list: List of performance metrics
        :type metrics_list: List[PerformanceMetrics]
        :return: Structured metrics data
        :rtype: Dict[str, Any]
        """
        structured_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': [],
            'north_star_metrics': [],
            'summary': {},
        }
        
        for metrics in metrics_list:
            # Convert metrics to dict
            metrics_dict = {
                'provider': metrics.provider,
                'mode': metrics.mode,
                'total_operations': metrics.total_operations,
                'operations_per_second': metrics.operations_per_second,
                'avg_latency': metrics.avg_latency,
                'p95_latency': metrics.p95_latency,
                'tracer_overhead_percent': metrics.tracer_overhead_percent,
                'memory_overhead_percent': metrics.memory_overhead_percent,
                'success_rate': metrics.success_rate,
                'network_bytes_per_operation': metrics.network_bytes_per_operation,
                'trace_coverage_percent': metrics.trace_coverage_percent,
                'attribute_completeness_percent': metrics.attribute_completeness_percent,
            }
            structured_data['metrics'].append(metrics_dict)
            
            # Extract north-star metrics
            north_star = self.calculator.extract_north_star_metrics(metrics)
            north_star_dict = {
                'provider': metrics.provider,
                'mode': metrics.mode,
                'overhead_latency_percent': north_star.overhead_latency_percent,
                'dropped_span_rate_percent': north_star.dropped_span_rate_percent,
                'export_latency_p95_ms': north_star.export_latency_p95_ms,
                'trace_coverage_percent': north_star.trace_coverage_percent,
                'attribute_completeness_percent': north_star.attribute_completeness_percent,
                'memory_overhead_percent': north_star.memory_overhead_percent,
            }
            structured_data['north_star_metrics'].append(north_star_dict)
        
        # Add summary statistics
        if metrics_list:
            structured_data['summary'] = {
                'total_providers': len(set(m.provider for m in metrics_list)),
                'total_operations': sum(m.total_operations for m in metrics_list),
                'avg_success_rate': sum(m.success_rate for m in metrics_list) / len(metrics_list),
            }
        
        logger.debug(f"📊 Structured data exported for {len(metrics_list)} metrics")
        return structured_data
