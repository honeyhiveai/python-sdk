# Parameter Planning

**🎯 Prevent R0917: Too many positional arguments violations through systematic planning**

## 🚨 **The Problem**

**Common AI Assistant Failure:**
```python
# ❌ WRONG - Generates too many positional arguments
def test_method(self, mock1, mock2, mock3, mock4, mock5, mock6):
# Result: R0917: Too many positional arguments (6/5)
```

## ✅ **The Solution: Systematic Parameter Planning**

### **Step 1: Count Parameters Before Writing (30 seconds)**

**MANDATORY: Count parameters BEFORE writing function signature:**

```python
# PARAMETER COUNTING WORKSHEET
"""
Function: test_initialization_with_optimized_session_failure

Parameters needed:
1. self                           # Always present for methods
2. mock_safe_log                  # From @patch decorator  
3. mock_create_session           # From @patch decorator
4. mock_otlp_exporter           # From @patch decorator
5. mock_tracer                  # From fixture
6. mock_otlp_session_config     # From fixture

TOTAL: 6 parameters
RULE: ≤5 positional arguments allowed
SOLUTION: Use keyword-only arguments after position 5
"""
```

### **Step 2: Apply Keyword-Only Pattern**

**When you have >5 parameters, use `*,` to make some keyword-only:**

```python
# ✅ CORRECT - Use keyword-only arguments
def test_initialization_with_optimized_session_failure(
    self,
    mock_safe_log: Mock,
    mock_create_session: Mock,
    mock_otlp_exporter: Mock,
    *,  # Everything after this must be keyword-only
    mock_tracer: Mock,
    mock_otlp_session_config: OTLPSessionConfig,
) -> None:
```

### **Step 3: Understand @patch Injection Order**

**Critical: @patch decorators inject mocks as positional arguments in REVERSE order:**

```python
# @patch decorators inject in REVERSE order
@patch("module.function_c")  # Injected as 2nd parameter
@patch("module.function_b")  # Injected as 3rd parameter  
@patch("module.function_a")  # Injected as 4th parameter
def test_method(
    self,                    # 1st parameter (always self)
    mock_a: Mock,           # 4th @patch (function_a)
    mock_b: Mock,           # 3rd @patch (function_b)  
    mock_c: Mock,           # 2nd @patch (function_c)
    fixture_param: Mock     # Fixture parameters come last
) -> None:
```

## 📋 **Parameter Planning Templates**

### **Template 1: Simple Test Method (≤5 parameters)**
```python
def test_simple_functionality(
    self,
    mock_dependency: Mock,
    fixture_param: Mock
) -> None:
    """Test simple functionality.
    
    Args:
        mock_dependency: Mock for external dependency
        fixture_param: Test fixture parameter
    """
```

### **Template 2: Complex Test Method (>5 parameters)**
```python
def test_complex_functionality(
    self,
    mock_primary: Mock,
    mock_secondary: Mock,
    *,  # Keyword-only arguments start here
    fixture_param1: Mock,
    fixture_param2: SomeType,
    config_param: ConfigType,
) -> None:
    """Test complex functionality with many parameters.
    
    Args:
        mock_primary: Primary mock dependency
        mock_secondary: Secondary mock dependency
        fixture_param1: First test fixture
        fixture_param2: Second test fixture  
        config_param: Configuration parameter
    """
```

### **Template 3: Multiple @patch Decorators**
```python
@patch("module.function_c")
@patch("module.function_b")
@patch("module.function_a")
def test_with_multiple_patches(
    self,
    mock_a: Mock,      # Last @patch (function_a)
    mock_b: Mock,      # Middle @patch (function_b)
    mock_c: Mock,      # First @patch (function_c)
    *,                 # Keyword-only for additional params
    fixture_param: Mock,
) -> None:
    """Test with multiple patch decorators.
    
    Args:
        mock_a: Mock for function_a (injected by @patch)
        mock_b: Mock for function_b (injected by @patch)
        mock_c: Mock for function_c (injected by @patch)
        fixture_param: Test fixture parameter
    """
```

## 🚨 **Parameter Planning Checklist**

**Before writing ANY function signature:**

- [ ] **Counted total parameters**: Including self, mocks, fixtures
- [ ] **Identified @patch injections**: Counted @patch decorators
- [ ] **Planned parameter order**: @patch mocks first (reverse order), then fixtures
- [ ] **Applied keyword-only rule**: Used `*,` if >5 total parameters
- [ ] **Added type annotations**: All parameters have complete type hints
- [ ] **Added return annotation**: Function has `-> None` or appropriate return type

## 📊 **Parameter Count Quick Reference**

| Scenario | Max Positional | Pattern |
|----------|----------------|---------|
| **Simple test** | 1-3 params | `def test(self, param1, param2):` |
| **Medium test** | 4-5 params | `def test(self, p1, p2, p3, p4):` |
| **Complex test** | 6+ params | `def test(self, p1, p2, *, p3, p4, p5):` |

## ✅ **Success Criteria**

**Your function signature is correct when:**
- Total positional arguments ≤ 5 (including `self`)
- @patch mocks are in reverse decorator order
- Keyword-only arguments used for >5 parameters
- All parameters have type annotations
- Function has return type annotation

---

**📝 Next**: [type-annotations.md](type-annotations.md) - Complete type annotation requirements
