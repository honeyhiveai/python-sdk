# LLM Provider Integration Examples

This directory contains examples for integrating HoneyHive with various LLM providers using the BYOI (Bring Your Own Instrumentor) architecture.

## 🔧 **Integration Types**

### **OpenInference Instrumentors**
Lightweight, community-driven instrumentors following OpenTelemetry standards:

- **[`openinference_openai_example.py`](openinference_openai_example.py)** - OpenAI integration
- **[`openinference_anthropic_example.py`](openinference_anthropic_example.py)** - Anthropic integration  
- **[`openinference_google_ai_example.py`](openinference_google_ai_example.py)** - Google AI integration
- **[`openinference_google_adk_example.py`](openinference_google_adk_example.py)** - Google Agent Development Kit
- **[`openinference_bedrock_example.py`](openinference_bedrock_example.py)** - AWS Bedrock integration
- **[`openinference_mcp_example.py`](openinference_mcp_example.py)** - MCP (Model Context Protocol) integration

### **Traceloop Instrumentors**
Enhanced instrumentors with production optimizations and extended metrics:

- **[`traceloop_openai_example.py`](traceloop_openai_example.py)** - OpenAI integration
- **[`traceloop_anthropic_example.py`](traceloop_anthropic_example.py)** - Anthropic integration
- **[`traceloop_bedrock_example.py`](traceloop_bedrock_example.py)** - AWS Bedrock integration (✅ multi-model support)
- **[`traceloop_azure_openai_example.py`](traceloop_azure_openai_example.py)** - Azure OpenAI integration (✅ multi-deployment support)
- **[`traceloop_mcp_example.py`](traceloop_mcp_example.py)** - MCP integration (✅ tool orchestration)
- **[`traceloop_google_ai_example.py`](traceloop_google_ai_example.py)** - Google AI integration (⚠️ upstream issue)
- **[`traceloop_google_ai_example_with_workaround.py`](traceloop_google_ai_example_with_workaround.py)** - Google AI with workaround (✅ functional)

## 🚀 **Quick Start**

1. **Choose Your Instrumentor**: OpenInference (lightweight) or Traceloop (enhanced)
2. **Install Dependencies**: Each example includes specific requirements
3. **Set Environment Variables**: API keys and configuration
4. **Run Example**: `python integrations/[example_name].py`

## 📖 **Documentation**

For detailed integration guides, see:
- **[How-To Guides](../../docs/how-to/integrations/)** - Step-by-step integration instructions
- **[Compatibility Matrix](../../docs/explanation/)** - Full compatibility and version support
- **[BYOI Architecture](../../docs/explanation/architecture/)** - Technical architecture details

## 🎯 **Integration Pattern**

All examples follow the standard HoneyHive integration pattern:

```python
from honeyhive import HoneyHiveTracer

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    source="production"
)

# Install your chosen instrumentor
# Your LLM calls are automatically traced!
```

**Choose the integration that best fits your needs!** 🚀
