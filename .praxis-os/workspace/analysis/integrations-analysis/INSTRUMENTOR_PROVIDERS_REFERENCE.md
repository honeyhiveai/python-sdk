# HoneyHive BYOI: Instrumentor Providers Reference

**Last Updated:** October 15, 2025  
**Purpose:** Quick reference for the three instrumentor providers supported by HoneyHive's BYOI architecture

---

## Overview

HoneyHive's **Bring Your Own Instrumentor (BYOI)** architecture supports three major OpenTelemetry-based instrumentor providers. When analyzing a new SDK/framework, always check these three providers first before considering custom instrumentation.

---

## Supported Providers

### 1. OpenInference (Arize)

**GitHub:** https://github.com/Arize-ai/openinference  
**Instrumentation Location:** [python/instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation)  
**Stars:** 657+ ⭐  
**Status:** Production/Stable  
**Documentation:** https://docs.arize.com/phoenix  

**Package Naming Convention:**
```
openinference-instrumentation-<sdk-name>
```

**Examples:**
- `openinference-instrumentation-langchain`
- `openinference-instrumentation-openai`
- `openinference-instrumentation-anthropic`
- `openinference-instrumentation-bedrock`
- `openinference-instrumentation-vertexai`

**Usage Pattern:**
```python
from openinference.instrumentation.<sdk> import <SDK>Instrumentor
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(project="my-project")
<SDK>Instrumentor().instrument(tracer_provider=tracer.provider)
```

**Semantic Conventions:** OpenInference-specific conventions  
**Key Features:**
- Explicit tracer_provider injection
- Comprehensive framework coverage
- Well-documented
- Production-grade stability

---

### 2. Traceloop (OpenLLMetry)

**GitHub:** https://github.com/traceloop/openllmetry  
**Instrumentation Location:** [packages](https://github.com/traceloop/openllmetry/tree/main/packages)  
**Stars:** 6.5k+ ⭐  
**Status:** Actively maintained  
**Documentation:** https://www.traceloop.com/docs/openllmetry/getting-started  

**Package Naming Convention:**
```
opentelemetry-instrumentation-<sdk-name>
```

**Examples:**
- `opentelemetry-instrumentation-langchain`
- `opentelemetry-instrumentation-openai`
- `opentelemetry-instrumentation-anthropic`
- `opentelemetry-instrumentation-bedrock`
- `opentelemetry-instrumentation-cohere`

**Usage Pattern:**
```python
from opentelemetry.instrumentation.<sdk> import <SDK>Instrumentor
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(project="my-project")
<SDK>Instrumentor().instrument()  # Uses global tracer provider
```

**Semantic Conventions:** OpenTelemetry AI semantic conventions  
**Key Features:**
- Largest community (6.5k+ stars)
- Extensive provider coverage
- Cost tracking capabilities
- Privacy controls via environment variables

---

### 3. OpenLIT

**GitHub:** https://github.com/openlit/openlit  
**Instrumentation Location:** [sdk/python/src/openlit/instrumentation](https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation)  
**Stars:** 2k+ ⭐  
**Status:** Growing rapidly  
**Documentation:** https://docs.openlit.io/  

**Package Naming Convention:**
```
openlit (single package with multiple instrumentors)
```

**Supported SDKs:**
Check the `openlit/instrumentation/` directory for complete list. Examples:
- LangChain
- OpenAI
- Anthropic
- Cohere
- HuggingFace

**Usage Pattern:**
```python
import openlit
from honeyhive import HoneyHiveTracer

# Option 1: Auto-instrumentation
openlit.init()  # Auto-detects and instruments all supported frameworks

# Option 2: With custom endpoint
openlit.init(otlp_endpoint="http://your-collector-endpoint")

# Note: May need to configure to work with HoneyHive's tracer provider
```

**Semantic Conventions:** OpenTelemetry + custom extensions  
**Key Features:**
- Single package for all instrumentors
- Auto-detection of frameworks
- Simplified initialization
- Built-in observability dashboard

---

## Quick Discovery Checklist

When analyzing a new SDK, check in this order:

### 1. Check GitHub Repositories

```bash
# Clone and search locally
cd /tmp

# OpenInference
git clone --depth 1 https://github.com/Arize-ai/openinference.git
ls openinference/python/instrumentation/ | grep -i <sdk-name>

# Traceloop
git clone --depth 1 https://github.com/traceloop/openllmetry.git
ls openllmetry/packages/ | grep -i <sdk-name>

# OpenLIT
git clone --depth 1 https://github.com/openlit/openlit.git
ls openlit/sdk/python/src/openlit/instrumentation/ | grep -i <sdk-name>
```

### 2. Search PyPI

```bash
# OpenInference
pip index versions openinference-instrumentation-<sdk-name>

# Traceloop
pip index versions opentelemetry-instrumentation-<sdk-name>

# OpenLIT (check docs for supported frameworks)
pip show openlit
```

### 3. Web Search

Use these search queries:
```
"openinference-instrumentation-<sdk-name>"
"opentelemetry-instrumentation-<sdk-name>"
"openlit <sdk-name> instrumentation"
"honeyhive byoi <sdk-name>"
```

---

## Comparison Matrix

| Feature | OpenInference | Traceloop | OpenLIT |
|---------|---------------|-----------|---------|
| **Stars** | 657+ | 6.5k+ | 2k+ |
| **Package per SDK** | ✅ Yes | ✅ Yes | ❌ Single package |
| **Tracer Provider** | Explicit injection | Global provider | Custom init |
| **Semantic Conventions** | OpenInference | OTel AI | OTel + custom |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Community** | Growing | Largest | Emerging |
| **HoneyHive Compatibility** | ✅ Excellent | ✅ Excellent | ⚠️ Needs testing |

---

## Integration Examples

### Example 1: LangChain (All Three Providers)

**OpenInference:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.langchain import LangChainInstrumentor

tracer = HoneyHiveTracer.init(project="langchain-app")
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# Use LangChain normally - automatically traced
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
result = llm.invoke("Hello world")
```

**Traceloop:**
```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

tracer = HoneyHiveTracer.init(project="langchain-app")
LangchainInstrumentor().instrument()

# Use LangChain normally - automatically traced
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
result = llm.invoke("Hello world")
```

**OpenLIT:**
```python
import openlit

openlit.init()  # Auto-instruments LangChain if detected

# Use LangChain normally - automatically traced
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
result = llm.invoke("Hello world")
```

### Example 2: Multiple Providers

You can use instrumentors from different providers simultaneously:

```python
from honeyhive import HoneyHiveTracer

# Initialize HoneyHive
tracer = HoneyHiveTracer.init(project="multi-provider")

# OpenInference for LangChain
from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# Traceloop for Anthropic (if OpenInference doesn't have it)
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
AnthropicInstrumentor().instrument()

# All frameworks now traced!
```

---

## Decision Tree

```
New SDK to instrument?
│
├─ Check OpenInference GitHub
│  ├─ Found? → Use openinference-instrumentation-<sdk>
│  └─ Not found? → Continue
│
├─ Check Traceloop GitHub
│  ├─ Found? → Use opentelemetry-instrumentation-<sdk>
│  └─ Not found? → Continue
│
├─ Check OpenLIT docs
│  ├─ Supported? → Use openlit.init()
│  └─ Not supported? → Continue
│
└─ No instrumentor found
   └─ Follow SDK_ANALYSIS_METHODOLOGY.md Phase 2+
      (Custom instrumentation required)
```

---

## Testing New Instrumentors

When you find an instrumentor, test it with HoneyHive:

```python
# test_instrumentor.py
import os
from honeyhive import HoneyHiveTracer

# Set credentials
os.environ["HONEYHIVE_API_KEY"] = "your_key"
os.environ["OPENAI_API_KEY"] = "your_openai_key"  # or other provider

def test_instrumentor():
    # Initialize HoneyHive
    tracer = HoneyHiveTracer.init(project="test-instrumentor")
    
    # Initialize instrumentor (adjust based on provider)
    from openinference.instrumentation.<sdk> import <SDK>Instrumentor
    <SDK>Instrumentor().instrument(tracer_provider=tracer.provider)
    
    # Test basic functionality
    # ... SDK-specific code here ...
    
    # Check HoneyHive dashboard for traces
    print("✅ Test complete - check HoneyHive dashboard")

if __name__ == "__main__":
    test_instrumentor()
```

---

## Troubleshooting

### Issue: Instrumentor not capturing traces

**Solutions:**
1. Verify instrumentor is called BEFORE importing the SDK
2. Check that tracer_provider is correctly passed
3. Ensure HoneyHive tracer is initialized
4. Check for conflicting instrumentors

### Issue: Which provider to choose?

**Decision criteria:**
1. **Stability:** OpenInference (Production/Stable)
2. **Community:** Traceloop (Largest, 6.5k+ stars)
3. **Simplicity:** OpenLIT (Single package, auto-detection)
4. **SDK support:** Check which provider has the instrumentor

**Recommendation:** Try OpenInference first, then Traceloop, then OpenLIT.

---

## Maintenance

This reference should be updated when:
- New instrumentor providers emerge
- Provider GitHub locations change
- Package naming conventions change
- New SDK instrumentors are added

**Last verified:** October 15, 2025

---

## Related Documents

- [SDK_ANALYSIS_METHODOLOGY.md](./SDK_ANALYSIS_METHODOLOGY.md) - Complete analysis methodology
- [LANGCHAIN_ANALYSIS_CORRECTION.md](./LANGCHAIN_ANALYSIS_CORRECTION.md) - LangChain case study
- HoneyHive BYOI Architecture docs - (internal)

---

## Quick Command Reference

```bash
# Check all providers for a specific SDK
SDK="langchain"  # Change this

echo "Checking OpenInference..."
git ls-remote --heads https://github.com/Arize-ai/openinference | grep -q . && \
  curl -s "https://api.github.com/repos/Arize-ai/openinference/git/trees/main?recursive=1" | \
  grep "instrumentation-${SDK}"

echo "Checking Traceloop..."
curl -s "https://api.github.com/repos/traceloop/openllmetry/git/trees/main?recursive=1" | \
  grep "instrumentation-${SDK}"

echo "Checking OpenLIT..."
curl -s "https://api.github.com/repos/openlit/openlit/git/trees/main?recursive=1" | \
  grep "instrumentation.*${SDK}"

echo "Checking PyPI..."
pip index versions "openinference-instrumentation-${SDK}" 2>/dev/null
pip index versions "opentelemetry-instrumentation-${SDK}" 2>/dev/null
```

---

**Need help?** Consult the full [SDK_ANALYSIS_METHODOLOGY.md](./SDK_ANALYSIS_METHODOLOGY.md) Phase 1.5 for detailed instructions.

