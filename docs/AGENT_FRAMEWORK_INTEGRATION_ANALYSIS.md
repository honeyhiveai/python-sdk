# Agent Framework Integration Analysis

**Date:** February 2026  
**SDK Version:** 1.0.0rc16  
**Target Market:** Large Regulated Enterprises

## Executive Summary

This document provides a comprehensive analysis of agent framework integrations available in the HoneyHive Python SDK, evaluated against competitor offerings and enterprise requirements for debugging agent behavior.

---

## 1. Complete Integration Enumeration

### Sources Verified

1. `pyproject.toml` (lines 71-196) - SDK optional dependencies
2. `examples/integrations/` - 25 example files
3. `docs/integrations/` - 25 MDX documentation files
4. PyPI registry - OpenInference and Traceloop packages
5. Arize-ai/openinference GitHub - 39 published packages

### Agent Frameworks (10 Total)

| Framework | OpenInference Package | Traceloop Package | In HoneyHive SDK |
|-----------|----------------------|-------------------|------------------|
| LangChain/LangGraph | `openinference-instrumentation-langchain` | `opentelemetry-instrumentation-langchain` | Yes (pyproject.toml + examples) |
| OpenAI Agents SDK | `openinference-instrumentation-openai-agents` | `opentelemetry-instrumentation-openai-agents` | Yes (examples) |
| CrewAI | `openinference-instrumentation-crewai` | `opentelemetry-instrumentation-crewai` | Docs only |
| AutoGen | (via LangSmith OTEL) | (via LangSmith OTEL) | Example only |
| Pydantic AI | `openinference-instrumentation-pydantic-ai` | - | Example only |
| DSPy | `openinference-instrumentation-dspy` | - | Example only |
| LlamaIndex | `openinference-instrumentation-llama-index` | - | Docs only |
| Google ADK | `openinference-instrumentation-google-adk` | - | Yes (pyproject.toml) |
| Semantic Kernel | (via OTEL) | - | Example only |
| AWS Strands | - | - | Example only |

### LLM Provider Integrations (13 Packages in pyproject.toml)

**OpenInference Ecosystem (7 packages):**
- `openinference-openai`
- `openinference-anthropic`
- `openinference-google-ai`
- `openinference-google-adk`
- `openinference-aws-bedrock`
- `openinference-azure-openai`
- `openinference-mcp`

**Traceloop/OpenLLMetry Ecosystem (6 packages):**
- `traceloop-openai`
- `traceloop-anthropic`
- `traceloop-google-ai`
- `traceloop-aws-bedrock`
- `traceloop-azure-openai`
- `traceloop-mcp`

### Gap Analysis vs PyPI Registry

**Missing from HoneyHive SDK that exist on PyPI:**
- `openinference-instrumentation-haystack`
- `openinference-instrumentation-smolagents`
- `openinference-instrumentation-beeai`
- `openinference-instrumentation-agno`

---

## 2. Competitor Landscape

### Top LLM Observability Platforms (2025-2026)

| Platform | Open Source | Enterprise Features | Agent Framework Support |
|----------|-------------|---------------------|------------------------|
| **LangSmith** | No | SOC2, RBAC, on-prem (enterprise) | LangChain-centric, AutoGen, CrewAI |
| **Arize Phoenix** | Yes (Elastic 2.0) | VPC/on-prem | All OpenInference frameworks |
| **Langfuse** | Yes (MIT) | Self-host, Docker/K8s | Framework agnostic |
| **Datadog LLM Obs** | No | Full enterprise stack | OpenTelemetry native |
| **Helicone** | Partial | Gateway proxy model | Provider-level tracing |
| **HoneyHive** | No | SOC2/GDPR/HIPAA | BYOI architecture |

### Key Differentiators

| Platform | Strength | Weakness |
|----------|----------|----------|
| LangSmith | Best LangChain integration | Proprietary, LangChain-centric |
| Arize Phoenix | Best open-source, maintains OpenInference | Less enterprise support |
| Langfuse | Best self-hosted option, MIT license | Smaller ecosystem |
| Datadog | Enterprise APM integration | Higher cost, less LLM-specific |
| HoneyHive | BYOI flexibility, evaluation framework | Smaller community |

---

## 3. Trace Quality Evaluation

### Test Sessions Executed

| Test | Session ID | Purpose |
|------|------------|---------|
| LangGraph Workflow | `2260bb8e-b0a2-4718-8e02-a6d40d90c954` | Enterprise workflow with audit trails |
| OpenAI Agents Pattern | `e651e2cc-2b09-41eb-a53b-3161cf62a6d3` | Nested decorator patterns |
| LLM/Cost Tracking | `3c5d6bd6-1f2b-4da3-9dcb-a736ee011c90` | Cost tracking simulation |
| Error Handling | `0865577a-c253-46f8-8330-8ae61ee51040` | Exception capture |
| Metadata Enrichment | `d22e7232-94f1-4b90-b6be-2d1dae06af0f` | Enterprise metadata |

### Quality Criteria Results

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Input/Output Capture | PASS | Full state objects captured in `inputs`/`outputs` fields |
| Span Hierarchy | PASS | `parent_id` links verified in LangGraph traces |
| Metadata Richness | PASS | `langgraph_step`, `langgraph_node`, `langgraph_triggers`, instrumentor attribution |
| Error Capture | PASS | Exception propagation test captured error info |
| Session Enrichment | PASS | `enrich_session()` added compliance metadata |
| Span Enrichment | PASS | `enrich_span()` added request-specific metadata |
| Audit Trail | PASS | `audit_trail` arrays propagate through workflow |
| Duration Tracking | PASS | `start_time`/`end_time`/`duration` fields populated |

### Sample Trace Structure (LangGraph)

```json
{
  "event_id": "92b6c19c-91b6-43b9-8f98-006bf3d1f7d5",
  "session_id": "2260bb8e-b0a2-4718-8e02-a6d40d90c954",
  "event_type": "chain",
  "event_name": "LangGraph",
  "duration": 113,
  "metadata": {
    "langgraph_step": 1,
    "langgraph_node": "classify",
    "langgraph_triggers": ["branch:to:classify"],
    "langgraph_checkpoint_ns": "classify:1dccd3d2-72e7-1ecb-1dbe-0b1928f29b04",
    "instrumentor": "OpenInference",
    "system": "langchain"
  },
  "inputs": {
    "chat_history": [{"content": "{...state...}", "role": "user"}]
  },
  "outputs": {
    "content": "{...updated_state...}",
    "role": "assistant"
  }
}
```

### Issues Found

1. **Deprecation warnings** in `span_processor.py` (lines 237-256)
   - `instrumentation_info` should be `instrumentation_scope`
   - OpenTelemetry API change since v1.11.1

2. **Cost tracking limitation**
   - Requires actual LLM API calls to populate token/cost metrics
   - Traceloop instrumentors provide cost tracking; OpenInference does not

3. **API route 404**
   - Events export endpoint returned 404 on staging
   - Could not programmatically verify trace data via API

---

## 4. Enterprise Suitability Assessment

### Strengths for Regulated Enterprises

1. **BYOI Architecture**
   - Choose instrumentors based on compliance needs
   - Mix OpenInference (lightweight) and Traceloop (cost tracking) per provider

2. **Audit Trail Support**
   - `enrich_session()` supports compliance metadata (SOC2, GDPR, HIPAA flags)
   - `enrich_span()` supports request-specific audit data
   - LangGraph integration captures full decision flow with checkpoint metadata

3. **OpenTelemetry Foundation**
   - Enables integration with existing enterprise APM (Datadog, New Relic, Splunk)
   - Standard OTLP export format

4. **Evaluation Framework Integration**
   - `evaluate()` function for systematic testing
   - Multi-instance tracer pattern for experiment isolation

### Gaps for Enterprise

1. **No explicit compliance metadata fields** in trace schema
   - Workaround: Use `enrich_session()` with custom metadata

2. **Cost tracking requires Traceloop instrumentors**
   - Not enabled by default
   - Recommendation: Add `[traceloop-*]` extras for enterprise deployments

3. **Missing newer agent frameworks**
   - Haystack, smolagents, beeai, agno not in SDK
   - Available on PyPI via OpenInference

4. **Technical debt in span processor**
   - Deprecation warnings should be addressed

---

## 5. Recommendations

### For Enterprise Deployments

1. **Framework Selection**
   - Use LangGraph or Semantic Kernel for workflow orchestration (best audit trail support)
   - Use CrewAI for multi-agent orchestration (role-based, good for compliance workflows)

2. **Instrumentor Selection**
   - Use Traceloop instrumentors for cost tracking requirements
   - Use OpenInference for lightweight, open-source preference

3. **Compliance Metadata Pattern**
   ```python
   tracer.enrich_session(
       metadata={
           "compliance_level": "SOC2",
           "data_classification": "confidential",
           "audit_id": "AUDIT-2026-001",
           "approver": "john.doe@enterprise.com"
       },
       user_properties={
           "user_id": "user-12345",
           "role": "compliance_officer"
       }
   )
   ```

4. **Debugging Agent Behavior**
   - Use `@trace` decorator with explicit `event_name` for compliance-friendly naming
   - Leverage LangGraph metadata (`langgraph_step`, `langgraph_node`) for decision flow analysis
   - Use `enrich_span()` for request-specific context

### SDK Improvements Suggested

1. Add CrewAI, LlamaIndex to `pyproject.toml` optional dependencies
2. Fix deprecation warnings in `span_processor.py`
3. Add explicit compliance metadata fields to trace schema
4. Document cost tracking setup with Traceloop instrumentors

---

## Appendix: Test Code Examples

### LangGraph Enterprise Workflow Test

```python
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace
from langgraph.graph import StateGraph

tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="langgraph_enterprise_test",
    source="agent_framework_evaluation",
)

@trace(event_type="tool", event_name="classify_request", tracer=tracer)
def classify_request(state: dict) -> dict:
    # Classification logic with audit trail
    audit_trail = state.get("audit_trail", [])
    audit_trail.append(f"Classification: {classification}")
    return {**state, "classification": classification, "audit_trail": audit_trail}
```

### Error Handling Test

```python
@trace(event_type="chain", event_name="error_prone_workflow", tracer=tracer)
def error_prone_workflow(should_fail: bool) -> dict:
    try:
        validated = validate_input({"test": "data"})
        result = process_data(validated)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error_type": type(e).__name__, "error_message": str(e)}
```

---

*Analysis conducted using HoneyHive Python SDK 1.0.0rc16 against staging environment.*
