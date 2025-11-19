# AWS Bedrock AgentCore SDK Analysis Report

**Date:** 2025-10-15  
**Analyst:** AI Assistant  
**Analysis Version:** Based on SDK_ANALYSIS_METHODOLOGY.md v1.3  
**SDK Version Analyzed:** v1.0.0 (Released 2025-10-15)

---

## Executive Summary

**🚨 CRITICAL FINDING: This SDK is fundamentally different from typical instrumentation targets**

- **SDK Purpose:** **Deployment runtime platform** - NOT an agent framework itself
- **SDK Type:** Framework-agnostic HTTP wrapper for AI agents (wraps ANY agent code)
- **LLM Client:** **NONE** - SDK does not make LLM calls; user agents do
- **Observability:** **❌ NONE** - No OpenTelemetry, no custom tracing, no telemetry infrastructure
- **Existing Instrumentors:** **❌ NO** - No instrumentors exist (OpenInference, Traceloop, OpenLIT)
- **HoneyHive BYOI Compatible:** **⚠️ NOT APPLICABLE** - SDK is not the instrumentation target
- **Recommended Approach:** **Instrument user agent frameworks**, not Bedrock AgentCore SDK itself

### Key Insight

AWS Bedrock AgentCore is analogous to **AWS Lambda** or **FastAPI** for agent deployment:
- It provides **runtime infrastructure** (HTTP server, memory services, auth, tools)
- User brings their own agent logic (LangGraph, CrewAI, Strands, custom code)
- AgentCore **wraps** user functions as HTTP endpoints
- **User's agent code** makes LLM calls, not the AgentCore SDK

**Instrumentation Strategy:**
- ✅ **DO:** Instrument the **user's agent framework** (LangGraph, CrewAI, etc.)
- ❌ **DON'T:** Try to instrument Bedrock AgentCore SDK (it's just HTTP routing)
- ⚠️ **CONSIDER:** Custom span enrichment to capture AgentCore-specific context (session_id, request_id)

---

## Phase 1: Initial Discovery

### 1.1 Repository Metadata

**GitHub:** https://github.com/aws/bedrock-agentcore-sdk-python  
**PyPI:** https://pypi.org/project/bedrock-agentcore/  
**Version:** 1.0.0 (GA release: 2025-10-15)

**Dependencies:**
```python
dependencies = [
    "boto3>=1.40.35",
    "botocore>=1.40.35",
    "pydantic>=2.0.0,<2.41.3",
    "urllib3>=1.26.0",
    "starlette>=0.46.2",
    "typing-extensions>=4.13.2,<5.0.0",
    "uvicorn>=0.34.2",
]
```

**Optional Dependencies:**
- `strands-agents>=1.1.0` (for Strands memory integration)

**Python Support:** >= 3.10

**Key Features Listed:**
- 🚀 **Runtime** - HTTP server wrapping user agent functions
- 🧠 **Memory** - AWS-managed persistent memory service (Boto3 client)
- 🔗 **Gateway** - API-to-MCP tool transformation (AWS-managed)
- 💻 **Code Interpreter** - Sandboxed execution (AWS-managed service)
- 🌐 **Browser** - Web automation (AWS-managed service)
- 📊 **Observability** - **CLAIMED but NOT IMPLEMENTED in SDK**
- 🔐 **Identity** - OAuth2 and API key authentication (AWS-managed)

### 1.2 File Structure

**Total Lines of Code:** ~6,133 lines  
**Total Python Files:** 27 files

**Module Structure:**
```
src/bedrock_agentcore/
├── __init__.py              # Main exports: BedrockAgentCoreApp, BedrockAgentCoreContext
├── runtime/                 # HTTP server (Starlette-based)
│   ├── app.py              # Main app class (Starlette wrapper) ~534 lines
│   ├── models.py           # PingStatus, header constants
│   ├── context.py          # RequestContext, ContextVars
│   └── utils.py            # JSON serialization helpers
├── memory/                  # AWS Memory service client
│   ├── client.py           # High-level memory operations ~1,854 lines
│   ├── controlplane.py     # Control plane API wrapper
│   ├── session.py          # Session management
│   ├── constants.py        # Enums and constants
│   └── integrations/
│       └── strands/        # Strands framework integration
│           ├── config.py
│           ├── session_manager.py
│           └── bedrock_converter.py
├── tools/                   # AWS-managed tool clients
│   ├── browser_client.py   # Browser service (Boto3)
│   └── code_interpreter_client.py  # Code execution service (Boto3)
├── identity/                # Authentication
│   └── auth.py             # OAuth2 and API key decorators
└── services/                # Service clients
    └── identity.py         # Identity service client
```

### 1.3 Entry Point Discovery

**Main User-Facing Class:** `BedrockAgentCoreApp`

**Typical Usage Pattern:**
```python
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def production_agent(request):
    # YOUR agent logic here (LangGraph, CrewAI, Strands, custom)
    return my_agent.run(request.get("prompt"))

app.run()  # Starts HTTP server (Starlette/Uvicorn)
```

**What BedrockAgentCoreApp Does:**
1. Creates Starlette ASGI application
2. Registers `/invocations` (POST) and `/ping` (GET) endpoints
3. Wraps user function to handle HTTP request/response
4. Manages context (session_id, request_id, workload_access_token)
5. Provides async task tracking for ping status

**What BedrockAgentCoreApp Does NOT Do:**
- ❌ Does NOT make LLM API calls
- ❌ Does NOT implement agent logic
- ❌ Does NOT create traces/spans
- ❌ Does NOT instrument anything

---

## Phase 1.5: Existing Instrumentor Discovery

### Instrumentor Search Results

| Provider | Package Name | Status | GitHub | PyPI |
|----------|-------------|---------|--------|------|
| **OpenInference (Arize)** | openinference-instrumentation-bedrock-agentcore | ❌ **NOT FOUND** | Not in https://github.com/Arize-ai/openinference/tree/main/python/instrumentation | N/A |
| **Traceloop (OpenLLMetry)** | opentelemetry-instrumentation-bedrock-agentcore | ❌ **NOT FOUND** | Not in https://github.com/traceloop/openllmetry/tree/main/packages | N/A |
| **OpenLIT** | openlit (with bedrock-agentcore support) | ❌ **NOT FOUND** | Not in https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation | N/A |

**Search Methods Used:**
- ✅ Checked OpenInference GitHub repository
- ✅ Checked Traceloop GitHub repository
- ✅ Checked OpenLIT GitHub repository
- ✅ Searched PyPI
- ✅ Web searches (multiple queries)
- ✅ Checked SDK documentation (README, CHANGELOG)

### Why No Instrumentors Exist

**Reason:** Bedrock AgentCore is a **runtime wrapper**, not an agent framework.

Instrumentors target **LLM-calling frameworks**:
- LangChain instrumentors capture chain/agent execution
- OpenAI instrumentors capture `client.chat.completions.create()` calls
- Anthropic instrumentors capture `client.messages.create()` calls

Bedrock AgentCore SDK:
- Does NOT call LLMs
- Does NOT execute agent logic
- Only routes HTTP requests to user functions
- User functions contain the actual agent code (which should be instrumented)

**Analogy:** You wouldn't create a "FastAPI instrumentor" or "AWS Lambda instrumentor" - you instrument the **application code running on those platforms**.

---

## Phase 2: LLM Client Discovery

### 2.1 LLM Client Analysis

**Finding:** The SDK itself does **NOT use any LLM client libraries**.

**No LLM dependencies found:**
```bash
$ grep -i "openai\|anthropic\|google\|cohere\|azure" pyproject.toml
# No results

$ grep -r "^import openai\|^from openai\|^import anthropic" src/
# No results
```

**Only Strands Integration Found:**
```python
# In memory/integrations/strands/
from strands.types.session import SessionMessage
from strands.hooks import MessageAddedEvent
from strands.agent.agent import Agent
```

This is NOT for LLM calls - it's for **memory service integration** with the Strands framework.

### 2.2 Architecture Clarification

**Bedrock AgentCore SDK Architecture:**

```
┌─────────────────────────────────────────────────────┐
│  AWS Bedrock AgentCore Runtime (Managed Service)    │
│  ┌───────────────────────────────────────────────┐  │
│  │  HTTP Server (receives POST /invocations)     │  │
│  └───────────────────────────────────────────────┘  │
│                       │                              │
│                       ▼                              │
│  ┌───────────────────────────────────────────────┐  │
│  │   BedrockAgentCoreApp.entrypoint()            │  │
│  │   (routes request to user function)           │  │
│  └───────────────────────────────────────────────┘  │
│                       │                              │
│                       ▼                              │
│  ┌───────────────────────────────────────────────┐  │
│  │   USER'S AGENT CODE                           │  │
│  │   - LangGraph chain/agent                     │  │
│  │   - CrewAI crew                               │  │
│  │   - Strands agent                             │  │
│  │   - Custom OpenAI calls                       │  │
│  │   ◄─── THIS IS WHERE LLM CALLS HAPPEN        │  │
│  │   ◄─── THIS IS WHERE INSTRUMENTATION NEEDED  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**User's Agent Code Example:**
```python
# User writes this - NOT in Bedrock AgentCore SDK
from langchain.agents import create_openai_functions_agent
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# This is where LangChain code (which SHOULD be instrumented) runs
@app.entrypoint
def my_agent(request):
    agent = create_openai_functions_agent(llm, tools, prompt)
    result = agent.invoke({"input": request.get("prompt")})
    return result["output"]

app.run()
```

### 2.3 Summary: No LLM Client in SDK

- ❌ SDK does NOT import openai, anthropic, or any LLM client
- ❌ SDK does NOT make `chat.completions.create()` or similar calls
- ✅ SDK only manages HTTP routing and AWS service integration (memory, browser, code interpreter)
- ✅ **USER'S code** (wrapped by SDK) makes LLM calls

---

## Phase 3: Observability System Analysis

### 3.1 Built-in Tracing Detection

**Finding:** **NO built-in tracing or observability system exists**.

**Searches Conducted:**
```bash
$ grep -r "opentelemetry\|otel" src/ --include="*.py"
# No results

$ grep -r "tracing\|tracer\|telemetry\|observability" src/ --include="*.py"
# No results

$ grep -r "span\|trace" src/ --include="*.py" | grep -v "transport"
# No results (only "transport" in unrelated contexts)
```

**Documentation Claims vs Reality:**

| Claim (from README/Web Search) | Reality (from Code Analysis) |
|--------------------------------|------------------------------|
| "📊 **Observability** - OpenTelemetry tracing" | ❌ No OpenTelemetry imports or usage |
| "OpenTelemetry-compatible telemetry for tracing, debugging, and monitoring" | ❌ No telemetry infrastructure in SDK code |
| "Advanced tracing, monitoring, and debugging capabilities" | ❌ No tracing/monitoring code found |

**What EXISTS in the SDK:**
- ✅ Structured logging (JSON format for AWS Lambda)
- ✅ Request/session context propagation (ContextVars)
- ✅ Request ID and Session ID tracking
- ✅ Ping/health status management
- ❌ NO trace/span creation
- ❌ NO OTEL instrumentation

### 3.2 Context Management

**What the SDK Provides:**

```python
# From runtime/context.py
class BedrockAgentCoreContext:
    _workload_access_token: ContextVar[Optional[str]]
    _request_id: ContextVar[Optional[str]]
    _session_id: ContextVar[Optional[str]]
    _request_headers: ContextVar[Optional[Dict[str, str]]]
    
    @classmethod
    def get_request_id(cls) -> Optional[str]:
        # Returns current request ID
    
    @classmethod
    def get_session_id(cls) -> Optional[str]:
        # Returns current session ID
```

**Logging with Context:**
```python
# From runtime/app.py
class RequestContextFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": ...,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add context if available
        request_id = BedrockAgentCoreContext.get_request_id()
        if request_id:
            log_entry["requestId"] = request_id
            
        session_id = BedrockAgentCoreContext.get_session_id()
        if session_id:
            log_entry["sessionId"] = session_id
```

**Value for Instrumentation:**
- ✅ `request_id` - Unique identifier for each HTTP request
- ✅ `session_id` - Identifier for conversation session
- ✅ `workload_access_token` - AWS workload identity token
- ✅ `request_headers` - Custom headers (Authorization + X-Amzn-Bedrock-AgentCore-Runtime-Custom-*)

These context values **can be added as span attributes** in user's instrumented agent code.

### 3.3 Observability Verdict

**Observability Infrastructure:** ❌ **NONE**

- No OpenTelemetry integration
- No custom tracing system
- No span/trace creation APIs
- Only logging and context management

**What "observability" means in AgentCore:**
- Observability is **user's responsibility** to instrument their agent code
- AgentCore provides **context** (request_id, session_id) that can be used
- Observability happens **outside the SDK** in user's agent framework

---

## Phase 4: Architecture Deep Dive

### 4.1 Core Flow Analysis

**Execution Flow:**

```
1. HTTP POST /invocations arrives at AgentCore runtime (AWS-managed)
2. BedrockAgentCoreApp._handle_invocation(request) called
3. Request context extracted:
   - X-Amzn-Bedrock-AgentCore-Runtime-Request-Id → request_id
   - X-Amzn-Bedrock-AgentCore-Runtime-Session-Id → session_id
   - WorkloadAccessToken → workload_access_token
4. ContextVars set for the request scope
5. User's @app.entrypoint function invoked with request payload
6. ┌─────────────────────────────────────────┐
   │  USER'S AGENT CODE EXECUTES HERE       │
   │  - LangGraph runs                       │
   │  - CrewAI runs                          │
   │  - OpenAI client calls made             │
   │  ◄─── INSTRUMENTATION HAPPENS HERE     │
   └─────────────────────────────────────────┘
7. User function returns result
8. Result serialized to JSON (or streamed as SSE)
9. HTTP response sent back to client
```

**Key Code Locations:**

**`runtime/app.py:318-366` - Request Handler:**
```python
async def _handle_invocation(self, request):
    # Build request context (session_id, request_id, headers)
    request_context = self._build_request_context(request)
    
    # Get user's entrypoint handler
    handler = self.handlers.get("main")
    
    # Invoke user's function (THIS IS WHERE USER'S AGENT RUNS)
    result = await self._invoke_handler(
        handler, 
        request_context, 
        takes_context, 
        payload
    )
    
    # Handle streaming vs non-streaming responses
    if inspect.isgenerator(result):
        return StreamingResponse(self._sync_stream_with_error_handling(result))
    elif inspect.isasyncgen(result):
        return StreamingResponse(self._stream_with_error_handling(result))
    
    return Response(safe_json_string, media_type="application/json")
```

**`runtime/app.py:405-418` - User Function Invocation:**
```python
async def _invoke_handler(self, handler, request_context, takes_context, payload):
    args = (payload, request_context) if takes_context else (payload,)
    
    if asyncio.iscoroutinefunction(handler):
        return await handler(*args)  # User's async function
    else:
        # Run sync function in executor with context propagation
        loop = asyncio.get_event_loop()
        ctx = contextvars.copy_context()
        return await loop.run_in_executor(None, ctx.run, handler, *args)
```

**No Instrumentation Hooks:**
- ❌ No `before_invoke` / `after_invoke` hooks
- ❌ No span processor injection points
- ❌ No middleware system for instrumentation
- ✅ Only HTTP middleware (Starlette ASGI middleware could be used externally)

### 4.2 Agent/Handoff Analysis

**Finding:** **NO agent concepts in the SDK**.

Bedrock AgentCore does NOT implement:
- ❌ Agent classes
- ❌ Tool calling mechanisms
- ❌ Handoff logic
- ❌ Guardrails
- ❌ Planning/reasoning

All agent concepts are in **user's code** (LangGraph, CrewAI, Strands, custom logic).

**SDK's Role:**
- HTTP wrapper for user's agent
- Context management (session, request IDs)
- Integration with AWS services (memory, tools, auth)

### 4.3 AWS Service Integration

**AWS Services Used by SDK:**

**1. Memory Service** (`bedrock-agentcore` and `bedrock-agentcore-control`):
```python
# memory/client.py
self.gmcp_client = boto3.client("bedrock-agentcore-control", region_name=region)
self.gmdp_client = boto3.client("bedrock-agentcore", region_name=region)

# Operations:
# - create_memory, list_memories, delete_memory
# - create_event (save conversations)
# - retrieve_memory_records (semantic search)
# - add_semantic_strategy, add_summary_strategy
```

**2. Code Interpreter Service** (`bedrock-agentcore`):
```python
# tools/code_interpreter_client.py
client = boto3.client("bedrock-agentcore", region_name=region)

# Operations:
# - create_code_session
# - execute_code (Python execution in sandbox)
```

**3. Browser Service** (`bedrock-agentcore`):
```python
# tools/browser_client.py  
client = boto3.client("bedrock-agentcore", region_name=region)

# Operations:
# - create_browser_session
# - navigate, click, type, screenshot
```

**4. Identity Service** (`bedrock-agentcore-identity`):
```python
# services/identity.py
client = boto3.client("bedrock-agentcore-identity", region_name=region)

# Operations:
# - get_resource_oauth2_token
# - get_workload_access_token  
# - create_workload_identity
```

**Instrumentation Considerations:**
- These are AWS API calls via Boto3
- Could be instrumented with **AWS SDK instrumentors** (separate from agent instrumentation)
- HoneyHive may already capture AWS SDK calls if using Boto3 instrumentor

---

## Phase 5: Integration Strategy & Testing

### 5.1 Instrumentation Strategy

**⚠️ PARADIGM SHIFT: Don't Instrument Bedrock AgentCore SDK**

Unlike typical SDK analysis (LangChain, OpenAI, etc.), Bedrock AgentCore is **NOT the instrumentation target**.

**Correct Approach:**

```python
# ✅ CORRECT: Instrument user's agent framework
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangChainInstrumentor  # Example
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(project="my-agents")

# Instrument LangChain (user's framework choice)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # Get AgentCore context for span enrichment
    session_id = BedrockAgentCoreContext.get_session_id()
    request_id = BedrockAgentCoreContext.get_request_id()
    
    # Add AgentCore context to current span
    from opentelemetry import trace
    span = trace.get_current_span()
    if span:
        span.set_attribute("agentcore.session_id", session_id)
        span.set_attribute("agentcore.request_id", request_id)
    
    # Run LangChain agent (instrumentation captures this)
    result = my_langchain_agent.invoke({"input": request.get("prompt")})
    return result["output"]

app.run()
```

**What Gets Instrumented:**
- ✅ User's agent framework (LangChain, LangGraph, CrewAI, etc.)
- ✅ LLM client calls (OpenAI, Anthropic, etc.)
- ✅ Optional: AWS SDK calls (Boto3 Memory/Browser/Code Interpreter)
- ❌ BedrockAgentCoreApp HTTP routing (not useful for LLM observability)

**AgentCore Context Enrichment:**
```python
# Helper function to add AgentCore context to spans
def enrich_span_with_agentcore_context(span):
    """Add Bedrock AgentCore context to current OpenTelemetry span."""
    session_id = BedrockAgentCoreContext.get_session_id()
    if session_id:
        span.set_attribute("agentcore.session_id", session_id)
    
    request_id = BedrockAgentCoreContext.get_request_id()
    if request_id:
        span.set_attribute("agentcore.request_id", request_id)
    
    headers = BedrockAgentCoreContext.get_request_headers()
    if headers:
        # Add relevant custom headers
        for key, value in headers.items():
            if key.startswith("X-Amzn-Bedrock-AgentCore-Runtime-Custom-"):
                span.set_attribute(f"agentcore.header.{key}", value)
```

### 5.2 Integration Patterns

**Pattern 1: LangChain/LangGraph Agents on AgentCore**

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangChainInstrumentor
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

# Initialize tracing
tracer = HoneyHiveTracer.init(project="langchain-on-agentcore")
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()

# Create LangChain agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

@app.entrypoint
def my_langchain_agent(request):
    # Add AgentCore context to root span
    from opentelemetry import trace
    span = trace.get_current_span()
    if span:
        span.set_attribute("agentcore.session_id", 
                          BedrockAgentCoreContext.get_session_id())
        span.set_attribute("agentcore.request_id", 
                          BedrockAgentCoreContext.get_request_id())
    
    # LangChain execution (automatically traced)
    result = agent_executor.invoke({"input": request.get("prompt")})
    return result["output"]

app.run()
```

**What Gets Traced:**
- ✅ LangChain agent execution (chains, tools, LLM calls)
- ✅ OpenAI API calls
- ✅ Tool invocations
- ✅ AgentCore session/request context as span attributes
- ❌ HTTP routing (not traced, not useful)

---

**Pattern 2: CrewAI Crews on AgentCore**

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.crewai import CrewAIInstrumentor  # If exists
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from crewai import Agent, Task, Crew

# Initialize tracing
tracer = HoneyHiveTracer.init(project="crewai-on-agentcore")
# Assume CrewAI instrumentor exists
CrewAIInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()

# Define CrewAI crew
researcher = Agent(role='Researcher', goal='...')
writer = Agent(role='Writer', goal='...')
crew = Crew(agents=[researcher, writer], tasks=[...])

@app.entrypoint
def my_crew_agent(request):
    # Add AgentCore context
    from opentelemetry import trace
    span = trace.get_current_span()
    if span:
        span.set_attribute("agentcore.session_id", 
                          BedrockAgentCoreContext.get_session_id())
    
    # CrewAI execution (automatically traced if instrumentor exists)
    result = crew.kickoff(inputs={"topic": request.get("prompt")})
    return result

app.run()
```

---

**Pattern 3: Strands Agents with AgentCore Memory**

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.strands import StrandsInstrumentor  # If exists
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from bedrock_agentcore.memory.integrations.strands import AgentCoreMemoryConfig
from strands import Agent

# Initialize tracing
tracer = HoneyHiveTracer.init(project="strands-on-agentcore")
StrandsInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()

# Configure Strands with AgentCore Memory
memory_config = AgentCoreMemoryConfig(
    memory_id="mem-xyz",
    region="us-west-2"
)

agent = Agent(
    name="ResearchAgent",
    instructions="You are a helpful research assistant",
    memory_config=memory_config
)

@app.entrypoint
def my_strands_agent(request):
    # Strands execution (automatically traced if instrumentor exists)
    result = agent.run(request.get("prompt"))
    
    # AgentCore Memory calls (could be traced with Boto3 instrumentor)
    return result

app.run()
```

---

**Pattern 4: Custom Agents (Manual Instrumentation)**

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from openai import OpenAI

# Initialize tracing
tracer = HoneyHiveTracer.init(project="custom-agent-on-agentcore")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()
client = OpenAI()

@app.entrypoint
def my_custom_agent(request):
    from opentelemetry import trace
    
    # Create custom span for agent logic
    tracer_obj = trace.get_tracer(__name__)
    with tracer_obj.start_as_current_span("custom_agent_execution") as span:
        # Add AgentCore context
        span.set_attribute("agentcore.session_id", 
                          BedrockAgentCoreContext.get_session_id())
        span.set_attribute("agentcore.request_id", 
                          BedrockAgentCoreContext.get_request_id())
        span.set_attribute("agent.name", "CustomAgent")
        span.set_attribute("agent.version", "1.0")
        
        # OpenAI call (automatically traced by OpenAIInstrumentor)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": request.get("prompt")}]
        )
        
        result = response.choices[0].message.content
        span.set_attribute("agent.output_length", len(result))
        
        return result

app.run()
```

### 5.3 AWS Service Instrumentation (Optional)

**Instrumenting AgentCore Memory/Browser/Code Interpreter Calls:**

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.boto3 import Boto3Instrumentor  # If exists
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.tools import code_session

# Initialize tracing
tracer = HoneyHiveTracer.init(project="agentcore-aws-services")

# Instrument Boto3 to capture AWS API calls
Boto3Instrumentor().instrument(tracer_provider=tracer.provider)

app = BedrockAgentCoreApp()
memory_client = MemoryClient(region_name="us-west-2")

@app.entrypoint
def agent_with_memory(request):
    # Memory operations (traced via Boto3 instrumentor)
    memories = memory_client.retrieve_memories(
        memory_id="mem-xyz",
        namespace="support/facts/session-123",
        query=request.get("prompt"),
        top_k=5
    )
    
    # Use memories in agent logic...
    
    # Code execution (also traced via Boto3)
    with code_session(region="us-west-2") as code_interp:
        result = code_interp.execute("print('Hello')")
    
    return result

app.run()
```

**What Gets Traced:**
- ✅ `bedrock-agentcore.CreateEvent` (save conversation)
- ✅ `bedrock-agentcore.RetrieveMemoryRecords` (semantic search)
- ✅ `bedrock-agentcore.ExecuteCode` (code execution)
- ✅ `bedrock-agentcore.CreateBrowserSession` (browser automation)
- ✅ API latency, request/response payloads

### 5.4 Recommended Instrumentation Stack

**For LangChain/LangGraph Agents:**
```python
# Install
pip install honeyhive \
    opentelemetry-instrumentation-langchain \
    bedrock-agentcore

# Instrument
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangChainInstrumentor

tracer = HoneyHiveTracer.init(project="my-project")
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)
```

**For Custom Agents:**
```python
# Install
pip install honeyhive \
    opentelemetry-instrumentation-openai \
    opentelemetry-instrumentation-anthropic \
    bedrock-agentcore

# Instrument
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

tracer = HoneyHiveTracer.init(project="my-project")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
AnthropicInstrumentor().instrument(tracer_provider=tracer.provider)
```

**Add AgentCore Context Enrichment:**
```python
# Create middleware or helper
from opentelemetry import trace
from bedrock_agentcore import BedrockAgentCoreContext

def add_agentcore_context_to_span():
    """Call at the start of your entrypoint function."""
    span = trace.get_current_span()
    if span and span.is_recording():
        session_id = BedrockAgentCoreContext.get_session_id()
        if session_id:
            span.set_attribute("agentcore.session_id", session_id)
        
        request_id = BedrockAgentCoreContext.get_request_id()
        if request_id:
            span.set_attribute("agentcore.request_id", request_id)

# Use in entrypoint
@app.entrypoint
def my_agent(request):
    add_agentcore_context_to_span()  # Add context first
    # ... rest of agent logic
```

---

## Phase 6: Documentation & Delivery

### 6.1 Summary of Findings

**SDK Classification:** Runtime Platform (NOT an Agent Framework)

**Key Architectural Insights:**

1. **Bedrock AgentCore is a Wrapper, Not a Framework**
   - Analogous to AWS Lambda, FastAPI, or Flask for agents
   - Provides HTTP server + AWS service integrations
   - User brings their own agent logic

2. **No LLM Calls in SDK**
   - User's code makes LLM calls (via OpenAI, Anthropic, etc.)
   - SDK just routes HTTP requests to user functions

3. **No Built-in Observability**
   - Documentation claims observability, but code doesn't implement it
   - No OpenTelemetry integration in SDK
   - Only logging and context management

4. **No Existing Instrumentors**
   - None found (OpenInference, Traceloop, OpenLIT)
   - Makes sense - you instrument the agent framework, not the runtime

5. **Context Management Exists**
   - SDK provides session_id, request_id, headers via ContextVars
   - Can be added as span attributes for correlation

### 6.2 HoneyHive Integration Guidance

**✅ DO:**

1. **Instrument User's Agent Framework**
   - LangChain: Use `opentelemetry-instrumentation-langchain`
   - OpenAI: Use `opentelemetry-instrumentation-openai`
   - Anthropic: Use `opentelemetry-instrumentation-anthropic`
   - CrewAI: Check for instrumentor or manual instrumentation
   - Strands: Check for instrumentor or manual instrumentation

2. **Add AgentCore Context Enrichment**
   ```python
   span.set_attribute("agentcore.session_id", BedrockAgentCoreContext.get_session_id())
   span.set_attribute("agentcore.request_id", BedrockAgentCoreContext.get_request_id())
   ```

3. **Optional: Instrument AWS Services**
   - Use Boto3 instrumentor to capture Memory/Browser/Code Interpreter calls
   - Provides visibility into AgentCore service usage

**❌ DON'T:**

1. **Don't Create Bedrock AgentCore SDK Instrumentor**
   - SDK doesn't make LLM calls
   - Only HTTP routing (not valuable for LLM observability)
   - Would be like instrumenting FastAPI/Lambda itself

2. **Don't Instrument Starlette Middleware**
   - HTTP request/response timing not useful for agent observability
   - Focus on agent execution and LLM calls instead

### 6.3 Documentation Recommendations

**For HoneyHive Documentation:**

Create guide: **"Tracing AI Agents on AWS Bedrock AgentCore"**

```markdown
# Tracing AI Agents on AWS Bedrock AgentCore

AWS Bedrock AgentCore is a deployment platform for AI agents. To trace your agents
running on AgentCore, instrument **your agent code**, not the AgentCore SDK.

## Quick Start

### Step 1: Instrument Your Agent Framework

Choose based on your agent framework:

**LangChain/LangGraph:**
```python
pip install honeyhive opentelemetry-instrumentation-langchain bedrock-agentcore

from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangChainInstrumentor

tracer = HoneyHiveTracer.init(project="my-agents")
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)
```

**Custom OpenAI Agents:**
```python
pip install honeyhive opentelemetry-instrumentation-openai bedrock-agentcore

from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(project="my-agents")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
```

### Step 2: Add AgentCore Context

Enrich traces with AgentCore session and request IDs:

```python
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from opentelemetry import trace

app = BedrockAgentCoreApp()

@app.entrypoint
def my_agent(request):
    # Add AgentCore context to current span
    span = trace.get_current_span()
    if span:
        span.set_attribute("agentcore.session_id", 
                          BedrockAgentCoreContext.get_session_id())
        span.set_attribute("agentcore.request_id", 
                          BedrockAgentCoreContext.get_request_id())
    
    # Your agent logic (automatically traced)
    return my_agent.run(request.get("prompt"))

app.run()
```

### Step 3: Deploy to AgentCore

Follow AWS Bedrock AgentCore deployment guide. Traces will appear in HoneyHive
with AgentCore session/request context.

## What Gets Traced

✅ **Traced Automatically:**
- LLM API calls (OpenAI, Anthropic, etc.)
- Agent framework execution (LangChain chains, tools, etc.)
- Tool invocations
- Embeddings and vector searches

✅ **Added via Context Enrichment:**
- AgentCore session ID (for multi-turn conversation tracking)
- AgentCore request ID (for request correlation)

❌ **Not Traced (Not Useful):**
- HTTP routing (AgentCore internal)
- Starlette middleware

## AWS Service Tracing (Optional)

To trace AgentCore Memory, Browser, and Code Interpreter calls:

```python
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

BotocoreInstrumentor().instrument(tracer_provider=tracer.provider)
```

This captures:
- Memory operations (create_event, retrieve_memories)
- Browser automation (navigate, click, screenshot)
- Code execution (execute_code)

## Framework-Specific Guides

- **LangChain on AgentCore:** See [guide](...)
- **CrewAI on AgentCore:** See [guide](...)
- **Strands on AgentCore:** See [guide](...)
- **Custom Agents on AgentCore:** See [guide](...)
```

### 6.4 Gaps and Limitations

**Gaps Identified:**

1. **No AgentCore-Specific Span Attributes Standard**
   - Recommend: Define standard attributes for AgentCore context
   - `agentcore.session_id`, `agentcore.request_id`, `agentcore.workload_identity`

2. **No Built-in Instrumentation Helpers**
   - SDK could provide: `@app.traced_entrypoint` decorator
   - Would automatically add context to spans

3. **Documentation Mismatch**
   - README claims "OpenTelemetry-compatible telemetry"
   - Reality: No telemetry in SDK code
   - User must implement their own instrumentation

4. **No Propagation from AgentCore Runtime to User Code**
   - AgentCore runtime (AWS-managed) doesn't propagate trace context
   - User's code starts new trace (no parent span from HTTP request)
   - Workaround: Use request_id as correlation identifier

**Limitations:**

1. **Cannot Instrument HTTP Layer**
   - AgentCore runtime (AWS-managed) is closed-source
   - Cannot add instrumentation to incoming HTTP requests
   - Only user's Python code is instrumentable

2. **No Control Over Service Integration Tracing**
   - Memory/Browser/Code Interpreter are AWS services
   - Can only trace Boto3 client-side calls
   - Cannot see service-side execution details

3. **Framework-Dependent Instrumentation**
   - Different users use different frameworks
   - No single "Bedrock AgentCore instrumentor" possible
   - Must document per-framework approach

---

## Appendix

### A. Files Analyzed

**Complete File List:**
```
src/bedrock_agentcore/__init__.py
src/bedrock_agentcore/runtime/app.py (534 lines - CRITICAL)
src/bedrock_agentcore/runtime/models.py
src/bedrock_agentcore/runtime/context.py (74 lines - IMPORTANT for context)
src/bedrock_agentcore/runtime/utils.py
src/bedrock_agentcore/memory/client.py (1854 lines)
src/bedrock_agentcore/memory/controlplane.py
src/bedrock_agentcore/memory/session.py
src/bedrock_agentcore/memory/constants.py
src/bedrock_agentcore/memory/integrations/strands/config.py
src/bedrock_agentcore/memory/integrations/strands/session_manager.py
src/bedrock_agentcore/memory/integrations/strands/bedrock_converter.py
src/bedrock_agentcore/tools/browser_client.py
src/bedrock_agentcore/tools/code_interpreter_client.py
src/bedrock_agentcore/identity/auth.py
src/bedrock_agentcore/services/identity.py
```

### B. Commands Used

```bash
# Clone
git clone https://github.com/aws/bedrock-agentcore-sdk-python.git /tmp/bedrock-agentcore-sdk-python

# Structure analysis
find src -name "*.py" | wc -l
find src -type d | sort
wc -l src/**/*.py

# Dependency analysis
cat pyproject.toml
grep -i "openai\|anthropic\|langchain" pyproject.toml

# LLM client search
grep -r "openai\|anthropic\|google\|bedrock\|azure" src/ --include="*.py"
grep -r "chat.completions\|messages.create" src/ --include="*.py"

# Observability search
grep -r "opentelemetry\|otel\|tracing\|tracer" src/ --include="*.py"
grep -r "span\|trace" src/ --include="*.py" | grep -v transport

# Strands integration search
grep -r "strands" src/ --include="*.py"

# Boto3 usage search
grep -r "boto3\|botocore" src/ --include="*.py"
```

### C. References

- **SDK GitHub:** https://github.com/aws/bedrock-agentcore-sdk-python
- **SDK PyPI:** https://pypi.org/project/bedrock-agentcore/
- **Starter Toolkit:** https://github.com/aws/bedrock-agentcore-starter-toolkit
- **AWS Documentation:** https://docs.aws.amazon.com/bedrock-agentcore/
- **HoneyHive BYOI:** https://docs.honeyhive.ai/byoi
- **SDK_ANALYSIS_METHODOLOGY:** integrations-analysis/SDK_ANALYSIS_METHODOLOGY.md v1.3

### D. Version Information

- **Analysis Date:** 2025-10-15
- **SDK Version:** v1.0.0 (GA release)
- **Python Support:** >=3.10
- **Core Dependencies:** boto3, starlette, uvicorn, pydantic
- **Optional Dependencies:** strands-agents

---

## Conclusion

AWS Bedrock AgentCore SDK is a **runtime platform**, not an agent framework. It does not make LLM calls or implement agent logic - it wraps user's agent code as HTTP endpoints.

**For HoneyHive Integration:**
1. ✅ Instrument user's agent framework (LangChain, OpenAI, etc.)
2. ✅ Add AgentCore context (session_id, request_id) as span attributes
3. ✅ Optional: Instrument Boto3 for AWS service tracing
4. ❌ Do NOT create a "Bedrock AgentCore instrumentor"

**Recommendation:** Document the correct instrumentation approach for each framework that users deploy on AgentCore, with emphasis on context enrichment for session/request correlation.

---

**Analysis completed:** 2025-10-15  
**Next steps:**
1. Create HoneyHive documentation guide for AgentCore
2. Test instrumentation patterns with LangChain/CrewAI on AgentCore
3. Create example repositories showing correct instrumentation
4. Add AgentCore context enrichment helpers to HoneyHive SDK

