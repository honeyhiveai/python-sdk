Tracing Fundamentals
====================

.. note::
   This document explains the fundamental concepts of distributed tracing and how they apply to LLM applications.

.. seealso::
   **HoneyHive Tracer Architecture**
   
   For a deep dive into how the HoneyHive SDK implements these concepts with a modular, mixin-based architecture, see :doc:`/reference/api/tracer-architecture`.

What is Distributed Tracing?
----------------------------

Distributed tracing is a method for tracking requests as they flow through complex systems. It provides:

- **End-to-end visibility** into request execution
- **Performance insights** at each step
- **Error correlation** across system boundaries
- **Context propagation** between services

**Traditional Web Application Tracing:**

.. code-block:: text

   User Request → Load Balancer → Web Server → Database → Response
   [-------------- Single Trace --------------]

**LLM Application Tracing:**

.. code-block:: text

   User Query → Preprocessing → LLM Call → Post-processing → Response
   [-------------- Enhanced with AI Context --------------]

Core Tracing Concepts
---------------------

**Traces**

A trace represents a complete request journey:

.. code-block:: text

   # Example trace hierarchy
   customer_support_request  # Root span
   ├── validate_input       # Child span
   ├── classify_query       # Child span
   ├── llm_completion      # Child span
   │   ├── prompt_preparation
   │   └── api_call
   └── format_response     # Child span

**Spans**

Individual operations within a trace:

.. code-block:: python

   # Each span contains:
   {
       "span_id": "abc123",
       "trace_id": "xyz789",
       "parent_id": "parent456",
       "operation_name": "llm_completion",
       "start_time": "2024-01-15T10:30:00Z",
       "end_time": "2024-01-15T10:30:02Z",
       "duration": 2000,  # milliseconds
       "attributes": {
           "llm.model": "gpt-4",
           "llm.tokens.input": 45,
           "llm.tokens.output": 67
       },
       "status": "ok"
   }

**Attributes**

Key-value metadata attached to spans:

.. code-block:: python

   # Standard attributes
   "http.method": "POST"
   "http.status_code": 200
   
   # LLM-specific attributes
   "llm.model": "gpt-3.5-turbo"
   "llm.temperature": 0.7
   "llm.tokens.prompt": 150
   "llm.tokens.completion": 89
   
   # Business attributes
   "customer.id": "cust_123"
   "support.priority": "high"

**Context Propagation**

How trace context flows between operations:

.. code-block:: python

   def parent_function():
       with tracer.trace("parent_operation") as span:
           span.set_attribute("operation.type", "parent")
           child_function()  # Automatically inherits context
   
   def child_function():
       with tracer.trace("child_operation") as span:
           span.set_attribute("operation.type", "child")
           # This span is automatically a child of parent_operation

**Unified Enrichment Architecture**

The HoneyHive SDK provides a unified approach to span and session enrichment through a carefully designed architecture that supports multiple usage patterns while maintaining backwards compatibility:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       subgraph "Enrichment Entry Points"
           EP1["from tracer<br/>import enrich_span"]
           EP2["from decorators<br/>import enrich_span"]
           EP3["from otel<br/>import enrich_span"]
       end
       
       subgraph "Unified Implementation"
           UI["otel_tracer.enrich_span()<br/>(Main Implementation)"]
           
           subgraph "Pattern Detection Logic"
               PD["if context_manager_args:<br/>return context_manager<br/>else:<br/>return direct_call"]
           end
       end
       
       subgraph "Execution Paths"
           CM["Context Manager Pattern<br/>_enrich_span_context_manager()<br/>• Sets span attributes<br/>• Yields context<br/>• Rich experiments"]
           DC["Direct Method Call<br/>HoneyHiveTracer.enrich_span()<br/>• Updates HH events<br/>• Returns boolean<br/>• Direct API calls"]
       end
       
       subgraph "OpenTelemetry Integration"
           SPAN["Span Creation & Attributes"]
           OTEL["OpenTelemetry Tracer"]
       end
       
       EP1 ==> UI
       EP2 ==> UI  
       EP3 ==> UI
       
       UI ==> PD
       
       PD ==> CM
       PD ==> DC
       
       CM ==> SPAN
       DC ==> SPAN
       
       SPAN ==> OTEL
       
       classDef entryPoint fill:#01579b,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef unified fill:#e65100,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef pattern fill:#4a148c,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef execution fill:#1b5e20,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef otel fill:#ad1457,stroke:#ffffff,stroke-width:4px,color:#ffffff
       
       class EP1,EP2,EP3 entryPoint
       class UI unified
       class PD pattern
       class CM,DC execution
       class SPAN,OTEL otel

**Key Benefits:**

1. **Single Source of Truth** - All enrichment logic centralized in ``otel_tracer.py``
2. **No Circular Imports** - Clean dependency flow from decorators → otel_tracer
3. **Consistent Behavior** - Same functionality regardless of import path
4. **Pattern Detection** - Automatic detection of usage pattern based on arguments
5. **Full Backwards Compatibility** - All existing code continues to work unchanged

LLM-Specific Tracing Considerations
-----------------------------------

**Token-Level Observability**

Unlike traditional requests, LLM calls have unique characteristics:

.. code-block:: python

   # Traditional API call
   {
       "operation": "database_query",
       "duration": 50,  # milliseconds
       "rows_returned": 25
   }
   
   # LLM API call
   {
       "operation": "llm_completion",
       "duration": 1500,  # milliseconds
       "tokens": {
           "prompt": 150,
           "completion": 89,
           "total": 239
       },
       "cost_usd": 0.00478,
       "model": "gpt-3.5-turbo"
   }

**Prompt Engineering Context**

Tracking how different prompts affect outcomes:

.. code-block:: python

   from honeyhive.models import EventType
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def test_prompt_variations(query: str):
       """Test different prompt strategies."""
       
       prompts = {
           "basic": f"Answer: {query}",
           "detailed": f"Provide a detailed answer to: {query}",
           "step_by_step": f"Think step by step and answer: {query}"
       }
       
       results = {}
       for strategy, prompt in prompts.items():
           with tracer.trace(f"prompt_strategy_{strategy}") as span:
               span.set_attribute("prompt.strategy", strategy)
               span.set_attribute("prompt.length", len(prompt))
               
               result = llm_call(prompt)
               
               span.set_attribute("response.length", len(result))
               span.set_attribute("response.quality_score", evaluate_quality(result))
               
               results[strategy] = result
       
       return results

**Quality and Evaluation Tracking**

Embedding evaluation directly in traces:

.. code-block:: python

   @trace(tracer=tracer)
   @evaluate(evaluator=quality_evaluator)
   def generate_response(prompt: str) -> str:
       """Generate response with automatic quality evaluation."""
       
       response = llm_call(prompt)
       
       # Evaluation results automatically added to span:
       # - evaluation.score: 8.5
       # - evaluation.feedback: "Clear and helpful response"
       # - evaluation.criteria_scores: {...}
       
       return response

Sampling and Performance
------------------------

**Why Sampling Matters**

High-volume applications need intelligent sampling:

.. code-block:: python

   # Sampling strategies
   
   # 1. Percentage-based sampling
   @trace(tracer=tracer) if random.random() < 0.1 else lambda f: f
   def high_volume_function():
       pass  # Only trace 10% of calls
   
   # 2. Conditional sampling
   def should_trace(request):
       # Always trace errors
       if request.get("error"):
           return True
       # Always trace premium customers
       if request.get("customer_tier") == "premium":
           return True
       # Sample 1% of regular requests
       return random.random() < 0.01
   
   # 3. Adaptive sampling
   def adaptive_trace(tracer, request):
       current_load = get_system_load()
       sample_rate = 0.1 if current_load < 0.7 else 0.01
       
       if random.random() < sample_rate:
           return trace(tracer=tracer)
       return lambda f: f

**Performance Best Practices**

.. code-block:: python

   # Good: Selective attribute collection
   @trace(tracer=tracer)
   def optimized_function(large_data: dict):
       # Don't trace large objects directly
       enrich_span({
           "data.size_mb": len(str(large_data)) / 1024 / 1024,
           "data.keys_count": len(large_data),
           "data.type": type(large_data).__name__
       })
       
       # Process large_data...
       
   # Bad: Tracing large objects
   @trace(tracer=tracer)
   def unoptimized_function(large_data: dict):
       enrich_span({
           "data.full_content": large_data  # This could be huge!
       })

Trace Analysis Patterns
-----------------------

**Finding Performance Bottlenecks**

.. code-block:: python

   # Query traces to find slow operations
   slow_traces = tracer.query_traces(
       time_range="last_24h",
       filter="duration > 5000",  # Slower than 5 seconds
       group_by="operation_name"
   )
   
   for operation, traces in slow_traces.items():
       avg_duration = sum(t.duration for t in traces) / len(traces)
       print(f"{operation}: {avg_duration}ms average")

**Error Pattern Analysis**

.. code-block:: python

   # Find common error patterns
   error_traces = tracer.query_traces(
       time_range="last_7d",
       filter="status = error",
       group_by=["error.type", "llm.model"]
   )
   
   for (error_type, model), count in error_traces.items():
       print(f"Model {model}: {count} {error_type} errors")

**Cost Analysis**

.. code-block:: python

   # Track LLM costs over time
   cost_data = tracer.query_traces(
       time_range="last_30d",
       filter="llm.cost_usd > 0",
       aggregate=["sum(llm.cost_usd)", "avg(llm.tokens.total)"],
       group_by=["llm.model", "date"]
   )

Integration with Monitoring Systems
-----------------------------------

**Metrics from Traces**

Convert trace data into monitoring metrics:

.. code-block:: python

   # Example: Generate metrics from trace data
   def generate_metrics_from_traces():
       recent_traces = tracer.get_traces(hours=1)
       
       metrics = {
           "llm_requests_total": len(recent_traces),
           "llm_requests_by_model": Counter(),
           "llm_avg_latency": {},
           "llm_error_rate": {},
           "llm_cost_per_hour": 0
       }
       
       for trace in recent_traces:
           model = trace.get_attribute("llm.model")
           if model:
               metrics["llm_requests_by_model"][model] += 1
               
               # Track latency
               if model not in metrics["llm_avg_latency"]:
                   metrics["llm_avg_latency"][model] = []
               metrics["llm_avg_latency"][model].append(trace.duration)
               
               # Track costs
               cost = trace.get_attribute("llm.cost_usd", 0)
               metrics["llm_cost_per_hour"] += cost
       
       return metrics

**Alerting Integration**

.. code-block:: python

   def check_trace_health():
       """Monitor trace data for alerting conditions."""
       
       recent_traces = tracer.get_traces(minutes=15)
       
       # Check error rate
       error_rate = sum(1 for t in recent_traces if t.status == "error") / len(recent_traces)
       if error_rate > 0.05:  # 5% error rate
           send_alert(f"High error rate: {error_rate:.2%}")
       
       # Check latency
       avg_latency = sum(t.duration for t in recent_traces) / len(recent_traces)
       if avg_latency > 5000:  # 5 seconds
           send_alert(f"High latency: {avg_latency}ms")
       
       # Check cost burn rate
       hourly_cost = sum(t.get_attribute("llm.cost_usd", 0) for t in recent_traces) * 4  # 15min → 1hr
       if hourly_cost > 10:  # $10/hour
           send_alert(f"High cost burn rate: ${hourly_cost:.2f}/hour")

Best Practices Summary
----------------------

**1. Start Simple**
- Begin with basic @trace decorators
- Add complexity gradually
- Focus on business-critical operations

**2. Balance Detail with Performance**
- Use sampling for high-volume operations
- Avoid tracing large data objects
- Focus on actionable metrics

**3. Structure Your Traces**
- Use consistent naming conventions
- Add business context with attributes
- Maintain clear span hierarchies

**4. Monitor Your Monitoring**
- Track tracing overhead
- Monitor data volume and costs
- Set up alerting on trace health

**5. Use Traces for Improvement**
- Analyze patterns regularly
- Use data to optimize prompts
- Feed insights back into development

See Also
--------

- :doc:`llm-observability` - LLM-specific observability concepts
- :doc:`../architecture/overview` - Overall system architecture
- :doc:`../../tutorials/01-setup-first-tracer` - Practical tracing tutorial
