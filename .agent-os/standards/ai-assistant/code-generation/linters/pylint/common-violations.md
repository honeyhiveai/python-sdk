# Pylint Common Violations Prevention

**🎯 PREVENT the most frequent Pylint errors DURING code generation**

## 🚨 **CRITICAL: These errors are 100% preventable**

**AI assistants make these errors because they don't plan before writing code. Follow the prevention patterns below.**

## 🚨 **Top 10 Pylint Violations by AI Assistants**

### **1. R0917: Too many positional arguments (>5)**

**Most common Pylint error in AI-generated code:**

```python
# ❌ VIOLATION - 6 positional arguments
def process_data(data, config, options, timeout, retries, verbose):
    pass

# ✅ CORRECT - Use keyword-only arguments after 5th
def process_data(data, config, options, timeout, *, retries=3, verbose=False):
    pass

# ✅ BETTER - Use keyword-only after 3rd for readability
def process_data(data, config, *, options=None, timeout=30, retries=3, verbose=False):
    pass
```

### **2. W0611: Unused import**

**PREVENTION: Plan exact imports before writing ANY code**

```python
# ❌ VIOLATION - Import not used (AI assistant didn't plan)
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock  # MagicMock unused

def test_function() -> None:
    data: Dict[str, str] = {}  # List, Optional, Any, MagicMock unused

# ✅ PREVENTION - Plan imports first, then write code
# STEP 1: Plan what I need: Dict for data variable, that's it
# STEP 2: Import only what I planned
from typing import Dict

def test_function() -> None:
    data: Dict[str, str] = {}
```

**🚨 MANDATORY: Write import plan before coding:**
```python
# Import planning worksheet:
# - Will I use Dict? YES (for data variable)
# - Will I use List? NO (remove it)
# - Will I use Optional? NO (remove it)
# - Will I use Any? NO (remove it)
# - Will I use MagicMock? NO (remove it)
```

### **3. C0301: Line too long (>88 characters)**

**PREVENTION: Plan line breaks BEFORE writing long lines**

```python
# ❌ VIOLATION - Line too long (AI assistant didn't plan)
def very_long_function_name_that_exceeds_line_limit(parameter_one, parameter_two, parameter_three):
    pass

# ✅ PREVENTION - Count characters first, then format
# STEP 1: Count characters in signature: ~95 characters
# STEP 2: Since >88, plan multi-line format BEFORE writing
def very_long_function_name_that_exceeds_line_limit(
    parameter_one: str,
    parameter_two: int,
    parameter_three: bool
) -> None:
    pass
```

**🚨 MANDATORY: Character counting before writing:**
```python
# Line length planning:
# "def very_long_function_name_that_exceeds_line_limit(parameter_one, parameter_two, parameter_three):"
# Character count: 95 characters
# Limit: 88 characters
# Action: Use multi-line format
```

### **4. C0116: Missing function or method docstring**

```python
# ❌ VIOLATION - No docstring
def process_items(items):
    return [item.upper() for item in items]

# ✅ CORRECT - Proper docstring
def process_items(items: List[str]) -> List[str]:
    """Process items by converting to uppercase.
    
    Args:
        items: List of strings to process
        
    Returns:
        List of uppercase strings
    """
    return [item.upper() for item in items]
```

### **5. C0103: Invalid name (doesn't conform to naming convention)**

```python
# ❌ VIOLATION - Invalid variable names
def test_function():
    TestData = {"key": "value"}  # Should be snake_case
    URL = "https://example.com"  # Should be lowercase
    myVar = "value"  # Should be snake_case

# ✅ CORRECT - Proper naming
def test_function():
    test_data = {"key": "value"}
    url = "https://example.com"
    my_var = "value"
```

### **6. W0613: Unused argument**

```python
# ❌ VIOLATION - Unused parameter
def process_data(data, config, unused_param):
    return data.process()

# ✅ CORRECT - Remove unused parameter
def process_data(data, config):
    return data.process()

# ✅ ALTERNATIVE - Use underscore prefix if needed for interface
def process_data(data, config, _unused_param):
    return data.process()
```

**🚨 MOST COMMON TEST ERROR: Unused Mock Arguments**

```python
# ❌ VIOLATION - Mock parameter not used in test
@patch('honeyhive.utils.logger.safe_log')
def test_method(self, mock_safe_log: Mock) -> None:
    """Test method without using mock_safe_log."""
    processor = SomeProcessor()
    processor.process_data()
    # mock_safe_log never used - Pylint violation W0613

# ✅ CORRECT - Either use the mock or remove it
@patch('honeyhive.utils.logger.safe_log')
def test_method(self, mock_safe_log: Mock) -> None:
    """Test method with mock verification."""
    processor = SomeProcessor()
    processor.process_data()
    mock_safe_log.assert_called()  # Now mock is used

# ✅ ALTERNATIVE - Use underscore prefix if mock needed for patching only
@patch('honeyhive.utils.logger.safe_log')
def test_method(self, _mock_safe_log: Mock) -> None:
    """Test method where mock is needed for patching but not verification."""
    processor = SomeProcessor()
    processor.process_data()
    # Mock patches the method but we don't need to verify calls
```

### **7. W0612: Unused variable**

```python
# ❌ VIOLATION - Variable assigned but never used
def test_function():
    result = expensive_computation()
    unused_var = "not used"  # Pylint violation
    return result

# ✅ CORRECT - Remove unused variable
def test_function():
    result = expensive_computation()
    return result
```

### **8. C1803: Use implicit booleanness**

```python
# ❌ VIOLATION - Explicit comparison with empty containers
if len(items) == 0:
    return None
if items == []:
    return None
assert result == {}  # Common in tests - use implicit instead

# ✅ CORRECT - Use implicit booleanness
if not items:
    return None
assert not result  # Much cleaner for empty containers
```

**🚨 MOST COMMON TEST ERROR: Empty Dict/List Comparisons**

```python
# ❌ VIOLATION - Explicit empty comparison in tests
def test_empty_result(self) -> None:
    result = processor.get_attributes()
    assert result == {}  # Pylint violation C1803

# ✅ CORRECT - Use implicit booleanness
def test_empty_result(self) -> None:
    result = processor.get_attributes()
    assert not result  # Clean and Pythonic
```

### **9. C0303: Trailing whitespace**

```python
# ❌ VIOLATION - Trailing spaces (invisible)
def function():    
    return "value"    

# ✅ CORRECT - No trailing whitespace
def function():
    return "value"
```

### **10. W0108: Unnecessary lambda**

```python
# ❌ VIOLATION - Lambda that could be direct call
def test_baggage_side_effect(self) -> None:
    mock_get_baggage.side_effect = lambda key, ctx: baggage_data.get(key)

# ✅ CORRECT - Direct method reference
def test_baggage_side_effect(self) -> None:
    mock_get_baggage.side_effect = baggage_data.get
```

**🚨 COMMON TEST ERROR: Unnecessary Lambda in Mock side_effect**

```python
# ❌ VIOLATION - Lambda wrapper not needed
def mock_baggage_side_effect(key: str, ctx: Context) -> Optional[str]:
    return baggage_data.get(key)

mock_get_baggage.side_effect = lambda k, c: mock_baggage_side_effect(k, c)

# ✅ CORRECT - Direct function reference
def mock_baggage_side_effect(key: str, ctx: Context) -> Optional[str]:
    return baggage_data.get(key)

mock_get_baggage.side_effect = mock_baggage_side_effect
```

### **11. W0621: Redefining name from outer scope**

```python
# ❌ VIOLATION - Redefining outer scope variable
items = ["a", "b", "c"]

def process():
    items = []  # Shadows outer scope
    return items

# ✅ CORRECT - Use different variable name
items = ["a", "b", "c"]

def process():
    processed_items = []
    return processed_items
```

## 📋 **Prevention Checklist**

**Before generating ANY function, check:**

- [ ] **≤5 positional arguments**: Use `*,` for keyword-only after 5th
- [ ] **All imports used**: Remove unused imports (uuid, pytest if not used)
- [ ] **Line length ≤88**: Break long lines appropriately (especially docstrings)
- [ ] **Docstring present**: Add Sphinx-style docstring
- [ ] **snake_case naming**: All variables and functions
- [ ] **No unused parameters**: Remove or prefix with `_` (especially mock parameters)
- [ ] **No unused variables**: Remove unnecessary assignments
- [ ] **Implicit booleanness**: Use `assert not result` not `assert result == {}`
- [ ] **No trailing whitespace**: Clean line endings (run Black)
- [ ] **No name shadowing**: Use unique variable names
- [ ] **No unnecessary lambdas**: Use direct function references for side_effect
- [ ] **Mock arguments used**: Either verify calls or prefix with `_`

## ⚡ **Quick Fixes**

### **R0917 Fix**
```python
# Add *, after 5th parameter
def func(a, b, c, d, e, *, f=None, g=None):
```

### **W0611 Fix**
```python
# Remove unused imports or add # noqa: F401 if needed for re-export
```

### **C0301 Fix**
```python
# Break long lines
very_long_expression = (
    first_part +
    second_part +
    third_part
)
```

### **C0116 Fix**
```python
def function():
    """Brief description.
    
    Returns:
        Description of return value
    """
```

---

**🎯 Remember**: These 10 violations account for 80% of Pylint errors in AI-generated code.
