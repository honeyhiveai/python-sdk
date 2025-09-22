# Unit Test Path

## 🎯 **UNIT TEST PRINCIPLES**

### **Core Philosophy**
- **Test Isolation**: Each test completely independent with comprehensive mocking
- **Mock ALL External Dependencies**: requests, os, sys, time, external APIs
- **Coverage Target**: 90%+ line coverage (non-negotiable)
- **Quality Standard**: 10.0/10 Pylint, 0 MyPy errors, 100% pass rate

### **When to Choose Unit Path**
- Testing individual classes/functions in isolation
- Single module focus with business logic
- Need comprehensive mocking strategy
- Target: 90%+ code coverage

---

## 📋 **PHASE-SPECIFIC REQUIREMENTS**

### **Phase 1: Method Verification (Unit Focus)**

**🔍 Unit-Specific Analysis:**
- **All public methods** with exact signatures (primary test targets)
- **All classes** with initialization parameters (constructor testing)
- **All module-level functions** and their parameters (function testing)
- **Complex private methods** that affect public behavior (indirect testing)
- **Property methods** and their getter/setter logic (property testing)

**🚨 Mandatory Commands:**
```bash
grep -n "^class\|^def\|^    def" [PRODUCTION_FILE]
python -c "import ast, inspect; [print(f'{node.name}: {ast.get_docstring(node)}') for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]"
grep -E "^    def [^_]|^def [^_]" [PRODUCTION_FILE]
```

### **Phase 2: Logging Analysis (Mocking Focus)**

**🔍 Unit-Specific Analysis:**
- **All logging calls** (will be mocked to verify correct messages)
- **Logging levels used** (debug, info, warning, error) for assertion testing
- **Safe_log integration** (mock strategy for multi-instance safe logging)
- **Error logging patterns** (verify errors are logged correctly)
- **Conditional logging** (test different logging paths)

**🚨 Mandatory Commands:**
```bash
grep -n "log\." [PRODUCTION_FILE]
grep -n "import.*log\|from.*log\|getLogger\|basicConfig" [PRODUCTION_FILE]
grep -n "safe_log" [PRODUCTION_FILE]
```

### **Phase 3: Dependency Analysis (Comprehensive Mocking)**

**🔍 Unit-Specific Analysis:**
- **Standard library imports** (os, sys, json, etc.) - Mock when used
- **Third-party libraries** (requests, pydantic, etc.) - Always mock
- **Internal project modules** (honeyhive.* imports) - Mock for isolation
- **Configuration dependencies** - Mock for test control
- **Mock strategies** (patch.object vs patch, return values, side effects)

**🚨 Critical Principle:** Mock ALL external dependencies for true isolation.

**🚨 Mandatory Commands:**
```bash
grep -E "^import |^from " [PRODUCTION_FILE]
grep -E "requests\.|urllib\.|json\.|os\.|sys\.|time\." [PRODUCTION_FILE]
grep -E "from honeyhive|import honeyhive" [PRODUCTION_FILE]
grep -E "config\.|settings\.|env\.|getenv" [PRODUCTION_FILE]
```

### **Phase 4: Usage Patterns (Isolation Focus)**

**🔍 Unit-Specific Analysis:**
- **Common instantiation patterns** (constructor parameter combinations)
- **Typical method call sequences** (test method interactions)
- **Error handling patterns** (test exception scenarios)
- **Integration boundaries** (what to mock at module edges)
- **Configuration patterns** (test different config scenarios)

**🚨 Focus:** Understand real usage to create realistic isolated tests.

**🚨 Mandatory Commands:**
```bash
grep -r "from.*[MODULE_NAME]\|import.*[MODULE_NAME]" src/ --include="*.py"
grep -r "[CLASS_NAME](" src/ --include="*.py" | head -10
grep -r "\.[METHOD_NAME](" src/ --include="*.py" | head -10
```

### **Phase 5: Coverage Analysis (90%+ Target)**

**🔍 Unit-Specific Analysis:**
- **Happy path scenarios** (normal operation with mocked dependencies)
- **Error conditions** (exceptions, invalid inputs with proper mocking)
- **Edge cases** (boundary values, empty inputs, None values)
- **Configuration variations** (different settings via mocked config)
- **All conditional branches** (if/else, try/except, loops)
- **All method combinations** (different parameter combinations)

**🚨 Target:** 90%+ line coverage with comprehensive mocking.

**🚨 Mandatory Commands:**
```bash
tox -e unit -- --cov=[MODULE_PATH] --cov-report=term-missing
python -c "import ast; print([f'{node.lineno}: {node.name}' for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With))])"
```

### **Phase 6: Pre-Generation Linting (Unit Standards)**

**🔍 Unit-Specific Planning:**
- **Import organization** (all imports at top, grouped: standard, third-party, local)
- **Mock patterns** (use `patch.object`, avoid `Mock(spec=Class)` for MyPy compatibility)
- **Type annotations** (minimal for test functions, proper for fixtures)
- **Line length management** (Black will handle, but plan for descriptive test names)
- **Pylint disables** (justified only: `too-many-lines`, `redefined-outer-name` for fixtures)

---

## 🧪 **UNIT TEST GENERATION PATTERNS**

### **Standard Unit Test Structure**
```python
# File header with approved pylint disables
# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

import pytest
from unittest.mock import Mock, patch, PropertyMock

# Use proven fixtures from tests/unit/conftest.py
def test_example(honeyhive_client, mock_tracer_base, mock_safe_log) -> None:
    """Test description with clear purpose."""
    # Arrange: Set up mocks and test data
    # Act: Execute the method under test
    # Assert: Verify expected behavior and mock calls
```

### **Proven Mock Patterns**
```python
# ✅ CORRECT: Use patch.object for MyPy compatibility
with patch.object(target_object, 'method_name') as mock_method:
    mock_method.return_value = expected_value

# ✅ CORRECT: PropertyMock for properties
with patch.object(ClassName, 'property_name', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = expected_value

# ✅ CORRECT: Standard fixtures
def test_with_fixtures(honeyhive_client, mock_tracer_base, mock_safe_log) -> None:
```

### **Standard Unit Test Fixtures**
- `honeyhive_client`: HoneyHive client in test mode
- `honeyhive_tracer`: HoneyHive tracer in test mode with HTTP tracing disabled
- `fresh_honeyhive_tracer`: Fresh tracer instance for isolation
- `mock_client`: Mock HoneyHive client for full mocking
- `mock_tracer`: Mock HoneyHive tracer with context manager support
- `mock_tracer_base`: Comprehensive mock tracer with all standard attributes
- `mock_safe_log`: Standard mock for safe_log function
- `mock_response`: Mock HTTP response (status_code=200, json={"success": True})

---

## ✅ **UNIT TEST QUALITY ENFORCEMENT**

### **Quality Targets**
- **Test Pass Rate**: 100% (all tests must pass)
- **Coverage**: 90%+ line coverage (comprehensive)
- **Pylint Score**: 10.0/10 (perfect)
- **MyPy Errors**: 0 (no type issues)
- **Black Formatting**: Clean (proper formatting)

### **Enhanced Pre-Generation Validation**
**Phase 6 now includes comprehensive test generation readiness checks:**

1. **Import Path Validation:**
   ```python
   # Verify all imports are accessible
   from honeyhive.tracer.instrumentation.initialization import initialize_tracer_instance
   ```

2. **Function Signature Verification:**
   ```python
   # Check function signatures match expected patterns
   import inspect
   sig = inspect.signature(initialize_tracer_instance)
   ```

3. **Mock Strategy Validation:**
   ```python
   # Verify mock patterns work with actual dependencies
   from unittest.mock import Mock, patch
   ```

4. **Type Annotation Requirements:**
   ```python
   # All test methods must have return type annotations
   def test_example(self) -> None:
   ```

### **Approved Pylint Disables**
```python
# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name  
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior
```

### **Quality Enforcement Loop (Enhanced)**
1. Generate comprehensive unit tests with mocks
2. Execute metrics collection
3. Fix any quality issues (tests, coverage, Pylint, MyPy)
4. **Execute automated validation**: `python .agent-os/scripts/validate-test-quality.py --test-file [FILE]`
5. **Continue fixing until exit code 0** - No exceptions, no bypasses
6. Re-run validation until perfect scores achieved
7. Document final quality achievement with automated validation evidence

### **🚨 MANDATORY AUTOMATED VALIDATION**
**Phase 8 cannot be completed without:**
```bash
# REQUIRED: Must return exit code 0
python .agent-os/scripts/validate-test-quality.py --test-file [GENERATED_FILE]
echo "Exit code: $?"  # Must be 0
```

**Quality Gate Rules:**
- **100% test pass rate** confirmed by script
- **10.0/10 Pylint score** confirmed by script  
- **0 MyPy errors** confirmed by script
- **Black formatting** confirmed by script
- **No framework completion** without exit code 0
