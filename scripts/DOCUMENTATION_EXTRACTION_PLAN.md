# Documentation Extraction Plan - Schema Research from Existing Sources

## 🎯 **Strategy: Documentation-First, API Calls Last**

Instead of running expensive API calls, systematically extract schema information from:
1. **Semantic Convention Source Code** (already documented)
2. **Provider API Documentation** (already documented)
3. **API calls only as validation** (minimal, targeted)

## 📚 **Existing Documentation Sources**

### **1. Semantic Conventions (Already Documented)**

**Location**: `universal_llm_discovery_engine_v4_final/RESEARCH_REFERENCES.md` (lines 19-46)

#### **OpenInference**
- **Source Code**: https://github.com/Arize-ai/openinference/blob/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py
- **Namespace**: `llm.*`
- **Known Attributes**:
  - `llm.input_messages` - Input messages array
  - `llm.output_messages` - Output messages array
  - `llm.token_count_prompt` - Input tokens
  - `llm.token_count_completion` - Output tokens
  - `llm.model_name` - Model identifier
  - `llm.invocation_parameters` - Parameters

**Question to Answer**: How does OpenInference serialize `llm.input_messages`?
- **Method**: Read the source code directly
- **Output**: Document if it's flattened, nested, or JSON string

#### **Traceloop/OpenLLMetry**
- **Source Code**: https://github.com/traceloop/openllmetry/blob/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py
- **Namespace**: `gen_ai.*`
- **Known Attributes**:
  - `gen_ai.request.model` - Requested model
  - `gen_ai.response.model` - Actual model
  - `gen_ai.usage.prompt_tokens` - Input tokens
  - `gen_ai.usage.completion_tokens` - Output tokens
  - `gen_ai.system` - Provider identifier
  - `gen_ai.completion` - Output text
  - `gen_ai.prompt` - Input text/messages

**Question to Answer**: How does Traceloop serialize `gen_ai.prompt`?
- **Method**: Read the source code directly
- **Output**: Document the actual format

#### **OpenLit**
- **Source Code**: https://github.com/openlit/openlit/blob/2f07f37f41ad1834048e27e49e08bb7577502c7c/sdk/python/src/openlit/semcov/__init__.py#L11
- **Namespace**: `gen_ai.*`
- **Additional**: Cost tracking, usage analytics

**Question to Answer**: How does OpenLit handle attributes?
- **Method**: Read the source code
- **Output**: Document unique patterns

### **2. Provider API Response Schemas (Already Documented)**

**Location**: `config/dsl/providers/openai/RESEARCH_SOURCES.md`

#### **OpenAI**
- **API Reference**: https://platform.openai.com/docs/api-reference/chat/object#chat/object-choices-message
- **Known Response Structure** (from docs):
  ```json
  {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "...",
        "tool_calls": [...],
        "function_call": {...},
        "refusal": "...",
        "audio": {...}
      }
    }],
    "usage": {
      "prompt_tokens": 56,
      "completion_tokens": 31,
      "total_tokens": 87
    }
  }
  ```

**Task**: Extract complete schema from documentation
- **Method**: Read OpenAI API reference systematically
- **Output**: Complete JSON schema for all response types

#### **Anthropic**
- **API Reference**: https://docs.anthropic.com/en/api/messages
- **Known Response Structure**:
  ```json
  {
    "id": "msg_...",
    "type": "message",
    "role": "assistant",
    "content": [
      {"type": "text", "text": "..."},
      {"type": "thinking", "thinking": "..."}
    ],
    "model": "claude-3-5-sonnet-20241022",
    "stop_reason": "end_turn",
    "usage": {
      "input_tokens": 12,
      "output_tokens": 6
    }
  }
  ```

**Task**: Extract complete schema including content block types
- **Method**: Read Anthropic API docs systematically
- **Output**: Complete schema for all content types

## 🔬 **Systematic Extraction Process**

### **Phase 1: Extract Semantic Convention Schemas (2 hours)**

For each instrumentor:

1. **Read Source Code**: Navigate to GitHub links
2. **Find Attribute Definitions**: Look for constants/enums defining attributes
3. **Find Serialization Logic**: How do they convert provider responses to span attributes?
4. **Document Format**: Create schema showing exact format used

**Deliverables**:
- `semantic_conventions_schemas.md` with:
  - OpenInference: Complete attribute list + format examples
  - Traceloop: Complete attribute list + format examples
  - OpenLit: Complete attribute list + format examples

### **Phase 2: Extract Provider Response Schemas (3 hours)**

For each provider:

1. **Read API Documentation**: Follow links in RESEARCH_SOURCES.md
2. **Extract Response Schemas**: Copy/document all response formats
3. **Identify Variations**: Tool calls, multimodal, streaming, errors
4. **Create Examples**: Realistic example responses for each type

**Deliverables**:
- `provider_response_schemas/`
  - `openai_schemas.md` - All OpenAI response formats
  - `anthropic_schemas.md` - All Anthropic response formats
  - `gemini_schemas.md` - All Gemini response formats

### **Phase 3: Map Provider → Instrumentor → HoneyHive (2 hours)**

Create transformation flow documentation:

```
Provider Response → Instrumentor Serialization → HoneyHive Extraction

Example: OpenAI Tool Calls
┌─────────────────────────────────────────────────────────────┐
│ 1. OpenAI API Response                                      │
│ {                                                            │
│   "choices": [{                                              │
│     "message": {                                             │
│       "tool_calls": [{                                       │
│         "id": "call_123",                                    │
│         "type": "function",                                  │
│         "function": {                                        │
│           "name": "get_weather",                             │
│           "arguments": '{"location": "SF"}'                  │
│         }                                                    │
│       }]                                                     │
│     }                                                        │
│   }]                                                         │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. OpenInference Span Attributes                            │
│ llm.output_messages.0.tool_calls.0.id = "call_123"          │
│ llm.output_messages.0.tool_calls.0.function.name = "..."    │
│ llm.output_messages.0.tool_calls.0.function.arguments = ... │
│ (Flattened with dot notation)                               │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. HoneyHive Schema (Target)                                │
│ outputs.tool_calls = [                                      │
│   {                                                          │
│     "id": "call_123",                                        │
│     "function": {                                            │
│       "name": "get_weather",                                 │
│       "arguments": {"location": "SF"}                        │
│     }                                                        │
│   }                                                          │
│ ]                                                            │
│ (Reconstructed complex object)                              │
└─────────────────────────────────────────────────────────────┘
```

**Deliverables**:
- `transformation_flows.md` - Complete mapping documentation

### **Phase 4: Validate with Minimal API Calls (1 hour)**

Only after documentation extraction, run minimal validation:

```bash
# Validate OpenInference format for OpenAI
python scripts/research_span_attributes.py \
    --instrumentors openinference \
    --providers openai \
    --scenarios basic_chat \
    --operations 1  # Just ONE call to validate

# Compare captured attributes vs. documentation
# If they match: documentation is accurate ✅
# If they don't: update documentation and investigate
```

## 📋 **Immediate Action Items**

### **Task 1: Read OpenInference Source Code (30 min)**

```bash
# Clone or browse OpenInference repo
curl https://raw.githubusercontent.com/Arize-ai/openinference/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py

# Look for:
# - Attribute name constants
# - Serialization functions
# - How messages/arrays are handled
```

**Output**: Document in `semantic_conventions_schemas.md`

### **Task 2: Read Traceloop Source Code (30 min)**

```bash
# Clone or browse Traceloop repo
curl https://raw.githubusercontent.com/traceloop/openllmetry/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py

# Look for:
# - gen_ai.* attribute definitions
# - How prompts/completions are serialized
```

**Output**: Add to `semantic_conventions_schemas.md`

### **Task 3: Extract OpenAI Response Schema (45 min)**

Navigate to: https://platform.openai.com/docs/api-reference/chat/object

**Extract**:
- Chat completion object structure
- Message object structure
- Tool calls structure
- Audio structure (new)
- Usage structure
- All optional/required fields

**Output**: `provider_response_schemas/openai_schemas.md`

### **Task 4: Extract Anthropic Response Schema (45 min)**

Navigate to: https://docs.anthropic.com/en/api/messages

**Extract**:
- Message response structure
- Content block types (text, thinking, tool_use, etc.)
- Usage structure
- Stop reasons
- All variations

**Output**: `provider_response_schemas/anthropic_schemas.md`

## 🎯 **Success Criteria**

We have enough documentation when we can answer:

1. **How does OpenInference serialize arrays?** ✅ Documented
2. **How does Traceloop serialize messages?** ✅ Documented
3. **What's the exact structure of OpenAI tool_calls?** ✅ Documented
4. **What's the exact structure of Anthropic content blocks?** ✅ Documented
5. **How do we reconstruct from flattened?** ✅ Algorithm documented

## 💰 **Cost Savings**

**Documentation-First Approach**:
- Cost: $0 (reading docs)
- Time: ~7 hours
- Coverage: Complete understanding

**API-First Approach** (previous plan):
- Cost: ~$5-10 in API calls
- Time: ~2 hours (but incomplete understanding)
- Coverage: Limited to scenarios we tested

**Validation Calls** (after documentation):
- Cost: ~$0.10 (minimal testing)
- Time: 1 hour
- Coverage: Confirms documentation accuracy

## 🚀 **Next Steps**

1. **Create documentation extraction script** (optional, can do manually)
2. **Start with OpenInference source code review**
3. **Document findings systematically**
4. **Build transform logic based on documentation**
5. **Validate with 1-2 API calls per combination**

---

**Priority**: Start with OpenInference + OpenAI since:
- We already use it
- Most common combination
- Will inform patterns for others
