# Classes - OOP Patterns (v2)

## 🎯 **OBJECT-ORIENTED DESIGN PATTERNS FOR CLASSES**

**Purpose**: Essential OOP patterns for robust class design and implementation.

**Focus**: Proven patterns that enhance maintainability, extensibility, and testability.

---

## 🏗️ **CREATIONAL PATTERNS**

### **1. Singleton Pattern**
**Use Case**: Ensure single instance (configuration, logging, database connections)

```python
import threading
from typing import Optional, Dict, Any

class ConfigurationManager:
    """Thread-safe singleton configuration manager."""
    
    _instance: Optional['ConfigurationManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ConfigurationManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._config: Dict[str, Any] = {}
            self._initialized = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
```

### **2. Factory Pattern**
**Use Case**: Create objects without specifying exact classes

```python
from typing import Dict, Type, Any, Protocol
from abc import ABC, abstractmethod

class Processor(Protocol):
    def process(self, data: Any) -> Any: ...

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class JSONProcessor(DataProcessor):
    def process(self, data: Any) -> Any:
        return json.loads(data) if isinstance(data, str) else data

class XMLProcessor(DataProcessor):
    def process(self, data: Any) -> Any:
        return parse_xml(data)

class ProcessorFactory:
    """Factory for creating processor instances."""
    
    _processors: Dict[str, Type[DataProcessor]] = {
        'json': JSONProcessor,
        'xml': XMLProcessor,
    }
    
    @classmethod
    def register(cls, name: str, processor_class: Type[DataProcessor]) -> None:
        """Register a processor class."""
        cls._processors[name] = processor_class
    
    @classmethod
    def create(cls, processor_type: str, **kwargs) -> DataProcessor:
        """Create a processor instance."""
        if processor_type not in cls._processors:
            raise ValueError(f"Unknown processor type: {processor_type}")
        
        processor_class = cls._processors[processor_type]
        return processor_class(**kwargs)
```

### **3. Builder Pattern**
**Use Case**: Construct complex objects step by step

```python
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class APIRequest:
    """API request configuration."""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    timeout: float = 30.0

class APIRequestBuilder:
    """Builder for constructing API requests."""
    
    def __init__(self, url: str) -> None:
        self._url = url
        self._method = "GET"
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, Any] = {}
        self._data: Optional[Dict[str, Any]] = None
        self._timeout = 30.0
    
    def method(self, method: str) -> 'APIRequestBuilder':
        """Set HTTP method."""
        self._method = method.upper()
        return self
    
    def header(self, key: str, value: str) -> 'APIRequestBuilder':
        """Add header."""
        self._headers[key] = value
        return self
    
    def param(self, key: str, value: Any) -> 'APIRequestBuilder':
        """Add query parameter."""
        self._params[key] = value
        return self
    
    def json_data(self, data: Dict[str, Any]) -> 'APIRequestBuilder':
        """Set JSON data."""
        self._data = data
        self._headers["Content-Type"] = "application/json"
        return self
    
    def timeout(self, seconds: float) -> 'APIRequestBuilder':
        """Set timeout."""
        self._timeout = seconds
        return self
    
    def build(self) -> APIRequest:
        """Build the API request."""
        return APIRequest(
            url=self._url,
            method=self._method,
            headers=self._headers.copy(),
            params=self._params.copy(),
            data=self._data.copy() if self._data else None,
            timeout=self._timeout
        )
```

---

## 🏛️ **STRUCTURAL PATTERNS**

### **4. Adapter Pattern**
**Use Case**: Make incompatible interfaces work together

```python
from typing import Any, Dict
from abc import ABC, abstractmethod

class ModernAPI(ABC):
    """Modern API interface."""
    
    @abstractmethod
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        pass

class LegacyUserService:
    """Legacy service with different interface."""
    
    def fetch_user_info(self, id: int) -> tuple:
        """Legacy method returning tuple."""
        return (id, "John Doe", "john@example.com", 30)

class UserServiceAdapter(ModernAPI):
    """Adapter to make legacy service compatible with modern interface."""
    
    def __init__(self, legacy_service: LegacyUserService) -> None:
        self._legacy_service = legacy_service
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Adapt legacy interface to modern format."""
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user ID format: {user_id}")
        
        user_tuple = self._legacy_service.fetch_user_info(user_id_int)
        
        return {
            "id": str(user_tuple[0]),
            "name": user_tuple[1],
            "email": user_tuple[2],
            "age": user_tuple[3]
        }
```

### **5. Decorator Pattern**
**Use Case**: Add behavior to objects dynamically

```python
from typing import Any, Callable
from abc import ABC, abstractmethod
import time
import logging

class DataProcessor(ABC):
    """Base data processor interface."""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class BasicProcessor(DataProcessor):
    """Basic data processor implementation."""
    
    def process(self, data: Any) -> Any:
        return data.upper() if isinstance(data, str) else data

class ProcessorDecorator(DataProcessor):
    """Base decorator for processors."""
    
    def __init__(self, processor: DataProcessor) -> None:
        self._processor = processor
    
    def process(self, data: Any) -> Any:
        return self._processor.process(data)

class LoggingDecorator(ProcessorDecorator):
    """Add logging to processor."""
    
    def __init__(self, processor: DataProcessor, logger: logging.Logger) -> None:
        super().__init__(processor)
        self._logger = logger
    
    def process(self, data: Any) -> Any:
        self._logger.info(f"Processing data: {type(data).__name__}")
        result = super().process(data)
        self._logger.info(f"Processing complete: {type(result).__name__}")
        return result

class TimingDecorator(ProcessorDecorator):
    """Add timing to processor."""
    
    def process(self, data: Any) -> Any:
        start_time = time.time()
        result = super().process(data)
        duration = time.time() - start_time
        print(f"Processing took {duration:.3f} seconds")
        return result
```

---

## 🎭 **BEHAVIORAL PATTERNS**

### **6. Observer Pattern**
**Use Case**: Notify multiple objects about state changes

```python
from typing import List, Protocol, Any
from abc import ABC, abstractmethod

class Observer(Protocol):
    """Observer interface."""
    def update(self, event: str, data: Any) -> None: ...

class Subject(ABC):
    """Subject interface."""
    
    def __init__(self) -> None:
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event: str, data: Any = None) -> None:
        """Notify all observers."""
        for observer in self._observers:
            try:
                observer.update(event, data)
            except Exception as e:
                print(f"Observer notification failed: {e}")

class UserManager(Subject):
    """User manager with observer notifications."""
    
    def __init__(self) -> None:
        super().__init__()
        self._users: Dict[str, Dict[str, Any]] = {}
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create user and notify observers."""
        user_id = str(len(self._users) + 1)
        self._users[user_id] = user_data
        
        self.notify("user_created", {"user_id": user_id, "data": user_data})
        return user_id
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> None:
        """Update user and notify observers."""
        if user_id in self._users:
            old_data = self._users[user_id].copy()
            self._users[user_id].update(updates)
            
            self.notify("user_updated", {
                "user_id": user_id,
                "old_data": old_data,
                "new_data": self._users[user_id]
            })

class EmailNotifier:
    """Observer that sends email notifications."""
    
    def update(self, event: str, data: Any) -> None:
        if event == "user_created":
            print(f"Sending welcome email to user {data['user_id']}")
        elif event == "user_updated":
            print(f"Sending update notification to user {data['user_id']}")

class AuditLogger:
    """Observer that logs audit events."""
    
    def update(self, event: str, data: Any) -> None:
        print(f"AUDIT: {event} - {data}")
```

### **7. Strategy Pattern**
**Use Case**: Select algorithm at runtime

```python
from typing import Protocol, Any, Dict
from abc import ABC, abstractmethod

class ValidationStrategy(Protocol):
    """Validation strategy interface."""
    def validate(self, data: Any) -> List[str]: ...

class EmailValidationStrategy:
    """Email validation strategy."""
    
    def validate(self, email: str) -> List[str]:
        errors = []
        if not email:
            errors.append("Email is required")
        elif "@" not in email:
            errors.append("Email must contain @")
        elif "." not in email.split("@")[-1]:
            errors.append("Email domain must contain .")
        return errors

class PasswordValidationStrategy:
    """Password validation strategy."""
    
    def validate(self, password: str) -> List[str]:
        errors = []
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")
        elif not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letter")
        elif not any(c.islower() for c in password):
            errors.append("Password must contain lowercase letter")
        elif not any(c.isdigit() for c in password):
            errors.append("Password must contain digit")
        return errors

class UserValidator:
    """User validator using strategy pattern."""
    
    def __init__(self) -> None:
        self._strategies: Dict[str, ValidationStrategy] = {
            'email': EmailValidationStrategy(),
            'password': PasswordValidationStrategy(),
        }
    
    def register_strategy(self, field: str, strategy: ValidationStrategy) -> None:
        """Register validation strategy for field."""
        self._strategies[field] = strategy
    
    def validate_user(self, user_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate user data using registered strategies."""
        errors = {}
        
        for field, value in user_data.items():
            if field in self._strategies:
                field_errors = self._strategies[field].validate(value)
                if field_errors:
                    errors[field] = field_errors
        
        return errors
```

---

## 🎯 **PATTERN SELECTION GUIDE**

### **By Class Type**

| Class Type | Recommended Patterns | When to Use |
|------------|---------------------|-------------|
| **Data Models** | Builder, Decorator | Complex construction, validation |
| **Service Classes** | Singleton, Strategy, Observer | Shared services, pluggable algorithms |
| **Configuration** | Singleton, Factory | Single instance, type creation |
| **Managers** | Observer, Strategy | Event handling, algorithm selection |
| **Repositories** | Factory, Adapter | Object creation, interface adaptation |

### **By Problem Domain**

| Problem | Pattern | Solution |
|---------|---------|----------|
| **Single Instance** | Singleton | Global access point |
| **Object Creation** | Factory, Builder | Flexible object construction |
| **Interface Mismatch** | Adapter | Make incompatible interfaces work |
| **Add Behavior** | Decorator | Extend functionality dynamically |
| **Event Notification** | Observer | Loose coupling for notifications |
| **Algorithm Selection** | Strategy | Runtime algorithm switching |

---

## 🔧 **PATTERN IMPLEMENTATION CHECKLIST**

### **✅ Singleton Pattern**
- [ ] **Thread safety** - Use locks for thread-safe implementation
- [ ] **Lazy initialization** - Create instance only when needed
- [ ] **Prevent multiple instances** - Override `__new__` method
- [ ] **Initialization guard** - Prevent re-initialization

### **✅ Factory Pattern**
- [ ] **Registration mechanism** - Allow dynamic type registration
- [ ] **Type validation** - Validate registered types
- [ ] **Error handling** - Handle unknown types gracefully
- [ ] **Extensibility** - Easy to add new types

### **✅ Builder Pattern**
- [ ] **Fluent interface** - Method chaining for ease of use
- [ ] **Validation** - Validate required fields before building
- [ ] **Immutability** - Builder doesn't affect built objects
- [ ] **Reset capability** - Allow builder reuse

### **✅ Observer Pattern**
- [ ] **Error isolation** - Observer failures don't affect others
- [ ] **Weak references** - Prevent memory leaks
- [ ] **Event filtering** - Allow selective event subscription
- [ ] **Async support** - Handle async observers properly

---

## 📊 **PATTERN COMBINATION EXAMPLES**

### **Multi-Pattern Integration Example**
```python
class ConfigurationManager:
    """Configuration manager combining Singleton, Observer, and Strategy patterns."""
    
    _instance: Optional['ConfigurationManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ConfigurationManager':
        # Singleton pattern implementation
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._observers: List[Observer] = []  # Observer pattern
            self._loaders: Dict[str, ConfigLoader] = {}  # Strategy pattern
            self._config: Dict[str, Any] = {}
            self._initialized = True
    
    def load_config(self, file_path: str, format_type: str) -> None:
        """Load configuration using strategy and notify observers."""
        loader = self._loaders.get(format_type)
        if not loader:
            raise ValueError(f"Unknown format: {format_type}")
        
        new_config = loader.load(file_path)
        self._config.update(new_config)
        self._notify_observers("config_updated", new_config)
```

---

**💡 Key Principle**: OOP patterns should be selected based on specific design challenges and combined thoughtfully to create maintainable, extensible class hierarchies.
