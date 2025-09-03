Build Custom Tracing
=====================

Sophisticated observability patterns for complex LLM applications and production environments.

.. toctree::
   :maxdepth: 2

   custom-spans
   tracer-auto-discovery

Overview
--------

Advanced tracing techniques help you gain deeper insights into complex LLM applications, optimize performance, and implement production-ready observability patterns.

**When to use advanced techniques:**

- Multi-service LLM applications
- High-throughput production systems
- Complex agent workflows
- Performance-critical applications
- Distributed architectures

Quick Reference
---------------

**Key Techniques:**

- **Custom Spans**: Custom business logic tracing with detailed context
- **Distributed Tracing**: Multi-service architectures and workflows
- **Performance Optimization**: High-performance applications with minimal overhead
- **Context Propagation**: Service boundary management and async operations
- **Sampling Strategies**: Cost and performance optimization techniques
- **Batch Processing**: High-throughput data processing patterns

Getting Started
---------------

**1. Basic Custom Spans**

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       
   )

   # Custom business logic tracing
   with tracer.start_span("business_process") as span:
       span.set_attribute("process.type", "user_onboarding")
       span.set_attribute("user.tier", "premium")
       result = complex_business_logic()

**2. Performance Monitoring**

.. code-block:: python

   import time
   
   with tracer.start_span("performance_critical") as span:
       start_time = time.perf_counter()
       
       # Your operation
       result = expensive_operation()
       
       duration = time.perf_counter() - start_time
       span.set_attribute("performance.duration_ms", duration * 1000)
       span.set_attribute("performance.result_size", len(str(result)))

**3. Context Enrichment**

.. code-block:: python

   # Rich context for debugging and analysis
   with tracer.start_span("llm_generation") as span:
       span.set_attribute("user.id", user_id)
       span.set_attribute("session.id", session_id)
       span.set_attribute("model.provider", "openai")
       span.set_attribute("model.version", "gpt-4")
       span.set_attribute("prompt.template", template_name)
       span.set_attribute("prompt.variables", json.dumps(variables))

Best Practices
--------------

**1. Span Hierarchy Design**

.. code-block:: python

   # Good: Logical hierarchy
   with tracer.start_span("user_request") as request_span:
       request_span.set_attribute("request.id", request_id)
       
       with tracer.start_span("authentication") as auth_span:
           auth_result = authenticate_user()
           auth_span.set_attribute("auth.success", auth_result.success)
       
       with tracer.start_span("business_logic") as logic_span:
           logic_span.set_attribute("logic.complexity", "high")
           result = process_request()
       
       with tracer.start_span("response_formatting") as format_span:
           formatted_result = format_response(result)

**2. Attribute Naming Conventions**

.. code-block:: python

   # Use consistent, hierarchical naming
   span.set_attribute("llm.provider", "openai")          # Provider info
   span.set_attribute("llm.model", "gpt-4")              # Model info
   span.set_attribute("llm.temperature", 0.7)            # Parameters
   span.set_attribute("llm.tokens.input", 150)           # Token counts
   span.set_attribute("llm.tokens.output", 89)
   span.set_attribute("user.id", "user123")              # User context
   span.set_attribute("session.duration_ms", 1500)       # Session info
   span.set_attribute("performance.cache_hit", True)     # Performance

**3. Error Handling and Status**

.. code-block:: python

   with tracer.start_span("risky_operation") as span:
       try:
           result = potentially_failing_operation()
           span.set_attribute("operation.success", True)
           span.set_attribute("operation.result_type", type(result).__name__)
           
       except SpecificError as e:
           span.set_attribute("operation.success", False)
           span.set_attribute("error.type", "SpecificError")
           span.set_attribute("error.message", str(e))
           span.set_status("ERROR", f"Operation failed: {e}")
           raise
           
       except Exception as e:
           span.set_attribute("operation.success", False)
           span.set_attribute("error.type", type(e).__name__)
           span.set_attribute("error.message", str(e))
           span.set_status("ERROR", f"Unexpected error: {e}")
           raise

Common Patterns
---------------

**Agent Workflow Tracing**

.. code-block:: python

   def trace_agent_workflow(user_query: str):
       with tracer.start_span("agent_workflow") as workflow_span:
           workflow_span.set_attribute("workflow.type", "multi_step_reasoning")
           workflow_span.set_attribute("workflow.input", user_query)
           
           # Step 1: Query understanding
           with tracer.start_span("query_understanding") as understand_span:
               intent = classify_intent(user_query)
               understand_span.set_attribute("intent.classified", intent)
           
           # Step 2: Information retrieval
           with tracer.start_span("information_retrieval") as retrieval_span:
               context = retrieve_context(intent, user_query)
               retrieval_span.set_attribute("retrieval.sources", len(context))
           
           # Step 3: LLM reasoning
           with tracer.start_span("llm_reasoning") as reasoning_span:
               response = llm_generate(user_query, context)
               reasoning_span.set_attribute("reasoning.tokens", len(response.split()))
           
           workflow_span.set_attribute("workflow.success", True)
           return response

**Multi-Provider Fallback**

.. code-block:: python

   def resilient_llm_call(prompt: str, providers: list):
       with tracer.start_span("resilient_llm_call") as main_span:
           main_span.set_attribute("resilience.providers", len(providers))
           main_span.set_attribute("resilience.prompt", prompt)
           
           for i, provider in enumerate(providers):
               with tracer.start_span(f"provider_attempt_{i+1}") as attempt_span:
                   attempt_span.set_attribute("provider.name", provider.name)
                   attempt_span.set_attribute("provider.priority", i + 1)
                   
                   try:
                       result = provider.generate(prompt)
                       attempt_span.set_attribute("provider.success", True)
                       main_span.set_attribute("resilience.successful_provider", provider.name)
                       main_span.set_attribute("resilience.attempts", i + 1)
                       return result
                       
                   except Exception as e:
                       attempt_span.set_attribute("provider.success", False)
                       attempt_span.set_attribute("provider.error", str(e))
                       attempt_span.set_status("ERROR", str(e))
           
           main_span.set_attribute("resilience.all_failed", True)
           raise Exception("All providers failed")

Performance Monitoring
----------------------

**Resource Usage Tracking**

.. code-block:: python

   import psutil
   import threading

   def trace_with_resource_monitoring(operation_name: str):
       def decorator(func):
           def wrapper(*args, **kwargs):
               with tracer.start_span(operation_name) as span:
                   # Pre-execution metrics
                   process = psutil.Process()
                   cpu_before = process.cpu_percent()
                   memory_before = process.memory_info().rss / 1024 / 1024  # MB
                   
                   span.set_attribute("resources.cpu_before", cpu_before)
                   span.set_attribute("resources.memory_before_mb", memory_before)
                   
                   start_time = time.perf_counter()
                   
                   try:
                       result = func(*args, **kwargs)
                       
                       # Post-execution metrics
                       end_time = time.perf_counter()
                       cpu_after = process.cpu_percent()
                       memory_after = process.memory_info().rss / 1024 / 1024
                       
                       span.set_attribute("resources.duration_ms", (end_time - start_time) * 1000)
                       span.set_attribute("resources.cpu_after", cpu_after)
                       span.set_attribute("resources.memory_after_mb", memory_after)
                       span.set_attribute("resources.memory_delta_mb", memory_after - memory_before)
                       
                       return result
                       
                   except Exception as e:
                       span.set_status("ERROR", str(e))
                       raise
           
           return wrapper
       return decorator

   # Usage
   @trace_with_resource_monitoring("heavy_computation")
   def process_large_dataset(data):
       # Resource-intensive operation
       return process(data)

See Also
--------

- :doc:`../integrations/index` - LLM provider integrations
- :doc:`../../development/testing/performance-testing` - Performance testing strategies
- :doc:`../monitoring/index` - Monitoring and alerting
- :doc:`../../reference/api/tracer` - HoneyHiveTracer API reference
