# OpenAI API Response Schemas

**Provider**: OpenAI  
**Last Updated**: 2025-01-30  
**API Version**: Current (as of 2025)  
**Official Documentation**: https://platform.openai.com/docs/api-reference/chat/object

---

## 📋 **Schema Extraction Methodology**

**Sources**:
1. OpenAI API Reference: https://platform.openai.com/docs/api-reference/chat/object
2. OpenAI Chat Completions: https://platform.openai.com/docs/api-reference/chat/create
3. Structured Outputs: https://openai.com/index/introducing-structured-outputs-in-the-api/

**Extraction Date**: 2025-01-30  
**Purpose**: Document exact structure of OpenAI response objects for DSL design

---

## 🎯 **Core Response Object**

### **1. Chat Completion Response (Basic)**

**Endpoint**: `POST /v1/chat/completions`

**Response Structure**:

```typescript
interface ChatCompletionResponse {
  id: string;                           // Unique identifier, e.g. "chatcmpl-123"
  object: "chat.completion";            // Object type (literal)
  created: number;                      // Unix timestamp
  model: string;                        // Model used, e.g. "gpt-4o-2024-08-06"
  choices: ChatCompletionChoice[];      // Array of completion choices
  usage: UsageInfo;                     // Token usage information
  system_fingerprint?: string;          // System configuration fingerprint
  service_tier?: string;                // Service tier used (if applicable)
}
```

**JSON Example**:

```json
{
  "id": "chatcmpl-9nYAG9LPNonX8DAyrkwYfemr3C8HC",
  "object": "chat.completion",
  "created": 1721596428,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 9,
    "total_tokens": 21
  },
  "system_fingerprint": "fp_3407719c7f"
}
```

---

## 💬 **Message Object Structures**

### **2. Basic Message (Text Only)**

```typescript
interface ChatCompletionMessage {
  role: "assistant" | "user" | "system" | "tool";
  content: string | null;               // Text content, can be null
  name?: string;                        // Optional name for the participant
  refusal?: string;                     // ⚠️ NEW: Model refusal message
}
```

**JSON Example**:

```json
{
  "role": "assistant",
  "content": "Paris is the capital of France."
}
```

### **3. Message with Refusal** ⚠️ NEW

```typescript
interface RefusalMessage {
  role: "assistant";
  content: null;                        // Content is null when refused
  refusal: string;                      // Refusal explanation
}
```

**JSON Example**:

```json
{
  "role": "assistant",
  "content": null,
  "refusal": "I'm sorry, I cannot assist with that request."
}
```

---

## 🛠️ **Tool Calls (Function Calling)**

### **4. Message with Tool Calls**

```typescript
interface ToolCallMessage {
  role: "assistant";
  content: string | null;               // Can be null if only tool calls
  tool_calls: ToolCall[];               // Array of tool calls
}

interface ToolCall {
  id: string;                           // Unique ID, e.g. "call_abc123"
  type: "function";                     // Currently only "function"
  function: FunctionCall;
}

interface FunctionCall {
  name: string;                         // Function name
  arguments: string;                    // ⚠️ JSON STRING, not object!
}
```

**JSON Example**:

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
        "arguments": "{\"location\": \"San Francisco\", \"unit\": \"celsius\"}"
      }
    }
  ]
}
```

**⚠️ CRITICAL NOTES**:
1. `function.arguments` is a **JSON STRING**, not a parsed object
2. Must parse this string to get actual parameters
3. Can have multiple tool_calls in one message
4. content can be null when only returning tool calls

---

## 🎵 **Audio Responses** ⚠️ NEW

### **5. Message with Audio**

```typescript
interface AudioMessage {
  role: "assistant";
  content: string;                      // Text content
  audio?: AudioData;                    // Optional audio data
}

interface AudioData {
  id: string;                           // Audio ID
  expires_at: number;                   // Unix timestamp
  data: string;                         // Base64 encoded audio
  transcript: string;                   // Text transcript
}
```

**JSON Example**:

```json
{
  "role": "assistant",
  "content": "Hello, I'm speaking to you.",
  "audio": {
    "id": "audio_abc123",
    "expires_at": 1721600000,
    "data": "SGVsbG8gd29ybGQ=",
    "transcript": "Hello, I'm speaking to you."
  }
}
```

---

## 🎨 **Multimodal Content (Images)**

### **6. User Message with Image**

**Input Structure** (for reference):

```typescript
interface MultimodalUserMessage {
  role: "user";
  content: ContentPart[];               // Array of content parts
}

type ContentPart = TextContent | ImageContent;

interface TextContent {
  type: "text";
  text: string;
}

interface ImageContent {
  type: "image_url";
  image_url: {
    url: string;                        // URL or base64 data URL
    detail?: "low" | "high" | "auto";   // Image detail level
  };
}
```

**JSON Example (Input)**:

```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "What's in this image?"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/image.jpg",
        "detail": "high"
      }
    }
  ]
}
```

**Response**: Standard text response (assistant doesn't return images)

---

## 📊 **Usage Information**

### **7. Usage Object**

```typescript
interface UsageInfo {
  prompt_tokens: number;                // Input tokens
  completion_tokens: number;            // Output tokens
  total_tokens: number;                 // Sum of input + output
  prompt_tokens_details?: {
    cached_tokens?: number;             // Cached prompt tokens
    audio_tokens?: number;              // Audio input tokens
  };
  completion_tokens_details?: {
    reasoning_tokens?: number;          // ⚠️ NEW: Reasoning tokens (o1 models)
    audio_tokens?: number;              // Audio output tokens
  };
}
```

**JSON Example (Basic)**:

```json
{
  "prompt_tokens": 56,
  "completion_tokens": 31,
  "total_tokens": 87
}
```

**JSON Example (With Details)**:

```json
{
  "prompt_tokens": 100,
  "completion_tokens": 50,
  "total_tokens": 150,
  "prompt_tokens_details": {
    "cached_tokens": 20
  },
  "completion_tokens_details": {
    "reasoning_tokens": 10
  }
}
```

---

## 🚦 **Finish Reasons**

### **8. Possible Finish Reasons**

```typescript
type FinishReason =
  | "stop"              // Natural completion
  | "length"            // Max tokens reached
  | "tool_calls"        // Model wants to call tool
  | "content_filter"    // Content filtered by safety system
  | "function_call";    // Legacy function calling (deprecated)
```

**Mapping**:
- `stop`: Completed normally
- `length`: Hit max_tokens limit
- `tool_calls`: Requesting tool execution
- `content_filter`: Safety system intervened
- `function_call`: Old function calling (use tool_calls instead)

---

## ❌ **Error Responses**

### **9. Error Object**

```typescript
interface ErrorResponse {
  error: {
    message: string;                    // Human-readable error
    type: string;                       // Error type
    param: string | null;               // Parameter that caused error
    code: string | null;                // Error code
  };
}
```

**JSON Example**:

```json
{
  "error": {
    "message": "Invalid API key provided",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

**Common Error Types**:
- `invalid_request_error`: Bad request parameters
- `authentication_error`: Invalid API key
- `permission_error`: Insufficient permissions
- `not_found_error`: Resource not found
- `rate_limit_error`: Rate limit exceeded
- `api_error`: Server error
- `service_unavailable`: Temporary unavailability

---

## 🎯 **DSL Implications**

### **Key Observations for Transform Design**:

1. **Tool Call Arguments as JSON Strings**:
   ```json
   "arguments": "{\"location\": \"SF\"}"  // ← STRING, not object!
   ```
   **DSL Need**: JSON parsing transform

2. **Nullable Content**:
   ```json
   "content": null  // ← Can be null for tool_calls or refusals
   ```
   **DSL Need**: Null-safe extraction

3. **Optional Fields**:
   ```typescript
   refusal?: string;
   audio?: AudioData;
   ```
   **DSL Need**: Optional field handling

4. **Nested Usage Details**:
   ```json
   "completion_tokens_details": {
     "reasoning_tokens": 10
   }
   ```
   **DSL Need**: Nested object navigation

5. **Array of Tool Calls**:
   ```json
   "tool_calls": [...]  // ← Array, not single object
   ```
   **DSL Need**: Array iteration/extraction

---

## 📝 **Complete Response Examples**

### **Example 1: Basic Chat**

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1721596428,
  "model": "gpt-4o",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 6,
    "total_tokens": 16
  }
}
```

### **Example 2: Tool Calls**

```json
{
  "id": "chatcmpl-456",
  "object": "chat.completion",
  "created": 1721596500,
  "model": "gpt-4o",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\":\"Boston\",\"unit\":\"fahrenheit\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }],
  "usage": {
    "prompt_tokens": 82,
    "completion_tokens": 17,
    "total_tokens": 99
  }
}
```

### **Example 3: Refusal**

```json
{
  "id": "chatcmpl-789",
  "object": "chat.completion",
  "created": 1721596600,
  "model": "gpt-4o",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": null,
      "refusal": "I cannot help with that request."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 8,
    "total_tokens": 23
  }
}
```

---

## 🔄 **Streaming Responses** (Optional Research)

**Note**: Streaming uses Server-Sent Events (SSE) with delta updates.  
**TODO**: Document streaming schema if needed for DSL design.

---

## ✅ **Research Status**

- [x] Basic chat completion structure
- [x] Message object variations
- [x] Tool calls structure
- [x] Audio response structure
- [x] Usage information (including new fields)
- [x] Finish reasons
- [x] Error responses
- [x] Multimodal input structure (reference)
- [ ] Streaming response format (deferred)

---

**Next Steps**: Extract Anthropic response schemas for comparison
