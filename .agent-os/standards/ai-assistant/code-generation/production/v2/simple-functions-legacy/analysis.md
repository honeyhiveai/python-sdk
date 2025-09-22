# Simple Functions - Analysis Phase

## 🎯 **PHASE 2: REQUIREMENTS ANALYSIS FOR SIMPLE FUNCTIONS**

**Purpose**: Gather complete requirements for simple function generation.

**Complexity Level**: Simple (single purpose, minimal dependencies, basic validation)

---

## 📋 **MANDATORY ANALYSIS COMMANDS**

### **Command 1: Define Function Purpose**
```bash
# AI MUST document the exact function purpose
echo "Function purpose: [EXACT DESCRIPTION]"
```

**Required Output:**
- Single, clear purpose statement
- Primary use case identification
- Expected behavior description

### **Command 2: Determine Function Signature**
```bash
# AI MUST define exact signature with types
echo "Function signature: def function_name(param1: Type1, param2: Type2) -> ReturnType:"
```

**Required Output:**
- Complete function name
- All parameters with type annotations
- Return type specification
- Optional parameters identified

### **Command 3: Identify Dependencies**
```bash
# AI MUST list all required imports
echo "Required imports: [LIST OF IMPORTS]"
```

**Required Output:**
- Standard library imports
- Third-party imports (should be minimal for simple functions)
- Internal project imports
- Total import count (target: 0-2 for simple functions)

### **Command 4: Plan Validation Requirements**
```bash
# AI MUST define validation needs
echo "Validation requirements: [SPECIFIC VALIDATIONS]"
```

**Required Output:**
- Parameter validation needs
- Input sanitization requirements
- Error conditions to handle
- Return value validation

---

## 🔍 **SIMPLE FUNCTION ANALYSIS CHECKLIST**

### **✅ Function Purpose Analysis**
- [ ] **Single responsibility confirmed** - Function has one clear purpose
- [ ] **Use case documented** - Primary use case clearly defined
- [ ] **Behavior specified** - Expected input/output behavior described

### **✅ Signature Analysis**
- [ ] **Function name chosen** - Descriptive, follows naming conventions
- [ ] **Parameters defined** - All parameters with appropriate types
- [ ] **Return type specified** - Clear return type annotation
- [ ] **Optional parameters handled** - Default values where appropriate

### **✅ Dependency Analysis**
- [ ] **Import count verified** - 0-2 imports maximum for simple functions
- [ ] **Standard library preferred** - Minimal external dependencies
- [ ] **Import necessity justified** - Each import serves a clear purpose

### **✅ Validation Analysis**
- [ ] **Input validation planned** - Parameter validation strategy defined
- [ ] **Error handling scoped** - Appropriate error handling for simple function
- [ ] **Edge cases identified** - Common edge cases documented

---

## 📊 **ANALYSIS EXAMPLES**

### **Example 1: Email Validator**
```python
# Function Purpose: Validate email address format using regex
# Function Signature: def is_valid_email(email: str) -> bool:
# Required Imports: import re
# Validation Requirements: 
#   - Check email is not None/empty
#   - Validate basic email format with regex
#   - Return boolean result
```

### **Example 2: String Formatter**
```python
# Function Purpose: Format user display name from first/last name
# Function Signature: def format_display_name(first_name: str, last_name: str, *, middle_initial: Optional[str] = None) -> str:
# Required Imports: from typing import Optional
# Validation Requirements:
#   - Check names are not None/empty
#   - Strip whitespace
#   - Handle optional middle initial
#   - Return formatted string
```

### **Example 3: Configuration Getter**
```python
# Function Purpose: Get configuration value with default fallback
# Function Signature: def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
# Required Imports: import os, from typing import Optional
# Validation Requirements:
#   - Check key is valid string
#   - Handle missing environment variables
#   - Return default if not found
```

---

## 🎯 **QUALITY REQUIREMENTS FOR SIMPLE FUNCTIONS**

### **📝 Documentation Requirements**
- **Docstring**: One-line summary + parameter descriptions
- **Examples**: At least one usage example in docstring
- **Type Hints**: 100% coverage for all parameters and return

### **🔧 Implementation Requirements**
- **Error Handling**: Basic parameter validation only
- **Logging**: Minimal or no logging (simple functions should be lightweight)
- **Performance**: Optimized for speed and simplicity

### **📊 Testing Requirements**
- **Unit Tests**: 90%+ coverage
- **Test Cases**: Happy path + edge cases + error conditions
- **Mock Usage**: Minimal mocking (simple functions should have few dependencies)

---

## 🚨 **ANALYSIS GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- All 4 mandatory commands executed with evidence
- Function confirmed as "simple" complexity level
- Complete requirements documented
- All checklist items verified
- Quality requirements understood

**❌ GATE FAILED IF:**
- Function requires 3+ imports (consider complex path)
- Multiple responsibilities identified (consider refactoring)
- Complex error handling needed (consider complex path)
- State management required (consider class path)

---

**💡 Key Principle**: Simple functions should do one thing well with minimal dependencies and straightforward validation.
