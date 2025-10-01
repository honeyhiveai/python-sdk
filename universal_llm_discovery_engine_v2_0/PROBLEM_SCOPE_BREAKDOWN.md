# Universal LLM Discovery Engine - Problem Scope Breakdown

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Clarification Document  

## 🎯 **The Core Problem: Two Distinct Challenges**

### **Challenge 1: Semantic Convention Diversity**
Different observability frameworks use different attribute names for the same concepts.

#### **Example: Model Name**
- **OpenInference**: `llm.model_name = "gpt-3.5-turbo"`
- **Traceloop**: `gen_ai.request.model = "gpt-3.5-turbo"`  
- **OpenLit**: `openlit.model = "gpt-3.5-turbo"`

#### **Example: Token Usage**
- **OpenInference**: `llm.token_count_prompt = 10`
- **Traceloop**: `gen_ai.usage.prompt_tokens = 10`
- **OpenLit**: `openlit.tokens.input = 10`

### **Challenge 2: LLM Provider Response Structure Diversity**
Each LLM provider returns data in completely different JSON structures.

#### **OpenAI Structure**
```json
{
  "id": "chatcmpl-123",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello!",
      "tool_calls": [{"id": "call_123", "function": {...}}],
      "refusal": null,
      "audio": {"id": "audio_123"}
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  },
  "model": "gpt-3.5-turbo"
}
```

#### **Anthropic Structure**
```json
{
  "id": "msg_123",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "Hello!"},
    {"type": "tool_use", "id": "toolu_123", "name": "function_name"}
  ],
  "model": "claude-3-sonnet",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 5
  }
}
```

#### **Google Gemini Structure**
```json
{
  "candidates": [{
    "content": {
      "parts": [{"text": "Hello!"}],
      "role": "model"
    },
    "finishReason": "STOP",
    "safetyRatings": [
      {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"}
    ]
  }],
  "usageMetadata": {
    "promptTokenCount": 10,
    "candidatesTokenCount": 5,
    "totalTokenCount": 15
  }
}
```

## 🔧 **Current Implementation Problems**

### **Problem 1: Static Field Mapping**
The current `_normalize_message` function only handles basic OpenAI structure:

```python
def _normalize_message(message_data):
    return {
        "role": message_data.get("role"),
        "content": message_data.get("content")
    }
```

**What's Missing:**
- OpenAI's new fields: `tool_calls`, `refusal`, `audio`, `name`, `tool_call_id`
- Anthropic's structure: `content` arrays, `tool_use` objects
- Gemini's structure: `parts` arrays, `functionCall` objects
- Usage metrics: Different field names across providers
- Model identification: Different locations and formats

### **Problem 2: Provider-Specific Hardcoding**
Each provider requires different parsing logic:

```python
# This approach doesn't scale
if provider == "openai":
    content = data["choices"][0]["message"]["content"]
elif provider == "anthropic":
    content = data["content"][0]["text"]  
elif provider == "gemini":
    content = data["candidates"][0]["content"]["parts"][0]["text"]
```

### **Problem 3: Schema Evolution**
Providers frequently add new fields:
- OpenAI added `tool_calls` (replacing `function_call`)
- OpenAI added `refusal` for safety
- OpenAI added `audio` for voice responses
- Each addition breaks static mapping

## 🎯 **Our Universal Solution Approach**

### **Dynamic Field Discovery**
Instead of hardcoding field locations, we:

1. **Analyze Response Structure**: Examine the JSON structure dynamically
2. **Classify Field Types**: Determine what each field represents (message, usage, config)
3. **Learn Patterns**: Build understanding of where different data types appear
4. **Map Semantically**: Convert to HoneyHive's unified schema

### **Example: Dynamic Message Content Discovery**

```python
# Instead of hardcoded paths, we discover dynamically
discovered_fields = {
    "choices.0.message.content": {
        "type": "MESSAGE_CONTENT",
        "confidence": 0.95,
        "provider_pattern": "openai"
    },
    "content.0.text": {
        "type": "MESSAGE_CONTENT", 
        "confidence": 0.90,
        "provider_pattern": "anthropic"
    },
    "candidates.0.content.parts.0.text": {
        "type": "MESSAGE_CONTENT",
        "confidence": 0.85,
        "provider_pattern": "gemini"
    }
}
```

### **Universal HoneyHive Schema Mapping**

All discovered fields map to HoneyHive's four-section schema:

```python
honeyhive_schema = {
    "inputs": {
        # User inputs, prompts, chat history
        "chat_history": extracted_messages,
        "system_prompt": extracted_system
    },
    "outputs": {
        # Model responses, completions, tool calls
        "content": extracted_content,
        "tool_calls": extracted_tool_calls,
        "finish_reason": extracted_finish_reason
    },
    "config": {
        # Model parameters, settings
        "model": extracted_model,
        "temperature": extracted_temperature
    },
    "metadata": {
        # Usage metrics, timestamps, provider info
        "usage": extracted_usage,
        "provider": detected_provider,
        "processing_time": processing_metrics
    }
}
```

## 🚀 **Why This Approach Works**

### **1. Provider Agnostic**
- Works with any LLM provider without code changes
- Automatically adapts to new providers

### **2. Future Proof**
- Handles new fields automatically
- Adapts to schema changes without updates

### **3. High Performance**
- O(1) field discovery using hash-based lookups
- Pre-computed classification patterns

### **4. Maintains Accuracy**
- Semantic understanding, not just pattern matching
- Confidence scoring for field classification

## 📋 **Implementation Scope**

### **What We're Building**
1. **Dynamic Field Discovery Engine**: Analyzes any JSON structure
2. **Semantic Classification System**: Understands what fields represent
3. **Universal Mapping Engine**: Converts to HoneyHive schema
4. **Provider Detection System**: Identifies LLM provider automatically
5. **Performance Optimization**: O(1) operations throughout

### **What We're Replacing**
1. **Static `_normalize_message` function**: Replace with dynamic discovery
2. **Hardcoded provider mappings**: Replace with learned patterns
3. **Manual field extraction**: Replace with automatic classification
4. **Provider-specific code paths**: Replace with universal processing

## 🎯 **Success Criteria**

### **Functional Success**
- [ ] Handle OpenAI responses (including new fields like `tool_calls`, `refusal`, `audio`)
- [ ] Handle Anthropic responses (content arrays, tool_use objects)
- [ ] Handle Gemini responses (parts arrays, safety ratings)
- [ ] Handle unknown providers gracefully
- [ ] Maintain >99% mapping accuracy

### **Performance Success**
- [ ] <10ms processing time per message
- [ ] O(1) performance characteristics
- [ ] <100MB memory usage per tracer instance
- [ ] Support 10,000+ messages/second

### **Operational Success**
- [ ] Zero breaking changes to existing APIs
- [ ] Seamless integration with current HoneyHive SDK
- [ ] Comprehensive monitoring and rollback capabilities

---

**The Universal LLM Discovery Engine solves both semantic convention diversity AND LLM provider response structure diversity with a single, dynamic, high-performance solution.**
