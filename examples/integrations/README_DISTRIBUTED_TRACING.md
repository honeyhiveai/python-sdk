# Distributed Tracing with Google ADK Agent Server

This example demonstrates distributed tracing with Google ADK.

We have a script that uses two agents one running remotely on another server and one running in the same script.

We show how you can setup tracing such that the agent traces are linked together properly.

## Architecture

```
Client Script (google_adk_conditional_agents_example.py)
  ├── Agent 1 → HTTP with trace context → Agent Server (google_adk_agent_server.py)
  └── Agent 2 → Local execution
```

## Setup

1. **Install dependencies:**
```bash
pip install honeyhive google-adk openinference-instrumentation-google-adk flask requests
```

2. **Set environment variables:**
```bash
export HH_API_KEY="your-honeyhive-api-key"
export HH_PROJECT="your-project-name"
export GOOGLE_API_KEY="your-google-api-key"
```

## Running the Example

### Terminal 1 - Start the Agent Server:
```bash
cd examples/integrations
source ../../.env  # If you have a .env file
python google_adk_agent_server.py
```

The server will start on port 5003 and wait for requests.

### Terminal 2 - Run the Client Script:
```bash
cd examples/integrations
source ../../.env
export AGENT_SERVER_URL="http://localhost:5003"  # Default, can be omitted
python google_adk_conditional_agents_example.py
```

The client will execute two user calls, each invoking both agents (remote + local).

## How It Works

### **Client Script** (`google_adk_conditional_agents_example.py`):

**Key Patterns:**
- **Global tracer initialization:** `tracer = HoneyHiveTracer.init(...)` at module level
- **`@trace` decorators:** Automatic span creation for `user_call()` and `call_principal()`
- **`enrich_span_context()`:** Explicit child spans for `call_agent_1` and `call_agent_2`
- **`inject_context_into_carrier()`:** Adds trace context to HTTP headers for remote calls

**Agent 1 (Remote):**
```python
with enrich_span_context(event_name="call_agent_1", inputs={"query": query}):
    headers = {}
    inject_context_into_carrier(headers, tracer)
    response = requests.post(f"{agent_server_url}/agent/invoke", headers=headers, ...)
```

**Agent 2 (Local):**
```python
with enrich_span_context(event_name="call_agent_2", inputs={"research": query}):
    agent = LlmAgent(...)
    runner = Runner(agent=agent, ...)
    # Google ADK instrumentation automatically creates child spans
```

### **Agent Server** (`google_adk_agent_server.py`):

**Key Pattern: `with_distributed_trace_context()` helper**

This single context manager handles the session linking seamlessly.

```python
@app.route("/agent/invoke", methods=["POST"])
async def invoke_agent():
    with with_distributed_trace_context(dict(request.headers), tracer):
        # All spans created here (manual or Google ADK) are part of the distributed trace
        result = await run_agent(user_id, query, agent_name)
        return jsonify({"response": result})
```

## Trace Structure

The example demonstrates **mixed invocation** in a single unified trace:

```
user_call (client)
  └── call_principal (client)
      ├── call_agent_1 (client) → HTTP → Agent Server
      │   └── run_agent (server)
      │       └── Google ADK spans (remote: invocation, agent_run, call_llm)
      └── call_agent_2 (client)
          └── Google ADK spans (local: invocation, agent_run, call_llm)
```

**Key Points:**
- **Agent 1 spans cross process boundaries** - client span → HTTP → server spans
- **Agent 2 spans are in-process** - all in client process
- **Same trace ID throughout** - unified observability
- **Both patterns coexist** - demonstrates flexibility

## Verification

After running both scripts, check HoneyHive dashboard for:
- ✅ Single unified trace with both client and server spans
- ✅ `call_agent_1` span has children from the remote server
- ✅ `call_agent_2` span has children in the same process
- ✅ All Google ADK spans have correct `session_id`, `project`, `source` from client
