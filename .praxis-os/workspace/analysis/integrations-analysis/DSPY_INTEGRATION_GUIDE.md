# HoneyHive + DSPy Integration Guide

**Last Updated:** 2025-10-15  
**DSPy Version:** 3.0.4b1+  
**HoneyHive SDK:** Compatible with BYOI architecture  
**Difficulty:** Medium  
**Estimated Setup Time:** 15-30 minutes

---

## Overview

This guide shows you how to integrate HoneyHive observability with DSPy applications using DSPy's native callback system.

### What Gets Traced

When you integrate HoneyHive with DSPy, you automatically capture:

- ✅ All language model calls (prompts, completions, tokens, cost)
- ✅ DSPy module executions (ChainOfThought, ReAct, etc.)
- ✅ Adapter operations (JSON, XML formatting/parsing)
- ✅ Tool calls
- ✅ Evaluation metrics
- ✅ Complete execution hierarchy
- ✅ Error and exception tracking

### Prerequisites

- Python 3.10 or higher
- DSPy installed (`pip install dspy`)
- HoneyHive SDK installed (`pip install honeyhive`)
- HoneyHive API key ([get one here](https://app.honeyhive.ai))

---

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install dspy honeyhive
```

### 2. Set Up Environment

```bash
# Set your HoneyHive API key
export HONEYHIVE_API_KEY="your-api-key-here"

# Set your OpenAI API key (or other LLM provider)
export OPENAI_API_KEY="your-openai-key-here"
```

### 3. Create a Traced DSPy Application

```python
import os
import dspy
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    project="my-dspy-project",
    api_key=os.getenv("HONEYHIVE_API_KEY"),
    source="dspy-quickstart"
)

# Create HoneyHive callback
callback = HoneyHiveCallback(tracer)

# Configure DSPy with HoneyHive tracing
dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    callbacks=[callback]
)

# Use DSPy normally - everything is automatically traced!
cot = dspy.ChainOfThought("question -> answer")
result = cot(question="What is the capital of France?")
print(result.answer)

# Check your HoneyHive dashboard to see the trace!
```

**That's it!** 🎉 All DSPy operations are now being traced to HoneyHive.

---

## Configuration Options

### Global Configuration (Recommended)

Configure HoneyHive tracing once, applies to all DSPy modules:

```python
import dspy
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

# Initialize once
tracer = HoneyHiveTracer.init(project="my-project", api_key="...")
callback = HoneyHiveCallback(tracer)

# Configure globally
dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    callbacks=[callback]
)

# All modules automatically traced
module1 = dspy.ChainOfThought("q -> a")
module2 = dspy.ReAct("task -> result")
module1(q="Question 1")  # Traced
module2(task="Task 1")    # Traced
```

### Per-Module Configuration

Configure tracing for specific modules only:

```python
import dspy
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

tracer = HoneyHiveTracer.init(project="my-project", api_key="...")
callback = HoneyHiveCallback(tracer)

# Configure DSPy without global callbacks
dspy.settings.configure(lm=dspy.LM("openai/gpt-4o-mini"))

# Only trace specific modules
traced_module = dspy.ChainOfThought(
    "question -> answer",
    callbacks=[callback]
)

untraced_module = dspy.ChainOfThought("question -> answer")

traced_module(question="Q1")    # ✅ Traced
untraced_module(question="Q2")  # ❌ Not traced
```

---

## Common Patterns

### Pattern 1: RAG Pipeline with DSPy

```python
import dspy
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

# Initialize tracing
tracer = HoneyHiveTracer.init(project="rag-demo", api_key="...")
callback = HoneyHiveCallback(tracer)

# Configure DSPy with retriever
dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    rm=dspy.ColBERTv2(url="http://localhost:8893"),
    callbacks=[callback]
)

# Define RAG module
class RAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)
        self.generate = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

# Use it - retrieval + generation both traced
rag = RAG()
result = rag(question="What is DSPy?")
print(result.answer)

# In HoneyHive, you'll see:
# - RAG module span (parent)
#   - Retrieve operation
#   - ChainOfThought module
#     - LM call with context and question
```

### Pattern 2: Multi-Agent System

```python
import dspy
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

tracer = HoneyHiveTracer.init(project="multi-agent", api_key="...")
callback = HoneyHiveCallback(tracer)

dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    callbacks=[callback]
)

# Define specialized agents
class ResearchAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.research = dspy.ChainOfThought("topic -> findings")
    
    def forward(self, topic):
        return self.research(topic=topic)

class WriterAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.write = dspy.ChainOfThought("findings -> article")
    
    def forward(self, findings):
        return self.write(findings=findings)

# Orchestrator
class MultiAgentSystem(dspy.Module):
    def __init__(self):
        super().__init__()
        self.researcher = ResearchAgent()
        self.writer = WriterAgent()
    
    def forward(self, topic):
        findings = self.researcher(topic=topic)
        article = self.writer(findings=findings.findings)
        return article

# Run multi-agent system - all operations traced with hierarchy
system = MultiAgentSystem()
result = system(topic="Quantum Computing")
print(result.article)

# HoneyHive shows complete execution tree:
# - MultiAgentSystem
#   - ResearchAgent
#     - ChainOfThought (research)
#       - LM call
#   - WriterAgent
#     - ChainOfThought (write)
#       - LM call
```

---

## Best Practices

### 1. Use Global Configuration for Simplicity

```python
# ✅ Good: Configure once, trace everything
dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    callbacks=[HoneyHiveCallback(tracer)]
)

# ❌ Bad: Configure per-module (tedious and error-prone)
module1 = dspy.ChainOfThought("q -> a", callbacks=[callback])
module2 = dspy.ReAct("task -> result", callbacks=[callback])
```

### 2. Use Environment Variables for Configuration

```python
# ✅ Good: Environment-based configuration
import os
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

tracer = HoneyHiveTracer.init(
    project=os.getenv("HONEYHIVE_PROJECT", "default"),
    api_key=os.getenv("HONEYHIVE_API_KEY"),
    source=os.getenv("ENV", "development")
)

# ❌ Bad: Hardcoded API keys
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="sk-..."  # Don't hardcode!
)
```

### 3. Use Privacy Mode for Sensitive Data

```python
# For applications handling sensitive data
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

callback = HoneyHiveCallback(
    tracer=tracer,
    capture_inputs=False,   # Don't log user inputs
    capture_outputs=False   # Don't log model outputs
)

# Still captures:
# - Model names and parameters
# - Token usage and cost
# - Latency and timing
# - Error rates
# - Module hierarchy
```

---

## Troubleshooting

### Issue: No traces appearing in HoneyHive

**Possible causes:**
1. API key not set or incorrect
2. Callback not configured properly
3. Network connectivity issues

**Solutions:**
```python
# Verify API key
import os
print(f"API Key set: {bool(os.getenv('HONEYHIVE_API_KEY'))}")

# Verify callback is configured
import dspy
print(f"Global callbacks: {dspy.settings.get('callbacks', [])}")

# Test HoneyHive connection
from honeyhive import HoneyHiveTracer
tracer = HoneyHiveTracer.init(project="test", api_key="...")
with tracer.trace("test-span"):
    print("If this works, HoneyHive connection is OK")
```

### Issue: Sensitive data in traces

**Solution:** Use privacy mode
```python
from honeyhive.integrations.dspy_callback import HoneyHiveCallback

# Don't capture inputs/outputs
private_callback = HoneyHiveCallback(
    tracer=tracer,
    capture_inputs=False,
    capture_outputs=False
)

dspy.settings.configure(callbacks=[private_callback])
```

---

## FAQ

### Q: Do I need to change my existing DSPy code?

**A:** No! Just add 3 lines to configure HoneyHive callback. All existing code works unchanged.

### Q: Does this work with all LLM providers?

**A:** Yes! DSPy uses LiteLLM which supports 100+ providers. HoneyHive tracing works with all of them.

### Q: Can I use this in production?

**A:** Yes! The callback system has minimal overhead (<1% latency) and is designed for production use.

### Q: What about sensitive data?

**A:** Use privacy mode to disable input/output capture while still getting metrics and metadata.

### Q: Does this work with DSPy optimizers?

**A:** Yes! All LM calls during optimization are traced. Optimizer-level spans aren't exposed via callbacks, but you'll see all the underlying LM calls.

---

## Additional Resources

- **DSPy Documentation:** https://dspy.ai
- **HoneyHive Documentation:** https://docs.honeyhive.ai
- **DSPy GitHub:** https://github.com/stanfordnlp/dspy
- **HoneyHive Dashboard:** https://app.honeyhive.ai

---

**Happy Tracing!** 🐝🔍

