# Classes - Generation Core (v2)

## 🎯 **GENERATION PHASE FOR CLASSES**

**Purpose**: Template-based generation of classes with OOP patterns and comprehensive validation.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, robust validation.

---

## 📋 **MANDATORY GENERATION COMMANDS**

### **Command 1: Select Template & Patterns**
```bash
# AI MUST select appropriate template and design patterns
echo "Template selected: [TEMPLATE_NAME] from classes/templates.md"
echo "Design patterns applied: [PATTERN_LIST]"
echo "OOP principles enforced: [PRINCIPLE_LIST]"
```

**Required Output:**
- Specific class template name and justification
- Design patterns to be implemented
- Object-oriented principles to enforce
- Template customization strategy

### **Command 2: Generate Class Structure**
```bash
# AI MUST generate complete class structure
echo "Class structure generated: attributes, methods, properties, inheritance"
```

**Required Output:**
- Complete class definition with inheritance
- All attributes with type annotations
- Method signatures and implementations
- Property definitions and logic
- Class and static methods

### **Command 3: Implement Validation Logic**
```bash
# AI MUST implement comprehensive validation
echo "Validation implemented: [FIELD_VALIDATION, CROSS_FIELD_VALIDATION, BUSINESS_RULES]"
```

**Required Output:**
- Field-level validation with custom validators
- Cross-field validation logic
- Business rule enforcement
- Validation error handling
- Custom exception types

### **Command 4: Add Serialization Support**
```bash
# AI MUST implement serialization/deserialization
echo "Serialization implemented: [JSON, DICT, DATABASE, API] with [TRANSFORMATION_LOGIC]"
```

**Required Output:**
- Multiple serialization formats
- Data transformation logic
- Deserialization with validation
- Custom serialization methods
- Format-specific optimizations

---

## 🛠️ **TEMPLATE SELECTION GUIDE**

### **Available Templates**
1. **Pydantic Data Model Template** - Validated data models
2. **Service Class Template** - Business logic and external integration
3. **Configuration Class Template** - Settings management
4. **Manager Class Template** - Resource and state management
5. **Factory Class Template** - Object creation and dependency injection
6. **Repository Class Template** - Data access abstraction

### **Template Selection Criteria**

| Class Type | Template | Use When |
|------------|----------|----------|
| **Data Models** | Pydantic Data Model | API models, configuration, validation |
| **Business Logic** | Service Class | External integrations, business operations |
| **Configuration** | Configuration Class | Settings, environment management |
| **Resource Management** | Manager Class | Resource lifecycle, state management |
| **Object Creation** | Factory Class | Dynamic object creation, plugin systems |
| **Data Access** | Repository Class | Database abstraction, data persistence |

---

## 🔧 **GENERATION PROCESS**

### **Step 1: Template Customization**
**Apply comprehensive customizations:**

1. **Class Definition**: Set class name, inheritance, and metaclass
2. **Attributes**: Define all instance and class attributes with types
3. **Properties**: Implement computed properties with getters/setters
4. **Methods**: Implement all public and private methods
5. **Validation**: Add field and business rule validation
6. **Serialization**: Implement serialization/deserialization methods
7. **Design Patterns**: Integrate selected patterns
8. **Error Handling**: Add comprehensive exception handling
9. **Documentation**: Create detailed docstrings
10. **Testing Hooks**: Add testability features

### **Step 2: Pattern Integration**
**Integrate design patterns appropriately:**

1. **Pattern Selection**: Choose patterns based on class type
2. **Pattern Implementation**: Implement patterns correctly
3. **Pattern Composition**: Combine patterns effectively
4. **Pattern Testing**: Ensure patterns work as expected

### **Step 3: Quality Integration**
**Ensure generated code includes:**

1. **Type Safety**: 100% type annotation coverage
2. **Validation**: Comprehensive input validation
3. **Documentation**: Complete docstrings with examples
4. **Error Handling**: Robust exception handling
5. **Serialization**: Multiple format support
6. **Performance**: Optimized implementations
7. **Thread Safety**: Concurrent access considerations
8. **Testing**: Dependency injection and test-friendly design

---

## 📝 **GENERATION EXAMPLES**

### **Basic Class Structure Example**
```python
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"

class UserModel(BaseModel):
    """User model with comprehensive features.
    
    Demonstrates:
    - Field validation with custom validators
    - Cross-field business rule enforcement
    - Multiple serialization formats
    - Builder pattern integration
    
    Example:
        >>> user = UserModel(name="John Doe", email="john@example.com", age=30)
        >>> print(user.display_name)
        "John Doe"
    """
    
    # Core attributes
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="User's email address")
    age: int = Field(..., ge=0, le=150)
    role: UserRole = Field(UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    
    # Computed properties
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return self.name.title()
    
    @property
    def is_adult(self) -> bool:
        """Check if user is an adult."""
        return self.age >= 18
    
    # Field validators
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate name with business rules."""
        if '@' in v:
            raise ValueError("Name cannot contain email address")
        return v.strip()
    
    # Business logic methods
    def add_tag(self, tag: str) -> bool:
        """Add tag with validation."""
        normalized_tag = tag.strip().lower()
        if normalized_tag and normalized_tag not in self.tags:
            self.tags.append(normalized_tag)
            return True
        return False
    
    # Serialization methods
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API response format."""
        data = self.dict()
        data['display_name'] = self.display_name
        data['is_adult'] = self.is_adult
        return data
    
    # Builder pattern
    @classmethod
    def builder(cls) -> 'UserModelBuilder':
        """Create builder for fluent construction."""
        return UserModelBuilder()

class UserModelBuilder:
    """Builder for fluent UserModel construction."""
    
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
    
    def name(self, name: str) -> 'UserModelBuilder':
        self._data['name'] = name
        return self
    
    def email(self, email: str) -> 'UserModelBuilder':
        self._data['email'] = email
        return self
    
    def age(self, age: int) -> 'UserModelBuilder':
        self._data['age'] = age
        return self
    
    def build(self) -> UserModel:
        return UserModel(**self._data)
```

**Related Modules**: For comprehensive implementation details, see:
- **🎨 [OOP Patterns](oop-patterns.md)** - Design patterns for classes (504 lines)
- **🛡️ [Validation Strategies](validation-strategies.md)** - Field and business rule validation (436 lines)
- **📦 [Serialization Formats](serialization-formats.md)** - Multiple format support (490 lines)
- **📊 [Quality Core](quality-core.md)** - Quality enforcement (pending)

---

## 🎯 **GENERATION QUALITY CHECKLIST**

### **✅ Template Compliance**
- [ ] **Template selected** from available class templates
- [ ] **Template structure followed** correctly
- [ ] **Template customizations applied** appropriately

### **✅ Class Structure Quality**
- [ ] **Class definition** complete with proper inheritance
- [ ] **Attributes** all defined with type annotations
- [ ] **Methods** implemented with proper signatures
- [ ] **Properties** computed correctly with getters/setters
- [ ] **Class/static methods** used appropriately

### **✅ Pattern Integration**
- [ ] **Patterns selected** appropriately for class type
- [ ] **Pattern implementation** follows best practices
- [ ] **Pattern integration** works seamlessly
- [ ] **Pattern interactions** handled correctly

### **✅ Validation Implementation**
- [ ] **Field validation** comprehensive with custom validators
- [ ] **Cross-field validation** implemented correctly
- [ ] **Business rules** enforced with clear error messages
- [ ] **Custom exceptions** defined and used appropriately

### **✅ Serialization Support**
- [ ] **Multiple formats** supported (JSON, dict, database)
- [ ] **Serialization methods** implemented correctly
- [ ] **Deserialization** with validation
- [ ] **Custom transformations** applied appropriately

---

## 🚨 **GENERATION GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Template selected and properly customized
- All 4 mandatory commands executed with evidence
- Class structure complete with all components
- Validation logic comprehensive and tested
- Serialization support implemented for all required formats
- Design patterns correctly integrated
- Quality checklist completed

**❌ GATE FAILED IF:**
- No template used or improperly customized
- Class structure incomplete or incorrect
- Validation logic insufficient or missing
- Serialization support inadequate
- Design patterns missing or incorrect

---

**💡 Key Principle**: Class generation requires systematic application of OOP principles, proven templates, and comprehensive validation to create robust, maintainable implementations.
