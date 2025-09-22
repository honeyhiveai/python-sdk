# Unit Test Generation Framework

## 🎯 **UNIT TEST SPECIFIC REQUIREMENTS**

**Purpose**: Generate comprehensive unit tests for individual modules with proper isolation.

---

## 📋 **MANDATORY FILE NAMING STANDARDS**

### **✅ CORRECT NAMING PATTERN**
```
tests/unit/test_[module_path]_[specific_file].py
```

**Examples:**
- `src/honeyhive/tracer/core/operations.py` → `test_tracer_core_operations.py`
- `src/honeyhive/utils/dotdict.py` → `test_utils_dotdict.py`
- `src/honeyhive/config/utils.py` → `test_config_utils.py`

### **❌ FORBIDDEN PATTERNS**
- `test_models_integration.py` - Too broad, tests entire module
- `test_honeyhive_tracer.py` - Too generic
- `test_integration_*.py` - Wrong test type (should be in integration/)

---

## 🚨 **TARGET VALIDATION FOR UNIT TESTS**

### **✅ VALID UNIT TEST TARGETS**
- **Single module files** with specific business logic
- **Utility classes** with methods to test
- **Configuration modules** with validation logic
- **Processing modules** with data transformation

### **❌ INVALID UNIT TEST TARGETS**
- **`__init__.py` files** - Only imports, no business logic
- **Entire module directories** - Too broad for unit tests
- **Integration points** - Should be integration tests
- **`conftest.py` files** - Pytest configuration

---

## 🎯 **UNIT TEST SCOPE REQUIREMENTS**

### **Single Module Focus**
```python
# CORRECT: Tests single specific module
# File: test_tracer_core_operations.py
# Target: src/honeyhive/tracer/core/operations.py

class TestSpanProcessor:
    """Test span processing functionality."""
    
class TestEventHandler:
    """Test event handling functionality."""
```

### **Mock External Dependencies**
```python
# CORRECT: Mock all external dependencies
@patch("honeyhive.tracer.core.operations.safe_log")
@patch("honeyhive.tracer.core.operations.get_tracer_registry")
def test_process_span_isolated(self, mock_registry: Mock, mock_log: Mock) -> None:
    """Test span processing in isolation."""
```

---

## 🔗 **INTEGRATION WITH TESTING STANDARDS**

**MANDATORY: Follow existing testing standards:**

### **File Structure Standards**
- **Reference**: [Unit Testing Standards](../../testing/unit-testing-standards.md)
- **Naming**: `test_[module_path]_[file].py` pattern
- **Organization**: Group by functionality, not alphabetically

### **🚨 MANDATORY FILE HEADER TEMPLATE**
```python
"""Unit tests for [MODULE_NAME].

This module contains comprehensive unit tests for [DESCRIPTION].
"""
# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name  
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import pytest
from unittest.mock import Mock, patch
# ... other imports
```

**🚨 CRITICAL**: ALL unit test files MUST start with these pre-approved pylint disables to prevent common violations.

### **Mock Standards**
- **Reference**: [Fixture and Patterns](../../testing/fixture-and-patterns.md)
- **Strategy**: Use `@patch.object` to avoid MyPy errors
- **Imports**: All imports at top level (never inside methods)

### **Quality Standards**
- **Reference**: Quality standards embedded in framework workflows
- **Pylint**: 10.0/10 score required
- **Coverage**: 90%+ for unit tests
- **MyPy**: 0 errors required

### **🛠️ Proven Unit Test Fixtures**
**MANDATORY: Use existing proven fixtures from `tests/unit/conftest.py`:**

```python
# ✅ IMPORT PROVEN FIXTURES: Standard unit test fixtures
def test_example(
    honeyhive_client,        # HoneyHive client in test mode
    honeyhive_tracer,        # HoneyHive tracer in test mode
    mock_tracer_base,        # Comprehensive mock tracer with all attributes
    mock_safe_log,           # Standard mock for safe_log function
    standard_mock_responses  # Dict of standard mock responses
) -> None:
    """Example using proven unit test fixtures."""
    
    # Use client for API testing
    assert honeyhive_client.api_key == "test-api-key-12345"
    
    # Use tracer for tracer component testing
    assert honeyhive_tracer.project_name == "test-project"
    
    # Use mock_tracer_base for comprehensive tracer mocking
    assert mock_tracer_base.is_initialized is True
    assert mock_tracer_base.project_name == "test-project"
    
    # Use standard responses for consistent mocking
    session_response = standard_mock_responses["session"]
    assert session_response["session_id"] == "session-test-123"

# ✅ AVAILABLE FIXTURES:
# Core Fixtures:
# - api_key: "test-api-key-12345"
# - project: "test-project" 
# - source: "test"
# - honeyhive_client: HoneyHive client in test mode
# - honeyhive_tracer: HoneyHive tracer in test mode with HTTP tracing disabled
# - fresh_honeyhive_tracer: Fresh tracer instance for complete isolation

# Mock Fixtures:
# - mock_client: Mock HoneyHive client for full mocking
# - mock_tracer: Mock HoneyHive tracer with context manager support
# - mock_tracer_base: Comprehensive mock tracer with all standard attributes
# - mock_safe_log: Standard mock for safe_log function
# - mock_response: Mock HTTP response (status_code=200, json={"success": True})
# - mock_async_response: Mock async HTTP response
# - standard_mock_responses: Dict of standard responses for all API endpoints

# Auto-Applied Fixtures:
# - reset_otel_state_for_test: Resets OpenTelemetry state between tests
# - disable_tracing_for_unit_tests: Disables tracing for performance/isolation
```

**Why Use These Fixtures:**
- **Proven Reliability**: Used across 70+ unit test files
- **Complete Isolation**: Automatic OTEL state reset and tracing disabled
- **Comprehensive Mocking**: `mock_tracer_base` includes all standard tracer attributes
- **Consistent Responses**: `standard_mock_responses` provides predictable API responses
- **Performance Optimized**: Auto-disabled tracing for faster test execution

**📚 Advanced Patterns**: [Fixture and Patterns](../../testing/fixture-and-patterns.md) - Parametrized tests, multiple patches, context managers, custom assertions

---

## 🚀 **UNIT TEST GENERATION WORKFLOW**

### **Phase 0C: Enhanced Target Validation**
```bash
# 1. Validate single module target (not directory)
basename "src/[MODULE_PATH].py"  # Must be specific .py file

# 2. Ensure not testing aggregated modules
echo "src/[MODULE_PATH].py" | grep -v "__init__.py\|conftest.py"

# 3. Verify business logic exists (>50 lines non-import)
grep -v "^import\|^from\|^#\|^$" "src/[MODULE_PATH].py" | wc -l

# 4. Check for classes/functions to test
grep -E "^class |^def " "src/[MODULE_PATH].py" | wc -l
```

### **Test File Naming Validation**
```bash
# Validate test file follows naming convention
echo "tests/unit/test_[MODULE_PATH_UNDERSCORED].py" | grep -E "test_[a-z_]+\.py$"

# Ensure not testing entire modules
echo "test_models_integration.py" | grep -v "integration\|module\|package"
```

---

## 📊 **UNIT TEST QUALITY TARGETS**

| Metric | Target | Enforcement |
|--------|--------|-------------|
| **Pass Rate** | 100% | Phase 8 mandatory |
| **Coverage** | 90%+ | Phase 8 mandatory |
| **Pylint Score** | 10.0/10 | Phase 8 mandatory |
| **MyPy Errors** | 0 | Phase 8 mandatory |
| **File Focus** | Single module | Phase 0C validation |

---

## 🔗 **NEXT STEPS**

**After unit test generation:**
1. **Integration Tests**: Use [Integration Test Generation](integration-test-generation.md)
2. **End-to-End Tests**: Use [E2E Test Generation](e2e-test-generation.md)
3. **Performance Tests**: Use [Performance Test Generation](performance-test-generation.md)

---

**🎯 Key Principle**: Unit tests focus on single modules in isolation with comprehensive mocking of dependencies.
