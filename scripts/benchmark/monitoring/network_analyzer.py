"""
Network I/O Analyzer Module

This module provides detailed network analysis by separating:
1. LLM Network I/O (OpenAI/Anthropic API calls - inherent variability)
2. Tracer Network I/O (HoneyHive OTLP exports - our overhead)
3. Payload size analysis for both components

This helps distinguish between network variability from LLM APIs vs
actual tracer network overhead.
"""

import json
import logging
import statistics
import time
from typing import Dict, List, Any, Optional, Sequence, Tuple
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

logger = logging.getLogger(__name__)


class NetworkIOAnalyzer:
    """Analyze network I/O patterns separating LLM traffic from tracer traffic.
    
    This class provides detailed network analysis by monitoring:
    - LLM API call patterns (request/response sizes, latencies)
    - Tracer OTLP export patterns (span payload sizes, export latencies)
    - Network overhead breakdown and attribution
    
    Example:
        >>> analyzer = NetworkIOAnalyzer()
        >>> analyzer.start_monitoring()
        >>> # ... perform traced LLM operations ...
        >>> analysis = analyzer.get_network_analysis()
        >>> print(f"LLM traffic: {analysis['llm_traffic']['total_bytes']} bytes")
        >>> print(f"Tracer traffic: {analysis['tracer_traffic']['total_bytes']} bytes")
    """
    
    def __init__(self) -> None:
        """Initialize network I/O analysis."""
        # LLM Network I/O tracking
        self.llm_request_sizes: List[int] = []  # Estimated LLM request sizes
        self.llm_response_sizes: List[int] = []  # Estimated LLM response sizes
        self.llm_latencies: List[float] = []  # LLM API call latencies
        
        # Tracer Network I/O tracking
        self.tracer_export_sizes: List[int] = []  # OTLP export payload sizes
        self.tracer_export_latencies: List[float] = []  # OTLP export latencies
        self.tracer_request_count: int = 0
        
        # General tracking
        self.monitoring_active: bool = False
        self.start_time: Optional[float] = None
        self.wrapped_exporters: List[Any] = []
        
        logger.debug("🌐 NetworkIOAnalyzer initialized")
    
    def start_monitoring(self) -> None:
        """Start network I/O monitoring."""
        self.monitoring_active = True
        self.start_time = time.perf_counter()
        
        # Reset all counters
        self.llm_request_sizes.clear()
        self.llm_response_sizes.clear()
        self.llm_latencies.clear()
        self.tracer_export_sizes.clear()
        self.tracer_export_latencies.clear()
        self.tracer_request_count = 0
        
        logger.debug("🌐 Network I/O monitoring started")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return network analysis.
        
        :return: Comprehensive network I/O analysis
        :rtype: Dict[str, Any]
        """
        if not self.monitoring_active:
            logger.warning("Network I/O monitoring not active")
            return self._empty_analysis()
        
        self.monitoring_active = False
        
        return self.get_network_analysis()
    
    def record_llm_operation(self, 
                           request_size_bytes: int,
                           response_size_bytes: int, 
                           latency_ms: float) -> None:
        """Record an LLM API operation for network analysis.
        
        :param request_size_bytes: Size of LLM request payload
        :type request_size_bytes: int
        :param response_size_bytes: Size of LLM response payload
        :type response_size_bytes: int
        :param latency_ms: LLM API call latency in milliseconds
        :type latency_ms: float
        """
        if not self.monitoring_active:
            return
        
        self.llm_request_sizes.append(request_size_bytes)
        self.llm_response_sizes.append(response_size_bytes)
        self.llm_latencies.append(latency_ms)
        
        logger.debug(f"🌐 LLM operation: {request_size_bytes}B req, {response_size_bytes}B resp, {latency_ms:.1f}ms")
    
    def wrap_exporter(self, exporter: Any) -> None:
        """Wrap an OTLP exporter to monitor tracer network I/O.
        
        :param exporter: OTLP exporter to wrap
        :type exporter: Any
        """
        if hasattr(exporter, '_original_export'):
            logger.debug("🌐 Exporter already wrapped, skipping")
            return
        
        # Store original export method
        exporter._original_export = exporter.export
        
        # Replace with our intercepting version
        exporter.export = lambda spans: self._intercept_export(exporter, spans)
        
        self.wrapped_exporters.append(exporter)
        logger.debug(f"🌐 Wrapped OTLP exporter: {type(exporter).__name__}")
    
    def _intercept_export(self, exporter: Any, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Intercept OTLP export to measure tracer network I/O.
        
        :param exporter: The wrapped exporter
        :type exporter: Any
        :param spans: Spans to export
        :type spans: Sequence[ReadableSpan]
        :return: Export result
        :rtype: SpanExportResult
        """
        if not self.monitoring_active:
            return exporter._original_export(spans)
        
        # Estimate payload size (rough approximation)
        estimated_payload_size = self._estimate_otlp_payload_size(spans)
        
        # Measure export latency
        export_start = time.perf_counter()
        
        try:
            result = exporter._original_export(spans)
            
            export_end = time.perf_counter()
            export_latency_ms = (export_end - export_start) * 1000
            
            # Record tracer network I/O
            self.tracer_export_sizes.append(estimated_payload_size)
            self.tracer_export_latencies.append(export_latency_ms)
            self.tracer_request_count += 1
            
            logger.debug(f"🌐 Tracer export: {estimated_payload_size}B payload, {export_latency_ms:.1f}ms latency")
            
            return result
            
        except Exception as e:
            export_end = time.perf_counter()
            export_latency_ms = (export_end - export_start) * 1000
            
            # Still record the attempt
            self.tracer_export_sizes.append(estimated_payload_size)
            self.tracer_export_latencies.append(export_latency_ms)
            self.tracer_request_count += 1
            
            logger.debug(f"🌐 Tracer export failed: {estimated_payload_size}B payload, {export_latency_ms:.1f}ms latency, error: {e}")
            raise
    
    def _estimate_otlp_payload_size(self, spans: Sequence[ReadableSpan]) -> int:
        """Estimate OTLP payload size for spans.
        
        :param spans: Spans to estimate size for
        :type spans: Sequence[ReadableSpan]
        :return: Estimated payload size in bytes
        :rtype: int
        """
        if not spans:
            return 0
        
        # Rough estimation based on span complexity
        total_size = 0
        
        for span in spans:
            # Base span overhead (timestamps, IDs, etc.)
            span_base_size = 200  # bytes
            
            # Span name
            span_name = getattr(span, 'name', '')
            span_base_size += len(span_name.encode('utf-8'))
            
            # Attributes
            attributes = getattr(span, 'attributes', {}) or {}
            for key, value in attributes.items():
                key_size = len(str(key).encode('utf-8'))
                value_size = len(str(value).encode('utf-8'))
                span_base_size += key_size + value_size + 20  # JSON overhead
            
            # Events (if any)
            events = getattr(span, 'events', []) or []
            for event in events:
                span_base_size += 100  # Base event size
                if hasattr(event, 'attributes'):
                    event_attrs = getattr(event, 'attributes', {}) or {}
                    for key, value in event_attrs.items():
                        span_base_size += len(str(key).encode('utf-8')) + len(str(value).encode('utf-8'))
            
            total_size += span_base_size
        
        # Add OTLP protocol overhead (headers, compression, etc.)
        protocol_overhead = int(total_size * 0.1)  # ~10% overhead
        
        return total_size + protocol_overhead
    
    def estimate_llm_payload_sizes(self, prompt: str, response: str, model: str) -> Tuple[int, int]:
        """Estimate LLM request and response payload sizes.
        
        :param prompt: LLM input prompt
        :type prompt: str
        :param response: LLM response text
        :type response: str
        :param model: Model name
        :type model: str
        :return: Tuple of (request_size_bytes, response_size_bytes)
        :rtype: Tuple[int, int]
        """
        # Estimate request payload
        request_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.1
        }
        request_size = len(json.dumps(request_payload).encode('utf-8'))
        
        # Estimate response payload
        response_payload = {
            "choices": [{"message": {"content": response}}],
            "usage": {"total_tokens": len(response.split()) * 1.3}  # Rough token estimate
        }
        response_size = len(json.dumps(response_payload).encode('utf-8'))
        
        return request_size, response_size
    
    def get_network_analysis(self) -> Dict[str, Any]:
        """Get comprehensive network I/O analysis.
        
        :return: Detailed network analysis breakdown
        :rtype: Dict[str, Any]
        """
        if not self.llm_latencies and not self.tracer_export_latencies:
            return self._empty_analysis()
        
        # LLM traffic analysis
        llm_analysis = self._analyze_llm_traffic()
        
        # Tracer traffic analysis
        tracer_analysis = self._analyze_tracer_traffic()
        
        # Comparative analysis
        comparative_analysis = self._analyze_network_comparison(llm_analysis, tracer_analysis)
        
        return {
            "llm_traffic": llm_analysis,
            "tracer_traffic": tracer_analysis,
            "comparison": comparative_analysis,
            "summary": {
                "total_operations": len(self.llm_latencies),
                "total_exports": self.tracer_request_count,
                "monitoring_duration_ms": (time.perf_counter() - self.start_time) * 1000 if self.start_time else 0
            }
        }
    
    def _analyze_llm_traffic(self) -> Dict[str, Any]:
        """Analyze LLM network traffic patterns."""
        if not self.llm_latencies:
            return {
                "total_bytes": 0, 
                "request_bytes": 0,
                "response_bytes": 0,
                "avg_request_size": 0,
                "avg_response_size": 0,
                "avg_latency_ms": 0, 
                "latency_std_ms": 0,
                "latency_variability_percent": 0,
                "operation_count": 0
            }
        
        total_request_bytes = sum(self.llm_request_sizes) if self.llm_request_sizes else 0
        total_response_bytes = sum(self.llm_response_sizes) if self.llm_response_sizes else 0
        total_bytes = total_request_bytes + total_response_bytes
        
        avg_latency = statistics.mean(self.llm_latencies) if self.llm_latencies else 0
        latency_std = statistics.stdev(self.llm_latencies) if len(self.llm_latencies) > 1 else 0
        latency_cv = (latency_std / avg_latency) * 100 if avg_latency > 0 else 0
        
        return {
            "total_bytes": total_bytes,
            "request_bytes": total_request_bytes,
            "response_bytes": total_response_bytes,
            "avg_request_size": statistics.mean(self.llm_request_sizes) if self.llm_request_sizes else 0,
            "avg_response_size": statistics.mean(self.llm_response_sizes) if self.llm_response_sizes else 0,
            "avg_latency_ms": avg_latency,
            "latency_std_ms": latency_std,
            "latency_variability_percent": latency_cv,
            "operation_count": len(self.llm_latencies)
        }
    
    def _analyze_tracer_traffic(self) -> Dict[str, Any]:
        """Analyze tracer network traffic patterns."""
        if not self.tracer_export_latencies:
            return {
                "total_bytes": 0, 
                "avg_payload_size": 0,
                "avg_latency_ms": 0, 
                "latency_std_ms": 0,
                "latency_variability_percent": 0,
                "export_count": 0
            }
        
        total_bytes = sum(self.tracer_export_sizes) if self.tracer_export_sizes else 0
        avg_latency = statistics.mean(self.tracer_export_latencies) if self.tracer_export_latencies else 0
        latency_std = statistics.stdev(self.tracer_export_latencies) if len(self.tracer_export_latencies) > 1 else 0
        latency_cv = (latency_std / avg_latency) * 100 if avg_latency > 0 else 0
        
        return {
            "total_bytes": total_bytes,
            "avg_payload_size": statistics.mean(self.tracer_export_sizes) if self.tracer_export_sizes else 0,
            "avg_latency_ms": avg_latency,
            "latency_std_ms": latency_std,
            "latency_variability_percent": latency_cv,
            "export_count": self.tracer_request_count
        }
    
    def _analyze_network_comparison(self, llm_analysis: Dict[str, Any], tracer_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare LLM vs tracer network patterns."""
        llm_bytes = llm_analysis.get("total_bytes", 0)
        tracer_bytes = tracer_analysis.get("total_bytes", 0)
        total_bytes = llm_bytes + tracer_bytes
        
        llm_latency = llm_analysis.get("avg_latency_ms", 0)
        tracer_latency = tracer_analysis.get("avg_latency_ms", 0)
        
        return {
            "tracer_bytes_percent": (tracer_bytes / total_bytes * 100) if total_bytes > 0 else 0,
            "llm_bytes_percent": (llm_bytes / total_bytes * 100) if total_bytes > 0 else 0,
            "tracer_latency_ratio": (tracer_latency / llm_latency) if llm_latency > 0 else 0,
            "llm_variability_dominance": llm_analysis.get("latency_variability_percent", 0) / max(tracer_analysis.get("latency_variability_percent", 1), 1),
            "network_efficiency_score": self._calculate_network_efficiency(llm_analysis, tracer_analysis)
        }
    
    def _calculate_network_efficiency(self, llm_analysis: Dict[str, Any], tracer_analysis: Dict[str, Any]) -> float:
        """Calculate network efficiency score (0-100).
        
        Higher score = tracer adds minimal network overhead relative to LLM traffic.
        """
        tracer_bytes_ratio = tracer_analysis.get("total_bytes", 0) / max(llm_analysis.get("total_bytes", 1), 1)
        tracer_latency_ratio = tracer_analysis.get("avg_latency_ms", 0) / max(llm_analysis.get("avg_latency_ms", 1), 1)
        
        # Score based on how small tracer overhead is relative to LLM traffic
        bytes_score = max(0, 100 - (tracer_bytes_ratio * 100))
        latency_score = max(0, 100 - (tracer_latency_ratio * 100))
        
        return (bytes_score + latency_score) / 2
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "llm_traffic": {"total_bytes": 0, "avg_latency_ms": 0, "latency_variability": 0},
            "tracer_traffic": {"total_bytes": 0, "avg_latency_ms": 0, "latency_variability": 0},
            "comparison": {"tracer_bytes_percent": 0, "network_efficiency_score": 0},
            "summary": {"total_operations": 0, "total_exports": 0, "monitoring_duration_ms": 0}
        }
    
    def get_metrics_format(self) -> Dict[str, Any]:
        """Get network analysis data in the format expected by MetricsCalculator.
        
        :return: Flattened network analysis data for metrics calculation
        :rtype: Dict[str, Any]
        """
        analysis = self.get_network_analysis()
        
        # Extract LLM traffic data
        llm_traffic = analysis.get("llm_traffic", {})
        tracer_traffic = analysis.get("tracer_traffic", {})
        comparison = analysis.get("comparison", {})
        
        # Convert to MetricsCalculator format (bytes to KB)
        return {
            "llm_request_avg_kb": llm_traffic.get("avg_request_size", 0) / 1024,
            "llm_response_avg_kb": llm_traffic.get("avg_response_size", 0) / 1024,
            "llm_latency_avg_ms": llm_traffic.get("avg_latency_ms", 0.0),
            "tracer_export_avg_kb": tracer_traffic.get("avg_payload_size", 0) / 1024,
            "tracer_export_latency_avg_ms": tracer_traffic.get("avg_latency_ms", 0.0),
            "total_llm_traffic_kb": llm_traffic.get("total_bytes", 0) / 1024,
            "total_tracer_traffic_kb": tracer_traffic.get("total_bytes", 0) / 1024,
            "tracer_traffic_percent": comparison.get("tracer_bytes_percent", 0.0),
        }
    
    def cleanup(self) -> None:
        """Clean up wrapped exporters."""
        for exporter in self.wrapped_exporters:
            if hasattr(exporter, '_original_export'):
                exporter.export = exporter._original_export
                delattr(exporter, '_original_export')
        
        self.wrapped_exporters.clear()
        logger.debug("🌐 NetworkIOAnalyzer cleaned up")
