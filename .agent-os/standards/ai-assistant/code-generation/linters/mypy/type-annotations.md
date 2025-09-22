# MyPy Type Annotations

**🎯 Complete type annotation requirements for MyPy compliance**

## 🚨 **Critical Type Annotation Rules**

### **🚨 MOST COMMON ERROR: Return Value vs None Methods**

**AI assistants frequently test return values of methods that return None**

```python
# ❌ MYPY ERROR - Method returns None, test expects value
def test_method_return(self) -> None:
    processor = SomeProcessor()
    result = processor.shutdown()  # shutdown() returns None
    assert result is True  # MyPy error: method returns None

# ❌ MYPY ERROR - Assigning return value of None method  
def test_process_method(self) -> None:
    processor = SomeProcessor()
    result = processor._process_data(data)  # _process_data() returns None
    assert result is None  # MyPy error: method returns None
```

**✅ SOLUTION: Check production method signatures FIRST**

```python
# STEP 1: Check production code return type
# grep -A 3 "def shutdown" production_file.py
# Result: def shutdown(self) -> None:

# STEP 2: Don't assign return value for None methods
def test_method_return(self) -> None:
    processor = SomeProcessor()
    processor.shutdown()  # Just call the method
    # Test side effects, not return value

# STEP 3: For methods that DO return values, assign properly
def test_force_flush(self) -> None:
    processor = SomeProcessor()
    result: bool = processor.force_flush()  # Returns bool
    assert result is True
```

**🚨 MANDATORY: Production Code Analysis**
```bash
# Before writing tests, check actual return types:
grep -A 3 "def method_name" production_file.py
# Look for "-> None" or no return annotation (implies None)
# Look for "-> bool", "-> str", etc. for actual return types
```

### **All Functions Must Have Complete Type Annotations**

```python
# ❌ MYPY ERROR - Missing type annotations
def process_data(data, config=None):
    result = transform(data)
    return result

# ✅ CORRECT - Complete type annotations
def process_data(
    data: Dict[str, Any], 
    config: Optional[ProcessConfig] = None
) -> ProcessedData:
    """Process data with optional configuration."""
    result: ProcessedData = transform(data)
    return result
```

### **All Variables Must Have Type Annotations**

```python
# ❌ MYPY ERROR - Missing variable type annotations
def test_function():
    items = []  # MyPy can't infer type
    result = process_items(items)
    config = get_config()
    attributes = {}  # Common in tests - MyPy needs type hint

# ✅ CORRECT - Explicit variable type annotations
def test_function() -> None:
    items: List[DataItem] = []
    result: ProcessResult = process_items(items)
    config: ProcessConfig = get_config()
    attributes: Dict[str, Any] = {}  # Common test pattern
```

**🚨 MOST COMMON TEST ERROR: Empty Dict/List Without Types**

```python
# ❌ MYPY ERROR - "Need type annotation for 'attributes'"
def test_span_conversion(self) -> None:
    attributes = {}  # MyPy can't infer Dict type
    session_id = "session-123"
    result = processor._convert_span_to_event(span, attributes, session_id)

# ✅ CORRECT - Always type empty containers
def test_span_conversion(self) -> None:
    attributes: Dict[str, Any] = {}  # Explicit type annotation
    session_id: str = "session-123"
    result: Dict[str, Any] = processor._convert_span_to_event(span, attributes, session_id)
```

### **All Class Attributes Must Have Type Annotations**

```python
# ❌ MYPY ERROR - Missing attribute type annotations
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.logger = logging.getLogger(__name__)

# ✅ CORRECT - Complete attribute type annotations
class DataProcessor:
    def __init__(self, config: ProcessorConfig) -> None:
        self.config: ProcessorConfig = config
        self.cache: Dict[str, Any] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)
```

## 📋 **Type Annotation Patterns**

### **Pattern 1: Basic Function Types**

```python
# Simple function with basic types
def calculate_total(items: List[float], tax_rate: float = 0.08) -> float:
    """Calculate total with tax."""
    subtotal: float = sum(items)
    tax: float = subtotal * tax_rate
    total: float = subtotal + tax
    return total

# Function with no return value
def log_message(message: str, level: str = "INFO") -> None:
    """Log a message at specified level."""
    logger: logging.Logger = logging.getLogger(__name__)
    logger.log(getattr(logging, level), message)
```

### **Pattern 2: Complex Function Types**

```python
# Function with Union types
def parse_value(value: Union[str, int, float]) -> Union[int, float, str]:
    """Parse value to appropriate type."""
    if isinstance(value, str):
        try:
            parsed_int: int = int(value)
            return parsed_int
        except ValueError:
            try:
                parsed_float: float = float(value)
                return parsed_float
            except ValueError:
                return value
    return value

# Function with Optional and complex return type
def find_user(
    user_id: str, 
    *, 
    include_deleted: bool = False
) -> Optional[Dict[str, Any]]:
    """Find user by ID."""
    users: List[Dict[str, Any]] = get_all_users(include_deleted)
    
    for user in users:
        if user.get("id") == user_id:
            return user
    
    return None
```

### **Pattern 3: Generic Types**

```python
from typing import TypeVar, Generic, List, Dict, Callable

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Generic function
def first_item(items: List[T]) -> Optional[T]:
    """Get first item from list."""
    if items:
        return items[0]
    return None

# Generic class
class Cache(Generic[K, V]):
    """Generic cache implementation."""
    
    def __init__(self) -> None:
        self._data: Dict[K, V] = {}
    
    def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        return self._data.get(key)
    
    def set(self, key: K, value: V) -> None:
        """Set key-value pair."""
        self._data[key] = value

# Function with callable type
def apply_transform(
    items: List[T], 
    transform_func: Callable[[T], T]
) -> List[T]:
    """Apply transformation function to all items."""
    results: List[T] = []
    for item in items:
        transformed: T = transform_func(item)
        results.append(transformed)
    return results
```

### **Pattern 4: Test Method Types**

```python
# Test method with proper typing
def test_data_processing(self, mock_processor: Mock) -> None:
    """Test data processing functionality."""
    # Arrange
    test_data: List[DataItem] = [
        DataItem(id="1", value="test1"),
        DataItem(id="2", value="test2")
    ]
    expected_result: ProcessResult = ProcessResult(
        success=True,
        processed_count=2
    )
    
    with patch.object(mock_processor, 'process', return_value=expected_result):
        # Act
        result: ProcessResult = function_under_test(mock_processor, test_data)
        
        # Assert
        assert result.success is True
        assert result.processed_count == 2

# Fixture with proper typing
@pytest.fixture
def mock_data_items() -> List[DataItem]:
    """Create mock data items for testing."""
    items: List[DataItem] = []
    for i in range(3):
        item = DataItem(id=f"item-{i}", value=f"value-{i}")
        items.append(item)
    return items
```

## 🚨 **Common Type Annotation Errors**

### **Error 1: Incompatible return value type**

```python
# ❌ MYPY ERROR - Return type doesn't match annotation
def get_items() -> List[DataItem]:
    items = []  # MyPy sees List[Any]
    items.append(create_item())  # Could be Any type
    return items  # List[Any] incompatible with List[DataItem]

# ✅ CORRECT - Explicit type annotation
def get_items() -> List[DataItem]:
    items: List[DataItem] = []  # Explicit type
    item: DataItem = create_item()  # Ensure correct type
    items.append(item)
    return items
```

### **Error 2: Argument has incompatible type**

```python
# ❌ MYPY ERROR - Wrong argument type
def process_config(config: ProcessorConfig) -> None:
    pass

def test_function():
    config = {"batch_size": 100}  # Dict, not ProcessorConfig
    process_config(config)  # Type error

# ✅ CORRECT - Use proper type
def test_function() -> None:
    config: ProcessorConfig = ProcessorConfig(batch_size=100)
    process_config(config)
```

### **Error 3: Missing type annotation**

```python
# ❌ MYPY ERROR - Function missing return type
def calculate_average(numbers):  # Missing parameter and return types
    total = sum(numbers)  # Missing variable type
    return total / len(numbers)

# ✅ CORRECT - Complete type annotations
def calculate_average(numbers: List[float]) -> float:
    """Calculate average of numbers."""
    total: float = sum(numbers)
    return total / len(numbers)
```

## 📋 **Type Import Patterns**

### **Standard Type Imports**

```python
# Basic typing imports
from typing import Any, Dict, List, Optional, Union

# Advanced typing imports
from typing import Callable, Generic, TypeVar, Protocol

# Python 3.9+ alternative (if using newer Python)
from collections.abc import Callable
from typing import Optional  # Still needed for Optional
```

### **Conditional Type Imports**

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported for type checking, not at runtime
    from honeyhive.tracer.core.base import HoneyHiveTracer
    from expensive.module import ExpensiveClass
```

### **Mock Type Handling**

```python
from unittest.mock import Mock
from typing import cast

# When you need to type a Mock object
def test_with_typed_mock() -> None:
    mock_tracer = Mock(spec=HoneyHiveTracer)
    # Type cast when necessary
    typed_tracer: HoneyHiveTracer = cast(HoneyHiveTracer, mock_tracer)
```

## 📋 **Type Annotation Checklist**

**Before generating ANY code, verify:**

- [ ] **All function parameters typed**: Every parameter has type annotation
- [ ] **All function returns typed**: Every function has return type annotation
- [ ] **All variables typed**: Local variables have explicit types when needed
- [ ] **All class attributes typed**: Instance attributes have type annotations
- [ ] **Proper Optional usage**: Use `Optional[T]` for nullable types
- [ ] **Correct Union usage**: Use `Union[T, U]` for multiple possible types
- [ ] **Generic types imported**: Import `List`, `Dict`, etc. from `typing`
- [ ] **Mock objects typed**: Use `spec=` parameter for type safety

## ⚡ **Quick Type Fixes**

### **Add Missing Return Type**
```python
# Add -> None for functions that don't return values
# Add -> ReturnType for functions that return values
```

### **Fix Variable Types**
```python
# Add explicit type annotation
items: List[DataItem] = []
config: Optional[Config] = None
```

### **Fix Mock Types**
```python
# Use spec parameter for type safety
mock_obj = Mock(spec=TargetClass)
```

---

**🎯 Remember**: Complete type annotations make code more maintainable and catch errors early.
