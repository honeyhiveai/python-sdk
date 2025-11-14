# Amazon Bedrock (LLM API Service) Analysis Report

**Date:** 2025-10-15  
**Analyst:** AI Assistant  
**Analysis Version:** Based on SDK_ANALYSIS_METHODOLOGY.md v1.3  
**Service Type:** Managed LLM API Service (accessed via Boto3)

---

## Executive Summary

- **Service Purpose:** AWS-managed LLM API service providing access to foundation models
- **Service Type:** API service (NOT an SDK - accessed via Boto3)
- **Client Library:** Boto3 `bedrock-runtime` and `bedrock-agent-runtime` clients
- **Observability:** No built-in tracing (provided by external instrumentors)
- **Existing Instrumentors:** ✅ **YES - 2 production-ready instrumentors exist!**
  - `openinference-instrumentation-bedrock` (OpenInference/Arize) - **Production/Stable**
  - `opentelemetry-instrumentation-bedrock` (Traceloop/OpenLLMetry) - **v0.47.3**
- **HoneyHive BYOI Compatible:** ✅ **YES** - Both instrumentors work with HoneyHive
- **Recommended Approach:** Use existing instrumentors (OpenInference or Traceloop)

### Key Distinction

⚠️ **IMPORTANT:** This is **Amazon Bedrock** (LLM API service), NOT **Amazon Bedrock AgentCore** (deployment platform).
- See `BEDROCK_VS_BEDROCK_AGENTCORE.md` for detailed comparison
- These are separate AWS services with different instrumentation strategies

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Phase 1.5: Instrumentor Discovery](#phase-15-instrumentor-discovery)
3. [Phase 2: API Client Discovery](#phase-2-api-client-discovery)
4. [Phase 3: Instrumentor Implementation Analysis](#phase-3-instrumentor-implementation-analysis)
5. [Phase 4: Gap Analysis](#phase-4-gap-analysis)
6. [Phase 5: HoneyHive Integration Strategy](#phase-5-honeyhive-integration-strategy)
7. [Recommendations](#recommendations)

---

## Service Overview

### What is Amazon Bedrock?

**Amazon Bedrock** is AWS's managed LLM API service - their equivalent of OpenAI API or Anthropic API.

**Key Characteristics:**
- Provides API access to multiple foundation models from various providers
- Pay-per-use pricing (no infrastructure management)
- Accessed via Boto3 (AWS SDK for Python)
- Supports multiple model families: Anthropic Claude, Meta Llama, Mistral, Amazon Titan, etc.
- Competes with: OpenAI API, Anthropic API, Google Vertex AI, Azure OpenAI

### Service Endpoints

| Service | Purpose | Boto3 Client |
|---------|---------|--------------|
| **bedrock-runtime** | Model inference (LLM calls) | `boto3.client('bedrock-runtime')` |
| **bedrock-agent-runtime** | Agent invocation & RAG | `boto3.client('bedrock-agent-runtime')` |
| **bedrock** | Model management (control plane) | `boto3.client('bedrock')` |

### Supported Models (Sample)

| Provider | Model ID Example | Notes |
|----------|-----------------|-------|
| **Anthropic** | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Claude 3/3.5 models |
| **Anthropic** | `anthropic.claude-v2` | Legacy Claude 2 |
| **Meta** | `meta.llama3-8b-instruct-v1:0` | Llama 3 models |
| **Mistral** | `mistral.mistral-7b-instruct-v0:2` | Mistral models |
| **Amazon** | `amazon.titan-text-express-v1` | Titan models |
| **AI21** | `ai21.j2-ultra-v1` | Jurassic models |
| **Cohere** | `cohere.command-text-v14` | Command models |

**Full list:** https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html

---

## Phase 1.5: Instrumentor Discovery

### Summary: Two Production-Ready Instrumentors Found ✅

| Provider | Package | Version | Status | GitHub Stars |
|----------|---------|---------|---------|--------------|
| **OpenInference (Arize)** | `openinference-instrumentation-bedrock` | Latest | **Production/Stable** | 657+ (parent repo) |
| **Traceloop (OpenLLMetry)** | `opentelemetry-instrumentation-bedrock` | v0.47.3 | **Active Development** | 6.5k+ (parent repo) |

### 1. OpenInference Bedrock Instrumentor

**Package Information:**
- **PyPI:** https://pypi.org/project/openinference-instrumentation-bedrock/
- **GitHub:** https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-bedrock
- **Development Status:** 5 - Production/Stable
- **Python Support:** >=3.9, <3.15
- **Minimum Boto3:** >=1.38.17
- **Minimum Botocore for Converse:** >=1.34.116

**Dependencies:**
```python
dependencies = [
    "opentelemetry-api",
    "opentelemetry-instrumentation",
    "opentelemetry-semantic-conventions",
    "openinference-instrumentation>=0.1.27",
    "openinference-semantic-conventions>=0.1.17",
    "wrapt",
    "typing-extensions",
    "dacite>=1.8.1",
]
```

**Installation:**
```bash
pip install openinference-instrumentation-bedrock
```

**Usage:**
```python
from openinference.instrumentation.bedrock import BedrockInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Set up tracer provider
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Instrument Bedrock
BedrockInstrumentor().instrument()

# Now all Bedrock API calls are traced
import boto3
client = boto3.client('bedrock-runtime')
response = client.converse(...)  # Traced!
```

**Supported API Methods:**
- ✅ `invoke_model()` (legacy API)
- ✅ `invoke_model_with_response_stream()` (streaming)
- ✅ `converse()` (unified API - requires botocore >=1.34.116)
- ✅ `converse_stream()` (streaming)
- ✅ `invoke_agent()` (Bedrock Agents - legacy)
- ✅ `invoke_inline_agent()` (inline agents)
- ✅ `retrieve()` (RAG retrieval)
- ✅ `retrieve_and_generate()` (RAG with generation)
- ✅ `retrieve_and_generate_stream()` (streaming RAG)

**Supported Models (Documented):**
- Anthropic Claude 2.0, 2.1 (converse, invoke)
- Anthropic Claude 3 Sonnet 1.0 (converse)
- Anthropic Claude 3.5 Sonnet (converse)
- Anthropic Claude 3 Haiku (converse)
- Meta Llama 3 8b/70b Instruct (converse)
- Mistral 7B/8X7B/Large/Small Instruct (converse)

**Semantic Conventions:**
- Uses **OpenInference Semantic Conventions**
- Span attributes follow OpenTelemetry standards
- Custom conventions for LLM-specific data

### 2. Traceloop Bedrock Instrumentor

**Package Information:**
- **PyPI:** https://pypi.org/project/opentelemetry-instrumentation-bedrock/
- **GitHub:** https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-bedrock
- **Version:** v0.47.3
- **Python Support:** >=3.9, <4
- **License:** Apache-2.0

**Dependencies:**
```python
dependencies = [
    "opentelemetry-api>=1.28.0",
    "opentelemetry-instrumentation>=0.55b0",
    "opentelemetry-semantic-conventions>=0.55b0",
    "opentelemetry-semantic-conventions-ai>=0.4.13",
    "anthropic>=0.17.0",
    "tokenizers>=0.13.0",
]
```

**Installation:**
```bash
pip install opentelemetry-instrumentation-bedrock
```

**Usage:**
```python
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

# Simple instrumentation
BedrockInstrumentor().instrument()

# Now all Bedrock API calls are traced
```

**Privacy Controls:**
```bash
# Disable content logging (for privacy)
export TRACELOOP_TRACE_CONTENT=false
```

**Features:**
- ✅ Prompts, completions, and embeddings logged by default
- ✅ Privacy controls via environment variable
- ✅ Event-based telemetry (span events for messages)
- ✅ Metrics support (tokens, latency, errors, guardrails)
- ✅ Guardrail telemetry (activation, latency, coverage)
- ✅ Prompt caching detection
- ✅ Streaming support

**Supported API Methods:**
- ✅ `invoke_model()`
- ✅ `invoke_model_with_response_stream()`
- ✅ `converse()`
- ✅ `converse_stream()`

**Advanced Features:**
- **Event Emission:** Uses OpenTelemetry Events for message content
- **Metrics:** Comprehensive metrics for tokens, guardrails, caching
- **Guardrail Support:** Detailed guardrail telemetry (activation, intervention types)
- **Prompt Caching:** Detects and tracks cache hits/misses

---

## Phase 2: API Client Discovery

### 2.1 Bedrock API Overview

Amazon Bedrock APIs are accessed via Boto3. There are **two main API styles**:

#### API Style 1: `invoke_model` (Legacy/Model-Specific)

**Characteristics:**
- Older API style
- Model-specific request/response formats
- Body is JSON string
- Works with all models but requires model-specific formatting

**Example:**
```python
import boto3
import json

client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Claude 2 format (example)
body = json.dumps({
    "prompt": "\\n\\nHuman: Hello\\n\\nAssistant:",
    "max_tokens_to_sample": 100,
    "temperature": 0.7
})

response = client.invoke_model(
    modelId='anthropic.claude-v2',
    body=body
)

response_body = json.loads(response['body'].read())
print(response_body['completion'])
```

**Streaming Version:**
```python
response = client.invoke_model_with_response_stream(
    modelId='anthropic.claude-v2',
    body=body
)

for event in response['body']:
    chunk = json.loads(event['chunk']['bytes'])
    print(chunk.get('completion', ''), end='')
```

#### API Style 2: `converse` (Unified/Modern)

**Characteristics:**
- Modern unified API (introduced in botocore 1.34.116)
- Standardized message format (similar to OpenAI/Anthropic)
- Works with most newer models
- **Recommended for new applications**

**Example:**
```python
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')

response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    messages=[
        {
            "role": "user",
            "content": [{"text": "Hello, how are you?"}]
        }
    ],
    inferenceConfig={
        "maxTokens": 512,
        "temperature": 0.7
    }
)

output = response['output']['message']
print(output['content'][0]['text'])
```

**Streaming Version:**
```python
response = client.converse_stream(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)

for event in response['stream']:
    if 'contentBlockDelta' in event:
        delta = event['contentBlockDelta']['delta']
        if 'text' in delta:
            print(delta['text'], end='', flush=True)
```

### 2.2 Additional Bedrock APIs

#### RAG APIs (Knowledge Base)

```python
client = boto3.client('bedrock-agent-runtime')

# Retrieve only
response = client.retrieve(
    knowledgeBaseId='KB123',
    retrievalQuery={'text': 'What is AI?'}
)

# Retrieve + Generate
response = client.retrieve_and_generate(
    input={'text': 'Explain AI'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'KB123',
            'modelArn': 'arn:aws:bedrock:...'
        }
    }
)
```

#### Agent APIs (Legacy Bedrock Agents)

```python
client = boto3.client('bedrock-agent-runtime')

response = client.invoke_agent(
    agentId='AGENT123',
    agentAliasId='ALIAS456',
    sessionId='session-789',
    inputText='Help me book a flight',
    enableTrace=True  # Enable tracing for agent steps
)

for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='')
    elif 'trace' in event:
        print(f"\\nTrace: {event['trace']}")
```

### 2.3 Request/Response Formats

#### `converse` API (Standardized)

**Request Structure:**
```python
{
    "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "messages": [
        {
            "role": "user|assistant",
            "content": [
                {"text": "string"},
                {"image": {"format": "png|jpeg|gif|webp", "source": {"bytes": "base64"}}},
                {"document": {"format": "pdf|csv|doc|...", "name": "...", "source": {"bytes": "base64"}}},
                {"toolUse": {"toolUseId": "...", "name": "...", "input": {...}}},
                {"toolResult": {"toolUseId": "...", "content": [...]}}
            ]
        }
    ],
    "system": [{"text": "System prompt"}],  # Optional
    "inferenceConfig": {
        "maxTokens": 512,
        "temperature": 0.7,
        "topP": 0.9,
        "stopSequences": ["..."]
    },
    "toolConfig": {  # Optional - for function calling
        "tools": [
            {
                "toolSpec": {
                    "name": "get_weather",
                    "description": "...",
                    "inputSchema": {"type": "object", "properties": {...}}
                }
            }
        ]
    },
    "guardranilConfig": {  # Optional - for content filtering
        "guardrailIdentifier": "...",
        "guardrailVersion": "..."
    }
}
```

**Response Structure:**
```python
{
    "ResponseMetadata": {...},
    "output": {
        "message": {
            "role": "assistant",
            "content": [
                {"text": "Response text"},
                {"toolUse": {"toolUseId": "...", "name": "...", "input": {...}}}
            ]
        }
    },
    "stopReason": "end_turn|tool_use|max_tokens|stop_sequence|content_filtered",
    "usage": {
        "inputTokens": 123,
        "outputTokens": 456,
        "totalTokens": 579
    },
    "metrics": {
        "latencyMs": 1234
    }
}
```

---

## Phase 3: Instrumentor Implementation Analysis

### 3.1 OpenInference Bedrock Instrumentor

#### Architecture

**Instrumentation Method:** Monkey-patching via `wrapt`

**How It Works:**
1. Wraps Boto3 client creation (`botocore.client.ClientCreator.create_client`)
2. Detects when `bedrock-runtime` or `bedrock-agent-runtime` clients are created
3. Wraps API methods (`invoke_model`, `converse`, `invoke_agent`, etc.)
4. Creates OpenTelemetry spans around API calls
5. Extracts request/response data and sets span attributes
6. Handles streaming responses via custom wrapper classes

**Key Implementation Files:**
- `__init__.py` - Main instrumentor class and client wrapping logic
- `_wrappers.py` - Streaming response wrappers
- `_attribute_extractor.py` - Attribute extraction from requests/responses
- `utils/anthropic/_attributes.py` - Claude-specific attribute handling
- `_converse_attributes.py` - Converse API attribute handling
- `_rag_wrappers.py` - RAG API wrappers

#### Span Creation

**Span Names:**
- `bedrock.invoke_model` - for `invoke_model()` calls
- `bedrock.converse` - for `converse()` calls
- `bedrock.invoke_agent` - for `invoke_agent()` calls
- `bedrock.retrieve` - for `retrieve()` calls
- `bedrock.retrieve_and_generate` - for `retrieve_and_generate()` calls

**SpanKind:** `SpanKind.CLIENT` (outgoing API call)

#### Attributes Captured

**OpenInference uses custom semantic conventions:**

**Model Information:**
- `llm.model_name` - Model ID (e.g., "anthropic.claude-3-5-sonnet")
- `llm.provider` - "bedrock"
- `llm.system` - Model family

**Request Attributes:**
- `llm.input_messages` - Input messages array
- `llm.prompt_template.template` - Prompt text (for invoke_model)
- `llm.invocation_parameters` - Inference config (temperature, max_tokens, etc.)
- `llm.tools` - Tool definitions (for function calling)

**Response Attributes:**
- `llm.output_messages` - Output messages array
- `llm.token_count.prompt` - Input tokens
- `llm.token_count.completion` - Output tokens
- `llm.token_count.total` - Total tokens

**Message Format (JSON):**
```json
{
    "message.role": "user|assistant",
    "message.content": "text content",
    "message.tool_calls": [{"tool.name": "...", "tool.parameters": {...}}]
}
```

**Streaming Support:**
- Custom `BufferedStreamingBody` class buffers stream for replay
- Allows reading stream multiple times (once for user, once for instrumentation)
- Span completed after stream is consumed

#### Special Features

**1. Claude Messages API Detection:**
```python
is_claude_message_api = _extract_invoke_model_attributes.is_claude_message_api(model_id)
```
- Detects if model uses Claude 3+ Messages API
- Applies appropriate attribute extraction logic

**2. RAG Support:**
- Captures knowledge base ID
- Captures retrieval queries and results
- Captures generated responses from RAG

**3. Agent Support:**
- Captures agent trace events (when `enableTrace=True`)
- Extracts agent steps and reasoning

### 3.2 Traceloop Bedrock Instrumentor

#### Architecture

**Instrumentation Method:** Monkey-patching via `wrapt` + Event-based telemetry

**How It Works:**
1. Similar client wrapping approach as OpenInference
2. Creates OpenTelemetry spans + span events
3. Emits OpenTelemetry metrics
4. Special handling for guardrails, prompt caching, streaming

**Key Implementation Files:**
- `__init__.py` - Main instrumentor with wrapping logic
- `span_utils.py` - Span attribute setters (~25KB - comprehensive)
- `event_emitter.py` - Event emission for message content
- `event_models.py` - Event data models
- `guardrail.py` - Guardrail telemetry (~8.6KB)
- `prompt_caching.py` - Prompt caching detection
- `streaming_wrapper.py` - Streaming support
- `reusable_streaming_body.py` - Buffered stream reading

#### Span Creation

**Span Names:**
- `bedrock.completion` - for `invoke_model()` calls
- `bedrock.converse` - for `converse()` calls

**SpanKind:** `SpanKind.CLIENT`

#### Attributes Captured

**Traceloop uses GenAI semantic conventions:**

**Model Information:**
- `gen_ai.system` - "bedrock"
- `gen_ai.request.model` - Model ID
- `server.address` - AWS region endpoint

**Request Attributes:**
- `gen_ai.request.temperature` - Temperature
- `gen_ai.request.max_tokens` - Max tokens
- `gen_ai.request.top_p` - Top P
- `gen_ai.prompt` - Prompt text (if `TRACELOOP_TRACE_CONTENT=true`)

**Response Attributes:**
- `gen_ai.completion` - Completion text (if content logging enabled)
- `gen_ai.usage.input_tokens` - Input tokens
- `gen_ai.usage.output_tokens` - Output tokens
- `gen_ai.response.finish_reason` - Stop reason

**Privacy Control:**
```bash
# Disable content logging
export TRACELOOP_TRACE_CONTENT=false
```
- When disabled: Only metadata (tokens, model, latency) logged
- When enabled: Full prompts and completions logged

#### Events (OpenTelemetry Events API)

**Traceloop uses span events for message content:**

**Event Types:**
- `gen_ai.user.message` - User messages
- `gen_ai.system.message` - System messages
- `gen_ai.assistant.message` - Assistant messages
- `gen_ai.tool.message` - Tool use/results

**Event Attributes (per message):**
```python
{
    "gen_ai.message.role": "user|assistant|system|tool",
    "gen_ai.message.content": "text content",
    "gen_ai.message.tool_calls": [...],  # For assistant tool calls
    "gen_ai.message.tool_call_id": "...",  # For tool results
}
```

**Why Events?**
- Keeps span attributes clean (no giant JSON blobs)
- Better for structured message history
- Easier to query individual messages

#### Metrics

**Traceloop provides comprehensive metrics:**

**Token Metrics:**
- `gen_ai.client.token.usage` (Histogram)
  - Labels: `gen_ai.token.type` (input/output)
  - Labels: `gen_ai.request.model`

**Operation Metrics:**
- `gen_ai.client.operation.duration` (Histogram) - Latency
- `gen_ai.client.generation.choices` (Counter) - Number of completions

**Error Metrics:**
- Exception counter for failed API calls

**Guardrail Metrics:**
- `gen_ai.client.guardrails.activation` (Counter) - Guardrail triggers
- `gen_ai.client.guardrails.latency` (Histogram) - Guardrail processing time
- `gen_ai.client.guardrails.coverage` (Counter) - Coverage type
- `gen_ai.client.guardrails.sensitive_information_policy` (Counter)
- `gen_ai.client.guardrails.topic_policy` (Counter)
- `gen_ai.client.guardrails.content_policy` (Counter)
- `gen_ai.client.guardrails.word_policy` (Counter)

**Prompt Caching Metrics:**
- `gen_ai.client.prompt_caching` (Counter)
  - Labels: `gen_ai.prompt.cache.result` (hit/miss)

#### Special Features

**1. Guardrail Telemetry:**
```python
# Automatic detection from response
if 'amazonBedrockGuardrailAction' in response:
    # Extract intervention type, actions, sensitive info, etc.
    # Emit metrics and span attributes
```

**Guardrail Span Attributes:**
- `gen_ai.guardrails.intervention` - Guardrail triggered (true/false)
- `gen_ai.guardrails.input.assessment` - Input assessment result
- `gen_ai.guardrails.output.assessment` - Output assessment result
- `gen_ai.guardrails.coverage` - Coverage types applied
- `gen_ai.guardrails.sensitive_information_policy.action` - Action taken

**2. Prompt Caching:**
```python
# Detects cache hits in usage metadata
if 'cacheReadInputTokens' in usage:
    # Emit cache hit metrics
```

**3. Multi-turn Conversation Support:**
- Tracks message sequences
- Maintains conversation context
- Proper indexing of messages

**4. Streaming Support:**
```python
class StreamingWrapper:
    # Buffers stream chunks
    # Accumulates full response
    # Sets final span attributes after stream completes
```

---

## Phase 4: Gap Analysis

### 4.1 Comparison: OpenInference vs Traceloop

| Feature | OpenInference | Traceloop | Winner |
|---------|--------------|-----------|---------|
| **Semantic Conventions** | OpenInference (custom) | GenAI (standard) | Traceloop ⭐ |
| **Message Handling** | Span attributes (JSON) | Span events (structured) | Traceloop ⭐ |
| **Metrics** | Not provided | Comprehensive | Traceloop ⭐ |
| **Privacy Controls** | Not documented | `TRACELOOP_TRACE_CONTENT` | Traceloop ⭐ |
| **Guardrail Telemetry** | Not provided | Detailed | Traceloop ⭐ |
| **Prompt Caching** | Not provided | Tracked | Traceloop ⭐ |
| **RAG Support** | ✅ Full support | Not documented | OpenInference ⭐ |
| **Agent Support** | ✅ invoke_agent, trace | Not documented | OpenInference ⭐ |
| **API Coverage** | 9 methods | 4 methods | OpenInference ⭐ |
| **Stability** | Production/Stable | v0.47.3 | OpenInference ⭐ |
| **Documentation** | Comprehensive | Minimal | OpenInference ⭐ |
| **Model Support Docs** | Explicit list | Not documented | OpenInference ⭐ |

**Summary:**
- **OpenInference:** Better API coverage (RAG, Agents), more stable, better documented
- **Traceloop:** Better observability (events, metrics, guardrails), standard conventions

### 4.2 Gaps in Both Instrumentors

**1. Multi-Model Orchestration**
- **Gap:** No tracking of which models are used in sequence
- **Impact:** Can't see agent switching between models
- **Example:** Agent uses Claude for reasoning, Titan for embeddings
- **Missing:** Parent-child span relationships across model calls

**2. Custom Metadata**
- **Gap:** No built-in way to add custom business metadata
- **Impact:** Can't correlate with application-specific context
- **Example:** User ID, session ID, business transaction ID
- **Workaround:** Manually set span attributes in user code

**3. Cost Tracking Beyond Tokens**
- **Gap:** No automatic cost calculation
- **Impact:** Token counts captured, but not $ cost
- **Example:** Different models have different pricing
- **Workaround:** Post-processing based on tokens + model pricing

**4. Latency Breakdown**
- **Gap:** Single latency metric (total API time)
- **Impact:** Can't see time-to-first-token vs generation time
- **Example:** Streaming: TTFT vs full completion time
- **Missing:** Streaming latency breakdown

**5. Request/Response Size**
- **Gap:** No tracking of payload sizes
- **Impact:** Can't detect oversized requests/responses
- **Example:** Large context windows, image inputs
- **Missing:** Byte counts for request/response

**6. Retry Logic**
- **Gap:** No automatic retry detection
- **Impact:** Can't see if API calls are being retried
- **Example:** Rate limiting, transient errors
- **Missing:** Retry attempt counts, backoff strategies

**7. Regional Failover**
- **Gap:** No tracking of region switching
- **Impact:** Can't see if fallback regions are used
- **Example:** us-east-1 fails, switches to us-west-2
- **Missing:** Region metadata in spans

**8. Batch Operations**
- **Gap:** No support for batch embeddings/classification
- **Impact:** Multiple API calls not grouped
- **Example:** Embedding 100 documents
- **Missing:** Parent span for batch operations

### 4.3 Model-Specific Gaps

**Anthropic Claude:**
- ✅ Well supported (both instrumentors)
- ⚠️ Prompt caching: Only Traceloop tracks it
- ⚠️ Extended thinking: Not captured separately

**Meta Llama:**
- ✅ Supported via converse API
- ⚠️ Model-specific parameters: Not all captured

**Mistral:**
- ✅ Supported via converse API
- ⚠️ Limited testing documented

**Amazon Titan:**
- ⚠️ No specific testing documented
- ⚠️ Embeddings: Not clear if supported

**Stability AI:**
- ❌ Image generation: Not documented
- ❌ No testing documented

### 4.4 Bedrock-Specific Feature Gaps

**Bedrock Guardrails:**
- ✅ Traceloop: Comprehensive support
- ❌ OpenInference: Not documented
- **Gap:** Guardrail cost not tracked (separate from model cost)

**Bedrock Agents (Legacy):**
- ✅ OpenInference: Supported (`invoke_agent`)
- ❌ Traceloop: Not documented
- **Gap:** Agent step details not fully captured

**Bedrock Knowledge Bases:**
- ✅ OpenInference: RAG methods supported
- ❌ Traceloop: Not documented
- **Gap:** Retrieval relevance scores not captured

**Cross-Region Inference:**
- ❌ Both: No tracking of cross-region calls
- **Gap:** Can't see if inference routed to different region

**Model Customization:**
- ❌ Both: No tracking of custom model usage
- **Gap:** Provisioned throughput not identified

---

## Phase 5: HoneyHive Integration Strategy

### 5.1 Recommended Approach

**Primary Recommendation:** Use **Traceloop** instrumentor for most use cases

**Rationale:**
1. ✅ Standard GenAI semantic conventions (better compatibility)
2. ✅ Span events for messages (better structure)
3. ✅ Comprehensive metrics (tokens, latency, guardrails)
4. ✅ Privacy controls (`TRACELOOP_TRACE_CONTENT`)
5. ✅ Guardrail telemetry (important for production)
6. ✅ Prompt caching visibility

**Alternative:** Use **OpenInference** if you need:
- RAG operations (Knowledge Bases)
- Bedrock Agents (legacy agents)
- More comprehensive API coverage

### 5.2 HoneyHive Integration Patterns

#### Pattern 1: Basic Integration (Traceloop)

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
import boto3

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    project="bedrock-app",
    api_key="YOUR_API_KEY",
    source="bedrock-runtime"
)

# Instrument Bedrock
BedrockInstrumentor().instrument()

# Use Bedrock normally
client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)

# ✅ Traced automatically in HoneyHive
```

**What Gets Captured:**
- ✅ Model ID
- ✅ Messages (if `TRACELOOP_TRACE_CONTENT=true`)
- ✅ Token usage
- ✅ Latency
- ✅ Stop reason
- ✅ Guardrail activations (if used)
- ✅ Metrics (tokens, latency)

---

#### Pattern 2: Privacy-Controlled Integration

```python
import os
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
import boto3

# Disable content logging for privacy
os.environ['TRACELOOP_TRACE_CONTENT'] = 'false'

tracer = HoneyHiveTracer.init(project="bedrock-app")
BedrockInstrumentor().instrument()

client = boto3.client('bedrock-runtime')
response = client.converse(...)

# ✅ Only metadata captured (no prompts/completions)
```

**What Gets Captured (Content Disabled):**
- ✅ Model ID
- ✅ Token counts
- ✅ Latency
- ✅ Stop reason
- ❌ Prompt text (privacy protected)
- ❌ Completion text (privacy protected)

---

#### Pattern 3: Integration with Custom Metadata

```python
from honeyhive import HoneyHiveTracer
from opentelemetry import trace
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
import boto3

tracer = HoneyHiveTracer.init(project="bedrock-app")
BedrockInstrumentor().instrument()

client = boto3.client('bedrock-runtime')

# Add custom metadata to current span
current_span = trace.get_current_span()
current_span.set_attribute("user.id", "user-123")
current_span.set_attribute("session.id", "session-456")
current_span.set_attribute("environment", "production")

response = client.converse(...)

# ✅ Custom metadata included in trace
```

---

#### Pattern 4: Multi-Model Orchestration

```python
from honeyhive import HoneyHiveTracer
from opentelemetry import trace
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
import boto3

tracer = HoneyHiveTracer.init(project="multi-model-app")
BedrockInstrumentor().instrument()

client = boto3.client('bedrock-runtime')

# Create parent span for orchestration
tracer_obj = trace.get_tracer(__name__)
with tracer_obj.start_as_current_span("agent_orchestration") as parent_span:
    parent_span.set_attribute("agent.type", "multi_model")
    parent_span.set_attribute("agent.version", "1.0")
    
    # Step 1: Use Claude for reasoning
    with tracer_obj.start_as_current_span("reasoning_step") as step1:
        step1.set_attribute("step.purpose", "reasoning")
        reasoning = client.converse(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            messages=[...]
        )
    
    # Step 2: Use Titan for embeddings
    with tracer_obj.start_as_current_span("embedding_step") as step2:
        step2.set_attribute("step.purpose", "embedding")
        embedding = client.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({"inputText": "..."})
        )
    
    # ✅ Full orchestration traced with hierarchy
```

---

#### Pattern 5: RAG with Knowledge Bases (OpenInference)

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.bedrock import BedrockInstrumentor
import boto3

# Use OpenInference for RAG support
tracer = HoneyHiveTracer.init(project="rag-app")
BedrockInstrumentor().instrument(tracer_provider=tracer.provider)

client = boto3.client('bedrock-agent-runtime')

# RAG operations automatically traced
response = client.retrieve_and_generate(
    input={'text': 'What is machine learning?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'KB123',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2'
        }
    }
)

# ✅ Retrieval + generation traced separately
```

---

#### Pattern 6: Guardrails Monitoring

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
import boto3

tracer = HoneyHiveTracer.init(project="bedrock-guardrails")
BedrockInstrumentor().instrument()

client = boto3.client('bedrock-runtime')

response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    messages=[{"role": "user", "content": [{"text": "..."}]}],
    guardrailConfig={
        'guardrailIdentifier': 'guardrail-123',
        'guardrailVersion': '1'
    }
)

# ✅ Guardrail telemetry captured automatically (Traceloop)
# - Activation events
# - Intervention types
# - Latency impact
# - Coverage metrics
```

---

### 5.3 Testing with HoneyHive

**Test Checklist:**

**Basic Functionality:**
- [ ] `invoke_model` traced correctly
- [ ] `converse` traced correctly
- [ ] Streaming responses captured
- [ ] Token counts accurate
- [ ] Latency captured

**Message Content:**
- [ ] User messages captured (if content enabled)
- [ ] Assistant messages captured
- [ ] System messages captured
- [ ] Message events structured correctly

**Tool Calling:**
- [ ] Tool definitions captured
- [ ] Tool calls captured
- [ ] Tool results captured
- [ ] Multi-turn tool use works

**Privacy:**
- [ ] `TRACELOOP_TRACE_CONTENT=false` works
- [ ] Only metadata captured when disabled
- [ ] Re-enabling works correctly

**Guardrails:**
- [ ] Guardrail activations captured
- [ ] Intervention types logged
- [ ] Guardrail metrics emitted
- [ ] Latency impact visible

**RAG (OpenInference only):**
- [ ] `retrieve` traced
- [ ] `retrieve_and_generate` traced
- [ ] Knowledge base ID captured
- [ ] Retrieval results captured

**Custom Metadata:**
- [ ] Can add custom span attributes
- [ ] Custom attributes appear in HoneyHive
- [ ] Span hierarchy preserved

---

## Recommendations

### For HoneyHive Documentation

**Create 3 Integration Guides:**

1. **"Instrumenting Amazon Bedrock with Traceloop"** (Primary)
   - Use case: General Bedrock API usage
   - Instrumentor: `opentelemetry-instrumentation-bedrock`
   - Features: Events, metrics, guardrails, privacy
   - Best for: Production applications with full observability needs

2. **"Instrumenting Amazon Bedrock with OpenInference"** (Alternative)
   - Use case: RAG and legacy Bedrock Agents
   - Instrumentor: `openinference-instrumentation-bedrock`
   - Features: RAG, agents, comprehensive API coverage
   - Best for: Applications using Knowledge Bases or Agents

3. **"Amazon Bedrock Privacy & Compliance"**
   - Privacy controls (`TRACELOOP_TRACE_CONTENT`)
   - Content filtering best practices
   - Guardrail monitoring
   - Compliance considerations

### Integration Decision Matrix

| Use Case | Recommended Instrumentor | Reason |
|----------|-------------------------|---------|
| **General LLM calls** | Traceloop | Events, metrics, privacy |
| **Function calling** | Traceloop | Better tool call tracking |
| **Guardrails** | Traceloop | Comprehensive guardrail telemetry |
| **Privacy-sensitive** | Traceloop | `TRACELOOP_TRACE_CONTENT` control |
| **RAG/Knowledge Bases** | OpenInference | Only one with RAG support |
| **Legacy Agents** | OpenInference | Only one with agent support |
| **Need stability** | OpenInference | Production/Stable status |

### Key Takeaways

1. **Two excellent instrumentors exist** - Both production-ready, choose based on needs
2. **Traceloop is more comprehensive** - Events, metrics, guardrails, privacy
3. **OpenInference has better coverage** - RAG, agents, more API methods
4. **Both work with HoneyHive BYOI** - Standard OpenTelemetry integration
5. **Privacy controls are critical** - Disable content logging for sensitive data
6. **Guardrail monitoring is unique** - Traceloop provides this, very valuable
7. **Test both for your use case** - Different strengths for different scenarios

---

## Appendix

### A. API Method Coverage Comparison

| API Method | OpenInference | Traceloop | Notes |
|------------|--------------|-----------|-------|
| `invoke_model` | ✅ | ✅ | Both support |
| `invoke_model_with_response_stream` | ✅ | ✅ | Streaming |
| `converse` | ✅ | ✅ | Requires botocore >= 1.34.116 |
| `converse_stream` | ✅ | ✅ | Streaming |
| `invoke_agent` | ✅ | ❌ | Legacy agents |
| `invoke_inline_agent` | ✅ | ❌ | Inline agents |
| `retrieve` | ✅ | ❌ | RAG retrieval |
| `retrieve_and_generate` | ✅ | ❌ | RAG + generation |
| `retrieve_and_generate_stream` | ✅ | ❌ | Streaming RAG |

### B. Semantic Conventions Used

**OpenInference:**
- `llm.model_name`
- `llm.provider`
- `llm.input_messages`
- `llm.output_messages`
- `llm.token_count.prompt`
- `llm.token_count.completion`
- `llm.token_count.total`
- `llm.invocation_parameters`
- `llm.tools`

**Traceloop:**
- `gen_ai.system`
- `gen_ai.request.model`
- `gen_ai.request.temperature`
- `gen_ai.request.max_tokens`
- `gen_ai.usage.input_tokens`
- `gen_ai.usage.output_tokens`
- `gen_ai.response.finish_reason`
- `gen_ai.prompt` (if content enabled)
- `gen_ai.completion` (if content enabled)
- `gen_ai.guardrails.*` (guardrail attributes)

### C. References

- **Amazon Bedrock:** https://aws.amazon.com/bedrock/
- **Bedrock API Docs:** https://docs.aws.amazon.com/bedrock/
- **OpenInference Bedrock:** https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-bedrock
- **Traceloop Bedrock:** https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-bedrock
- **Boto3 Docs:** https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html
- **HoneyHive BYOI:** https://docs.honeyhive.ai/byoi
- **Bedrock vs AgentCore Comparison:** `BEDROCK_VS_BEDROCK_AGENTCORE.md`

---

**Analysis completed:** 2025-10-15  
**Next steps:**
1. Test both instrumentors with HoneyHive BYOI
2. Create integration guides for each instrumentor
3. Document privacy and compliance best practices
4. Create decision matrix for choosing instrumentor
5. Monitor instrumentor updates for new features

