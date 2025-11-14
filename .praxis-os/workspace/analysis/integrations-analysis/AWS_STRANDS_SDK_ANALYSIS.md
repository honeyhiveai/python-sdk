# AWS Strands SDK Comprehensive Analysis
**Date:** October 15, 2025  
**SDK Version:** 1.12.0+  
**Analysis Methodology:** SDK_ANALYSIS_METHODOLOGY.md  
**Repository:** https://github.com/strands-agents/sdk-python

---

## Executive Summary

**SDK Purpose:** Model-driven AI agent framework for building conversational assistants and autonomous workflows

**LLM Clients:** Multi-provider architecture supporting:
- OpenAI (via `openai` package)
- Anthropic (via `anthropic` package)
- Amazon Bedrock (via `boto3`)
- Gemini, Ollama, LiteLLM, LlamaAPI, Mistral, SageMaker, Writer

**Observability:** ✅ **Built-in OpenTelemetry with comprehensive GenAI semantic conventions**

**Recommendation:** **STANDARD OTEL INTEGRATION (Low-Medium Effort)**
- Strands respects global TracerProvider via `trace_api.get_tracer_provider()`
- HoneyHive can provide TracerProvider and automatically capture ALL agent traces
- Agent-specific context already captured via GenAI semantic conventions
- **NO custom instrumentor needed** - standard OTel integration pattern

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Code                            │
│                                                              │
│   agent = Agent(model=model, tools=[...])                   │
│   result = agent("task")                                    │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Class                             │
│                                                              │
│  • get_tracer() - Singleton tracer instance                 │
│  • start_agent_span() - Top-level agent invocation         │
│  • Conversation management                                  │
│  • Tool registry                                            │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Loop                                │
│                                                              │
│  • start_event_loop_cycle_span()                            │
│  • Orchestrates model → tool → model cycles                │
│  • Parent span for all cycle operations                    │
└──────────────────┬───────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
┌─────────────────┐  ┌─────────────────┐
│  Model Provider │  │  Tool Executor  │
│                 │  │                 │
│  • start_model_ │  │  • start_tool_  │
│    invoke_span()│  │    call_span()  │
│  • OpenAI       │  │  • Parallel     │
│  • Anthropic    │  │    execution    │
│  • Bedrock      │  │  • Result       │
│  • etc.         │  │    capture      │
└─────────────────┘  └─────────────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenTelemetry Tracer                            │
│                                                              │
│  • trace_api.get_tracer_provider() ← INTEGRATION POINT     │
│  • Respects global TracerProvider                          │
│  • GenAI semantic conventions                              │
│  • Span attributes + events                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Findings

### 1. LLM Client Usage

**Architecture:** Abstract base class `Model` with provider-specific implementations

**Supported Providers:**
| Provider | Package | Client Class | API Method |
|----------|---------|--------------|------------|
| OpenAI | `openai>=1.68.0` | `AsyncOpenAI` | `chat.completions.create` |
| Anthropic | `anthropic>=0.21.0` | `AsyncAnthropic` | `messages.create` |
| Bedrock | `boto3>=1.26.0` | `boto3.client('bedrock-runtime')` | `converse_stream` |
| Gemini | `google-genai>=1.32.0` | `genai.Client` | `models.generate_content_stream` |
| Ollama | `ollama>=0.4.8` | `ollama.AsyncClient` | `chat` |
| LiteLLM | `litellm>=1.75.9` | Via OpenAI interface | `completion` |

**Client Instantiation:**
- **OpenAI:** Created per-request via context manager: `async with openai.AsyncOpenAI(**self.client_args)`
- **Anthropic:** Single instance created in `__init__`: `self.client = anthropic.AsyncAnthropic(**client_args)`
- **Bedrock:** Boto3 client managed by SDK
- **Others:** Provider-specific patterns

**API Call Sites:**
```python
# OpenAI (src/strands/models/openai.py:392)
async with openai.AsyncOpenAI(**self.client_args) as client:
    response = await client.chat.completions.create(**request)

# Anthropic (src/strands/models/anthropic.py:77)
self.client = anthropic.AsyncAnthropic(**client_args)
# ... later ...
async with self.client.messages.stream(**converse_args) as stream:
```

**Key Insight:** Model providers are abstracted - SDK users don't directly instantiate LLM clients. This means **existing LLM instrumentors may not capture calls** unless Strands-specific hooks are used.

---

### 2. Observability System - OpenTelemetry Integration

#### 2.1 OpenTelemetry Architecture

**Type:** ✅ **Native OpenTelemetry with comprehensive instrumentation**

**Components:**
```
src/strands/telemetry/
├── __init__.py          # Public API exports
├── config.py            # StrandsTelemetry setup class
├── tracer.py            # Tracer singleton with span creation methods
├── metrics.py           # Metrics collection (EventLoopMetrics)
└── metrics_constants.py # Metric name constants
```

**Dependencies:**
```toml
[project.dependencies]
opentelemetry-api>=1.30.0,<2.0.0
opentelemetry-sdk>=1.30.0,<2.0.0
opentelemetry-instrumentation-threading>=0.51b0,<1.00b0

[project.optional-dependencies]
otel = ["opentelemetry-exporter-otlp-proto-http>=1.30.0,<2.0.0"]
```

#### 2.2 Tracer Initialization Pattern

**Critical Discovery:** Strands uses `trace_api.get_tracer_provider()` to obtain the tracer:

```python
# src/strands/telemetry/tracer.py:90
self.tracer_provider = trace_api.get_tracer_provider()
self.tracer = self.tracer_provider.get_tracer(self.service_name)
```

**What This Means:**
- ✅ **Respects global TracerProvider** set by external systems
- ✅ **Standard OTel integration point** - no monkey-patching needed
- ✅ **HoneyHive can provide its own TracerProvider** and Strands will use it automatically

#### 2.3 Span Creation Patterns

Strands creates spans at multiple levels with specific naming conventions:

| Span Type | Method | Span Name | SpanKind | Parent |
|-----------|--------|-----------|----------|--------|
| Agent Invocation | `start_agent_span()` | `invoke_agent {agent_name}` | CLIENT | None (root) |
| Event Loop Cycle | `start_event_loop_cycle_span()` | `execute_event_loop_cycle` | INTERNAL | Agent span |
| Model Call | `start_model_invoke_span()` | `chat` | CLIENT | Cycle span |
| Tool Execution | `start_tool_call_span()` | `execute_tool {tool_name}` | INTERNAL | Cycle span |
| Multi-Agent | `start_multiagent_span()` | `invoke_{instance}` | CLIENT | None (root) |

**Span Hierarchy Example:**
```
invoke_agent ResearchAgent (CLIENT, root)
  └─ execute_event_loop_cycle (INTERNAL)
      ├─ chat (CLIENT) → LLM call
      └─ execute_tool web_search (INTERNAL)
          └─ execute_event_loop_cycle (INTERNAL) → next cycle
              └─ chat (CLIENT) → LLM call with tool results
```

#### 2.4 OpenTelemetry Span Attributes

Strands follows **GenAI Semantic Conventions** (v1.36.0):

**Common Attributes (all spans):**
```python
{
    "gen_ai.operation.name": "chat" | "execute_tool" | "invoke_agent",
    "gen_ai.system": "strands-agents",  # Old convention
    "gen_ai.provider.name": "strands-agents",  # New convention (if opted in)
    "gen_ai.event.start_time": "2025-10-15T10:30:00.000Z",
    "gen_ai.event.end_time": "2025-10-15T10:30:05.000Z"
}
```

**Agent Span Attributes:**
```python
{
    "gen_ai.agent.name": "ResearchAgent",
    "gen_ai.request.model": "us.amazon.nova-pro-v1:0",
    "gen_ai.agent.tools": "[{\"name\": \"web_search\", ...}]"  # JSON serialized
}
```

**Model Invocation Attributes:**
```python
{
    "gen_ai.request.model": "us.amazon.nova-pro-v1:0",
    "gen_ai.usage.prompt_tokens": 150,
    "gen_ai.usage.input_tokens": 150,
    "gen_ai.usage.completion_tokens": 50,
    "gen_ai.usage.output_tokens": 50,
    "gen_ai.usage.total_tokens": 200,
    "gen_ai.usage.cache_read_input_tokens": 100,  # Optional
    "gen_ai.usage.cache_write_input_tokens": 50,  # Optional
    "gen_ai.server.time_to_first_token": 245.3,  # ms
    "gen_ai.server.request.duration": 1523.7  # ms
}
```

**Tool Execution Attributes:**
```python
{
    "gen_ai.tool.name": "web_search",
    "gen_ai.tool.call.id": "tooluse_abc123",
    "gen_ai.tool.status": "success" | "error"
}
```

**Event Loop Attributes:**
```python
{
    "event_loop.cycle_id": "3",
    "event_loop.parent_cycle_id": "2"  # If nested
}
```

#### 2.5 OpenTelemetry Span Events

**Strands uses span.add_event() extensively to record LLM interactions:**

**Event Types (Old Convention):**
- `gen_ai.user.message` - User input
- `gen_ai.assistant.message` - Model response
- `gen_ai.tool.message` - Tool call or result
- `gen_ai.choice` - Model completion with finish_reason

**Event Types (New Convention - OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental):**
- `gen_ai.client.inference.operation.details` - Unified event for all messages

**Event Attribute Structure (Old Convention):**
```python
# User message event
{
    "content": '[{"text": "Analyze this data"}]'  # JSON serialized ContentBlock[]
}

# Choice event (model response)
{
    "finish_reason": "end_turn" | "tool_use" | "max_tokens",
    "message": '[{"text": "Here is the analysis..."}]'
}

# Tool message event
{
    "role": "tool",
    "content": '{"name": "web_search", "input": {...}}',
    "id": "tooluse_abc123"
}
```

**Event Attribute Structure (New Convention):**
```python
# Input messages
{
    "gen_ai.input.messages": [
        {
            "role": "user",
            "parts": [{"type": "text", "content": "Analyze this data"}]
        }
    ]
}

# Output messages
{
    "gen_ai.output.messages": [
        {
            "role": "assistant",
            "parts": [{"type": "text", "content": "Here is..."}],
            "finish_reason": "end_turn"
        }
    ]
}

# Tool call
{
    "gen_ai.input.messages": [
        {
            "role": "tool",
            "parts": [{
                "type": "tool_call",
                "name": "web_search",
                "id": "tooluse_abc123",
                "arguments": {"query": "..."}
            }]
        }
    ]
}
```

**Key Insight:** Strands captures **all message content** via events, not just metadata via attributes. This provides complete conversation history in traces.

#### 2.6 Semantic Convention Version Support

Strands supports **both old and new GenAI semantic conventions** based on environment variable:

```python
# src/strands/telemetry/tracer.py:103
opt_in_env = os.getenv("OTEL_SEMCONV_STABILITY_OPT_IN", "")
self.use_latest_genai_conventions = "gen_ai_latest_experimental" in opt_in_env
```

**Old Convention (default):**
- `gen_ai.system` attribute
- Separate events per message role
- Event names: `gen_ai.user.message`, `gen_ai.choice`, etc.

**New Convention (opt-in):**
- `gen_ai.provider.name` attribute
- Unified `gen_ai.client.inference.operation.details` event
- Structured message parts with types

**HoneyHive Consideration:** Need to support both conventions or recommend users set the opt-in flag.

#### 2.7 Tracer Provider Configuration

**StrandsTelemetry Setup Class:**

```python
from strands.telemetry import StrandsTelemetry

# Automatic global setup with OTLP export
StrandsTelemetry().setup_otlp_exporter()

# With custom tracer provider
from opentelemetry.sdk.trace import TracerProvider
custom_provider = TracerProvider(...)
StrandsTelemetry(tracer_provider=custom_provider)

# Console export for debugging
StrandsTelemetry().setup_console_exporter()
```

**Environment Variables:**
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTLP endpoint URL
- `OTEL_EXPORTER_OTLP_HEADERS` - Headers for OTLP requests
- `OTEL_SEMCONV_STABILITY_OPT_IN` - Opt into new conventions (set to include `gen_ai_latest_experimental`)

**Resource Attributes:**
```python
{
    "service.name": "strands-agents",
    "service.version": "1.12.0",  # From package metadata
    "telemetry.sdk.name": "opentelemetry",
    "telemetry.sdk.language": "python"
}
```

**Propagators:**
Strands sets up W3C propagation:
- `W3CBaggagePropagator` - Baggage propagation
- `TraceContextTextMapPropagator` - W3C Trace Context

---

### 3. Integration Points Discovery

#### 3.1 TracerProvider Injection (PRIMARY INTEGRATION POINT)

**Where:** `src/strands/telemetry/tracer.py:90`

```python
class Tracer:
    def __init__(self) -> None:
        self.tracer_provider = trace_api.get_tracer_provider()  # ← Gets global provider
        self.tracer = self.tracer_provider.get_tracer(self.service_name)
```

**✅ HoneyHive Integration Opportunity:**
1. HoneyHive sets global TracerProvider before Strands agent is created
2. Strands automatically uses HoneyHive's provider
3. All spans flow through HoneyHive's span processors

**Example Integration:**
```python
from honeyhive import HoneyHiveTracer
from strands import Agent
from opentelemetry import trace as trace_api

# Initialize HoneyHive tracer with its provider
hh_tracer = HoneyHiveTracer.init(
    project="strands-demo",
    api_key="your_api_key"
)

# Set HoneyHive's provider as global
trace_api.set_tracer_provider(hh_tracer.provider)

# Create Strands agent - will automatically use HoneyHive's provider
agent = Agent(name="ResearchAgent", tools=[...])
result = agent("Analyze this data")  # ← Traced to HoneyHive!
```

#### 3.2 Custom TracerProvider via StrandsTelemetry

**Where:** `src/strands/telemetry/config.py:71`

```python
from strands.telemetry import StrandsTelemetry
from honeyhive import HoneyHiveTracer

# Get HoneyHive's TracerProvider
hh_tracer = HoneyHiveTracer.init(project="strands-demo")

# Pass to Strands (bypasses global provider)
StrandsTelemetry(tracer_provider=hh_tracer.provider)

# Now create agents
agent = Agent(...)
```

**❌ Limitation:** This approach requires explicit StrandsTelemetry instantiation, which users may not do.

#### 3.3 Cannot Hook Model Providers Directly

**Finding:** Model clients are created internally by provider classes:
- OpenAI: `async with openai.AsyncOpenAI(**self.client_args)`
- Anthropic: `self.client = anthropic.AsyncAnthropic(**client_args)`

**Implication:** Existing OpenAI/Anthropic instrumentors **will NOT capture these calls** because:
1. Clients are created inside Strands code
2. Instrumentors hook client creation, but Strands creates them dynamically
3. Strands wraps calls with its own spans anyway

**Solution:** Don't try to instrument model providers - let Strands' built-in tracing handle it.

#### 3.4 Span Processor Injection

**Opportunity:** Add custom span processor to enrich or filter spans

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Create provider with HoneyHive exporter
provider = TracerProvider()
hh_processor = BatchSpanProcessor(HoneyHiveSpanExporter(...))
provider.add_span_processor(hh_processor)

# Set as global
trace_api.set_tracer_provider(provider)

# Strands will use it
agent = Agent(...)
```

---

## Integration Approach for HoneyHive

### Recommended: TracerProvider Integration (Low Effort, High Coverage)

**Why This Approach:**
- ✅ Strands explicitly uses `trace_api.get_tracer_provider()`
- ✅ Standard OpenTelemetry integration pattern
- ✅ Zero modifications to Strands code
- ✅ Captures ALL agent activity (model calls, tool use, cycles)
- ✅ Agent-specific metadata already included via GenAI conventions
- ✅ Works with ANY model provider (Bedrock, OpenAI, Anthropic, etc.)

**How It Works:**
```python
from honeyhive import HoneyHiveTracer
from strands import Agent
from opentelemetry import trace as trace_api

# 1. Initialize HoneyHive with TracerProvider
tracer = HoneyHiveTracer.init(
    project="strands-agents",
    api_key=os.getenv("HONEYHIVE_API_KEY")
)

# 2. Set as global provider (before creating agents)
trace_api.set_tracer_provider(tracer.provider)

# 3. Use Strands normally - tracing is automatic
agent = Agent(
    name="ResearchAgent",
    model=BedrockModel(model_id="us.amazon.nova-pro-v1:0"),
    tools=[web_search, calculator]
)

result = agent("What is the market cap of Tesla?")
# ↑ All spans sent to HoneyHive:
#   - invoke_agent ResearchAgent
#     - execute_event_loop_cycle
#       - chat (Bedrock call)
#       - execute_tool web_search
#       - chat (Bedrock call with results)
```

**What HoneyHive Gets:**

1. **Span Hierarchy:**
   - Root: `invoke_agent {agent_name}`
   - Children: Event loop cycles
   - Grandchildren: Model calls and tool executions

2. **Attributes:**
   - Agent name, model ID, tools list
   - Token usage (prompt, completion, cache hits)
   - Latency metrics (TTFT, total duration)
   - Tool names, IDs, status

3. **Events:**
   - Complete message history (user, assistant, tool)
   - Finish reasons
   - Content blocks (text, tool_use, tool_result)

4. **Metadata:**
   - Event loop cycle IDs
   - Parent-child relationships
   - Timestamps

**Pros:**
- ✅ **Minimal code** - 3 lines of setup
- ✅ **Comprehensive** - Captures everything
- ✅ **Provider agnostic** - Works with all LLM providers
- ✅ **Standard pattern** - Uses OTel best practices
- ✅ **No SDK changes** - Strands works as-is
- ✅ **Agent context included** - GenAI conventions provide metadata

**Cons:**
- ⚠️ Requires HoneyHive TracerProvider to support GenAI semantic conventions
- ⚠️ Users must set up TracerProvider before creating agents
- ⚠️ May capture spans from other OTel-instrumented libraries (could be a pro!)

---

### Alternative: Custom Span Enrichment Processor

If HoneyHive wants to add additional metadata or filter spans:

```python
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.sdk.trace import TracerProvider
from honeyhive import HoneyHiveTracer

class HoneyHiveEnrichmentProcessor(SpanProcessor):
    """Add HoneyHive-specific metadata to Strands spans."""
    
    def on_start(self, span: Span, parent_context: Context) -> None:
        # Add custom attributes
        if span.name.startswith("invoke_agent"):
            span.set_attribute("honeyhive.agent_type", "strands")
            span.set_attribute("honeyhive.sdk_version", "strands-1.12.0")
    
    def on_end(self, span: ReadableSpan) -> None:
        # Post-process or filter
        if span.attributes.get("gen_ai.operation.name") == "chat":
            # Extract tokens for cost calculation
            tokens = span.attributes.get("gen_ai.usage.total_tokens", 0)
            model = span.attributes.get("gen_ai.request.model", "")
            # Calculate cost...
    
    def shutdown(self) -> None:
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True

# Setup
hh_tracer = HoneyHiveTracer.init(project="strands")
provider = TracerProvider()
provider.add_span_processor(HoneyHiveEnrichmentProcessor())
provider.add_span_processor(hh_tracer.span_processor)  # HoneyHive exporter
trace_api.set_tracer_provider(provider)

# Use Strands
agent = Agent(...)
```

**Pros:**
- ✅ Full control over span data
- ✅ Can enrich, filter, or transform spans
- ✅ Can add HoneyHive-specific metadata

**Cons:**
- ⚠️ More complex setup
- ⚠️ Need to maintain processor logic

---

### NOT Recommended: Existing LLM Instrumentors

**Why Not:**
- ❌ Strands creates LLM clients internally
- ❌ OpenAI/Anthropic instrumentors won't hook these calls
- ❌ Would create duplicate spans (Strands + instrumentor)
- ❌ Would miss agent context (tools, cycles, etc.)

**Example of what DOESN'T work:**
```python
# This WON'T capture Strands' LLM calls
from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument()  # ← Won't hook Strands' internal OpenAI usage

agent = Agent(model=OpenAIModel(...))
agent("task")  # ← OpenAI calls not captured by instrumentor
```

---

## Testing Strategy

### Test Case 1: Basic TracerProvider Integration

**Setup:**
```python
from honeyhive import HoneyHiveTracer
from strands import Agent
from strands.models import BedrockModel
from opentelemetry import trace as trace_api

tracer = HoneyHiveTracer.init(
    project="strands-test",
    api_key=os.getenv("HONEYHIVE_API_KEY")
)
trace_api.set_tracer_provider(tracer.provider)

agent = Agent(
    name="TestAgent",
    model=BedrockModel(model_id="us.amazon.nova-micro-v1:0"),
    instructions="You are a helpful assistant"
)
```

**Test:**
```python
result = agent("What is 2+2?")
print(result)
```

**Expected in HoneyHive:**
- Span: `invoke_agent TestAgent` (root)
  - Span: `execute_event_loop_cycle`
    - Span: `chat` (Bedrock call)
- Attributes:
  - `gen_ai.agent.name = "TestAgent"`
  - `gen_ai.request.model = "us.amazon.nova-micro-v1:0"`
  - `gen_ai.usage.total_tokens > 0`
- Events:
  - `gen_ai.user.message` with "What is 2+2?"
  - `gen_ai.choice` with response

### Test Case 2: Tool Execution Tracing

**Setup:**
```python
from strands import tool

@tool
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic math operations."""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    return 0

agent = Agent(
    name="MathAgent",
    tools=[calculator]
)
```

**Test:**
```python
result = agent("What is 15 times 23?")
```

**Expected in HoneyHive:**
- Span: `invoke_agent MathAgent`
  - Span: `execute_event_loop_cycle` (cycle 1)
    - Span: `chat` (requests tool)
    - Span: `execute_tool calculator`
  - Span: `execute_event_loop_cycle` (cycle 2)
    - Span: `chat` (uses tool result)
- Tool span attributes:
  - `gen_ai.tool.name = "calculator"`
  - `gen_ai.tool.status = "success"`

### Test Case 3: Multi-Provider Support

**Test with different providers:**
```python
from strands.models import OpenAIModel, BedrockModel, AnthropicModel

providers = [
    OpenAIModel(model_id="gpt-4"),
    BedrockModel(model_id="us.amazon.nova-pro-v1:0"),
    AnthropicModel(model_id="claude-3-5-sonnet-20241022")
]

for model in providers:
    agent = Agent(model=model)
    result = agent("Say hello")
    # Check HoneyHive for traces with correct model IDs
```

**Expected:** All providers traced with correct `gen_ai.request.model` attribute.

### Test Case 4: Custom Trace Attributes

**Setup:**
```python
agent = Agent(
    name="CustomAgent",
    custom_trace_attributes={
        "user_id": "user_123",
        "session_id": "session_456",
        "environment": "production"
    }
)
```

**Test:**
```python
result = agent("Process this request")
```

**Expected:** Custom attributes present on agent span.

### Test Case 5: Streaming Support

**Setup:**
```python
agent = Agent(model=BedrockModel(streaming=True))
```

**Test:**
```python
for chunk in agent.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

**Expected:** Spans captured even with streaming responses.

---

## Implementation Guide for HoneyHive

### Step 1: Update HoneyHiveTracer to Expose TracerProvider

**Ensure HoneyHiveTracer provides access to its TracerProvider:**

```python
class HoneyHiveTracer:
    def __init__(self, ...):
        self.provider = self._create_tracer_provider()
        self.tracer = self.provider.get_tracer("honeyhive")
    
    def _create_tracer_provider(self) -> TracerProvider:
        provider = TracerProvider(resource=self._create_resource())
        provider.add_span_processor(
            BatchSpanProcessor(HoneyHiveSpanExporter(...))
        )
        return provider
    
    @property
    def provider(self) -> TracerProvider:
        """Expose TracerProvider for integration with OTel-native frameworks."""
        return self._provider
```

### Step 2: Add Strands Integration Example to Documentation

**File:** `docs/how-to/integrations/aws-strands.rst`

```rst
AWS Strands Agents SDK
======================

The AWS Strands Agents SDK has native OpenTelemetry support, making
integration with HoneyHive straightforward.

Installation
------------

.. code-block:: bash

    pip install honeyhive strands-agents

Basic Setup
-----------

.. code-block:: python

    import os
    from honeyhive import HoneyHiveTracer
    from strands import Agent
    from strands.models import BedrockModel
    from opentelemetry import trace as trace_api

    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        project="strands-agents",
        api_key=os.getenv("HONEYHIVE_API_KEY")
    )

    # Set as global TracerProvider (MUST be done before creating agents)
    trace_api.set_tracer_provider(tracer.provider)

    # Create and use Strands agent
    agent = Agent(
        name="ResearchAgent",
        model=BedrockModel(model_id="us.amazon.nova-pro-v1:0"),
        instructions="You are a research assistant"
    )

    result = agent("What is the capital of France?")
    print(result)

What Gets Captured
------------------

HoneyHive automatically captures:

* **Agent invocations** - Agent name, model, tools
* **LLM calls** - All model providers (Bedrock, OpenAI, Anthropic, etc.)
* **Token usage** - Input, output, cached tokens
* **Tool executions** - Tool name, inputs, outputs, status
* **Message history** - Complete conversation with content
* **Latency metrics** - TTFT, total duration
* **Event loop cycles** - Multi-turn conversation tracking

With Tools
----------

.. code-block:: python

    from strands import Agent, tool

    @tool
    def web_search(query: str) -> str:
        """Search the web for information."""
        # Implementation
        return f"Results for: {query}"

    agent = Agent(
        name="SearchAgent",
        tools=[web_search]
    )

    result = agent("What is the latest news?")

Tool executions are automatically traced with inputs and outputs.

Multiple Model Providers
-------------------------

Works with all Strands-supported providers:

.. code-block:: python

    from strands.models import (
        BedrockModel,
        OpenAIModel,
        AnthropicModel,
        OllamaModel
    )

    # Bedrock
    agent_bedrock = Agent(model=BedrockModel(
        model_id="us.amazon.nova-pro-v1:0"
    ))

    # OpenAI
    agent_openai = Agent(model=OpenAIModel(
        model_id="gpt-4",
        client_args={"api_key": os.getenv("OPENAI_API_KEY")}
    ))

    # Anthropic
    agent_anthropic = Agent(model=AnthropicModel(
        model_id="claude-3-5-sonnet-20241022",
        client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")}
    ))

All model providers are traced consistently.

Custom Attributes
-----------------

Add custom metadata to traces:

.. code-block:: python

    agent = Agent(
        name="CustomAgent",
        custom_trace_attributes={
            "user_id": "user_123",
            "environment": "production",
            "version": "1.0.0"
        }
    )

Semantic Conventions
--------------------

Strands supports both old and new GenAI semantic conventions.
To use the latest conventions:

.. code-block:: bash

    export OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental

This enables structured message parts and unified event format.

Troubleshooting
---------------

**Issue:** Traces not appearing in HoneyHive

**Solution:** Ensure ``trace_api.set_tracer_provider()`` is called
**before** creating any Strands agents.

**Issue:** Duplicate spans

**Solution:** Don't use additional LLM instrumentors (OpenAI, Anthropic).
Strands' native tracing handles all model calls.

**Issue:** Missing agent context

**Solution:** Verify HoneyHive is capturing GenAI semantic convention
attributes (``gen_ai.*``).
```

### Step 3: Update Compatibility Matrix

**File:** `docs/compatibility-matrix.md`

Add entry:
```markdown
| Framework | Version | Support Level | Integration Method | Notes |
|-----------|---------|---------------|-------------------|-------|
| AWS Strands | 1.12.0+ | ✅ Full | TracerProvider | Native OTel with GenAI conventions |
```

### Step 4: Add Integration Test

**File:** `tests/integration/test_strands_integration.py`

```python
"""Integration tests for AWS Strands SDK."""

import pytest
import os
from honeyhive import HoneyHiveTracer
from opentelemetry import trace as trace_api

# Only run if Strands is installed
pytest.importorskip("strands")

from strands import Agent, tool
from strands.models import BedrockModel


@pytest.fixture(scope="module")
def honeyhive_tracer():
    """Initialize HoneyHive tracer."""
    tracer = HoneyHiveTracer.init(
        project="strands-integration-test",
        api_key=os.getenv("HONEYHIVE_API_KEY"),
    )
    trace_api.set_tracer_provider(tracer.provider)
    return tracer


def test_basic_agent_tracing(honeyhive_tracer):
    """Test basic agent invocation is traced."""
    agent = Agent(
        name="TestAgent",
        model=BedrockModel(model_id="us.amazon.nova-micro-v1:0"),
        instructions="You are helpful"
    )
    
    result = agent("Say hello")
    
    # Verify result
    assert result is not None
    assert "hello" in str(result).lower()
    
    # TODO: Query HoneyHive API to verify span was recorded


def test_tool_execution_tracing(honeyhive_tracer):
    """Test tool executions are traced."""
    
    @tool
    def test_calculator(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    agent = Agent(
        name="MathAgent",
        tools=[test_calculator]
    )
    
    result = agent("What is 5 + 3?")
    
    assert "8" in str(result)
    # TODO: Verify tool span exists with correct attributes


def test_custom_attributes(honeyhive_tracer):
    """Test custom trace attributes are captured."""
    agent = Agent(
        name="CustomAgent",
        custom_trace_attributes={
            "test_user": "user_123",
            "test_env": "ci"
        }
    )
    
    result = agent("Hello")
    
    # TODO: Verify custom attributes in span
```

---

## Next Steps

### For HoneyHive Team:

1. **✅ Verify TracerProvider API**
   - Ensure `HoneyHiveTracer.provider` is accessible
   - Test with Strands to confirm spans are captured

2. **✅ Test GenAI Semantic Conventions**
   - Verify HoneyHive backend understands `gen_ai.*` attributes
   - Test both old and new convention formats

3. **✅ Create Integration Example**
   - Write sample code showing TracerProvider setup
   - Test with multiple model providers (Bedrock, OpenAI, Anthropic)

4. **✅ Add to Documentation**
   - Create `docs/how-to/integrations/aws-strands.rst`
   - Update compatibility matrix
   - Add to main integrations list

5. **✅ Test Edge Cases**
   - Streaming responses
   - Multi-agent systems (Swarm, Graph)
   - Tool failures
   - Context window overflow

### For Users:

1. Install dependencies:
   ```bash
   pip install honeyhive strands-agents
   ```

2. Set up tracing (3 lines):
   ```python
   from honeyhive import HoneyHiveTracer
   from opentelemetry import trace as trace_api
   
   tracer = HoneyHiveTracer.init(project="my-agents")
   trace_api.set_tracer_provider(tracer.provider)
   ```

3. Use Strands normally - tracing is automatic!

---

## References

### Strands Documentation
- Main docs: https://strandsagents.com/
- GitHub: https://github.com/strands-agents/sdk-python
- PyPI: https://pypi.org/project/strands-agents/

### OpenTelemetry Resources
- GenAI Semantic Conventions v1.36.0: https://github.com/open-telemetry/semantic-conventions/blob/v1.36.0/docs/gen-ai/
- TracerProvider API: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.html
- Python SDK: https://opentelemetry.io/docs/languages/python/

### Related
- AWS Blog: Amazon Strands Agents SDK Deep Dive - https://aws.amazon.com/blogs/machine-learning/amazon-strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/

---

**Analysis Completed:** October 15, 2025  
**Analyzed By:** AI Assistant following SDK_ANALYSIS_METHODOLOGY.md  
**Status:** ✅ Ready for HoneyHive Integration
