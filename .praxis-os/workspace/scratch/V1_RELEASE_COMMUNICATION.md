# HoneyHive Python SDK v1.0 Release Communication

**Date**: October 31, 2025  
**Version**: v1.0 (complete-refactor → production)  
**Type**: Major release with breaking changes

---

## 🎯 TL;DR: What Users Need to Know

### For Simple Use Cases (90% of users)
**✅ Your code will work unchanged.**
```python
# This still works exactly as before:
from honeyhive import HoneyHiveTracer, trace

HoneyHiveTracer.init(api_key="...", project="...")

@trace()
def my_function():
    return "result"
```

### For evaluate() Users (10% of users)
**⚠️ You need to add one parameter.**
```python
# OLD (main branch):
def evaluation_function(datapoint):
    return {"output": process(datapoint)}

# NEW (v1.0):
def evaluation_function(datapoint, tracer):  # ← Add tracer parameter
    tracer.enrich_span(metadata={"key": "value"})  # Now works!
    return {"output": process(datapoint)}
```

**Why?** Main branch evaluate() was fundamentally broken (session ID contamination, thread collisions). v1.0 fixes it properly, but requires this small API change.

---

## 🚀 What's New in v1.0

### Complete Rewrite Using Direct OpenTelemetry
- **Removed:** Traceloop wrapper
- **Added:** Direct OpenTelemetry integration
- **Benefit:** Full control, better performance, easier debugging

### Multi-Instance Tracer Architecture
- **Old:** One global tracer for entire application (singleton)
- **New:** Multiple independent tracer instances
- **Benefit:** Proper isolation for concurrent use cases (evaluate(), FastAPI, multi-tenant)

### Fixed: evaluate() Pattern
- **Old:** All datapoints shared one tracer → session ID contamination ❌
- **New:** Each datapoint gets isolated tracer → clean separation ✅
- **Impact:** evaluate() is now production-ready

### New Features
1. **Auto-track inputs:** `@trace` decorator automatically captures function arguments
2. **Meaningful session names:** Evaluation sessions use experiment name
3. **Ground truth tracking:** Fixed ground truth storage in session feedback
4. **Tracer parameter:** Pass tracer to evaluation functions for enrich_span/enrich_session

---

## ⚠️ Breaking Changes (Be Honest)

### 1. evaluate() Pattern Requires Tracer Parameter

**What changed:**
```python
# Main branch (worked but produced corrupted data):
def evaluation_function(datapoint):
    enrich_span(metadata={...})  # Found global singleton
    return {"output": "result"}

# v1.0 (produces correct data):
def evaluation_function(datapoint, tracer):  # ← New parameter
    tracer.enrich_span(metadata={...})  # Explicit instance method
    return {"output": "result"}
```

**Why necessary:**
- Main branch: ALL datapoints shared ONE tracer → session IDs mixed together
- v1.0: Each datapoint gets OWN tracer → proper isolation
- **Trade-off:** Small API change for correct, production-ready data

**Migration:**
1. Add `tracer` parameter to your evaluation function signature
2. Change `enrich_span(...)` → `tracer.enrich_span(...)`
3. Change `enrich_session(session_id, ...)` → `tracer.enrich_session(tracer.session_id, ...)`

### 2. Free Functions Deprecated (But Still Work)

**What changed:**
- `enrich_span()` free function → **DEPRECATED** (use `tracer.enrich_span()`)
- `enrich_session()` free function → **DEPRECATED** (use `tracer.enrich_session()`)

**Why necessary:**
- Free functions rely on global state (incompatible with multi-instance architecture)
- Instance methods are explicit and reliable

**Migration timeline:**
- v1.0: Free functions work (via tracer discovery) but deprecated
- v2.0: Free functions removed

**What to do:**
```python
# OLD (deprecated but works in v1.0):
enrich_span(metadata={"key": "value"})

# NEW (recommended):
tracer.enrich_span(metadata={"key": "value"})
```

### 3. Instrumentor Routing in evaluate() (Known Limitation)

**What doesn't work yet:**
```python
# In evaluate() with Strands/OpenAI auto-instrumentors:
def evaluation_function(datapoint):
    from strands import Agent
    agent = Agent(...)  # Strands spans may route to first session
    result = agent.run(prompt)
    return {"output": result}
```

**Why:**
- Third-party instrumentors (OpenAI, Anthropic, Strands) use global tracer provider
- Multi-instance architecture doesn't propagate to their instrumentation (yet)

**Workaround:**
```python
# Use manual @trace wrapping:
@trace(tracer=tracer, event_type="tool")
def call_strands_agent(prompt):
    from strands import Agent
    agent = Agent(...)
    return agent.run(prompt)

def evaluation_function(datapoint, tracer):
    result = call_strands_agent(datapoint["prompt"])
    return {"output": result}
```

**Timeline:** Will be fixed in v1.1 (2-3 days work)

---

## 🎯 Philosophy: Correctness Over Compatibility

### The Hard Truth

Main branch evaluate() **looked like it worked** but **produced corrupted data:**
- Session IDs mixed between datapoints
- Spans ended up in wrong sessions
- Thread collisions caused data loss
- **Result:** Silently incorrect telemetry

### The Choice We Made

**Option A:** Maintain 100% API compatibility
- ✅ Code doesn't error
- ❌ Data is **silently corrupted**
- ❌ Users unknowingly get bad telemetry

**Option B:** Accept breaking changes
- ⚠️ Code needs updates (tracer parameter)
- ✅ Data is **correct and isolated**
- ✅ Users get reliable telemetry

**We chose Option B: Functionality and correctness over 100% backward compatibility.**

### What We Did to Minimize Impact

1. **Tracer discovery mechanism:** Free functions work where possible
2. **Signature detection:** evaluate() auto-detects old vs new signature
3. **Backward compatibility layer:** Instance methods + free functions (deprecated)
4. **Comprehensive migration guide:** Clear before/after examples
5. **Honest documentation:** Explain why changes needed

---

## 📋 Migration Guide

### Simple Use Cases (No Changes Needed)

**If you're doing this, no action required:**
```python
# Single tracer initialization
HoneyHiveTracer.init(api_key="...", project="...")

# Basic @trace decorators
@trace()
def my_function():
    return "result"

# Direct instrumentor usage (non-evaluate)
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(...)
```

### evaluate() Use Cases (Changes Required)

**Step 1: Update evaluation function signature**
```python
# OLD:
def evaluation_function(datapoint):
    ...

# NEW:
def evaluation_function(datapoint, tracer):  # ← Add tracer
    ...
```

**Step 2: Update enrich_span calls**
```python
# OLD:
enrich_span(metadata={"key": "value"})

# NEW:
tracer.enrich_span(metadata={"key": "value"})
```

**Step 3: Update enrich_session calls**
```python
# OLD:
enrich_session(session_id, outputs={"result": result})

# NEW:
tracer.enrich_session(tracer.session_id, outputs={"result": result})
```

**Step 4: Test with small dataset**
```python
# Run evaluate with 3 datapoints to verify:
result = evaluate(
    function=evaluation_function,  # New signature
    dataset=[dp1, dp2, dp3],
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    name="test-migration"
)

# Verify in HoneyHive UI:
# - 3 separate sessions (not 1)
# - enrich_span metadata appears
# - Ground truth tracked
```

### Multi-Instance Use Cases (New Capability)

**You can now do this (impossible in main branch):**
```python
# Create multiple independent tracers:
tracer_prod = HoneyHiveTracer.init(
    api_key="prod_key",
    project="production",
    source="prod-app"
)

tracer_staging = HoneyHiveTracer.init(
    api_key="staging_key",
    project="staging",
    source="staging-app"
)

# Use different tracers in different contexts:
@trace(tracer=tracer_prod)
def prod_function():
    pass

@trace(tracer=tracer_staging)
def staging_function():
    pass
```

---

## 🆘 Getting Help

### Common Issues

**Issue:** "enrich_span() not working in evaluate()"
- **Cause:** Using free function without tracer parameter
- **Fix:** Add `tracer` parameter to evaluation function, use `tracer.enrich_span()`

**Issue:** "Strands/OpenAI spans in wrong session"
- **Cause:** Instrumentor routing limitation in v1.0
- **Fix:** Use manual `@trace` wrapping (workaround) or wait for v1.1

**Issue:** "Cannot find tracer"
- **Cause:** Tracer discovery failure in multi-instance scenario
- **Fix:** Pass explicit `tracer` parameter to functions

### Support Channels
- GitHub Issues: https://github.com/honeyhiveai/python-sdk/issues
- Documentation: https://honeyhiveai.github.io/python-sdk/
- Migration Guide: [link to migration guide]

---

## 📊 What Users Get in v1.0

### ✅ Benefits
1. **Correct evaluate() behavior:** No more session ID contamination
2. **Production-ready concurrency:** Thread-safe multi-instance support
3. **Auto-track inputs:** Function arguments automatically captured
4. **Better debugging:** Explicit tracer passing makes ownership clear
5. **Faster performance:** Direct OTel integration (no Traceloop overhead)

### ⚠️ Trade-offs
1. **evaluate() API change:** Need to add `tracer` parameter
2. **Free functions deprecated:** Use instance methods instead
3. **Instrumentor routing:** Known limitation (v1.1 fix coming)

### 🎯 Bottom Line
- ⚠️ Some code needs updates
- ✅ But the code **actually works correctly** after updates
- 🎯 **Correct data > unchanged API**

---

## 🗓️ Timeline

- **Oct 27, 2025:** Discovered baggage context issue breaking evaluate()
- **Oct 29, 2025:** Fixed multi-instance isolation bugs
- **Oct 30, 2025:** Finalized 5 immediate ship requirements
- **Oct 31, 2025:** **Ship v1.0 to production**
- **Nov 2025:** v1.1 with instrumentor routing fix (estimated)

---

## 🙏 Thank You

We know breaking changes are painful. We bent over backwards to minimize them while ensuring evaluate() works correctly. Thank you for understanding that **functionality and correctness** must come before **100% backward compatibility** for production-ready software.

If you have questions, concerns, or feedback, please reach out through our support channels. We're here to help you migrate successfully.

---

**Prepared**: October 30, 2025  
**Ship Date**: October 31, 2025  
**Version**: v1.0  
**Philosophy**: Correctness over compatibility

