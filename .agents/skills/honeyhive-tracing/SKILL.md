---
name: honeyhive-tracing
description: Add HoneyHive tracing to a Python application. Use when asked to instrument an app with HoneyHive, add observability, set up tracing, or integrate HoneyHive's SDK for monitoring AI/LLM calls. Covers tracer initialization, auto-instrumentation, custom spans, enrichment, and deployment patterns.
metadata:
  author: honeyhive
  version: "1.0"
---

# HoneyHive Tracing

Add HoneyHive's OpenTelemetry-based tracing to a Python application. This skill covers tracer initialization, auto-instrumentation of LLM providers, custom spans, trace enrichment, and production deployment patterns.

## Prerequisites

- A HoneyHive project (create at https://app.honeyhive.ai/projects)
- A HoneyHive API key (org settings > Copy API Key)
- Python 3.9+

Environment variables expected:
- `HH_API_KEY` - HoneyHive API key
- `HH_PROJECT` - HoneyHive project name
- `HH_API_URL` - (optional) Custom API URL for self-hosted/dedicated deployments

---

## Concepts

### Data Model

HoneyHive uses a **wide-event** data model. Every event carries its full context in a single record: inputs, outputs, timing, metrics, metadata, feedback, and errors.

Events form a hierarchical tree:

```
session (root)              # event_type: session
+-- validate_input          # event_type: tool
+-- retrieve_context        # event_type: tool
+-- llm_completion          # event_type: model
+-- format_response         # event_type: chain
```

**Session**: The root event. Groups all child events. Can be single-turn (one request) or multi-turn (entire conversation). Equivalent to a "trace" in APM tools.

**Event**: A discrete operation. Each has an `event_type`:

| `event_type` | What it represents | Examples |
|--------------|-------------------|----------|
| `model` | An LLM API request | GPT-4 completion, Claude message |
| `tool` | An external service or function call | Vector DB search, API call, database query |
| `chain` | A logical grouping of child events | RAG pipeline, agent workflow |

**Event Schema** (all types share this):

| Field | Description |
|-------|-------------|
| `event_id` | Unique identifier (UUID) |
| `session_id` | Groups all events in the same trace |
| `parent_id` | Links child to parent (`null` for root session) |
| `event_type` | `"session"`, `"model"`, `"tool"`, or `"chain"` |
| `event_name` | Human-readable operation name |
| `inputs` / `outputs` | Input/output data |
| `config` | Configuration (model params, prompt template, etc.) |
| `metadata` | Custom key-value pairs |
| `metrics` | Numeric measurements (latency, tokens, cost, eval scores) |
| `feedback` | User ratings, corrections |
| `error` | Error details if failed |

### Architecture

HoneyHive is built on OpenTelemetry. The SDK wraps an OTel `TracerProvider` and exports spans via OTLP. Any OTel-compatible instrumentor works. The SDK itself has zero dependencies on AI libraries --- instrumentors are installed separately (BYOI: Bring Your Own Instrumentor).

---

## Step 1: Install Dependencies

Install the HoneyHive SDK plus the instrumentor for your LLM provider:

```bash
# Core SDK
pip install honeyhive

# Provider instrumentors (install only what you use)
pip install openinference-instrumentation-openai       # OpenAI
pip install openinference-instrumentation-anthropic     # Anthropic
pip install openinference-instrumentation-bedrock       # AWS Bedrock
pip install openinference-instrumentation-litellm       # LiteLLM
pip install openinference-instrumentation-langchain     # LangChain
pip install openinference-instrumentation-llama-index   # LlamaIndex
pip install openinference-instrumentation-crewai        # CrewAI
pip install openinference-instrumentation-google-adk    # Google ADK
```

For agent frameworks with native OTel support (e.g., AWS Strands, PydanticAI), check framework-specific docs --- they may not need an OpenInference instrumentor.

---

## Step 2: Initialize the Tracer

Choose the pattern that matches your use case:

### Scripts / Notebooks (simplest)

Initialize once at module level. All traced operations share the same session.

```python
import os
from honeyhive import HoneyHiveTracer, trace

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    session_name="my-session",       # Optional: human-readable label
    source="development",            # Optional: label where traces come from
    # server_url=os.getenv("HH_API_URL"),  # Required for self-hosted/dedicated
)
```

### Web Servers (FastAPI / Flask / Django)

Initialize **one** tracer at startup, create a **new session per request** using `create_session()` (sync) or `acreate_session()` (async).

```python
import os
from fastapi import FastAPI, Request
from honeyhive import HoneyHiveTracer, trace

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    source="production",
)

app = FastAPI()

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = await tracer.acreate_session(
        session_name=f"api-{request.url.path}",
        inputs={"method": request.method, "path": str(request.url)},
    )
    response = await call_next(request)
    tracer.enrich_session(outputs={"status_code": response.status_code})
    if session_id:
        response.headers["X-Session-ID"] = session_id
    return response
```

**Important**: Use `create_session()` / `acreate_session()`, NOT `session_start()` for web servers. The former stores session ID in request-scoped baggage (safe for concurrent requests); the latter stores it on the tracer instance (race condition).

### Serverless (AWS Lambda)

Lazy init + per-request sessions. Set `disable_batch=True` to flush spans before the function terminates.

```python
import os
from typing import Optional
from honeyhive import HoneyHiveTracer, trace

_tracer: Optional[HoneyHiveTracer] = None

def get_tracer() -> HoneyHiveTracer:
    global _tracer
    if _tracer is None:
        _tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            disable_batch=True,
        )
    return _tracer

def lambda_handler(event, context):
    tracer = get_tracer()
    session_id = tracer.create_session(
        session_name=f"lambda-{context.aws_request_id}",
        inputs={"event": event},
    )
    result = process_event(event)
    tracer.enrich_session(outputs={"result": result})
    return result
```

### Evaluation / Experiments

When running experiments with `evaluate()`, **do NOT** create your own tracer. The SDK creates a new tracer per datapoint automatically. See the `honeyhive-evaluators` skill for details.

---

## Step 3: Add Auto-Instrumentation

After initializing the tracer, register instrumentors for your LLM providers. This captures all LLM calls automatically.

```python
from openinference.instrumentation.openai import OpenAIInstrumentor

# Register the instrumentor with the tracer's provider
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Now all OpenAI calls are automatically traced
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

Multiple instrumentors can be registered simultaneously:

```python
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
AnthropicInstrumentor().instrument(tracer_provider=tracer.provider)
```

---

## Step 4: Add Custom Spans with `@trace`

Auto-instrumentation captures LLM and vector DB calls. For any other function (preprocessing, postprocessing, business logic), use the `@trace` decorator:

```python
from honeyhive import trace, enrich_span

@trace
def process_request(user_id: str, data: dict) -> dict:
    """Automatically traced with inputs/outputs captured."""
    enrich_span(metadata={"user_id": user_id})
    result = do_processing(data)
    return {"status": "success", "data": result}

@trace
def nested_workflow(request: dict) -> dict:
    """Nested calls create trace hierarchy automatically."""
    validated = validate(request)      # Child span
    processed = process(validated)     # Child span
    return save(processed)             # Child span
```

### Decorator Options

```python
# Specify event type and name
@trace(event_type="tool", event_name="database_lookup")
def lookup(query: str):
    ...

# Bind to a specific tracer instance (recommended for production)
@trace(event_type="chain", tracer=tracer)
def my_pipeline(input_data):
    ...
```

### Async Functions

`@trace` works with both sync and async functions automatically --- no separate decorator needed:

```python
@trace
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Context Managers (for loops, conditionals)

Use `enrich_span_context()` when decorators don't fit:

```python
from honeyhive.tracer.processing.context import enrich_span_context

@trace
def process_batch(items: list) -> list:
    results = []
    for i, item in enumerate(items):
        with enrich_span_context(
            event_name=f"process_item_{i}",
            inputs={"item": item},
        ):
            result = transform_item(item)
            results.append(result)
    return results
```

---

## Step 5: Enrich Traces

Enrichments add context beyond what auto-instrumentation captures. Three levels:

### Session-Level (applies to all events)

```python
tracer.enrich_session(
    metadata={"tenant_id": "acme_corp", "app_version": "2.1.0"},
    user_properties={"user_id": "user_123", "plan": "premium"},
    config={"model": "gpt-4o", "prompt_version": "v2.3"},
)
```

### Span-Level (inside a `@trace` function)

```python
from honeyhive import enrich_span

@trace
def generate_response(query: str):
    response = call_llm(query)
    enrich_span(
        metadata={"query_length": len(query)},
        metrics={"relevance_score": 0.95, "contains_pii": False},
        feedback={"rating": True},
    )
    return response
```

### Auto-Instrumented Span Enrichment (without `@trace`)

Use `using_attributes` from OpenInference to enrich auto-instrumented LLM spans:

```python
from openinference.instrumentation import using_attributes

with using_attributes(
    user_id="user_12345",
    metadata={"feature": "chat_support"},
):
    response = client.chat.completions.create(...)
```

### Enrichment Namespaces

| Namespace | Type | Description |
|-----------|------|-------------|
| `config` | Object | Model params, prompt templates, hyperparameters |
| `feedback` | Object | User ratings, corrections, ground truth |
| `metrics` | Object | Scores, evaluations, numeric measurements |
| `metadata` | Object | Arbitrary key-value pairs (catch-all) |
| `inputs` | Object | Input data |
| `outputs` | Object | Output data |
| `user_properties` | Object | User ID, tier, email, etc. |
| `error` | String | Error information (span-level only) |

### Invocation Patterns

All of these are equivalent:

```python
# Simple dict
enrich_span({"user_id": "user_123", "feature": "chat"})

# Keyword arguments (go to metadata)
enrich_span(user_id="user_123", feature="chat")

# Explicit namespaces
enrich_span(
    metadata={"user_id": "user_123"},
    metrics={"score": 0.95},
)

# Mixed
enrich_span(
    metadata={"user_id": "user_123"},
    metrics={"score": 0.95},
    feature="chat",  # extra kwargs go to metadata
)
```

---

## Step 6: Distributed Tracing (Multi-Service)

### Simple: Session ID Passing

Pass `session_id` between services so events land in the same session:

```python
# Service A: get session_id
session_id = tracer.session_id

# Service B: init tracer with same session_id
tracer_b = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    session_id=session_id,
)
```

### Full: W3C Context Propagation

For true parent-child relationships across services:

```python
# Client side: inject context into outgoing headers
from honeyhive.tracer.processing.context import inject_context_into_carrier, enrich_span_context

with enrich_span_context(event_name="call_remote"):
    headers = {"Content-Type": "application/json"}
    inject_context_into_carrier(headers, tracer)
    response = requests.post(url, json=payload, headers=headers)

# Server side: extract context from incoming headers
from honeyhive.tracer.processing.context import with_distributed_trace_context

@app.route("/agent/invoke", methods=["POST"])
async def invoke_agent():
    with with_distributed_trace_context(dict(request.headers), tracer):
        result = await run_agent(...)
```

---

## Step 7: Multi-Turn Conversations

For multi-turn conversations in web servers, the first request creates a session and returns the ID. Subsequent requests link to that session:

```python
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    existing_session = request.headers.get("X-Session-ID")
    if existing_session:
        await tracer.acreate_session(
            session_id=existing_session,
            skip_api_call=True,  # Session already exists, just set context
        )
    else:
        session_id = await tracer.acreate_session(
            session_name=f"conversation-{request.url.path}"
        )
        request.state.new_session_id = session_id

    response = await call_next(request)
    if hasattr(request.state, "new_session_id"):
        response.headers["X-Session-ID"] = request.state.new_session_id
    return response
```

---

## Complete Example

```python
import os
from honeyhive import HoneyHiveTracer, trace, enrich_span
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

# 1. Initialize tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    session_name="rag-pipeline",
    source="development",
)

# 2. Register instrumentor
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# 3. Session-level enrichment
tracer.enrich_session(
    user_properties={"user_id": "user_123", "plan": "premium"},
    metadata={"app_version": "2.1.0"},
)

client = OpenAI()

# 4. Custom spans with enrichment
@trace(event_type="tool")
def retrieve_docs(query: str) -> list:
    docs = search_vector_db(query)
    enrich_span(metrics={"num_docs": len(docs)})
    return docs

@trace(event_type="chain")
def rag_pipeline(query: str) -> str:
    docs = retrieve_docs(query)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer using context: {docs}"},
            {"role": "user", "content": query},
        ],
    )
    answer = response.choices[0].message.content
    enrich_span(metrics={"answer_length": len(answer)})
    return answer

result = rag_pipeline("How do I build an integration?")
print(result)
```

---

## Best Practices

1. **Pass an explicit tracer to `@trace`** in production: `@trace(event_type="tool", tracer=tracer)`
2. **Create sessions per logical unit of work** even with a global tracer
3. **Use `test_mode=True`** for local development without sending data: `HoneyHiveTracer.init(..., test_mode=True)`
4. **Use descriptive span names**: `@trace(event_name="payment_processing_stripe")` not `@trace(event_name="process")`
5. **Avoid over-instrumentation**: Don't create a span per item in a hot loop --- trace the batch
6. **Use consistent key names** across your app for enrichment
7. **Don't include sensitive data** (passwords, API keys, PII) in enrichments
8. **Keep enrichment values under 1KB** per field
9. **Use namespaces explicitly**: `metadata=`, `metrics=`, `user_properties=` for clarity

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Traces not appearing | Check `HH_API_KEY` and `HH_PROJECT` are set correctly |
| Events in wrong session | Remove global `HoneyHiveTracer.init()` if using `evaluate()` |
| Race conditions in web server | Use `create_session()` not `session_start()` |
| Lambda spans missing | Set `disable_batch=True` on tracer init |
| Instrumentor not capturing | Ensure `tracer_provider=tracer.provider` is passed to `.instrument()` |
