# OpenAI Agents SDK Support Analysis

**Date:** October 15, 2025  
**Status:** Investigation Complete - Decision Required

## Executive Summary

The OpenAI Agents SDK (released March 2025) introduces agent orchestration capabilities on top of the existing OpenAI Chat Completions API. We need to determine the level of support required for HoneyHive's BYOI (Bring Your Own Instrumentor) architecture.

## Background

### What is the OpenAI Agents SDK?

The OpenAI Agents SDK is a framework for building and orchestrating AI agents with:
- **Agent Builder**: Visual and code-first agent design
- **Runner**: Executes agent workflows (synchronous and asynchronous)
- **Handoffs**: Agent-to-agent task delegation
- **Guardrails**: Input/output validation
- **Built-in Tools**: Web search, file search, code interpretation, image generation
- **ChatKit**: Deployable chat interfaces
- **Evals**: Testing and refinement tools

### Current HoneyHive Architecture

HoneyHive uses a **BYOI (Bring Your Own Instrumentor) architecture**:
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

openai_instrumentor = OpenAIInstrumentor()

tracer = HoneyHiveTracer.init(
    api_key="your_api_key",
    project="your_project",
    instrumentors=[openai_instrumentor]
)

import openai
client = openai.OpenAI()
response = client.chat.completions.create(...)  # Automatically traced
```

**Supported Instrumentors:**
- OpenInference (via `openinference-instrumentation-openai`)
- Traceloop/OpenLLMetry (via `opentelemetry-instrumentation-openai`)

## Key Questions

### 1. Do existing OpenAI instrumentors automatically support Agents SDK?

**Likely YES**, because:
- The Agents SDK is built on the Responses API and Chat Completions API
- The SDK uses the OpenAI client internally
- Existing instrumentors hook into the base OpenAI client at the HTTP/SDK level

**Test Needed:** Verify that `Runner.run_sync()` and `Runner.run()` calls produce traces

### 2. Are agent-specific concepts captured?

**Agent-specific concepts that may need special handling:**
- Agent names and roles
- Handoff events (agent → agent transitions)
- Guardrail validations (pass/fail events)
- Tool invocations within agents
- Multi-step agent workflows

**Current behavior:**
- ✅ Base LLM calls are captured (via existing instrumentors)
- ❓ Agent metadata (agent names, handoffs) may not be captured
- ❓ Guardrail events may not be visible
- ❓ Agent workflow structure may not be hierarchical

### 3. Do we need agent-specific instrumentation?

**Options:**

**Option A: Rely on existing instrumentors (Low effort)**
- Pros: Zero changes needed, works out of the box
- Cons: Missing agent-specific context (handoffs, guardrails, agent names)

**Option B: Add agent-aware enrichment (Medium effort)**
- Create wrapper decorators for agent-specific concepts
- Use HoneyHive's `enrich_span()` to add agent metadata
- Manual instrumentation by users

**Option C: Build custom Agents SDK instrumentor (High effort)**
- Create `openinference-instrumentation-openai-agents`
- Auto-capture agent metadata, handoffs, guardrails
- Submit to OpenInference project or maintain ourselves

## Recommended Approach

### Phase 1: Validate Existing Support (1-2 days)

**Goal:** Confirm that existing instrumentors work with Agents SDK

**Actions:**
1. Create test script using `openai-agents` with HoneyHive + OpenInference
2. Test `Runner.run_sync()` with simple agent
3. Test multi-agent workflow with handoffs
4. Verify spans are created and sent to HoneyHive

**Success Criteria:**
- ✅ LLM calls from agents are traced
- ✅ Spans appear in HoneyHive dashboard
- ✅ Token usage is captured

**Test Script Location:** `tests/compatibility_matrix/test_openai_agents_sdk.py`

### Phase 2: Assess Agent Metadata Gaps (2-3 days)

**Goal:** Identify missing agent-specific context

**Actions:**
1. Analyze what metadata is NOT captured
2. Document user pain points (e.g., "Can't see which agent made this call")
3. Evaluate if gaps are critical for users

**Evaluation Questions:**
- Can users distinguish between agent calls vs direct LLM calls?
- Are handoff events visible in trace hierarchy?
- Do guardrail failures show up as events?
- Is tool usage within agents clear?

### Phase 3: Decide on Enhancement Level (Decision Point)

**Decision Matrix:**

| Scenario | Action | Effort |
|----------|--------|--------|
| **Existing instrumentors work perfectly** | Document as supported, add examples | 1 day |
| **Minor gaps, user can enrich manually** | Create enrichment guide + examples | 2-3 days |
| **Critical gaps, need auto-instrumentation** | Build custom instrumentor | 2-3 weeks |

### Phase 4: Implementation (Variable)

**If manual enrichment approach:**
```python
from honeyhive import HoneyHiveTracer, enrich_span
from openinference.instrumentation.openai import OpenAIInstrumentor
from agents import Agent, Runner

tracer = HoneyHiveTracer.init(project="agents-demo")
openai_instrumentor = OpenAIInstrumentor()
openai_instrumentor.instrument(tracer_provider=tracer.provider)

# Define agent
agent = Agent(name="ResearchAgent", instructions="...")

# Use enrich_span to add agent context
with tracer.enrich_span(metadata={"agent.name": "ResearchAgent", "agent.type": "research"}):
    result = Runner.run_sync(agent, "Research quantum computing")
```

**If custom instrumentor approach:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor  # New!

agents_instrumentor = OpenAIAgentsInstrumentor()

tracer = HoneyHiveTracer.init(
    project="agents-demo",
    instrumentors=[agents_instrumentor]
)

# Automatic capture of:
# - agent.name
# - agent.handoffs
# - agent.guardrails
# - agent.tools
```

## Implementation Checklist

### Validation Phase
- [ ] Install `openai-agents` in test environment
- [ ] Create test script with simple agent workflow
- [ ] Run test with OpenInference instrumentor
- [ ] Run test with Traceloop instrumentor
- [ ] Verify traces in HoneyHive dashboard
- [ ] Document what IS captured automatically
- [ ] Document what is NOT captured

### Gap Analysis Phase
- [ ] Test multi-agent handoffs
- [ ] Test guardrail validations
- [ ] Test tool usage within agents
- [ ] Interview potential users about needs
- [ ] Prioritize missing metadata by importance
- [ ] Create RFC/spec for enhancement approach

### Enhancement Phase (if needed)
- [ ] Create enrichment guide (if manual approach)
- [ ] Create example scripts for common patterns
- [ ] Update documentation with Agents SDK section
- [ ] Add to compatibility matrix tests
- [ ] Build custom instrumentor (if needed)
- [ ] Submit to OpenInference (if custom instrumentor)

## Technical Considerations

### Compatibility Matrix

Current support:
| Provider | OpenInference | Traceloop | Status |
|----------|--------------|-----------|--------|
| OpenAI Chat Completions | ✅ | ✅ | Supported |
| OpenAI Embeddings | ✅ | ✅ | Supported |
| OpenAI Assistants API | ⚠️ | ⚠️ | Partial |
| **OpenAI Agents SDK** | ❓ | ❓ | **To Test** |

### Dependencies

```bash
# Current OpenAI support
pip install honeyhive[openinference-openai]
# or
pip install honeyhive[traceloop-openai]

# Agents SDK support (proposed)
pip install honeyhive[openinference-openai]  # Should work already
pip install openai-agents
```

### Documentation Needs

If we support Agents SDK:
1. **New how-to guide:** `docs/how-to/integrations/openai-agents.rst`
2. **Update main OpenAI guide:** Add Agents SDK section
3. **Example scripts:** Add to `examples/integrations/`
4. **Compatibility test:** Add to `tests/compatibility_matrix/`

## Next Steps

### Immediate (This Week)
1. **Create validation test script** - Verify existing instrumentor support
2. **Run manual tests** - Test with real Agents SDK workflows
3. **Document findings** - What works, what doesn't

### Short-term (Next 2 Weeks)
1. **User research** - Talk to customers about agent observability needs
2. **Decision on approach** - Manual enrichment vs custom instrumentor
3. **Create implementation spec** - If enhancements needed

### Medium-term (Next Month)
1. **Implement chosen approach** - Either guide or instrumentor
2. **Create documentation** - Integration guides and examples
3. **Release support** - Add to next minor version

## Questions for Discussion

1. **Do we have customers using the OpenAI Agents SDK?**
   - If yes, what are their observability pain points?
   - If no, is this a competitive feature we need?

2. **What level of agent visibility is required?**
   - Just LLM calls? (Already supported)
   - Agent names and roles? (May need enrichment)
   - Handoffs and workflow structure? (May need custom instrumentor)

3. **Who should maintain an Agents SDK instrumentor?**
   - OpenInference community?
   - HoneyHive internally?
   - Contribute to upstream?

4. **Timeline and priority?**
   - Urgent (block customers)?
   - Important (competitive feature)?
   - Nice-to-have (future enhancement)?

## Resources

- **OpenAI Agents SDK Docs:** https://openai.github.io/openai-agents-python/
- **OpenAI Agent Platform:** https://openai.com/agent-platform/
- **HoneyHive BYOI Architecture:** `.agent-os/standards/ai-assistant/AI-ASSISTED-DEVELOPMENT-PLATFORM-CASE-STUDY.md`
- **Current OpenAI Integration:** `docs/how-to/integrations/openai.rst`
- **OpenInference Instrumentors:** https://github.com/Arize-ai/openinference

---

**Author:** AI Assistant  
**Review Required:** Yes  
**Next Action:** Create validation test script

