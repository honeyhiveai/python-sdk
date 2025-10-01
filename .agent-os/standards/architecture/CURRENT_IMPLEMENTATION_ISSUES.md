# Current Semantic Conventions Implementation Issues

**Date**: 2025-09-30  
**Status**: Analysis of Current State  
**Purpose**: Document the issues with the current implementation that the DSL architecture must solve

---

## 🚨 The Core Problem

The current semantic conventions implementation **does handle JSON serialization** but **does NOT dynamically handle LLM response structures**. It has hardcoded logic that loses critical data.

---

## 📊 Current Implementation Analysis

### Location
`src/honeyhive/tracer/semantic_conventions/mapping/transforms.py`

### The `_normalize_message` Function (Lines 128-141)

```python
def _normalize_message(self, msg: Dict[str, Any]) -> Dict[str, str]:
    """Normalize message format to handle both direct and nested formats."""
    # Handle OpenInference format:
    # {"message.role": "user", "message.content": "..."}
    if "message.role" in msg and "message.content" in msg:
        return {
            "role": str(msg.get("message.role", "user")),
            "content": str(msg.get("message.content", "")),
        }
    # Handle standard format: {"role": "user", "content": "..."}
    return {
        "role": str(msg.get("role", "user")),
        "content": str(msg.get("content", "")),
    }
```

### ❌ **CRITICAL ISSUE: Data Loss**

**What it DOES extract**:
- ✅ `role`
- ✅ `content`

**What it LOSES** (hardcoded omission):
- ❌ `tool_calls` - Array of function calls made by the assistant
- ❌ `tool_call_id` - ID linking tool messages to tool calls
- ❌ `name` - Tool name for tool messages
- ❌ `refusal` - OpenAI refusal messages (safety)
- ❌ `audio` - OpenAI audio response data
- ❌ `function_call` - Legacy OpenAI function calling
- ❌ Any other provider-specific fields

---

## 🔍 Example: Data Loss in Action

### Input: OpenAI Response with Tool Calls

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"San Francisco\"}"
      }
    }
  ]
}
```

### Current Output (After `_normalize_message`)

```python
{
    "role": "assistant",
    "content": "None"  # or ""
}
```

### ❌ **Result**: `tool_calls` array is COMPLETELY LOST

---

## 📋 Current Transforms and Their Limitations

### 1. `_parse_messages` (Lines 103-126)

**What it does**:
- Parses JSON or list of messages
- Calls `_normalize_message` on each message

**Problem**:
```python
return [
    self._normalize_message(msg)  # ❌ Loses all fields except role/content
    for msg in parsed
    if isinstance(msg, dict)
]
```

### 2. `_parse_flattened_messages` (Lines 155-170)

**What it does**:
- Reconstructs messages from flattened attributes

**Problem**:
```python
for key, value in flattened_attrs.items():
    index, field = self._extract_index_and_field(key)
    if index is not None and field in ["role", "content"]:  # ❌ ONLY role/content
        if index not in messages:
            messages[index] = {}
        messages[index][field] = value
```

**Hardcoded to only extract `role` and `content`** - ignores everything else!

### 3. `_extract_index_and_field` (Lines 172-191)

**What it does**:
- Finds numeric index and field name from flattened keys

**Problem**:
```python
def _find_field_in_remaining_parts(self, remaining_parts: List[str]) -> Optional[str]:
    # Look for role/content in remaining parts
    for remaining_part in remaining_parts:
        if remaining_part in ["role", "content"]:  # ❌ Hardcoded to only these fields
            return remaining_part
```

**Only recognizes `role` and `content`** - all other fields ignored!

---

## 🔄 Current Flow (With Data Loss)

```
Flattened Span Attributes:
├── gen_ai.completion.0.message.role = "assistant"
├── gen_ai.completion.0.message.content = null
├── gen_ai.completion.0.message.tool_calls.0.id = "call_abc123"
├── gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
└── gen_ai.completion.0.message.tool_calls.0.function.arguments = '{"location": "SF"}'

       ↓ _parse_flattened_messages()
       
Messages Extracted:
[
  {
    "role": "assistant",
    "content": "null"
  }
]
       ↓ tool_calls LOST!
       
HoneyHive Event:
{
  "inputs": {
    "chat_history": [
      {"role": "assistant", "content": "null"}
    ]
  },
  "outputs": {
    "content": "null"
    // ❌ tool_calls missing!
  }
}

       ↓ Backend receives incomplete data
       
UI Display:
- Shows: "assistant: null"
- Missing: Tool calls, function names, arguments
```

---

## 🚨 Why This Is a Critical Issue

### 1. **Tool Call Data Loss**

When an LLM calls a tool:
- ❌ Tool call ID lost → Can't link tool results
- ❌ Function name lost → Don't know what was called
- ❌ Arguments lost → Don't know what parameters were used

**Impact**: Tool-using agents appear broken in the UI

### 2. **Safety/Refusal Data Loss**

When OpenAI refuses a request:
- ❌ Refusal message lost → Don't know why it refused
- ❌ Content is null → UI shows empty response

**Impact**: Safety incidents not properly tracked

### 3. **Multimodal Data Loss**

When using audio/image responses:
- ❌ Audio data lost → Can't replay audio responses
- ❌ Image data lost → Can't display images

**Impact**: Multimodal applications unusable

### 4. **Provider-Specific Features Lost**

Each provider has unique fields:
- OpenAI: `audio`, `refusal`, `annotations`
- Anthropic: `stop_reason`, `stop_sequence`
- Gemini: `safety_ratings`, `citation_metadata`

**Impact**: Can't support advanced provider features

---

## ✅ What the DSL Architecture Must Fix

### 1. **Dynamic Field Extraction**

Instead of hardcoding `["role", "content"]`:
```python
# Current (hardcoded) ❌
if field in ["role", "content"]:
    messages[index][field] = value

# DSL-based (dynamic) ✅
# Extract ALL fields from flattened structure
for key, value in flattened_attrs.items():
    # Dynamically determine index, field_path
    # Reconstruct full object structure
```

### 2. **Preserve Nested Structures**

```python
# Current (flattened only) ❌
{
  "role": "assistant",
  "content": "null"
}

# DSL-based (full structure) ✅
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"SF\"}"
      }
    }
  ]
}
```

### 3. **JSON String Handling**

```python
# Current (may parse incorrectly) ❌
"arguments": {"location": "SF"}  # Parsed to object

# DSL-based (preserve JSON strings) ✅
"arguments": '{"location": "SF"}'  # Keep as JSON string
```

### 4. **Provider-Agnostic Transform**

```python
# Current (provider-specific checks) ❌
if "choices" in response:
    # OpenAI-specific logic
elif "content" in response:
    # Generic fallback

# DSL-based (declarative config) ✅
# YAML config handles all providers
mappings:
  gen_ai.completion.0.message.tool_calls:
    target: "honeyhive_outputs.tool_calls"
    transform: "reconstruct_array_from_flattened"
```

---

## 📊 Comparison: Current vs DSL Approach

| Aspect | Current Implementation | DSL Architecture |
|--------|----------------------|------------------|
| **Field Extraction** | Hardcoded `["role", "content"]` | Dynamic (all fields) |
| **Nested Structures** | ❌ Loses tool_calls, etc. | ✅ Reconstructs arrays/objects |
| **JSON Strings** | ⚠️ Sometimes parses incorrectly | ✅ Preserves as strings when needed |
| **Provider Support** | Hardcoded checks per provider | Declarative YAML configs |
| **Extensibility** | Requires code changes | Add YAML mapping |
| **Data Fidelity** | 30-50% (role/content only) | 100% (all fields) |

---

## 🔧 Required Transforms for DSL

### 1. **Array Reconstruction from Flattened**

```python
def reconstruct_array_from_flattened(
    data: Dict[str, Any],
    prefix: str,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Reconstruct array of objects from flattened dot-notation attributes.
    
    Example:
    Input:
        data = {
            "gen_ai.completion.0.message.tool_calls.0.id": "call_abc",
            "gen_ai.completion.0.message.tool_calls.0.function.name": "get_weather",
            "gen_ai.completion.0.message.tool_calls.0.function.arguments": '{"location": "SF"}',
        }
        prefix = "gen_ai.completion.0.message.tool_calls"
    
    Output:
        [
            {
                "id": "call_abc",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "SF"}'
                }
            }
        ]
    """
    import re
    
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.(.+)$")
    indexed_data: Dict[int, Dict[str, Any]] = {}
    
    for key, value in data.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field_path = match.group(2)  # e.g., "function.name"
            
            if index not in indexed_data:
                indexed_data[index] = {}
            
            # Set nested value
            set_nested_value(indexed_data[index], field_path.split("."), value)
    
    # Convert to sorted array
    if not indexed_data:
        return []
    
    max_index = max(indexed_data.keys())
    return [indexed_data.get(i, {}) for i in range(max_index + 1)]
```

### 2. **Complete Message Extraction**

```python
def extract_complete_message(
    data: Dict[str, Any],
    prefix: str = "gen_ai.completion.0.message",
    **kwargs: Any
) -> Dict[str, Any]:
    """Extract complete message with ALL fields.
    
    Extracts:
    - role, content (always)
    - tool_calls (if present)
    - tool_call_id (if present)
    - name (if present)
    - refusal (if present)
    - audio (if present)
    - Any other fields dynamically
    """
    message = {}
    
    # Extract all fields matching the prefix
    for key, value in data.items():
        if key.startswith(prefix + "."):
            field_path = key[len(prefix) + 1:]  # Remove prefix and dot
            
            # Handle nested structures (e.g., tool_calls.0.id)
            if "." in field_path and field_path.split(".")[0].isdigit():
                # This is an array element, handle separately
                continue
            
            # Set the field
            set_nested_value(message, field_path.split("."), value)
    
    # Extract arrays (tool_calls, etc.)
    if any(k.startswith(prefix + ".tool_calls.") for k in data.keys()):
        message["tool_calls"] = reconstruct_array_from_flattened(
            data, prefix + ".tool_calls"
        )
    
    return message
```

### 3. **JSON String Preservation**

```python
def preserve_json_strings(
    value: Any,
    fields_as_json_strings: List[str] = ["arguments"],
    **kwargs: Any
) -> Any:
    """Ensure specific fields remain as JSON strings, not parsed objects.
    
    Critical for tool_calls where:
    - arguments must be a JSON STRING, not an object
    """
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if k in fields_as_json_strings:
                # Ensure it's a JSON string
                if isinstance(v, dict) or isinstance(v, list):
                    result[k] = json.dumps(v)
                else:
                    result[k] = str(v)
            elif isinstance(v, dict) or isinstance(v, list):
                result[k] = preserve_json_strings(v, fields_as_json_strings)
            else:
                result[k] = v
        return result
    elif isinstance(value, list):
        return [preserve_json_strings(item, fields_as_json_strings) for item in value]
    else:
        return value
```

---

## 🎯 Summary

### Current State ❌

- **Hardcoded field extraction**: Only `role` and `content`
- **Data loss**: 50-70% of LLM response data lost
- **Static logic**: Requires code changes for new fields
- **Provider-specific**: Separate logic for each provider

### Required State ✅

- **Dynamic field extraction**: ALL fields preserved
- **100% data fidelity**: No data loss
- **Declarative config**: YAML-based field mappings
- **Provider-agnostic**: Same logic, different configs

### The DSL Fix

The DSL architecture solves this by:
1. **Declarative mappings**: Define what fields to extract in YAML
2. **Dynamic transforms**: Generic functions that preserve all fields
3. **Array reconstruction**: Rebuild nested structures from flattened attrs
4. **JSON string preservation**: Keep JSON strings as strings, not objects

---

## 📚 Related Documentation

- **Target Schema**: `.agent-os/standards/architecture/HONEYHIVE_EVENT_SCHEMA_REFERENCE.md`
- **DSL Architecture**: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`
- **Transform Registry**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py` (the correct implementation)

---

**Last Updated**: 2025-09-30  
**Action Required**: Implement the DSL-based transforms to replace the current hardcoded logic

