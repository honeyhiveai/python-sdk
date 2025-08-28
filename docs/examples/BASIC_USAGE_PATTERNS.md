# Basic SDK Usage Patterns

Common usage patterns and examples for the HoneyHive SDK.

## Table of Contents

- [Initialization Patterns](#initialization-patterns)
- [Tracing Patterns](#tracing-patterns)
- [Session Management](#session-management)
- [Error Handling](#error-handling)
- [Configuration Patterns](#configuration-patterns)

---

## Initialization Patterns

### 1. Simple Initialization

Basic tracer initialization with minimal configuration:

```python
from honeyhive import HoneyHiveTracer

# Initialize with environment variables
tracer = HoneyHiveTracer()

# Or with explicit configuration
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production"
)
```

### 2. Environment-Based Configuration

Use environment variables for configuration:

```python
import os
from honeyhive import HoneyHiveTracer

# Set environment variables
os.environ["HH_API_KEY"] = "your-api-key"
os.environ["HH_PROJECT"] = "my-project"
os.environ["HH_SOURCE"] = "production"

# Initialize tracer (automatically reads environment)
tracer = HoneyHiveTracer()
```

### 3. Conditional Initialization

Initialize based on environment or configuration:

```python
import os
from honeyhive import HoneyHiveTracer

def create_tracer():
    """Create tracer based on environment."""
    
    if os.getenv("ENVIRONMENT") == "production":
        return HoneyHiveTracer(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            source="production"
        )
    else:
        # Development mode
        return HoneyHiveTracer(
            api_key="dev-key",
            project="dev-project",
            source="development"
        )

tracer = create_tracer()
```

### 4. Singleton Pattern Usage

The tracer is a singleton, so you can access it from anywhere:

```python
from honeyhive import HoneyHiveTracer

# Initialize once
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# Access from anywhere else in your code
def some_function():
    current_tracer = HoneyHiveTracer._instance
    print(f"Current project: {current_tracer.project}")
```

---

## Tracing Patterns

### 1. Function Decorators

Use decorators for automatic function tracing:

```python
from honeyhive import trace, atrace

@trace
def process_data(data):
    """This function is automatically traced."""
    result = data.upper()
    return result

@atrace
async def fetch_data_async(url):
    """This async function is automatically traced."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Usage
result = process_data("hello world")
```

### 2. Class Decorators

Trace all methods in a class:

```python
from honeyhive import trace_class

@trace_class
class DataProcessor:
    def __init__(self):
        self.cache = {}
    
    def process(self, data):
        """This method is automatically traced."""
        if data in self.cache:
            return self.cache[data]
        
        result = data.upper()
        self.cache[data] = result
        return result
    
    def clear_cache(self):
        """This method is also automatically traced."""
        self.cache.clear()

# Usage
processor = DataProcessor()
result = processor.process("hello")
processor.clear_cache()
```

### 3. Manual Span Management

Create and manage spans manually:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def complex_operation():
    with tracer.start_span("data-processing") as span:
        # Set span attributes
        span.set_attribute("operation.type", "batch")
        span.set_attribute("data.size", 1000)
        
        # Process data
        result = process_large_dataset()
        
        # Add result attributes
        span.set_attribute("operation.result", "success")
        span.set_attribute("operation.duration", get_operation_duration())
        
        return result

def process_large_dataset():
    with tracer.start_span("dataset-processing") as span:
        span.set_attribute("dataset.type", "csv")
        span.set_attribute("dataset.rows", 10000)
        
        # Process dataset
        return "processed_data"
```

### 4. Span Enrichment

Enrich existing spans with additional context:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def process_user_request(user_id, request_data):
    with tracer.start_span("user-request") as span:
        # Set basic attributes
        span.set_attribute("user.id", user_id)
        span.set_attribute("request.type", "data_processing")
        
        # Process request
        result = process_request(request_data)
        
        # Enrich span with results
        with tracer.enrich_span("request-results", {
            "result.status": "success",
            "result.size": len(result),
            "processing.time": get_processing_time()
        }):
            # Additional processing if needed
            pass
        
        return result
```

---

## Session Management

### 1. Automatic Session Creation

Sessions are automatically created when the tracer initializes:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="chat-application",
    source="production"
)

# Session is automatically created
print(f"Session ID: {tracer.session_id}")
print(f"Project: {tracer.project}")
print(f"Source: {tracer.source}")
```

### 2. Session Enrichment

Enrich the current session with additional context:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def handle_user_conversation(user_id, conversation_id):
    # Enrich session with user context
    tracer.enrich_session(f"user_{user_id}_conv_{conversation_id}")
    
    with tracer.start_span("conversation-handling") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("conversation.id", conversation_id)
        
        # Handle conversation
        return process_conversation(user_id, conversation_id)
```

### 3. Multi-Session Applications

Handle multiple sessions in a single application:

```python
from honeyhive import HoneyHiveTracer

class MultiSessionManager:
    def __init__(self):
        self.tracer = HoneyHiveTracer()
        self.sessions = {}
    
    def create_user_session(self, user_id):
        """Create a new session for a user."""
        session_id = f"user_{user_id}_{int(time.time())}"
        
        # Enrich current context with new session
        self.tracer.enrich_session(session_id)
        
        # Store session info
        self.sessions[user_id] = {
            "session_id": session_id,
            "created_at": time.time()
        }
        
        return session_id
    
    def switch_to_session(self, user_id):
        """Switch to a specific user's session."""
        if user_id in self.sessions:
            session_id = self.sessions[user_id]["session_id"]
            self.tracer.enrich_session(session_id)
            return session_id
        return None

# Usage
manager = MultiSessionManager()
session1 = manager.create_user_session("user123")
session2 = manager.create_user_session("user456")

# Switch between sessions
manager.switch_to_session("user123")
# Now all spans will be associated with user123's session
```

---

## Error Handling

### 1. Basic Error Handling

Handle errors gracefully in traced functions:

```python
from honeyhive import trace

@trace
def risky_operation(data):
    try:
        # Perform risky operation
        result = process_data(data)
        return result
    except ValueError as e:
        # Error will be captured in span automatically
        raise
    except Exception as e:
        # Handle unexpected errors
        raise RuntimeError(f"Operation failed: {e}") from e
```

### 2. Manual Error Handling

Manually handle errors in spans:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def robust_operation(data):
    with tracer.start_span("robust-operation") as span:
        try:
            # Set operation attributes
            span.set_attribute("operation.input_size", len(data))
            span.set_attribute("operation.type", "data_processing")
            
            # Perform operation
            result = process_data(data)
            
            # Set success attributes
            span.set_attribute("operation.success", True)
            span.set_attribute("operation.result_size", len(result))
            
            return result
            
        except ValueError as e:
            # Handle validation errors
            span.set_attribute("operation.success", False)
            span.set_attribute("operation.error_type", "validation_error")
            span.set_attribute("operation.error_message", str(e))
            raise
            
        except Exception as e:
            # Handle other errors
            span.set_attribute("operation.success", False)
            span.set_attribute("operation.error_type", type(e).__name__)
            span.set_attribute("operation.error_message", str(e))
            span.set_attribute("operation.error_traceback", get_traceback())
            raise
```

### 3. Error Recovery

Implement error recovery patterns:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

def resilient_operation(data, max_retries=3):
    with tracer.start_span("resilient-operation") as span:
        span.set_attribute("operation.max_retries", max_retries)
        
        for attempt in range(max_retries):
            try:
                span.set_attribute("operation.attempt", attempt + 1)
                
                # Attempt operation
                result = process_data(data)
                
                # Success
                span.set_attribute("operation.success", True)
                span.set_attribute("operation.attempts_needed", attempt + 1)
                return result
                
            except Exception as e:
                span.set_attribute(f"operation.attempt_{attempt + 1}_error", str(e))
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    span.set_attribute("operation.success", False)
                    span.set_attribute("operation.final_error", str(e))
                    raise
                
                # Wait before retry
                time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Configuration Patterns

### 1. Environment-Based Configuration

Use environment variables for different environments:

```python
import os
from honeyhive import HoneyHiveTracer

def get_environment_config():
    """Get configuration based on environment."""
    
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "api_key": "dev-key",
            "project": "dev-project",
            "source": "development",
            "test_mode": True
        },
        "staging": {
            "api_key": os.getenv("HH_API_KEY"),
            "project": "staging-project",
            "source": "staging",
            "test_mode": False
        },
        "production": {
            "api_key": os.getenv("HH_API_KEY"),
            "project": os.getenv("HH_PROJECT"),
            "source": "production",
            "test_mode": False
        }
    }
    
    return configs.get(env, configs["development"])

# Usage
config = get_environment_config()
tracer = HoneyHiveTracer(**config)
```

### 2. Configuration File

Load configuration from a file:

```python
import json
import os
from honeyhive import HoneyHiveTracer

def load_config_from_file(config_path):
    """Load configuration from JSON file."""
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def create_tracer_from_config(config_path):
    """Create tracer from configuration file."""
    
    config = load_config_from_file(config_path)
    
    # Validate required fields
    required_fields = ["api_key", "project"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")
    
    return HoneyHiveTracer(**config)

# Usage
tracer = create_tracer_from_config("config/honeyhive.json")
```

### 3. Dynamic Configuration

Update configuration dynamically:

```python
from honeyhive import HoneyHiveTracer
from honeyhive.utils.config import get_config

class DynamicTracer:
    def __init__(self):
        self.tracer = HoneyHiveTracer()
        self.config = get_config()
    
    def update_project(self, new_project):
        """Update the project dynamically."""
        self.config.project = new_project
        self.config.reload()
        
        # Update tracer
        self.tracer.project = new_project
        
        print(f"Project updated to: {new_project}")
    
    def update_source(self, new_source):
        """Update the source dynamically."""
        self.config.source = new_source
        self.config.reload()
        
        # Update tracer
        self.tracer.source = new_source
        
        print(f"Source updated to: {new_source}")
    
    def get_current_config(self):
        """Get current configuration."""
        return {
            "project": self.tracer.project,
            "source": self.tracer.source,
            "session_id": self.tracer.session_id
        }

# Usage
dynamic_tracer = DynamicTracer()
dynamic_tracer.update_project("new-project")
dynamic_tracer.update_source("staging")

current_config = dynamic_tracer.get_current_config()
print(f"Current config: {current_config}")
```

---

## Performance Patterns

### 1. Conditional Tracing

Enable tracing only when needed:

```python
import os
from honeyhive import HoneyHiveTracer

def create_performance_aware_tracer():
    """Create tracer with performance considerations."""
    
    # Check if tracing should be enabled
    enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    
    if enable_tracing:
        return HoneyHiveTracer(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            source=os.getenv("HH_SOURCE")
        )
    else:
        # Return a no-op tracer or None
        return None

# Usage
tracer = create_performance_aware_tracer()

if tracer:
    with tracer.start_span("operation"):
        # Perform operation with tracing
        pass
else:
    # Perform operation without tracing
    pass
```

### 2. Span Sampling

Implement span sampling for high-volume applications:

```python
import random
from honeyhive import HoneyHiveTracer

class SampledTracer:
    def __init__(self, sample_rate=0.1):
        self.tracer = HoneyHiveTracer()
        self.sample_rate = sample_rate
    
    def should_trace(self):
        """Determine if current operation should be traced."""
        return random.random() < self.sample_rate
    
    def start_span(self, name, attributes=None):
        """Start span only if sampling allows."""
        if self.should_trace():
            return self.tracer.start_span(name, attributes)
        else:
            # Return a no-op context manager
            return NoOpSpan()
    
    def enrich_span(self, name, attributes=None):
        """Enrich span only if sampling allows."""
        if self.should_trace():
            return self.tracer.enrich_span(name, attributes)
        else:
            return NoOpSpan()

class NoOpSpan:
    """No-op span for when tracing is disabled."""
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_attribute(self, key, value):
        pass

# Usage
sampled_tracer = SampledTracer(sample_rate=0.1)

# Only 10% of operations will be traced
with sampled_tracer.start_span("high-volume-operation"):
    # Perform operation
    pass
```

---

## Testing Patterns

### 1. Test Configuration

Configure tracer for testing:

```python
import pytest
from honeyhive import HoneyHiveTracer

@pytest.fixture
def test_tracer():
    """Create a test tracer."""
    tracer = HoneyHiveTracer(
        api_key="test-key",
        project="test-project",
        source="test",
        test_mode=True
    )
    
    yield tracer
    
    # Cleanup
    tracer.reset()

def test_tracing_functionality(test_tracer):
    """Test that tracing works correctly."""
    
    with test_tracer.start_span("test-operation") as span:
        span.set_attribute("test.attribute", "test-value")
        
        # Verify span was created
        assert span is not None
        assert span.get_attribute("test.attribute") == "test-value"
```

### 2. Mock Tracer

Use mocks for testing:

```python
from unittest.mock import Mock, patch
from honeyhive import HoneyHiveTracer

@pytest.fixture
def mock_tracer():
    """Create a mock tracer for testing."""
    return Mock(spec=HoneyHiveTracer)

def test_with_mock_tracer(mock_tracer):
    """Test using a mock tracer."""
    
    # Configure mock
    mock_span = Mock()
    mock_tracer.start_span.return_value.__enter__.return_value = mock_span
    
    # Use mock tracer
    with mock_tracer.start_span("test-operation"):
        pass
    
    # Verify mock was called
    mock_tracer.start_span.assert_called_once_with("test-operation")
```

---

## Best Practices

### 1. Initialization
- Initialize tracer once at application startup
- Use environment variables for configuration
- Validate configuration before use

### 2. Tracing
- Use decorators for simple functions
- Use manual spans for complex operations
- Set meaningful span names and attributes

### 3. Error Handling
- Always handle errors gracefully
- Set error attributes on spans
- Implement retry logic when appropriate

### 4. Performance
- Use conditional tracing for performance-critical paths
- Implement span sampling for high-volume applications
- Monitor tracing overhead

### 5. Testing
- Use test mode for unit tests
- Mock tracer for integration tests
- Test error scenarios

---

This guide covers the essential usage patterns for the HoneyHive SDK. For more advanced patterns and specific use cases, refer to the other documentation files.
