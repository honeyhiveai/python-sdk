# HoneyHive LiteLLM Integration Guide

This guide shows how to integrate HoneyHive with LiteLLM for comprehensive LLM observability.

---

## Overview

[LiteLLM](https://github.com/BerriAI/litellm) is an abstraction layer that provides OpenAI-compatible API access to 100+ LLM providers (OpenAI, Anthropic, Bedrock, Azure, etc.).

HoneyHive's integration captures:
- ✅ All LLM calls (completion, streaming, embeddings)
- ✅ Complete request/response data
- ✅ Token usage and costs
- ✅ Provider-specific metadata
- ✅ Router deployment selection
- ✅ Proxy team/user tracking
- ✅ Custom user metadata

---

## Installation

```bash
pip install honeyhive-litellm
```

**Requirements:**
- Python 3.8+
- `litellm` installed
- HoneyHive API key ([get one here](https://app.honeyhive.ai))

---

## Quick Start

### Option 1: Simple Init (Recommended)

```python
import honeyhive_litellm
import litellm

# Initialize HoneyHive
honeyhive_litellm.init(
    api_key="YOUR_HONEYHIVE_API_KEY",
    project="my-project"
)

# Use LiteLLM normally - all calls are automatically logged
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### Option 2: Environment Variables

```bash
export HONEYHIVE_API_KEY="your-api-key"
export HONEYHIVE_PROJECT="my-project"
export HONEYHIVE_ENVIRONMENT="production"
```

```python
import honeyhive_litellm
import litellm

# Load from environment
honeyhive_litellm.init()

# Use LiteLLM
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Option 3: Manual Logger Setup

```python
from honeyhive_litellm import HoneyHiveLogger
import litellm

logger = HoneyHiveLogger(
    api_key="YOUR_HONEYHIVE_API_KEY",
    project="my-project",
    environment="production",
    capture_message_content=True,  # Capture input/output
    debug=False,  # Enable for troubleshooting
)

litellm.callbacks = [logger]

# Use LiteLLM
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## Configuration

### All Options

```python
honeyhive_litellm.init(
    api_key="YOUR_HONEYHIVE_API_KEY",  # Required
    project="my-project",              # Required
    environment="production",          # Optional, default: "production"
    api_url="https://api.honeyhive.ai", # Optional, default: HoneyHive API
    capture_message_content=True,      # Optional, default: True
    capture_headers=False,             # Optional, default: False
    capture_raw_request=False,         # Optional, default: False (includes full provider request)
    custom_attributes={                # Optional, added to all traces
        "service": "recommendation-engine",
        "version": "1.2.3"
    },
    debug=False,                       # Optional, default: False
)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HONEYHIVE_API_KEY` | Your HoneyHive API key | Required |
| `HONEYHIVE_PROJECT` | Project name | Required |
| `HONEYHIVE_ENVIRONMENT` | Environment (prod/staging/dev) | `"production"` |
| `HONEYHIVE_API_URL` | API base URL | `"https://api.honeyhive.ai"` |
| `HONEYHIVE_CAPTURE_CONTENT` | Capture message content | `"true"` |
| `HONEYHIVE_CAPTURE_HEADERS` | Capture HTTP headers | `"false"` |
| `HONEYHIVE_CAPTURE_RAW` | Capture raw requests | `"false"` |
| `HONEYHIVE_DEBUG` | Enable debug logging | `"false"` |

---

## Usage Examples

### Example 1: Basic Completion

```python
import honeyhive_litellm
import litellm

honeyhive_litellm.init(
    api_key="your-key",
    project="chatbot"
)

response = litellm.completion(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in one sentence."}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
# ✅ Automatically logged to HoneyHive with:
# - Model: gpt-4
# - Provider: openai
# - Input/output messages
# - Token usage
# - Latency
```

### Example 2: With Custom Metadata

```python
import honeyhive_litellm
import litellm

honeyhive_litellm.init(api_key="...", project="...")

response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Recommend a movie"}],
    metadata={
        "user_id": "user_123",
        "session_id": "sess_456",
        "feature": "movie_recommendation",
        "experiment": "recommendation_v2"
    }
)

# ✅ Metadata attached to trace in HoneyHive for filtering/analysis
```

### Example 3: Multiple Providers

```python
import honeyhive_litellm
import litellm

honeyhive_litellm.init(api_key="...", project="...")

# OpenAI
response1 = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Anthropic
response2 = litellm.completion(
    model="anthropic/claude-3-opus",
    messages=[{"role": "user", "content": "Hello"}]
)

# AWS Bedrock
response3 = litellm.completion(
    model="bedrock/anthropic.claude-3-sonnet",
    messages=[{"role": "user", "content": "Hello"}]
)

# ✅ All three calls logged with provider-specific metadata
```

### Example 4: Streaming

```python
import honeyhive_litellm
import litellm

honeyhive_litellm.init(api_key="...", project="...")

response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")

# ✅ Complete streaming response logged after completion
```

### Example 5: Function Calling

```python
import honeyhive_litellm
import litellm

honeyhive_litellm.init(api_key="...", project="...")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=tools,
    tool_choice="auto"
)

# ✅ Tool calls logged with complete parameters
```

---

## Using with LiteLLM Router

The Router provides load balancing and fallback across multiple deployments.

```python
from litellm import Router
import honeyhive_litellm

# Initialize HoneyHive
honeyhive_litellm.init(api_key="...", project="router-demo")

# Set up Router with multiple deployments
router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": "openai-key-1",
            },
            "model_info": {"id": "openai-primary"}
        },
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "azure/gpt-4-deployment",
                "api_key": "azure-key",
                "api_base": "https://my-endpoint.openai.azure.com"
            },
            "model_info": {"id": "azure-fallback"}
        }
    ],
    routing_strategy="lowest-latency",
    fallbacks=[{"gpt-4": ["azure-fallback"]}],
    num_retries=2,
)

# Router calls automatically logged
response = router.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# ✅ HoneyHive captures:
# - Which deployment was selected (openai-primary or azure-fallback)
# - Routing strategy used
# - Fallback information if primary failed
# - Retry count
```

---

## Using with LiteLLM Proxy

The Proxy provides an HTTP gateway with authentication and budget tracking.

### Proxy Server Setup

```yaml
# config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  callbacks: ["honeyhive"]
  success_callback: ["honeyhive"]
  failure_callback: ["honeyhive"]
  
  # HoneyHive configuration
  honeyhive_api_key: os.environ/HONEYHIVE_API_KEY
  honeyhive_project: "proxy-demo"
  honeyhive_environment: "production"
```

```bash
# Start proxy
litellm --config config.yaml
```

### Client Usage

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="your-proxy-virtual-key"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# ✅ HoneyHive captures:
# - Virtual key used
# - Team/user information
# - Budget tracking
# - Request ID
```

---

## Data Captured

### Standard Fields

Every trace includes:
- `trace_id` - Unique identifier
- `timestamp` - Request start time
- `duration_ms` - Request duration
- `success` - Whether call succeeded
- `model` - Model name (e.g., "gpt-4")
- `provider` - LLM provider (e.g., "openai", "anthropic")

### Input Data

- `messages` - Input messages (if `capture_message_content=True`)
- `parameters` - Request parameters (temperature, max_tokens, etc.)
- `tools` - Function calling tools (if used)
- `tool_choice` - Tool selection strategy

### Output Data

- `content` - Response content (if `capture_message_content=True`)
- `tool_calls` - Function call results
- `finish_reason` - Why generation stopped
- `reasoning_content` - Thinking/reasoning tokens (if available)

### Usage Data

- `prompt_tokens` - Input tokens
- `completion_tokens` - Output tokens
- `total_tokens` - Total tokens
- `cache_read_tokens` - Cached tokens read
- `cache_creation_tokens` - Cached tokens created
- `estimated_cost` - Cost estimate (if available)

### Router Data (when using Router)

- `routing_strategy` - Strategy used (lowest-latency, least-busy, etc.)
- `deployment_id` - Selected deployment
- `model_group` - Model group name
- `fallback_info` - Fallback chain if used
- `retry_count` - Number of retries

### Proxy Data (when using Proxy)

- `virtual_key_hash` - Virtual key used
- `team_id` - Team identifier
- `user_id` - User identifier
- `request_id` - Proxy request ID

### User Metadata

- All fields passed via `metadata={}` parameter
- Custom attributes from `custom_attributes` config

---

## Privacy & Security

### PII Considerations

By default, input and output messages are captured. To disable:

```python
honeyhive_litellm.init(
    api_key="...",
    project="...",
    capture_message_content=False  # Don't capture message content
)
```

### Redaction

Implement custom redaction in your code before calling LiteLLM:

```python
def redact_pii(text):
    # Your redaction logic
    return text.replace("user@example.com", "[REDACTED_EMAIL]")

messages = [
    {"role": "user", "content": redact_pii(user_input)}
]

response = litellm.completion(model="gpt-4", messages=messages)
```

### API Key Security

Never hardcode API keys. Use environment variables or secret management:

```python
import os

honeyhive_litellm.init(
    api_key=os.getenv("HONEYHIVE_API_KEY"),
    project=os.getenv("HONEYHIVE_PROJECT")
)
```

---

## Troubleshooting

### Enable Debug Logging

```python
honeyhive_litellm.init(
    api_key="...",
    project="...",
    debug=True  # Prints detailed logs
)
```

### Verify Integration

```python
import honeyhive_litellm
import litellm

# Initialize with debug
honeyhive_litellm.init(api_key="...", project="...", debug=True)

# Make a test call
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "test"}],
    metadata={"test": True}
)

# Check debug output for "HoneyHive Trace Logged" message
```

### Common Issues

**Issue:** Traces not appearing in HoneyHive
- Verify API key is correct
- Check `debug=True` output for errors
- Ensure `project` name matches HoneyHive project

**Issue:** High latency
- Traces are logged asynchronously (non-blocking)
- If concerned, measure impact with and without integration

**Issue:** Missing metadata
- Ensure `metadata` parameter is a dict
- Check that `capture_message_content=True` (default)

---

## Performance Impact

- **Overhead:** < 5ms per request (async logging)
- **Network:** Traces sent asynchronously (non-blocking)
- **Memory:** Minimal (traces queued and batched)

---

## Migration Guides

### From OpenInference

```python
# Before
from openinference.instrumentation.litellm import LiteLLMInstrumentor
LiteLLMInstrumentor().instrument()

# After
import honeyhive_litellm
honeyhive_litellm.init(api_key="...", project="...")
```

### From OpenLIT

```python
# Before
import openlit
openlit.init(otlp_endpoint="...")

# After
import honeyhive_litellm
honeyhive_litellm.init(api_key="...", project="...")
```

---

## Support

- **Documentation:** https://docs.honeyhive.ai
- **Issues:** https://github.com/honeyhiveai/python-sdk/issues
- **Discord:** https://discord.gg/honeyhive
- **Email:** support@honeyhive.ai

---

## License

[Same as honeyhiveai/python-sdk]

