# OpenAI DSL Translation Implementation Plan

**Date**: 2025-09-30  
**Goal**: Get the precompiled DSL path properly translating OpenAI spans to HoneyHive events  
**Status**: Detailed Implementation Roadmap

---

## 🎯 Executive Summary

The current DSL configs for OpenAI are **incomplete**. They have basic field mappings but are missing critical advanced fields like `tool_calls`, `refusal`, `audio`, and proper array reconstruction from flattened attributes.

**Current State**: ~30% coverage (basic fields only)  
**Target State**: 100% coverage (all OpenAI response fields)  
**Estimated Effort**: 2-3 days

---

## 📊 Current DSL Config Analysis

### ✅ What EXISTS in Current Configs

**File**: `config/dsl/providers/openai/field_mappings.yaml`

| Section | Fields Mapped | Status |
|---------|---------------|--------|
| **inputs** | chat_history, prompt, system_message | ✅ Basic |
| **outputs** | response, completion, tool_calls, finish_reason | ⚠️ Partial |
| **config** | model, temperature, max_tokens, top_p, penalties | ✅ Good |
| **metadata** | provider, tokens, cost, latency, request_id | ✅ Good |

**File**: `config/dsl/providers/openai/navigation_rules.yaml`

| Instrumentor | Rules | Status |
|--------------|-------|--------|
| **OpenInference** | input_messages, output_messages, model, tokens | ✅ Good |
| **Traceloop** | model, prompt, completion, tokens | ✅ Good |
| **OpenLit** | model, messages, tokens, cost | ✅ Good |

**File**: `config/dsl/providers/openai/transforms.yaml`

| Transform | Status | Notes |
|-----------|--------|-------|
| extract_user_prompt | ✅ | Uses shared registry |
| extract_system_prompt | ✅ | Uses shared registry |
| extract_completion_text | ✅ | Uses shared registry |
| calculate_total_tokens | ✅ | Uses shared registry |

### ❌ What's MISSING

#### 1. **Tool Calls Extraction** (CRITICAL)

**Problem**: `tool_calls` field mapping exists but has no implementation

```yaml
# Current in field_mappings.yaml
outputs:
  tool_calls:
    source_rule: "extract_tool_calls"  # ❌ This rule doesn't exist!
    required: false
    description: "Function/tool call results"
```

**What's Missing**:
- No navigation rule named `extract_tool_calls`
- No transform configuration for tool call extraction
- No array reconstruction from flattened attributes like:
  - `gen_ai.completion.0.message.tool_calls.0.id`
  - `gen_ai.completion.0.message.tool_calls.0.function.name`
  - `gen_ai.completion.0.message.tool_calls.0.function.arguments`

#### 2. **Advanced OpenAI Fields** (HIGH PRIORITY)

**Missing from field_mappings.yaml**:
- `refusal` - Safety refusal messages
- `audio` - Audio response data
- `annotations` - Web search citations
- `function_call` - Legacy function calling
- `logprobs` - Token probabilities
- `system_fingerprint` - Response fingerprint

#### 3. **Flattened Array Reconstruction** (CRITICAL)

**Current Issue**: DSL doesn't handle flattened arrays

**Example**: Traceloop/OpenLit flatten arrays:
```
gen_ai.completion.0.message.role = "assistant"
gen_ai.completion.0.message.content = "Hello"
gen_ai.completion.0.message.tool_calls.0.id = "call_abc"
gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
gen_ai.completion.0.message.tool_calls.0.function.arguments = '{"location": "SF"}'
```

**Needed**: Reconstruct into:
```python
{
  "role": "assistant",
  "content": "Hello",
  "tool_calls": [
    {
      "id": "call_abc",
      "function": {
        "name": "get_weather",
        "arguments": '{"location": "SF"}'  # JSON string!
      }
    }
  ]
}
```

#### 4. **JSON String Preservation** (CRITICAL)

**Problem**: `arguments` must remain a JSON STRING, not be parsed to object

**Current Risk**: Transform might parse JSON string → object (wrong!)

**Required**: Ensure `arguments` stays as string for backend compatibility

---

## 🏗️ Implementation Phases

### Phase 1: Add Missing Navigation Rules (4 hours)

**File**: `config/dsl/providers/openai/navigation_rules.yaml`

#### 1.1 Add Tool Calls Extraction Rules

```yaml
# Add to navigation_rules section:

  # === Tool Calls Extraction (All Instrumentors) ===
  traceloop_tool_calls_flattened:
    source_pattern: "gen_ai.completion.0.message.tool_calls.*"
    extraction_method: "reconstruct_array"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract tool calls from flattened Traceloop attributes"
    
  openinference_tool_calls:
    source_field: "llm.output_messages.0.tool_calls"
    extraction_method: "direct_copy"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract tool calls from OpenInference"
    
  openlit_tool_calls_flattened:
    source_pattern: "gen_ai.completion.0.message.tool_calls.*"
    extraction_method: "reconstruct_array"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract tool calls from flattened OpenLit attributes"
```

#### 1.2 Add Advanced Field Rules

```yaml
  # === Advanced OpenAI Fields ===
  traceloop_refusal:
    source_field: "gen_ai.completion.0.message.refusal"
    extraction_method: "direct_copy"
    fallback_value: null
    validation: "string_or_null"
    description: "Extract refusal message from Traceloop"
    
  traceloop_audio:
    source_field: "gen_ai.completion.0.message.audio"
    extraction_method: "direct_copy"
    fallback_value: null
    validation: "object_or_null"
    description: "Extract audio response from Traceloop"
    
  traceloop_system_fingerprint:
    source_field: "gen_ai.openai.system_fingerprint"
    extraction_method: "direct_copy"
    fallback_value: null
    validation: "string_or_null"
    description: "Extract system fingerprint from Traceloop"
```

---

### Phase 2: Add Transform Configurations (3 hours)

**File**: `config/dsl/providers/openai/transforms.yaml`

#### 2.1 Add Tool Calls Transform

```yaml
  # === TOOL CALLS EXTRACTION ===
  extract_tool_calls:
    function_type: "array_reconstruction"
    implementation: "reconstruct_array_from_flattened"
    parameters:
      prefix: "gen_ai.completion.0.message.tool_calls"
      preserve_json_strings: ["arguments"]  # Keep arguments as JSON string!
    description: "Extract and reconstruct tool calls array from flattened attributes"
    
  extract_tool_calls_openinference:
    function_type: "array_extraction"
    implementation: "extract_nested_array"
    parameters:
      source_path: "llm.output_messages.0.tool_calls"
      preserve_json_strings: ["arguments"]
    description: "Extract tool calls from OpenInference structured format"
```

#### 2.2 Add Advanced Field Transforms

```yaml
  # === ADVANCED OPENAI FIELD EXTRACTION ===
  extract_refusal:
    function_type: "string_extraction"
    implementation: "extract_first_non_empty"
    parameters:
      source_fields:
        - "gen_ai.completion.0.message.refusal"
        - "llm.output_messages.0.refusal"
      fallback_value: null
    description: "Extract refusal message if present"
    
  extract_audio:
    function_type: "object_extraction"
    implementation: "extract_nested_object"
    parameters:
      source_fields:
        - "gen_ai.completion.0.message.audio"
        - "llm.output_messages.0.audio"
      fallback_value: null
    description: "Extract audio response object if present"
    
  extract_system_fingerprint:
    function_type: "string_extraction"
    implementation: "extract_first_non_empty"
    parameters:
      source_fields:
        - "gen_ai.openai.system_fingerprint"
        - "llm.system_fingerprint"
      fallback_value: null
    description: "Extract OpenAI system fingerprint"
```

---

### Phase 3: Update Field Mappings (2 hours)

**File**: `config/dsl/providers/openai/field_mappings.yaml`

#### 3.1 Fix Tool Calls Mapping

```yaml
# REPLACE existing tool_calls mapping with:
  outputs:
    # ... existing fields ...
    
    tool_calls:
      source_rule: "extract_tool_calls"  # Now this rule exists!
      required: false
      description: "Function/tool call results (reconstructed from flattened)"
```

#### 3.2 Add Advanced Output Fields

```yaml
    refusal:
      source_rule: "extract_refusal"
      required: false
      description: "Safety refusal message if model refused the request"
      
    audio:
      source_rule: "extract_audio"
      required: false
      description: "Audio response data (OpenAI audio preview models)"
      
    annotations:
      source_rule: "extract_annotations"
      required: false
      description: "Web search citations/annotations"
```

#### 3.3 Add Advanced Metadata Fields

```yaml
  metadata:
    # ... existing fields ...
    
    system_fingerprint:
      source_rule: "extract_system_fingerprint"
      required: false
      description: "OpenAI system fingerprint for debugging"
      
    response_model:
      source_rule: "extract_response_model"
      required: false
      description: "Actual model used for response (may differ from request)"
```

---

### Phase 4: Verify Transform Registry Functions (2 hours)

**File**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py`

#### 4.1 Check Required Functions Exist

```bash
# Verify these functions exist in transform_registry.py:
grep -A 10 "def reconstruct_array_from_flattened" transform_registry.py
grep -A 10 "def extract_nested_array" transform_registry.py
grep -A 10 "def extract_nested_object" transform_registry.py
grep -A 10 "def extract_first_non_empty" transform_registry.py
```

#### 4.2 If Missing, Add to Transform Registry

**Location**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py`

```python
# Add to TRANSFORM_REGISTRY if missing:

def reconstruct_array_from_flattened(
    data: Dict[str, Any],
    prefix: str,
    preserve_json_strings: Optional[List[str]] = None,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Reconstruct array of objects from flattened dot-notation attributes.
    
    Args:
        data: Flattened attributes dict
        prefix: Prefix pattern (e.g., "gen_ai.completion.0.message.tool_calls")
        preserve_json_strings: List of field names to keep as JSON strings
        
    Returns:
        List of reconstructed objects
    """
    import re
    
    preserve_json_strings = preserve_json_strings or []
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.(.+)$")
    indexed_data: Dict[int, Dict[str, Any]] = {}
    
    for key, value in data.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field_path = match.group(2)
            
            if index not in indexed_data:
                indexed_data[index] = {}
            
            # Check if this field should be preserved as JSON string
            field_name = field_path.split('.')[-1]
            if field_name in preserve_json_strings:
                # Ensure it's a JSON string, not an object
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                else:
                    value = str(value)
            
            # Set nested value
            _set_nested_value(indexed_data[index], field_path.split("."), value)
    
    if not indexed_data:
        return []
    
    max_index = max(indexed_data.keys())
    return [indexed_data.get(i, {}) for i in range(max_index + 1)]


def _set_nested_value(obj: Dict[str, Any], path: List[str], value: Any) -> None:
    """Set a nested value in a dictionary using a path list."""
    current = obj
    for part in path[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[path[-1]] = value


# Add to TRANSFORM_REGISTRY dict:
TRANSFORM_REGISTRY["reconstruct_array_from_flattened"] = reconstruct_array_from_flattened
```

---

### Phase 5: Recompile DSL Bundle (1 hour)

#### 5.1 Check Compiler Script

```bash
# Find the DSL compiler
find . -name "*compile*" -name "*.py" | grep -i dsl
```

#### 5.2 Run Compilation

```bash
# Run the DSL compiler to regenerate compiled_providers.pkl
python scripts/compile_dsl_providers.py  # Or wherever the compiler is

# OR if using development-aware loading (auto-recompile):
# The bundle_loader.py will auto-recompile if source files are newer
```

#### 5.3 Verify Bundle

```python
# Check the compiled bundle contains our new rules
import pickle

with open("src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl", "rb") as f:
    bundle = pickle.load(f)
    
    # Check OpenAI provider exists
    print("Providers:", list(bundle.keys()))
    
    # Check OpenAI has tool_calls extraction
    openai_config = bundle.get("openai", {})
    print("OpenAI field mappings:", openai_config.get("field_mappings", {}).get("outputs", {}).keys())
    print("OpenAI transforms:", openai_config.get("transforms", {}).keys())
```

---

### Phase 6: Integration Testing (4 hours)

#### 6.1 Create Test Span Attributes

**File**: `tests/integration/test_openai_dsl_translation.py`

```python
def test_openai_tool_calls_translation():
    """Test that tool calls are properly extracted and reconstructed."""
    
    # Simulate Traceloop flattened attributes
    span_attributes = {
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-4o",
        "gen_ai.completion.0.message.role": "assistant",
        "gen_ai.completion.0.message.content": None,
        "gen_ai.completion.0.message.tool_calls.0.id": "call_abc123",
        "gen_ai.completion.0.message.tool_calls.0.type": "function",
        "gen_ai.completion.0.message.tool_calls.0.function.name": "get_weather",
        "gen_ai.completion.0.message.tool_calls.0.function.arguments": '{"location": "San Francisco"}',  # JSON STRING
        "gen_ai.usage.prompt_tokens": 50,
        "gen_ai.usage.completion_tokens": 20,
    }
    
    # Process with Universal Engine
    from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor
    
    processor = UniversalSemanticConventionProcessor()
    result = processor.processor.process_span_attributes(span_attributes)
    
    # Verify outputs
    assert result["outputs"]["tool_calls"] == [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "San Francisco"}'  # Still a JSON STRING!
            }
        }
    ]
    
    # Verify arguments is a STRING, not object
    assert isinstance(result["outputs"]["tool_calls"][0]["function"]["arguments"], str)
```

#### 6.2 Test Advanced Fields

```python
def test_openai_refusal_translation():
    """Test that refusal messages are extracted."""
    
    span_attributes = {
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-4o",
        "gen_ai.completion.0.message.role": "assistant",
        "gen_ai.completion.0.message.content": None,
        "gen_ai.completion.0.message.refusal": "I cannot help with that request due to safety guidelines.",
    }
    
    processor = UniversalSemanticConventionProcessor()
    result = processor.processor.process_span_attributes(span_attributes)
    
    assert result["outputs"]["refusal"] == "I cannot help with that request due to safety guidelines."


def test_openai_audio_translation():
    """Test that audio responses are extracted."""
    
    span_attributes = {
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-4o-audio-preview",
        "gen_ai.completion.0.message.role": "assistant",
        "gen_ai.completion.0.message.content": "Hello!",
        "gen_ai.completion.0.message.audio.id": "audio_abc123",
        "gen_ai.completion.0.message.audio.data": "base64encodeddata...",
        "gen_ai.completion.0.message.audio.transcript": "Hello!",
    }
    
    processor = UniversalSemanticConventionProcessor()
    result = processor.processor.process_span_attributes(span_attributes)
    
    assert "audio" in result["outputs"]
    assert result["outputs"]["audio"]["id"] == "audio_abc123"
```

#### 6.3 End-to-End Test with Real Spans

```python
def test_openai_e2e_with_honeyhive_sdk():
    """Test complete flow: SDK → DSL → Backend-ready attributes."""
    
    from honeyhive import HoneyHiveTracer
    from opentelemetry.trace import Span
    
    # Initialize tracer
    tracer = HoneyHiveTracer(
        api_key="test_key",
        project="test_project",
        session_name="dsl_test"
    )
    
    # Create a span (simulating OpenLit instrumentation)
    with tracer.start_span("openai.chat.completion") as span:
        # Set OpenLit-style attributes (flattened)
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", "gpt-4o")
        span.set_attribute("gen_ai.completion.0.message.role", "assistant")
        span.set_attribute("gen_ai.completion.0.message.content", "Hello!")
        span.set_attribute("gen_ai.completion.0.message.tool_calls.0.id", "call_xyz")
        span.set_attribute("gen_ai.completion.0.message.tool_calls.0.function.name", "greet")
        span.set_attribute("gen_ai.completion.0.message.tool_calls.0.function.arguments", '{"name": "Alice"}')
        span.set_attribute("gen_ai.usage.prompt_tokens", 10)
        span.set_attribute("gen_ai.usage.completion_tokens", 15)
    
    # Verify honeyhive_* attributes were added
    span_attrs = dict(span.attributes)
    
    # Should have honeyhive_outputs.tool_calls as JSON string
    assert "honeyhive_outputs.tool_calls" in span_attrs
    tool_calls_json = span_attrs["honeyhive_outputs.tool_calls"]
    tool_calls = json.loads(tool_calls_json)  # Backend will do this
    
    assert tool_calls[0]["id"] == "call_xyz"
    assert tool_calls[0]["function"]["name"] == "greet"
    assert tool_calls[0]["function"]["arguments"] == '{"name": "Alice"}'  # Still a string!
```

---

## 📋 Implementation Checklist

### Week 1: Core Implementation

- [ ] **Day 1: Phase 1** - Add missing navigation rules
  - [ ] Tool calls extraction rules (all instrumentors)
  - [ ] Advanced field rules (refusal, audio, annotations)
  - [ ] Validation rules for new types
  
- [ ] **Day 2: Phase 2** - Add transform configurations
  - [ ] Tool calls reconstruction transform
  - [ ] Advanced field extraction transforms
  - [ ] JSON string preservation logic
  
- [ ] **Day 3: Phase 3** - Update field mappings
  - [ ] Fix tool_calls mapping
  - [ ] Add advanced output fields
  - [ ] Add advanced metadata fields

### Week 2: Testing & Validation

- [ ] **Day 4: Phase 4** - Verify transform registry
  - [ ] Check existing functions
  - [ ] Add missing functions if needed
  - [ ] Test transforms in isolation
  
- [ ] **Day 5: Phase 5** - Recompile & verify
  - [ ] Run DSL compiler
  - [ ] Verify bundle contents
  - [ ] Test bundle loading
  
- [ ] **Day 6-7: Phase 6** - Integration testing
  - [ ] Unit tests for each field type
  - [ ] Integration tests with real spans
  - [ ] End-to-end tests with SDK

---

## 🔍 Verification Steps

### Step 1: Check DSL Configs

```bash
# Verify all configs updated
git diff config/dsl/providers/openai/

# Check for tool_calls references
grep -r "tool_calls" config/dsl/providers/openai/
grep -r "refusal" config/dsl/providers/openai/
grep -r "audio" config/dsl/providers/openai/
```

### Step 2: Test Transform Functions

```python
# Test reconstruct_array_from_flattened
from honeyhive.tracer.processing.semantic_conventions.transform_registry import TRANSFORM_REGISTRY

data = {
    "gen_ai.completion.0.message.tool_calls.0.id": "call_abc",
    "gen_ai.completion.0.message.tool_calls.0.function.name": "test",
    "gen_ai.completion.0.message.tool_calls.0.function.arguments": '{"key": "value"}',
}

result = TRANSFORM_REGISTRY["reconstruct_array_from_flattened"](
    data,
    prefix="gen_ai.completion.0.message.tool_calls",
    preserve_json_strings=["arguments"]
)

assert result[0]["function"]["arguments"] == '{"key": "value"}'  # Still a string!
```

### Step 3: Test Bundle Compilation

```bash
# Force recompile
rm src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl

# Import will trigger auto-recompile
python -c "from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor; p = UniversalSemanticConventionProcessor()"
```

### Step 4: Integration Test

```bash
# Run integration tests
pytest tests/integration/test_openai_dsl_translation.py -v

# Run with real OpenLit spans
pytest tests/integration/test_openlit_openai.py -v
```

---

## 🚨 Critical Success Criteria

### Must Have (P0)

- ✅ **Tool calls extraction works** - Reconstruct from flattened attributes
- ✅ **Arguments preserved as JSON strings** - Not parsed to objects
- ✅ **All instrumentors supported** - OpenInference, Traceloop, OpenLit
- ✅ **Bundle compiles successfully** - No errors
- ✅ **Integration tests pass** - All test scenarios

### Should Have (P1)

- ✅ **Refusal messages extracted** - Safety compliance
- ✅ **Audio responses extracted** - Multimodal support
- ✅ **System fingerprint captured** - Debugging support
- ✅ **Response model tracked** - Actual vs requested model

### Nice to Have (P2)

- ✅ **Annotations extracted** - Web search citations
- ✅ **Logprobs extracted** - Token probabilities
- ✅ **Legacy function_call support** - Backward compatibility

---

## 📊 Expected Outcomes

### Before Implementation

| Metric | Current | Target | Delta |
|--------|---------|--------|-------|
| **Field Coverage** | 30% | 100% | +70% |
| **Tool Calls Work** | ❌ No | ✅ Yes | Fixed |
| **Advanced Fields** | ❌ No | ✅ Yes | Fixed |
| **JSON String Handling** | ⚠️ Maybe | ✅ Yes | Fixed |
| **Array Reconstruction** | ❌ No | ✅ Yes | Fixed |

### After Implementation

- ✅ **100% OpenAI field coverage** - All response fields mapped
- ✅ **Tool-using agents work** - Tool calls properly extracted
- ✅ **Safety tracking works** - Refusal messages captured
- ✅ **Multimodal support** - Audio/image data preserved
- ✅ **Backend receives clean data** - No parsing needed

---

## 🔗 Related Documentation

- **Transform Registry**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py`
- **Event Schema**: `.agent-os/standards/architecture/HONEYHIVE_EVENT_SCHEMA_REFERENCE.md`
- **Current vs Legacy**: `.agent-os/standards/architecture/CURRENT_VS_LEGACY_IMPLEMENTATION.md`
- **DSL Architecture**: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`

---

**Last Updated**: 2025-09-30  
**Next Steps**: Begin Phase 1 - Add missing navigation rules

