# HoneyHive SDK API Reference

Complete API reference for the HoneyHive Python SDK.

## Table of Contents

- [Core Classes](#core-classes)
- [Tracing Decorators](#tracing-decorators)
- [API Client](#api-client)
- [Configuration](#configuration)
- [Utilities](#utilities)
- [Models](#models)
- [Examples](#examples)

---

## Core Classes

### HoneyHiveTracer

The main tracer class providing OpenTelemetry integration and session management.

#### Constructor

```python
HoneyHiveTracer(
    api_key: Optional[str] = None,
    project: Optional[str] = None,
    source: str = "production",
    test_mode: bool = False,
    session_name: Optional[str] = None,
    instrumentors: Optional[list] = None,
    **kwargs
)
```

**Parameters:**
- `api_key`: HoneyHive API key (required if not in environment)
- `project`: Project name (defaults to environment or "default")
- `source`: Source environment (defaults to "production")
- `test_mode`: Enable test mode (defaults to False)
- `session_name`: Custom session name (auto-generated if not provided)
- `instrumentors`: List of OpenInference instrumentors to integrate

**Example:**
```python
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="development"
)
```

#### Methods

##### `start_span(name, attributes=None)`

Create a new span with the given name and attributes.

**Parameters:**
- `name`: Span name
- `attributes`: Optional dictionary of span attributes

**Returns:** Context manager for span management

**Example:**
```python
with tracer.start_span("database-query", {"db.system": "postgresql"}):
    # Execute database query
    pass
```

##### `enrich_span(name, attributes=None)`

Enrich the current span with additional attributes.

**Parameters:**
- `name`: Enrichment operation name
- `attributes`: Dictionary of attributes to add

**Returns:** Context manager for span enrichment

**Example:**
```python
with tracer.enrich_span("data-processing", {"batch_size": 1000}):
    # Process data
    pass
```

##### `enrich_session(session_id)`

Enrich the current session with a specific session ID.

**Parameters:**
- `session_id`: Session identifier to set

**Example:**
```python
tracer.enrich_session("sess_123456")
```

##### `reset()`

Reset the tracer instance for testing purposes.

**Example:**
```python
tracer.reset()
```

#### Properties

- `session_id`: Current session identifier
- `project`: Current project name
- `source`: Current source environment
- `test_mode`: Whether test mode is enabled

---

## Tracing Decorators

### @trace

Decorator for tracing synchronous functions.

**Signature:**
```python
@trace(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None)
def function_name():
    pass
```

**Parameters:**
- `name`: Optional custom span name (defaults to function name)
- `attributes`: Optional dictionary of span attributes

**Example:**
```python
from honeyhive import trace

@trace
def process_data(data):
    return data.upper()

@trace(name="custom-operation", attributes={"operation_type": "data_processing"})
def custom_function():
    return "result"
```

### @atrace

Decorator for tracing asynchronous functions.

**Signature:**
```python
@atrace(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None)
async def async_function_name():
    pass
```

**Parameters:**
- `name`: Optional custom span name (defaults to function name)
- `attributes`: Optional dictionary of span attributes

**Example:**
```python
from honeyhive import atrace

@atrace
async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@atrace(name="async-operation", attributes={"operation_type": "http_request"})
async def custom_async_function():
    return "async result"
```

### @trace_class

Decorator for tracing all methods in a class.

**Signature:**
```python
@trace_class(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None)
class ClassName:
    pass
```

**Parameters:**
- `name`: Optional custom span name (defaults to class name)
- `attributes`: Optional dictionary of span attributes

**Example:**
```python
from honeyhive import trace_class

@trace_class
class DataProcessor:
    def process(self, data):
        return data.upper()
    
    def validate(self, data):
        return len(data) > 0

@trace_class(name="CustomClass", attributes={"class_type": "processor"})
class CustomProcessor:
    def method1(self):
        return "method 1"
```

---

## API Client

### HoneyHiveClient

Main API client for interacting with HoneyHive services.

#### Constructor

```python
HoneyHiveClient(
    api_key: str,
    base_url: Optional[str] = None,
    test_mode: bool = False,
    timeout: float = 30.0,
    retry_config: Optional[RetryConfig] = None
)
```

**Parameters:**
- `api_key`: HoneyHive API key
- `base_url`: API base URL (defaults to environment or production URL)
- `test_mode`: Enable test mode (defaults to False)
- `timeout`: Request timeout in seconds (defaults to 30.0)
- `retry_config`: Retry configuration (defaults to exponential backoff)

**Example:**
```python
client = HoneyHiveClient(
    api_key="your-api-key",
    base_url="https://api.honeyhive.ai",
    timeout=60.0
)
```

#### Methods

##### `get_health()`

Check API health status.

**Returns:** Health check response

**Example:**
```python
health = client.get_health()
print(f"API Status: {health['status']}")
```

##### `sessions`

Access session operations.

**Returns:** SessionAPI instance

**Example:**
```python
# Start a new session
session_response = client.sessions.start_session({
    "project": "my-project",
    "session_name": "chat-session",
    "source": "production"
})

# Get session details
session = client.sessions.get_session(session_id)
```

##### `events`

Access event operations.

**Returns:** EventAPI instance

**Example:**
```python
# Create an event
event_response = client.events.create_event({
    "project": "my-project",
    "event_type": "model",
    "event_name": "model_inference",
    "source": "production",
    "session_id": "sess_123",
    "inputs": {"prompt": "Hello"},
    "outputs": {"response": "Hi!"}
})

# Get event details
event = client.events.get_event(event_id)
```

##### `close()`

Close the client and cleanup resources.

**Example:**
```python
client.close()
```

#### API Endpoints

##### Sessions

- `POST /sessions` - Start a new session
- `GET /sessions/{session_id}` - Get session details
- `PUT /sessions/{session_id}` - Update session
- `DELETE /sessions/{session_id}` - Delete session

##### Events

- `POST /events` - Create a new event
- `GET /events/{event_id}` - Get event details
- `PUT /events/{event_id}` - Update event
- `DELETE /events/{event_id}` - Delete event
- `POST /events/batch` - Create multiple events

##### Projects

- `GET /projects` - List projects
- `POST /projects` - Create a new project
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

##### Metrics

- `GET /metrics` - List metrics
- `POST /metrics` - Create a new metric
- `GET /metrics/{metric_id}` - Get metric details
- `PUT /metrics/{metric_id}` - Update metric
- `DELETE /metrics/{metric_id}` - Delete metric

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HH_API_KEY` | HoneyHive API key | None | Yes |
| `HH_API_URL` | API base URL | `https://api.honeyhive.ai` | No |
| `HH_PROJECT` | Project name | `default` | No |
| `HH_SOURCE` | Source environment | `production` | No |
| `HH_TEST_MODE` | Enable test mode | `false` | No |
| `HH_DISABLE_TRACING` | Disable tracing | `false` | No |
| `HH_DISABLE_HTTP_TRACING` | Disable HTTP instrumentation | `false` | No |
| `HH_OTLP_ENABLED` | Enable OTLP export | `true` | No |

### Configuration Object

```python
from honeyhive.utils.config import get_config

config = get_config()

# Access configuration values
api_key = config.api_key
api_url = config.api_url
project = config.project
source = config.source
test_mode = config.test_mode
```

#### Methods

##### `reload()`

Reload configuration from environment variables.

**Example:**
```python
config.reload()
```

---

## Utilities

### Connection Pool

HTTP connection pooling for efficient API communication.

```python
from honeyhive.utils.connection_pool import get_global_pool, close_global_pool

# Get global connection pool
pool = get_global_pool()

# Close global pool
close_global_pool()
```

### Retry Configuration

Configurable retry strategies for API calls.

```python
from honeyhive.utils.retry import RetryConfig

# Exponential backoff
retry_config = RetryConfig.exponential(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0
)

# Linear backoff
retry_config = RetryConfig.linear(
    max_attempts=5,
    delay=2.0
)

# Constant delay
retry_config = RetryConfig.constant(
    max_attempts=3,
    delay=5.0
)
```

### Logging

Configure logging for the SDK.

```python
from honeyhive.utils.logger import get_logger, HoneyHiveLogger

# Get logger instance
logger = get_logger(__name__)

# Configure logging level
logger.setLevel(logging.DEBUG)

# Log messages
logger.info("Operation completed successfully")
logger.error("Operation failed", exc_info=True)
```

---

## Models

### Auto-generated Models

The SDK includes Pydantic models auto-generated from the OpenAPI specification.

```python
from honeyhive.models.generated import (
    SessionStartRequest,
    CreateEventRequest,
    Project,
    Event
)

# Create session request
session_request = SessionStartRequest(
    project="my-project",
    session_name="chat-session",
    source="production",
    inputs={"user_query": "Hello"}
)

# Create event request
event_request = CreateEventRequest(
    project="my-project",
    event_type="model",
    event_name="model_inference",
    source="production",
    session_id="sess_123",
    inputs={"prompt": "Hello"},
    outputs={"response": "Hi!"}
)
```

---

## Examples

### Basic Tracing

```python
from honeyhive import HoneyHiveTracer, trace

# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="development"
)

@trace
def process_data(data):
    """Process data with automatic tracing."""
    result = data.upper()
    return result

# Use the traced function
result = process_data("hello world")
```

### Session Management

```python
from honeyhive import HoneyHiveTracer
from honeyhive.api.client import HoneyHiveClient

# Initialize tracer and client
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

client = HoneyHiveClient(
    api_key="your-api-key",
    base_url="https://api.honeyhive.ai"
)

# Start a session
session_response = client.sessions.start_session({
    "project": "my-project",
    "session_name": "chat-session",
    "source": "production"
})

session_id = session_response.session_id

# Enrich current span with session
tracer.enrich_session(session_id)

# Create an event
event_response = client.events.create_event({
    "project": "my-project",
    "event_type": "model",
    "event_name": "model_inference",
    "source": "production",
    "session_id": session_id,
    "inputs": {"prompt": "Hello"},
    "outputs": {"response": "Hi!"}
})

# Cleanup
client.close()
```

### OpenInference Integration

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize tracer with OpenInference
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[OpenAIInstrumentor()]
)

# OpenInference automatically traces OpenAI calls
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Advanced Span Management

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def complex_operation():
    with tracer.start_span("data-processing") as span:
        span.set_attribute("operation.type", "batch")
        span.set_attribute("data.size", 1000)
        
        # Process data in chunks
        for i in range(0, 1000, 100):
            with tracer.start_span(f"chunk-{i//100}") as chunk_span:
                chunk_span.set_attribute("chunk.start", i)
                chunk_span.set_attribute("chunk.end", min(i+100, 1000))
                
                # Process chunk
                process_chunk(i, min(i+100, 1000))
                
                # Add custom attributes
                chunk_span.set_attribute("chunk.processed", True)
                chunk_span.set_attribute("chunk.timestamp", time.time())

def process_chunk(start, end):
    with tracer.enrich_span("chunk-processing", {
        "chunk_start": start,
        "chunk_end": end,
        "chunk_size": end - start
    }):
        # Process chunk data
        pass
```

### Error Handling

```python
from honeyhive import HoneyHiveTracer, trace

tracer = HoneyHiveTracer()

@trace
def risky_operation():
    try:
        # Perform risky operation
        result = perform_operation()
        return result
    except Exception as e:
        # Error will be automatically captured in span
        raise

def manual_error_handling():
    with tracer.start_span("manual-operation") as span:
        try:
            result = perform_operation()
            span.set_attribute("operation.success", True)
            return result
        except Exception as e:
            span.set_attribute("operation.success", False)
            span.set_attribute("operation.error", str(e))
            span.set_attribute("operation.error_type", type(e).__name__)
            raise
```

### Performance Monitoring

```python
from honeyhive import HoneyHiveTracer, trace
import time

tracer = HoneyHiveTracer()

@trace
def performance_critical_function():
    start_time = time.time()
    
    # Perform operation
    result = perform_operation()
    
    # Calculate duration
    duration = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Duration is automatically captured by the tracer
    return result

def manual_performance_tracking():
    with tracer.start_span("performance-tracked-operation") as span:
        start_time = time.time()
        
        # Perform operation
        result = perform_operation()
        
        # Calculate and set custom metrics
        duration = (time.time() - start_time) * 1000
        span.set_attribute("operation.duration_ms", duration)
        span.set_attribute("operation.memory_usage", get_memory_usage())
        
        return result
```

---

## Error Handling

### Common Exceptions

#### `HoneyHiveError`

Base exception for all HoneyHive SDK errors.

#### `AuthenticationError`

Raised when API authentication fails.

#### `ValidationError`

Raised when request validation fails.

#### `RateLimitError`

Raised when API rate limits are exceeded.

#### `ConnectionError`

Raised when connection to the API fails.

### Error Handling Best Practices

```python
from honeyhive import HoneyHiveTracer
from honeyhive.exceptions import HoneyHiveError, AuthenticationError

tracer = HoneyHiveTracer()

try:
    with tracer.start_span("api-operation"):
        # Perform API operation
        result = perform_api_operation()
        return result
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    # Handle authentication error
    raise
except HoneyHiveError as e:
    logger.error(f"HoneyHive error: {e}")
    # Handle other HoneyHive errors
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors
    raise
```

---

## Testing

### Test Configuration

Tests automatically configure the environment:

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["HH_TEST_MODE"] = "true"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with tox (recommended)
tox
```

### Test Categories

- **Unit Tests** (203 tests) - Core functionality testing
- **Integration Tests** (8 tests) - API integration testing
- **Tracer Tests** - OpenTelemetry integration testing
- **CLI Tests** - Command-line interface testing
- **API Tests** - API client testing

---

## Performance Considerations

### Span Processing

- **Efficient Attribute Setting** - Batch attribute operations
- **Context Caching** - Minimize context lookups
- **Early Exit Logic** - Skip processing when not needed
- **Memory Management** - Proper cleanup of resources

### HTTP Instrumentation

- **Conditional Application** - Only when enabled
- **Graceful Fallbacks** - Handle missing dependencies
- **Performance Monitoring** - Built-in performance metrics

### Best Practices

1. **Use decorators** for simple function tracing
2. **Manual span management** for complex operations
3. **Batch operations** for high-throughput scenarios
4. **Proper cleanup** of resources
5. **Monitor performance** with built-in metrics

---

## Security

### API Key Management

- **Environment Variables** - Secure key storage
- **Test Mode** - Safe testing without real credentials
- **Header Authentication** - Bearer token authentication
- **Secure Transmission** - HTTPS-only communication

### Data Privacy

- **Local Processing** - Sensitive data stays local
- **Configurable Sampling** - Control data volume
- **Audit Logging** - Track data access

### Best Practices

1. **Never hardcode API keys** in source code
2. **Use environment variables** for configuration
3. **Enable test mode** during development
4. **Monitor API usage** and rate limits
5. **Implement proper error handling** for security-related errors

---

This API reference covers all the major components and functionality of the HoneyHive SDK. For more detailed examples and use cases, refer to the main README.md and the examples directory.
