# HoneyHive Model Provider Compatibility Matrix

This directory contains test implementations for various model providers using OpenInference instrumentors with the HoneyHive SDK.

## Overview

The compatibility matrix tests demonstrate how HoneyHive integrates with different model providers through OpenInference instrumentation. Each test file shows the "Bring Your Own Instrumentor" pattern where users can integrate their preferred provider's instrumentor with HoneyHive's OpenTelemetry-based tracing.

## Test Structure

Each test file follows this pattern:
1. **Initialize HoneyHive Tracer** - Set up HoneyHive with OpenTelemetry
2. **Configure OpenInference Instrumentor** - Initialize the provider-specific instrumentor
3. **Integrate Instrumentor** - Pass instrumentor to HoneyHive via the `instrumentors` parameter
4. **Execute Test Calls** - Make API calls to verify tracing works
5. **Validate Traces** - Ensure spans are captured and enriched

## Available Tests

### Direct Provider Support
- `test_openai.py` - OpenAI models (GPT-4, GPT-3.5)
- `test_azure_openai.py` - Azure-hosted OpenAI models
- `test_anthropic.py` - Anthropic Claude models
- `test_cohere.py` - Cohere language models
- `test_google_vertexai.py` - Google Cloud Vertex AI
- `test_google_genai.py` - Google Generative AI (Gemini)

### AWS Ecosystem
- `test_aws_bedrock.py` - AWS Bedrock (multiple model families)

### Framework Integration
- `test_langchain.py` - LangChain orchestration framework
- `test_llamaindex.py` - LlamaIndex data framework
- `test_dspy.py` - DSPy programming framework

### Specialized Platforms
- `test_groq.py` - Groq inference platform
- `test_mistralai.py` - Mistral AI models
- `test_ollama.py` - Ollama local models

### Open Source & Self-Hosted
- `test_huggingface.py` - Hugging Face Transformers
- `test_litellm.py` - LiteLLM proxy

## Running Tests

### Prerequisites
```bash
# Install base dependencies
pip install honeyhive[opentelemetry]

# Install provider-specific packages (as needed)
pip install openai anthropic cohere
pip install google-cloud-aiplatform google-generativeai
pip install boto3 langchain llama-index
```

### Run Individual Tests
```bash
# Test specific provider
python tests/compatibility_matrix/test_openai.py

# Test with environment variables
HH_API_KEY=your_key HH_PROJECT=test python tests/compatibility_matrix/test_openai.py
```

### Run Full Compatibility Suite
```bash
# Run all compatibility tests
python tests/compatibility_matrix/run_compatibility_tests.py

# Generate compatibility matrix report
python tests/compatibility_matrix/generate_matrix.py
```

## Environment Variables

Each test requires appropriate environment variables:

```bash
# HoneyHive Configuration
export HH_API_KEY="your_honeyhive_api_key"
export HH_PROJECT="your_project_name"

# Provider API Keys (as needed)
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export COHERE_API_KEY="your_cohere_key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"

# AWS Configuration
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

## Compatibility Matrix Results

| Provider | OpenInference Instrumentor | HoneyHive Integration | Status | Notes |
|----------|----------------------------|----------------------|---------|-------|
| OpenAI | `openinference-instrumentation-openai` | ✅ Full Support | Tested | GPT-4, GPT-3.5, embeddings |
| Azure OpenAI | `openinference-instrumentation-openai` | ✅ Full Support | Tested | Same as OpenAI with Azure endpoints |
| Anthropic | `openinference-instrumentation-anthropic` | ✅ Full Support | Tested | Claude models |
| Google Vertex AI | `openinference-instrumentation-vertexai` | ✅ Full Support | Tested | PaLM, Gemini via Vertex |
| Google Generative AI | `openinference-instrumentation-google-generativeai` | ✅ Full Support | Tested | Direct Gemini API |
| AWS Bedrock | `openinference-instrumentation-bedrock` | ✅ Full Support | Tested | Multi-model support |
| Cohere | `openinference-instrumentation-cohere` | ✅ Full Support | Tested | Command models |
| LangChain | `openinference-instrumentation-langchain` | ✅ Full Support | Tested | Any LangChain-supported provider |
| LlamaIndex | `openinference-instrumentation-llama-index` | ✅ Full Support | Tested | RAG and data frameworks |
| DSPy | `openinference-instrumentation-dspy` | ✅ Full Support | Tested | Programming framework |
| Hugging Face | `openinference-instrumentation-huggingface` | ✅ Full Support | Tested | Transformers library |
| Mistral AI | `openinference-instrumentation-mistralai` | ✅ Full Support | Tested | Mistral models |
| Groq | `openinference-instrumentation-groq` | ✅ Full Support | Tested | Fast inference |
| Ollama | `openinference-instrumentation-ollama` | ✅ Full Support | Tested | Local model serving |
| LiteLLM | `openinference-instrumentation-litellm` | ✅ Full Support | Tested | Multi-provider proxy |

## Architecture

The compatibility tests demonstrate HoneyHive's **"Bring Your Own Instrumentor"** architecture:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# 1. Initialize instrumentor
openai_instrumentor = OpenAIInstrumentor()

# 2. Pass to HoneyHive during initialization
tracer = HoneyHiveTracer.init(
    api_key="your_key",
    project="your_project",
    instrumentors=[openai_instrumentor]  # <-- Integration point
)

# 3. Use provider normally - tracing happens automatically
client = OpenAI()
response = client.chat.completions.create(...)  # <-- Automatically traced
```

## Benefits

1. **Provider Agnostic** - Works with any OpenInference-supported provider
2. **Future Proof** - New OpenInference instrumentors work automatically
3. **Standard Compliant** - Uses OpenTelemetry standards
4. **Minimal Changes** - Existing provider code requires minimal modification
5. **Rich Traces** - Captures input/output, metadata, and performance metrics
