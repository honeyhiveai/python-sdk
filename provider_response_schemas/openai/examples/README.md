# OpenAI Response Examples

This directory contains real and schema-based examples of OpenAI API responses for validation and testing purposes.

---

## 📊 **Inventory**

**Total Examples**: 11  
**Last Updated**: 2025-09-30  
**Source**: OpenAPI spec v2.3.0 + manual creation based on schema

---

## 🟢 **Basic Examples** (4)

### `basic_chat.json`
- **Description**: Simple Q&A text completion
- **Scenario**: User asks "What is the capital of France?"
- **Key Features**: Basic content field, stop finish_reason
- **Source**: Manual creation

### `multimodal_image.json`
- **Description**: Vision/multimodal image description response
- **Scenario**: User provides image, model describes it
- **Key Features**: Extended usage details with token breakdowns
- **Source**: OpenAPI spec v2.3.0 official example

### `streaming_chunk.json`
- **Description**: Streaming response delta chunk
- **Scenario**: Chunk during streaming generation
- **Key Features**: Uses `delta` instead of `message`, `object: "chat.completion.chunk"`
- **Source**: Based on CreateChatCompletionStreamResponse schema

### `multiple_choices.json`
- **Description**: Multiple completions (n parameter > 1)
- **Scenario**: User requests 2 different completions
- **Key Features**: Multiple items in choices array
- **Source**: Based on CreateChatCompletionResponse schema

---

## 🔴 **Edge Case Examples** (7)

### `tool_calls.json`
- **Description**: Function calling with tool invocation
- **Scenario**: User asks about weather, model calls get_weather function
- **Key Features**: **CRITICAL** - `function.arguments` is JSON **string**, not object
- **Source**: Manual creation based on schema
- **Note**: finish_reason is "tool_calls"

### `refusal.json`
- **Description**: Safety refusal response
- **Scenario**: User request violates usage policies
- **Key Features**: `content` is null, `refusal` field contains explanation
- **Source**: Manual creation based on schema
- **Note**: finish_reason is "stop"

### `error_response.json`
- **Description**: API error response structure
- **Scenario**: Rate limit exceeded
- **Key Features**: Different structure (error object, not completion)
- **Source**: Based on OpenAI API error format
- **Note**: Used for API-level errors, not completion responses

### `content_filter.json`
- **Description**: Content filter trigger response
- **Scenario**: Model stops due to content filter
- **Key Features**: finish_reason is "content_filter", content is null
- **Source**: Based on CreateChatCompletionResponse schema

### `max_tokens.json`
- **Description**: Maximum token limit reached
- **Scenario**: Response truncated at token limit
- **Key Features**: finish_reason is "length", content is incomplete
- **Source**: Based on CreateChatCompletionResponse schema

### `audio_response.json`
- **Description**: Audio modality response
- **Scenario**: Model generates audio output (gpt-4o-audio-preview)
- **Key Features**: `audio` object with base64 data, transcript, expiration
- **Source**: Based on ChatCompletionResponseMessage audio field
- **Note**: audio_tokens in completion_tokens_details

### `logprobs_response.json`
- **Description**: Response with token-level log probabilities
- **Scenario**: User requests logprobs for model confidence
- **Key Features**: `logprobs.content` array with token probabilities
- **Source**: Based on CreateChatCompletionResponse logprobs schema
- **Note**: Includes top_logprobs for alternative tokens

---

## 🎯 **Critical Schema Findings**

### Tool Call Arguments Format
The `tool_calls[].function.arguments` field is a **JSON string**, not a parsed object:
```json
"arguments": "{\"location\": \"San Francisco\", \"unit\": \"celsius\"}"
```

This requires JSON parsing transform in the DSL to extract actual argument values.

### Content Field Nullability
The `content` field can be `null` in these cases:
- Tool calls (content is null, tool_calls is present)
- Refusals (content is null, refusal is present)
- Content filter (content is null or partial)

### Finish Reasons
- `stop` - Natural completion or stop sequence
- `length` - Token limit reached
- `tool_calls` - Model called a tool/function
- `content_filter` - Content filter triggered
- `function_call` - (Deprecated) Legacy function calling

### Usage Details Structure
Extended usage breakdowns:
- `prompt_tokens_details` - cached_tokens, audio_tokens
- `completion_tokens_details` - reasoning_tokens, audio_tokens, prediction tokens

---

## 🔄 **Usage**

These examples are used for:
1. **JSON Schema Validation** - Validate provider response schemas
2. **DSL Testing** - Test field extraction and transforms
3. **Integration Testing** - Verify instrumentor processing
4. **Documentation** - Reference examples for developers

---

## 📝 **Maintenance**

When OpenAI API changes:
1. Download new OpenAPI spec
2. Extract new official examples
3. Update existing examples if schema changes
4. Add new examples for new features
5. Update this README

---

**Framework Version**: 1.0 (SDK-First)  
**Validated**: 2025-09-30  
**All Examples**: ✅ Valid JSON
