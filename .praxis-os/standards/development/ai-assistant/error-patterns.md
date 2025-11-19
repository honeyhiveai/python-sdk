# AI Assistant Error Pattern Recognition

**🎯 Comprehensive error pattern recognition and resolution guide for AI assistants**

This document provides detailed patterns for recognizing, diagnosing, and resolving common errors that AI assistants encounter when working with the HoneyHive Python SDK.

## 🚨 **CRITICAL: Error Pattern Recognition Framework**

**AI assistants MUST use systematic pattern recognition to debug efficiently**

### **Error Classification System**
```
Error Type → Pattern Recognition → Diagnostic Steps → Resolution Template
```

## 🔍 **Import and Module Errors**

### **Pattern 1: ImportError - Module Not Found**
```python
# ERROR MESSAGE:
# ImportError: cannot import name 'EnvironmentAnalyzer' from 'honeyhive.tracer.processing.otlp_profiles'

# PATTERN RECOGNITION:
# - Class/function moved or renamed
# - Module structure changed
# - Outdated import paths

# DIAGNOSTIC STEPS:
grep -r "EnvironmentAnalyzer" src/honeyhive/  # Find current location
read_file src/honeyhive/__init__.py           # Check current exports
git log --oneline -10 -- src/honeyhive/tracer/processing/otlp_profiles.py  # Check recent changes

# RESOLUTION TEMPLATE:
# 1. Find new location: src/honeyhive/tracer/infra/environment.py
# 2. Update import: from honeyhive.tracer.infra.environment import get_comprehensive_environment_analysis
# 3. Update usage: get_comprehensive_environment_analysis() instead of EnvironmentAnalyzer()
```

### **Pattern 2: ImportError - Circular Dependencies**
```python
# ERROR MESSAGE:
# ImportError: cannot import name 'HoneyHiveTracer' from partially initialized module

# PATTERN RECOGNITION:
# - Circular import between modules
# - Import at module level causing loop
# - Incorrect import order

# DIAGNOSTIC STEPS:
grep -r "from.*honeyhive.*import.*HoneyHiveTracer" src/honeyhive/  # Find all imports
python -c "import honeyhive.tracer.core.base"  # Test direct import

# RESOLUTION TEMPLATE:
# 1. Move import inside function/method
# 2. Use TYPE_CHECKING import pattern
# 3. Restructure module dependencies
```

### **Pattern 3: ModuleNotFoundError - Missing Dependencies**
```python
# ERROR MESSAGE:
# ModuleNotFoundError: No module named 'pytest'

# PATTERN RECOGNITION:
# - Missing test dependencies in lint environment
# - Virtual environment not activated
# - Incomplete installation

# DIAGNOSTIC STEPS:
which python                    # Verify virtual environment
pip list | grep pytest         # Check if pytest installed
cat tox.ini | grep -A5 "testenv:lint"  # Check lint environment deps

# RESOLUTION TEMPLATE:
# 1. Add missing dependency to tox.ini [testenv:lint] deps
# 2. Reinstall: pip install -e .[dev]
# 3. Verify: python -c "import pytest"
```

## 🧪 **Test Execution Errors**

### **Pattern 4: TypeError - Argument Count Mismatch**
```python
# ERROR MESSAGE:
# TypeError: test_method() takes 2 positional arguments but 6 were given

# PATTERN RECOGNITION:
# - @patch decorators inject mocks as positional arguments
# - Method signature doesn't account for injected mocks
# - Incorrect mock parameter order

# DIAGNOSTIC STEPS:
grep -B5 -A10 "def test_method" test_file.py  # Find method signature
grep -B10 "def test_method" test_file.py | grep "@patch"  # Count @patch decorators

# RESOLUTION TEMPLATE:
# Before: def test_method(self, fixture):
# After:  def test_method(self, mock1: Mock, mock2: Mock, fixture: Mock) -> None:
# Rule: @patch decorators inject mocks in reverse order as positional args
```

### **Pattern 5: AttributeError - Missing Mock Configuration**
```python
# ERROR MESSAGE:
# AttributeError: 'Mock' object has no attribute 'config'

# PATTERN RECOGNITION:
# - Mock object not properly configured
# - Missing nested attribute structure
# - Incorrect mock setup for complex objects

# DIAGNOSTIC STEPS:
grep -A10 -B5 "mock_tracer" test_file.py     # Find mock configuration
read_file src/honeyhive/tracer/core/base.py  # Understand real object structure

# RESOLUTION TEMPLATE:
# Configure nested mock structure:
mock_tracer.config.session.inputs = "test_value"
mock_tracer.config.experiment.experiment_metadata = {"key": "value"}
# Or use spec_set for automatic attribute creation
```

### **Pattern 6: AssertionError - Logic Mismatch**
```python
# ERROR MESSAGE:
# AssertionError: assert {'key': 'value'} == {}

# PATTERN RECOGNITION:
# - Expected vs actual value mismatch
# - Incorrect test logic or assumptions
# - Production code behavior changed

# DIAGNOSTIC STEPS:
read_file src/honeyhive/path/to/module.py    # Understand production behavior
python -c "print(repr(actual_value))"        # Debug actual return value

# RESOLUTION TEMPLATE:
# 1. Verify production code behavior matches test expectation
# 2. Update test assertion to match correct behavior
# 3. Use assert not result for empty containers (pylint preference)
```

## 🔧 **Type Checking Errors**

### **Pattern 7: Mypy - Missing Type Annotations**
```python
# ERROR MESSAGE:
# error: Function is missing a type annotation for one or more arguments

# PATTERN RECOGNITION:
# - Missing parameter type annotations
# - Missing return type annotation
# - Incomplete typing imports

# DIAGNOSTIC STEPS:
grep -A5 "def.*(" file.py | grep -v ":" # Find functions without type annotations
grep "from typing import" file.py        # Check typing imports

# RESOLUTION TEMPLATE:
# Before: def function(param1, param2):
# After:  def function(param1: str, param2: int) -> bool:
# Add: from typing import Any, Dict, List, Optional
```

### **Pattern 8: Mypy - Type Incompatibility**
```python
# ERROR MESSAGE:
# error: Argument 1 has incompatible type "dict[str, str | None]"; expected "dict[str, str]"

# PATTERN RECOGNITION:
# - Type mismatch between expected and actual
# - Optional values where non-optional expected
# - Incorrect type annotation

# DIAGNOSTIC STEPS:
grep -A5 -B5 "Dict\[str, str\]" file.py     # Find type annotation
grep -A5 -B5 "Optional\[str\]" file.py      # Find optional types

# RESOLUTION TEMPLATE:
# Filter None values before passing to function:
filtered_dict: Dict[str, str] = {k: v for k, v in original_dict.items() if v is not None}
function_call(filtered_dict)
```

### **Pattern 9: Mypy - Import Type Issues**
```python
# ERROR MESSAGE:
# error: Skipping analyzing "honeyhive": module is installed, but missing library stubs

# PATTERN RECOGNITION:
# - Missing py.typed file in package
# - Package not recognized as typed
# - Import from untyped module

# DIAGNOSTIC STEPS:
ls src/honeyhive/py.typed                    # Check if py.typed exists
grep -r "import-untyped" .mypy.ini          # Check mypy config

# RESOLUTION TEMPLATE:
# 1. Create empty py.typed file in src/honeyhive/
# 2. Add # type: ignore[import-untyped] to imports if needed
# 3. Ensure package includes type information
```

## 🏗️ **Configuration and Architecture Errors**

### **Pattern 10: AttributeError - Config Access Pattern**
```python
# ERROR MESSAGE:
# AttributeError: 'HoneyHiveTracer' object has no attribute 'disable_http_tracing'

# PATTERN RECOGNITION:
# - Using old direct attribute access pattern
# - Should use nested config structure
# - Outdated test patterns

# DIAGNOSTIC STEPS:
grep -r "tracer\.disable_http_tracing" tests/  # Find old patterns
read_file src/honeyhive/config/utils.py       # Understand config structure

# RESOLUTION TEMPLATE:
# Before: tracer.disable_http_tracing
# After:  tracer.config.disable_http_tracing
# Before: tracer.config.get("experiment_metadata")
# After:  tracer.config.experiment.experiment_metadata
```

### **Pattern 11: KeyError - Missing Configuration**
```python
# ERROR MESSAGE:
# KeyError: 'experiment_metadata'

# PATTERN RECOGNITION:
# - Accessing config key that doesn't exist
# - Using flat config access on nested structure
# - Missing default value handling

# DIAGNOSTIC STEPS:
read_file src/honeyhive/config/models/experiment.py  # Check config model
grep -r "experiment_metadata" src/honeyhive/         # Find usage patterns

# RESOLUTION TEMPLATE:
# Use getattr with default for nested config:
experiment_metadata = getattr(tracer.config.experiment, "experiment_metadata", None)
# Or ensure config is properly initialized with defaults
```

## 🔄 **Linting and Formatting Errors**

### **Pattern 12: Pylint - Too Many Arguments**
```python
# ERROR MESSAGE:
# R0917: Too many positional arguments (6/5) (too-many-positional-arguments)

# PATTERN RECOGNITION:
# - Function has more than 5 positional arguments
# - Should use keyword-only arguments
# - Need to refactor function signature

# DIAGNOSTIC STEPS:
grep -A3 "def.*(" file.py | grep -E "\w+," | wc -l  # Count parameters

# RESOLUTION TEMPLATE:
# Before: def function(a, b, c, d, e, f):
# After:  def function(a, b, *, c, d, e, f):
# Or add disable: # pylint: disable=too-many-positional-arguments
```

### **Pattern 13: Pylint - Unused Variables**
```python
# ERROR MESSAGE:
# W0612: Unused variable 'span' (unused-variable)

# PATTERN RECOGNITION:
# - Variable assigned but never used
# - Mock parameter not referenced in test
# - Temporary variable in development

# DIAGNOSTIC STEPS:
grep -n "span.*=" file.py                    # Find variable assignment
grep -A10 -B10 "span" file.py               # Check usage context

# RESOLUTION TEMPLATE:
# Rename unused variables to underscore:
# Before: span = tracer.start_span("test")
# After:  _ = tracer.start_span("test")
# Or: _span = tracer.start_span("test")  # If might be used later
```

## 🎯 **Quick Error Diagnosis Commands**

### **Rapid Pattern Recognition**
```bash
# Quick error type identification
grep -E "(Error|Exception):" test_output.log | head -5

# Import error diagnosis
grep -A3 -B3 "ImportError\|ModuleNotFoundError" test_output.log

# Type error diagnosis  
grep -A3 -B3 "TypeError\|AttributeError" test_output.log

# Assertion error diagnosis
grep -A5 -B5 "AssertionError" test_output.log

# Mypy error summary
python -m mypy src/ 2>&1 | grep "error:" | sort | uniq -c | sort -nr

# Pylint error summary
pylint src/ 2>&1 | grep -E "^\w+:" | sort | uniq -c | sort -nr
```

### **Context Gathering Commands**
```bash
# Understand current codebase state
git log --oneline -5                          # Recent changes
git diff --name-only HEAD~1                   # Files changed recently
find src/ -name "*.py" -mtime -1             # Recently modified files

# Analyze specific error context
grep -r "error_pattern" src/ tests/           # Find related code
git blame file.py | grep -A5 -B5 "line_num"  # Who changed problematic line
```

## 📋 **Error Resolution Workflow**

### **Systematic Error Resolution Process**

1. **Pattern Recognition** (30 seconds)
   ```bash
   # Identify error type and pattern
   grep -E "(Error|Exception):" error_output | head -1
   ```

2. **Context Gathering** (60 seconds)
   ```bash
   # Understand current state and recent changes
   read_file relevant_file.py
   git log --oneline -3 -- relevant_file.py
   ```

3. **Diagnostic Execution** (90 seconds)
   ```bash
   # Run specific diagnostic commands for error pattern
   # Use pattern-specific commands from above
   ```

4. **Resolution Application** (120 seconds)
   ```bash
   # Apply resolution template
   # Test fix in isolation
   # Verify no regressions
   ```

5. **Validation** (60 seconds)
   ```bash
   # Confirm fix works
   python -m pytest specific_test -v
   tox -e lint file.py
   ```

## 🔗 **Related Error Resources**

- **[Debugging Methodology](../testing/debugging-methodology.md)** - Systematic 6-step debugging process
- **[Quality Framework](quality-framework.md)** - Quality gates and validation requirements
- **[Code Generation Patterns](code-generation-patterns.md)** - Correct code patterns to prevent errors
- **[Validation Protocols](validation-protocols.md)** - Pre-work validation to prevent errors

---

**📝 Next Steps**: When encountering errors, use this pattern recognition guide first, then apply the [Debugging Methodology](../testing/debugging-methodology.md) for systematic resolution.
