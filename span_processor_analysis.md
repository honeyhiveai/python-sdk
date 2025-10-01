# Span Processor Analysis: Current vs Real Event Structure

## Summary
After querying 100 real events from the 'Deep Research Prod' project, I've identified critical gaps between the current span processor implementation and the actual event structure expected by the HoneyHive backend.

## Key Issues Found

### 1. **Incorrect Input Structure Mapping**
**Current Implementation (lines 771-783):**
```python
# Add all attributes as inputs (for test compatibility)
for key, value in attributes.items():
    if not key.startswith("honeyhive.") and not key.startswith("traceloop."):
        event_data["inputs"][key] = value
```

**Real Event Structure:**
```json
"inputs": {
  "chat_history": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "tool_calls.0.id": "...", "tool_calls.0.name": "...", "tool_calls.0.arguments": "..."}
  ],
  "functions": [...]  // Sometimes present
}
```

**Problem:** Current code dumps ALL span attributes into inputs, but real events have structured chat_history arrays.

### 2. **Missing Config Structure**
**Current Implementation:** No config extraction logic

**Real Event Structure:**
```json
"config": {
  "provider": "OpenAI",
  "model": "gpt-4o", 
  "headers": "None",
  "is_streaming": false
}
```

**Problem:** Config section is completely missing from span conversion.

### 3. **Incorrect Output Structure**
**Current Implementation:** No output extraction logic

**Real Event Structure:**
```json
"outputs": {
  "finish_reason": "stop",
  "role": "assistant",
  "content": "## Valuation Metrics Comparison Report: Tesla (TSLA) vs. Ford (F)..."
}
```

**Problem:** Outputs are not being extracted from span attributes.

### 4. **Metadata Confusion**
**Current Implementation (lines 785-793):**
```python
# Add HoneyHive-specific attributes as metadata
for key, value in attributes.items():
    if key.startswith("honeyhive.") and key not in [...]:
        clean_key = key.replace("honeyhive.", "")
        event_data["metadata"][clean_key] = value
```

**Real Event Structure:**
```json
"metadata": {
  "scope": {"name": "opentelemetry.instrumentation.openai.v1", "version": "0.30.0"},
  "llm.request.type": "chat",
  "disable_http_tracing": false,
  "run_id": "16035610-14ad-4fda-ada6-04b76ec8a46c",
  "dataset_id": "6840a7b6022be4aea3779970", 
  "datapoint_id": "6840a7b684dac281786dcd86",
  "gen_ai.openai.api_base": "https://api.openai.com/v1/",
  "response_model": "gpt-4o-2024-08-06",
  "system_fingerprint": "fp_07871e2ad8",
  "total_tokens": 3261,
  "completion_tokens": 410,
  "prompt_tokens": 2851
}
```

**Problem:** Real metadata contains instrumentation data, not just honeyhive.* attributes.

### 5. **Missing Critical Fields**
**Real events contain fields not handled by current processor:**
- `project_id` (not just project name)
- `parent_id` and `children_ids` for span relationships
- `duration` (calculated from start/end times)
- `feedback` and `metrics` (empty but present)
- `user_properties` (empty but present)

## Recommended Fixes

### 1. **Implement Proper Input Extraction**
Need to extract structured chat_history from span attributes like:
- `gen_ai.request.messages.0.role`
- `gen_ai.request.messages.0.content`
- `gen_ai.request.messages.1.role`
- etc.

### 2. **Add Config Extraction**
Extract from span attributes:
- `gen_ai.request.model` → config.model
- `gen_ai.system` → config.provider  
- `gen_ai.request.streaming` → config.is_streaming
- Request headers → config.headers

### 3. **Add Output Extraction**
Extract from span attributes:
- `gen_ai.response.finish_reasons` → outputs.finish_reason
- `gen_ai.response.model` → outputs.role (assistant)
- Response content → outputs.content

### 4. **Fix Metadata Mapping**
Map instrumentation attributes to metadata:
- `gen_ai.usage.prompt_tokens` → metadata.prompt_tokens
- `gen_ai.usage.completion_tokens` → metadata.completion_tokens
- `gen_ai.usage.total_tokens` → metadata.total_tokens
- `gen_ai.response.model` → metadata.response_model
- etc.

### 5. **Add Missing Fields**
- Calculate duration from start_time/end_time
- Extract parent_id from span context
- Initialize empty feedback, metrics, user_properties

## Priority
**HIGH** - This affects all event data sent to HoneyHive backend and impacts the quality of observability data.
