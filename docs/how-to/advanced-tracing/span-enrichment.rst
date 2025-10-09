Span Enrichment Patterns
=========================

**Problem:** You need to add rich context, business metadata, and performance metrics to your traces to make them useful for debugging, analysis, and business intelligence.

**Solution:** Use these 5 proven span enrichment patterns to transform basic traces into powerful observability data.

This guide covers advanced enrichment techniques beyond the basics. For an introduction, see :doc:`/tutorials/03-enable-span-enrichment`.

Pattern 1: Basic Enrichment with ``enrich_span()``
---------------------------------------------------

**When to use:** Add simple key-value metadata to any span.

**Example:** Add user and request context to every LLM call.

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(project="my-app")
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   def process_user_request(user_id: str, request_id: str, query: str):
       """Process user request with basic enrichment."""
       
       # Enrich the current span with context
       enrich_span({
           "user_id": user_id,
           "request_id": request_id,
           "query_length": len(query),
           "timestamp": time.time()
       })
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": query}]
       )
       
       return response.choices[0].message.content

**Key Points:**

- ``enrich_span()`` adds metadata to the **current active span**
- Call it anywhere in your function before or after LLM calls
- Metadata is automatically attached to the instrumentor-created span
- Use consistent key names across your application for filtering

Pattern 2: Automatic Enrichment in Decorators
----------------------------------------------

**When to use:** Automatically enrich all calls to a decorated function with consistent metadata.

**Example:** Add function-level context automatically.

.. code-block:: python

   from functools import wraps
   from honeyhive import enrich_span, trace
   from honeyhive.models import EventType
   import time
   
   def auto_enrich(feature: str, event_type: EventType = EventType.chain):
       """Decorator that automatically enriches spans."""
       def decorator(func):
           @wraps(func)
           @trace(event_type=event_type)
           def wrapper(*args, **kwargs):
               # Automatic enrichment
               enrich_span({
                   "feature": feature,
                   "function_name": func.__name__,
                   "module": func.__module__,
                   "timestamp": time.time()
               })
               
               # Execute function
               start_time = time.time()
               try:
                   result = func(*args, **kwargs)
                   
                   # Success enrichment
                   enrich_span({
                       "status": "success",
                       "execution_time_ms": round((time.time() - start_time) * 1000, 2)
                   })
                   
                   return result
                   
               except Exception as e:
                   # Error enrichment
                   enrich_span({
                       "status": "error",
                       "error_type": type(e).__name__,
                       "error_message": str(e),
                       "execution_time_ms": round((time.time() - start_time) * 1000, 2)
                   })
                   raise
           
           return wrapper
       return decorator
   
   # Usage
   @auto_enrich(feature="customer_support")
   def handle_support_query(query: str) -> str:
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": query}]
       )
       return response.choices[0].message.content

**Key Points:**

- Decorator ensures consistent enrichment across functions
- Automatically captures timing and error context
- Reduces code duplication
- Can be composed with other decorators

Pattern 3: Context-Aware Enrichment
------------------------------------

**When to use:** Enrich spans with data from application context (web requests, user sessions, etc.).

**Example:** Add Flask/Django request context to traces.

.. code-block:: python

   from flask import Flask, request, g
   from honeyhive import enrich_span, trace
   from honeyhive.models import EventType
   import openai
   
   app = Flask(__name__)
   
   @app.before_request
   def before_request():
       """Store request context for enrichment."""
       g.request_start = time.time()
       g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
   
   def enrich_with_request_context():
       """Helper to enrich with current request context."""
       if not request:
           return
       
       enrich_span({
           "request_id": g.request_id,
           "endpoint": request.endpoint,
           "method": request.method,
           "path": request.path,
           "user_agent": request.user_agent.string,
           "ip_address": request.remote_addr,
           "referrer": request.referrer
       })
   
   @app.route("/api/chat", methods=["POST"])
   def chat_endpoint():
       """Chat endpoint with context-aware enrichment."""
       @trace(event_type=EventType.chain)
       def _handle_chat():
           # Enrich with request context
           enrich_with_request_context()
           
           # Add business context
           data = request.json
           enrich_span({
               "user_id": data.get("user_id"),
               "message_length": len(data.get("message", "")),
               "feature": "chat_api"
           })
           
           # LLM call
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": data["message"]}]
           )
           
           return response.choices[0].message.content
       
       result = _handle_chat()
       return {"response": result}

**Key Points:**

- Extract context from framework globals (Flask's ``g``, Django's middleware)
- Create reusable enrichment helpers
- Combine request context with business context
- Useful for debugging production issues

Pattern 4: Performance Metadata Enrichment
-------------------------------------------

**When to use:** Track detailed timing breakdowns and performance metrics.

**Example:** Measure and enrich with pipeline stage timings.

.. code-block:: python

   import time
   from dataclasses import dataclass
   from typing import Dict
   from honeyhive import enrich_span, trace
   from honeyhive.models import EventType
   import openai
   
   @dataclass
   class TimingContext:
       """Context manager for timing measurements."""
       stage: str
       timings: Dict[str, float]
       
       def __enter__(self):
           self.start = time.time()
           return self
       
       def __exit__(self, *args):
           elapsed = (time.time() - self.start) * 1000  # Convert to ms
           self.timings[f"{self.stage}_ms"] = round(elapsed, 2)
   
   @trace(event_type=EventType.chain)
   def rag_pipeline_with_timing(query: str, context_docs: list) -> str:
       """RAG pipeline with detailed performance tracking."""
       timings = {}
       pipeline_start = time.time()
       
       # Stage 1: Document retrieval
       with TimingContext("retrieval", timings):
           relevant_docs = retrieve_documents(query, context_docs)
           enrich_span({
               "retrieval_doc_count": len(relevant_docs),
               "total_docs_searched": len(context_docs)
           })
       
       # Stage 2: Context building
       with TimingContext("context_building", timings):
           context = "\n\n".join(relevant_docs)
           prompt = build_prompt(query, context)
           enrich_span({
               "context_length": len(context),
               "prompt_length": len(prompt)
           })
       
       # Stage 3: LLM generation
       with TimingContext("llm_generation", timings):
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               max_tokens=500,
               messages=[{"role": "user", "content": prompt}]
           )
           result = response.choices[0].message.content
       
       # Stage 4: Post-processing
       with TimingContext("post_processing", timings):
           processed_result = post_process(result)
       
       # Enrich with all timings
       total_time = (time.time() - pipeline_start) * 1000
       timings["total_pipeline_ms"] = round(total_time, 2)
       
       # Calculate percentages
       for stage, duration in timings.items():
           if stage != "total_pipeline_ms":
               percentage = (duration / total_time) * 100
               timings[f"{stage}_percentage"] = round(percentage, 1)
       
       enrich_span(timings)
       enrich_span({
           "performance_tier": "fast" if total_time < 1000 else "slow",
           "pipeline_stages_completed": 4
       })
       
       return processed_result

**Key Points:**

- Use context managers for clean timing code
- Track stage-by-stage performance
- Calculate and enrich with percentages
- Identify performance bottlenecks easily

Pattern 5: Error Context Enrichment
------------------------------------

**When to use:** Add comprehensive error context for debugging failures.

**Example:** Capture detailed error information with retry logic.

.. code-block:: python

   import time
   from typing import Optional
   from honeyhive import enrich_span, trace
   from honeyhive.models import EventType
   import openai
   
   @trace(event_type=EventType.chain)
   def resilient_llm_call_with_enrichment(
       prompt: str,
       max_retries: int = 3,
       backoff_base: float = 2.0
   ) -> Optional[str]:
       """LLM call with retry logic and rich error enrichment."""
       
       enrich_span({
           "max_retries": max_retries,
           "backoff_strategy": "exponential",
           "prompt_length": len(prompt)
       })
       
       client = openai.OpenAI()
       attempt = 0
       errors_encountered = []
       
       while attempt < max_retries:
           attempt += 1
           attempt_start = time.time()
           
           try:
               response = client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": prompt}],
                   timeout=30.0
               )
               
               # Success enrichment
               enrich_span({
                   "status": "success",
                   "attempts_needed": attempt,
                   "final_attempt_duration_ms": round((time.time() - attempt_start) * 1000, 2),
                   "errors_before_success": len(errors_encountered)
               })
               
               return response.choices[0].message.content
               
           except openai.RateLimitError as e:
               error_info = {
                   "attempt": attempt,
                   "error_type": "rate_limit",
                   "error_message": str(e),
                   "retry_after": e.response.headers.get("Retry-After"),
                   "duration_ms": round((time.time() - attempt_start) * 1000, 2)
               }
               errors_encountered.append(error_info)
               
               if attempt < max_retries:
                   wait_time = backoff_base ** attempt
                   enrich_span({
                       f"attempt_{attempt}_error": "rate_limit",
                       f"attempt_{attempt}_wait_time": wait_time
                   })
                   time.sleep(wait_time)
               else:
                   # Final failure enrichment
                   enrich_span({
                       "status": "error",
                       "final_error_type": "rate_limit",
                       "total_attempts": attempt,
                       "all_errors": errors_encountered,
                       "retry_exhausted": True
                   })
                   raise
                   
           except openai.APIError as e:
               error_info = {
                   "attempt": attempt,
                   "error_type": "api_error",
                   "error_message": str(e),
                   "status_code": e.status_code if hasattr(e, 'status_code') else None,
                   "duration_ms": round((time.time() - attempt_start) * 1000, 2)
               }
               errors_encountered.append(error_info)
               
               if attempt < max_retries:
                   wait_time = backoff_base ** attempt
                   enrich_span({
                       f"attempt_{attempt}_error": "api_error",
                       f"attempt_{attempt}_status_code": error_info["status_code"],
                       f"attempt_{attempt}_wait_time": wait_time
                   })
                   time.sleep(wait_time)
               else:
                   enrich_span({
                       "status": "error",
                       "final_error_type": "api_error",
                       "total_attempts": attempt,
                       "all_errors": errors_encountered,
                       "retry_exhausted": True
                   })
                   raise
       
       return None

**Key Points:**

- Capture error details at each retry attempt
- Track error history across retries
- Include timing for failed attempts
- Differentiate between transient and permanent failures

Advanced Techniques
-------------------

Conditional Enrichment
^^^^^^^^^^^^^^^^^^^^^^

Only enrich based on conditions:

.. code-block:: python

   def conditional_enrichment(user_tier: str, result: str):
       # Always enrich with tier
       enrich_span({"user_tier": user_tier})
       
       # Only enrich premium users with detailed info
       if user_tier == "premium":
           enrich_span({
               "result_length": len(result),
               "result_word_count": len(result.split()),
               "premium_features_used": True
           })

Structured Enrichment
^^^^^^^^^^^^^^^^^^^^^

Organize related metadata:

.. code-block:: python

   def structured_enrichment(user_data: dict, request_data: dict):
       # User namespace
       enrich_span({
           "user.id": user_data["id"],
           "user.tier": user_data["tier"],
           "user.region": user_data["region"]
       })
       
       # Request namespace
       enrich_span({
           "request.id": request_data["id"],
           "request.priority": request_data["priority"],
           "request.source": request_data["source"]
       })

Best Practices
--------------

**DO:**

- Use dot notation for hierarchical keys (``user.id``, ``request.priority``)
- Enrich early and often throughout function execution
- Include timing information for performance analysis
- Add error context in exception handlers
- Use consistent key naming conventions

**DON'T:**

- Include sensitive data (PII, credentials, API keys)
- Add extremely large values (>10KB per field)
- Use random/dynamic key names
- Over-enrich (100+ fields per span becomes noise)
- Duplicate data already captured by instrumentors

Troubleshooting
---------------

**Enrichment not appearing:**

- Ensure you're calling ``enrich_span()`` within a traced context
- Check that instrumentor is properly initialized
- Verify tracer is sending data to HoneyHive

**Performance impact:**

- Enrichment adds <1ms overhead per call
- Serialize complex objects before enriching
- Use sampling for high-frequency enrichment

Next Steps
----------

- :doc:`custom-spans` - Create custom spans for complex workflows
- :doc:`class-decorators` - Class-level tracing patterns
- :doc:`advanced-patterns` - Session enrichment and distributed tracing
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns

**Key Takeaway:** Span enrichment transforms basic traces into rich observability data that powers debugging, analysis, and business intelligence. Use these 5 patterns as building blocks for your tracing strategy. ✨

