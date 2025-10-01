# Current HoneyHive Tracer Features Analysis

## 🔍 Deep Analysis of Existing Tracer Features

Based on the codebase analysis, the current HoneyHive tracer has several sophisticated features that **MUST be preserved** and **properly integrated** with the new semantic convention architecture.

## 📋 Current Feature Inventory

### 1. **Core Tracing Features**

#### **@trace Decorator System**
- **Universal decorator**: Auto-detects sync/async functions
- **Event type specification**: `@trace(event_type=EventType.model, event_name="gpt_call")`
- **Class-level tracing**: `@trace_class` for automatic method tracing
- **Manual span management**: Context managers and direct span creation

#### **Span Enrichment System**
- **enrich_span()**: Add attributes to current active span
- **enrich_session()**: Add session-level context
- **Dynamic attribute handling**: Recursive attribute setting with type conversion
- **Context manager patterns**: `with enrich_span(...):`

### 2. **Multi-Instance Architecture**

#### **Tracer Registry System**
- **WeakValueDictionary registry**: Automatic cleanup of tracer instances
- **Tracer ID baggage propagation**: `honeyhive_tracer_id` in OpenTelemetry baggage
- **Auto-discovery**: `get_tracer_from_baggage()` for decorator resolution
- **Priority system**: Explicit tracer > Context tracer > Default tracer

#### **Session Management**
- **Per-instance sessions**: Each tracer maintains its own session
- **Session ID propagation**: Via baggage context for span processor
- **Session API integration**: Direct session creation and management

### 3. **Advanced Attribute Processing**

#### **HoneyHive Native Attributes**
Current span processor handles these **honeyhive_*** attributes:

**Basic Attributes:**
- `honeyhive_event_type`, `honeyhive_event_name`, `honeyhive_event_id`
- `honeyhive_source`, `honeyhive_project`, `honeyhive_session_id`
- `honeyhive_user_id`, `honeyhive_session_name`

**Complex Attributes:**
- `honeyhive_inputs`, `honeyhive_config`, `honeyhive_metadata`
- `honeyhive_metrics`, `honeyhive_feedback`, `honeyhive_outputs`

#### **Dynamic Attribute Normalization**
- **Recursive attribute setting**: `_set_span_attributes()` with nested dict/list handling
- **Type conversion**: Automatic conversion of enums, complex objects to strings
- **JSON serialization**: Fallback for unserializable objects

### 4. **Context and Baggage Management**

#### **Baggage Propagation**
- **Session context**: `session_id`, `project`, `source` in baggage
- **Experiment context**: `experiment_id`, `experiment_name`, `experiment_variant`
- **Tracer identification**: `honeyhive_tracer_id` for multi-instance support

#### **Context Extraction**
- **Baggage attributes**: `_get_basic_baggage_attributes()`
- **Experiment attributes**: `_get_experiment_attributes()`
- **Compatibility attributes**: `_get_traceloop_compatibility_attributes()`

### 5. **Export Modes and Processing**

#### **Dual Export Architecture**
- **Client mode**: Direct HoneyHive API via `client.events.create()`
- **OTLP mode**: OpenTelemetry Protocol export with batch/immediate options
- **Mode detection**: Automatic selection based on initialization parameters

#### **Event Conversion**
- **Span-to-event mapping**: `_convert_span_to_event()` method
- **Event type detection**: Dynamic detection via `_detect_event_type()`
- **Attribute processing**: `_process_honeyhive_attributes()`

### 6. **Performance and Reliability Features**

#### **Graceful Degradation**
- **No-op spans**: Fallback when tracing unavailable
- **Error handling**: Comprehensive try/catch with logging
- **Shutdown detection**: Prevents operations during shutdown

#### **Caching and Optimization**
- **Pattern caching**: Compiled regex patterns for event type detection
- **Attribute caching**: Efficient attribute processing
- **Connection pooling**: Optimized HTTP client management

## 🚨 Critical Integration Points for RC3

### 1. **HoneyHive Native Attribute Priority**

The new semantic convention system MUST respect existing `honeyhive_*` attributes:

```python
# CRITICAL: HoneyHive native attributes must have HIGHEST priority
CONVENTION_PRIORITY = [
    "honeyhive_native",  # HIGHEST - existing honeyhive_* attributes
    "openllmetry",       # New semantic conventions
    "openinference", 
    "openlit"
]
```

### 2. **Preserve @trace Decorator Functionality**

The `@trace` decorator currently sets these attributes that semantic convention mapper must handle:

```python
# From decorators.py - these must be preserved
span.set_attribute("honeyhive_event_type", event_type)
span.set_attribute("honeyhive_event_name", event_name)
span.set_attribute("honeyhive_inputs", inputs)
span.set_attribute("honeyhive_outputs", outputs)
span.set_attribute("honeyhive_config", config)
span.set_attribute("honeyhive_metadata", metadata)
```

### 3. **Multi-Instance Session Isolation**

The semantic convention mapper must respect per-instance sessions:

```python
# CRITICAL: Session ID must come from tracer instance, not just baggage
session_id = None
if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
    session_id = self.tracer_instance.session_id  # PRIORITY 1

if not session_id:
    session_id = baggage.get_baggage("session_id", ctx)  # FALLBACK
```

### 4. **Experiment and Context Attributes**

Current experiment attribute handling must be preserved:

```python
# From span_processor.py - must be integrated
experiment_attrs = [
    "experiment_id", "experiment_name", 
    "experiment_variant", "experiment_group"
]
```

### 5. **Backward Compatibility with Event Conversion**

The existing `_convert_span_to_event()` logic must be enhanced, not replaced:

```python
# Current logic that must be preserved:
event_data = {
    "project": attributes.get("honeyhive.project", "Unknown"),
    "source": attributes.get("honeyhive.source", "python-sdk"),
    "session_id": session_id,
    "event_name": span.name,
    "event_type": attributes.get("honeyhive_event_type", detected_event_type),
    # ... existing logic must be enhanced with semantic conventions
}
```

## 🎯 RC3 Integration Strategy

### **Phase 1: Preserve Existing Functionality**

1. **HoneyHiveNativeExtractor** must handle all existing `honeyhive_*` attributes
2. **Maintain @trace decorator behavior** - no breaking changes
3. **Preserve multi-instance session isolation**
4. **Keep experiment attribute processing**

### **Phase 2: Enhance with Semantic Conventions**

1. **Add OpenLLMetry/OpenInference/OpenLit extractors** as lower priority
2. **Merge semantic convention data** with existing HoneyHive attributes
3. **Enhance event structure** while maintaining backward compatibility

### **Phase 3: Optimize Integration**

1. **Unified attribute processing** pipeline
2. **Performance optimization** with caching
3. **Comprehensive testing** against existing functionality

## 🔥 Critical Requirements for Semantic Convention Mapper

### **Must Handle Existing Patterns:**

```python
class HoneyHiveNativeExtractor(BaseExtractor):
    """CRITICAL: Must handle all existing honeyhive_* attribute patterns"""
    
    def extract_config(self, attributes: dict) -> dict:
        """Extract from honeyhive_config and individual config attributes"""
        config = {}
        
        # Handle complex honeyhive_config attribute
        if "honeyhive_config" in attributes:
            config.update(attributes["honeyhive_config"])
        
        # Handle individual config attributes
        for key, value in attributes.items():
            if key.startswith("honeyhive_") and key.endswith(("_model", "_provider", "_temperature")):
                clean_key = key.replace("honeyhive_", "")
                config[clean_key] = value
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Handle honeyhive_inputs and nested input attributes"""
        inputs = {}
        
        if "honeyhive_inputs" in attributes:
            inputs.update(attributes["honeyhive_inputs"])
        
        return inputs
```

### **Must Preserve Multi-Instance Context:**

```python
class SemanticConventionMapper:
    def __init__(self, tracer_instance=None):
        self.tracer_instance = tracer_instance  # CRITICAL: Must receive tracer instance
        
    def convert_to_honeyhive_schema(self, span_data: SpanData) -> dict:
        """Must respect tracer instance session and configuration"""
        
        # CRITICAL: Session ID from tracer instance takes priority
        session_id = None
        if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
            session_id = self.tracer_instance.session_id
```

## 💡 Success Criteria

1. **Zero Breaking Changes**: All existing `@trace` decorator usage continues to work
2. **Session Isolation**: Multi-instance tracers maintain separate sessions
3. **Attribute Preservation**: All `honeyhive_*` attributes processed correctly
4. **Performance Maintained**: No regression in span processing performance
5. **Enhanced Capability**: New semantic conventions properly mapped to HoneyHive schema

The semantic convention system must be **additive enhancement**, not a replacement of existing functionality.
