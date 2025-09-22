# Unit Testing Standards - Advanced Reference

**🎯 Advanced unit testing requirements and examples for the HoneyHive Python SDK**

## 🚨 **MANDATORY: Use Test Generation Framework First**

**⛔ BEFORE using these standards, AI assistants MUST follow the comprehensive framework:**

- **📋 Framework Hub**: [Test Generation Framework](../ai-assistant/code-generation/tests/README.md)
- **🚀 Unit Test Path**: Framework → Setup → Unit Test Analysis → Unit Test Generation → Unit Test Quality
- **🎯 Embedded Standards**: Framework includes type annotations, mock patterns, and quality requirements

**🚨 RULE**: This document provides **detailed examples** that complement the framework's embedded unit test standards

---

## 🚨 **Advanced Type Annotation Examples**

### **Complex Method Signatures**
```python
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock

class TestTracerProcessing:
    """Test tracer processing functionality."""
    
    def test_process_span_with_complex_types(
        self, 
        mock_tracer: Mock, 
        mock_span: Mock
    ) -> None:
        """Test span processing with complex type annotations."""
        # Complex variable annotations
        baggage_items: Dict[str, str] = {"session_id": "test-session"}
        mock_data: List[Dict[str, Any]] = [{"key": "value"}]
        result: Optional[Union[Dict[str, Any], str]] = None
        
        # Process with proper typing
        result = process_span(mock_span, baggage_items)
        assert isinstance(result, dict)
```

### **Generic Type Annotations**
```python
from typing import TypeVar, Generic, Callable

T = TypeVar('T')

def test_generic_processing(
    self,
    mock_tracer: Mock
) -> None:
    """Test generic type processing."""
    processor: Callable[[T], T] = lambda x: x
    data: Dict[str, Union[str, int, float]] = {"key": "value", "count": 42}
    
    result = processor(data)
    assert result == data
```

---

## 🏗️ **Advanced Test Structure Examples**

### **Complex Class Organization**
```python
class TestTracerLifecycle:
    """Test complete tracer lifecycle management.
    
    This class tests all aspects of tracer lifecycle including:
    - Initialization and configuration
    - Session management and cleanup
    - Error handling and recovery
    - Resource management and disposal
    """
    
    def setup_method(self) -> None:
        """Set up test environment for each test method."""
        self.test_data: Dict[str, Any] = {
            "api_key": "test-key",
            "project": "test-project"
        }
    
    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Cleanup logic here
        pass
    
    def test_initialization_success(self, mock_tracer: Mock) -> None:
        """Test successful tracer initialization."""
        # Test implementation
        pass
        
    def test_initialization_failure_invalid_key(self, mock_tracer: Mock) -> None:
        """Test initialization failure with invalid API key."""
        # Test implementation
        pass
```

### **Advanced Method Naming Conventions**
```python
class TestConfigurationHandling:
    """Test configuration handling scenarios."""
    
    # Success scenarios
    def test_get_config_value_success_with_default(self) -> None:
        """Test successful config retrieval with default value."""
        
    def test_get_config_value_success_nested_path(self) -> None:
        """Test successful config retrieval from nested path."""
    
    # Error scenarios  
    def test_get_config_value_error_missing_key_no_default(self) -> None:
        """Test config retrieval error when key missing and no default."""
        
    def test_get_config_value_error_invalid_type_conversion(self) -> None:
        """Test config retrieval error during type conversion."""
    
    # Edge cases
    def test_get_config_value_edge_case_empty_string_key(self) -> None:
        """Test config retrieval edge case with empty string key."""
        
    def test_get_config_value_edge_case_none_value_with_default(self) -> None:
        """Test config retrieval edge case when value is None but default exists."""
```

---

## 🎭 **Advanced Mock Usage Examples**

### **Complex Fixture Composition**
```python
@pytest.fixture
def configured_mock_tracer() -> Mock:
    """Create a fully configured mock tracer instance."""
    tracer = Mock()
    
    # Configure nested attributes
    tracer.config.api_key = "test-api-key"
    tracer.config.project = "test-project"
    tracer.config.session_id = "test-session"
    
    # Configure method return values
    tracer.get_config.return_value = {"batch_size": 100}
    tracer.is_initialized.return_value = True
    
    # Configure side effects for complex scenarios
    tracer.process_span.side_effect = lambda span: {"processed": True, "span_id": span.id}
    
    return tracer

@pytest.fixture
def mock_span_with_attributes() -> Mock:
    """Create a mock span with realistic attributes."""
    span = Mock()
    span.name = "test-operation"
    span.attributes = {
        "service.name": "test-service",
        "operation.type": "test",
        "user.id": "test-user"
    }
    span.status.status_code = "OK"
    span.start_time = 1234567890
    span.end_time = 1234567900
    return span
```

### **Advanced Patch Decorator Usage**
```python
class TestComplexPatching:
    """Test complex patching scenarios."""
    
    @patch("honeyhive.tracer.processing.context.safe_log")
    @patch("honeyhive.tracer.processing.context.get_baggage")
    def test_with_ordered_patches(
        self,
        mock_get_baggage: Mock,
        mock_safe_log: Mock,
        configured_mock_tracer: Mock
    ) -> None:
        """Test with multiple patches in correct order."""
        # Configure mocks
        mock_get_baggage.return_value = {"session_id": "test"}
        
        # Execute test
        result = process_with_context(configured_mock_tracer)
        
        # Verify interactions
        mock_get_baggage.assert_called_once()
        mock_safe_log.assert_called_with("info", "Processing context")
        assert result is not None
```

---

## 🔍 **Advanced Assertion Examples**

### **Complex Data Structure Assertions**
```python
def test_complex_event_structure(self, mock_tracer: Mock) -> None:
    """Test complex event structure validation."""
    event = create_complex_event(mock_tracer)
    
    # Nested structure assertions
    assert "metadata" in event
    assert "inputs" in event
    assert "outputs" in event
    
    # Type-specific assertions
    assert isinstance(event["metadata"], dict)
    assert isinstance(event["inputs"], dict)
    assert isinstance(event["outputs"], dict)
    
    # Content validation
    assert event["metadata"]["model"] in ["gpt-4", "gpt-3.5-turbo"]
    assert "prompt" in event["inputs"]
    assert "response" in event["outputs"]
    
    # Numeric validations
    assert isinstance(event["metadata"]["temperature"], (int, float))
    assert 0.0 <= event["metadata"]["temperature"] <= 2.0
```

### **Mock Interaction Verification**
```python
def test_mock_interaction_patterns(self, mock_tracer: Mock) -> None:
    """Test complex mock interaction verification."""
    # Setup
    mock_tracer.process_batch.return_value = {"processed": 5, "failed": 0}
    
    # Execute
    result = batch_process_spans(mock_tracer, ["span1", "span2", "span3"])
    
    # Verify call patterns
    assert mock_tracer.process_batch.call_count == 1
    
    # Verify call arguments
    call_args = mock_tracer.process_batch.call_args
    assert len(call_args[0][0]) == 3  # First positional arg should have 3 spans
    
    # Verify keyword arguments
    if call_args[1]:  # If keyword args exist
        assert "batch_size" in call_args[1]
        assert call_args[1]["batch_size"] > 0
```

---

## 🚨 **Advanced Error Handling Examples**

### **Exception Testing with Context**
```python
def test_exception_with_context_preservation(self, mock_tracer: Mock) -> None:
    """Test exception handling preserves context information."""
    # Setup error condition
    mock_tracer.send_batch.side_effect = ConnectionError("Network unavailable")
    
    # Test exception with context
    with pytest.raises(ConnectionError) as exc_info:
        send_spans_with_retry(mock_tracer, ["span1", "span2"])
    
    # Verify exception details
    assert "Network unavailable" in str(exc_info.value)
    
    # Verify context preservation (e.g., spans should be queued for retry)
    assert mock_tracer.queue_for_retry.called
    retry_args = mock_tracer.queue_for_retry.call_args[0][0]
    assert len(retry_args) == 2  # Both spans should be queued
```

### **Graceful Degradation Testing**
```python
def test_graceful_degradation_scenarios(self, mock_tracer: Mock) -> None:
    """Test graceful degradation under various failure conditions."""
    # Test partial failure
    mock_tracer.config.get.side_effect = lambda key, default=None: {
        "api_key": "test-key",
        "project": "test-project"
    }.get(key, default)
    
    # Should not raise, should use defaults
    result = initialize_with_fallbacks(mock_tracer)
    
    assert result is not None
    assert result["status"] == "initialized_with_defaults"
    assert "warnings" in result
```

---

## 📊 **Advanced Coverage Strategies**

### **Branch Coverage Examples**
```python
def test_all_conditional_branches(self, mock_tracer: Mock) -> None:
    """Test all branches of conditional logic."""
    # Test if branch
    mock_tracer.is_enabled.return_value = True
    result_enabled = process_if_enabled(mock_tracer, "test-data")
    assert result_enabled["processed"] is True
    
    # Test else branch
    mock_tracer.is_enabled.return_value = False
    result_disabled = process_if_enabled(mock_tracer, "test-data")
    assert result_disabled["processed"] is False
    assert result_disabled["reason"] == "tracer_disabled"
```

### **Edge Case Coverage**
```python
def test_edge_cases_comprehensive(self, mock_tracer: Mock) -> None:
    """Test comprehensive edge case coverage."""
    edge_cases = [
        None,                    # None input
        "",                     # Empty string
        [],                     # Empty list
        {},                     # Empty dict
        {"key": None},          # Dict with None value
        {"key": ""},            # Dict with empty string
        {"nested": {"deep": {}}}, # Nested empty structures
    ]
    
    for case in edge_cases:
        result = process_flexible_input(mock_tracer, case)
        assert result is not None, f"Failed for case: {case}"
        assert "status" in result, f"Missing status for case: {case}"
```

---

## 💡 **Best Practices Summary**

### **Type Safety**
- **Complete annotations** - every function, method, and variable
- **Generic types** - use TypeVar and Generic for reusable code
- **Union types** - handle multiple possible types explicitly
- **Optional types** - be explicit about nullable values

### **Test Organization**
- **Descriptive class names** - clearly indicate what's being tested
- **Logical grouping** - group related tests in the same class
- **Setup/teardown** - use proper fixture management
- **Clear naming** - test names should describe the scenario

### **Mock Strategy**
- **Realistic configuration** - mocks should behave like real objects
- **Proper isolation** - each test should have independent mocks
- **Verification patterns** - assert on both return values and interactions
- **Error simulation** - test error conditions with side_effect

---

**💡 Key Principle**: These advanced examples demonstrate comprehensive unit testing techniques that complement the framework's embedded standards for complex testing scenarios.