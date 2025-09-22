# Assertion Patterns - Standard Test Validation

**🎯 AI Guide for Standard Assertion Patterns in Unit and Integration Tests**

⚠️ MUST-READ: Complete assertion patterns before test generation
🛑 VALIDATE-GATE: Assertion Pattern Understanding
- [ ] Behavior verification patterns comprehended ✅/❌
- [ ] Mock verification patterns understood ✅/❌
- [ ] Error handling assertions reviewed ✅/❌
- [ ] Integration test assertions accepted ✅/❌
- [ ] Anti-patterns identified and avoided ✅/❌

🚨 FRAMEWORK-VIOLATION: If using assertion anti-patterns

## 📋 **BEHAVIOR VERIFICATION PATTERNS**

### **Return Value Assertions**
```python
# Test function return values (interfaces)
assert result == expected_value
assert result is not None
assert result is None  # For graceful failure cases
assert isinstance(result, ExpectedType)
assert len(result) == expected_count

# Test boolean conditions
assert condition is True
assert condition is False
assert tracer._initialized is True
assert tracer.is_main_provider is False
```

### **State Change Assertions**
```python
# Test object state changes (behavior)
assert mock_tracer.session_id == "expected-session-id"
assert mock_tracer._initialized is True
assert mock_tracer.provider is not None
assert mock_tracer.config.api_key == "test-key"

# Test attribute assignments
assert hasattr(mock_tracer, 'otlp_exporter')
assert mock_tracer.span_processor is not None
```

### **Collection Assertions**
```python
# Test lists and dictionaries
assert "expected_key" in result_dict
assert result_list[0] == expected_first_item
assert len(result_list) > 0
assert all(item.is_valid for item in result_list)

# Test configuration dictionaries
assert result["session_id"] is not None
assert "libraries" in result
assert result["enabled"] is True
```

## 🔧 **MOCK VERIFICATION PATTERNS**

### **Function Call Verification**
```python
# Verify mock function calls (behavior)
mock_function.assert_called_once()
mock_function.assert_called_once_with(expected_args)
mock_function.assert_called_with(arg1, arg2, keyword=value)
mock_function.assert_not_called()

# Verify call counts
assert mock_function.call_count == 2
mock_function.assert_has_calls([
    call(first_args),
    call(second_args)
])
```

### **Logging Verification**
```python
# Verify safe_log calls (standard pattern)
mock_safe_log.assert_any_call(
    mock_tracer, 
    "info", 
    "Expected log message"
)

# Verify multiple log calls
mock_safe_log.assert_has_calls([
    call(mock_tracer, "debug", "First message"),
    call(mock_tracer, "info", "Second message")
])

# Verify log call count
assert mock_safe_log.call_count == 3
mock_safe_log.assert_called()  # At least one call
```

### **Mock Configuration Verification**
```python
# Verify mock return values were used
mock_client.get.return_value = {"status": "success"}
result = function_under_test(mock_client)
mock_client.get.assert_called_once()
assert result["status"] == "success"

# Verify side effects triggered
mock_function.side_effect = Exception("Test error")
with pytest.raises(Exception, match="Test error"):
    function_under_test(mock_function)
```

## 🎯 **ERROR HANDLING ASSERTIONS**

### **Exception Testing**
```python
# Test expected exceptions
with pytest.raises(ValueError, match="Invalid configuration"):
    function_with_validation(invalid_input)

with pytest.raises(KeyError, match="Missing required key"):
    function_requiring_key({})

# Test exception types without message matching
with pytest.raises(TypeError):
    function_with_type_validation(wrong_type)
```

### **Graceful Degradation Testing**
```python
# Test graceful failure handling
mock_external.side_effect = Exception("External service failed")
result = function_with_fallback(mock_external)

# Verify graceful fallback
assert result is None  # or appropriate fallback value
mock_safe_log.assert_any_call(
    mock_tracer, 
    "error", 
    "External service failed, using fallback"
)
```

### **Error Recovery Testing**
```python
# Test retry and recovery mechanisms
mock_api.side_effect = [
    Exception("First attempt failed"),
    {"success": True}  # Second attempt succeeds
]

result = function_with_retry(mock_api)
assert result["success"] is True
assert mock_api.call_count == 2
```

## 🔗 **INTEGRATION TEST ASSERTIONS**

### **Backend Verification**
```python
# Verify data appears in HoneyHive backend
verify_backend_event(
    tracer=honeyhive_tracer,
    expected_event_type="model",
    expected_data={
        "inputs": {"prompt": "test input"},
        "outputs": {"response": "test output"},
        "project": honeyhive_tracer.project_name
    },
    timeout=30
)

# Verify session creation in backend
verify_backend_event(
    tracer=honeyhive_tracer,
    expected_event_type="session",
    expected_data={
        "session_id": honeyhive_tracer.session_id,
        "project": "integration-test-project"
    }
)
```

### **Real API Assertions**
```python
# Test real tracer state
assert honeyhive_tracer._initialized is True
assert honeyhive_tracer.session_id is not None
assert honeyhive_tracer.provider is not None
assert honeyhive_tracer.config.api_key is not None

# Test real configuration
assert honeyhive_tracer.test_mode is True
assert honeyhive_tracer.config.server_url == "https://api.honeyhive.ai"
```

## 🚨 **ASSERTION ANTI-PATTERNS**

### **Avoid These Patterns**
```python
# ❌ Don't test implementation details
# mock_function.assert_called_with(internal_variable)

# ❌ Don't assert on mock internals
# assert mock_object._mock_calls == expected_calls

# ❌ Don't use overly specific assertions
# assert result == {"exact": "dictionary", "with": "all", "keys": "specified"}

# ❌ Don't ignore error conditions
# result = function_that_might_fail()
# assert result  # Should check for None/error cases
```

### **Use These Instead**
```python
# ✅ Test behavior and interfaces
assert result.is_successful is True
assert result.error_message is None

# ✅ Use flexible assertions for complex data
assert "expected_key" in result
assert result["status"] in ["success", "completed"]

# ✅ Test error handling explicitly
if result is None:
    mock_safe_log.assert_any_call(mock_tracer, "error", "Operation failed")
else:
    assert result.is_valid is True
```

## 🛑 **MANDATORY ASSERTION SELECTION**

🛑 VALIDATE-GATE: Assertion Pattern Selection
- [ ] Test path confirmed (unit OR integration) ✅/❌
- [ ] Appropriate assertion patterns selected for path ✅/❌
- [ ] Anti-patterns avoided ✅/❌
- [ ] Path-specific verification methods used ✅/❌

### **Unit Tests (Mock Everything)**
🛑 EXECUTE-NOW: Use these assertion patterns for unit tests ONLY
📊 COUNT-AND-DOCUMENT: Mock verification assertions: [NUMBER]
- ✅ **Mock call verification**: `mock_function.assert_called_once()`
- ✅ **Logging verification**: `mock_safe_log.assert_any_call()`
- ✅ **State change verification**: `assert mock_tracer.attribute == value`
- ✅ **Return value verification**: `assert result == expected`
🚨 FRAMEWORK-VIOLATION: If using real API assertions in unit tests

### **Integration Tests (Real APIs)**
🛑 EXECUTE-NOW: Use these assertion patterns for integration tests ONLY
📊 COUNT-AND-DOCUMENT: Backend verification assertions: [NUMBER]
- ✅ **Backend verification**: `verify_backend_event()`
- ✅ **Real state verification**: `assert tracer._initialized is True`
- ✅ **API response verification**: `assert response.status_code == 200`
- ✅ **End-to-end verification**: Complete flow validation
🚨 FRAMEWORK-VIOLATION: If using mock assertions in integration tests

🛑 UPDATE-TABLE: Assertion patterns applied with path compliance
🎯 NEXT-MANDATORY: Apply assertion patterns in test generation

---

**🎯 This guide ensures generated tests use appropriate assertion patterns with mandatory path compliance validation.**
