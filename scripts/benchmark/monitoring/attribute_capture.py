"""
Attribute Capture Module

Comprehensive span attribute capture system for documenting real-world
instrumentor and framework span attribute formats.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
from opentelemetry.sdk.trace import ReadableSpan

logger = logging.getLogger(__name__)


@dataclass
class CapturedSpan:
    """Represents a captured span with all attributes for analysis.
    
    :param span_name: Name of the span
    :type span_name: str
    :param instrumentor: Instrumentor that created the span
    :type instrumentor: str
    :param provider: LLM provider (openai, anthropic, etc.)
    :type provider: str
    :param scenario: Test scenario that generated this span
    :type scenario: str
    :param attributes: All span attributes as dict
    :type attributes: Dict[str, Any]
    :param capture_timestamp: When this was captured
    :type capture_timestamp: str
    :param metadata: Additional metadata about the capture
    :type metadata: Dict[str, Any]
    """
    span_name: str
    instrumentor: str
    provider: str
    scenario: str
    attributes: Dict[str, Any]
    capture_timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpanAttributeCapture:
    """Captures and organizes span attributes for research and analysis.
    
    This class systematically captures span attributes from different
    instrumentors, providers, and scenarios to create a comprehensive
    reference for transform development.
    
    Example:
        >>> capture = SpanAttributeCapture(output_dir="span_captures")
        >>> capture.capture_span(span, "openinference", "openai", "basic_chat")
        >>> capture.save_captures()
    """
    
    def __init__(self, output_dir: str = "span_attribute_captures") -> None:
        """Initialize span attribute capture system.
        
        :param output_dir: Directory to save captured span data
        :type output_dir: str
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.captured_spans: List[CapturedSpan] = []
        self.capture_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"📸 Span attribute capture initialized: session={self.capture_session_id}")
    
    def capture_span(
        self,
        span: ReadableSpan,
        instrumentor: str,
        provider: str,
        scenario: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Capture a single span with all its attributes.
        
        :param span: The span to capture
        :type span: ReadableSpan
        :param instrumentor: Instrumentor name (openinference, traceloop, openlit, manual)
        :type instrumentor: str
        :param provider: Provider name (openai, anthropic, gemini, etc.)
        :type provider: str
        :param scenario: Scenario name (basic_chat, tool_calls, multimodal, etc.)
        :type scenario: str
        :param metadata: Additional metadata to store
        :type metadata: Optional[Dict[str, Any]]
        """
        # Extract all attributes
        attributes = {}
        if hasattr(span, 'attributes') and span.attributes:
            # Convert all values to JSON-serializable format
            for key, value in span.attributes.items():
                try:
                    # Test if value is JSON serializable
                    json.dumps(value)
                    attributes[key] = value
                except (TypeError, ValueError):
                    # Convert to string if not serializable
                    attributes[key] = str(value)
        
        # Get span name
        span_name = getattr(span, 'name', 'unknown')
        
        # Create captured span
        captured = CapturedSpan(
            span_name=span_name,
            instrumentor=instrumentor,
            provider=provider,
            scenario=scenario,
            attributes=attributes,
            capture_timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.captured_spans.append(captured)
        
        logger.debug(
            f"📸 Captured span: {instrumentor}/{provider}/{scenario} - "
            f"{len(attributes)} attributes"
        )
    
    def save_captures(self, filename: Optional[str] = None) -> Path:
        """Save all captured spans to JSON file.
        
        :param filename: Optional custom filename
        :type filename: Optional[str]
        :return: Path to saved file
        :rtype: Path
        """
        if not filename:
            filename = f"span_captures_{self.capture_session_id}.json"
        
        output_path = self.output_dir / filename
        
        # Convert to dict for JSON serialization
        data = {
            "capture_session_id": self.capture_session_id,
            "capture_count": len(self.captured_spans),
            "captured_at": datetime.now().isoformat(),
            "spans": [asdict(span) for span in self.captured_spans]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(
            f"📸 Saved {len(self.captured_spans)} captured spans to {output_path}"
        )
        
        return output_path
    
    def save_by_category(self) -> Dict[str, Path]:
        """Save captured spans organized by instrumentor/provider.
        
        :return: Dictionary mapping category to file path
        :rtype: Dict[str, Path]
        """
        # Group by instrumentor and provider
        categories: Dict[str, List[CapturedSpan]] = {}
        
        for captured in self.captured_spans:
            category = f"{captured.instrumentor}_{captured.provider}"
            if category not in categories:
                categories[category] = []
            categories[category].append(captured)
        
        # Save each category
        saved_files = {}
        for category, spans in categories.items():
            filename = f"{category}_{self.capture_session_id}.json"
            output_path = self.output_dir / category / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "category": category,
                "capture_session_id": self.capture_session_id,
                "span_count": len(spans),
                "captured_at": datetime.now().isoformat(),
                "spans": [asdict(span) for span in spans]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            saved_files[category] = output_path
            logger.info(f"📸 Saved {len(spans)} spans for {category} to {output_path}")
        
        return saved_files
    
    def generate_attribute_matrix(self) -> Dict[str, Any]:
        """Generate a matrix showing which attributes appear in which contexts.
        
        :return: Matrix data structure
        :rtype: Dict[str, Any]
        """
        # Collect all unique attributes
        all_attributes = set()
        for captured in self.captured_spans:
            all_attributes.update(captured.attributes.keys())
        
        # Build matrix: instrumentor/provider -> attributes
        matrix = {}
        for captured in self.captured_spans:
            key = f"{captured.instrumentor}/{captured.provider}"
            if key not in matrix:
                matrix[key] = {
                    "scenarios": set(),
                    "attributes": {},
                    "span_count": 0
                }
            
            matrix[key]["scenarios"].add(captured.scenario)
            matrix[key]["span_count"] += 1
            
            for attr_name in captured.attributes:
                if attr_name not in matrix[key]["attributes"]:
                    matrix[key]["attributes"][attr_name] = {
                        "count": 0,
                        "example_values": []
                    }
                
                matrix[key]["attributes"][attr_name]["count"] += 1
                
                # Store up to 3 example values
                if len(matrix[key]["attributes"][attr_name]["example_values"]) < 3:
                    value = captured.attributes[attr_name]
                    if value not in matrix[key]["attributes"][attr_name]["example_values"]:
                        matrix[key]["attributes"][attr_name]["example_values"].append(value)
        
        # Convert sets to lists for JSON serialization
        for key in matrix:
            matrix[key]["scenarios"] = list(matrix[key]["scenarios"])
        
        # Save matrix
        matrix_path = self.output_dir / f"attribute_matrix_{self.capture_session_id}.json"
        with open(matrix_path, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Generated attribute matrix: {matrix_path}")
        
        return matrix
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of captured spans.
        
        :return: Summary statistics
        :rtype: Dict[str, Any]
        """
        if not self.captured_spans:
            return {
                "total_spans": 0,
                "instrumentors": [],
                "providers": [],
                "scenarios": []
            }
        
        instrumentors = set(s.instrumentor for s in self.captured_spans)
        providers = set(s.provider for s in self.captured_spans)
        scenarios = set(s.scenario for s in self.captured_spans)
        
        # Count by combination
        combinations = {}
        for captured in self.captured_spans:
            key = f"{captured.instrumentor}/{captured.provider}"
            combinations[key] = combinations.get(key, 0) + 1
        
        return {
            "total_spans": len(self.captured_spans),
            "instrumentors": sorted(list(instrumentors)),
            "providers": sorted(list(providers)),
            "scenarios": sorted(list(scenarios)),
            "combinations": combinations,
            "capture_session_id": self.capture_session_id
        }
    
    def print_summary(self) -> None:
        """Print a human-readable summary of captured spans."""
        summary = self.get_summary()
        
        print("\n" + "=" * 80)
        print("📸 SPAN ATTRIBUTE CAPTURE SUMMARY")
        print("=" * 80)
        print(f"Session ID: {summary['capture_session_id']}")
        print(f"Total Spans Captured: {summary['total_spans']}")
        print(f"\nInstrumentors: {', '.join(summary['instrumentors'])}")
        print(f"Providers: {', '.join(summary['providers'])}")
        print(f"Scenarios: {', '.join(summary['scenarios'])}")
        print(f"\nCombinations:")
        for combo, count in sorted(summary['combinations'].items()):
            print(f"  {combo}: {count} spans")
        print("=" * 80 + "\n")
