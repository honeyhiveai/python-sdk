# OpenAI Response Schema - Critical Findings

**Schema Version**: v2025-01-30  
**Date**: 2025-09-30  
**Purpose**: Document critical format notes, common pitfalls, and usage guidance for DSL integration

---

## 🚨 Critical Format Notes

### 1. Tool Call Arguments are JSON STRINGS (Not Objects)

**Finding**: The most critical discovery - tool call arguments are serialized as JSON strings, NOT parsed objects.

```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"San Francisco\", \"unit\": \"celsius\"}"
        // ⚠️  This is a STRING, not an object!
      }
    }
  ]
}
```

**DSL Impact**:
- ❌ **DO NOT** parse `arguments` into an object during extraction
- ✅ **DO** preserve as JSON string in `honeyhive_outputs.tool_calls[].function.arguments`
- ✅ **DO** use `format: "json-string"` hint in schema for DSL guidance

**Common Pitfall**: DSL transform functions may be tempted to `json.loads()` the arguments. This will break the schema contract.

**Correct Transform**:
```python
# In transform_registry.py
def extract_tool_call_arguments(data: Dict[str, Any], **kwargs) -> str:
    """Extract tool call arguments as JSON STRING (do not parse)."""
    args = data.get("function", {}).get("arguments", "{}")
    # Return as-is, do NOT json.loads()
    return args
```

---

### 2. Content Field Can Be Null

**Finding**: The `content` field in `ChatCompletionMessage` can be `null` when tool calls or refusal is the primary response.

```json
{
  "message": {
    "role": "assistant",
    "content": null,  // ⚠️  Null, not empty string!
    "tool_calls": [
      // ... tool calls present
    ]
  }
}
```

**DSL Impact**:
- ❌ **DO NOT** assume `content` always has a string value
- ✅ **DO** handle `null` explicitly in navigation rules
- ✅ **DO** use fallback values in field mappings

**Common Pitfall**: DSL navigation rules that don't check for null will fail on tool-calling responses.

**Correct Navigation Rule**:
```yaml
# In navigation_rules.yaml
traceloop_content:
  source_field: "gen_ai.completion.0.message.content"
  extraction_method: "direct_copy"
  fallback_value: ""  # Empty string when null
  null_handling: "use_fallback"
```

---

### 3. Audio Data is Base64 Encoded

**Finding**: Audio responses contain base64-encoded audio data in the `audio.data` field.

```json
{
  "message": {
    "audio": {
      "id": "audio_abc123",
      "expires_at": 1728442073,
      "data": "UklGRhwa...",  // ⚠️  Base64 string
      "transcript": "Hello, how can I help you?"
    }
  }
}
```

**DSL Impact**:
- ❌ **DO NOT** attempt to decode base64 during extraction
- ✅ **DO** preserve as base64 string in `honeyhive_outputs.audio.data`
- ✅ **DO** use `format: "base64"` hint in schema

**Storage Consideration**: Base64 audio data can be very large (100KB+ per message). Consider:
- Truncation for UI display
- Separate storage for full audio
- Reference by ID rather than embedding full data

---

### 4. Refusal Indicates Safety Policy Violation

**Finding**: The `refusal` field (added in API v2024-08-06) indicates the model refused to generate a response due to safety policies.

```json
{
  "message": {
    "role": "assistant",
    "content": null,
    "refusal": "I'm sorry, I can't assist with that request."
  }
}
```

**DSL Impact**:
- ✅ **DO** extract `refusal` to `honeyhive_outputs.refusal`
- ✅ **DO** treat as alternative to `content` (mutually exclusive in some cases)
- ✅ **DO** flag for safety monitoring/alerting

**Common Pitfall**: Assuming all responses have content. Refusal responses may have null content.

---

### 5. Flattened Attributes in Instrumentors

**Finding**: All instrumentors (Traceloop, OpenLit, OpenInference) flatten nested arrays into dot-notation attributes.

**Example**: A tool call response becomes:
```
gen_ai.completion.0.message.tool_calls.0.id = "call_abc123"
gen_ai.completion.0.message.tool_calls.0.type = "function"
gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
gen_ai.completion.0.message.tool_calls.0.function.arguments = "{...}"
gen_ai.completion.0.message.tool_calls.1.id = "call_def456"
gen_ai.completion.0.message.tool_calls.1.type = "function"
...
```

**DSL Impact**:
- ❌ **DO NOT** expect array structure in span attributes
- ✅ **DO** use `reconstruct_array_from_flattened()` transform
- ✅ **DO** specify correct prefix (e.g., `"gen_ai.completion.0.message.tool_calls"`)

**Required Transform**:
```python
# In transforms.yaml
extract_tool_calls:
  function_type: "array_reconstruction"
  implementation: "reconstruct_array_from_flattened"
  parameters:
    prefix: "gen_ai.completion.0.message.tool_calls"
    preserve_json_strings: true  # Critical for arguments field
```

---

## ⚠️ Common Pitfalls

### Pitfall 1: Parsing JSON Strings
**Problem**: Calling `json.loads()` on `tool_calls[].function.arguments`  
**Impact**: Breaks schema contract, causes type mismatches  
**Solution**: Preserve as JSON string, document with `format: "json-string"`

### Pitfall 2: Assuming Content Always Exists
**Problem**: Not handling null `content` field  
**Impact**: DSL extraction fails on tool calls and refusal responses  
**Solution**: Use null-safe extraction with fallback values

### Pitfall 3: Missing Array Reconstruction
**Problem**: Not reconstructing arrays from flattened attributes  
**Impact**: Tool calls, multiple choices, annotations all lost  
**Solution**: Use `reconstruct_array_from_flattened()` for all array fields

### Pitfall 4: Hardcoding Array Indices
**Problem**: Using fixed paths like `gen_ai.completion.0.message.tool_calls.0.*`  
**Impact**: Only first tool call extracted, rest lost  
**Solution**: Use dynamic array reconstruction with numeric index detection

### Pitfall 5: Ignoring Format Hints
**Problem**: Not respecting `format: "json-string"` or `format: "base64"` schema hints  
**Impact**: Incorrect data transformation, lost fidelity  
**Solution**: Check format field in schema, preserve accordingly

---

## 📚 Usage Examples for DSL

### Example 1: Extracting Tool Calls (Complete Pipeline)

**Input** (Flattened Span Attributes):
```python
{
  "gen_ai.completion.0.message.tool_calls.0.id": "call_abc",
  "gen_ai.completion.0.message.tool_calls.0.function.name": "get_weather",
  "gen_ai.completion.0.message.tool_calls.0.function.arguments": '{"location": "SF"}',
  "gen_ai.completion.0.message.tool_calls.1.id": "call_def",
  "gen_ai.completion.0.message.tool_calls.1.function.name": "get_time",
  "gen_ai.completion.0.message.tool_calls.1.function.arguments": '{"timezone": "PST"}'
}
```

**Navigation Rule**:
```yaml
# navigation_rules.yaml
traceloop_tool_calls_flattened:
  source_field: "gen_ai.completion.0.message.tool_calls"
  extraction_method: "array_reconstruction"
  description: "Reconstructs tool_calls array from flattened Traceloop attributes"
```

**Transform**:
```yaml
# transforms.yaml
extract_tool_calls:
  function_type: "array_reconstruction"
  implementation: "reconstruct_array_from_flattened"
  parameters:
    prefix: "gen_ai.completion.0.message.tool_calls"
    preserve_json_strings: ["function.arguments"]  # Critical!
```

**Field Mapping**:
```yaml
# field_mappings.yaml
outputs:
  tool_calls:
    source_rule: "extract_tool_calls"
    transform: "extract_tool_calls"
    required: false
```

**Output** (HoneyHive Schema):
```python
{
  "honeyhive_outputs": {
    "tool_calls": [
      {
        "id": "call_abc",
        "function": {
          "name": "get_weather",
          "arguments": '{"location": "SF"}'  # JSON string preserved!
        }
      },
      {
        "id": "call_def",
        "function": {
          "name": "get_time",
          "arguments": '{"timezone": "PST"}'  # JSON string preserved!
        }
      }
    ]
  }
}
```

---

### Example 2: Handling Null Content with Fallback

**Input**:
```python
{
  "gen_ai.completion.0.message.content": None,  # Null!
  "gen_ai.completion.0.message.tool_calls.0.id": "call_abc",
}
```

**Navigation Rule** (Correct):
```yaml
traceloop_content:
  source_field: "gen_ai.completion.0.message.content"
  extraction_method: "direct_copy"
  fallback_value: ""
  null_handling: "use_fallback"
```

**Output**:
```python
{
  "honeyhive_outputs": {
    "content": "",  # Empty string, not null
    "tool_calls": [...]
  }
}
```

---

### Example 3: Extracting Refusal Messages

**Input**:
```python
{
  "gen_ai.completion.0.message.content": None,
  "gen_ai.completion.0.message.refusal": "I can't assist with that."
}
```

**Navigation Rule**:
```yaml
traceloop_refusal:
  source_field: "gen_ai.completion.0.message.refusal"
  extraction_method: "direct_copy"
  description: "Extracts safety refusal message (API v2024-08-06+)"
```

**Field Mapping**:
```yaml
outputs:
  refusal:
    source_rule: "traceloop_refusal"
    required: false
```

**Output**:
```python
{
  "honeyhive_outputs": {
    "content": "",
    "refusal": "I can't assist with that."  # Flagged for safety monitoring
  }
}
```

---

## 🎯 DSL Design Principles (Derived from Findings)

### 1. Preserve Source Fidelity
- Never mutate data during extraction
- Preserve JSON strings as strings
- Preserve base64 as base64
- Document format with schema hints

### 2. Handle Null Explicitly
- Always define fallback values
- Use null-safe extraction methods
- Don't assume fields exist

### 3. Reconstruct Arrays Properly
- Detect numeric indices dynamically
- Reconstruct in correct order
- Preserve nested object structure
- Keep JSON string fields intact

### 4. Document Format Contracts
- Use `format` field in schema
- Document DSL impact in schema
- Provide usage examples
- List common pitfalls

### 5. Validate Against Examples
- Test extraction on all 11 examples
- Verify edge cases (null, arrays, JSON strings)
- Confirm 100% field coverage
- Check for data loss/mutation

---

## 📋 Quality Checklist for DSL Integration

Before considering OpenAI DSL "complete", verify:

- [ ] Tool calls extracted with arguments as JSON **strings**
- [ ] Null content handled with fallback
- [ ] Refusal messages extracted
- [ ] Audio data preserved as base64
- [ ] Arrays reconstructed from flattened attributes
- [ ] System fingerprint captured
- [ ] Annotations array handled
- [ ] All 11 examples extract correctly
- [ ] No data loss or mutation
- [ ] Format hints documented

---

**Last Updated**: 2025-09-30  
**Framework**: Provider Schema Extraction Framework v1.0  
**Next**: Phase 7 (Integration Testing with DSL)

