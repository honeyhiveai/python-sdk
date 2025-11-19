HoneyHiveTracer API Reference
=============================

.. note::
   **Complete API documentation for the HoneyHiveTracer class**
   
   The primary interface for tracing LLM operations and custom application logic with HoneyHive observability.

.. important::
   **🆕 NEW: Modular Architecture & Hybrid Configuration**
   
   The ``HoneyHiveTracer`` has been completely rewritten with a modular, mixin-based architecture and now supports Pydantic configuration models.
   
   **See Also:**
   
   - :doc:`tracer-architecture` - Detailed architectural information
   - :doc:`config-models` - Complete configuration models API reference

.. currentmodule:: honeyhive

.. autoclass:: HoneyHiveTracer
   :members:
   :undoc-members:
   :show-inheritance:

The ``HoneyHiveTracer`` is the core component of the HoneyHive SDK, providing OpenTelemetry-based tracing with LLM-specific optimizations and BYOI (Bring Your Own Instrumentor) architecture support.

**🆕 Architecture Overview:**

The tracer is now composed from multiple mixins using dynamic inheritance:

.. code-block:: python

   class HoneyHiveTracer(HoneyHiveTracerBase, TracerOperationsMixin, TracerContextMixin):
       """Main tracer class composed from multiple mixins."""

**Modular Components:**

- **HoneyHiveTracerBase**: Core initialization and configuration (``tracer/core/base.py``)
- **TracerOperationsMixin**: Span creation and event management (``tracer/core/operations.py``)
- **TracerContextMixin**: Context and baggage management (``tracer/core/context.py``)

**Key Features:**

- **🆕 Hybrid Configuration**: Supports both Pydantic config objects and traditional parameters
- **🆕 Modular Architecture**: Mixin-based composition with 35 files across 6 modules
- Multi-instance support for different projects/environments
- Automatic OpenTelemetry configuration and management  
- LLM-specific span attributes and conventions
- Graceful degradation and error handling
- Built-in instrumentor management
- Thread-safe operations
- Context propagation across async/threaded operations

**🆕 Configuration Options:**

The tracer supports three initialization patterns:

.. tabs::

   .. tab:: 🆕 Modern Config Objects (Recommended)

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         from honeyhive.config.models import TracerConfig
         
         config = TracerConfig(
             api_key="hh_1234567890abcdef",
             project="my-llm-project",
             verbose=True
         )
         tracer = HoneyHiveTracer(config=config)

   .. tab:: 🔄 Traditional Parameters (Backwards Compatible)

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         
         tracer = HoneyHiveTracer(
             api_key="hh_1234567890abcdef",
             project="my-llm-project",
             verbose=True
         )

   .. tab:: 🔀 Mixed Approach

      .. code-block:: python

         from honeyhive import HoneyHiveTracer
         from honeyhive.config.models import TracerConfig
         
         config = TracerConfig(api_key="hh_1234567890abcdef", project="my-llm-project")
         tracer = HoneyHiveTracer(config=config, verbose=True)  # verbose overrides config

Class Methods
-------------

init()
~~~~~~

.. py:classmethod:: HoneyHiveTracer.init(api_key: Optional[str] = None, project: Optional[str] = None, session_name: Optional[str] = None, source: str = "dev", server_url: Optional[str] = None, session_id: Optional[str] = None, disable_http_tracing: bool = True, disable_batch: bool = False, verbose: bool = False, inputs: Optional[Dict[str, Any]] = None, is_evaluation: bool = False, run_id: Optional[str] = None, dataset_id: Optional[str] = None, datapoint_id: Optional[str] = None, link_carrier: Optional[Dict[str, Any]] = None, test_mode: bool = False, **kwargs) -> "HoneyHiveTracer"
   :no-index:

   Initialize a new HoneyHiveTracer instance with the specified configuration.
   
   **Core Parameters:**
   
   :param api_key: HoneyHive API key. If not provided, reads from ``HH_API_KEY`` environment variable.
   :type api_key: Optional[str]
   
   :param project: Project name (required by backend API). If not provided, reads from ``HH_PROJECT`` environment variable.
   :type project: Optional[str]
   
   :param session_name: Custom session name for grouping related traces. Auto-generated if not provided based on filename.
   :type session_name: Optional[str]
   
   :param source: Source environment identifier (e.g., "production", "staging", "development"). Defaults to "dev".
   :type source: str
   
   :param test_mode: Enable test mode (no data sent to HoneyHive). Defaults to False.
   :type test_mode: bool
   
   **Advanced Configuration:**
   
   :param server_url: Custom HoneyHive server URL for self-hosted deployments. Overrides ``HH_API_URL`` environment variable.
   :type server_url: Optional[str]
   
   :param session_id: Existing session ID to link to. Must be a valid UUID string. If invalid and not in test mode, raises ValueError.
   :type session_id: Optional[str]
   
   :param disable_http_tracing: Whether to disable HTTP request tracing. Defaults to True for performance.
   :type disable_http_tracing: bool
   
   :param disable_batch: Whether to disable batch processing and use SimpleSpanProcessor instead of BatchSpanProcessor. Defaults to False.
   :type disable_batch: bool
   
   :param verbose: Enable verbose debug logging throughout tracer initialization. Defaults to False.
   :type verbose: bool
   
   **Evaluation Parameters (Backwards Compatibility):**
   
   :param inputs: Session initialization inputs for backwards compatibility with main branch.
   :type inputs: Optional[Dict[str, Any]]
   
   :param is_evaluation: Whether this is an evaluation session. When True, adds evaluation-specific baggage context.
   :type is_evaluation: bool
   
   :param run_id: Evaluation run ID. Added to baggage context when ``is_evaluation`` is True.
   :type run_id: Optional[str]
   
   :param dataset_id: Evaluation dataset ID. Added to baggage context when ``is_evaluation`` is True.
   :type dataset_id: Optional[str]
   
   :param datapoint_id: Evaluation datapoint ID. Added to baggage context when ``is_evaluation`` is True.
   :type datapoint_id: Optional[str]
   
   **Context Propagation (Backwards Compatibility):**
   
   :param link_carrier: Context propagation carrier for linking to parent traces. Uses OpenTelemetry propagation.
   :type link_carrier: Optional[Dict[str, Any]]
   
   :param kwargs: Additional configuration options for future compatibility
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
        - Project identifier
        - **Required**
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
      # Requires HH_API_KEY and HH_PROJECT environment variables to be set
      tracer = HoneyHiveTracer.init()
      
      # Or specify project explicitly
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Explicit configuration
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_api_key_here",  # Or set HH_API_KEY environment variable
          project="your-project",          # Or set HH_PROJECT environment variable
          source="production"              # Or set HH_SOURCE environment variable
      )
      
      # Development mode
      tracer = HoneyHiveTracer.init(
          api_key="hh_dev_key",            # Or set HH_API_KEY environment variable
          project="your-project",          # Or set HH_PROJECT environment variable
          source="development",            # Or set HH_SOURCE environment variable
          test_mode=True                   # No data sent to HoneyHive (or set HH_TEST_MODE=true)
      )
   
   **BYOI (Bring Your Own Instrumentor) Pattern:**
   
   .. code-block:: python
   
      from openinference.instrumentation.openai import OpenAIInstrumentor
      from openinference.instrumentation.anthropic import AnthropicInstrumentor
      
      # Single instrumentor
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          api_key="your-api-key",  # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)
      
      # Multiple instrumentors for multi-LLM applications
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          api_key="your-api-key",  # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentors separately with tracer_provider
      openai_instrumentor = OpenAIInstrumentor()
      anthropic_instrumentor = AnthropicInstrumentor()
      
      openai_instrumentor.instrument(tracer_provider=tracer.provider)
      anthropic_instrumentor.instrument(tracer_provider=tracer.provider)

**Multi-Instance Examples:**

   .. note::
      **Multi-Instance Pattern**: Each tracer instance requires a unique ``api_key`` + ``project`` pair to properly target different HoneyHive projects. For same project across environments, use the same API key but different ``source`` values.
      
      **Environment Variable Limitation**: Standard ``HH_API_KEY`` and ``HH_PROJECT`` environment variables are global per process and don't work for multi-project scenarios. Use explicit parameters or custom environment variables for each service.
   
   .. code-block:: python
   
      # Different projects - MUST use explicit parameters (not HH_* env vars)
      user_tracer = HoneyHiveTracer.init(
          api_key="hh_user_service_key",    # Unique API key for user-service project
          project="user-service",           # Target project: user-service
          source="production"               # Explicit source (HH_SOURCE won't work for multi-instance)
      )
      
      payment_tracer = HoneyHiveTracer.init(
          api_key="hh_payment_service_key", # Unique API key for payment-service project  
          project="payment-service",        # Target project: payment-service
          source="production"               # Explicit source (HH_SOURCE won't work for multi-instance)
      )
      
      # Different environments - same project (can use HH_* env vars OR explicit params)
      # Option 1: Explicit parameters (recommended for clarity)
      prod_tracer = HoneyHiveTracer.init(
          api_key="hh_my_project_key",     # Same API key for same project
          project="my-project",            # Same target project
          source="production"              # Different environment
      )
      
      staging_tracer = HoneyHiveTracer.init(
          api_key="hh_my_project_key",     # Same API key for same project
          project="my-project",            # Same target project  
          source="staging"                 # Different environment
      )
      
      # Option 2: Environment variables (works for single project only)
      # export HH_API_KEY="hh_my_project_key"
      # export HH_PROJECT="my-project"
      dev_tracer = HoneyHiveTracer.init(
          source="development",            # Only source differs
          test_mode=True                   # Enable test mode for development
      )
      
      # Option 3: Custom environment variables for multi-project (recommended pattern)
      # Use service-specific environment variables instead of global HH_* vars:
      # export USER_SERVICE_API_KEY="hh_user_service_key"
      # export USER_SERVICE_PROJECT="user-service"
      # export PAYMENT_SERVICE_API_KEY="hh_payment_service_key"  
      # export PAYMENT_SERVICE_PROJECT="payment-service"
      
      import os
      user_tracer = HoneyHiveTracer.init(
          api_key=os.getenv("USER_SERVICE_API_KEY"),      # Service-specific env var
          project=os.getenv("USER_SERVICE_PROJECT"),      # Service-specific env var
          source="production"
      )
      
      payment_tracer = HoneyHiveTracer.init(
          api_key=os.getenv("PAYMENT_SERVICE_API_KEY"),   # Service-specific env var
          project=os.getenv("PAYMENT_SERVICE_PROJECT"),   # Service-specific env var
          source="production"
      )
   
   **Self-Hosted Deployment:**
   
   .. code-block:: python
   
      # Custom HoneyHive deployment
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_key",                      # Or set HH_API_KEY environment variable
          project="your-project",                     # Or set HH_PROJECT environment variable
          server_url="https://honeyhive.company.com"  # Or set HH_API_URL environment variable
      )
   
   **Backwards Compatibility Examples (v0.1.0rc2+):**
   
   All 16 original parameters from the main branch are now supported:
   
   .. code-block:: python
   
      from honeyhive import HoneyHiveTracer
      
      # Full backwards compatibility - all original parameters work
      tracer = HoneyHiveTracer.init(
          api_key="hh_your_key",                   # Or set HH_API_KEY environment variable
          project="my-project",                    # Required parameter (or set HH_PROJECT)
          session_name="evaluation-session",
          source="production",
          server_url="https://custom.honeyhive.ai", # Overrides HH_API_URL
          session_id="550e8400-e29b-41d4-a716-446655440000", # Valid UUID
          disable_http_tracing=True,               # Default for performance
          disable_batch=False,                     # Use BatchSpanProcessor (default)
          verbose=True,                            # Enable debug output
          inputs={"user_id": "123", "query": "test"}, # Session inputs
          is_evaluation=True,                      # Evaluation workflow
          run_id="eval-run-001",                   # Evaluation run
          dataset_id="dataset-123",                # Evaluation dataset
          datapoint_id="datapoint-456",            # Evaluation datapoint
          test_mode=False                          # Send data to HoneyHive
      )
      
      # Evaluation workflow example
      evaluation_tracer = HoneyHiveTracer.init(
          api_key="hh_eval_key",           # Or set HH_API_KEY environment variable
          project="evaluation-project",    # Or set HH_PROJECT environment variable
          is_evaluation=True,
          run_id="experiment-2024-001",
          dataset_id="benchmark-dataset",
          verbose=True  # See evaluation baggage being set
      )
      
      # Context propagation example
      parent_carrier = {"traceparent": "00-trace-id-span-id-01"}
      child_tracer = HoneyHiveTracer.init(
          api_key="hh_key",                # Or set HH_API_KEY environment variable
          project="your-project",          # Or set HH_PROJECT environment variable
          link_carrier=parent_carrier,     # Links to parent trace
          verbose=True
      )
      
      # Performance tuning example
      high_throughput_tracer = HoneyHiveTracer.init(
          api_key="hh_key",                # Or set HH_API_KEY environment variable
          project="your-project",          # Or set HH_PROJECT environment variable
          disable_batch=True,              # Use SimpleSpanProcessor for immediate export
          disable_http_tracing=True,       # Reduce overhead (or set HH_DISABLE_HTTP_TRACING=true)
          verbose=False                    # Minimal logging
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
      with HoneyHiveTracer.init(
          api_key="hh_key",        # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      ) as tracer:
          # Use tracer for operations
          with tracer.trace("operation"):
              do_work()
      # Tracer automatically flushed and closed here
      
      # In application cleanup handlers
      import atexit
      
      tracer = HoneyHiveTracer.init(
          api_key="hh_key",        # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      )
      
      def cleanup_tracer():
          print("Cleaning up tracer...")
          tracer.flush(timeout=5.0)
          tracer.close()
      
      atexit.register(cleanup_tracer)

Context Propagation Methods (Backwards Compatibility)
-----------------------------------------------------

link()
~~~~~~

.. py:method:: link(carrier: Optional[Dict[str, Any]] = None, getter: Optional[Any] = None) -> Any

   Link to parent context via carrier for distributed tracing (backwards compatibility).
   
   **Parameters:**
   
   :param carrier: Context propagation carrier containing trace context
   :type carrier: Optional[Dict[str, Any]]
   
   :param getter: Custom getter for extracting context from carrier
   :type getter: Optional[Any]
   
   **Returns:**
   
   :rtype: Any
   :returns: Context token for later unlinking
   
   **Usage:**
   
   .. code-block:: python
   
      # Link to parent trace from HTTP headers
      headers = {"traceparent": "00-trace-id-span-id-01"}
      token = tracer.link(headers)
      
      # Your traced operations will now be children of the parent trace
      with tracer.trace("child_operation") as span:
          span.set_attribute("linked_to_parent", True)
      
      # Unlink when done
      tracer.unlink(token)

unlink()
~~~~~~~~

.. py:method:: unlink(token: Any) -> None

   Unlink from parent context (backwards compatibility).
   
   **Parameters:**
   
   :param token: Context token returned by link() method
   :type token: Any
   
   **Usage:**
   
   .. code-block:: python
   
      # Link to parent context
      token = tracer.link(parent_carrier)
      
      try:
          # Operations linked to parent
          with tracer.trace("linked_operation"):
              do_work()
      finally:
          # Always unlink to restore original context
          tracer.unlink(token)

inject()
~~~~~~~~

.. py:method:: inject(carrier: Optional[Dict[str, Any]] = None, setter: Optional[Any] = None) -> Dict[str, Any]

   Inject current trace and baggage context into carrier (backwards compatibility).
   
   **Parameters:**
   
   :param carrier: Carrier dictionary to inject context into
   :type carrier: Optional[Dict[str, Any]]
   
   :param setter: Custom setter for injecting context into carrier
   :type setter: Optional[Any]
   
   **Returns:**
   
   :rtype: Dict[str, Any]
   :returns: Carrier with injected trace context
   
   **Usage:**
   
   .. code-block:: python
   
      # Inject current trace context into HTTP headers
      headers = {"Content-Type": "application/json"}
      headers_with_trace = tracer.inject(headers)
      
      # Make HTTP request with trace context
      response = requests.post(
          "https://api.example.com/data",
          headers=headers_with_trace,
          json=payload
      )
      
      # Or inject into empty carrier
      trace_context = tracer.inject()
      print(f"Trace context: {trace_context}")

Properties
----------

project
~~~~~~~

.. py:attribute:: project
   :type: str

   The project name associated with this tracer instance.
   
   .. code-block:: python
   
      # Uses HH_API_KEY and HH_PROJECT environment variables
      # Or specify project explicitly:
      tracer = HoneyHiveTracer.init(project="user-service")  # Or set HH_PROJECT environment variable
      print(f"Tracer project: {tracer.project}")  # "user-service"

source
~~~~~~

.. py:attribute:: source
   :type: str

   The source environment identifier for this tracer instance.
   
   .. code-block:: python
   
      # Uses HH_API_KEY and HH_PROJECT environment variables
      tracer = HoneyHiveTracer.init(
          project="your-project",  # Or set HH_PROJECT environment variable
          source="production"
      )
      print(f"Environment: {tracer.source}")  # "production"

session_id
~~~~~~~~~~

.. py:attribute:: session_id
   :type: str

   Unique session identifier for this tracer instance.
   
   .. code-block:: python
   
      # Uses HH_API_KEY and HH_PROJECT environment variables
      tracer = HoneyHiveTracer.init(
          project="your-project",  # Or set HH_PROJECT environment variable
          session_name="user-onboarding"
      )
      print(f"Session ID: {tracer.session_id}")  # Auto-generated unique ID

test_mode
~~~~~~~~~

.. py:attribute:: test_mode
   :type: bool

   Whether the tracer is in test mode (no data sent to HoneyHive).
   
   .. code-block:: python
   
      # Requires HH_API_KEY environment variable
      tracer = HoneyHiveTracer.init(
          project="your-project",          # Or set HH_PROJECT environment variable
          test_mode=True                   # Or set HH_TEST_MODE=true environment variable
      )
      if tracer.test_mode:
          print("Running in test mode - no data will be sent")

Multi-Instance Architecture
---------------------------

The HoneyHiveTracer supports multiple independent instances for flexible workflow management:

**Environment Separation:**

.. code-block:: python

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-api-key",      # Or set HH_API_KEY environment variable
       project="my-project",        # Or set HH_PROJECT environment variable
       source="production"          # Or set HH_SOURCE environment variable
   )
   
   # Staging tracer
   staging_tracer = HoneyHiveTracer.init(
       api_key="staging-api-key",   # Or set HH_API_KEY environment variable
       project="my-project",        # Or set HH_PROJECT environment variable
       source="staging"             # Or set HH_SOURCE environment variable
   )
   
   # Development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-api-key",       # Or set HH_API_KEY environment variable
       project="my-project",        # Or set HH_PROJECT environment variable
       source="development",        # Or set HH_SOURCE environment variable
       test_mode=True               # Or set HH_TEST_MODE=true environment variable
   )

**Service-Based Separation:**

.. code-block:: python

   # Microservices architecture
   # Each service uses HH_API_KEY environment variable
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
   # All tracers use HH_API_KEY environment variable
   
   # Chat workflow tracer
   chat_tracer = HoneyHiveTracer.init(
       project="chat-service"
   )
   
   # Initialize instrumentor for chat workflow
   chat_instrumentor = OpenAIInstrumentor()
   chat_instrumentor.instrument(tracer_provider=chat_tracer.provider)
   
   # Analysis workflow tracer  
   analysis_tracer = HoneyHiveTracer.init(
       project="analysis-service"
   )
   
   # Initialize instrumentor for analysis workflow
   analysis_instrumentor = AnthropicInstrumentor()
   analysis_instrumentor.instrument(tracer_provider=analysis_tracer.provider)
   
   # Background tasks tracer (no LLM instrumentors needed)
   background_tracer = HoneyHiveTracer.init(
       project="background-tasks"
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
       api_key="your-key",  # Or set HH_API_KEY environment variable
       project="your-project"
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
       tracer = HoneyHiveTracer.init(
           api_key="potentially_invalid_key",  # Or set HH_API_KEY environment variable
           project="your-project"              # Or set HH_PROJECT environment variable
       )
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
   # Requires HH_API_KEY environment variable
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
   # Requires HH_API_KEY environment variable
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
   
   # Requires HH_API_KEY environment variable
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
   
   tracer = HoneyHiveTracer.init(project="your-project")  # Requires HH_API_KEY environment variable
   
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
- :doc:`../../tutorials/01-setup-first-tracer` - Basic tracing tutorial
- :doc:`../../tutorials/advanced-configuration` - Advanced configuration patterns
- :doc:`../../how-to/index` - Troubleshooting tracing issues (see Troubleshooting section)
- :doc:`../../explanation/concepts/tracing-fundamentals` - Tracing concepts and theory
- :doc:`../../explanation/architecture/overview` - Architecture overview and patterns