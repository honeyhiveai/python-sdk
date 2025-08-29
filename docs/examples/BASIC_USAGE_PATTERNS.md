# Basic Usage Patterns

Getting started and common usage patterns for the HoneyHive Python SDK.

## Table of Contents

- [Initialization Patterns](#initialization-patterns)
- [Tracing Patterns](#tracing-patterns)
- [Manual Span Management](#manual-span-management)
- [Session Management](#session-management)
- [Error Handling](#error-handling)
- [Configuration Patterns](#configuration-patterns)
- [Performance Patterns](#performance-patterns)
- [Testing Patterns](#testing-patterns)
- [Best Practices](#best-practices)

---

## Initialization Patterns

### 1. Primary Pattern (Recommended)

Use the official SDK pattern for production code:

```python
from honeyhive import HoneyHiveTracer

# Official SDK pattern (recommended)
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# Access the tracer instance
tracer = HoneyHiveTracer._instance

# With HTTP tracing enabled
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production",
    disable_http_tracing=False
)
```

### 1.1. Alternative Pattern (Enhanced)

For advanced use cases with additional options:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Enhanced initialization with all features available
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production",
    test_mode=True,  # Test mode support
    instrumentors=[OpenAIInstrumentor()],  # Auto-integration
    disable_http_tracing=True  # Performance control
)
```

**Note:** The `init()` method now supports ALL constructor features and is the recommended way to initialize the tracer. It follows the official HoneyHive SDK documentation pattern and provides the same functionality as the constructor.

## Environment-Based Configuration

Use environment variables for configuration:

```python
import os
from honeyhive import HoneyHiveTracer

# Set environment variables
os.environ["HH_API_KEY"] = "your-api-key"
os.environ["HH_PROJECT"] = "my-project"
os.environ["HH_SOURCE"] = "production"

# Initialize tracer (automatically reads environment)
tracer = HoneyHiveTracer.init()
```

## Conditional Initialization

Initialize based on environment or configuration:

```python
import os
from honeyhive import HoneyHiveTracer

def create_tracer():
    """Create tracer based on environment."""
    
    if os.getenv("ENVIRONMENT") == "production":
        return HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            source="production"
        )
    else:
        # Development mode
        return HoneyHiveTracer.init(
            api_key="dev-key",
            project="dev-project",
            source="development"
        )

# Initialize and get tracer instance
tracer = HoneyHiveTracer.init()
```

## Singleton Pattern Usage

The tracer is a singleton, so you can access it from anywhere:

```python
from honeyhive import HoneyHiveTracer

# Initialize once using the recommended pattern
tracer = HoneyHiveTracer.init(
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

### 1. Basic Tracing

Use the `@trace` decorator for automatic tracing:

```python
from honeyhive import trace

@trace(event_type="demo", event_name="my_function")
def my_function():
    return "Hello, World!"

@trace(event_type="demo", event_name="my_async_function")
async def my_async_function():
    await asyncio.sleep(0.1)
    return "Hello, Async World!"
```

### 2. Class Tracing

Use the `@trace_class` decorator for automatic method tracing:

```python
from honeyhive import trace_class

@trace_class
class DataProcessor:
    def process_data(self, data):
        """This method will be automatically traced."""
        return data.upper()
    
    def analyze_data(self, data):
        """This method will also be automatically traced."""
        return len(data)
```

## Manual Span Management

Create and manage spans manually:

```python
from honeyhive import HoneyHiveTracer

# Initialize tracer
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# Get tracer instance
tracer = HoneyHiveTracer._instance

def complex_operation():
    with tracer.start_span("data-processing") as span:
        # Set span attributes
        span.set_attribute("operation.type", "batch")
        span.set_attribute("data.size", 1000)
        
        # Process data
        result = process_large_dataset()
        
        # Add result attributes
        span.set_attribute("operation.result", "success")
```

### 4. Span Enrichment

Enrich existing spans with additional context:

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init()

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

tracer = HoneyHiveTracer.init(
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

tracer = HoneyHiveTracer.init()

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
        self.tracer = HoneyHiveTracer.init()
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

tracer = HoneyHiveTracer.init()

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

tracer = HoneyHiveTracer.init()

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
tracer = HoneyHiveTracer.init(**config)
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
    
    return HoneyHiveTracer.init(**config)

# Usage
tracer = create_tracer_from_config("config/honeyhive.json")
```



### 4. Experiment Environment Variables

Configure experiment tracking using environment variables:

```python
import os
from honeyhive import HoneyHiveTracer

# Set experiment environment variables
os.environ["HH_EXPERIMENT_ID"] = "exp_12345"
os.environ["HH_EXPERIMENT_NAME"] = "model_comparison"
os.environ["HH_EXPERIMENT_VARIANT"] = "baseline"
os.environ["HH_EXPERIMENT_GROUP"] = "control"
os.environ["HH_EXPERIMENT_METADATA"] = '{"model_type": "gpt-4", "temperature": 0.7}'

# Initialize tracer (automatically picks up experiment variables)
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# All spans automatically include experiment attributes
with tracer.start_span("model_inference") as span:
    # span.attributes automatically includes:
    # - honeyhive.experiment_id: "exp_12345"
    # - honeyhive.experiment_name: "model_comparison"
    # - honeyhive.experiment_variant: "baseline"
    # - honeyhive.experiment_group: "control"
    # - honeyhive.experiment_metadata.model_type: "gpt-4"
    # - honeyhive.experiment_metadata.temperature: "0.7"
    pass
```

### 5. MLflow Integration

Automatically detect MLflow experiment variables:

```python
import os
from honeyhive import HoneyHiveTracer

# MLflow automatically sets these environment variables
# os.environ["MLFLOW_EXPERIMENT_ID"] = "mlflow_exp_123"
# os.environ["MLFLOW_EXPERIMENT_NAME"] = "my_mlflow_experiment"

# Initialize tracer (automatically detects MLflow variables)
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# Experiment context automatically available in all spans
with tracer.start_span("mlflow_training") as span:
    # span.attributes automatically includes:
    # - honeyhive.experiment_id: "mlflow_exp_123"
    # - honeyhive.experiment_name: "my_mlflow_experiment"
    pass
```

### 6. Weights & Biases Integration

Automatically detect Weights & Biases environment variables:

```python
import os
from honeyhive import HoneyHiveTracer

# Weights & Biases automatically sets these environment variables
# os.environ["WANDB_RUN_ID"] = "wandb_run_456"
# os.environ["WANDB_PROJECT"] = "my_wandb_project"

# Initialize tracer (automatically detects W&B variables)
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production"
)

# Experiment context automatically available in all spans
with tracer.start_span("wandb_training") as span:
    # span.attributes automatically includes:
    # - honeyhive.experiment_id: "wandb_run_456"
    # - honeyhive.experiment_name: "my_wandb_project"
    pass
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
        return HoneyHiveTracer.init(
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
        self.tracer = HoneyHiveTracer.init()
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
    tracer = HoneyHiveTracer.init(
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

def test_with_mock_tracer():
    """Test using a mock tracer."""
    
    # Create mock tracer
    mock_tracer = Mock(spec=HoneyHiveTracer)
    mock_span = Mock()
    mock_tracer.start_span.return_value.__enter__.return_value = mock_span
    
    # Test with mock
    with mock_tracer.start_span("test-operation") as span:
        span.set_attribute("test.attribute", "test-value")
        
        # Verify mock was called
        mock_span.set_attribute.assert_called_with("test.attribute", "test-value")
```

---

## Best Practices

### 1. Initialization
- Use `HoneyHiveTracer.init()` for production code
- Use environment variables for configuration
- Initialize once at application startup

### 2. Tracing
- Use `@trace` decorator for automatic tracing
- Add meaningful span names and attributes
- Handle errors gracefully in spans

### 3. Error Handling
- Always use try-catch blocks in traced functions
- Set error attributes on spans when exceptions occur
- Log errors appropriately

### 4. Performance
- Use conditional tracing for high-volume operations
- Implement span sampling for production workloads
- Monitor tracing overhead

### 5. Testing
- Use test fixtures for consistent tracer setup
- Mock external dependencies
- Test both success and error scenarios
