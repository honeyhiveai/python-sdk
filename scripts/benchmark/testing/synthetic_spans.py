"""
Synthetic Spans Testing Module

This module provides synthetic span generation with known DAGs and fixed
durations for testing fidelity and attribution accuracy. Allows precise
validation of tracer behavior under controlled conditions.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import random

logger = logging.getLogger(__name__)


class SpanType(Enum):
    """Types of synthetic spans for different testing scenarios."""
    ROOT = "root"
    LLM_CALL = "llm_call"
    PREPROCESSING = "preprocessing"
    POSTPROCESSING = "postprocessing"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    INTERNAL_FUNCTION = "internal_function"


@dataclass
class SyntheticSpanNode:
    """A node in the synthetic span DAG.
    
    :param span_id: Unique identifier for this span
    :type span_id: str
    :param name: Human-readable name for the span
    :type name: str
    :param span_type: Type of span (root, llm_call, etc.)
    :type span_type: SpanType
    :param duration_ms: Fixed duration in milliseconds
    :type duration_ms: float
    :param attributes: Span attributes to set
    :type attributes: Dict[str, Any]
    :param children: Child span nodes
    :type children: List['SyntheticSpanNode']
    :param parent_id: Parent span ID (None for root)
    :type parent_id: Optional[str]
    """
    span_id: str
    name: str
    span_type: SpanType
    duration_ms: float
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['SyntheticSpanNode'] = field(default_factory=list)
    parent_id: Optional[str] = None
    
    def add_child(self, child: 'SyntheticSpanNode') -> None:
        """Add a child span to this node.
        
        :param child: Child span node to add
        :type child: SyntheticSpanNode
        """
        child.parent_id = self.span_id
        self.children.append(child)
    
    def get_total_duration(self) -> float:
        """Calculate total duration including all children.
        
        :return: Total duration in milliseconds
        :rtype: float
        """
        return self.duration_ms + sum(child.get_total_duration() for child in self.children)
    
    def get_span_count(self) -> int:
        """Count total number of spans in this subtree.
        
        :return: Total span count
        :rtype: int
        """
        return 1 + sum(child.get_span_count() for child in self.children)


@dataclass
class SyntheticSpanDAG:
    """A directed acyclic graph of synthetic spans for testing.
    
    :param name: Name of this DAG scenario
    :type name: str
    :param description: Description of what this DAG tests
    :type description: str
    :param root_span: Root span of the DAG
    :type root_span: SyntheticSpanNode
    :param expected_attributes: Expected attributes that should be present
    :type expected_attributes: Dict[str, Any]
    :param validation_rules: Rules for validating span correctness
    :type validation_rules: List[str]
    """
    name: str
    description: str
    root_span: SyntheticSpanNode
    expected_attributes: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)
    
    def get_all_spans(self) -> List[SyntheticSpanNode]:
        """Get all spans in the DAG in execution order.
        
        :return: List of all spans
        :rtype: List[SyntheticSpanNode]
        """
        spans = []
        
        def collect_spans(node: SyntheticSpanNode) -> None:
            spans.append(node)
            for child in node.children:
                collect_spans(child)
        
        collect_spans(self.root_span)
        return spans
    
    def get_expected_trace_structure(self) -> Dict[str, Any]:
        """Get the expected trace structure for validation.
        
        :return: Expected trace structure
        :rtype: Dict[str, Any]
        """
        return {
            "total_spans": self.root_span.get_span_count(),
            "total_duration_ms": self.root_span.get_total_duration(),
            "root_span_id": self.root_span.span_id,
            "span_types": [span.span_type.value for span in self.get_all_spans()],
            "expected_attributes": self.expected_attributes,
            "validation_rules": self.validation_rules
        }


class SyntheticSpanGenerator:
    """Generator for synthetic span DAGs with known characteristics.
    
    Creates controlled test scenarios with predictable span structures,
    durations, and attributes for precise tracer validation.
    
    :param seed: Random seed for reproducible generation
    :type seed: int
    
    Example:
        >>> generator = SyntheticSpanGenerator(seed=42)
        >>> dag = generator.create_llm_conversation_dag()
        >>> result = generator.execute_dag(dag, tracer)
        >>> print(f"Generated {result.actual_spans} spans")
    """
    
    def __init__(self, seed: int = 42) -> None:
        """Initialize synthetic span generator.
        
        :param seed: Random seed for reproducible generation
        :type seed: int
        """
        self.seed = seed
        random.seed(seed)
        logger.info(f"🧬 Synthetic Span Generator initialized with seed {seed}")
    
    def create_simple_llm_dag(self) -> SyntheticSpanDAG:
        """Create a simple LLM call DAG for basic testing.
        
        :return: Simple LLM DAG
        :rtype: SyntheticSpanDAG
        """
        root = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="llm_request",
            span_type=SpanType.ROOT,
            duration_ms=5000.0,
            attributes={
                "llm.request.model": "gpt-4o",
                "llm.request.max_tokens": 500,
                "llm.request.temperature": 0.7,
                "gen_ai.system": "openai",
                "gen_ai.request.model": "gpt-4o"
            }
        )
        
        return SyntheticSpanDAG(
            name="Simple LLM Call",
            description="Basic LLM request with standard attributes",
            root_span=root,
            expected_attributes={
                "llm.request.model": "gpt-4o",
                "gen_ai.system": "openai"
            },
            validation_rules=[
                "root_span_present",
                "model_attribute_present",
                "duration_within_range"
            ]
        )
    
    def create_complex_llm_dag(self) -> SyntheticSpanDAG:
        """Create a complex LLM DAG with preprocessing and postprocessing.
        
        :return: Complex LLM DAG
        :rtype: SyntheticSpanDAG
        """
        root = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="complex_llm_workflow",
            span_type=SpanType.ROOT,
            duration_ms=100.0,  # Root span overhead
            attributes={
                "workflow.type": "llm_processing",
                "workflow.complexity": "high"
            }
        )
        
        # Preprocessing step
        preprocessing = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="input_preprocessing",
            span_type=SpanType.PREPROCESSING,
            duration_ms=200.0,
            attributes={
                "preprocessing.type": "tokenization",
                "preprocessing.input_length": 150
            }
        )
        
        # Database lookup
        db_lookup = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="context_lookup",
            span_type=SpanType.DATABASE,
            duration_ms=50.0,
            attributes={
                "db.system": "postgresql",
                "db.operation": "select",
                "db.table": "context_store"
            }
        )
        
        # LLM call
        llm_call = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="llm_generation",
            span_type=SpanType.LLM_CALL,
            duration_ms=4500.0,
            attributes={
                "llm.request.model": "gpt-4o",
                "llm.request.max_tokens": 1000,
                "llm.request.temperature": 0.3,
                "gen_ai.system": "openai",
                "gen_ai.request.model": "gpt-4o",
                "gen_ai.usage.input_tokens": 150,
                "gen_ai.usage.output_tokens": 800
            }
        )
        
        # Postprocessing
        postprocessing = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="output_postprocessing",
            span_type=SpanType.POSTPROCESSING,
            duration_ms=150.0,
            attributes={
                "postprocessing.type": "formatting",
                "postprocessing.output_length": 800
            }
        )
        
        # Build DAG structure
        preprocessing.add_child(db_lookup)
        root.add_child(preprocessing)
        root.add_child(llm_call)
        root.add_child(postprocessing)
        
        return SyntheticSpanDAG(
            name="Complex LLM Workflow",
            description="Multi-step LLM workflow with preprocessing, DB lookup, and postprocessing",
            root_span=root,
            expected_attributes={
                "llm.request.model": "gpt-4o",
                "gen_ai.system": "openai",
                "db.system": "postgresql",
                "workflow.type": "llm_processing"
            },
            validation_rules=[
                "root_span_present",
                "child_spans_present",
                "model_attribute_present",
                "token_usage_present",
                "db_attributes_present",
                "duration_hierarchy_correct"
            ]
        )
    
    def create_conversation_dag(self, turns: int = 3) -> SyntheticSpanDAG:
        """Create a multi-turn conversation DAG.
        
        :param turns: Number of conversation turns
        :type turns: int
        :return: Conversation DAG
        :rtype: SyntheticSpanDAG
        """
        root = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="conversation_session",
            span_type=SpanType.ROOT,
            duration_ms=50.0,
            attributes={
                "conversation.session_id": str(uuid.uuid4()),
                "conversation.turns": turns,
                "conversation.type": "multi_turn"
            }
        )
        
        # Add conversation turns
        for turn in range(turns):
            turn_span = SyntheticSpanNode(
                span_id=str(uuid.uuid4()),
                name=f"conversation_turn_{turn + 1}",
                span_type=SpanType.LLM_CALL,
                duration_ms=3000.0 + random.uniform(-500, 500),  # Realistic variation
                attributes={
                    "conversation.turn": turn + 1,
                    "llm.request.model": "gpt-4o",
                    "gen_ai.system": "openai",
                    "gen_ai.request.model": "gpt-4o",
                    "gen_ai.usage.input_tokens": 100 + turn * 50,  # Context grows
                    "gen_ai.usage.output_tokens": 200 + random.randint(-50, 50)
                }
            )
            root.add_child(turn_span)
        
        return SyntheticSpanDAG(
            name=f"Conversation ({turns} turns)",
            description=f"Multi-turn conversation with {turns} LLM interactions",
            root_span=root,
            expected_attributes={
                "conversation.session_id": root.attributes["conversation.session_id"],
                "conversation.turns": turns,
                "llm.request.model": "gpt-4o"
            },
            validation_rules=[
                "root_span_present",
                "conversation_turns_correct",
                "session_id_consistent",
                "token_usage_progressive"
            ]
        )
    
    def create_error_scenario_dag(self) -> SyntheticSpanDAG:
        """Create a DAG with error scenarios for testing error handling.
        
        :return: Error scenario DAG
        :rtype: SyntheticSpanDAG
        """
        root = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="error_scenario",
            span_type=SpanType.ROOT,
            duration_ms=100.0,
            attributes={
                "scenario.type": "error_testing",
                "expected.errors": True
            }
        )
        
        # Successful preprocessing
        preprocessing = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="preprocessing_success",
            span_type=SpanType.PREPROCESSING,
            duration_ms=150.0,
            attributes={
                "status": "success",
                "preprocessing.type": "validation"
            }
        )
        
        # Failed LLM call
        failed_llm = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="llm_call_failed",
            span_type=SpanType.LLM_CALL,
            duration_ms=1000.0,
            attributes={
                "llm.request.model": "gpt-4o",
                "gen_ai.system": "openai",
                "error.type": "rate_limit_exceeded",
                "error.message": "Rate limit exceeded",
                "status": "error"
            }
        )
        
        # Retry LLM call (successful)
        retry_llm = SyntheticSpanNode(
            span_id=str(uuid.uuid4()),
            name="llm_call_retry",
            span_type=SpanType.LLM_CALL,
            duration_ms=3500.0,
            attributes={
                "llm.request.model": "gpt-4o",
                "gen_ai.system": "openai",
                "gen_ai.request.model": "gpt-4o",
                "retry.attempt": 2,
                "status": "success"
            }
        )
        
        # Build DAG
        root.add_child(preprocessing)
        root.add_child(failed_llm)
        root.add_child(retry_llm)
        
        return SyntheticSpanDAG(
            name="Error Scenario",
            description="Error handling with failed LLM call and successful retry",
            root_span=root,
            expected_attributes={
                "scenario.type": "error_testing",
                "error.type": "rate_limit_exceeded",
                "retry.attempt": 2
            },
            validation_rules=[
                "root_span_present",
                "error_span_present",
                "retry_span_present",
                "error_attributes_present",
                "status_attributes_correct"
            ]
        )
    
    def execute_dag(self, dag: SyntheticSpanDAG, tracer: Any) -> Dict[str, Any]:
        """Execute a synthetic DAG and measure tracer behavior.
        
        :param dag: Synthetic span DAG to execute
        :type dag: SyntheticSpanDAG
        :param tracer: Tracer instance to test
        :type tracer: Any
        :return: Execution results and validation metrics
        :rtype: Dict[str, Any]
        """
        logger.info(f"🧬 Executing synthetic DAG: {dag.name}")
        
        start_time = time.perf_counter()
        executed_spans = []
        
        def execute_span_node(node: SyntheticSpanNode, parent_span: Any = None) -> Any:
            """Execute a single span node and its children."""
            # Create span
            if parent_span:
                span = tracer.start_span(node.name, parent=parent_span)
            else:
                span = tracer.start_span(node.name)
            
            # Set attributes
            for key, value in node.attributes.items():
                span.set_attribute(key, value)
            
            # Simulate work (sleep for specified duration)
            time.sleep(node.duration_ms / 1000.0)
            
            # Execute children
            for child in node.children:
                execute_span_node(child, span)
            
            # End span
            span.end()
            executed_spans.append({
                "span_id": node.span_id,
                "name": node.name,
                "type": node.span_type.value,
                "duration_ms": node.duration_ms,
                "attributes": node.attributes
            })
            
            return span
        
        # Execute the DAG
        try:
            execute_span_node(dag.root_span)
            execution_success = True
            error_message = None
        except Exception as e:
            execution_success = False
            error_message = str(e)
            logger.error(f"❌ DAG execution failed: {e}")
        
        end_time = time.perf_counter()
        actual_duration = (end_time - start_time) * 1000
        
        # Validate results
        validation_results = self._validate_dag_execution(dag, executed_spans, actual_duration)
        
        results = {
            "dag_name": dag.name,
            "execution_success": execution_success,
            "error_message": error_message,
            "expected_spans": dag.root_span.get_span_count(),
            "actual_spans": len(executed_spans),
            "expected_duration_ms": dag.root_span.get_total_duration(),
            "actual_duration_ms": actual_duration,
            "duration_accuracy": abs(actual_duration - dag.root_span.get_total_duration()) / dag.root_span.get_total_duration() * 100,
            "executed_spans": executed_spans,
            "validation_results": validation_results
        }
        
        logger.info(f"✅ DAG execution completed: {len(executed_spans)} spans in {actual_duration:.1f}ms")
        return results
    
    def _validate_dag_execution(
        self,
        dag: SyntheticSpanDAG,
        executed_spans: List[Dict[str, Any]],
        actual_duration: float
    ) -> Dict[str, Any]:
        """Validate DAG execution against expected results.
        
        :param dag: Original DAG specification
        :type dag: SyntheticSpanDAG
        :param executed_spans: Actually executed spans
        :type executed_spans: List[Dict[str, Any]]
        :param actual_duration: Actual execution duration
        :type actual_duration: float
        :return: Validation results
        :rtype: Dict[str, Any]
        """
        validation_results = {
            "passed_rules": [],
            "failed_rules": [],
            "attribute_completeness": 0.0,
            "structure_correctness": 0.0,
            "duration_accuracy": 0.0
        }
        
        expected_structure = dag.get_expected_trace_structure()
        
        # Validate each rule
        for rule in dag.validation_rules:
            if self._validate_rule(rule, dag, executed_spans, actual_duration):
                validation_results["passed_rules"].append(rule)
            else:
                validation_results["failed_rules"].append(rule)
        
        # Calculate attribute completeness
        expected_attrs = set(dag.expected_attributes.keys())
        found_attrs = set()
        for span in executed_spans:
            found_attrs.update(span["attributes"].keys())
        
        if expected_attrs:
            validation_results["attribute_completeness"] = len(expected_attrs & found_attrs) / len(expected_attrs) * 100
        
        # Calculate structure correctness
        structure_score = 0
        if len(executed_spans) == expected_structure["total_spans"]:
            structure_score += 50
        if abs(actual_duration - expected_structure["total_duration_ms"]) < 100:  # Within 100ms
            structure_score += 50
        validation_results["structure_correctness"] = structure_score
        
        # Calculate duration accuracy
        expected_duration = expected_structure["total_duration_ms"]
        if expected_duration > 0:
            validation_results["duration_accuracy"] = max(0, 100 - abs(actual_duration - expected_duration) / expected_duration * 100)
        
        return validation_results
    
    def _validate_rule(self, rule: str, dag: SyntheticSpanDAG, executed_spans: List[Dict[str, Any]], actual_duration: float) -> bool:
        """Validate a specific rule against execution results.
        
        :param rule: Rule name to validate
        :type rule: str
        :param dag: Original DAG
        :type dag: SyntheticSpanDAG
        :param executed_spans: Executed spans
        :type executed_spans: List[Dict[str, Any]]
        :param actual_duration: Actual duration
        :type actual_duration: float
        :return: True if rule passes
        :rtype: bool
        """
        if rule == "root_span_present":
            return any(span["type"] == "root" for span in executed_spans)
        
        elif rule == "model_attribute_present":
            return any("llm.request.model" in span["attributes"] or "gen_ai.request.model" in span["attributes"] 
                      for span in executed_spans)
        
        elif rule == "duration_within_range":
            expected = dag.root_span.get_total_duration()
            return abs(actual_duration - expected) < expected * 0.1  # Within 10%
        
        elif rule == "child_spans_present":
            return len(executed_spans) > 1
        
        elif rule == "token_usage_present":
            return any("gen_ai.usage.input_tokens" in span["attributes"] for span in executed_spans)
        
        elif rule == "db_attributes_present":
            return any("db.system" in span["attributes"] for span in executed_spans)
        
        elif rule == "conversation_turns_correct":
            expected_turns = dag.expected_attributes.get("conversation.turns", 0)
            actual_turns = sum(1 for span in executed_spans if "conversation.turn" in span["attributes"])
            return actual_turns == expected_turns
        
        elif rule == "session_id_consistent":
            session_ids = [span["attributes"].get("conversation.session_id") for span in executed_spans 
                          if "conversation.session_id" in span["attributes"]]
            return len(set(session_ids)) <= 1  # All same or none
        
        elif rule == "error_span_present":
            return any("error.type" in span["attributes"] for span in executed_spans)
        
        elif rule == "retry_span_present":
            return any("retry.attempt" in span["attributes"] for span in executed_spans)
        
        else:
            logger.warning(f"Unknown validation rule: {rule}")
            return False
