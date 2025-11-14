# HoneyHive Event Schema & Integration Patterns

**Standard for creating correct integration fixtures that produce optimal HoneyHive event data patterns for frontend rendering and semantic consistency.**

---

## 🎯 TL;DR - HoneyHive Event Schema Quick Reference

**Keywords for search**: honeyhive event schema, fixture patterns, integration fixtures, event type semantics, model vs tool events, chat history patterns, tool inputs outputs, frontend rendering patterns, zod schema validation, instrumentor integration, span attribute mapping, optimal data patterns, fixture creation, ingestion service compatibility, event schema conventions

**Core Principle:** HoneyHive event fixtures are *specifications* that define optimal ingestion behavior, not just validation of current state. The schema is flexible, but specific patterns produce optimal frontend rendering.

**Critical Insight:** Event type semantics must match data structure - MODEL events contain conversations (`chat_history`, `role/content`), TOOL events contain parameters and results (`direct params`, `message`), not conversations.

**4 Event Types & Their Optimal Patterns:**
1. **MODEL** (LLM calls) → `inputs.chat_history` + `outputs.role/content`
2. **TOOL** (function calls) → `inputs.{params}` + `outputs.message` (NOT role/content!)
3. **CHAIN** (orchestration) → Flexible inputs/outputs based on chain type
4. **SESSION** (trace root) → Metadata and user properties

**Common Fixture Mistakes:**
- ❌ Tool spans with `inputs.chat_history` (semantic mismatch)
- ❌ Tool spans with `outputs.role/content` (breaks frontend rendering)
- ❌ **CHAIN spans forced into `outputs.role/content` format** (chain is NOT a model!)
- ❌ Model spans without `chat_history` (poor table rendering)
- ❌ Missing `config.model` or `config.provider` (incomplete context)
- ❌ Token counts in `metrics` instead of `metadata` (wrong namespace - tokens need session aggregation!)

**Fixture as Specification Philosophy:**
- ✅ Fixture `expected` section = desired ingestion output
- ✅ Test failures = gaps in ingestion service mapping
- ✅ Correct fixtures guide ingestion service improvements
- ❌ NOT just validation - fixtures drive implementation

**Frontend Rendering Impact:**
- `inputs.chat_history` → Renders as multi-turn conversation in table
- `outputs.role/content` → Renders as markdown message
- `outputs.message` → Renders as JSON/text (tool results)
- `config.*` → Displayed in event detail panel
- `metadata.*` → Displayed in metadata section (includes token counts!)
- `metrics.*` → Displayed in metrics panel (cost, timing - NOT tokens!)

**When Creating Fixtures:**
1. Identify span kind: MODEL, TOOL, CHAIN
2. Apply semantic pattern (not just OTel attributes)
3. Validate frontend rendering expectations
4. Test in HoneyHive UI (does it look right?)

---

## ❓ Questions This Answers

1. "What is the HoneyHive event schema structure?"
2. "How do I create correct integration fixtures?"
3. "What's the difference between MODEL and TOOL event patterns?"
4. "Why can't tool inputs use chat_history?"
5. "What data patterns produce optimal frontend rendering?"
6. "Where do token metrics belong - metadata or metrics?"
7. "What does the Zod schema validate?"
8. "How does the frontend render inputs and outputs?"
9. "What are common fixture mistakes from PR #623?"
10. "Why do fixture tests fail after creation?"
11. "How do I validate fixture semantic correctness?"
12. "What config fields are required for MODEL events?"
13. "How should tool results be structured?"
14. "What's the fixture-as-specification philosophy?"
15. "How do I know if my fixture will render correctly?"
16. "What attributes should go in config vs metadata?"
17. "How does event_type affect data structure expectations?"
18. "What makes a fixture 'correct' vs 'valid'?"
19. "How do I structure chain event inputs/outputs?"
20. "What's the relationship between OTel spans and HoneyHive events?"

---

## 🎯 Purpose

Define the HoneyHive event schema structure, optimal data patterns for each event type, and how to create semantically correct integration fixtures that produce excellent frontend rendering and developer experience.

**Key Distinction:** Valid vs Optimal
- **Valid**: Passes Zod schema validation (basic structure correct)
- **Optimal**: Produces excellent frontend rendering and semantic clarity

This standard ensures all integration fixtures specify optimal patterns that guide ingestion service improvements.

---

## 🚨 The Problem (Without This Standard)

**Integration Fixture Mistakes:**
- ❌ Tool spans wrapped in `chat_history` (semantic mismatch - tools aren't conversations)
- ❌ Tool outputs using `role/content` (frontend renders as chat message, not tool result)
- ❌ Token metrics scattered between `metadata` and `metrics` (inconsistent access patterns)
- ❌ Missing required `config` fields (incomplete event context)
- ❌ Inconsistent patterns across instrumentors (poor developer experience)

**Impact:**
- 🔴 Frontend table shows garbled data (empty columns, wrong formatting)
- 🔴 Event detail view renders incorrectly (tools look like LLM calls)
- 🔴 Ingestion service perpetuates wrong patterns (no specification to fix against)
- 🔴 Customer traces look broken (poor observability experience)
- 🔴 Knowledge loss (PR #623 learnings not preserved in discoverable form)

**Real Example from PR #623:**
```json
// ❌ BEFORE: Google ADK tool fixture (WRONG)
{
  "expected": {
    "inputs": {
      "chat_history": [{             // Tool wrapped as conversation!
        "role": "user",
        "content": "{\"city\": \"New York\"}"
      }]
    },
    "outputs": {
      "role": "assistant",           // Tool result as chat message!
      "content": "{...tool response...}"
    }
  }
}

// ✅ AFTER: Corrected pattern
{
  "expected": {
    "inputs": {
      "city": "New York"              // Direct tool parameters
    },
    "outputs": {
      "message": "{...tool response...}"  // Tool result as message
    }
  }
}
```

---

## 📋 The Standard - HoneyHive Event Schema

### Core Schema Structure (Zod)

**All HoneyHive events share this base structure:**

```typescript
{
  event_id: string (UUID),
  event_type: "model" | "tool" | "chain" | "session",
  event_name?: string,
  inputs?: Record<string, unknown>,        // Event-type specific
  outputs?: Record<string, unknown> | Array<...>,  // Event-type specific
  config?: Record<string, unknown>,        // Provider/model config
  metadata?: Record<string, unknown>,      // Telemetry, span kind, etc.
  metrics?: Record<string, unknown>,       // Tokens, cost, latency
  feedback?: Record<string, unknown>,      // User feedback
  user_properties?: Record<string, unknown>,
  error?: string | null,
  parent_id?: string (UUID) | null,
  session_id?: string (UUID),
  project_id?: string,
  tenant?: string,
  source?: string,
  children_ids?: string[],
  start_time?: number,
  end_time?: number,
  duration?: number
}
```

**Schema Philosophy:**
- ✅ **Flexible by design** - Uses `Record<string, unknown>` with `.passthrough()`
- ✅ **Forward compatible** - Additional fields allowed
- ✅ **Validation, not constraint** - Ensures basic structure, allows innovation

---

## 🎨 Optimal Patterns by Event Type

### 1. MODEL Events (LLM Calls)

**Semantic Definition:** LLM inference requests (chat, completion, embeddings)

**REQUIRED for Optimal Frontend:**
```json
{
  "event_type": "model",
  "inputs": {
    "chat_history": [                    // ✅ REQUIRED for conversation rendering
      {
        "role": "user",                  // ✅ REQUIRED
        "content": "user message"        // ✅ REQUIRED
      },
      {
        "role": "assistant",
        "content": "previous response"
      }
    ]
  },
  "outputs": {
    "role": "assistant",                 // ✅ REQUIRED for markdown rendering
    "content": "model response text"     // ✅ REQUIRED
  },
  "config": {
    "model": "gpt-4",                    // ✅ REQUIRED
    "provider": "openai",                // ✅ REQUIRED
    "temperature": 0.7,                  // ✅ RECOMMENDED
    "max_tokens": 1000                   // ✅ RECOMMENDED
  },
  "metrics": {
    "cost": 0.00234                      // ✅ Cost in metrics (NOT tokens!)
  },
  "metadata": {
    "provider": "openai",                // ✅ OK to duplicate from config
    "system": "openai",
    "model_name": "gpt-4",
    "response_model": "gpt-4-0125-preview",
    "prompt_tokens": 50,                 // ✅ REQUIRED - tokens in metadata!
    "completion_tokens": 75,             // ✅ REQUIRED
    "total_tokens": 125,                 // ✅ REQUIRED
    "finish_reason": "stop"
  }
}
```

**Frontend Rendering:**
- 📊 **Table view**: Displays `inputs.chat_history[0].content` (first user message)
- 💬 **Detail view**: Renders full conversation with markdown formatting
- ⚙️ **Config panel**: Shows model, provider, temperature
- 📈 **Metrics panel**: Displays token counts and cost

---

### 2. TOOL Events (Function Calls)

**Semantic Definition:** Function/tool executions (NOT LLM calls, NOT conversations)

**REQUIRED for Optimal Frontend:**
```json
{
  "event_type": "tool",
  "inputs": {
    "city": "New York",                  // ✅ Direct parameters (NOT chat_history!)
    "units": "metric"                    // ✅ Flat parameter structure
  },
  "outputs": {
    "message": "Tool execution result"   // ✅ Use 'message' (NOT role/content!)
  },
  "config": {
    "tool_name": "get_weather",          // ✅ REQUIRED
    "tool_description": "Get weather",   // ✅ RECOMMENDED
    "tool_type": "FunctionTool"          // ✅ RECOMMENDED
  },
  "metadata": {
    "span_kind": "TOOL",
    "operation_name": "execute_tool",
    "tool_call_id": "call_abc123"
  }
}
```

**❌ ANTI-PATTERN (Common Mistake):**
```json
{
  "event_type": "tool",
  "inputs": {
    "chat_history": [{                   // ❌ WRONG! Tools don't have conversations!
      "role": "user",
      "content": "{\"city\": \"New York\"}"
    }]
  },
  "outputs": {
    "role": "assistant",                 // ❌ WRONG! Tool results aren't chat messages!
    "content": "tool response"
  }
}
```

**Why This Matters:**
- 🔴 `chat_history` → Frontend renders as conversation (semantically wrong)
- 🔴 `role/content` → Markdown rendering for chat (tool results should be JSON/text)
- ✅ Direct params → Frontend displays as key-value parameters
- ✅ `message` → Frontend renders as tool result (proper formatting)

**Frontend Rendering:**
- 📊 **Table view**: Displays `inputs` as key-value pairs
- 🔧 **Detail view**: Renders `outputs.message` as text/JSON (NOT markdown)
- ⚙️ **Config panel**: Shows tool name and description
- 🏷️ **Event type icon**: Shows tool icon (not LLM icon)

---

### 3. CHAIN Events (Orchestration)

**Semantic Definition:** Multi-step workflows, agent loops, orchestration

**⚠️ CRITICAL: CHAIN events use TOOL-LIKE flexible structure, NOT MODEL-like chat format!**

**Standard Pattern (Flexible Structure):**
```json
{
  "event_type": "chain",
  "inputs": {
    // Flexible structure based on chain semantics
    "query": "What's the weather in NYC?",           // ✅ Structured input
    "parameters": {...},                             // ✅ Chain parameters
    "system_instructions": "You are helpful..."      // ✅ If applicable
  },
  "outputs": {
    // Flexible structure based on chain results
    "result": "It's 72°F and sunny!",               // ✅ Structured output
    "status": "success",                            // ✅ Chain status
    "metadata": {...}                                // ✅ Chain metadata
  },
  "config": {
    "agent_name": "WeatherAgent",                   // ✅ RECOMMENDED (for agents)
    "workflow_name": "weather_workflow",            // ✅ RECOMMENDED (for workflows)
    "model": "gpt-4",                               // ✅ If using LLM
    "provider": "openai"                            // ✅ If using LLM
  },
  "metadata": {
    "span_kind": "CHAIN",
    "tools_used": ["get_weather"],                  // ✅ If tools used
    "iterations": 2,                                // ✅ For multi-step
    "prompt_tokens": 156,                           // ✅ Token counts in metadata!
    "completion_tokens": 89,
    "total_tokens": 245
  }
}
```

**Dual Behavior: Embedding Model Messages (When Applicable):**

**IF** the chain contains model messages (e.g., agent conversations), include them as **fields within the flexible structure**:

```json
{
  "event_type": "chain",
  "inputs": {
    "query": "What's the weather in NYC?",           // ✅ Structured agent input
    "chat_history": [                                // ✅ Model messages as a field
      {
        "role": "user",
        "content": "Previous question..."
      },
      {
        "role": "assistant",
        "content": "Previous answer..."
      }
    ]
  },
  "outputs": {
    "result": "It's 72°F and sunny!",               // ✅ Structured agent result
    "conversation": [                                // ✅ Model messages as a field
      {
        "role": "user",
        "content": "What's the weather in NYC?"
      },
      {
        "role": "assistant",
        "content": "It's 72°F and sunny!"
      }
    ]
  }
}
```

**Key Principle:** 
- ✅ **CHAIN structure** = Flexible (like TOOL), NOT forced into chat format
- ✅ **Model messages** = Go in `chat_history`/`conversation` fields **within** that structure
- ❌ **DO NOT** force entire chain into `outputs.role/content` format

**Why This Matters:**
- ✅ Preserves structured data (query, result, status, etc.)
- ✅ Allows frontend to render chain as orchestration (not as single LLM call)
- ✅ Model messages still available for conversation views when present
- ✅ Aligns with boss guidance: "tool like content for chain types"

---

### 4. SESSION Events (Trace Root)

**Semantic Definition:** Top-level trace container for multi-event traces

```json
{
  "event_type": "session",
  "inputs": {},
  "outputs": {},
  "user_properties": {                   // ✅ User context
    "user_id": "user_123",
    "environment": "production"
  },
  "metadata": {
    "session_name": "customer_support",
    "total_events": 15,
    "trace_id": "abc123"
  }
}
```

---

## 🗂️ Attribute Namespacing Rules

**Critical:** Different data types belong in specific namespaces for optimal frontend access.

### config.*
**Purpose:** Provider/model configuration for LLM calls

**REQUIRED:**
- `config.model` - Model identifier
- `config.provider` - Provider name (openai, anthropic, etc.)

**RECOMMENDED:**
- `config.temperature` - Sampling temperature
- `config.max_tokens` - Token limit
- `config.top_p` - Nucleus sampling
- `config.tool_name` - For tool events
- `config.tool_description` - For tool events

### metrics.*
**Purpose:** Cost and timing measurements (NOT token counts!)

**Cost Metrics:**
- `metrics.cost` - Cost in USD (from `gen_ai.usage.cost` or `operation.cost`)
- `metrics.cost_usd` - Alternative cost field

**Timing Metrics:**
- `metrics.ttft_ms` - Time to first token (from `gen_ai.server.ttft`)
- `metrics.latency_ms` - Total latency
- `metrics.duration_ms` - Request duration

**⚠️ CRITICAL:** Token counts go in `metadata.*`, NOT `metrics.*`!

**❌ ANTI-PATTERN:**
```json
{
  "metrics": {
    "prompt_tokens": 50,      // ❌ WRONG namespace!
    "completion_tokens": 75,  // ❌ Should be in metadata!
    "total_tokens": 125       // ❌ Should be in metadata!
  }
}
```

**✅ CORRECT:**
```json
{
  "metrics": {
    "cost": 0.00234            // ✅ Cost in metrics
  },
  "metadata": {
    "prompt_tokens": 50,       // ✅ Tokens in metadata
    "completion_tokens": 75,
    "total_tokens": 125
  }
}
```

### metadata.*
**Purpose:** Telemetry, span semantics, auxiliary data, **AND TOKEN COUNTS**

**Token Metrics (REQUIRED for MODEL events):**
- `metadata.prompt_tokens` - Input token count (session-aggregatable)
- `metadata.completion_tokens` - Output token count (session-aggregatable)
- `metadata.total_tokens` - Total token count (session-aggregatable)

**Why tokens in metadata?** Token counts need session-level aggregation. The ingestion service sums these across all events in a session to show total session cost/usage. Cost goes in `metrics` because it's already aggregated per-event.

**Other Metadata Fields:**
- `metadata.provider` - Can duplicate config.provider
- `metadata.system` - System identifier
- `metadata.span_kind` - OTel span kind (MODEL, TOOL, CHAIN)
- `metadata.operation_name` - Operation type
- `metadata.finish_reason` - Completion reason
- `metadata.response_model` - Actual model used (vs requested)
- `metadata.response_id` - Response ID from provider
- `metadata.instrumentor` - Instrumentor name (openlit, traceloop, etc.)
- `metadata.sdk_version` - Instrumentor version

---

## ✅ Fixture Creation Checklist

Use this checklist when creating integration fixtures:

### Semantic Validation
- [ ] Event type matches semantic content?
  - MODEL = LLM inference (chat, completion)
  - TOOL = Function/tool execution
  - CHAIN = Multi-step workflow
  - SESSION = Trace container
- [ ] Data structure matches event type semantics?
  - MODEL → `chat_history` + `role/content`
  - TOOL → Direct params + `message`
  - CHAIN → Context-dependent
  - SESSION → User properties + metadata

### MODEL Event Checklist
- [ ] `inputs.chat_history` present with role/content structure?
- [ ] `outputs.role` = "assistant"?
- [ ] `outputs.content` contains response text?
- [ ] `config.model` specified?
- [ ] `config.provider` specified?
- [ ] Token counts in `metadata.*` (NOT `metrics.*`)?
- [ ] Cost (if present) in `metrics.*` (NOT `metadata.*`)?

### TOOL Event Checklist
- [ ] `inputs` contains direct parameters (NOT `chat_history`)?
- [ ] `outputs.message` used (NOT `role/content`)?
- [ ] `config.tool_name` specified?
- [ ] No chat semantics applied to tool execution?

### CHAIN Event Checklist
- [ ] Flexible structure with semantic field names (query, result, status, etc.)?
- [ ] **NOT** forced into `outputs.role/content` format? (Chain is NOT a model!)
- [ ] If chain contains model messages:
  - [ ] Model messages in `inputs.chat_history` field? (as a field, not top-level)
  - [ ] Model messages in `outputs.conversation` field? (as a field, not top-level)
- [ ] Workflow/agent name in `config.agent_name` or `config.workflow_name`?
- [ ] Token counts in `metadata.*` (NOT `metrics.*`)?
- [ ] `metadata.span_kind` = "CHAIN"?
- [ ] Tools/iterations captured in `metadata` if applicable?

### Universal Checklist
- [ ] `event_id` is UUID?
- [ ] `event_type` is valid enum value?
- [ ] `config` has required fields for event type?
- [ ] `metrics` has token counts (if applicable)?
- [ ] `metadata` has span_kind and operation_name?
- [ ] `session_id` links to parent session?
- [ ] Fixture tested in HoneyHive UI (visual validation)?

---

## 💡 Real-World Examples

### Example 1: Pydantic AI Model Event (✅ Correct)

```json
{
  "name": "Pydantic AI Anthropic Chat",
  "input": {
    "attributes": {
      "gen_ai.operation.name": "chat",
      "gen_ai.system": "anthropic",
      "gen_ai.request.model": "claude-3-5-sonnet-20241022",
      "pydantic_ai.all_messages": "[{\"role\": \"user\", \"parts\": [...]}]",
      "gen_ai.system_instructions": "[{\"type\": \"text\", \"content\": \"Be concise\"}]"
    },
    "scopeName": "pydantic-ai",
    "eventType": "model"                  // ✅ Semantic match!
  },
  "expected": {
    "inputs": {
      "chat_history": [                   // ✅ MODEL events need chat_history
        {
          "role": "user",
          "content": "Where does \"hello world\" come from?"
        }
      ]
    },
    "outputs": {
      "role": "assistant",                // ✅ MODEL outputs use role/content
      "content": "\"Hello, World!\" originates from..."
    },
    "config": {
      "model": "claude-3-5-sonnet-20241022",
      "provider": "anthropic",
      "system_instructions": "Be concise, reply with one sentence."
    }
  }
}
```

**Why This Is Correct:**
- ✅ `eventType: "model"` matches semantic content (LLM chat)
- ✅ `inputs.chat_history` provides conversation context
- ✅ `outputs.role/content` enables markdown rendering
- ✅ `config` has model and provider

---

### Example 2: Google ADK Tool Event (✅ Correct after PR #623)

```json
{
  "name": "Google ADK Unknown Tool",
  "input": {
    "attributes": {
      "gen_ai.operation.name": "execute_tool",
      "gen_ai.tool.name": "get_weather",
      "tool.parameters": "{\"city\": \"New York\"}",
      "output.value": "{\"id\":\"...\",\"response\":{...}}"
    },
    "scopeName": "openinference.instrumentation.google_adk",
    "eventType": "tool"                   // ✅ Semantic match!
  },
  "expected": {
    "inputs": {
      "city": "New York"                  // ✅ Direct parameters (NOT chat_history)
    },
    "outputs": {
      "message": "{\"id\":\"...\",\"response\":{...}}"  // ✅ Use 'message' (NOT role/content)
    },
    "config": {
      "tool_name": "get_weather",
      "tool_description": "Retrieves the current weather...",
      "tool_type": "FunctionTool"
    }
  }
}
```

**Why This Is Correct:**
- ✅ `eventType: "tool"` matches semantic content (function call)
- ✅ `inputs` contains direct function parameters
- ✅ `outputs.message` treats result as tool output (not chat)
- ✅ No conversation semantics applied

---

### Example 3: ❌ Anti-Pattern (Common Mistake)

```json
{
  "name": "Tool Event with Chat Semantics",  // ❌ SEMANTIC MISMATCH
  "input": {
    "attributes": {
      "gen_ai.operation.name": "execute_tool",
      "tool.parameters": "{\"city\": \"New York\"}"
    },
    "eventType": "tool"
  },
  "expected": {
    "inputs": {
      "chat_history": [                   // ❌ WRONG! Tool wrapped as conversation!
        {
          "role": "user",
          "content": "{\"city\": \"New York\"}"
        }
      ]
    },
    "outputs": {
      "role": "assistant",                // ❌ WRONG! Tool result as chat message!
      "content": "{\"response\": \"sunny\"}"
    }
  }
}
```

**Why This Is WRONG:**
- 🔴 Tool execution is NOT a conversation
- 🔴 Frontend will render tool parameters as chat messages (confusing)
- 🔴 Frontend will render tool result with markdown (incorrect formatting)
- 🔴 Semantic mismatch makes debugging harder
- 🔴 Violates principle: event type semantics must match data structure

**Impact:**
- Event table shows `inputs.chat_history[0].content` = `"{\"city\": \"New York\"}"` (ugly!)
- Detail view renders tool result as markdown chat message (wrong!)
- Developer sees conversation UI for function call (cognitive dissonance)

---

## 🚫 Anti-Patterns to Avoid

### 1. Semantic Type Mismatch
```json
// ❌ BAD: Tool event with chat semantics
{
  "eventType": "tool",
  "inputs": {"chat_history": [...]}  // Tools don't chat!
}

// ✅ GOOD: Tool event with parameter semantics
{
  "eventType": "tool",
  "inputs": {"city": "New York"}
}
```

### 2. Wrong Attribute Namespace for Token Counts
```json
// ❌ BAD: Token counts in metrics
{
  "metrics": {
    "prompt_tokens": 50,        // ❌ WRONG! Breaks session aggregation
    "completion_tokens": 75,
    "cost": 0.00234
  }
}

// ✅ GOOD: Token counts in metadata, cost in metrics
{
  "metadata": {
    "prompt_tokens": 50,        // ✅ Tokens in metadata (aggregatable)
    "completion_tokens": 75,
    "total_tokens": 125
  },
  "metrics": {
    "cost": 0.00234              // ✅ Cost in metrics
  }
}
```

### 3. Missing Required Fields
```json
// ❌ BAD: MODEL event without chat_history
{
  "event_type": "model",
  "inputs": {"prompt": "Hello"}  // Poor table rendering
}

// ✅ GOOD: MODEL event with chat_history
{
  "event_type": "model",
  "inputs": {
    "chat_history": [{"role": "user", "content": "Hello"}]
  }
}
```

### 4. Incomplete Config
```json
// ❌ BAD: MODEL event without provider/model
{
  "event_type": "model",
  "config": {"temperature": 0.7}  // Missing critical context
}

// ✅ GOOD: MODEL event with complete config
{
  "event_type": "model",
  "config": {
    "model": "gpt-4",
    "provider": "openai",
    "temperature": 0.7
  }
}
```

### 5. Treating Fixtures as Validation Only
```plaintext
❌ WRONG Mindset: "Fixture tests current ingestion behavior"
✅ CORRECT Mindset: "Fixture specifies optimal behavior, tests guide implementation"

When fixture tests fail:
❌ "Fixture is wrong, update to match ingestion output"
✅ "Ingestion is incomplete, update to match fixture specification"
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating new fixture** | `search_standards("honeyhive event schema fixture patterns")` |
| **Fixture test failing** | `search_standards("fixture semantic correctness validation")` |
| **Tool event confusion** | `search_standards("tool vs model event semantics")` |
| **Frontend rendering issue** | `search_standards("optimal data patterns frontend rendering")` |
| **Attribute namespace question** | `search_standards("config vs metadata vs metrics namespace")` |
| **Chat history question** | `search_standards("when to use chat history inputs")` |
| **Tool output format** | `search_standards("tool outputs message vs role content")` |
| **Token metrics placement** | `search_standards("where do token metrics belong")` |
| **Integration analysis** | `search_standards("instrumentor integration patterns")` |
| **PR #623 lessons** | `search_standards("google adk tool fixture mistakes")` |

---

## 🔗 Related Standards

- `standards/development/testing/test-execution-commands.md` - Running integration tests
- `standards/development/coding/quality-standards.md` - Code quality requirements
- `standards/universal/ai-assistant/rag-content-authoring.md` - Documentation patterns
- `standards/universal/testing/test-data-patterns.md` - Test fixture best practices

---

## 📚 Source of Truth

**Authoritative Schema Definitions (hive-kube):**
- `hive-kube/packages/core/src/schemas/events/honeyhive_event.schema.ts` - Core Zod schema
- `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js` - Ingestion validation
- `hive-kube/kubernetes/ingestion_service/app/utils/attribute_router.ts` - Attribute mapping logic

**Frontend Rendering (hive-kube):**
- `hive-kube/kubernetes/frontend_service/src/partials/events/EventsTableComponent.tsx` - Table view
- `hive-kube/kubernetes/frontend_service/src/partials/events/EventsSideView.tsx` - Detail view

**Example Fixtures (hive-kube):**
- `hive-kube/kubernetes/ingestion_service/tests/fixtures/instrumentor_spans/*.json`

**Key Analysis Documents (python-sdk):**
- `.praxis-os/workspace/analysis/2025-11-13-honeyhive-event-schema-frontend-usage.md` - Schema deep dive
- `.praxis-os/workspace/analysis/2025-11-13-integrations-workflow-lessons-from-pr623.md` - PR #623 lessons

---

## 📝 Maintenance & Updates

**Review Triggers:**
- New instrumentor integration added
- Frontend rendering behavior changes
- Schema validation requirements change
- Fixture test patterns evolve
- Customer feedback on event display

**Update Process:**
1. Query this standard before changes
2. Update optimal patterns if needed
3. Update examples to match new conventions
4. Re-validate with multi-angle queries
5. Update related fixtures in hive-kube

**Version History:**
- v1.0 (2025-11-13): Initial standard based on PR #623 learnings and schema analysis
- v1.1 (2025-11-14): **CRITICAL FIX** - Token counts go in `metadata.*` (NOT `metrics.*`) for session-level aggregation. Cost/timing go in `metrics.*`. This is intentional per `attribute_router.ts` lines 2501-2510, 2847-2851.
- v1.2 (2025-11-14): **CRITICAL UPDATE** - CHAIN events use TOOL-LIKE flexible structure (NOT MODEL-like chat format). Boss guidance: "tool like content for chain types". CHAIN events should NOT be forced into `outputs.role/content` format. Model messages go in `chat_history`/`conversation` FIELDS within the flexible structure, not at top level. This preserves structured data while allowing model messages when applicable.

---

**🎯 Remember:** Fixtures are *specifications*, not validations. When tests fail, fix the ingestion service to meet the specification, don't change the spec to match current behavior (unless the spec itself was wrong).

