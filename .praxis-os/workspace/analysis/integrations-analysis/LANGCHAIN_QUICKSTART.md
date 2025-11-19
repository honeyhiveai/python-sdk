# LangChain + HoneyHive Quick Start Guide

**Last Updated:** October 15, 2025  
**Status:** Current (v0.1.0rc3)

---

## Overview

This guide shows you how to use HoneyHive with LangChain to get observability for your LLM applications. We support two approaches:

1. **Tier 1 (Available Now):** Passthrough via existing instrumentors - captures LLM API calls
2. **Tier 2 (Coming Soon):** Custom callback handler - captures chain/agent context

---

## Installation

```bash
# Install HoneyHive SDK
pip install honeyhive

# Install LangChain packages
pip install langchain langchain-openai

# Install instrumentors for the providers you use
pip install openinference-instrumentation-openai    # For OpenAI
pip install openinference-instrumentation-anthropic  # For Anthropic
# ... add others as needed
```

---

## Tier 1: Basic Setup (Passthrough)

### What's Captured

✅ LLM model name  
✅ Input/output tokens and usage  
✅ Request latency  
✅ Prompt and completion content  
❌ Chain/agent context (use Tier 2 for this)

### Code Example

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key="YOUR_HONEYHIVE_API_KEY",
    project="langchain-app"
)

# Instrument OpenAI client (before importing LangChain components)
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Now use LangChain as normal - calls are automatically traced!
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
response = llm.invoke("What is the capital of France?")
print(response.content)

# Traces automatically sent to HoneyHive dashboard
```

### How It Works

1. **HoneyHive** sets up the tracer with your API key
2. **OpenAIInstrumentor** patches the OpenAI client globally
3. **LangChain** creates its own OpenAI client internally
4. **API calls** are automatically intercepted and traced
5. **Traces** are sent to your HoneyHive project

**Key Point:** This works because LangChain uses the official `openai` Python SDK internally, and the instrumentor patches it at the module level.

---

## Multiple Providers

If you're using multiple LLM providers (OpenAI, Anthropic, etc.), instrument all of them:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="YOUR_HONEYHIVE_API_KEY",
    project="langchain-app"
)

# Instrument all providers
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
AnthropicInstrumentor().instrument(tracer_provider=tracer.provider)

# Now both work
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

gpt4 = ChatOpenAI(model="gpt-4")
claude = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Both calls are traced
response1 = gpt4.invoke("Hello from OpenAI")
response2 = claude.invoke("Hello from Anthropic")
```

---

## Chains and Agents

Tier 1 captures the underlying LLM calls, but not the chain/agent orchestration:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(api_key="YOUR_API_KEY", project="my-app")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Create a chain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4")
prompt = PromptTemplate.from_template("What is the capital of {country}?")
chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain
result = chain.invoke({"country": "France"})

# ✅ What's captured:
#    - LLM API call to OpenAI
#    - Prompt: "What is the capital of France?"
#    - Response: "The capital of France is Paris."
#    - Token usage, latency, etc.

# ❌ What's NOT captured:
#    - Chain name or type
#    - Input variable {"country": "France"}
#    - Chain execution flow
```

For full chain/agent observability, use **Tier 2** (coming soon).

---

## Environment Variables

Set these environment variables for automatic configuration:

```bash
# HoneyHive
export HONEYHIVE_API_KEY="your_api_key"
export HONEYHIVE_PROJECT="langchain-app"

# Optional: LangChain (if you also want LangSmith tracing)
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="your_langsmith_api_key"
```

Then in code:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Reads from env vars
tracer = HoneyHiveTracer.init()
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Ready to go!
```

---

## What You'll See in HoneyHive

When you run the above code, you'll see traces in your HoneyHive dashboard with:

- **Span Name:** `ChatCompletions` (from OpenAI instrumentor)
- **Attributes:**
  - `gen_ai.system`: `openai`
  - `gen_ai.request.model`: `gpt-4`
  - `gen_ai.usage.input_tokens`: `15`
  - `gen_ai.usage.output_tokens`: `8`
  - `gen_ai.usage.total_tokens`: `23`
  - Plus full prompt and completion content

---

## Complete Example

```python
"""
LangChain + HoneyHive Integration Example
Demonstrates Tier 1 (passthrough) approach.
"""

import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def main():
    # Step 1: Initialize HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HONEYHIVE_API_KEY"),
        project="langchain-demo"
    )
    
    # Step 2: Instrument OpenAI (before using LangChain)
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    # Step 3: Create LangChain components
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
    )
    
    prompt = PromptTemplate.from_template(
        "You are a helpful assistant. {question}"
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 4: Run queries - automatically traced!
    questions = [
        "What is the capital of France?",
        "What is 2+2?",
        "Who wrote Romeo and Juliet?",
    ]
    
    for question in questions:
        print(f"\n🤔 Question: {question}")
        result = chain.invoke({"question": question})
        print(f"✅ Answer: {result['text']}")
    
    print("\n📊 Check your HoneyHive dashboard for traces!")
    print(f"   Project: langchain-demo")

if __name__ == "__main__":
    main()
```

Run it:
```bash
export HONEYHIVE_API_KEY="your_api_key"
python example.py
```

---

## Advanced: Streaming Responses

Streaming also works with Tier 1:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(api_key="YOUR_API_KEY", project="my-app")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", streaming=True)

# Stream the response
for chunk in llm.stream("Tell me a joke"):
    print(chunk.content, end="", flush=True)

# Full trace including all chunks sent to HoneyHive
```

---

## Limitations of Tier 1

**What's NOT captured:**

- ❌ Chain names and types
- ❌ Agent actions and reasoning
- ❌ Tool calls (function calling)
- ❌ Retriever queries
- ❌ LangChain-specific metadata (tags, custom metadata)
- ❌ Hierarchical relationships between chains

**Why?** Because Tier 1 only instruments the underlying LLM API clients. It doesn't hook into LangChain's callback system.

**Solution:** Use **Tier 2** when it's available (see roadmap below).

---

## Tier 2: Coming Soon

Tier 2 will add a custom LangChain callback handler to capture:

✅ Chain hierarchy  
✅ Agent actions and decisions  
✅ Tool calls and results  
✅ Retriever queries  
✅ LangChain tags and metadata  

**Expected API:**
```python
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.langchain import HoneyHiveLangChainHandler

tracer = HoneyHiveTracer.init(project="my-app")
handler = HoneyHiveLangChainHandler(tracer)

# Pass handler to chains
result = chain.invoke(
    {"input": "..."},
    config={"callbacks": [handler]}  # 👈 Captures chain context
)
```

**Status:** In development. [Star our repo](https://github.com/honeyhiveai/python-sdk) for updates!

---

## Troubleshooting

### Problem: No traces showing up

**Solution 1:** Make sure instrumentor is called BEFORE importing LangChain:

```python
# ❌ WRONG ORDER
from langchain_openai import ChatOpenAI
OpenAIInstrumentor().instrument()  # Too late!

# ✅ CORRECT ORDER
OpenAIInstrumentor().instrument()  # First!
from langchain_openai import ChatOpenAI
```

**Solution 2:** Verify your API key:

```python
import os
print(os.getenv("HONEYHIVE_API_KEY"))  # Should print your key
```

**Solution 3:** Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code - you'll see trace export logs
```

### Problem: Getting OpenAI API errors

**Make sure OpenAI API key is set:**

```python
import os
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# Or pass to LangChain directly
llm = ChatOpenAI(model="gpt-4", openai_api_key="your_key")
```

### Problem: Instrumentor import error

**Make sure you installed the instrumentor:**

```bash
pip install openinference-instrumentation-openai
```

**Note:** Package name is `openinference-instrumentation-openai`, not `openai-instrumentor`.

---

## Best Practices

### 1. Instrument Early

Always instrument before importing LangChain components:

```python
# Put this at the top of your main file
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(project="my-app")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Now import and use LangChain
from langchain_openai import ChatOpenAI
```

### 2. Use Environment Variables

Set API keys via environment variables instead of hardcoding:

```bash
# .env file
HONEYHIVE_API_KEY=your_honeyhive_key
OPENAI_API_KEY=your_openai_key
```

```python
# Load from .env
from dotenv import load_dotenv
load_dotenv()

# Initialize without passing keys
tracer = HoneyHiveTracer.init()  # Reads from env
```

### 3. One Tracer Per Application

Create a single tracer instance and reuse it:

```python
# tracer.py
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(project="my-app")

# Export for use in other modules
__all__ = ["tracer"]
```

```python
# app.py
from tracer import tracer
from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
```

### 4. Separate Projects by Environment

Use different HoneyHive projects for dev/staging/prod:

```python
import os

env = os.getenv("ENVIRONMENT", "development")
project_name = f"langchain-app-{env}"

tracer = HoneyHiveTracer.init(project=project_name)
# Development: "langchain-app-development"
# Production: "langchain-app-production"
```

---

## Examples Repository

See more examples in our repository:

- [Basic LangChain Integration](../../examples/integrations/langchain_basic.py)
- [Multiple Providers](../../examples/integrations/langchain_multi_provider.py)
- [Chain Example](../../examples/integrations/langchain_chain.py)
- [Streaming Example](../../examples/integrations/langchain_streaming.py)

---

## Further Reading

- [Full Analysis Report](./LANGCHAIN_ANALYSIS_REPORT.md) - Deep technical analysis
- [HoneyHive Documentation](https://docs.honeyhive.ai)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenInference Instrumentors](https://github.com/Arize-ai/openinference)

---

## Support

Questions or issues?

- 📖 [HoneyHive Docs](https://docs.honeyhive.ai)
- 💬 [Community Slack](https://honeyhive.ai/slack)
- 🐛 [Report Issues](https://github.com/honeyhiveai/python-sdk/issues)
- 📧 Email: support@honeyhive.ai

---

**Happy Tracing! 🐝**

