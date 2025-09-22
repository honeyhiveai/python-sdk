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

**Naming Pattern**: `test_<instrumentor>_<provider>.py`

### OpenInference Instrumentor Tests
- `test_openinference_openai.py` - OpenAI models (GPT-4, GPT-3.5)
- `test_openinference_azure_openai.py` - Azure-hosted OpenAI models
- `test_openinference_anthropic.py` - Anthropic Claude models
- `test_openinference_google_ai.py` - Google Generative AI (Gemini)
- `test_openinference_google_adk.py` - Google Agent Development Kit
- `test_openinference_bedrock.py` - AWS Bedrock (multiple model families)
- `test_openinference_mcp.py` - Model Context Protocol

### Traceloop (OpenLLMetry) Instrumentor Tests
- `test_traceloop_openai.py` - OpenAI models with enhanced metrics
- `test_traceloop_azure_openai.py` - Azure OpenAI with enhanced metrics
- `test_traceloop_anthropic.py` - Anthropic Claude with enhanced metrics
- `test_traceloop_google_ai.py` - Google AI with enhanced metrics
- `test_traceloop_bedrock.py` - AWS Bedrock with enhanced metrics
- `test_traceloop_mcp.py` - MCP with enhanced metrics

### Framework Integration Tests
- `test_strands_integration.py` - AWS Strands agent framework integration

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
# Test specific provider with OpenInference
python tests/compatibility_matrix/test_openinference_openai.py

# Test specific provider with Traceloop
python tests/compatibility_matrix/test_traceloop_openai.py

# Test with environment variables
HH_API_KEY=your_key HH_PROJECT=test python tests/compatibility_matrix/test_openinference_openai.py
```

### Run Full Compatibility Suite
```bash
# Run all compatibility tests
python tests/compatibility_matrix/run_compatibility_tests.py

# Generate Python version compatibility matrix report
python tests/compatibility_matrix/generate_version_matrix.py
```

## Environment Variables

Each test requires appropriate environment variables. See `env.example` for a complete template.

### Required for All Tests
```bash
# HoneyHive Configuration
export HH_API_KEY="your_honeyhive_api_key"
export HH_PROJECT="your_project_name"
```

### Provider-Specific Variables
```bash
# OpenAI (Required for: OpenAI tests)
export OPENAI_API_KEY="your_openai_key"

# Anthropic (Required for: Anthropic tests)
export ANTHROPIC_API_KEY="your_anthropic_key"

# Google AI (Required for: Google Generative AI tests)
export GOOGLE_API_KEY="your_google_ai_studio_api_key"

# Google ADK (Required for: Google Agent Development Kit tests)
export GOOGLE_ADK_API_KEY="your_google_adk_api_key"

# Azure OpenAI (Required for: Azure OpenAI tests)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"  # Optional
export AZURE_OPENAI_DEPLOYMENT="gpt-35-turbo"  # Optional
export AZURE_OPENAI_GPT4_DEPLOYMENT="gpt-4"  # Optional

# AWS (Required for: Bedrock tests)
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export AWS_DEFAULT_REGION="us-east-1"

# Google Cloud (Required for: Vertex AI tests - currently not implemented)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
export GCP_PROJECT="your_gcp_project_id"
export GCP_REGION="us-central1"
```

### Using .env File
The test runner automatically loads variables from a `.env` file in the project root:

```bash
# Copy the example file
cp tests/compatibility_matrix/env.example .env

# Edit with your actual credentials
vim .env
```

## Compatibility Matrix Results

### Currently Implemented Tests

| Provider | Instrumentor Category | Test File | Status | Notes |
|----------|----------------------|-----------|---------|-------|
| **OpenAI** | OpenInference | `test_openinference_openai.py` | ✅ Implemented | GPT-4, GPT-3.5, embeddings |
| **OpenAI** | Traceloop | `test_traceloop_openai.py` | ✅ Implemented | Enhanced metrics |
| **Azure OpenAI** | OpenInference | `test_openinference_azure_openai.py` | ✅ Implemented | Azure-hosted OpenAI |
| **Azure OpenAI** | Traceloop | `test_traceloop_azure_openai.py` | ✅ Implemented | Enhanced metrics |
| **Anthropic** | OpenInference | `test_openinference_anthropic.py` | ✅ Implemented | Claude models |
| **Anthropic** | Traceloop | `test_traceloop_anthropic.py` | ✅ Implemented | Enhanced metrics |
| **Google AI** | OpenInference | `test_openinference_google_ai.py` | ✅ Implemented | Gemini models |
| **Google AI** | Traceloop | `test_traceloop_google_ai.py` | ✅ Implemented | Enhanced metrics |
| **Google ADK** | OpenInference | `test_openinference_google_adk.py` | ✅ Implemented | Agent Development Kit |
| **AWS Bedrock** | OpenInference | `test_openinference_bedrock.py` | ✅ Implemented | Multi-model support |
| **AWS Bedrock** | Traceloop | `test_traceloop_bedrock.py` | ✅ Implemented | Enhanced metrics |
| **Model Context Protocol** | OpenInference | `test_openinference_mcp.py` | ✅ Implemented | MCP integration |
| **Model Context Protocol** | Traceloop | `test_traceloop_mcp.py` | ✅ Implemented | Enhanced metrics |
| **AWS Strands** | Framework | `test_strands_integration.py` | ✅ Implemented | Agent framework integration |

### Python Version Compatibility

| Python Version | HoneyHive SDK | OpenInference Core | Traceloop SDK | Notes |
|----------------|---------------|-------------------|---------------|-------|
| **3.11** | ✅ Supported | ✅ Compatible | ✅ Compatible | Minimum version |
| **3.12** | ✅ Supported | ✅ Compatible | ✅ Compatible | Recommended |
| **3.13** | ✅ Supported | ✅ Compatible | ✅ Compatible | Latest |

### Provider Onboarding Status

**Currently Supported (11 instrumentors)**: All providers listed above have completed the HoneyHive onboarding process and are officially supported.

**Implementation Details**: We run 13 tests total because Azure OpenAI reuses the same instrumentors as regular OpenAI but requires separate endpoint testing.

**Not Yet Onboarded**: Other providers (Cohere, Vertex AI, LangChain, LlamaIndex, DSPy, Hugging Face, Mistral AI, Groq, Ollama, LiteLLM) have not completed the official onboarding process and are not included in compatibility testing.

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

## Dynamic Generation System

The compatibility matrix uses **dynamic generation** to automatically discover instrumentors and providers from test configurations, significantly reducing maintenance burden.

### How It Works

1. **Single Source of Truth**: Both generators read from `run_compatibility_tests.py`'s `test_configs` dictionary
2. **Automatic Discovery**: Instrumentors are automatically categorized as OpenInference or OpenTelemetry
3. **Consistent Formatting**: All entries follow the same structure and formatting rules
4. **Fallback Safety**: If dynamic loading fails, generators fall back to minimal static data

### Adding New Providers

**Old Process (Manual)**:
```bash
# Required updates for each new provider:
1. Add test file: test_openinference_newprovider.py
2. Update run_compatibility_tests.py test_configs
3. Update generate_version_matrix.py instrumentor list
4. Update README.md provider count
```

**New Process (Automatic)**:
```bash
# Only required updates:
1. Add test file: test_openinference_newprovider.py
2. Update run_compatibility_tests.py test_configs

# Everything else updates automatically! 🎉
```

### Benefits of Dynamic Generation

- **✅ Reduced Maintenance**: Only update test configs when adding providers
- **✅ Consistency Guaranteed**: Single source of truth ensures consistency
- **✅ Future-Proof**: Documentation automatically reflects current tests

### Validation

```bash
# Test version matrix generation
python tests/compatibility_matrix/generate_version_matrix.py

# Should show current instrumentor counts:
# - 11 total instrumentors (6 OpenInference + 5 OpenTelemetry)
```
