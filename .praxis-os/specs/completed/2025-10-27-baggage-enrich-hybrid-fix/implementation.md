# Implementation Approach

**Project:** Baggage Context + Enrich Functions Hybrid API Fix  
**Date:** 2025-10-27  
**Ship Date:** 2025-10-31 (Friday)

---

## 1. Implementation Philosophy

**Core Principles:**

1. **Fix Root Cause First** - Address the baggage propagation bug before anything else (Phase 1)
2. **Zero Breaking Changes** - All v0.2.x patterns must work unchanged (NFR-1)
3. **Test-Driven Validation** - Write tests to validate fixes before declaring success
4. **Incremental Delivery** - Complete one phase before starting the next
5. **Documentation as Code** - Update docs alongside implementation, not after

**Quality Gates:**
- Pylint ≥ 9.5 (enforced by pre-commit)
- MyPy 0 errors (enforced by pre-commit)
- Test coverage ≥ 90% for changed code
- All integration tests pass with real APIs

**AI-Assisted Development:**
- This implementation uses Agent OS workflows
- Follow the phased approach strictly (no skipping ahead)
- Use `pos_search_project(action="search_standards", query=)` liberally for pattern guidance
- Document learnings for knowledge compounding

---

## 2. Implementation Order

**Critical Path:**
```
Phase 1: Core Baggage Fix (Monday, 4 hours)
    ↓
Phase 4: Testing (Thursday, 6 hours) ← Validates Phase 1
    ↓
Phase 2: Documentation (Tuesday, 4 hours) ← Can overlap with Phase 4
    ↓
Phase 3: Examples (Wednesday, 4 hours)
    ↓
Phase 5: Release (Friday AM, 2 hours)
```

**Rationale:**
- Phase 1 is the most critical (unblocks evaluate() pattern)
- Phase 4 validates Phase 1 before proceeding
- Phase 2 and 3 can be done in parallel or interleaved
- Phase 5 is the final quality gate

**Parallelization:**
- Phase 2 documentation can be written while Phase 4 tests run
- Phase 3 example updates are independent (parallelize across files)

---

## 3. Code Patterns

### Pattern 1: Selective Baggage Propagation

**Used in:** Component 1 (Baggage Context Propagation) - `_apply_baggage_context()`

**Purpose:** Propagate only safe, non-instance-specific keys to enable tracer discovery without causing conflicts.

**✅ GOOD: Whitelist Approach**

```python
# src/honeyhive/tracer/processing/context.py

from opentelemetry import context, baggage
from typing import Dict, Optional, Any

# Define safe keys at module level (immutable)
SAFE_PROPAGATION_KEYS = frozenset({
    'run_id',              # Evaluation run ID
    'dataset_id',          # Dataset ID
    'datapoint_id',        # Current datapoint ID
    'honeyhive_tracer_id', # Tracer instance ID (for discovery)
    'project',             # Project name
    'source'               # Source identifier
})

def _apply_baggage_context(
    baggage_items: Dict[str, str], 
    tracer_instance: Optional[Any] = None
) -> None:
    """Apply selective baggage propagation.
    
    Only propagates safe keys (evaluation context, tracer ID).
    Excludes session-specific keys to prevent multi-instance conflicts.
    
    Args:
        baggage_items: Full dict of baggage key-value pairs
        tracer_instance: Optional tracer for logging
    """
    if not baggage_items:
        return  # Early return for empty dict
    
    # Filter to safe keys only (whitelist approach)
    safe_items = {
        key: value 
        for key, value in baggage_items.items() 
        if key in SAFE_PROPAGATION_KEYS
    }
    
    if not safe_items:
        return  # Nothing to propagate
    
    # Build context with filtered baggage
    ctx = context.get_current()
    for key, value in safe_items.items():
        ctx = baggage.set_baggage(key, str(value), context=ctx)
    
    # Attach context to propagate (CRITICAL FIX)
    try:
        context.attach(ctx)
        
        # Log success for debugging
        if tracer_instance:
            safe_log(
                tracer_instance, 
                "debug", 
                f"Baggage propagated: {list(safe_items.keys())}"
            )
    except Exception as e:
        # Graceful degradation - don't crash tracer init
        if tracer_instance:
            safe_log(
                tracer_instance, 
                "warning", 
                f"Baggage propagation failed: {e}"
            )
```

**Why This Works:**
- Whitelist approach (explicit allow) is safer than blacklist (explicit deny)
- `frozenset` ensures immutability (can't be modified accidentally)
- Early returns optimize for common cases (empty dict)
- Try/except ensures graceful degradation
- Logging aids debugging without breaking functionality

---

**❌ BAD: Blacklist Approach**

```python
# DON'T DO THIS
UNSAFE_KEYS = {'session_id', 'session_name'}

def _apply_baggage_context(baggage_items, tracer_instance=None):
    # Filter out unsafe keys
    safe_items = {
        key: value 
        for key, value in baggage_items.items() 
        if key not in UNSAFE_KEYS  # ← Problem: Doesn't scale
    }
    
    # ... rest of implementation
```

**Problems:**
- Blacklist doesn't scale (every new key is unsafe by default)
- Easy to forget to add new unsafe keys
- Security risk: unknown keys propagated

---

**❌ BAD: No context.attach() (Original Bug)**

```python
# DON'T DO THIS
def _apply_baggage_context(baggage_items, tracer_instance=None):
    ctx = context.get_current()
    for key, value in baggage_items.items():
        ctx = baggage.set_baggage(key, str(value), context=ctx)
    
    # context.attach(ctx)  # ← BUG: Commented out!
    # Result: Baggage never propagates to child operations
```

**Problems:**
- Baggage set but not propagated (ctx is local variable)
- `discover_tracer()` can't find tracer ID in child operations
- evaluate() pattern breaks completely

---

### Pattern 2: Priority-Based Discovery

**Used in:** Component 2 (Tracer Discovery) - `discover_tracer()`

**Purpose:** Discover tracer instance with clear fallback hierarchy for robustness.

**✅ GOOD: Explicit Priority Order**

```python
# src/honeyhive/tracer/registry.py

from opentelemetry import context, baggage
from typing import Optional

def discover_tracer(
    explicit_tracer: Optional['HoneyHiveTracer'] = None,
    ctx: Optional[Any] = None,
) -> Optional['HoneyHiveTracer']:
    """Discover tracer with priority-based fallback.
    
    Priority:
        1. explicit_tracer parameter (highest)
        2. Baggage context (honeyhive_tracer_id)
        3. Global default tracer
        4. None (graceful failure)
    
    Args:
        explicit_tracer: Explicitly provided tracer instance
        ctx: Optional context (uses current if not provided)
    
    Returns:
        HoneyHiveTracer instance or None
    """
    # Priority 1: Explicit parameter (highest)
    if explicit_tracer is not None:
        return explicit_tracer
    
    # Priority 2: Baggage context
    ctx = ctx or context.get_current()
    tracer_id = baggage.get_baggage("honeyhive_tracer_id", context=ctx)
    
    if tracer_id:
        # Look up in registry
        tracer = _TRACER_REGISTRY.get(tracer_id)
        if tracer:
            return tracer
        # Fall through if ID in baggage but not in registry
    
    # Priority 3: Global default
    default_tracer = get_default_tracer()
    if default_tracer:
        return default_tracer
    
    # Priority 4: None (graceful failure)
    return None
```

**Why This Works:**
- Clear priority order (most explicit to least explicit)
- Early returns optimize for common cases
- Graceful degradation (returns None, doesn't crash)
- Fall-through logic handles edge cases (ID in baggage but not in registry)

---

**❌ BAD: No Priority Order**

```python
# DON'T DO THIS
def discover_tracer(explicit_tracer=None, ctx=None):
    # Check baggage first (wrong priority)
    ctx = ctx or context.get_current()
    tracer_id = baggage.get_baggage("honeyhive_tracer_id", context=ctx)
    if tracer_id and tracer_id in _TRACER_REGISTRY:
        return _TRACER_REGISTRY[tracer_id]
    
    # Check explicit parameter (should be first!)
    if explicit_tracer:
        return explicit_tracer
    
    # Check default
    return get_default_tracer()
```

**Problems:**
- Wrong priority (baggage before explicit)
- Explicit parameter should always win (user intent)
- Confusing behavior for callers

---

**❌ BAD: Exception on Failure**

```python
# DON'T DO THIS
def discover_tracer(explicit_tracer=None, ctx=None):
    tracer = _try_discover(explicit_tracer, ctx)
    if tracer is None:
        raise RuntimeError("Tracer not found!")  # ← BAD: Crashes user code
    return tracer
```

**Problems:**
- Crashes user code (breaks graceful degradation principle)
- Forces users to wrap in try/except
- Better to return None and log warning

---

### Pattern 3: Instance Method as Primary API

**Used in:** Component 3 (Instance Method API) - `HoneyHiveTracer.enrich_span()`

**Purpose:** Provide explicit, type-safe API that doesn't require discovery.

**✅ GOOD: Direct Instance Method**

```python
# src/honeyhive/tracer/core/context.py

from opentelemetry import trace
from typing import Dict, Any, Optional

class HoneyHiveTracer:
    def enrich_span(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Enrich current span with metadata (PRIMARY API).
        
        This is the RECOMMENDED way to enrich spans. It provides:
        - No tracer discovery overhead
        - Type safety via type hints
        - Clear ownership (explicit tracer instance)
        - Thread-safe (operates on thread-local span)
        
        Args:
            metadata: Custom metadata key-value pairs
            metrics: Performance metrics (latency, tokens, etc.)
            config: Configuration used (model, temperature, etc.)
            feedback: User feedback (ratings, corrections)
            inputs: Input data (prompts, queries, etc.)
            outputs: Output data (completions, results, etc.)
            error: Error message if operation failed
            **kwargs: Additional fields (merged into metadata)
        
        Returns:
            True if enrichment succeeded, False otherwise
        
        Example:
            >>> tracer = HoneyHiveTracer(api_key="...", project="...")
            >>> with tracer.start_span("llm_call") as span:
            ...     result = call_openai()
            ...     tracer.enrich_span(
            ...         metadata={"model": "gpt-4"},
            ...         metrics={"latency_ms": 150}
            ...     )
        """
        try:
            # Get current span (thread-local)
            span = trace.get_current_span()
            if not span or not span.is_recording():
                return False  # No span or span not recording
            
            # Set attributes in OpenTelemetry namespaces
            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"metadata.{key}", value)
            
            if metrics:
                for key, value in metrics.items():
                    span.set_attribute(f"metrics.{key}", value)
            
            # ... other namespaces ...
            
            # Merge kwargs into metadata
            if kwargs:
                for key, value in kwargs.items():
                    span.set_attribute(f"metadata.{key}", value)
            
            return True
            
        except Exception as e:
            # Graceful failure - log but don't crash
            safe_log(self, "warning", f"enrich_span failed: {e}")
            return False
```

**Why This Works:**
- No discovery overhead (direct method call)
- Type hints provide IDE autocomplete and static analysis
- Comprehensive docstring with example
- Graceful error handling (returns False, doesn't crash)
- Thread-safe (operates on thread-local span)

---

**❌ BAD: Instance Method that Calls Discovery**

```python
# DON'T DO THIS
class HoneyHiveTracer:
    def enrich_span(self, metadata=None, **kwargs):
        # Don't discover - we already have the tracer (self)!
        tracer = discover_tracer()  # ← Unnecessary overhead
        if tracer:
            tracer._enrich_span_internal(metadata, **kwargs)
```

**Problems:**
- Unnecessary discovery overhead
- `self` is already the tracer instance
- Defeats the purpose of instance method

---

### Pattern 4: Free Function with Delegation

**Used in:** Component 4 (Free Function Compatibility) - `enrich_span()`

**Purpose:** Backward compatibility for v0.2.x users via automatic discovery.

**✅ GOOD: Discovery + Delegation**

```python
# src/honeyhive/tracer/integration/compatibility.py

from typing import Dict, Any, Optional
from ..registry import discover_tracer

def enrich_span(
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> bool:
    """Enrich current span (LEGACY COMPATIBILITY).
    
    This free function is provided for backward compatibility with v0.2.x.
    
    ⚠️ DEPRECATED: This pattern will be removed in v2.0.
    
    RECOMMENDED: Use instance method instead:
        tracer = HoneyHiveTracer(...)
        tracer.enrich_span(metadata={...})
    
    Args:
        Same as HoneyHiveTracer.enrich_span()
        tracer_instance: Optional explicit tracer (for advanced use)
    
    Returns:
        True if enrichment succeeded, False otherwise
    """
    # Discover tracer (priority: explicit > baggage > default)
    tracer = discover_tracer(explicit_tracer=tracer_instance)
    
    if tracer is None:
        # Graceful failure - log warning
        import logging
        logging.warning(
            "enrich_span() failed: No tracer found. "
            "Consider using instance method: tracer.enrich_span()"
        )
        return False
    
    # Delegate to instance method
    return tracer.enrich_span(
        metadata=metadata,
        metrics=metrics,
        config=config,
        feedback=feedback,
        inputs=inputs,
        outputs=outputs,
        error=error,
        **kwargs,
    )
```

**Why This Works:**
- Clear deprecation notice in docstring
- Recommends migration path (instance method)
- Discovery with graceful failure
- Simple delegation (no duplicate logic)
- Helpful error message points to solution

---

**❌ BAD: Duplicate Implementation**

```python
# DON'T DO THIS
def enrich_span(metadata=None, **kwargs):
    # Duplicate all the logic from instance method
    span = trace.get_current_span()
    if not span:
        return False
    
    if metadata:
        for key, value in metadata.items():
            span.set_attribute(f"metadata.{key}", value)
    
    # ... 50 more lines of duplicate logic ...
```

**Problems:**
- Code duplication (maintenance burden)
- Logic can diverge between instance method and free function
- Violates DRY (Don't Repeat Yourself)

---

**❌ BAD: Silent Failure**

```python
# DON'T DO THIS
def enrich_span(metadata=None, **kwargs):
    tracer = discover_tracer()
    if tracer is None:
        return False  # ← Silent failure, no logging
    
    return tracer.enrich_span(metadata=metadata, **kwargs)
```

**Problems:**
- Silent failure frustrates debugging
- Users don't know why enrichment failed
- Should log warning with helpful message

---

### Pattern 5: Weak Reference Registry

**Used in:** Component 5 (Tracer Registry) - `_TRACER_REGISTRY`

**Purpose:** Store tracer instances for discovery without preventing garbage collection.

**✅ GOOD: WeakValueDictionary**

```python
# src/honeyhive/tracer/registry.py

from weakref import WeakValueDictionary
from typing import Optional
import uuid

# Weak references allow automatic cleanup
_TRACER_REGISTRY: WeakValueDictionary[str, 'HoneyHiveTracer'] = WeakValueDictionary()

def register_tracer(tracer: 'HoneyHiveTracer') -> str:
    """Register tracer and return unique ID.
    
    Uses weak references to avoid preventing garbage collection.
    When tracer is garbage collected, registry entry auto-removed.
    
    Args:
        tracer: HoneyHiveTracer instance to register
    
    Returns:
        Unique tracer ID (UUID)
    """
    tracer_id = str(uuid.uuid4())
    _TRACER_REGISTRY[tracer_id] = tracer
    return tracer_id

def get_tracer_by_id(tracer_id: str) -> Optional['HoneyHiveTracer']:
    """Lookup tracer by ID.
    
    Args:
        tracer_id: Tracer ID from baggage or explicit parameter
    
    Returns:
        HoneyHiveTracer instance or None if not found
    """
    return _TRACER_REGISTRY.get(tracer_id)

# Usage in HoneyHiveTracer.__init__:
self.tracer_id = register_tracer(self)
```

**Why This Works:**
- `WeakValueDictionary` automatically removes entries when tracer garbage collected
- No memory leaks (tracer can be cleaned up when no longer referenced)
- Thread-safe (weak references are thread-safe)
- Simple lookup via `get()` (returns None if not found)

---

**❌ BAD: Strong References (Memory Leak)**

```python
# DON'T DO THIS
_TRACER_REGISTRY: Dict[str, 'HoneyHiveTracer'] = {}

def register_tracer(tracer):
    tracer_id = str(uuid.uuid4())
    _TRACER_REGISTRY[tracer_id] = tracer  # ← Strong reference
    return tracer_id
```

**Problems:**
- Strong references prevent garbage collection
- Memory leak: tracers never cleaned up
- Registry grows indefinitely (memory grows unbounded)

---

**❌ BAD: Manual Cleanup Required**

```python
# DON'T DO THIS
_TRACER_REGISTRY = {}

def register_tracer(tracer):
    tracer_id = str(uuid.uuid4())
    _TRACER_REGISTRY[tracer_id] = tracer
    return tracer_id

def unregister_tracer(tracer_id):
    """User must manually call this! (Bad UX)"""
    _TRACER_REGISTRY.pop(tracer_id, None)

# Usage (BAD):
tracer = HoneyHiveTracer(...)
# ... use tracer ...
unregister_tracer(tracer.tracer_id)  # ← Users forget this!
```

**Problems:**
- Requires manual cleanup (bad UX)
- Users forget to unregister (memory leak)
- Error-prone (what if exception before unregister?)

---

### Pattern 6: Thread-Local Context Safety

**Used in:** All components (OpenTelemetry guarantee)

**Purpose:** Ensure each thread has isolated context for multi-instance safety.

**✅ GOOD: Rely on OpenTelemetry Guarantees**

```python
# OpenTelemetry context is thread-local by design

from opentelemetry import context, baggage
from concurrent.futures import ThreadPoolExecutor

def thread_func(thread_id):
    """Each thread has isolated context."""
    tracer = HoneyHiveTracer(
        api_key="test",
        project=f"p{thread_id}"
    )
    
    # Baggage is thread-local
    ctx = context.get_current()
    tracer_id = baggage.get_baggage("honeyhive_tracer_id", context=ctx)
    
    # This thread sees only its own tracer_id
    return tracer_id

# Run 10 threads concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(thread_func, range(10)))

# All threads have unique tracer IDs (no collision)
assert len(set(results)) == 10
```

**Why This Works:**
- OpenTelemetry context is thread-local (built-in guarantee)
- No explicit locking needed (context isolation automatic)
- Each thread sees only its own baggage
- No cross-thread contamination

---

**❌ BAD: Global Context (Thread Collision)**

```python
# DON'T DO THIS
_GLOBAL_CONTEXT = {}  # ← Shared across threads

def set_tracer_id(tracer_id):
    _GLOBAL_CONTEXT['tracer_id'] = tracer_id  # ← Race condition

def get_tracer_id():
    return _GLOBAL_CONTEXT.get('tracer_id')
```

**Problems:**
- Shared mutable state across threads (race condition)
- Thread 1 can overwrite Thread 2's tracer ID
- Requires explicit locking (complex, error-prone)

---

**❌ BAD: Thread-Local Storage (Over-Engineering)**

```python
# DON'T DO THIS (OpenTelemetry already provides thread-local context)
import threading

_thread_local = threading.local()

def set_tracer(tracer):
    _thread_local.tracer = tracer  # ← Unnecessary

def get_tracer():
    return getattr(_thread_local, 'tracer', None)
```

**Problems:**
- Duplicates OpenTelemetry's built-in thread-local context
- Over-engineering (OpenTelemetry already handles this)
- Introduces parallel context mechanism (confusing)

---

## 4. Anti-Patterns to Avoid

### Anti-Pattern 1: Blacklist Security

**Problem:** Excluding specific unsafe keys instead of allowing specific safe keys.

**Why Bad:** Doesn't scale, new keys unsafe by default.

**Fix:** Use whitelist (SAFE_PROPAGATION_KEYS).

---

### Anti-Pattern 2: Silent Failures

**Problem:** Returning False without logging why.

**Why Bad:** Frustrates debugging, users don't know root cause.

**Fix:** Log warning with helpful message.

---

### Anti-Pattern 3: Code Duplication

**Problem:** Duplicating logic between instance method and free function.

**Why Bad:** Logic can diverge, maintenance burden.

**Fix:** Free function delegates to instance method.

---

### Anti-Pattern 4: Strong References in Registry

**Problem:** Using normal dict instead of WeakValueDictionary.

**Why Bad:** Memory leak, tracers never garbage collected.

**Fix:** Use WeakValueDictionary for automatic cleanup.

---

### Anti-Pattern 5: Exception on Failure

**Problem:** Raising exception when discovery fails.

**Why Bad:** Crashes user code, breaks graceful degradation.

**Fix:** Return None, log warning, let user code continue.

---

### Anti-Pattern 6: Wrong Priority Order

**Problem:** Checking baggage before explicit parameter.

**Why Bad:** Explicit parameter should always win (user intent).

**Fix:** Explicit > Baggage > Default > None.

---

## 5. Testing Patterns

### Test Pattern 1: Selective Propagation Verification

```python
def test_safe_keys_propagated():
    """Verify only safe keys propagated."""
    baggage_items = {
        'run_id': 'r1',           # Safe
        'honeyhive_tracer_id': 't1',  # Safe
        'session_id': 's1',       # Unsafe
    }
    
    _apply_baggage_context(baggage_items)
    
    ctx = context.get_current()
    assert baggage.get_baggage('run_id', ctx) == 'r1'  # ✅ Propagated
    assert baggage.get_baggage('honeyhive_tracer_id', ctx) == 't1'  # ✅ Propagated
    assert baggage.get_baggage('session_id', ctx) is None  # ✅ Filtered
```

---

### Test Pattern 2: Priority Order Verification

```python
def test_discovery_priority_order():
    """Verify priority: explicit > baggage > default."""
    # Setup
    explicit_tracer = HoneyHiveTracer(api_key="test1", project="p1")
    default_tracer = HoneyHiveTracer(api_key="test2", project="p2")
    set_default_tracer(default_tracer)
    
    # Explicit wins over default
    result = discover_tracer(explicit_tracer=explicit_tracer)
    assert result is explicit_tracer  # ✅
    
    # Default used if no explicit
    result = discover_tracer()
    assert result is default_tracer  # ✅
```

---

### Test Pattern 3: Thread Isolation Verification

```python
def test_thread_isolation():
    """Verify each thread has isolated context."""
    def thread_func(thread_id):
        tracer = HoneyHiveTracer(api_key="test", project=f"p{thread_id}")
        ctx = context.get_current()
        return baggage.get_baggage("honeyhive_tracer_id", context=ctx)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(thread_func, range(10)))
    
    # All unique (no collision)
    assert len(set(results)) == 10  # ✅
```

---

### Test Pattern 4: Graceful Degradation Verification

```python
def test_enrich_span_graceful_failure():
    """Verify graceful failure when no tracer found."""
    # No tracer in context
    result = enrich_span(metadata={"key": "value"})
    
    assert result is False  # ✅ Returns False, doesn't crash
    # Check logs for warning message
```

---

## 6. Error Handling Strategy

### Strategy 1: Graceful Degradation

**Principle:** Never crash user code due to enrichment failure.

**Implementation:**
- Return False on failure (don't raise exception)
- Log warning with helpful context
- Allow user code to continue

**Example:**
```python
try:
    tracer = discover_tracer()
    if tracer:
        return tracer.enrich_span(metadata=metadata)
    else:
        logging.warning("Tracer not found - enrichment skipped")
        return False
except Exception as e:
    logging.warning(f"Enrichment failed: {e}")
    return False
```

---

### Strategy 2: Helpful Error Messages

**Principle:** Error messages should guide users to solution.

**Implementation:**
- Explain what went wrong
- Suggest fix or alternative approach
- Include link to documentation

**Example:**
```python
logging.warning(
    "enrich_span() failed: No tracer found. "
    "Consider using instance method: tracer.enrich_span(). "
    "See: https://docs.honeyhive.ai/migration-guide"
)
```

---

### Strategy 3: Fail-Fast for Critical Errors

**Principle:** Crash early for configuration errors.

**Implementation:**
- Invalid API key → raise exception (user must fix)
- Missing required parameter → raise exception
- Invalid configuration → raise exception

**Example:**
```python
def __init__(self, api_key: str, project: str):
    if not api_key:
        raise ValueError("api_key is required")
    if not project:
        raise ValueError("project is required")
```

---

## 7. Code Quality Checklist

Before committing code:

- [ ] Pylint score ≥ 9.5
- [ ] MyPy 0 errors
- [ ] All tests pass (pytest)
- [ ] Test coverage ≥ 90% (changed code)
- [ ] Docstrings complete (function + class level)
- [ ] Type hints on all public functions
- [ ] Error messages helpful (include solution)
- [ ] No code duplication (DRY)
- [ ] Patterns match this document
- [ ] Anti-patterns avoided

---

## 8. Review Checklist

Code reviewers should verify:

- [ ] **Security:** Only safe keys propagated
- [ ] **Thread Safety:** No shared mutable state
- [ ] **Backward Compat:** v0.2.x patterns work
- [ ] **Performance:** No regression (< 5% overhead)
- [ ] **Graceful Degradation:** Failures don't crash
- [ ] **Error Messages:** Helpful and actionable
- [ ] **Documentation:** Docstrings complete
- [ ] **Tests:** Comprehensive coverage
- [ ] **Code Quality:** Pylint ≥ 9.5, MyPy 0 errors

---

## 9. Performance Optimization Guidelines

### Optimization 1: Early Returns

**Pattern:** Return early for common cases.

```python
def _apply_baggage_context(baggage_items, tracer_instance=None):
    if not baggage_items:
        return  # ← Early return (no work needed)
    
    safe_items = filter_safe_keys(baggage_items)
    if not safe_items:
        return  # ← Early return (nothing to propagate)
    
    # ... rest of logic ...
```

---

### Optimization 2: Minimize Baggage Keys

**Pattern:** Propagate only essential keys (6 keys instead of 10+).

```python
# Only propagate what's needed for discovery + eval context
SAFE_PROPAGATION_KEYS = frozenset({
    'run_id', 'dataset_id', 'datapoint_id',  # Eval context
    'honeyhive_tracer_id', 'project', 'source'  # Discovery
})
```

---

### Optimization 3: Single context.attach() Call

**Pattern:** Build full context first, then attach once.

```python
# GOOD: Single attach call
ctx = context.get_current()
for key, value in safe_items.items():
    ctx = baggage.set_baggage(key, str(value), context=ctx)
context.attach(ctx)  # ← Once

# BAD: Multiple attach calls (slower)
for key, value in safe_items.items():
    ctx = baggage.set_baggage(key, str(value))
    context.attach(ctx)  # ← Multiple calls (overhead)
```

---

## 10. Migration Strategy for Future

### v1.0 → v1.1 (Optional Deprecation Warnings)

- Add deprecation warnings to free functions
- Update documentation to emphasize instance methods
- Provide automated migration tool

### v1.1 → v2.0 (Breaking Change)

- Remove free function exports from `__init__.py`
- Update evaluate() to pass tracer to user function
- Require explicit tracer in user code
- Provide comprehensive migration guide

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27  
**Status:** Draft - Pending Approval

