# Classes - Quality Commands

## 🎯 **MANDATORY VALIDATION COMMANDS**

**Purpose**: Comprehensive command-by-command validation for generated classes.

**Usage**: Run these commands in sequence after class generation to ensure quality compliance.

---

## 📋 **COMMAND SEQUENCE**

### **Command 1: Comprehensive Pylint Validation**
```bash
# AI MUST run Pylint with class-specific focus and achieve 10.0/10
tox -e lint -- path/to/generated_class.py
```

**Required Output:**
- Pylint score: 10.0/10
- Zero violations across all categories
- Class-specific rules satisfied
- Any disables justified with detailed comments

**Common Class Issues to Fix:**
- `C0103` - Invalid name (use descriptive, PEP 8 names)
- `C0115` - Missing class docstring
- `C0116` - Missing function/method docstring
- `R0902` - Too many instance attributes (>7, use composition)
- `R0903` - Too few public methods (<2 for non-data classes)
- `R0904` - Too many public methods (>20, split responsibilities)
- `R0913` - Too many arguments (>5, use dataclasses/builders)

### **Command 2: Advanced MyPy Validation**
```bash
# AI MUST run MyPy with strict settings and achieve 0 errors
tox -e mypy -- path/to/generated_class.py
```

**Required Output:**
- MyPy errors: 0
- All complex type annotations validated
- Generic types and protocols correctly used
- Inheritance relationships properly typed
- No type: ignore comments needed

**Class-Specific Type Checks:**
- All instance and class attributes typed
- Method parameters and returns typed
- Property getters/setters consistently typed
- Generic types (TypeVar, Generic) used correctly
- Protocol implementations fully typed
- Inheritance method signatures match

### **Command 3: Complete Type Annotation Coverage**
```bash
# AI MUST verify 100% type annotation coverage for classes
echo "Type annotation coverage: 100% - all attributes, methods, properties, and complex types annotated"
```

**Required Output:**
- All class and instance attributes typed
- All method parameters and returns typed
- Property getters/setters properly typed
- Generic types and type variables used correctly
- Protocol implementations fully typed

**Coverage Verification:**
```python
# Example of complete type coverage
class UserModel:
    """User data model."""
    
    # Class attributes typed
    _registry: ClassVar[Dict[str, Type['UserModel']]] = {}
    
    def __init__(
        self, 
        user_id: str, 
        email: str, 
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize user model."""
        self.user_id: str = user_id
        self.email: str = email
        self.created_at: datetime = created_at or datetime.now()
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return f"User {self.user_id}"
    
    def validate(self) -> bool:
        """Validate user data."""
        return bool(self.user_id and self.email)
```

### **Command 4: Comprehensive Docstring Validation**
```bash
# AI MUST verify complete docstring coverage for classes
echo "Docstring validation: Complete - class, methods, properties, examples, design notes"
```

**Required Output:**
- Class docstring with detailed description and examples
- All methods documented with comprehensive details
- All properties documented with behavior
- Multiple usage examples provided
- Design patterns and architecture notes included

**Docstring Template:**
```python
class UserModel:
    """User data model with validation and serialization.
    
    This class represents a user entity with comprehensive validation,
    multiple serialization formats, and business rule enforcement.
    
    The class implements the following patterns:
    - Builder pattern for complex construction
    - Strategy pattern for validation rules
    - Observer pattern for change notifications
    
    Attributes:
        user_id: Unique identifier for the user
        email: User's email address (validated format)
        created_at: Timestamp of user creation
        
    Example:
        Basic usage:
        >>> user = UserModel(user_id="123", email="user@example.com")
        >>> user.validate()
        True
        
        With builder pattern:
        >>> user = (UserModel.builder()
        ...          .with_id("123")
        ...          .with_email("user@example.com")
        ...          .build())
        
        Serialization:
        >>> user.to_dict()
        {'user_id': '123', 'email': 'user@example.com', ...}
        >>> UserModel.from_dict(data)
        <UserModel: 123>
        
    Raises:
        ValidationError: When user data fails validation rules
        SerializationError: When serialization/deserialization fails
        
    Note:
        This class is thread-safe for read operations but requires
        external synchronization for write operations.
    """
```

### **Command 5: Validation Logic Testing**
```bash
# AI MUST verify all validation logic works correctly
echo "Validation testing: Complete - field validation, cross-field validation, business rules tested"
```

**Required Output:**
- All field validators tested with valid/invalid inputs
- Cross-field validation scenarios tested
- Business rule enforcement verified
- Custom exception handling tested
- Edge cases and boundary conditions covered

**Validation Test Examples:**
```python
# Test field validation
assert user.validate_email("valid@example.com") == True
assert user.validate_email("invalid-email") == False

# Test cross-field validation
assert user.validate_consistency() == True

# Test business rules
assert user.can_perform_action("delete") == False  # New users can't delete

# Test edge cases
assert user.validate_email("") == False
assert user.validate_email(None) == False
```

### **Command 6: Serialization Testing**
```bash
# AI MUST verify all serialization formats work correctly
echo "Serialization testing: Complete - JSON, dict, database, API formats tested with round-trip validation"
```

**Required Output:**
- All serialization formats tested
- Round-trip serialization/deserialization verified
- Data transformation logic tested
- Format-specific optimizations validated
- Error handling in serialization tested

**Serialization Test Examples:**
```python
# Test round-trip serialization
original = UserModel(user_id="123", email="user@example.com")
data = original.to_dict()
restored = UserModel.from_dict(data)
assert original == restored

# Test JSON serialization
json_str = original.to_json()
from_json = UserModel.from_json(json_str)
assert original == from_json

# Test database format
db_data = original.to_db_format()
from_db = UserModel.from_db_format(db_data)
assert original == from_db
```

### **Command 7: Design Pattern Validation**
```bash
# AI MUST verify design patterns are correctly implemented
echo "Design pattern validation: Complete - pattern implementation, interactions, and compliance verified"
```

**Required Output:**
- All implemented patterns tested
- Pattern interactions verified
- Pattern compliance with standard implementations
- Pattern-specific behavior validated
- Integration with class functionality tested

### **Command 8: Integration Testing**
```bash
# AI MUST run integration tests for class interactions
tox -e integration -- -k "test_class_name"
```

**Required Output:**
- All integration tests passing
- Class interactions with dependencies tested
- Inheritance relationships validated
- Composition patterns tested
- External system integrations verified

---

## 🔗 **RELATED MODULES**

**For complete class quality enforcement:**
- **📊 [Quality Core](quality-core.md)** - Essential quality enforcement (194 lines)
- **📋 [Quality Standards](quality-standards.md)** - Detailed requirements (pending)
- **✅ [Quality Checklist](quality-checklist.md)** - Complete validation checklist (pending)

**For class implementation:**
- **📋 [Analysis Core](analysis-core.md)** - Requirements gathering (257 lines)
- **🎨 [OOP Patterns](oop-patterns.md)** - Design patterns (504 lines)
- **🔧 [Generation Core](generation-core.md)** - Class creation (290 lines)
- **🛡️ [Validation Strategies](validation-strategies.md)** - Validation patterns (436 lines)
- **📦 [Serialization Formats](serialization-formats.md)** - Multi-format support (490 lines)

---

**💡 Key Principle**: Each command must pass completely before proceeding to the next. No shortcuts or partial compliance allowed.
