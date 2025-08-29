# OpenInference Integration

Using the HoneyHive SDK with OpenInference instrumentors.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Supported Instrumentors](#supported-instrumentors)
- [Integration Patterns](#integration-patterns)
- [Advanced Configuration](#advanced-configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

OpenInference is a collection of instrumentors that automatically trace AI/ML operations across various frameworks and providers. When combined with the HoneyHive SDK, you get seamless observability into your AI applications without modifying your existing code.

### Key Benefits

- **Zero Code Changes** - Automatic instrumentation of AI operations
- **Framework Agnostic** - Works with OpenAI, Anthropic, Google AI, and more
- **Session Context** - Automatic session tracking and correlation
- **Rich Metadata** - Detailed span attributes for AI operations
- **Performance Monitoring** - Built-in latency and token tracking

### How It Works

1. **Initialize HoneyHiveTracer** with OpenInference instrumentors
2. **Instrumentors automatically wrap** AI library calls
3. **Spans are created** for each AI operation
4. **HoneyHive enriches** spans with session context
5. **Data is exported** via OTLP to your backend

---

## Quick Start

### Basic Integration

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize tracer with OpenInference instrumentor
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[OpenAIInstrumentor()]
)

# OpenInference automatically traces OpenAI calls
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Multiple Instrumentors

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

# Initialize with multiple instrumentors
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[
        OpenAIInstrumentor(),
        AnthropicInstrumentor()
    ]
)
```

---

## Supported Instrumentors

### OpenAI

**Package**: `openinference-instrumentation-openai`

```python
from openinference.instrumentation.openai import OpenAIInstrumentor

# Basic instrumentation
instrumentor = OpenAIInstrumentor()

# Advanced configuration
instrumentor = OpenAIInstrumentor(
    # Custom span names
    span_name_prefix="openai",
    # Custom attributes
    span_attributes={"framework": "openai"},
    # Exclude specific operations
    exclude_operations=["embeddings"]
)
```

**Supported Operations**:
- Chat completions
- Text completions
- Embeddings
- Fine-tuning
- File operations

### Anthropic

**Package**: `openinference-instrumentation-anthropic`

```python
from openinference.instrumentation.anthropic import AnthropicInstrumentor

instrumentor = AnthropicInstrumentor(
    span_name_prefix="anthropic",
    span_attributes={"framework": "anthropic"}
)
```

**Supported Operations**:
- Chat completions
- Text completions
- Embeddings

### Google AI

**Package**: `openinference-instrumentation-google`

```python
from openinference.instrumentation.google import GoogleAIInstrumentor

instrumentor = GoogleAIInstrumentor(
    span_name_prefix="google-ai",
    span_attributes={"framework": "google-ai"}
)
```

**Supported Operations**:
- Chat completions
- Text generation
- Embeddings
- Image generation

### LangChain

**Package**: `openinference-instrumentation-langchain`

```python
from openinference.instrumentation.langchain import LangChainInstrumentor

instrumentor = LangChainInstrumentor(
    span_name_prefix="langchain",
    span_attributes={"framework": "langchain"}
)
```

**Supported Operations**:
- LLM calls
- Chain execution
- Agent operations
- Tool usage

### LlamaIndex

**Package**: `openinference-instrumentation-llamaindex`

```python
from openinference.instrumentation.llamaindex import LlamaIndexInstrumentor

instrumentor = LlamaIndexInstrumentor(
    span_name_prefix="llamaindex",
    span_attributes={"framework": "llamaindex"}
)
```

**Supported Operations**:
- Query engine operations
- Index operations
- Document processing
- Retrieval operations

---

## Integration Patterns

### 1. Application-Level Integration

Initialize the tracer once at application startup:

```python
# app.py
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Global tracer instance
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[OpenAIInstrumentor()]
)

# Your application code continues unchanged
import openai
# All OpenAI calls are automatically traced
```

### 2. Module-Level Integration

Initialize instrumentors in specific modules:

```python
# ai_service.py
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

class AIService:
    def __init__(self):
        self.tracer = HoneyHiveTracer(
            api_key="your-api-key",
            project="ai-service",
            source="production",
            instrumentors=[OpenAIInstrumentor()]
        )
    
    def generate_response(self, prompt):
        # This call is automatically traced
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response
```

### 3. Conditional Integration

Enable instrumentation based on environment:

```python
import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

def create_tracer():
    instrumentors = []
    
    # Only instrument OpenAI in production
    if os.getenv("ENVIRONMENT") == "production":
        instrumentors.append(OpenAIInstrumentor())
    
    return HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        source=os.getenv("HH_SOURCE"),
        instrumentors=instrumentors
    )
```

### 4. Custom Instrumentor Configuration

Configure instrumentors with custom settings:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Custom OpenAI instrumentor
openai_instrumentor = OpenAIInstrumentor(
    span_name_prefix="my-openai",
    span_attributes={
        "service": "chat-service",
        "version": "1.0.0"
    },
    # Exclude specific operations
    exclude_operations=["embeddings"],
    # Custom span creation logic
    span_callback=lambda span, operation: span.set_attribute("custom", "value")
)

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[openai_instrumentor]
)
```

---

## Advanced Configuration

### Custom Span Attributes

Add custom attributes to all instrumented spans:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

class CustomOpenAIInstrumentor(OpenAIInstrumentor):
    def _create_span(self, operation, **kwargs):
        span = super()._create_span(operation, **kwargs)
        
        # Add custom attributes
        span.set_attribute("ai.provider", "openai")
        span.set_attribute("ai.operation", operation)
        span.set_attribute("custom.service", "my-ai-service")
        
        return span

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[CustomOpenAIInstrumentor()]
)
```

### Span Filtering

Filter spans based on custom logic:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

class FilteredOpenAIInstrumentor(OpenAIInstrumentor):
    def _should_instrument(self, operation, **kwargs):
        # Only instrument chat completions
        if operation != "chat.completions.create":
            return False
        
        # Skip if prompt is too short
        messages = kwargs.get("messages", [])
        if messages and len(messages[0].get("content", "")) < 10:
            return False
        
        return True

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[FilteredOpenAIInstrumentor()]
)
```

### Custom Span Names

Override default span naming:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

class NamedOpenAIInstrumentor(OpenAIInstrumentor):
    def _get_span_name(self, operation, **kwargs):
        # Custom span naming logic
        if operation == "chat.completions.create":
            messages = kwargs.get("messages", [])
            if messages:
                first_message = messages[0].get("content", "")
                # Truncate long messages
                if len(first_message) > 50:
                    first_message = first_message[:50] + "..."
                return f"OpenAI Chat: {first_message}"
        
        return f"OpenAI {operation}"

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="my-project",
    source="production",
    instrumentors=[NamedOpenAIInstrumentor()]
)
```

---

## Examples

### Chat Application

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
import openai

# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="chat-app",
    source="production",
    instrumentors=[OpenAIInstrumentor()]
)

class ChatBot:
    def __init__(self):
        self.conversation_history = []
    
    def chat(self, user_message):
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        try:
            # This call is automatically traced
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            # Extract response
            ai_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_message})
            
            return ai_message
            
        except Exception as e:
            # Error will be captured in span
            raise
    
    def get_conversation_summary(self):
        # This call is also automatically traced
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this conversation in one sentence."},
                {"role": "user", "content": str(self.conversation_history)}
            ],
            max_tokens=50
        )
        
        return response.choices[0].message.content

# Usage
bot = ChatBot()
response = bot.chat("Hello! How are you?")
summary = bot.get_conversation_summary()
```

### Multi-Provider AI Service

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor
import openai
import anthropic

# Initialize tracer with multiple instrumentors
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="multi-ai-service",
    source="production",
    instrumentors=[
        OpenAIInstrumentor(),
        AnthropicInstrumentor()
    ]
)

class MultiAIProvider:
    def __init__(self):
        self.openai_client = openai
        self.anthropic_client = anthropic.Anthropic(api_key="your-anthropic-key")
    
    def generate_with_openai(self, prompt, model="gpt-3.5-turbo"):
        # Automatically traced by OpenAI instrumentor
        response = self.openai_client.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def generate_with_anthropic(self, prompt, model="claude-3-sonnet-20240229"):
        # Automatically traced by Anthropic instrumentor
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def compare_models(self, prompt):
        openai_result = self.generate_with_openai(prompt)
        anthropic_result = self.generate_with_anthropic(prompt)
        
        return {
            "openai": openai_result,
            "anthropic": anthropic_result
        }

# Usage
ai_service = MultiAIProvider()
results = ai_service.compare_models("Explain quantum computing in simple terms")
```

### LangChain Integration

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.langchain import LangChainInstrumentor
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize tracer with LangChain instrumentor
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="langchain-app",
    source="production",
    instrumentors=[LangChainInstrumentor()]
)

# Create LangChain components
llm = OpenAI(temperature=0.7)
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short poem about {topic}."
)
chain = LLMChain(llm=llm, prompt=prompt)

# All LangChain operations are automatically traced
def generate_poem(topic):
    return chain.run(topic)

# Usage
poem = generate_poem("artificial intelligence")
```

---

## Troubleshooting

### Common Issues

#### 1. Instrumentation Not Working

**Symptoms**: Spans not appearing in HoneyHive

**Solutions**:
```python
# Check if instrumentor is properly initialized
print(f"Tracer instance: {HoneyHiveTracer._instance}")
print(f"Session ID: {HoneyHiveTracer._instance.session_id}")

# Verify instrumentor is in the list
print(f"Instrumentors: {HoneyHiveTracer._instance.instrumentors}")
```

#### 2. Missing Dependencies

**Symptoms**: Import errors for instrumentors

**Solutions**:
```bash
# Install required packages
pip install openinference-instrumentation-openai
pip install openinference-instrumentation-anthropic
pip install openinference-instrumentation-google
```

#### 3. Span Attributes Missing

**Symptoms**: Spans appear but lack expected attributes

**Solutions**:
```python
# Check if session context is properly set
tracer = HoneyHiveTracer._instance
print(f"Session ID: {tracer.session_id}")
print(f"Project: {tracer.project}")
print(f"Source: {tracer.source}")

# Verify baggage context
from opentelemetry import baggage
ctx = baggage.get_all()
print(f"Baggage: {ctx}")
```

#### 4. Performance Issues

**Symptoms**: Slow response times after instrumentation

**Solutions**:
```python
# Disable instrumentation for performance-critical operations
import os
os.environ["HH_DISABLE_HTTP_TRACING"] = "true"

# Or use conditional instrumentation
if not performance_critical:
    instrumentors.append(OpenAIInstrumentor())
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize tracer with debug output
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="debug-project",
    source="development",
    instrumentors=[OpenAIInstrumentor()],
    debug=True
)

# Check tracer status
print(f"Tracer initialized: {tracer is not None}")
print(f"Session created: {tracer.session_id is not None}")
print(f"Instrumentors loaded: {len(tracer.instrumentors)}")
```

### Testing Instrumentation

Test if instrumentation is working:

```python
def test_instrumentation():
    """Test if OpenInference instrumentation is working."""
    
    # Create a simple test
    import openai
    
    try:
        # This should create a span
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test message"}],
            max_tokens=5
        )
        
        print("✅ Instrumentation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Instrumentation test failed: {e}")
        return False

# Run test
test_instrumentation()
```

---

## Best Practices

### 1. Instrumentor Selection

- **Use specific instrumentors** for the frameworks you actually use
- **Avoid unnecessary instrumentation** to minimize overhead
- **Test instrumentors individually** before combining them

### 2. Configuration Management

- **Environment-based configuration** for different deployment stages
- **Centralized tracer initialization** to avoid conflicts
- **Consistent naming conventions** for spans and attributes

### 3. Performance Optimization

- **Monitor instrumentation overhead** in production
- **Use conditional instrumentation** for performance-critical paths
- **Implement span sampling** for high-volume applications

### 4. Error Handling

- **Graceful degradation** when instrumentation fails
- **Comprehensive error logging** for troubleshooting
- **Fallback mechanisms** for critical operations

### 5. Monitoring

- **Track instrumentation coverage** across your application
- **Monitor span creation rates** and performance impact
- **Alert on instrumentation failures** or missing spans

---

## Additional Resources

- **[OpenInference Documentation](https://github.com/Arize-ai/openinference)** - Official OpenInference documentation
- **[HoneyHive API Reference](API_REFERENCE.md)** - Complete SDK API reference
- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Technical implementation details
- **[Examples Directory](../examples/)** - Code examples and demonstrations

---

This guide covers the essential aspects of integrating the HoneyHive SDK with OpenInference instrumentors. For more advanced usage patterns and troubleshooting, refer to the OpenInference documentation and the HoneyHive API reference.
