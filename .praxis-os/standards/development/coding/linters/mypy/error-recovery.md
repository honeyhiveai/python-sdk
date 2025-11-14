# MyPy Error Recovery

**🎯 Systematic approach to fixing MyPy errors in AI-generated code**

## 🚨 **Most Common MyPy Errors and Fixes**

### **Error 1: "Cannot assign to a method [method-assign]"**

**Most frequent MyPy error in test generation:**

```python
# ❌ ERROR - Direct method assignment
def test_method(self, mock_obj: Mock) -> None:
    mock_obj.process = Mock(return_value="result")  # MyPy error!
    result = function_under_test(mock_obj)

# ✅ FIX - Use patch.object context manager
def test_method(self, mock_obj: Mock) -> None:
    with patch.object(mock_obj, 'process', return_value="result"):
        result = function_under_test(mock_obj)
```

**Recovery Steps:**
1. **Identify the assignment**: Find `obj.method = Mock(...)`
2. **Convert to patch.object**: Use `with patch.object(obj, 'method', ...):`
3. **Indent test code**: Move test logic inside `with` block
4. **Re-run MyPy**: Verify error is resolved

### **Error 2: "Missing return statement [return]"**

```python
# ❌ ERROR - Function claims to return value but doesn't
def get_config(name: str) -> Config:
    if name == "default":
        return Config()
    # Missing return for other cases - MyPy error!

# ✅ FIX - Handle all code paths
def get_config(name: str) -> Config:
    if name == "default":
        return Config()
    raise ValueError(f"Unknown config: {name}")

# ✅ ALTERNATIVE - Use Optional if None is valid
def get_config(name: str) -> Optional[Config]:
    if name == "default":
        return Config()
    return None
```

### **Error 3: "Incompatible return value type"**

```python
# ❌ ERROR - Return type doesn't match annotation
def get_items() -> List[DataItem]:
    items = []  # MyPy sees List[Any]
    items.append(create_item())  # Could be Any
    return items  # List[Any] incompatible with List[DataItem]

# ✅ FIX - Explicit type annotation
def get_items() -> List[DataItem]:
    items: List[DataItem] = []  # Explicit type
    item: DataItem = create_item()  # Ensure correct type
    items.append(item)
    return items
```

### **Error 4: "Argument has incompatible type"**

```python
# ❌ ERROR - Wrong argument type
def process_config(config: ProcessorConfig) -> None:
    pass

def test_function() -> None:
    config = {"batch_size": 100}  # Dict, not ProcessorConfig
    process_config(config)  # MyPy error!

# ✅ FIX - Use correct type
def test_function() -> None:
    config: ProcessorConfig = ProcessorConfig(batch_size=100)
    process_config(config)
```

### **Error 5: "Function is missing a type annotation"**

```python
# ❌ ERROR - Missing type annotations
def process_data(data, config=None):
    return transform(data)

# ✅ FIX - Add complete type annotations
def process_data(
    data: Dict[str, Any], 
    config: Optional[ProcessConfig] = None
) -> ProcessedData:
    return transform(data)
```

## 🔧 **Systematic Error Recovery Process**

### **Step 1: Read the Error Message**

```bash
# MyPy error format:
filename.py:line: error: Error description [error-code]

# Example:
test_file.py:45: error: Cannot assign to a method [method-assign]
test_file.py:67: error: Missing return statement [return]
```

### **Step 2: Identify Error Category**

**Method Assignment Errors:**
- `Cannot assign to a method [method-assign]`
- `Cannot assign to a function [assignment]`

**Type Annotation Errors:**
- `Function is missing a type annotation [no-untyped-def]`
- `Missing return statement [return]`

**Type Compatibility Errors:**
- `Incompatible return value type [return-value]`
- `Argument has incompatible type [arg-type]`

**Import/Module Errors:**
- `Cannot find implementation or library stub [import]`
- `Module has no attribute [attr-defined]`

### **Step 3: Apply Specific Fix**

#### **Fix Method Assignment Errors**

```python
# Pattern: obj.method = Mock(...)
# Solution: with patch.object(obj, 'method', ...):

# Before fix:
exporter.get_stats = Mock(return_value={"count": 5})

# After fix:
with patch.object(exporter, 'get_stats', return_value={"count": 5}):
    # Test code here
```

#### **Fix Type Annotation Errors**

```python
# Pattern: Missing parameter/return types
# Solution: Add complete type annotations

# Before fix:
def process(data, config=None):
    return result

# After fix:
def process(data: DataType, config: Optional[Config] = None) -> ResultType:
    return result
```

#### **Fix Type Compatibility Errors**

```python
# Pattern: Type mismatch
# Solution: Use correct types or explicit casting

# Before fix:
items = []  # List[Any]
return items  # Error if expecting List[SpecificType]

# After fix:
items: List[SpecificType] = []
return items
```

## 📋 **Error Recovery Patterns**

### **Pattern 1: Mock Method Recovery**

```python
# Original error-prone code:
def test_export_spans(self, mock_exporter: Mock) -> None:
    mock_exporter.export = Mock(return_value=SpanExportResult.SUCCESS)
    mock_exporter.get_session_stats = Mock(return_value={"requests": 5})
    
    result = function_under_test(mock_exporter)

# Fixed code:
def test_export_spans(self, mock_exporter: Mock) -> None:
    with patch.object(mock_exporter, 'export', return_value=SpanExportResult.SUCCESS):
        with patch.object(mock_exporter, 'get_session_stats', return_value={"requests": 5}):
            result = function_under_test(mock_exporter)
```

### **Pattern 2: Type Annotation Recovery**

```python
# Original error-prone code:
def test_process_items(self, mock_processor):
    items = [create_item(), create_item()]
    result = mock_processor.process(items)
    assert len(result) == 2

# Fixed code:
def test_process_items(self, mock_processor: Mock) -> None:
    items: List[DataItem] = [create_item(), create_item()]
    result: List[ProcessedItem] = mock_processor.process(items)
    assert len(result) == 2
```

### **Pattern 3: Return Type Recovery**

```python
# Original error-prone code:
def get_test_data():
    return [{"id": 1}, {"id": 2}]

# Fixed code:
def get_test_data() -> List[Dict[str, int]]:
    return [{"id": 1}, {"id": 2}]
```

## 🚨 **Emergency Recovery Commands**

### **Quick MyPy Check**
```bash
# Check specific file
python -m mypy tests/unit/test_file.py

# Check with verbose output
python -m mypy --show-error-codes tests/unit/test_file.py
```

### **Common Quick Fixes**

```python
# 1. Add missing imports
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

# 2. Add return type annotations
def function() -> None:  # For functions that don't return
def function() -> ReturnType:  # For functions that return

# 3. Add variable type annotations
variable: VariableType = value

# 4. Fix method mocking
with patch.object(obj, 'method', return_value=value):
    # test code
```

## 📋 **Error Recovery Checklist**

**When MyPy errors occur:**

- [ ] **Read error message carefully**: Understand what MyPy is complaining about
- [ ] **Identify error category**: Method assignment, type annotation, compatibility
- [ ] **Apply appropriate pattern**: Use the recovery pattern for that error type
- [ ] **Add missing imports**: Import required types from `typing`
- [ ] **Re-run MyPy**: Verify the error is fixed
- [ ] **Check for new errors**: Fixing one error might reveal others
- [ ] **Test the fix**: Ensure code still works correctly

## ⚡ **Recovery Priority Order**

**Fix errors in this order for efficiency:**

1. **Import errors**: Fix missing imports first
2. **Method assignment errors**: Fix `patch.object` usage
3. **Type annotation errors**: Add missing type annotations
4. **Compatibility errors**: Fix type mismatches
5. **Logic errors**: Fix missing return statements

## 🎯 **Prevention vs Recovery**

**Prevention (Better):**
- Follow type annotation checklist before generating code
- Use proper mocking patterns from the start
- Import all required types upfront

**Recovery (When needed):**
- Use systematic error recovery process
- Fix errors in priority order
- Verify fixes don't introduce new errors

---

**🎯 Remember**: Prevention is better than recovery. Follow the type annotation standards to avoid MyPy errors in the first place.
