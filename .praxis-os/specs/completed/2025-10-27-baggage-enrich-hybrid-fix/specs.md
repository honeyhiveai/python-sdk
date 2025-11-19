# Technical Specifications

**Project:** Baggage Context + Enrich Functions Hybrid API Fix  
**Date:** 2025-10-27  
**Based on:** srd.md (requirements)  
**Version:** 1.0

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Hybrid API Pattern  
**Secondary Pattern:** Selective Context Propagation

**Description:**
This implementation uses a **Hybrid API Pattern** that maintains two parallel interfaces:
1. **Instance Methods** (Primary): Direct method calls on `HoneyHiveTracer` instances
2. **Free Functions** (Legacy): Global functions with automatic tracer discovery

The architecture leverages **Selective Baggage Propagation** to enable tracer discovery in multi-instance scenarios while maintaining thread safety.

**Rationale:**
- Balances backward compatibility (business requirement) with clean API design (long-term maintainability)
- Aligns with multi-instance architecture (no global singleton)
- Provides gradual migration path (v1.0 → v2.0)

### 1.2 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ User Code                                                         │
│                                                                   │
│  Option A: Instance Method (PRIMARY - Recommended)               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ tracer = HoneyHiveTracer(...)                          │     │
│  │ tracer.enrich_span(metadata={...})      ← Explicit     │     │
│  └────────────────────────────────────────────────────────┘     │
│         │                                                         │
│         │ Direct call                                            │
│         ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ HoneyHiveTracer.enrich_span() [Instance Method]       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  Option B: Free Function (LEGACY - Backward Compat)              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ enrich_span(metadata={...})          ← Discovery       │     │
│  └────────────────────────────────────────────────────────┘     │
│         │                                                         │
│         │ Tracer discovery via baggage                           │
│         ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ discover_tracer(ctx=current_context)                   │     │
│  │   1. Check explicit tracer parameter                   │     │
│  │   2. Check baggage for honeyhive_tracer_id ← FIXED     │     │
│  │   3. Check global default                              │     │
│  │   4. Return None (graceful failure)                    │     │
│  └────────────────────────────────────────────────────────┘     │
│         │                                                         │
│         │ Tracer instance                                        │
│         ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Free function delegates to instance method             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│ OpenTelemetry Context Layer                                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ context.get_current()                                  │     │
│  │   → Thread-local context stack                         │     │
│  │   → Baggage: {                                         │     │
│  │       "honeyhive_tracer_id": "abc123",   ← Discovery   │     │
│  │       "run_id": "run-456",               ← Eval context│     │
│  │       "dataset_id": "ds-789",            ← Eval context│     │
│  │       "datapoint_id": "dp-001"           ← Eval context│     │
│  │     }                                                   │     │
│  └────────────────────────────────────────────────────────┘     │
│         │                                                         │
│         │ Baggage propagation (FIXED)                            │
│         ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ _apply_baggage_context()                               │     │
│  │   → Selective key propagation                          │     │
│  │   → Safe keys only (run_id, tracer_id, etc.)          │     │
│  │   → context.attach(ctx)  ← RE-ENABLED                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Tracer Registry                                                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ _TRACER_REGISTRY: WeakValueDictionary                  │     │
│  │   tracer_id_1 → HoneyHiveTracer instance 1             │     │
│  │   tracer_id_2 → HoneyHiveTracer instance 2             │     │
│  │   tracer_id_3 → HoneyHiveTracer instance 3             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 1.3 Architectural Decisions

#### Decision 1: Hybrid API Pattern (Instance + Free Function)

**Decision:** Maintain both instance methods and free functions in v1.0, with instance methods as primary.

**Rationale:**
- **FR-2**: Instance methods needed for clean multi-instance API
- **FR-3**: Free functions needed for backward compatibility
- **NFR-1**: Zero breaking changes required for v1.0
- Provides gradual migration path to v2.0

**Alternatives Considered:**
- **Instance only (breaking)**: Clean but breaks existing users → Rejected for v1.0
- **Free function only**: Can't scale to multi-instance → Architecturally incompatible
- **Deprecate immediately**: Too aggressive for v1.0 → Deferred to v1.1+

**Trade-offs:**
- **Pros**: Zero breaking changes, smooth migration, clear recommendation
- **Cons**: Two patterns to maintain (temporary), documentation complexity

#### Decision 2: Selective Baggage Propagation

**Decision:** Re-enable `context.attach()` but only propagate safe keys (evaluation context, tracer_id).

**Rationale:**
- **FR-1**: Fixes tracer discovery in evaluate() pattern
- Original concern: session ID conflicts in multi-instance
- Solution: Don't propagate session-specific keys
- OpenTelemetry context is thread-local (no cross-thread conflicts)

**Alternatives Considered:**
- **Context Variables (contextvars)**: Python-native, async-safe → Complexity not needed
- **Thread-Local Storage**: Works but not OpenTelemetry-native → Less elegant
- **Explicit Tracer Passing**: Clean but breaking change → Deferred to v2.0

**Trade-offs:**
- **Pros**: OpenTelemetry-native, thread-safe, fixes discovery, minimal change
- **Cons**: Requires careful key selection, needs testing

#### Decision 3: No Deprecation Warnings in v1.0

**Decision:** Keep free functions working without deprecation warnings in v1.0.

**Rationale:**
- **Goal 2**: 100% backward compatibility
- Give users time to migrate without pressure
- Friday deadline - focus on implementation over migration

**Alternatives Considered:**
- **Immediate deprecation**: Pressures users → Rejected
- **No timeline**: Unclear migration path → Rejected

**Trade-offs:**
- **Pros**: User-friendly, smooth transition, clear timeline
- **Cons**: Delayed migration, both patterns maintained longer

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| **FR-1**: Selective Baggage | `_apply_baggage_context()` with safe key filter | Only propagates evaluation context keys, excludes session-specific |
| **FR-2**: Instance Methods | `HoneyHiveTracer.enrich_span()` / `.enrich_session()` | Direct instance methods, no discovery overhead |
| **FR-3**: Free Functions | `enrich_span()` / `enrich_session()` with discovery | Backward compat via baggage-based discovery |
| **FR-4**: Documentation | README, API reference, migration guide updates | Instance methods featured prominently |
| **FR-5**: Testing | Unit + integration test suites | 90%+ coverage for changed code |
| **NFR-1**: Backward Compat | Free functions unchanged, no API removals | All v0.2.x patterns work |
| **NFR-2**: Performance | Baggage propagation < 1ms overhead | Minimal performance impact |
| **NFR-3**: Code Quality | Pylint ≥ 9.5, MyPy 0 errors | Pre-commit hooks enforce |
| **NFR-4**: Testability | Comprehensive test coverage | Unit, integration, multi-instance tests |
| **NFR-5**: Documentation | Clear examples, migration guide | Instance methods primary in docs |

### 1.5 Technology Stack

**Language:** Python 3.8+  
**Core Framework:** OpenTelemetry SDK (context, baggage, trace)  
**Tracing Backend:** HoneyHive API  
**Testing:** pytest, unittest.mock  
**Type Checking:** mypy  
**Linting:** pylint, black  
**Documentation:** Sphinx, reStructuredText  
**CI/CD:** GitHub Actions, pre-commit hooks

**Key Dependencies:**
- `opentelemetry-api` - Context and baggage APIs
- `opentelemetry-sdk` - TracerProvider, SpanProcessor
- Existing HoneyHive SDK infrastructure

### 1.6 Deployment Architecture

**Deployment Model:** PyPI package distribution

```
Development → Testing → PyPI Release
     │            │           │
     ▼            ▼           ▼
  Local Dev    CI/CD      pip install
  (venv)      (pytest)     honeyhive
     │            │           │
     │            │           └─→ Customer Environments
     │            │                   │
     │            └───────────────────┤
     │                                │
     └────────────────────────────────┤
                                      ▼
                              Production Usage
                              (Multi-instance)
```

**Rollout Plan:**
- Monday-Thursday: Development + Testing
- Friday: PyPI deployment
- Week 1: Customer onboarding + monitoring

---

## 2. Component Design

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────┐
│ Public API Layer                                        │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ Instance Methods │  │ Free Functions   │           │
│  │ (Primary)        │  │ (Legacy)         │           │
│  └──────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
         │                        │
         └────────────┬───────────┘
                      │
┌─────────────────────┴─────────────────────────────────┐
│ Discovery & Propagation Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐          │
│  │ discover_tracer() │  │ Baggage Context  │          │
│  │                   │  │ Propagation      │          │
│  └──────────────────┘  └──────────────────┘          │
└──────────────────────────────────────────────────────┘
         │
┌────────┴────────────────────────────────────────────────┐
│ Core Tracer Layer                                       │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ HoneyHiveTracer  │  │ Tracer Registry  │           │
│  │ (Multi-instance) │  │                  │           │
│  └──────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
         │
┌────────┴────────────────────────────────────────────────┐
│ OpenTelemetry Layer                                     │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ TracerProvider   │  │ SpanProcessor    │           │
│  │ (per instance)   │  │ (per instance)   │           │
│  └──────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Component Specifications

#### Component 1: Baggage Context Propagation

**Location:** `src/honeyhive/tracer/processing/context.py`  
**Function:** `_apply_baggage_context()`

**Responsibilities:**
- Set up OpenTelemetry baggage with tracer and evaluation context
- Propagate only safe keys (no session-specific data)
- Attach context to enable discovery in child operations
- Thread-safe propagation

**Interfaces:**

```python
def _apply_baggage_context(
    baggage_items: Dict[str, str], 
    tracer_instance: Optional[Any] = None
) -> None:
    """Apply selective baggage propagation.
    
    Args:
        baggage_items: Full dict of baggage key-value pairs
        tracer_instance: Optional tracer for logging
    
    Behavior:
        - Filters to safe keys only
        - Sets baggage in OpenTelemetry context
        - Calls context.attach() to propagate
    """
```

**Dependencies:**
- OpenTelemetry `context`, `baggage` modules
- `safe_log()` for error logging

**Configuration:**
```python
SAFE_PROPAGATION_KEYS = {
    'run_id',              # Experiment run
    'dataset_id',          # Dataset ID
    'datapoint_id',        # Current datapoint
    'honeyhive_tracer_id', # Tracer discovery
    'project',             # Project name
    'source'               # Source identifier
}
```

#### Component 2: Tracer Discovery

**Location:** `src/honeyhive/tracer/registry.py`  
**Function:** `discover_tracer()`

**Responsibilities:**
- Discover active tracer instance using priority-based fallback
- Check explicit parameter, baggage, then global default
- Return None for graceful degradation
- Thread-safe discovery

**Interfaces:**

```python
def discover_tracer(
    explicit_tracer: Optional[HoneyHiveTracer] = None,
    ctx: Optional[Context] = None,
) -> Optional[HoneyHiveTracer]:
    """Discover tracer with priority fallback.
    
    Priority:
        1. explicit_tracer parameter
        2. Baggage context (honeyhive_tracer_id)
        3. Global default tracer
        4. None
    
    Returns:
        HoneyHiveTracer instance or None
    """
```

**Dependencies:**
- Tracer registry (`_TRACER_REGISTRY`)
- OpenTelemetry baggage
- Default tracer getter

#### Component 3: Instance Method API

**Location:** `src/honeyhive/tracer/core/context.py`  
**Class:** `HoneyHiveTracer`

**Responsibilities:**
- Primary API for span/session enrichment
- Direct access without discovery overhead
- Type-safe with clear method signatures
- Full control over tracer instance

**Interfaces:**

```python
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
        """Enrich current span (PRIMARY API)."""
    
    def enrich_session(
        self,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Enrich session (PRIMARY API)."""
```

**Dependencies:**
- OpenTelemetry `trace.get_current_span()`
- Session API for enrichment

#### Component 4: Free Function Compatibility

**Location:** `src/honeyhive/tracer/integration/compatibility.py`  
**Functions:** `enrich_span()`, `enrich_session()`

**Responsibilities:**
- Backward compatibility with v0.2.x
- Automatic tracer discovery
- Delegate to instance methods
- Graceful degradation

**Interfaces:**

```python
def enrich_span(
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    # ... other params ...
    tracer_instance: Optional[Any] = None,
) -> bool:
    """Legacy free function (BACKWARD COMPAT)."""
    
def enrich_session(
    session_id: str,
    metadata: Optional[Dict[str, Any]],
    tracer_instance: Optional[Any] = None,
) -> None:
    """Legacy free function (BACKWARD COMPAT)."""
```

**Dependencies:**
- `discover_tracer()` for automatic discovery
- Instance methods for delegation

#### Component 5: Tracer Registry

**Location:** `src/honeyhive/tracer/registry.py`  
**Variable:** `_TRACER_REGISTRY`

**Responsibilities:**
- Store weak references to active tracers
- Enable lookup by tracer_id
- Automatic cleanup when tracers garbage collected
- Thread-safe access

**Interfaces:**

```python
_TRACER_REGISTRY: WeakValueDictionary[str, HoneyHiveTracer]

def register_tracer(tracer: HoneyHiveTracer) -> str:
    """Register tracer and return ID."""

def get_tracer_by_id(tracer_id: str) -> Optional[HoneyHiveTracer]:
    """Lookup tracer by ID."""
```

**Dependencies:**
- `weakref.WeakValueDictionary`
- Thread safety via weak references

### 2.3 Component Interaction Flows

#### Flow 1: evaluate() with Instance Method

```
1. evaluate() creates HoneyHiveTracer(run_id="...", datapoint_id="...")
2. Tracer initialization calls setup_baggage_context()
3. _apply_baggage_context() sets baggage with safe keys
4. context.attach(ctx) propagates context (FIXED)
5. user_function(datapoint) executes
6. Inside user function: @trace decorator discovers tracer via baggage
7. User calls: tracer.enrich_span(metadata={...})
8. Instance method directly enriches span (no discovery)
9. Span enriched successfully ✅
```

#### Flow 2: evaluate() with Free Function (Legacy)

```
1. evaluate() creates HoneyHiveTracer(run_id="...", datapoint_id="...")
2. Tracer initialization calls setup_baggage_context()
3. _apply_baggage_context() sets baggage with safe keys
4. context.attach(ctx) propagates context (FIXED)
5. user_function(datapoint) executes
6. User calls: enrich_span(metadata={...})  # Free function
7. Free function calls discover_tracer()
8. discover_tracer() checks baggage → finds honeyhive_tracer_id
9. Looks up tracer in registry → returns tracer instance
10. Free function delegates to tracer.enrich_span(metadata={...})
11. Span enriched successfully ✅
```

#### Flow 3: Thread Isolation (Multi-Instance)

```
Thread 1:
  1. tracer_1 = HoneyHiveTracer(session_id="s1", run_id="r1")
  2. Baggage: {tracer_id: "t1", run_id: "r1"}
  3. context.attach(ctx_1) → Thread-local context 1
  4. user_function() → discovers tracer_1 via baggage ✅

Thread 2 (concurrent):
  1. tracer_2 = HoneyHiveTracer(session_id="s2", run_id="r1")
  2. Baggage: {tracer_id: "t2", run_id: "r1"}
  3. context.attach(ctx_2) → Thread-local context 2 (ISOLATED)
  4. user_function() → discovers tracer_2 via baggage ✅

No collision: Each thread has isolated context ✅
```

---

## 3. Data Models

### 3.1 Baggage Items Structure

```python
BaggageItems = {
    # Safe for propagation (evaluation context)
    'run_id': str,              # Experiment run identifier
    'dataset_id': str,          # Dataset identifier
    'datapoint_id': str,        # Current datapoint ID
    'honeyhive_tracer_id': str, # Tracer instance ID
    'project': str,             # Project name
    'source': str,              # Source identifier
    
    # NOT propagated (instance-specific)
    # 'session_id': str,        # Unique per tracer
    # 'session_name': str,      # Instance-specific
}
```

### 3.2 Enrich Span Parameters

```python
EnrichSpanParams = {
    'metadata': Dict[str, Any],      # Custom metadata
    'metrics': Dict[str, Any],       # Performance metrics
    'config': Dict[str, Any],        # Configuration used
    'feedback': Dict[str, Any],      # User feedback
    'inputs': Dict[str, Any],        # Input data
    'outputs': Dict[str, Any],       # Output data
    'error': Optional[str],          # Error message
    '**kwargs': Any,                 # Additional fields → metadata
}
```

### 3.3 Enrich Session Parameters

```python
EnrichSessionParams = {
    'session_id': Optional[str],     # Explicit or auto-detect
    'metadata': Dict[str, Any],      # Session metadata
    'inputs': Dict[str, Any],        # Session inputs
    'outputs': Dict[str, Any],       # Session outputs
    'config': Dict[str, Any],        # Session config
    'feedback': Dict[str, Any],      # Session feedback
    'metrics': Dict[str, Any],       # Session metrics
    'user_properties': Dict[str, Any], # Legacy support
    '**kwargs': Any,                 # Additional fields
}
```

### 3.4 Discovery Result

```python
DiscoveryResult = Optional[HoneyHiveTracer]
# None = graceful failure, no tracer found
# HoneyHiveTracer = successfully discovered instance
```

---

## 4. API Contracts

### 4.1 Public APIs

#### Instance Method API (Primary)

**Endpoint:** `HoneyHiveTracer.enrich_span()`

```python
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
) -> bool
```

**Contract:**
- **Input**: Optional dicts for different namespaces, kwargs → metadata
- **Output**: `True` if enrichment succeeded, `False` otherwise
- **Side Effects**: Sets attributes on current OpenTelemetry span
- **Error Handling**: Graceful failure, returns `False`, logs warning
- **Thread Safety**: Thread-safe (operates on thread-local span)

**Example:**
```python
tracer = HoneyHiveTracer(api_key="...", project="...")
success = tracer.enrich_span(
    metadata={"model": "gpt-4"},
    metrics={"latency_ms": 150}
)
```

#### Free Function API (Legacy)

**Endpoint:** `enrich_span()`

```python
def enrich_span(
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    # ... same params as instance method ...
    tracer_instance: Optional[Any] = None,
) -> bool
```

**Contract:**
- **Input**: Same as instance method + optional `tracer_instance`
- **Output**: `True` if enrichment succeeded, `False` otherwise
- **Side Effects**: Discovers tracer, sets span attributes
- **Error Handling**: Graceful failure if discovery fails
- **Thread Safety**: Thread-safe (discovery is thread-local)

**Discovery Contract:**
1. Check `tracer_instance` parameter (explicit)
2. Check baggage for `honeyhive_tracer_id`
3. Check global default tracer
4. Return `None` (graceful failure)

**Example:**
```python
# Legacy pattern (still works)
enrich_span(metadata={"model": "gpt-4"})  # Discovers tracer
```

### 4.2 Internal APIs

#### Baggage Propagation API

**Endpoint:** `_apply_baggage_context()`

```python
def _apply_baggage_context(
    baggage_items: Dict[str, str],
    tracer_instance: Optional[Any] = None
) -> None
```

**Contract:**
- **Input**: Full baggage dict, optional tracer for logging
- **Output**: None (side effect: context attached)
- **Side Effects**: 
  - Filters to safe keys
  - Sets baggage in OpenTelemetry context
  - Calls `context.attach()` to propagate
- **Error Handling**: Logs warning, doesn't raise
- **Thread Safety**: Thread-safe (context is thread-local)

#### Discovery API

**Endpoint:** `discover_tracer()`

```python
def discover_tracer(
    explicit_tracer: Optional[HoneyHiveTracer] = None,
    ctx: Optional[Context] = None,
) -> Optional[HoneyHiveTracer]
```

**Contract:**
- **Input**: Optional explicit tracer, optional context
- **Output**: `HoneyHiveTracer` instance or `None`
- **Side Effects**: None (pure lookup)
- **Error Handling**: Returns `None` on any failure
- **Thread Safety**: Thread-safe (reads from thread-local context)

**Priority:**
1. `explicit_tracer` parameter (highest)
2. Baggage lookup via `honeyhive_tracer_id`
3. Global default tracer
4. `None` (lowest)

---

## 5. Security Considerations

### 5.1 Baggage Propagation Security

**Threat:** Sensitive session data leaked via baggage

**Mitigation:**
- Selective key propagation (whitelist approach)
- Only propagate evaluation context (non-sensitive)
- Exclude session IDs, session names (instance-specific)

**Validation:**
- Code review of safe keys list
- Security audit of propagated data

### 5.2 Multi-Instance Isolation

**Threat:** Cross-instance data contamination

**Mitigation:**
- Each tracer instance completely isolated
- No shared mutable state
- Thread-local context (OpenTelemetry guarantee)
- WeakValueDictionary for registry (automatic cleanup)

**Validation:**
- Multi-instance safety tests
- Thread isolation tests
- Concurrent tracer tests

### 5.3 API Key Handling

**Threat:** API keys in traces/logs

**Mitigation:**
- No changes to existing API key handling
- API keys not in baggage
- API keys not in span attributes
- Existing security model unchanged

**Validation:**
- Security audit of baggage items
- No regression in existing security

### 5.4 Input Validation

**Threat:** Malicious data in enrichment parameters

**Mitigation:**
- Type validation via type hints
- MyPy static analysis
- Runtime type checking where needed
- OpenTelemetry attribute sanitization

**Validation:**
- Type checker passes (MyPy 0 errors)
- Unit tests for malformed inputs

---

## 6. Performance Considerations

### 6.1 Baggage Propagation Performance

**Target:** < 1ms overhead per call

**Optimization:**
- Selective propagation (6 keys instead of full dict)
- Early return if no baggage items
- Minimal dict filtering
- Single `context.attach()` call

**Measurement:**
- Performance benchmarks before/after
- Profile with `cProfile` or `py-spy`

**Expected Impact:** Negligible (< 0.5ms per call)

### 6.2 Discovery Performance

**Target:** < 1ms overhead per discovery

**Optimization:**
- Priority-based early return (check explicit first)
- Fast baggage lookup (OpenTelemetry optimized)
- WeakValueDictionary lookup O(1)
- No complex traversal

**Measurement:**
- Benchmark discovery in evaluate() pattern
- Compare with/without discovery

**Expected Impact:** < 1ms per call

### 6.3 Memory Usage

**Target:** No memory leaks, minimal overhead

**Optimization:**
- WeakValueDictionary for registry (auto cleanup)
- Context detach not required (OpenTelemetry manages)
- No large data structures in baggage

**Measurement:**
- Memory profiling with `memory_profiler`
- Long-running test (1000+ datapoints)

**Expected Impact:** Stable memory usage

### 6.4 Thread Safety Performance

**Target:** No performance degradation from locks

**Optimization:**
- OpenTelemetry context is thread-local (no locks)
- Registry uses weak references (no locking needed)
- No shared mutable state

**Measurement:**
- Concurrent tracer benchmark (10+ threads)
- ThreadPoolExecutor stress test

**Expected Impact:** Linear scaling with threads

### 6.5 Performance Benchmarks

**Baseline (v0.2.x):**
- `enrich_span()` call: ~0.1ms (singleton lookup)
- `evaluate()` with 10 datapoints: ~500ms (varies by user function)

**Target (v1.0):**
- `tracer.enrich_span()` call: ~0.1ms (no discovery)
- `enrich_span()` call: ~0.2ms (with discovery)
- Baggage propagation: ~0.5ms per tracer init
- `evaluate()` with 10 datapoints: ~500ms (no regression)

**Acceptable Degradation:** < 5% overall overhead

---

## 7. Scalability

### 7.1 Multi-Instance Scalability

**Scenario:** 100+ concurrent tracer instances

**Design:**
- WeakValueDictionary scales to 1000s of instances
- No global bottlenecks
- Thread-local context (no contention)
- Independent TracerProviders per instance

**Validation:**
- Stress test with 100 concurrent tracers
- Memory usage monitoring
- No performance degradation observed

### 7.2 High-Throughput evaluate()

**Scenario:** 1000+ datapoints in single evaluate() call

**Design:**
- ThreadPoolExecutor handles concurrency
- Each thread isolated (no shared state)
- Baggage propagation per thread
- No global locks or bottlenecks

**Validation:**
- Load test with 1000 datapoints
- Verify thread safety
- Monitor memory and CPU

### 7.3 Long-Running Sessions

**Scenario:** Sessions lasting hours with many spans

**Design:**
- No memory accumulation (WeakValueDictionary)
- Context cleanup automatic
- No resource leaks

**Validation:**
- Long-running test (1 hour, 10000+ spans)
- Memory profiling
- No leaks detected

---

## 8. Error Handling

### 8.1 Discovery Failures

**Scenario:** `discover_tracer()` returns `None`

**Handling:**
- Free functions return `False` (graceful failure)
- Log warning with context
- No exception raised
- User code continues

**Example:**
```python
success = enrich_span(metadata={...})
if not success:
    logger.warning("Enrichment failed - tracer not found")
# Continue execution
```

### 8.2 Baggage Propagation Errors

**Scenario:** `context.attach()` fails

**Handling:**
- Catch exception in `_apply_baggage_context()`
- Log warning with details
- Don't crash tracer initialization
- Graceful degradation

**Example:**
```python
try:
    context.attach(ctx)
except Exception as e:
    safe_log(tracer, "warning", f"Baggage propagation failed: {e}")
    # Continue without baggage propagation
```

### 8.3 Registry Lookup Failures

**Scenario:** Tracer ID in baggage but not in registry

**Handling:**
- `discover_tracer()` returns `None`
- Falls back to global default
- If no default, graceful failure
- Log for debugging

**Example:**
```python
tracer_id = baggage.get_baggage("honeyhive_tracer_id")
if tracer_id and tracer_id in _TRACER_REGISTRY:
    return _TRACER_REGISTRY[tracer_id]
# Fallback to default or None
```

### 8.4 Parameter Validation Errors

**Scenario:** Invalid parameters to enrich functions

**Handling:**
- Type hints + MyPy catch at development time
- Runtime: Convert to appropriate types where possible
- Invalid data: Log warning, skip that parameter
- Don't fail entire enrichment

**Example:**
```python
if not isinstance(metadata, dict):
    logger.warning("metadata must be dict, skipping")
    metadata = None
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Coverage Target:** ≥ 90% for changed code

**Test Categories:**

1. **Baggage Propagation**
   - Selective key filtering
   - Context attachment
   - Thread isolation
   - Error handling

2. **Discovery Mechanism**
   - Priority ordering (explicit > baggage > default)
   - Baggage lookup
   - Registry lookup
   - Graceful failures

3. **Instance Methods**
   - Span enrichment
   - Session enrichment
   - Parameter handling
   - Return values

4. **Free Functions**
   - Discovery integration
   - Delegation to instance methods
   - Backward compatibility
   - Error cases

**Example Test:**
```python
def test_selective_baggage_propagation():
    """Test only safe keys propagated."""
    baggage_items = {
        'run_id': 'r1',
        'session_id': 's1',  # Should NOT propagate
    }
    _apply_baggage_context(baggage_items)
    
    ctx = context.get_current()
    assert baggage.get_baggage('run_id', ctx) == 'r1'
    assert baggage.get_baggage('session_id', ctx) is None
```

### 9.2 Integration Tests

**Test Categories:**

1. **evaluate() + Instance Method**
   - Tracer discovery via baggage
   - Enrichment success
   - Evaluation context propagation

2. **evaluate() + Free Function**
   - Backward compatibility
   - Discovery works
   - Context propagated

3. **Multi-Datapoint Isolation**
   - Each datapoint gets unique tracer
   - No cross-contamination
   - Thread safety

4. **Real API Calls**
   - OpenAI integration
   - Anthropic integration
   - End-to-end tracing

**Example Test:**
```python
def test_evaluate_with_enrich_span():
    """Test evaluate() + enrich_span() pattern."""
    @trace(event_type="tool")
    def user_function(datapoint):
        result = {"output": "test"}
        enrich_span(metadata={"result": result})
        return result
    
    result = evaluate(
        function=user_function,
        dataset=[{"inputs": {}}],
        api_key=os.environ["HH_API_KEY"],
        project="test"
    )
    
    assert result["status"] == "completed"
```

### 9.3 Multi-Instance Safety Tests

**Test Categories:**

1. **Concurrent Tracers**
   - 10+ threads with different tracers
   - Verify isolation
   - No data leakage

2. **Thread Pool Stress Test**
   - 100+ datapoints concurrently
   - Memory stability
   - Performance check

**Example Test:**
```python
def test_concurrent_tracer_isolation():
    """Test 10 concurrent tracers isolated."""
    def thread_func(thread_id):
        tracer = HoneyHiveTracer(
            api_key="test",
            project=f"p{thread_id}"
        )
        ctx = context.get_current()
        tid = baggage.get_baggage("honeyhive_tracer_id", ctx)
        return tid
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(thread_func, range(10)))
    
    # All threads should have unique tracer IDs
    assert len(set(results)) == 10
```

### 9.4 Backward Compatibility Tests

**Test Categories:**

1. **v0.2.x Pattern Tests**
   - All old patterns work unchanged
   - No modifications required
   - Same behavior

**Example Test:**
```python
def test_v0_2_x_free_function_pattern():
    """Test v0.2.x enrich_span pattern still works."""
    tracer = HoneyHiveTracer(api_key="test", project="test")
    set_default_tracer(tracer)
    
    with tracer.start_span("test"):
        # v0.2.x pattern
        success = enrich_span(metadata={"key": "value"})
        assert success is True
```

### 9.5 Performance Tests

**Test Categories:**

1. **Baggage Overhead**
   - Measure propagation time
   - Compare with/without propagation

2. **Discovery Overhead**
   - Measure discovery time
   - Compare instance method vs free function

3. **Throughput Test**
   - 1000 datapoints in evaluate()
   - Memory stability
   - No leaks

**Example Test:**
```python
def test_baggage_propagation_performance():
    """Test baggage propagation < 1ms."""
    baggage_items = {
        'run_id': 'r1',
        'dataset_id': 'd1',
        'datapoint_id': 'dp1',
        'honeyhive_tracer_id': 't1',
    }
    
    start = time.perf_counter()
    for _ in range(1000):
        _apply_baggage_context(baggage_items)
    elapsed = time.perf_counter() - start
    
    avg_per_call = elapsed / 1000
    assert avg_per_call < 0.001  # < 1ms
```

---

## 10. Migration from Design Document

This specification is based on the comprehensive design document:
- **Source:** `.praxis-os/workspace/design/2025-10-27-baggage-enrich-hybrid-fix.md`
- **Supporting Docs:**
  - `ENRICH_SPAN_ARCHITECTURE_ANALYSIS.md`
  - `ENRICH_SESSION_FIX_SUMMARY.md`
  - `EVALUATION_BAGGAGE_ISSUE.md`

**Key Sections Mapped:**
- Design Doc Section 3 (Proposed Solution) → Architecture Overview (Section 1)
- Design Doc Section 4 (Technical Design) → Component Design (Section 2)
- Design Doc Section 6 (Testing Plan) → Testing Strategy (Section 9)
- Design Doc Section 7 (Documentation Updates) → Out of scope (in srd.md)
- Design Doc Section 8 (Implementation Phases) → Deferred to tasks.md

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27  
**Next Review:** Post-implementation (Phase 4)

