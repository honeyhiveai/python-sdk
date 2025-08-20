# HoneyHive Tracer Refactoring: From Traceloop to OpenTelemetry

## Overview

This document describes the refactoring of the HoneyHive Python SDK tracer from using Traceloop to a native OpenTelemetry implementation with wrapt for instrumentation.

## Changes Made

### 1. Replaced Traceloop with OpenTelemetry

**Before:**
- Used `traceloop-sdk` for tracing
- Traceloop handled span creation, propagation, and export
- Limited control over the tracing implementation

**After:**
- Native OpenTelemetry implementation using `opentelemetry-api`, `opentelemetry-sdk`
- Direct control over tracer provider, span processors, and exporters
- Better integration with the OpenTelemetry ecosystem

### 2. HTTP Instrumentation with Wrapt

**Before:**
- Traceloop provided HTTP instrumentation
- Limited customization options

**After:**
- Custom HTTP instrumentation using `wrapt` library
- Supports both `requests` and `httpx` libraries
- Configurable via environment variables
- Better control over what gets traced

### 3. New File Structure

```
src/honeyhive/tracer/
├── __init__.py              # Main entry point (backward compatible)
├── otel_tracer.py           # New OpenTelemetry tracer implementation
├── http_instrumentation.py  # HTTP instrumentation using wrapt
├── custom.py               # Updated to use new tracer
└── asyncio_tracer.py       # Unchanged (already used OpenTelemetry)
```

### 4. Updated Dependencies

**Removed:**
- `traceloop-sdk = "0.42.0"`

**Added:**
- `opentelemetry-api = ">=1.21.0"`
- `opentelemetry-sdk = ">=1.21.0"`
- `opentelemetry-exporter-otlp-proto-http = ">=1.21.0"`
- `opentelemetry-instrumentation = ">=0.42b0"`
- `wrapt = ">=1.16.0"`

## Key Features

### 1. Backward Compatibility

The refactoring maintains full backward compatibility:
- `HoneyHiveTracer` class interface remains the same
- `enrich_session()` function works as before
- `@trace` and `@atrace` decorators function identically
- All existing code should work without changes

### 2. Enhanced HTTP Tracing

- Automatic instrumentation of `requests` and `httpx` libraries
- Configurable via `HH_DISABLE_HTTP_TRACING` environment variable
- Detailed span attributes including method, URL, status code, and duration
- Support for both synchronous and asynchronous HTTP clients

### 3. Better OpenTelemetry Integration

- Native OpenTelemetry span and metric exporters
- Proper context propagation using W3C standards
- Support for custom span processors and exporters
- Better integration with OpenTelemetry ecosystem tools

### 4. Improved Error Handling

- Better error messages and validation
- Graceful fallbacks when instrumentation fails
- Thread-safe operations

## Usage

### Basic Usage (Unchanged)

```python
from honeyhive.tracer import HoneyHiveTracer

# Initialize tracer (same as before)
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="your-project"
)

# Use trace decorators (same as before)
from honeyhive.tracer.custom import trace, atrace

@trace
def my_function(x, y):
    return x + y

@atrace
async def my_async_function(x, y):
    return x + y
```

### HTTP Tracing

HTTP tracing is automatically enabled and will trace:
- `requests.Session.request()` calls
- `httpx.Client.request()` calls  
- `httpx.AsyncClient.request()` calls

To disable HTTP tracing:
```bash
export HH_DISABLE_HTTP_TRACING=true
```

### Manual HTTP Instrumentation

```python
from honeyhive.tracer.http_instrumentation import instrument_http, uninstrument_http

# Enable HTTP instrumentation
instrument_http()

# Disable HTTP instrumentation
uninstrument_http()
```

## Migration Guide

### For Existing Users

No changes required! The refactoring is completely backward compatible.

### For New Users

The API remains the same, but you now have access to:
- Better OpenTelemetry integration
- More configurable HTTP tracing
- Improved error handling and debugging

### Environment Variables

All existing environment variables continue to work:
- `HH_API_KEY`
- `HH_PROJECT`
- `HH_SOURCE`
- `HH_API_URL`

New environment variables:
- `HH_DISABLE_HTTP_TRACING` - Set to "true" to disable HTTP tracing

## Testing

Run the tests to verify the refactoring:

```bash
pytest tests/test_otel_tracer.py -v
```

## Benefits

1. **Reduced Dependencies**: Removed dependency on Traceloop SDK
2. **Better Control**: Direct control over OpenTelemetry configuration
3. **Improved Performance**: Native OpenTelemetry implementation
4. **Enhanced Debugging**: Better error messages and debugging capabilities
5. **Future-Proof**: Better alignment with OpenTelemetry standards
6. **Flexibility**: More options for customization and extension

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all OpenTelemetry dependencies are installed
2. **HTTP Tracing Not Working**: Check if `HH_DISABLE_HTTP_TRACING` is set
3. **Performance Issues**: Consider adjusting batch sizes in span processors

### Debug Mode

Enable verbose mode for debugging:
```python
tracer = HoneyHiveTracer(verbose=True)
```

## Future Enhancements

1. **Additional Instrumentation**: Support for more libraries (SQLAlchemy, Redis, etc.)
2. **Custom Exporters**: Support for custom span and metric exporters
3. **Sampling**: Configurable sampling strategies
4. **Metrics**: Enhanced metrics collection and export
5. **Distributed Tracing**: Better support for distributed tracing scenarios
