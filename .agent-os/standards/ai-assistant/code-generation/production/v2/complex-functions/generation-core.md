# Complex Functions - Generation Core (v2)

## 🎯 **GENERATION PHASE FOR COMPLEX FUNCTIONS**

**Purpose**: Template-based generation of complex functions with design patterns integration.

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

### **Command 4: Integrate Dependencies**
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

## 🛠️ **TEMPLATE SELECTION GUIDE**

### **Available Templates**
1. **API Client Template** - HTTP requests with retry logic
2. **Data Pipeline Template** - Multi-stage processing
3. **Event Handler Template** - Asynchronous event processing
4. **Resource Manager Template** - Resource allocation/cleanup
5. **Configuration Manager Template** - Complex config handling

### **Template Selection Criteria**

| Function Type | Template | Use When |
|---------------|----------|----------|
| **API Integration** | API Client | External HTTP/REST API interactions |
| **Data Processing** | Data Pipeline | Multi-step data transformations |
| **Event Processing** | Event Handler | Asynchronous event handling |
| **Resource Management** | Resource Manager | Resource allocation/cleanup |
| **Configuration** | Configuration Manager | Complex config loading/validation |

---

## 🔧 **GENERATION PROCESS**

### **Step 1: Template Customization**
**Apply comprehensive customizations:**

1. **Function Signature**: Adapt parameters for specific requirements
2. **Type Annotations**: Add complex type hints (Union, Optional, Generic)
3. **Docstring**: Create comprehensive documentation
4. **Core Logic**: Implement primary responsibility
5. **Error Handling**: Add exception handling and recovery
6. **Dependencies**: Integrate external systems safely
7. **Logging**: Add structured logging throughout
8. **Performance**: Optimize for expected load

### **Step 2: Pattern Integration**
**Integrate design patterns appropriately:**

1. **Pattern Selection**: Choose patterns based on requirements
2. **Pattern Implementation**: Implement patterns correctly
3. **Pattern Composition**: Combine patterns effectively
4. **Pattern Testing**: Ensure patterns work as expected

### **Step 3: Quality Integration**
**Ensure generated code includes:**

1. **Type Safety**: 100% type annotation coverage
2. **Documentation**: Comprehensive docstrings with examples
3. **Error Resilience**: Robust error handling and recovery
4. **Resource Management**: Proper cleanup and resource handling
5. **Observability**: Logging, metrics, and monitoring hooks
6. **Testability**: Dependency injection and test-friendly design

---

## 📝 **GENERATION EXAMPLE**

### **API Client with Comprehensive Patterns**
```python
import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union, List
from contextlib import asynccontextmanager
import httpx

from ..models.errors import APIError, CircuitBreakerOpenError
from ..utils.circuit_breaker import CircuitBreaker
from ..utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)

class APIClient:
    """Robust API client with comprehensive error handling and resilience patterns.
    
    This client implements multiple design patterns for maximum reliability:
    - Circuit Breaker: Prevents cascade failures
    - Retry with Exponential Backoff: Handles transient failures
    - Resource Management: Proper connection lifecycle
    - Strategy Pattern: Pluggable authentication methods
    
    Example:
        >>> async with APIClient("https://api.example.com") as client:
        ...     result = await client.get("/users/123")
        ...     print(result["name"])
    """
    
    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5
    ) -> None:
        """Initialize API client with configuration.
        
        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            circuit_breaker_threshold: Failure threshold for circuit breaker
        """
        self._base_url = base_url.rstrip('/')
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        
        # Initialize circuit breaker
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout=60.0
        )
        
        # HTTP client (managed by context manager)
        self._client: Optional[httpx.AsyncClient] = None
        
        # Request statistics
        self._request_count = 0
        self._error_count = 0
    
    async def __aenter__(self) -> 'APIClient':
        """Async context manager entry."""
        await self._initialize_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self._cleanup_client()
    
    async def _initialize_client(self) -> None:
        """Initialize HTTP client with proper configuration."""
        if self._client is not None:
            return
        
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout),
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            )
        )
        
        logger.info(f"API client initialized for {self._base_url}")
    
    async def _cleanup_client(self) -> None:
        """Cleanup HTTP client resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("API client cleaned up")
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make GET request with comprehensive error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: For API-related errors
            CircuitBreakerOpenError: When circuit breaker is open
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers)
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def post(
        self,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make POST request with comprehensive error handling."""
        return await self._make_request("POST", endpoint, data=data, params=params, headers=headers)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Core request method with circuit breaker protection."""
        if not self._client:
            raise APIError("Client not initialized - use async context manager")
        
        # Circuit breaker check
        if self._circuit_breaker.is_open():
            raise CircuitBreakerOpenError("Circuit breaker is open")
        
        # Prepare request
        request_headers = self._prepare_headers(headers)
        request_data = {
            "method": method,
            "url": endpoint,
            "params": params,
            "headers": request_headers
        }
        
        if data is not None:
            request_data["json"] = data
        
        try:
            start_time = time.time()
            
            # Execute request
            response = await self._client.request(**request_data)
            
            # Handle response
            result = await self._handle_response(response)
            
            # Record success
            self._circuit_breaker.record_success()
            self._request_count += 1
            
            request_time = time.time() - start_time
            logger.debug(f"Request successful: {method} {endpoint} ({request_time:.3f}s)")
            
            return result
            
        except Exception as e:
            # Record failure
            self._circuit_breaker.record_failure()
            self._error_count += 1
            
            logger.error(f"Request failed: {method} {endpoint} - {e}")
            raise
    
    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Prepare request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        
        # Add API key if available
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def _handle_response(self, response: httpx.Response) -> Union[Dict[str, Any], List[Any]]:
        """Handle HTTP response with proper error handling."""
        # Handle specific status codes
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise APIError(f"Rate limit exceeded, retry after {retry_after}s")
        
        # Raise for HTTP errors
        response.raise_for_status()
        
        # Parse JSON response
        try:
            return response.json()
        except ValueError as e:
            if response.status_code == 204:  # No Content
                return {}
            raise APIError(f"Invalid JSON response: {e}") from e
    
    # Properties for monitoring
    @property
    def request_count(self) -> int:
        """Get total request count."""
        return self._request_count
    
    @property
    def error_count(self) -> int:
        """Get total error count."""
        return self._error_count
    
    @property
    def error_rate(self) -> float:
        """Get current error rate."""
        return self._error_count / max(self._request_count, 1)
    
    @property
    def circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self._circuit_breaker.is_open()
```

---

## 🎯 **GENERATION QUALITY CHECKLIST**

### **✅ Template Compliance**
- [ ] **Template selected** from available complex function templates
- [ ] **Template structure followed** with all required sections
- [ ] **Template customizations applied** appropriately

### **✅ Pattern Integration**
- [ ] **Patterns selected** appropriately for requirements
- [ ] **Pattern implementation** follows best practices
- [ ] **Pattern integration** works seamlessly
- [ ] **Pattern interactions** handled correctly

### **✅ Code Quality**
- [ ] **Function signature** comprehensive with proper typing
- [ ] **Type annotations** on all parameters, returns, and variables
- [ ] **Docstring** comprehensive with all sections
- [ ] **Error handling** robust with recovery mechanisms
- [ ] **Resource management** with proper cleanup

### **✅ Requirements Compliance**
- [ ] **Primary responsibility** implemented correctly
- [ ] **Secondary responsibilities** handled appropriately
- [ ] **Dependencies** integrated safely with fallbacks
- [ ] **Error handling strategy** fully implemented

---

## 🚨 **GENERATION GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Template selected and properly customized
- All 4 mandatory commands executed with evidence
- Core implementation complete and functional
- Error handling comprehensive and tested
- Dependencies integrated with fallbacks
- Design patterns correctly applied
- Quality checklist completed

**❌ GATE FAILED IF:**
- No template used or improperly customized
- Core functionality incomplete
- Error handling insufficient
- Dependencies not properly integrated
- Design patterns missing or incorrect

---

**💡 Key Principle**: Complex function generation requires systematic application of proven templates and design patterns to ensure robust, maintainable implementations.
