# Fixture and Patterns - Advanced Reference

**🎯 Advanced testing patterns and fixture examples for the HoneyHive Python SDK**

## 🚨 **MANDATORY: Use Test Generation Framework First**

**⛔ BEFORE using these patterns, AI assistants MUST follow the comprehensive framework:**

- **📋 Framework Hub**: [Test Generation Framework](../ai-assistant/code-generation/tests/README.md)
- **🚀 Natural Discovery**: Framework → Setup → Choose Path (Unit/Integration) → Analysis → Generation → Quality
- **🎯 Standard Fixtures**: Framework includes proven fixtures from `tests/unit/conftest.py` and `tests/integration/conftest.py`

**🚨 RULE**: This document provides **advanced patterns** that complement the framework's embedded standards

---

## 🔧 **Advanced Parametrized Test Patterns**

### **Configuration Testing Pattern**
```python
@pytest.mark.parametrize("config_key,expected_value", [
    ("api_key", "test-api-key"),
    ("project", "test-project"),
    ("session_id", "test-session"),
    ("batch_size", 100),
])
def test_config_access(
    self, 
    mock_tracer: Mock, 
    config_key: str, 
    expected_value: Any
) -> None:
    """Test configuration value access with various keys."""
    mock_tracer.config.get.return_value = expected_value
    
    result = get_config_value(mock_tracer, config_key)
    assert result == expected_value
```

### **Error Condition Testing Pattern**
```python
@pytest.mark.parametrize("exception_type,error_message", [
    (ValueError, "Invalid configuration"),
    (KeyError, "Missing required key"),
    (TypeError, "Incorrect type provided"),
    (AttributeError, "Missing attribute"),
])
def test_error_handling(
    self,
    mock_tracer: Mock,
    exception_type: type,
    error_message: str
) -> None:
    """Test error handling for various exception types."""
    mock_tracer.process.side_effect = exception_type(error_message)
    
    with pytest.raises(exception_type, match=error_message):
        process_with_tracer(mock_tracer)
```

---

## 🎯 **Advanced Patch Decorator Patterns**

### **Multiple Patch Pattern**
```python
@patch("honeyhive.tracer.processing.context._add_core_context")
@patch("honeyhive.tracer.processing.context._add_evaluation_context")
@patch("honeyhive.tracer.processing.context.safe_log")
def test_with_multiple_patches(
    self,
    mock_log: Mock,           # Last patch (bottom)
    mock_evaluation: Mock,    # Second patch
    mock_core: Mock,          # First patch (top)
    mock_tracer: Mock         # Fixture parameter
) -> None:
    """Test with multiple patch decorators (reverse order)."""
    process_contexts(mock_tracer)
    
    mock_core.assert_called_once()
    mock_evaluation.assert_called_once()
    mock_log.assert_called()
```

### **Keyword-Only Parameter Pattern**
```python
@patch("module.function_a")
@patch("module.function_b")
@patch("module.function_c")
def test_with_keyword_fixture(
    self,
    mock_c: Mock,
    mock_b: Mock,
    mock_a: Mock,
    *,                        # Keyword-only separator
    fixture_param: Mock       # Fixture must be keyword-only
) -> None:
    """Test with many patches and keyword-only fixture."""
    # Reduces positional argument count for pylint
```

---

## 🔄 **Context Manager Testing Patterns**

### **Context Manager Success Pattern**
```python
def test_context_manager_success(self, mock_tracer: Mock) -> None:
    """Test successful context manager usage."""
    with some_context_manager(mock_tracer) as ctx:
        assert ctx is not None
        # Test operations within context
        result = ctx.process()
        assert result is not None
```

### **Context Manager Exception Pattern**
```python
def test_context_manager_exception(self, mock_tracer: Mock) -> None:
    """Test context manager with exception handling."""
    with pytest.raises(ValueError):
        with some_context_manager(mock_tracer):
            raise ValueError("Test exception")
```

### **Async Context Manager Pattern**
```python
async def test_async_context_manager(self, mock_tracer: Mock) -> None:
    """Test async context manager functionality."""
    async with async_context_manager(mock_tracer) as ctx:
        result = await ctx.async_process()
        assert result is not None
```

---

## 🎨 **Custom Assertion Patterns**

### **Complex Assertion Pattern**
```python
def assert_event_structure(event: Dict[str, Any]) -> None:
    """Assert event has required structure.
    
    Args:
        event: Event dictionary to validate
    """
    required_fields = ["event_type", "project", "session_id"]
    for field in required_fields:
        assert field in event, f"Missing required field: {field}"
    
    assert isinstance(event["inputs"], dict)
    assert isinstance(event["outputs"], dict)
    assert event["event_type"] in ["model", "tool", "chain", "session"]

def test_event_creation(self, mock_tracer: Mock) -> None:
    """Test event creation with custom assertion."""
    event = create_event(mock_tracer, "test-data")
    assert_event_structure(event)
```

### **Mock Verification Pattern**
```python
def assert_mock_called_with_pattern(
    mock_obj: Mock, 
    expected_pattern: Dict[str, Any]
) -> None:
    """Assert mock was called with data matching pattern.
    
    Args:
        mock_obj: Mock object to verify
        expected_pattern: Expected call pattern
    """
    mock_obj.assert_called_once()
    call_args = mock_obj.call_args[0][0]
    
    for key, expected_value in expected_pattern.items():
        assert key in call_args
        assert call_args[key] == expected_value
```

---

## 📋 **Pattern Selection Guide**

### **When to Use Each Pattern**

**Parametrized Tests**: Testing multiple scenarios
- Use for: Configuration variations, error conditions
- Example: Testing different config keys

**Multiple Patch Decorators**: Mocking complex dependencies
- Use for: Isolating units with many external calls
- Example: Mocking logging, context processing, API calls

**Context Manager Testing**: Testing resource management
- Use for: Testing proper setup/teardown, exception handling
- Example: Session management, span lifecycle

**Custom Assertions**: Complex validation logic
- Use for: Repeated validation patterns, structured data validation
- Example: Event structure validation, API response validation

---

## 💡 **Best Practices**

### **Pattern Usage**
- **Follow framework first** - use embedded standards before advanced patterns
- **Keep patterns focused** - one responsibility per pattern
- **Document patterns** - clear docstrings explaining purpose
- **Compose patterns** - build complex tests from simple patterns

### **Integration with Framework**
- **Standard fixtures first** - use proven fixtures from framework
- **Advanced patterns second** - use these patterns for complex scenarios
- **Quality enforcement** - all patterns must meet framework quality targets
- **Consistent naming** - follow framework naming conventions

---

**💡 Key Principle**: These advanced patterns complement the framework's embedded standards for complex testing scenarios that require specialized approaches.