# v1.0 Release Context & Architecture

**Date**: October 30, 2025  
**Branch**: `complete-refactor` (RC3 → v1.0)  
**Ship Date**: October 31, 2025 (tomorrow)  
**Type**: **COMPLETE REWRITE** from ground up

---

## 🎯 What is complete-refactor?

The `complete-refactor` branch is **NOT an incremental update**. It is a:

### ✅ Complete Rewrite
- **Removed ALL files** from the repository
- Started with empty repo
- Rebuilt SDK from scratch

### 📊 Analyzed Main Branch
- Studied original SDK (main branch) behaviors
- Understood expected public API
- Documented user expectations
- Identified pain points to fix

### 🏗️ New Architecture
**Main Branch (Original SDK):**
- Wrapped Traceloop SDK
- Heavy abstraction layers
- Singleton global instrumentor
- Magic global state
- Hard to debug
- Thread safety issues

**complete-refactor (v1.0):**
- ✅ **Direct OpenTelemetry** integration
- ✅ **Multi-instance tracer architecture** (proper isolation)
- ✅ **No Traceloop wrapper** (simpler, more maintainable)
- ✅ **Explicit over implicit** (clearer ownership)
- ✅ **Thread-safe by design** (context propagation)
- ✅ **Production-ready** (better error handling, logging)

---

## 🎭 Backward Compatibility Strategy (Realistic Approach)

### What "Backward Compatible" ACTUALLY Means

**Target**: Original SDK on **main branch**

**Goal**: **Maximize compatibility while prioritizing correctness**

**Reality Check:** 
> "We bent over backwards to maintain compatibility, but the singleton → multi-instance architecture change means there WILL be breaking changes, especially for evaluate(). **Functionality and correctness > 100% backward compatibility.**"

**What Works Unchanged:**
- ✅ Simple single-tracer applications
- ✅ Basic `HoneyHiveTracer.init()` + `@trace` decorators
- ✅ Direct OpenAI/Anthropic instrumentor usage (non-evaluate)
- ✅ Session and event APIs

**What Requires Changes:**
- ⚠️ **evaluate() pattern:** Evaluation functions need `tracer` parameter
- ⚠️ **Free functions:** `enrich_span()`, `enrich_session()` unreliable in multi-instance
- ⚠️ **Concurrent patterns:** Multi-tracer scenarios behave differently (correctly)

**Approach**: Pragmatic, not purist
- ✅ Preserve main branch API **where possible**
- ⚠️ **Break compatibility where necessary** for correctness
- ✅ Provide clear migration guide
- ✅ Document breaking changes explicitly
- 🎯 **Priority: Production-ready evaluate() over 100% compatibility**

### Examples

#### evaluate() Function
```python
# MAIN BRANCH pattern - works unchanged in v1.0
def evaluation_function(datapoint):
    return {"output": process(datapoint["inputs"])}

result = evaluate(
    function=evaluation_function,
    dataset=[...],
    api_key="...",
    project="..."
)
# ✅ Works identically in v1.0

# v1.0 NEW pattern - unlocks new features
def evaluation_function_v1(datapoint, tracer):  # Optional tracer param
    tracer.enrich_span(metadata={"custom": "value"})
    return {"output": process(datapoint["inputs"])}

result = evaluate(
    function=evaluation_function_v1,  # v1.0 detects signature
    dataset=[...],
    api_key="...",
    project="..."
)
# ✅ New features work, main branch code still works
```

#### @trace Decorator
```python
# MAIN BRANCH pattern - works unchanged in v1.0
@trace(event_type="tool")
def my_function(arg1, arg2):
    return process(arg1, arg2)
# ✅ Works identically in v1.0

# v1.0 ENHANCEMENT - auto-captures inputs
@trace(event_type="tool")  # No code changes needed!
def my_function(arg1, arg2):
    return process(arg1, arg2)
# ✅ In v1.0: automatically adds honeyhive_inputs.arg1, honeyhive_inputs.arg2
# ✅ Main branch: would need manual enrich_span() call
```

---

## 🚀 Why Rewrite? The Multi-Instance Architecture Journey

### 📊 Main Branch SDK: The Problems

#### 1. **Traceloop Dependency Hell**
- Heavy abstraction overhead from Traceloop wrapper
- Limited control over OpenTelemetry tracing primitives
- Hard to debug issues (multiple layers of indirection)
- Version coupling to Traceloop SDK releases
- Difficult to add custom instrumentation

#### 2. **Singleton Architecture: The Core Problem**
**Why this broke evaluate():**
- ✅ Main branch: ONE global tracer for entire application
- ❌ Need: MULTIPLE independent tracers for each evaluation datapoint
- ❌ Result: Session ID contamination, thread collisions, context leaks

**Specific issues:**
```python
# Main branch pattern (singleton):
HoneyHiveTracer.init(...)  # Global singleton
evaluate(function=eval_fn, dataset=[...])  # ALL datapoints share ONE tracer
# Result: Session IDs mixed, spans cross-contaminate, thread collisions

# What we NEEDED (multi-instance):
# Thread 1: tracer_1 for datapoint_1 → session_1
# Thread 2: tracer_2 for datapoint_2 → session_2
# Thread 3: tracer_3 for datapoint_3 → session_3
# Result: Clean isolation, no contamination
```

#### 3. **Magic Behavior (Global State)**
- Implicit global instrumentor auto-created spans
- Hard to understand span ownership (who created this span?)
- Difficult to reason about multi-threaded behavior
- Surprising side effects from global state mutations
- No way to have different configs for different contexts

#### 4. **Production Issues**
- 🐛 Memory leaks in long-running processes (global state never freed)
- 🐛 Thread collisions in concurrent scenarios (evaluate(), FastAPI apps)
- 🐛 Session ID contamination (spans ending up in wrong sessions)
- 🐛 Hard to debug with verbose logs (global state makes stack traces confusing)
- 🐛 Context propagation failures (baggage not properly isolated)

### 💡 The Multi-Instance Architecture Solution

**Core Design Principle:**
> **Explicit over Implicit. Isolation over Shared State.**

#### What Changed:

**Main Branch (Singleton):**
```python
# Implicit global tracer
HoneyHiveTracer.init(api_key="...", project="...")  # Sets GLOBAL singleton

# Anywhere in code:
@trace()  # Uses global singleton automatically
def my_function():
    enrich_span(...)  # Finds global singleton

# Problem: What if you need DIFFERENT tracers for different contexts?
# Answer: You can't. Singleton = one tracer for entire app.
```

**v1.0 (Multi-Instance):**
```python
# Explicit tracer instances
tracer_1 = HoneyHiveTracer.init(api_key="...", project="proj1")
tracer_2 = HoneyHiveTracer.init(api_key="...", project="proj2")

# Explicit instance usage:
@trace(tracer=tracer_1)  # Uses tracer_1
def function_1():
    tracer_1.enrich_span(...)  # Explicit instance method

@trace(tracer=tracer_2)  # Uses tracer_2
def function_2():
    tracer_2.enrich_span(...)  # Explicit instance method

# Benefit: Full control, clean isolation, no conflicts
```

#### Why This Was Essential for evaluate():

**The evaluate() Use Case:**
```python
# evaluate() runs 100 datapoints concurrently in ThreadPoolExecutor
evaluate(
    function=eval_fn,
    dataset=[...],  # 100 datapoints
    max_workers=10   # 10 threads
)

# Need: Each datapoint gets its OWN tracer with its OWN session_id
# Thread 1: tracer_1 → session_1 → datapoint_1 spans
# Thread 2: tracer_2 → session_2 → datapoint_2 spans
# ...
# Thread 10: tracer_10 → session_10 → datapoint_10 spans

# Main branch (singleton): IMPOSSIBLE ❌
# - All threads share ONE tracer
# - All spans end up in ONE session (or random sessions)
# - Session IDs leak between threads
# - Thread-unsafe attribute mutations

# v1.0 (multi-instance): POSSIBLE ✅
# - Each thread creates its OWN tracer
# - Each tracer has its OWN session_id
# - Clean isolation, no leakage
# - Thread-safe by design
```

### 🔥 Breaking Changes We Discovered

#### 1. **enrich_span() / enrich_session() Free Functions Broken**

**Main Branch:**
```python
def evaluation_function(datapoint):
    # Works because global singleton exists
    enrich_span(metadata={"key": "value"})  # Finds global singleton
    enrich_session(session_id, outputs={...})  # Uses global singleton
```

**v1.0 Multi-Instance:**
```python
# Process datapoint in thread:
def process_datapoint(datapoint):
    tracer = HoneyHiveTracer.init(...)  # Thread-local tracer
    
    def evaluation_function(datapoint):
        # ❌ BROKEN: enrich_span() can't find tracer!
        # - No global singleton
        # - Baggage context not propagated (was disabled to prevent leaks)
        # - Free function has no tracer reference
        enrich_span(metadata={"key": "value"})  # FAILS: no tracer found
```

**Fix for v1.0:**
```python
# Option 1: Pass tracer explicitly (RECOMMENDED)
def evaluation_function(datapoint, tracer):  # ← NEW parameter
    tracer.enrich_span(metadata={"key": "value"})  # ✅ Works
    tracer.enrich_session(tracer.session_id, outputs={...})  # ✅ Works

# Option 2: Free functions with baggage discovery (BACKWARD COMPAT)
# - Re-enabled baggage propagation with selective keys
# - enrich_span() discovers tracer via baggage
# - Less reliable, deprecated in v2.0
```

#### 2. **@trace Decorator Needs Tracer Discovery**

**Main Branch:**
```python
@trace()  # Auto-discovers global singleton
def my_function():
    pass
```

**v1.0 Multi-Instance:**
```python
# Option 1: Explicit tracer (RECOMMENDED)
@trace(tracer=tracer_instance)
def my_function():
    pass

# Option 2: Auto-discovery (BACKWARD COMPAT)
@trace()  # Discovers via baggage or default tracer
def my_function():
    pass
# Works but less reliable in multi-instance scenarios
```

#### 3. **Instrumentor (OpenAI, Anthropic, Strands) Routing Broken**

**The Problem:**
```python
# evaluate() creates 3 tracers in ThreadPoolExecutor:
# Thread 1: tracer_1 (becomes global default via set_default_tracer())
# Thread 2: tracer_2 (isolated)
# Thread 3: tracer_3 (isolated)

# Inside evaluation_function:
from strands import Agent  # Strands has built-in OTEL

agent = Agent(...)  # Strands internally calls:
# - get_tracer_provider() → gets default provider
# - discover_tracer() → finds tracer_1 (the default)

# Result:
# ❌ ALL Strands spans from ALL threads → tracer_1.session_id
# ❌ Thread 2 Strands spans → tracer_1 (not tracer_2) ❌
# ❌ Thread 3 Strands spans → tracer_1 (not tracer_3) ❌
```

**Status:** **NOT FIXED IN v1.0** (deferred to v1.1)
- Complex multi-tracer instrumentation challenge
- Needs architectural changes to context propagation
- 2-3 days work estimate
- Documented as known limitation with workaround

### 📈 Evolution Timeline

**2024-01-XX: v0.1.0 (Main Branch)**
- Singleton architecture
- Traceloop wrapper
- Global state everywhere
- Works for simple use cases
- Breaks for evaluate(), concurrent apps

**2025-09-11: v0.1.0rc1 (Complete Refactor Begins)**
- Zero failing tests policy
- Documentation overhaul
- Testing infrastructure improvements
- Started identifying architecture issues

**2025-09-03 - 2025-09-05: v0.1.0rc2 Phase**
- Multi-instance architecture implementation
- Automatic tracer discovery system
- Backward compatibility layer
- Lambda compatibility testing
- Performance optimization

**2025-10-27: Baggage Context Crisis**
- Discovered: `context.attach()` disabled → broke evaluate()
- Root cause: Session ID conflicts in multi-instance
- Fix: Selective baggage propagation with safe keys
- Issue: project/source leaked between instances

**2025-10-29: Multi-Instance Isolation Fix**
- Removed project/source from SAFE_PROPAGATION_KEYS
- Modified span processor to prioritize tracer instance values
- Fixed context isolation in multi-instance scenarios

**2025-10-30: v1.0 RC3 → Production (TOMORROW)**
- 5 immediate ship requirements identified
- Strands integration issue deferred to v1.1
- Backward compatibility maintained
- Breaking changes documented
- Migration guide complete

### Benefits of v1.0 (complete-refactor)

1. **Direct OpenTelemetry**
   - Full control over tracing
   - Standard OTel patterns
   - Better debugging
   - Industry standard

2. **Multi-Instance Architecture**
   - Proper tracer isolation
   - No shared state
   - Thread-safe by design
   - Evaluation pattern works correctly

3. **Explicit Design**
   - Clear ownership (pass tracer explicitly)
   - Predictable behavior
   - Easy to reason about
   - No magic surprises

4. **Production Ready**
   - Better error handling
   - Comprehensive logging
   - Memory efficient
   - Handles edge cases

---

## 📦 Release Strategy

### Version Numbers
- **Main Branch**: v0.x.x (legacy, deprecated after v1.0)
- **complete-refactor**: 
  - RC1, RC2, RC3 (internal testing)
  - **v1.0** (production release tomorrow)

### Migration Path

**For existing users (main branch SDK):**
1. No code changes required for basic usage
2. Opt-in to new features by:
   - Adding `tracer` parameter to evaluation functions
   - Using new instance methods (tracer.enrich_span)
   - Leveraging auto-input capture in @trace

**For new users:**
- Start directly with v1.0 patterns
- Use recommended patterns from docs
- Get best performance and features

### Documentation Updates

**Must update:**
- ✅ Migration guide (main branch → v1.0)
- ✅ Evaluation pattern docs (show both patterns)
- ✅ Architecture docs (explain multi-instance)
- ✅ Troubleshooting (new patterns, new issues)
- ✅ Known limitations (instrumentor routing)

**Highlight:**
- Complete rewrite using direct OTel
- Better architecture
- Backward compatible API
- New opt-in features

---

## 🎯 v1.0 Scope (Shipping Tomorrow)

### ✅ Shipping (5 items)
1. Change default session name to experiment name
2. Pass tracer reference to evaluation function (with backward compat)
3. Set ground_truth on session feedback
4. Auto-track function inputs in @trace decorator
5. Verify session_id linking works

### ❌ NOT Shipping (Defer)
- Instrumentor (Strands/OpenAI) session routing in evaluate()
  - Complex multi-tracer instrumentation challenge
  - Needs architectural changes
  - 2-3 days work estimate
  - Ship in v1.1

### 📝 Document as Known Limitation
- Instrumentor traces in evaluate() may route to first session
- Workaround: Use manual @trace wrapping instead of auto-instrumentors
- Fix coming in v1.1

---

## 🧪 Testing Strategy

### Backward Compatibility Tests

**CRITICAL**: Test against main branch behavior

```python
# Test suite should verify:

def test_main_branch_evaluate_pattern_works():
    """Verify main branch evaluate() pattern works unchanged."""
    # EXACTLY as main branch users write it
    def evaluation_function(datapoint):
        return {"output": process(datapoint["inputs"])}
    
    result = evaluate(function=evaluation_function, dataset=[...], ...)
    assert result is not None
    # ✅ Should work identically to main branch

def test_v1_evaluate_pattern_with_tracer():
    """Verify v1.0 new pattern works."""
    def evaluation_function(datapoint, tracer):
        tracer.enrich_span(metadata={"test": "value"})
        return {"output": "test"}
    
    result = evaluate(function=evaluation_function, dataset=[...], ...)
    assert result is not None
    # ✅ Should work with new features

def test_trace_decorator_main_branch_compatible():
    """Verify @trace works as main branch expects."""
    @trace(event_type="tool")
    def my_function(arg):
        return arg
    
    result = my_function("test")
    assert result == "test"
    # ✅ Should work identically to main branch
```

### Regression Tests
- All main branch examples should work
- All main branch integration tests should pass
- No breaking changes in public API

### New Feature Tests
- Tracer parameter in evaluate()
- Auto-input capture in @trace
- Ground truth in feedback
- Session name uses experiment name

---

## 🎯 Philosophy: Correctness Over Compatibility

### Why We Accept Breaking Changes

**The Decision:**
> "For the most part old SDK code will work unchanged, but due to the singleton to multi-instance arch changes there will be some breakage. We have bent over backwards to make this happen, but the eval use case especially, we need to focus on **functionality and correctness over 100% backwards compatibility.**"

### The Rationale

**Main Branch evaluate() Was Fundamentally Broken:**
```python
# This code in main branch LOOKS like it works:
evaluate(function=eval_fn, dataset=[...])

# But internally:
# - All datapoints share ONE tracer ❌
# - Session IDs contaminate each other ❌
# - Thread collisions in ThreadPoolExecutor ❌
# - Spans end up in random sessions ❌
# - RESULT: Data is corrupted, unusable
```

**Maintaining "backward compatibility" would mean:**
- ✅ Code doesn't error (looks like it works)
- ❌ But produces **incorrect, corrupted data**
- ❌ False sense of success
- ❌ Users unknowingly get bad telemetry

**Breaking compatibility to fix it means:**
- ⚠️ Code may need updates (tracer parameter)
- ✅ But produces **correct, isolated data**
- ✅ Clear error messages if tracer missing
- ✅ Users get reliable, production-ready telemetry

### What We Did to Minimize Impact

1. **Tracer discovery mechanism** (baggage + default tracer)
   - Free functions work where possible
   - Graceful degradation
   - Clear error messages when fails

2. **Signature detection in evaluate()**
   - Old signature: `def eval_fn(datapoint):` → works (limited features)
   - New signature: `def eval_fn(datapoint, tracer):` → works (full features)
   - Automatic detection via `inspect.signature()`

3. **Backward compatibility layer**
   - Instance methods (recommended) + free functions (deprecated but working)
   - Automatic default tracer for simple use cases
   - Registry system for tracer lookup

4. **Comprehensive migration guide**
   - Clear before/after examples
   - Explanation of why changes needed
   - Step-by-step migration path

### Trade-offs We Accept

| Aspect | v0.x (Main Branch) | v1.0 (Complete Refactor) |
|--------|-------------------|--------------------------|
| **evaluate() API** | ✅ Same signature | ⚠️ New optional parameter |
| **evaluate() Correctness** | ❌ **Broken** (data corruption) | ✅ **Fixed** (correct isolation) |
| **enrich_span() in eval** | ✅ Works (finds global) | ⚠️ Needs tracer reference |
| **enrich_session() in eval** | ❌ **Broken** (wrong session) | ✅ **Fixed** (correct session) |
| **Code updates needed** | ✅ None | ⚠️ Add `tracer` parameter |
| **Production readiness** | ❌ **Not production-ready** | ✅ **Production-ready** |

**Bottom Line:**
- ⚠️ Some code needs updates
- ✅ But the code **actually works correctly** after updates
- 🎯 **Correct data > unchanged API**

---

## 📊 Comparison: Main Branch vs v1.0

| Aspect | Main Branch (v0.x) | v1.0 (complete-refactor) |
|--------|-------------------|-------------------------|
| **Architecture** | Traceloop wrapper | Direct OpenTelemetry |
| **Tracer Pattern** | Singleton global | Multi-instance isolated |
| **State Management** | Global shared state | Context propagation |
| **evaluate() Pattern** | ❌ Broken (session contamination) | ✅ Fixed (proper isolation) |
| **Tracer Access** | Implicit global | Explicit parameter (breaking) |
| **Input Tracking** | Manual enrich_span | Auto-capture in @trace |
| **Thread Safety** | ❌ Issues with evaluate() | ✅ Safe by design |
| **Debugging** | Hard (magic behavior) | Easy (explicit) |
| **Production Ready** | ❌ Memory leaks, collisions | ✅ Solid, tested |
| **Instrumentor Integration** | Works (global) | ⚠️ Needs work (multi-instance) |
| **Backward Compatible** | N/A (baseline) | ⚠️ Mostly (breaking changes documented) |
| **Correctness** | ❌ Session ID contamination | ✅ Correct isolation |
| **Evaluate Use Case** | ❌ Fundamentally broken | ✅ Production-ready |

---

## 🎉 Success Criteria for v1.0

### Must Have (Shipping)
- ✅ **evaluate() WORKS CORRECTLY** with proper session isolation (breaking change accepted)
- ✅ Simple main branch code (single tracer + @trace) works unchanged
- ✅ New tracer parameter works in evaluate()
- ✅ Auto-input capture works in @trace
- ✅ Ground truth tracking works
- ✅ Session names meaningful
- ✅ **Breaking changes documented** with clear migration guide
- ✅ **Functionality > 100% compatibility** for evaluate() use case

### Known Limitations (Documented)
- ⚠️ Instrumentor routing in evaluate() - workaround documented
- ⚠️ Ships in v1.1

### Nice to Have (Future)
- 🔮 Instrumentor routing fixed (v1.1)
- 🔮 Context variable tracer discovery (v1.1)
- 🔮 More auto-capture options (v1.2)

---

**Prepared**: October 30, 2025  
**Review**: Team + Josh  
**Ship**: October 31, 2025 (v1.0)  
**Architecture**: Complete rewrite, backward compatible API

