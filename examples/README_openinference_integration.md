# OpenInference Integration with HoneyHive SDK

This example demonstrates how to integrate [OpenInference](https://github.com/Arize-ai/openinference) with our HoneyHive SDK and tracer instance **without requiring any code changes** to the SDK itself.

## Overview

OpenInference is an open-source observability framework that provides automatic instrumentation for various AI/ML libraries, including OpenAI. This integration allows you to:

- Automatically capture all OpenAI API calls
- Send traces through your existing HoneyHive tracer
- Enhance observability without modifying SDK code
- Get detailed insights into AI model usage and performance

## Key Benefits

✅ **Zero Code Changes**: Our SDK works exactly as before  
✅ **Vanilla Tracer Only**: Uses only our core tracer and spans, no provider complexity  
✅ **Automatic Instrumentation**: All OpenAI calls are automatically traced  
✅ **Enhanced Observability**: Rich metadata from OpenInference  
✅ **Seamless Integration**: Works with existing HoneyHive infrastructure  
✅ **Async Support**: Full support for both sync and async operations  

## How It Works

The integration works through OpenTelemetry's global tracer provider system:

1. **HoneyHive Tracer**: Our SDK provides the OpenTelemetry tracer provider
2. **OpenInference Instrumentation**: Automatically instruments OpenAI clients
3. **Automatic Tracing**: All OpenAI API calls generate spans automatically
4. **Unified Observability**: Traces flow through our existing HoneyHive infrastructure

## Prerequisites

```bash
# Install OpenInference OpenAI instrumentation
pip install openinference-instrumentation-openai

# Install OpenAI client
pip install openai

# Ensure our HoneyHive SDK is available
pip install -e .
```

## Environment Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Set HoneyHive configuration (optional, will use defaults if not set)
export HH_API_KEY="your-honeyhive-api-key"
export HH_PROJECT="your-project"
export HH_SOURCE="your-source"
```

## Usage Examples

### Basic Integration

```python
from openinference.instrumentation.openai import OpenAIInstrumentor
from honeyhive.tracer import HoneyHiveTracer

# Initialize HoneyHive tracer using modern approach
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="development"
)

# Enable OpenInference instrumentation
instrumentor = OpenAIInstrumentor()
instrumentor.instrument()

# Now all OpenAI calls are automatically traced!
import openai
client = openai.OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Clean up
instrumentor.uninstrument()
```

### With Vanilla Tracer and Spans

```python
from honeyhive.tracer import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="development"
)

# Enable instrumentation
instrumentor = OpenAIInstrumentor()
instrumentor.instrument()

# Create custom spans
with tracer.start_span("ai_operation") as span:
    span.set_attribute("operation.type", "openai_chat_completion")
    span.set_attribute("business.context", "user_query")
    
    # Make OpenAI call - automatically traced by OpenInference
    client = openai.OpenAI(api_key="your-key")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-3.5-turbo"
    )
    
    # Enrich span with response data
    span.set_attribute("openai.model", "gpt-3.5-turbo")
    span.set_attribute("openai.tokens_used", response.usage.total_tokens)

# Clean up
instrumentor.uninstrument()
```

## What Gets Traced

OpenInference automatically captures:

- **Request Details**: Model, messages, parameters, temperature, etc.
- **Response Data**: Tokens used, completion time, model response
- **Performance Metrics**: Latency, throughput, error rates
- **Usage Patterns**: Model selection, parameter trends, cost analysis

## Integration Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   Your Code     │───▶│  OpenInference      │───▶│  HoneyHive      │
│                 │    │  Instrumentation    │    │  Vanilla Tracer │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
         │                       │                        │
         │                       ▼                        ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         └─────────────▶│   OpenAI API    │    │   HoneyHive     │
                        │   (Instrumented)│    │   Backend       │
                        └─────────────────┘    └─────────────────┘
```

## Advanced Features

### Hierarchical Span Management

```python
from honeyhive.tracer import HoneyHiveTracer

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="development"
)

# Create parent span for complex workflow
with tracer.start_span("ai_workflow") as parent_span:
    parent_span.set_attribute("workflow.type", "multi_step_processing")
    
    # Step 1
    with tracer.start_span("step_1") as step1_span:
        step1_span.set_attribute("step.name", "initial_generation")
        # OpenAI call automatically traced by OpenInference
        response1 = client.chat.completions.create(...)
    
    # Step 2
    with tracer.start_span("step_2") as step2_span:
        step2_span.set_attribute("step.name", "refinement")
        # OpenAI call automatically traced by OpenInference
        response2 = client.chat.completions.create(...)
    
    # Parent span contains workflow summary
    parent_span.set_attribute("total_tokens", total_tokens)
```

### Custom Span Attributes

```python
with tracer.start_span("custom_operation") as span:
    # Add custom attributes
    span.set_attribute("custom.attribute", "value")
    span.set_attribute("integration.type", "openinference_honeyhive")
    
    # Make OpenAI call - automatically traced
    response = client.chat.completions.create(...)
    
    # Enrich span with response data
    span.set_attribute("openai.response_tokens", response.usage.total_tokens)
```

### Async Support

```python
import asyncio
from openinference.instrumentation.openai import OpenAIInstrumentor

# Enable instrumentation
instrumentor = OpenAIInstrumentor()
instrumentor.instrument()

async def async_operation():
    with tracer.start_span("async_ai_call") as span:
        client = openai.AsyncOpenAI(api_key="your-key")
        response = await client.chat.completions.create(...)
        return response

# Run async operation
result = asyncio.run(async_operation())

# Clean up
instrumentor.uninstrument()
```

## Configuration Options

OpenInference provides various configuration options:

```python
from openinference.instrumentation.openai import OpenAIInstrumentor

# Configure instrumentation
instrumentor = OpenAIInstrumentor(
    # Custom span names
    span_name_prefix="openai",
    
    # Custom attributes
    span_attributes={
        "custom.attribute": "value"
    },
    
    # Filter specific operations
    include_operations=["chat.completions.create"]
)

# Enable instrumentation
instrumentor.instrument()
```

## Running the Example

### Quick Start

```bash
# Install dependencies
pip install openinference-instrumentation-openai openai

# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Run the example
python examples/openinference_integration_simple.py
```

### Expected Output

```
🚀 OpenInference + HoneyHive Vanilla Tracer Integration Example
======================================================================
✓ OpenInference OpenAI instrumentation available
✓ OpenAI client available
✓ HoneyHive configuration loaded
  - Project: your-project
  - Source: your-source
  - API URL: https://api.honeyhive.ai

=== Basic OpenInference Integration Demo ===
Setting up OpenInference integration with HoneyHive...
✓ OpenInference OpenAI instrumentation enabled
✓ All OpenAI API calls will now be traced through HoneyHive
Making OpenAI API call (automatically traced)...
✓ OpenAI API call completed successfully
✓ Response: Hello! I'm doing well, thank you for asking...
✓ Usage: CompletionUsage(prompt_tokens=9, completion_tokens=15, total_tokens=24)
✓ OpenInference instrumentation disabled

=== Vanilla Tracer + OpenInference Integration Demo ===
Setting up OpenInference integration with HoneyHive...
✓ OpenInference OpenAI instrumentation enabled
✓ All OpenAI API calls will now be traced through HoneyHive
✓ HoneyHive vanilla tracer loaded
✓ Project: your-project
✓ Source: your-source
✓ Custom span created with HoneyHive vanilla tracer
✓ This span will be enriched with OpenInference data
✓ OpenAI call completed successfully
✓ Response: Quantum computing is a revolutionary technology...
✓ Usage: CompletionUsage(prompt_tokens=12, completion_tokens=45, total_tokens=57)
✓ Custom span completed with enriched data
✓ OpenInference automatically traced the OpenAI API call
✓ Both spans are now available in HoneyHive
✓ OpenInference instrumentation disabled

🎉 Integration demonstration completed!

Key Benefits:
✓ No code changes required in our SDK
✓ Uses only vanilla tracer and spans
✓ Automatic OpenAI API call tracing through OpenInference
✓ Enhanced observability without provider complexity
✓ Seamless integration with existing HoneyHive infrastructure
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure OpenInference is installed
   ```bash
   pip install openinference-instrumentation-openai
   ```

2. **No Traces**: Check that instrumentation is enabled
   ```python
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument()  # Don't forget this!
   ```

3. **Missing OpenAI Key**: Set the environment variable
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

### Debug Mode

Enable debug logging to see instrumentation details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# OpenInference will show detailed instrumentation logs
```

## Best Practices

1. **Enable Early**: Instrument as early as possible in your application
2. **Clean Up**: Always call `uninstrument()` when done
3. **Error Handling**: Wrap instrumentation in try-finally blocks
4. **Performance**: Instrumentation overhead is minimal (<1ms per call)
5. **Monitoring**: Use HoneyHive's monitoring tools to observe traces
6. **Vanilla Approach**: Use only our core tracer and spans for simplicity

## Comparison with Provider Approach

| Aspect | Vanilla Tracer | Provider Integration |
|--------|----------------|---------------------|
| **Complexity** | Simple, direct | More complex, additional layers |
| **Flexibility** | High - full control | Lower - constrained by provider |
| **Maintenance** | Easy - fewer dependencies | Harder - more moving parts |
| **Performance** | Minimal overhead | Slight additional overhead |
| **Debugging** | Straightforward | More complex debugging |
| **Integration** | Direct OpenTelemetry | Provider-specific patterns |

## Next Steps

1. **Run the Example**: Execute `python examples/openinference_integration_simple.py`
2. **Customize**: Adapt the integration to your specific use case
3. **Monitor**: Use HoneyHive's dashboard to observe the enhanced traces
4. **Extend**: Explore other OpenInference instrumentations (Anthropic, LangChain, etc.)

## Learn More

- [OpenInference Documentation](https://github.com/Arize-ai/openinference)
- [OpenInference OpenAI Instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [HoneyHive SDK Documentation](https://docs.honeyhive.ai/)
