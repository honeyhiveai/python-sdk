# Complex Functions - Generation Phase

## 🎯 **PHASE 4: CODE GENERATION FOR COMPLEX FUNCTIONS**

**Purpose**: Generate high-quality complex functions using proven templates and patterns.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, comprehensive docstrings.

---

## 📋 **MANDATORY GENERATION COMMANDS**

### **Command 1: Select Template & Patterns**
```bash
# AI MUST select appropriate template and design patterns
echo "Template selected: [TEMPLATE_NAME] from complex-functions/templates.md"
echo "Design patterns applied: [PATTERN_LIST]"
```

**Required Output:**
- Specific template name and justification
- Design patterns to be implemented
- Template customization strategy
- Pattern integration approach

### **Command 2: Generate Core Implementation**
```bash
# AI MUST generate core function implementation
echo "Core implementation generated with primary responsibility handling"
```

**Required Output:**
- Complete primary function logic
- Core algorithm implementation
- Main execution path coded
- Primary responsibility fulfilled

### **Command 3: Implement Error Handling**
```bash
# AI MUST implement comprehensive error handling
echo "Error handling implemented: [ERROR_TYPES] with [RECOVERY_STRATEGIES]"
```

**Required Output:**
- All identified error types handled
- Recovery mechanisms implemented
- Appropriate exception types used
- Error logging integrated

### **Command 4: Add State Management**
```bash
# AI MUST implement state management requirements
echo "State management implemented: [STATE_VARIABLES] with [PERSISTENCE_STRATEGY]"
```

**Required Output:**
- State variables properly managed
- State validation implemented
- Thread safety considerations addressed
- State persistence handled

### **Command 5: Integrate External Dependencies**
```bash
# AI MUST integrate all external dependencies safely
echo "Dependencies integrated: [DEPENDENCY_LIST] with [FALLBACK_STRATEGIES]"
```

**Required Output:**
- All dependencies properly integrated
- Dependency injection patterns used
- Fallback mechanisms implemented
- Resource cleanup handled

---

## 🛠️ **PROVEN COMPLEX FUNCTION TEMPLATES**

**MANDATORY: Use existing proven templates from `templates.md`:**

### **📝 Available Templates:**
1. **API Client Template** - HTTP requests with retry logic and error handling
2. **Data Pipeline Template** - Multi-stage data processing with error aggregation
3. **Configuration Manager Template** - Complex configuration loading and validation
4. **Event Handler Template** - Asynchronous event processing with state management
5. **Resource Manager Template** - Resource allocation and cleanup with monitoring

### **🎯 Template Selection Criteria:**

| Function Type | Template | Use When |
|---------------|----------|----------|
| **API Integration** | API Client | External HTTP/REST API interactions |
| **Data Processing** | Data Pipeline | Multi-step data transformations |
| **Configuration** | Configuration Manager | Complex config loading/validation |
| **Event Processing** | Event Handler | Asynchronous event handling |
| **Resource Management** | Resource Manager | Resource allocation/cleanup |

---

## 🏗️ **DESIGN PATTERNS FOR COMPLEX FUNCTIONS**

### **Essential Patterns to Apply:**

#### **1. Strategy Pattern**
```python
# Use for multiple algorithm implementations
from typing import Protocol

class ProcessingStrategy(Protocol):
    def process(self, data: Any) -> Any: ...

def complex_processor(
    data: Any,
    *,
    strategy: ProcessingStrategy,
    fallback_strategy: Optional[ProcessingStrategy] = None
) -> Any:
    try:
        return strategy.process(data)
    except Exception as e:
        if fallback_strategy:
            logger.warning(f"Primary strategy failed: {e}, using fallback")
            return fallback_strategy.process(data)
        raise
```

#### **2. Circuit Breaker Pattern**
```python
# Use for external service calls
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

def api_call_with_circuit_breaker(
    url: str,
    *,
    circuit_breaker: CircuitBreaker,
    **kwargs
) -> Any:
    if circuit_breaker.state == "open":
        if time.time() - circuit_breaker.last_failure_time > circuit_breaker.timeout:
            circuit_breaker.state = "half-open"
        else:
            raise CircuitBreakerOpenError("Circuit breaker is open")
    
    try:
        response = make_request(url, **kwargs)
        if circuit_breaker.state == "half-open":
            circuit_breaker.state = "closed"
            circuit_breaker.failure_count = 0
        return response
    except Exception as e:
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = time.time()
        
        if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
            circuit_breaker.state = "open"
        
        raise
```

#### **3. Retry with Exponential Backoff**
```python
# Use for transient failure handling
import time
import random
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator
```

#### **4. Resource Context Manager**
```python
# Use for resource management
from contextlib import contextmanager
from typing import Generator, Any

@contextmanager
def managed_resource(
    resource_config: Dict[str, Any],
    *,
    cleanup_timeout: float = 30.0
) -> Generator[Any, None, None]:
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
```

---

## 🔧 **GENERATION PROCESS**

### **Step 1: Template Customization**
**Apply comprehensive customizations to selected template:**

1. **Function Signature**: Adapt parameters for specific requirements
2. **Type Annotations**: Add complex type hints (Union, Optional, Generic)
3. **Docstring**: Create comprehensive documentation
4. **Core Logic**: Implement primary responsibility
5. **Error Handling**: Add exception handling and recovery
6. **State Management**: Implement state variables and persistence
7. **Dependencies**: Integrate external systems safely
8. **Logging**: Add structured logging throughout
9. **Performance**: Optimize for expected load
10. **Testing Hooks**: Add testability features

### **Step 2: Quality Integration**
**Ensure generated code includes:**

1. **Type Safety**: 100% type annotation coverage
2. **Documentation**: Comprehensive docstrings with examples
3. **Error Resilience**: Robust error handling and recovery
4. **Resource Management**: Proper cleanup and resource handling
5. **Observability**: Logging, metrics, and monitoring hooks
6. **Testability**: Dependency injection and test-friendly design
7. **Performance**: Efficient algorithms and resource usage
8. **Security**: Input validation and secure practices

### **Step 3: Pattern Integration**
**Integrate design patterns appropriately:**

1. **Pattern Selection**: Choose patterns based on requirements
2. **Pattern Implementation**: Implement patterns correctly
3. **Pattern Composition**: Combine patterns effectively
4. **Pattern Testing**: Ensure patterns work as expected

### **Step 4: Code Verification**
**Verify generated code meets all criteria:**

1. **Template Compliance**: Follows selected template structure
2. **Requirements Coverage**: Meets all analysis phase requirements
3. **Pattern Implementation**: Design patterns correctly applied
4. **Quality Standards**: Ready for quality enforcement phase
5. **Integration Ready**: Can be integrated into larger system

---

## 📝 **GENERATION EXAMPLES**

### **Example 1: API Client with Retry Logic**
```python
import time
import logging
import requests
from typing import Dict, Any, Optional, Union, List
from contextlib import contextmanager

from ..models.errors import APIError, CircuitBreakerOpenError
from ..utils.auth import get_auth_headers
from ..utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

def make_api_request(
    url: str,
    method: str = "GET",
    *,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    circuit_breaker: Optional[CircuitBreaker] = None
) -> Union[Dict[str, Any], List[Any], str]:
    """Make HTTP API request with retry logic and circuit breaker.
    
    Implements exponential backoff retry strategy with circuit breaker
    pattern for resilient API communication. Handles authentication,
    request/response logging, and various error conditions.
    
    Args:
        url: Target API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request payload for POST/PUT requests
        headers: Additional HTTP headers
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        circuit_breaker: Circuit breaker instance for failure handling
        
    Returns:
        Parsed JSON response as dict/list, or raw string for non-JSON
        
    Raises:
        APIError: For API-specific errors with context
        CircuitBreakerOpenError: When circuit breaker is open
        requests.RequestException: For network-level errors
        ValueError: For invalid parameters
        
    Example:
        >>> response = make_api_request(
        ...     "https://api.example.com/users",
        ...     method="POST",
        ...     data={"name": "John Doe"},
        ...     max_retries=3
        ... )
        >>> print(response["id"])
        12345
    """
    # Input validation
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    if timeout <= 0:
        raise ValueError("Timeout must be positive")
    
    if max_retries < 0:
        raise ValueError("Max retries cannot be negative")
    
    # Check circuit breaker
    if circuit_breaker and circuit_breaker.is_open():
        raise CircuitBreakerOpenError(f"Circuit breaker open for {url}")
    
    # Prepare request
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    
    # Add authentication
    try:
        auth_headers = get_auth_headers()
        request_headers.update(auth_headers)
    except Exception as auth_error:
        logger.warning(f"Authentication failed: {auth_error}")
        # Continue without auth headers for public endpoints
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"API request attempt {attempt + 1}: {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                json=data if data else None,
                headers=request_headers,
                timeout=timeout
            )
            
            # Log response
            logger.debug(f"API response: {response.status_code} from {url}")
            
            # Handle HTTP errors
            response.raise_for_status()
            
            # Parse response
            try:
                result = response.json()
            except ValueError:
                # Non-JSON response
                result = response.text
            
            # Success - reset circuit breaker
            if circuit_breaker:
                circuit_breaker.record_success()
            
            logger.info(f"API request successful: {method} {url}")
            return result
            
        except requests.exceptions.Timeout as e:
            last_exception = APIError(f"Request timeout for {url}: {e}")
            logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
            
        except requests.exceptions.ConnectionError as e:
            last_exception = APIError(f"Connection error for {url}: {e}")
            logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
            
        except requests.exceptions.HTTPError as e:
            # Don't retry client errors (4xx)
            if 400 <= response.status_code < 500:
                error_msg = f"Client error {response.status_code} for {url}: {e}"
                logger.error(error_msg)
                raise APIError(error_msg) from e
            
            # Retry server errors (5xx)
            last_exception = APIError(f"Server error {response.status_code} for {url}: {e}")
            logger.warning(f"Server error on attempt {attempt + 1}: {e}")
            
        except Exception as e:
            last_exception = APIError(f"Unexpected error for {url}: {e}")
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
        
        # Record failure in circuit breaker
        if circuit_breaker:
            circuit_breaker.record_failure()
        
        # Don't sleep after last attempt
        if attempt < max_retries:
            delay = backoff_factor * (2 ** attempt)
            logger.info(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    
    # All retries exhausted
    logger.error(f"API request failed after {max_retries + 1} attempts: {url}")
    raise last_exception
```

### **Example 2: Data Processing Pipeline**
```python
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from contextlib import contextmanager

from ..models.errors import ProcessingError, ValidationError
from ..utils.cache import get_cache_client
from ..transformations import get_transformer

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of data processing pipeline."""
    processed_data: List[Dict[str, Any]]
    errors: List[ProcessingError]
    statistics: Dict[str, Any]

def process_data_pipeline(
    input_data: List[Dict[str, Any]],
    *,
    transformations: List[str],
    batch_size: int = 100,
    enable_caching: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    error_threshold: float = 0.1,
    max_workers: int = 4
) -> ProcessingResult:
    """Process data through multiple transformation stages with error handling.
    
    Implements a robust data processing pipeline with batching, caching,
    progress tracking, and comprehensive error handling. Supports parallel
    processing and graceful degradation on errors.
    
    Args:
        input_data: List of data items to process
        transformations: List of transformation names to apply
        batch_size: Number of items to process in each batch
        enable_caching: Whether to cache intermediate results
        progress_callback: Optional callback for progress updates
        error_threshold: Maximum error rate before aborting (0.0-1.0)
        max_workers: Maximum number of worker threads
        
    Returns:
        ProcessingResult containing processed data, errors, and statistics
        
    Raises:
        ValueError: For invalid parameters
        ProcessingError: When error threshold is exceeded
        
    Example:
        >>> result = process_data_pipeline(
        ...     input_data=[{"id": 1, "value": "test"}],
        ...     transformations=["validate", "normalize", "enrich"],
        ...     batch_size=50,
        ...     error_threshold=0.05
        ... )
        >>> print(f"Processed {len(result.processed_data)} items")
        >>> print(f"Encountered {len(result.errors)} errors")
    """
    # Input validation
    if not input_data:
        return ProcessingResult([], [], {"total_items": 0, "processing_time": 0.0})
    
    if not transformations:
        raise ValueError("At least one transformation must be specified")
    
    if not 0 <= error_threshold <= 1:
        raise ValueError("Error threshold must be between 0.0 and 1.0")
    
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")
    
    if max_workers <= 0:
        raise ValueError("Max workers must be positive")
    
    # Initialize processing state
    total_items = len(input_data)
    processed_items = []
    processing_errors = []
    statistics = {
        "total_items": total_items,
        "processed_items": 0,
        "error_count": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "processing_time": 0.0
    }
    
    start_time = time.time()
    cache_client = get_cache_client() if enable_caching else None
    
    logger.info(f"Starting data pipeline: {total_items} items, {len(transformations)} transformations")
    
    try:
        # Process data in batches
        for batch_start in range(0, total_items, batch_size):
            batch_end = min(batch_start + batch_size, total_items)
            batch_data = input_data[batch_start:batch_end]
            
            logger.debug(f"Processing batch {batch_start}-{batch_end}")
            
            # Process batch with parallel workers
            batch_results, batch_errors = _process_batch(
                batch_data,
                transformations,
                cache_client,
                max_workers,
                statistics
            )
            
            processed_items.extend(batch_results)
            processing_errors.extend(batch_errors)
            
            # Update statistics
            statistics["processed_items"] = len(processed_items)
            statistics["error_count"] = len(processing_errors)
            
            # Check error threshold
            current_error_rate = len(processing_errors) / (batch_end)
            if current_error_rate > error_threshold:
                error_msg = f"Error threshold exceeded: {current_error_rate:.2%} > {error_threshold:.2%}"
                logger.error(error_msg)
                raise ProcessingError(error_msg)
            
            # Progress callback
            if progress_callback:
                try:
                    progress_callback(batch_end, total_items)
                except Exception as callback_error:
                    logger.warning(f"Progress callback failed: {callback_error}")
    
    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        raise
    
    finally:
        statistics["processing_time"] = time.time() - start_time
        logger.info(f"Pipeline completed: {statistics}")
    
    return ProcessingResult(
        processed_data=processed_items,
        errors=processing_errors,
        statistics=statistics
    )

def _process_batch(
    batch_data: List[Dict[str, Any]],
    transformations: List[str],
    cache_client: Optional[Any],
    max_workers: int,
    statistics: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[ProcessingError]]:
    """Process a batch of data items with parallel workers."""
    results = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all items for processing
        future_to_item = {
            executor.submit(_process_item, item, transformations, cache_client): item
            for item in batch_data
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                if isinstance(result, ProcessingError):
                    errors.append(result)
                else:
                    results.append(result)
            except Exception as e:
                error = ProcessingError(f"Item processing failed: {e}", item_id=item.get("id"))
                errors.append(error)
    
    return results, errors

def _process_item(
    item: Dict[str, Any],
    transformations: List[str],
    cache_client: Optional[Any]
) -> Union[Dict[str, Any], ProcessingError]:
    """Process a single data item through all transformations."""
    try:
        current_data = item.copy()
        item_id = item.get("id", "unknown")
        
        for transformation_name in transformations:
            # Check cache first
            if cache_client:
                cache_key = f"{transformation_name}:{hash(str(current_data))}"
                cached_result = cache_client.get(cache_key)
                if cached_result:
                    current_data = cached_result
                    continue
            
            # Apply transformation
            transformer = get_transformer(transformation_name)
            current_data = transformer.transform(current_data)
            
            # Cache result
            if cache_client:
                cache_client.set(cache_key, current_data, ttl=3600)
        
        return current_data
        
    except Exception as e:
        return ProcessingError(f"Transformation failed: {e}", item_id=item_id)
```

---

## 🎯 **GENERATION QUALITY CHECKLIST**

### **✅ Template Compliance**
- [ ] **Template selected** from available complex function templates
- [ ] **Template structure followed** with all required sections
- [ ] **Template customizations applied** appropriately
- [ ] **Design patterns integrated** correctly

### **✅ Code Quality**
- [ ] **Function signature** comprehensive with proper typing
- [ ] **Type annotations** on all parameters, returns, and variables
- [ ] **Docstring** comprehensive with all sections
- [ ] **Error handling** robust with recovery mechanisms
- [ ] **State management** properly implemented
- [ ] **Resource management** with proper cleanup

### **✅ Requirements Compliance**
- [ ] **Primary responsibility** implemented correctly
- [ ] **Secondary responsibilities** handled appropriately
- [ ] **Dependencies** integrated safely with fallbacks
- [ ] **Error handling strategy** fully implemented
- [ ] **State requirements** met with validation

### **✅ Design Pattern Implementation**
- [ ] **Patterns selected** appropriately for requirements
- [ ] **Pattern implementation** follows best practices
- [ ] **Pattern integration** works seamlessly
- [ ] **Pattern testing** considerations included

### **✅ Performance & Scalability**
- [ ] **Algorithm efficiency** optimized for expected load
- [ ] **Resource usage** minimized and monitored
- [ ] **Concurrency** handled safely where applicable
- [ ] **Caching strategy** implemented where beneficial

---

## 🚨 **GENERATION GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Template selected and properly customized
- All 5 mandatory commands executed with evidence
- Core implementation complete and functional
- Error handling comprehensive and tested
- State management properly implemented
- Dependencies integrated with fallbacks
- Design patterns correctly applied
- Quality checklist completed
- Code ready for quality enforcement

**❌ GATE FAILED IF:**
- No template used or improperly customized
- Core functionality incomplete
- Error handling insufficient
- State management missing or incorrect
- Dependencies not properly integrated
- Design patterns missing or incorrect
- Quality standards not met

---

**💡 Key Principle**: Complex function generation requires systematic application of proven templates and design patterns to ensure robust, maintainable, and scalable implementations.
