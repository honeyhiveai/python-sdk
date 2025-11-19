# Python Coding Standards

**🎯 Comprehensive Python coding guidelines for the HoneyHive Python SDK**

This document defines the mandatory Python coding standards, patterns, and best practices that ensure consistent, maintainable, and reliable code across the project.

## 🚨 MANDATORY: Sphinx Docstring Format

**All Python code MUST use Sphinx-compatible docstrings:**

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Brief description of the function.
    
    Longer description providing more context about what the function does,
    when to use it, and any important considerations.
    
    :param param1: Description of the first parameter
    :type param1: str
    :param param2: Description of the second parameter with default value
    :type param2: int
    :return: Description of what the function returns
    :rtype: bool
    :raises ValueError: When param1 is empty
    :raises TypeError: When param2 is not an integer
    
    **Example:**
    
    .. code-block:: python
    
        result = example_function("test", 5)
        if result:
            print("Success!")
    
    **Note:**
    
    This function is thread-safe and can be called concurrently.
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

### Docstring Requirements
- **Every module** needs a docstring with purpose and usage
- **Every public function/method** needs a complete Sphinx docstring
- **Every class** needs a docstring with purpose and basic usage
- **Complex logic** requires inline comments
- **Include usage examples** in docstrings using `.. code-block:: python`
- **Use proper Sphinx directives**: `:param:`, `:type:`, `:return:`, `:rtype:`, `:raises:`
- **Private functions** (starting with `_`) should have brief docstrings
- **Type hints are mandatory** and must match docstring types

## 🔧 Code Formatting Standards

### Black Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

**Formatting Rules:**
- **Line length**: 88 characters maximum
- **String quotes**: Double quotes preferred
- **Trailing commas**: Required in multi-line structures
- **Automatic formatting**: Run Black on save (MANDATORY)

### Import Organization (isort)
```python
# Standard library imports
import os
import sys
from typing import Any, Dict, Optional

# Third-party imports
import requests
from opentelemetry import trace

# Local imports
from ..utils.config import config
from ..utils.logger import get_logger
from .span_processor import HoneyHiveSpanProcessor
```

**Import Rules:**
- **Group imports**: Standard library, third-party, local
- **Alphabetical order** within groups
- **Absolute imports** preferred over relative
- **No wildcard imports** (`from module import *`)

## 🏗️ Code Structure Standards

### File Organization
```python
"""Module docstring describing purpose and usage.

This module provides functionality for X, Y, and Z operations
with support for A, B, and C patterns.
"""

# Standard library imports
import os
from typing import Any, Dict

# Third-party imports
import requests

# Local imports
from ..utils.logger import get_logger

# Module-level constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Module-level logger
logger = get_logger(__name__)


class ExampleClass:
    """Class docstring with purpose and usage."""
    
    def __init__(self, param: str) -> None:
        """Initialize the class."""
        self.param = param
    
    def public_method(self) -> str:
        """Public method with full docstring."""
        return self._private_method()
    
    def _private_method(self) -> str:
        """Private method with brief docstring."""
        return f"processed_{self.param}"


def module_function(param: str) -> bool:
    """Module-level function with full docstring."""
    return len(param) > 0
```

### Class Design Patterns
```python
class HoneyHiveComponent:
    """Base pattern for HoneyHive components.
    
    All HoneyHive components should follow this pattern for consistency
    and maintainability across the SDK.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize component with optional configuration.
        
        :param config: Optional configuration dictionary
        :type config: Optional[Dict[str, Any]]
        """
        self.config = config or {}
        self.logger = get_logger(f"honeyhive.{self.__class__.__name__}")
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the component.
        
        :raises RuntimeError: If component is already initialized
        """
        if self._initialized:
            raise RuntimeError("Component already initialized")
        
        self._setup()
        self._initialized = True
        self.logger.debug("Component initialized successfully")
    
    def _setup(self) -> None:
        """Setup component internals (override in subclasses)."""
        pass
    
    def cleanup(self) -> None:
        """Clean up component resources."""
        if self._initialized:
            self._teardown()
            self._initialized = False
            self.logger.debug("Component cleaned up successfully")
    
    def _teardown(self) -> None:
        """Teardown component internals (override in subclasses)."""
        pass
```

## 🔍 Type Safety Requirements

### Type Annotations
```python
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic

# Generic type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Complex type annotations
def process_data(
    items: List[Dict[str, Any]],
    filters: Optional[Dict[str, Union[str, int]]] = None,
    callback: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """Process data items with optional filtering and callback.
    
    :param items: List of data items to process
    :type items: List[Dict[str, Any]]
    :param filters: Optional filters to apply
    :type filters: Optional[Dict[str, Union[str, int]]]
    :param callback: Optional callback for custom processing
    :type callback: Optional[Callable[[Dict[str, Any]], bool]]
    :return: Tuple of processed items and count
    :rtype: Tuple[List[Dict[str, Any]], int]
    """
    # Implementation here
    pass

# Generic classes
class Repository(Generic[T]):
    """Generic repository pattern."""
    
    def __init__(self, item_type: Type[T]) -> None:
        """Initialize repository for specific type.
        
        :param item_type: Type of items stored in repository
        :type item_type: Type[T]
        """
        self.item_type = item_type
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        """Add item to repository.
        
        :param item: Item to add
        :type item: T
        """
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        """Get all items from repository.
        
        :return: List of all items
        :rtype: List[T]
        """
        return self._items.copy()
```

### EventType Usage (HoneyHive-Specific)
```python
# ✅ CORRECT: Proper enum imports and usage
from honeyhive.models import EventType

@trace(event_type=EventType.model)  # Type-safe enum value
def llm_function():
    """Process LLM requests."""
    pass

@trace(event_type=EventType.tool)   # Individual function/utility
def utility_function():
    """Process individual data operations."""
    pass

@trace(event_type=EventType.chain)  # Multi-step workflow
def workflow_function():
    """Orchestrate multiple operations."""
    pass

# ❌ INCORRECT: String literals (deprecated, breaks type safety)
@trace(event_type="model")  # Don't use strings
```

## 🛡️ Error Handling Patterns

### Exception Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def robust_operation(param: str, timeout: float = 30.0) -> Optional[str]:
    """Perform operation with comprehensive error handling.
    
    :param param: Operation parameter
    :type param: str
    :param timeout: Operation timeout in seconds
    :type timeout: float
    :return: Operation result or None if failed
    :rtype: Optional[str]
    :raises ValueError: If param is invalid
    :raises TimeoutError: If operation times out
    """
    # Input validation
    if not param or not isinstance(param, str):
        raise ValueError("param must be a non-empty string")
    
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    
    try:
        # Attempt operation
        result = perform_operation(param, timeout)
        logger.debug(f"Operation successful: {param}")
        return result
        
    except ConnectionError as e:
        logger.warning(f"Connection failed for {param}: {e}")
        return None
        
    except TimeoutError as e:
        logger.error(f"Operation timed out for {param}: {e}")
        raise  # Re-raise timeout errors
        
    except Exception as e:
        logger.error(f"Unexpected error for {param}: {e}", exc_info=True)
        return None

def safe_conversion(value: Any, default: float = 30.0) -> float:
    """Safely convert value to float with fallback.
    
    :param value: Value to convert
    :type value: Any
    :param default: Default value if conversion fails
    :type default: float
    :return: Converted float value
    :rtype: float
    """
    try:
        result = float(value)
        if result <= 0:
            logger.warning(f"Invalid value: {value}, using default")
            return default
        return result
    except (ValueError, TypeError):
        logger.warning(f"Invalid value: {value}, using default")
        return default
```

### Graceful Degradation
```python
def optional_feature(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data with optional enhancement feature.
    
    Falls back gracefully if enhancement fails.
    
    :param data: Input data to process
    :type data: Dict[str, Any]
    :return: Processed data (enhanced or basic)
    :rtype: Dict[str, Any]
    """
    # Basic processing (always works)
    result = basic_processing(data)
    
    # Optional enhancement (may fail)
    try:
        enhanced_result = enhance_data(result)
        logger.debug("Data enhancement successful")
        return enhanced_result
    except Exception as e:
        logger.warning(f"Enhancement failed, using basic result: {e}")
        return result  # Graceful fallback
```

## 🧪 Testing Patterns

### Unit Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict

from honeyhive.tracer.span_processor import HoneyHiveSpanProcessor

class TestHoneyHiveSpanProcessor:
    """Test suite for HoneyHiveSpanProcessor."""
    
    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.processor = HoneyHiveSpanProcessor()
        self.mock_span = Mock()
        self.mock_context = Mock()
    
    def test_initialization(self) -> None:
        """Test processor initialization."""
        processor = HoneyHiveSpanProcessor()
        assert processor is not None
        assert hasattr(processor, 'on_start')
        assert hasattr(processor, 'on_end')
    
    @pytest.mark.parametrize("event_type,expected", [
        ("model", "model"),
        ("tool", "tool"), 
        ("chain", "chain"),
        ("unknown", "tool"),  # Default fallback
    ])
    def test_event_type_detection(self, event_type: str, expected: str) -> None:
        """Test event type detection with various inputs.
        
        :param event_type: Input event type
        :type event_type: str
        :param expected: Expected output event type
        :type expected: str
        """
        result = self.processor._infer_event_type_from_span_name(event_type)
        assert result == expected
    
    def test_error_handling(self) -> None:
        """Test processor handles errors gracefully."""
        # Test with invalid input
        with pytest.raises(ValueError, match="Invalid span"):
            self.processor.on_start(None, self.mock_context)
    
    @patch('honeyhive.tracer.span_processor.logger')
    def test_logging(self, mock_logger: Mock) -> None:
        """Test that appropriate logging occurs.
        
        :param mock_logger: Mocked logger instance
        :type mock_logger: Mock
        """
        self.processor.on_start(self.mock_span, self.mock_context)
        mock_logger.debug.assert_called()
```

## 🏛️ Architecture Patterns

### Multi-Instance Pattern
```python
class HoneyHiveTracer:
    """Multi-instance tracer implementation.
    
    Each instance is independent and thread-safe, supporting
    multiple concurrent tracer instances in the same process.
    """
    
    def __init__(self, api_key: str, project: str) -> None:
        """Initialize tracer instance.
        
        :param api_key: HoneyHive API key
        :type api_key: str
        :param project: Project identifier
        :type project: str
        """
        self.api_key = api_key
        self.project = project
        self._lock = threading.Lock()
        self._initialized = False
    
    @classmethod
    def init(cls, **kwargs: Any) -> 'HoneyHiveTracer':
        """Factory method for tracer creation.
        
        :param kwargs: Tracer configuration parameters
        :type kwargs: Any
        :return: Configured tracer instance
        :rtype: HoneyHiveTracer
        """
        instance = cls(**kwargs)
        instance._initialize()
        return instance
```

### Registry Pattern
```python
import weakref
from typing import Dict, Optional, WeakValueDictionary

class TracerRegistry:
    """Registry for tracer instances using weak references."""
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._tracers: WeakValueDictionary[str, HoneyHiveTracer] = (
            weakref.WeakValueDictionary()
        )
    
    def register(self, tracer: HoneyHiveTracer) -> str:
        """Register tracer instance.
        
        :param tracer: Tracer to register
        :type tracer: HoneyHiveTracer
        :return: Registration ID
        :rtype: str
        """
        tracer_id = f"{tracer.project}_{id(tracer)}"
        self._tracers[tracer_id] = tracer
        return tracer_id
    
    def get(self, tracer_id: str) -> Optional[HoneyHiveTracer]:
        """Get tracer by ID.
        
        :param tracer_id: Tracer registration ID
        :type tracer_id: str
        :return: Tracer instance or None
        :rtype: Optional[HoneyHiveTracer]
        """
        return self._tracers.get(tracer_id)
```

### Dynamic Logic Pattern

**🚨 MANDATORY: Prefer dynamic logic over static patterns wherever possible**

Dynamic logic provides extensibility, maintainability, and adaptability. Replace hardcoded mappings, static lists, and fixed patterns with configuration-driven, discoverable systems.

```python
# ❌ BAD: Static hardcoded mapping
STATIC_ATTRIBUTES = {
    "experiment_id": "honeyhive.experiment_id",
    "experiment_name": "honeyhive.experiment_name",
    "experiment_variant": "honeyhive.experiment_variant",
}

def process_attributes_static(config: Config) -> Dict[str, str]:
    """Static attribute processing (inflexible)."""
    attributes = {}
    for config_attr, span_attr in STATIC_ATTRIBUTES.items():
        value = getattr(config, config_attr, None)
        if value:
            attributes[span_attr] = str(value)
    return attributes

# ✅ GOOD: Dynamic discovery and processing
def process_attributes_dynamic(config: Config) -> Dict[str, str]:
    """Dynamic attribute processing with discovery.
    
    :param config: Configuration object to process
    :type config: Config
    :return: Processed attributes dictionary
    :rtype: Dict[str, str]
    """
    attributes = {}
    
    # Dynamically discover all experiment-related attributes
    for attr_name in dir(config):
        if attr_name.startswith("experiment_") and not attr_name.startswith("_"):
            value = getattr(config, attr_name, None)
            if value is not None:
                # Dynamic attribute name generation
                span_attr = f"honeyhive.{attr_name}"
                attributes[span_attr] = str(value)
                
    return attributes

# ✅ EXCELLENT: Pattern-based dynamic processing
def process_attributes_pattern_based(
    config: Config, 
    patterns: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """Pattern-based dynamic attribute processing.
    
    :param config: Configuration object to process
    :type config: Config
    :param patterns: Optional custom patterns for attribute mapping
    :type patterns: Optional[Dict[str, str]]
    :return: Processed attributes dictionary
    :rtype: Dict[str, str]
    """
    # Default patterns can be overridden
    default_patterns = {
        "experiment_": "honeyhive.",
        "session_": "honeyhive.session.",
        "user_": "honeyhive.user.",
    }
    
    active_patterns = patterns or default_patterns
    attributes = {}
    
    for attr_name in dir(config):
        if attr_name.startswith("_"):
            continue
            
        value = getattr(config, attr_name, None)
        if value is None:
            continue
            
        # Apply dynamic patterns
        for prefix, span_prefix in active_patterns.items():
            if attr_name.startswith(prefix):
                span_attr = f"{span_prefix}{attr_name}"
                attributes[span_attr] = str(value)
                break
                
    return attributes
```

**Dynamic Logic Benefits:**
- **Extensibility**: New configuration attributes are automatically discovered
- **Maintainability**: No need to update hardcoded mappings when adding features
- **Flexibility**: Behavior can be customized through configuration
- **Future-Proof**: Adapts to new requirements without code changes
- **DRY Principle**: Eliminates repetitive mapping code

**When to Use Dynamic Logic:**
- ✅ Attribute processing and mapping
- ✅ Configuration discovery and validation
- ✅ Provider detection and classification
- ✅ Plugin and extension systems
- ✅ Data transformation pipelines
- ✅ Semantic convention compatibility

**When Static Logic is Acceptable:**
- ❌ Performance-critical hot paths (after profiling proves necessity)
- ❌ Security-sensitive operations requiring explicit control
- ❌ Simple, stable mappings that will never change
- ❌ Type safety requirements that dynamic logic cannot satisfy

## 📊 Performance Considerations

### Efficient Patterns
```python
# ✅ GOOD: Use generators for large datasets
def process_large_dataset(items: Iterable[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """Process large dataset efficiently using generators.
    
    :param items: Input items to process
    :type items: Iterable[Dict[str, Any]]
    :return: Generator of processed items
    :rtype: Iterator[Dict[str, Any]]
    """
    for item in items:
        if should_process(item):
            yield process_item(item)

# ✅ GOOD: Use __slots__ for memory efficiency
class SpanData:
    """Memory-efficient span data storage."""
    
    __slots__ = ('name', 'start_time', 'end_time', 'attributes')
    
    def __init__(self, name: str) -> None:
        """Initialize span data.
        
        :param name: Span name
        :type name: str
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, Any] = {}

# ✅ GOOD: Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param: str) -> str:
    """Expensive computation with caching.
    
    :param param: Computation parameter
    :type param: str
    :return: Computation result
    :rtype: str
    """
    # Expensive operation here
    return f"computed_{param}"
```

## 🔧 Configuration Patterns

### Environment-Driven Configuration
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Application configuration with environment variable support."""
    
    api_key: Optional[str] = None
    project: Optional[str] = None
    source: str = "dev"
    test_mode: bool = False
    
    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        self.api_key = self.api_key or os.getenv("HH_API_KEY")
        self.project = self.project or os.getenv("HH_PROJECT")
        self.source = os.getenv("HH_SOURCE", self.source)
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
    
    def validate(self) -> None:
        """Validate configuration completeness.
        
        :raises ValueError: If required configuration is missing
        """
        if not self.api_key:
            raise ValueError("API key is required (set HH_API_KEY)")
        if not self.project:
            raise ValueError("Project is required (set HH_PROJECT)")
```

## 🤖 **AI Assistant Code Generation Requirements**

**MANDATORY: AI assistants must generate code that meets these exact standards**

### **Complete Function Generation Template**
```python
def function_name(
    param1: Type1,
    param2: Type2,
    *,
    optional_param: Optional[Type3] = None,
    keyword_param: Type4 = default_value
) -> ReturnType:
    """Brief description of what the function does.
    
    Detailed description providing context, usage patterns, and any
    important considerations for using this function.
    
    :param param1: Description of the first parameter
    :type param1: Type1
    :param param2: Description of the second parameter
    :type param2: Type2
    :param optional_param: Description of optional parameter
    :type optional_param: Optional[Type3]
    :param keyword_param: Description of keyword parameter
    :type keyword_param: Type4
    :return: Description of what the function returns
    :rtype: ReturnType
    :raises SpecificError: When specific condition occurs
    :raises ValueError: When validation fails
    
    **Example:**
    
    .. code-block:: python
    
        result = function_name("value", 42, keyword_param="test")
        if result:
            print("Success!")
    
    **Note:**
    
    This function is thread-safe and handles graceful degradation.
    """
    # Type annotation for local variables
    processed_data: Dict[str, Any] = {}
    
    try:
        # Main implementation with error handling
        if not param1:
            raise ValueError("param1 cannot be empty")
        
        # Business logic here
        processed_data = perform_operation(param1, param2)
        
        return processed_data
        
    except SpecificError as e:
        # Handle known exceptions with appropriate logging
        safe_log(logger, "warning", f"Known issue in {function_name.__name__}: {e}")
        raise  # Re-raise if caller should handle
        
    except Exception as e:
        # Handle unexpected exceptions with graceful degradation
        safe_log(logger, "debug", f"Unexpected error in {function_name.__name__}: {e}")
        return default_return_value  # Safe fallback
```

### **MANDATORY Code Generation Checklist**

**AI assistants MUST verify ALL items before generating code:**

#### **Type Annotations (100% Required)**
- [ ] **Function signature**: Complete parameter and return type annotations
- [ ] **Local variables**: Type annotations for all variables (`var: Type = value`)
- [ ] **Complex types**: Use `Dict[str, Any]`, `List[Type]`, `Optional[Type]` appropriately
- [ ] **Import statements**: Include all necessary typing imports

#### **Documentation (100% Required)**
- [ ] **Sphinx docstring**: Complete with `:param:`, `:type:`, `:return:`, `:rtype:`
- [ ] **Examples**: Working code examples in `.. code-block:: python`
- [ ] **Error documentation**: All raised exceptions documented with `:raises:`
- [ ] **Context**: Explain when and why to use the function

#### **Error Handling (100% Required)**
- [ ] **Graceful degradation**: Never crash host application
- [ ] **Specific exceptions**: Catch known exceptions first
- [ ] **Generic exception**: Always catch `Exception` as final fallback
- [ ] **Safe logging**: Use `safe_log()` utility, not print statements
- [ ] **Appropriate returns**: Return sensible defaults or None on errors

#### **Code Quality (100% Required)**
- [ ] **Keyword-only args**: Use `*,` for functions with >3 parameters
- [ ] **Default values**: Provide sensible defaults for optional parameters
- [ ] **Validation**: Input validation with clear error messages
- [ ] **Thread safety**: Consider concurrent usage patterns

### **AI Assistant Anti-Patterns (NEVER Generate)**

#### **❌ Incomplete Type Annotations**
```python
# NEVER generate code like this:
def process_events(events, tracer, batch_size=100):  # ❌ No type hints
    items = []  # ❌ No type annotation
    return items  # ❌ No return type
```

#### **❌ Missing Error Handling**
```python
# NEVER generate code like this:
def risky_operation(data):  # ❌ No error handling
    return external_api_call(data)  # ❌ Can crash host app
```

#### **❌ Incomplete Documentation**
```python
# NEVER generate code like this:
def complex_function(a, b, c):
    """Does something."""  # ❌ Incomplete docstring
    pass
```

#### **❌ Print Statements**
```python
# NEVER generate code like this:
def debug_function(data):
    print(f"Processing: {data}")  # ❌ Use safe_log() instead
    return process(data)
```

### **AI Assistant Quality Verification**

**Before submitting generated code, AI assistants MUST:**

1. **Verify imports**: Check against current `src/honeyhive/__init__.py`
2. **Test type annotations**: Ensure mypy compliance
3. **Validate examples**: Ensure all code examples work
4. **Check error handling**: Verify graceful degradation patterns
5. **Review documentation**: Ensure Sphinx compatibility

## 📚 Related Standards

- **[Docstring Standards](docstring-standards.md)** - Detailed Sphinx docstring requirements
- **[Type Safety](type-safety.md)** - Advanced type annotation patterns
- **[Error Handling](error-handling.md)** - Comprehensive error handling strategies
- **[Code Quality](../development/code-quality.md)** - Quality gates and tool configuration

---

**📝 Next Steps**: Review [Type Safety](type-safety.md) and [Error Handling](error-handling.md) for advanced Python patterns.
