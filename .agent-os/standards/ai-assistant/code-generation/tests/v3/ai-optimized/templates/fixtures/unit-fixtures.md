# Unit Test Fixtures - Standard Patterns

**🎯 AI Guide for Using Unit Test Fixtures from conftest.py**

🛑 VALIDATE-GATE: Unit Fixtures Entry Requirements
- [ ] Standard fixture usage patterns understood ✅/❌
- [ ] Mock configuration requirements reviewed ✅/❌
- [ ] Unit fixture commitment confirmed ✅/❌

🚨 FRAMEWORK-VIOLATION: If using real fixtures or mixing with integration fixture patterns

## 🛑 **CORE UNIT FIXTURES EXECUTION**

⚠️ MUST-READ: Unit fixtures must provide complete mocking - no real dependencies

### **mock_tracer_base Usage**
```python
def test_with_mock_tracer(self, mock_tracer_base: Mock) -> None:
    """Test using complete mock tracer with all attributes."""
    # Setup required attributes
    mock_tracer_base.project_name = "test-project"
    mock_tracer_base.source_environment = "test"
    mock_tracer_base._initialized = False
    mock_tracer_base.session_id = "test-session-123"
    
    # Configure nested objects
    mock_tracer_base.config.api_key = "test-key"
    mock_tracer_base.config.server_url = "https://api.honeyhive.ai"
    
    # Execute test
    result = function_under_test(mock_tracer_base)
    assert result is not None
```

### **mock_safe_log Usage**
```python
def test_with_logging(self, mock_tracer_base: Mock, mock_safe_log: Mock) -> None:
    """Test logging behavior with standard mock."""
    # Execute function
    result = function_that_logs(mock_tracer_base)
    
    # Verify logging calls
    mock_safe_log.assert_any_call(
        mock_tracer_base, 
        "info", 
        "Expected log message"
    )
    assert mock_safe_log.call_count >= 1
```

### **standard_mock_responses Usage**
```python
def test_api_calls(
    self, 
    mock_client: Mock, 
    standard_mock_responses: Dict
) -> None:
    """Test API integration with standard responses."""
    # Configure mock responses
    mock_client.post.return_value = standard_mock_responses["session"]
    mock_client.get.return_value = standard_mock_responses["event"]
    
    # Execute and verify
    result = api_function(mock_client)
    assert result["session_id"] == "session-test-123"
```

## 🎯 **FIXTURE COMBINATIONS**

### **Complete Unit Test Pattern**
```python
def test_complete_functionality(
    self,
    mock_tracer_base: Mock,
    mock_safe_log: Mock,
    mock_client: Mock,
    standard_mock_responses: Dict
) -> None:
    """Test with all standard unit fixtures."""
    # Setup mocks
    mock_tracer_base.config.api_key = "test-key"
    mock_client.post.return_value = standard_mock_responses["session"]
    
    # Execute
    result = complex_function(mock_tracer_base, mock_client)
    
    # Verify all aspects
    assert result is not None
    mock_safe_log.assert_called()
    mock_client.post.assert_called_once()
```

## 🚨 **CRITICAL REQUIREMENTS**

- ✅ **Always use mock_tracer_base** instead of creating Mock()
- ✅ **Always use mock_safe_log** for logging verification
- ✅ **Always use standard_mock_responses** for API responses
- ❌ **Never create custom mocks** when standard fixtures exist

---

**🎯 These patterns ensure consistent fixture usage across all unit tests.**
