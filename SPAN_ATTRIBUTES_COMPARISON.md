# Span Attributes Comparison: Our Implementation vs Official SDK

This document compares the span attributes and tracing behavior between our HoneyHive SDK implementation and the official SDK on the `remove-traceloop` branch.

## Overview

Both implementations use OpenTelemetry for tracing, but they differ in how they set span attributes, handle session context, and manage the tracing pipeline.

## Core Span Attributes Comparison

### 1. **Session Context Attributes**

| Attribute | Our Implementation | Official SDK | Notes |
|-----------|-------------------|--------------|-------|
| `honeyhive.session_id` | ✅ Set in `start_span()` | ✅ Set in `HoneyHiveSpanProcessor.on_start()` | Both set from baggage |
| `honeyhive.project` | ✅ Set in `start_span()` | ✅ Set in `HoneyHiveSpanProcessor.on_start()` | Both set from baggage |
| `honeyhive.source` | ✅ Set in `start_span()` | ✅ Set in `HoneyHiveSpanProcessor.on_start()` | Both set from baggage |
| `honeyhive.parent_id` | ❌ Not set | ✅ Set in `HoneyHiveSpanProcessor.on_start()` | Official SDK includes parent_id |

### 2. **Span Creation Method**

| Aspect | Our Implementation | Official SDK | Notes |
|--------|-------------------|--------------|-------|
| **Method** | `start_span()` context manager | `@trace` decorator | Different approaches |
| **Context Manager** | ✅ Direct span creation | ❌ No direct context manager | Our approach is more flexible |
| **Decorator Support** | ❌ No decorator support | ✅ Full decorator support | Official SDK has `@trace` and `@atrace` |

### 3. **Attribute Setting Strategy**

| Strategy | Our Implementation | Official SDK | Notes |
|----------|-------------------|--------------|-------|
| **Direct Setting** | ✅ In `start_span()` method | ❌ Not in main tracer | Our approach sets attributes directly |
| **Processor Setting** | ✅ In `HoneyHiveSpanProcessor.on_start()` | ✅ In `HoneyHiveSpanProcessor.on_start()` | Both use span processor |
| **Baggage Integration** | ✅ Full baggage support | ✅ Full baggage support | Both integrate with OpenTelemetry baggage |

## Detailed Implementation Comparison

### Our Implementation: `start_span()` Method

```python
@contextmanager
def start_span(
    self,
    name: str,
    session_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    **kwargs
):
    # Use tracer's session ID if none provided
    if session_id is None:
        session_id = self.session_id
    
    # Prepare attributes
    span_attributes = attributes or {}
    span_attributes.update(kwargs)
    
    # Add session information to attributes
    if session_id:
        span_attributes["honeyhive.session_id"] = session_id
        span_attributes["honeyhive.project"] = self.project
        span_attributes["honeyhive.source"] = self.source
    
    # Set up baggage
    baggage_items = {}
    if session_id:
        baggage_items["session_id"] = session_id
        baggage_items["project"] = self.project
        baggage_items["source"] = self.source
    
    # Create span context with baggage
    ctx = context.get_current()
    if baggage_items:
        for key, value in baggage_items.items():
            if value:
                ctx = baggage.set_baggage(key, str(value), ctx)
    
    # Start span with context
    with trace.get_tracer("honeyhive").start_as_current_span(
        name, 
        context=ctx,
        attributes=span_attributes
    ) as span:
        yield span
```

**Key Features:**
- ✅ Direct span attribute setting
- ✅ Automatic session context inclusion
- ✅ Baggage integration
- ✅ Context manager pattern
- ✅ Flexible attribute customization

### Official SDK: `HoneyHiveSpanProcessor.on_start()` Method

```python
def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None) -> None:
    # Get current context
    ctx = parent_context if parent_context is not None else context.get_current()
    if not ctx:
        return
    
    # Cache miss - compute attributes with early exit optimization
    attributes_to_set = {}
    
    # Add session_id from baggage (most important) - early exit if missing
    session_id = baggage.get_baggage('session_id', ctx)
    if not session_id:
        # No session_id means no HoneyHive context, skip processing
        return
    
    attributes_to_set["honeyhive.session_id"] = session_id
    
    # Add project from baggage - early exit if missing
    project = baggage.get_baggage('project', ctx)
    if not project:
        # No project means no HoneyHive context, skip processing
        return
        
    attributes_to_set["honeyhive.project"] = project
    
    # Add source from baggage
    source = baggage.get_baggage('source', ctx)
    if source:
        attributes_to_set["honeyhive.source"] = source
    
    # Also check for association_properties (legacy support)
    association_properties = ctx.get('association_properties')
    if association_properties and isinstance(association_properties, dict):
        for key, value in association_properties.items():
            if value is not None and not baggage.get_baggage(key, ctx):
                # Only set if not already set via baggage
                attributes_to_set[f"honeyhive.{key}"] = str(value)
    
    # Set all attributes at once (more efficient)
    for key, value in attributes_to_set.items():
        span.set_attribute(key, value)
```

**Key Features:**
- ✅ Automatic span attribute setting
- ✅ Performance optimization with caching
- ✅ Early exit optimization
- ✅ Legacy support for `association_properties`
- ✅ Efficient batch attribute setting

## Additional Attributes in Official SDK

### 1. **Decorator-Based Attributes**

The official SDK's `@trace` decorator sets additional attributes:

```python
# From custom.py
span.set_attribute("honeyhive_event_type", self.event_type)
span.set_attribute("honeyhive_outputs.result", json.dumps(result, default=str))
span.set_attribute("honeyhive_error", str(e))
```

**Additional Attributes Set by Decorators:**
- `honeyhive_event_type` - Type of traced event
- `honeyhive_outputs.result` - Function result/output
- `honeyhive_error` - Error information if function fails
- `honeyhive_prompt_template.template` - Template information
- `honeyhive_prompt_template.prompt` - Actual prompt
- `honeyhive_config` - Configuration data
- `honeyhive_metadata` - Metadata information
- `honeyhive_metrics` - Performance metrics
- `honeyhive_feedback` - User feedback
- `honeyhive_inputs` - Input data
- `honeyhive_outputs` - Output data

### 2. **Legacy Support Attributes**

The official SDK includes support for legacy `association_properties`:

```python
# Check for association_properties (legacy support)
association_properties = ctx.get('association_properties')
if association_properties and isinstance(association_properties, dict):
    for key, value in association_properties.items():
        if value is not None and not baggage.get_baggage(key, ctx):
            # Only set if not already set via baggage
            attributes_to_set[f"honeyhive.{key}"] = str(value)
```

**Our Implementation - Enhanced with Traceloop Compatibility:**

```python
# Also check for association_properties (legacy support) - only if needed
try:
    # Check if context has association_properties (legacy support)
    if hasattr(ctx, 'get') and callable(getattr(ctx, 'get', None)):
        association_properties = ctx.get('association_properties')
        if association_properties and isinstance(association_properties, dict):
            for key, value in association_properties.items():
                if value is not None and not baggage.get_baggage(key, ctx):
                    # Use traceloop.association.properties format for backend compatibility
                    attributes_to_set[f"traceloop.association.properties.{key}"] = str(value)
except Exception:
    # Silently ignore legacy property access errors
    pass
```

**Key Differences:**
- **Official SDK**: Uses `honeyhive.{key}` format
- **Our Implementation**: Uses `traceloop.association.properties.{key}` format for backend compatibility
- **Our Implementation**: Includes robust error handling and graceful degradation
- **Our Implementation**: Maintains compatibility with existing backend systems

## Performance Characteristics

### Our Implementation
- **Attribute Setting**: Direct setting in span creation
- **Caching**: No built-in caching
- **Optimization**: Manual optimization in span creation
- **Memory Usage**: Lower memory footprint
- **Flexibility**: High - direct control over attributes

### Official SDK
- **Attribute Setting**: Automatic via span processor
- **Caching**: Built-in context caching with TTL
- **Optimization**: Early exit, batch attribute setting
- **Memory Usage**: Higher due to caching
- **Flexibility**: Lower - automatic attribute setting

## Session Management Comparison

### Our Implementation
```python
def _initialize_session(self):
    """Initialize session management."""
    try:
        # Import session API here to avoid circular imports
        from ..api.session import SessionAPI
        from ..api.client import HoneyHive
        
        # Create client and session API
                    self.client = HoneyHive(
            api_key=self.api_key,
            base_url=config.api_url,
            test_mode=self.test_mode
        )
        self.session_api = SessionAPI(self.client)
        
        # Create a new session automatically
        session_response = self.session_api.start_session(
            project=self.project,
            session_name=self.session_name,
            source=self.source
        )
        
        self.session_id = session_response.session_id
        print(f"✓ HoneyHive session created: {self.session_id}")
        
    except Exception as e:
        if not self.test_mode:
            print(f"Warning: Failed to create session: {e}")
        self.session_id = None
        self.client = None
        self.session_api = None
```

**Features:**
- ✅ Automatic session creation during tracer initialization
- ✅ Session API integration
- ✅ Error handling with fallback
- ✅ Session ID management

### Official SDK
The official SDK doesn't have automatic session creation in the tracer. Sessions are managed separately through the main SDK.

## Recommendations

### 1. **Add Missing Attributes**
Our implementation should add:
- `honeyhive.parent_id` support
- Legacy `association_properties` support
- Decorator-based attribute setting

### 2. **Performance Optimizations**
Consider adding:
- Context caching for span attributes
- Early exit optimization
- Batch attribute setting

### 3. **Enhanced Decorator Support**
Add support for:
- `@trace` decorator
- `@atrace` decorator
- Automatic attribute setting based on function execution

### 4. **Maintain Current Strengths**
Keep our advantages:
- Direct span creation with context manager
- Automatic session management
- Flexible attribute customization
- Clean, simple API

## Conclusion

Our implementation provides a solid foundation with automatic session management and flexible span creation, while the official SDK offers more comprehensive attribute coverage and performance optimizations. The ideal approach would be to combine the best of both: our session management and flexibility with the official SDK's comprehensive attribute coverage and performance optimizations.
