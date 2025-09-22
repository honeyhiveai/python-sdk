# Simple Functions - Quality Core

## 🎯 **QUALITY ENFORCEMENT FOR SIMPLE FUNCTIONS**

**Purpose**: Essential quality enforcement for simple utility functions, validators, and formatters.

**Quality Targets**: 10.0/10 Pylint + 0 MyPy errors + 100% type annotations + complete docstrings

---

## 📋 **MANDATORY QUALITY COMMANDS**

### **Command 1: Pylint Validation (10.0/10)**
```bash
# MUST achieve perfect score
tox -e lint -- path/to/generated_function.py
```

**Required Output:**
- Pylint score: 10.0/10
- Zero violations reported
- Any disables must be justified

### **Command 2: MyPy Validation (0 errors)**
```bash
# MUST achieve zero errors
tox -e mypy -- path/to/generated_function.py
```

**Required Output:**
- MyPy errors: 0
- All type annotations validated
- No type: ignore comments needed

### **Command 3: Type Coverage (100%)**
```bash
# Verify complete type annotation coverage
echo "Type annotation coverage: 100% - all parameters and return types annotated"
```

**Required Output:**
- All function parameters typed
- Return type specified
- Optional/Union types used correctly

### **Command 4: Docstring Validation**
```bash
# Verify complete docstring coverage
echo "Docstring validation: Complete - includes args, returns, raises, example"
```

**Required Output:**
- Function purpose clearly described
- All parameters documented
- Return value documented
- Usage example provided

---

## 🎯 **SIMPLE FUNCTION QUALITY STANDARDS**

### **📊 Pylint Requirements (10.0/10)**

**Critical Rules for Simple Functions:**
- **C0103**: Invalid name (use descriptive, PEP 8 names)
- **C0116**: Missing function docstring
- **C0301**: Line too long (>88 characters)
- **R0913**: Too many arguments (max 5 for simple functions)
- **R0915**: Too many statements (max 15 for simple functions)

**Simple Function Specific:**
- **W0613**: Unused argument (remove or prefix with _)
- **R0911**: Too many return statements (max 6)
- **C0200**: Consider using enumerate (for index loops)

### **🔍 MyPy Requirements (0 errors)**

**Essential Type Checks:**
- **Function signature**: All parameters and return typed
- **Union types**: Use Union[] or | for multiple types
- **Optional types**: Use Optional[] or | None
- **Generic types**: Use TypeVar for generic functions

**Simple Function Examples:**
```python
from typing import Optional, Union, List

def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    return f"{amount:.2f} {currency}"

def safe_divide(a: float, b: float) -> Optional[float]:
    """Safely divide two numbers."""
    return a / b if b != 0 else None
```

### **📝 Docstring Requirements**

**Simple Function Docstring Template:**
```python
def process_data(data: List[str], filter_empty: bool = True) -> List[str]:
    """Process list of strings with optional filtering.
    
    Args:
        data: List of strings to process
        filter_empty: Whether to remove empty strings
        
    Returns:
        Processed list of strings
        
    Raises:
        ValueError: When data is None or invalid
        
    Example:
        >>> process_data(["hello", "", "world"], filter_empty=True)
        ["hello", "world"]
    """
```

---

## 🛡️ **VALIDATION ENFORCEMENT**

### **✅ Immediate Validation Checklist**

**After generating any simple function, MUST verify:**

- [ ] **Pylint Score**: Exactly 10.0/10
- [ ] **MyPy Errors**: Exactly 0
- [ ] **Type Coverage**: 100% of parameters and return
- [ ] **Docstring**: Complete with args, returns, example
- [ ] **Function Name**: Descriptive and PEP 8 compliant
- [ ] **Parameter Count**: ≤ 5 parameters
- [ ] **Function Length**: ≤ 15 statements
- [ ] **Single Responsibility**: One clear purpose

### **🚨 Blocking Issues for Simple Functions**

**These issues BLOCK function acceptance:**
- Any Pylint score < 10.0
- Any MyPy errors
- Missing type annotations
- Missing or incomplete docstring
- Function name not descriptive
- Too many parameters (>5)
- Function too complex (>15 statements)

---

## 🔗 **RELATED MODULES**

**For complete simple function implementation:**
- **📋 Simple Function Analysis** - Use existing `../simple-functions/analysis.md` (161 lines)
- **🔧 Simple Function Generation** - Use existing `../simple-functions/generation.md` (214 lines)
- **📄 Simple Function Templates** - Use existing `../simple-functions/templates.md` (75 lines)

**For framework integration:**
- **🎯 [Framework Core](../framework-core.md)** - Overall framework guidance (127 lines)
- **⚙️ Complexity Assessment** - Use existing `../complexity-assessment.md` (198 lines)

---

## 🎯 **SIMPLE FUNCTION QUALITY WORKFLOW**

### **Step 1: Generate Function**
- Follow simple-functions/generation.md patterns
- Use simple-functions/templates.md as base
- Keep function focused and single-purpose

### **Step 2: Immediate Validation**
- Run all mandatory quality commands
- Verify simple function quality standards
- Check immediate validation checklist

### **Step 3: Integration**
- Ensure function fits within larger module
- Test with expected inputs/outputs
- Validate error handling

---

**💡 Key Principle**: Simple functions should be immediately readable, single-purpose, and require minimal mental overhead to understand and maintain.
