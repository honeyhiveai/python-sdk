# HoneyHive SDK Implementation Guide

A comprehensive technical guide explaining how the HoneyHive SDK is implemented, including architecture decisions, design patterns, and implementation details.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Design Patterns](#design-patterns)
- [Implementation Details](#implementation-details)
- [Testing Strategy](#testing-strategy)
- [Performance Optimizations](#performance-optimizations)
- [Security Considerations](#security-considerations)
- [Deployment Guide](#deployment-guide)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                    HoneyHive SDK                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Tracer    │  │ API Client  │  │   Evaluation        │ │
│  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  OpenTelemetry Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │Span Processor│  │Span Exporter│  │   Instrumentation   │ │
│  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Transport Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   HTTPX     │  │  Connection │  │      Retry          │ │
│  │             │  │    Pool     │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     HoneyHive API                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Sessions   │  │   Events    │  │     Metrics         │ │
│  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns** - Each component has a single responsibility
2. **Dependency Injection** - Components are loosely coupled
3. **Configuration as Code** - Environment-based configuration
4. **Graceful Degradation** - Fallback mechanisms for missing dependencies
5. **Testability** - All components are designed for easy testing

---

## Core Components

### 1. HoneyHiveTracer

The central component that orchestrates OpenTelemetry integration and session management.

#### Implementation Details

```python
class HoneyHiveTracer:
    _instance = None
    _lock = threading.Lock()
    _is_initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for tracer."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Key Features:**
- **Singleton Pattern** - Ensures single tracer instance per application
- **Thread Safety** - Uses locks for thread-safe initialization
- **Lazy Initialization** - Components initialized only when needed
- **Session Auto-Creation** - Automatically creates HoneyHive sessions

#### Initialization Flow

```python
def __init__(self, api_key=None, project=None, source="production", 
             test_mode=False, session_name=None, instrumentors=None):
    # 1. Validate API key
    self.api_key = api_key or config.api_key
    if not self.api_key:
        raise ValueError("API key is required for HoneyHiveTracer")
    
    # 2. Set configuration
    self.project = project or config.project or "default"
    self.source = source
    self.test_mode = test_mode
    
    # 3. Initialize OpenTelemetry
    self._initialize_otel()
    
    # 4. Initialize session management
    self._initialize_session()
    
    # 5. Set up baggage context
    self._setup_baggage_context()
    
    # 6. Integrate instrumentors
    if instrumentors:
        self._integrate_instrumentors(instrumentors)
```

### 2. HoneyHiveSpanProcessor

Custom OpenTelemetry span processor that enriches spans with HoneyHive-specific attributes.

#### Implementation Details

```python
class HoneyHiveSpanProcessor(SpanProcessor):
    def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None):
        """Enrich span with HoneyHive attributes on start."""
        
        # 1. Extract context information
        ctx = parent_context or context.get_current()
        baggage_items = baggage.get_all(ctx)
        
        # 2. Set HoneyHive attributes
        attributes_to_set = {}
        
        # 3. Handle session context
        if session_id := baggage_items.get("session_id"):
            attributes_to_set["honeyhive.session_id"] = session_id
            attributes_to_set["traceloop.association.properties.session_id"] = session_id
        
        # 4. Handle project and source
        if project := baggage_items.get("project"):
            attributes_to_set["honeyhive.project"] = project
            attributes_to_set["traceloop.association.properties.project"] = project
        
        # 5. Set attributes on span
        for key, value in attributes_to_set.items():
            span.set_attribute(key, value)
```

**Key Features:**
- **Context Extraction** - Extracts information from OpenTelemetry context
- **Attribute Enrichment** - Adds HoneyHive-specific attributes to spans
- **Legacy Compatibility** - Sets both new and legacy attribute formats
- **Performance Optimized** - Batch attribute setting for efficiency

### 3. OTLP Integration

OpenTelemetry Protocol (OTLP) integration for sending spans to backend services.

#### Implementation Details

```python
def _initialize_otel(self):
    """Initialize OpenTelemetry components."""
    
    # 1. Create tracer provider
    self.provider = TracerProvider()
    
    # 2. Add custom span processor
    self.span_processor = HoneyHiveSpanProcessor()
    self.provider.add_span_processor(self.span_processor)
    
    # 3. Configure OTLP export (conditional)
    otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true").lower() != "false"
    
    if otlp_enabled and not self.test_mode:
        # Use OTLP exporter for production
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{config.api_url}/opentelemetry/v1/traces",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Project": self.project,
                "X-Source": self.source
            }
        )
        self.provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    else:
        # Use no-op exporter for tests
        self.provider.add_span_processor(BatchSpanProcessor(NoOpExporter()))
```

**Key Features:**
- **Conditional Export** - OTLP export only when enabled
- **Authentication** - Bearer token authentication with API key
- **Context Headers** - Project and source information in headers
- **Test Mode Support** - No-op exporter during tests

### 4. HTTP Instrumentation

Automatic HTTP request tracing for both `httpx` and `requests` libraries.

#### Implementation Details

```python
class HTTPInstrumentation:
    def _instrument_httpx(self):
        """Instrument httpx for automatic tracing."""
        
        # 1. Store original methods
        self._original_httpx_request = httpx.Client.request
        
        # 2. Create instrumented request method
        def instrumented_request(self, method, url, **kwargs):
            # 3. Get tracer instance
            tracer = HoneyHiveTracer._instance
            if tracer:
                # 4. Create span for request
                with tracer.start_span(f"HTTP {method.upper()}", 
                                     {"http.method": method.upper(), "http.url": str(url)}):
                    return self._original_httpx_request(method, url, **kwargs)
            else:
                return self._original_httpx_request(method, url, **kwargs)
        
        # 5. Replace methods
        httpx.Client.request = instrumented_request
        httpx.AsyncClient.request = instrumented_request
```

**Key Features:**
- **Automatic Instrumentation** - No code changes required
- **Library Support** - Both `httpx` and `requests` libraries
- **Performance Aware** - Minimal overhead when tracing disabled
- **Graceful Fallbacks** - Continues working if tracing unavailable

---

## Design Patterns

### 1. Singleton Pattern

Used for the `HoneyHiveTracer` to ensure single instance per application.

```python
class HoneyHiveTracer:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Benefits:**
- **Resource Efficiency** - Single tracer instance
- **State Consistency** - Shared state across application
- **Configuration Management** - Centralized configuration

### 2. Factory Pattern

Used for creating different types of exporters and processors.

```python
def _create_exporter(self, exporter_type: str):
    """Factory method for creating exporters."""
    
    if exporter_type == "otlp":
        return OTLPSpanExporter(...)
    elif exporter_type == "console":
        return ConsoleSpanExporter()
    elif exporter_type == "noop":
        return NoOpExporter()
    else:
        raise ValueError(f"Unknown exporter type: {exporter_type}")
```

### 3. Strategy Pattern

Used for different retry strategies and export strategies.

```python
class RetryConfig:
    @classmethod
    def exponential(cls, max_attempts=3, base_delay=1.0, max_delay=60.0):
        return cls(strategy="exponential", max_attempts=max_attempts, 
                  base_delay=base_delay, max_delay=max_delay)
    
    @classmethod
    def linear(cls, max_attempts=5, delay=2.0):
        return cls(strategy="linear", max_attempts=max_attempts, delay=delay)
    
    @classmethod
    def constant(cls, max_attempts=3, delay=5.0):
        return cls(strategy="constant", max_attempts=max_attempts, delay=delay)
```

### 4. Decorator Pattern

Used for tracing functions and classes without modifying their code.

```python
def trace(name=None, attributes=None):
    """Decorator for tracing synchronous functions."""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Get tracer instance
            tracer = HoneyHiveTracer._instance
            
            # 2. Create span
            span_name = name or f"{func.__module__}.{func.__name__}"
            with tracer.start_span(span_name, attributes or {}):
                # 3. Execute function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator
```

---

## Implementation Details

### 1. Session Management

Automatic session creation and management for tracking user interactions.

#### Session Creation Flow

```python
def _initialize_session(self):
    """Initialize session management."""
    
    try:
        # 1. Import session API
        from ..api.session import SessionAPI
        from ..api.client import HoneyHive
        
        # 2. Create client and session API
                    self.client = HoneyHive(
            api_key=self.api_key,
            base_url=config.api_url,
            test_mode=self.test_mode
        )
        self.session_api = SessionAPI(self.client)
        
        # 3. Create new session automatically
        session_response = self.session_api.start_session({
            "project": self.project,
            "session_name": self.session_name,
            "source": self.source
        })
        
        # 4. Extract session ID
        if hasattr(session_response, 'session_id'):
            self.session_id = session_response.session_id
        else:
            self.session_id = None
            
    except Exception as e:
        if not self.test_mode:
            print(f"Warning: Failed to create session: {e}")
        self.session_id = None
        self.client = None
        self.session_api = None
```

#### Session Context Injection

```python
def _setup_baggage_context(self):
    """Set up baggage with session context for OpenInference integration."""
    
    try:
        # 1. Prepare baggage items
        baggage_items = {}
        
        if self.session_id:
            baggage_items["session_id"] = self.session_id
        
        # 2. Always set project and source
        baggage_items["project"] = self.project
        baggage_items["source"] = self.source
        
        # 3. Set up baggage context
        ctx = context.get_current()
        for key, value in baggage_items.items():
            if value:
                ctx = baggage.set_baggage(key, str(value), ctx)
        
        # 4. Attach context
        context.attach(ctx)
        
    except Exception as e:
        print(f"Warning: Failed to setup baggage context: {e}")
```

### 2. Baggage Management

Context propagation across service boundaries using OpenTelemetry baggage.

#### Baggage Operations

```python
def set_baggage(self, key: str, value: str):
    """Set baggage item in current context."""
    
    try:
        ctx = context.get_current()
        ctx = baggage.set_baggage(key, value, ctx)
        context.attach(ctx)
        return True
    except Exception as e:
        print(f"Warning: Failed to set baggage {key}: {e}")
        return False

def get_baggage(self, key: str, default=None):
    """Get baggage item from current context."""
    
    try:
        ctx = context.get_current()
        return baggage.get_baggage(key, ctx) or default
    except Exception as e:
        print(f"Warning: Failed to get baggage {key}: {e}")
        return default
```

### 3. Error Handling

Comprehensive error handling with graceful degradation.

#### Error Handling Strategy

```python
def _safe_operation(self, operation, fallback=None, error_message="Operation failed"):
    """Execute operation with error handling."""
    
    try:
        return operation()
    except Exception as e:
        if not self.test_mode:
            print(f"Warning: {error_message}: {e}")
        return fallback

def _handle_api_error(self, error, operation_name):
    """Handle API errors with appropriate logging."""
    
    if "401" in str(error):
        print(f"Authentication failed for {operation_name}")
    elif "403" in str(error):
        print(f"Authorization failed for {operation_name}")
    elif "429" in str(error):
        print(f"Rate limit exceeded for {operation_name}")
    else:
        print(f"API error in {operation_name}: {error}")
```

### 4. Configuration Management

Environment-based configuration with fallback values.

#### Configuration Loading

```python
class Config:
    def __init__(self):
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        
        # 1. Required configuration
        self.api_key = os.getenv("HH_API_KEY")
        if not self.api_key:
            raise ValueError("HH_API_KEY environment variable is required")
        
        # 2. Optional configuration with defaults
        self.api_url = os.getenv("HH_API_URL", "https://api.honeyhive.ai")
        self.project = os.getenv("HH_PROJECT", "default")
        self.source = os.getenv("HH_SOURCE", "production")
        
        # 3. Feature flags
        self.test_mode = os.getenv("HH_TEST_MODE", "false").lower() == "true"
        self.disable_tracing = os.getenv("HH_DISABLE_TRACING", "false").lower() == "true"
        self.disable_http_tracing = os.getenv("HH_DISABLE_HTTP_TRACING", "false").lower() == "true"
        self.otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true").lower() != "false"
    
    def reload(self):
        """Reload configuration from environment."""
        self._load_from_env()
```

---

## Testing Strategy

### 1. Test Architecture

Comprehensive testing strategy covering all components and scenarios.

#### Test Categories

- **Unit Tests** (203 tests) - Core functionality testing
- **Integration Tests** (8 tests) - API integration testing
- **Tracer Tests** - OpenTelemetry integration testing
- **CLI Tests** - Command-line interface testing
- **API Tests** - API client testing

#### Test Environment Configuration

```python
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    
    # 1. Enable test mode
    os.environ["HH_TEST_MODE"] = "true"
    
    # 2. Disable tracing features
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"
    
    # 3. Patch HTTP instrumentation
    with patch("honeyhive.tracer.http_instrumentation.instrument_http") as mock_instrument:
        mock_instrument.return_value = None
        
        # 4. Patch instrumentation methods
        with patch("honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_httpx") as mock_httpx:
            mock_httpx.return_value = None
            with patch("honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_requests") as mock_requests:
                mock_requests.return_value = None
                yield
    
    # 5. Cleanup
    for key in ["HH_TEST_MODE", "HH_DISABLE_HTTP_TRACING", "HH_OTLP_ENABLED"]:
        if key in os.environ:
            del os.environ[key]
```

### 2. Mocking Strategy

Comprehensive mocking to isolate components and prevent external dependencies.

#### Mock Examples

```python
def test_tracer_initialization(self):
    """Test that the tracer initializes correctly."""
    
    # 1. Mock external dependencies
    with patch("honeyhive.api.session.SessionAPI.start_session") as mock_start_session:
        mock_start_session.return_value = Mock(session_id="test-session-123")
        
        # 2. Initialize tracer
        tracer = HoneyHiveTracer()
        
        # 3. Verify initialization
        assert tracer.session_id == "test-session-123"
        assert tracer.project == "default"
        assert tracer.source == "production"

def test_span_processor_attributes(self):
    """Test span processor attribute setting."""
    
    # 1. Mock span and context
    mock_span = Mock()
    mock_context = Mock()
    
    # 2. Mock baggage
    with patch("honeyhive.tracer.span_processor.baggage.get_all") as mock_get_all:
        mock_get_all.return_value = {
            "session_id": "test-session",
            "project": "test-project",
            "source": "test-source"
        }
        
        # 3. Test processor
        processor = HoneyHiveSpanProcessor()
        processor.on_start(mock_span, mock_context)
        
        # 4. Verify attributes
        mock_span.set_attribute.assert_any_call("honeyhive.session_id", "test-session")
        mock_span.set_attribute.assert_any_call("honeyhive.project", "test-project")
        mock_span.set_attribute.assert_any_call("honeyhive.source", "test-source")
```

### 3. Test Data Management

Consistent test data and fixtures for reliable testing.

#### Test Fixtures

```python
@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "project": "test-project",
        "session_name": "test-session",
        "source": "test",
        "inputs": {"test": True}
    }

@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "project": "test-project",
        "event_type": "model",
        "event_name": "test-event",
        "source": "test",
        "session_id": "test-session-123",
        "inputs": {"prompt": "test"},
        "outputs": {"response": "test response"}
    }

@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True, "data": {"id": "test-123"}}
    return response
```

---

## Performance Optimizations

### 1. Span Processing Optimization

Efficient span processing with minimal overhead.

#### Optimization Techniques

```python
class HoneyHiveSpanProcessor(SpanProcessor):
    def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None):
        """Optimized span processing."""
        
        # 1. Early exit if no context
        if not parent_context:
            return
        
        # 2. Batch attribute operations
        attributes_to_set = {}
        
        # 3. Efficient context extraction
        try:
            baggage_items = baggage.get_all(parent_context)
        except Exception:
            return  # Skip if baggage extraction fails
        
        # 4. Conditional attribute setting
        if session_id := baggage_items.get("session_id"):
            attributes_to_set.update({
                "honeyhive.session_id": session_id,
                "traceloop.association.properties.session_id": session_id
            })
        
        # 5. Batch set attributes
        for key, value in attributes_to_set.items():
            span.set_attribute(key, value)
```

### 2. Connection Pooling

Efficient HTTP connection management for API calls.

#### Pool Implementation

```python
class ConnectionPool:
    def __init__(self, max_connections=10, max_keepalive=5):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self._connections = {}
        self._lock = threading.Lock()
    
    def get_connection(self, base_url: str):
        """Get connection from pool."""
        
        with self._lock:
            if base_url in self._connections:
                connections = self._connections[base_url]
                if connections:
                    return connections.pop()
            
            # Create new connection if pool is empty
            return self._create_connection(base_url)
    
    def return_connection(self, base_url: str, connection):
        """Return connection to pool."""
        
        with self._lock:
            if base_url not in self._connections:
                self._connections[base_url] = []
            
            connections = self._connections[base_url]
            if len(connections) < self.max_keepalive:
                connections.append(connection)
            else:
                connection.close()
```

### 3. Caching Strategy

Intelligent caching for frequently accessed data.

#### Cache Implementation

```python
class GlobalCache:
    def __init__(self, max_size=1000, ttl=300):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.Lock()
    
    def get(self, key: str, default=None):
        """Get value from cache."""
        
        with self._lock:
            if key in self._cache:
                # Check TTL
                if time.time() - self._timestamps[key] < self.ttl:
                    return self._cache[key]
                else:
                    # Expired, remove
                    del self._cache[key]
                    del self._timestamps[key]
            
            return default
    
    def set(self, key: str, value, ttl=None):
        """Set value in cache."""
        
        with self._lock:
            # Evict if cache is full
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def _evict_oldest(self):
        """Evict oldest entries from cache."""
        
        if not self._timestamps:
            return
        
        # Find oldest entry
        oldest_key = min(self._timestamps.keys(), 
                        key=lambda k: self._timestamps[k])
        
        # Remove oldest entry
        del self._cache[oldest_key]
        del self._timestamps[oldest_key]
```

---

## Security Considerations

### 1. API Key Management

Secure handling of sensitive credentials.

#### Security Measures

```python
class SecureConfig:
    def __init__(self):
        self._api_key = None
        self._load_api_key()
    
    def _load_api_key(self):
        """Load API key securely."""
        
        # 1. Environment variable (preferred)
        api_key = os.getenv("HH_API_KEY")
        if api_key:
            self._api_key = api_key
            return
        
        # 2. Configuration file (fallback)
        config_file = os.path.expanduser("~/.honeyhive/config")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self._api_key = config.get("api_key")
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
        
        # 3. Validation
        if not self._api_key:
            raise ValueError("API key not found in environment or config file")
    
    @property
    def api_key(self):
        """Get API key (never log this value)."""
        return self._api_key
    
    def __str__(self):
        """String representation (hides sensitive data)."""
        return f"SecureConfig(api_key='***', project='{self.project}')"
```

### 2. Data Privacy

Protection of sensitive data in traces and logs.

#### Privacy Measures

```python
class PrivacyAwareTracer:
    def __init__(self, sensitive_fields=None):
        self.sensitive_fields = sensitive_fields or [
            "password", "token", "secret", "key", "credential"
        ]
    
    def sanitize_attributes(self, attributes):
        """Remove sensitive information from attributes."""
        
        sanitized = {}
        for key, value in attributes.items():
            if self._is_sensitive(key):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _is_sensitive(self, key):
        """Check if a key contains sensitive information."""
        
        key_lower = key.lower()
        return any(field in key_lower for field in self.sensitive_fields)
    
    def start_span(self, name, attributes=None):
        """Start span with privacy protection."""
        
        if attributes:
            attributes = self.sanitize_attributes(attributes)
        
        return super().start_span(name, attributes)
```

### 3. Rate Limiting

Protection against API abuse and rate limiting.

#### Rate Limiting Implementation

```python
class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self._lock = threading.Lock()
    
    def allow_request(self):
        """Check if request is allowed."""
        
        now = time.time()
        
        with self._lock:
            # Remove old requests
            self.requests = [req for req in self.requests 
                           if now - req < self.window_seconds]
            
            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def wait_if_needed(self):
        """Wait if rate limit exceeded."""
        
        while not self.allow_request():
            time.sleep(0.1)  # Small delay
```

---

## Deployment Guide

### 1. Production Deployment

Best practices for deploying the SDK in production environments.

#### Environment Configuration

```bash
# Production environment variables
export HH_API_KEY="your-production-api-key"
export HH_PROJECT="production-project"
export HH_SOURCE="production"
export HH_API_URL="https://api.honeyhive.ai"
export HH_OTLP_ENABLED="true"
export HH_DISABLE_HTTP_TRACING="false"

# Optional: Performance tuning
export HH_MAX_CONNECTIONS="50"
export HH_REQUEST_TIMEOUT="30"
export HH_RETRY_ATTEMPTS="3"
```

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Set environment variables
ENV HH_API_KEY=${HH_API_KEY}
ENV HH_PROJECT=${HH_PROJECT}
ENV HH_SOURCE=${HH_SOURCE}

# Run application
CMD ["python", "app.py"]
```

### 2. Monitoring and Observability

Monitoring the SDK in production environments.

#### Health Checks

```python
def health_check():
    """Health check endpoint for monitoring."""
    
    try:
        # 1. Check tracer status
        tracer = HoneyHiveTracer._instance
        if not tracer:
            return {"status": "unhealthy", "reason": "tracer_not_initialized"}
        
        # 2. Check API connectivity
        client = HoneyHive(api_key=config.api_key)
        health = client.get_health()
        client.close()
        
        if health.get("status") == "healthy":
            return {"status": "healthy", "tracer": "ok", "api": "ok"}
        else:
            return {"status": "unhealthy", "reason": "api_unhealthy"}
            
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
```

#### Metrics Collection

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "spans_created": 0,
            "spans_exported": 0,
            "api_calls": 0,
            "errors": 0
        }
        self._lock = threading.Lock()
    
    def increment(self, metric_name):
        """Increment metric counter."""
        
        with self._lock:
            if metric_name in self.metrics:
                self.metrics[metric_name] += 1
    
    def get_metrics(self):
        """Get current metrics."""
        
        with self._lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics (useful for testing)."""
        
        with self._lock:
            for key in self.metrics:
                self.metrics[key] = 0
```

### 3. Troubleshooting

Common issues and their solutions.

#### Common Issues

1. **Authentication Failures**
   - Verify API key is correct
   - Check API key permissions
   - Ensure API key is not expired

2. **Connection Timeouts**
   - Check network connectivity
   - Verify API endpoint is accessible
   - Adjust timeout settings

3. **Rate Limiting**
   - Implement exponential backoff
   - Reduce request frequency
   - Contact support for rate limit increases

4. **Memory Issues**
   - Monitor span buffer size
   - Implement span sampling
   - Check for memory leaks in custom code

#### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize tracer with debug output
tracer = HoneyHiveTracer(debug=True)

# Check tracer status
print(f"Tracer initialized: {tracer is not None}")
print(f"Session ID: {tracer.session_id}")
print(f"Project: {tracer.project}")
print(f"Source: {tracer.source}")
```

---

This implementation guide provides comprehensive technical details about how the HoneyHive SDK is implemented, including architecture decisions, design patterns, and best practices for deployment and monitoring.
