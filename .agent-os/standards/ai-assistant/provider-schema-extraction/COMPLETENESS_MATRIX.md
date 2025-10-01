# Provider Schema Completeness Matrix

**Purpose**: Systematic tracking of provider API response schema coverage

**Scope**: This framework covers ONLY provider API schemas, NOT trace source serialization patterns (instrumentors/frameworks)

**Last Updated**: 2025-09-30

---

## 🎯 **Completeness Dimensions**

### Dimension 1: Provider × Operation Type
Every LLM provider supports multiple operation types that produce different response structures.

### Dimension 2: Response Variations × Examples
Each operation type has multiple response variations (success, error, edge cases).

---

## 📊 **OpenAI Completeness Matrix**

### Provider API Coverage

| Operation Type | Response Schema | OpenAPI Spec | Examples | Schema File | Status |
|----------------|-----------------|--------------|----------|-------------|--------|
| **Chat Completion** | CreateChatCompletionResponse | ✅ Line 31698 | ✅ 6 | v2025-01-30.json | ✅ COMPLETE |
| **Chat Streaming** | CreateChatCompletionStreamResponse | ✅ Line 31849 | ✅ 1 | v2025-01-30.json | ✅ COMPLETE |
| **Legacy Completion** | CreateCompletionResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |
| **Embeddings** | CreateEmbeddingResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |
| **Image Generation** | ImagesResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |
| **Audio (Whisper)** | CreateTranscriptionResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |
| **Audio (TTS)** | AudioResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |
| **Moderation** | CreateModerationResponse | ⏳ TODO | ❌ 0 | ❌ No | ⏳ PENDING |

**Provider Schema Coverage**: 2/8 operations (25%)

**Note**: This framework documents ONLY the provider's API response structure. Trace source serialization patterns (how instrumentors/frameworks serialize these responses into spans) are handled by a separate **Trace Source Validation Framework**.

---

## 📊 **Other Provider Matrices** (TODO)

### Anthropic
- Claude Messages
- Claude Streaming
- (others TBD)

### Google  
- Gemini Pro
- Gemini Vision
- (others TBD)

### AWS Bedrock
- Claude via Bedrock
- Titan
- (others TBD)

---

## 🔗 **Related Frameworks**

This framework is part of a larger system:

### **Framework Dependency Chain**

```
1. Provider Schema Extraction (THIS FRAMEWORK)
   ↓ Produces: Provider response JSON Schemas
   
2. DSL Assembly Framework (SEPARATE)
   ↓ Uses schemas to build DSL extraction configs
   
3. Trace Source Validation Framework (SEPARATE)
   ↓ Tests DSL against real instrumented spans
```

### **Out of Scope for This Framework**

The following are handled by **separate frameworks**:
- ❌ Instrumentor span attribute patterns (OpenLit, Traceloop, etc.)
- ❌ Framework serialization patterns (Strands, Pydantic AI, etc.)
- ❌ DSL configuration assembly
- ❌ DSL extraction validation
- ❌ Span attribute navigation rules

**See Also**:
- `TRACE_SOURCE_RESEARCH.md` - For trace source serialization patterns
- DSL Assembly Framework (to be built)
- Trace Source Validation Framework (to be built)

---

## 🎯 **Completeness Quality Gates**

### Provider Schema Extraction Complete When:

For each provider operation type:
1. ✅ **OpenAPI Schema Located**: Found in official spec
2. ✅ **Schema Extracted**: Converted to JSON Schema format
3. ✅ **Examples Created**: At least 3 basic + 2 edge case examples
4. ✅ **Examples Validated**: All examples valid JSON, match schema
5. ✅ **Schema Metadata**: Source, version, date documented

### OpenAI Operation Coverage Goals

**Current Status**: 2/8 operations complete (25%)

**Priority Order**:
1. ✅ Chat Completions (COMPLETE)
2. ✅ Chat Streaming (COMPLETE)
3. ⏳ Embeddings (TODO - high priority, ~40% of API usage)
4. ⏳ Image Generation (TODO - medium priority)
5. ⏳ Audio/STT (TODO - medium priority)
6. ⏳ Audio/TTS (TODO - medium priority)
7. ⏳ Legacy Completions (TODO - low priority, deprecated)
8. ⏳ Moderation (TODO - low priority)

---

## 📋 **Next Actions**

### Immediate (Finish OpenAI Chat)
1. ✅ Complete Phases 5-7 for chat completions
2. ✅ Validate all documentation is complete
3. ✅ Verify schema accuracy against OpenAPI spec

### Short-Term (Expand OpenAI Coverage)
1. ⏳ Extract embeddings schema from OpenAPI spec
2. ⏳ Extract image generation schema
3. ⏳ Extract audio schemas (STT/TTS)
4. ⏳ Create examples for each operation type

### Long-Term (Provider Expansion)
1. ⏳ Repeat framework for Anthropic
2. ⏳ Repeat framework for Google (Gemini)
3. ⏳ Repeat framework for AWS Bedrock
4. ⏳ Repeat framework for Cohere, Mistral, etc.

---

## 🚨 **Critical Question**

**Do we need to support ALL operation types, or just the primary ones?**

### Option 1: Full Coverage (Recommended for Production)
- Support all 8 OpenAI operation types
- Validate against all major instrumentors
- Ensures DSL works for any HoneyHive user scenario

### Option 2: Primary Coverage (MVP)
- Focus on chat completions only (80% of use cases)
- Add other operations as user demand requires
- Faster to production, incremental expansion

### Option 3: Chat + Embeddings (Balanced)
- Cover chat (most common) + embeddings (second most common)
- ~90% coverage of real-world usage
- Manageable scope, high value

---

**Decision Required**: Which coverage level for initial DSL release?
