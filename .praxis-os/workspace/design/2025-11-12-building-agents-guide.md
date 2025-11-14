# Building Agents with HoneyHive

**Last Updated:** 2025-11-12  
**Audience:** Developers building production AI agents  
**Estimated Reading Time:** 15 minutes

---

## 🎯 Overview

This guide shows practical patterns for building production agents with HoneyHive tracing, evaluation, cost tracking, and retry management. All examples are based on real SDK patterns discovered through code intelligence.

---

## 1. Multi-Agent Orchestration Patterns

### Pattern 1: Independent Agents (Separate Projects)

**Use Case:** Multiple specialized agents that operate independently.

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace as trace_api

# Agent 1: Customer Support
support_tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="customer-support-agent"
)
trace_api.set_tracer_provider(support_tracer.provider)
OpenAIInstrumentor().instrument()

@support_tracer.trace(event_type="chain", event_name="handle_ticket")
def handle_support_ticket(ticket_id: str):
    # Your agent logic
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Handle ticket {ticket_id}"}]
    )
    return response.choices[0].message.content


# Agent 2: Sales Assistant (Different Tracer Instance)
sales_tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="sales-assistant-agent"
)

@sales_tracer.trace(event_type="chain", event_name="qualify_lead")
def qualify_sales_lead(lead_id: str):
    # Completely isolated from support_tracer
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Qualify lead {lead_id}"}]
    )
    return response.choices[0].message.content
```

**Key Benefits:**
- ✅ Zero context pollution between agents
- ✅ Separate dashboards per agent
- ✅ Independent evaluation pipelines

---

### Pattern 2: Coordinated Multi-Agent System (Parent-Child Spans)

**Use Case:** Orchestrator agent that delegates to specialized sub-agents.

```python
from honeyhive import HoneyHiveTracer

# Single tracer for the entire multi-agent system
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="multi-agent-orchestrator"
)

@tracer.trace(event_type="chain", event_name="orchestrator")
def orchestrate_request(user_request: str):
    """Main orchestrator - creates parent span."""
    
    # Step 1: Research Agent (child span)
    research_results = research_agent(user_request)
    
    # Step 2: Analysis Agent (child span)
    analysis = analysis_agent(research_results)
    
    # Step 3: Response Agent (child span)
    final_response = response_agent(analysis)
    
    return final_response


@tracer.trace(event_type="tool", event_name="research_agent")
def research_agent(query: str):
    """Research sub-agent - automatically creates child span."""
    with tracer.enrich_span(
        metadata={
            "agent_role": "research",
            "query_type": "web_search"
        }
    ):
        # LLM call here (auto-instrumented)
        results = openai_client.chat.completions.create(...)
        return results


@tracer.trace(event_type="tool", event_name="analysis_agent")
def analysis_agent(data: str):
    """Analysis sub-agent - automatically creates child span."""
    with tracer.enrich_span(
        metadata={
            "agent_role": "analysis",
            "complexity": "high"
        }
    ):
        analysis = openai_client.chat.completions.create(...)
        return analysis


@tracer.trace(event_type="tool", event_name="response_agent")
def response_agent(analysis: str):
    """Response sub-agent - automatically creates child span."""
    with tracer.enrich_span(
        metadata={
            "agent_role": "response",
            "tone": "professional"
        }
    ):
        response = openai_client.chat.completions.create(...)
        return response
```

**Resulting Span Hierarchy:**
```
orchestrator (CHAIN) → parent span
  ├─ research_agent (TOOL) → child span 1
  │   └─ openai.chat.completions (MODEL) → grandchild span
  ├─ analysis_agent (TOOL) → child span 2
  │   └─ openai.chat.completions (MODEL) → grandchild span
  └─ response_agent (TOOL) → child span 3
      └─ openai.chat.completions (MODEL) → grandchild span
```

**Key Benefits:**
- ✅ Full trace of multi-agent workflow
- ✅ Automatic parent-child relationships via OpenTelemetry context
- ✅ Per-agent metadata for filtering/analysis

---

## 2. Retry Tracking Patterns

### Pattern 1: Application-Level Retry with Tracing

**Use Case:** Tracking LLM call retries (rate limits, timeouts) with full observability.

```python
from honeyhive import HoneyHiveTracer
import time

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="retry-demo"
)

@tracer.trace(event_type="chain", event_name="agent_with_retry")
def call_llm_with_retry(prompt: str, max_retries: int = 3):
    """LLM call with exponential backoff and full retry tracking."""
    
    for attempt in range(1, max_retries + 1):
        # Create a span for each retry attempt
        with tracer.trace_context(
            event_type="model",
            event_name=f"llm_call_attempt_{attempt}"
        ):
            tracer.enrich_span(
                metadata={
                    "retry_attempt": attempt,
                    "max_retries": max_retries,
                    "backoff_strategy": "exponential"
                }
            )
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Success - enrich with success metadata
                tracer.enrich_span(
                    metadata={
                        "retry_success": True,
                        "successful_attempt": attempt
                    }
                )
                return response.choices[0].message.content
                
            except Exception as e:
                error_type = type(e).__name__
                
                # Enrich span with failure details
                tracer.enrich_span(
                    metadata={
                        "retry_failed": True,
                        "error_type": error_type,
                        "error_message": str(e),
                        "will_retry": attempt < max_retries
                    }
                )
                
                if attempt == max_retries:
                    # Final attempt failed - raise
                    raise
                
                # Calculate backoff delay
                delay = min(2 ** attempt, 60)  # Cap at 60s
                tracer.enrich_span(metadata={"backoff_delay_seconds": delay})
                time.sleep(delay)
```

**What You'll See in HoneyHive:**
- Each retry attempt as a separate span
- Full error context for failed attempts
- Backoff timing metadata
- Success rate analytics across all retries

---

### Pattern 2: Circuit Breaker Pattern with Tracing

**Use Case:** Prevent cascading failures in agent systems.

```python
from honeyhive import HoneyHiveTracer
from datetime import datetime, timedelta

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="circuit-breaker-demo"
)

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        # Check circuit state
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half_open"
            else:
                # Circuit is open - fail fast
                tracer.enrich_span(
                    metadata={
                        "circuit_breaker_state": "open",
                        "action": "fail_fast",
                        "failure_count": self.failure_count
                    }
                )
                raise Exception("Circuit breaker is OPEN - failing fast")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
                tracer.enrich_span(
                    metadata={
                        "circuit_breaker_state": "closed",
                        "action": "reset"
                    }
                )
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                tracer.enrich_span(
                    metadata={
                        "circuit_breaker_state": "open",
                        "action": "opened",
                        "failure_count": self.failure_count,
                        "threshold": self.failure_threshold
                    }
                )
            
            raise


# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)

@tracer.trace(event_type="model", event_name="protected_llm_call")
def protected_llm_call(prompt: str):
    def _call():
        return openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
    
    return circuit_breaker.call(_call)
```

---

## 3. Evaluation Integration Patterns

### Pattern 1: Inline Evaluation During Agent Execution

**Use Case:** Evaluate agent outputs in real-time as part of your agent workflow.

```python
from honeyhive import HoneyHiveTracer, evaluator

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="agent-with-evaluation"
)

# Define evaluators
@evaluator
def response_quality(outputs, inputs, ground_truth):
    """Evaluate response quality on 0-1 scale."""
    response_text = outputs.get("response", "")
    
    # Your evaluation logic here
    score = 0.0
    if len(response_text) > 50:
        score += 0.3
    if "specific" in response_text.lower():
        score += 0.3
    if ground_truth and ground_truth.get("expected_keyword") in response_text:
        score += 0.4
    
    return {"score": score, "passed": score >= 0.7}


@evaluator
def safety_check(outputs, inputs, ground_truth):
    """Check for unsafe content."""
    response_text = outputs.get("response", "")
    
    unsafe_patterns = ["violence", "illegal", "harm"]
    is_safe = not any(pattern in response_text.lower() for pattern in unsafe_patterns)
    
    return {"score": 1.0 if is_safe else 0.0, "passed": is_safe}


@tracer.trace(event_type="chain", event_name="evaluated_agent")
def agent_with_evaluation(user_query: str, expected_keyword: str = None):
    """Agent that evaluates its own outputs."""
    
    # Generate response
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_query}]
    )
    output_text = response.choices[0].message.content
    
    # Prepare evaluation inputs
    inputs = {"query": user_query}
    outputs = {"response": output_text}
    ground_truth = {"expected_keyword": expected_keyword} if expected_keyword else None
    
    # Run evaluators
    quality_result = response_quality(outputs, inputs, ground_truth)
    safety_result = safety_check(outputs, inputs, ground_truth)
    
    # Enrich span with evaluation metrics
    tracer.enrich_span(
        metadata={
            "evaluation": {
                "quality_score": quality_result["score"],
                "quality_passed": quality_result["passed"],
                "safety_score": safety_result["score"],
                "safety_passed": safety_result["passed"],
                "overall_passed": quality_result["passed"] and safety_result["passed"]
            }
        }
    )
    
    return {
        "response": output_text,
        "evaluation": {
            "quality": quality_result,
            "safety": safety_result
        }
    }
```

---

### Pattern 2: Batch Evaluation with Experiment Tracking

**Use Case:** Evaluate agent performance across a dataset with full experiment tracking.

```python
from honeyhive import HoneyHiveTracer
from honeyhive.experiments import evaluate

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="agent-experiments"
)

# Define your agent function
def my_agent(inputs, ground_truth=None):
    """Your agent logic to test."""
    query = inputs.get("query", "")
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    
    return {"output": response.choices[0].message.content}


# Define evaluators (same as Pattern 1)
@evaluator
def accuracy(outputs, inputs, ground_truth):
    """Check if output matches expected answer."""
    output_text = outputs.get("output", "").lower()
    expected = ground_truth.get("answer", "").lower() if ground_truth else ""
    
    # Simple keyword matching (you'd use embeddings in production)
    score = 1.0 if expected in output_text else 0.0
    return {"score": score, "passed": score == 1.0}


@evaluator
def response_length(outputs, inputs, ground_truth):
    """Evaluate response comprehensiveness."""
    output_text = outputs.get("output", "")
    word_count = len(output_text.split())
    
    # Expect 50-200 words
    if 50 <= word_count <= 200:
        score = 1.0
    elif word_count < 50:
        score = word_count / 50.0
    else:
        score = max(0.5, 200 / word_count)
    
    return {"score": score, "passed": score >= 0.7}


# Prepare dataset
dataset = [
    {
        "inputs": {"query": "What is machine learning?"},
        "ground_truth": {"answer": "algorithms that learn from data"}
    },
    {
        "inputs": {"query": "Explain neural networks"},
        "ground_truth": {"answer": "inspired by biological neurons"}
    },
    # ... more examples
]

# Run experiment with evaluation
result = evaluate(
    function=my_agent,
    dataset=dataset,
    evaluators=[accuracy, response_length],
    api_key=os.getenv("HH_API_KEY"),
    project="agent-experiments",
    name="Agent v1.2 - GPT-4 Baseline",
    max_workers=5,  # Parallel execution
    aggregate_function="average",  # Backend aggregates metrics
    verbose=True
)

# Access results
print(f"Experiment Success: {result.success}")
print(f"Passed: {len(result.passed)}/{len(dataset)}")
print(f"Failed: {len(result.failed)}/{len(dataset)}")
print(f"Average Accuracy: {result.metrics.get('accuracy', {}).get('average', 0):.2f}")
print(f"Average Length Score: {result.metrics.get('response_length', {}).get('average', 0):.2f}")
```

**What This Does:**
- ✅ Creates an experiment run in HoneyHive
- ✅ Executes agent against all datapoints (with tracing)
- ✅ Runs evaluators on all outputs
- ✅ Backend aggregates metrics (average, min, max, etc.)
- ✅ Full trace for every datapoint in the experiment

---

## 4. Cost Tracking Patterns

### Pattern 1: Automatic Cost Tracking via Instrumentors

**Use Case:** Zero-code cost tracking for instrumented LLM calls.

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace as trace_api

# Initialize tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="cost-tracking-demo"
)

# Set as global provider
trace_api.set_tracer_provider(tracer.provider)

# Instrument OpenAI (automatically tracks costs)
OpenAIInstrumentor().instrument()

# Your agent code - costs tracked automatically!
@tracer.trace(event_type="chain", event_name="cost_tracked_agent")
def my_agent(query: str):
    # These LLM calls automatically track:
    # - gen_ai.usage.input_tokens
    # - gen_ai.usage.output_tokens
    # - cost_usd (if instrumentor supports it)
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    
    return response.choices[0].message.content
```

**What Gets Tracked Automatically:**
- `gen_ai.usage.input_tokens`
- `gen_ai.usage.output_tokens`
- `gen_ai.request.model`
- `gen_ai.response.model`
- `cost_usd` (if instrumentor calculates it)

---

### Pattern 2: Manual Cost Enrichment for Custom Models

**Use Case:** Track costs for models not covered by instrumentors (self-hosted, custom pricing).

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="custom-cost-tracking"
)

# Define your pricing (example)
PRICING = {
    "llama-2-70b": {"input": 0.0007 / 1000, "output": 0.0009 / 1000},  # per token
    "claude-3-opus": {"input": 0.015 / 1000, "output": 0.075 / 1000},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for custom models."""
    pricing = PRICING.get(model, {"input": 0, "output": 0})
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    return input_cost + output_cost


@tracer.trace(event_type="model", event_name="custom_model_call")
def call_custom_model(prompt: str, model: str = "llama-2-70b"):
    """Custom model call with manual cost tracking."""
    
    # Your custom LLM API call
    response = your_custom_llm_api.generate(
        model=model,
        prompt=prompt
    )
    
    # Extract token counts (from your API response)
    input_tokens = response.get("usage", {}).get("prompt_tokens", 0)
    output_tokens = response.get("usage", {}).get("completion_tokens", 0)
    total_tokens = input_tokens + output_tokens
    
    # Calculate cost
    cost = calculate_cost(model, input_tokens, output_tokens)
    
    # Enrich span with cost metadata
    tracer.enrich_span(
        metadata={
            "gen_ai.usage.input_tokens": input_tokens,
            "gen_ai.usage.output_tokens": output_tokens,
            "gen_ai.usage.total_tokens": total_tokens,
            "cost_usd": cost,
            "gen_ai.request.model": model,
            "gen_ai.response.model": model,
            "pricing_tier": "custom"
        }
    )
    
    return response.get("text", "")
```

---

### Pattern 3: Session-Level Cost Aggregation

**Use Case:** Track total cost for an entire agent session (multi-turn conversation).

```python
from honeyhive import HoneyHiveTracer

class CostTrackingAgent:
    def __init__(self, api_key: str, project: str):
        self.tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            session_name="cost-tracking-session"
        )
        self.session_cost = 0.0
        self.session_tokens = {"input": 0, "output": 0}
    
    @tracer.trace(event_type="chain", event_name="conversation_turn")
    def process_turn(self, user_message: str):
        """Process a single conversation turn with cost tracking."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        
        # Extract usage (OpenAI format)
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        
        # Calculate turn cost (GPT-4 pricing as of 2025)
        turn_cost = (input_tokens * 0.03 / 1000) + (output_tokens * 0.06 / 1000)
        
        # Update session totals
        self.session_cost += turn_cost
        self.session_tokens["input"] += input_tokens
        self.session_tokens["output"] += output_tokens
        
        # Enrich span with turn-level AND session-level costs
        self.tracer.enrich_span(
            metadata={
                "turn_cost_usd": turn_cost,
                "turn_input_tokens": input_tokens,
                "turn_output_tokens": output_tokens,
                "session_cost_usd": self.session_cost,
                "session_input_tokens": self.session_tokens["input"],
                "session_output_tokens": self.session_tokens["output"],
                "session_total_tokens": sum(self.session_tokens.values())
            }
        )
        
        return response.choices[0].message.content
    
    def get_session_summary(self):
        """Get session-level cost summary."""
        return {
            "total_cost_usd": self.session_cost,
            "input_tokens": self.session_tokens["input"],
            "output_tokens": self.session_tokens["output"],
            "total_tokens": sum(self.session_tokens.values())
        }


# Usage
agent = CostTrackingAgent(
    api_key=os.getenv("HH_API_KEY"),
    project="cost-demo"
)

# Multi-turn conversation
agent.process_turn("What is machine learning?")
agent.process_turn("Can you give me an example?")
agent.process_turn("What about deep learning?")

# Get final cost
summary = agent.get_session_summary()
print(f"Session Total Cost: ${summary['total_cost_usd']:.4f}")
print(f"Total Tokens: {summary['total_tokens']:,}")
```

---

## 5. Production Best Practices

### 1. Environment-Specific Configuration

```python
import os

# Use environment variables for configuration
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),  # Required
    project=os.getenv("HH_PROJECT", "my-agent"),
    source=os.getenv("HH_SOURCE", "production"),
    test_mode=os.getenv("HH_TEST_MODE", "false").lower() == "true"
)
```

### 2. Graceful Degradation

```python
# SDK degrades gracefully if API key is missing
try:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),  # May be None
        project="my-agent"
    )
except Exception as e:
    print(f"Warning: Tracing disabled - {e}")
    tracer = None

# Agent still works without tracing
if tracer:
    @tracer.trace(event_type="chain")
    def my_agent(query):
        # ...
        pass
else:
    def my_agent(query):
        # Same logic, no tracing
        # ...
        pass
```

### 3. Lambda Optimization

```python
# SDK auto-detects Lambda and optimizes itself
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="lambda-agent"
)
# Automatically uses:
# - Lambda-optimized lock strategy (0.5s timeout)
# - Fast flush (2.0s timeout)
# - Reduced batch size for faster sends
```

### 4. Structured Metadata

```python
# Use structured metadata for easy filtering
@tracer.trace(event_type="chain", event_name="structured_agent")
def my_agent(user_id: str, query: str):
    tracer.enrich_span(
        metadata={
            "user": {
                "id": user_id,
                "tier": "premium"
            },
            "request": {
                "type": "query",
                "category": "support"
            },
            "agent": {
                "version": "1.2.0",
                "model": "gpt-4"
            }
        }
    )
    # ...
```

---

## 📚 Next Steps

- **Try the Examples:** Copy-paste these patterns into your agent code
- **Explore the Dashboard:** View traces, costs, and evaluations in HoneyHive
- **Customize Evaluators:** Write domain-specific evaluators for your use case
- **Scale Up:** Use multi-instance tracers for complex multi-agent systems

---

## 🔗 Related Documentation

- [BYOI Architecture](../explanation/architecture/byoi-design.rst) - Bring Your Own Instrumentor pattern
- [Multi-Instance Tracers](../how-to/tracer/multi-instance.rst) - Advanced multi-agent patterns
- [Lambda Testing](../development/testing/lambda-testing.rst) - Production Lambda deployment
- [Evaluation API](../api-reference/experiments.rst) - Full evaluation API reference

---

**Questions?** Open an issue on GitHub or join our Discord community!

