# Unit Test Template - Mock Everything Strategy

**🎯 AI Template for Generating Unit Tests with Complete Isolation**

⚠️ MUST-READ: Complete template before test generation
🛑 VALIDATE-GATE: Unit Template Understanding
- [ ] Mock everything strategy comprehended ✅/❌
- [ ] Standard fixtures identified and understood ✅/❌
- [ ] Template structure reviewed ✅/❌

## 📋 **UNIT TEST PRINCIPLES**

### **Mock Everything Strategy**
- **External Dependencies**: Mock all imports, APIs, databases
- **Internal Dependencies**: Mock all other modules and classes  
- **Test Interfaces**: Test behavior, not implementation
- **Complete Isolation**: Each test runs independently

## 🔧 **STANDARD FIXTURES (from conftest.py)**

### **Required Fixtures**
```python
# Use these fixtures from tests/unit/conftest.py
def test_function(
    self,
    mock_tracer_base: Mock,      # Complete mock tracer
    mock_safe_log: Mock,         # Standard logging mock
    mock_client: Mock,           # API client mock
    standard_mock_responses: Dict # Predefined responses
) -> None:
```

### **Fixture Usage Patterns**
```python
# Setup mock behavior
mock_tracer_base.project_name = "test-project"
mock_tracer_base.config.api_key = "test-key"
mock_tracer_base._initialized = False

# Configure mock responses
mock_client.post.return_value = standard_mock_responses["session"]
```

## 🏗️ **TEST CLASS TEMPLATE**

```python
"""Unit tests for [MODULE_NAME].

This module tests [MODULE_PURPOSE] with complete isolation via mocking.
All external dependencies are mocked to ensure fast, deterministic tests.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive test coverage requires extensive test cases, testing private methods
# requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and mock patch decorators create unavoidable long lines.

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from src.module.under.test import function_to_test


class Test[FunctionName]:
    """Test suite for [function_name] with complete mocking."""

    @patch("src.module.external_dependency")
    def test_[scenario]_success(
        self, 
        mock_external: Mock,
        mock_tracer_base: Mock,
        mock_safe_log: Mock
    ) -> None:
        """Test [scenario] succeeds with expected behavior."""
        # Setup mocks
        mock_external.return_value = "expected_result"
        
        # Execute function (test interface, not implementation)
        result = function_to_test(mock_tracer_base)
        
        # Verify behavior (not internal calls)
        assert result == "expected_result"
        mock_safe_log.assert_any_call(mock_tracer_base, "info", "Expected message")

    @patch("src.module.external_dependency")  
    def test_[scenario]_error_handling(
        self,
        mock_external: Mock,
        mock_tracer_base: Mock,
        mock_safe_log: Mock
    ) -> None:
        """Test [scenario] handles errors gracefully."""
        # Setup error condition
        mock_external.side_effect = Exception("Test error")
        
        # Execute and verify graceful handling
        result = function_to_test(mock_tracer_base)
        
        # Verify error handling behavior
        assert result is None  # or appropriate fallback
        mock_safe_log.assert_any_call(mock_tracer_base, "error", "Error handled")
```

## 🎯 **ASSERTION PATTERNS**

### **Behavior Verification**
```python
# Test return values (interfaces)
assert result == expected_value
assert result is not None
assert isinstance(result, ExpectedType)

# Test state changes (behavior)
assert mock_tracer_base._initialized is True
assert mock_tracer_base.session_id == "expected-id"
```

### **Mock Verification**
```python
# Verify function calls (behavior)
mock_external.assert_called_once_with(expected_args)
mock_safe_log.assert_any_call(tracer, "level", "message")

# Verify call counts
assert mock_external.call_count == 2
```

### **Error Handling Verification**
```python
# Test exception handling
with pytest.raises(ExpectedError, match="expected message"):
    function_to_test(invalid_input)

# Test graceful degradation  
result = function_to_test(error_condition)
assert result is None  # Graceful fallback
```

## 🚨 **CRITICAL REQUIREMENTS**

### **Must Use Standard Fixtures**
- ✅ Use `mock_tracer_base` from conftest.py
- ✅ Use `mock_safe_log` for logging
- ✅ Use `standard_mock_responses` for API responses
- ❌ Never create custom mock objects when standard fixtures exist

### **Must Mock Everything**
- ✅ Mock all external imports with `@patch`
- ✅ Mock all internal dependencies
- ✅ Mock all I/O operations (files, network, database)
- ❌ Never call real functions or services

### **Must Test Interfaces**
- ✅ Test function return values and behavior
- ✅ Test error handling and edge cases
- ✅ Test state changes and side effects
- ❌ Never test internal implementation details

---

**🎯 This template ensures generated unit tests use standard fixtures, maintain complete isolation, and test interfaces rather than implementation details.**
