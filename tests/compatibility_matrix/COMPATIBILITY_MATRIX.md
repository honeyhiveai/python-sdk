# HoneyHive Model Provider Compatibility Matrix

*Generated on: 2025-08-29 18:05:35*

This document provides a comprehensive mapping of model providers supported by HoneyHive through
OpenInference instrumentation, demonstrating the **'Bring Your Own Instrumentor'** architecture.

## Architecture Overview

HoneyHive integrates with model providers through OpenInference instrumentors:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# 1. Initialize instrumentor
instrumentor = OpenAIInstrumentor()

# 2. Pass to HoneyHive during initialization
tracer = HoneyHiveTracer.init(
    api_key='your_key',
    project='your_project',
    instrumentors=[instrumentor]  # <-- Integration point
)

# 3. Use provider normally - tracing happens automatically
client = OpenAI()
response = client.chat.completions.create(...)  # <-- Automatically traced
```

## Direct Provider Support

| Provider | Models | Instrumentor | Integration | Test File | Notes |
|----------|---------|-------------|-------------|-----------|-------|
| **OpenAI** | GPT-4, GPT-3.5-turbo, embeddings | `openinference-instrumentation-openai` | ✅ Full Support | `test_openai.py` | Complete chat, completion, and embedding support |
| **Azure OpenAI** | Same as OpenAI via Azure endpoints | `openinference-instrumentation-openai` | ✅ Full Support | `test_azure_openai.py` | Enterprise Azure-hosted OpenAI models |
| **Anthropic** | Claude 3, Claude 2, Claude Instant | `openinference-instrumentation-anthropic` | ✅ Full Support | `test_anthropic.py` | Messages API and legacy completions |
| **Cohere** | Command, Embed, Classify, Summarize | `openinference-instrumentation-cohere` | ✅ Full Support | `test_cohere.py` | Generation, embeddings, classification, reranking |
| **Google Vertex AI** | PaLM, Gemini, Codey, Embedding | `openinference-instrumentation-vertexai` | ✅ Full Support | `test_google_vertexai.py` | Google Cloud managed AI platform |
| **Google Generative AI (Gemini)** | Gemini Pro, Gemini Pro Vision | `openinference-instrumentation-google-generativeai` | ✅ Full Support | `test_google_genai.py` | Direct Google AI Studio API access |

## AWS Ecosystem

| Provider | Models | Instrumentor | Integration | Test File | Notes |
|----------|---------|-------------|-------------|-----------|-------|
| **AWS Bedrock** | Claude, Titan, Cohere, AI21, Stability AI | `openinference-instrumentation-bedrock` | ✅ Full Support | `test_aws_bedrock.py` | Multi-model AWS managed service |

## Framework Integration

| Provider | Models | Instrumentor | Integration | Test File | Notes |
|----------|---------|-------------|-------------|-----------|-------|
| **LangChain** | Any LangChain-supported provider | `openinference-instrumentation-langchain` | ✅ Full Support | `test_langchain.py` | Chains, agents, tools, and RAG pipelines |
| **LlamaIndex** | Any LlamaIndex-supported provider | `openinference-instrumentation-llama-index` | ✅ Full Support | `test_llama_index.py` | RAG, indexing, query engines, chat engines |
| **DSPy** | Any DSPy-supported provider | `openinference-instrumentation-dspy` | ✅ Full Support | `test_dspy.py` | Programming framework for LM pipelines |

## Specialized Platforms

| Provider | Models | Instrumentor | Integration | Test File | Notes |
|----------|---------|-------------|-------------|-----------|-------|
| **Groq** | Llama, Mixtral (fast inference) | `openinference-instrumentation-groq` | ✅ Full Support | `test_groq.py` | Ultra-fast inference with custom chips |
| **Mistral AI** | Mistral 7B, Mixtral, Mistral Small/Large | `openinference-instrumentation-mistralai` | ✅ Full Support | `test_mistralai.py` | European AI company, open models |
| **Ollama** | Local Llama, Mistral, CodeLlama, etc. | `openinference-instrumentation-ollama` | ✅ Full Support | `test_ollama.py` | Local model serving, privacy-focused |

## Open Source & Self-Hosted

| Provider | Models | Instrumentor | Integration | Test File | Notes |
|----------|---------|-------------|-------------|-----------|-------|
| **Hugging Face Transformers** | Thousands of open-source models | `openinference-instrumentation-huggingface` | ✅ Full Support | `test_huggingface.py` | Pipelines, direct model usage, custom models |
| **LiteLLM** | Multi-provider proxy (100+ models) | `openinference-instrumentation-litellm` | ✅ Full Support | `test_litellm.py` | Unified API, cost tracking, fallbacks |

## Summary

- **Total Providers**: 15
- **Categories**: 5
- **Integration Status**: All providers have full OpenTelemetry-based tracing support
- **Architecture**: 'Bring Your Own Instrumentor' pattern

## Testing

### Run All Tests
```bash
# Install dependencies
pip install -r tests/compatibility_matrix/requirements.txt

# Set environment variables (see env.example)
export HH_API_KEY='your_honeyhive_api_key'
export HH_PROJECT='your_project'
export OPENAI_API_KEY='your_openai_key'
# ... other provider keys ...

# Run compatibility test suite
python tests/compatibility_matrix/run_compatibility_tests.py
```

### Run Individual Tests
```bash
# Test specific provider
python tests/compatibility_matrix/test_openai.py
python tests/compatibility_matrix/test_anthropic.py
python tests/compatibility_matrix/test_langchain.py
```

## Benefits of This Architecture

1. **Provider Agnostic**: Works with any OpenInference-supported provider
2. **Future Proof**: New OpenInference instrumentors work automatically
3. **Standard Compliant**: Uses OpenTelemetry standards
4. **Minimal Changes**: Existing provider code requires minimal modification
5. **Rich Traces**: Captures input/output, metadata, and performance metrics
6. **Extensible**: Easy to add new providers as OpenInference support grows

## Provider-Specific Notes

### Cloud Providers
- **OpenAI/Azure OpenAI**: Most mature integration, supports all features
- **AWS Bedrock**: Multi-model support, handles different model APIs seamlessly
- **Google Cloud**: Both Vertex AI and direct Generative AI APIs supported

### Framework Integration
- **LangChain**: Traces chains, agents, tools, and complex workflows
- **LlamaIndex**: Comprehensive RAG pipeline tracing and optimization
- **DSPy**: Advanced LM programming patterns and optimization

### Specialized Platforms
- **Groq**: Ultra-fast inference monitoring for performance-critical apps
- **Ollama**: Local deployment monitoring for privacy-sensitive applications
- **LiteLLM**: Multi-provider abstraction with cost tracking
