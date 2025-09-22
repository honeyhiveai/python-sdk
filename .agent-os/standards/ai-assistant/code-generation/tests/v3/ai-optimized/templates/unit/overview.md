# Unit Test Template - Overview

**🎯 AI Template for Unit Tests with Mock Everything Strategy**

🛑 VALIDATE-GATE: Unit Template Overview Entry Requirements
- [ ] Unit test mock everything strategy understood ✅/❌
- [ ] Template usage commitment confirmed ✅/❌
- [ ] Complete isolation requirement acknowledged ✅/❌

🚨 FRAMEWORK-VIOLATION: If using real dependencies in unit tests or mixing with integration patterns

## 🛑 **UNIT TEST PRINCIPLES EXECUTION**

⚠️ MUST-READ: Unit tests require complete mocking - no real dependencies allowed

### **Mock Everything Strategy**
- **External Dependencies**: Mock all imports, APIs, databases
- **Internal Dependencies**: Mock all other modules and classes  
- **Test Interfaces**: Test behavior, not implementation
- **Complete Isolation**: Each test runs independently

## 🔧 **REQUIRED FIXTURES**

### **Standard Fixtures (from conftest.py)**
```python
def test_function(
    self,
    mock_tracer_base: Mock,      # Complete mock tracer
    mock_safe_log: Mock,         # Standard logging mock
    mock_client: Mock,           # API client mock
    standard_mock_responses: Dict # Predefined responses
) -> None:
```

## 🏗️ **BASIC STRUCTURE**

```python
"""Unit tests for [MODULE_NAME].

Complete isolation via mocking for fast, deterministic tests.
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
    
    # Test methods here...
```

## 🔗 **DETAILED PATTERNS**

- **Class Structure**: [unit/class-structure.md](class-structure.md)
- **Mock Patterns**: [unit/mock-patterns.md](mock-patterns.md)  
- **Assertion Examples**: [../assertions/unit-assertions.md](../assertions/unit-assertions.md)
- **Fixture Usage**: [../fixtures/unit-fixtures.md](../fixtures/unit-fixtures.md)

---

**🎯 Use this overview for quick reference, then follow detailed pattern files for complete implementation.**
