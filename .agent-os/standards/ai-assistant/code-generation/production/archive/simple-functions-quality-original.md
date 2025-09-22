# Simple Functions - Quality Enforcement

## 🎯 **PHASE 5: QUALITY ENFORCEMENT FOR SIMPLE FUNCTIONS**

**Purpose**: Ensure generated simple functions meet perfect quality standards.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, complete docstrings.

---

## 📋 **MANDATORY QUALITY COMMANDS**

### **Command 1: Pylint Validation**
```bash
# AI MUST run Pylint and achieve 10.0/10 score
tox -e lint -- path/to/generated_function.py
```

**Required Output:**
- Pylint score: 10.0/10
- Zero violations reported
- Any disables must be justified

### **Command 2: MyPy Validation**
```bash
# AI MUST run MyPy and achieve 0 errors
tox -e mypy -- path/to/generated_function.py
```

**Required Output:**
- MyPy errors: 0
- All type annotations validated
- No type: ignore comments needed

### **Command 3: Type Annotation Coverage**
```bash
# AI MUST verify 100% type annotation coverage
echo "Type annotation coverage: 100% - all parameters and return types annotated"
```

**Required Output:**
- All function parameters typed
- Return type specified
- Optional/Union types used correctly

### **Command 4: Docstring Validation**
```bash
# AI MUST verify complete docstring coverage
echo "Docstring validation: Complete - includes args, returns, raises, example"
```

**Required Output:**
- Function docstring present
- All parameters documented
- Return value documented
- Exceptions documented
- Usage example included

### **Command 5: Black Formatting**
```bash
# AI MUST run Black formatting
tox -e format -- path/to/generated_function.py
```

**Required Output:**
- Code formatted with Black
- No formatting changes needed
- Line length within limits

---

## 🎯 **SIMPLE FUNCTION QUALITY STANDARDS**

### **📊 Pylint Requirements (10.0/10)**
**Zero tolerance for these violations:**
- `C0103` - Invalid name
- `C0111` - Missing docstring
- `C0301` - Line too long
- `W0613` - Unused argument
- `R0903` - Too few public methods (not applicable to functions)

**Approved disables for simple functions (with justification):**
```python
# pylint: disable=too-few-public-methods  # Not applicable to functions
```

### **🔍 MyPy Requirements (0 errors)**
**Perfect type safety required:**
- All parameters must have type annotations
- Return type must be specified
- No `Any` types unless absolutely necessary
- No `type: ignore` comments

**Example of perfect typing:**
```python
from typing import Optional, Union

def process_value(
    value: Union[str, int], 
    default: Optional[str] = None
) -> str:
    """Process value with proper typing."""
    # Implementation
```

### **📝 Docstring Requirements (Sphinx-compatible)**
**Required sections for simple functions:**
```python
def example_function(param1: str, param2: int) -> bool:
    """One-line summary of function purpose.
    
    Longer description if needed (optional for simple functions).
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When parameter validation fails
        TypeError: When parameter types are incorrect
        
    Example:
        >>> example_function("test", 42)
        True
    """
```

### **🎨 Code Style Requirements**
**Black formatting compliance:**
- Line length: 88 characters maximum
- Proper import organization
- Consistent indentation
- Trailing commas where appropriate

---

## 🔧 **QUALITY ISSUE FIXES**

### **Common Pylint Issues & Solutions**

#### **C0103: Invalid Name**
```python
# ❌ BAD
def validateEmail(email):
    pass

# ✅ GOOD  
def validate_email(email: str) -> bool:
    pass
```

#### **C0111: Missing Docstring**
```python
# ❌ BAD
def format_name(first, last):
    return f"{first} {last}"

# ✅ GOOD
def format_name(first: str, last: str) -> str:
    """Format first and last name into display name.
    
    Args:
        first: First name
        last: Last name
        
    Returns:
        Formatted display name
    """
    return f"{first} {last}"
```

#### **W0613: Unused Argument**
```python
# ❌ BAD
def process_data(data, unused_param):
    return data.upper()

# ✅ GOOD - Remove unused parameter
def process_data(data: str) -> str:
    return data.upper()

# ✅ ALTERNATIVE - Use parameter or mark as intentionally unused
def process_data(data: str, _context: Optional[str] = None) -> str:
    return data.upper()
```

### **Common MyPy Issues & Solutions**

#### **Missing Type Annotations**
```python
# ❌ BAD
def calculate_total(items):
    return sum(item.price for item in items)

# ✅ GOOD
from typing import List, Protocol

class Item(Protocol):
    price: float

def calculate_total(items: List[Item]) -> float:
    return sum(item.price for item in items)
```

#### **Incorrect Return Type**
```python
# ❌ BAD - MyPy can't infer Optional return
def find_user(user_id):
    if user_id in users:
        return users[user_id]
    return None

# ✅ GOOD
from typing import Optional

def find_user(user_id: str) -> Optional[User]:
    if user_id in users:
        return users[user_id]
    return None
```

---

## 📊 **QUALITY VALIDATION CHECKLIST**

### **✅ Pylint Validation**
- [ ] **Score achieved**: 10.0/10
- [ ] **No violations**: All Pylint rules satisfied
- [ ] **Justified disables**: Any disables have clear justification
- [ ] **Naming conventions**: All names follow Python standards

### **✅ MyPy Validation**
- [ ] **Zero errors**: No MyPy errors reported
- [ ] **Complete typing**: All parameters and returns typed
- [ ] **Proper imports**: All typing imports included
- [ ] **No type ignores**: No `type: ignore` comments needed

### **✅ Docstring Validation**
- [ ] **Function docstring**: Present and complete
- [ ] **Parameter docs**: All parameters documented
- [ ] **Return docs**: Return value documented
- [ ] **Exception docs**: All raised exceptions documented
- [ ] **Usage example**: At least one example provided

### **✅ Code Style Validation**
- [ ] **Black formatted**: Code passes Black formatting
- [ ] **Import organization**: Imports properly organized
- [ ] **Line length**: All lines within 88 character limit
- [ ] **Consistent style**: Follows project conventions

### **✅ Functional Validation**
- [ ] **Requirements met**: Function meets analysis requirements
- [ ] **Edge cases handled**: Appropriate error handling
- [ ] **Input validation**: Parameters validated correctly
- [ ] **Return handling**: Return values handled properly

---

## 🚨 **QUALITY GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Pylint score: 10.0/10
- MyPy errors: 0
- Type annotation coverage: 100%
- Docstring coverage: Complete
- Black formatting: Clean
- All quality checklist items verified

**❌ GATE FAILED IF:**
- Any quality metric below target
- Unresolved linting issues
- Missing or incomplete documentation
- Code style violations

---

## 🎯 **QUALITY ENFORCEMENT EXAMPLES**

### **Perfect Simple Function Example**
```python
import re
from typing import Optional

def validate_email_format(
    email: str, 
    *, 
    allow_empty: bool = False
) -> bool:
    """Validate email address format using regex.
    
    Validates email format according to basic RFC standards.
    Does not verify email deliverability.
    
    Args:
        email: Email address to validate
        allow_empty: Whether to allow empty email strings
        
    Returns:
        True if email format is valid, False otherwise
        
    Raises:
        TypeError: If email is not a string
        ValueError: If email is empty and allow_empty is False
        
    Example:
        >>> validate_email_format("user@example.com")
        True
        >>> validate_email_format("invalid-email")
        False
        >>> validate_email_format("", allow_empty=True)
        True
    """
    if not isinstance(email, str):
        raise TypeError("Email must be a string")
    
    if not email and not allow_empty:
        raise ValueError("Email cannot be empty when allow_empty=False")
    
    if not email:
        return allow_empty
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))
```

**Quality Metrics:**
- ✅ Pylint: 10.0/10
- ✅ MyPy: 0 errors  
- ✅ Type annotations: 100%
- ✅ Docstring: Complete
- ✅ Black: Formatted

---

**💡 Key Principle**: Perfect quality standards for simple functions establish the foundation for maintainable, reliable code that requires no post-generation fixes.
