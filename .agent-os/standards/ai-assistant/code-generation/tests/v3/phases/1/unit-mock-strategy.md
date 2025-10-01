# Phase 1: Unit Mock Strategy

**🎯 Complete Isolation via Mock Configuration**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Unit Mock Strategy Prerequisites
- [ ] All shared analysis completed (Tasks 1.1-1.4) with evidence ✅/❌
- [ ] Unit test path selected and locked (no integration mixing) ✅/❌
- [ ] Phase 1.4 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If integration path selected - cannot proceed with unit strategy

## 🛑 **UNIT MOCK STRATEGY DEFINITION**

⚠️ MUST-COMPLETE: Define complete mock strategy based on shared analysis
📊 COUNT-AND-DOCUMENT: External dependencies requiring mocks: [NUMBER from import analysis]
📊 COUNT-AND-DOCUMENT: Attributes requiring mock configuration: [NUMBER from attribute analysis]
📊 COUNT-AND-DOCUMENT: Methods requiring return value mocks: [NUMBER from AST analysis]

## 📋 **MOCK CONFIGURATION STRATEGY**

### **Using Shared Analysis Results**
```python
# Based on AST analysis: Configure mock for each function signature
# Based on attributes: Setup mock attributes for each access pattern
# Based on imports: Mock all external dependencies
# Based on fixtures: Use standard mock_tracer_base, mock_safe_log

def test_function(
    self,
    mock_tracer_base: Mock,
    mock_safe_log: Mock,
    standard_mock_responses: Dict
) -> None:
    # Configure mock attributes (from attribute analysis)
    mock_tracer_base.config.api_key = "test-key"
    mock_tracer_base._initialized = False
    mock_tracer_base.session_id = "test-session-123"
    
    # Configure method returns (from method analysis)
    mock_tracer_base.start_span.return_value = Mock()
    
    # Execute with complete isolation
    result = function_under_test(mock_tracer_base)
    
    # Verify mock interactions
    assert result is not None
    mock_safe_log.assert_called()
```

### **External Dependency Mocking**
```python
# Mock all external imports (from import analysis)
@patch('opentelemetry.trace.get_tracer')
@patch('honeyhive.utils.logger.safe_log')
@patch('os.environ.get')
def test_with_external_mocks(mock_env, mock_safe_log, mock_tracer):
    # Complete isolation achieved
```

### **Pylint Disables** (Archive Standard)
```python
# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive test coverage requires extensive test cases, testing private methods
# requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and mock patch decorators create unavoidable long lines.
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 QUANTIFY-RESULTS: All dependencies mocked: [YES/NO with count verification]
📊 QUANTIFY-RESULTS: Standard fixtures used: [YES/NO with fixture list]
📊 QUANTIFY-RESULTS: Complete isolation achieved: [YES/NO with validation]
⚠️ EVIDENCE-REQUIRED: Mock strategy documented with specific counts from analysis

## 🛑 **VALIDATION GATE: UNIT MOCK STRATEGY COMPLETE**
🛑 VALIDATE-GATE: Unit Mock Strategy Evidence
- [ ] All external dependencies have mock strategy (count matches import analysis) ✅/❌
- [ ] All attributes configured in mock objects (count matches attribute analysis) ✅/❌
- [ ] Standard fixtures integrated correctly (fixtures verified) ✅/❌
- [ ] Complete isolation verified (no real API calls planned) ✅/❌
- [ ] Pylint disables documented with justifications ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete unit mock strategy

---

## 🚨 **COMMON AI MISINTERPRETATIONS (AVOID THESE)**

### **Misinterpretation 1: "Mock All Methods to Achieve Isolation"**
**❌ What AI Often Thinks**: Mock every method, including internal ones, for complete isolation

**✅ Correct Understanding**: Mock only EXTERNAL dependencies. Internal methods of the class under test should execute normally to achieve coverage.

**Why It Matters**:
```python
# ❌ WRONG - This achieves 0% coverage of internal methods
@patch.object(ProviderCompiler, '_generate_extraction_function')
def test_compile(mock_generate):
    compiler.compile()  # Internal method mocked → no coverage

# ✅ CORRECT - This achieves 95% coverage
@patch('yaml.safe_load')  # Mock external dependency only
def test_compile(mock_yaml):
    compiler.compile()  # Internal methods execute → full coverage
```

### **Misinterpretation 2: "External = Third-Party Libraries Only"**
**❌ What AI Often Thinks**: Only mock `requests`, `os`, etc. Everything else is internal

**✅ Correct Understanding**: External = anything the class/function DEPENDS ON (third-party libraries + other project modules + I/O operations)

**Classification**:
```python
# External (MOCK THESE):
import yaml  # ✅ Third-party library
import logging  # ✅ Standard library with side effects
from honeyhive.utils.logger import safe_log  # ✅ Other project module
from pathlib import Path  # ✅ I/O operations

# Internal (DON'T MOCK):
class ProviderCompiler:  # ❌ Class being tested
    def _internal_method(self):  # ❌ Method of class under test
    def _another_internal(self):  # ❌ Another internal method
```

### **Misinterpretation 3: "Complete Isolation = Mock Everything"**
**❌ What AI Often Thinks**: True isolation means mocking all function/method calls

**✅ Correct Understanding**: Isolation means the test doesn't depend on external services/files/state. Internal code execution is required for coverage.

**Isolation Definition**:
- ✅ Mock external API calls (requests.post)
- ✅ Mock file system operations (Path.exists)
- ✅ Mock environment variables (os.getenv)
- ❌ Don't mock the code you're trying to test
- ❌ Don't mock helper methods of the same class

---

🛑 UPDATE-TABLE: Phase 1.5 → Unit mock strategy complete with evidence
🎯 NEXT-MANDATORY: [integration-real-strategy.md](integration-real-strategy.md)
