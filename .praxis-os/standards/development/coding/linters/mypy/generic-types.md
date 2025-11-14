# MyPy Generic Types

**🎯 Proper usage of generic types for MyPy compliance**

## 🚨 **Critical Generic Type Rules**

### **Always Import Generic Types from typing**

```python
# ❌ MYPY ERROR - Using built-in types for annotations
def process_items(items: list, config: dict) -> list:
    pass

# ✅ CORRECT - Import from typing module
from typing import Dict, List

def process_items(items: List[DataItem], config: Dict[str, Any]) -> List[ProcessedItem]:
    pass
```

### **Specify Generic Type Parameters**

```python
# ❌ MYPY ERROR - Generic type without parameters
def get_cache() -> Dict:
    return {}

def get_items() -> List:
    return []

# ✅ CORRECT - Specify type parameters
def get_cache() -> Dict[str, Any]:
    return {}

def get_items() -> List[DataItem]:
    return []
```

### **Use Optional for Nullable Types**

```python
# ❌ MYPY ERROR - Using None without Optional
def find_item(item_id: str) -> DataItem:
    if item_id in cache:
        return cache[item_id]
    return None  # Error: None not compatible with DataItem

# ✅ CORRECT - Use Optional for nullable returns
from typing import Optional

def find_item(item_id: str) -> Optional[DataItem]:
    if item_id in cache:
        return cache[item_id]
    return None
```

## 📋 **Generic Type Patterns**

### **Pattern 1: Basic Generic Types**

```python
from typing import Any, Dict, List, Optional, Set, Tuple

# List with specific element type
def process_user_ids(user_ids: List[str]) -> List[User]:
    """Process list of user IDs to User objects."""
    users: List[User] = []
    for user_id in user_ids:
        user: Optional[User] = find_user(user_id)
        if user is not None:
            users.append(user)
    return users

# Dictionary with specific key/value types
def get_user_preferences() -> Dict[str, bool]:
    """Get user preferences as string->bool mapping."""
    preferences: Dict[str, bool] = {
        "notifications": True,
        "dark_mode": False,
        "auto_save": True
    }
    return preferences

# Set with specific element type
def get_unique_tags(items: List[DataItem]) -> Set[str]:
    """Extract unique tags from data items."""
    tags: Set[str] = set()
    for item in items:
        item_tags: List[str] = item.get_tags()
        tags.update(item_tags)
    return tags

# Tuple with specific element types
def get_coordinates() -> Tuple[float, float]:
    """Get x, y coordinates."""
    x: float = 10.5
    y: float = 20.3
    return (x, y)
```

### **Pattern 2: Union Types**

```python
from typing import Union

# Union for multiple possible types
def parse_id(id_value: Union[str, int]) -> str:
    """Parse ID value to string format."""
    if isinstance(id_value, int):
        return str(id_value)
    return id_value

# Union with None (alternative to Optional)
def get_config(name: str) -> Union[Config, None]:
    """Get configuration by name."""
    if name in configs:
        return configs[name]
    return None

# Complex Union types
ProcessResult = Union[SuccessResult, ErrorResult, PendingResult]

def process_request(request: Request) -> ProcessResult:
    """Process request and return appropriate result type."""
    if request.is_valid():
        return SuccessResult(data=request.process())
    elif request.has_errors():
        return ErrorResult(errors=request.get_errors())
    else:
        return PendingResult(request_id=request.id)
```

### **Pattern 3: Callable Types**

```python
from typing import Callable

# Function that takes a callable
def apply_filter(
    items: List[DataItem], 
    filter_func: Callable[[DataItem], bool]
) -> List[DataItem]:
    """Apply filter function to items."""
    filtered_items: List[DataItem] = []
    for item in items:
        if filter_func(item):
            filtered_items.append(item)
    return filtered_items

# Callable with specific return type
def execute_with_callback(
    operation: Callable[[], str],
    callback: Callable[[str], None]
) -> None:
    """Execute operation and call callback with result."""
    result: str = operation()
    callback(result)

# Method type annotation
class DataProcessor:
    def set_transform_func(
        self, 
        transform: Callable[[DataItem], ProcessedItem]
    ) -> None:
        """Set transformation function."""
        self._transform: Callable[[DataItem], ProcessedItem] = transform
```

### **Pattern 4: Custom Generic Classes**

```python
from typing import Generic, TypeVar

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Generic cache class
class Cache(Generic[K, V]):
    """Generic key-value cache."""
    
    def __init__(self) -> None:
        self._data: Dict[K, V] = {}
        self._access_count: Dict[K, int] = {}
    
    def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        if key in self._data:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._data[key]
        return None
    
    def set(self, key: K, value: V) -> None:
        """Set key-value pair."""
        self._data[key] = value
        self._access_count[key] = 0
    
    def get_stats(self) -> Dict[K, int]:
        """Get access statistics."""
        return self._access_count.copy()

# Usage of generic class
def create_string_cache() -> Cache[str, str]:
    """Create cache for string key-value pairs."""
    return Cache[str, str]()

def create_user_cache() -> Cache[str, User]:
    """Create cache for user objects."""
    return Cache[str, User]()
```

## 🚨 **Generic Type Errors to Avoid**

### **Error 1: Missing type parameters**

```python
# ❌ MYPY ERROR - Generic type without parameters
def process_data() -> Dict:
    return {}

def get_items() -> List:
    return []

# ✅ CORRECT - Specify type parameters
def process_data() -> Dict[str, Any]:
    return {}

def get_items() -> List[DataItem]:
    return []
```

### **Error 2: Incorrect Optional usage**

```python
# ❌ MYPY ERROR - Wrong Optional usage
def find_user(user_id: str) -> Optional[User, None]:  # Wrong syntax
    pass

def get_config() -> Optional:  # Missing type parameter
    pass

# ✅ CORRECT - Proper Optional usage
def find_user(user_id: str) -> Optional[User]:
    pass

def get_config() -> Optional[Config]:
    pass
```

### **Error 3: Mixing built-in and typing types**

```python
# ❌ MYPY ERROR - Mixing built-in and typing types
from typing import List

def process(items: list[str]) -> List[str]:  # Mixed usage
    pass

# ✅ CORRECT - Consistent typing usage
from typing import List

def process(items: List[str]) -> List[str]:
    pass
```

## 📋 **Test-Specific Generic Types**

### **Mock with Generic Types**

```python
from unittest.mock import Mock
from typing import List

def test_process_items(self) -> None:
    """Test item processing with proper generic types."""
    # Arrange
    mock_items: List[DataItem] = [
        Mock(spec=DataItem),
        Mock(spec=DataItem),
        Mock(spec=DataItem)
    ]
    
    expected_results: List[ProcessedItem] = [
        ProcessedItem(id="1", status="processed"),
        ProcessedItem(id="2", status="processed"),
        ProcessedItem(id="3", status="processed")
    ]
    
    # Act
    results: List[ProcessedItem] = process_items(mock_items)
    
    # Assert
    assert len(results) == 3
    for result in results:
        assert result.status == "processed"
```

### **Fixture with Generic Types**

```python
@pytest.fixture
def mock_data_cache() -> Dict[str, DataItem]:
    """Create mock data cache for testing."""
    cache: Dict[str, DataItem] = {}
    for i in range(5):
        item_id: str = f"item-{i}"
        item: DataItem = DataItem(id=item_id, value=f"value-{i}")
        cache[item_id] = item
    return cache

@pytest.fixture
def test_user_list() -> List[User]:
    """Create list of test users."""
    users: List[User] = []
    for i in range(3):
        user: User = User(
            id=f"user-{i}",
            name=f"Test User {i}",
            email=f"user{i}@test.com"
        )
        users.append(user)
    return users
```

## 📋 **Generic Types Checklist**

**Before using ANY generic type, verify:**

- [ ] **Imported from typing**: Use `from typing import List, Dict, etc.`
- [ ] **Type parameters specified**: `List[str]` not just `List`
- [ ] **Optional for nullable**: Use `Optional[T]` for values that can be None
- [ ] **Union for alternatives**: Use `Union[T, U]` for multiple possible types
- [ ] **Callable properly typed**: Specify parameter and return types
- [ ] **Generic classes parameterized**: Use TypeVar for custom generic classes
- [ ] **Consistent usage**: Don't mix built-in and typing module types
- [ ] **Test types match**: Mock and fixture types match expected types

## ⚡ **Quick Generic Type Fixes**

### **Add Type Parameters**
```python
# Change List to List[ElementType]
# Change Dict to Dict[KeyType, ValueType]
```

### **Fix Optional Usage**
```python
# Change T | None to Optional[T] (for older Python)
# Use Optional[T] for nullable types
```

### **Import Required Types**
```python
from typing import Any, Dict, List, Optional, Union
```

---

**🎯 Remember**: Proper generic types make your code more precise and catch type errors early.
