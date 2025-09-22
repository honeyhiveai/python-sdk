# Debugging Methodology

**🎯 Systematic 6-step process for debugging failing tests in the HoneyHive Python SDK**

## 🚨 **MANDATORY: 6-Step Debugging Process**

**AI assistants MUST follow this systematic approach when debugging failing tests**

### **Step 1: Identify the Failing Test**
```bash
# Run specific failing test to isolate the issue
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
python -m pytest tests/unit/test_specific_file.py::TestClass::test_method -v
```

**What to Look For:**
- Exact test method that's failing
- Error type (ImportError, AttributeError, TypeError, etc.)
- Line number where failure occurs
- Full stack trace

### **Step 2: Read and Analyze Error Message**
```python
# Example error analysis
"""
TypeError: TestClass.test_method() takes 2 positional arguments but 6 were given

Analysis:
- Method signature expects 2 args (self + 1 parameter)
- @patch decorators are injecting 5 additional mock objects
- Need to add mock parameters to method signature
"""
```

**Common Error Patterns:**
- **ImportError**: Missing imports or circular dependencies
- **AttributeError**: Missing attributes or incorrect object access
- **TypeError**: Incorrect method signatures or argument counts
- **AssertionError**: Test logic or expected values incorrect

### **Step 3: Analyze Production Code Being Tested**
```python
# Read and understand the production code under test
# Example: If testing honeyhive.tracer.processing.context.process_span()

# 1. Examine function signature
def process_span(
    span: ReadableSpan,
    tracer_instance: Any,
    *,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

# 2. Understand function behavior
# - What does it do?
# - What are the inputs/outputs?
# - What are the dependencies?
# - What error conditions exist?

# 3. Identify key logic paths
# - Main success path
# - Error handling paths
# - Edge cases and boundary conditions
# - External dependencies (APIs, files, etc.)
```

**Production Code Analysis Checklist:**
- [ ] **Function Signature**: Understand parameters, types, return values
- [ ] **Core Logic**: Identify main functionality and business logic
- [ ] **Dependencies**: Note external calls, imports, and integrations
- [ ] **Error Handling**: Understand exception types and error conditions
- [ ] **Edge Cases**: Identify boundary conditions and special cases
- [ ] **State Changes**: Note any side effects or state modifications
- [ ] **Configuration**: Understand config dependencies and defaults

**Detailed Analysis Questions:**
```python
# When analyzing production code, ask these questions:

# 1. FUNCTIONALITY
# - What is the primary purpose of this function/method?
# - What business logic does it implement?
# - What are the expected inputs and outputs?

# 2. DEPENDENCIES
# - What external modules/functions does it call?
# - What configuration values does it read?
# - What state does it access or modify?

# 3. ERROR CONDITIONS
# - What exceptions can it raise?
# - What validation does it perform?
# - How does it handle invalid inputs?

# 4. TEST COVERAGE NEEDS
# - What are the main code paths to test?
# - What edge cases need coverage?
# - What error conditions should be tested?
# - What mocks are needed for dependencies?

# Example: Analyzing honeyhive.tracer.processing.context._add_experiment_context
def _add_experiment_context(baggage_items: Dict[str, str], tracer_instance: Any) -> None:
    """Add experiment context to baggage items."""
    # Analysis:
    # - Purpose: Adds experiment metadata to baggage for tracing
    # - Dependencies: tracer_instance.config.experiment.experiment_metadata
    # - Error conditions: AttributeError if config missing, JSON serialization errors
    # - Test needs: Mock tracer with config, test with/without metadata, test JSON errors
```

### **Step 4: Check Imports and Setup**
```python
# Verify all required imports are present
from typing import Any, Dict, List, Optional  # Type annotations
from unittest.mock import Mock, patch         # Mocking framework
import pytest                                 # Test framework

# Check for missing project imports
from honeyhive.tracer.processing.context import some_function
```

**Import Checklist:**
- [ ] All typing imports for annotations
- [ ] Mock and patch imports for testing
- [ ] Project-specific imports
- [ ] No circular import issues
- [ ] All imports actually used (no unused imports)

### **Step 5: Verify Test Logic and Structure**
```python
# Check method signature matches @patch decorators
@patch("module.function_c")
@patch("module.function_b") 
@patch("module.function_a")
def test_method(
    self,
    mock_a: Mock,  # Injected by patches in reverse order
    mock_b: Mock,
    mock_c: Mock,
    fixture_param: Mock  # Fixture parameters come last
) -> None:
```

**Logic Verification:**
- [ ] Method signature matches patch decorators
- [ ] Mock objects properly configured
- [ ] Assertions test the right behavior
- [ ] Test data matches expected format
- [ ] Edge cases properly handled

### **Step 6: Run in Isolation and Validate Fix**
```bash
# Test the specific method in isolation
python -m pytest tests/unit/test_file.py::TestClass::test_method -v -s

# Run all tests in the class to check for side effects
python -m pytest tests/unit/test_file.py::TestClass -v

# Run full file to ensure no regressions
python -m pytest tests/unit/test_file.py -v
```

**Validation Checklist:**
- [ ] Specific test passes
- [ ] Related tests still pass
- [ ] No new failures introduced
- [ ] Code quality maintained (pylint/mypy)

## 🔧 **Common Debugging Scenarios**

### **Scenario 1: Mock Injection Issues**
```python
# PROBLEM: Too many positional arguments
@patch("module.func_a")
@patch("module.func_b")
def test_method(self, honeyhive_tracer):  # Missing mock parameters
    pass

# SOLUTION: Add mock parameters in reverse patch order
@patch("module.func_a")
@patch("module.func_b")
def test_method(self, mock_b: Mock, mock_a: Mock, honeyhive_tracer: Mock) -> None:
    pass
```

### **Scenario 2: Missing Type Annotations**
```python
# PROBLEM: Mypy errors for missing types
def test_method(self, mock_tracer):
    baggage_items = {}
    
# SOLUTION: Add complete type annotations
def test_method(self, mock_tracer: Mock) -> None:
    baggage_items: Dict[str, str] = {}
```

### **Scenario 3: Import Errors**
```python
# PROBLEM: Module not found
from honeyhive.nonexistent.module import function

# SOLUTION: Check actual module structure
from honeyhive.tracer.processing.context import function
```

### **Scenario 4: Attribute Errors**
```python
# PROBLEM: Mock missing expected attributes
mock_tracer.config.get("key")  # AttributeError: Mock has no attribute 'config'

# SOLUTION: Properly configure mock
mock_tracer.config = Mock()
mock_tracer.config.get.return_value = "value"
```

### **Scenario 5: Assertion Failures**
```python
# PROBLEM: Unexpected test behavior
assert result == {"expected": "value"}  # AssertionError

# SOLUTION: Debug actual vs expected
print(f"Actual result: {result}")
print(f"Expected: {{'expected': 'value'}}")
# Then fix test logic or expectations
```

## 🚨 **Error Prevention Strategies**

### **Before Writing Tests**
1. **Read existing patterns** in similar test files
2. **Check imports** in working test files
3. **Verify mock configurations** match production code
4. **Follow type annotation standards** from the start

### **During Test Development**
1. **Run tests frequently** to catch issues early
2. **Use descriptive variable names** for easier debugging
3. **Add debug prints** temporarily if needed
4. **Test one scenario at a time** to isolate issues

### **After Test Implementation**
1. **Run pylint and mypy** to catch quality issues
2. **Test in isolation** to verify independence
3. **Check for side effects** by running related tests
4. **Validate with full test suite** before committing

## 🎯 **Debugging Tools and Commands**

### **Isolation Testing**
```bash
# Single test method
pytest tests/unit/test_file.py::TestClass::test_method -v -s

# Single test class
pytest tests/unit/test_file.py::TestClass -v

# Single test file
pytest tests/unit/test_file.py -v
```

### **Verbose Output**
```bash
# Maximum verbosity for debugging
pytest tests/unit/test_file.py -vvv -s --tb=long

# Show local variables in tracebacks
pytest tests/unit/test_file.py --tb=long --showlocals
```

### **Quality Checks**
```bash
# Check code quality issues
pylint tests/unit/test_file.py --rcfile=pyproject.toml
mypy tests/unit/test_file.py --config-file=pyproject.toml

# Format code automatically
black tests/unit/test_file.py
```

## 🤖 **Common AI Assistant Error Patterns**

**CRITICAL: Recognize these patterns to debug faster and more accurately**

### **Pattern 1: Mock Injection Signature Mismatch**
```python
# PROBLEM: @patch decorators inject mocks as positional arguments
@patch('honeyhive.tracer.processing.context.some_function')
def test_something(self, mock_tracer):  # ❌ Missing mock parameter
    # TypeError: takes 2 positional arguments but 3 were given

# SOLUTION: Add all mock parameters before fixture parameters
@patch('honeyhive.tracer.processing.context.some_function') 
def test_something(self, mock_func: Mock, mock_tracer: Mock) -> None:  # ✅ Correct
    # All @patch mocks come first as positional args, then fixtures
```

### **Pattern 2: Missing Type Annotations in Tests**
```python
# PROBLEM: Test variables without type annotations (mypy errors)
def test_baggage_items(self, mock_tracer):
    baggage_items = {"key": "value"}  # ❌ No type annotation
    # error: Need type annotation for 'baggage_items'

# SOLUTION: Add complete type annotations to ALL variables
def test_baggage_items(self, mock_tracer: Mock) -> None:
    baggage_items: Dict[str, str] = {"key": "value"}  # ✅ Correct
    result: Dict[str, Any] = process_baggage(baggage_items)
```

### **Pattern 3: Incorrect Import Paths After Refactoring**
```python
# PROBLEM: Imports don't match current production code structure
from honeyhive.tracer.processing.otlp_profiles import EnvironmentAnalyzer  # ❌ Moved/removed

# SOLUTION: Always verify imports against current codebase
from honeyhive.tracer.infra.environment import get_comprehensive_environment_analysis  # ✅ Current
```

### **Pattern 4: Config Access Pattern Mismatch**
```python
# PROBLEM: Using old flat config access pattern
tracer.disable_http_tracing  # ❌ Direct attribute access (old pattern)
tracer.config.get("experiment_metadata")  # ❌ Flat config access (old pattern)

# SOLUTION: Use new nested config structure
tracer.config.disable_http_tracing  # ✅ Root TracerConfig access
tracer.config.experiment.experiment_metadata  # ✅ Nested config access
```

### **Pattern 5: Assertion Logic Errors**
```python
# PROBLEM: Incorrect assertion patterns
assert result == {}  # ❌ Pylint prefers 'not result' for empty containers
assert some_value == None  # ❌ Should use 'is None'

# SOLUTION: Use preferred assertion patterns
assert not result  # ✅ For empty containers
assert some_value is None  # ✅ For None checks
assert len(items) == 0  # ✅ Alternative for empty containers
```

### **Pattern 6: Mock Object Type Mismatches**
```python
# PROBLEM: Mock objects not properly typed or configured
mock_tracer.config = {"key": "value"}  # ❌ Dict instead of proper config object
mock_tracer.some_method.return_value = "string"  # ❌ Wrong return type

# SOLUTION: Properly configure mock objects to match production
mock_tracer.config.experiment.experiment_metadata = {"key": "value"}  # ✅ Nested structure
mock_tracer.some_method.return_value = SomeClass()  # ✅ Correct return type
```

### **Quick Error Pattern Recognition**
```bash
# Use these patterns to quickly identify error types:

# TypeError with argument count → Pattern 1 (Mock injection)
grep -A5 -B5 "takes.*arguments but.*were given" test_output

# Missing type annotation → Pattern 2 (Type annotations)  
grep -A3 -B3 "Need type annotation" test_output

# ImportError → Pattern 3 (Import paths)
grep -A3 -B3 "cannot import name" test_output

# AttributeError with config → Pattern 4 (Config access)
grep -A3 -B3 "has no attribute.*config" test_output
```

## 📋 **Debugging Checklist**

When a test fails, systematically check:

- [ ] **Step 1**: Identified exact failing test and error type
- [ ] **Step 2**: Analyzed error message and stack trace
- [ ] **Step 3**: Analyzed production code being tested for full context
- [ ] **Step 4**: Verified all imports are correct and present
- [ ] **Step 5**: Checked test logic, mocks, and assertions
- [ ] **Step 6**: Validated fix in isolation and with related tests
- [ ] **Quality**: Maintained pylint 10/10 and mypy 0 errors
- [ ] **Documentation**: Updated docstrings if needed

## 💡 **Best Practices**

### **Systematic Approach**
- **Never skip steps** - each step builds on the previous
- **Document findings** - note what you discover at each step
- **Test incrementally** - fix one issue at a time
- **Validate thoroughly** - ensure no regressions

### **Efficient Debugging**
- **Use specific test commands** - don't run full suite unnecessarily
- **Leverage IDE features** - use debugger when available
- **Read error messages carefully** - they often contain the solution
- **Check similar working tests** - use them as reference patterns

---

**💡 Key Principle**: Systematic debugging with thorough production code analysis prevents random fixes and ensures tests properly validate the intended functionality.
