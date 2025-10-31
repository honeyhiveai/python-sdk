# Framework Integration Pattern Analysis
## Pydantic AI, OpenAI Agents SDK, Semantic Kernel

**Date:** October 9, 2025  
**Analysis:** Integration patterns for three candidate "non-instrumentor frameworks"

---

## Summary of Findings

**❌ These frameworks DO NOT share a common integration pattern**  
**❌ They DO NOT fit the "non-instrumentor framework" pattern (like AWS Strands)**  
**✅ Each requires a completely different integration approach**

---

## Framework Analysis

### 1. Pydantic AI (github.com/pydantic/pydantic-ai)

**Tracing Architecture:**
- ✅ Uses OpenTelemetry
- ❌ Does NOT set up its own TracerProvider
- Uses `get_tracer_provider()` to get an existing provider
- Expects Logfire or user to configure the TracerProvider

**Integration Pattern:**
```python
from opentelemetry.trace import TracerProvider, get_tracer_provider

# In pydantic_ai/models/instrumented.py:
tracer_provider: TracerProvider | None = None
self.tracer_provider = tracer_provider or get_tracer_provider()
```

**HoneyHive Integration Approach:**
- User must initialize HoneyHive FIRST (sets up TracerProvider)
- Then Pydantic AI will use HoneyHive's TracerProvider automatically
- Alternative: Use with Logfire (which is OpenTelemetry-based)

**Category:** OpenTelemetry-compatible, TracerProvider Consumer

---

### 2. OpenAI Agents SDK (github.com/openai/openai-agents-python)

**Tracing Architecture:**
- ❌ Does NOT use OpenTelemetry
- Has a completely custom tracing system
- Custom `TraceProvider`, `Span`, `Trace` abstractions
- Custom `TracingProcessor` interface

**Integration Pattern:**
```python
# From agents/tracing/setup.py:
GLOBAL_TRACE_PROVIDER: TraceProvider | None = None

def set_trace_provider(provider: TraceProvider) -> None:
    global GLOBAL_TRACE_PROVIDER
    GLOBAL_TRACE_PROVIDER = provider
```

**HoneyHive Integration Approach:**
- Would require a custom TracingProcessor implementation
- Need to bridge between OpenAI Agents' custom tracing and HoneyHive
- Completely different from OpenTelemetry-based integrations

**Category:** Custom Tracing System (Non-OpenTelemetry)

---

### 3. Semantic Kernel (github.com/microsoft/semantic-kernel)

**Tracing Architecture:**
- ✅ Uses OpenTelemetry
- ❌ Does NOT set up its own TracerProvider automatically
- Uses `get_tracer_provider()` or accepts optional TracerProvider parameter
- Falls back to `NoOpTracerProvider()` if none available
- User examples show explicitly calling `set_tracer_provider()`

**Integration Pattern:**
```python
# From semantic_kernel/agents/runtime/core/telemetry/tracing.py:
def __init__(self, tracer_provider: TracerProvider | None, ...):
    self.tracer_provider = tracer_provider or get_tracer_provider() or NoOpTracerProvider()
    
# From samples - USER sets up the provider:
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider

tracer_provider = TracerProvider(resource=resource)
set_tracer_provider(tracer_provider)
```

**HoneyHive Integration Approach:**
- User must initialize HoneyHive FIRST (sets up TracerProvider)
- Then Semantic Kernel will use HoneyHive's TracerProvider automatically
- OR: Pass HoneyHive's provider explicitly to Semantic Kernel runtime

**Category:** OpenTelemetry-compatible, Optional TracerProvider Consumer

---

## Comparison with AWS Strands ("Non-Instrumentor Framework")

**AWS Strands Pattern:**
- ✅ Uses OpenTelemetry directly
- ✅ Sets up its own TracerProvider
- ✅ Requires careful initialization order with HoneyHive
- ✅ HoneyHive detects and integrates with Strands' provider

**Why these frameworks DON'T match:**
- **Pydantic AI**: Doesn't set up TracerProvider, expects external setup
- **OpenAI Agents SDK**: Doesn't use OpenTelemetry at all
- **Semantic Kernel**: Doesn't set up TracerProvider, expects user setup

---

## Documentation Recommendation

### ❌ DO NOT create a unified template generator

**Reasons:**
1. Each framework has a completely different integration pattern
2. Only 1 out of 3 uses OpenTelemetry exclusively
3. Integration approaches vary significantly
4. No common "TracerProvider self-setup" pattern like Strands

### ✅ CREATE individual documentation pages

**Approach:**
1. Create separate `.rst` files for each framework
2. Document each framework's unique integration approach
3. Group them in docs under "how-to/integrations/frameworks/"
4. Each gets custom examples and integration tests

**Proposed Structure:**
```
docs/how-to/integrations/
├── frameworks/
│   ├── pydantic-ai.rst      # OpenTelemetry-based integration
│   ├── openai-agents.rst    # Custom tracing bridge
│   └── semantic-kernel.rst  # OpenTelemetry-based integration
```

---

## Next Steps

1. ✅ Analysis complete - frameworks don't share common patterns
2. 📝 Create individual documentation pages (3 separate files)
3. 🔧 Create framework-specific examples (3 separate examples)
4. ✅ Create integration tests (3 separate test files)
5. 📚 Update navigation to link to new framework docs

---

## Key Insight

**The "non-instrumentor-frameworks.rst" pattern only applies to frameworks like AWS Strands that:**
1. Use OpenTelemetry directly
2. Set up their own TracerProvider
3. Create manual spans

**These three frameworks require different documentation approaches:**
- **Pydantic AI & Semantic Kernel:** "OpenTelemetry-Compatible Frameworks" guide
- **OpenAI Agents SDK:** "Custom Tracing Integration" guide

They are NOT "non-instrumentor frameworks" in the AWS Strands sense.

