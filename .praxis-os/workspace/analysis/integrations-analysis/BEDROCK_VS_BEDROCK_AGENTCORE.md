# Amazon Bedrock vs Amazon Bedrock AgentCore

**Critical Distinction for Instrumentation**

Date: 2025-10-15

---

## TL;DR

These are **TWO COMPLETELY DIFFERENT AWS SERVICES**:

| Service | What It Is | Instrumentor Exists? | What to Instrument |
|---------|-----------|---------------------|-------------------|
| **Amazon Bedrock** | AWS-managed LLM API service (like OpenAI API) | ✅ **YES** - OpenInference, Traceloop | Boto3 `bedrock-runtime` client calls |
| **Amazon Bedrock AgentCore** | Agent deployment/runtime platform (like AWS Lambda) | ❌ **NO** | User's agent framework (LangChain, etc.) |

---

## Amazon Bedrock (LLM Service)

### What It Is

**Amazon Bedrock** is AWS's **managed LLM service** - their version of OpenAI API or Anthropic API.

- Provides access to foundation models (Claude, Llama, Mistral, etc.)
- Pay-per-use API for model inference
- Accessed via Boto3 `bedrock-runtime` client
- Competes with: OpenAI API, Anthropic API, Google Vertex AI

### API Methods

```python
import boto3

client = boto3.client('bedrock-runtime')

# Method 1: invoke_model (older API)
response = client.invoke_model(
    modelId='anthropic.claude-v2',
    body=json.dumps({"prompt": "Hello", "max_tokens": 100})
)

# Method 2: converse (newer unified API)
response = client.converse(
    modelId='anthropic.claude-3-sonnet',
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)

# Method 3: invoke_agent (for Bedrock Agents - legacy feature)
response = client.invoke_agent(
    agentId='AGENT123',
    sessionId='SESSION456',
    inputText='Help me'
)
```

### Existing Instrumentors

**✅ OpenInference Bedrock Instrumentor**
- **Package:** `openinference-instrumentation-bedrock`
- **GitHub:** https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-bedrock
- **PyPI:** https://pypi.org/project/openinference-instrumentation-bedrock/
- **What it instruments:** Boto3 calls to `bedrock-runtime` and `bedrock-agent-runtime`
  - `invoke_model()`
  - `invoke_model_with_response_stream()`
  - `converse()`
  - `converse_stream()`
  - `invoke_agent()`
  - `retrieve()` and `retrieve_and_generate()` (RAG)

**✅ Traceloop Bedrock Instrumentor**
- **Package:** `opentelemetry-instrumentation-bedrock`
- **GitHub:** https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-bedrock
- **PyPI:** https://pypi.org/project/opentelemetry-instrumentation-bedrock/
- **What it instruments:** Boto3 calls to Bedrock (same methods as above)

### Usage Example

```python
from openinference.instrumentation.bedrock import BedrockInstrumentor
from honeyhive import HoneyHiveTracer
import boto3

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(project="bedrock-llm-calls")

# Instrument Bedrock API calls
BedrockInstrumentor().instrument(tracer_provider=tracer.provider)

# Now all Bedrock API calls are traced
client = boto3.client('bedrock-runtime')
response = client.converse(
    modelId='anthropic.claude-3-sonnet',
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
# ✅ This API call is traced with LLM attributes (model, tokens, latency, etc.)
```

### What Gets Traced

When using Bedrock instrumentors:
- ✅ Model ID (e.g., `anthropic.claude-3-sonnet`)
- ✅ Prompt/messages
- ✅ Completion/response
- ✅ Token usage (input/output tokens)
- ✅ Latency
- ✅ Streaming support
- ✅ Tool calls (if using function calling)
- ✅ RAG operations (retrieve, retrieve_and_generate)

---

## Amazon Bedrock AgentCore (Deployment Platform)

### What It Is

**Amazon Bedrock AgentCore** is an **agent deployment and runtime platform** - AWS's version of a serverless platform for AI agents.

- NOT an LLM service - it's infrastructure for running agents
- Framework-agnostic (works with any agent: LangChain, CrewAI, custom code)
- Provides: HTTP runtime, memory service, tool integrations, authentication
- Competes with: Self-managed servers, AWS Lambda with custom setup, containerized deployments

### Architecture

```
┌────────────────────────────────────────────────────────┐
│  AWS Bedrock AgentCore (Managed Runtime)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  HTTP Server (receives requests)                 │  │
│  └──────────────────────────────────────────────────┘  │
│                        ▼                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  BedrockAgentCoreApp (Python SDK)                │  │
│  │  Routes request to user's function               │  │
│  └──────────────────────────────────────────────────┘  │
│                        ▼                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  YOUR AGENT CODE                                 │  │
│  │  - LangChain agent                               │  │
│  │  - Makes OpenAI/Anthropic/Bedrock API calls     │  │
│  │  ◄─── THIS is where LLM calls happen            │  │
│  │  ◄─── THIS is what needs instrumentation        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  AWS Services (optional):                             │
│  - Memory (persistent conversation storage)           │
│  - Browser (web automation)                           │
│  - Code Interpreter (sandboxed Python execution)      │
└────────────────────────────────────────────────────────┘
```

### Code Example

```python
from bedrock_agentcore import BedrockAgentCoreApp
from langchain.agents import create_openai_functions_agent

# BedrockAgentCoreApp is just HTTP routing
app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # YOUR agent code runs here
    # YOU make LLM API calls here (not AgentCore)
    agent = create_openai_functions_agent(llm, tools, prompt)
    return agent.invoke({"input": request.get("prompt")})

# This starts an HTTP server (like FastAPI/Flask)
app.run()
```

### Existing Instrumentors

**❌ NONE** - And it doesn't make sense to create one.

Why? Because Bedrock AgentCore SDK:
- Does NOT make LLM calls
- Does NOT execute agent logic
- Only routes HTTP requests to user functions

It's like asking "Should I create a FastAPI instrumentor?" or "Should I create an AWS Lambda instrumentor?"
- Answer: No, you instrument the **application code running on those platforms**

### What to Instrument Instead

**✅ Instrument YOUR agent framework:**

```python
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(project="my-agent-on-agentcore")

# Instrument YOUR agent framework (LangChain example)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # Optional: Add AgentCore context to spans
    span = trace.get_current_span()
    if span:
        span.set_attribute("agentcore.session_id", 
                          BedrockAgentCoreContext.get_session_id())
        span.set_attribute("agentcore.request_id", 
                          BedrockAgentCoreContext.get_request_id())
    
    # Your LangChain agent (instrumented automatically)
    return my_langchain_agent.invoke({"input": request.get("prompt")})

app.run()
```

### What Gets Traced

When running on Bedrock AgentCore with proper instrumentation:
- ✅ Your agent's LLM calls (via OpenAI/Anthropic/Bedrock instrumentors)
- ✅ Agent framework execution (via LangChain/CrewAI instrumentors)
- ✅ Tool invocations
- ✅ AgentCore context (session_id, request_id) as span attributes
- ❌ HTTP routing (not useful for LLM observability)

---

## Comparison Table

| Aspect | Amazon Bedrock (LLM Service) | Amazon Bedrock AgentCore (Platform) |
|--------|----------------------------|-----------------------------------|
| **Service Type** | LLM API | Agent deployment platform |
| **Analogous To** | OpenAI API, Anthropic API | AWS Lambda, FastAPI, Fly.io |
| **Makes LLM Calls?** | ✅ YES - this IS the LLM service | ❌ NO - user's code makes calls |
| **Client Library** | `boto3.client('bedrock-runtime')` | `bedrock-agentcore` SDK (HTTP wrapper) |
| **Instrumentor Exists?** | ✅ YES - OpenInference, Traceloop | ❌ NO - not needed |
| **What to Instrument** | The Boto3 client calls | User's agent framework |
| **PyPI Packages** | `openinference-instrumentation-bedrock`<br>`opentelemetry-instrumentation-bedrock` | None (instrument your agent code) |
| **Traces Capture** | Model, prompts, tokens, latency | Agent logic, tool calls, LLM calls |
| **Use Case** | Direct LLM API access | Deploying complete agents |

---

## Common Confusion Scenarios

### Scenario 1: Using Bedrock LLM Service Directly

```python
# Using Amazon Bedrock (the LLM service)
import boto3

client = boto3.client('bedrock-runtime')
response = client.converse(
    modelId='anthropic.claude-3-sonnet',
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
```

**What to instrument:** `boto3` Bedrock calls  
**Instrumentor:** `openinference-instrumentation-bedrock` or `opentelemetry-instrumentation-bedrock`

---

### Scenario 2: Using Bedrock AgentCore with OpenAI

```python
# Running on Bedrock AgentCore (the platform)
# But calling OpenAI (not Bedrock LLM service)
from bedrock_agentcore import BedrockAgentCoreApp
from openai import OpenAI

app = BedrockAgentCoreApp()
client = OpenAI()

@app.entrypoint
def my_agent(request):
    # Calling OpenAI, not Bedrock
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": request.get("prompt")}]
    )
    return response.choices[0].message.content

app.run()
```

**What to instrument:** OpenAI calls (NOT Bedrock, NOT AgentCore)  
**Instrumentor:** `opentelemetry-instrumentation-openai`  
**Why:** You're using OpenAI API, just deployed on AgentCore platform

---

### Scenario 3: Using Bedrock AgentCore with Bedrock LLM Service

```python
# Running on Bedrock AgentCore (the platform)
# AND calling Bedrock LLM service
from bedrock_agentcore import BedrockAgentCoreApp
import boto3

app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # Calling Bedrock LLM service
    client = boto3.client('bedrock-runtime')
    response = client.converse(
        modelId='anthropic.claude-3-sonnet',
        messages=[{"role": "user", "content": [{"text": request.get("prompt")}]}]
    )
    return response['output']['message']['content'][0]['text']

app.run()
```

**What to instrument:** Bedrock LLM API calls (NOT AgentCore)  
**Instrumentor:** `openinference-instrumentation-bedrock`  
**Why:** You're calling Bedrock LLM service, just deployed on AgentCore platform

---

### Scenario 4: Using Bedrock AgentCore with LangChain

```python
# Running on Bedrock AgentCore (the platform)
# Using LangChain (which might call any LLM)
from bedrock_agentcore import BedrockAgentCoreApp
from langchain.agents import create_openai_functions_agent

app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # LangChain agent execution
    agent = create_openai_functions_agent(llm, tools, prompt)
    return agent.invoke({"input": request.get("prompt")})

app.run()
```

**What to instrument:** LangChain + underlying LLM (NOT AgentCore)  
**Instrumentors:** 
- `opentelemetry-instrumentation-langchain` (for LangChain chains/agents)
- Plus LLM-specific instrumentor based on what LLM LangChain uses:
  - `opentelemetry-instrumentation-openai` (if using OpenAI)
  - `openinference-instrumentation-bedrock` (if using Bedrock)
  - `opentelemetry-instrumentation-anthropic` (if using Anthropic)

---

## Key Takeaways

1. **Amazon Bedrock** (LLM service) ≠ **Amazon Bedrock AgentCore** (deployment platform)
   - Different services with similar names
   - Bedrock = LLM API
   - Bedrock AgentCore = Agent hosting platform

2. **Bedrock instrumentors exist and work great**
   - Use them when you call Bedrock LLM API directly
   - They instrument `boto3.client('bedrock-runtime')` calls
   - Capture model, prompts, tokens, latency

3. **Don't instrument Bedrock AgentCore SDK**
   - It's just HTTP routing (like FastAPI/Lambda)
   - Instrument your agent code instead
   - Add AgentCore context (session_id, request_id) as span attributes

4. **Can use both together**
   - Run agent on Bedrock AgentCore platform
   - Call Bedrock LLM API from your agent
   - Instrument Bedrock LLM calls with Bedrock instrumentor
   - Add AgentCore context enrichment for correlation

---

## For HoneyHive Documentation

**Recommended Documentation Structure:**

1. **"Instrumenting Amazon Bedrock (LLM API)"**
   - Use case: Direct Bedrock API calls
   - Instrumentor: `openinference-instrumentation-bedrock`
   - Captures: Model, prompts, tokens, latency

2. **"Instrumenting Agents on Amazon Bedrock AgentCore"**
   - Use case: Agents deployed on AgentCore platform
   - Instrumentor: Based on agent framework (LangChain, etc.)
   - Context enrichment: Add session_id, request_id from AgentCore
   - Note: AgentCore is the platform, not the agent itself

3. **"Combined Setup: Bedrock LLM on Bedrock AgentCore"**
   - Use case: Agent on AgentCore calling Bedrock API
   - Instrumentors: Both Bedrock instrumentor + context enrichment
   - Shows complete integration

---

**Date:** 2025-10-15  
**References:**
- Amazon Bedrock: https://aws.amazon.com/bedrock/
- Amazon Bedrock AgentCore: https://aws.amazon.com/bedrock/agentcore/
- OpenInference Bedrock: https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-bedrock
- Traceloop Bedrock: https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-bedrock
- AWS Bedrock AgentCore Analysis: `AWS_BEDROCK_AGENTCORE_ANALYSIS.md`

