"""
Unit tests for synthetic spans testing module.

Tests the SyntheticSpanGenerator class for controlled span generation and validation.
"""

import pytest
from unittest.mock import Mock, patch
from ..testing.synthetic_spans import (
    SyntheticSpanGenerator, SyntheticSpanDAG, SyntheticSpanNode, SpanType
)


class TestSyntheticSpanNode:
    """Test cases for SyntheticSpanNode class."""
    
    def test_initialization(self):
        """Test SyntheticSpanNode initialization."""
        node = SyntheticSpanNode(
            span_id="test-span-1",
            name="test_span",
            span_type=SpanType.LLM_CALL,
            duration_ms=1000.0,
            attributes={"test": "value"}
        )
        
        assert node.span_id == "test-span-1"
        assert node.name == "test_span"
        assert node.span_type == SpanType.LLM_CALL
        assert node.duration_ms == 1000.0
        assert node.attributes == {"test": "value"}
        assert node.children == []
        assert node.parent_id is None
    
    def test_add_child(self):
        """Test adding child spans."""
        parent = SyntheticSpanNode(
            span_id="parent",
            name="parent_span",
            span_type=SpanType.ROOT,
            duration_ms=100.0
        )
        
        child = SyntheticSpanNode(
            span_id="child",
            name="child_span",
            span_type=SpanType.LLM_CALL,
            duration_ms=50.0
        )
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert child.parent_id == "parent"
    
    def test_get_total_duration(self):
        """Test total duration calculation."""
        parent = SyntheticSpanNode(
            span_id="parent",
            name="parent_span",
            span_type=SpanType.ROOT,
            duration_ms=100.0
        )
        
        child1 = SyntheticSpanNode(
            span_id="child1",
            name="child1_span",
            span_type=SpanType.LLM_CALL,
            duration_ms=200.0
        )
        
        child2 = SyntheticSpanNode(
            span_id="child2",
            name="child2_span",
            span_type=SpanType.PREPROCESSING,
            duration_ms=150.0
        )
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        # Total should be parent + all children
        assert parent.get_total_duration() == 450.0  # 100 + 200 + 150
    
    def test_get_span_count(self):
        """Test span count calculation."""
        parent = SyntheticSpanNode(
            span_id="parent",
            name="parent_span",
            span_type=SpanType.ROOT,
            duration_ms=100.0
        )
        
        child1 = SyntheticSpanNode(
            span_id="child1",
            name="child1_span",
            span_type=SpanType.LLM_CALL,
            duration_ms=200.0
        )
        
        grandchild = SyntheticSpanNode(
            span_id="grandchild",
            name="grandchild_span",
            span_type=SpanType.DATABASE,
            duration_ms=50.0
        )
        
        child1.add_child(grandchild)
        parent.add_child(child1)
        
        assert parent.get_span_count() == 3  # parent + child1 + grandchild


class TestSyntheticSpanDAG:
    """Test cases for SyntheticSpanDAG class."""
    
    def test_initialization(self):
        """Test SyntheticSpanDAG initialization."""
        root_span = SyntheticSpanNode(
            span_id="root",
            name="root_span",
            span_type=SpanType.ROOT,
            duration_ms=100.0
        )
        
        dag = SyntheticSpanDAG(
            name="Test DAG",
            description="Test description",
            root_span=root_span,
            expected_attributes={"test": "value"},
            validation_rules=["rule1", "rule2"]
        )
        
        assert dag.name == "Test DAG"
        assert dag.description == "Test description"
        assert dag.root_span == root_span
        assert dag.expected_attributes == {"test": "value"}
        assert dag.validation_rules == ["rule1", "rule2"]
    
    def test_get_all_spans(self):
        """Test getting all spans in execution order."""
        root = SyntheticSpanNode("root", "root", SpanType.ROOT, 100.0)
        child1 = SyntheticSpanNode("child1", "child1", SpanType.LLM_CALL, 200.0)
        child2 = SyntheticSpanNode("child2", "child2", SpanType.PREPROCESSING, 150.0)
        grandchild = SyntheticSpanNode("grandchild", "grandchild", SpanType.DATABASE, 50.0)
        
        child1.add_child(grandchild)
        root.add_child(child1)
        root.add_child(child2)
        
        dag = SyntheticSpanDAG("Test", "Description", root)
        all_spans = dag.get_all_spans()
        
        assert len(all_spans) == 4
        assert all_spans[0] == root
        assert all_spans[1] == child1
        assert all_spans[2] == grandchild
        assert all_spans[3] == child2
    
    def test_get_expected_trace_structure(self):
        """Test expected trace structure generation."""
        root = SyntheticSpanNode("root", "root", SpanType.ROOT, 100.0)
        child = SyntheticSpanNode("child", "child", SpanType.LLM_CALL, 200.0)
        root.add_child(child)
        
        dag = SyntheticSpanDAG(
            name="Test",
            description="Description",
            root_span=root,
            expected_attributes={"model": "gpt-4"},
            validation_rules=["rule1"]
        )
        
        structure = dag.get_expected_trace_structure()
        
        assert structure["total_spans"] == 2
        assert structure["total_duration_ms"] == 300.0
        assert structure["root_span_id"] == "root"
        assert structure["span_types"] == ["root", "llm_call"]
        assert structure["expected_attributes"] == {"model": "gpt-4"}
        assert structure["validation_rules"] == ["rule1"]


class TestSyntheticSpanGenerator:
    """Test cases for SyntheticSpanGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SyntheticSpanGenerator(seed=42)
    
    def test_initialization(self):
        """Test SyntheticSpanGenerator initialization."""
        assert self.generator.seed == 42
    
    def test_create_simple_llm_dag(self):
        """Test simple LLM DAG creation."""
        dag = self.generator.create_simple_llm_dag()
        
        assert isinstance(dag, SyntheticSpanDAG)
        assert dag.name == "Simple LLM Call"
        assert dag.root_span.span_type == SpanType.ROOT
        assert dag.root_span.duration_ms == 5000.0
        assert "llm.request.model" in dag.root_span.attributes
        assert dag.root_span.attributes["llm.request.model"] == "gpt-4o"
        assert len(dag.validation_rules) > 0
    
    def test_create_complex_llm_dag(self):
        """Test complex LLM DAG creation."""
        dag = self.generator.create_complex_llm_dag()
        
        assert isinstance(dag, SyntheticSpanDAG)
        assert dag.name == "Complex LLM Workflow"
        assert dag.root_span.span_type == SpanType.ROOT
        assert len(dag.root_span.children) == 3  # preprocessing, llm_call, postprocessing
        
        # Check that we have different span types
        all_spans = dag.get_all_spans()
        span_types = [span.span_type for span in all_spans]
        assert SpanType.ROOT in span_types
        assert SpanType.LLM_CALL in span_types
        assert SpanType.PREPROCESSING in span_types
        assert SpanType.POSTPROCESSING in span_types
        assert SpanType.DATABASE in span_types
    
    def test_create_conversation_dag(self):
        """Test conversation DAG creation."""
        turns = 3
        dag = self.generator.create_conversation_dag(turns=turns)
        
        assert isinstance(dag, SyntheticSpanDAG)
        assert dag.name == f"Conversation ({turns} turns)"
        assert dag.root_span.span_type == SpanType.ROOT
        assert len(dag.root_span.children) == turns
        
        # Check conversation attributes
        assert "conversation.session_id" in dag.root_span.attributes
        assert dag.root_span.attributes["conversation.turns"] == turns
        
        # Check turn spans
        for i, child in enumerate(dag.root_span.children):
            assert child.span_type == SpanType.LLM_CALL
            assert child.attributes["conversation.turn"] == i + 1
    
    def test_create_error_scenario_dag(self):
        """Test error scenario DAG creation."""
        dag = self.generator.create_error_scenario_dag()
        
        assert isinstance(dag, SyntheticSpanDAG)
        assert dag.name == "Error Scenario"
        assert dag.root_span.span_type == SpanType.ROOT
        assert len(dag.root_span.children) == 3  # success, failed, retry
        
        # Check for error attributes
        all_spans = dag.get_all_spans()
        error_span = next((span for span in all_spans if "error.type" in span.attributes), None)
        assert error_span is not None
        assert error_span.attributes["error.type"] == "rate_limit_exceeded"
        
        # Check for retry span
        retry_span = next((span for span in all_spans if "retry.attempt" in span.attributes), None)
        assert retry_span is not None
        assert retry_span.attributes["retry.attempt"] == 2
    
    @patch('time.sleep')
    @patch('time.perf_counter')
    def test_execute_dag(self, mock_time, mock_sleep):
        """Test DAG execution."""
        # Mock time progression
        mock_time.side_effect = [0.0, 1.0]  # 1 second execution
        
        # Create a simple DAG
        dag = self.generator.create_simple_llm_dag()
        
        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        
        # Execute DAG
        results = self.generator.execute_dag(dag, mock_tracer)
        
        assert results["dag_name"] == "Simple LLM Call"
        assert results["execution_success"] is True
        assert results["expected_spans"] == 1
        assert results["actual_spans"] == 1
        assert "validation_results" in results
        
        # Verify tracer interactions
        mock_tracer.start_span.assert_called_once()
        mock_span.set_attribute.assert_called()
        mock_span.end.assert_called_once()
    
    def test_validate_rule_root_span_present(self):
        """Test root span validation rule."""
        dag = self.generator.create_simple_llm_dag()
        executed_spans = [{"type": "root", "attributes": {}}]
        
        result = self.generator._validate_rule(
            "root_span_present", dag, executed_spans, 1000.0
        )
        assert result is True
        
        # Test failure case
        executed_spans_no_root = [{"type": "llm_call", "attributes": {}}]
        result = self.generator._validate_rule(
            "root_span_present", dag, executed_spans_no_root, 1000.0
        )
        assert result is False
    
    def test_validate_rule_model_attribute_present(self):
        """Test model attribute validation rule."""
        dag = self.generator.create_simple_llm_dag()
        
        # Test success case
        executed_spans = [{"type": "llm_call", "attributes": {"llm.request.model": "gpt-4o"}}]
        result = self.generator._validate_rule(
            "model_attribute_present", dag, executed_spans, 1000.0
        )
        assert result is True
        
        # Test alternative attribute
        executed_spans_alt = [{"type": "llm_call", "attributes": {"gen_ai.request.model": "gpt-4o"}}]
        result = self.generator._validate_rule(
            "model_attribute_present", dag, executed_spans_alt, 1000.0
        )
        assert result is True
        
        # Test failure case
        executed_spans_no_model = [{"type": "llm_call", "attributes": {}}]
        result = self.generator._validate_rule(
            "model_attribute_present", dag, executed_spans_no_model, 1000.0
        )
        assert result is False
    
    def test_validate_rule_duration_within_range(self):
        """Test duration validation rule."""
        dag = self.generator.create_simple_llm_dag()
        expected_duration = dag.root_span.get_total_duration()
        
        # Test within range (within 10%)
        actual_duration = expected_duration * 1.05  # 5% difference
        result = self.generator._validate_rule(
            "duration_within_range", dag, [], actual_duration
        )
        assert result is True
        
        # Test outside range (more than 10%)
        actual_duration = expected_duration * 1.5  # 50% difference
        result = self.generator._validate_rule(
            "duration_within_range", dag, [], actual_duration
        )
        assert result is False
    
    def test_validate_dag_execution(self):
        """Test complete DAG validation."""
        dag = self.generator.create_simple_llm_dag()
        executed_spans = [
            {
                "span_id": "test-1",
                "name": "llm_request",
                "type": "root",
                "duration_ms": 5000.0,
                "attributes": {
                    "llm.request.model": "gpt-4o",
                    "gen_ai.system": "openai"
                }
            }
        ]
        actual_duration = 5100.0  # Close to expected
        
        validation_results = self.generator._validate_dag_execution(
            dag, executed_spans, actual_duration
        )
        
        assert "passed_rules" in validation_results
        assert "failed_rules" in validation_results
        assert "attribute_completeness" in validation_results
        assert "structure_correctness" in validation_results
        assert "duration_accuracy" in validation_results
        
        # Should have high attribute completeness
        assert validation_results["attribute_completeness"] > 0
        
        # Should have good structure correctness
        assert validation_results["structure_correctness"] > 0
