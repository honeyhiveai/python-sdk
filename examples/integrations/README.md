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
- **[`dspy_integration.py`](dspy_integration.py)** - DSPy framework with OpenAI instrumentor (✅ signatures, modules, ChainOfThought, ReAct, RAG, classification)
- **[`semantic_kernel_integration.py`](semantic_kernel_integration.py)** - Microsoft Semantic Kernel with OpenAI instrumentor (✅ agents, plugins, function calling, streaming)
- **[`strands_integration.py`](strands_integration.py)** - AWS Strands with TracerProvider pattern (✅ Bedrock models, streaming, tools)
- **[`bedrock_integration.py`](bedrock_integration.py)** - AWS Bedrock direct with Bedrock instrumentor (✅ Nova, Titan, Claude, Converse API, streaming)
- **[`langgraph_integration.py`](langgraph_integration.py)** - LangGraph workflows with LangChain instrumentor (✅ state graphs, conditional routing, agent graphs)
- **[`pydantic_ai_integration.py`](pydantic_ai_integration.py)** - Pydantic AI agents with Anthropic instrumentor (✅ structured outputs, tools, dependencies, streaming)
- **[`openinference_google_adk_example.py`](openinference_google_adk_example.py)** - Google ADK with workflow agents (✅ sequential, parallel, loop workflows)

## 🚀 **Quick Start**

### For Instrumentor-Based Integrations
1. **Choose Your Instrumentor**: OpenInference (lightweight) or Traceloop (enhanced)
2. **Install Dependencies**: Each example includes specific requirements
3. **Set Environment Variables**: API keys and configuration
4. **Run Example**: `python integrations/[example_name].py`

### For Agent Framework Integrations

#### DSPy Framework
```bash
pip install dspy openinference-instrumentation-dspy openinference-instrumentation-openai
export OPENAI_API_KEY=sk-...
export HH_API_KEY=your-honeyhive-key
export HH_PROJECT=your-project
python integrations/dspy_integration.py
```

**Features demonstrated:**
- ✅ Basic Predict module for simple completions
- ✅ ChainOfThought for reasoning with intermediate steps
- ✅ Custom signatures with typed input/output fields
- ✅ ReAct agents with tool usage
- ✅ Multi-step reasoning for complex problems
- ✅ Custom DSPy modules (QuestionAnswerModule)
- ✅ Text classification with sentiment analysis
- ✅ Retrieval-augmented generation (RAG) simulation
- ✅ BootstrapFewShot optimizer for program optimization
- ✅ GEPA optimizer (facility support analyzer)
- ✅ Evaluation with custom metrics

#### OpenAI Agents SDK
```bash
pip install openai-agents openinference-instrumentation-openai-agents openinference-instrumentation-openai
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
- ✅ Bedrock model integration via Strands
- ✅ Tool execution with agents
- ✅ Streaming mode support
- ✅ Custom trace attributes
- ✅ Structured outputs
- ✅ Event loop cycle tracing

#### AWS Bedrock Direct
```bash
pip install boto3 openinference-instrumentation-bedrock
export HH_API_KEY=your-honeyhive-key
export HH_PROJECT=your-project

# Option 1: Long-term credentials
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# Option 2: Temporary credentials with session token
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_SESSION_TOKEN=your-session-token

# Option 3: Use AWS CLI default profile (no env vars needed)
# aws configure

export AWS_REGION=us-east-1
python integrations/bedrock_integration.py
```

**Features demonstrated:**
- ✅ Amazon Nova models (nova-lite-v1:0)
- ✅ Amazon Titan Text models (titan-text-express-v1)
- ✅ Anthropic Claude models (3-haiku, 3-sonnet)
- ✅ Converse API (unified interface)
- ✅ Streaming responses with ConverseStream
- ✅ Multi-turn conversations with context
- ✅ Document understanding (PDF, TXT, DOC formats)
- ✅ Native invoke_model API with streaming
- ✅ Native Bedrock Runtime client integration
- ✅ Multiple authentication methods (keys, session tokens, IAM roles)

#### LangGraph
```bash
pip install langgraph langchain-openai openinference-instrumentation-langchain
export OPENAI_API_KEY=sk-...
export HH_API_KEY=your-honeyhive-key
python integrations/langgraph_integration.py
```

**Features demonstrated:**
- ✅ Basic state graph workflows
- ✅ Sequential node execution
- ✅ Conditional routing based on state
- ✅ Multi-step agent graphs
- ✅ Node-level tracing with @trace decorator
- ✅ Automatic LangChain call tracing
- ✅ State management across nodes

#### Pydantic AI
```bash
pip install pydantic-ai openinference-instrumentation-anthropic
export ANTHROPIC_API_KEY=your-anthropic-key
export HH_API_KEY=your-honeyhive-key
python integrations/pydantic_ai_integration.py
```

**Features demonstrated:**
- ✅ Basic agent with instructions
- ✅ Structured outputs with Pydantic models
- ✅ Agent tools/functions with @agent.tool
- ✅ Dynamic system prompts with @agent.system_prompt
- ✅ Dependency injection with RunContext
- ✅ Streaming responses with async iteration
- ✅ Type-safe agent development

#### Google ADK
```bash
pip install google-adk openinference-instrumentation-google-adk
export GOOGLE_API_KEY=your-google-api-key
export HH_API_KEY=your-honeyhive-key
python integrations/openinference_google_adk_example.py
```

**Features demonstrated:**
- ✅ LlmAgent with tools
- ✅ Sequential workflow agents (pipeline processing)
- ✅ Parallel workflow agents (concurrent execution)
- ✅ Loop workflow agents (iterative refinement)
- ✅ Runner and session management
- ✅ State-based agent communication
- ✅ Async/await patterns

## 📖 **Documentation**

For detailed integration guides, see:

**LLM Provider Integrations:**
- [OpenAI Integration](../../docs/how-to/integrations/openai.rst)
- [Anthropic Integration](../../docs/how-to/integrations/anthropic.rst)
- [Google AI Integration](../../docs/how-to/integrations/google-ai.rst)
- [Google ADK Integration](../../docs/how-to/integrations/google-adk.rst)
- [AWS Bedrock Integration](../../docs/how-to/integrations/bedrock.rst)
- [Azure OpenAI Integration](../../docs/how-to/integrations/azure-openai.rst)
- [MCP Integration](../../docs/how-to/integrations/mcp.rst)
- [Multi-Provider Guide](../../docs/how-to/integrations/multi-provider.rst)

**Agent Framework Integrations:**
- [LangGraph Integration](../../docs/how-to/integrations/langgraph.rst) - State graphs, conditional routing
- [DSPy Integration](../../docs/how-to/integrations/dspy.rst) - Signatures, modules, optimizers
- [AutoGen Integration](../../docs/how-to/integrations/autogen.rst) - Multi-agent conversations
- [Semantic Kernel Integration](../../docs/how-to/integrations/semantic-kernel.rst) - Plugins, agents, planning
- [Pydantic AI Integration](../../docs/how-to/integrations/pydantic-ai.rst) - Type-safe agents

**Other Resources:**
- **[How-To Guides](../../docs/how-to/integrations/)** - All integration guides
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

## 🧪 **Testing & Validation Utilities**

### Exercise Scripts

Generate comprehensive traffic for fixture validation and attribute mapping testing:

**[`exercise_google_adk.py`](exercise_google_adk.py)** - Google ADK traffic generator

```bash
# Generate traffic to validate fixtures and mappings
python exercise_google_adk.py --verbose --iterations 3

# Quick single run (with automatic rate limiting)
python exercise_google_adk.py

# Adjust rate limit delay for different quotas
python exercise_google_adk.py --rate-limit-delay 10.0  # 10 seconds between calls
```

**Features:**
- ⏱️  **Automatic rate limiting** (7s delay between calls, configurable)
- 🔄 **Retry logic** with exponential backoff for 429 errors
- 📊 **Progress tracking** with clear console output

**Exercises 5 test scenarios:**
1. **Basic Model Calls** - Validates MODEL span attributes (prompt_tokens, completion_tokens → metadata.*)
2. **Tool Calls** - Validates TOOL span attributes (tool names, inputs, outputs)
3. **Chain Workflows** - Validates CHAIN span attributes (flexible structure, inputs, outputs)
4. **Error Scenarios** - Validates error attribute mapping and status codes
5. **Metadata & Metrics** - Validates metadata.* and metrics.* attribute separation

**Purpose:**
- Validate fixture accuracy against real API responses
- Test attribute mapping fixes (token metrics → metadata.*, cost/timing → metrics.*)
- Verify frontend rendering behavior for different event types
- Generate diverse span patterns for ingestion service testing

### Span Capture Utilities

**[`capture_spans.py`](capture_spans.py)** - Capture and export spans for fixture creation
**[`convert_spans_to_test_cases.py`](convert_spans_to_test_cases.py)** - Generate test fixtures from captured spans

See [`GENERATE_TEST_CASES.md`](GENERATE_TEST_CASES.md) for detailed workflow.

---

**Choose the integration that best fits your needs!** 🚀
