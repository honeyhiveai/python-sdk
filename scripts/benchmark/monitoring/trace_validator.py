"""
Trace Validator Module

This module provides trace coverage and attribute completeness validation
for tracer performance benchmarks, implementing north-star metrics #4 and #5
from teammate feedback. Follows Agent OS production code standards.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

logger = logging.getLogger(__name__)


@dataclass
class SpanValidationResult:
    """Result of span validation for attribute completeness.
    
    :param span_id: Unique identifier for the span
    :type span_id: str
    :param has_root_span: Whether this request has a complete root span
    :type has_root_span: bool
    :param required_attributes_present: Set of required attributes that are present
    :type required_attributes_present: Set[str]
    :param missing_attributes: Set of required attributes that are missing
    :type missing_attributes: Set[str]
    :param attribute_completeness_percent: Percentage of required attributes present
    :type attribute_completeness_percent: float
    :param validation_timestamp: When this validation occurred
    :type validation_timestamp: float
    """
    span_id: str
    has_root_span: bool
    required_attributes_present: Set[str] = field(default_factory=set)
    missing_attributes: Set[str] = field(default_factory=set)
    attribute_completeness_percent: float = 0.0
    validation_timestamp: float = field(default_factory=time.time)


class TraceValidator:
    """Validator for trace coverage and attribute completeness metrics.
    
    Implements north-star metrics #4 (Trace Coverage) and #5 (Attribute Completeness)
    by monitoring spans and validating their structure and required attributes.
    
    North-Star Metric #4: Trace Coverage (%) - Share of requests with complete root span
    North-Star Metric #5: Attribute Completeness (%) - Spans with all required fields present
    
    :param required_attributes: Set of attribute names that must be present in spans
    :type required_attributes: Optional[Set[str]]
    
    Example:
        >>> validator = TraceValidator(required_attributes={
        ...     "http.method", "http.url", "http.status_code"
        ... })
        >>> validator.start_validation()
        >>> # ... perform traced operations ...
        >>> coverage = validator.get_trace_coverage_percent()
        >>> completeness = validator.get_attribute_completeness_percent()
    """
    
    def __init__(self, required_attributes: Optional[Set[str]] = None) -> None:
        """Initialize trace validator.
        
        :param required_attributes: Set of required attribute names for completeness validation
        :type required_attributes: Optional[Set[str]]
        """
        # Default required attributes for HoneyHive spans
        self.required_attributes = required_attributes or {
            "honeyhive.event_type",
            "honeyhive.project", 
            "honeyhive.session_id",
            "honeyhive.source",
            "service.name",
            "service.version",
        }
        
        # Validation state
        self.validation_active: bool = False
        self.total_requests: int = 0
        self.requests_with_root_span: int = 0
        self.span_validations: List[SpanValidationResult] = []
        self.trace_ids_seen: Set[str] = set()
        self.root_trace_ids: Set[str] = set()
        
        logger.debug(f"🔍 TraceValidator initialized with {len(self.required_attributes)} required attributes")
    
    def start_validation(self) -> None:
        """Start trace validation monitoring.
        
        Resets all counters and begins tracking trace coverage and attribute completeness.
        """
        self.validation_active = True
        self.total_requests = 0
        self.requests_with_root_span = 0
        self.span_validations = []
        self.trace_ids_seen = set()
        self.root_trace_ids = set()
        
        logger.debug("🔍 Trace validation started")
    
    def validate_span(self, span: ReadableSpan) -> SpanValidationResult:
        """Validate a single span for attribute completeness.
        
        :param span: The span to validate
        :type span: ReadableSpan
        :return: Validation result with completeness metrics
        :rtype: SpanValidationResult
        
        Example:
            >>> validator = TraceValidator()
            >>> result = validator.validate_span(span)
            >>> print(f"Completeness: {result.attribute_completeness_percent:.1f}%")
        """
        if not self.validation_active:
            logger.warning("Trace validation not active, starting automatically")
            self.start_validation()
        
        span_id = format(span.context.span_id, '016x')
        trace_id = format(span.context.trace_id, '032x')
        
        # Track trace IDs
        self.trace_ids_seen.add(trace_id)
        
        # Check if this is a root span (no parent)
        is_root_span = span.parent is None
        if is_root_span:
            self.root_trace_ids.add(trace_id)
        
        # Validate required attributes
        span_attributes = span.attributes or {}
        present_attributes = set()
        missing_attributes = set()
        
        for required_attr in self.required_attributes:
            if required_attr in span_attributes:
                present_attributes.add(required_attr)
            else:
                missing_attributes.add(required_attr)
        
        # Calculate completeness percentage
        completeness_percent = (len(present_attributes) / len(self.required_attributes)) * 100
        
        result = SpanValidationResult(
            span_id=span_id,
            has_root_span=is_root_span,
            required_attributes_present=present_attributes,
            missing_attributes=missing_attributes,
            attribute_completeness_percent=completeness_percent,
        )
        
        self.span_validations.append(result)
        
        logger.debug(
            f"🔍 Span validated: {span_id[:8]}... "
            f"completeness={completeness_percent:.1f}% "
            f"root={is_root_span}"
        )
        
        return result
    
    def record_request(self, has_complete_trace: bool = True) -> None:
        """Record a request for trace coverage calculation.
        
        :param has_complete_trace: Whether this request has a complete root span
        :type has_complete_trace: bool
        
        Example:
            >>> validator = TraceValidator()
            >>> validator.record_request(has_complete_trace=True)
            >>> coverage = validator.get_trace_coverage_percent()
        """
        if not self.validation_active:
            logger.warning("Trace validation not active, starting automatically")
            self.start_validation()
        
        self.total_requests += 1
        if has_complete_trace:
            self.requests_with_root_span += 1
        
        logger.debug(f"🔍 Request recorded: complete_trace={has_complete_trace}")
    
    def get_trace_coverage_percent(self) -> float:
        """Calculate trace coverage percentage (north-star metric #4).
        
        Returns the percentage of requests that have a complete root span.
        
        :return: Trace coverage percentage (0-100)
        :rtype: float
        
        Example:
            >>> validator = TraceValidator()
            >>> # ... record requests ...
            >>> coverage = validator.get_trace_coverage_percent()
            >>> print(f"Trace coverage: {coverage:.1f}%")
        """
        if self.total_requests == 0:
            return 0.0
        
        coverage = (self.requests_with_root_span / self.total_requests) * 100
        logger.debug(f"🔍 Trace coverage: {coverage:.1f}% ({self.requests_with_root_span}/{self.total_requests})")
        return coverage
    
    def get_attribute_completeness_percent(self) -> float:
        """Calculate attribute completeness percentage (north-star metric #5).
        
        Returns the percentage of spans that have all required attributes present.
        
        :return: Attribute completeness percentage (0-100)
        :rtype: float
        
        Example:
            >>> validator = TraceValidator()
            >>> # ... validate spans ...
            >>> completeness = validator.get_attribute_completeness_percent()
            >>> print(f"Attribute completeness: {completeness:.1f}%")
        """
        if not self.span_validations:
            return 0.0
        
        # Count spans with 100% attribute completeness
        complete_spans = sum(
            1 for result in self.span_validations 
            if result.attribute_completeness_percent == 100.0
        )
        
        completeness = (complete_spans / len(self.span_validations)) * 100
        logger.debug(f"🔍 Attribute completeness: {completeness:.1f}% ({complete_spans}/{len(self.span_validations)})")
        return completeness
    
    def get_average_attribute_completeness(self) -> float:
        """Calculate average attribute completeness across all spans.
        
        :return: Average completeness percentage across all validated spans
        :rtype: float
        """
        if not self.span_validations:
            return 0.0
        
        total_completeness = sum(result.attribute_completeness_percent for result in self.span_validations)
        average = total_completeness / len(self.span_validations)
        
        logger.debug(f"🔍 Average attribute completeness: {average:.1f}%")
        return average
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation summary with all metrics.
        
        :return: Dictionary containing all validation metrics and statistics
        :rtype: Dict[str, Any]
        
        Example:
            >>> validator = TraceValidator()
            >>> # ... perform validation ...
            >>> summary = validator.get_validation_summary()
            >>> print(f"Coverage: {summary['trace_coverage_percent']:.1f}%")
        """
        return {
            # North-star metrics
            'trace_coverage_percent': self.get_trace_coverage_percent(),
            'attribute_completeness_percent': self.get_attribute_completeness_percent(),
            
            # Additional metrics
            'average_attribute_completeness': self.get_average_attribute_completeness(),
            'total_requests': self.total_requests,
            'requests_with_root_span': self.requests_with_root_span,
            'total_spans_validated': len(self.span_validations),
            'unique_traces_seen': len(self.trace_ids_seen),
            'traces_with_root_spans': len(self.root_trace_ids),
            
            # Configuration
            'required_attributes_count': len(self.required_attributes),
            'required_attributes': list(self.required_attributes),
            
            # Validation details
            'validation_active': self.validation_active,
            'validation_results': self.span_validations,
        }
    
    def stop_validation(self) -> Dict[str, Any]:
        """Stop validation and return final summary.
        
        :return: Final validation summary with all metrics
        :rtype: Dict[str, Any]
        """
        self.validation_active = False
        summary = self.get_validation_summary()
        
        logger.debug(
            f"🔍 Trace validation stopped - "
            f"coverage: {summary['trace_coverage_percent']:.1f}%, "
            f"completeness: {summary['attribute_completeness_percent']:.1f}%"
        )
        
        return summary
    
    def reset(self) -> None:
        """Reset validator state for new validation session."""
        self.validation_active = False
        self.total_requests = 0
        self.requests_with_root_span = 0
        self.span_validations = []
        self.trace_ids_seen = set()
        self.root_trace_ids = set()
        
        logger.debug("🔍 Trace validator reset")
    
    def add_required_attribute(self, attribute_name: str) -> None:
        """Add a required attribute for completeness validation.
        
        :param attribute_name: Name of the required attribute
        :type attribute_name: str
        """
        self.required_attributes.add(attribute_name)
        logger.debug(f"🔍 Added required attribute: {attribute_name}")
    
    def remove_required_attribute(self, attribute_name: str) -> None:
        """Remove a required attribute from completeness validation.
        
        :param attribute_name: Name of the attribute to remove
        :type attribute_name: str
        """
        self.required_attributes.discard(attribute_name)
        logger.debug(f"🔍 Removed required attribute: {attribute_name}")
    
    def set_required_attributes(self, attributes: Set[str]) -> None:
        """Set the complete list of required attributes.
        
        :param attributes: Set of required attribute names
        :type attributes: Set[str]
        """
        self.required_attributes = attributes.copy()
        logger.debug(f"🔍 Set required attributes: {len(attributes)} attributes")
