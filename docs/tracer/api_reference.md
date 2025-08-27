# HoneyHive Tracer API Reference

This document provides detailed API reference for all classes, functions, and decorators in the HoneyHive tracer module.

## Table of Contents

- [Core Classes](#core-classes)
- [Decorators](#decorators)
- [Functions](#functions)
- [Constants](#constants)
- [Types](#types]
- [Error Handling](#error-handling)

## Core Classes

### HoneyHiveOTelTracer

The main OpenTelemetry-based tracer class that orchestrates all tracing components.

```python
class HoneyHiveOTelTracer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        session_name: Optional[str] = None,
        source: Optional[str] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        disable_http_tracing: bool = False,
        disable_batch: bool = False,
        verbose: bool = False,
        inputs: Optional[Dict[str, Any]] = None,
        is_evaluation: bool = False,
        run_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        datapoint_id: Optional[str] = None,
        link_carrier: Optional[Dict[str, Any]] = None,
        test_mode: bool = False
    ) -> None
```

**Parameters:**
- `api_key`: HoneyHive API key (required via environment or parameter)
- `project`: Project identifier (required via environment or parameter)
- `session_name`: Custom session name (optional, defaults to script name)
- `source`: Source identifier (optional, defaults to "dev")
- `server_url`: HoneyHive server URL (optional, defaults to production)
- `session_id`: Existing session ID (optional, must be valid UUID)
- `disable_http_tracing`: Disable HTTP instrumentation (optional)
- `disable_batch`: Disable batch processing (optional)
- `verbose`: Enable verbose logging (optional)
- `inputs`: Input parameters for the session (optional)
- `is_evaluation`: Enable evaluation mode (optional)
- `run_id`: Evaluation run ID (optional)
- `dataset_id`: Evaluation dataset ID (optional)
- `datapoint_id`: Evaluation datapoint ID (optional)
- `link_carrier`: Link to existing session (optional)
- `test_mode`: Enable test mode for simplified initialization (optional)

**Class Attributes:**
- `api_key`: The configured API key (static)
- `server_url`: The configured server URL (static)
- `tracer_provider`: OpenTelemetry tracer provider (static)
- `meter_provider`: OpenTelemetry meter provider (static)
- `propagator`: OpenTelemetry propagator (static)
- `tracer`: OpenTelemetry tracer instance (static)
- `meter`: OpenTelemetry meter instance (static)
- `span_processor`: Custom span processor (static)
- `_is_initialized`: Internal initialization flag (static)
- `_test_mode`: Test mode flag (static)
- `verbose`: Verbose logging flag (static)

**Instance Attributes:**
- `_api_key`: Instance API key reference
- `project`: The configured project
- `source`: The configured source
- `session_id`: The session identifier
- `session_name`: The session name
- `inputs`: Input parameters
- `metadata`: Session metadata
- `baggage`: OpenTelemetry baggage context
- `_test_mode`: Test mode flag

**Methods:**

#### `enable_tracing(enabled: bool = True, min_duration_ms: float = 1.0, max_spans_per_second: int = 1000) -> None`
Enable or disable tracing with performance optimizations.

**Parameters:**
- `enabled`: Whether to enable tracing
- `min_duration_ms`: Minimum span duration to trace (in milliseconds)
- `max_spans_per_second`: Maximum spans per second to prevent overwhelming

#### `is_tracing_enabled() -> bool`
Check if tracing is currently enabled.

**Returns:**
- `True` if tracing is enabled, `False` otherwise

#### `should_trace_span(estimated_duration_ms: float = 0.0) -> bool`
Check if a span should be traced based on performance criteria.

**Parameters:**
- `estimated_duration_ms`: Estimated duration of the operation in milliseconds

**Returns:**
- `True` if the span should be traced, `False` otherwise

#### `flush() -> None`
Force flush all pending spans to the exporter.

#### `link(carrier: Dict[str, Any]) -> None`
Link to an existing session using carrier data.

**Parameters:**
- `carrier`: Session linking data

#### `session_start() -> None`
Start a new HoneyHive session (internal method).

#### `_initialize_otel(disable_batch: bool = False) -> None`
Initialize OpenTelemetry components (internal method).

#### `_initialize_otel_test_mode() -> None`
Initialize OpenTelemetry components in test mode (internal method).

### HoneyHiveSpanProcessor

Custom span processor that enriches spans with HoneyHive-specific metadata and context.

```python
class HoneyHiveSpanProcessor:
    def __init__(self) -> None
```

**Attributes:**
- `_context_cache`: Cache for context lookups (TTL-based)
- `_cache_ttl`: Cache time-to-live in operations (default: 1000)
- `_operation_count`: Counter for cache cleanup operations

**Methods:**

#### `on_start(span: ReadableSpan, parent_context: Optional[Context] = None) -> None`
Called when a span starts. Adds HoneyHive context and attributes.

**Parameters:**
- `span`: The span that is starting
- `parent_context`: The parent context (optional)

#### `on_end(span: ReadableSpan) -> None`
Called when a span ends. Performs cleanup and final processing.

**Parameters:**
- `span`: The span that is ending

#### `should_process_span(span: ReadableSpan) -> bool`
Determine if a span should be processed by this processor.

**Parameters:**
- `span`: The span to check

**Returns:**
- `True` if the span should be processed, `False` otherwise

#### `shutdown() -> None`
Shutdown the processor and clean up resources.

#### `force_flush(timeout_millis: Optional[float] = None) -> bool`
Force flush pending spans.

**Parameters:**
- `timeout_millis`: Timeout for flush operation (optional)

**Returns:**
- Always returns `True` (success)

#### `_cleanup_cache() -> None`
Clean up expired cache entries (internal method).

### HoneyHiveSpanExporter

Custom span exporter that converts OpenTelemetry spans to HoneyHive events.

```python
class HoneyHiveSpanExporter:
    def __init__(
        self,
        batch_size: int = 100,
        delay: float = 2.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> None
```

**Parameters:**
- `batch_size`: Number of spans to batch together
- `delay`: Delay between batch exports in seconds
- `max_retries`: Maximum number of retry attempts
- `retry_delay`: Delay between retries in seconds

**Methods:**

#### `export(spans: Sequence[ReadableSpan]) -> SpanExportResult`
Export a batch of spans to HoneyHive.

**Parameters:**
- `spans`: Sequence of spans to export

**Returns:**
- `SpanExportResult` indicating success or failure

#### `shutdown() -> None`
Shutdown the exporter and flush remaining spans.

#### `force_flush(timeout_millis: Optional[float] = None) -> bool`
Force flush pending spans.

**Parameters:**
- `timeout_millis`: Timeout for flush operation (optional)

**Returns:**
- `True` if flush was successful, `False` otherwise

### HTTPInstrumentor

HTTP instrumentation for requests and httpx libraries.

```python
class HTTPInstrumentor:
    def __init__(self) -> None
```

**Methods:**

#### `instrument() -> None`
Enable HTTP instrumentation for supported libraries.

#### `uninstrument() -> None`
Disable HTTP instrumentation.

#### `_is_http_tracing_disabled() -> bool`
Check if HTTP tracing is disabled via context baggage.

**Returns:**
- `True` if HTTP tracing is disabled, `False` otherwise

### AsyncioInstrumentor

Asyncio instrumentation for coroutines and tasks.

```python
class AsyncioInstrumentor:
    def __init__(self) -> None
```

**Methods:**

#### `instrument() -> None`
Enable asyncio instrumentation.

#### `uninstrument() -> None`
Disable asyncio instrumentation.

## Decorators

### @trace

Universal decorator that automatically handles both synchronous and asynchronous functions.

```python
@trace
def my_function():
    return "result"

@trace
async def my_async_function():
    await asyncio.sleep(0.1)
    return "async result"
```

**Features:**
- Automatic async/sync detection
- Performance optimization
- Context propagation
- Error handling
- Conditional tracing based on duration

### @atrace

Legacy decorator for explicit async function tracing (maintained for backward compatibility).

```python
@atrace
async def my_async_function():
    return "async result"

# Note: Will raise ValueError if used on sync functions
```

**Validation:**
- Ensures decorated function is async
- Raises `ValueError` for sync functions
- Maintains backward compatibility

### @trace_class

Class-level decorator for bulk method instrumentation.

```python
@trace_class
class MyService:
    def method1(self):
        return "method1"
    
    async def method2(self):
        return "method2"
    
    def __init__(self):  # Dunder methods are automatically excluded
        pass
```

**Parameters:**
- `include_list`: List of method names to include (optional)
- `exclude_list`: List of method names to exclude (optional)

**Features:**
- Automatic method discovery
- Dunder method exclusion
- Include/exclude lists for selective instrumentation
- Performance optimization

## Functions

### Global Instrumentation Functions

#### `instrument_http() -> None`
Enable HTTP instrumentation globally.

#### `uninstrument_http() -> None`
Disable HTTP instrumentation globally.

#### `instrument_asyncio() -> None`
Enable asyncio instrumentation globally.

#### `uninstrument_asyncio() -> None`
Disable asyncio instrumentation globally.

### Utility Functions

#### `enrich_span(config: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> None`
Enrich the current span with additional configuration and metadata.

**Parameters:**
- `config`: Configuration data to add to the span
- `metadata`: Metadata to add to the span

#### `reset_tracer_state() -> None`
Reset the global tracer state (useful for testing).

#### `enable_tracing(enabled: bool = True, min_duration_ms: float = 1.0, max_spans_per_second: int = 1000) -> None`
Enable or disable tracing globally with performance optimizations.

**Parameters:**
- `enabled`: Whether to enable tracing
- `min_duration_ms`: Minimum span duration to trace (in milliseconds)
- `max_spans_per_second`: Maximum spans per second to prevent overwhelming

## Constants

### Default Values

```python
DEFAULT_API_URL = "https://api.honeyhive.ai"
DEFAULT_SOURCE = "dev"
DEFAULT_BATCH_SIZE = 100
DEFAULT_BATCH_DELAY = 2.0
DEFAULT_CACHE_TTL = 1000
DEFAULT_MIN_DURATION_MS = 1.0
DEFAULT_MAX_SPANS_PER_SECOND = 1000
```

### Environment Variables

```python
HH_API_KEY = "HH_API_KEY"           # Required: API key
HH_PROJECT = "HH_PROJECT"           # Required: Project identifier
HH_SOURCE = "HH_SOURCE"             # Optional: Source identifier
HH_API_URL = "HH_API_URL"           # Optional: Server URL
HH_DISABLE_HTTP_TRACING = "HH_DISABLE_HTTP_TRACING"  # Optional: Disable HTTP tracing
```

## Types

### Type Aliases

```python
from typing import Dict, Any, Optional, Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry import context as Context

# Common type aliases used throughout the module
SpanExportResult = Any  # OpenTelemetry export result
BaggageDict = Any      # Custom baggage dictionary implementation
```

### Custom Types

#### `BaggageDict`
Custom implementation of OpenTelemetry baggage with additional functionality.

**Methods:**
- `update(data: Dict[str, Any]) -> BaggageDict`: Update baggage with new data
- `from_context(ctx: Context) -> BaggageDict`: Create from OpenTelemetry context
- `set_all_baggage(ctx: Context) -> Context`: Set all baggage in context
- `get(key: str, default: Any = None) -> Any`: Get baggage value

## Error Handling

### Exception Types

#### `SDKError`
Base exception for HoneyHive SDK errors.

```python
class SDKError(Exception):
    """Base exception for HoneyHive SDK errors."""
    pass
```

**Common Error Messages:**
- `"api_key must be a non-empty string"`
- `"project must be specified or set in environment variable HH_PROJECT"`
- `"session_id must be a valid UUID string"`
- `"project must be a non-empty string"`

### Error Handling Patterns

#### **Validation Errors**
Clear error messages for configuration issues:
```python
try:
    tracer = HoneyHiveOTelTracer(project="")
except SDKError as e:
    print(f"Configuration error: {e}")
```

#### **API Errors**
Graceful handling of network and authentication failures:
```python
# The tracer automatically handles API errors and continues operation
tracer = HoneyHiveOTelTracer(api_key="invalid-key")
# Will log error but continue initialization
```

#### **Initialization Errors**
Fallback behavior when components fail to initialize:
```python
# Test mode provides simplified initialization
tracer = HoneyHiveOTelTracer(test_mode=True, project="test")
```

#### **Runtime Errors**
Safe error handling during span processing:
```python
# Span processor continues operation even with errors
processor = HoneyHiveSpanProcessor()
# Safe fallback behavior
```

### Error Recovery

The tracer provides comprehensive error recovery:

1. **Graceful Degradation**: Continue operation even when components fail
2. **Fallback Behavior**: Use default values when configuration is invalid
3. **Error Logging**: Comprehensive error logging for debugging
4. **Safe Defaults**: Sensible defaults for all configuration options

### Debug Mode

Enable verbose logging for debugging:

```python
tracer = HoneyHiveOTelTracer(verbose=True)

# Check tracer state
print(f"Initialized: {HoneyHiveOTelTracer._is_initialized}")
print(f"Tracing enabled: {HoneyHiveOTelTracer._tracing_enabled}")
print(f"Test mode: {HoneyHiveOTelTracer._test_mode}")
```

---

*This API reference covers the current implementation of the HoneyHive tracer module. For examples and usage patterns, see the [examples.md](examples.md) file.*
