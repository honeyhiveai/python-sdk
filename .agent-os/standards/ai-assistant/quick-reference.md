# AI Assistant Quick Reference Cards

**🎯 Essential quick reference cards for AI assistants working on the HoneyHive Python SDK**

This document provides condensed, actionable reference cards that AI assistants can quickly consult during development tasks.

## 🚨 **CRITICAL: Pre-Work Validation Card**

### **Environment Setup (30 seconds)**
```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
python --version && which python
git status --porcelain && git branch --show-current
```
**✅ Must be clean, correct branch, Python 3.11+**

### **Codebase Validation (60 seconds)**
```bash
read_file src/honeyhive/__init__.py      # Current API
grep -r "class.*Tracer" src/honeyhive/   # Class names
grep -r "EventType\." src/honeyhive/     # Enum patterns
```
**✅ Understand current structure before changes**

## 🧪 **Test Debugging Quick Card**

### **Failing Test Diagnosis (90 seconds)**
```bash
# 1. Isolate the failure
python -m pytest tests/unit/test_file.py::TestClass::test_method -v

# 2. Read production code being tested
read_file src/honeyhive/path/to/module.py

# 3. Check mock patterns
grep -A5 -B5 "@patch" tests/unit/test_file.py

# 4. Verify config access patterns
grep -r "config\." src/honeyhive/path/to/module.py
```

### **Common Test Fix Patterns**
| Error Pattern | Quick Fix |
|---------------|-----------|
| `takes 2 positional arguments but 6 were given` | Add mock parameters: `def test(self, mock1: Mock, mock2: Mock, fixture: Mock)` |
| `cannot import name 'X'` | Check if moved: `grep -r "X" src/honeyhive/` |
| `'Mock' object has no attribute 'config'` | Configure mock: `mock.config.session.inputs = "value"` |
| `Need type annotation for 'variable'` | Add type: `variable: Dict[str, str] = {}` |

## ⚡ **Pylint Violation Prevention Card**

### **🚨 CRITICAL: Avoid These Patterns**
| **Violation** | **❌ Wrong** | **✅ Correct** |
|---------------|--------------|----------------|
| **C0303: Trailing whitespace** | `result = func()   ` | `result = func()` |
| **W0611: Unused import** | `import os  # unused` | Only import what's used |
| **C1803: Non-pythonic boolean** | `assert result == {}` | `assert not result` |
| **W0621: Redefined outer name** | Missing disable | `# pylint: disable=redefined-outer-name` |
| **C0415: Import outside toplevel** | No disable comment | `# pylint: disable=import-outside-toplevel` |

### **⚡ Test File Generation Checklist**
```python
# ✅ MANDATORY: Start every test file with this header
"""Unit tests for [module].

This module follows Agent OS testing standards.
"""

# pylint: disable=protected-access,too-many-lines,redefined-outer-name
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.

from typing import Any  # ✅ Use Any for flexible fixture types
from unittest.mock import Mock, patch  # ✅ Only import what's used

import pytest
```

### **⚡ Generation Rules (30 seconds)**
```
□ No trailing whitespace on any line
□ Use `not collection` instead of `== {}`  
□ Only import what will actually be used
□ Use `Any` for fixture return types
□ Add appropriate pylint disables for test files
□ Ensure all variables and parameters are used
```

## 🏗️ **Code Generation Quick Card**

### **⚡ PYLINT-COMPLIANT Function Template (2 minutes)**
```python
def function_name(
    param1: Type1,
    param2: Type2,
    *,
    optional_param: Optional[Type3] = None
) -> ReturnType:
    """Brief description.
    
    :param param1: Description
    :type param1: Type1
    :param param2: Description
    :type param2: Type2
    :param optional_param: Description
    :type optional_param: Optional[Type3]
    :return: Description
    :rtype: ReturnType
    :raises ValueError: When validation fails
    
    **Example:**
    
    .. code-block:: python
    
        result = function_name("value", 42)
        print(result)
    """
    # Type annotations for local variables
    processed_data: Dict[str, Any] = {}
    
    try:
        # Main logic with validation
        if not param1:
            raise ValueError("param1 cannot be empty")
        
        # Business logic here
        processed_data = perform_operation(param1, param2)
        return processed_data
        
    except SpecificError as e:
        safe_log(logger, "warning", f"Known issue: {e}")
        raise
        
    except Exception as e:
        safe_log(logger, "debug", f"Unexpected error: {e}")
        return default_value
```

### **Mandatory Checklist (30 seconds)**
- [ ] **Type annotations**: All params, returns, variables
- [ ] **Docstring**: Sphinx format with example
- [ ] **Error handling**: Graceful degradation with safe_log
- [ ] **Keyword args**: Use `*,` for >3 parameters
- [ ] **Pylint compliance**: Generate 10/10 code without post-fixes

### **Pylint Violation Prevention (Quick Check)**
| Violation | Prevention |
|-----------|------------|
| **R0917: Too many args** | Use `*,` for keyword-only after 3rd param |
| **C0103: Invalid name** | Use descriptive names: `item_list` not `l` |
| **C0116: Missing docstring** | Always include complete Sphinx docstring |
| **W0613: Unused argument** | Use all params or prefix with `_unused_param` |
| **W0612: Unused variable** | Remove unused vars or use `_` for throwaway |
| **R0903: Too few methods** | Add 2+ public methods or use `@dataclass` |

## ⚡ **Quality Gates Quick Card**

### **Sequential Quality Execution (5 minutes)**
```bash
# Run in order - STOP if any fail
tox -e format           # Black formatting
tox -e lint            # Pylint + mypy  
tox -e unit            # Unit tests
tox -e integration     # Integration tests
cd docs && make html   # Documentation
```

### **Quality Gate Targets**
| Gate | Target | Fix Command |
|------|--------|-------------|
| Format | 100% pass | `black file.py` |
| Pylint | ≥8.0/10.0 | Fix violations or add approved disables |
| Mypy | 0 errors | Add type annotations |
| Unit Tests | 100% pass | Use debugging methodology |
| Integration | 100% pass | Check API connectivity |
| Docs | 0 warnings | Fix RST syntax |

## 🔧 **Configuration Usage Quick Card**

### **Direct Usage in Logic (No Intermediate Variables)**
```python
# Use config values directly in conditional logic
if tracer.config.disable_http_tracing:
    return make_request_without_tracing(endpoint, data)

# Use config values directly in span attributes
span.set_attribute("session_context", tracer.config.session.inputs)

# Use config values directly in data processing
user_data["experiment_id"] = tracer.config.experiment.experiment_metadata.get("id")

# Use config values directly in function calls
timeout = tracer.config.http.timeout
response = make_request(url, timeout=timeout)
```

### **Test Config Setup**
```python
# In tests - direct assignment for mocking
mock_tracer.config.disable_http_tracing = True
mock_tracer.config.session.inputs = "test_context"
mock_tracer.config.experiment.experiment_metadata = {"id": "exp_123"}

# Test the direct usage in your functions
result = your_function(data, mock_tracer)
assert result["used_config_directly"]
```

## 🚨 **Error Pattern Quick Card**

### **Instant Error Recognition**
```bash
# Quick error type identification
grep -E "(Error|Exception):" error_output | head -1

# Pattern-specific diagnosis
grep -A3 -B3 "ImportError" error_output          # Pattern 1-3
grep -A3 -B3 "TypeError.*arguments" error_output # Pattern 4
grep -A3 -B3 "AttributeError.*config" error_output # Pattern 10
grep -A3 -B3 "Need type annotation" error_output  # Pattern 7
```

### **Top 5 Error Fixes**
1. **Mock injection**: Add mock parameters to test method signature
2. **Import paths**: Update to current module structure  
3. **Type annotations**: Add to all functions and variables
4. **Config access**: Use nested pattern (`tracer.config.session.inputs`)
5. **Assertion patterns**: Use `assert not result` for empty containers

## 📝 **Documentation Quick Card**

### **Sphinx Docstring Essentials**
```python
"""Brief description.

Detailed description with context.

:param param_name: Parameter description
:type param_name: ParameterType
:return: Return value description
:rtype: ReturnType
:raises ExceptionType: When this exception occurs

**Example:**

.. code-block:: python

    result = function_call("example")
    print(result)

**Note:**

Additional context or warnings.
"""
```

### **Documentation Quality Checklist**
- [ ] **EventType enums**: Use `EventType.model` not `"model"`
- [ ] **Complete imports**: All necessary imports in examples
- [ ] **Working examples**: Copy-paste executable code
- [ ] **Cross-references**: All internal links work

## 🎯 **Decision Tree Quick Card**

### **Test Failure Decision Tree**
```
Test Failed?
├── ImportError? → Check if module moved → Update import
├── TypeError (args)? → Check @patch count → Add mock params  
├── AttributeError (config)? → Use nested config → tracer.config.X.Y
├── AssertionError? → Read production code → Fix logic
└── Type annotation? → Add type hints → All variables
```

### **Code Generation Decision Tree**
```
Writing Function?
├── >3 params? → Use keyword-only args (*, param)
├── Error handling? → Add try/except with safe_log
├── Type hints? → Add to ALL params/returns/variables
├── Docstring? → Sphinx format with example
└── Tests? → Write unit tests with type annotations
```

## 🔗 **Quick Navigation Links**

### **Essential Documents**
- **[Quality Framework](quality-framework.md)** - Complete validation checklist
- **[Code Generation Standards](code-generation-standards.md)** - Core requirements and compliance
- **[Function Templates](function-templates.md)** - Complete code templates
- **[Test Generation Patterns](test-generation-patterns.md)** - Test-specific guidance
- **[Error Patterns](error-patterns.md)** - Comprehensive error guide
- **[Debugging Methodology](../testing/debugging-methodology.md)** - 6-step process

### **Command References**
- **[Validation Protocols](validation-protocols.md)** - Pre-work validation
- **[Test Execution Commands](../testing/test-execution-commands.md)** - All tox commands
- **[Code Quality Requirements](../testing/code-quality-requirements.md)** - Quality standards

## 📊 **Success Metrics Card**

### **AI Assistant Quality Indicators**
✅ **Excellent Performance**:
- First-attempt quality gate passes: >90%
- Test fixes without regressions: >95%
- Code generation with complete annotations: 100%

⚠️ **Needs Improvement**:
- Multiple quality gate iterations required
- Frequent import/config pattern errors
- Missing type annotations in generated code

❌ **Critical Issues**:
- Failing tests committed
- Quality gates bypassed
- Production code crashes

---

**💡 Pro Tip**: Keep this reference open in a separate tab while working. Use the quick commands and checklists to maintain consistent quality and speed.
