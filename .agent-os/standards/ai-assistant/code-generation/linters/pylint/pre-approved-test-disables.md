# Pre-Approved Pylint Disables for Test Files

**🎯 Canonical list of approved Pylint disables for test file generation**

⚠️ MUST-READ: Use ONLY these approved disables without requesting permission
🚨 FRAMEWORK-VIOLATION: If applying disables not on this list without user approval

---

## ✅ **ALWAYS APPROVED - Standard Test File Header**

### **Mandatory Header for ALL Test Files**
```python
# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.
```

### **Justifications**:
| Disable | Reason | When Applied |
|---------|--------|--------------|
| `protected-access` | Testing requires access to protected methods (`self._method()`) | All test files with private method testing |
| `too-many-lines` | Comprehensive coverage requires extensive test cases | Test files >1000 lines |
| `redefined-outer-name` | Pytest fixtures are used as parameters (by design) | All test files using fixtures |
| `too-many-public-methods` | Comprehensive test classes need many test methods | Test classes with 20+ test methods |

---

## ✅ **APPROVED - Add as Needed with Inline Justification**

### **Test Method Specific**
```python
# pylint: disable=too-many-positional-arguments  
# Justification: Test methods with multiple mock fixtures

# pylint: disable=too-many-arguments
# Justification: Complex test setups requiring many fixtures
```

### **Test Class Specific**
```python
# pylint: disable=too-few-public-methods
# Justification: Test fixture/helper classes may have single method
```

### **Import Specific (Special Cases Only)**
```python
# pylint: disable=import-error
# Justification: config.dsl is separate package, not in src/

# Use ONLY when:
# - Testing cross-package imports
# - Module intentionally not in standard Python path
# - Pylint configuration cannot resolve the import
```

---

## ❌ **NEVER APPROVED - Fix the Issue Instead**

### **Import and Formatting Issues**
| Disable | Why Rejected | What to Do Instead |
|---------|--------------|-------------------|
| `wrong-import-position` | Violates import ordering standards | Fix import order to match isort configuration |
| `unused-import` | Indicates dead code | Remove the unused import |
| `unused-argument` | Violates Pythonic conventions | Use `_` prefix for unused parameters (e.g., `_mock_file`) |
| `line-too-long` | Should be handled by Black | Let Black formatter handle line length. File-level disable ONLY if absolutely unavoidable (e.g., `@patch` decorator with long `read_data` strings) |
| `missing-module-docstring` | Documentation is mandatory | Add proper module docstring |
| `invalid-name` | Violates naming conventions | Use proper snake_case naming |

### **Code Quality Issues**
| Disable | Why Rejected | What to Do Instead |
|---------|--------------|-------------------|
| `too-many-locals` | Indicates complex test | Break into smaller, focused tests |
| `too-many-branches` | Indicates complex logic | Simplify test or use parametrize |
| `duplicate-code` | Violates DRY principle | Extract common setup to fixtures |
| `fixme` / `todo` | Incomplete work | Complete the work or file issue |

---

## 🎯 **USAGE PATTERNS**

### **Pattern 1: Standard Test File**
```python
"""Unit tests for provider compiler.

This module follows Agent OS testing standards.
"""

# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
```

### **Pattern 2: Test with Unused Mock Parameters**
```python
@patch('module.external_dependency')
def test_function_with_mocks(
    self,
    _mock_external: Mock,  # Prefix with _ for unused parameters
    fixture_data: Dict[str, Any]
) -> None:
    """Test function behavior.
    
    Note: _mock_external is required for patching but not directly used in test.
    Use underscore prefix instead of pylint disable.
    """
    # Test implementation
```

### **Pattern 3: Cross-Package Import**
```python
# pylint: disable=import-error  # config.dsl is separate package, not in src/
from config.dsl.compiler import ProviderCompiler
```

---

## 📋 **DECISION CHECKLIST**

**Before applying ANY Pylint disable, verify:**

- [ ] Is it in the "Always Approved" list? → Use standard header
- [ ] Is it in the "Approved as Needed" list? → Add inline with justification
- [ ] Is it in the "Never Approved" list? → ❌ Fix the issue instead
- [ ] Is it NOT on any list? → ❌ Get user approval first

---

## 🚨 **REAL-WORLD EXAMPLE: test_compiler.py**

### **What Was Applied (All Approved)**
```python
# Line 1-6: Standard header
# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.

# Line 23: Cross-package import
# pylint: disable=import-error  # config.dsl is separate package, not in src/
```

### **What Was Requested and Approved**
```
User approved these additional disables for test files:
- too-many-positional-arguments (Test methods with many mocks)
- too-few-public-methods (Test fixture classes)
- too-many-arguments (Complex test setups)
```

### **What Was Explicitly Rejected**
```python
# ❌ User rejected these:
# pylint: disable=wrong-import-position
# Fix applied: Moved imports to top of file instead

# pylint: disable=unused-argument  
# Fix applied: Use _parameter_name prefix instead
```

---

## 🎯 **APPROVAL HISTORY**

### **Explicitly User-Approved Disables**
Date: 2025-09-29 (test_compiler.py generation)

**Approved**:
- `too-many-positional-arguments`
- `too-few-public-methods`
- `too-many-arguments`

**Rejected**:
- `wrong-import-position` - Must fix import order instead
- `unused-argument` - Use `_` prefix instead (2025-09-30)

---

🛑 VALIDATE-GATE: Pre-Approved Disables Understanding
- [ ] Standard header memorized ✅/❌
- [ ] Approved inline disables identified ✅/❌
- [ ] Never-approved disables understood ✅/❌
- [ ] Will request approval for anything not on this list ✅/❌

🎯 **This reference prevents unapproved Pylint disables and user intervention**