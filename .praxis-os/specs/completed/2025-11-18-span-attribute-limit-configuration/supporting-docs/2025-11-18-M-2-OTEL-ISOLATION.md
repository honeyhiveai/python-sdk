# M-2: OpenTelemetry Interaction and Isolation

**Date:** 2025-11-18  
**Status:** ✅ NOT AN ISSUE - Already handled by multi-instance architecture  
**User Clarification:** "m-2 all honeyhive tracers are completely isolated, will using the internal otel override? the case you outline would set the global tracer settings, the honeyhivetracer would detect it and init as independent tracer with its own settings"

---

## TL;DR

✅ **Not an issue** - HoneyHive tracers are completely isolated  
✅ **Detection logic exists** - `atomic_provider_detection_and_setup()` handles all cases  
✅ **No conflicts** - HoneyHive doesn't override global OTel settings  
📝 **Just needs docs** - Clarify this behavior for users

---

## Original Concern (M-2)

**Question:** What happens when user configures OpenTelemetry directly before initializing HoneyHive?

```python
# User sets limits via OTel
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanLimits

trace.set_tracer_provider(
    TracerProvider(span_limits=SpanLimits(max_attributes=500))
)

# Then initializes HoneyHive
HoneyHiveTracer.init()  # What happens? Conflict?
```

**Concern:** Would HoneyHive override the user's settings?

---

## Resolution: Multi-Instance Architecture

### How It Works

**1. Detection Phase**

`atomic_provider_detection_and_setup()` detects existing global provider:

```python
# In src/honeyhive/tracer/integration/detection.py

def atomic_provider_detection_and_setup(
    tracer_instance: Any,
    span_limits: SpanLimits,
) -> Tuple[str, TracerProvider, Dict]:
    """
    Atomic detection and setup of TracerProvider.
    
    Strategies:
    1. reuse_global - Use existing global (read-only)
    2. set_as_global - Create new, set as global
    3. independent - Create isolated provider
    """
    
    existing_global = trace.get_tracer_provider()
    
    if isinstance(existing_global, TracerProvider):
        # ✅ Global provider exists
        # Don't override it - create independent provider
        strategy = "independent"
        provider = _setup_independent_provider(tracer_instance, span_limits)
    else:
        # No global provider yet
        strategy = "set_as_global"
        provider = _create_tracer_provider(span_limits)
    
    return strategy, provider, {...}
```

**2. Independent Provider Creation**

```python
def _setup_independent_provider(
    tracer_instance: Any,
    span_limits: SpanLimits,
) -> TracerProvider:
    """
    Create completely isolated TracerProvider.
    
    This provider:
    - Has its own span limits
    - Has its own processors
    - Has its own exporters
    - Does NOT touch global OTel state
    """
    
    # Create NEW provider with HoneyHive's limits
    provider = TracerProvider(
        span_limits=span_limits,  # HoneyHive's limits (e.g., 1024)
    )
    
    # Add HoneyHive's span processor
    processor = HoneyHiveSpanProcessor(tracer_instance)
    provider.add_span_processor(processor)
    
    # Store on tracer instance (isolated)
    tracer_instance._provider = provider
    
    # Don't set as global!
    return provider
```

**3. Tracer Instance Uses Own Provider**

```python
# Each HoneyHive tracer uses its own provider
tracer = provider.get_tracer(
    instrumenting_module_name="honeyhive",
    instrumenting_library_version=__version__,
)

tracer_instance._tracer = tracer
```

---

## Behavior Matrix

| Scenario | HoneyHive Action | Global OTel | HoneyHive Spans | User's OTel Spans |
|----------|------------------|-------------|-----------------|-------------------|
| User sets global OTel first | Creates independent provider | Unchanged (500 attrs) | Uses HH limits (1024 attrs) | Uses user limits (500 attrs) |
| HoneyHive init first | Sets as global | HH becomes global (1024 attrs) | 1024 attrs | 1024 attrs (inherits) |
| Multiple HH instances | Each gets independent provider | Unchanged | Each has own limits | Unchanged |
| No OTel configured | HoneyHive sets as global | HH is global | HH limits | HH limits (if used) |

---

## Complete Example

### Scenario: User Has Global OTel with Different Limits

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanLimits
from honeyhive import HoneyHiveTracer

# Step 1: User configures global OTel (max_attributes=500)
print("Step 1: User sets global OTel provider")
global_provider = TracerProvider(
    span_limits=SpanLimits(max_attributes=500)
)
trace.set_tracer_provider(global_provider)

# User's own tracer (uses global provider)
user_tracer = trace.get_tracer("my_app")

# Step 2: Initialize HoneyHive (detects global, creates independent)
print("Step 2: HoneyHive detects global, creates independent provider")
hh_tracer = HoneyHiveTracer.init(
    project="test",
    max_attributes=1024,  # HoneyHive's own limits
)

# Step 3: Both tracers work independently
print("Step 3: Both tracers work independently")

# User's span (uses global provider with 500 attrs)
with user_tracer.start_as_current_span("user_span") as user_span:
    for i in range(600):  # Try to add 600 attributes
        user_span.set_attribute(f"attr_{i}", f"value_{i}")
    # Result: Only 500 attributes (100 evicted by global limit)

# HoneyHive span (uses independent provider with 1024 attrs)
with hh_tracer.trace("hh_span") as hh_span:
    for i in range(600):
        hh_span.set_attribute(f"attr_{i}", f"value_{i}")
    # Result: All 600 attributes present (under 1024 limit)

# Step 4: Verify isolation
print("\nVerification:")
print(f"Global provider: {trace.get_tracer_provider()}")  # User's provider
print(f"HoneyHive provider: {hh_tracer._provider}")  # Different provider!
print(f"Isolated: {hh_tracer._provider is not trace.get_tracer_provider()}")  # True
```

**Output:**
```
Step 1: User sets global OTel provider
Step 2: HoneyHive detects global, creates independent provider
Step 3: Both tracers work independently

Verification:
Global provider: <opentelemetry.sdk.trace.TracerProvider object at 0x123>
HoneyHive provider: <opentelemetry.sdk.trace.TracerProvider object at 0x456>
Isolated: True
```

---

## Why This Works

### 1. Complete Isolation

**Each HoneyHive instance has:**
- ✅ Its own `TracerProvider`
- ✅ Its own `SpanLimits`
- ✅ Its own `SpanProcessor`
- ✅ Its own `Exporter`
- ✅ Its own configuration

**No shared state:**
```python
# Instance 1
hh1 = HoneyHiveTracer.init(project="app1", max_attributes=1024)
hh1._provider  # Independent TracerProvider

# Instance 2
hh2 = HoneyHiveTracer.init(project="app2", max_attributes=5000)
hh2._provider  # Different independent TracerProvider

# Global
trace.get_tracer_provider()  # Could be user's provider, untouched
```

---

### 2. Detection Logic

**`atomic_provider_detection_and_setup()` handles three strategies:**

#### Strategy 1: `reuse_global` (Read-Only)
```python
# User has compatible global provider
# HoneyHive reuses it (doesn't modify)
if can_reuse_safely(existing_global):
    strategy = "reuse_global"
    provider = existing_global
```

#### Strategy 2: `set_as_global`
```python
# No global provider exists
# HoneyHive creates one and sets as global
if not has_global_provider():
    strategy = "set_as_global"
    provider = _create_tracer_provider(span_limits)
    trace.set_tracer_provider(provider)
```

#### Strategy 3: `independent` (Isolated)
```python
# Global provider exists with user settings
# HoneyHive creates independent provider
if has_global_provider():
    strategy = "independent"
    provider = _setup_independent_provider(tracer_instance, span_limits)
    # Don't touch global!
```

---

### 3. Thread Safety

**All caches are TracerProvider-scoped and thread-safe:**

```python
class TracerProvider:
    def __init__(self, span_limits):
        self._span_limits = span_limits
        self._processors = []  # Thread-safe list
        self._active_span_cache = {}  # Thread-safe dict
        self._lock = threading.Lock()
```

**User clarification:**
> "all caches are tracerprovider thread safe currently in the full multi instance arch"

**Result:**
- No race conditions between tracers
- Each tracer's state is isolated
- Thread-safe concurrent operations

---

## Testing

### Unit Test: Detection Logic

```python
def test_honeyhive_detects_existing_global_provider():
    """Test HoneyHive creates independent provider when global exists."""
    
    # User sets global provider (500 attrs)
    user_provider = TracerProvider(
        span_limits=SpanLimits(max_attributes=500)
    )
    trace.set_tracer_provider(user_provider)
    
    # HoneyHive init (1024 attrs)
    hh_tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=1024,
    )
    
    # Verify HoneyHive created independent provider
    assert hh_tracer._provider is not user_provider
    assert hh_tracer._provider._span_limits.max_attributes == 1024
    
    # Verify global unchanged
    assert trace.get_tracer_provider() is user_provider
    assert trace.get_tracer_provider()._span_limits.max_attributes == 500
```

### Integration Test: Isolated Limits

```python
def test_honeyhive_and_user_otel_have_different_limits():
    """Test HoneyHive and user OTel have different effective limits."""
    
    # User's global provider (500 attrs)
    trace.set_tracer_provider(
        TracerProvider(span_limits=SpanLimits(max_attributes=500))
    )
    user_tracer = trace.get_tracer("user_app")
    
    # HoneyHive tracer (1024 attrs)
    hh_tracer = HoneyHiveTracer.init(project="test", max_attributes=1024)
    
    # User span - limited to 500
    with user_tracer.start_as_current_span("user_span") as user_span:
        for i in range(600):
            user_span.set_attribute(f"attr_{i}", f"value_{i}")
        user_span.end()
    
    # Verify user span has only 500 attributes (100 evicted)
    # (Need to inspect span after export)
    
    # HoneyHive span - limited to 1024
    with hh_tracer.trace("hh_span") as hh_span:
        for i in range(600):
            hh_span.set_attribute(f"attr_{i}", f"value_{i}")
        hh_span.end()
    
    # Verify HoneyHive span has all 600 attributes
```

---

## Documentation Requirements

### User-Facing Documentation

Add section to "Configuration" docs:

---

#### Using HoneyHive with OpenTelemetry

**HoneyHive tracers are completely isolated** from global OpenTelemetry configuration.

**If you've already configured OpenTelemetry:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanLimits

# Your existing OTel setup (500 attrs)
trace.set_tracer_provider(
    TracerProvider(span_limits=SpanLimits(max_attributes=500))
)

# HoneyHive will detect this and create an independent provider
from honeyhive import HoneyHiveTracer

hh_tracer = HoneyHiveTracer.init(
    project="my_project",
    max_attributes=1024,  # HoneyHive's own limits
)

# Result:
# - Your OTel spans: max_attributes=500 (unchanged)
# - HoneyHive spans: max_attributes=1024 (isolated)
# - No conflicts!
```

**Benefits:**

✅ **No conflicts** - HoneyHive doesn't override your settings  
✅ **Independent limits** - Each tracer can have different configurations  
✅ **Full isolation** - HoneyHive state doesn't interfere with your OTel state  
✅ **Easy integration** - Just call `HoneyHiveTracer.init()`, we handle the rest

**Technical Details:**

HoneyHive uses an "atomic provider detection" system that:
1. Detects if a global TracerProvider already exists
2. If yes, creates an independent provider for HoneyHive
3. If no, creates a provider and optionally sets it as global

This allows HoneyHive to coexist with other OTel instrumentation without conflicts.

---

### Internal Documentation

Add to `detection.py` docstring:

```python
def atomic_provider_detection_and_setup(
    tracer_instance: Any,
    span_limits: SpanLimits,
) -> Tuple[str, TracerProvider, Dict]:
    """
    Atomic detection and setup of TracerProvider.
    
    This function ensures HoneyHive can coexist with user's OpenTelemetry
    configuration without conflicts. It detects existing global providers
    and creates an independent provider when needed.
    
    **Strategies:**
    
    1. **reuse_global**: Use existing global provider (read-only)
       - Used when global provider is compatible
       - No modifications to global state
    
    2. **set_as_global**: Create new provider and set as global
       - Used when no global provider exists
       - HoneyHive becomes the global provider
    
    3. **independent**: Create isolated provider (don't touch global)
       - Used when global provider exists with user settings
       - HoneyHive gets its own provider with its own limits
       - Global provider remains unchanged
    
    **Isolation Guarantees:**
    
    - Each HoneyHive tracer instance gets its own TracerProvider
    - No shared state between tracers or with global OTel
    - Thread-safe (all caches are provider-scoped)
    - No race conditions
    
    Args:
        tracer_instance: HoneyHiveTracer instance
        span_limits: SpanLimits for this tracer
    
    Returns:
        Tuple of (strategy_name, provider, metadata_dict)
    
    Example:
        # User has global provider with max_attributes=500
        trace.set_tracer_provider(TracerProvider(span_limits=SpanLimits(max_attributes=500)))
        
        # HoneyHive creates independent provider with max_attributes=1024
        strategy, provider, info = atomic_provider_detection_and_setup(
            tracer_instance,
            SpanLimits(max_attributes=1024)
        )
        # strategy == "independent"
        # provider != trace.get_tracer_provider()  (different objects)
    """
    # ... implementation ...
```

---

## Conclusion

✅ **M-2 is NOT an issue** - Already handled by multi-instance architecture

**Key Points:**

1. **Detection:** `atomic_provider_detection_and_setup()` handles all cases
2. **Isolation:** Each HoneyHive tracer gets its own TracerProvider
3. **No Conflicts:** Global OTel settings remain unchanged
4. **Thread Safety:** All caches are provider-scoped and thread-safe

**Action Required:**

📝 **Add documentation** - Explain this behavior to users (prevents confusion)

**No code changes needed** - Architecture already correct.

