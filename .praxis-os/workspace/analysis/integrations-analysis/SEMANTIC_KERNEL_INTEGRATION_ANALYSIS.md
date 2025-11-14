# Microsoft Semantic Kernel Analysis Report
## Integration Strategy for HoneyHive BYOI Architecture

**Date:** October 15, 2025  
**Analyst:** AI Assistant  
**Methodology:** SDK Analysis Methodology v1.0  
**Analysis Location:** `/tmp/sdk-analysis/semantic-kernel`

---

## Executive Summary

- **SDK Purpose:** Enterprise-ready orchestration framework for building AI agents and multi-agent systems
- **LLM Client:** OpenAI SDK (`openai >= 1.98.0`) with support for Azure OpenAI, Anthropic, Google AI, AWS Bedrock, and others
- **Observability:** **Built-in OpenTelemetry instrumentation** (experimental, opt-in via environment variables)
- **Recommendation:** **Option A - Standard OpenAI Instrumentors** (Easiest, works immediately) + **Option C - TracerProvider Injection** (Full integration with SK's built-in telemetry)

---

## Architecture Overview

```
Microsoft Semantic Kernel Architecture:
├── Kernel (Central Orchestrator)
│   ├── AI Services (Chat, Embeddings, TTS, etc.)
│   ├── Plugins (Functions, Tools)
│   └── Memory (Context Management)
├── Agents Framework
│   ├── ChatCompletionAgent
│   ├── OpenAI Assistant Agent
│   ├── Azure AI Agent
│   └── Multi-Agent Orchestration
├── Connectors
│   ├── OpenAI (AsyncOpenAI, AsyncAzureOpenAI)
│   ├── Anthropic
│   ├── Google AI / Vertex AI
│   ├── AWS Bedrock
│   ├── Ollama, ONNX, Hugging Face
│   └── Memory Stores (15+ vector DBs)
└── Telemetry (OpenTelemetry)
    ├── Model Diagnostics (LLM calls)
    ├── Agent Diagnostics (Agent invocations)
    └── Function Diagnostics (Tool calls)
```

---

## Key Findings

### 1. Repository Metadata

**Language:** Python 3.10+  
**Files:** 552 Python files (77,709 lines of code)  
**Version:** Production/Stable (v1.x)  
**License:** MIT  
**Repository:** https://github.com/microsoft/semantic-kernel

**Core Dependencies:**
```toml
openai >= 1.98.0                # Required
opentelemetry-api ~= 1.24       # Built-in
opentelemetry-sdk ~= 1.24       # Built-in
pydantic >=2.0,<2.12            # Data validation
aiohttp ~= 3.8                  # Async HTTP
```

**Optional LLM Provider Dependencies:**
- `anthropic ~= 0.32`
- `google-cloud-aiplatform == 1.97.0`
- `boto3 >= 1.36.4` (AWS Bedrock)
- `mistralai >= 1.2`
- `ollama ~= 0.4`

### 2. LLM Client Usage

#### 2.1 Client Instantiation

**Primary Pattern:** Semantic Kernel creates LLM clients internally, but **also accepts pre-configured clients**:

```python
# Pattern 1: SK creates client internally
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

service = AzureChatCompletion(
    deployment_name="gpt-4",
    api_key="your-api-key",
    endpoint="your-endpoint"
)
# SK creates AsyncAzureOpenAI internally

# Pattern 2: Pass existing client (user-controlled)
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

my_client = AsyncOpenAI(api_key="...")
service = OpenAIChatCompletion(
    ai_model_id="gpt-4",
    async_client=my_client  # ✅ User controls the client!
)
```

**Client Creation Files:**
- `semantic_kernel/connectors/ai/open_ai/services/open_ai_config_base.py:68` - Creates `AsyncOpenAI`
- `semantic_kernel/connectors/ai/open_ai/services/azure_config_base.py:114` - Creates `AsyncAzureOpenAI`

**API Call Sites:**
- All services in `semantic_kernel/connectors/ai/open_ai/services/` make API calls
- Decorated with `@trace_chat_completion` or `@trace_streaming_chat_completion`

### 3. Observability System

#### 3.1 Built-in OpenTelemetry Tracing

**Type:** ✅ **OpenTelemetry-based** (experimental, opt-in)

**Components:**
```
semantic_kernel/utils/telemetry/
├── model_diagnostics/          # LLM call tracing
│   ├── decorators.py           # @trace_chat_completion decorators
│   ├── gen_ai_attributes.py    # OpenTelemetry semantic conventions
│   └── model_diagnostics_settings.py  # Enable via env vars
├── agent_diagnostics/          # Agent invocation tracing
│   ├── decorators.py           # @trace_agent_invocation decorators
│   └── gen_ai_attributes.py    # Agent-specific attributes
└── user_agent.py               # HTTP User-Agent management
```

**Activation:**
Set environment variables to enable:
```bash
# Enable basic diagnostics
export SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS=true

# Enable diagnostics with sensitive data (prompts/responses)
export SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE=true
```

**Span Model:**
```python
# SK uses standard OpenTelemetry spans
from opentelemetry.trace import get_tracer

tracer = get_tracer(__name__)
span = tracer.start_span(f"chat.completions {model_name}")
span.set_attributes({
    "gen_ai.operation.name": "chat.completions",
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4",
    "gen_ai.request.temperature": 0.7,
    "gen_ai.usage.input_tokens": 150,
    "gen_ai.usage.output_tokens": 50,
})
```

**Semantic Conventions:**
Follows OpenTelemetry GenAI semantic conventions:
- https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/

#### 3.2 Instrumentation Decorators

SK decorates its service methods with custom tracing decorators:

```python
# In semantic_kernel/connectors/ai/open_ai/services/open_ai_chat_completion_base.py

from semantic_kernel.utils.telemetry.model_diagnostics import trace_chat_completion

class OpenAIChatCompletionBase:
    @trace_chat_completion(model_provider="openai")
    async def get_chat_message_contents(
        self,
        chat_history: ChatHistory,
        settings: PromptExecutionSettings,
        **kwargs: Any,
    ) -> list[ChatMessageContent]:
        # Makes OpenAI API call
        # Decorator automatically creates span, logs input/output
        pass
```

**Available Decorators:**
- `@trace_chat_completion` - Chat completion calls
- `@trace_streaming_chat_completion` - Streaming chat calls
- `@trace_text_completion` - Text completion calls
- `@trace_streaming_text_completion` - Streaming text calls
- `@trace_agent_invocation` - Agent execution
- `@trace_agent_get_response` - Agent single response

### 4. Integration Points

#### 4.1 TracerProvider Injection

✅ **YES** - SK uses `get_tracer()` from global TracerProvider

```python
# In semantic_kernel/utils/telemetry/model_diagnostics/decorators.py:71
from opentelemetry.trace import get_tracer

tracer = get_tracer(__name__)
```

**This means:** If you set a custom TracerProvider globally, SK will use it automatically!

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from honeyhive import HoneyHiveTracer

# Set up HoneyHive as global TracerProvider
tracer = HoneyHiveTracer.init(
    api_key="your-key",
    project="semantic-kernel-demo"
)

# SK will automatically use HoneyHive's TracerProvider!
trace.set_tracer_provider(tracer.provider)
```

#### 4.2 Client Wrapping

✅ **YES** - Services accept pre-configured OpenAI clients

All SK services accept an optional `async_client` or `client` parameter:

```python
# semantic_kernel/connectors/ai/open_ai/services/open_ai_chat_completion.py:30
def __init__(
    self,
    ai_model_id: str,
    api_key: str | None = None,
    org_id: str | None = None,
    service_id: str | None = None,
    async_client: AsyncOpenAI | None = None,  # ✅ Pass your own client!
    **kwargs: Any,
) -> None:
```

**This means:** You can create an instrumented OpenAI client and pass it to SK!

#### 4.3 Lifecycle Hooks

⚠️ **PARTIAL** - No direct lifecycle hooks, but:
- Environment variable based activation
- Global TracerProvider integration
- Decorator-based instrumentation

---

## Integration Strategy

### Key Insight: Two Different Instrumentation Layers

**Important:** Understanding what gets instrumented where is crucial:

| What | SK's Telemetry | OpenAI Instrumentor |
|------|----------------|---------------------|
| **Instruments** | Semantic Kernel's service methods | OpenAI SDK library methods |
| **Layer** | Application/Framework layer | SDK/Library layer |
| **Mechanism** | Decorators on SK methods (`@trace_chat_completion`) | Monkey-patching OpenAI SDK (`client.chat.completions.create`) |
| **Captures** | Agent context, SK metadata, extracted tokens/responses | HTTP requests, retries, network timing, request/response bodies |
| **Example Span Name** | `"chat.completions gpt-4"` | `"ChatCompletion.create"` |
| **Activation** | Environment variables | Instrumentor initialization |

**When SK calls OpenAI:**
```python
# What happens inside Semantic Kernel:
@trace_chat_completion(model_provider="openai")  # ← SK's decorator wraps this
async def get_chat_message_contents(self, ...):
    # SK creates a span here (SK layer)
    response = await self.client.chat.completions.create(...)  # ← OpenAI SDK call
    # ↑ This call is only instrumented if OpenAI Instrumentor is active!
    return self._process_response(response)
```

**Result:**
- **With SK telemetry only:** One span at SK service layer, extracts metadata from response
- **With OpenAI instrumentor only:** One span at SDK layer, captures HTTP details
- **With both (hybrid):** Nested spans showing both layers (recommended!)

### Multi-Provider Support

**Important:** Semantic Kernel supports **9+ LLM providers**, each with SK telemetry at the service layer:

| Provider | SK Telemetry | Underlying SDK | Recommended Instrumentor |
|----------|-------------|----------------|--------------------------|
| **OpenAI** | ✅ `model_provider="openai"` | `openai` SDK | OpenInference/Traceloop OpenAI |
| **Azure OpenAI** | ✅ `model_provider="openai"` | `openai` SDK | OpenInference/Traceloop OpenAI |
| **Anthropic** | ✅ `model_provider="anthropic"` | `anthropic` SDK | OpenInference/Traceloop Anthropic |
| **Google AI** | ✅ `model_provider="googleai"` | `google-generativeai` | OpenInference/Traceloop Google |
| **Vertex AI** | ✅ `model_provider="vertexai"` | `google-cloud-aiplatform` | OpenInference/Traceloop Google |
| **AWS Bedrock** | ✅ `model_provider="bedrock"` | `boto3` | OpenInference/Traceloop Bedrock |
| **Mistral AI** | ✅ `model_provider="mistralai"` | `mistralai` SDK | OpenInference/Traceloop Mistral |
| **Ollama** | ✅ `model_provider="ollama"` | `ollama` SDK | OpenInference Ollama |
| **Nvidia** | ✅ `model_provider="nvidia"` | `openai` SDK (compatible) | OpenInference OpenAI |
| **Hugging Face** | ✅ `model_provider="huggingface"` | `transformers` | Not typically instrumented |

**Key Insight:** For each provider you use, you should initialize the corresponding instrumentor for SDK-layer coverage!

**Example with multiple providers:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from openinference.instrumentation.bedrock import BedrockInstrumentor

# Initialize HoneyHive with instrumentors for all providers you use
tracer = HoneyHiveTracer.init(
    project="multi-provider-app",
    api_key="your-key",
    instrumentors=[
        OpenAIInstrumentor(),      # For OpenAI/Azure OpenAI
        AnthropicInstrumentor(),   # For Anthropic Claude
        BedrockInstrumentor(),     # For AWS Bedrock
    ]
)
```

### Recommended Approach: **Hybrid with Multi-Provider Support**

Combine **Provider-Specific Instrumentors** with **TracerProvider Injection** for complete coverage across all providers.

### Option A: Provider-Specific Instrumentors (Easiest)

**Why:** SK creates LLM client instances internally (OpenAI, Anthropic, etc.). Provider-specific instrumentors will automatically catch these SDK calls.

**Important:** Use the instrumentor(s) that match the provider(s) you're using in your SK application!

**Implementation (Single Provider):**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize HoneyHive with OpenAI instrumentor
tracer = HoneyHiveTracer.init(
    project="semantic-kernel-app",
    api_key="your-honeyhive-api-key",
    instrumentors=[OpenAIInstrumentor()]
)

# Use Semantic Kernel with OpenAI
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="SK-Assistant",
    instructions="You are a helpful assistant.",
)

# LLM calls are automatically traced! ✅
response = await agent.get_response(messages="Hello!")
```

**Implementation (Multiple Providers):**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

# Initialize with multiple instrumentors
tracer = HoneyHiveTracer.init(
    project="multi-model-app",
    api_key="your-honeyhive-api-key",
    instrumentors=[
        OpenAIInstrumentor(),      # For GPT-4
        AnthropicInstrumentor(),   # For Claude
    ]
)

# Use different providers in SK
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion

gpt_agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="GPT-Agent"
)

claude_agent = ChatCompletionAgent(
    service=AnthropicChatCompletion(),
    name="Claude-Agent"
)

# Both providers are traced! ✅
```

**Pros:**
- ✅ Works immediately with zero SK configuration
- ✅ Captures all LLM API calls across all providers you use
- ✅ No code changes to SK usage
- ✅ Compatible with HoneyHive BYOI architecture
- ✅ Provider-agnostic: works with any provider SK supports

**Cons:**
- ❌ Missing agent-specific context (agent names, instructions, multi-agent flows)
- ❌ Missing SK plugin/function calling details
- ❌ Missing SK-specific metadata (kernel info, planning steps)
- ⚠️ Must remember to add instrumentor for each provider you use

### Option B: TracerProvider Injection (SK Telemetry Only)

**Why:** SK's built-in telemetry provides agent-level and function-level spans. Inject HoneyHive's TracerProvider to capture SK's spans without additional instrumentors.

**Important:** This option relies entirely on SK's telemetry. SK creates spans at its service layer and extracts metadata from response objects. The actual OpenAI SDK HTTP calls are NOT instrumented separately (but SK's spans capture the same information from the response).

**Implementation:**
```python
import os
from honeyhive import HoneyHiveTracer
from opentelemetry import trace

# Enable SK's built-in telemetry
os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true"
os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] = "true"

# Initialize HoneyHive and set as global TracerProvider
tracer = HoneyHiveTracer.init(
    project="semantic-kernel-app",
    api_key="your-honeyhive-api-key",
)

# Make HoneyHive the global TracerProvider
# SK will automatically use it via get_tracer()
trace.set_tracer_provider(tracer.provider)

# Use Semantic Kernel normally
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="ResearchAgent",
    instructions="You are a research assistant.",
)

# SK's built-in telemetry creates spans with agent context! ✅
response = await agent.get_response(messages="Research quantum computing")
```

**Pros:**
- ✅ Captures agent-level spans (agent name, description, instructions)
- ✅ Captures function/tool calling spans
- ✅ Captures multi-agent orchestration flows
- ✅ Follows OpenTelemetry GenAI semantic conventions
- ✅ Rich metadata (tokens, temperature, model, finish reasons)

**Cons:**
- ⚠️ Requires environment variables to be set (no tracing if disabled!)
- ⚠️ SK telemetry is marked "experimental" (API may change)
- ⚠️ No HTTP-level details (retries, network errors) - only SK-layer spans
- ⚠️ Single point of failure - if SK's telemetry breaks, you have no tracing

### Option C: Hybrid Approach (Recommended for Robustness)

**Why:** Combine both approaches for maximum coverage with graceful degradation.

**Important Note:** SK's telemetry creates spans at the **Semantic Kernel service layer** (wraps SK methods), while OpenAI instrumentor instruments the **OpenAI SDK library itself** (monkey-patches `client.chat.completions.create()`). These are **complementary, not duplicate** - you get nested spans showing both layers.

**Implementation:**
```python
import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace

# Enable SK's built-in telemetry (if available)
os.environ.setdefault("SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS", "true")
os.environ.setdefault("SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE", "true")

# Initialize HoneyHive with OpenAI instrumentor for SDK-level tracing
tracer = HoneyHiveTracer.init(
    project="semantic-kernel-app",
    api_key="your-honeyhive-api-key",
    instrumentors=[OpenAIInstrumentor()],  # Instruments OpenAI SDK
)

# Set as global TracerProvider for SK's built-in telemetry
trace.set_tracer_provider(tracer.provider)

# Use Semantic Kernel normally
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="HybridAgent",
    instructions="You are a hybrid instrumented assistant.",
)

# Both instrumentations work together (nested spans):
# 1. SK's built-in telemetry creates agent/SK-service spans
# 2. OpenAI instrumentor creates nested spans for OpenAI SDK calls
response = await agent.get_response(messages="Hello!")
```

**Trace Structure:**
```
Trace:
├─ Agent Span: "invoke_agent HybridAgent" (from SK agent telemetry)
│  └─ SK Service Span: "chat.completions gpt-4" (from SK @trace_chat_completion)
│     └─ OpenAI SDK Span: "ChatCompletion.create" (from OpenAI Instrumentor)
│        └─ Attributes: HTTP details, retries, network timing
```

**Pros:**
- ✅ **Layered observability**: Agent layer → SK service layer → SDK layer
- ✅ Graceful degradation if SK telemetry is disabled (falls back to SDK tracing)
- ✅ HTTP-level details (retries, network errors) from OpenAI instrumentor
- ✅ Future-proof against SK telemetry API changes
- ✅ Works with current and future SK versions

**Cons:**
- ⚠️ More spans per request (but they're nested, not duplicates)
- ⚠️ Slightly higher overhead (minimal in practice)

---

## Testing Strategy

### Test Case 1: Basic Agent Integration

```python
"""Test basic SK agent with HoneyHive tracing."""
import asyncio
import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def test_basic_agent():
    # Setup
    tracer = HoneyHiveTracer.init(
        project="sk-test-basic",
        api_key=os.getenv("HONEYHIVE_API_KEY"),
        instrumentors=[OpenAIInstrumentor()]
    )
    
    # Create agent
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="TestAgent",
        instructions="You are helpful",
    )
    
    # Execute
    response = await agent.get_response(messages="Say hello")
    
    # Verify
    print(f"✓ Response: {response.content}")
    print("✓ Check HoneyHive dashboard for trace with agent name")
    
asyncio.run(test_basic_agent())
```

**Expected in HoneyHive:**
- Trace with project name "sk-test-basic"
- Span for OpenAI API call (or whatever provider you're using)
- Metadata: model, tokens, temperature

**Note:** If using multiple providers, create test cases for each to verify instrumentor coverage.

### Test Case 2: Agent with Built-in Telemetry

```python
"""Test SK built-in telemetry integration."""
import asyncio
import os
from honeyhive import HoneyHiveTracer
from opentelemetry import trace
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def test_builtin_telemetry():
    # Enable SK telemetry
    os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true"
    
    # Setup HoneyHive as global TracerProvider
    tracer = HoneyHiveTracer.init(
        project="sk-test-telemetry",
        api_key=os.getenv("HONEYHIVE_API_KEY"),
    )
    trace.set_tracer_provider(tracer.provider)
    
    # Create agent
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="TelemetryAgent",
        instructions="You are a telemetry test agent",
    )
    
    # Execute
    response = await agent.get_response(messages="Test telemetry")
    
    # Verify
    print(f"✓ Response: {response.content}")
    print("✓ Check HoneyHive for agent-level spans with 'invoke_agent' operation")
    
asyncio.run(test_builtin_telemetry())
```

**Expected in HoneyHive:**
- Agent invocation span with `gen_ai.operation.name = "invoke_agent"`
- Agent attributes: `gen_ai.agent.name`, `gen_ai.agent.id`
- LLM call span nested under agent span
- Token usage and model metadata

### Test Case 3: Multi-Agent System

```python
"""Test multi-agent orchestration tracing."""
import asyncio
import os
from honeyhive import HoneyHiveTracer
from opentelemetry import trace
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def test_multi_agent():
    # Setup
    os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true"
    
    tracer = HoneyHiveTracer.init(
        project="sk-test-multi-agent",
        api_key=os.getenv("HONEYHIVE_API_KEY"),
    )
    trace.set_tracer_provider(tracer.provider)
    
    # Create specialist agents
    billing_agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="BillingAgent",
        instructions="Handle billing issues",
    )
    
    refund_agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="RefundAgent",
        instructions="Handle refund requests",
    )
    
    triage_agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="TriageAgent",
        instructions="Route to specialist agents",
        plugins=[billing_agent, refund_agent],
    )
    
    # Execute
    response = await triage_agent.get_response(
        messages="I was charged twice last month"
    )
    
    # Verify
    print(f"✓ Response: {response.content}")
    print("✓ Check HoneyHive for multi-agent trace with agent handoffs")
    
asyncio.run(test_multi_agent())
```

**Expected in HoneyHive:**
- Parent span for TriageAgent invocation
- Child spans for specialist agent invocations
- Clear agent flow visualization: Triage → Billing → Response

---

## Next Steps

### Phase 1: Proof of Concept (1-2 days)

1. [ ] Create test script `test_semantic_kernel_honeyhive.py` with hybrid approach
2. [ ] Test basic agent tracing
3. [ ] Test SK built-in telemetry integration
4. [ ] Verify spans appear in HoneyHive dashboard
5. [ ] Document any issues or edge cases

### Phase 2: Documentation (1 day)

1. [ ] Create integration guide: `docs/how-to/integrations/semantic-kernel.rst`
2. [ ] Add code examples for all three options (A, B, C)
3. [ ] Document environment variables
4. [ ] Add troubleshooting section
5. [ ] Include "What's Captured" vs "What's Not" table

### Phase 3: Compatibility Matrix (1 day)

1. [ ] Add Semantic Kernel to `tests/compatibility_matrix/`
2. [ ] Create test suite for SK integration
3. [ ] Add to official compatibility documentation
4. [ ] Test with different SK versions (1.x)

---

## What's Captured vs What's Not

| Feature | Option A (OpenAI Instrumentor) | Option B (TracerProvider) | Option C (Hybrid) |
|---------|-------------------------------|--------------------------|-------------------|
| **LLM API Calls** | ✅ Always | ✅ If telemetry enabled | ✅ Always |
| **Agent Name** | ❌ No | ✅ Yes | ✅ Yes |
| **Agent Instructions** | ❌ No | ✅ Yes (if sensitive enabled) | ✅ Yes (if sensitive enabled) |
| **Agent Descriptions** | ❌ No | ✅ Yes | ✅ Yes |
| **Function/Tool Calls** | ⚠️ Partial | ✅ Full | ✅ Full |
| **Multi-Agent Flows** | ❌ No | ✅ Yes | ✅ Yes |
| **Token Usage** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Model Parameters** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Prompts/Responses** | ✅ Yes | ✅ If sensitive enabled | ✅ If sensitive enabled |
| **Error Tracking** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Graceful Degradation** | ✅ Always works | ❌ Requires env vars | ✅ Falls back to Option A |

---

## Troubleshooting

### Issue: No spans appearing in HoneyHive

**Cause:** SK's telemetry is disabled by default

**Solution:**
```bash
export SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS=true
```

### Issue: Only seeing LLM calls, no agent spans

**Cause:** Using Option A without TracerProvider injection

**Solution:** Upgrade to Option C (Hybrid)

### Issue: Multiple nested spans for same LLM call

**Cause:** Both SK telemetry and OpenAI instrumentor creating spans (this is expected!)

**Why this is GOOD:**
- SK creates spans at the service layer (semantic-kernel's abstraction)
- OpenAI instrumentor creates spans at the SDK layer (OpenAI library HTTP calls)
- These are **nested, not duplicates** - showing different layers of the stack

**If you want fewer spans:**
- Use Option B (SK telemetry only) - but lose HTTP-level details and graceful degradation
- Or use Option A (OpenAI instrumentor only) - but lose agent context

### Issue: Missing prompts/responses in spans

**Cause:** Sensitive events not enabled

**Solution:**
```bash
export SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE=true
```

---

## Appendix: File Structure Analysis

**Total Files:** 552 Python files (77,709 LOC)

**Largest Files:**
- `semantic_kernel/data/vector.py` - 2,367 lines (Vector store implementations)
- `semantic_kernel/agents/open_ai/responses_agent_thread_actions.py` - 1,219 lines
- `semantic_kernel/agents/open_ai/openai_responses_agent.py` - 1,214 lines
- `semantic_kernel/agents/azure_ai/agent_thread_actions.py` - 1,139 lines

**Key Directories:**
```
semantic_kernel/
├── agents/              # Agent framework (ChatCompletionAgent, etc.)
├── connectors/          # LLM and vector store connectors
│   ├── ai/             # OpenAI, Anthropic, Google, Bedrock, etc.
│   └── memory_stores/  # 15+ vector database connectors
├── functions/          # Plugin system (KernelFunction, decorators)
├── contents/           # Message types (ChatMessageContent, etc.)
├── filters/            # Auto function invocation, prompt filters
├── processes/          # Process framework (workflows)
└── utils/
    └── telemetry/      # Built-in OpenTelemetry tracing
```

---

## References

- **Semantic Kernel Docs:** https://learn.microsoft.com/en-us/semantic-kernel/overview/
- **SK GitHub:** https://github.com/microsoft/semantic-kernel
- **SK Python API:** https://learn.microsoft.com/en-us/python/api/semantic-kernel/
- **OpenTelemetry GenAI Conventions:** https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/
- **HoneyHive BYOI Architecture:** See `standards/ai-assistant/AI-ASSISTED-DEVELOPMENT-PLATFORM-CASE-STUDY.md`

---

**Analysis Complete:** October 15, 2025  
**Next Action:** Create POC test script using Option C (Hybrid Approach)

