Span Enrichment Patterns
========================

**Problem:** You need to add rich context, business metadata, and performance metrics to your traces to make them useful for debugging, analysis, and business intelligence.

**Solution:** Use these 5 proven span enrichment patterns to transform basic traces into powerful observability data.

This guide covers advanced enrichment techniques beyond the basics. For an introduction, see :doc:`/tutorials/03-enable-span-enrichment`.

Session-Level vs Span-Level Enrichment
---------------------------------------

HoneyHive provides two enrichment scopes: **session-level** and **span-level**.

**``enrich_session()`` - Apply metadata to all spans in a session:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(project="my-app")
   
   # Apply to ALL spans in this session
   tracer.enrich_session({
       "user_id": "user_456",
       "user_tier": "enterprise",
       "environment": "production",
       "deployment_region": "us-east-1"
   })
   
   # All subsequent operations inherit this metadata
   response1 = call_llm(...)
   response2 = call_llm(...)
   response3 = call_llm(...)
   # All 3 traces will have user_id, user_tier, environment, deployment_region

**Use ``enrich_session()`` for:**

- ✅ User identification (user_id, email, tier)
- ✅ Session context (session_type, workflow_name)
- ✅ Environment info (environment, region, version)
- ✅ Business context (customer_id, account_type, plan)
- ✅ Any metadata that applies to the entire user session

**``enrich_span()`` - Apply metadata to a single span:**

.. code-block:: python

   from honeyhive import enrich_span
   
   def process_query(query: str, use_cache: bool):
       # Apply to THIS specific span only
       enrich_span({
           "query_length": len(query),
           "cache_enabled": use_cache,
           "model": "gpt-4",
           "temperature": 0.7
       })
       
       return call_llm(query)

**Use ``enrich_span()`` for:**

- ✅ Per-call parameters (model, temperature, max_tokens)
- ✅ Call-specific metrics (input_length, cache_hit, latency)
- ✅ Dynamic metadata (intent_classification, confidence_score)
- ✅ Error details (error_type, retry_count)
- ✅ Any metadata that varies per LLM call

**Example combining both:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Session-level: Set once for the entire user session
   tracer = HoneyHiveTracer.init(
       project="customer-support",
       session_name="support-session-789"
   )
   
   tracer.enrich_session({
       "user_id": "user_456",
       "support_tier": "premium",
       "issue_category": "billing"
   })
   
   # Span-level: Varies per call
   def handle_query(query: str):
       intent = classify_intent(query)
       
       tracer.enrich_span({
           "query_intent": intent,
           "query_length": len(query),
           "model": "gpt-4" if intent == "complex" else "gpt-3.5-turbo"
       })
       
       return generate_response(query)
   
   # Each call has both session + span metadata
   handle_query("How do I change my billing address?")
   handle_query("What's my current balance?")
   handle_query("Can I upgrade my plan?")

**Decision Matrix:**

+------------------------------+-------------------------+-------------------------+
| **Metadata Type**            | **Scope**               | **Method**              |
+==============================+=========================+=========================+
| User ID, email               | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Model name, temperature      | Span (varies)           | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Environment (prod/dev)       | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Cache hit/miss               | Span (per-call)         | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Customer tier                | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Prompt token count           | Span (per-call)         | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Deployment region            | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Error type/message           | Span (when it occurs)   | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+

.. tip::
   **Rule of Thumb:**
   
   If the metadata is the same for all LLM calls in a user session, use ``enrich_session()``.
   If it changes per call, use ``enrich_span()``.

Understanding Enrichment Interfaces
-----------------------------------

``enrich_span()`` supports multiple invocation patterns. Choose the one that fits your use case:

Quick Reference Table
^^^^^^^^^^^^^^^^^^^^^

+----------------------------+----------------------------------+----------------------------------------------+
| Pattern                    | When to Use                      | Backend Namespace                            |
+============================+==================================+==============================================+
| Simple Dict                | Quick metadata                   | ``honeyhive_metadata.*``                     |
+----------------------------+----------------------------------+----------------------------------------------+
| Keyword Arguments          | Concise inline enrichment        | ``honeyhive_metadata.*``                     |
+----------------------------+----------------------------------+----------------------------------------------+
| Reserved Namespaces        | Structured organization          | ``honeyhive_<namespace>.*``                  |
+----------------------------+----------------------------------+----------------------------------------------+
| Mixed Usage                | Combine multiple patterns        | Multiple namespaces                          |
+----------------------------+----------------------------------+----------------------------------------------+

Simple Dict Pattern (New)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from honeyhive import enrich_span
   
   # Pass a dictionary - routes to metadata
   enrich_span({
       "user_id": "user_123",
       "feature": "chat",
       "session": "abc"
   })
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.session = "abc"

Keyword Arguments Pattern (New)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from honeyhive import enrich_span
   
   # Pass keyword arguments - also routes to metadata
   enrich_span(
       user_id="user_123",
       feature="chat",
       session="abc"
   )
   
   # Same backend storage as simple dict

Reserved Namespaces Pattern (Backwards Compatible)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use explicit namespace parameters for organized data:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Explicit namespaces for structured organization
   enrich_span(
       metadata={"user_id": "user_123", "session": "abc"},
       metrics={"latency_ms": 150, "score": 0.95},
       user_properties={"user_id": "user_123", "plan": "premium"},
       feedback={"rating": 5, "helpful": True},
       inputs={"query": "What is AI?"},
       outputs={"answer": "AI is artificial intelligence..."},
       config={"model": "gpt-4", "temperature": 0.7},
       error="Optional error message",
       event_id="evt_unique_identifier"
   )
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.session = "abc"
   # honeyhive_metrics.latency_ms = 150
   # honeyhive_metrics.score = 0.95
   # honeyhive_user_properties.user_id = "user_123"
   # honeyhive_user_properties.plan = "premium"
   # honeyhive_feedback.rating = 5
   # honeyhive_feedback.helpful = True
   # honeyhive_inputs.query = "What is AI?"
   # honeyhive_outputs.answer = "AI is artificial intelligence..."
   # honeyhive_config.model = "gpt-4"
   # honeyhive_config.temperature = 0.7
   # honeyhive_error = "Optional error message"
   # honeyhive_event_id = "evt_unique_identifier"

**Available Namespaces:**

- ``metadata``: Business context (user IDs, features, session info)
- ``metrics``: Numeric measurements (latencies, scores, counts)
- ``user_properties``: User-specific properties (user_id, plan, tier, etc.) - stored in dedicated namespace
- ``feedback``: User or system feedback (ratings, thumbs up/down)
- ``inputs``: Input data to the operation
- ``outputs``: Output data from the operation
- ``config``: Configuration parameters (model settings, hyperparams)
- ``error``: Error messages or exceptions (stored as direct attribute)
- ``event_id``: Unique event identifier (stored as direct attribute)

**Why use namespaces?**

- Organize different data types separately
- Easier to query specific categories in the backend
- Maintain backwards compatibility with existing code
- Clear semantic meaning for different attribute types

Mixed Usage Pattern
^^^^^^^^^^^^^^^^^^^

Combine multiple patterns - later values override earlier ones:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Combine namespaces with kwargs
   enrich_span(
       metadata={"user_id": "user_123"},
       metrics={"score": 0.95, "latency_ms": 150},
       feature="chat",     # Adds to metadata
       priority="high",    # Also adds to metadata
       retries=3           # Also adds to metadata
   )
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.priority = "high"
   # honeyhive_metadata.retries = 3
   # honeyhive_metrics.score = 0.95
   # honeyhive_metrics.latency_ms = 150

Pattern 1: Basic Enrichment with ``enrich_span()``
--------------------------------------------------

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
---------------------------------------------

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
-----------------------------------

**When to use:** Enrich spans with data from application context (web requests, user sessions, etc.).

**Example:** Add Flask/Django request context to traces.

.. code-block:: python

   from flask import Flask, request, g
   from honeyhive import enrich_span, trace
   from honeyhive.models import EventType
   import openai
   import time
   import uuid
   
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
------------------------------------------

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
-----------------------------------

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

