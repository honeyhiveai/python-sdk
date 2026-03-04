---
name: honeyhive-evaluators
description: Add HoneyHive evaluators and run experiments against datasets. Use when asked to set up evaluations, write evaluator functions, run experiments with evaluate(), compare prompt versions, or add client-side scoring to an AI application. Covers client-side evaluators, the evaluate() API, multi-step pipeline evaluation, and integration with tracing.
metadata:
  author: honeyhive
  version: "1.0"
---

# HoneyHive Evaluators

Set up HoneyHive evaluators and run experiments. This skill covers writing client-side evaluator functions, running experiments with `evaluate()`, scoring multi-step pipelines, and understanding how evaluators integrate with tracing.

## Prerequisites

- A HoneyHive project (create at https://app.honeyhive.ai/projects)
- A HoneyHive API key (org settings > Copy API Key)
- Python 3.9+
- `pip install honeyhive`

Environment variables expected:
- `HH_API_KEY` - HoneyHive API key
- `HH_PROJECT` - HoneyHive project name
- `HH_API_URL` - (optional) Custom API URL for self-hosted/dedicated deployments

---

## Concepts

### Experiment Structure

Every experiment combines three independent, decoupled parts:

```
Dataset --> Your Function --> Evaluators --> Results
```

| Component | What it is | Interface |
|-----------|------------|-----------|
| **Dataset** | Test cases with inputs and expected outputs | List of `{inputs, ground_truth}` dicts, or a `dataset_id` |
| **Function** | Your application logic | `def fn(datapoint)` -> output dict |
| **Evaluators** | Scoring functions that assess outputs | `def eval(outputs, inputs, ground_truth)` -> score |

These are deliberately decoupled: reuse a dataset across multiple functions, run the same function against different datasets, and swap evaluators without changing anything else.

### Evaluator Types

| Type | What runs the logic | Best for |
|------|---------------------|----------|
| **Code (client-side)** | Deterministic Python in your env | Format checks, metrics, validation |
| **Code (server-side)** | Python on HoneyHive infra | Consistent eval across all traces |
| **LLM-as-judge** | An LLM model (server-side) | Subjective quality, relevance, tone |
| **Human** | Domain experts (server-side) | Edge cases, compliance, ground truth |
| **Composite** | Aggregation formula (server-side) | Weighted indexes, pass/fail gates |

This skill focuses on **client-side code evaluators** (the ones you write and pass to `evaluate()`). Server-side evaluators are configured in the HoneyHive UI and run automatically on matching traces without code changes.

### Client-Side vs Server-Side

| | Client-side | Server-side |
|---|---|---|
| **Where it runs** | Your environment | HoneyHive infrastructure |
| **When it runs** | During `evaluate()` only | Every matching trace (production + experiments) |
| **Setup** | Define in code, pass to `evaluate()` | Configure once in HoneyHive UI |
| **Data interface** | `(outputs, inputs, ground_truth)` | `event` dict or `{{ }}` templates |
| **Versioning** | Your source control | Built-in version history with rollback |

You can use both together. Common pattern: client-side for experiment-specific scoring, server-side for baseline checks (toxicity, format, PII) that run on all traces automatically.

---

## Step 1: Create Your Dataset

Define test cases with inputs and (optionally) expected outputs:

```python
dataset = [
    {
        "inputs": {"text": "I was charged twice for my subscription."},
        "ground_truth": {"intent": "billing"},
    },
    {
        "inputs": {"text": "The export button gives error 500."},
        "ground_truth": {"intent": "technical"},
    },
    {
        "inputs": {"text": "I forgot my password and reset email never arrived."},
        "ground_truth": {"intent": "account"},
    },
    {
        "inputs": {"text": "Your support team was amazing. Thanks!"},
        "ground_truth": {"intent": "general"},
    },
]
```

You can also reference a managed dataset by ID:

```python
result = evaluate(
    function=my_function,
    dataset="dataset_id_here",
    evaluators=[my_evaluator],
    name="my-experiment",
)
```

---

## Step 2: Write Your Function

Your function receives a `datapoint` dict and returns an output dict. There are no constraints on what happens inside --- call models, query databases, invoke tools, orchestrate sub-agents.

```python
from openai import OpenAI

client = OpenAI()

def classify_intent(datapoint):
    text = datapoint["inputs"]["text"]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"""Classify this message into ONE category:
- billing: payment issues, invoices, charges, refunds
- technical: bugs, errors, how to use features
- account: login, password, profile, settings
- general: other questions, feedback

Reply with ONLY the category name.

Message: {text}
Category:"""}],
        temperature=0,
    )
    return {"intent": response.choices[0].message.content.strip().lower()}
```

**Key pattern**: `def fn(datapoint)` receives `{"inputs": {...}, "ground_truth": {...}}` and returns a dict.

---

## Step 3: Write Evaluator Functions

Evaluators receive three arguments and return a score:

```python
def my_evaluator(outputs, inputs, ground_truth):
    """
    Args:
        outputs: Return value from your function (dict)
        inputs: The inputs dict from the datapoint
        ground_truth: The ground_truth dict from the datapoint

    Returns:
        A score (number, boolean, or string)
    """
    ...
```

### Common Evaluator Patterns

**Exact match:**

```python
def intent_match(outputs, inputs, ground_truth):
    actual = outputs.get("intent", "").lower()
    expected = ground_truth.get("intent", "").lower()
    return 1.0 if expected in actual else 0.0
```

**Length / format check:**

```python
def length_check(outputs, inputs, ground_truth):
    answer = outputs.get("answer", "")
    return 1.0 if len(answer) > 50 else 0.0
```

**Substring containment:**

```python
def answer_contains_expected(outputs, inputs, ground_truth):
    expected = ground_truth.get("answer", "").lower()
    actual = str(outputs).lower()
    return 1.0 if expected in actual else 0.0
```

**Multi-criteria scoring:**

```python
def quality_score(outputs, inputs, ground_truth):
    answer = outputs.get("answer", "")
    score = 0.0
    if len(answer) > 20:
        score += 0.25
    if not answer.startswith("I'm sorry"):
        score += 0.25
    if ground_truth.get("keyword", "") in answer.lower():
        score += 0.5
    return score
```

---

## Step 4: Run Experiments with `evaluate()`

```python
import os
from honeyhive import evaluate

result = evaluate(
    function=classify_intent,
    dataset=dataset,
    evaluators=[intent_match],
    name="intent-classifier-v1",
    # api_key and project are read from HH_API_KEY / HH_PROJECT env vars
    # or pass explicitly:
    # api_key=os.getenv("HH_API_KEY"),
    # project=os.getenv("HH_PROJECT"),
)

print(f"Run ID: {result.run_id}")
```

### Comparing Two Versions

Run the same dataset with different functions to compare:

```python
result_v1 = evaluate(
    function=classify_vague,
    dataset=dataset,
    evaluators=[intent_match],
    name="intent-vague-prompt",
)

result_v2 = evaluate(
    function=classify_structured,
    dataset=dataset,
    evaluators=[intent_match],
    name="intent-structured-prompt",
)

print(f"V1 run: {result_v1.run_id}")
print(f"V2 run: {result_v2.run_id}")
```

View and compare results in the HoneyHive dashboard under **Experiments**.

---

## Step 5: Built-in Tracing (Automatic)

When you call `evaluate()`, your function is automatically traced using HoneyHive's OpenTelemetry-based tracing. Every datapoint execution produces a full traced session --- no additional setup required.

**Important**: Do NOT create your own `HoneyHiveTracer.init()` alongside `evaluate()`. The SDK creates a new tracer per datapoint automatically. A global tracer will conflict and cause traces to land in the wrong session.

```python
# WRONG - global tracer conflicts with evaluate()
tracer = HoneyHiveTracer.init(...)
@trace(event_type="tool", tracer=tracer)
def my_function(datapoint):
    ...

# CORRECT - let evaluate() manage tracers
@trace(event_type="tool")  # No tracer parameter
def my_function(datapoint):
    ...
```

All tracing primitives work inside your function:
- **Auto-instrumentation**: LLM calls via OpenAI, Anthropic, etc. are captured if you have instrumentors configured
- **Custom spans**: Use `@trace` to create spans for any step
- **Enrichment**: Call `enrich_span()` to attach metrics, metadata, or feedback to any span
- **Nested traces**: Multi-agent orchestration is traced with full parent-child relationships

---

## Step 6: Multi-Step Pipeline Evaluation

For pipelines with multiple steps, combine session-level evaluators (via `evaluate()`) with span-level metrics (via `enrich_span()`):

```python
import os
from honeyhive import evaluate, trace, enrich_span

# Session-level evaluator: scores the final pipeline output
def answer_quality(outputs, inputs, ground_truth):
    expected = ground_truth.get("answer", "")
    return 1.0 if expected.lower() in str(outputs).lower() else 0.0

# Span-level metrics: scores individual steps
@trace
def retrieve_docs(query):
    docs = search_database(query)
    enrich_span(metrics={"num_docs": len(docs), "retrieval_score": 0.85})
    return docs

@trace
def generate_answer(docs, query):
    answer = call_llm(docs, query)
    enrich_span(metrics={"answer_length": len(answer)})
    return answer

# Pipeline function
def rag_pipeline(datapoint):
    query = datapoint["inputs"]["query"]
    docs = retrieve_docs(query)
    return generate_answer(docs, query)

# Run experiment
result = evaluate(
    function=rag_pipeline,
    dataset=my_dataset,
    evaluators=[answer_quality],
    name="rag-eval",
)
```

After running, the dashboard shows:
- `answer_quality` scores at the **session level**
- `num_docs`, `retrieval_score`, `answer_length` at individual **span levels**

### Evaluation Scope

| Scope | What it evaluates | How |
|-------|-------------------|-----|
| **Session-level** | End-to-end pipeline output | Pass evaluators to `evaluate()` |
| **Span-level** | Individual steps | Call `enrich_span(metrics={...})` inside traced functions |

---

## Step 7: Adding Client-Side Metrics to Production Traces

Outside of experiments, you can add evaluation metrics directly to production traces using `enrich_span()` and `enrich_session()`. This is useful for guardrails, format validation, and real-time scoring.

```python
import os
from honeyhive import HoneyHiveTracer, trace, enrich_span

HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
)

@trace
def generate_response(query):
    response = call_llm(query)

    # Compute and attach metrics inline
    enrich_span(metrics={
        "response_length": len(response),
        "contains_pii": check_pii(response),
        "relevance_score": compute_relevance(query, response),
        "json_valid": is_valid_json(response),
    })

    return response
```

### Metrics Data Types

| Type | Available Measurements | Use Case |
|------|------------------------|----------|
| Boolean | True/False percentage | Pass/fail checks |
| Number | Sum, Avg, Median, Min, Max, P95, P98, P99 | Scores, latencies |
| String | Filters and group by | Classifications |

Metrics appear in the HoneyHive dashboard for charting, alerting, and filtering.

---

## Complete Example

```python
import os
from openai import OpenAI
from honeyhive import evaluate, trace, enrich_span

client = OpenAI()

# --- Dataset ---
dataset = [
    {
        "inputs": {"text": "I was charged twice for my subscription."},
        "ground_truth": {"intent": "billing"},
    },
    {
        "inputs": {"text": "The export button gives error code 500."},
        "ground_truth": {"intent": "technical"},
    },
    {
        "inputs": {"text": "I forgot my password and reset email never arrived."},
        "ground_truth": {"intent": "account"},
    },
    {
        "inputs": {"text": "Your support team was amazing. Thanks!"},
        "ground_truth": {"intent": "general"},
    },
]

# --- Function ---
@trace
def classify_intent(datapoint):
    text = datapoint["inputs"]["text"]
    enrich_span(metadata={"text_length": len(text)})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"""Classify into ONE category:
- billing, technical, account, general
Reply with ONLY the category name.
Message: {text}
Category:"""}],
        temperature=0,
    )
    return {"intent": response.choices[0].message.content.strip().lower()}

# --- Evaluator ---
def intent_match(outputs, inputs, ground_truth):
    actual = outputs.get("intent", "").lower()
    expected = ground_truth.get("intent", "").lower()
    return 1.0 if expected in actual else 0.0

# --- Run ---
result = evaluate(
    function=classify_intent,
    dataset=dataset,
    evaluators=[intent_match],
    name="intent-classifier-v1",
)

print(f"Run ID: {result.run_id}")
```

---

## Best Practices

1. **Evaluator signature**: Always `(outputs, inputs, ground_truth)` -> score. Return a number (0.0-1.0), boolean, or string.
2. **No global tracer with `evaluate()`**: Let the SDK manage per-datapoint tracers automatically.
3. **Use `@trace` without `tracer=`** inside `evaluate()` functions --- the SDK provides the tracer.
4. **Combine session-level and span-level**: Use `evaluate(evaluators=[...])` for end-to-end scoring and `enrich_span(metrics={...})` for per-step scoring.
5. **Keep evaluators simple and deterministic**: Complex eval logic should be in server-side LLM-as-judge evaluators.
6. **Use consistent metric names** across experiments for meaningful comparisons.
7. **Name experiments descriptively**: `"rag-v2-gpt4o-temperature0.3"` not `"test-1"`.
8. **Use production trace metrics for guardrails**: Attach `enrich_span(metrics={...})` for real-time format validation, PII detection, safety checks.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Traces landing in wrong session | Remove any global `HoneyHiveTracer.init()` when using `evaluate()` |
| Evaluator not scoring | Check function signature is `(outputs, inputs, ground_truth)` |
| Missing span-level metrics | Ensure `enrich_span()` is called inside a `@trace`-decorated function |
| `evaluate()` hangs | Check network connectivity to HoneyHive API and valid `HH_API_KEY` |
| Server-side evals not running | Server-side evaluators are configured in UI, not passed to `evaluate()` |
