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

**1. Decorator-First Approach (Recommended)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType

   # Create HoneyHive tracer as a specialized tracer (doesn't override existing default)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Option 1: Use tracer instance directly (explicit, multi-instance friendly)
   @trace(tracer=tracer, event_type=EventType.tool)
   def explicit_tracer_function():
       """Function traced with specific HoneyHive tracer instance."""
       pass
   
   # Option 2: Set as default only if no other tracer exists (conditional)
   from opentelemetry import trace as otel_trace
   if not hasattr(otel_trace.get_tracer_provider(), '_tracer_provider'):
       # No existing tracer provider, safe to set as default
       from honeyhive import set_default_tracer
       set_default_tracer(tracer)

   # Multi-instance friendly approach (recommended)
   @trace(tracer=tracer, event_type=EventType.tool)
   def complex_business_logic(user_id: str, data: dict) -> dict:
       """Business logic with explicit HoneyHive tracer."""
       enrich_span({
           "process.type": "user_onboarding",
           "user.tier": "premium",
           "user.id": user_id,
           "data.size": len(str(data))
       })
       
       # Your business logic here
       result = process_user_data(data)
       
       enrich_span({
           "process.success": True,
           "result.items": len(result)
       })
       
       return result

   @trace(tracer=tracer, event_type=EventType.chain)
   def user_onboarding_workflow(user_id: str) -> bool:
       """Complete workflow with explicit HoneyHive tracer."""
       enrich_span({
           "workflow.type": "onboarding",
           "user.id": user_id
       })
       
       # Each function call uses the same tracer instance
       user_data = fetch_user_data(user_id)
       processed_data = complex_business_logic(user_id, user_data)
       success = save_processed_data(processed_data)
       
       enrich_span({"workflow.success": success})
       return success
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def fetch_user_data(user_id: str) -> dict:
       """Fetch user data with explicit HoneyHive tracer."""
       enrich_span({"user.id": user_id})
       return {"id": user_id, "name": "User"}
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def save_processed_data(data: dict) -> bool:
       """Save data with explicit HoneyHive tracer."""
       enrich_span({"data.size": len(str(data))})
       return True

**2. Performance Monitoring with Decorators**

.. code-block:: python

   import time
   
   # Multi-instance friendly approach
   @trace(tracer=tracer, event_type=EventType.tool)
   def expensive_operation(data_size: int) -> list:
       """Performance-critical operation with explicit HoneyHive tracer."""
       start_time = time.perf_counter()
       
       enrich_span({
           "performance.input_size": data_size,
           "performance.operation_type": "data_processing"
       })
       
       # Your expensive operation
       result = process_large_dataset(data_size)
       
       duration = time.perf_counter() - start_time
       enrich_span({
           "performance.duration_ms": duration * 1000,
           "performance.result_size": len(result),
           "performance.throughput": data_size / duration if duration > 0 else 0
       })
       
       return result

**3. Multi-Instance Philosophy**

HoneyHive tracers are designed to coexist with other tracing systems as specialized tracers:

.. code-block:: python

   # ✅ GOOD: HoneyHive as specialized tracer alongside general-purpose tracing
   import opentelemetry.trace as otel_trace
   from honeyhive import HoneyHiveTracer, trace
   
   # General-purpose tracer (e.g., for infrastructure monitoring)
   general_tracer = otel_trace.get_tracer("my-app")
   
   # Specialized HoneyHive tracer (for LLM/AI observability)
   honeyhive_tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Both tracers can coexist and create independent spans
   def my_function():
       # General infrastructure tracing
       with general_tracer.start_span("infrastructure_operation") as infra_span:
           infra_span.set_attribute("service.name", "my-service")
           
           # Specialized LLM tracing within the same operation
           llm_result = process_with_llm()  # Uses HoneyHive tracer
           
           infra_span.set_attribute("operation.success", True)

   @trace(tracer=honeyhive_tracer, event_type=EventType.model)
   def process_with_llm() -> str:
       """LLM processing with specialized HoneyHive tracing."""
       enrich_span({"llm.provider": "openai", "llm.model": "gpt-4"})
       return "LLM response"

**4. Context Manager (When Needed)**

Use context managers only for specific scenarios where decorators aren't suitable:

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def batch_processing_with_iterations(items: list) -> list:
       """Batch processing with per-item tracing."""
       results = []
       
       enrich_span({
           "batch.total_items": len(items),
           "batch.processing_mode": "sequential"
       })
       
       # Context manager for iteration-level spans (appropriate use)
       for i, item in enumerate(items):
           with tracer.start_span(f"process_item_{i}") as item_span:
               item_span.set_attribute("item.index", i)
               item_span.set_attribute("item.id", item.get("id"))
               
               # Use decorated function for actual processing
               result = process_single_item(item)
               results.append(result)
               
               item_span.set_attribute("item.success", result is not None)
       
       enrich_span({"batch.processed_items": len(results)})
       return results
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def process_single_item(item: dict) -> dict:
       """Process individual item with explicit tracer."""
       enrich_span({"item.type": item.get("type")})
       return {"processed": True, **item}

Best Practices
--------------

**1. Multi-Instance Tracer Design Pattern**

.. code-block:: python

   # ✅ RECOMMENDED: Explicit tracer instances for multi-instance compatibility
   honeyhive_tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )

   @trace(tracer=honeyhive_tracer, event_type=EventType.session)
   def handle_user_request(request_id: str, user_data: dict) -> dict:
       """Handle complete user request with explicit HoneyHive tracer."""
       enrich_span({
           "request.id": request_id,
           "request.type": "user_action"
       })
       
       # Each function call uses the same tracer instance
       auth_result = authenticate_user(user_data)
       processed_result = process_business_logic(auth_result)
       formatted_response = format_response(processed_result)
       
       enrich_span({"request.success": True})
       return formatted_response

   @trace(tracer=honeyhive_tracer, event_type=EventType.tool)
   def authenticate_user(user_data: dict) -> dict:
       """Authentication with explicit HoneyHive tracer."""
       enrich_span({"auth.method": "oauth2"})
       # Authentication logic
       result = {"success": True, "user_id": user_data["id"]}
       enrich_span({"auth.success": result["success"]})
       return result

   @trace(tracer=honeyhive_tracer, event_type=EventType.chain)
   def process_business_logic(auth_result: dict) -> dict:
       """Business logic with explicit HoneyHive tracer."""
       enrich_span({"logic.complexity": "high"})
       # Business logic here
       return {"processed": True, "data": auth_result}

   @trace(tracer=honeyhive_tracer, event_type=EventType.tool)
   def format_response(result: dict) -> dict:
       """Response formatting with explicit HoneyHive tracer."""
       enrich_span({"format.type": "json"})
       return {"status": "success", "result": result}

**2. When to Use Context Managers**

.. code-block:: python

   # ✅ APPROPRIATE: Non-function operations, iterations, conditional spans
   @trace(event_type=EventType.chain)
   def process_batch_with_context_managers(items: list) -> list:
       """Use context managers only when decorators aren't suitable."""
       results = []
       
       # Context manager for iteration-level spans (appropriate)
       for i, item in enumerate(items):
           with tracer.start_span(f"item_{i}") as item_span:
               item_span.set_attribute("item.index", i)
               
               # Still use decorated functions for actual work
               result = process_single_item(item)
               results.append(result)
       
       return results

   # ❌ AVOID: Using context managers for regular functions
   def bad_example():
       with tracer.start_span("business_function") as span:
           span.set_attribute("function.name", "business_logic")
           # This should be a decorated function instead
           return do_business_logic()

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

**Agent Workflow Tracing (Multi-Instance Friendly)**

.. code-block:: python

   # Explicit tracer for LLM/AI observability
   ai_tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="ai-workflows"
   )

   @trace(tracer=ai_tracer, event_type=EventType.session)
   def agent_workflow(user_query: str) -> str:
       """Multi-step agent workflow with explicit HoneyHive tracer."""
       enrich_span({
           "workflow.type": "multi_step_reasoning",
           "workflow.input": user_query,
           "workflow.steps": 3
       })
       
       # Each step uses the same tracer instance
       intent = classify_intent(user_query)
       context = retrieve_context(intent, user_query)
       response = llm_reasoning(user_query, context)
       
       enrich_span({
           "workflow.success": True,
           "workflow.response_length": len(response)
       })
       return response

   @trace(tracer=ai_tracer, event_type=EventType.tool)
   def classify_intent(user_query: str) -> str:
       """Query understanding with explicit HoneyHive tracer."""
       enrich_span({
           "intent.model": "bert-base-uncased",
           "intent.query_length": len(user_query)
       })
       
       intent = "information_seeking"  # Your classification logic
       
       enrich_span({
           "intent.classified": intent,
           "intent.confidence": 0.95
       })
       return intent

   @trace(tracer=ai_tracer, event_type=EventType.tool)
   def retrieve_context(intent: str, user_query: str) -> list:
       """Information retrieval with explicit HoneyHive tracer."""
       enrich_span({
           "retrieval.intent": intent,
           "retrieval.method": "vector_search"
       })
       
       context = ["doc1", "doc2", "doc3"]  # Your retrieval logic
       
       enrich_span({
           "retrieval.sources": len(context),
           "retrieval.success": True
       })
       return context

   @trace(tracer=ai_tracer, event_type=EventType.model)
   def llm_reasoning(user_query: str, context: list) -> str:
       """LLM reasoning with explicit HoneyHive tracer."""
       enrich_span({
           "reasoning.context_items": len(context),
           "reasoning.model": "gpt-4"
       })
       
       response = "Generated response"  # Your LLM call
       
       enrich_span({
           "reasoning.tokens": len(response.split()),
           "reasoning.success": True
       })
       return response

**Multi-Provider Fallback (Multi-Instance Friendly)**

.. code-block:: python

   # Explicit tracer for resilience monitoring
   resilience_tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="llm-resilience"
   )

   @trace(tracer=resilience_tracer, event_type=EventType.chain)
   def resilient_llm_call(prompt: str, providers: list) -> str:
       """Resilient LLM call with explicit HoneyHive tracer."""
       enrich_span({
           "resilience.providers": len(providers),
           "resilience.prompt_length": len(prompt),
           "resilience.strategy": "sequential_fallback"
       })
       
       for i, provider in enumerate(providers):
           try:
               # Each provider attempt uses the same tracer instance
               result = attempt_provider_call(provider, prompt, i + 1)
               
               enrich_span({
                   "resilience.successful_provider": provider.name,
                   "resilience.attempts": i + 1,
                   "resilience.success": True
               })
               return result
               
           except Exception as e:
               enrich_span({
                   f"resilience.attempt_{i+1}_failed": True,
                   f"resilience.attempt_{i+1}_error": str(e)
               })
               
               if i == len(providers) - 1:  # Last provider
                   enrich_span({"resilience.all_failed": True})
                   raise Exception("All providers failed")
       
       return ""  # Should never reach here

   @trace(tracer=resilience_tracer, event_type=EventType.model)
   def attempt_provider_call(provider, prompt: str, attempt_number: int) -> str:
       """Single provider attempt with explicit HoneyHive tracer."""
       enrich_span({
           "provider.name": provider.name,
           "provider.priority": attempt_number,
           "provider.model": getattr(provider, 'model', 'unknown')
       })
       
       try:
           result = provider.generate(prompt)
           
           enrich_span({
               "provider.success": True,
               "provider.response_length": len(result)
           })
           return result
           
       except Exception as e:
           enrich_span({
               "provider.success": False,
               "provider.error_type": type(e).__name__,
               "provider.error_message": str(e)
           })
           raise

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

- :doc:`../index` - LLM provider integrations
- :doc:`../../development/testing/performance-testing` - Performance testing strategies
- :doc:`../monitoring/index` - Monitoring and alerting
- :doc:`../../reference/api/tracer` - HoneyHiveTracer API reference
