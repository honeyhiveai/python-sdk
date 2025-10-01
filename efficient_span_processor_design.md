# Efficient Span Processor Design: Performance-Critical Dynamic Mapping

## Key Constraints & Requirements

### Performance Requirements:
- ✅ **Microsecond-level performance** - runs on every span
- ✅ **Zero allocation overhead** where possible
- ✅ **Minimal CPU cycles** for attribute processing
- ✅ **No I/O operations** in hot path
- ✅ **No ML/AI processing** - too heavy for tracer
- ✅ **No hot-reload** - updates via version upgrades only

### Deployment Model:
- ✅ **Static configuration** compiled into code
- ✅ **Version-based updates** via customer upgrades
- ✅ **Lightweight dynamic logic** for attribute mapping
- ✅ **Efficient pattern matching** using pre-compiled structures

## Efficient Dynamic Mapping Architecture

### 1. **Pre-Compiled Mapping Tables**

Instead of YAML configs, use **static Python dictionaries** compiled at import time:

```python
# semantic_mappings.py - Static, efficient mapping tables
SEMANTIC_CONVENTION_MAPPINGS = {
    # OpenLLMetry patterns (most common - check first)
    "openllmetry": {
        "detection_patterns": frozenset([
            "gen_ai.request.model",
            "gen_ai.system", 
            "gen_ai.usage.prompt_tokens"
        ]),
        "config_mappings": {
            "gen_ai.system": "provider",
            "gen_ai.request.model": "model",
            "gen_ai.request.streaming": "is_streaming"
        },
        "metadata_mappings": {
            "gen_ai.usage.prompt_tokens": "prompt_tokens",
            "gen_ai.usage.completion_tokens": "completion_tokens", 
            "gen_ai.usage.total_tokens": "total_tokens",
            "gen_ai.response.model": "response_model"
        },
        "message_pattern": "gen_ai.request.messages.{}.{}",
        "output_mappings": {
            "gen_ai.response.finish_reasons": "finish_reason"
        }
    },
    
    # OpenInference patterns
    "openinference": {
        "detection_patterns": frozenset([
            "llm.model_name",
            "llm.provider",
            "llm.token_count.prompt"
        ]),
        "config_mappings": {
            "llm.provider": "provider",
            "llm.model_name": "model"
        },
        "metadata_mappings": {
            "llm.token_count.prompt": "prompt_tokens",
            "llm.token_count.completion": "completion_tokens",
            "llm.token_count.total": "total_tokens"
        },
        "input_mappings": {
            "llm.input_messages": "chat_history"
        },
        "output_mappings": {
            "output.value": "content"
        }
    },
    
    # OpenLit patterns  
    "openlit": {
        "detection_patterns": frozenset([
            "gen_ai.usage.input_tokens",
            "gen_ai.usage.output_tokens"
        ]),
        "config_mappings": {
            "gen_ai.system": "provider",
            "gen_ai.request.model": "model"
        },
        "metadata_mappings": {
            "gen_ai.usage.input_tokens": "prompt_tokens",
            "gen_ai.usage.output_tokens": "completion_tokens"
        }
    }
}

# Priority order for convention detection (most common first)
CONVENTION_PRIORITY = ["openllmetry", "openinference", "openlit"]

# Pre-compiled regex patterns for efficient message extraction
MESSAGE_PATTERNS = {
    "openllmetry": re.compile(r"gen_ai\.request\.messages\.(\d+)\.(role|content|tool_calls\..*)")
}
```

### 2. **Lightweight Convention Detection**

```python
def _detect_semantic_convention(self, attributes: dict) -> str:
    """Fast convention detection using set intersection - O(1) average case"""
    
    attr_keys = frozenset(attributes.keys())
    
    # Check each convention in priority order
    for convention in CONVENTION_PRIORITY:
        detection_patterns = SEMANTIC_CONVENTION_MAPPINGS[convention]["detection_patterns"]
        
        # Fast set intersection to detect presence
        if detection_patterns & attr_keys:
            return convention
    
    return "honeyhive_legacy"  # Fallback
```

### 3. **Efficient Attribute Mapping**

```python
def _map_attributes_efficiently(self, attributes: dict) -> dict:
    """High-performance attribute mapping with minimal allocations"""
    
    # Pre-allocate result structure
    result = {
        "config": {},
        "inputs": {},
        "outputs": {},
        "metadata": {}
    }
    
    # Fast convention detection
    convention = self._detect_semantic_convention(attributes)
    
    if convention == "honeyhive_legacy":
        return self._map_legacy_attributes(attributes, result)
    
    mappings = SEMANTIC_CONVENTION_MAPPINGS[convention]
    
    # Direct dictionary lookups - O(1) for each mapping
    self._map_section_efficiently(attributes, mappings.get("config_mappings", {}), result["config"])
    self._map_section_efficiently(attributes, mappings.get("metadata_mappings", {}), result["metadata"])
    self._map_section_efficiently(attributes, mappings.get("output_mappings", {}), result["outputs"])
    
    # Special handling for structured inputs (chat messages)
    if convention == "openllmetry":
        result["inputs"]["chat_history"] = self._extract_messages_efficiently(attributes)
    elif "input_mappings" in mappings:
        self._map_section_efficiently(attributes, mappings["input_mappings"], result["inputs"])
    
    return result

def _map_section_efficiently(self, attributes: dict, mappings: dict, target: dict):
    """Map a section with minimal overhead"""
    for source_key, target_key in mappings.items():
        if source_key in attributes:  # O(1) lookup
            target[target_key] = attributes[source_key]
```

### 4. **Optimized Message Extraction**

```python
def _extract_messages_efficiently(self, attributes: dict) -> list:
    """Extract chat messages with pre-compiled regex - optimized for speed"""
    
    messages = {}  # Use dict for O(1) index access
    pattern = MESSAGE_PATTERNS["openllmetry"]
    
    # Single pass through attributes
    for key, value in attributes.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field = match.group(2)
            
            if index not in messages:
                messages[index] = {}
            
            # Handle nested tool_calls efficiently
            if field.startswith("tool_calls."):
                if "tool_calls" not in messages[index]:
                    messages[index]["tool_calls"] = {}
                
                # Extract tool_calls.0.id -> tool_calls[0]["id"]
                parts = field.split(".")
                if len(parts) >= 3:
                    tool_index = parts[1]
                    tool_field = parts[2]
                    messages[index][f"tool_calls.{tool_index}.{tool_field}"] = value
            else:
                messages[index][field] = value
    
    # Convert to sorted list (only sort once at the end)
    return [messages[i] for i in sorted(messages.keys())]
```

### 5. **Optimized Span Conversion**

```python
def _convert_span_to_event_efficiently(self, span: ReadableSpan, attributes: dict, session_id: str) -> dict:
    """Convert span to event with minimal allocations and maximum speed"""
    
    # Fast attribute mapping
    mapped = self._map_attributes_efficiently(attributes)
    
    # Pre-calculate timing
    duration_ns = span.end_time - span.start_time if span.end_time else 0
    duration_ms = duration_ns / 1_000_000  # Convert nanoseconds to milliseconds
    
    # Build event with minimal object creation
    event = {
        "project": attributes.get("honeyhive.project") or mapped["config"].get("project", "Unknown"),
        "source": attributes.get("honeyhive.source", "python-sdk"),
        "session_id": session_id,
        "event_name": span.name,
        "event_type": self._detect_event_type_fast(span, attributes),
        "config": mapped["config"],
        "inputs": mapped["inputs"],
        "outputs": mapped["outputs"],
        "metadata": mapped["metadata"],
        "start_time": span.start_time,
        "end_time": span.end_time,
        "duration": duration_ms,
        "feedback": {},
        "metrics": {},
        "user_properties": {}
    }
    
    # Add instrumentation scope efficiently
    if hasattr(span, "instrumentation_scope") and span.instrumentation_scope:
        event["metadata"]["scope"] = {
            "name": span.instrumentation_scope.name,
            "version": span.instrumentation_scope.version
        }
    
    return event
```

## Performance Optimizations

### 1. **Memory Efficiency**
```python
# Use __slots__ for memory efficiency
class EfficientSpanProcessor(SpanProcessor):
    __slots__ = ['client', 'disable_batch', 'otlp_exporter', 'tracer_instance', 'mode']
    
    # Pre-allocate frequently used objects
    _empty_dict = {}
    _empty_list = []
```

### 2. **CPU Optimization**
```python
# Cache compiled patterns at module level
_COMPILED_PATTERNS = {
    pattern_name: re.compile(pattern) 
    for pattern_name, pattern in MESSAGE_PATTERNS.items()
}

# Use frozensets for O(1) membership testing
_OPENLLMETRY_KEYS = frozenset([
    "gen_ai.request.model", "gen_ai.system", "gen_ai.usage.prompt_tokens"
])
```

### 3. **Minimal Allocations**
```python
def _fast_event_type_detection(self, span_name: str, attributes: dict) -> str:
    """Ultra-fast event type detection with minimal string operations"""
    
    # Check explicit attributes first (fastest)
    if "honeyhive_event_type" in attributes:
        return str(attributes["honeyhive_event_type"])
    
    # Pre-compiled span name patterns (compiled once at import)
    if _MODEL_PATTERN.match(span_name):
        return "model"
    elif _TOOL_PATTERN.match(span_name):
        return "tool"
    elif _CHAIN_PATTERN.match(span_name):
        return "chain"
    
    return "tool"  # Fast fallback

# Pre-compile at module level
_MODEL_PATTERN = re.compile(r".*(chat|completion|generate|model).*", re.IGNORECASE)
_TOOL_PATTERN = re.compile(r".*(tool|function|search|api).*", re.IGNORECASE)
_CHAIN_PATTERN = re.compile(r".*(chain|workflow|pipeline).*", re.IGNORECASE)
```

## Version Update Strategy

### 1. **Static Configuration Updates**
```python
# New semantic conventions added via code updates
# semantic_mappings.py v1.1.0
SEMANTIC_CONVENTION_MAPPINGS = {
    # ... existing mappings ...
    
    # New convention added in v1.1.0
    "new_instrumentor_v2": {
        "detection_patterns": frozenset(["ai.model.name", "ai.provider.type"]),
        "config_mappings": {
            "ai.provider.type": "provider",
            "ai.model.name": "model"
        },
        # ... rest of mappings
    }
}

# Update priority order
CONVENTION_PRIORITY = ["openllmetry", "new_instrumentor_v2", "openinference", "openlit"]
```

### 2. **Backward Compatibility**
```python
# Support multiple versions of same convention
SEMANTIC_CONVENTION_MAPPINGS = {
    "openllmetry_v0_30": {
        "detection_patterns": frozenset(["gen_ai.request.model"]),
        # ... v0.30 mappings
    },
    "openllmetry_v0_35": {
        "detection_patterns": frozenset(["gen_ai.request.model_name"]),  # Breaking change
        "config_mappings": {
            "gen_ai.request.model_name": "model",  # New attribute name
        }
    }
}

def _detect_openllmetry_version(self, attributes: dict) -> str:
    """Detect OpenLLMetry version based on attribute patterns"""
    if "gen_ai.request.model_name" in attributes:
        return "openllmetry_v0_35"
    elif "gen_ai.request.model" in attributes:
        return "openllmetry_v0_30"
    return "openllmetry_v0_30"  # Default fallback
```

## Performance Benchmarks Target

### Acceptable Performance:
- **< 100 microseconds** per span conversion
- **< 50 microseconds** for attribute mapping
- **< 10 microseconds** for convention detection
- **Zero heap allocations** in steady state
- **Minimal string operations** and regex usage

### Measurement:
```python
import time

def benchmark_span_conversion():
    start = time.perf_counter_ns()
    event = processor._convert_span_to_event_efficiently(span, attributes, session_id)
    end = time.perf_counter_ns()
    
    duration_us = (end - start) / 1000
    assert duration_us < 100, f"Span conversion too slow: {duration_us}μs"
```

## Summary

This design provides:
- ✅ **Ultra-fast attribute mapping** using pre-compiled dictionaries
- ✅ **Minimal memory allocations** with object reuse
- ✅ **Efficient pattern matching** with compiled regex
- ✅ **Static configuration** updated via version releases
- ✅ **Backward compatibility** through version detection
- ✅ **Performance monitoring** with built-in benchmarks

The approach balances **dynamic flexibility** with **performance requirements**, ensuring the span processor remains efficient while supporting evolving semantic conventions through version upgrades.
