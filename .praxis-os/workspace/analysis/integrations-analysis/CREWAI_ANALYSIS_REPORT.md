# CrewAI Analysis Report
**Date:** October 15, 2025  
**Analyzer:** AI Assistant  
**Purpose:** Determine instrumentation strategy for CrewAI support in HoneyHive Python SDK

---

## Executive Summary

- **SDK Purpose:** Multi-agent orchestration framework with Crews (autonomous agents) and Flows (event-driven workflows)
- **LLM Client:** LiteLLM (universal LLM abstraction) with OpenAI as dependency
- **Observability:** OpenTelemetry-based + Custom event-driven tracing system
- **Version Analyzed:** 0.203.1 (latest as of Oct 2025)
- **Repository:** https://github.com/crewAIInc/crewAI
- **Codebase Size:** 372 Python files, ~41,000 LOC

### **Recommendation:** Tiered Approach (Easy → Advanced)

**Tier 1 (Easy):** LiteLLM Instrumentation → Basic LLM observability  
**Tier 2 (Advanced):** CrewAI Event Listener → Full agent orchestration context

Since CrewAI uses LiteLLM for all LLM calls, instrumenting LiteLLM provides immediate value with basic LLM observability (model, prompts, tokens, timing). Adding CrewAI-specific event listener instrumentation enriches these traces with agent/task/crew context for complete multi-agent workflow visibility.

**Best approach:** Implement both, starting with LiteLLM (universal, works for all frameworks) then add CrewAI event listener (optional, for power users needing agent context).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Findings](#key-findings)
   - [LLM Client Usage](#llm-client-usage)
   - [Observability System](#observability-system)
   - [Event System](#event-system)
3. [Integration Approach](#integration-approach)
4. [Proof of Concept](#proof-of-concept)
5. [Testing Strategy](#testing-strategy)
6. [Limitations & Considerations](#limitations--considerations)
7. [Next Steps](#next-steps)

---

## Architecture Overview

CrewAI is a standalone multi-agent framework built from scratch (not based on LangChain). It provides two complementary approaches:

1. **Crews**: Teams of autonomous AI agents with role-based collaboration
2. **Flows**: Event-driven workflows with precise control over execution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Code                           │
│  crew = Crew(agents=[...], tasks=[...])                │
│  result = crew.kickoff(inputs={...})                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  v
┌─────────────────────────────────────────────────────────┐
│                  Crew Orchestration                     │
│  - Task planning & execution                            │
│  - Agent coordination                                   │
│  - Process flow (sequential/hierarchical)               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  v
┌─────────────────────────────────────────────────────────┐
│                  Agent Execution                        │
│  - Agent.execute_task()                                 │
│  - Tool calling                                         │
│  - Memory retrieval                                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  v
┌─────────────────────────────────────────────────────────┐
│                   LLM Layer (llm.py)                    │
│  - LiteLLM abstraction                                  │
│  - Multi-provider support                               │
│  - Streaming & function calling                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  v
┌─────────────────────────────────────────────────────────┐
│              LiteLLM (litellm.completion)               │
│  - OpenAI, Anthropic, Google, Azure, Bedrock, etc.     │
└─────────────────────────────────────────────────────────┘
                  │
                  │ (All layers emit events)
                  v
┌─────────────────────────────────────────────────────────┐
│              Event Bus (Blinker Signals)                │
│  - LLMCallStartedEvent / CompletedEvent / FailedEvent  │
│  - AgentExecutionStartedEvent / CompletedEvent         │
│  - TaskStartedEvent / CompletedEvent                    │
│  - ToolUsageStartedEvent / FinishedEvent               │
│  - MemoryQueryEvents, KnowledgeEvents, etc.            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ├──> TraceCollectionListener (CrewAI AMP)
                  ├──> OpenTelemetry Telemetry (internal)
                  └──> [Our HoneyHive Listener] ← Integration Point!
```

---

## Key Findings

### Phase 1: Initial Discovery

#### SDK Metadata
- **Name:** CrewAI
- **Version:** 0.203.1
- **Python Requirements:** >=3.10,<3.14
- **Installation:** `pip install crewai` or `pip install 'crewai[tools]'`
- **License:** MIT

#### Core Dependencies
```toml
# Core
pydantic>=2.11.9
openai>=1.13.3
litellm==1.74.9
instructor>=1.3.3

# Telemetry and Monitoring (CRITICAL!)
opentelemetry-api>=1.30.0
opentelemetry-sdk>=1.30.0
opentelemetry-exporter-otlp-proto-http>=1.30.0

# Data Handling
chromadb~=1.1.0
tokenizers>=0.20.3

# Configuration
python-dotenv>=1.1.1
click>=8.1.7
blinker>=1.9.0  # Event system
```

#### File Structure
- **Total Python files:** 372
- **Total LOC:** ~41,000
- **Largest files:**
  - `crew.py` (1,576 lines) - Core orchestration
  - `llm.py` (1,295 lines) - LLM abstraction
  - `flow.py` (1,254 lines) - Flow orchestration
  - `telemetry.py` (896 lines) - OpenTelemetry implementation
  - `agent.py` (869 lines) - Agent implementation
  - `task.py` (791 lines) - Task implementation
  - `trace_listener.py` (471 lines) - Event-based tracing

#### Main Entry Points
```python
from crewai import Crew, Agent, Task, Flow, Process

# Crew API
crew = Crew(agents=[...], tasks=[...], process=Process.sequential)
result = crew.kickoff(inputs={...})

# Flow API
@flow
class MyFlow(Flow):
    @start()
    def begin(self):
        pass
```

---

### Phase 2: LLM Client Discovery

#### LLM Client Library: **LiteLLM**

CrewAI uses LiteLLM as a universal abstraction layer, supporting:
- OpenAI
- Anthropic
- Google (Gemini)
- Azure OpenAI
- AWS Bedrock
- Ollama (local models)
- And 100+ other providers

#### Client Instantiation

**File:** `src/crewai/llm.py`

CrewAI's `LLM` class wraps LiteLLM:

```python
# Line 20: Import
from litellm.types.utils import ChatCompletionDeltaToolCall

# LiteLLM is NOT instantiated as a client object
# It's used as a module with direct function calls
```

#### API Call Points

**File:** `src/crewai/llm.py`

```python
# Line 442: Streaming API calls
for chunk in litellm.completion(**params):
    # Process streaming chunk
    
# Line 799: Non-streaming API calls
response = litellm.completion(**params)
```

**Total LiteLLM API calls:** 3 locations (2 in llm.py, 1 in token counter)

**API Call Pattern:**
- LiteLLM is used as a module, not an instantiated client
- All calls go through `litellm.completion()` function
- Supports both sync and async
- Streaming and non-streaming modes

#### LLM Events Emitted

CrewAI emits rich events for every LLM call:

```python
# src/crewai/events/types/llm_events.py
@dataclass
class LLMCallStartedEvent(BaseEvent):
    """Emitted when an LLM call starts"""
    task_name: str
    task_description: str
    agent_role: str
    messages: list[dict]
    model: str
    
@dataclass
class LLMCallCompletedEvent(BaseEvent):
    """Emitted when an LLM call completes"""
    response: Any
    usage: dict  # Token usage
    model: str
```

---

### Phase 3: Observability System Analysis

#### 3.1 Built-in Tracing: **YES** (OpenTelemetry)

CrewAI uses OpenTelemetry for internal telemetry, but **in a way that makes standard OTel integration difficult**.

**File:** `src/crewai/telemetry/telemetry.py`

#### 3.2 OpenTelemetry Usage Deep Dive

##### ❌ CRITICAL ISSUE: Custom TracerProvider

```python
# Line 114-126
self.resource = Resource(
    attributes={SERVICE_NAME: CREWAI_TELEMETRY_SERVICE_NAME},
)
self.provider = TracerProvider(resource=self.resource)

processor = BatchSpanProcessor(
    SafeOTLPSpanExporter(
        endpoint=f"{CREWAI_TELEMETRY_BASE_URL}/v1/traces",
        timeout=30,
    )
)
self.provider.add_span_processor(processor)

# Line 149: Sets global TracerProvider
trace.set_tracer_provider(self.provider)
```

**Decision:** ❌ **Does NOT use `get_tracer_provider()`** - Creates and sets its own provider

This means:
- Standard OTel integration via `TracerProvider` injection **WILL NOT WORK**
- CrewAI overwrites any global TracerProvider you set
- Their spans go to their own OTLP endpoint: `CREWAI_TELEMETRY_BASE_URL`

##### ✅ GOOD NEWS: Telemetry Can Be Disabled

```python
# Line 134-138
@classmethod
def _is_telemetry_disabled(cls) -> bool:
    return (
        os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true"
        or os.getenv("CREWAI_DISABLE_TELEMETRY", "false").lower() == "true"
        or os.getenv("CREWAI_DISABLE_TRACKING", "false").lower() == "true"
    )
```

**Environment Variables:**
- `OTEL_SDK_DISABLED=true` - Disables CrewAI's OTel telemetry
- `CREWAI_DISABLE_TELEMETRY=true` - Disables telemetry
- `CREWAI_DISABLE_TRACKING=true` - Disables tracking

##### Span Attributes Analysis

**Total `span.set_attribute` calls:** 1 (in `_add_attribute` helper method)

CrewAI sets custom attributes (not GenAI semantic conventions):
- `crewai_version`
- `python_version`
- `crew_process`
- `crew_memory`
- `crew_number_of_tasks`
- `crew_number_of_agents`
- `llm` (model name)
- `tool_name`
- `agent_role`
- `task_description`
- And many more custom attributes

**Does NOT use GenAI semantic conventions** (`gen_ai.*` attributes)

##### Span Events Analysis

**Total `span.add_event` calls:** 0

CrewAI does **NOT** use span events. All data is captured via span attributes only.

##### Span Hierarchy and SpanKind

**SpanKind usage:** 0 occurrences

CrewAI does not set `SpanKind` on spans. All spans default to `SpanKind.INTERNAL`.

##### Resource Attributes

```python
self.resource = Resource(
    attributes={SERVICE_NAME: CREWAI_TELEMETRY_SERVICE_NAME},
)
```

Sets `service.name` to `"crewai.telemetry"` (from constants.py)

##### Exporter Configuration

- **Exporter:** SafeOTLPSpanExporter (custom wrapper around OTLPSpanExporter)
- **Processor:** BatchSpanProcessor
- **Endpoint:** `f"{CREWAI_TELEMETRY_BASE_URL}/v1/traces"`
- **Timeout:** 30 seconds

---

### 3.3 Custom Event-Driven Tracing System

#### ✅ CRITICAL DISCOVERY: Blinker Event Bus

**File:** `src/crewai/events/event_bus.py`

CrewAI has a **sophisticated event-driven architecture** using Blinker signals:

```python
class CrewAIEventsBus:
    """A singleton event bus that uses blinker signals for event handling."""
    
    def on(self, event_type: type[EventT]) -> Callable:
        """Decorator to register an event handler for a specific event type."""
```

#### Event Types Available

**LLM Events:**
- `LLMCallStartedEvent`
- `LLMCallCompletedEvent`
- `LLMCallFailedEvent`
- `LLMStreamChunkEvent`

**Agent Events:**
- `AgentExecutionStartedEvent`
- `AgentExecutionCompletedEvent`
- `AgentExecutionErrorEvent`
- `AgentReasoningStartedEvent`
- `AgentReasoningCompletedEvent`
- `AgentReasoningFailedEvent`

**Task Events:**
- `TaskStartedEvent`
- `TaskCompletedEvent`
- `TaskFailedEvent`

**Tool Events:**
- `ToolUsageStartedEvent`
- `ToolUsageFinishedEvent`
- `ToolUsageErrorEvent`

**Memory Events:**
- `MemoryQueryStartedEvent`
- `MemoryQueryCompletedEvent`
- `MemoryQueryFailedEvent`
- `MemorySaveStartedEvent`
- `MemorySaveCompletedEvent`
- `MemorySaveFailedEvent`

**Knowledge Events:**
- `KnowledgeRetrievalStartedEvent`
- `KnowledgeRetrievalCompletedEvent`
- `KnowledgeQueryStartedEvent`
- `KnowledgeQueryCompletedEvent`
- `KnowledgeQueryFailedEvent`

**Crew Events:**
- `CrewKickoffStartedEvent`
- `CrewKickoffCompletedEvent`
- `CrewKickoffFailedEvent`

**Flow Events:**
- `FlowCreatedEvent`
- `FlowStartedEvent`
- `FlowFinishedEvent`
- `MethodExecutionStartedEvent`
- `MethodExecutionFinishedEvent`
- `MethodExecutionFailedEvent`

#### Event Registration Pattern

```python
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.llm_events import LLMCallCompletedEvent

@crewai_event_bus.on(LLMCallCompletedEvent)
def on_llm_call_completed(source: Any, event: LLMCallCompletedEvent):
    print(f"LLM call completed: {event.model}")
    print(f"Tokens used: {event.usage}")
```

#### Existing Event Listener: TraceCollectionListener

**File:** `src/crewai/events/listeners/tracing/trace_listener.py`

CrewAI already has a sophisticated event listener for their Control Plane (CrewAI AMP):

```python
class TraceCollectionListener(BaseEventListener):
    """Trace collection listener that orchestrates trace collection"""
    
    def setup_listeners(self, crewai_event_bus):
        """Setup event listeners - delegates to specific handlers"""
        
        @event_bus.on(LLMCallStartedEvent)
        def on_llm_call_started(source, event):
            self._handle_action_event("llm_call_started", source, event)
        
        @event_bus.on(LLMCallCompletedEvent)
        def on_llm_call_completed(source, event):
            self._handle_action_event("llm_call_completed", source, event)
```

**This is our integration model!** We can create a similar listener for HoneyHive.

---

### 3.4 Integration Points Discovery

#### ✅ Integration Point 1: Event Bus Registration

**Location:** `crewai_event_bus` (global singleton)

**How to inject:**
```python
from crewai.events.event_bus import crewai_event_bus

# Register custom event handlers
@crewai_event_bus.on(LLMCallCompletedEvent)
def my_handler(source, event):
    # Send to HoneyHive
    pass
```

**Pros:**
- ✅ Clean, documented API
- ✅ Captures ALL events (LLM calls, agent execution, tool usage)
- ✅ Rich event data with agent/task context
- ✅ Non-invasive (doesn't require modifying CrewAI code)

**Cons:**
- ⚠️ Requires converting events to HoneyHive trace format
- ⚠️ Need to maintain span hierarchy manually

#### ❌ Integration Point 2: TracerProvider Injection

**Location:** `Telemetry.set_tracer()`

**Why it doesn't work:**
- CrewAI creates its own `TracerProvider`
- Sets it globally via `trace.set_tracer_provider(self.provider)`
- No way to inject our own provider without monkey-patching

#### ⚠️ Integration Point 3: LiteLLM Callbacks

**Location:** `litellm.completion(**params)`

**Possible but limited:**
- LiteLLM supports custom callbacks
- Could inject via `callbacks` parameter in llm.py
- But requires monkey-patching CrewAI's LLM class
- Misses agent/task context

---

## Phase 4: Architecture Deep Dive

### 4.1 Core Execution Flow

#### Crew Kickoff Flow

```python
# User code
crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
result = crew.kickoff(inputs={"topic": "AI agents"})
```

**Execution Path:**

```
1. crew.kickoff(inputs)
   └─> Emits: CrewKickoffStartedEvent
   
2. crew._run_sequential_process() or crew._run_hierarchical_process()
   └─> For each task:
   
3. task.execute(context, tools)
   └─> Emits: TaskStartedEvent
   └─> agent = task.agent
   
4. agent.execute_task(task, context, tools)
   └─> Emits: AgentExecutionStartedEvent
   └─> Enters agent reasoning loop:
   
5. agent._think_and_act()
   └─> Calls LLM to decide next action
   
6. llm.call(messages, tools)
   └─> Emits: LLMCallStartedEvent
   └─> litellm.completion(**params)
   └─> Emits: LLMCallCompletedEvent
   
7. If tool call needed:
   └─> Emits: ToolUsageStartedEvent
   └─> Execute tool
   └─> Emits: ToolUsageFinishedEvent
   └─> Back to step 5 (agent reasoning loop)
   
8. Agent completes task
   └─> Emits: AgentExecutionCompletedEvent
   └─> Emits: TaskCompletedEvent
   
9. All tasks complete
   └─> Emits: CrewKickoffCompletedEvent
   └─> Return CrewOutput
```

### 4.2 Agent Execution Details

**File:** `src/crewai/agent.py`

**Key methods:**
- `execute_task(task, context, tools)` - Main entry point
- `_think_and_act()` - Agent reasoning loop
- `_use_tool(tool_name, tool_input)` - Tool execution

**Agent attributes captured:**
- `role` - Agent's role (e.g., "Senior Researcher")
- `goal` - Agent's goal
- `backstory` - Agent's backstory
- `llm` - LLM configuration
- `tools` - Available tools
- `allow_delegation` - Can delegate to other agents
- `verbose` - Logging level

### 4.3 LLM Layer Details

**File:** `src/crewai/llm.py`

**Key methods:**
- `call(messages, tools, ...)` - Main LLM call
- `_stream_response()` - Streaming handler
- `_make_litellm_call()` - Actual LiteLLM invocation

**LLM call captures:**
- Model name
- Messages (prompt)
- Tools available
- Token usage (from response)
- Response content
- Tool calls (function calling)

### 4.4 Multi-Provider Support

CrewAI's LLM abstraction supports multiple providers through LiteLLM:

```python
# OpenAI
llm = LLM(model="gpt-4o-mini")

# Anthropic
llm = LLM(model="claude-3-5-sonnet-20241022")

# Local via Ollama
llm = LLM(model="ollama/llama3")

# Azure
llm = LLM(model="azure/gpt-4")
```

All providers emit the same events through the event bus.

---

## Integration Approach

### Tiered Strategy: LiteLLM First, CrewAI Events Second

#### Comparison: What Each Tier Captures

| Feature | Tier 1: LiteLLM Only | Tier 2: + CrewAI Events |
|---------|---------------------|------------------------|
| **LLM model name** | ✅ YES | ✅ YES |
| **Prompts/messages** | ✅ YES | ✅ YES |
| **Responses/completions** | ✅ YES | ✅ YES |
| **Token usage** | ✅ YES | ✅ YES |
| **Latency/timing** | ✅ YES | ✅ YES (more accurate) |
| **Agent role/goal** | ❌ NO | ✅ YES |
| **Task description** | ❌ NO | ✅ YES |
| **Crew hierarchy** | ❌ NO | ✅ YES |
| **Tool usage** | ❌ NO | ✅ YES |
| **Agent collaboration** | ❌ NO | ✅ YES |
| **Task outputs** | ❌ NO | ✅ YES |
| **Memory operations** | ❌ NO | ✅ YES |
| **Implementation effort** | LOW (1-2 days) | MEDIUM (8-11 days) |
| **Works with other frameworks** | ✅ YES (AutoGen, etc.) | ❌ NO (CrewAI only) |

#### Why This Strategy?

1. **LiteLLM is universal** - Works with CrewAI, AutoGen, LangGraph, and any custom code using LiteLLM
2. **Immediate value** - Users get LLM observability on day 1
3. **Incremental enhancement** - Add CrewAI events later for users who need agent context
4. **Cost-effective** - Don't build CrewAI-specific instrumentation if LiteLLM coverage is enough

#### Usage Pattern

```python
from honeyhive import HoneyHiveTracer
from honeyhive.instrumentation import litellm

# Basic setup - works for all LiteLLM-based frameworks
tracer = HoneyHiveTracer.init(project="my-project")
litellm.instrument(tracer_provider=tracer.provider)

# Use CrewAI - LLM calls are automatically traced
from crewai import Crew, Agent, Task
crew = Crew(agents=[...], tasks=[...])
result = crew.kickoff()  # ✅ LLM calls captured!
```

```python
# Power users: Add CrewAI events for full context
from honeyhive.instrumentation import litellm, crewai

tracer = HoneyHiveTracer.init(project="my-project")
litellm.instrument(tracer_provider=tracer.provider)
crewai.instrument(tracer_provider=tracer.provider)  # Adds agent/task context

# Now traces include both LLM data AND agent orchestration
```

---

### Recommended: Custom Event Listener (Medium Effort - Tier 2)

#### Why This Approach?

| Factor | Assessment |
|--------|------------|
| **Captures Agent Context** | ✅ YES - Full agent/task/tool metadata |
| **Captures LLM Calls** | ✅ YES - All LLM events with token usage |
| **Non-Invasive** | ✅ YES - No monkey-patching required |
| **Multi-Provider Support** | ✅ YES - Works with all LiteLLM providers |
| **Maintenance** | ✅ LOW - Stable event API |
| **Implementation Effort** | ⚠️ MEDIUM - Need event-to-span conversion |

#### Why NOT Standard OTel Integration?

| Approach | Works? | Why Not? |
|----------|--------|----------|
| **OpenAI Instrumentor** | ❌ NO | CrewAI uses LiteLLM, not OpenAI directly |
| **LiteLLM Instrumentor** | ⚠️ PARTIAL | Would capture LLM calls but miss agent context |
| **TracerProvider Injection** | ❌ NO | CrewAI sets its own global TracerProvider |
| **Event Listener** | ✅ YES | Clean API, full context, non-invasive |

---

## Proof of Concept

### Implementation Design

```python
# File: src/honeyhive/instrumentation/crewai.py

from typing import Any, Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.llm_events import (
    LLMCallStartedEvent,
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
)
from crewai.events.types.agent_events import (
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
)
from crewai.events.types.task_events import (
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
)
from crewai.events.types.tool_usage_events import (
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
    ToolUsageErrorEvent,
)
from crewai.events.types.crew_events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
)

class CrewAIInstrumentor:
    """Instrumentor for CrewAI that registers event listeners."""
    
    def __init__(self, tracer_provider=None):
        self.tracer_provider = tracer_provider
        self.tracer = trace.get_tracer(
            "honeyhive.crewai",
            tracer_provider=tracer_provider
        )
        
        # Track active spans for hierarchy
        self._crew_spans = {}  # crew_id -> span
        self._task_spans = {}  # task_id -> span
        self._agent_spans = {}  # (task_id, agent_role) -> span
        self._llm_spans = {}  # event_id -> span
        
        self._registered = False
    
    def instrument(self):
        """Register event listeners with CrewAI event bus."""
        if self._registered:
            return
        
        # Crew lifecycle
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            self._handle_crew_started(source, event)
        
        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            self._handle_crew_completed(source, event)
        
        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event):
            self._handle_crew_failed(source, event)
        
        # Task lifecycle
        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event):
            self._handle_task_started(source, event)
        
        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            self._handle_task_completed(source, event)
        
        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event):
            self._handle_task_failed(source, event)
        
        # Agent execution
        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_started(source, event):
            self._handle_agent_started(source, event)
        
        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_completed(source, event):
            self._handle_agent_completed(source, event)
        
        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_error(source, event):
            self._handle_agent_error(source, event)
        
        # LLM calls
        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_started(source, event):
            self._handle_llm_started(source, event)
        
        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_completed(source, event):
            self._handle_llm_completed(source, event)
        
        @crewai_event_bus.on(LLMCallFailedEvent)
        def on_llm_failed(source, event):
            self._handle_llm_failed(source, event)
        
        # Tool usage
        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_started(source, event):
            self._handle_tool_started(source, event)
        
        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_finished(source, event):
            self._handle_tool_finished(source, event)
        
        @crewai_event_bus.on(ToolUsageErrorEvent)
        def on_tool_error(source, event):
            self._handle_tool_error(source, event)
        
        self._registered = True
    
    def uninstrument(self):
        """Unregister event listeners."""
        # Blinker doesn't provide easy way to remove specific handlers
        # Would need to track handler references
        self._registered = False
    
    # Handler implementations
    
    def _handle_crew_started(self, source, event):
        """Handle crew kickoff started."""
        crew_id = str(source.id) if hasattr(source, 'id') else None
        
        span = self.tracer.start_span(
            f"Crew: {event.crew_name if hasattr(event, 'crew_name') else 'Unknown'}",
            kind=SpanKind.INTERNAL
        )
        
        # Set attributes
        span.set_attribute("crewai.crew.name", event.crew_name if hasattr(event, 'crew_name') else "Unknown")
        span.set_attribute("crewai.crew.id", crew_id or "unknown")
        
        if hasattr(source, 'process'):
            span.set_attribute("crewai.crew.process", str(source.process))
        
        if hasattr(source, 'agents'):
            span.set_attribute("crewai.crew.agent_count", len(source.agents))
        
        if hasattr(source, 'tasks'):
            span.set_attribute("crewai.crew.task_count", len(source.tasks))
        
        if crew_id:
            self._crew_spans[crew_id] = span
    
    def _handle_crew_completed(self, source, event):
        """Handle crew kickoff completed."""
        crew_id = str(source.id) if hasattr(source, 'id') else None
        
        if crew_id and crew_id in self._crew_spans:
            span = self._crew_spans[crew_id]
            
            if hasattr(event, 'output'):
                span.set_attribute("crewai.crew.output", str(event.output))
            
            span.set_status(Status(StatusCode.OK))
            span.end()
            del self._crew_spans[crew_id]
    
    def _handle_crew_failed(self, source, event):
        """Handle crew kickoff failed."""
        crew_id = str(source.id) if hasattr(source, 'id') else None
        
        if crew_id and crew_id in self._crew_spans:
            span = self._crew_spans[crew_id]
            
            if hasattr(event, 'error'):
                span.record_exception(event.error)
                span.set_status(Status(StatusCode.ERROR, str(event.error)))
            else:
                span.set_status(Status(StatusCode.ERROR))
            
            span.end()
            del self._crew_spans[crew_id]
    
    def _handle_task_started(self, source, event):
        """Handle task started."""
        task = event.task if hasattr(event, 'task') else source
        task_id = str(task.id) if hasattr(task, 'id') else None
        
        # Find parent crew span
        parent_context = None
        if hasattr(source, 'id'):
            crew_id = str(source.id)
            if crew_id in self._crew_spans:
                parent_context = trace.set_span_in_context(self._crew_spans[crew_id])
        
        span = self.tracer.start_span(
            f"Task: {task.description[:50] if hasattr(task, 'description') else 'Unknown'}",
            context=parent_context,
            kind=SpanKind.INTERNAL
        )
        
        # Set attributes
        if hasattr(task, 'description'):
            span.set_attribute("crewai.task.description", task.description)
        
        if hasattr(task, 'expected_output'):
            span.set_attribute("crewai.task.expected_output", task.expected_output)
        
        if hasattr(task, 'agent') and task.agent:
            span.set_attribute("crewai.task.agent_role", task.agent.role)
        
        if task_id:
            self._task_spans[task_id] = span
    
    def _handle_task_completed(self, source, event):
        """Handle task completed."""
        task = event.task if hasattr(event, 'task') else source
        task_id = str(task.id) if hasattr(task, 'id') else None
        
        if task_id and task_id in self._task_spans:
            span = self._task_spans[task_id]
            
            if hasattr(event, 'output') and event.output:
                span.set_attribute("crewai.task.output", str(event.output.raw if hasattr(event.output, 'raw') else event.output))
            
            span.set_status(Status(StatusCode.OK))
            span.end()
            del self._task_spans[task_id]
    
    def _handle_task_failed(self, source, event):
        """Handle task failed."""
        task = event.task if hasattr(event, 'task') else source
        task_id = str(task.id) if hasattr(task, 'id') else None
        
        if task_id and task_id in self._task_spans:
            span = self._task_spans[task_id]
            
            if hasattr(event, 'error'):
                span.record_exception(event.error)
                span.set_status(Status(StatusCode.ERROR, str(event.error)))
            else:
                span.set_status(Status(StatusCode.ERROR))
            
            span.end()
            del self._task_spans[task_id]
    
    def _handle_llm_started(self, source, event):
        """Handle LLM call started."""
        event_id = id(event)
        
        # Find parent task or agent span
        parent_context = None
        if hasattr(event, 'task_name') and event.task_name:
            # Try to find task span
            for task_id, span in self._task_spans.items():
                parent_context = trace.set_span_in_context(span)
                break
        
        span = self.tracer.start_span(
            f"LLM Call: {event.model if hasattr(event, 'model') else 'Unknown'}",
            context=parent_context,
            kind=SpanKind.CLIENT
        )
        
        # Set attributes
        if hasattr(event, 'model'):
            span.set_attribute("gen_ai.request.model", event.model)
        
        if hasattr(event, 'messages'):
            # Add messages as span event
            span.add_event(
                "gen_ai.messages",
                {
                    "gen_ai.messages": str(event.messages)[:1000]  # Truncate for safety
                }
            )
        
        if hasattr(event, 'agent_role'):
            span.set_attribute("crewai.agent.role", event.agent_role)
        
        if hasattr(event, 'task_description'):
            span.set_attribute("crewai.task.description", event.task_description[:100])
        
        self._llm_spans[event_id] = span
    
    def _handle_llm_completed(self, source, event):
        """Handle LLM call completed."""
        # Find corresponding start event span
        # This is tricky - we need to correlate completion with start
        # For now, end the most recent LLM span
        
        if self._llm_spans:
            # Get most recent span (LIFO)
            event_id = list(self._llm_spans.keys())[-1]
            span = self._llm_spans[event_id]
            
            # Set completion attributes
            if hasattr(event, 'usage'):
                usage = event.usage
                if isinstance(usage, dict):
                    if 'prompt_tokens' in usage:
                        span.set_attribute("gen_ai.usage.prompt_tokens", usage['prompt_tokens'])
                    if 'completion_tokens' in usage:
                        span.set_attribute("gen_ai.usage.completion_tokens", usage['completion_tokens'])
                    if 'total_tokens' in usage:
                        span.set_attribute("gen_ai.usage.total_tokens", usage['total_tokens'])
            
            if hasattr(event, 'response'):
                # Add response as span event
                response_str = str(event.response)[:1000]  # Truncate
                span.add_event(
                    "gen_ai.response",
                    {
                        "gen_ai.response.content": response_str
                    }
                )
            
            span.set_status(Status(StatusCode.OK))
            span.end()
            del self._llm_spans[event_id]
    
    def _handle_llm_failed(self, source, event):
        """Handle LLM call failed."""
        if self._llm_spans:
            event_id = list(self._llm_spans.keys())[-1]
            span = self._llm_spans[event_id]
            
            if hasattr(event, 'error'):
                span.record_exception(event.error)
                span.set_status(Status(StatusCode.ERROR, str(event.error)))
            else:
                span.set_status(Status(StatusCode.ERROR))
            
            span.end()
            del self._llm_spans[event_id]
    
    def _handle_agent_started(self, source, event):
        """Handle agent execution started."""
        # Create agent span as child of task span
        pass  # Implementation similar to task handling
    
    def _handle_agent_completed(self, source, event):
        """Handle agent execution completed."""
        pass
    
    def _handle_agent_error(self, source, event):
        """Handle agent execution error."""
        pass
    
    def _handle_tool_started(self, source, event):
        """Handle tool usage started."""
        # Create tool span as child of agent span
        pass
    
    def _handle_tool_finished(self, source, event):
        """Handle tool usage finished."""
        pass
    
    def _handle_tool_error(self, source, event):
        """Handle tool usage error."""
        pass


# Public API

_instrumentor = None

def instrument(tracer_provider=None):
    """Instrument CrewAI to send traces to HoneyHive."""
    global _instrumentor
    
    if _instrumentor is None:
        _instrumentor = CrewAIInstrumentor(tracer_provider=tracer_provider)
    
    _instrumentor.instrument()
    return _instrumentor

def uninstrument():
    """Remove CrewAI instrumentation."""
    global _instrumentor
    
    if _instrumentor is not None:
        _instrumentor.uninstrument()
        _instrumentor = None
```

### Usage Example

```python
# example_crewai_instrumentation.py

import os
from honeyhive import HoneyHiveTracer
from honeyhive.instrumentation import crewai as crewai_instrumentation
from crewai import Agent, Task, Crew, Process

# Initialize HoneyHive
tracer = HoneyHiveTracer.init(
    project="crewai-demo",
    api_key=os.getenv("HONEYHIVE_API_KEY")
)

# Instrument CrewAI
crewai_instrumentation.instrument(tracer_provider=tracer.provider)

# Disable CrewAI's own telemetry (optional but recommended)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# Define agents
researcher = Agent(
    role="Senior Researcher",
    goal="Research AI agent frameworks",
    backstory="You're an expert in AI and software engineering",
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Write clear documentation about AI agents",
    backstory="You excel at explaining complex technical concepts",
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the latest trends in AI agent frameworks, focusing on CrewAI",
    expected_output="A comprehensive report on AI agent frameworks",
    agent=researcher
)

write_task = Task(
    description="Write a blog post based on the research about AI agents",
    expected_output="A well-written blog post about AI agents",
    agent=writer
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True
)

# Execute crew - traces will be sent to HoneyHive!
result = crew.kickoff()

print(f"\n\nResult:\n{result}")
```

### Expected Trace Structure in HoneyHive

```
Crew: crew_name
├── Task: Research the latest trends in AI agent frameworks
│   ├── Agent Execution: Senior Researcher
│   │   ├── LLM Call: gpt-4o-mini
│   │   │   └── [prompt, response, tokens captured]
│   │   ├── Tool Usage: search_tool
│   │   │   └── [tool input/output]
│   │   └── LLM Call: gpt-4o-mini (final answer)
│   └── [task output captured]
├── Task: Write a blog post based on the research
│   ├── Agent Execution: Technical Writer
│   │   ├── LLM Call: gpt-4o-mini
│   │   │   └── [prompt, response, tokens captured]
│   │   └── LLM Call: gpt-4o-mini (final answer)
│   └── [task output captured]
└── [crew output captured]
```

---

## Testing Strategy

### Test Suite Structure

```python
# tests/integration/test_crewai_instrumentation.py

import pytest
import os
from unittest.mock import Mock, patch
from honeyhive import HoneyHiveTracer
from honeyhive.instrumentation import crewai as crewai_instrumentation
from crewai import Agent, Task, Crew, Process

@pytest.fixture
def tracer():
    """Initialize HoneyHive tracer for testing."""
    return HoneyHiveTracer.init(
        project="crewai-test",
        api_key=os.getenv("HONEYHIVE_API_KEY") or "test-key"
    )

@pytest.fixture
def instrumented_crewai(tracer):
    """Instrument CrewAI for testing."""
    os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
    crewai_instrumentation.instrument(tracer_provider=tracer.provider)
    yield
    crewai_instrumentation.uninstrument()

def test_simple_crew_execution(instrumented_crewai, tracer):
    """Test that a simple crew execution produces traces."""
    
    # Create simple agent and task
    agent = Agent(
        role="Test Agent",
        goal="Complete the test task",
        backstory="A test agent",
        llm="gpt-4o-mini"
    )
    
    task = Task(
        description="Say hello",
        expected_output="A greeting",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    
    # Execute
    with tracer.trace(session_name="test_crewai"):
        result = crew.kickoff()
    
    # Verify result
    assert result is not None
    
    # TODO: Add assertions for trace data in HoneyHive

def test_multi_agent_collaboration(instrumented_crewai, tracer):
    """Test that multi-agent crews produce correct trace hierarchy."""
    
    researcher = Agent(
        role="Researcher",
        goal="Research topics",
        backstory="Expert researcher",
        llm="gpt-4o-mini"
    )
    
    writer = Agent(
        role="Writer",
        goal="Write content",
        backstory="Expert writer",
        llm="gpt-4o-mini"
    )
    
    research_task = Task(
        description="Research AI agents",
        expected_output="Research report",
        agent=researcher
    )
    
    write_task = Task(
        description="Write about AI agents",
        expected_output="Article",
        agent=writer
    )
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process=Process.sequential
    )
    
    with tracer.trace(session_name="test_multi_agent"):
        result = crew.kickoff()
    
    assert result is not None
    # TODO: Verify trace hierarchy

def test_tool_usage_captured(instrumented_crewai, tracer):
    """Test that tool usage is captured in traces."""
    from crewai_tools import SerperDevTool
    
    search_tool = SerperDevTool()
    
    agent = Agent(
        role="Researcher",
        goal="Research topics",
        backstory="Expert researcher",
        tools=[search_tool],
        llm="gpt-4o-mini"
    )
    
    task = Task(
        description="Search for information about CrewAI",
        expected_output="Search results",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    
    with tracer.trace(session_name="test_tools"):
        result = crew.kickoff()
    
    # TODO: Verify tool usage in traces

def test_error_handling(instrumented_crewai, tracer):
    """Test that errors are captured in traces."""
    
    agent = Agent(
        role="Test Agent",
        goal="Fail gracefully",
        backstory="A test agent",
        llm="invalid-model"  # This should cause an error
    )
    
    task = Task(
        description="This will fail",
        expected_output="Error",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    
    with pytest.raises(Exception):
        with tracer.trace(session_name="test_errors"):
            crew.kickoff()
    
    # TODO: Verify error captured in traces

def test_token_usage_captured(instrumented_crewai, tracer):
    """Test that token usage is captured in traces."""
    
    agent = Agent(
        role="Test Agent",
        goal="Complete task",
        backstory="A test agent",
        llm="gpt-4o-mini"
    )
    
    task = Task(
        description="Write a short paragraph about AI",
        expected_output="Paragraph about AI",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    
    with tracer.trace(session_name="test_tokens"):
        result = crew.kickoff()
    
    # TODO: Verify token usage in traces

def test_parallel_task_execution(instrumented_crewai, tracer):
    """Test parallel task execution produces correct traces."""
    # CrewAI supports parallel task execution
    # Test that concurrent tasks are captured correctly
    pass

def test_hierarchical_process(instrumented_crewai, tracer):
    """Test hierarchical process (manager agent) produces correct traces."""
    # CrewAI supports hierarchical process with a manager agent
    # Test that the manager's coordination is captured
    pass

def test_flow_integration(instrumented_crewai, tracer):
    """Test that CrewAI Flows are instrumented correctly."""
    # CrewAI has a Flow API for event-driven workflows
    # Test that Flows produce correct traces
    pass
```

### Manual Testing Checklist

- [ ] Install CrewAI: `pip install crewai`
- [ ] Run simple example with instrumentation
- [ ] Verify traces appear in HoneyHive dashboard
- [ ] Check span hierarchy is correct
- [ ] Verify LLM calls have token usage
- [ ] Verify agent/task metadata is captured
- [ ] Test with different LLM providers (OpenAI, Anthropic, Ollama)
- [ ] Test tool usage is captured
- [ ] Test error scenarios produce error spans
- [ ] Test performance (overhead should be minimal)

---

## Limitations & Considerations

### Limitations

1. **Event Correlation Challenge**
   - Challenge: Correlating `LLMCallStartedEvent` with `LLMCallCompletedEvent`
   - CrewAI events don't have correlation IDs
   - Current solution: Use LIFO stack (most recent span)
   - Better solution: Track event IDs or timestamps

2. **Span Context Propagation**
   - Challenge: Maintaining correct span hierarchy across events
   - Events don't include parent span context
   - Current solution: Track active spans per crew/task/agent
   - May have edge cases in parallel execution

3. **Event Timing**
   - Events are emitted but may not have precise timestamps
   - May need to add custom timing for accurate duration tracking

4. **Memory Overhead**
   - Tracking active spans in dictionaries adds memory overhead
   - Should clean up completed spans promptly
   - Consider adding span limit for long-running crews

5. **Streaming Support**
   - CrewAI emits `LLMStreamChunkEvent` for streaming responses
   - Current POC doesn't handle streaming
   - Should add span events for each chunk

6. **Multi-Provider Testing**
   - Need to test with various LLM providers
   - Token usage format may differ per provider
   - Some providers may not emit all events

### Considerations

1. **Disable CrewAI Telemetry**
   - Recommend users set `CREWAI_DISABLE_TELEMETRY=true`
   - Avoids conflict with CrewAI's own OTel telemetry
   - Reduces overhead

2. **Performance Impact**
   - Event listener adds overhead to each event
   - Should benchmark performance impact
   - Consider making instrumentation opt-in per event type

3. **Compatibility**
   - Test with different CrewAI versions
   - Event API may change in future versions
   - Monitor CrewAI releases for breaking changes

4. **Documentation Needs**
   - Need clear setup instructions
   - Document which CrewAI features are supported
   - Provide troubleshooting guide

5. **Alternative: LiteLLM Instrumentation**
   - Could also instrument LiteLLM directly
   - Would work for all frameworks using LiteLLM
   - But would miss agent/task context
   - Consider as complementary approach

---

## Next Steps

### Recommended Implementation Order

#### Priority 1: LiteLLM Instrumentation (1-2 days)
- [ ] Analyze LiteLLM SDK (separate analysis report)
- [ ] Create `src/honeyhive/instrumentation/litellm.py`
- [ ] Test with CrewAI, AutoGen, custom code
- [ ] Document LiteLLM integration
- [ ] **Result:** Basic LLM observability for ALL LiteLLM-based frameworks

#### Priority 2: CrewAI Event Listener (8-11 days) - Optional Enhancement
Only implement if users need agent/task context beyond basic LLM calls.

### Phase 1: Prototype (Estimated: 2-3 days)

- [ ] Create `src/honeyhive/instrumentation/crewai.py`
- [ ] Implement `CrewAIInstrumentor` class
- [ ] Implement event handlers for:
  - [ ] Crew lifecycle events
  - [ ] Task lifecycle events
  - [ ] LLM call events
  - [ ] Tool usage events (basic)
- [ ] Create basic example script
- [ ] Manual testing with simple crew

### Phase 2: Polish (Estimated: 2-3 days)

- [ ] Improve span correlation logic
- [ ] Add streaming support
- [ ] Add agent execution events
- [ ] Add memory/knowledge events
- [ ] Handle edge cases (errors, timeouts)
- [ ] Add comprehensive docstrings
- [ ] Performance optimization

### Phase 3: Testing (Estimated: 2 days)

- [ ] Write integration tests
- [ ] Test with multiple LLM providers:
  - [ ] OpenAI
  - [ ] Anthropic
  - [ ] Ollama (local)
  - [ ] Azure OpenAI
- [ ] Test with CrewAI Flows
- [ ] Test hierarchical process
- [ ] Test parallel task execution
- [ ] Performance benchmarking

### Phase 4: Documentation (Estimated: 1-2 days)

- [ ] Create integration guide: `docs/how-to/integrations/crewai.rst`
- [ ] Add to compatibility matrix
- [ ] Create example notebooks
- [ ] Write troubleshooting guide
- [ ] Update README with CrewAI support

### Phase 5: Release (Estimated: 1 day)

- [ ] Code review
- [ ] Update CHANGELOG
- [ ] Version bump
- [ ] Release notes
- [ ] Announce on community channels

### Total Estimated Effort: 8-11 days

---

## Alternative Approaches Considered

### Approach 1: LiteLLM Instrumentation (RECOMMENDED TIER 1)

**Approach:** Instrument LiteLLM directly - captures all LLM calls from CrewAI and other frameworks

**Pros:**
- ✅ Works for ANY framework using LiteLLM (CrewAI, AutoGen, LangGraph, custom code)
- ✅ Simpler implementation (1-2 days vs 8-11 days)
- ✅ No dependency on CrewAI event system
- ✅ Immediate value on day 1
- ✅ Universal solution

**Cons:**
- ⚠️ Misses agent/task/tool context (but captures core LLM data)
- ⚠️ Can't show crew structure
- ⚠️ Less useful for multi-agent workflow debugging

**Verdict:** ✅ **RECOMMENDED as Tier 1** - Start here, add CrewAI events later if needed

### Approach 2: CrewAI Event Listener (RECOMMENDED TIER 2)

**Approach:** Register event listeners with CrewAI's event bus to capture agent/task/crew context

**Pros:**
- ✅ Captures complete agent context (role, goal, backstory)
- ✅ Shows crew structure and task flow
- ✅ Non-invasive (no monkey-patching)
- ✅ Works with all LLM providers via LiteLLM
- ✅ Stable, documented API

**Cons:**
- ⚠️ CrewAI-specific (doesn't help with other frameworks)
- ⚠️ Medium implementation effort (8-11 days)
- ⚠️ Requires span correlation logic

**Verdict:** ✅ **RECOMMENDED as Tier 2** - Add after LiteLLM for full context

### Approach 3: Monkey-Patching (NOT RECOMMENDED)

**Approach:** Monkey-patch CrewAI's `Crew.kickoff()`, `Agent.execute_task()`, `LLM.call()` methods

**Pros:**
- Full control over instrumentation points
- Can ensure correct span hierarchy

**Cons:**
- ❌ Fragile - breaks with CrewAI updates
- ❌ Hard to maintain
- ❌ May conflict with CrewAI internals

**Verdict:** ❌ Not recommended - too brittle

### Approach 4: Fork CrewAI (NOT RECOMMENDED)

**Approach:** Fork CrewAI and add HoneyHive instrumentation directly

**Pros:**
- Perfect integration
- No limitations

**Cons:**
- ❌ Maintenance nightmare
- ❌ Users need to use our fork
- ❌ Not scalable

**Verdict:** ❌ Not recommended

### Approach 5: Wrapper API (NOT RECOMMENDED)

**Approach:** Create a wrapper around CrewAI APIs that adds instrumentation

**Pros:**
- Clean separation
- Easy to maintain

**Cons:**
- Users need to change their code
- Need to wrap every CrewAI class
- Doesn't work with existing code

**Verdict:** ⚠️ Possible, but less user-friendly than event listeners

---

## References

### CrewAI Documentation
- Homepage: https://crewai.com
- Docs: https://docs.crewai.com
- GitHub: https://github.com/crewAIInc/crewAI
- Examples: https://github.com/crewAIInc/crewAI-examples

### Key Files Analyzed
- `src/crewai/crew.py` (1,576 lines) - Core orchestration
- `src/crewai/llm.py` (1,295 lines) - LLM abstraction
- `src/crewai/agent.py` (869 lines) - Agent implementation
- `src/crewai/telemetry/telemetry.py` (896 lines) - OTel implementation
- `src/crewai/events/event_bus.py` - Event system
- `src/crewai/events/listeners/tracing/trace_listener.py` (471 lines) - Event-based tracing

### Technologies
- **LiteLLM:** https://docs.litellm.ai/
- **Blinker:** https://pythonhosted.org/blinker/
- **OpenTelemetry:** https://opentelemetry.io/

---

## Changelog

- **2025-10-15:** Initial analysis completed
  - Comprehensive analysis of CrewAI 0.203.1
  - Identified event-driven architecture as integration point
  - Created POC design with event listeners
  - Documented limitations and testing strategy

---

## Appendix: CrewAI Event System Reference

### Event Class Hierarchy

```python
# Base event class
@dataclass
class BaseEvent:
    timestamp: datetime
    source_id: str

# Event types inherit from BaseEvent
@dataclass
class LLMCallStartedEvent(BaseEvent):
    model: str
    messages: list[dict]
    agent_role: str
    task_name: str
    task_description: str

@dataclass  
class LLMCallCompletedEvent(BaseEvent):
    model: str
    response: Any
    usage: dict  # {prompt_tokens, completion_tokens, total_tokens}

# And many more event types...
```

### Event Registration Example

```python
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.llm_events import LLMCallCompletedEvent

# Register handler via decorator
@crewai_event_bus.on(LLMCallCompletedEvent)
def my_handler(source: Any, event: LLMCallCompletedEvent):
    print(f"LLM call completed: {event.model}")
    print(f"Tokens: {event.usage}")
```

### All Available Event Types

See "Event Types Available" section in [3.3 Custom Event-Driven Tracing System](#33-custom-event-driven-tracing-system)

---

**END OF ANALYSIS REPORT**

