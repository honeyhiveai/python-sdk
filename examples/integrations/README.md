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

### **Agent Framework Integrations**
Comprehensive examples for popular AI agent frameworks:

- **[`openai_agents_integration.py`](openai_agents_integration.py)** - OpenAI Agents SDK with OpenInference instrumentor (✅ multi-agent, handoffs, guardrails, tools)
- **[`semantic_kernel_integration.py`](semantic_kernel_integration.py)** - Microsoft Semantic Kernel with OpenAI instrumentor (✅ agents, plugins, function calling, streaming)
- **[`strands_integration.py`](strands_integration.py)** - AWS Strands with TracerProvider pattern (✅ Bedrock models, streaming, tools)

## 🚀 **Quick Start**

### For Instrumentor-Based Integrations
1. **Choose Your Instrumentor**: OpenInference (lightweight) or Traceloop (enhanced)
2. **Install Dependencies**: Each example includes specific requirements
3. **Set Environment Variables**: API keys and configuration
4. **Run Example**: `python integrations/[example_name].py`

### For Agent Framework Integrations

#### OpenAI Agents SDK
```bash
pip install openai-agents openinference-instrumentation-openai-agents
export OPENAI_API_KEY=sk-...
export HH_API_KEY=your-honeyhive-key
python integrations/openai_agents_integration.py
```

**Features demonstrated:**
- ✅ Basic agent invocation and tracing
- ✅ Multi-agent orchestration with handoffs
- ✅ Tool/function calling with automatic capture
- ✅ Input/output guardrails
- ✅ Structured outputs with Pydantic
- ✅ Streaming responses
- ✅ Custom context and metadata
- ✅ Complex multi-agent workflows

#### Microsoft Semantic Kernel
```bash
pip install semantic-kernel openinference-instrumentation-openai
export OPENAI_API_KEY=sk-...
export HH_API_KEY=your-honeyhive-key
python integrations/semantic_kernel_integration.py
```

**Features demonstrated:**
- ✅ ChatCompletionAgent with plugins
- ✅ Automatic function calling by AI
- ✅ Structured outputs with Pydantic
- ✅ Multi-turn conversations with history
- ✅ Multiple agents with different models
- ✅ Streaming responses with TTFT
- ✅ Multi-agent workflows
- ✅ Plugin development with @kernel_function

#### AWS Strands
```bash
pip install strands boto3
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
export HH_API_KEY=your-honeyhive-key
python integrations/strands_integration.py
```

**Features demonstrated:**
- ✅ Bedrock model integration
- ✅ Tool execution with agents
- ✅ Streaming mode support
- ✅ Custom trace attributes
- ✅ Structured outputs
- ✅ Event loop cycle tracing

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
    project="my-project",  # Required for OTLP tracing
    source="production"
)

# Install your chosen instrumentor
# Your LLM calls are automatically traced!
```

**Choose the integration that best fits your needs!** 🚀
