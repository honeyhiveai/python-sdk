# MyPy Method Mocking Patterns

**🎯 Prevent "Cannot assign to a method" errors in test generation**

## 🚨 **CRITICAL: The #1 MyPy Error in Tests**

**"Cannot assign to a method [method-assign]" - Most common MyPy error in AI-generated tests**

### **The Problem**

```python
# ❌ FORBIDDEN - Causes MyPy error
exporter.get_session_stats = Mock(return_value={"requests": 5})
tracer.process_spans = Mock(side_effect=Exception("error"))
client.send_request = Mock(return_value=response_data)

# MyPy Error: Cannot assign to a method [method-assign]
```

### **The Solution**

```python
# ✅ REQUIRED - Use patch.object context manager
with patch.object(exporter, 'get_session_stats', return_value={"requests": 5}):
    # Test code here
    result = exporter.log_session_stats()

with patch.object(tracer, 'process_spans', side_effect=Exception("error")):
    # Test code here
    
with patch.object(client, 'send_request', return_value=response_data):
    # Test code here
```

## 🔧 **Method Mocking Patterns**

### **Pattern 1: Simple Return Value**

```python
def test_method_with_return_value(self, mock_exporter: Mock) -> None:
    """Test method that returns a value."""
    # Arrange
    expected_stats: Dict[str, int] = {"requests": 10, "errors": 0}
    
    # ✅ CORRECT - Use patch.object
    with patch.object(mock_exporter, 'get_session_stats', return_value=expected_stats):
        # Act
        result: Dict[str, int] = function_under_test(mock_exporter)
        
        # Assert
        assert result == expected_stats
```

### **Pattern 2: Exception Side Effect**

```python
def test_method_with_exception(self, mock_tracer: Mock) -> None:
    """Test method that raises an exception."""
    # Arrange
    test_error = RuntimeError("Connection failed")
    
    # ✅ CORRECT - Use patch.object with side_effect
    with patch.object(mock_tracer, 'export_spans', side_effect=test_error):
        # Act & Assert
        with pytest.raises(RuntimeError, match="Connection failed"):
            function_under_test(mock_tracer)
```

### **Pattern 3: Multiple Method Mocks**

```python
def test_multiple_method_mocks(self, mock_client: Mock) -> None:
    """Test with multiple method mocks."""
    # Arrange
    auth_response: Dict[str, str] = {"token": "abc123"}
    data_response: List[Dict[str, Any]] = [{"id": 1, "name": "test"}]
    
    # ✅ CORRECT - Nested patch.object contexts
    with patch.object(mock_client, 'authenticate', return_value=auth_response):
        with patch.object(mock_client, 'fetch_data', return_value=data_response):
            # Act
            result: ProcessResult = function_under_test(mock_client)
            
            # Assert
            assert result.success is True
            assert len(result.data) == 1
```

### **Pattern 4: Method Mock with Call Verification**

```python
def test_method_call_verification(self, mock_processor: Mock) -> None:
    """Test that verifies method was called correctly."""
    # Arrange
    test_data: List[str] = ["item1", "item2", "item3"]
    
    # ✅ CORRECT - Mock method and verify calls
    with patch.object(mock_processor, 'process_item', return_value="processed") as mock_process:
        # Act
        result: List[str] = function_under_test(mock_processor, test_data)
        
        # Assert
        assert mock_process.call_count == 3
        mock_process.assert_any_call("item1")
        mock_process.assert_any_call("item2")
        mock_process.assert_any_call("item3")
```

## 🚨 **Common Mistakes and Fixes**

### **Mistake 1: Direct Method Assignment**

```python
# ❌ WRONG - Direct assignment
def test_wrong_approach(self, mock_obj: Mock) -> None:
    mock_obj.method = Mock(return_value="value")  # MyPy error!
    result = function_under_test(mock_obj)

# ✅ CORRECT - Use patch.object
def test_correct_approach(self, mock_obj: Mock) -> None:
    with patch.object(mock_obj, 'method', return_value="value"):
        result = function_under_test(mock_obj)
```

### **Mistake 2: Missing Type Annotations**

```python
# ❌ WRONG - No type annotations
def test_no_types(self, mock_obj):
    with patch.object(mock_obj, 'method', return_value="value"):
        result = function_under_test(mock_obj)

# ✅ CORRECT - Complete type annotations
def test_with_types(self, mock_obj: Mock) -> None:
    with patch.object(mock_obj, 'method', return_value="value"):
        result: str = function_under_test(mock_obj)
```

### **Mistake 3: Incorrect Mock Spec**

```python
# ❌ WRONG - Mock without spec
@pytest.fixture
def mock_spans():
    return [Mock(), Mock(), Mock()]  # No type info

# ✅ CORRECT - Mock with proper spec
@pytest.fixture
def mock_spans() -> List[ReadableSpan]:
    spans: List[ReadableSpan] = []
    for i in range(3):
        span = Mock(spec=ReadableSpan)
        span.name = f"span_{i}"
        spans.append(span)
    return spans
```

## 📋 **Method Mocking Checklist**

**Before mocking ANY method, verify:**

- [ ] **Using patch.object**: Never assign directly to methods
- [ ] **Context manager**: Use `with patch.object(...):`
- [ ] **Type annotations**: All variables and parameters typed
- [ ] **Mock specs**: Use `spec=` for type safety when creating Mocks
- [ ] **Return types**: Mock return values match expected types
- [ ] **Exception handling**: Use `side_effect` for exceptions
- [ ] **Call verification**: Assert calls when needed
- [ ] **Proper indentation**: Test code inside `with` block

## ⚡ **Quick Reference**

### **Basic Pattern**
```python
with patch.object(obj, 'method_name', return_value=expected):
    result = function_under_test(obj)
```

### **Exception Pattern**
```python
with patch.object(obj, 'method_name', side_effect=Exception("error")):
    with pytest.raises(Exception):
        function_under_test(obj)
```

### **Multiple Mocks Pattern**
```python
with patch.object(obj, 'method1', return_value=val1):
    with patch.object(obj, 'method2', return_value=val2):
        result = function_under_test(obj)
```

---

**🎯 Remember**: NEVER assign to methods directly. Always use `patch.object` context managers.
