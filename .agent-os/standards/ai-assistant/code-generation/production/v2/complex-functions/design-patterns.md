# Complex Functions - Design Patterns (v2)

## 🎯 **DESIGN PATTERNS FOR COMPLEX FUNCTIONS**

**Purpose**: Essential design patterns for robust complex function implementation.

**Focus**: Proven patterns that enhance reliability, maintainability, and testability.

---

## 🏗️ **ESSENTIAL PATTERNS**

### **1. Strategy Pattern**
**Use Case**: Multiple algorithm implementations with runtime selection

```python
from typing import Protocol, Any

class ProcessingStrategy(Protocol):
    def process(self, data: Any) -> Any: ...

def complex_processor(
    data: Any,
    *,
    strategy: ProcessingStrategy,
    fallback_strategy: Optional[ProcessingStrategy] = None
) -> Any:
    """Process data with strategy pattern and fallback."""
    try:
        return strategy.process(data)
    except Exception as e:
        if fallback_strategy:
            logger.warning(f"Primary strategy failed: {e}, using fallback")
            return fallback_strategy.process(data)
        raise
```

### **2. Circuit Breaker Pattern**
**Use Case**: External service protection with failure detection

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self._record_failure()
            raise

    def _record_failure(self) -> None:
        """Record failure and update circuit state."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### **3. Retry with Exponential Backoff**
**Use Case**: Transient failure handling with intelligent delays

```python
import random
import asyncio
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
```

### **4. Resource Context Manager**
**Use Case**: Automatic resource management with cleanup

```python
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

@contextmanager
def managed_resource(
    resource_config: Dict[str, Any],
    *,
    cleanup_timeout: float = 30.0
) -> Generator[Any, None, None]:
    """Context manager for resource lifecycle management."""
    resource = None
    try:
        resource = acquire_resource(resource_config)
        logger.info(f"Resource acquired: {resource.id}")
        yield resource
    except Exception as e:
        logger.error(f"Resource operation failed: {e}")
        raise
    finally:
        if resource:
            try:
                release_resource(resource, timeout=cleanup_timeout)
                logger.info(f"Resource released: {resource.id}")
            except Exception as cleanup_error:
                logger.error(f"Resource cleanup failed: {cleanup_error}")

@asynccontextmanager
async def async_managed_resource(
    resource_config: Dict[str, Any]
) -> AsyncGenerator[Any, None]:
    """Async context manager for resource management."""
    resource = None
    try:
        resource = await acquire_resource_async(resource_config)
        yield resource
    finally:
        if resource:
            await release_resource_async(resource)
```

### **5. Command Pattern**
**Use Case**: Encapsulate operations for undo/redo, queuing, logging

```python
from abc import ABC, abstractmethod
from typing import Any, List

class Command(ABC):
    """Abstract command interface."""
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

class CommandInvoker:
    """Command invoker with history and undo support."""
    
    def __init__(self):
        self._history: List[Command] = []
        self._current_position = -1
    
    def execute_command(self, command: Command) -> Any:
        """Execute command and add to history."""
        # Remove any commands after current position
        self._history = self._history[:self._current_position + 1]
        
        # Execute and add to history
        result = command.execute()
        self._history.append(command)
        self._current_position += 1
        
        return result
    
    def undo(self) -> bool:
        """Undo the last command."""
        if self._current_position >= 0:
            command = self._history[self._current_position]
            command.undo()
            self._current_position -= 1
            return True
        return False
    
    def redo(self) -> bool:
        """Redo the next command."""
        if self._current_position < len(self._history) - 1:
            self._current_position += 1
            command = self._history[self._current_position]
            command.execute()
            return True
        return False
```

---

## 🎯 **PATTERN SELECTION GUIDE**

### **By Use Case**

| Use Case | Recommended Pattern | When to Use |
|----------|-------------------|-------------|
| **Multiple Algorithms** | Strategy | Runtime algorithm selection |
| **External Service Calls** | Circuit Breaker | Prevent cascade failures |
| **Transient Failures** | Retry with Backoff | Network/temporary errors |
| **Resource Management** | Context Manager | File/connection/memory cleanup |
| **Operation Encapsulation** | Command | Undo/redo, queuing, logging |
| **State Management** | State Machine | Complex state transitions |
| **Event Handling** | Observer | Decoupled event notifications |

### **By Complexity Level**

| Complexity | Essential Patterns | Optional Patterns |
|------------|-------------------|-------------------|
| **Low Complex** | Context Manager | Strategy |
| **Medium Complex** | + Retry, Circuit Breaker | Command |
| **High Complex** | + Strategy, Observer | State Machine |

---

## 🔧 **PATTERN IMPLEMENTATION CHECKLIST**

### **✅ Strategy Pattern**
- [ ] **Protocol defined** - Clear interface for strategies
- [ ] **Fallback strategy** - Handle strategy failures
- [ ] **Strategy validation** - Ensure strategy compatibility
- [ ] **Performance consideration** - Strategy selection overhead

### **✅ Circuit Breaker Pattern**
- [ ] **Failure threshold** - Appropriate failure count
- [ ] **Timeout configuration** - Recovery time window
- [ ] **State transitions** - Proper state management
- [ ] **Monitoring integration** - Circuit breaker metrics

### **✅ Retry Pattern**
- [ ] **Exception filtering** - Only retry appropriate exceptions
- [ ] **Backoff strategy** - Exponential with jitter
- [ ] **Max retry limit** - Prevent infinite loops
- [ ] **Logging integration** - Track retry attempts

### **✅ Context Manager Pattern**
- [ ] **Resource acquisition** - Proper resource initialization
- [ ] **Exception handling** - Cleanup on errors
- [ ] **Timeout handling** - Cleanup timeout configuration
- [ ] **Async support** - Async context managers where needed

---

## 📊 **PATTERN COMBINATION STRATEGIES**

### **Resilient API Client Pattern**
```python
class ResilientAPIClient:
    """API client combining multiple patterns for maximum reliability."""
    
    def __init__(self, config: APIConfig):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.failure_threshold,
            timeout=config.circuit_timeout
        )
        self.retry_config = config.retry_config
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make API request with circuit breaker and retry protection."""
        return await self.circuit_breaker.call(
            self._execute_request, request
        )
    
    async def _execute_request(self, request: APIRequest) -> APIResponse:
        """Execute the actual API request."""
        async with self._get_http_client() as client:
            response = await client.request(
                method=request.method,
                url=request.url,
                **request.kwargs
            )
            return self._parse_response(response)
```

### **Processing Pipeline Pattern**
```python
class ProcessingPipeline:
    """Data processing pipeline with strategy and command patterns."""
    
    def __init__(self):
        self.strategies: Dict[str, ProcessingStrategy] = {}
        self.command_invoker = CommandInvoker()
    
    def register_strategy(self, name: str, strategy: ProcessingStrategy):
        """Register a processing strategy."""
        self.strategies[name] = strategy
    
    async def process_with_strategy(
        self, 
        data: Any, 
        strategy_name: str,
        *,
        fallback_strategy: Optional[str] = None
    ) -> Any:
        """Process data using specified strategy with optional fallback."""
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        fallback = None
        if fallback_strategy:
            fallback = self.strategies.get(fallback_strategy)
        
        command = ProcessingCommand(data, strategy, fallback)
        return await self.command_invoker.execute_command(command)
```

---

**💡 Key Principle**: Design patterns should be selected based on specific requirements and combined thoughtfully to create robust, maintainable complex functions.
