# LangChain Analysis Report
## Deep Analysis for HoneyHive Instrumentation Support

**Date:** October 15, 2025  
**Analyst:** AI Agent (Agent OS Enhanced)  
**Methodology:** SDK_ANALYSIS_METHODOLOGY.md v1.1  
**Repository:** https://github.com/langchain-ai/langchain  
**Version Analyzed:** master branch (latest as of 2025-10-15)

---

## Executive Summary

**SDK Purpose:** LangChain is a framework for building LLM-powered applications through composable components and integrations. It provides abstractions for models, chains, agents, retrievers, and tools.

**Architecture Type:** Monorepo with modular packages (langchain-core, langchain, langchain-{provider})

**LLM Client Integration:** Partner packages (e.g., langchain-openai) create their own OpenAI/Anthropic/etc. client instances internally

**Observability:** **Custom callback-based tracing system**, NOT OpenTelemetry. Tightly integrated with LangSmith.

**Recommendation:** **Multi-Tier Integration Strategy**
1. **Tier 1 (Immediate):** Leverage existing OpenAI/Anthropic instrumentors via passthrough
2. **Tier 2 (Medium-term):** Build custom LangChainCallbackHandler to capture chain/agent context
3. **Tier 3 (Long-term):** Contribute OpenTelemetry support to LangChain core

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Findings](#key-findings)
3. [LLM Client Usage](#llm-client-usage)
4. [Observability System](#observability-system)
5. [Integration Points](#integration-points)
6. [Integration Strategy](#integration-strategy)
7. [Comparison with Other SDKs](#comparison-with-other-sdks)
8. [Recommendations](#recommendations)
9. [Testing Strategy](#testing-strategy)
10. [Next Steps](#next-steps)

---

## Architecture Overview

### Repository Structure

LangChain is organized as a **monorepo** with multiple packages:

```
langchain/
├── libs/
│   ├── core/               # langchain-core: Base abstractions (320 Python files)
│   │   ├── callbacks/      # Callback system
│   │   ├── tracers/        # Tracing implementation
│   │   ├── language_models/# LLM abstractions
│   │   ├── runnables/      # Execution runtime
│   │   └── ...
│   ├── langchain/          # langchain: Main package (1581 Python files)
│   └── partners/           # Provider integrations
│       ├── openai/         # langchain-openai
│       ├── anthropic/      # langchain-anthropic
│       ├── google-genai/   # langchain-google-genai
│       ├── fireworks/
│       ├── groq/
│       ├── mistralai/
│       ├── ollama/
│       └── ... (17 partner packages)
```

### Dependency Model

**Clean Separation:**
- `langchain-core`: No LLM client dependencies (only pydantic, langsmith, PyYAML, etc.)
- `langchain`: Optional dependencies for providers (`[openai]`, `[anthropic]`, etc.)
- `langchain-{provider}`: Each has its own client library dependency

**Example - langchain-openai dependencies:**
```toml
dependencies = [
    "langchain-core>=1.0.0a7,<2.0.0",
    "openai>=1.109.1,<3.0.0",  # Official OpenAI Python SDK
    "tiktoken>=0.7.0,<1.0.0",   # Token counting
]
```

### Key Components

1. **Callbacks:** Event-driven hooks for LLM lifecycle events
2. **Tracers:** Specialized callbacks that create hierarchical run trees
3. **Runnables:** Composable execution units with built-in callback support
4. **Language Models:** Base classes for LLMs, chat models, embeddings
5. **Chains/Agents:** Higher-level orchestration primitives

---

## Key Findings

### 1. No OpenTelemetry Usage

```bash
$ grep -r "from opentelemetry" libs/core/ | wc -l
0
```

**Conclusion:** LangChain does NOT use OpenTelemetry. It has a completely custom tracing system.

### 2. Custom Callback-Based Tracing

**Hierarchy:**
```python
BaseCallbackHandler (base interface)
  ├── BaseTracer (extends BaseCallbackHandler)
  │   ├── LangChainTracer → Sends to LangSmith
  │   ├── EvaluatorCallbackHandler
  │   ├── LogStreamCallbackHandler
  │   ├── RunCollectorCallbackHandler
  │   └── FunctionCallbackHandler
  └── StdOutCallbackHandler
```

**Key Files:**
- `langchain_core/callbacks/base.py` (34KB) - Base callback interface
- `langchain_core/callbacks/manager.py` (84KB) - Callback orchestration
- `langchain_core/tracers/base.py` (25KB) - Base tracer implementation
- `langchain_core/tracers/langchain.py` (10KB) - LangSmith integration
- `langchain_core/tracers/core.py` (23KB) - Core tracing logic

### 3. LangSmith Integration

**Critical Finding:**
```python
# From langchain_core/tracers/schemas.py
from langsmith import RunTree

Run = RunTree  # For backwards compatibility
```

**Implication:** LangChain's `Run` data model is **LangSmith's `RunTree`**. The entire tracing system is designed for LangSmith.

### 4. LLM Client Instantiation

**Pattern:** Provider packages create their own client instances

**Example from langchain-openai:**
```python
# libs/partners/openai/langchain_openai/chat_models/base.py:818
self.root_client = openai.OpenAI(**client_params, **sync_specific)

# Line 839
self.root_async_client = openai.AsyncOpenAI(**client_params, **async_specific)
```

**Implication:** Users don't typically instantiate OpenAI clients themselves. LangChain does it internally.

### 5. Callback Integration Pattern

**LLM calls are wrapped with callback hooks:**
```python
# Simplified from base.py
def _generate(
    self,
    messages: List[BaseMessage],
    run_manager: CallbackManagerForLLMRun | None = None,
    **kwargs: Any,
) -> ChatResult:
    # Before LLM call
    # (run_manager.on_llm_start already called by base class)
    
    # Make actual API call
    response = self.root_client.chat.completions.create(...)
    
    # Process response
    for token in response:
        if run_manager:
            run_manager.on_llm_new_token(token)  # Stream callback
    
    # After LLM call
    # (run_manager.on_llm_end will be called by base class)
    
    return result
```

---

## LLM Client Usage

### Client Instantiation Points

**1. langchain-openai (`libs/partners/openai/langchain_openai/chat_models/base.py`)**

Lines 818-839:
```python
self.root_client = openai.OpenAI(**client_params, **sync_specific)
self.root_async_client = openai.AsyncOpenAI(**client_params, **async_specific)
```

**2. langchain-anthropic (`libs/partners/anthropic/`)**

Similar pattern - creates `anthropic.Anthropic()` clients internally.

**3. Other Providers**

Each partner package follows the same pattern:
- Creates client in `__init__` or lazily on first use
- Client is stored as instance variable
- All API calls go through the internal client

### API Call Sites

**OpenAI Example:**
```python
# chat_models/base.py - actual API call happens in various methods
response = self.root_client.chat.completions.create(
    model=self.model_name,
    messages=messages,
    stream=stream,
    **kwargs
)
```

**Anthropic Example:**
```python
# Similar pattern
response = self.client.messages.create(
    model=self.model_name,
    messages=messages,
    **kwargs
)
```

### Integration Challenge

**Problem:** Since LangChain creates clients internally, users can't easily inject instrumented clients.

**Implication:** Standard "wrap the client" approaches won't work without modifications.

---

## Observability System

### Callback System Architecture

#### 1. Base Interface: `BaseCallbackHandler`

**Key Methods:**
```python
class BaseCallbackHandler:
    # LLM lifecycle
    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, **kwargs)
    def on_llm_new_token(self, token, *, chunk=None, run_id, parent_run_id=None, **kwargs)
    def on_llm_end(self, response: LLMResult, *, run_id, parent_run_id=None, **kwargs)
    def on_llm_error(self, error, *, run_id, parent_run_id=None, **kwargs)
    
    # Chat model lifecycle
    def on_chat_model_start(self, serialized, messages, *, run_id, parent_run_id=None, **kwargs)
    
    # Chain lifecycle
    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None, **kwargs)
    def on_chain_end(self, outputs, *, run_id, parent_run_id=None, **kwargs)
    def on_chain_error(self, error, *, run_id, parent_run_id=None, **kwargs)
    
    # Tool lifecycle
    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, **kwargs)
    def on_tool_end(self, output, *, run_id, parent_run_id=None, **kwargs)
    def on_tool_error(self, error, *, run_id, parent_run_id=None, **kwargs)
    
    # Retriever lifecycle
    def on_retriever_start(self, serialized, query, *, run_id, parent_run_id=None, **kwargs)
    def on_retriever_end(self, documents, *, run_id, parent_run_id=None, **kwargs)
    
    # Agent lifecycle
    def on_agent_action(self, action: AgentAction, *, run_id, parent_run_id=None, **kwargs)
    def on_agent_finish(self, finish: AgentFinish, *, run_id, parent_run_id=None, **kwargs)
```

#### 2. Tracer Abstraction: `BaseTracer`

**Extends `BaseCallbackHandler` with:**
- Run tree management (`run_map: Dict[str, Run]`)
- Parent-child run relationships
- Persistence abstraction (`_persist_run()`)

**Abstract method:**
```python
@abstractmethod
def _persist_run(self, run: Run) -> None:
    """Persist a run - subclasses implement this."""
```

#### 3. LangSmith Tracer: `LangChainTracer`

**Implementation:**
```python
class LangChainTracer(BaseTracer):
    def _persist_run(self, run: Run) -> None:
        """Send run to LangSmith API."""
        # Uses langsmith.Client to POST run data
```

**Environment Variable:**
- Set `LANGCHAIN_TRACING_V2=true` to enable
- Requires `LANGCHAIN_API_KEY`
- Sends to `LANGCHAIN_ENDPOINT` (default: https://api.smith.langchain.com)

### Callback Manager System

**Purpose:** Orchestrate multiple callback handlers and manage run hierarchy

**Key Classes:**
```python
CallbackManager          # Sync callback coordinator
AsyncCallbackManager     # Async callback coordinator

# Per-component run managers (passed to _generate, _call, etc.)
CallbackManagerForLLMRun
CallbackManagerForChainRun
CallbackManagerForToolRun
```

**Usage Pattern:**
```python
# Context manager for grouping runs
with trace_as_chain_group("my_workflow", inputs={"query": "..."}) as manager:
    result = llm.invoke(query, {"callbacks": manager})
    manager.on_chain_end({"output": result})
```

### Run Data Model

**From LangSmith `RunTree`:**
```python
class Run:
    id: UUID
    name: str
    run_type: Literal["llm", "chain", "tool", "retriever", "agent"]
    start_time: datetime
    end_time: Optional[datetime]
    parent_run_id: Optional[UUID]
    
    # Inputs/outputs
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]]
    
    # Metadata
    tags: List[str]
    metadata: Dict[str, Any]
    
    # LLM-specific
    serialized: Dict[str, Any]  # Model config
    prompts: List[str]
    response: Optional[LLMResult]
    
    # Error tracking
    error: Optional[str]
    
    # Execution info
    execution_order: int
    child_runs: List[Run]
```

### Semantic Conventions

**LangChain uses its own conventions (NOT GenAI semconv):**

| Field | Example | Description |
|-------|---------|-------------|
| `run_type` | `"llm"`, `"chain"`, `"tool"` | Type of operation |
| `name` | `"ChatOpenAI"`, `"MyChain"` | Component name |
| `serialized` | `{"name": "ChatOpenAI", "model": "gpt-4"}` | Configuration |
| `tags` | `["production", "critical"]` | User-defined tags |
| `metadata` | `{"user_id": "123", "session_id": "abc"}` | Custom metadata |

**No standard OpenTelemetry attributes like:**
- ❌ `gen_ai.system`
- ❌ `gen_ai.request.model`
- ❌ `gen_ai.usage.input_tokens`

**But has equivalent data in `LLMResult`:**
```python
class LLMResult:
    generations: List[List[Generation]]
    llm_output: Dict[str, Any]  # Contains token usage
    run: Optional[List[RunInfo]]
```

---

## Integration Points

### 1. ✅ **Callback Handler Injection** (Primary Integration Point)

**How it works:**
```python
from langchain_openai import ChatOpenAI
from honeyhive import HoneyHiveTracer

# Create custom callback handler
class HoneyHiveCallbackHandler(BaseCallbackHandler):
    def __init__(self, tracer: HoneyHiveTracer):
        self.tracer = tracer
    
    def on_llm_start(self, serialized, prompts, *, run_id, **kwargs):
        # Create HoneyHive span
        pass
    
    def on_llm_end(self, response: LLMResult, *, run_id, **kwargs):
        # Close HoneyHive span with metadata
        pass

# Usage
handler = HoneyHiveCallbackHandler(tracer)
llm = ChatOpenAI(callbacks=[handler])
result = llm.invoke("Hello")  # Traced!
```

**Pros:**
- ✅ Official, supported integration point
- ✅ Works with all LangChain components (chains, agents, tools)
- ✅ Captures LangChain-specific context (run_type, tags, metadata)
- ✅ No monkey-patching required

**Cons:**
- ⚠️ User must explicitly pass `callbacks=[handler]`
- ⚠️ Doesn't capture raw LLM API data (only what LangChain exposes)
- ⚠️ Miss low-level details (exact request/response bodies)

### 2. ✅ **Passthrough via Existing Instrumentors** (Complementary)

**How it works:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Instrument OpenAI client globally
tracer = HoneyHiveTracer.init(project="langchain-app")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# LangChain creates OpenAI client internally
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")

# API calls are automatically traced!
result = llm.invoke("Hello")
```

**Pros:**
- ✅ Zero code changes for LLM API tracing
- ✅ Captures detailed LLM API data (tokens, model, latency)
- ✅ Works with any LangChain provider (if instrumentor exists)
- ✅ Standard OpenTelemetry spans

**Cons:**
- ⚠️ **Missing LangChain context** (chains, agents, tools)
- ⚠️ Spans not hierarchically nested with LangChain runs
- ⚠️ Requires instrumentor per provider (OpenAI, Anthropic, etc.)

### 3. ⚠️ **Client Wrapping** (Not Recommended)

**Would require:**
- Monkey-patching LangChain partner packages
- Replacing internal client creation
- High maintenance burden

**Verdict:** Don't pursue this approach.

### 4. ❌ **TracerProvider Integration** (Not Applicable)

**Reason:** LangChain doesn't use OpenTelemetry, so providing a custom TracerProvider has no effect.

---

## Integration Strategy

### Recommended: **Hybrid Multi-Tier Approach**

Combine multiple approaches to get complete observability:

#### **Tier 1: Passthrough (Immediate - Week 1)**

**Goal:** Capture LLM API calls with zero code changes

**Implementation:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

tracer = HoneyHiveTracer.init(project="my-app")

# Instrument all providers
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
AnthropicInstrumentor().instrument(tracer_provider=tracer.provider)
# ... add more as needed

# LangChain code works unchanged
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
result = llm.invoke("What is the capital of France?")  # ✅ Traced!
```

**What's captured:**
- ✅ LLM model name
- ✅ Input tokens, output tokens, total tokens
- ✅ Latency
- ✅ Request/response content
- ❌ Chain/agent context
- ❌ Tool calls context
- ❌ LangChain-specific metadata

**Effort:** Low (already works with existing instrumentors)

---

#### **Tier 2: Custom Callback Handler (Medium-term - Week 2-3)**

**Goal:** Capture LangChain chain/agent/tool context

**Implementation:**

Create `HoneyHiveLangChainHandler`:
```python
from langchain_core.callbacks import BaseCallbackHandler
from honeyhive import HoneyHiveTracer
from typing import Dict, Any, Optional
from uuid import UUID

class HoneyHiveLangChainHandler(BaseCallbackHandler):
    """HoneyHive callback handler for LangChain.
    
    Captures chain, agent, and tool execution context.
    Complements LLM-level instrumentation from Tier 1.
    """
    
    def __init__(self, tracer: HoneyHiveTracer):
        self.tracer = tracer
        self.run_map: Dict[UUID, Any] = {}  # Track active runs
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Start chain span."""
        span = self.tracer.start_span(
            name=serialized.get("name", "Chain"),
            attributes={
                "langchain.run_type": "chain",
                "langchain.run_id": str(run_id),
                "langchain.parent_run_id": str(parent_run_id) if parent_run_id else None,
                "langchain.tags": tags or [],
                **metadata or {},
            },
            inputs=inputs,
        )
        self.run_map[run_id] = span
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """End chain span."""
        span = self.run_map.pop(run_id, None)
        if span:
            span.set_outputs(outputs)
            span.end()
    
    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Record chain error."""
        span = self.run_map.pop(run_id, None)
        if span:
            span.set_error(error)
            span.end()
    
    # Similar implementations for:
    # - on_llm_start/end/error (enrichment layer on top of Tier 1)
    # - on_tool_start/end/error
    # - on_agent_action/finish
    # - on_retriever_start/end
```

**Usage:**
```python
from honeyhive import HoneyHiveTracer
from honeyhive.integrations.langchain import HoneyHiveLangChainHandler

tracer = HoneyHiveTracer.init(project="my-app")
handler = HoneyHiveLangChainHandler(tracer)

# Use with LangChain
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(model="gpt-4")
prompt = PromptTemplate.from_template("What is the capital of {country}?")
chain = LLMChain(llm=llm, prompt=prompt)

# Pass handler to capture chain context
result = chain.invoke(
    {"country": "France"},
    config={"callbacks": [handler]}  # 👈 Key integration point
)
```

**What's additionally captured:**
- ✅ Chain hierarchy (parent-child relationships)
- ✅ Agent actions and decisions
- ✅ Tool calls and results
- ✅ Retriever queries
- ✅ LangChain tags and metadata
- ✅ Custom user metadata

**Effort:** Medium (2-3 days implementation, 2 days testing)

---

#### **Tier 3: OpenTelemetry Contribution (Long-term - Months)**

**Goal:** Get LangChain to natively support OpenTelemetry

**Strategy:**
1. **Proposal:** Submit RFC to LangChain community
2. **Implementation:** Contribute PR adding OpenTelemetry support alongside existing callback system
3. **Design:** Create `OpenTelemetryTracer(BaseTracer)` that converts runs to OTel spans
4. **Compatibility:** Keep existing callback system, add OTel as optional

**Example Design:**
```python
# Proposed langchain_core/tracers/opentelemetry.py
from opentelemetry import trace
from langchain_core.tracers.base import BaseTracer

class OpenTelemetryTracer(BaseTracer):
    """OpenTelemetry-compatible tracer for LangChain.
    
    Converts LangChain runs to OpenTelemetry spans following
    GenAI semantic conventions.
    """
    
    def __init__(self, tracer_provider=None):
        from opentelemetry.trace import get_tracer_provider
        provider = tracer_provider or get_tracer_provider()
        self.tracer = provider.get_tracer("langchain")
        self.span_map = {}
    
    def _persist_run(self, run: Run) -> None:
        """Convert Run to OpenTelemetry span."""
        # Implementation here
        pass
```

**Benefits:**
- ✅ Standard approach for all observability tools
- ✅ Reduced maintenance burden
- ✅ Community benefit
- ✅ Future-proof

**Effort:** High (weeks to months, community engagement)

---

### Implementation Phases

| Phase | Timeline | Goal | Deliverables |
|-------|----------|------|--------------|
| **Phase 1** | Week 1 | Passthrough support | Documentation, examples |
| **Phase 2** | Week 2-3 | Callback handler | `honeyhive.integrations.langchain` module |
| **Phase 3** | Month 2+ | OTel contribution | RFC, PR to LangChain |

---

## Comparison with Other SDKs

### OpenAI Agents SDK vs LangChain

| Aspect | OpenAI Agents SDK | LangChain |
|--------|-------------------|-----------|
| **Observability** | Custom tracing (non-OTel) | Custom callbacks + LangSmith |
| **Client Creation** | Internal (`openai.Client()`) | Internal (per-provider) |
| **Architecture** | Simple (agents SDK) | Complex (modular framework) |
| **Extensibility** | Limited | Highly extensible |
| **Integration Point** | Tracer processor injection | Callback handler injection |
| **Difficulty** | Medium | Medium-High |

**Similarity:** Both use custom tracing, require custom integration

### AWS Strands SDK vs LangChain

| Aspect | AWS Strands SDK | LangChain |
|--------|-----------------|-----------|
| **Observability** | **OpenTelemetry native** ✅ | Custom (non-OTel) ❌ |
| **Client Creation** | User-provided (BYOC) | Internal |
| **Integration** | TracerProvider injection | Callback handler |
| **Difficulty** | Low (OTel standard) | Medium-High |

**Key Difference:** Strands uses OTel natively, making integration trivial. LangChain requires custom work.

---

## Recommendations

### Immediate Actions (Week 1)

1. **✅ Document Tier 1 (Passthrough) approach**
   - Add section to docs: `docs/how-to/integrations/langchain.rst`
   - Show how existing OpenAI/Anthropic instrumentors work with LangChain
   - Clarify what's captured vs. what's missing

2. **✅ Create example**
   - `examples/integrations/langchain_passthrough.py`
   - Demonstrate Tier 1 approach
   - Show what traces look like

### Short-term Actions (Week 2-3)

3. **🔨 Build Tier 2 (Callback Handler)**
   - Implement `HoneyHiveLangChainHandler` in `honeyhive/integrations/langchain.py`
   - Support all callback methods (llm, chain, tool, agent, retriever)
   - Map LangChain runs to HoneyHive spans
   - Preserve parent-child relationships

4. **✅ Create comprehensive examples**
   - Simple chain example
   - Agent example with tools
   - RAG example with retrievers
   - Streaming example

5. **📚 Write integration docs**
   - Installation
   - Basic setup (Tier 1)
   - Advanced setup (Tier 1 + Tier 2 combined)
   - Troubleshooting
   - What's captured

### Long-term Actions (Month 2+)

6. **🌍 Contribute to LangChain**
   - Draft RFC for OpenTelemetry support
   - Engage with LangChain maintainers
   - Implement `OpenTelemetryTracer` if accepted
   - Submit PR

7. **🔄 Monitor LangChain developments**
   - Watch for any OTel movement in community
   - Track LangSmith API changes (affects Run schema)
   - Stay updated on new providers

---

## Testing Strategy

### Unit Tests

**Test Tier 1 (Passthrough):**
```python
def test_langchain_openai_with_openinference():
    """Test that OpenAI instrumentor captures LangChain LLM calls."""
    tracer = HoneyHiveTracer.init(project="test")
    OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
    
    llm = ChatOpenAI(model="gpt-4")
    with tracer.start_session():
        result = llm.invoke("Hello")
    
    spans = tracer.get_spans()
    assert len(spans) > 0
    assert any(s.attributes.get("gen_ai.system") == "openai" for s in spans)
```

**Test Tier 2 (Callback Handler):**
```python
def test_langchain_chain_with_callback_handler():
    """Test that custom handler captures chain context."""
    tracer = HoneyHiveTracer.init(project="test")
    handler = HoneyHiveLangChainHandler(tracer)
    
    llm = ChatOpenAI(model="gpt-4")
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{text}"))
    
    result = chain.invoke(
        {"text": "Hello"},
        config={"callbacks": [handler]}
    )
    
    spans = tracer.get_spans()
    
    # Should have both chain span AND llm span
    chain_spans = [s for s in spans if s.attributes.get("langchain.run_type") == "chain"]
    llm_spans = [s for s in spans if s.attributes.get("langchain.run_type") == "llm"]
    
    assert len(chain_spans) > 0
    assert len(llm_spans) > 0
    
    # Verify hierarchy
    chain_span = chain_spans[0]
    llm_span = llm_spans[0]
    assert llm_span.parent_id == chain_span.span_id
```

### Integration Tests

```python
def test_langchain_agent_with_tools():
    """Test agent with tool calls."""
    from langchain.agents import initialize_agent, AgentType
    from langchain.tools import Tool
    
    tracer = HoneyHiveTracer.init(project="test")
    handler = HoneyHiveLangChainHandler(tracer)
    
    def mock_search(query: str) -> str:
        return f"Results for: {query}"
    
    tools = [Tool(name="Search", func=mock_search, description="Search tool")]
    llm = ChatOpenAI(model="gpt-4")
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    
    result = agent.run(
        "What is the capital of France?",
        callbacks=[handler]
    )
    
    spans = tracer.get_spans()
    
    # Should capture: agent span, llm spans, tool span
    assert len(spans) >= 3
    assert any(s.attributes.get("langchain.run_type") == "agent" for s in spans)
    assert any(s.attributes.get("langchain.run_type") == "tool" for s in spans)
```

### Example Tests

**Test all examples actually work:**
```python
@pytest.mark.integration
def test_examples():
    """Run all example scripts to ensure they work."""
    examples = [
        "examples/integrations/langchain_passthrough.py",
        "examples/integrations/langchain_advanced.py",
        "examples/integrations/langchain_agent.py",
    ]
    
    for example in examples:
        result = subprocess.run(["python", example], capture_output=True)
        assert result.returncode == 0, f"Example {example} failed"
```

---

## Next Steps

### For HoneyHive Team

1. **Approve Strategy:**
   - Review this report
   - Approve Tier 1 + Tier 2 approach
   - Decide on Tier 3 timeline

2. **Prioritize Implementation:**
   - Week 1: Documentation for Tier 1
   - Week 2-3: Implement Tier 2 handler
   - Month 2+: Begin Tier 3 community engagement

3. **Resource Allocation:**
   - 1 engineer for Tier 2 implementation (2-3 days)
   - Technical writer for documentation (1 day)
   - QA for testing examples (1 day)

### For Community

4. **Draft LangChain RFC:**
   - Title: "RFC: OpenTelemetry Support for LangChain Tracing"
   - Propose `OpenTelemetryTracer(BaseTracer)` class
   - Show benefits to ecosystem
   - Offer to implement and maintain

5. **Engage with Maintainers:**
   - Post RFC to LangChain GitHub discussions
   - Share on LangChain community Slack/Discord
   - Present at community call if available

---

## Appendix A: File Locations

### Key Source Files Analyzed

```
langchain-core:
  langchain_core/callbacks/base.py          # Callback interface (428 lines)
  langchain_core/callbacks/manager.py       # Callback orchestration (2,842 lines)
  langchain_core/tracers/base.py            # Base tracer (880 lines)
  langchain_core/tracers/core.py            # Core tracing logic (683 lines)
  langchain_core/tracers/langchain.py       # LangSmith integration (277 lines)
  langchain_core/tracers/schemas.py         # Run data model (12 lines - imports RunTree)

langchain-openai:
  langchain_openai/chat_models/base.py      # OpenAI chat model (4,000+ lines)
  
langchain-anthropic:
  langchain_anthropic/chat_models.py        # Anthropic chat model
```

### Dependencies

```toml
langchain-core:
  langsmith>=0.3.45,<1.0.0       # LangSmith RunTree used as Run
  tenacity>=8.1.0                # Retry logic
  pydantic>=2.7.4                # Data models
  PyYAML>=5.3.0                  # Config
  packaging>=23.2.0              # Version handling

langchain-openai:
  langchain-core>=1.0.0a7
  openai>=1.109.1,<3.0.0         # Official OpenAI SDK
  tiktoken>=0.7.0                # Token counting
```

---

## Appendix B: Useful Commands

### Analysis Commands Used

```bash
# Clone repository
cd /tmp
git clone --depth 1 https://github.com/langchain-ai/langchain.git
cd langchain

# Count files
find libs/core -name "*.py" | wc -l
find libs/langchain -name "*.py" | wc -l

# Check for OpenTelemetry
grep -r "from opentelemetry" libs/core/ | wc -l  # Result: 0

# Explore structure
ls -la libs/
ls -la libs/partners/

# Find tracers
grep -n "class.*Tracer" libs/core/langchain_core/tracers/*.py

# Find client creation
grep -n "openai.OpenAI\|openai.AsyncOpenAI" libs/partners/openai/langchain_openai/chat_models/base.py
```

---

## Appendix C: Integration Code Skeleton

### Minimal Tier 2 Implementation

```python
# honeyhive/integrations/langchain.py
"""LangChain integration for HoneyHive.

Provides callback handler to capture chain, agent, and tool context.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.documents import Document
from langchain_core.outputs import LLMResult

from honeyhive import HoneyHiveTracer


class HoneyHiveLangChainHandler(BaseCallbackHandler):
    """HoneyHive callback handler for LangChain.
    
    Captures LangChain-specific context (chains, agents, tools) and
    sends to HoneyHive for observability.
    
    Usage:
        ```python
        from honeyhive import HoneyHiveTracer
        from honeyhive.integrations.langchain import HoneyHiveLangChainHandler
        
        tracer = HoneyHiveTracer.init(project="my-app")
        handler = HoneyHiveLangChainHandler(tracer)
        
        # Use with any LangChain component
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4")
        result = llm.invoke("Hello", config={"callbacks": [handler]})
        ```
    """
    
    def __init__(self, tracer: HoneyHiveTracer):
        """Initialize handler.
        
        Args:
            tracer: HoneyHiveTracer instance for sending traces.
        """
        self.tracer = tracer
        self.run_map: Dict[UUID, Any] = {}
    
    # Implement all required callback methods here...
    # See full implementation in Tier 2 section above
```

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2025-10-15  
**Reviewed By:** [Pending]  
**Status:** Draft - Awaiting Review

**Changelog:**
- 2025-10-15: Initial analysis completed following SDK_ANALYSIS_METHODOLOGY.md v1.1

