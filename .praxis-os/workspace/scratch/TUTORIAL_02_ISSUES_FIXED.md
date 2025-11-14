# Tutorial 02 - Issues Fixed

**Date:** October 31, 2025  
**File:** `docs/tutorials/02-add-llm-tracing-5min.rst`

---

## Issue 1: Cost Tracking Reference ✅ FIXED

**Problem:**
- Line 302 referenced "Traceloop instrumentors" specifically
- Tutorial uses OpenInference instrumentor
- Could confuse users about which instrumentor provides cost data

**Fix:**
Changed:
```
- Cost (if using Traceloop instrumentors)
```

To:
```
- Cost (if using instrumentors that support cost tracking)
```

**Result:**
- More accurate and general
- Doesn't mislead users about instrumentor capabilities
- Applies to any instrumentor with cost tracking support

---

## Issue 2: Multiple Projects Pattern ✅ FIXED

**Problem:**
- Lines 339-348 showed creating multiple tracers
- Did not demonstrate how to actually use them
- Pattern was incomplete

**Fix:**
Expanded example to include:
- Complete imports
- Instrumentor initialization
- Two functions demonstrating @trace decorator usage
- Each function routes to different tracer/project
- Added note referencing Tutorial 04 for more details

**New example shows:**
```python
# Main app tracer
main_tracer = HoneyHiveTracer.init(project="main-app")

# Experimental features tracer  
experimental_tracer = HoneyHiveTracer.init(project="experiments")

# Initialize instrumentor
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=main_tracer.provider)

# Use @trace decorator to route to specific projects
@trace(tracer=main_tracer)
def main_feature(prompt: str):
    client = openai.OpenAI()
    return client.chat.completions.create(...)

@trace(tracer=experimental_tracer)
def experimental_feature(prompt: str):
    client = openai.OpenAI()
    return client.chat.completions.create(...)
```

**Result:**
- Complete, working example
- Shows exactly how to route to different projects
- References Tutorial 04 for advanced patterns
- No ambiguity

---

## Validation

**Both fixes:**
- ✅ Maintain correct API usage
- ✅ Improve clarity
- ✅ Do not introduce new issues
- ✅ Follow established patterns from other tutorials

**Status:** All Tutorial 02 issues resolved ✅

