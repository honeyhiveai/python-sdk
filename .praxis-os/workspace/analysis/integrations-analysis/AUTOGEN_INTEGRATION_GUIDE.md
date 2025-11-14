# Microsoft AutoGen Integration Guide for HoneyHive

**Last Updated:** 2025-10-15  
**AutoGen Version:** v0.7.5+  
**HoneyHive SDK:** python-sdk  
**Integration Type:** BYOI (Bring Your Own Instrumentation) - Native OpenTelemetry

---

## Overview

Microsoft AutoGen v0.7.5+ has **built-in OpenTelemetry support** that is fully compatible with HoneyHive's BYOI architecture. This guide shows how to integrate AutoGen with HoneyHive to capture complete observability for multi-agent AI applications.

**What You'll Get:**
- ✅ Agent invocations and timing
- ✅ Tool executions
- ✅ LLM API calls (prompts, completions, tokens)
- ✅ Complete span hierarchy
- ✅ GenAI semantic conventions

---

## Prerequisites

### Required Packages

```bash
# AutoGen packages
pip install autogen-agentchat autogen-ext[openai]

# HoneyHive SDK
pip install honeyhive

# OpenTelemetry (if not already installed via dependencies)
pip install opentelemetry-sdk

# LLM Client Instrumentor (choose based on your LLM provider)
pip install openinference-instrumentation-openai  # For OpenAI
# OR
pip install opentelemetry-instrumentation-anthropic  # For Anthropic (via Traceloop)
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."  # Your OpenAI API key
export HH_API_KEY="hh_..."      # Your HoneyHive API key
```

---

## Quick Start

### Basic Integration (OpenAI)

```python
import asyncio
import os
from honeyhive import HoneyHiveTracer
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.openai import OpenAIInstrumentor

async def main():
    # Step 1: Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        project="autogen-demo",
        api_key=os.getenv("HH_API_KEY"),
        source="autogen-app"
    )
    
    # Step 2: Instrument OpenAI client (captures LLM calls)
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # Step 3: Create model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Step 4: Create runtime with HoneyHive TracerProvider (captures agent spans)
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    # Step 5: Create and use agent
    agent = AssistantAgent(
        "assistant",
        model_client=model_client,
        description="A helpful assistant"
    )
    
    result = await agent.run(task="What is 2+2? Explain your reasoning.")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

**What This Captures:**
- Agent invocation span (`invoke_agent`)
- OpenAI API call spans (`chat.completions.create`)
- Complete prompt and completion text
- Token usage and costs
- Error traces

---

## Integration Patterns

### Pattern 1: Single Agent with Tools

```python
import asyncio
from honeyhive import HoneyHiveTracer
from autogen_core import SingleThreadedAgentRuntime, FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.openai import OpenAIInstrumentor

def calculate(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async def main():
    # Initialize tracing
    tracer = HoneyHiveTracer.init(project="autogen-tools")
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # Create components
    model_client = OpenAIChatCompletionClient(model="gpt-4")
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    # Create tool
    calculator = FunctionTool(calculate, description="Adds two numbers")
    
    # Create agent with tools
    agent = AssistantAgent(
        "calculator_agent",
        model_client=model_client,
        tools=[calculator],
        description="An agent that can perform calculations"
    )
    
    result = await agent.run(task="What is 15 + 27?")
    print(result)

asyncio.run(main())
```

**Additional Spans Captured:**
- Tool execution spans (`execute_tool calculate`)
- Tool parameters and results

### Pattern 2: Multi-Agent Team

```python
import asyncio
from honeyhive import HoneyHiveTracer
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.openai import OpenAIInstrumentor

async def main():
    # Initialize tracing
    tracer = HoneyHiveTracer.init(project="autogen-multiagent")
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # Create shared model client
    model_client = OpenAIChatCompletionClient(model="gpt-4")
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    # Create multiple agents
    researcher = AssistantAgent(
        "researcher",
        model_client=model_client,
        system_message="You are a research assistant. Gather information.",
        description="Research agent"
    )
    
    writer = AssistantAgent(
        "writer",
        model_client=model_client,
        system_message="You are a writer. Create clear summaries.",
        description="Writer agent"
    )
    
    # Create team
    team = RoundRobinGroupChat([researcher, writer])
    
    result = await team.run(task="Research and write about quantum computing")
    print(result)

asyncio.run(main())
```

**Additional Spans Captured:**
- Multiple agent invocations (one per agent)
- Agent handoffs
- Team orchestration

### Pattern 3: Anthropic Integration

```python
import asyncio
from honeyhive import HoneyHiveTracer
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
# Use Traceloop's Anthropic instrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

async def main():
    # Initialize tracing
    tracer = HoneyHiveTracer.init(project="autogen-anthropic")
    AnthropicInstrumentor().instrument()  # Uses global tracer provider
    
    # Create Anthropic model client
    model_client = AnthropicChatCompletionClient(
        model="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    agent = AssistantAgent(
        "claude_assistant",
        model_client=model_client,
        description="Claude-powered assistant"
    )
    
    result = await agent.run(task="Explain machine learning")
    print(result)

asyncio.run(main())
```

---

## Advanced Configuration

### Disabling Runtime Tracing

If you only want LLM call traces (not agent spans):

```python
import os
os.environ["AUTOGEN_DISABLE_RUNTIME_TRACING"] = "true"

# OR via NoOpTracerProvider
from opentelemetry.trace import NoOpTracerProvider

runtime = SingleThreadedAgentRuntime(tracer_provider=NoOpTracerProvider())
```

### Custom Span Attributes

Add custom metadata to spans:

```python
from opentelemetry import trace

async def main():
    tracer_obj = HoneyHiveTracer.init(project="autogen-custom")
    OpenAIInstrumentor().instrument(tracer_provider=tracer_obj.provider)
    
    # Get current span and add attributes
    span = trace.get_current_span()
    span.set_attribute("user_id", "user-123")
    span.set_attribute("session_id", "session-456")
    span.set_attribute("environment", "production")
    
    # Use AutoGen normally
    agent = AssistantAgent("assistant", model_client=model_client)
    result = await agent.run(task="Hello")
```

### Streaming Responses

AutoGen supports streaming with full observability:

```python
async def main():
    tracer = HoneyHiveTracer.init(project="autogen-streaming")
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    model_client = OpenAIChatCompletionClient(model="gpt-4")
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    agent = AssistantAgent(
        "assistant",
        model_client=model_client,
        model_client_stream=True  # Enable streaming
    )
    
    # Stream results
    async for message in agent.run_stream(task="Write a poem"):
        print(message)
```

**Streaming Traces:**
- Individual chunks captured as events
- Complete response timing
- Token-by-token latency visible

---

## Span Hierarchy

### Example Trace Structure

```
└── invoke_agent assistant [AutoGen]
    ├── chat.completions.create gpt-4 [OpenAI Instrumentor]
    │   └── Request: "What is 2+2?"
    │   └── Response: "Let me calculate that..."
    │   └── Tokens: {prompt: 10, completion: 15}
    ├── execute_tool calculate [AutoGen]
    │   └── Input: {a: 2, b: 2}
    │   └── Output: 4
    └── chat.completions.create gpt-4 [OpenAI Instrumentor]
        └── Request: "The answer is 4"
        └── Response: "2+2 equals 4"
        └── Tokens: {prompt: 12, completion: 8}
```

---

## Supported LLM Providers

| Provider | Model Client | Instrumentor | Package |
|----------|--------------|--------------|---------|
| **OpenAI** | `OpenAIChatCompletionClient` | OpenInference | `openinference-instrumentation-openai` |
| **Azure OpenAI** | `OpenAIChatCompletionClient` | OpenInference | `openinference-instrumentation-openai` |
| **Anthropic** | `AnthropicChatCompletionClient` | Traceloop | `opentelemetry-instrumentation-anthropic` |
| **Ollama** | `OllamaChatCompletionClient` | Manual* | N/A |
| **Gemini** | `GeminiChatCompletionClient` | Manual* | N/A |

*Manual: Requires custom instrumentation or will only capture agent-level spans

---

## Troubleshooting

### No Traces Appearing in HoneyHive

**Check:**
1. HoneyHive API key is correct
2. TracerProvider is passed to both instrumentor AND runtime
3. `AUTOGEN_DISABLE_RUNTIME_TRACING` is not set to `true`

```python
# Verify tracer provider is set
print(f"Tracer provider: {tracer.provider}")

# Check if instrumentor is registered
from opentelemetry import trace
print(f"Global tracer: {trace.get_tracer_provider()}")
```

### Only Seeing LLM Calls, No Agent Spans

**Problem:** Forgot to pass `tracer_provider` to runtime

**Solution:**
```python
# Wrong:
runtime = SingleThreadedAgentRuntime()  # Uses default (NoOp)

# Correct:
runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
```

### Only Seeing Agent Spans, No LLM Details

**Problem:** Forgot to instrument LLM client

**Solution:**
```python
# Add before creating agents:
from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
```

### Duplicate Spans

**Problem:** Instrumentor registered multiple times

**Solution:**
```python
# Only call instrument() once per application lifecycle
instrumentor = OpenAIInstrumentor()
if not instrumentor.is_instrumented_by_opentelemetry:
    instrumentor.instrument(tracer_provider=tracer.provider)
```

### AttributeError: 'NoneType' has no attribute 'provider'

**Problem:** HoneyHiveTracer not initialized

**Solution:**
```python
# Make sure init() returns a tracer
tracer = HoneyHiveTracer.init(project="...", api_key="...")
# Not: HoneyHiveTracer.init(...)  # (missing assignment)
```

---

## Best Practices

### 1. Initialize Tracing Early

```python
# At application startup (before creating any agents)
tracer = HoneyHiveTracer.init(project="my-app")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
```

### 2. Use Consistent Project Names

```python
# Group related runs by project
tracer = HoneyHiveTracer.init(
    project="customer-support-bot",  # Consistent name
    source=f"agent-{agent_name}"     # Differentiate sources
)
```

### 3. Add Context with Attributes

```python
span = trace.get_current_span()
span.set_attribute("user_id", user_id)
span.set_attribute("request_id", request_id)
span.set_attribute("agent_version", "v1.2.3")
```

### 4. Handle Cleanup

```python
try:
    result = await agent.run(task="...")
finally:
    # Optional: explicitly flush spans
    tracer.provider.force_flush()
```

### 5. Use Environment-Specific Configuration

```python
import os

tracer = HoneyHiveTracer.init(
    project=f"autogen-{os.getenv('ENV', 'dev')}",
    api_key=os.getenv("HH_API_KEY"),
    # Disable in test environments if needed
    enabled=os.getenv("ENV") != "test"
)
```

---

## Complete Example Application

```python
"""
Complete AutoGen + HoneyHive integration example
Demonstrates: Single agent, tools, error handling, custom attributes
"""

import asyncio
import os
from typing import Annotated
from honeyhive import HoneyHiveTracer
from autogen_core import SingleThreadedAgentRuntime, FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace

def get_weather(city: Annotated[str, "The city name"]) -> str:
    """Get the weather for a city."""
    # Simulate weather API
    return f"Sunny, 72°F in {city}"

async def main():
    # 1. Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        project="weather-assistant",
        api_key=os.getenv("HH_API_KEY"),
        source="demo-app"
    )
    
    # 2. Instrument OpenAI
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # 3. Add custom context
    span = trace.get_current_span()
    span.set_attribute("app_version", "1.0.0")
    span.set_attribute("environment", "demo")
    
    # 4. Create components
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer.provider)
    
    weather_tool = FunctionTool(
        get_weather,
        description="Get current weather for a city"
    )
    
    # 5. Create agent
    agent = AssistantAgent(
        "weather_assistant",
        model_client=model_client,
        tools=[weather_tool],
        description="An assistant that provides weather information",
        system_message="You are a helpful weather assistant. Use the get_weather tool to answer questions."
    )
    
    # 6. Run task
    try:
        print("Running weather query...")
        result = await agent.run(
            task="What's the weather like in San Francisco?"
        )
        print(f"\nResult: {result}\n")
        
        # Check HoneyHive dashboard for traces at:
        # https://app.honeyhive.ai/projects/weather-assistant
        
    except Exception as e:
        print(f"Error: {e}")
        # Error will be captured in spans automatically
    finally:
        # Ensure all spans are sent
        tracer.provider.force_flush(timeout_millis=5000)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## What's Captured

### From AutoGen (Built-in OTel)

✅ **Agent Spans:**
- Operation: `invoke_agent`, `create_agent`
- Attributes:
  - `gen_ai.agent.name`
  - `gen_ai.agent.id`
  - `gen_ai.agent.description`
  - `gen_ai.operation.name`
  - `gen_ai.system` = `"autogen"`

✅ **Tool Spans:**
- Operation: `execute_tool`
- Attributes:
  - `gen_ai.tool.name`
  - `gen_ai.tool.description`
  - `gen_ai.tool.call.id`

✅ **Runtime Spans:**
- Message operations (send, receive, process)
- Attributes:
  - `messaging.operation`
  - `messaging.destination`
  - `messaging.message.type`

### From LLM Client Instrumentors

✅ **OpenAI (via OpenInference):**
- Model name, parameters
- Prompt messages (if enabled)
- Completion text (if enabled)
- Token usage (prompt, completion, total)
- Function calls
- Streaming chunks

✅ **Anthropic (via Traceloop):**
- Model name
- Prompt and completion
- Token usage
- Tool use
- Streaming events

---

## Known Limitations

### What's NOT Captured

❌ **Agent State:**
- Internal conversation history (unless explicitly traced)
- Agent memory operations
- Custom state modifications

❌ **Team Orchestration:**
- Detailed team decision-making
- Speaker selection logic in group chats

❌ **Some Model Providers:**
- Ollama, Gemini, LlamaCpp require manual instrumentation

### Workarounds

**For Agent State:**
```python
# Manually add state to spans
span = trace.get_current_span()
span.set_attribute("conversation_length", len(agent.state.messages))
span.add_event("agent_state_change", {"state": agent.state.to_dict()})
```

**For Unsupported Providers:**
- Use AutoGen's built-in tracing (agent-level only)
- Implement custom span creation around model calls
- Contribute instrumentor to OpenInference/Traceloop!

---

## Migration Notes

### From AutoGen v0.2

AutoGen v0.7.5+ is a **complete rewrite** with different APIs:

**v0.2 (Legacy):**
```python
from autogen import AssistantAgent, UserProxyAgent
agent = AssistantAgent(name="assistant", llm_config={...})
```

**v0.7.5+ (Current):**
```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4")
agent = AssistantAgent("assistant", model_client=model_client)
```

**OpenLIT's AG2 instrumentor is for v0.2 only and NOT compatible with v0.7.5+**

---

## Additional Resources

- **AutoGen Documentation:** https://microsoft.github.io/autogen/
- **Telemetry Guide:** https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/telemetry.html
- **HoneyHive Dashboard:** https://app.honeyhive.ai/
- **OpenTelemetry GenAI Conventions:** https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **AutoGen GitHub:** https://github.com/microsoft/autogen
- **AutoGen Discord:** https://aka.ms/autogen-discord

---

## Support

For questions or issues:
- HoneyHive Support: support@honeyhive.ai
- AutoGen Issues: https://github.com/microsoft/autogen/issues
- This integration guide: [internal repository]

---

**Last Updated:** 2025-10-15  
**Tested with:** AutoGen v0.7.5, HoneyHive Python SDK latest, OpenInference v0.x

