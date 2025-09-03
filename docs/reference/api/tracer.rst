HoneyHiveTracer API Reference
=============================

.. note::
   **Complete API documentation for the HoneyHiveTracer class**
   
   The primary interface for tracing LLM operations and custom application logic with HoneyHive observability.

.. currentmodule:: honeyhive

.. autoclass:: HoneyHiveTracer
   :members:
   :undoc-members:
   :show-inheritance:

The ``HoneyHiveTracer`` is the core component of the HoneyHive SDK, providing OpenTelemetry-based tracing with LLM-specific optimizations and BYOI (Bring Your Own Instrumentor) architecture support.

**Key Features:**

- Multi-instance support for different projects/environments
- Automatic OpenTelemetry configuration and management  
- LLM-specific span attributes and conventions
- Graceful degradation and error handling
- Built-in instrumentor management
- Thread-safe operations
- Context propagation across async/threaded operations

Class Methods
-------------

init()
~~~~~~

.. py:classmethod:: HoneyHiveTracer.init(api_key: Optional[str] = None, project: Optional[str] = None, source: str = "production", test_mode: bool = False, session_name: Optional[str] = None, server_url: Optional[str] = None, instrumentors: Optional[list] = None, disable_http_tracing: bool = True, **kwargs) -> "HoneyHiveTracer"
   :no-index:

   Initialize a new HoneyHiveTracer instance with the specified configuration.
   
   **Parameters:**
   
   :param api_key: HoneyHive API key. If not provided, reads from ``HH_API_KEY`` environment variable.
   :type api_key: Optional[str]
   
   :param project: Project name for organizing traces. If not provided, reads from ``HH_PROJECT`` environment variable or defaults to "default".
   :type project: Optional[str]
   
   :param source: Source environment identifier (e.g., "production", "staging", "development"). Defaults to "production".
   :type source: str
   
   :param test_mode: Enable test mode (no data sent to HoneyHive). Defaults to False.
   :type test_mode: bool
   
   :param session_name: Custom session name for grouping related traces. Auto-generated if not provided based on filename.
   :type session_name: Optional[str]
   
   :param server_url: Custom HoneyHive server URL for self-hosted deployments.
   :type server_url: Optional[str]
   
   :param instrumentors: List of OpenTelemetry instrumentors to apply automatically (BYOI pattern).
   :type instrumentors: Optional[List[BaseInstrumentor]]
   
   :param disable_http_tracing: Whether to disable HTTP request tracing. Defaults to True for performance.
   :type disable_http_tracing: bool
   
   :param kwargs: Additional configuration options passed to the underlying tracer
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: HoneyHiveTracer
   :returns: Configured HoneyHiveTracer instance
   
   **Raises:**
   
   :raises ValueError: If required configuration is missing or invalid
   :raises ConnectionError: If unable to connect to HoneyHive API
   :raises ImportError: If required dependencies are missing
   
   **Environment Variable Priority:**
   
   The ``init()`` method respects environment variables with the following precedence:
   
   1. Explicit parameters (highest priority)
   2. Environment variables
   3. Default values (lowest priority)
   
   **Supported Environment Variables:**
   
   .. list-table::
      :header-rows: 1
      :widths: 25 45 30
      
      * - Variable
        - Description
        - Default
      * - ``HH_API_KEY``
        - HoneyHive API key
        - **Required**
      * - ``HH_PROJECT``
        - Project name
        - "default"
      * - ``HH_SOURCE``
        - Source identifier
        - "production"
      * - ``HH_SESSION_NAME``
        - Session name
        - Auto-generated from filename
      * - ``HH_SERVER_URL``
        - Custom server URL
        - "https://api.honeyhive.ai"
      * - ``HH_TEST_MODE``
        - Enable test mode
        - "false"
      * - ``HH_DISABLE_HTTP_TRACING``
        - Disable HTTP tracing
        - "true"
   
   **Basic Usage Examples:**
   
   .. code-block:: python
   
      from honeyhive import HoneyHiveTracer
      
      # Minimal setup (uses environment variables)
      tracer = HoneyHiveTracer.init()
      
      # Explicit configuration
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_api_key_here",
          project="my-llm-app",
          source="production"
      )
      
      # Development mode
      tracer = HoneyHiveTracer.init(
          api_key="hh_dev_key",
          project="my-app-dev",
          source="development",
          test_mode=True  # No data sent to HoneyHive
      )
   
   **BYOI (Bring Your Own Instrumentor) Pattern:**
   
   .. code-block:: python
   
      from openinference.instrumentation.openai import OpenAIInstrumentor
      from openinference.instrumentation.anthropic import AnthropicInstrumentor
      
      # Single instrumentor
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_key",
          project="openai-app",
          instrumentors=[OpenAIInstrumentor()]
      )
      
      # Multiple instrumentors for multi-LLM applications
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_key",
          project="multi-llm-app",
          instrumentors=[
              OpenAIInstrumentor(),
              AnthropicInstrumentor()
          ]
      )
   
   **Multi-Instance Examples:**
   
   .. code-block:: python
   
      # Different projects
      user_tracer = HoneyHiveTracer.init(
          project="user-service",
          source="production"
      )
      
      payment_tracer = HoneyHiveTracer.init(
          project="payment-service", 
          source="production"
      )
      
      # Different environments
      prod_tracer = HoneyHiveTracer.init(
          project="my-app",
          source="production"
      )
      
      staging_tracer = HoneyHiveTracer.init(
          project="my-app-staging",
          source="staging"
      )
      
      dev_tracer = HoneyHiveTracer.init(
          project="my-app-dev",
          source="development",
          test_mode=True
      )
   
   **Self-Hosted Deployment:**
   
   .. code-block:: python
   
      # Custom HoneyHive deployment
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_key",
          project="enterprise-app",
          server_url="https://honeyhive.company.com"
      )

Constructor
-----------

__init__()
~~~~~~~~~~

.. automethod:: HoneyHiveTracer.__init__

   Direct constructor method. Generally prefer using the ``init()`` class method for initialization.

Instance Methods
----------------

trace()
~~~~~~~

.. py:method:: trace(name: str, event_type: Optional[str] = None, **kwargs) -> ContextManager[Span]
   :no-index:

   Create a traced span as a context manager for manual instrumentation.
   
   **Parameters:**
   
   :param name: Human-readable name for the operation being traced
   :type name: str
   
   :param event_type: Event type for categorization. Must be one of: ``"model"``, ``"tool"``, or ``"chain"``
   :type event_type: Optional[str]
   
   :param kwargs: Additional span attributes to set on creation
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: ContextManager[opentelemetry.trace.Span]
   :returns: Context manager yielding an OpenTelemetry Span object
   
   **Automatic Span Attributes:**
   
   The span automatically includes HoneyHive-specific attributes:
   
   - ``honeyhive.project``: Project name
   - ``honeyhive.source``: Source identifier  
   - ``honeyhive.session_name``: Session name
   - ``honeyhive.tracer_version``: SDK version
   - ``honeyhive.event_type``: Event type (if provided)
   
   **Basic Usage:**
   
   .. code-block:: python
   
      # Simple operation tracing
      with tracer.trace("user_lookup") as span:
          user = get_user_by_id(user_id)
          span.set_attribute("user.id", user_id)
          span.set_attribute("user.found", user is not None)
      
      # With custom event type
      with tracer.trace("llm_completion", event_type="openai_gpt4") as span:
          response = openai_client.chat.completions.create(
              model="gpt-4",
              messages=[{"role": "user", "content": prompt}]
          )
          span.set_attribute("model", "gpt-4")
          span.set_attribute("prompt.length", len(prompt))
          span.set_attribute("response.length", len(response.choices[0].message.content))
      
      # With initial attributes
      with tracer.trace("data_processing", 
                       operation_type="batch",
                       batch_size=100) as span:
          result = process_batch(data)
          span.set_attribute("processing.success", True)
   
   **Nested Spans (Automatic Context Propagation):**
   
   .. code-block:: python
   
      # Parent-child span relationships are automatic
      with tracer.trace("parent_operation") as parent:
          parent.set_attribute("operation.level", "parent")
          
          # Child spans inherit trace context
          with tracer.trace("child_operation") as child:
              child.set_attribute("operation.level", "child")
              
              # Grandchild spans
              with tracer.trace("grandchild_operation") as grandchild:
                  grandchild.set_attribute("operation.level", "grandchild")
   
   **Error Handling and Status:**
   
   .. code-block:: python
   
      from opentelemetry import trace
      
      with tracer.trace("risky_operation") as span:
          try:
              result = risky_function()
              span.set_status(trace.Status(trace.StatusCode.OK))
              span.set_attribute("operation.success", True)
          except ValueError as e:
              span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
              span.record_exception(e)
              span.set_attribute("operation.success", False)
              span.set_attribute("error.type", "ValueError")
              raise
          except Exception as e:
              span.set_status(trace.Status(trace.StatusCode.ERROR, "Unexpected error"))
              span.record_exception(e)
              span.set_attribute("operation.success", False)
              span.set_attribute("error.type", type(e).__name__)
              raise
   
   **Performance Measurement:**
   
   .. code-block:: python
   
      import time
      
      with tracer.trace("performance_critical_operation") as span:
          start_time = time.perf_counter()
          
          # Your operation here
          result = expensive_computation()
          
          duration = time.perf_counter() - start_time
          span.set_attribute("performance.duration_seconds", duration)
          span.set_attribute("performance.operations_per_second", 1 / duration)

enrich_current_span()
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: enrich_current_span(attributes: Dict[str, Any]) -> None

   Add attributes to the currently active span without needing direct span reference.
   
   **Parameters:**
   
   :param attributes: Dictionary of attributes to add to the current span
   :type attributes: Dict[str, Any]
   
   **Usage:**
   
   This method is particularly useful when using the ``@trace`` decorator where you don't have direct access to the span object.
   
   .. code-block:: python
   
      from honeyhive import trace
      
      @trace(tracer=tracer, event_type="user_processing")
      def process_user_request(user_id: str, request_data: dict):
          # Add attributes to the automatically created span
          tracer.enrich_current_span({
              "user.id": user_id,
              "user.tier": get_user_tier(user_id),
              "request.size": len(str(request_data)),
              "request.type": request_data.get("type", "unknown"),
              "request.timestamp": time.time()
          })
          
          # Continue processing...
          result = process_request(request_data)
          
          # Add more attributes based on results
          tracer.enrich_current_span({
              "response.success": True,
              "response.size": len(str(result)),
              "processing.duration": time.time() - start_time
          })
          
          return result
      
      # In a nested function without decorator
      def helper_function(data):
          # This will add to the active span from the parent function
          tracer.enrich_current_span({
              "helper.input_size": len(data),
              "helper.processing_method": "optimized"
          })
          return processed_data
   
   **Conditional Enrichment:**
   
   .. code-block:: python
   
      @trace(tracer=tracer)
      def conditional_processing(user_id: str, options: dict):
          # Always add basic info
          tracer.enrich_current_span({
              "user.id": user_id,
              "options.provided": len(options)
          })
          
          # Conditionally add detailed info for premium users
          user_tier = get_user_tier(user_id)
          if user_tier == "premium":
              tracer.enrich_current_span({
                  "user.tier": user_tier,
                  "user.detailed_options": str(options),
                  "processing.enhanced": True
              })

flush()
~~~~~~~

.. py:method:: flush(timeout: Optional[float] = None) -> bool

   Force immediate export of all pending trace data to HoneyHive.
   
   **Parameters:**
   
   :param timeout: Maximum time to wait for flush completion in seconds. If None, uses default timeout.
   :type timeout: Optional[float]
   
   **Returns:**
   
   :rtype: bool
   :returns: True if flush completed successfully within timeout, False otherwise
   
   **Usage:**
   
   .. code-block:: python
   
      # Before application shutdown
      print("Flushing traces before exit...")
      success = tracer.flush(timeout=10.0)
      if success:
          print("All traces sent successfully")
      else:
          print("Warning: Some traces may not have been sent")
      
      # In exception handlers
      try:
          main_application_logic()
      except KeyboardInterrupt:
          print("Received interrupt, flushing traces...")
          tracer.flush(timeout=5.0)
          raise
      
      # Periodic flushing in long-running applications
      import time
      import threading
      
      def periodic_flush():
          while True:
              time.sleep(60)  # Flush every minute
              success = tracer.flush(timeout=30.0)
              if not success:
                  logger.warning("Periodic flush failed")
      
      # Start background flush thread
      flush_thread = threading.Thread(target=periodic_flush, daemon=True)
      flush_thread.start()

close()
~~~~~~~

.. py:method:: close() -> None

   Gracefully shutdown the tracer and release all resources.
   
   **Usage:**
   
   .. code-block:: python
   
      # Clean shutdown sequence
      try:
          # First flush any pending traces
          tracer.flush(timeout=10.0)
      finally:
          # Then close the tracer
          tracer.close()
      
      # Using context manager for automatic cleanup
      with HoneyHiveTracer.init(api_key="hh_key", project="myapp") as tracer:
          # Use tracer for operations
          with tracer.trace("operation"):
              do_work()
      # Tracer automatically flushed and closed here
      
      # In application cleanup handlers
      import atexit
      
      tracer = HoneyHiveTracer.init(api_key="hh_key", project="myapp")
      
      def cleanup_tracer():
          print("Cleaning up tracer...")
          tracer.flush(timeout=5.0)
          tracer.close()
      
      atexit.register(cleanup_tracer)

Properties
----------

project
~~~~~~~

.. py:attribute:: project
   :type: str

   The project name associated with this tracer instance.
   
   .. code-block:: python
   
      tracer = HoneyHiveTracer.init(project="user-service")
      print(f"Tracer project: {tracer.project}")  # "user-service"

source
~~~~~~

.. py:attribute:: source
   :type: str

   The source environment identifier for this tracer instance.
   
   .. code-block:: python
   
      tracer = HoneyHiveTracer.init(source="production")
      print(f"Environment: {tracer.source}")  # "production"

session_id
~~~~~~~~~~

.. py:attribute:: session_id
   :type: str

   Unique session identifier for this tracer instance.
   
   .. code-block:: python
   
      tracer = HoneyHiveTracer.init(session_name="user-onboarding")
      print(f"Session ID: {tracer.session_id}")  # Auto-generated unique ID

test_mode
~~~~~~~~~

.. py:attribute:: test_mode
   :type: bool

   Whether the tracer is in test mode (no data sent to HoneyHive).
   
   .. code-block:: python
   
      tracer = HoneyHiveTracer.init(test_mode=True)
      if tracer.test_mode:
          print("Running in test mode - no data will be sent")

Multi-Instance Architecture
---------------------------

The HoneyHiveTracer supports multiple independent instances for flexible workflow management:

**Environment Separation:**

.. code-block:: python

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-api-key",
       project="my-app",
       source="production"
   )
   
   # Staging tracer
   staging_tracer = HoneyHiveTracer.init(
       api_key="staging-api-key",
       project="my-app-staging",
       source="staging"
   )
   
   # Development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-api-key",
       project="my-app-dev",
       source="development",
       test_mode=True
   )

**Service-Based Separation:**

.. code-block:: python

   # Microservices architecture
   auth_tracer = HoneyHiveTracer.init(
       project="auth-service",
       session_name="auth_operations"
   )
   
   user_tracer = HoneyHiveTracer.init(
       project="user-service",
       session_name="user_operations"
   )
   
   payment_tracer = HoneyHiveTracer.init(
       project="payment-service",
       session_name="payment_operations"
   )

**Workflow-Based Separation:**

.. code-block:: python

   # Different workflows with different instrumentors
   chat_tracer = HoneyHiveTracer.init(
       project="chat-service",
       instrumentors=[OpenAIInstrumentor()]
   )
   
   analysis_tracer = HoneyHiveTracer.init(
       project="analysis-service",
       instrumentors=[AnthropicInstrumentor()]
   )
   
   background_tracer = HoneyHiveTracer.init(
       project="background-jobs",
       # No instrumentors for non-LLM background tasks
   )

Thread Safety
-------------

All HoneyHiveTracer instances are thread-safe and can be safely used across multiple threads:

.. code-block:: python

   import threading
   import concurrent.futures
   from honeyhive import HoneyHiveTracer, trace
   
   # Global tracer instance
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="concurrent-app"
   )
   
   @trace(tracer=tracer)
   def worker_function(worker_id: int, data: str):
       """Safe to call from multiple threads simultaneously."""
       with tracer.trace(f"worker_{worker_id}_processing") as span:
           span.set_attribute("worker.id", worker_id)
           span.set_attribute("data.length", len(data))
           
           # Simulate work
           time.sleep(random.uniform(0.1, 0.5))
           
           tracer.enrich_current_span({
               "worker.completion_time": time.time(),
               "worker.thread_id": threading.current_thread().ident
           })
           
           return f"Worker {worker_id} processed {len(data)} characters"
   
   # Concurrent execution
   with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
       futures = []
       for i in range(50):
           future = executor.submit(worker_function, i, f"data_for_worker_{i}")
           futures.append(future)
       
       # Collect results
       for future in concurrent.futures.as_completed(futures):
           result = future.result()
           print(result)

Context Propagation
-------------------

The tracer automatically handles OpenTelemetry context propagation across different execution contexts:

**Thread Context Propagation:**

.. code-block:: python

   import threading
   from opentelemetry import trace
   
   @trace(tracer=tracer, event_type="parent_operation")
   def parent_function():
       # Start a parent span
       tracer.enrich_current_span({"operation.type": "parent"})
       
       def worker():
           # Child span automatically inherits parent context
           with tracer.trace("child_operation") as span:
               span.set_attribute("operation.type", "child")
               span.set_attribute("thread.id", threading.current_thread().ident)
       
       # Start worker in separate thread
       thread = threading.Thread(target=worker)
       thread.start()
       thread.join()

**Async Context Propagation:**

.. code-block:: python

   import asyncio
   
   @trace(tracer=tracer, event_type="async_parent")
   async def async_parent():
       tracer.enrich_current_span({"operation.type": "async_parent"})
       
       # Child async operations inherit context
       await async_child()
   
   @trace(tracer=tracer, event_type="async_child")
   async def async_child():
       tracer.enrich_current_span({"operation.type": "async_child"})
       await asyncio.sleep(0.1)
   
   # Run async operations
   asyncio.run(async_parent())

**HTTP Context Propagation:**

.. code-block:: python

   import requests
   from opentelemetry.propagate import inject
   
   @trace(tracer=tracer, event_type="http_client_call")
   def make_http_request(url: str):
       headers = {"Content-Type": "application/json"}
       
       # Inject trace context into HTTP headers
       inject(headers)
       
       response = requests.get(url, headers=headers)
       
       tracer.enrich_current_span({
           "http.url": url,
           "http.status_code": response.status_code,
           "http.response_size": len(response.content)
       })
       
       return response

Error Handling and Resilience
-----------------------------

The HoneyHiveTracer is designed for production resilience with graceful degradation:

**Graceful Degradation:**

.. code-block:: python

   # If HoneyHive API is unavailable, your application continues normally
   try:
       tracer = HoneyHiveTracer.init(api_key="potentially_invalid_key")
   except Exception as e:
       # Tracer initialization failed, but app can continue
       print(f"Tracing unavailable: {e}")
       tracer = None
   
   # Safe usage pattern
   def safe_trace_operation():
       if tracer:
           with tracer.trace("operation") as span:
               span.set_attribute("tracing.enabled", True)
               result = business_logic()
       else:
           # Business logic still runs without tracing
           result = business_logic()
       return result

**Automatic Exception Capture:**

.. code-block:: python

   @trace(tracer=tracer, event_type="error_prone_operation")
   def operation_that_might_fail():
       if random.random() < 0.3:
           raise ValueError("Simulated failure")
       elif random.random() < 0.6:
           raise ConnectionError("Network issue")
       return "Success!"
   
   # The tracer automatically captures:
   # - Exception type and message
   # - Stack trace
   # - Execution time up to failure
   # - Span status marking as error
   
   try:
       result = operation_that_might_fail()
   except Exception as e:
       # Exception info is already captured in the trace
       print(f"Operation failed: {e}")

**Retry Logic Integration:**

.. code-block:: python

   import time
   from functools import wraps
   
   def with_retry(max_retries=3, delay=1.0):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               for attempt in range(max_retries):
                   try:
                       with tracer.trace(f"{func.__name__}_attempt_{attempt + 1}") as span:
                           span.set_attribute("retry.attempt", attempt + 1)
                           span.set_attribute("retry.max_attempts", max_retries)
                           
                           result = func(*args, **kwargs)
                           
                           span.set_attribute("retry.success", True)
                           span.set_attribute("retry.final_attempt", attempt + 1)
                           return result
                           
                   except Exception as e:
                       span.set_attribute("retry.success", False)
                       span.set_attribute("retry.error", str(e))
                       
                       if attempt == max_retries - 1:
                           span.set_attribute("retry.exhausted", True)
                           raise
                       
                       time.sleep(delay * (2 ** attempt))  # Exponential backoff
           return wrapper
       return decorator
   
   @with_retry(max_retries=3, delay=0.5)
   @trace(tracer=tracer, event_type="external_api_call")
   def call_external_api():
       # Potentially flaky external API call
       response = requests.get("https://api.example.com/data", timeout=5)
       response.raise_for_status()
       return response.json()

Framework Integration Examples
------------------------------

**Flask Integration:**

.. code-block:: python

   from flask import Flask, request, g
   
   app = Flask(__name__)
   tracer = HoneyHiveTracer.init(project="flask-app")
   
   @app.before_request
   def start_trace():
       g.span = tracer.trace(f"{request.method} {request.path}")
       g.span.__enter__()
       g.span.set_attribute("http.method", request.method)
       g.span.set_attribute("http.url", request.url)
       g.span.set_attribute("http.user_agent", request.headers.get("User-Agent", ""))
   
   @app.after_request
   def end_trace(response):
       if hasattr(g, 'span'):
           g.span.set_attribute("http.status_code", response.status_code)
           g.span.set_attribute("http.response_size", len(response.get_data()))
           g.span.__exit__(None, None, None)
       return response
   
   @app.route("/users/<user_id>")
   def get_user(user_id):
       with tracer.trace("get_user_operation") as span:
           span.set_attribute("user.id", user_id)
           
           # Your business logic here
           user_data = fetch_user_from_db(user_id)
           
           span.set_attribute("user.found", user_data is not None)
           return {"user": user_data}

**FastAPI Integration:**

.. code-block:: python

   from fastapi import FastAPI, Request, Response
   import time
   
   app = FastAPI()
   tracer = HoneyHiveTracer.init(project="fastapi-app")
   
   @app.middleware("http")
   async def trace_requests(request: Request, call_next):
       start_time = time.time()
       
       with tracer.trace(f"{request.method} {request.url.path}") as span:
           span.set_attribute("http.method", request.method)
           span.set_attribute("http.url", str(request.url))
           span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))
           
           response = await call_next(request)
           
           duration = time.time() - start_time
           span.set_attribute("http.status_code", response.status_code)
           span.set_attribute("http.duration", duration)
           
           return response
   
   @app.get("/users/{user_id}")
   async def get_user(user_id: str):
       with tracer.trace("get_user_async") as span:
           span.set_attribute("user.id", user_id)
           
           # Simulate async database call
           await asyncio.sleep(0.1)
           user_data = {"id": user_id, "name": "User Name"}
           
           span.set_attribute("user.found", True)
           return user_data

**Django Integration:**

.. code-block:: python

   # middleware.py
   from django.utils.deprecation import MiddlewareMixin
   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(project="django-app")
   
   class HoneyHiveMiddleware(MiddlewareMixin):
       def process_request(self, request):
           request.honeyhive_span = tracer.trace(f"{request.method} {request.path}")
           request.honeyhive_span.__enter__()
           
           request.honeyhive_span.set_attribute("http.method", request.method)
           request.honeyhive_span.set_attribute("http.path", request.path)
           request.honeyhive_span.set_attribute("http.user_agent", 
                                               request.META.get("HTTP_USER_AGENT", ""))
       
       def process_response(self, request, response):
           if hasattr(request, 'honeyhive_span'):
               request.honeyhive_span.set_attribute("http.status_code", response.status_code)
               request.honeyhive_span.__exit__(None, None, None)
           return response
   
   # views.py
   from django.http import JsonResponse
   from django.conf import settings
   
   def user_detail(request, user_id):
       with settings.HONEYHIVE_TRACER.trace("get_user_detail") as span:
           span.set_attribute("user.id", user_id)
           
           # Your Django logic here
           user_data = {"id": user_id, "name": "User Name"}
           
           span.set_attribute("user.found", True)
           return JsonResponse(user_data)

Performance Considerations
--------------------------

**Batching and Sampling:**

.. code-block:: python

   # For high-throughput applications, consider sampling
   import random
   
   def should_trace():
       return random.random() < 0.1  # 10% sampling
   
   @trace(tracer=tracer if should_trace() else None)
   def high_volume_operation():
       # Only 10% of calls will be traced
       pass

**Efficient Attribute Setting:**

.. code-block:: python

   # Batch attribute setting for better performance
   with tracer.trace("efficient_operation") as span:
       # Instead of multiple set_attribute calls
       attributes = {
           "user.id": user_id,
           "user.tier": user_tier,
           "operation.type": "batch",
           "operation.size": batch_size,
           "operation.priority": priority
       }
       
       # Set all at once
       for key, value in attributes.items():
           span.set_attribute(key, value)

Best Practices
--------------

**Naming Conventions:**

.. code-block:: python

   # Good: Descriptive, hierarchical names
   with tracer.trace("user.authentication.login"):
       pass
   
   with tracer.trace("payment.processing.stripe.charge"):
       pass
   
   with tracer.trace("llm.openai.completion.gpt4"):
       pass
   
   # Avoid: Generic or unclear names
   with tracer.trace("operation"):  # Too generic
       pass
   
   with tracer.trace("func1"):  # Not descriptive
       pass

**Consistent Attribute Patterns:**

.. code-block:: python

   # Establish consistent attribute patterns across your application
   with tracer.trace("user_operation") as span:
       # User-related attributes
       span.set_attribute("user.id", user_id)
       span.set_attribute("user.email", user_email)
       span.set_attribute("user.tier", user_tier)
       
       # Operation-related attributes  
       span.set_attribute("operation.type", "user_update")
       span.set_attribute("operation.duration", duration)
       span.set_attribute("operation.success", success)
       
       # Resource-related attributes
       span.set_attribute("resource.database", "users")
       span.set_attribute("resource.table", "user_profiles")

**Resource Management:**

.. code-block:: python

   # Ensure proper cleanup in long-running applications
   import atexit
   import signal
   import sys
   
   tracer = HoneyHiveTracer.init(project="long-running-app")
   
   def cleanup_handler(signum=None, frame=None):
       print("Shutting down, flushing traces...")
       tracer.flush(timeout=10.0)
       tracer.close()
       if signum:
           sys.exit(0)
   
   # Register cleanup handlers
   atexit.register(cleanup_handler)
   signal.signal(signal.SIGINT, cleanup_handler)
   signal.signal(signal.SIGTERM, cleanup_handler)

See Also
--------

- :doc:`decorators` - ``@trace`` and ``@evaluate`` decorator reference
- :doc:`client` - HoneyHive client API reference
- :doc:`../../tutorials/02-basic-tracing` - Basic tracing tutorial
- :doc:`../../tutorials/advanced-setup` - Advanced configuration patterns
- :doc:`../../how-to/troubleshooting` - Troubleshooting tracing issues
- :doc:`../../explanation/concepts/tracing-fundamentals` - Tracing concepts and theory
- :doc:`../../explanation/architecture/overview` - Architecture overview and patterns