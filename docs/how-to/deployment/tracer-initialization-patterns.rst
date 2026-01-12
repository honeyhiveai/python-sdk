Where Should I Initialize the Tracer?
======================================

.. note::
   **Common Question**: "Should I initialize the tracer globally or per-request?"
   
   **Answer**: It depends on your use case. This guide explains which pattern to use when.

The HoneyHive SDK uses a **multi-instance tracer architecture** that supports both global and per-request initialization. Each pattern has specific use cases where it excels.

Overview
--------

**Key Decision Factors:**

1. **Execution Model** - Are you running in a long-lived server or stateless serverless environment?
2. **Session Isolation** - Do you need to isolate traces per user/request?
3. **Evaluation Context** - Are you using ``evaluate()`` for experiments?
4. **Distributed Tracing** - Do you need to trace across multiple services?

Quick Decision Matrix
---------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Use Case
     - Initialization Pattern
     - Why?
   * - Local development/debugging
     - Global (module-level)
     - Simple, single trace needed
   * - ``evaluate()`` experiments
     - Automatic (SDK-managed)
     - Per-datapoint isolation required
   * - AWS Lambda/Cloud Functions
     - Per-request (cold start)
     - Stateless execution model
   * - Long-running server (FastAPI/Flask)
     - Global + per-session context
     - Reuse tracer, isolate sessions
   * - Distributed tracing (microservices)
     - Global + baggage propagation
     - Cross-service trace context

Pattern 1: Local Development / Single Trace
--------------------------------------------

**Use When:**

- Writing scripts or notebooks
- Debugging locally
- Testing a single execution flow
- No need for session isolation

**Pattern: Global Tracer Initialization**

.. code-block:: python

   # app.py
   from honeyhive import HoneyHiveTracer, trace
   import os

   # Initialize tracer once at module level
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="my-project",
       session_name="local-dev-session"
   )

   @trace(event_type="tool", tracer=tracer)
   def process_data(input_text):
       # All calls to this function use the same tracer instance
       result = transform(input_text)
       tracer.enrich_span(metadata={"input_length": len(input_text)})
       return result

   if __name__ == "__main__":
       # Run multiple operations - all go to same session
       result1 = process_data("Hello")
       result2 = process_data("World")

**Characteristics:**

✅ **Simple** - Initialize once, use everywhere
✅ **Efficient** - No overhead creating tracer instances
✅ **Single session** - All traces grouped together
❌ **No isolation** - Can't separate traces by user/request

Pattern 2: Evaluation / Experiments (``evaluate()``)
-----------------------------------------------------

**Use When:**

- Running experiments with ``evaluate()``
- Testing multiple datapoints in parallel
- Need isolated traces per datapoint

**Pattern: Automatic Per-Datapoint Isolation**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.experiments import evaluate
   import os

   # DON'T initialize tracer here - evaluate() does it for you
   
   @trace(event_type="tool")  # No tracer parameter needed
   def my_rag_pipeline(query: str, context: str):
       """This function gets called once per datapoint."""
       # evaluate() automatically creates a tracer instance per datapoint
       # Each datapoint gets its own isolated session
       response = generate_response(query, context)
       return {"answer": response}

   # Run evaluation - SDK handles tracer creation automatically
   result = evaluate(
       function=my_rag_pipeline,
       dataset=my_dataset,
       api_key=os.getenv("HH_API_KEY"),
       project="my-project",
       name="rag-experiment-1"
   )

**How It Works:**

1. ``evaluate()`` creates a **new tracer instance** per datapoint
2. Each tracer gets its own **isolated session**
3. Sessions are linked to the experiment via ``run_id``
4. No cross-contamination between datapoint traces

**DON'T Do This:**

.. code-block:: python

   # ❌ WRONG - Don't create global tracer with evaluate()
   tracer = HoneyHiveTracer.init(...)  # Will cause session conflicts
   
   @trace(event_type="tool", tracer=tracer)  # All datapoints share session
   def my_function(input):
       pass

**Characteristics:**

✅ **Automatic** - SDK manages tracer lifecycle
✅ **Isolated** - Each datapoint gets own session
✅ **Linked** - All sessions tied to experiment run
⚠️ **No global tracer** - Don't initialize tracer yourself

Pattern 3: Serverless (AWS Lambda / Cloud Functions)
-----------------------------------------------------

**Use When:**

- Running in AWS Lambda, Google Cloud Functions, Azure Functions
- Stateless, per-invocation execution model
- Cold starts reset all state

**Pattern: Per-Request Tracer with Lazy Initialization**

.. code-block:: python

   # lambda_function.py
   from honeyhive import HoneyHiveTracer, trace
   import os
   from typing import Optional

   # Module-level variable (survives warm starts)
   _tracer: Optional[HoneyHiveTracer] = None

   def get_tracer() -> HoneyHiveTracer:
       """Lazy initialization - reuses tracer on warm starts."""
       global _tracer
       if _tracer is None:
           _tracer = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="lambda"
           )
       return _tracer

   def lambda_handler(event, context):
       """Lambda entry point - creates new session per invocation."""
       tracer = get_tracer()
       
       # Create new session for this invocation
       request_id = context.request_id
       session_id = tracer.create_session(
           session_name=f"lambda-{request_id}",
           inputs={"event": event}
       )
       
       # Process request with session context
       with tracer.start_span("process_request"):
           result = process_event(event, tracer)
           
       # Update session with outputs
       tracer.enrich_session(
           outputs={"result": result},
           metadata={"request_id": request_id}
       )
       
       return result

   @trace(event_type="tool")
   def process_event(event, tracer):
       tracer.enrich_span(metadata={"event_type": event.get("type")})
       return {"status": "success"}

**Persisting Session IDs Across Invocations:**

If you need to link multiple Lambda invocations together (e.g., request/response cycles), explicitly set the session_id:

.. code-block:: python

   import os
   import uuid
   from honeyhive import HoneyHiveTracer, trace
   
   def lambda_handler(event, context):
       # Extract or generate session ID
       session_id = event.get("session_id") or str(uuid.uuid4())
       
       # Initialize tracer with explicit session_id
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),
           project=os.getenv("HH_PROJECT"),
           session_id=session_id,  # Override to link invocations
           session_name=f"lambda-{context.function_name}-{session_id[:8]}"
       )
       
       # Process event...
       result = process_event(event)
       
       # Return session_id so caller can link subsequent calls
       return {
           "session_id": session_id,
           "result": result
       }

.. important::
   **Session ID Best Practices:**
   
   - Use UUID v4 format for session IDs: ``str(uuid.uuid4())``
   - If receiving session_id from external source, validate it's UUID v4
   - For non-UUID identifiers, convert deterministically:
   
   .. code-block:: python
   
      import uuid
      
      def to_session_id(identifier: str) -> str:
          """Convert any identifier to deterministic UUID v4."""
          # Create deterministic UUID from namespace + identifier
          namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
          return str(uuid.uuid5(namespace, identifier))
      
      # Usage
      session_id = to_session_id(request_id)  # Deterministic conversion

**Optimization for Warm Starts:**

.. code-block:: python

   # Alternative: Initialize once, create sessions per request
   from functools import lru_cache

   @lru_cache(maxsize=1)
   def get_tracer():
       """Cached tracer - persists across warm starts."""
       return HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),
           project=os.getenv("HH_PROJECT")
       )

**Characteristics:**

✅ **Efficient** - Reuses tracer on warm starts
✅ **Isolated** - New session per invocation
✅ **Stateless** - No assumptions about container lifecycle
⚠️ **Session management** - Must create/update sessions manually

Pattern 4: Long-Running Server (FastAPI / Flask / Django)
----------------------------------------------------------

**Use When:**

- Running web server (FastAPI, Flask, Django, etc.)
- Handling multiple concurrent requests
- Need to trace each user request separately
- Want distributed tracing across services

**Pattern: Global Tracer + Per-Request Session via Baggage**

.. important::
   **How Multi-Session Handling Works:**
   
   The ``create_session()`` method stores the session_id in OpenTelemetry **baggage**,
   which uses Python's ``ContextVar`` internally. This means:
   
   - Each async task/thread gets its own isolated session context
   - The span processor reads session_id from baggage first
   - No race conditions between concurrent requests
   - The tracer instance is safely shared across all requests
   
   **Do NOT use** ``session_start()`` for concurrent requests - it stores session_id
   on the tracer instance, which causes race conditions.

.. code-block:: python

   # main.py (FastAPI example)
   from fastapi import FastAPI, Request
   from honeyhive import HoneyHiveTracer, trace
   import os

   # Initialize tracer ONCE at application startup
   # This instance is shared across ALL requests
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="my-api",
       source="production"
   )

   app = FastAPI()

   @app.middleware("http")
   async def session_middleware(request: Request, call_next):
       """Create isolated session for each request using baggage."""
       # acreate_session() is the async version - use for async middleware
       # It creates a session via API and stores session_id in baggage
       # (NOT on the tracer instance - that would cause race conditions)
       session_id = await tracer.acreate_session(
           session_name=f"api-{request.url.path}",
           inputs={
               "method": request.method,
               "path": str(request.url),
               "user_id": request.headers.get("X-User-ID")
           }
       )
       
       # Process request - all spans will use this session_id from baggage
       response = await call_next(request)
       
       # enrich_session reads session_id from baggage automatically
       tracer.enrich_session(
           outputs={"status_code": response.status_code}
       )
       
       # Optionally return session_id to client
       if session_id:
           response.headers["X-Session-ID"] = session_id
       
       return response

   @app.post("/api/chat")
   @trace(event_type="chain", tracer=tracer)
   async def chat_endpoint(message: str):
       """Each request traced to its own session."""
       # The span processor reads session_id from baggage (set by middleware)
       # This span automatically uses the correct session for this request
       tracer.enrich_span(metadata={"message_length": len(message)})
       
       response = await process_message(message)
       return {"response": response}

   @trace(event_type="tool", tracer=tracer)
   async def process_message(message: str):
       """Nested spans automatically use request's session context."""
       result = await llm_call(message)
       tracer.enrich_span(metadata={"tokens": len(result.split())})
       return result

**Sync Version (Flask / Django):**

For synchronous frameworks, use ``create_session()`` instead of ``acreate_session()``:

.. code-block:: python

   # Flask example
   from flask import Flask, request, g
   from honeyhive import HoneyHiveTracer, trace
   
   app = Flask(__name__)
   tracer = HoneyHiveTracer.init(api_key="...", project="my-api")
   
   @app.before_request
   def create_session_for_request():
       """Create session before each request."""
       g.session_id = tracer.create_session(
           session_name=f"flask-{request.path}",
           inputs={"method": request.method}
       )
   
   @app.after_request
   def enrich_session_after_request(response):
       """Enrich session with response data."""
       tracer.enrich_session(outputs={"status_code": response.status_code})
       return response

**Custom Session IDs and the ``skip_api_call`` Parameter:**

The ``create_session()`` method supports two different session ID scenarios:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Scenario
     - Code
     - When to Use
   * - Auto-generate ID
     - ``create_session(session_name="request")``
     - Default - HoneyHive creates and returns a new session ID
   * - Custom ID (API creates session)
     - ``create_session(session_id="my-id")``
     - You want to use your own ID scheme (e.g., ``user-{user_id}-{timestamp}``)
   * - Link to existing session
     - ``create_session(session_id="existing", skip_api_call=True)``
     - Session already exists - just set context for tracing

.. important::
   **When to use ``skip_api_call=True``:**
   
   Set ``skip_api_call=True`` ONLY when linking to a session that **already exists** 
   in HoneyHive (created by a previous request or external system).
   
   **Examples where ``skip_api_call=True`` makes sense:**
   
   - Multi-turn conversations: First request creates session, subsequent requests link to it
   - Webhook handlers: Parent service created session, webhook links to same session
   - Background jobs: Job receives session_id from queue message
   
   **Examples where ``skip_api_call=False`` (default) is correct:**
   
   - New user request: Create a new session in HoneyHive
   - Custom ID scheme: Create session with your own ID format
   - Any case where the session doesn't exist yet

.. code-block:: python

   # SCENARIO 1: Multi-turn conversation (first request creates, others link)
   @app.middleware("http")
   async def session_middleware(request: Request, call_next):
       existing_session = request.headers.get("X-Session-ID")
       
       if existing_session:
           # Link to existing session - NO API call needed
           await tracer.acreate_session(
               session_id=existing_session,
               skip_api_call=True  # Session already exists
           )
       else:
           # Create NEW session with auto-generated ID
           session_id = await tracer.acreate_session(
               session_name=f"conversation-{request.url.path}"
           )
           # Return session_id to client for future requests
           request.state.new_session_id = session_id
       
       response = await call_next(request)
       
       if hasattr(request.state, "new_session_id"):
           response.headers["X-Session-ID"] = request.state.new_session_id
       
       return response

.. code-block:: python

   # SCENARIO 2: Custom ID scheme (API creates session with YOUR ID)
   @app.middleware("http")
   async def session_middleware(request: Request, call_next):
       user_id = request.headers.get("X-User-ID", "anonymous")
       timestamp = int(time.time())
       
       # Create session with custom ID format
       # skip_api_call=False (default) - API creates session with this ID
       session_id = await tracer.acreate_session(
           session_id=f"user-{user_id}-{timestamp}",  # Your custom ID
           session_name=f"api-{request.url.path}",
           inputs={"user_id": user_id}
       )
       
       return await call_next(request)

**Using with_session Context Manager:**

For scoped session management, use the ``with_session`` context manager:

.. code-block:: python

   # Synchronous usage
   with tracer.with_session("batch-job", inputs={"batch_id": batch_id}) as session_id:
       # All spans created here use this session
       process_batch(items)
       tracer.enrich_session(outputs={"processed": len(items)})

**With Distributed Tracing:**

.. code-block:: python

   from opentelemetry import propagate, context

   @app.middleware("http")
   async def distributed_tracing_middleware(request: Request, call_next):
       """Extract trace context from upstream service."""
       # Extract parent trace context from headers
       ctx = propagate.extract(request.headers)
       
       # Make this context active for this request
       token = context.attach(ctx)
       
       try:
           # Create session - will be in the attached context
           session_id = await tracer.acreate_session(
               session_name=f"api-request",
               inputs={"path": str(request.url)}
           )
           
           response = await call_next(request)
           
           # Inject trace context into response for downstream
           propagate.inject(response.headers)
           
           return response
       finally:
           context.detach(token)

**Characteristics:**

✅ **Efficient** - Single tracer instance shared across requests
✅ **Isolated** - Each request gets own session via baggage (ContextVar)
✅ **Concurrent** - Handles multiple requests safely
✅ **Distributed** - Traces span multiple services
✅ **No race conditions** - Session stored in baggage, not on tracer instance

.. note::
   **Thread & Process Safety:**
   
   The global tracer pattern is safe for multi-threaded servers (FastAPI, Flask with threads) because:
   
   - ``create_session()`` stores session_id in OpenTelemetry baggage
   - Baggage uses Python's ``ContextVar`` (inherently request-scoped)
   - Each thread/async task has isolated context
   
   For **multi-process** deployments (Gunicorn with workers, uWSGI):
   
   - ✅ **Safe** - Each process gets its own tracer instance
   - ✅ **Safe** - Processes don't share state
   - ⚠️ **Note** - Tracer initialization happens per-process (acceptable overhead)

.. warning::
   **Common Mistake: Using session_start() for Web Servers**
   
   ``session_start()`` stores session_id on the tracer instance (``tracer._session_id``).
   In concurrent environments, this causes race conditions where requests overwrite
   each other's session_id.
   
   **Always use** ``create_session()`` or ``acreate_session()`` for web servers.
   These methods store session_id in baggage, which is request-scoped.

Pattern 5: Testing / Multi-Session Scenarios
---------------------------------------------

**Use When:**

- Writing integration tests
- Simulating multiple users/sessions
- Need explicit session control

**Pattern: Multiple Tracer Instances**

.. code-block:: python

   import pytest
   from honeyhive import HoneyHiveTracer

   @pytest.fixture
   def tracer_factory():
       """Factory for creating isolated tracer instances."""
       def _create_tracer(session_name: str):
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project="test-project",
               session_name=session_name,
               test_mode=True
           )
       return _create_tracer

   def test_user_flows(tracer_factory):
       """Test multiple user sessions concurrently."""
       # User 1 tracer instance
       user1_tracer = tracer_factory("user-1-session")
       
       # User 2 tracer instance
       user2_tracer = tracer_factory("user-2-session")
       
       # Completely isolated traces
       with user1_tracer.start_span("user-action"):
           process_user_action(user1_tracer, user_id="user-1")
           
       with user2_tracer.start_span("user-action"):
           process_user_action(user2_tracer, user_id="user-2")

**Characteristics:**

✅ **Explicit control** - Full control over tracer lifecycle
✅ **Isolated** - Each tracer completely independent
✅ **Testable** - Easy to verify trace output
⚠️ **More complex** - Must manage multiple instances

Common Patterns Summary
-----------------------

Global Tracer Pattern
~~~~~~~~~~~~~~~~~~~~~

**When to Use:**

- Local development and debugging
- Single execution context
- Simple scripts and notebooks
- Long-running servers (with per-request sessions)

**Example:**

.. code-block:: python

   # Module-level initialization
   tracer = HoneyHiveTracer.init(...)
   
   @trace(event_type="tool", tracer=tracer)
   def my_function():
       pass

**Pros:** Simple, efficient, reusable
**Cons:** Requires manual session management for isolation

Per-Request Tracer Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:**

- Serverless functions (cold start model)
- Need guaranteed isolation
- Stateless execution environments

**Example:**

.. code-block:: python

   def handler(event, context):
       # Create tracer per invocation
       tracer = HoneyHiveTracer.init(...)
       # Use tracer for this request only
       process(event, tracer)

**Pros:** Perfect isolation, no state leakage
**Cons:** Overhead of creating tracer instance

SDK-Managed Pattern (``evaluate()``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to Use:**

- Running experiments with ``evaluate()``
- Parallel datapoint processing
- Automatic per-datapoint isolation needed

**Example:**

.. code-block:: python

   @trace(event_type="tool")  # No tracer parameter
   def my_function(input):
       pass  # evaluate() manages tracer automatically

**Pros:** Zero configuration, automatic isolation
**Cons:** Only works with ``evaluate()`` function

Best Practices
--------------

1. **Choose Based on Execution Model**

   - **Stateless (serverless)**: Per-request or lazy initialization
   - **Stateful (server)**: Global tracer + per-request sessions
   - **Experiments**: Let ``evaluate()`` manage it

2. **Always Use Explicit Tracer Parameter**

   .. code-block:: python

      # ✅ GOOD - Explicit tracer reference
      @trace(event_type="tool", tracer=tracer)
      def my_function():
          tracer.enrich_span(...)

      # ❌ AVOID - Implicit tracer discovery (deprecated in v2.0)
      @trace(event_type="tool")
      def my_function():
          enrich_span(...)  # Global function - will be deprecated

3. **Create Sessions for Isolation**

   Even with a global tracer, create sessions per logical unit of work:

   .. code-block:: python

      # Per user request
      session_id = tracer.create_session(session_name=f"user-{user_id}")
      
      # Per batch job
      session_id = tracer.create_session(session_name=f"batch-{batch_id}")

4. **Use Test Mode for Development**

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key=os.getenv("HH_API_KEY"),
          project="my-project",
          test_mode=True  # Disables API calls for local testing
      )

5. **Enable Distributed Tracing in Microservices**

   .. code-block:: python

      from opentelemetry import propagate

      # Service A: Inject context
      propagate.inject(outgoing_request.headers)
      
      # Service B: Extract context
      ctx = propagate.extract(incoming_request.headers)
      tracer.create_session(..., link_carrier=ctx)

Troubleshooting
---------------

"My traces are getting mixed up between requests"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause:** Using ``session_start()`` or not creating sessions per request.
``session_start()`` stores session_id on the tracer instance, causing race conditions.

**Solution:** Use ``create_session()`` or ``acreate_session()`` which store session_id in baggage:

.. code-block:: python

   @app.middleware("http")
   async def session_middleware(request, call_next):
       # ✅ CORRECT: Uses baggage (request-scoped)
       await tracer.acreate_session(session_name=f"request-{request.url.path}")
       return await call_next(request)
   
   # ❌ WRONG: session_start() stores on tracer instance (race condition)
   # tracer.session_start()  # Don't use this for web servers!

"evaluate() is using the wrong tracer"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause:** You initialized a global tracer that conflicts with ``evaluate()``'s tracer management.

**Solution:** Remove global tracer initialization when using ``evaluate()``:

.. code-block:: python

   # ❌ DON'T DO THIS
   tracer = HoneyHiveTracer.init(...)
   
   @trace(tracer=tracer)  # This forces use of global tracer
   def my_function():
       pass

   # ✅ DO THIS
   @trace(event_type="tool")  # Let evaluate() provide tracer
   def my_function():
       pass

"Traces not appearing in HoneyHive"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause:** Tracer created but not linked to active spans.

**Solution:** Always pass ``tracer`` parameter to ``@trace``:

.. code-block:: python

   tracer = HoneyHiveTracer.init(...)
   
   @trace(event_type="tool", tracer=tracer)  # ✅ Explicit tracer
   def my_function():
       pass

Next Steps
----------

- :doc:`/how-to/evaluation/running-experiments` - Using ``evaluate()``
- :doc:`/how-to/deployment/production` - Production deployment patterns

