# Classes - Validation Strategies (v2)

## 🎯 **VALIDATION STRATEGIES FOR CLASSES**

**Purpose**: Comprehensive validation patterns and strategies for robust class implementations.

**Focus**: Field validation, cross-field validation, business rules, and custom validators.

---

## 📋 **VALIDATION TYPES**

### **1. Field-Level Validation**
**Purpose**: Validate individual field values with type checking and constraints

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class UserModel(BaseModel):
    """User model with comprehensive field validation."""
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        strip_whitespace=True,
        description="User's full name"
    )
    
    age: int = Field(
        ...,
        ge=0,
        le=150,
        description="User's age in years"
    )
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate name with business rules."""
        if not v or v.isspace():
            raise ValueError("Name cannot be empty")
        
        # Security validation
        dangerous_chars = ['<', '>', '&', '"', "'", '\\']
        if any(char in v for char in dangerous_chars):
            raise ValueError("Name contains invalid characters")
        
        # Business rule validation
        if '@' in v:
            raise ValueError("Name cannot contain email address")
        
        return v.strip().title()
    
    @validator('age')
    def validate_age_realistic(cls, v: int) -> int:
        """Validate age with realistic constraints."""
        if v < 13:
            raise ValueError("Users must be at least 13 years old")
        
        return v
```

### **2. Cross-Field Validation**
**Purpose**: Validate relationships and dependencies between multiple fields

```python
from pydantic import root_validator
from typing import Dict, Any

class UserModel(BaseModel):
    """User model with cross-field validation."""
    
    email: str
    role: str
    age: int
    department: Optional[str] = None
    
    @root_validator
    def validate_admin_requirements(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate admin role requirements across fields."""
        role = values.get('role')
        age = values.get('age')
        email = values.get('email')
        department = values.get('department')
        
        if role == 'admin':
            # Age requirement for admin
            if age is not None and age < 21:
                raise ValueError("Admin users must be at least 21 years old")
            
            # Email domain requirement for admin
            if email and not email.endswith('@company.com'):
                raise ValueError("Admin users must use company email domain")
            
            # Department requirement for admin
            if not department:
                raise ValueError("Admin users must have a department assigned")
        
        return values
    
    @root_validator
    def validate_email_department_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email and department consistency."""
        email = values.get('email')
        department = values.get('department')
        
        if email and department:
            email_domain = email.split('@')[0].lower()
            
            # Check department-specific email patterns
            department_patterns = {
                'engineering': ['eng', 'dev', 'tech'],
                'marketing': ['marketing', 'mkt', 'promo'],
                'sales': ['sales', 'biz', 'revenue']
            }
            
            if department.lower() in department_patterns:
                expected_patterns = department_patterns[department.lower()]
                if not any(pattern in email_domain for pattern in expected_patterns):
                    # This is a warning, not an error
                    logger.warning(f"Email '{email}' may not match department '{department}'")
        
        return values
```

### **3. Business Rule Validation**
**Purpose**: Enforce domain-specific business logic and constraints

```python
from datetime import datetime, date
from typing import List, Dict, Any

class OrderModel(BaseModel):
    """Order model with business rule validation."""
    
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    discount_percent: float = 0.0
    order_date: datetime
    customer_type: str = "regular"
    
    @validator('items')
    def validate_items_not_empty(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate order has items."""
        if not v:
            raise ValueError("Order must contain at least one item")
        
        # Validate each item structure
        for i, item in enumerate(v):
            required_fields = ['product_id', 'quantity', 'price']
            for field in required_fields:
                if field not in item:
                    raise ValueError(f"Item {i} missing required field: {field}")
            
            if item['quantity'] <= 0:
                raise ValueError(f"Item {i} quantity must be positive")
            
            if item['price'] <= 0:
                raise ValueError(f"Item {i} price must be positive")
        
        return v
    
    @validator('discount_percent')
    def validate_discount_rules(cls, v: float, values: Dict[str, Any]) -> float:
        """Validate discount based on business rules."""
        if v < 0:
            raise ValueError("Discount cannot be negative")
        
        if v > 50:
            raise ValueError("Discount cannot exceed 50%")
        
        # Business rule: VIP customers can have higher discounts
        customer_type = values.get('customer_type', 'regular')
        if customer_type != 'vip' and v > 20:
            raise ValueError("Regular customers cannot have discount > 20%")
        
        return v
    
    @root_validator
    def validate_total_amount_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate total amount matches items and discount."""
        items = values.get('items', [])
        total_amount = values.get('total_amount')
        discount_percent = values.get('discount_percent', 0.0)
        
        if items and total_amount is not None:
            # Calculate expected total
            items_total = sum(item['quantity'] * item['price'] for item in items)
            discount_amount = items_total * (discount_percent / 100)
            expected_total = items_total - discount_amount
            
            # Allow small floating point differences
            if abs(expected_total - total_amount) > 0.01:
                raise ValueError(
                    f"Total amount {total_amount} doesn't match calculated total {expected_total:.2f}"
                )
        
        return values
```

### **4. Custom Validator Strategies**
**Purpose**: Reusable validation logic for complex scenarios

```python
from typing import Callable, Any, Type
import re

class ValidationStrategies:
    """Collection of reusable validation strategies."""
    
    @staticmethod
    def create_regex_validator(pattern: str, error_message: str) -> Callable[[str], str]:
        """Create a regex-based validator."""
        compiled_pattern = re.compile(pattern)
        
        def validator(value: str) -> str:
            if not compiled_pattern.match(value):
                raise ValueError(error_message)
            return value
        
        return validator
    
    @staticmethod
    def create_length_validator(min_length: int, max_length: int) -> Callable[[str], str]:
        """Create a length-based validator."""
        def validator(value: str) -> str:
            if len(value) < min_length:
                raise ValueError(f"Value must be at least {min_length} characters")
            if len(value) > max_length:
                raise ValueError(f"Value cannot exceed {max_length} characters")
            return value
        
        return validator
    
    @staticmethod
    def create_enum_validator(allowed_values: List[str]) -> Callable[[str], str]:
        """Create an enum-based validator."""
        def validator(value: str) -> str:
            if value not in allowed_values:
                raise ValueError(f"Value must be one of: {', '.join(allowed_values)}")
            return value
        
        return validator
    
    @staticmethod
    def create_composite_validator(*validators: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Create a composite validator from multiple validators."""
        def validator(value: Any) -> Any:
            for validate_func in validators:
                value = validate_func(value)
            return value
        
        return validator

# Usage example
class ProductModel(BaseModel):
    """Product model using custom validation strategies."""
    
    sku: str
    category: str
    price: float
    
    # Create custom validators
    _validate_sku = ValidationStrategies.create_regex_validator(
        r'^[A-Z]{2}\d{4}$',
        "SKU must be 2 uppercase letters followed by 4 digits"
    )
    
    _validate_category = ValidationStrategies.create_enum_validator(
        ['electronics', 'clothing', 'books', 'home']
    )
    
    @validator('sku')
    def validate_sku(cls, v: str) -> str:
        """Validate SKU format."""
        return cls._validate_sku(v)
    
    @validator('category')
    def validate_category(cls, v: str) -> str:
        """Validate category."""
        return cls._validate_category(v)
    
    @validator('price')
    def validate_price_positive(cls, v: float) -> float:
        """Validate price is positive."""
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
```

---

## 🔧 **VALIDATION PATTERNS**

### **Validation Chain Pattern**
```python
from typing import List, Callable, Any

class ValidationChain:
    """Chain of responsibility pattern for validation."""
    
    def __init__(self) -> None:
        self._validators: List[Callable[[Any], Any]] = []
    
    def add_validator(self, validator: Callable[[Any], Any]) -> 'ValidationChain':
        """Add validator to chain."""
        self._validators.append(validator)
        return self
    
    def validate(self, value: Any) -> Any:
        """Run value through validation chain."""
        for validator in self._validators:
            value = validator(value)
        return value

# Usage
email_chain = (ValidationChain()
    .add_validator(lambda x: x.strip().lower())
    .add_validator(lambda x: x if '@' in x else ValueError("Invalid email"))
    .add_validator(lambda x: x if '.' in x.split('@')[1] else ValueError("Invalid domain"))
)
```

### **Validation Context Pattern**
```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ValidationContext:
    """Context for validation with additional information."""
    user_role: str
    environment: str
    request_source: str
    additional_data: Dict[str, Any] = None

class ContextAwareValidator:
    """Validator that uses context for decisions."""
    
    def __init__(self, context: ValidationContext) -> None:
        self.context = context
    
    def validate_sensitive_field(self, value: str) -> str:
        """Validate field based on context."""
        # Different validation rules based on user role
        if self.context.user_role == 'admin':
            # Admins can set any value
            return value
        elif self.context.user_role == 'user':
            # Regular users have restrictions
            if len(value) > 100:
                raise ValueError("Regular users cannot set values > 100 chars")
        else:
            raise ValueError("Insufficient permissions")
        
        return value
```

---

## 📊 **VALIDATION BEST PRACTICES**

### **✅ Field Validation Best Practices**
- [ ] **Type safety** - Use proper type annotations
- [ ] **Clear error messages** - Provide actionable feedback
- [ ] **Security validation** - Prevent XSS, injection attacks
- [ ] **Performance** - Avoid expensive validation in hot paths
- [ ] **Consistency** - Use consistent validation patterns

### **✅ Cross-Field Validation Best Practices**
- [ ] **Dependency order** - Validate dependencies first
- [ ] **Error aggregation** - Collect all errors, don't fail fast
- [ ] **Context awareness** - Consider business context
- [ ] **Partial validation** - Support incremental validation
- [ ] **Clear relationships** - Document field dependencies

### **✅ Business Rule Best Practices**
- [ ] **Domain modeling** - Reflect real business constraints
- [ ] **Flexibility** - Allow configuration of business rules
- [ ] **Auditability** - Log business rule violations
- [ ] **Testing** - Comprehensive test coverage for rules
- [ ] **Documentation** - Clear documentation of business logic

---

## 🚨 **VALIDATION ERROR HANDLING**

### **Custom Exception Hierarchy**
```python
class ValidationError(Exception):
    """Base validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.field = field
        self.code = code
        self.timestamp = datetime.now()

class FieldValidationError(ValidationError):
    """Field-specific validation error."""
    
    def __init__(self, field: str, message: str, value: Any = None) -> None:
        super().__init__(message, field, "FIELD_VALIDATION")
        self.value = value

class BusinessRuleError(ValidationError):
    """Business rule validation error."""
    
    def __init__(self, rule: str, message: str, context: Dict[str, Any] = None) -> None:
        super().__init__(message, None, "BUSINESS_RULE")
        self.rule = rule
        self.context = context or {}

class ValidationResult:
    """Comprehensive validation result."""
    
    def __init__(self) -> None:
        self.is_valid = True
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: ValidationError) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)
```

---

## 🔗 **RELATED MODULES**

**For complete class implementation, also see:**
- **📋 [Analysis Core](analysis-core.md)** - Requirements gathering (257 lines)
- **🎨 [OOP Patterns](oop-patterns.md)** - Design patterns (504 lines)
- **🔧 [Generation Core](generation-core.md)** - Class creation (290 lines)
- **📦 [Serialization Formats](serialization-formats.md)** - Multi-format support (490 lines)
- **📊 [Quality Core](quality-core.md)** - Quality enforcement (pending)

---

**💡 Key Principle**: Validation strategies should be comprehensive, reusable, and provide clear feedback while maintaining performance and security.
