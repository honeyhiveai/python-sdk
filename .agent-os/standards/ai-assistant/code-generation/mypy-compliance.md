# MyPy Compliance for All Code Generation

**🎯 Prevent mypy errors through systematic patterns - MANDATORY for ALL code generation**

## 📁 **MOVED TO LINTER-SPECIFIC DOCUMENTATION**

**This content has been moved to detailed, linter-specific files:**

- **[Type Annotations](linters/mypy/type-annotations.md)** - Complete type annotation requirements
- **[Method Mocking](linters/mypy/method-mocking.md)** - Method mocking patterns (patch.object)
- **[Generic Types](linters/mypy/generic-types.md)** - Proper usage of List, Dict, Optional, etc.
- **[Error Recovery](linters/mypy/error-recovery.md)** - Systematic MyPy error fixing

## 🚨 **Quick Reference: Most Critical Errors**

### **Error 1: Missing type annotations**

**Most common mypy error across all code generation:**

```python
# ❌ WRONG - No type annotations
def process_data(data, config):
    result = transform(data)
    return result
    
# ✅ CORRECT - Complete type annotations
def process_data(data: Dict[str, Any], config: Config) -> ProcessedData:
    result: ProcessedData = transform(data)
    return result
```

### **Error 2: Incompatible return value type**

```python
# ❌ WRONG - Return type doesn't match annotation
def get_items() -> List[Item]:
    items = []  # mypy sees this as List[Any]
    items.append(create_item())  # Could be Any type
    return items

# ✅ CORRECT - Explicit type annotation
def get_items() -> List[Item]:
    items: List[Item] = []  # Explicit type
    item: Item = create_item()  # Ensure correct type
    items.append(item)
    return items
```

### **Error 3: Untyped function parameters**

```python
# ❌ WRONG - Parameters without types
def configure_system(settings, options=None):
    if options is None:
        options = {}
    
# ✅ CORRECT - All parameters typed
def configure_system(
    settings: SystemSettings, 
    *, 
    options: Optional[Dict[str, Any]] = None
) -> None:
    if options is None:
        options = {}
```

## 📋 **Universal MyPy Prevention Checklist**

**MANDATORY: Complete this checklist before generating ANY code:**

### **Type Annotation Planning (ALL CODE)**
- [ ] **All parameters typed**: Every function parameter has type annotation
- [ ] **All variables typed**: Every local variable has type annotation  
- [ ] **All returns typed**: Every function has return type annotation
- [ ] **Optional types handled**: Use `Optional[T]` or `T | None` for nullable types

### **Import Planning for MyPy (ALL CODE)**
- [ ] **Type imports planned**: Only import types that will be used
- [ ] **Generic imports**: Import `List`, `Dict`, `Optional` from `typing`
- [ ] **Class imports**: Import classes used in type annotations
- [ ] **Avoid circular imports**: Plan import order to prevent circular dependencies

## 🚨 **Universal MyPy Patterns**

### **Pattern 1: Function Type Safety**
```python
# Template for properly typed functions
def process_items(
    items: List[Item], 
    *, 
    config: Optional[ProcessConfig] = None
) -> ProcessResult:
    """Process items with configuration."""
    if config is None:
        config = ProcessConfig()
    
    results: List[ProcessedItem] = []
    for item in items:
        processed: ProcessedItem = transform_item(item, config)
        results.append(processed)
    
    return ProcessResult(items=results, count=len(results))
```

### **Pattern 2: Class Type Safety**
```python
class DataProcessor:
    """Process data with type safety."""
    
    def __init__(self, config: ProcessorConfig) -> None:
        """Initialize processor."""
        self.config: ProcessorConfig = config
        self.cache: Dict[str, Any] = {}
    
    def process(self, data: InputData) -> OutputData:
        """Process input data."""
        processed_items: List[ProcessedItem] = []
        for item in data.items:
            result: ProcessedItem = self._process_item(item)
            processed_items.append(result)
        
        return OutputData(items=processed_items)
```

## 🧪 **Test-Specific MyPy Patterns**

### **Test Pattern 1: Method Mocking (CRITICAL)**

**🚨 NEVER assign to methods directly - causes mypy "Cannot assign to a method" errors:**

```python
# ❌ FORBIDDEN - Causes mypy error
exporter.get_session_stats = Mock(return_value=expected_stats)
obj.method = Mock(return_value="value")
instance.function = Mock(side_effect=Exception("error"))

# ✅ REQUIRED - Use patch.object context manager
def test_method_with_mock(self, mock_tracer: Mock) -> None:
    """Test with mocked method."""
    # Arrange
    expected_result: Dict[str, Any] = {"key": "value"}
    
    # ALWAYS use patch.object for method mocking
    with patch.object(mock_tracer, 'get_stats', return_value=expected_result):
        # Act
        result: Dict[str, Any] = function_under_test(mock_tracer)
        
        # Assert
        assert result == expected_result
```

### **Test Pattern 2: Fixture Type Safety**
```python
@pytest.fixture
def mock_spans() -> List[ReadableSpan]:
    """Create typed mock spans."""
    spans: List[ReadableSpan] = []
    for i in range(3):
        span = Mock(spec=ReadableSpan)  # Use spec for type safety
        span.name = f"span_{i}"
        spans.append(span)
    return spans
```

### **Test Pattern 3: Exception Mocking**
```python
def test_exception_handling(self, mock_tracer: Mock) -> None:
    """Test exception handling with proper typing."""
    # Arrange
    test_error = RuntimeError("Test error")
    
    # Use patch.object for exception side effects
    with patch.object(mock_tracer, 'process', side_effect=test_error):
        # Act & Assert
        with pytest.raises(RuntimeError, match="Test error"):
            function_under_test(mock_tracer)
```

## 🧪 **Test-Specific MyPy Checklist**

**Additional checklist items for TEST code generation:**

### **Method Mocking Planning (TESTS ONLY)**
- [ ] **Identified method mocks needed**: List all methods to be mocked
- [ ] **Planned patch.object usage**: Will use context managers, not direct assignment
- [ ] **Planned mock specifications**: Will use `spec=` for type safety
- [ ] **Planned return types**: All mocks have correct return type annotations

### **Test Type Planning (TESTS ONLY)**
- [ ] **All fixtures typed**: Every fixture has correct return type
- [ ] **All mocks typed**: Every Mock object has appropriate type/spec
- [ ] **Test method returns**: All test methods return `-> None`
- [ ] **Mock imports**: `from unittest.mock import Mock, patch` imported

## ⚡ **Immediate MyPy Validation**

**MANDATORY: Run mypy after generating ANY code:**

```bash
# For production code:
python -m mypy src/honeyhive/module/file.py

# For test code:
python -m mypy tests/unit/test_file.py

# MUST show: "Success: no issues found"
# If ANY errors, STOP and fix before continuing
```

## 🚨 **MyPy Error Recovery**

### **When "Cannot assign to a method" occurs:**
1. **Identify the assignment**: Find `obj.method = Mock(...)`
2. **Convert to patch.object**: Use context manager pattern
3. **Indent test code**: Move test logic inside `with` block
4. **Re-run mypy**: Verify error is resolved

### **When type annotation errors occur:**
1. **Add explicit types**: All variables need type annotations
2. **Use Mock specs**: Add `spec=` parameter for type safety
3. **Import required types**: Add missing type imports
4. **Re-run mypy**: Verify all errors resolved

## 📊 **MyPy Compliance Success Metrics**

**Your test generation is mypy-compliant when:**
- **0 mypy errors**: `python -m mypy test_file.py` shows success
- **No method assignments**: All method mocking uses `patch.object`
- **Complete type annotations**: All parameters, variables, and returns typed
- **Proper mock specs**: All Mock objects have appropriate `spec=` parameters

---

**🎯 Remember**: MyPy errors are **100% preventable** by following these patterns systematically.
