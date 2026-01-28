# Integration Test Suite Documentation

## Overview

This directory contains integration tests for the HoneyHive Python SDK across 13 providers and core tracing features. All tests are designed to:
- Skip gracefully when API keys are not present
- Use real API calls for end-to-end verification
- Demonstrate correct SDK usage patterns from documentation

## Test Suite Breakdown

### 1. Core Tracing (`test_tracing_integration.py`)

| Test Class | Tests | What is Tested | Verification Method |
|------------|-------|----------------|---------------------|
| `TestTracerInitialization` | 3 | HoneyHiveTracer.init() with various configurations | Assert tracer instance created, session_id is valid UUID |
| `TestTraceDecorator` | 4 | @trace decorator on sync/async functions, event_type, nested traces | Assert function returns expected value, decorator doesn't interfere |
| `TestEnrichment` | 3 | enrich_span(), enrich_session(), combined enrichment | Assert enrichment calls complete, no exceptions |
| `TestUserFeedback` | 4 | Boolean/numeric ratings, ground_truth, span-level feedback | Assert feedback dict is accepted by enrich methods |
| `TestUserProperties` | 3 | Session/span user properties, combined context | Assert user_properties dict is accepted by enrich methods |
| `TestDistributedTracing` | 2 | Session ID retrieval, multiple session isolation | Assert session_id is valid UUID, different tracers have different IDs |
| `TestEndToEndVerification` | 8 | **Full pipeline: SDK -> export -> ingest -> fetch via API** | **Fetch events.export() and assert inputs/outputs/metadata match** |

**Total: 23 tests**

#### End-to-End Verification Tests

| Test | What is Verified |
|------|------------------|
| `test_basic_trace_export_verification` | Traced function events are fetchable via API |
| `test_enrichment_export_verification` | Metadata/metrics in logged events match |
| `test_session_can_be_retrieved` | Session exists via `sessions.get()` API |
| `test_api_client_events_export` | `events.export()` API works correctly |
| `test_inputs_outputs_verification` | `@trace` decorated function args/return values |
| `test_openai_inputs_outputs_verification` | **OpenAI instrumentor** captures messages/completions |
| `test_anthropic_inputs_outputs_verification` | **Anthropic instrumentor** captures messages/responses |
| `test_langchain_inputs_outputs_verification` | **LangChain instrumentor** captures chain inputs/outputs |

#### Verification Pattern

```python
# 1. Create tracer and instrument provider
tracer = HoneyHiveTracer.init(project=os.getenv("HH_PROJECT"))
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# 2. Make LLM call (auto-traced by instrumentor)
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "test prompt"}],
)

tracer.flush()

# 3. Fetch and verify inputs/outputs were captured
events = fetch_session_events(session_id=tracer.session_id)
llm_event = find_llm_event(events)

# Verify inputs contain the prompt
assert "test prompt" in str(llm_event["inputs"])

# Verify outputs contain the response
assert len(llm_event["outputs"]) > 0
```

---

### 2. OpenAI (`test_openai_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_chat_completion` | OpenAI chat.completions.create with OpenInference instrumentor | Assert response.choices[0].message.content is non-empty |
| `test_chat_completion_with_enrichment` | @trace wrapper + enrich_span with metadata/metrics | Assert result returned, no exceptions from enrichment |
| `test_streaming_chat_completion` | Streaming response with iter chunks | Assert collected chunks form non-empty response |
| `test_traceloop_basic` | Traceloop OpenAI instrumentor (alternative to OpenInference) | Assert response content is non-empty |
| `test_traceloop_with_enrichment` | Traceloop + @trace + enrich_span | Assert enrichment integrates with Traceloop spans |

**Total: 5 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 3. Anthropic (`test_anthropic_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_message` | client.messages.create with OpenInference instrumentor | Assert response.content[0].text is non-empty |
| `test_message_with_system_prompt` | System prompt parameter | Assert system instruction is respected |
| `test_message_with_enrichment` | @trace + enrich_span with input/output length | Assert metrics captured, response returned |
| `test_streaming_message` | Streaming with stream events iteration | Assert delta.text chunks form response |

**Total: 4 tests** | **Env vars:** `ANTHROPIC_API_KEY`

---

### 4. LangChain / LangGraph (`test_langchain_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_llm_invoke` | ChatOpenAI.invoke with OpenInference instrumentor | Assert AIMessage.content is non-empty |
| `test_chain_with_prompt_template` | ChatPromptTemplate | PromptTemplate chaining | Assert chain produces formatted response |
| `test_chain_with_enrichment` | @trace wrapper on LangChain chain | Assert enrichment integrates with chain spans |
| `test_langgraph_basic_workflow` | StateGraph with node functions | Assert workflow executes all nodes in order |
| `test_langgraph_conditional_workflow` | add_conditional_edges for routing | Assert conditional logic routes to correct node |

**Total: 5 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 5. Azure OpenAI (`test_azure_openai_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_chat_completion` | AzureOpenAI client with Traceloop OpenAI instrumentor | Assert response.choices[0].message.content non-empty |
| `test_chat_with_enrichment` | @trace + enrich_span with deployment metadata + token metrics | Assert tokens captured, result returned |

**Total: 2 tests** | **Env vars:** `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`

---

### 6. AWS Bedrock (`test_bedrock_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_claude_invocation` | boto3 bedrock-runtime invoke_model with Claude v2 | Assert response contains 'completion' field |
| `test_titan_invocation` | Amazon Titan model invocation | Assert response contains 'results' array |
| `test_bedrock_with_enrichment` | @trace + enrich_span with model/region metadata | Assert metrics captured, completion returned |

**Total: 3 tests** | **Env vars:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`

---

### 7. Google ADK (`test_google_adk_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_agent_invocation` | LlmAgent + Runner with Gemini model | Assert response text is non-empty from streaming events |
| `test_agent_with_enrichment` | @trace async wrapper + enrich_span | Assert metrics captured, response returned |

**Total: 2 tests** | **Env vars:** `GOOGLE_API_KEY`

---

### 8. AWS Strands (`test_strands_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_agent_invocation` | Strands Agent with BedrockModel | Assert agent returns non-None, non-empty response |
| `test_agent_with_tool` | @tool decorated function + Agent tools parameter | Assert tool is invoked, result incorporates tool output |

**Total: 2 tests** | **Env vars:** `AWS_ACCESS_KEY_ID`, `BEDROCK_MODEL_ID`

---

### 9. Semantic Kernel (`test_semantic_kernel_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_chat_completion` | OpenAIChatCompletion service with ChatHistory | Assert response is non-empty |
| `test_kernel_function` | Kernel with plugin + @kernel_function decorator | Assert kernel.invoke returns expected result (e.g., uppercase) |

**Total: 2 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 10. Pydantic AI (`test_pydantic_ai_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_agent` | Agent with Claude model + system_prompt | Assert result.data is non-empty |
| `test_structured_output` | result_type=Pydantic model for extraction | Assert extracted fields match expected values (e.g., city name) |

**Total: 2 tests** | **Env vars:** `ANTHROPIC_API_KEY`

---

### 11. OpenAI Agents (`test_openai_agents_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_agent` | Agent + Runner.run execution | Assert result.final_output is non-empty |
| `test_agent_with_tool` | @function_tool decorator + tools parameter | Assert tool is invoked, output contains expected result (e.g., "8") |

**Total: 2 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 12. AutoGen (`test_autogen_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_assistant_agent` | AssistantAgent + OpenAIChatCompletionClient | Assert agent.run returns non-None |
| `test_agent_with_tool` | AgentTool wrapping Python function | Assert tool is callable, agent uses it |

**Total: 2 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 13. DSPy (`test_dspy_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_predict` | dspy.Predict with "question -> answer" signature | Assert result.answer is non-empty |
| `test_chain_of_thought` | dspy.ChainOfThought for reasoning | Assert answer contains expected value (e.g., "4" for 2+2) |
| `test_custom_signature` | Custom dspy.Signature with InputField/OutputField | Assert summary field is populated |

**Total: 3 tests** | **Env vars:** `OPENAI_API_KEY`

---

### 14. evaluate() Function (`test_evaluate_integration.py`)

| Test | What is Tested | Verification Method |
|------|----------------|---------------------|
| `test_basic_evaluation` | evaluate() with function and dataset | Assert result.run_id exists, result.status is valid |
| `test_evaluation_with_enrichment` | @trace wrapped evaluation function | Assert enrichment integrates with evaluation spans |
| `test_multiple_evaluators` | Multiple evaluator functions | Assert all evaluators execute |
| `test_ground_truth_comparison` | Evaluator comparing output to ground_truth | Assert comparison logic executes |
| `test_async_function_evaluation` | Async function as evaluation target | Assert async function is awaited correctly |

**Total: 5 tests** | **Env vars:** `HH_API_KEY`, `HH_PROJECT`

---

## Summary

| Category | Tests |
|----------|-------|
| Core Tracing | 19 |
| **E2E Verification** | **6** |
| OpenAI | 5 |
| Anthropic | 4 |
| LangChain/LangGraph | 5 |
| Azure OpenAI | 2 |
| AWS Bedrock | 3 |
| Google ADK | 2 |
| AWS Strands | 2 |
| Semantic Kernel | 2 |
| Pydantic AI | 2 |
| OpenAI Agents | 2 |
| AutoGen | 2 |
| DSPy | 3 |
| evaluate() | 5 |
| **Total** | **66** |

## Running Tests

```bash
# All integrations (requires all API keys)
PYTHONPATH=src pytest tests_v2/integrations/ -v

# Specific provider
PYTHONPATH=src pytest tests_v2/integrations/test_openai_integration.py -v

# Skip slow tests
PYTHONPATH=src pytest tests_v2/integrations/ -v -m "not slow"

# With tox
tox -e integrations
```

## Required Environment Variables

```bash
# Core (always required)
HH_API_KEY=your-honeyhive-key
HH_PROJECT=your-project-name

# OpenAI-based providers (OpenAI, LangChain, Semantic Kernel, AutoGen, DSPy, OpenAI Agents)
OPENAI_API_KEY=sk-...

# Anthropic (Anthropic, Pydantic AI)
ANTHROPIC_API_KEY=sk-ant-...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# AWS (Bedrock, Strands)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-haiku-4-5-20251001-v1:0

# Google (ADK)
GOOGLE_API_KEY=...
```
