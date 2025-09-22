# Unit Test Analysis - Phases 1-6

## 🎯 **PURPOSE**

Complete comprehensive analysis phases 1-6 with **unit test focus** (mocking, isolation, coverage).

**Previous**: [Phase 0 Setup](phase-0-setup.md) → Unit Test Path chosen  
**Next**: [Unit Test Generation](unit-test-generation.md)

---

# 📋 **PHASE 1: METHOD VERIFICATION (UNIT FOCUS)**

## 🔍 **DEEP ANALYSIS OF PRODUCTION CODE**

### 🚨 **MANDATORY ANALYSIS COMMANDS**

```bash
# 1. List all classes and methods with line numbers
grep -n "^class\|^def\|^    def" [PRODUCTION_FILE]
# Expected: Complete inventory of all testable units

# 2. Extract method signatures and docstrings
python -c "import ast, inspect; [print(f'{node.name}: {ast.get_docstring(node)}') for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]"
# Expected: Method signatures with documentation

# 3. Identify public vs private methods (unit test focus)
grep -E "^    def [^_]|^def [^_]" [PRODUCTION_FILE]
# Expected: Public methods that require comprehensive unit testing
```

### 📊 **UNIT TEST ANALYSIS REQUIREMENTS**

**MUST DOCUMENT FOR UNIT TESTING:**
- **All public methods** with exact signatures (primary test targets)
- **All classes** with initialization parameters (constructor testing)
- **All module-level functions** and their parameters (function testing)
- **Complex private methods** that affect public behavior (indirect testing)
- **Property methods** and their getter/setter logic (property testing)

### 🧪 **EMBEDDED UNIT TEST STANDARDS**

#### **🔒 Test Isolation (CRITICAL)**
- **Mock ALL External Dependencies**: requests, os, sys, time, external APIs
- **No Shared State**: Each test completely independent
- **Clean Fixtures**: Group by scope, clear naming (`mock_session`, `sample_data`)
- **Teardown**: Proper cleanup after each test

#### **📊 Coverage Requirements**
- **Target**: 90%+ line coverage (non-negotiable for unit tests)
- **Branch Coverage**: Test all if/else, try/except paths
- **Edge Cases**: Boundary values, None inputs, empty collections
- **Error Paths**: Exception scenarios with proper mocking

#### **🎭 Mock Patterns (MyPy Compatible)**
```python
# ✅ CORRECT: Use patch.object
with patch.object(target_object, 'method_name') as mock_method:
    mock_method.return_value = expected_value

# ✅ CORRECT: PropertyMock for properties
with patch.object(ClassName, 'property_name', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = expected_value

# ❌ WRONG: Avoid Mock(spec=Class) - causes MyPy issues
```

#### **🏷️ Approved Pylint Disables**
```python
# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name  
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior
```

### **🛠️ Proven Unit Test Fixtures (Use These)**
```python
# ✅ IMPORT PROVEN FIXTURES: Use existing unit test fixtures
# Standard fixtures from tests/unit/conftest.py
def test_example(honeyhive_client, honeyhive_tracer, mock_tracer_base, mock_safe_log) -> None:
    """Example using proven unit test fixtures."""
    
# ✅ STANDARD UNIT TEST FIXTURES:
# - honeyhive_client: HoneyHive client in test mode
# - honeyhive_tracer: HoneyHive tracer in test mode with HTTP tracing disabled
# - fresh_honeyhive_tracer: Fresh tracer instance for isolation
# - mock_client: Mock HoneyHive client for full mocking
# - mock_tracer: Mock HoneyHive tracer with context manager support
# - mock_tracer_base: Comprehensive mock tracer with all standard attributes
# - mock_safe_log: Standard mock for safe_log function
# - mock_response: Mock HTTP response (status_code=200, json={"success": True})
# - standard_mock_responses: Dict of standard mock responses for common scenarios

# ✅ STANDARD MOCK PATTERNS: Use proven mocking approaches
from unittest.mock import Mock, patch

# Mock external dependencies
@patch.object(requests, 'post')
def test_api_call(mock_post: Mock, honeyhive_client) -> None:
    """Test API call with mocked requests."""
    mock_post.return_value.json.return_value = {"event_id": "test-123"}
    
    result = honeyhive_client.events.create_event(event_data)
    assert result.event_id == "test-123"
    mock_post.assert_called_once()

# Mock internal components
def test_tracer_operations(mock_tracer_base, mock_safe_log) -> None:
    """Test tracer operations with comprehensive mocking."""
    # mock_tracer_base provides all standard tracer attributes
    assert mock_tracer_base.is_initialized is True
    assert mock_tracer_base.project_name == "test-project"
    
    # Test safe_log functionality
    mock_tracer_base._safe_log("info", "test message", {"key": "value"})
    mock_tracer_base._logger.log.assert_called_once()
```

**📚 Advanced Unit Patterns**: [Unit Testing Standards](../../testing/unit-testing-standards.md)

**🚨 CHECKPOINT GATE: Must have complete method inventory for unit test planning.**

### 🎯 **MANDATORY PHASE 1 COMPLETION**

**🛑 CRITICAL: You MUST update the progress table in chat window before proceeding to Phase 2.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|---------|
| 1: Method Verification | ✅ | Found X methods (Y public, Z private), A imports (B external, C internal), D classes verified with __init__ methods | 3/3 | ✅ |
```

**🚨 ENFORCEMENT**: If you proceed to Phase 2 without showing this table update, you are violating the framework contract.

**❌ VIOLATION INDICATORS:**
- "Phase 1 complete" without showing updated table
- "Moving to Phase 2" without table update  
- "Method analysis finished" without table evidence
- Creating/modifying files with table instead of chat window

**🛑 VIOLATION RESPONSE**: "STOP - You completed Phase 1 but didn't update the progress table. Show me the updated table in the chat window with Phase 1 marked as ✅ and evidence documented before proceeding to Phase 2."

---

# 🔍 **PHASE 2: LOGGING ANALYSIS (UNIT FOCUS)**

## 📝 **UNDERSTAND LOGGING FOR MOCKING**

### 🚨 **MANDATORY ANALYSIS COMMANDS**

```bash
# 1. Find all logging calls (will need mocking)
grep -n "log\." [PRODUCTION_FILE]
# Expected: All logger.debug, logger.info, logger.warning, logger.error calls

# 2. Identify logging imports and setup (mock targets)
grep -n "import.*log\|from.*log\|getLogger\|basicConfig" [PRODUCTION_FILE]
# Expected: How logging is configured and imported

# 3. Find safe_log usage (project-specific logging utility to mock)
grep -n "safe_log" [PRODUCTION_FILE]
# Expected: Usage of centralized logging utility
```

### 📊 **UNIT TEST LOGGING REQUIREMENTS**

**MUST DOCUMENT FOR UNIT TESTING:**
- **All logging calls** (will be mocked to verify correct messages)
- **Logging levels used** (debug, info, warning, error) for assertion testing
- **Safe_log integration** (mock strategy for multi-instance safe logging)
- **Error logging patterns** (verify errors are logged correctly)
- **Conditional logging** (test different logging paths)

**🚨 CHECKPOINT GATE: Must understand all logging for comprehensive mocking.**

### 🎯 **MANDATORY PHASE 2 COMPLETION**

**🛑 CRITICAL: You MUST update the progress table in chat window before proceeding to Phase 3.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|---------|
| 2: Logging Analysis | ✅ | Found X safe_log calls (Y debug, Z info, A error), B conditional branches analyzed in error paths | 3/3 | ✅ |
```

**🚨 ENFORCEMENT**: If you proceed to Phase 3 without showing this table update, you are violating the framework contract.

**❌ VIOLATION INDICATORS:**
- "Phase 2 complete" without showing updated table
- "Moving to Phase 3" without table update
- "Logging analysis finished" without table evidence
- "Found logging calls" without specific counts and evidence

**🛑 VIOLATION RESPONSE**: "STOP - You completed Phase 2 but didn't update the progress table. Show me the updated table in the chat window with Phase 2 marked as ✅ and evidence documented before proceeding to Phase 3."

---

# 🔗 **PHASE 3: DEPENDENCY ANALYSIS (MOCKING FOCUS)**

## 📦 **MAP ALL DEPENDENCIES FOR MOCKING**

### 🚨 **MANDATORY ANALYSIS COMMANDS**

```bash
# 1. Extract all imports (everything to potentially mock)
grep -E "^import |^from " [PRODUCTION_FILE]
# Expected: Complete list of all dependencies

# 2. Find external library usage (primary mock targets)
grep -E "requests\.|urllib\.|json\.|os\.|sys\.|time\." [PRODUCTION_FILE]
# Expected: All external library method calls

# 3. Identify internal project imports (mock for isolation)
grep -E "from honeyhive|import honeyhive" [PRODUCTION_FILE]
# Expected: Internal dependencies that need mocking

# 4. Find configuration dependencies (mock for test control)
grep -E "config\.|settings\.|env\.|getenv" [PRODUCTION_FILE]
# Expected: Configuration and environment dependencies
```

### 📊 **UNIT TEST MOCKING REQUIREMENTS**

**MUST DOCUMENT FOR COMPREHENSIVE MOCKING:**
- **Standard library imports** (os, sys, json, etc.) - Mock when used
- **Third-party libraries** (requests, pydantic, etc.) - Always mock
- **Internal project modules** (honeyhive.* imports) - Mock for isolation
- **Configuration dependencies** - Mock for test control
- **Mock strategies** (patch.object vs patch, return values, side effects)

**CRITICAL UNIT TEST PRINCIPLE:** Mock ALL external dependencies for true isolation.

**🚨 CHECKPOINT GATE: Must have complete mocking strategy before proceeding.**

### 🎯 **MANDATORY PHASE 3 COMPLETION**

**🛑 CRITICAL: You MUST update the progress table in chat window before proceeding to Phase 4.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|---------|
| 3: Dependency Analysis | ✅ | Analyzed X external deps (requests, json, os), Y internal imports mapped (tracer.core, utils.logger) | 4/4 | ✅ |
```

**🚨 ENFORCEMENT**: If you proceed to Phase 4 without showing this table update, you are violating the framework contract.

**❌ VIOLATION INDICATORS:**
- "Phase 3 complete" without showing updated table
- "Moving to Phase 4" without table update
- "Dependencies analyzed" without specific counts and names
- "Mocking strategy complete" without table evidence

**🛑 VIOLATION RESPONSE**: "STOP - You completed Phase 3 but didn't update the progress table. Show me the updated table in the chat window with Phase 3 marked as ✅ and evidence documented before proceeding to Phase 4."

---

# 🔄 **PHASE 4: USAGE PATTERN ANALYSIS (ISOLATION FOCUS)**

## 🎯 **UNDERSTAND USAGE FOR ISOLATED TESTING**

### 🚨 **MANDATORY ANALYSIS COMMANDS**

```bash
# 1. Find usage in other modules (understand integration points to mock)
grep -r "from.*[MODULE_NAME]\|import.*[MODULE_NAME]" src/ --include="*.py"
# Expected: How this module is imported and used elsewhere

# 2. Find instantiation patterns (for constructor testing)
grep -r "[CLASS_NAME](" src/ --include="*.py" | head -10
# Expected: How classes are instantiated in practice

# 3. Find method call patterns (for method testing)
grep -r "\.[METHOD_NAME](" src/ --include="*.py" | head -10
# Expected: How methods are called in real usage
```

### 📊 **UNIT TEST USAGE REQUIREMENTS**

**MUST DOCUMENT FOR ISOLATED TESTING:**
- **Common instantiation patterns** (constructor parameter combinations)
- **Typical method call sequences** (test method interactions)
- **Error handling patterns** (test exception scenarios)
- **Integration boundaries** (what to mock at module edges)
- **Configuration patterns** (test different config scenarios)

**UNIT TEST FOCUS:** Understand real usage to create realistic isolated tests.

**🚨 CHECKPOINT GATE: Must understand usage patterns for comprehensive unit testing.**

### 🎯 **MANDATORY PHASE 4 COMPLETION**

**🛑 CRITICAL: You MUST update the progress table in chat window before proceeding to Phase 5.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|---------|
| 4: Usage Patterns | ✅ | Found X usage patterns: error handling in Y locations, validation in Z methods, API calls use retry logic | 3/3 | ✅ |
```

**🚨 ENFORCEMENT**: If you proceed to Phase 5 without showing this table update, you are violating the framework contract.

**❌ VIOLATION INDICATORS:**
- "Phase 4 complete" without showing updated table
- "Moving to Phase 5" without table update
- "Usage patterns found" without specific counts and details
- "Pattern analysis finished" without table evidence

**🛑 VIOLATION RESPONSE**: "STOP - You completed Phase 4 but didn't update the progress table. Show me the updated table in the chat window with Phase 4 marked as ✅ and evidence documented before proceeding to Phase 5."

---

# 📊 **PHASE 5: COVERAGE ANALYSIS (90%+ TARGET)**

## 🎯 **PLAN COMPREHENSIVE UNIT TEST COVERAGE**

### 🚨 **MANDATORY ANALYSIS COMMANDS**

```bash
# 1. Run existing coverage analysis
tox -e unit -- --cov=[MODULE_PATH] --cov-report=term-missing
# Expected: Current coverage baseline and missing lines

# 2. Identify complex code paths requiring unit tests
python -c "import ast; print([f'{node.lineno}: {node.name}' for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With))])"
# Expected: All conditional and loop constructs that need coverage
```

### 📊 **UNIT TEST COVERAGE PLANNING**

**MUST PLAN UNIT TESTS FOR 90%+ COVERAGE:**
- **Happy path scenarios** (normal operation with mocked dependencies)
- **Error conditions** (exceptions, invalid inputs with proper mocking)
- **Edge cases** (boundary values, empty inputs, None values)
- **Configuration variations** (different settings via mocked config)
- **All conditional branches** (if/else, try/except, loops)
- **All method combinations** (different parameter combinations)

**UNIT TEST COVERAGE TARGET:** 90%+ line coverage with comprehensive mocking.

**🚨 CHECKPOINT GATE: Must have 90%+ coverage plan before generation.**

### 🎯 **MANDATORY PHASE 5 COMPLETION**

**🛑 CRITICAL: You MUST update the progress table in chat window before proceeding to Phase 6.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|---------|
| 5: Coverage Analysis | ✅ | Target: 90%+ coverage, X methods (Y public, Z private), A branches planned (B error paths, C validation branches, D business logic) | 2/2 | ✅ |
```

**🚨 ENFORCEMENT**: If you proceed to Phase 6 without showing this table update, you are violating the framework contract.

**❌ VIOLATION INDICATORS:**
- "Phase 5 complete" without showing updated table
- "Moving to Phase 6" without table update
- "Coverage planning complete" without specific method/branch counts
- "90% target set" without table evidence

**🛑 VIOLATION RESPONSE**: "STOP - You completed Phase 5 but didn't update the progress table. Show me the updated table in the chat window with Phase 5 marked as ✅ and evidence documented before proceeding to Phase 6."

---

# 🔍 **PHASE 6: PRE-GENERATION LINTING (UNIT FOCUS)**

## 🚨 **PROACTIVE QUALITY PLANNING FOR UNIT TESTS**

### 🚨 **MANDATORY VALIDATION COMMANDS**

```bash
# 1. Check current linting status of production code
tox -e lint -- [PRODUCTION_FILE]
# Expected: Current Pylint score and any existing issues

# 2. Validate Black formatting of production code
black --check [PRODUCTION_FILE]
# Expected: Confirm production code formatting is clean

# 3. Check MyPy status of production code
tox -e mypy -- [PRODUCTION_FILE]
# Expected: Current type checking status

# 4. Review linter-specific documentation for unit tests
find .agent-os/standards/ai-assistant/code-generation/linters/ -name "*.md"
# Expected: All linter documentation has been read
```

### 📋 **UNIT TEST PRE-GENERATION PLANNING**

**MUST PLAN FOR UNIT TEST QUALITY:**
- **Import organization** (all imports at top, grouped: standard, third-party, local)
- **Mock patterns** (use `patch.object`, avoid `Mock(spec=Class)` for MyPy compatibility)
- **Type annotations** (minimal for test functions, proper for fixtures)
- **Line length management** (Black will handle, but plan for descriptive test names)
- **Pylint disables** (justified only: `too-many-lines`, `redefined-outer-name` for fixtures)

**UNIT TEST SPECIFIC CONSIDERATIONS:**
- **Mock imports** (from unittest.mock import patch, MagicMock, PropertyMock)
- **Fixture organization** (group related fixtures, clear naming)
- **Test isolation** (each test independent, no shared state)
- **Assertion patterns** (specific assertions, avoid generic assertTrue)

**🚨 CHECKPOINT GATE: Must have unit test quality plan before generation.**

---

## 🎯 **UNIT TEST ANALYSIS COMPLETION**

### **Before proceeding to generation, verify:**

**✅ Phase 1 Complete:** Method inventory with unit test focus
**✅ Phase 2 Complete:** Logging analysis with mocking strategy  
**✅ Phase 3 Complete:** Dependency analysis with comprehensive mocking plan
**✅ Phase 4 Complete:** Usage patterns with isolation focus
**✅ Phase 5 Complete:** Coverage analysis with 90%+ target plan
**✅ Phase 6 Complete:** Linting validation with unit test quality planning

**🎯 UPDATE PROGRESS TABLE:** Mark Phases 1-6 as complete (✅) in chat window.

**Next Step:** Proceed to **[Unit Test Generation](unit-test-generation.md)** with comprehensive analysis complete.
