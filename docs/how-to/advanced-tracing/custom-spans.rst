Custom Span Management
======================

Learn how to create and manage custom spans for business logic tracing, performance monitoring, and complex workflow observability.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Custom spans allow you to trace your specific business logic, workflow steps, and application components beyond just LLM calls. This provides complete observability into your application's behavior.

**Use Cases**:
- Business process tracking
- Performance bottleneck identification
- Complex workflow visualization
- Custom error tracking
- Resource utilization monitoring

Basic Custom Spans with Decorator-First Approach
------------------------------------------------

**Problem**: Track custom business logic with detailed context.

**Solution**: Use decorators as the primary pattern, context managers only when needed.

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span, set_default_tracer
   from honeyhive.models import EventType
   import time

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",      # Or set HH_API_KEY environment variable
       project="your-project"       # Or set HH_PROJECT environment variable
   )
   set_default_tracer(tracer)

   @trace(event_type=EventType.tool)
   def validate_request(request_data: dict) -> bool:
       """Validate request schema - automatically traced."""
       enrich_span({
           "validation.schema_version": "v2.1",
           "validation.data_size": len(str(request_data))
       })
       
       # Simulate validation logic
       is_valid = "type" in request_data and request_data.get("type") in ["query", "action"]
       
       enrich_span({
           "validation.success": is_valid,
           "validation.error": "schema_mismatch" if not is_valid else None
       })
       
       if not is_valid:
           raise ValueError("Invalid request schema")
       
       return is_valid

   @trace(event_type=EventType.chain)
   def complex_business_processing(request_data: dict) -> list:
       """Process business logic - automatically traced."""
       enrich_span({
           "logic.complexity": "medium",
           "logic.requires_external_api": True,
           "logic.input_type": request_data.get("type")
       })
       
       # Simulate complex processing
       time.sleep(0.1)  # Simulate work
       result = [{"item": i, "processed": True} for i in range(3)]
       
       enrich_span({
           "logic.result_items": len(result),
           "logic.success": True
       })
       
       return result

   @trace(event_type=EventType.tool)
   def format_response(result: list) -> dict:
       """Format response - automatically traced."""
       enrich_span({
           "format.input_items": len(result),
           "format.output_type": "json"
       })
       
       formatted_response = {
           "status": "success",
           "data": result,
           "processed_at": time.time()
       }
       
       enrich_span({
           "format.response_size": len(str(formatted_response))
       })
       
       return formatted_response

   @trace(event_type=EventType.chain)
   def process_user_request(user_id: str, request_data: dict) -> dict:
       """Process user request with comprehensive tracing - automatically traced."""
       enrich_span({
           "user.id": user_id,
           "request.type": request_data.get("type"),
           "request.size_bytes": len(str(request_data)),
           "request.timestamp": time.time()
       })
       
       try:
           # Step 1: Validate request (automatically traced)
           validate_request(request_data)
           
           # Step 2: Business logic processing (automatically traced)
           result = complex_business_processing(request_data)
           
           # Step 3: Response formatting (automatically traced)
           formatted_response = format_response(result)
           
           enrich_span({
               "request.success": True,
               "request.response_size": len(str(formatted_response))
           })
           
           return formatted_response
           
       except Exception as e:
           enrich_span({
               "request.success": False,
               "request.error_type": type(e).__name__,
               "request.error_message": str(e)
           })
           raise

**Benefits of Decorator-First Approach:**

- **Cleaner Code**: Business logic isn't cluttered with span management
- **Better Testing**: Each function can be tested independently
- **Automatic Hierarchy**: Nested function calls create proper trace hierarchy
- **Consistent Tracing**: All functions follow the same pattern
- **Error Handling**: Automatic exception capture with custom context

When to Use Context Managers
----------------------------

**Problem**: Some scenarios require fine-grained span control that decorators can't provide.

**Solution**: Use context managers sparingly for specific use cases:

1. **Non-Function Operations**: Code blocks that aren't functions
2. **Conditional Spans**: Dynamic span creation based on runtime conditions
3. **Fine-Grained Timing**: Loop iterations or micro-operations

.. code-block:: python

   from honeyhive import trace, set_default_tracer
   
   set_default_tracer(tracer)
   
   @trace(event_type=EventType.tool)
   def process_batch_items(items: list) -> list:
       """Process a batch of items with individual item tracing."""
       results = []
       
       # Context manager for iteration-level spans (appropriate use)
       for i, item in enumerate(items):
           with tracer.start_span(f"process_item_{i}") as item_span:
               item_span.set_attribute("item.index", i)
               item_span.set_attribute("item.id", item.get("id"))
               
               # Use decorated function for actual processing
               result = process_single_item(item)
               results.append(result)
               
               item_span.set_attribute("item.success", result is not None)
       
       return results
   
   @trace(event_type=EventType.tool)
   def process_single_item(item: dict) -> dict:
       """Process individual item - automatically traced."""
       enrich_span({
           "item.type": item.get("type"),
           "item.complexity": len(str(item))
       })
       
       # Business logic here
       processed_item = {"processed": True, **item}
       
       enrich_span({"processing.success": True})
       return processed_item

   @trace(event_type=EventType.chain)
   def adaptive_processing_workflow(data: dict, enable_detailed_tracing: bool = False):
       """Adaptive workflow with conditional tracing."""
       enrich_span({
           "workflow.detailed_tracing": enable_detailed_tracing,
           "workflow.data_size": len(data)
       })
       
       # Context manager for conditional detailed tracing (appropriate use)
       if enable_detailed_tracing:
           with tracer.start_span("detailed_preprocessing") as detail_span:
               detail_span.set_attribute("preprocessing.mode", "detailed")
               # Detailed preprocessing steps
               preprocessed = detailed_preprocess(data)
       else:
           # Simple processing without extra spans
           preprocessed = simple_preprocess(data)
       
       # Use decorated function for main processing
       return main_process(preprocessed)
   
   @trace(event_type=EventType.tool)
   def detailed_preprocess(data: dict) -> dict:
       """Detailed preprocessing - automatically traced."""
       return {"detailed": True, **data}
   
   @trace(event_type=EventType.tool)
   def simple_preprocess(data: dict) -> dict:
       """Simple preprocessing - automatically traced.""" 
       return {"simple": True, **data}
   
   @trace(event_type=EventType.tool)
   def main_process(data: dict) -> dict:
       """Main processing - automatically traced."""
       return {"processed": True, **data}

**Guidelines for Context Manager Usage:**

- ✅ **Iteration loops**: When tracing individual items in batch processing
- ✅ **Conditional tracing**: When spans depend on runtime conditions  
- ✅ **Non-function blocks**: Setup, cleanup, or configuration phases
- ❌ **Business functions**: Use decorators instead for better maintainability
- ❌ **Simple operations**: Avoid over-instrumenting with unnecessary spans

Enhanced Context Manager: enrich_span_context()
------------------------------------------------

**New in v1.0+:** For creating custom spans with HoneyHive-specific enrichment.

**Problem**: You need to create explicit spans (not using decorators) but want HoneyHive's structured enrichment (inputs, outputs, metadata) with proper namespacing.

**Solution**: Use ``enrich_span_context()`` instead of ``tracer.start_span()``.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.processing.context import enrich_span_context
   
   def process_conditional_workflow(data: dict, mode: str):
       """Example showing enrich_span_context for conditional spans."""
       
       # Standard decorator for the main function
       if mode == "detailed":
           # Use enrich_span_context for explicit span with HoneyHive enrichment
           with enrich_span_context(
               event_name="detailed_processing",
               inputs={"data": data, "mode": mode},
               metadata={"processing_type": "detailed", "complexity": "high"}
           ):
               result = perform_detailed_processing(data)
               tracer.enrich_span(outputs={"result": result, "items_processed": len(result)})
               return result
       else:
           # Simple processing without extra span
           return perform_simple_processing(data)

**What it Does:**

1. Creates a new span with the specified name
2. Applies HoneyHive-specific namespacing automatically:
   - ``inputs`` → ``honeyhive_inputs.*``
   - ``outputs`` → ``honeyhive_outputs.*``
   - ``metadata`` → ``honeyhive_metadata.*``
   - ``metrics`` → ``honeyhive_metrics.*``
   - ``feedback`` → ``honeyhive_feedback.*``
3. Sets the span as "current" so subsequent ``tracer.enrich_span()`` calls work correctly
4. Automatically closes the span on exit

Full Feature Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.processing.context import enrich_span_context
   
   def process_agent_invocation(agent_name: str, query: str, use_cache: bool):
       """Example showing all enrich_span_context parameters."""
       
       # Create span with full HoneyHive enrichment
       with enrich_span_context(
           event_name=f"call_agent_{agent_name}",
           inputs={
               "query": query,
               "agent_name": agent_name,
               "use_cache": use_cache
           },
           metadata={
               "agent_type": "research" if "research" in agent_name else "analysis",
               "cache_enabled": use_cache,
               "invocation_mode": "remote" if should_use_remote() else "local"
           },
           metrics={
               "query_length": len(query),
               "estimated_tokens": estimate_tokens(query)
           },
           config={
               "model": "gpt-4",
               "temperature": 0.7,
               "max_tokens": 500
           }
       ):
           # Check cache
           if use_cache:
               cached_result = check_cache(agent_name, query)
               if cached_result:
                   tracer.enrich_span(
                       outputs={"response": cached_result, "cache_hit": True},
                       metrics={"response_time_ms": 5}
                   )
                   return cached_result
           
           # Call agent
           result = invoke_agent(agent_name, query)
           
           # Enrich with results
           tracer.enrich_span(
               outputs={
                   "response": result,
                   "cache_hit": False,
                   "response_length": len(result)
               },
               metrics={
                   "response_time_ms": 250,
                   "tokens_used": count_tokens(result)
               }
           )
           
           return result

Comparison: enrich_span_context() vs tracer.start_span()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ Without enrich_span_context (manual attribute setting)
   with tracer.start_span("process_data") as span:
       # Have to manually set attributes with correct namespacing
       span.set_attribute("honeyhive_inputs.data", str(data))
       span.set_attribute("honeyhive_metadata.type", "batch")
       
       result = process_data(data)
       
       # Have to manually set output attributes
       span.set_attribute("honeyhive_outputs.result", str(result))
   
   # ✅ With enrich_span_context (automatic HoneyHive namespacing)
   with enrich_span_context(
       event_name="process_data",
       inputs={"data": data},
       metadata={"type": "batch"}
   ):
       result = process_data(data)
       tracer.enrich_span(outputs={"result": result})

**Benefits:**

- ✅ **Automatic namespacing**: No need to manually add ``honeyhive_inputs.*`` prefixes
- ✅ **Type-safe**: Structured parameters (dict) instead of string keys
- ✅ **Consistent**: Same enrichment API as ``@trace`` decorator
- ✅ **Correct context**: Uses ``trace.use_span()`` to ensure enrichment applies to the right span
- ✅ **Flexible**: Can enrich at span creation and during execution

When to Use enrich_span_context()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use ``enrich_span_context()`` when:**

- ✅ Creating conditional spans (based on runtime conditions)
- ✅ Creating spans in loops or iterations
- ✅ Creating spans in non-function code blocks
- ✅ You need HoneyHive's structured enrichment (inputs/outputs/metadata)
- ✅ You want automatic namespacing for HoneyHive attributes

**Use ``tracer.start_span()`` when:**

- You only need basic OpenTelemetry attributes (not HoneyHive-specific)
- You're setting custom attribute names that don't fit HoneyHive's structure
- You need fine-grained control over span lifecycle

**Use ``@trace`` decorator when:**

- Tracing entire functions (the most common case)
- You want automatic exception handling
- You want cleaner, more maintainable code

Real-World Example: Distributed Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``enrich_span_context()`` is particularly useful for distributed tracing scenarios where you need to create explicit spans with proper enrichment:

.. code-block:: python

   from honeyhive.tracer.processing.context import enrich_span_context
   import requests
   
   async def call_remote_agent(agent_name: str, query: str):
       """Call remote agent with explicit span creation."""
       
       # Create explicit span for the remote call
       with enrich_span_context(
           event_name=f"call_{agent_name}_remote",
           inputs={"query": query, "agent": agent_name},
           metadata={"invocation_type": "remote", "protocol": "http"}
       ):
           # Inject distributed trace context
           headers = {}
           inject_context_into_carrier(headers, tracer)
           
           # Make remote call
           response = requests.post(
               f"{agent_server_url}/agent/invoke",
               json={"query": query, "agent_name": agent_name},
               headers=headers,
               timeout=60
           )
           
           result = response.json().get("response", "")
           
           # Enrich with response
           tracer.enrich_span(
               outputs={"response": result, "status_code": response.status_code},
               metrics={"response_time_ms": response.elapsed.total_seconds() * 1000}
           )
           
           return result

.. seealso::
   For more on distributed tracing, see :doc:`/tutorials/06-distributed-tracing`.

Performance Monitoring
----------------------

Complex RAG Pipeline Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime
   
   # Complete multi-phase RAG pipeline with nested spans
   @trace(event_type=EventType.session)
   def advanced_rag_pipeline(user_query: str) -> str:
       """Multi-phase RAG with detailed tracing at each level."""
       with tracer.start_span("rag_session") as session_span:
           session_span.set_attribute("session.query", user_query)
           session_span.set_attribute("session.timestamp", datetime.now().isoformat())
           
           # Phase 1: Query Analysis
           with tracer.start_span("analysis_phase") as analysis_phase:
               analysis_phase.set_attribute("phase.name", "analysis")
               analysis_phase.set_attribute("phase.order", 1)
               
               # Substep 1a: Intent classification
               with tracer.start_span("intent_classification") as intent_span:
                   intent_span.set_attribute("classification.model", "bert-base-uncased")
                   intent_span.set_attribute("classification.confidence_threshold", 0.8)
                   
                   intent_result = classify_intent(user_query)
                   
                   intent_span.set_attribute("classification.predicted_intent", intent_result.intent)
                   intent_span.set_attribute("classification.confidence", intent_result.confidence)
                   intent_span.set_attribute("classification.alternatives", len(intent_result.alternatives))
               
               # Substep 1b: Entity extraction
               with tracer.start_span("entity_extraction") as entity_span:
                   entity_span.set_attribute("extraction.model", "spacy-en-core-web-sm")
                   
                   entities = extract_entities(user_query)
                   
                   entity_span.set_attribute("extraction.entities_found", len(entities))
                   entity_span.set_attribute("extraction.entity_types", list(set(e.type for e in entities)))
               
               analysis_phase.set_attribute("phase.intent", intent_result.intent)
               analysis_phase.set_attribute("phase.entities_count", len(entities))
               analysis_phase.set_attribute("phase.success", True)
           
           # Phase 2: Information Retrieval
           with tracer.start_span("retrieval_phase") as retrieval_phase:
               retrieval_phase.set_attribute("phase.name", "retrieval")
               retrieval_phase.set_attribute("phase.order", 2)
               
               # Substep 2a: Vector search
               with tracer.start_span("vector_search") as vector_span:
                   vector_span.set_attribute("search.embedding_model", "text-embedding-ada-002")
                   vector_span.set_attribute("search.index_size", 1000000)
                   vector_span.set_attribute("search.top_k", 10)
                   
                   search_results = vector_search(user_query, top_k=10)
                   
                   vector_span.set_attribute("search.results_count", len(search_results))
                   vector_span.set_attribute("search.avg_similarity", 
                                           sum(r.similarity for r in search_results) / len(search_results))
               
               # Substep 2b: Reranking
               with tracer.start_span("result_reranking") as rerank_span:
                   rerank_span.set_attribute("reranking.model", "cross-encoder")
                   rerank_span.set_attribute("reranking.input_count", len(search_results))
                   
                   reranked_results = rerank_results(search_results, user_query)
                   
                   rerank_span.set_attribute("reranking.output_count", len(reranked_results))
                   rerank_span.set_attribute("reranking.score_improvement", 
                                           calculate_score_improvement(search_results, reranked_results))
               
               retrieval_phase.set_attribute("phase.final_context_size", 
                                            sum(len(r.content) for r in reranked_results))
               retrieval_phase.set_attribute("phase.success", True)
           
           # Phase 3: LLM Generation
           with tracer.start_span("generation_phase") as generation_phase:
               generation_phase.set_attribute("phase.name", "generation")
               generation_phase.set_attribute("phase.order", 3)
               
               # Build context and prompt
               context = build_context(reranked_results)
               prompt = build_prompt(user_query, context, intent_result.intent)
               
               generation_phase.set_attribute("prompt.template_version", "v2.3")
               generation_phase.set_attribute("prompt.context_length", len(context))
               generation_phase.set_attribute("prompt.total_length", len(prompt))
               
               # LLM call (automatically traced by instrumentor)
               response = llm_generate(prompt)
               
               generation_phase.set_attribute("generation.response_length", len(response))
               generation_phase.set_attribute("generation.success", True)
           
           # Session summary
           session_span.set_attribute("session.phases_completed", 3)
           session_span.set_attribute("session.final_response_length", len(response))
           session_span.set_attribute("session.success", True)
           
           return response

Performance-Focused Spans
-------------------------

**Problem**: Monitor performance bottlenecks and resource usage.

**Solution**:

.. code-block:: python

   import time
   import psutil
   import threading
   from contextlib import contextmanager

   @contextmanager
   def performance_span(tracer, operation_name: str, **attributes):
       """Context manager for performance-focused spans."""
       
       with tracer.start_span(operation_name) as span:
           # Set initial attributes
           for key, value in attributes.items():
               span.set_attribute(key, value)
           
           # Performance monitoring setup
           process = psutil.Process()
           thread_count_before = threading.active_count()
           
           # CPU and memory before
           cpu_percent_before = process.cpu_percent()
           memory_before = process.memory_info()
           
           span.set_attribute("perf.cpu_percent_before", cpu_percent_before)
           span.set_attribute("perf.memory_rss_before_mb", memory_before.rss / 1024 / 1024)
           span.set_attribute("perf.memory_vms_before_mb", memory_before.vms / 1024 / 1024)
           span.set_attribute("perf.threads_before", thread_count_before)
           
           start_time = time.perf_counter()
           start_cpu_time = time.process_time()
           
           try:
               yield span
               
           finally:
               # Calculate performance metrics
               end_time = time.perf_counter()
               end_cpu_time = time.process_time()
               
               wall_time = (end_time - start_time) * 1000  # ms
               cpu_time = (end_cpu_time - start_cpu_time) * 1000  # ms
               
               # CPU and memory after
               cpu_percent_after = process.cpu_percent()
               memory_after = process.memory_info()
               thread_count_after = threading.active_count()
               
               # Record performance metrics
               span.set_attribute("perf.wall_time_ms", wall_time)
               span.set_attribute("perf.cpu_time_ms", cpu_time)
               span.set_attribute("perf.cpu_efficiency", (cpu_time / wall_time) * 100 if wall_time > 0 else 0)
               
               span.set_attribute("perf.cpu_percent_after", cpu_percent_after)
               span.set_attribute("perf.cpu_percent_delta", cpu_percent_after - cpu_percent_before)
               
               span.set_attribute("perf.memory_rss_after_mb", memory_after.rss / 1024 / 1024)
               span.set_attribute("perf.memory_rss_delta_mb", 
                                (memory_after.rss - memory_before.rss) / 1024 / 1024)
               
               span.set_attribute("perf.threads_after", thread_count_after)
               span.set_attribute("perf.threads_delta", thread_count_after - thread_count_before)

   # Usage example
   def performance_critical_operation(data_size: int):
       """Example of performance monitoring with custom spans."""
       
       with performance_span(tracer, "data_processing", 
                           operation_type="batch_processing",
                           data_size=data_size) as span:
           
           # Simulate CPU-intensive work
           with performance_span(tracer, "computation_phase",
                               computation_type="matrix_operations") as comp_span:
               result = expensive_computation(data_size)
               comp_span.set_attribute("computation.result_size", len(result))
           
           # Simulate I/O work
           with performance_span(tracer, "io_phase",
                               io_type="file_operations") as io_span:
               saved_files = save_results(result)
               io_span.set_attribute("io.files_written", len(saved_files))
               io_span.set_attribute("io.total_bytes", sum(f.size for f in saved_files))
           
           span.set_attribute("operation.phases_completed", 2)
           span.set_attribute("operation.success", True)
           
           return result

Error-Focused Spans
-------------------

**Problem**: Comprehensive error tracking and debugging context.

**Solution**:

.. code-block:: python

   import traceback
   import sys
   from typing import Optional, Type, Any

   @contextmanager
   def error_tracking_span(tracer, operation_name: str, **context):
       """Enhanced span with comprehensive error tracking."""
       
       with tracer.start_span(operation_name) as span:
           # Add context attributes
           for key, value in context.items():
               span.set_attribute(f"context.{key}", str(value))
           
           # Environment context
           span.set_attribute("env.python_version", sys.version)
           span.set_attribute("env.platform", sys.platform)
           
           exception_occurred = False
           exception_info = None
           
           try:
               yield span
               span.set_attribute("operation.success", True)
               
           except Exception as e:
               exception_occurred = True
               exception_info = sys.exc_info()
               
               # Comprehensive error information
               span.set_attribute("operation.success", False)
               span.set_attribute("error.type", type(e).__name__)
               span.set_attribute("error.message", str(e))
               span.set_attribute("error.module", e.__class__.__module__)
               
               # Stack trace information
               tb = traceback.extract_tb(exception_info[2])
               span.set_attribute("error.traceback_length", len(tb))
               span.set_attribute("error.file", tb[-1].filename if tb else "unknown")
               span.set_attribute("error.line_number", tb[-1].lineno if tb else 0)
               span.set_attribute("error.function", tb[-1].name if tb else "unknown")
               
               # Full traceback as string (truncated if too long)
               full_traceback = ''.join(traceback.format_exception(*exception_info))
               if len(full_traceback) > 1000:
                   full_traceback = full_traceback[:1000] + "... (truncated)"
               span.set_attribute("error.traceback", full_traceback)
               
               # Set span status
               span.set_status("ERROR", f"{type(e).__name__}: {e}")
               
               # Re-raise the exception
               raise
           
           finally:
               span.set_attribute("operation.exception_occurred", exception_occurred)

   # Usage example
   def risky_operation_with_error_tracking(operation_id: str, data: dict):
       """Example operation with comprehensive error tracking."""
       
       with error_tracking_span(tracer, "risky_operation",
                               operation_id=operation_id,
                               data_size=len(str(data)),
                               operation_type="data_transformation") as span:
           
           span.set_attribute("operation.id", operation_id)
           span.set_attribute("operation.stage", "initialization")
           
           try:
               # Stage 1: Data validation
               span.set_attribute("operation.stage", "validation")
               with error_tracking_span(tracer, "data_validation",
                                       validator_version="v2.1") as validation_span:
                   validated_data = validate_complex_data(data)
                   validation_span.set_attribute("validation.fields_validated", len(validated_data))
               
               # Stage 2: Data transformation
               span.set_attribute("operation.stage", "transformation")
               with error_tracking_span(tracer, "data_transformation",
                                       transformation_type="normalize_and_enrich") as transform_span:
                   transformed_data = transform_data(validated_data)
                   transform_span.set_attribute("transformation.output_size", len(transformed_data))
               
               # Stage 3: Data persistence
               span.set_attribute("operation.stage", "persistence")
               with error_tracking_span(tracer, "data_persistence",
                                       storage_type="database") as persist_span:
                   result_id = save_to_database(transformed_data)
                   persist_span.set_attribute("persistence.result_id", result_id)
               
               span.set_attribute("operation.stage", "completed")
               span.set_attribute("operation.result_id", result_id)
               
               return result_id
               
           except ValidationError as e:
               span.set_attribute("operation.failure_stage", "validation")
               span.set_attribute("operation.failure_reason", "invalid_data")
               raise
               
           except TransformationError as e:
               span.set_attribute("operation.failure_stage", "transformation")
               span.set_attribute("operation.failure_reason", "transformation_failed")
               raise
               
           except DatabaseError as e:
               span.set_attribute("operation.failure_stage", "persistence")
               span.set_attribute("operation.failure_reason", "database_error")
               raise

Conditional and Dynamic Spans
-----------------------------

**Problem**: Create spans only when certain conditions are met or based on runtime decisions.

**Solution**:

.. code-block:: python

   from typing import Optional
   import random

   class ConditionalSpanManager:
       """Manager for creating spans based on conditions."""
       
       def __init__(self, tracer):
           self.tracer = tracer
       
       @contextmanager
       def conditional_span(self, 
                          span_name: str, 
                          condition: bool = True,
                          sampling_rate: float = 1.0,
                          **attributes):
           """Create span only if condition is met and sampling allows."""
           
           should_create_span = (
               condition and 
               random.random() < sampling_rate
           )
           
           if should_create_span:
               with self.tracer.start_span(span_name) as span:
                   # Mark this as a sampled span
                   span.set_attribute("span.sampled", True)
                   span.set_attribute("span.sampling_rate", sampling_rate)
                   
                   for key, value in attributes.items():
                       span.set_attribute(key, value)
                   
                   yield span
           else:
               # No-op context manager
               yield None
       
       @contextmanager
       def debug_span(self, span_name: str, debug_mode: bool = False, **attributes):
           """Create span only in debug mode."""
           
           if debug_mode:
               with self.tracer.start_span(f"DEBUG_{span_name}") as span:
                   span.set_attribute("span.debug_mode", True)
                   
                   for key, value in attributes.items():
                       span.set_attribute(f"debug.{key}", value)
                   
                   yield span
           else:
               yield None
       
       @contextmanager
       def performance_span(self, 
                          span_name: str,
                          min_duration_ms: float = 0,
                          **attributes):
           """Create span only if operation takes longer than threshold."""
           
           start_time = time.perf_counter()
           
           # Always yield a context, but decide later whether to create span
           temp_attributes = attributes.copy()
           
           yield self  # Yield self so caller can add more attributes
           
           duration_ms = (time.perf_counter() - start_time) * 1000
           
           if duration_ms >= min_duration_ms:
               # Create span retroactively for slow operations
               with self.tracer.start_span(span_name) as span:
                   span.set_attribute("span.created_retroactively", True)
                   span.set_attribute("span.min_duration_threshold_ms", min_duration_ms)
                   span.set_attribute("perf.actual_duration_ms", duration_ms)
                   
                   for key, value in temp_attributes.items():
                       span.set_attribute(key, value)

   # Usage examples
   def conditional_tracing_examples():
       """Examples of conditional span creation."""
       
       span_manager = ConditionalSpanManager(tracer)
       
       # Example 1: Sample only 10% of high-frequency operations
       with span_manager.conditional_span("frequent_operation", 
                                        sampling_rate=0.1,
                                        operation_type="cache_lookup") as span:
           if span:  # Only execute if span was created
               span.set_attribute("cache.hit", check_cache())
           
           result = frequent_cache_operation()
       
       # Example 2: Debug spans only in development
       debug_mode = os.getenv("DEBUG", "false").lower() == "true"
       
       with span_manager.debug_span("complex_algorithm",
                                  debug_mode=debug_mode,
                                  algorithm_version="v3.2") as debug_span:
           if debug_span:
               debug_span.set_attribute("debug.input_size", len(input_data))
           
           result = complex_algorithm(input_data)
           
           if debug_span:
               debug_span.set_attribute("debug.output_size", len(result))
       
       # Example 3: Performance spans for slow operations only
       with span_manager.performance_span("potentially_slow_operation",
                                        min_duration_ms=100,
                                        operation_complexity="high") as perf_context:
           
           # This operation might be fast or slow
           result = potentially_slow_operation()
           
           # Span will only be created if it took >100ms

Best Practices Summary
----------------------

**1. Span Naming**

.. code-block:: python

   # Good: Descriptive, hierarchical names
   "user_authentication"
   "database_query_users"
   "llm_generation_gpt4"
   "payment_processing_stripe"
   
   # Bad: Generic or unclear names
   "process"
   "api_call"
   "function"

**2. Attribute Organization**

.. code-block:: python

   # Good: Hierarchical, typed attributes
   span.set_attribute("user.id", "user123")
   span.set_attribute("user.tier", "premium")
   span.set_attribute("operation.type", "data_export")
   span.set_attribute("operation.complexity", "high")
   span.set_attribute("performance.duration_ms", 1500)
   
   # Bad: Flat, untyped attributes
   span.set_attribute("userid", "user123")
   span.set_attribute("type", "export")
   span.set_attribute("time", "1500")

**3. Error Handling**

.. code-block:: python

   # Good: Comprehensive error context
   try:
       result = risky_operation()
   except SpecificError as e:
       span.set_attribute("error.type", "SpecificError")
       span.set_attribute("error.code", e.error_code)
       span.set_attribute("error.recoverable", True)
       span.set_status("ERROR", str(e))
       raise

**4. Performance Awareness**

.. code-block:: python

   # Good: Efficient span creation
   if should_trace_detailed():
       with tracer.start_span("detailed_operation") as span:
           # Detailed tracing for specific scenarios
           pass
   
   # Avoid: Creating too many spans in hot paths
   # for item in million_items:  # Don't do this
   #     with tracer.start_span("process_item"):
   #         process(item)

See Also
--------

- :doc:`index` - Advanced tracing overview
- :doc:`../index` - LLM provider integrations
- :doc:`../monitoring/export-traces` - Export traces for analysis
- :doc:`../../reference/api/tracer` - HoneyHiveTracer API reference
