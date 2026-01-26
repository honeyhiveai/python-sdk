# Integration Test Checklist

## Target Providers

| Provider | Test File | Status | Docs Page |
|----------|-----------|--------|-----------|
| OpenAI | `test_openai_integration.py` | ✅ Done (5 tests) | `/integrations/openai.mdx` |
| Anthropic | `test_anthropic_integration.py` | ✅ Done (4 tests) | `/integrations/anthropic.mdx` |
| LangChain | `test_langchain_integration.py` | ✅ Done (3 tests) | `/integrations/langchain.mdx` |
| LangGraph | `test_langchain_integration.py` | ✅ Done (2 tests) | `/integrations/langgraph.mdx` |
| Azure OpenAI | `test_azure_openai_integration.py` | ✅ Done (2 tests) | `/integrations/azure_openai.mdx` |
| AWS Bedrock | `test_bedrock_integration.py` | ✅ Done (3 tests) | `/integrations/aws_bedrock.mdx` |
| Google ADK | `test_google_adk_integration.py` | ✅ Done (2 tests) | `/integrations/google-adk.mdx` |
| AWS Strands | `test_strands_integration.py` | ✅ Done (2 tests) | `/integrations/strands.mdx` |
| Semantic Kernel | `test_semantic_kernel_integration.py` | ✅ Done (2 tests) | `/integrations/semantic-kernel.mdx` |
| Pydantic AI | `test_pydantic_ai_integration.py` | ✅ Done (2 tests) | N/A |
| OpenAI Agents | `test_openai_agents_integration.py` | ✅ Done (2 tests) | N/A |
| AutoGen | `test_autogen_integration.py` | ✅ Done (2 tests) | N/A |
| DSPy | `test_dspy_integration.py` | ✅ Done (3 tests) | N/A |

## Core Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Tracer init | `test_tracing_integration.py` | ✅ Done (3 tests) |
| @trace decorator | `test_tracing_integration.py` | ✅ Done (4 tests) |
| enrich_span | `test_tracing_integration.py` | ✅ Done (3 tests) |
| User Feedback | `test_tracing_integration.py` | ✅ Done (4 tests) |
| User Properties | `test_tracing_integration.py` | ✅ Done (3 tests) |
| Distributed Tracing | `test_tracing_integration.py` | ✅ Done (2 tests) |
| evaluate() | `test_evaluate_integration.py` | ✅ Done (5 tests) |

## Running Tests

```bash
# All integrations
tox -e integrations

# Specific provider
PYTHONPATH=src pytest tests_v2/integrations/test_openai_integration.py -v

# Core tracing only
PYTHONPATH=src pytest tests_v2/integrations/test_tracing_integration.py -v
```

## Required Environment Variables

| Provider | Variables |
|----------|-----------|
| All | `HH_API_KEY`, `HH_PROJECT` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| AWS Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` |
| Google ADK | `GOOGLE_API_KEY` |
