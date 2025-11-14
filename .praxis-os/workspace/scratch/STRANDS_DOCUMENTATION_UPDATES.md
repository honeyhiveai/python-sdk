# AWS Strands Documentation Updates

**Date:** October 29, 2025  
**Status:** Updated with critical clarifications

## Key Updates Made

### 1. ✅ Clarified: NO Instrumentor Needed

**Added prominent section** explaining that AWS Strands has **built-in OpenTelemetry tracing**:

```
Unlike OpenAI or Anthropic (which require instrumentors like OpenInference 
or Traceloop), AWS Strands has built-in OpenTelemetry tracing. This means:

✅ NO instrumentor needed - Strands instruments its own LLM calls
✅ Built-in GenAI conventions - All model calls automatically traced
❌ Don't use OpenInference/Traceloop - Would create duplicate spans
```

**Why This Matters:**
- Strands creates LLM clients (OpenAI, Anthropic, Bedrock) internally
- Instrumentors hook client creation but can't catch Strands' internal clients
- Using instrumentors would create duplicate spans
- Strands already wraps all LLM calls with OpenTelemetry spans

### 2. ✅ Updated Example References

**Changed from:**
- Multiple references to `scripts/verify_strands_staging.py`
- References to `nw_test.py`

**Changed to:**
- Single reference to `examples/integrations/strands_integration.py`
- Clear note that this is the only example committed to the repo

**Examples section now says:**

```rst
Complete Example
----------------

A comprehensive example is available in the repository:

**`examples/integrations/strands_integration.py`** - Full integration demo with 8 test cases:

- Basic agent invocation
- Tool execution with calculator
- Streaming responses
- Custom trace attributes
- Structured outputs with Pydantic
- Swarm multi-agent collaboration
- Graph workflows with parallel processing
- All patterns shown in this guide
```

### 3. ✅ Added Troubleshooting for Duplicate Spans

**New troubleshooting entry:**

```rst
**Issue: "Duplicate spans in HoneyHive"**

This happens if you accidentally enable LLM instrumentors:

# ❌ DON'T DO THIS - Strands has built-in tracing
from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument()  # Will create duplicate spans!

# ✅ DO THIS - Just use TracerProvider pattern
from honeyhive import HoneyHiveTracer
from opentelemetry import trace as trace_api

tracer = HoneyHiveTracer.init(...)
trace_api.set_tracer_provider(tracer.provider)
# That's it - Strands handles the rest!
```

### 4. ✅ Enhanced Best Practices

**Added new best practice #2:**

```rst
2. **Don't Use LLM Instrumentors**

   AWS Strands has built-in tracing - don't add instrumentors:
   
   # ❌ DON'T DO THIS
   from openinference.instrumentation.openai import OpenAIInstrumentor
   OpenAIInstrumentor().instrument()  # Creates duplicate spans!
   
   # ✅ DO THIS - Strands instruments itself
   tracer = HoneyHiveTracer.init(...)
   trace_api.set_tracer_provider(tracer.provider)
   # Strands' built-in tracing handles everything
```

## Integration Pattern Clarification

### How Strands Tracing Works

```
┌─────────────────────────────────────┐
│  HoneyHive provides TracerProvider   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Set as global OTel provider         │
│  trace_api.set_tracer_provider()     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Strands Agent created               │
│  (gets global TracerProvider)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Strands' BUILT-IN tracing active    │
│  - Instruments its own LLM calls     │
│  - Adds GenAI semantic conventions   │
│  - Traces tools, agents, cycles      │
└─────────────────────────────────────┘
```

**Key Point:** No instrumentor layer needed because Strands does the instrumentation itself!

## What This Means for Users

### ✅ DO:
1. Initialize HoneyHive tracer
2. Set it as global TracerProvider
3. Create Strands agents
4. Everything is traced automatically

### ❌ DON'T:
1. Use OpenInference instrumentors
2. Use Traceloop instrumentors
3. Try to hook OpenAI/Anthropic clients
4. Worry about provider-specific instrumentation

## Technical Accuracy

Based on analysis of `integrations-analysis/AWS_STRANDS_SDK_ANALYSIS.md`:

```
**Observability:** ✅ Built-in OpenTelemetry with comprehensive GenAI semantic conventions

**Recommendation:** STANDARD OTEL INTEGRATION (Low-Medium Effort)
- Strands respects global TracerProvider via trace_api.get_tracer_provider()
- HoneyHive can provide TracerProvider and automatically capture ALL agent traces
- Agent-specific context already captured via GenAI semantic conventions
- NO custom instrumentor needed - standard OTel integration pattern

**Key Insight:** Model providers are abstracted - SDK users don't directly 
instantiate LLM clients. This means existing LLM instrumentors may not 
capture calls unless Strands-specific hooks are used.

**Implication:** Existing OpenAI/Anthropic instrumentors will NOT capture 
these calls because:
1. Clients are created inside Strands code
2. Instrumentors hook client creation, but Strands creates them dynamically
3. Strands wraps calls with its own spans anyway

**Solution:** Don't try to instrument model providers - let Strands' 
built-in tracing handle it.
```

## Files Updated

1. **`docs/how-to/integrations/strands.rst`** - Main documentation
   - Added "Key Difference from Other Integrations" section
   - Updated Integration Approach section
   - Added duplicate spans troubleshooting
   - Added "Don't Use LLM Instrumentors" best practice
   - Updated example references to only point to `examples/integrations/`

2. **`AWS_STRANDS_DOCUMENTATION_SUMMARY.md`** - Summary document
   - Updated Technical Highlights section
   - Added "Key Difference from Other Integrations" section
   - Updated Related Files to only reference committed examples

## Why This Update Was Critical

**Problem:** Users might assume Strands needs instrumentors like OpenAI/Anthropic do

**Risk:**
- Users add OpenInference/Traceloop instrumentors
- Creates duplicate spans (Strands tracing + instrumentor tracing)
- Confusion about what's being traced
- Potential performance impact

**Solution:** Clear documentation that:
- Strands has built-in tracing
- No instrumentor needed
- Don't add instrumentors
- Just use TracerProvider pattern

## Documentation Quality

After these updates:

✅ **Accurate** - Reflects how Strands actually works  
✅ **Clear** - Prominent warnings about instrumentors  
✅ **Complete** - Covers the unique integration pattern  
✅ **User-Friendly** - Prevents common mistake  
✅ **Example-Focused** - Points to committed example only

---

**Status:** Ready for users with critical clarifications 🎯

