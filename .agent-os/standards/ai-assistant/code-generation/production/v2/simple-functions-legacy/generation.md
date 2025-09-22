# Simple Functions - Generation Phase

## 🎯 **PHASE 4: CODE GENERATION FOR SIMPLE FUNCTIONS**

**Purpose**: Generate high-quality simple functions using proven templates.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, complete docstrings.

---

## 📋 **MANDATORY GENERATION COMMANDS**

### **Command 1: Select Template**
```bash
# AI MUST select appropriate template from templates.md
echo "Template selected: [TEMPLATE_NAME] from simple-functions/templates.md"
```

**Required Output:**
- Specific template name
- Template file reference
- Justification for template choice

### **Command 2: Generate Code**
```bash
# AI MUST generate code using selected template
echo "Code generated using template with customizations applied"
```

**Required Output:**
- Complete function implementation
- All template customizations applied
- Code ready for quality validation

---

## 🛠️ **PROVEN SIMPLE FUNCTION TEMPLATES**

**MANDATORY: Use existing proven templates from `templates.md`:**

### **📝 Available Templates:**
1. **Basic Validator Template** - Boolean validation functions
2. **String Formatter Template** - String manipulation and formatting
3. **Configuration Getter Template** - Environment/config value retrieval
4. **Data Converter Template** - Simple type conversions
5. **Utility Function Template** - General utility functions

### **🎯 Template Selection Criteria:**

| Function Type | Template | Use When |
|---------------|----------|----------|
| **Validation** | Basic Validator | Returns boolean, validates input |
| **Formatting** | String Formatter | Manipulates/formats strings |
| **Configuration** | Configuration Getter | Retrieves config/env values |
| **Conversion** | Data Converter | Converts between simple types |
| **Utility** | Utility Function | General purpose utility |

---

## 🔧 **GENERATION PROCESS**

### **Step 1: Template Customization**
**Apply these customizations to selected template:**

1. **Function Name**: Replace template name with actual function name
2. **Parameters**: Update parameter names and types
3. **Return Type**: Set correct return type annotation
4. **Docstring**: Customize docstring with actual description
5. **Implementation**: Adapt logic for specific requirements
6. **Imports**: Add only necessary imports

### **Step 2: Quality Integration**
**Ensure generated code includes:**

1. **Type Annotations**: 100% coverage
2. **Docstring**: Sphinx-compatible format
3. **Error Handling**: Appropriate for simple function
4. **Validation**: Input parameter validation
5. **Return**: Proper return value handling

### **Step 3: Code Verification**
**Verify generated code meets criteria:**

1. **Template Compliance**: Follows selected template structure
2. **Requirements Match**: Meets analysis phase requirements
3. **Quality Standards**: Ready for quality enforcement phase

---

## 📝 **GENERATION EXAMPLES**

### **Example 1: Email Validator (Basic Validator Template)**
```python
import re
from typing import Optional

def is_valid_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
        
    Raises:
        ValueError: If email is None or empty
        
    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))
```

### **Example 2: Display Name Formatter (String Formatter Template)**
```python
from typing import Optional

def format_display_name(
    first_name: str, 
    last_name: str, 
    *, 
    middle_initial: Optional[str] = None
) -> str:
    """Format user display name from name components.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        middle_initial: Optional middle initial
        
    Returns:
        Formatted display name string
        
    Raises:
        ValueError: If first_name or last_name is empty
        
    Example:
        >>> format_display_name("John", "Doe")
        "John Doe"
        >>> format_display_name("John", "Doe", middle_initial="M")
        "John M. Doe"
    """
    if not first_name or not isinstance(first_name, str):
        raise ValueError("First name must be a non-empty string")
    if not last_name or not isinstance(last_name, str):
        raise ValueError("Last name must be a non-empty string")
    
    first = first_name.strip()
    last = last_name.strip()
    
    if middle_initial and isinstance(middle_initial, str):
        middle = middle_initial.strip()
        if middle:
            return f"{first} {middle}. {last}"
    
    return f"{first} {last}"
```

---

## 🎯 **GENERATION QUALITY CHECKLIST**

### **✅ Template Compliance**
- [ ] **Template selected** from available templates
- [ ] **Template structure followed** correctly
- [ ] **All template sections customized** appropriately

### **✅ Code Quality**
- [ ] **Function name** follows naming conventions
- [ ] **Type annotations** on all parameters and return
- [ ] **Docstring** complete with args, returns, raises, example
- [ ] **Error handling** appropriate for simple function
- [ ] **Input validation** implemented correctly

### **✅ Requirements Compliance**
- [ ] **Function signature** matches analysis phase
- [ ] **Dependencies** match analysis (0-2 imports)
- [ ] **Validation requirements** implemented
- [ ] **Behavior** matches specified requirements

### **✅ Code Standards**
- [ ] **Import organization** follows project standards
- [ ] **Line length** within limits
- [ ] **Formatting** ready for Black
- [ ] **Naming** follows Python conventions

---

## 🚨 **GENERATION GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Template selected and justified
- Code generated using template
- All customizations applied correctly
- Quality checklist completed
- Code ready for quality enforcement

**❌ GATE FAILED IF:**
- No template used (code generated from scratch)
- Template not customized properly
- Quality standards not met
- Requirements not implemented

---

**💡 Key Principle**: Template-based generation ensures consistency, quality, and maintainability while reducing generation time and errors.
