# Classes - Quality Core

## 🎯 **QUALITY ENFORCEMENT OVERVIEW**

**Purpose**: Essential quality enforcement for generated classes with focus on immediate validation.

**Quality Targets**: 10.0/10 Pylint + 0 MyPy errors + 100% type annotations + comprehensive docstrings

---

## 🚨 **MANDATORY QUALITY COMMANDS**

### **Command 1: Pylint Validation (10.0/10)**
```bash
# MUST achieve perfect score
tox -e lint -- path/to/generated_class.py
```

**Required Output:**
- Pylint score: 10.0/10
- Zero violations
- Any disables justified with detailed comments

### **Command 2: MyPy Validation (0 errors)**
```bash
# MUST achieve zero errors
tox -e mypy -- path/to/generated_class.py
```

**Required Output:**
- MyPy errors: 0
- All type annotations validated
- No type: ignore comments needed

### **Command 3: Type Coverage (100%)**
```bash
# Verify complete type annotation coverage
echo "Type annotation coverage: 100% - all attributes, methods, properties typed"
```

**Required Output:**
- All class/instance attributes typed
- All method parameters and returns typed
- Property getters/setters properly typed

---

## 🎯 **CORE QUALITY STANDARDS**

### **📊 Pylint Requirements (10.0/10)**

**Critical Rules:**
- **C0103**: Invalid name (use descriptive, PEP 8 names)
- **C0115**: Missing class docstring
- **C0116**: Missing function/method docstring
- **R0903**: Too few public methods (justify or refactor)
- **R0913**: Too many arguments (use dataclasses/builders)

**Class-Specific Rules:**
- **R0902**: Too many instance attributes (max 7, use composition)
- **R0904**: Too many public methods (max 20, split responsibilities)
- **W0212**: Protected member access (use proper encapsulation)

### **🔍 MyPy Requirements (0 errors)**

**Essential Checks:**
- **Type annotations**: All parameters, returns, attributes
- **Generic types**: Proper use of TypeVar, Generic
- **Protocol compliance**: Interface implementations
- **Inheritance**: Proper method signatures

**Class-Specific Checks:**
- **Attribute types**: Instance and class variables
- **Method overrides**: Consistent signatures
- **Property types**: Getter/setter consistency

### **📝 Docstring Requirements**

**Class Docstring Must Include:**
```python
class UserModel:
    """User data model with validation and serialization.
    
    This class represents a user entity with comprehensive validation,
    multiple serialization formats, and business rule enforcement.
    
    Attributes:
        user_id: Unique identifier for the user
        email: User's email address (validated)
        created_at: Timestamp of user creation
        
    Example:
        >>> user = UserModel(user_id="123", email="user@example.com")
        >>> user.to_dict()
        {'user_id': '123', 'email': 'user@example.com', ...}
        
    Raises:
        ValidationError: When user data fails validation
        SerializationError: When serialization fails
    """
```

**Method Docstring Must Include:**
- Purpose and behavior
- All parameters with types
- Return value with type
- Exceptions raised
- Usage example for complex methods

---

## 🛡️ **VALIDATION ENFORCEMENT**

### **✅ Immediate Validation Checklist**

**After generating any class, MUST verify:**

- [ ] **Pylint Score**: Exactly 10.0/10 (no exceptions)
- [ ] **MyPy Errors**: Exactly 0 (no type: ignore)
- [ ] **Type Coverage**: 100% of all members
- [ ] **Docstrings**: Class + all public methods
- [ ] **Naming**: PEP 8 compliant names
- [ ] **Imports**: All imports used and necessary
- [ ] **Validation**: Input validation implemented
- [ ] **Error Handling**: Appropriate exceptions raised

### **🚨 Blocking Issues**

**These issues BLOCK class acceptance:**
- Any Pylint score < 10.0
- Any MyPy errors
- Missing type annotations
- Missing docstrings
- Unused imports
- Invalid naming conventions

---

## 🔗 **RELATED MODULES**

**For complete class implementation, also see:**
- **📋 [Analysis Core](analysis-core.md)** - Requirements gathering (257 lines)
- **🎨 [OOP Patterns](oop-patterns.md)** - Design patterns (504 lines)
- **🔧 [Generation Core](generation-core.md)** - Class creation (290 lines)
- **🛡️ [Validation Strategies](validation-strategies.md)** - Validation patterns (436 lines)
- **📦 [Serialization Formats](serialization-formats.md)** - Multi-format support (490 lines)
- **📊 [Quality Commands](quality-commands.md)** - Detailed validation commands (pending)
- **📋 [Quality Standards](quality-standards.md)** - Comprehensive requirements (pending)
- **✅ [Quality Checklist](quality-checklist.md)** - Complete validation checklist (pending)

---

## 🎯 **QUALITY ENFORCEMENT WORKFLOW**

### **Step 1: Generate Class**
- Follow generation-core.md patterns
- Apply oop-patterns.md principles
- Implement validation-strategies.md

### **Step 2: Immediate Validation**
- Run all mandatory quality commands
- Verify core quality standards
- Check immediate validation checklist

### **Step 3: Extended Validation**
- Use quality-commands.md for detailed validation
- Apply quality-standards.md comprehensive requirements
- Complete quality-checklist.md full validation

### **Step 4: Integration**
- Test with serialization-formats.md
- Validate with analysis-core.md requirements
- Ensure pattern compliance with oop-patterns.md

---

**💡 Key Principle**: Quality enforcement is non-negotiable. Every generated class must pass all core validations before proceeding to extended features.
