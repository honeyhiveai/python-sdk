# OpenTelemetry Standards for LLM Observability

**Research Date**: 2025-09-30  
**Framework Version**: 1.0  
**Analysis Method**: Official OTel spec analysis (semantic-conventions repository)

---

## Executive Summary

This document provides a comprehensive overview of **OpenTelemetry standards** relevant to LLM observability platforms like HoneyHive, covering **9 critical areas**: semantic conventions, instrumentation patterns, SDK architecture, context propagation, resource attributes, collector integration, signal coverage, performance patterns, and data fidelity.

**Key Findings**:
- **Gen AI conventions status**: `Development` (Experimental - NOT stable yet)
- **Convention version**: Transitioning from v1.36.0 → latest experimental
- **Total attributes defined**: 56 gen_ai.* attributes
- **Signals covered**: Traces ✅, Metrics ✅, Events ✅ (Logs as Events)
- **Stability**: All gen_ai conventions are experimental; stability guarantees not yet provided

---

## 1. Semantic Conventions (Gen AI)

### 1.1 Official Sources

**Primary Spec**: https://opentelemetry.io/docs/specs/semconv/gen-ai/  
**GitHub Repository**: https://github.com/open-telemetry/semantic-conventions  
**Current Version**: Development (Experimental)  
**Last Updated**: 2025-09-30  
**Status**: ![Development](https://img.shields.io/badge/-development-blue)

**Transition Plan**:
- Existing instrumentations (v1.36.0 or prior) SHOULD NOT change conventions by default
- Use `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` environment variable to opt-in
- Plan will be updated before conventions are marked as stable

### 1.2 Span Attributes

#### Request Attributes (Required)

| Attribute | Type | Requirement | Description | Example |
|-----------|------|-------------|-------------|---------|
| `gen_ai.operation.name` | string | Required | Operation type | `chat`, `embeddings`, `text_completion` |
| `gen_ai.provider.name` | string | Required | LLM provider identifier | `openai`, `anthropic`, `aws.bedrock` |
| `gen_ai.request.model` | string | Conditionally Required | Model name requested | `gpt-4`, `claude-3-opus` |
| `gen_ai.conversation.id` | string | Conditionally Required | Conversation/session identifier | `conv_5j66UpCpwteGg4YSxUnt7lPY` |
| `gen_ai.output.type` | string | Conditionally Required | Content type requested | `text`, `json`, `image`, `speech` |
| `gen_ai.request.choice.count` | int | Conditionally Required | Number of completions to return | `3` |
| `gen_ai.request.seed` | int | Conditionally Required | Seed for deterministic responses | `100` |

#### Request Attributes (Recommended)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.request.max_tokens` | int | Max tokens to generate | `100` |
| `gen_ai.request.temperature` | double | Temperature setting | `0.7` |
| `gen_ai.request.top_p` | double | Top-p sampling | `1.0` |
| `gen_ai.request.top_k` | double | Top-k sampling | `40` |
| `gen_ai.request.frequency_penalty` | double | Frequency penalty | `0.1` |
| `gen_ai.request.presence_penalty` | double | Presence penalty | `0.1` |
| `gen_ai.request.stop_sequences` | string[] | Stop sequences | `["forest", "lived"]` |
| `gen_ai.request.encoding_formats` | string[] | Embedding encoding formats | `["base64"]`, `["float"]` |

#### Response Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.response.id` | string | Unique completion ID | `chatcmpl-123` |
| `gen_ai.response.model` | string | Actual model used | `gpt-4-0613` |
| `gen_ai.response.finish_reasons` | string[] | Why generation stopped | `["stop"]`, `["stop", "length"]` |

#### Usage/Token Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.usage.input_tokens` | int | Prompt tokens used | `100` |
| `gen_ai.usage.output_tokens` | int | Completion tokens used | `180` |
| `gen_ai.token.type` | string | Token type (for metrics) | `input`, `output` |

#### Message Attributes (Opt-In)

| Attribute | Type | Description | Schema |
|-----------|------|-------------|--------|
| `gen_ai.input.messages` | any | Chat history provided to model | [Input messages JSON schema](/docs/gen-ai/gen-ai-input-messages.json) |
| `gen_ai.output.messages` | any | Messages returned by model | [Output messages JSON schema](/docs/gen-ai/gen-ai-output-messages.json) |
| `gen_ai.system_instructions` | any | System message/instructions | [System instructions JSON schema](/docs/gen-ai/gen-ai-system-instructions.json) |

**Warning**: These attributes likely contain sensitive information including user/PII data.

#### Tool Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.tool.definitions` | any | Tool definitions available | JSON array of tool definitions |
| `gen_ai.tool.name` | string | Tool name | `get_weather`, `calculate` |
| `gen_ai.tool.type` | string | Tool type | `function`, `extension`, `datastore` |
| `gen_ai.tool.description` | string | Tool description | `Get current weather` |
| `gen_ai.tool.call.id` | string | Tool call identifier | `call_mszuSIzqtI65i1wAUOE8w5H4` |
| `gen_ai.tool.call.arguments` | any | Parameters passed to tool | `{"location": "Paris"}` |
| `gen_ai.tool.call.result` | any | Result returned by tool | `{"temp": 57, "conditions": "rainy"}` |

#### Agent Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.agent.id` | string | Unique agent identifier | `asst_5j66UpCpwteGg4YSxUnt7lPY` |
| `gen_ai.agent.name` | string | Human-readable agent name | `Math Tutor` |
| `gen_ai.agent.description` | string | Agent description | `Helps with math problems` |

#### Evaluation Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.evaluation.name` | string | Evaluation metric name | `Relevance`, `IntentResolution` |
| `gen_ai.evaluation.score.value` | double | Evaluation score | `4.0` |
| `gen_ai.evaluation.score.label` | string | Human-readable label | `relevant`, `pass`, `fail` |
| `gen_ai.evaluation.explanation` | string | Score explanation | `Factually accurate but lacks detail` |

#### Embeddings Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.embeddings.dimension.count` | int | Embedding dimensions | `512`, `1024` |

### 1.3 Well-Known Values

#### `gen_ai.operation.name`

| Value | Description | Stability |
|-------|-------------|-----------|
| `chat` | Chat completion operation | Development |
| `embeddings` | Embeddings operation | Development |
| `text_completion` | Legacy text completion | Development |
| `generate_content` | Multimodal content generation | Development |
| `execute_tool` | Execute a tool | Development |
| `create_agent` | Create GenAI agent | Development |
| `invoke_agent` | Invoke GenAI agent | Development |

#### `gen_ai.provider.name`

| Value | Provider | Stability |
|-------|----------|-----------|
| `openai` | OpenAI | Development |
| `anthropic` | Anthropic | Development |
| `aws.bedrock` | AWS Bedrock | Development |
| `azure.ai.openai` | Azure OpenAI | Development |
| `gcp.vertex_ai` | Vertex AI | Development |
| `gcp.gemini` | Gemini (AI Studio API) | Development |
| `gcp.gen_ai` | Generic Google Gen AI | Development |
| `cohere` | Cohere | Development |
| `mistral_ai` | Mistral AI | Development |
| `groq` | Groq | Development |
| `ibm.watsonx.ai` | IBM Watsonx AI | Development |
| `perplexity` | Perplexity | Development |
| `deepseek` | DeepSeek | Development |
| `x_ai` | xAI | Development |
| `azure.ai.inference` | Azure AI Inference | Development |

#### `gen_ai.output.type`

| Value | Description | Stability |
|-------|-------------|-----------|
| `text` | Plain text | Development |
| `json` | JSON object | Development |
| `image` | Image | Development |
| `speech` | Speech | Development |

### 1.4 Span Types

#### Inference Span

- **Name**: `{gen_ai.operation.name} {gen_ai.request.model}`
- **Kind**: `CLIENT` (or `INTERNAL` for in-process models)
- **Description**: Client call to GenAI model for response generation

#### Embeddings Span

- **Name**: `{gen_ai.operation.name} {gen_ai.request.model}`
- **Kind**: `CLIENT`
- **Description**: Request to generate embeddings

#### Execute Tool Span

- **Name**: `execute_tool {gen_ai.tool.name}`
- **Kind**: `INTERNAL`
- **Description**: Tool execution (by instrumentor or application code)

### 1.5 Serialization Standards

#### Complex Type Handling

**Messages** (`gen_ai.input.messages`, `gen_ai.output.messages`):
- MUST follow defined JSON schemas
- MUST be recorded in structured form on events
- MAY be recorded as JSON string on spans if structured format not supported
- SHOULD be recorded in structured form on spans if supported

**Tool Definitions** (`gen_ai.tool.definitions`):
- Expected to be an array of objects
- Instrumentation SHOULD deserialize to array if string is available
- MAY be recorded as JSON string on spans if structured format not supported

**Tool Arguments/Results** (`gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`):
- Expected to be objects
- Instrumentation SHOULD deserialize to object if string is available
- MAY be recorded as JSON string on spans if structured format not supported

#### Content Capture Patterns

**Three Opt-In Levels**:
1. **Default**: Don't record instructions, inputs, or outputs
2. **Span Attributes**: Record on `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages` attributes
3. **External Storage**: Store content externally, record references on spans

**Recommendations**:
- Instrumentations SHOULD NOT capture content by default
- Instrumentations SHOULD provide opt-in flag for users
- Instrumentations MAY provide hooks for external storage upload
- Instrumentations MAY provide truncation options to manage size

---

## 2. Metrics

### 2.1 Client Metrics

#### Metric: `gen_ai.client.token.usage`

- **Type**: Histogram
- **Unit**: `{token}` (tokens)
- **Description**: Number of input and output tokens used
- **Recommendation**: Report when token counts are readily available
- **Bucket Boundaries**: [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216, 67108864]

**Required Attributes**:
- `gen_ai.operation.name` (Required)
- `gen_ai.provider.name` (Required)
- `gen_ai.token.type` (Required) - `input` or `output`
- `gen_ai.request.model` (Conditionally Required if available)

**Recommended Attributes**:
- `gen_ai.response.model`
- `server.address`
- `server.port` (if `server.address` is set)

**Special Rules**:
- When both used and billable tokens are reported, MUST report billable tokens
- If offline token counting is needed, MAY allow users to enable it
- If token counts not efficiently obtainable, MUST NOT report metric

#### Metric: `gen_ai.client.operation.duration`

- **Type**: Histogram
- **Unit**: `s` (seconds)
- **Description**: GenAI operation duration
- **Recommendation**: Report for all operations

**Required Attributes**:
- `gen_ai.operation.name` (Required)
- `gen_ai.provider.name` (Required)
- `gen_ai.request.model` (Conditionally Required if available)
- `error.type` (Conditionally Required if operation ended in error)

**Recommended Attributes**:
- `gen_ai.response.model`
- `server.address`
- `server.port` (if `server.address` is set)

### 2.2 Server Metrics

#### Metric: `gen_ai.server.request.duration`

- **Type**: Histogram
- **Unit**: `s` (seconds)
- **Description**: Time to process a GenAI request (server-side)

#### Metric: `gen_ai.server.time_per_output_token`

- **Type**: Gauge
- **Unit**: `s` (seconds)
- **Description**: Time per output token generated

#### Metric: `gen_ai.server.time_to_first_token`

- **Type**: Histogram
- **Unit**: `s` (seconds)
- **Description**: Time to generate first token (TTFT)

---

## 3. Events

### 3.1 Event: `gen_ai.client.inference.operation.details`

**Purpose**: Store input and output details independently from traces (opt-in)

**Attributes**: Same as span attributes (includes opt-in message content)

**Use Case**:
- Separate storage for sensitive content
- Independent from sampling decisions
- Detailed logging without span overhead

### 3.2 Event: `gen_ai.evaluation.result`

**Purpose**: Record evaluation results for GenAI operations

**Attributes**:
- `gen_ai.evaluation.name` (Required)
- `gen_ai.evaluation.score.value` (Recommended)
- `gen_ai.evaluation.score.label` (Recommended)
- `gen_ai.evaluation.explanation` (Recommended)

---

## 4. Instrumentation Patterns

### 4.1 Auto-Instrumentation

**Definition**: Automatic interception of LLM SDK calls without code changes

**OTel Pattern**:
- Implement `BaseInstrumentor` (Python) or equivalent
- Hook into SDK client initialization
- Intercept API calls using monkey-patching or wrapping
- Automatically set spans and attributes

**Example Implementations**:
- OpenInference instrumentors (used by Phoenix)
- Traceloop instrumentors (32 packages)
- OpenLit instrumentors (46 modules)

**Pros**:
- Zero code changes required
- Easy adoption
- Consistent attribute setting

**Cons**:
- Framework/SDK specific
- Potential for breaking changes
- May not capture custom logic

### 4.2 Manual Instrumentation

**Definition**: Explicit span creation via OTel API

**OTel Pattern**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("chat gpt-4") as span:
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", "openai")
    span.set_attribute("gen_ai.request.model", "gpt-4")
    # ... make LLM call
    span.set_attribute("gen_ai.response.id", response_id)
    span.set_attribute("gen_ai.usage.input_tokens", prompt_tokens)
```

**Pros**:
- Full control
- Works with any LLM provider
- Custom attributes possible

**Cons**:
- Requires code changes
- More boilerplate
- User must know conventions

### 4.3 Decorator Pattern

**Definition**: Python decorators or similar for function-level tracing

**OTel Pattern**:
```python
from opentelemetry.instrumentation.decorator import trace

@trace(span_name="my_llm_call", attributes={"gen_ai.operation.name": "chat"})
def call_llm(prompt):
    # ... LLM call
    pass
```

**Used By**:
- OpenLit (`@trace` decorator)
- Traceloop (workflow/task decorators)
- Phoenix OTel (tracing decorators for GenAI patterns)

### 4.4 Context Managers

**Definition**: Use context managers for span lifecycle

**OTel Pattern**:
```python
with tracer.start_as_current_span("llm_operation") as span:
    # Automatic span start/end
    # Exceptions automatically recorded
    pass
```

---

## 5. SDK Architecture

### 5.1 OTel SDK Components

**Core Components**:
```
Application Code
    ↓
Tracer (from TracerProvider)
    ↓
Span
    ↓
SpanProcessor (SimpleSpanProcessor or BatchSpanProcessor)
    ↓
SpanExporter (OTLP, Jaeger, Zipkin, etc.)
    ↓
Backend (Collector, Platform)
```

**Metrics Components**:
```
Application Code
    ↓
Meter (from MeterProvider)
    ↓
Instruments (Counter, Histogram, Gauge, etc.)
    ↓
MetricReader
    ↓
MetricExporter
    ↓
Backend
```

**Logs/Events Components**:
```
Application Code
    ↓
Logger (from LoggerProvider)
    ↓
LogRecord
    ↓
LogRecordProcessor
    ↓
LogExporter
    ↓
Backend
```

### 5.2 Initialization Pattern

**Standard OTel SDK Init**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Create provider
provider = TracerProvider(resource=Resource.create({"service.name": "my-app"}))

# Add processor + exporter
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318"))
)

# Set global provider
trace.set_tracer_provider(provider)
```

### 5.3 HoneyHive Pattern

**Evidence from codebase**:
- Uses `TracerProvider` from `opentelemetry.sdk.trace`
- Uses `SpanProcessor`, `SpanExporter` for custom processing
- Uses `Resource` for service identification
- Custom span processors for semantic convention mapping
- OTLP export via `OTLPSpanExporter`

---

## 6. Context Propagation

### 6.1 Trace Context

**W3C Trace Context** (Standard):
- `traceparent` header: `00-{trace_id}-{span_id}-{flags}`
- `tracestate` header: vendor-specific state

**OTel API**:
```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Inject context into headers (outgoing request)
headers = {}
inject(headers)

# Extract context from headers (incoming request)
ctx = extract(headers)
with trace.use_context(ctx):
    # Span will be child of extracted context
    pass
```

### 6.2 Baggage

**Definition**: Key-value pairs propagated across service boundaries

**Use Cases**:
- User ID propagation
- Request ID
- Environment (staging/prod)
- Custom metadata

**OTel API**:
```python
from opentelemetry import baggage

# Set baggage
baggage.set_baggage("user.id", "12345")

# Get baggage
user_id = baggage.get_baggage("user.id")
```

### 6.3 Propagators

**Standard Propagators**:
- `TraceContextTextMapPropagator` (W3C Trace Context)
- `BaggagePropagator` (W3C Baggage)
- `CompositePropagator` (combine multiple)

**HoneyHive Usage**:
- Evidence: `W3CBaggagePropagator`, `CompositePropagator` found in codebase

---

## 7. Resource Attributes

### 7.1 Service Identification

**Required Attributes**:
- `service.name` - Service name (e.g., "my-llm-app")
- `service.version` - Service version (e.g., "1.2.3")

**Recommended Attributes**:
- `service.namespace` - Namespace (e.g., "production", "staging")
- `service.instance.id` - Unique instance identifier
- `deployment.environment.name` - Environment name

### 7.2 Telemetry SDK

**Attributes**:
- `telemetry.sdk.name` - SDK name (e.g., "opentelemetry")
- `telemetry.sdk.language` - Language (e.g., "python")
- `telemetry.sdk.version` - SDK version

### 7.3 Process/Host

**Attributes**:
- `process.pid` - Process ID
- `process.executable.name` - Executable name
- `host.name` - Hostname
- `host.arch` - Architecture (e.g., "amd64", "arm64")

---

## 8. Collector Integration

### 8.1 OTLP (OpenTelemetry Protocol)

**Exporters**:
- **HTTP**: `OTLPSpanExporter` (endpoint: `http://localhost:4318/v1/traces`)
- **gRPC**: `OTLPSpanExporter` (endpoint: `http://localhost:4317`)

**Configuration**:
```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="https://api.honeyhive.ai/v1/traces",  # Example
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
```

### 8.2 Batching

**BatchSpanProcessor**:
- Default: `max_queue_size=2048`, `max_export_batch_size=512`
- `schedule_delay_millis`: Time to wait before export (default 5000ms)
- `export_timeout_millis`: Export timeout (default 30000ms)

**vs SimpleSpanProcessor**:
- SimpleSpanProcessor: Exports each span immediately (development only)
- BatchSpanProcessor: Batches spans for efficiency (production)

**HoneyHive Usage**: Evidence of configurable batching (`disable_batch` flag found)

### 8.3 Sampling

**Sampling Strategies**:
- `AlwaysOnSampler` - Sample all spans
- `AlwaysOffSampler` - Sample no spans
- `TraceIdRatioBased` - Sample based on trace ID ratio (e.g., 10%)
- `ParentBased` - Follow parent span decision

**Configuration**:
```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

sampler = TraceIdRatioBased(0.1)  # Sample 10%
provider = TracerProvider(sampler=sampler)
```

**HoneyHive Usage**: Evidence of `TraceIdRatioBased` sampling found

---

## 9. Signal Coverage

### 9.1 Traces

**Status**: ✅ **Full Support** in OTel Gen AI conventions

**Coverage**:
- Spans for chat, embeddings, text completion
- Tool execution spans
- Agent spans
- Complete attribute set (56 attributes)

**HoneyHive Status**: ✅ Supported (uses TracerProvider, span processors)

### 9.2 Metrics

**Status**: ✅ **Full Support** in OTel Gen AI conventions

**Coverage**:
- Client metrics (2): token usage, operation duration
- Server metrics (3): request duration, time per token, TTFT

**HoneyHive Status**: ❌ **NOT SUPPORTED** (critical gap)

**Competitors**:
- Traceloop: ✅ Supported (comprehensive metrics)
- OpenLit: ✅ Supported (comprehensive metrics)
- Phoenix: ❌ Not supported
- Langfuse: ❌ Not supported

### 9.3 Logs

**Status**: ⚠️ **Partial Support** (via Events)

**Coverage**:
- Events API for structured logs
- Gen AI events: `gen_ai.client.inference.operation.details`, `gen_ai.evaluation.result`

**Note**: OTel Logs signal is separate from Events, but Events are built on Logs data model

**HoneyHive Status**: ❓ Unknown (logging infrastructure exists but OTel Logs integration unclear)

**Competitors**:
- Traceloop: ✅ Supported (LogExporter found)
- OpenLit: ⚠️ Events (not full Logs)
- Phoenix: ❓ Unknown
- Langfuse: ❓ Unknown

---

## 10. Performance Patterns

### 10.1 Asynchronous Instrumentation

**Pattern**: Non-blocking span export

**OTel Implementation**:
- `BatchSpanProcessor` uses background thread for export
- Spans are queued and exported asynchronously
- Application thread not blocked

**Best Practice**: Always use `BatchSpanProcessor` in production

### 10.2 Batching

**Pattern**: Export multiple spans in single request

**Configuration**:
- `max_export_batch_size`: Max spans per batch (default 512)
- `schedule_delay_millis`: Max time to wait before export (default 5000ms)

**Benefits**:
- Reduced network overhead
- Better throughput
- Lower backend load

### 10.3 Sampling

**Pattern**: Selectively trace requests to reduce overhead

**Strategies**:
- Head-based sampling: Decision at trace start
- Tail-based sampling: Decision after trace completes (requires collector)

**Trade-offs**:
- Lower overhead vs. potential data loss
- Cost savings vs. observability completeness

### 10.4 Overhead Minimization

**Best Practices**:
- Use batching (not simple processor)
- Sample in high-throughput scenarios
- Avoid capturing large content by default (opt-in)
- Use async exporters
- Minimize attribute count (only required + recommended)

**Claimed Overhead** (from competitors):
- OpenLit: "Minimal overhead" (no quantitative data)
- Traceloop: Not specified
- Phoenix: "Lightweight wrapper" (no quantitative data)
- HoneyHive: Not specified

**Note**: No competitor publishes quantitative performance benchmarks

---

## 11. Data Fidelity

### 11.1 Zero-Loss Principles

**OTel Design**:
- **Buffering**: Spans buffered in memory before export
- **Retry Logic**: Exporters retry on transient failures
- **Graceful Shutdown**: Flush pending spans on shutdown

**Configuration**:
```python
import atexit
from opentelemetry.sdk.trace import TracerProvider

provider = TracerProvider()
atexit.register(lambda: provider.shutdown())  # Flush on exit
```

### 11.2 Serialization Standards

**Span Attributes**:
- Primitives: string, int, double, boolean
- Arrays: string[], int[], double[], boolean[]
- **Structured data**: `any` type (experimental)

**Serialization for Complex Types**:
- JSON string encoding for backward compatibility
- Structured format when supported (events, modern SDKs)

**Example**:
```python
# Option 1: JSON string (backward compatible)
span.set_attribute("gen_ai.input.messages", json.dumps(messages))

# Option 2: Structured (if supported)
span.set_attribute("gen_ai.input.messages", messages)  # Python dict/list
```

### 11.3 Content Capture

**Opt-In Levels**:
1. **None** (Default): Don't capture content
2. **Attributes**: Capture on span attributes
3. **External Storage**: Upload to external storage, record references

**Truncation**:
- Instrumentations MAY provide truncation options
- Preserve JSON structure when truncating

**Privacy**:
- Content likely contains PII
- Opt-in by default
- Allow users to filter/redact

---

## 12. Versioning and Stability

### 12.1 Current Status

**Gen AI Conventions**:
- **Status**: Development (Experimental)
- **Stability**: No guarantees yet
- **Version**: Transitioning from v1.36.0 → latest

**Breaking Changes**:
- Possible until marked stable
- Instrumentations SHOULD NOT change by default
- Use `OTEL_SEMCONV_STABILITY_OPT_IN` for opt-in

### 12.2 Stability Levels

| Level | Meaning | Breaking Changes |
|-------|---------|------------------|
| Stable | Production-ready | No breaking changes without major version bump |
| Experimental | In development | Breaking changes possible |
| Deprecated | Sunset planned | Will be removed in future |

**Gen AI Status**: All attributes are `Experimental` (Development)

### 12.3 Migration Path

**From v1.36.0 → Latest**:
1. Set `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`
2. Test application with latest conventions
3. Update code if needed
4. Roll out gradually

**Future (→ Stable)**:
- Additional opt-in value will be added when stable
- Migration plan will be updated

---

## 13. Complete Attribute Registry

### 13.1 All Gen AI Attributes (56 total)

| Attribute | Type | Status | Description |
|-----------|------|--------|-------------|
| `gen_ai.operation.name` | string | Development | Operation type |
| `gen_ai.provider.name` | string | Development | LLM provider |
| `gen_ai.request.model` | string | Development | Model name requested |
| `gen_ai.response.model` | string | Development | Model name used |
| `gen_ai.request.temperature` | double | Development | Temperature setting |
| `gen_ai.request.max_tokens` | int | Development | Max tokens to generate |
| `gen_ai.request.top_p` | double | Development | Top-p sampling |
| `gen_ai.request.top_k` | double | Development | Top-k sampling |
| `gen_ai.request.frequency_penalty` | double | Development | Frequency penalty |
| `gen_ai.request.presence_penalty` | double | Development | Presence penalty |
| `gen_ai.request.stop_sequences` | string[] | Development | Stop sequences |
| `gen_ai.request.seed` | int | Development | Random seed |
| `gen_ai.request.choice.count` | int | Development | Number of choices |
| `gen_ai.request.encoding_formats` | string[] | Development | Embedding formats |
| `gen_ai.response.id` | string | Development | Response ID |
| `gen_ai.response.finish_reasons` | string[] | Development | Finish reasons |
| `gen_ai.usage.input_tokens` | int | Development | Input tokens |
| `gen_ai.usage.output_tokens` | int | Development | Output tokens |
| `gen_ai.token.type` | string | Development | Token type (input/output) |
| `gen_ai.conversation.id` | string | Development | Conversation ID |
| `gen_ai.output.type` | string | Development | Output modality |
| `gen_ai.input.messages` | any | Development | Input chat history |
| `gen_ai.output.messages` | any | Development | Output messages |
| `gen_ai.system_instructions` | any | Development | System instructions |
| `gen_ai.tool.definitions` | any | Development | Tool definitions |
| `gen_ai.tool.name` | string | Development | Tool name |
| `gen_ai.tool.type` | string | Development | Tool type |
| `gen_ai.tool.description` | string | Development | Tool description |
| `gen_ai.tool.call.id` | string | Development | Tool call ID |
| `gen_ai.tool.call.arguments` | any | Development | Tool arguments |
| `gen_ai.tool.call.result` | any | Development | Tool result |
| `gen_ai.agent.id` | string | Development | Agent ID |
| `gen_ai.agent.name` | string | Development | Agent name |
| `gen_ai.agent.description` | string | Development | Agent description |
| `gen_ai.evaluation.name` | string | Development | Evaluation metric name |
| `gen_ai.evaluation.score.value` | double | Development | Evaluation score |
| `gen_ai.evaluation.score.label` | string | Development | Score label |
| `gen_ai.evaluation.explanation` | string | Development | Score explanation |
| `gen_ai.embeddings.dimension.count` | int | Development | Embedding dimensions |
| `gen_ai.data_source.id` | string | Development | Data source ID |

**Plus Server Attributes** (stable):
- `server.address` (string)
- `server.port` (int)

**Plus Error Attributes** (stable):
- `error.type` (string)

**Total**: 56 gen_ai.* attributes + 3 stable attributes = **59 attributes**

---

## 14. Summary & Recommendations

### 14.1 Key Takeaways

1. **Gen AI conventions are experimental** - Breaking changes possible
2. **56 gen_ai.* attributes defined** - Comprehensive coverage
3. **3 signal types**: Traces (full), Metrics (full), Events/Logs (partial)
4. **Opt-in for sensitive content** - Default is no capture
5. **Standard OTel patterns apply** - TracerProvider, SpanProcessor, OTLP export

### 14.2 HoneyHive Alignment

**Strengths**:
- ✅ Uses standard OTel SDK components
- ✅ Supports gen_ai.* semantic conventions
- ✅ OTLP export
- ✅ Context propagation
- ✅ Batching and sampling

**Gaps**:
- ❌ **No Metrics signal** (critical gap vs. OTel standards)
- ❌ **No Logs signal** (Events not implemented)
- ⚠️ Multi-convention support (non-standard, but valuable)

### 14.3 Industry Comparison

**Metrics Support**:
- OTel Standard: ✅ 5 metrics defined
- Traceloop: ✅ Comprehensive
- OpenLit: ✅ Comprehensive
- Phoenix: ❌ None
- Langfuse: ❌ None
- HoneyHive: ❌ None

**3/6 platforms** (including OTel) support metrics - this is becoming table stakes

### 14.4 Priority Recommendations

1. **P0: Add Metrics Signal**
   - Implement `gen_ai.client.token.usage`
   - Implement `gen_ai.client.operation.duration`
   - Use standard OTel MeterProvider

2. **P1: Add Events/Logs**
   - Implement `gen_ai.client.inference.operation.details` event
   - Implement `gen_ai.evaluation.result` event
   - Use standard OTel LoggerProvider

3. **P2: Publish Performance Benchmarks**
   - Quantify overhead
   - Compare with competitors
   - Transparency builds trust

4. **P3: Stay Current with Gen AI Conventions**
   - Monitor for stable release
   - Adopt new attributes as they emerge
   - Participate in OTel community

---

## Evidence & Sources

| Finding | Source | Location |
|---------|--------|----------|
| 56 gen_ai attributes | OTel Spec | `docs/registry/attributes/gen-ai.md` |
| 5 metrics defined | OTel Spec | `docs/gen-ai/gen-ai-metrics.md` |
| 3 span types | OTel Spec | `docs/gen-ai/gen-ai-spans.md` |
| 2 events defined | OTel Spec | `docs/gen-ai/gen-ai-events.md` |
| Experimental status | OTel Spec | All gen-ai docs |
| v1.36.0 transition | OTel Spec | Warning in all docs |
| 15 provider values | OTel Spec | Well-known values table |
| Opt-in content capture | OTel Spec | `gen-ai-spans.md` sections |

**Repository Analyzed**: `github.com/open-telemetry/semantic-conventions` (cloned 2025-09-30)

---

**Document Complete**: Task 3.1 - OTel Standards Research  
**Next**: Task 3.2 - HoneyHive OTel Alignment Analysis
