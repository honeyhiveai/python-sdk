# HoneyHive Tracer Documentation

The HoneyHive tracer is a comprehensive OpenTelemetry-based tracing solution that provides automatic instrumentation, custom decorators, and seamless integration with the HoneyHive platform.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Decorators](#decorators)
- [HTTP Instrumentation](#http-instrumentation)
- [Asyncio Instrumentation](#asyncio-instrumentation)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage]
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

The HoneyHive tracer replaces the legacy `traceloop` implementation with a modern OpenTelemetry-based solution. It provides:

- **Automatic Instrumentation**: HTTP requests, asyncio operations, and custom functions
- **Custom Decorators**: `@trace`, `@atrace`, and `@trace_class` for manual instrumentation
- **HoneyHive Integration**: Seamless session tracking and event creation
- **Performance Optimized**: Conditional tracing and span filtering
- **OpenTelemetry Compatible**: Standard-compliant tracing with custom processors
- **Comprehensive Testing**: 62% code coverage with 151 passing tests

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HoneyHive Tracer                        │
├─────────────────────────────────────────────────────────────────┤
│  Core Components                                               │
│  ├── HoneyHiveOTelTracer (Main Tracer) - 51% coverage        │
│  ├── HoneyHiveSpanProcessor (Custom Processing)               │
│  ├── HoneyHiveSpanExporter (Event Creation) - 91% coverage   │
│  └── FunctionInstrumentor (Decorator System)                  │
├─────────────────────────────────────────────────────────────────┤
│  Instrumentation Layers                                        │
│  ├── HTTP Instrumentation (requests, httpx) - 46% coverage    │
│  ├── Asyncio Instrumentation (coroutines, tasks) - 44% coverage│
│  └── Custom Instrumentation (decorators) - 83% coverage       │
├─────────────────────────────────────────────────────────────────┤
│  OpenTelemetry Integration                                     │
│  ├── TracerProvider                                           │
│  ├── BatchSpanProcessor                                       │
│  ├── OTLPSpanExporter                                         │
│  └── ConsoleSpanExporter                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Basic Setup

```python
from honeyhive.tracer import HoneyHiveOTelTracer

# Initialize the tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="your-project",
    source="your-source"
)

# The tracer automatically sets up OpenTelemetry components
```

### Using Decorators

```python
from honeyhive.tracer import trace, atrace

@trace
def my_function():
    return "Hello, World!"

@atrace
async def my_async_function():
    await asyncio.sleep(1)
    return "Async Hello!"

# Class-level instrumentation
from honeyhive.tracer import trace_class

@trace_class
class MyService:
    def method1(self):
        return "Method 1"
    
    async def method2(self):
        return "Method 2"
```

## Core Components

### HoneyHiveOTelTracer

The main tracer class that orchestrates all OpenTelemetry components:

```python
class HoneyHiveOTelTracer:
    """
    Main OpenTelemetry-based tracer for HoneyHive.
    
    Features:
    - Automatic OpenTelemetry initialization
    - Session management and context propagation
    - Performance optimizations and conditional tracing
    - Test mode for development and testing
    """
```

**Key Features:**
- **Test Mode**: Simplified initialization for testing environments
- **Performance Optimization**: Conditional tracing based on duration and rate limits
- **Context Management**: Automatic baggage and context propagation
- **Error Handling**: Graceful handling of initialization failures

### HoneyHiveSpanProcessor

Custom span processor that enriches spans with HoneyHive-specific metadata:

```python
class HoneyHiveSpanProcessor:
    """
    Custom span processor that adds HoneyHive context to spans.
    
    Features:
    - Context caching for performance
    - Automatic cleanup and memory management
    - Graceful error handling
    """
```

### HoneyHiveSpanExporter

Custom span exporter that converts OpenTelemetry spans to HoneyHive events:

```python
class HoneyHiveSpanExporter:
    """
    Exports OpenTelemetry spans to HoneyHive as events.
    
    Features:
    - Batch processing for performance
    - Automatic event creation and updates
    - Error handling and retry logic
    """
```

## Decorators

### @trace

Universal decorator that automatically handles both synchronous and asynchronous functions:

```python
from honeyhive.tracer import trace

@trace
def sync_function():
    return "sync result"

@trace
async def async_function():
    await asyncio.sleep(0.1)
    return "async result"
```

**Features:**
- Automatic async/sync detection
- Performance optimization
- Context propagation
- Error handling

### @atrace

Legacy decorator for explicit async function tracing (maintained for backward compatibility):

```python
from honeyhive.tracer import atrace

@atrace
async def async_function():
    return "async result"

# Note: Will raise ValueError if used on sync functions
```

### @trace_class

Class-level decorator for bulk method instrumentation:

```python
from honeyhive.tracer import trace_class

@trace_class
class MyService:
    def method1(self):
        return "method1"
    
    async def method2(self):
        return "method2"
    
    def __init__(self):  # Dunder methods are automatically excluded
        pass
```

**Features:**
- Automatic method discovery
- Dunder method exclusion
- Include/exclude lists for selective instrumentation
- Performance optimization

## HTTP Instrumentation

Automatic instrumentation for HTTP libraries:

```python
from honeyhive.tracer.http_instrumentation import instrument_http

# Enable HTTP tracing
instrument_http()

# Make HTTP requests - they're automatically traced
import requests
response = requests.get("https://api.example.com")

import httpx
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com")
```

**Supported Libraries:**
- `requests` - Synchronous HTTP requests
- `httpx` - Synchronous and asynchronous HTTP requests

**Features:**
- Automatic span creation
- Request/response metadata
- Error handling
- Performance metrics

## Asyncio Instrumentation

Automatic instrumentation for asyncio operations:

```python
from honeyhive.tracer.asyncio_tracer import instrument_asyncio

# Enable asyncio tracing
instrument_asyncio()

# All coroutines and tasks are automatically traced
async def my_coroutine():
    await asyncio.sleep(0.1)
    return "result"

# Create and run tasks
task = asyncio.create_task(my_coroutine())
result = await task
```

**Features:**
- Coroutine tracing
- Task creation tracking
- Context propagation
- Performance monitoring

## Configuration

### Environment Variables

```bash
# Required
export HH_API_KEY="your-api-key"
export HH_PROJECT="your-project"

# Optional
export HH_SOURCE="production"  # Default: "dev"
export HH_API_URL="https://api.honeyhive.ai"  # Default: production URL
export HH_DISABLE_HTTP_TRACING="false"  # Default: "false"
```

### Tracer Configuration

```python
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="your-project",
    source="production",
    server_url="https://custom.honeyhive.ai",
    verbose=True,
    test_mode=False,
    disable_http_tracing=False,
    disable_batch=False
)
```

### Performance Tuning

```python
from honeyhive.tracer import enable_tracing

# Enable tracing with performance optimizations
enable_tracing(
    enabled=True,
    min_duration_ms=1.0,      # Only trace operations > 1ms
    max_spans_per_second=1000  # Rate limit spans
)
```

## Advanced Usage

### Custom Span Attributes

```python
from honeyhive.tracer import enrich_span

@trace
def my_function():
    # Add custom metadata to the current span
    enrich_span(
        config={"model": "gpt-4"},
        metadata={"user_id": "123", "request_type": "chat"}
    )
    return "result"
```

### Session Management

```python
# Create tracer with existing session
tracer = HoneyHiveOTelTracer(
    session_id="existing-session-uuid",
    project="my-project"
)

# Link to existing session
tracer.link(carrier_data)
```

### Context Propagation

```python
from opentelemetry import context, baggage

# Set custom baggage
ctx = baggage.set_baggage("user_id", "123")
context.attach(ctx)

# Tracer automatically picks up context
tracer = HoneyHiveOTelTracer(project="my-project")
```

## Testing

### Test Mode

```python
# Initialize tracer in test mode
tracer = HoneyHiveOTelTracer(
    test_mode=True,
    project="test-project"
)

# Test mode provides:
# - Simplified initialization
# - Mock API responses
# - Generated session IDs
# - No external API calls
```

### Test Coverage

The tracer module maintains comprehensive test coverage:

- **Overall Coverage**: 62%
- **Total Tests**: 151
- **Test Success Rate**: 100%

**Coverage by Component:**
- `honeyhive_span_exporter.py`: 91%
- `custom.py`: 83%
- `__init__.py`: 60%
- `otel_tracer.py`: 51%
- `http_instrumentation.py`: 46%
- `asyncio_tracer.py`: 44%

### Running Tests

```bash
# Run all tracer tests
python -m pytest tests/test_otel_tracer.py tests/test_http_instrumentation.py tests/test_asyncio_tracer.py tests/test_custom_comprehensive.py tests/test_honeyhive_span_exporter_comprehensive.py

# Run specific test file
python -m pytest tests/test_otel_tracer.py

# Run with coverage
python -m coverage run --source=honeyhive.tracer -m pytest tests/
python -m coverage report --show-missing
```

## Troubleshooting

### Common Issues

#### 1. **Tracer Not Initializing**

```python
# Check environment variables
import os
print(os.getenv("HH_API_KEY"))
print(os.getenv("HH_PROJECT"))

# Use test mode for development
tracer = HoneyHiveOTelTracer(test_mode=True, project="test")
```

#### 2. **HTTP Tracing Not Working**

```python
# Check if HTTP tracing is disabled
from honeyhive.tracer.http_instrumentation import instrument_http

# Explicitly enable
instrument_http()

# Check environment variable
print(os.getenv("HH_DISABLE_HTTP_TRACING"))
```

#### 3. **Performance Issues**

```python
# Enable performance optimizations
from honeyhive.tracer import enable_tracing

enable_tracing(
    enabled=True,
    min_duration_ms=10.0,     # Only trace slow operations
    max_spans_per_second=100   # Reduce span volume
)
```

#### 4. **Context Propagation Issues**

```python
# Ensure context is properly attached
from opentelemetry import context

ctx = context.get_current()
if ctx is None:
    print("No current context")

# Check baggage
from honeyhive.tracer.otel_tracer import BaggageDict
baggage = BaggageDict.from_context(ctx)
print(baggage)
```

### Debug Mode

```python
# Enable verbose logging
tracer = HoneyHiveOTelTracer(verbose=True)

# Check tracer state
print(f"Initialized: {HoneyHiveOTelTracer._is_initialized}")
print(f"Tracing enabled: {HoneyHiveOTelTracer._tracing_enabled}")
print(f"Test mode: {HoneyHiveOTelTracer._test_mode}")
```

### Error Handling

The tracer provides comprehensive error handling:

- **Validation Errors**: Clear error messages for configuration issues
- **API Errors**: Graceful handling of network and authentication failures
- **Initialization Errors**: Fallback behavior when components fail to initialize
- **Runtime Errors**: Safe error handling during span processing

## Migration from Legacy Tracer

### Key Changes

1. **Import Changes**:
   ```python
   # Old
   from honeyhive.tracer import HoneyHiveTracer
   
   # New
   from honeyhive.tracer import HoneyHiveOTelTracer
   ```

2. **Initialization**:
   ```python
   # Old
   tracer = HoneyHiveTracer()
   
   # New
   tracer = HoneyHiveOTelTracer(
       api_key="your-key",
       project="your-project"
   )
   ```

3. **Decorators**:
   ```python
   # Old
   from honeyhive.tracer import trace
   
   # New (same import, enhanced functionality)
   from honeyhive.tracer import trace, atrace, trace_class
   ```

### Benefits of Migration

- **Better Performance**: OpenTelemetry optimizations
- **Standard Compliance**: Industry-standard tracing
- **Enhanced Features**: Conditional tracing, rate limiting
- **Better Testing**: Comprehensive test coverage
- **Future Proof**: Active OpenTelemetry ecosystem

## Support and Contributing

### Getting Help

- **Documentation**: This comprehensive guide
- **Examples**: See `examples.md` for practical usage
- **API Reference**: See `api_reference.md` for detailed API information
- **Issues**: Report bugs and request features through GitHub

### Contributing

The tracer module welcomes contributions:

1. **Test Coverage**: Improve test coverage for uncovered components
2. **Documentation**: Enhance examples and API documentation
3. **Performance**: Optimize tracing overhead and memory usage
4. **Features**: Add new instrumentation capabilities
5. **Bug Fixes**: Report and fix issues

### Development Setup

```bash
# Clone the repository
git clone https://github.com/honeyhiveai/python-sdk.git
cd python-sdk

# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Check coverage
python -m coverage run --source=honeyhive.tracer -m pytest tests/
python -m coverage report --show-missing
```

---

*This documentation covers the HoneyHive tracer module as of the latest consolidation and improvements. For the most up-to-date information, refer to the source code and test suite.*
