# Architecture Patterns - HoneyHive Python SDK

**🎯 MISSION: Define consistent architectural patterns that promote maintainability, testability, and scalability**

## Core Architecture Principles

### Multi-Instance Support
- Each tracer instance is independent
- No global singleton pattern
- Thread-safe initialization
- Support for multiple concurrent tracers
- Clear instance lifecycle management

### Separation of Concerns
```python
# Clear layer separation
src/honeyhive/
├── api/           # API client layer
├── tracer/        # OpenTelemetry integration
├── evaluation/    # Evaluation framework
├── models/        # Data models
└── utils/         # Shared utilities
```

### Dependency Injection
```python
# Pass dependencies explicitly for configuration
tracer = HoneyHiveTracer(
    api_key="key",
    project="project",
    server_url="https://custom.honeyhive.ai"
)

# Use factory methods for complex initialization
tracer = HoneyHiveTracer.init(
    api_key="key",
    server_url="https://custom.honeyhive.ai"
)
```

## Design Pattern Implementation

### Graceful Degradation Pattern

```python
def create_session(self) -> Optional[str]:
    """Create session with graceful failure."""
    try:
        response = self.api.create_session()
        return response.session_id
    except Exception as e:
        if not self.test_mode:
            logger.warning(f"Session creation failed: {e}")
        # Continue without session - don't crash host app
        return None
```

**Key Principles:**
- Never crash the host application
- Log warnings for debugging but continue execution
- Provide fallback behavior when possible
- Use test_mode flag to reduce noise during testing

### Decorator Pattern

```python
# Unified decorator for sync/async
@trace(event_type=EventType.model)
def sync_function():
    pass

@trace(event_type=EventType.model)
async def async_function():
    pass

# Class-level decoration
@trace_class
class MyService:
    def method(self):
        pass  # Automatically traced
```

**Implementation Guidelines:**
- Support both synchronous and asynchronous functions
- Preserve function signatures and return types
- Handle exceptions gracefully
- Maintain context across decorated calls

### Context Management Pattern

```python
# Use context managers for resource management
with tracer.start_span("operation") as span:
    # Span automatically closed on exit
    result = perform_operation()
    span.set_attribute("result", result)

# Enrich span context manager
with enrich_span(event_type=EventType.tool):
    # Enrichment applied to current span
    process_data()
```

**Best Practices:**
- Always use context managers for spans
- Ensure proper cleanup on exceptions
- Support nested contexts
- Provide both manual and automatic span management

## Mixin Architecture Pattern

### Base Class with Mixins

```python
# Base class provides core functionality
class HoneyHiveTracerBase:
    def __init__(self, **kwargs):
        self._initialize_core_attributes()
    
    def _initialize_core_attributes(self) -> None:
        """Initialize core tracer attributes."""
        pass

# Mixins provide specialized functionality
class TracerOperationsMixin:
    def start_span(self, name: str) -> Span:
        """Start a new span."""
        pass
    
    def create_event(self, **kwargs) -> Optional[str]:
        """Create an event."""
        pass

class TracerContextMixin:
    def enrich_span(self, **attributes) -> None:
        """Enrich current span."""
        pass
    
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage value."""
        pass

# Composed final class
class HoneyHiveTracer(
    HoneyHiveTracerBase,
    TracerOperationsMixin, 
    TracerContextMixin
):
    """Complete tracer with all functionality."""
    pass
```

**Benefits:**
- Clear separation of concerns
- Easier testing of individual components
- Flexible composition of functionality
- Reduced file sizes and complexity

### Type Safety in Mixins

**🚨 CRITICAL: Use ABC Interface Pattern - Do NOT Use Protocol Methods**

Protocol methods in `TYPE_CHECKING` blocks cause "assignment from no return" errors and provide weaker type safety. Always use ABC interfaces for mixin contracts.

**"Explicit is better than implicit"** - ABC interfaces provide explicit contracts that are enforced at runtime, while Protocol methods rely on implicit structural typing that can fail silently.

```python
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

class TracerContextInterface(ABC):  # pylint: disable=too-few-public-methods
    """Abstract interface for tracer context operations.
    This ABC defines the required methods that must be implemented by any class
    that uses TracerContextMixin. Provides explicit type safety and clear contracts.
    
    Note: too-few-public-methods disabled - ABC interface defines only abstract methods,
    concrete implementations in TracerContextMixin provide public methods.
    """
    
    @abstractmethod
    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Normalize attribute key dynamically for OpenTelemetry compatibility.
        Args:
            key: The attribute key to normalize
        Returns:
            Normalized key string
        """
    
    @abstractmethod
    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Normalize attribute value dynamically for OpenTelemetry compatibility.
        Args:
            value: The attribute value to normalize
        Returns:
            Normalized value
        """

class TracerContextMixin(TracerContextInterface):
    """Mixin providing dynamic context and baggage management for HoneyHive tracer.
    
    This mixin requires implementation of TracerContextInterface abstract methods.
    """
    
    # Type hint for mypy - these attributes will be provided by the composed class
    if TYPE_CHECKING:
        session_api: Optional[Any]
        _session_id: Optional[str]
        _baggage_lock: Any
    
    def enrich_span(self, **attributes) -> None:
        """Enrich current span with normalized attributes."""
        for key, value in attributes.items():
            normalized_key = self._normalize_attribute_key_dynamically(key)
            normalized_value = self._normalize_attribute_value_dynamically(value)
            # Use normalized values...

# Implementation in base class
class HoneyHiveTracerBase:
    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Concrete implementation of attribute key normalization."""
        return key.replace("-", "_").lower()
    
    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Concrete implementation of attribute value normalization."""
        if isinstance(value, (dict, list)):
            return str(value)
        return value

# Final composed class
class HoneyHiveTracer(HoneyHiveTracerBase, TracerContextMixin):
    """Complete tracer with ABC-enforced interface compliance."""
    pass
```

**Benefits of ABC Interface Pattern:**
- **Explicit Contracts**: Abstract methods must be implemented, enforced at runtime
- **Better Type Safety**: MyPy can validate abstract method implementations
- **Clear Documentation**: Abstract methods serve as interface documentation
- **Runtime Validation**: Python raises `TypeError` if abstract methods aren't implemented
- **IDE Support**: Better autocomplete and refactoring support
- **No Pylint Issues**: Eliminates "assignment from no return" errors from Protocol methods

## Dynamic Logic Patterns

### Configuration-Driven Behavior

```python
class DynamicProcessor:
    """Processor that adapts behavior based on configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        self._strategies = self._build_strategies_dynamically(config)
        self._patterns = self._load_patterns_dynamically(config)
    
    def _build_strategies_dynamically(self, config: Dict[str, Any]) -> Dict[str, Callable]:
        """Build processing strategies from configuration."""
        strategies = {}
        
        # Dynamic strategy loading
        for strategy_name, strategy_config in config.get("strategies", {}).items():
            if strategy_config.get("enabled", False):
                strategies[strategy_name] = self._create_strategy(strategy_config)
        
        return strategies
    
    def process(self, data: Any) -> Any:
        """Process data using dynamic strategy selection."""
        for strategy_name, strategy in self._strategies.items():
            if self._should_apply_strategy(strategy_name, data):
                data = strategy(data)
        return data
```

### Pattern-Based Processing

```python
class PatternMatcher:
    """Dynamic pattern matching for extensible processing."""
    
    def __init__(self):
        self._patterns = self._discover_patterns_dynamically()
    
    def _discover_patterns_dynamically(self) -> List[Dict[str, Any]]:
        """Discover processing patterns from multiple sources."""
        patterns = []
        
        # Load from configuration
        patterns.extend(self._load_config_patterns())
        
        # Load from plugins
        patterns.extend(self._load_plugin_patterns())
        
        # Load from environment
        patterns.extend(self._load_env_patterns())
        
        return sorted(patterns, key=lambda p: p.get("priority", 0))
    
    def match(self, input_data: Any) -> Optional[Dict[str, Any]]:
        """Match input against dynamic patterns."""
        for pattern in self._patterns:
            if self._pattern_matches(pattern, input_data):
                return pattern
        return None
```

## Error Handling Architecture

### Exception Hierarchy

```python
class HoneyHiveError(Exception):
    """Base exception for all HoneyHive errors."""

class ConfigurationError(HoneyHiveError):
    """Configuration-related errors."""

class APIError(HoneyHiveError):
    """API communication errors."""
    
class RateLimitError(APIError):
    """Rate limit exceeded."""
    
class AuthenticationError(APIError):
    """Authentication failed."""
```

### Retry Logic Pattern

```python
@retry(
    max_attempts=3,
    backoff_factor=2.0,
    exceptions=(httpx.TimeoutException, httpx.NetworkError)
)
async def make_api_call():
    """API call with exponential backoff retry."""
    return await client.post(url, json=data)
```

### Error Context Management

```python
class ErrorContext:
    """Provide rich context for error handling."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._log_error(exc_type, exc_val, exc_tb)
        return False  # Don't suppress exceptions
    
    def _log_error(self, exc_type, exc_val, exc_tb):
        """Log error with full context."""
        logger.error(
            f"Operation '{self.operation}' failed",
            extra={
                "operation": self.operation,
                "duration": time.time() - self.start_time,
                "error_type": exc_type.__name__,
                "error_message": str(exc_val),
                **self.context
            }
        )

# Usage
with ErrorContext("span_creation", span_name="test", tracer_id="123"):
    span = tracer.start_span("test")
```

## Performance Patterns

### Connection Pooling

```python
# Reuse HTTP connections
connection_pool = ConnectionPool(
    max_connections=config.max_connections,
    max_keepalive_connections=config.max_keepalive_connections,
    keepalive_expiry=config.keepalive_expiry
)

# Share client across requests
self._client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
)
```

### Batching Operations

```python
class BatchSpanProcessor:
    def __init__(self, max_batch_size=512, schedule_delay_millis=5000):
        self.batch = []
        self.max_batch_size = max_batch_size
        
    def on_end(self, span):
        self.batch.append(span)
        if len(self.batch) >= self.max_batch_size:
            self._export_batch()
```

### Lazy Loading Pattern

```python
class LazyResource:
    """Lazy loading for expensive resources."""
    
    def __init__(self, factory: Callable[[], Any]):
        self._factory = factory
        self._resource = None
        self._lock = threading.Lock()
    
    @property
    def resource(self) -> Any:
        """Get resource, creating it if necessary."""
        if self._resource is None:
            with self._lock:
                if self._resource is None:  # Double-check locking
                    self._resource = self._factory()
        return self._resource
```

## Testing Architecture Patterns

### Dependency Injection for Testing

```python
class TestableTracer(HoneyHiveTracer):
    """Tracer with injectable dependencies for testing."""
    
    def __init__(self, api_client=None, span_processor=None, **kwargs):
        self._api_client = api_client
        self._span_processor = span_processor
        super().__init__(**kwargs)
    
    def _create_api_client(self):
        """Create API client, using injected one for tests."""
        return self._api_client or super()._create_api_client()
    
    def _create_span_processor(self):
        """Create span processor, using injected one for tests."""
        return self._span_processor or super()._create_span_processor()

# In tests
def test_tracer_with_mock_api():
    mock_api = Mock()
    tracer = TestableTracer(api_client=mock_api, test_mode=True)
    # Test with controlled API behavior
```

### Factory Pattern for Test Fixtures

```python
class TracerFactory:
    """Factory for creating test tracers with different configurations."""
    
    @staticmethod
    def create_basic_tracer(**overrides):
        """Create basic tracer for testing."""
        config = {
            "api_key": "test-key",
            "project": "test-project", 
            "test_mode": True,
            **overrides
        }
        return HoneyHiveTracer(**config)
    
    @staticmethod
    def create_integration_tracer(**overrides):
        """Create tracer for integration testing."""
        config = {
            "api_key": os.getenv("HH_API_KEY"),
            "project": "integration-test",
            "test_mode": False,
            **overrides
        }
        return HoneyHiveTracer(**config)
```

## References

- **[SDK Design Patterns](sdk-design-patterns.md)** - Specific SDK implementation patterns
- **[Type Safety Standards](type-safety.md)** - Type safety in architectural patterns
- **[Error Handling](error-handling.md)** - Detailed error handling strategies

---

**📝 Next Steps**: Review [SDK Design Patterns](sdk-design-patterns.md) for specific implementation patterns.
