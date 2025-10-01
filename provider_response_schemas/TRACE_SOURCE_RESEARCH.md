# Trace Source Serialization Research

**Purpose**: Document how different trace sources serialize LLM responses into span attributes

**Critical for DSL**: The DSL must extract from ALL these patterns, not just instrumentors!

---

## 🎯 **Trace Source Categories**

### 1. **Auto-Instrumentors** (OpenTelemetry-based)
Automatic instrumentation that intercepts SDK calls

- OpenLit
- Traceloop (OpenLLMetry)
- OpenInference (Arize)
- LangChain OpenTelemetry
- LlamaIndex OpenTelemetry

### 2. **Direct HoneyHive SDK** ⚠️ **CRITICAL**
Manual tracing using HoneyHive's API

- `@trace` decorator
- `tracer.start_span()` context manager  
- `span.enrich()` method
- `create_event()` method

### 3. **Non-Instrumentor Frameworks**
Frameworks that integrate with HoneyHive tracer

- **Strands**: AWS agent framework
- **Pydantic AI**: Type-safe AI framework
- **Semantic Kernel**: Microsoft's AI framework
- **LangGraph**: State machine for agents

---

## 📊 **Direct HoneyHive SDK Serialization (VALIDATED)**

### Pattern: `honeyhive_outputs.*` (Flattened)

**Code Location**: `src/honeyhive/tracer/instrumentation/decorators.py:77`

**How it works**:
```python
def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    """Recursively flatten nested dictionaries into dot-notation attributes."""
    if isinstance(value, dict):
        for key, val in value.items():
            _set_span_attributes(span, f"{prefix}.{key}", val)
    else:
        span.set_attribute(prefix, str(value))
```

**Example**:
```python
# User code
@trace(tracer=tracer)
def my_llm_call():
    response = openai.ChatCompletion.create(...)
    # Option 1: Pass raw response object
    return response  # Gets JSON serialized

# OR manually set outputs
@trace(tracer=tracer, outputs={"message": response.choices[0].message})
def my_llm_call():
    ...
```

**Resulting Span Attributes**:
```
honeyhive_outputs.result = "{\"id\": \"chatcmpl-123\", \"choices\": ...}"  (JSON string)

OR (if manually flattened):

honeyhive_outputs.message.role = "assistant"
honeyhive_outputs.message.content = "Hello!"
honeyhive_outputs.message.tool_calls.0.id = "call_abc"
honeyhive_outputs.message.tool_calls.0.type = "function"
honeyhive_outputs.message.tool_calls.0.function.name = "get_weather"
honeyhive_outputs.message.tool_calls.0.function.arguments = "{\"location\": \"SF\"}"
```

**DSL Implications**:
- ✅ Already handles flattened dot-notation (current DSL design)
- ⚠️ Needs to handle JSON string in `honeyhive_outputs.result`
- ⚠️ Users might manually flatten tool_calls OR pass nested objects

---

## 📊 **Pydantic AI Integration (PARTIAL VALIDATION)**

### Pattern: Manual `@trace` decorator usage

**Code Location**: `.agent-os/specs/2025-09-17-compatibility-matrix-enhancement/specs.md:260`

**How it works**:
```python
from honeyhive import trace, HoneyHiveTracer
from pydantic_ai import Agent

tracer = HoneyHiveTracer.init(api_key="...")

@trace(tracer=tracer, event_type="model", event_name="pydantic_ai_agent")
async def run_pydantic_agent(query: str) -> WeatherResponse:
    agent = Agent('openai:gpt-4', result_type=WeatherResponse)
    
    with tracer.start_span("pydantic_ai_run") as span:
        span.set_attribute("query", query)
        result = await agent.run(query)
        # User manually sets structured output
        span.set_attribute("validated_output", result.data.model_dump())
        return result.data
```

**Resulting Span Attributes**:
```
honeyhive_outputs.result = <WeatherResponse object>  (serialized to string)

OR (manual attributes):

validated_output = "{\"temperature\": 72.5, \"condition\": \"sunny\", ...}"  (JSON string)
```

**DSL Implications**:
- ⚠️ Pydantic models might be serialized as JSON strings
- ⚠️ Users have full control over attribute naming
- ❓ Does Pydantic AI have its own instrumentor? (TODO: Research)

---

## 📊 **Strands Integration (UNKNOWN - TODO)**

### Pattern: Unknown

**Research Needed**:
- [ ] Does Strands create spans automatically?
- [ ] What attributes does it set for LLM calls?
- [ ] Does it follow any semantic convention?
- [ ] How does it serialize agent responses?

**Research Method**:
1. Search HoneyHive codebase for Strands integration code
2. Search Strands documentation for HoneyHive integration
3. Run example Strands + HoneyHive code and capture spans
4. Document attribute patterns

---

## 📊 **Semantic Kernel Integration (UNKNOWN - TODO)**

### Pattern: Unknown

**Research Needed**:
- [ ] How does SK integrate with OpenTelemetry?
- [ ] Does it use standard semantic conventions?
- [ ] How are SK responses serialized?
- [ ] Does it require manual span creation?

**Research Method**:
1. Review Semantic Kernel OpenTelemetry documentation
2. Test SK with HoneyHive tracer
3. Capture and analyze span attributes
4. Document patterns

---

## 📊 **LangGraph Integration (UNKNOWN - TODO)**

### Pattern: Unknown (likely similar to LangChain)

**Research Needed**:
- [ ] Does LangGraph use LangChain's instrumentation?
- [ ] How are graph state transitions traced?
- [ ] Where are LLM responses stored in spans?

---

## 🎯 **Completeness Validation Strategy**

### Phase 5.3 Enhancement: Multi-Source Validation

For OpenAI chat completions, validate DSL extraction from:

#### ✅ **Validated Sources**
1. Direct HoneyHive SDK (`honeyhive_outputs.*` flattened)

#### ⏳ **TODO: Validate**
2. OpenLit instrumentor (`gen_ai.*` attributes)
3. Traceloop instrumentor (`gen_ai.*` + custom)
4. OpenInference instrumentor (`llm.*` attributes)
5. Pydantic AI (manual attributes + possible instrumentor)
6. Strands (unknown pattern)
7. Semantic Kernel (unknown pattern)
8. LangGraph (unknown pattern)

### Validation Method

For each source:
1. **Capture Real Span**: Run integration example, export span JSON
2. **Document Pattern**: List all attributes and their paths
3. **Test DSL Extraction**: Validate DSL extracts correctly
4. **Document Gaps**: Identify any missing transforms or navigation rules

---

## 🚨 **Critical Framework Gap**

The current **Provider Schema Extraction Framework** (Phases 0-7) focuses on:
- Provider API response schemas (OpenAI, Anthropic, etc.)
- Example collection
- JSON Schema creation

**Missing**: **Trace Source Validation Phase**

### Proposed Phase 8: Trace Source Validation

**Purpose**: Validate DSL works with real span data from all trace sources

**Tasks**:
1. Capture example spans from each source
2. Document attribute patterns
3. Test DSL extraction
4. Update navigation rules/transforms as needed
5. Create cross-source compatibility matrix

---

## 📋 **Action Items**

### Immediate (After Phase 5-7)
- [ ] Research Strands integration
- [ ] Research Semantic Kernel integration
- [ ] Research LangGraph integration
- [ ] Capture real instrumentor spans (OpenLit, Traceloop, OpenInference)

### Short-Term (Phase 8)
- [ ] Build span capture tool
- [ ] Document all attribute patterns
- [ ] Create cross-source validation tests
- [ ] Update DSL for any gaps

### Long-Term
- [ ] Add to framework as permanent Phase 8
- [ ] Automate span pattern validation
- [ ] Create instrumentor compatibility matrix

---

**Last Updated**: 2025-09-30  
**Status**: Initial research - Direct SDK pattern documented
