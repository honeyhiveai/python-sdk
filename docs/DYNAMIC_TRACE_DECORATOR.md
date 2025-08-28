# Dynamic Trace Decorator

## Overview

The **Dynamic Trace Decorator** (`@dynamic_trace`) is a unified tracing solution that automatically detects whether a function is synchronous or asynchronous and applies the appropriate tracing wrapper. This eliminates the need to choose between different decorators while maintaining all existing functionality.

## 🆕 What's New

- **Unified Interface**: Single decorator for both sync and async functions
- **Automatic Detection**: No manual configuration needed
- **Zero Breaking Changes**: All existing decorators continue to work
- **Enhanced Developer Experience**: Less cognitive load when writing traced functions

## 🚀 Quick Start

### Basic Usage

```python
from honeyhive.tracer.decorators import dynamic_trace

# Automatically detected as sync function
@dynamic_trace(event_type="demo", event_name="sync_function")
def sync_function(name: str) -> str:
    return f"Hello, {name}!"

# Automatically detected as async function
@dynamic_trace(event_type="demo", event_name="async_function")
async def async_function(name: str) -> str:
    await asyncio.sleep(0.1)
    return f"Hello, {name}!"

# Both work with the same decorator!
result1 = sync_function("Alice")
result2 = await async_function("Bob")
```

### With All Parameters

```python
@dynamic_trace(
    event_type="llm",
    event_name="chat_completion",
    inputs={"model": "gpt-4", "messages": user_messages},
    metadata={"user_id": "123", "session_id": "sess_456"},
    config={"temperature": 0.7, "max_tokens": 1000},
    metrics={"token_count": 150},
    feedback={"rating": 5, "comment": "Great response!"}
)
async def chat_completion(messages, config):
    # Your LLM call here
    response = await llm_client.chat(messages, **config)
    return response
```

## 🔧 How It Works

### Automatic Detection

The decorator uses Python's `inspect.iscoroutinefunction()` to automatically detect function types:

```python
def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    # Create span name from function
    span_name = event_name or f"{func.__module__}.{func.__name__}"
    
    # Check if the function is async
    if inspect.iscoroutinefunction(func):
        return _create_async_wrapper(...)  # Async wrapper
    else:
        return _create_sync_wrapper(...)   # Sync wrapper
```

### Wrapper Creation

Based on the detection, it creates the appropriate wrapper:

- **Sync Functions**: Get a regular wrapper that handles tracing synchronously
- **Async Functions**: Get an async wrapper that handles tracing asynchronously
- **Both**: Share the same logic for span attributes, error handling, and metadata

## 📋 Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `event_type` | `Optional[str]` | Type of traced event | `"llm"`, `"tool"`, `"chain"` |
| `event_name` | `Optional[str]` | Name of the traced event | `"chat_completion"`, `"data_processing"` |
| `inputs` | `Optional[Dict[str, Any]]` | Input data for the event | `{"user_input": "Hello"}` |
| `outputs` | `Optional[Dict[str, Any]]` | Output data for the event | `{"response": "Hi there!"}` |
| `metadata` | `Optional[Dict[str, Any]]` | Additional metadata | `{"user_id": "123"}` |
| `config` | `Optional[Dict[str, Any]]` | Configuration data | `{"temperature": 0.7}` |
| `metrics` | `Optional[Dict[str, Any]]` | Performance metrics | `{"duration_ms": 150}` |
| `feedback` | `Optional[Dict[str, Any]]` | User feedback | `{"rating": 5}` |
| `error` | `Optional[Exception]` | Error information | `ValueError("Invalid input")` |
| `event_id` | `Optional[str]` | Unique event identifier | `"evt_123456"` |
| `**kwargs` | `Any` | Additional attributes | `custom_attr="value"` |

## 💡 Usage Patterns

### 1. Simple Tracing

```python
@dynamic_trace
def simple_function():
    return "Hello, World!"
```

### 2. Named Events

```python
@dynamic_trace(event_type="api", event_name="user_creation")
async def create_user(user_data: dict):
    # Create user logic
    return {"user_id": "123", "status": "created"}
```

### 3. Rich Metadata

```python
@dynamic_trace(
    event_type="llm",
    event_name="text_generation",
    inputs={"prompt": user_prompt, "model": "gpt-4"},
    metadata={"user_id": user_id, "session_id": session_id},
    config={"temperature": 0.8, "max_tokens": 500}
)
async def generate_text(prompt: str, config: dict):
    # Text generation logic
    return {"generated_text": "Generated content..."}
```

### 4. Class Methods

```python
class UserService:
    @dynamic_trace(event_type="service", event_name="user_validation")
    def validate_user(self, user_data: dict) -> bool:
        # Validation logic
        return True
    
    @dynamic_trace(event_type="service", event_name="user_creation")
    async def create_user(self, user_data: dict) -> dict:
        # Async user creation
        await asyncio.sleep(0.1)
        return {"user_id": "123"}
```

### 5. Error Handling

```python
@dynamic_trace(
    event_type="data_processing",
    event_name="file_upload",
    error=ValueError("File too large")
)
def process_file(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Process file
    return {"status": "processed"}
```

## 🔄 Migration from Legacy Decorators

### Before (Legacy)

```python
from honeyhive.tracer.decorators import trace, atrace

@trace(event_type="demo", event_name="sync_function")
def sync_function():
    return "sync result"

@atrace(event_type="demo", event_name="async_function")
async def async_function():
    return "async result"
```

### After (Recommended)

```python
from honeyhive.tracer.decorators import dynamic_trace

@dynamic_trace(event_type="demo", event_name="sync_function")
def sync_function():
    return "sync result"

@dynamic_trace(event_type="demo", event_name="async_function")
async def async_function():
    return "async result"
```

### Benefits of Migration

- **Unified Interface**: Single decorator for all function types
- **Automatic Detection**: No need to remember which decorator to use
- **Consistent Patterns**: Same parameter interface across all functions
- **Future-Proof**: New features will be added to the unified decorator

## 🧪 Testing

The decorator includes comprehensive tests covering:

- Sync function detection and wrapping
- Async function detection and wrapping
- Parameter passing and validation
- Function signature preservation
- Class method handling
- Mixed usage scenarios

Run tests with:
```bash
PYTHONPATH=src python -m pytest tests/tracer/test_dynamic_trace.py -v
```

## 🔍 Examples

### Real-World LLM Integration

```python
@dynamic_trace(
    event_type="llm",
    event_name="openai_chat_completion",
    inputs={"model": "gpt-4", "messages": messages},
    metadata={"user_id": user_id, "session_id": session_id},
    config={"temperature": 0.7, "max_tokens": 1000}
)
async def chat_with_openai(messages: list, config: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": config["model"], "messages": messages, **config}
        )
        return response.json()
```

### Data Processing Pipeline

```python
@dynamic_trace(
    event_type="pipeline",
    event_name="data_transformation",
    inputs={"input_format": "csv", "output_format": "json"},
    metadata={"pipeline_version": "1.0", "environment": "production"}
)
def transform_data(input_data: list, config: dict) -> dict:
    # Data transformation logic
    transformed = []
    for item in input_data:
        transformed.append({
            "id": item["id"],
            "processed_value": item["value"] * config["multiplier"]
        })
    
    return {"transformed_data": transformed, "count": len(transformed)}
```

## 🚨 Error Handling

The decorator provides comprehensive error handling:

- **Automatic Error Spans**: Creates separate spans for errors
- **Duration Tracking**: Measures execution time even when errors occur
- **Error Context**: Captures error type, message, and stack trace
- **Graceful Fallback**: Continues to work even if tracing fails

```python
@dynamic_trace(event_type="demo", event_name="risky_operation")
def risky_function():
    # This will create an error span if an exception occurs
    result = 1 / 0  # This will raise ZeroDivisionError
    return result
```

## 🔧 Advanced Usage

### Custom Span Names

```python
@dynamic_trace(
    event_name="custom.operation.name",
    event_type="custom"
)
def custom_function():
    return "custom result"
```

### Dynamic Metadata

```python
def create_traced_function(user_id: str):
    @dynamic_trace(
        event_type="user_operation",
        metadata={"user_id": user_id, "timestamp": time.time()}
    )
    def user_specific_function():
        return f"Operation for user {user_id}"
    
    return user_specific_function

# Usage
traced_func = create_traced_function("user_123")
result = traced_func()
```

### Conditional Tracing

```python
def conditional_trace(enable_tracing: bool = True):
    if enable_tracing:
        return dynamic_trace(event_type="conditional")
    else:
        return lambda func: func  # No-op decorator

@conditional_trace(enable_tracing=True)
def traced_function():
    return "This function is traced"

@conditional_trace(enable_tracing=False)
def untraced_function():
    return "This function is not traced"
```

## 📊 Performance Considerations

- **Minimal Overhead**: Function type detection is done once at decoration time
- **Efficient Wrappers**: Wrappers are created once and reused
- **No Runtime Cost**: Detection logic doesn't impact function execution
- **Memory Efficient**: Shared logic between sync and async wrappers

## 🔮 Future Enhancements

Potential improvements could include:

- **Generator Function Support**: Automatic detection of generator functions
- **Enhanced Coroutine Detection**: Support for more complex async patterns
- **Performance Optimizations**: Further optimization of wrapper creation
- **Additional Function Types**: Support for more Python function types

## 📚 Related Documentation

- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Examples](examples/README.md)** - Practical usage examples
- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Technical details
- **[Feature List](FEATURE_LIST.md)** - Complete feature overview

## 🤝 Contributing

We welcome contributions to improve the dynamic trace decorator! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Last Updated**: January 2025  
**SDK Version**: Latest  
**Feature Status**: Production Ready
