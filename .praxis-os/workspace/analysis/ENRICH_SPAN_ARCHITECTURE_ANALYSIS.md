# enrich_span() Architecture Analysis: Original vs Multi-Instance

**Date**: 2025-10-22  
**Author**: AI Analysis  
**Purpose**: Document the architectural incompatibility between the original singleton tracer design and the new multi-instance architecture, specifically regarding `enrich_span()` and `enrich_session()` functionality.

---

## Executive Summary

The refactor from singleton to multi-instance tracer architecture fundamentally breaks `enrich_span()` and `enrich_session()` when used with the `evaluate()` function. The original design relied on global state that no longer exists in the multi-instance architecture. This document provides a complete analysis to inform design decisions about the new API.

---

## Original SDK Architecture (main branch)

### 1. Singleton Pattern

```python
# src/honeyhive/tracer/custom.py (main branch)

class FunctionInstrumentor(BaseInstrumentor):
    """SINGLETON: One global instance for entire application"""
    
    def _instrument(self, **kwargs):
        tracer_provider = TracerProvider()
        otel_trace.set_tracer_provider(tracer_provider)  # GLOBAL
        self._tracer = otel_trace.get_tracer(__name__)   # GLOBAL

# Module-level singleton
instrumentor = FunctionInstrumentor()
instrumentor.instrument()  # Executed on import
```

**Key characteristics:**
- ONE `FunctionInstrumentor` instance per Python process
- ONE global `TracerProvider` set via `set_tracer_provider()`
- ONE global tracer accessible via `get_tracer()`
- All spans created from the same global tracer

### 2. Original enrich_span() Implementation

```python
def enrich_span(
    config=None,
    metadata=None,
    metrics=None,
    feedback=None,
    inputs=None,
    outputs=None,
    error=None,
    event_id=None
):
    """Free function - works with global tracer"""
    
    # Step 1: Get current span from OpenTelemetry global context
    span = otel_trace.get_current_span()
    
    if span is None:
        logger.warning("Please use enrich_span inside a traced function.")
    else:
        # Step 2: Use the GLOBAL instrumentor to enrich
        instrumentor._enrich_span(span, config, metadata, ...)
```

**How it worked:**
1. OpenTelemetry maintains a thread-local context with current span
2. `otel_trace.get_current_span()` retrieves span from this context
3. The span was created by the GLOBAL tracer, so global instrumentor can enrich it
4. No need to know which HoneyHive instance created the span

### 3. Original evaluate() Implementation

```python
# src/honeyhive/evaluation/__init__.py (main branch)

class Evaluation:
    def _init_tracer(self, datapoint_idx: int, inputs: Dict[str, Any]):
        """Initialize ONE tracer for the evaluation"""
        hh = HoneyHiveTracer(
            api_key=self.api_key,
            project=self.project,
            source="evaluation",
            session_name=self.name,
            inputs={'inputs': inputs},
            is_evaluation=True,
            **self._get_tracing_metadata(datapoint_idx)
        )
        return hh
    
    def run_each(self, datapoint_idx: int):
        """Run evaluation for ONE datapoint"""
        
        # Create tracer for this datapoint
        tracer = self._init_tracer(datapoint_idx, inputs)
        session_id = tracer.session_id
        
        # Call user function (NO tracer parameter)
        outputs = self.function(inputs, ground_truth)
        
        # Inside user function, enrich_span() works because:
        # 1. Global instrumentor exists
        # 2. Current span is from global tracer
        # 3. No instance discovery needed
```

**Threading behavior:**
```python
def run(self):
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        futures = []
        for i in range(num_points):
            ctx = contextvars.copy_context()
            futures.append(
                executor.submit(
                    ctx.run,
                    functools.partial(self.run_each, i)
                )
            )
```

**Critical observations:**
- Each thread calls `_init_tracer()` creating a new `HoneyHiveTracer` instance
- BUT these instances all use the SAME global `TracerProvider`
- The global singleton `instrumentor` can enrich any span
- `enrich_span()` works from any thread because it uses global state

### 4. Original @trace Decorator

```python
class FunctionInstrumentor:
    class trace:
        """Decorator that uses the global tracer"""
        
        _func_instrumentor = None  # Set to global instrumentor
        
        def sync_call(self, *args, **kwargs):
            # Uses global tracer
            with self._func_instrumentor._tracer.start_as_current_span(
                self.event_name or self.func.__name__
            ) as span:
                self._setup_span(span, args, kwargs)
                result = self.func(*args, **kwargs)
                return self._handle_result(span, result)

# Module level
trace = instrumentor.trace  # Uses the singleton instrumentor
```

**Key**: The `@trace` decorator always used the global singleton tracer.

---

## New Multi-Instance Architecture (complete-refactor branch)

### 1. Multi-Instance Pattern

```python
# src/honeyhive/tracer/core/tracer.py (complete-refactor)

class HoneyHiveTracer:
    """Each instance is INDEPENDENT"""
    
    def __init__(self, api_key, project, ...):
        # Each instance gets its OWN:
        self.provider = None      # Own TracerProvider
        self.tracer = None        # Own Tracer
        self.span_processor = None  # Own SpanProcessor
        self._tracer_id = None    # Unique ID
        
        # Instance-specific locks
        self._baggage_lock = threading.Lock()
        self._instance_lock = threading.RLock()
        self._flush_lock = threading.Lock()
        
        # Initialize this instance's OTEL components
        initialize_tracer_instance(self)
```

**Key changes:**
- NO global singleton
- Each `HoneyHiveTracer()` creates its own `TracerProvider`
- Each instance registers itself in a weak-reference registry
- Thread-safe: Each instance has its own locks

### 2. Tracer Registry System

```python
# src/honeyhive/tracer/registry.py

# Global registry (not singleton - just a lookup table)
_TRACER_REGISTRY: WeakValueDictionary[str, HoneyHiveTracer] = WeakValueDictionary()

def register_tracer(tracer: HoneyHiveTracer) -> str:
    """Register a tracer instance and return its unique ID"""
    tracer_id = str(id(tracer))
    _TRACER_REGISTRY[tracer_id] = tracer
    return tracer_id

def discover_tracer(
    explicit_tracer: Optional[HoneyHiveTracer] = None,
    ctx: Optional[Context] = None,
) -> Optional[HoneyHiveTracer]:
    """Discover tracer using priority-based fallback"""
    
    # Priority 1: Explicit tracer parameter
    if explicit_tracer is not None:
        return explicit_tracer
    
    # Priority 2: Baggage-discovered tracer (from context)
    tracer_id = baggage.get_baggage("honeyhive_tracer_id", ctx)
    if tracer_id and tracer_id in _TRACER_REGISTRY:
        return _TRACER_REGISTRY[tracer_id]
    
    # Priority 3: Global default tracer
    default_tracer = get_default_tracer()
    if default_tracer is not None:
        return default_tracer
    
    return None  # No tracer found
```

### 3. New enrich_span() Implementation

```python
# src/honeyhive/tracer/instrumentation/enrichment.py

def enrich_span_unified(
    attributes=None,
    metadata=None,
    metrics=None,
    tracer_instance=None,  # New parameter
    caller="direct_call",
    **kwargs
):
    """Unified implementation that needs to discover tracer"""
    
    # Try to discover tracer if not provided
    if tracer_instance is None:
        try:
            current_ctx = context.get_current()
            tracer_instance = discover_tracer(
                explicit_tracer=None, 
                ctx=current_ctx
            )
        except Exception as e:
            safe_log(None, "debug", f"Failed to discover tracer: {e}")
    
    # Get current span (same as before)
    current_span = trace.get_current_span()
    
    # Enrich the span
    if current_span:
        _set_span_attributes(current_span, "honeyhive_metadata", metadata)
        # ... etc
```

**The problem:**
- `discover_tracer()` tries three fallback methods
- In evaluate pattern, ALL THREE FAIL:
  - No explicit tracer passed
  - Baggage context not set up for evaluate pattern
  - No default tracer set

### 4. New evaluate() Implementation

```python
# src/honeyhive/experiments/core.py

def run_experiment(
    function: Callable,
    dataset: List[Dict],
    datapoint_ids: List[str],
    experiment_context: ExperimentContext,
    api_key: Optional[str] = None,
    max_workers: int = 10,
):
    """CRITICAL: Each datapoint gets its OWN tracer instance"""
    
    def process_datapoint(datapoint, datapoint_id):
        # Create NEW isolated tracer for THIS datapoint
        tracer_config = experiment_context.to_tracer_config(datapoint_id)
        tracer = HoneyHiveTracer(
            api_key=api_key,
            **tracer_config  # Unique per datapoint
        )
        
        try:
            # Execute user function
            # ❌ PROBLEM: No tracer passed to function
            outputs = function(datapoint)
            
            # Inside function, enrich_span() tries to discover tracer
            # but can't find it!
            
            session_id = getattr(tracer, "session_id", None)
            return {
                "datapoint_id": datapoint_id,
                "outputs": outputs,
                "session_id": session_id,
            }
        finally:
            force_flush_tracer(tracer)
    
    # ThreadPoolExecutor - each thread gets different tracer
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_datapoint, dp, dp_id)
            for dp, dp_id in zip(dataset, datapoint_ids)
        ]
```

**Why enrich_span() fails:**

```
Thread 1: tracer_1 → processes datapoint_1
  └─ user function calls enrich_span()
      └─ discover_tracer() searches:
          ❌ explicit_tracer: None (not passed)
          ❌ baggage: "honeyhive_tracer_id" not in context
          ❌ default: Not set for multi-instance
      └─ Returns None
      └─ enrich_span() fails silently

Thread 2: tracer_2 → processes datapoint_2
  └─ Same failure pattern
```

### 5. New @trace Decorator

```python
# src/honeyhive/tracer/instrumentation/decorators.py

def trace(event_type=None, event_name=None, **kwargs):
    """Decorator that discovers tracer dynamically"""
    
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            # Discover tracer at execution time
            tracer = _discover_tracer_safely(kwargs, func)
            
            if tracer is None:
                # Execute without tracing
                return func(*args, **func_kwargs)
            
            # Set up baggage context
            with tracer.start_span(event_name) as span:
                _setup_decorator_baggage_context(tracer, span)
                return func(*args, **func_kwargs)
```

**Baggage context setup:**
```python
def _setup_decorator_baggage_context(tracer, span):
    """Set tracer_id in baggage for child operations"""
    ctx = context.get_current()
    
    # Add tracer_id to baggage
    if hasattr(tracer, "_tracer_id"):
        ctx = baggage.set_baggage(
            "honeyhive_tracer_id", 
            str(tracer._tracer_id), 
            ctx
        )
    
    context.attach(ctx)
```

**Why this works for decorator but not evaluate:**
- Decorator sets up baggage explicitly
- Child operations (nested @trace calls) can discover via baggage
- But evaluate() doesn't use decorator pattern - it directly calls user function

---

## Detailed Comparison

### Scenario: User calls enrich_span() inside evaluated function

#### Original (Works):
```python
@trace(event_type="tool")  # Uses global instrumentor
def my_function(inputs, ground_truth):
    result = do_something(inputs)
    enrich_span(metadata={"step": "processing"})  # ✅ Works
    #          ↓
    #  Uses global instrumentor singleton
    #  Global tracer → global span → enrichment works
    return result

# evaluate() creates ONE tracer per thread
# All spans in thread use SAME global tracer
# enrich_span() uses global instrumentor
```

#### New (Broken):
```python
@trace(event_type="tool")  # Needs to discover which tracer
def my_function(datapoint):
    result = do_something(datapoint)
    enrich_span(metadata={"step": "processing"})  # ❌ Fails
    #          ↓
    #  Tries discover_tracer():
    #    - No explicit tracer
    #    - No baggage (not set by evaluate)
    #    - No default tracer
    #  Returns None → silent failure
    return result

# evaluate() creates DIFFERENT tracer per datapoint
# Each tracer is isolated
# enrich_span() can't find the right tracer
```

---

## Threading Behavior: Deep Dive

### Original SDK Threading Model

#### Global State + ThreadLocal Spans

```python
# Conceptual model of original threading behavior

┌─────────────────────────────────────────────────────────────────┐
│ Python Process                                                  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ GLOBAL: FunctionInstrumentor (singleton)                │   │
│  │ GLOBAL: TracerProvider (ONE for entire process)         │   │
│  │ GLOBAL: Tracer (ONE for entire process)                 │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ThreadPoolExecutor(max_workers=10):                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Thread 1     │  │ Thread 2     │  │ Thread 3     │        │
│  │              │  │              │  │              │        │
│  │ HH Tracer #1 │  │ HH Tracer #2 │  │ HH Tracer #3 │        │
│  │ (wrapper)    │  │ (wrapper)    │  │ (wrapper)    │        │
│  │      ↓       │  │      ↓       │  │      ↓       │        │
│  │  session_1   │  │  session_2   │  │  session_3   │        │
│  │      ↓       │  │      ↓       │  │      ↓       │        │
│  │ SAME GLOBAL  │  │ SAME GLOBAL  │  │ SAME GLOBAL  │        │
│  │ TracerProv.  │  │ TracerProv.  │  │ TracerProv.  │        │
│  │      ↓       │  │      ↓       │  │      ↓       │        │
│  │ ThreadLocal  │  │ ThreadLocal  │  │ ThreadLocal  │        │
│  │ Span Context │  │ Span Context │  │ Span Context │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                  │                  │                │
│         └──────────────────┴──────────────────┘                │
│                            │                                    │
│                    All use SAME                                 │
│                    instrumentor._enrich_span()                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Behaviors:

**1. HoneyHiveTracer Instances:**
```python
# Thread 1
tracer_1 = HoneyHiveTracer(
    api_key="key",
    project="proj",
    session_name="eval",
    # Datapoint 1 metadata
)
# Creates wrapper but uses GLOBAL TracerProvider

# Thread 2
tracer_2 = HoneyHiveTracer(
    api_key="key",
    project="proj", 
    session_name="eval",
    # Datapoint 2 metadata
)
# Also uses SAME GLOBAL TracerProvider
```

**2. OpenTelemetry Context (Thread-Local):**
```python
# Each thread has its own context stack
# but all tracers share the same provider

Thread 1:
  Context Stack:
    span_context_1 (datapoint 1)
      └─ current_span = tool_call_span
           ↓
      Uses GLOBAL TracerProvider
      
Thread 2:
  Context Stack:
    span_context_2 (datapoint 2)
      └─ current_span = tool_call_span
           ↓
      Uses GLOBAL TracerProvider (SAME!)
```

**3. enrich_span() Resolution:**
```python
# Called from Thread 1
def enrich_span(metadata={"model": "gpt-4"}):
    # Step 1: Get span from thread-local context
    span = otel_trace.get_current_span()
    # Gets span_context_1's current span ✅
    
    # Step 2: Use GLOBAL instrumentor
    instrumentor._enrich_span(span, metadata)
    # Uses the singleton instrumentor ✅
    
    # Works because:
    # - Span exists in thread-local context
    # - Instrumentor is global and always accessible
```

**4. Thread Safety:**
```python
# Original thread safety model:

✅ Thread-local span contexts (OpenTelemetry built-in)
✅ Each thread processes different datapoint
✅ No shared mutable state between threads
❌ BUT: Relies on global singleton state
❌ Can't have different tracer configs per thread
```

#### Example Flow:

```python
# Main thread: Start evaluate()
evaluate(
    function=my_function,
    dataset=[dp1, dp2, dp3],
    max_workers=3
)

# ThreadPoolExecutor spawns 3 threads:

Thread 1: 
  _init_tracer(datapoint_idx=0)
  → HoneyHiveTracer(session_name="eval", datapoint_id="dp1")
  → Wraps global tracer with datapoint-specific session
  → user_function(dp1)
      → @trace decorator uses global instrumentor
      → enrich_span() uses global instrumentor ✅

Thread 2:
  _init_tracer(datapoint_idx=1)  
  → HoneyHiveTracer(session_name="eval", datapoint_id="dp2")
  → Wraps global tracer with different session
  → user_function(dp2)
      → @trace decorator uses global instrumentor  
      → enrich_span() uses global instrumentor ✅

Thread 3:
  _init_tracer(datapoint_idx=2)
  → HoneyHiveTracer(session_name="eval", datapoint_id="dp3")
  → Wraps global tracer with different session
  → user_function(dp3)
      → @trace decorator uses global instrumentor
      → enrich_span() uses global instrumentor ✅

All threads use SAME global instrumentor!
enrich_span() always works!
```

### New SDK Threading Model

#### Isolated Instances + No Global State

```python
# Conceptual model of new threading behavior

┌─────────────────────────────────────────────────────────────────┐
│ Python Process                                                  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ REGISTRY: WeakValueDictionary (lookup only)             │   │
│  │ - Not a singleton                                        │   │
│  │ - Just maps tracer_id → tracer instance                 │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ThreadPoolExecutor(max_workers=10):                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Thread 1     │  │ Thread 2     │  │ Thread 3     │        │
│  │              │  │              │  │              │        │
│  │ HH Tracer #1 │  │ HH Tracer #2 │  │ HH Tracer #3 │        │
│  │ (isolated)   │  │ (isolated)   │  │ (isolated)   │        │
│  │      │       │  │      │       │  │      │       │        │
│  │ TracerProv#1 │  │ TracerProv#2 │  │ TracerProv#3 │        │
│  │ Tracer #1    │  │ Tracer #2    │  │ Tracer #3    │        │
│  │ SpanProc #1  │  │ SpanProc #2  │  │ SpanProc #3  │        │
│  │      ↓       │  │      ↓       │  │      ↓       │        │
│  │  session_1   │  │  session_2   │  │  session_3   │        │
│  │      ↓       │  │      ↓       │  │      ↓       │        │
│  │ ThreadLocal  │  │ ThreadLocal  │  │ ThreadLocal  │        │
│  │ Span Context │  │ Span Context │  │ Span Context │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                  │                  │                │
│         │                  │                  │                │
│    Need to find       Need to find       Need to find         │
│    tracer #1          tracer #2          tracer #3            │
│    for enrich!        for enrich!        for enrich!          │
│         ↓                  ↓                  ↓                │
│    ❌ No global     ❌ No global     ❌ No global            │
│    instrumentor!    instrumentor!    instrumentor!            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Behavioral Differences:

**1. Completely Isolated Tracer Instances:**
```python
# Thread 1
tracer_1 = HoneyHiveTracer(
    api_key="key",
    project="proj",
    # Creates OWN TracerProvider
    # Creates OWN Tracer
    # Creates OWN SpanProcessor
    # Completely isolated!
)

# Thread 2
tracer_2 = HoneyHiveTracer(
    api_key="key",
    project="proj",
    # Creates DIFFERENT TracerProvider
    # Creates DIFFERENT Tracer
    # Creates DIFFERENT SpanProcessor
    # No shared state with Thread 1!
)
```

**2. OpenTelemetry Context Still Thread-Local:**
```python
# Context is still thread-local (OpenTelemetry design)
# But now each thread's spans come from DIFFERENT tracers

Thread 1:
  Context Stack:
    span_context_1 (from tracer_1's provider)
      └─ current_span = tool_call_span (created by tracer_1)
           ↓
      Uses tracer_1's TracerProvider
      
Thread 2:
  Context Stack:
    span_context_2 (from tracer_2's provider)
      └─ current_span = tool_call_span (created by tracer_2)
           ↓
      Uses tracer_2's TracerProvider (DIFFERENT!)
```

**3. enrich_span() Discovery Problem:**
```python
# Called from Thread 1
def enrich_span(metadata={"model": "gpt-4"}):
    # Step 1: Try to discover which tracer to use
    tracer_instance = discover_tracer()
    
    # Discovery attempts:
    # 1. Check explicit parameter → None (not passed)
    # 2. Check baggage for tracer_id → None (not set by evaluate)
    # 3. Check default tracer → None (multi-instance, no default)
    
    # tracer_instance = None ❌
    
    # Step 2: Get span from thread-local context
    span = otel_trace.get_current_span()
    # Gets span created by tracer_1 ✅
    
    # Step 3: Try to enrich without knowing which tracer
    # We have the span but don't know it belongs to tracer_1!
    # Can't access tracer_1's configuration or methods ❌
```

**4. The Core Problem Visualized:**
```python
# Thread 1 execution flow:

evaluate() 
  → ThreadPoolExecutor.submit(process_datapoint, dp1)
      → tracer_1 = HoneyHiveTracer(...)  # Created in Thread 1
          → tracer_1._tracer_id = register_tracer(tracer_1)
          → Registry: {id(tracer_1): tracer_1}
          
      → function(datapoint)  # User function called
          → @trace decorator
              → discover_tracer()
                  → Check explicit: None
                  → Check baggage: None (not set!)
                  → Check default: None
                  → return None ❌
                  
              → Falls back to no-op tracing ❌
              
          → enrich_span(metadata={...})
              → discover_tracer()
                  → Same failures as above ❌
                  → return None
                  
              → Can't enrich without tracer reference ❌
```

**5. Thread Safety (Still Good):**
```python
# New thread safety model:

✅ Complete isolation per thread (own tracers)
✅ No shared mutable state between threads  
✅ Thread-safe by design (no global singleton)
✅ Can have different configs per thread
✅ Better for multi-tenant scenarios

❌ BUT: Lost ability for free functions to "just work"
❌ Requires explicit tracer passing or context setup
```

#### Example Flow (Broken):

```python
# Main thread: Start evaluate()
evaluate(
    function=my_function,
    dataset=[dp1, dp2, dp3],
    max_workers=3
)

# ThreadPoolExecutor spawns 3 threads:

Thread 1:
  process_datapoint(dp1)
  → tracer_1 = HoneyHiveTracer(...)  # New isolated instance
  → tracer_1 registered in registry with id1
  → user_function(dp1)  # No tracer passed! ❌
      → @trace decorator tries discover_tracer()
          → Can't find tracer_1 ❌
          → No baggage set ❌
      → enrich_span() tries discover_tracer()
          → Can't find tracer_1 ❌
          → Fails silently ❌

Thread 2:
  process_datapoint(dp2)
  → tracer_2 = HoneyHiveTracer(...)  # Different isolated instance
  → tracer_2 registered in registry with id2
  → user_function(dp2)  # No tracer passed! ❌
      → @trace decorator tries discover_tracer()
          → Can't find tracer_2 ❌
      → enrich_span() tries discover_tracer()
          → Can't find tracer_2 ❌

Thread 3:
  process_datapoint(dp3)
  → tracer_3 = HoneyHiveTracer(...)  # Another isolated instance
  → tracer_3 registered in registry with id3
  → user_function(dp3)  # No tracer passed! ❌
      → Same failures as above ❌

Each thread has its own tracer!
But enrich_span() can't discover which one to use!
```

### Why Baggage Discovery Doesn't Work

#### Baggage Context Propagation Flow

**Original (Not Needed):**
```python
# Baggage wasn't needed because of global singleton
# But let's see theoretical flow:

Thread 1:
  @trace decorator on user function
    → Uses global instrumentor
    → Creates span from global tracer
    → (Baggage not used, not needed)
    → enrich_span() uses global instrumentor directly
```

**New (Should Work But Doesn't):**
```python
# Baggage WOULD work if set up properly, but evaluate() doesn't set it

Thread 1:
  process_datapoint(dp1)
    → tracer_1 = HoneyHiveTracer(...)
    → tracer_1._tracer_id = "abc123"
    
    # What SHOULD happen:
    → with tracer_1.start_span("evaluate_wrapper"):
        → Sets baggage: {"honeyhive_tracer_id": "abc123"}
        → user_function(dp1)
            → @trace decorator
                → discover_tracer(ctx=current_context)
                → baggage.get("honeyhive_tracer_id") → "abc123"
                → registry["abc123"] → tracer_1 ✅
            → enrich_span()
                → discover_tracer() → tracer_1 ✅
    
    # What ACTUALLY happens:
    → user_function(dp1)  # Direct call, no span wrapper! ❌
        → No baggage set! ❌
        → @trace decorator can't discover tracer ❌
        → enrich_span() can't discover tracer ❌
```

### Threading Safety Comparison

#### Original: Thread-Safe via Thread-Local Context

```python
✅ OpenTelemetry's thread-local context isolates spans
✅ Each thread processes different datapoint  
✅ No race conditions on span data

⚠️ But global singleton has limitations:
  - All threads share same TracerProvider config
  - Can't have per-thread tracer configuration
  - Global state makes testing harder
```

#### New: Thread-Safe via Complete Isolation

```python
✅ Each thread has completely isolated tracer
✅ No shared state whatsoever
✅ Can have different configs per thread
✅ Better for testing (no global state)
✅ Supports multi-tenant scenarios

⚠️ But requires explicit tracer propagation:
  - Can't discover tracer from free functions
  - Requires passing tracer or setting up baggage
  - Breaking change from original API
```

### Why Multi-Instance is Better (Despite Breaking Changes)

**Isolation Benefits:**
```python
# Scenario: Multi-tenant SaaS evaluating for different customers

Thread 1 (Customer A):
  tracer_a = HoneyHiveTracer(
      api_key="customer_a_key",
      project="customer_a_project"
  )
  # Completely isolated, no data leakage

Thread 2 (Customer B):
  tracer_b = HoneyHiveTracer(
      api_key="customer_b_key", 
      project="customer_b_project"
  )
  # Completely isolated, no data leakage

# Original singleton couldn't support this!
```

**Configuration Flexibility:**
```python
# Each thread can have different config

Thread 1:
  tracer_1 = HoneyHiveTracer(
      disable_batch=True,    # Real-time for this test
      verbose=True
  )

Thread 2:
  tracer_2 = HoneyHiveTracer(
      disable_batch=False,   # Batched for this test
      verbose=False
  )

# Original singleton: one config for all threads
```

---

## Root Cause Analysis

### Why Original Design Worked

**Global State Advantages:**
1. Single source of truth (one instrumentor, one tracer provider)
2. Thread-local spans work naturally with global tracer
3. Any code can enrich any span - no instance tracking needed
4. Simple mental model: "enrich the current span"

**Trade-offs:**
- Singleton pattern (hard to have multiple independent tracers)
- Global state (thread-safety concerns)
- Inflexible (can't have different configs per tracer)

### Why New Design Breaks

**Multi-Instance Advantages:**
1. Complete isolation between tracer instances
2. Thread-safe by design (no shared mutable state)
3. Flexible (each tracer can have different config)
4. Scalable (support for multi-tenant scenarios)

**The Cost:**
- Need explicit tracer discovery
- Can't use free functions that "just work"
- Requires context propagation (baggage)
- Breaking change for enrich_span() API

**The Core Problem:**
```
Old: Global state → enrich_span() "just works"
New: No global state → enrich_span() needs instance reference
```

---

## Current Workarounds (All Incomplete)

### 1. Thread-Local Storage (Proposed)
```python
_thread_local = threading.local()

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    _thread_local.tracer = tracer  # Store in thread-local
    
    try:
        outputs = function(datapoint)
    finally:
        delattr(_thread_local, 'tracer')
```

**Issues:**
- Requires modifying evaluate() internals
- Thread-local is global state in disguise
- Import order dependencies
- Not discoverable from other modules

### 2. Set Default Tracer (Current Attempt)
```python
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    set_default_tracer(tracer)  # Set as global default
    
    outputs = function(datapoint)
```

**Issues:**
- Race condition: Multiple threads overwriting default
- Last thread wins (non-deterministic)
- Not actually thread-safe

### 3. Explicit Tracer Parameter (Clean but Breaking)
```python
# User code changes required
def my_function(datapoint, tracer):  # New parameter
    result = do_something(datapoint)
    tracer.enrich_span(metadata={"step": "processing"})  # Instance method
    return result

# evaluate() passes tracer explicitly
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    outputs = function(datapoint, tracer=tracer)  # Pass explicitly
```

**Issues:**
- Breaking API change
- Requires updating all user functions
- But: Clean, explicit, thread-safe

---

## Technical Details: Why Baggage Doesn't Work

### Baggage Context Propagation

```python
# In @trace decorator
def _setup_decorator_baggage_context(tracer, span):
    """This ONLY works when using @trace decorator"""
    ctx = context.get_current()
    ctx = baggage.set_baggage("honeyhive_tracer_id", tracer._tracer_id, ctx)
    context.attach(ctx)
```

### Why evaluate() Doesn't Set Baggage

```python
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # No span context manager here!
    # Just direct function call
    outputs = function(datapoint)  # Not wrapped in span
    
    # Inside function:
    @trace(event_type="tool")  # This creates span
    def my_function(datapoint):
        enrich_span(...)  # Tries to discover - but baggage not set!
```

**The issue:**
- Baggage is set INSIDE `@trace` decorator's span context
- But evaluate() doesn't wrap the user function call in a span
- So baggage is never set at the right level
- Child `@trace` decorators set their own baggage, but it's too late

---

## Conclusion

The multi-instance architecture is fundamentally incompatible with the original `enrich_span()` free function pattern. The original design relied on global singleton state that no longer exists.

**Three paths forward:**

1. **Keep free function, add thread-local** - Hacky, maintains backward compat
2. **Instance method only** - Clean, breaking change, explicit
3. **Hybrid approach** - Instance method primary, free function deprecated

**Recommendation**: Option 2 (instance method) with clear migration guide and version bump. The singleton-to-multi-instance refactor is a fundamental architectural change that warrants an API change.

---

## Current Unified enrich_span() Implementation

### Design Goals

The new implementation expands functionality while maintaining backward compatibility through a **unified entry point pattern**:

1. **Multiple invocation patterns** from single entry point
2. **Backward compatibility** with original reserved parameters
3. **Extended functionality** with new convenience features
4. **Graceful degradation** when tracer discovery fails

### Architecture Overview

```python
# Single entry point
enrich_span = UnifiedEnrichSpan()

# Supports multiple usage patterns:
enrich_span(metadata={...})              # Direct call → bool
with enrich_span(metadata={...}) as s:   # Context manager → span
if enrich_span(metadata={...}):          # Boolean evaluation → bool
```

### Component Breakdown

#### 1. UnifiedEnrichSpan Class (Entry Point)

```python
class UnifiedEnrichSpan:
    """Auto-detects invocation pattern via Python magic methods"""
    
    def __call__(self, ...):
        # Store parameters and return self
        # Enables method chaining
        return self
    
    def __enter__(self):
        # Context manager entry
        # Delegates to enrich_span_unified(caller="context_manager")
        return span
    
    def __exit__(self, ...):
        # Context manager cleanup
        pass
    
    def __bool__(self):
        # Direct call/boolean evaluation
        # Delegates to enrich_span_unified(caller="direct_call")
        return bool(success)
```

**Key Insight:** Uses Python's dunder methods to detect usage pattern automatically.

#### 2. enrich_span_unified() (Router)

```python
def enrich_span_unified(
    ...,
    tracer_instance=None,
    caller="direct_call",  # Explicit caller identification
    **kwargs
):
    """Routes to appropriate implementation based on caller"""
    
    # Step 1: Discover tracer if not provided
    if tracer_instance is None:
        tracer_instance = discover_tracer(
            explicit_tracer=None,
            ctx=context.get_current()
        )
        # Priority:
        # 1. Baggage-discovered tracer
        # 2. Global default tracer
        # 3. None (graceful failure)
    
    # Step 2: Route based on caller
    if caller == "context_manager":
        return _enrich_span_context_manager(...)
    else:
        return _enrich_span_direct_call(...)
```

**Key Insight:** Explicit `caller` parameter makes behavior predictable.

#### 3. enrich_span_core() (Core Logic)

```python
def enrich_span_core(
    attributes=None,     # NEW: Simple dict → metadata
    metadata=None,       # ORIGINAL: Metadata namespace
    metrics=None,        # ORIGINAL: Metrics namespace
    feedback=None,       # ORIGINAL: Feedback namespace
    inputs=None,         # ORIGINAL: Inputs namespace
    outputs=None,        # ORIGINAL: Outputs namespace
    config=None,         # ORIGINAL: Config namespace
    error=None,          # ORIGINAL: Error string
    event_id=None,       # ORIGINAL: Event ID
    tracer_instance=None,# NEW: Optional tracer
    **kwargs             # NEW: Convenience kwargs → metadata
):
    """Core enrichment with namespace routing"""
    
    # Get current span from OpenTelemetry
    current_span = trace.get_current_span()
    
    # Apply in precedence order:
    # 1. Reserved parameters (metadata, metrics, etc.)
    if metadata:
        _set_span_attributes(span, "honeyhive_metadata", metadata)
    if metrics:
        _set_span_attributes(span, "honeyhive_metrics", metrics)
    # ... other reserved params
    
    # 2. attributes dict → metadata namespace
    if attributes:
        _set_span_attributes(span, "honeyhive_metadata", attributes)
    
    # 3. kwargs → metadata namespace (wins conflicts)
    if kwargs:
        _set_span_attributes(span, "honeyhive_metadata", kwargs)
    
    return {"success": True, "span": span, "attribute_count": count}
```

### Supported Usage Patterns

#### Pattern 1: Direct Call (Original/Most Common)

```python
# Original main branch style
@trace(event_type="tool")
def my_function():
    enrich_span(
        metadata={"user_id": "123"},
        metrics={"score": 0.95}
    )
```

**Flow:**
1. `UnifiedEnrichSpan.__call__()` stores parameters
2. `UnifiedEnrichSpan.__bool__()` triggers evaluation
3. `enrich_span_unified(caller="direct_call")`
4. `_enrich_span_direct_call()` → returns `bool`

#### Pattern 2: Context Manager (New)

```python
@trace(event_type="tool")
def my_function():
    with enrich_span(metadata={"step": "processing"}) as span:
        # Do work
        # Span is enriched when entering context
        result = process_data()
```

**Flow:**
1. `UnifiedEnrichSpan.__call__()` stores parameters
2. `UnifiedEnrichSpan.__enter__()` triggers enrichment
3. `enrich_span_unified(caller="context_manager")`
4. `_enrich_span_context_manager()` → yields `span`

#### Pattern 3: Simplified Kwargs (New)

```python
@trace(event_type="tool")
def my_function():
    # Convenience: kwargs route to metadata automatically
    enrich_span(
        user_id="123",      # → honeyhive_metadata.user_id
        feature="chat",     # → honeyhive_metadata.feature
        temperature=0.7     # → honeyhive_metadata.temperature
    )
```

**Flow:**
1. `enrich_span_core()` routes kwargs to metadata namespace
2. Simpler than `enrich_span(metadata={"user_id": "123", ...})`

#### Pattern 4: Mixed Parameters (Advanced)

```python
@trace(event_type="tool")
def my_function():
    enrich_span(
        metadata={"base_info": "value"},  # Reserved param
        metrics={"score": 0.95},          # Reserved param
        user_id="123",                     # Kwarg → metadata
        feature="chat"                     # Kwarg → metadata
    )
    # Result:
    # honeyhive_metadata.base_info = "value"
    # honeyhive_metadata.user_id = "123"   (kwargs merged)
    # honeyhive_metadata.feature = "chat"
    # honeyhive_metrics.score = 0.95
```

### Parameter Precedence System

**When same key appears in multiple places:**

```python
enrich_span(
    metadata={"model": "gpt-3.5"},  # Priority 1
    attributes={"model": "gpt-4"},  # Priority 2
    model="claude-3"                # Priority 3 (WINS)
)
# Final: honeyhive_metadata.model = "claude-3"
```

**Precedence order (last wins):**
1. Reserved parameters (metadata, metrics, etc.)
2. `attributes` dict
3. `**kwargs`

### Namespace Routing

```python
# Different parameters route to different OpenTelemetry attribute namespaces:

enrich_span(
    metadata={"key": "val"},   # → honeyhive_metadata.key
    metrics={"key": "val"},    # → honeyhive_metrics.key
    feedback={"key": "val"},   # → honeyhive_feedback.key
    inputs={"key": "val"},     # → honeyhive_inputs.key
    outputs={"key": "val"},    # → honeyhive_outputs.key
    config={"key": "val"},     # → honeyhive_config.key
    error="message",           # → honeyhive_error (no namespace)
    event_id="uuid",           # → honeyhive_event_id (no namespace)
    
    # New convenience: kwargs → metadata
    custom_field="val"         # → honeyhive_metadata.custom_field
)
```

### Tracer Discovery Flow

```python
def enrich_span_unified(..., tracer_instance=None, ...):
    if tracer_instance is None:
        # Try to discover tracer automatically
        tracer_instance = discover_tracer(
            explicit_tracer=None,
            ctx=context.get_current()
        )
        # Priority order:
        # 1. Baggage context (from @trace decorator)
        # 2. Global default tracer
        # 3. None → graceful degradation
```

**Where discovery WORKS:**
```python
# Nested @trace decorators
@trace(event_type="chain")
def outer():
    @trace(event_type="tool")
    def inner():
        enrich_span(metadata={...})  # ✅ Works
        # Baggage set by @trace decorator
```

**Where discovery FAILS:**
```python
# evaluate() pattern
evaluate(
    function=my_function,
    dataset=[...]
)
# process_datapoint() creates tracer
# but doesn't set baggage
# enrich_span() can't discover tracer ❌
```

### Design Strengths

1. **Unified Entry Point**
   - Single `enrich_span` handles all patterns
   - No need for `enrich_span_sync`, `enrich_span_async`, `enrich_span_with`, etc.
   - Cleaner API surface

2. **Backward Compatibility**
   - All original parameters still work
   - Original usage patterns unchanged
   - Smooth migration path

3. **Extended Functionality**
   - Context manager pattern for scoped enrichment
   - Kwargs convenience for simpler calls
   - Boolean evaluation for conditional logic

4. **Graceful Degradation**
   - Tracer discovery failures don't crash
   - Returns NoOpSpan when no active span
   - Logging for debugging

5. **Type Safety**
   - Type hints throughout
   - Return types depend on usage pattern
   - IDE autocomplete support

### Design Weaknesses (For evaluate() Pattern)

1. **Tracer Discovery Limited**
   - Only works with baggage or default tracer
   - No thread-local discovery
   - Can't discover per-thread tracers in evaluate()

2. **Silent Failures**
   - When tracer not found, enrichment silently fails
   - Only debug logs, no exceptions
   - Hard to debug in production

3. **No Explicit Tracer Parameter in Public API**
   - `tracer` parameter exists but not documented for users
   - Could be exposed as explicit parameter:
   ```python
   enrich_span(
       metadata={...},
       tracer=my_tracer  # Explicit tracer
   )
   ```

4. **Context Manager Doesn't Add Value for evaluate()**
   - Context manager useful for scoped enrichment
   - But evaluate() doesn't use spans in user functions
   - Pattern mismatch

### Comparison: Original vs Unified

#### Original (main branch)

```python
def enrich_span(config=None, metadata=None, ...):
    """Simple free function"""
    span = otel_trace.get_current_span()
    instrumentor._enrich_span(span, ...)  # Uses global singleton
```

**Characteristics:**
- Single usage pattern (direct call)
- Uses global singleton instrumentor
- No tracer discovery needed
- Simple, straightforward

#### Unified (complete-refactor)

```python
class UnifiedEnrichSpan:
    """Multiple patterns via magic methods"""
    def __call__(self, ...): ...
    def __enter__(self, ...): ...
    def __bool__(self, ...): ...

enrich_span = UnifiedEnrichSpan()
```

**Characteristics:**
- Multiple usage patterns
- Requires tracer discovery
- More complex implementation
- More flexible

### Potential Improvements for evaluate()

#### Option A: Expose explicit tracer parameter

```python
# Public API update
enrich_span(
    metadata={"model": "gpt-4"},
    tracer=explicit_tracer  # Make this official
)

# In evaluate()
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    # Pass tracer to user function somehow
    outputs = function(datapoint, tracer=tracer)
```

#### Option B: Add instance method to HoneyHiveTracer

```python
class HoneyHiveTracer:
    def enrich_span(self, metadata=None, metrics=None, ...):
        """Instance method - direct access"""
        # Can access self.tracer, self.config, etc.
        # No discovery needed
```

#### Option C: Thread-local tracer storage

```python
# In experiments/core.py
from threading import local
_thread_local = local()

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    _thread_local.tracer = tracer  # Store in thread-local
    
    try:
        outputs = function(datapoint)
    finally:
        del _thread_local.tracer

# In discover_tracer()
def discover_tracer(...):
    # Priority 3: Check thread-local
    if hasattr(_thread_local, 'tracer'):
        return _thread_local.tracer
```

---

## The Core Propagation Problem

### The Real Issue: Getting Tracer from evaluate() to User Code

**The fundamental challenge is NOT just the API design (free function vs instance method). The challenge is PROPAGATION:**

```python
# Call stack:
evaluate()
  → run_experiment()
      → process_datapoint()
          → tracer = HoneyHiveTracer(...)  # ← Tracer created HERE
          → function(datapoint)              # ← User function called
              → @trace decorator
                  → enrich_span(...)         # ← Enrichment called HERE
                  # OR tracer.enrich_span()   # ← Still need tracer reference!
```

**The Gap:** How do we get `tracer` from `process_datapoint()` to the `enrich_span()` call inside the user's function?

### Why Instance Method Doesn't Solve It Alone

```python
# Even with instance method:
class HoneyHiveTracer:
    def enrich_span(self, metadata=None):
        # This works great IF user has reference to tracer
        pass

# But in evaluate():
def process_datapoint(datapoint):
    tracer = HoneyHiveTracer(...)
    
    # User function has NO reference to tracer!
    outputs = function(datapoint)
    
    # Inside user function:
    def user_function(datapoint):
        # How do we call tracer.enrich_span() without tracer reference?
        # tracer.enrich_span(...)  # ← Where does 'tracer' come from?
```

**Instance method is cleaner, but doesn't solve propagation.**

### All Possible Solutions for Propagation

#### Solution 1: Explicit Parameter (Breaking Change)

```python
# Modify evaluate() to pass tracer to user function
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Pass tracer as parameter
    outputs = function(datapoint, tracer=tracer)

# User must update their function signature
def user_function(datapoint, tracer):  # ← New parameter required
    result = process(datapoint)
    tracer.enrich_span(metadata={"step": "done"})  # ← Clean!
    return result
```

**Pros:**
- ✅ Explicit and clear
- ✅ Type-safe
- ✅ Thread-safe
- ✅ No magic
- ✅ Works with instance method pattern

**Cons:**
- ❌ Breaking change to user code
- ❌ Every evaluate function needs updating
- ❌ Not backward compatible

#### Solution 2: Thread-Local Storage (Implicit Propagation)

```python
# In experiments/core.py
from threading import local
_thread_local = local()

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Store in thread-local
    _thread_local.tracer = tracer
    
    try:
        # User function unchanged - no tracer parameter
        outputs = function(datapoint)
    finally:
        # Clean up
        if hasattr(_thread_local, 'tracer'):
            delattr(_thread_local, 'tracer')

# In enrichment.py or tracer method
def enrich_span(...):
    # Try thread-local discovery
    tracer = getattr(_thread_local, 'tracer', None)
    if tracer:
        # Found it!
        tracer._enrich_span_internal(...)
```

**Pros:**
- ✅ Backward compatible (no user code changes)
- ✅ Thread-safe (each thread has own storage)
- ✅ Works with both free function and instance method
- ✅ User code unchanged

**Cons:**
- ❌ Magic/implicit (harder to debug)
- ❌ Global state in disguise
- ❌ Import order dependencies
- ❌ Harder to test

#### Solution 3: Context Variables (Modern Thread-Local)

```python
# In experiments/core.py
import contextvars

# Create context variable
_current_tracer: contextvars.ContextVar[Optional[HoneyHiveTracer]] = (
    contextvars.ContextVar('current_tracer', default=None)
)

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Set in context
    token = _current_tracer.set(tracer)
    
    try:
        # User function unchanged
        outputs = function(datapoint)
    finally:
        # Reset context
        _current_tracer.reset(token)

# In enrichment
def enrich_span(...):
    tracer = _current_tracer.get()
    if tracer:
        tracer._enrich_span_internal(...)
```

**Pros:**
- ✅ Backward compatible
- ✅ Better than thread-local (async-safe)
- ✅ Proper context isolation
- ✅ Python standard library

**Cons:**
- ❌ Still implicit/magic
- ❌ Requires Python 3.7+ (already required)
- ❌ Import order dependencies

#### Solution 4: Baggage Context (OpenTelemetry Native)

```python
# In experiments/core.py
from opentelemetry import baggage, context

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Set tracer_id in baggage
    ctx = baggage.set_baggage(
        "honeyhive_tracer_id",
        tracer._tracer_id,
        context.get_current()
    )
    
    # Attach context
    token = context.attach(ctx)
    
    try:
        # User function unchanged
        outputs = function(datapoint)
    finally:
        # Detach context
        context.detach(token)

# Discovery already works via baggage!
def enrich_span(...):
    tracer = discover_tracer()  # Uses baggage
    if tracer:
        # Works!
```

**Pros:**
- ✅ Backward compatible
- ✅ Uses existing discovery mechanism
- ✅ OpenTelemetry standard pattern
- ✅ Already thread/async-safe
- ✅ No new infrastructure needed

**Cons:**
- ❌ Requires evaluate() to set up baggage
- ❌ Baggage designed for distributed tracing, not local state
- ❌ Slightly more complex setup

#### Solution 5: Decorator Parameter Injection

```python
# New decorator that discovers and injects tracer
from honeyhive import trace

@trace(event_type="chain", inject_tracer=True)  # ← New parameter
def user_function(datapoint, tracer=None):  # ← Optional tracer param
    if tracer:
        tracer.enrich_span(metadata={"step": "done"})
    return result

# Decorator implementation
def trace(event_type, inject_tracer=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = discover_tracer()
            
            if inject_tracer and tracer:
                # Inject tracer as keyword argument
                kwargs['tracer'] = tracer
            
            return func(*args, **kwargs)
```

**Pros:**
- ✅ Opt-in (backward compatible for those not using it)
- ✅ Explicit when needed
- ✅ Works with existing discovery

**Cons:**
- ❌ Requires user to update function signature
- ❌ Still needs working discovery mechanism
- ❌ More complex decorator logic

#### Solution 6: Global Default Tracer (Current Attempt - Flawed)

```python
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    set_default_tracer(tracer)  # Set as global default
    
    outputs = function(datapoint)

# Discovery falls back to default
def enrich_span(...):
    tracer = discover_tracer()  # Gets default
```

**Pros:**
- ✅ Backward compatible
- ✅ Simple implementation

**Cons:**
- ❌ RACE CONDITION: Multiple threads overwrite default
- ❌ Non-deterministic (last thread wins)
- ❌ Not actually thread-safe
- ❌ Breaks multi-instance isolation

### Recommendation Matrix

| Solution | Backward Compat | Thread-Safe | Explicit | Complexity | Recommendation |
|----------|----------------|-------------|----------|------------|----------------|
| 1. Explicit Parameter | ❌ | ✅ | ✅ | Low | **Best long-term** |
| 2. Thread-Local | ✅ | ✅ | ❌ | Medium | Good transition |
| 3. Context Variables | ✅ | ✅ | ❌ | Medium | Good transition |
| 4. Baggage Context | ✅ | ✅ | ❌ | Medium | **Best OTel-native** |
| 5. Decorator Injection | Partial | ✅ | Partial | High | Skip |
| 6. Global Default | ✅ | ❌ | ❌ | Low | **Never use** |

### Recommended Approach: Two-Phase Migration

#### Phase 1: Fix Immediately with Baggage (v0.2.0)

```python
# In experiments/core.py
from opentelemetry import baggage, context

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Set up baggage context
    ctx = baggage.set_baggage(
        "honeyhive_tracer_id",
        tracer._tracer_id,
        context.get_current()
    )
    token = context.attach(ctx)
    
    try:
        outputs = function(datapoint)
    finally:
        context.detach(token)
        force_flush_tracer(tracer)
```

**Result:**
- ✅ Works immediately
- ✅ No user code changes
- ✅ Uses existing discovery
- ✅ Thread-safe
- ✅ OTel standard pattern

#### Phase 2: Migrate to Instance Method (v1.0.0)

```python
# Add instance method
class HoneyHiveTracer:
    def enrich_span(self, metadata=None, metrics=None, ...):
        """Instance method for explicit tracer access"""
        current_span = trace.get_current_span()
        _set_span_attributes(current_span, "honeyhive_metadata", metadata)
        # ...

# Update evaluate() to pass tracer
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # New pattern: pass tracer explicitly
    outputs = function(datapoint, tracer=tracer)

# User code update (breaking change with migration guide)
def user_function(datapoint, tracer):  # Add tracer parameter
    result = process(datapoint)
    tracer.enrich_span(metadata={"done": True})  # Instance method
    return result
```

**Migration guide:**
```python
# OLD (v0.x - still works via baggage)
def my_function(datapoint):
    enrich_span(metadata={...})

# NEW (v1.0 - recommended)
def my_function(datapoint, tracer):
    tracer.enrich_span(metadata={...})
```

### Why This Approach Works

**Phase 1 (Baggage) solves:**
- ✅ Immediate fix for evaluate() pattern
- ✅ No breaking changes
- ✅ Uses OTel standard patterns
- ✅ Thread-safe

**Phase 2 (Instance Method) provides:**
- ✅ Clean, explicit API
- ✅ Type-safe
- ✅ Better IDE support
- ✅ Aligns with multi-instance architecture

**Both phases:**
- ✅ Maintain backward compatibility at each stage
- ✅ Clear migration path
- ✅ Proper deprecation cycle

---

## Next Steps

### Immediate (v0.2.0 - Bugfix)
1. ✅ Implement baggage context setup in `process_datapoint()`
2. ✅ Verify discovery works via baggage
3. ✅ Test with existing evaluate() usage
4. ✅ No user code changes required

### Near-term (v0.3.0 - Enhancement)
1. Add `HoneyHiveTracer.enrich_span()` instance method
2. Keep free function working via discovery
3. Document both patterns
4. Recommend instance method in examples

### Long-term (v1.0.0 - Breaking Change)
1. Deprecate free function `enrich_span()`
2. Update `evaluate()` to pass tracer parameter
3. Provide migration guide
4. Require explicit tracer in user functions
5. Remove deprecated free function in v2.0.0
