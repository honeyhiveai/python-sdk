API Reference
=============

Complete API reference for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Core Classes
------------

HoneyHiveTracer
~~~~~~~~~~~~~~~

The main tracer class providing OpenTelemetry integration and session management. Now supports multiple independent instances within the same runtime for flexible workflow management.

Primary Initialization (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   HoneyHiveTracer.init(
       api_key: Optional[str] = None,
       project: Optional[str] = None,
       source: str = "production",
       test_mode: bool = False,
       session_name: Optional[str] = None,
       server_url: Optional[str] = None,
       instrumentors: Optional[list] = None,
       disable_http_tracing: bool = True
   )

**Parameters:**

* ``api_key``: HoneyHive API key (required if not in environment)
* ``project``: Project name (defaults to environment or "default")
* ``source``: Source environment (defaults to "production")
* ``test_mode``: Enable test mode (defaults to False)
* ``session_name``: Custom session name (auto-generated if not provided)
* ``server_url``: Server URL for self-hosted deployments (optional)
* ``instrumentors``: List of OpenInference instrumentors to integrate
* ``disable_http_tracing``: Whether to disable HTTP tracing (defaults to True)

**Key Features:**

* **Multi-Instance Support**: Create multiple independent tracers
* **Dynamic Session Naming**: Automatic session naming based on initialization file
* **Smart TracerProvider Management**: Integrates with existing OpenTelemetry providers
* **Thread Safety**: Each instance is thread-safe and independent

**Dependency Philosophy:**

The ``instrumentors`` parameter follows our "bring your own instrumentor" approach. This prevents dependency conflicts by allowing you to choose exactly what gets instrumented rather than forcing specific LLM library versions.

**Example:**

.. code-block:: python

   # Multi-instance pattern (recommended)
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # For self-hosted deployments
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       server_url="https://custom-honeyhive-server.com"
   )

   # With HTTP tracing enabled
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       disable_http_tracing=False
   )

   # With OpenInference instrumentors
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       instrumentors=[OpenAIInstrumentor()]
   )

Multiple Tracer Instances
^^^^^^^^^^^^^^^^^^^^^^^^^

Create multiple tracers for different workflows and environments:

.. code-block:: python

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-api-key",
       project="production-app",
       source="prod"
   )
   
   # Development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-api-key",
       project="development-app",
       source="dev"
   )
   
   # Testing tracer
   test_tracer = HoneyHiveTracer.init(
       api_key="test-api-key",
       project="testing-app",
       source="test"
   )
   
   # Each tracer operates independently
   with prod_tracer.start_span("prod-operation") as span:
       # Production tracing
       pass
   
   with dev_tracer.start_span("dev-operation") as span:
       # Development tracing
       pass

Dynamic Session Naming
^^^^^^^^^^^^^^^^^^^^^^

Sessions are automatically named based on the file where the tracer is initialized:

.. code-block:: python

   # In file: src/my_app/main.py
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   # Session name will be: "main"

   # In file: src/my_app/processors/data_processor.py  
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   # Session name will be: "data_processor"

   # In file: src/my_app/api/endpoints.py
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   # Session name will be: "endpoints"

TracerProvider Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^

The tracer intelligently manages OpenTelemetry TracerProvider instances:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry import trace

   # Check if a provider already exists
   existing_provider = trace.get_tracer_provider()

   # Create tracer - will integrate with existing provider if available
   tracer = HoneyHiveTracer.init(
       api_key="key",
       project="project",
       source="source"
   )

   # The tracer automatically detects and integrates with existing providers
   # or creates a new one if none exists

Span and Session Enrichment
----------------------------

enrich_span
~~~~~~~~~~~

**Unified span enrichment function with multiple usage patterns and full backwards compatibility.**

The ``enrich_span`` function provides the modern, recommended approach for enriching OpenTelemetry spans with HoneyHive-specific attributes, metadata, and experiment data.

**Function Signature:**

.. code-block:: python

   def enrich_span(
       *args: Any,
       metadata: Optional[Dict[str, Any]] = None,
       metrics: Optional[Dict[str, Any]] = None,
       attributes: Optional[Dict[str, Any]] = None,
       event_type: Optional[str] = None,
       event_name: Optional[str] = None,
       inputs: Optional[Dict[str, Any]] = None,
       outputs: Optional[Dict[str, Any]] = None,
       config_data: Optional[Dict[str, Any]] = None,
       feedback: Optional[Dict[str, Any]] = None,
       error: Optional[Exception] = None,
       event_id: Optional[str] = None,
       tracer: Optional[HoneyHiveTracer] = None,
       **kwargs: Any,
   ) -> Union[contextmanager, bool]

**Parameters:**

* ``*args``: Positional arguments for backwards compatibility (event_type, metadata)
* ``metadata``: Span metadata dictionary
* ``metrics``: Performance metrics dictionary  
* ``attributes``: Additional span attributes
* ``event_type``: Type of traced event (e.g., "llm_inference", "preprocessing")
* ``event_name``: Name of the traced event
* ``inputs``: Input data for the event
* ``outputs``: Output data for the event (stored as ``honeyhive.span.outputs`` using ``_set_span_attributes``)
* ``config_data``: Configuration data including experiment parameters
* ``feedback``: User feedback data
* ``error``: Error information if applicable (stored as ``honeyhive.span.error`` using ``_set_span_attributes``)
* ``event_id``: Unique event identifier
* ``tracer``: HoneyHiveTracer instance (required for direct calls)
* ``**kwargs``: Additional attributes set with "honeyhive_" prefix

**Returns:**

* **Context Manager**: When used as ``with enrich_span(...):``
* **Boolean**: When used as direct method call (indicates success)

**Import Paths:**

.. code-block:: python

   # All equivalent - use any based on preference:
   from honeyhive.tracer import enrich_span                    # Public API (recommended)
   from honeyhive.tracer.otel_tracer import enrich_span        # Main implementation  
   from honeyhive.tracer.decorators import enrich_span         # Delegates to main

**Usage Patterns:**

*Context Manager (Recommended):*

.. code-block:: python

   # Enhanced pattern with rich attributes
   with enrich_span(
       event_type="llm_inference",
       event_name="gpt4_completion",
       inputs={"prompt": "What is AI?", "temperature": 0.7},
       metadata={"model": "gpt-4", "version": "2024-03"},
       metrics={"expected_tokens": 150},
       config_data={
           "experiment_id": "exp-123",
           "experiment_name": "temperature_test",
           "experiment_variant": "control"
       }
   ):
       response = llm_client.complete(prompt)

   # Basic pattern (backwards compatible)
   with enrich_span("user_session", {"user_id": "123", "action": "query"}):
       process_user_request()

*Tracer Instance Method:*

.. code-block:: python

   # Context manager pattern
   with tracer.enrich_span("operation_name", {"step": "preprocessing"}):
       preprocess_data()
   
   # Direct method call
   success = tracer.enrich_span(
       metadata={"stage": "postprocessing"},
       metrics={"latency": 0.1, "tokens": 150}
   )

*Global Function:*

.. code-block:: python

   # Direct call with tracer parameter
   success = enrich_span(
       metadata={"operation": "batch_processing"},
       tracer=my_tracer
   )

**Experiment Support:**

Automatic experiment attribute setting via ``config_data``:

.. code-block:: python

   with enrich_span(
       event_type="ab_test",
       config_data={
           "experiment_id": "exp-789",
           "experiment_name": "model_comparison",
           "experiment_variant": "gpt4_turbo",
           "experiment_group": "B",
           "experiment_metadata": {"version": "1.2"}
       }
   ):
       # Automatically sets honeyhive_experiment_* attributes
       run_experiment()

**Outputs and Error Handling:**

The ``outputs`` and ``error`` parameters provide comprehensive data capture and error tracking:

.. code-block:: python

   # Success case with outputs
   with enrich_span(
       event_type="data_processing",
       inputs={"dataset": "user_data.csv", "rows": 1000},
       outputs={"processed_rows": 950, "skipped_rows": 50, "format": "json"},
       metadata={"processor_version": "2.1.0"}
   ):
       result = process_dataset()

   # Error handling case
   try:
       with enrich_span(
           event_type="model_inference",
           inputs={"prompt": "What is AI?", "model": "gpt-4"},
           error=None  # Will be updated if error occurs
       ) as span:
           response = model.generate()
           # Update with outputs on success
           span.outputs = {"response": response, "tokens": len(response.split())}
   except Exception as e:
       # Error is automatically captured in span attributes as 'honeyhive.span.error'
       raise

   # Direct method with error
   inference_error = ValueError("Model not available")
   success = tracer.enrich_span(
       metadata={"operation": "model_call"},
       outputs=None,  # No outputs due to error
       error=inference_error  # Stored as 'honeyhive.span.error'
   )

enrich_session
~~~~~~~~~~~~~~

**Session-level enrichment for backend persistence in HoneyHive.**

Use ``enrich_session`` when you need to store session-level data directly in the HoneyHive backend for immediate availability in the UI.

**Function Signature:**

.. code-block:: python

   def enrich_session(
       self,
       session_id: Optional[str] = None,
       metadata: Optional[Dict[str, Any]] = None,
       feedback: Optional[Dict[str, Any]] = None,
       metrics: Optional[Dict[str, Any]] = None,
       config: Optional[Dict[str, Any]] = None,
       inputs: Optional[Dict[str, Any]] = None,
       outputs: Optional[Dict[str, Any]] = None,
       user_properties: Optional[Dict[str, Any]] = None,
   ) -> bool

**Parameters:**

* ``session_id``: Session ID to enrich (defaults to tracer's session)
* ``metadata``: Session metadata
* ``feedback``: User feedback and ratings
* ``metrics``: Computed metrics and performance data
* ``config``: Session configuration (model settings, etc.)
* ``inputs``: Session inputs
* ``outputs``: Session outputs  
* ``user_properties``: User-specific properties

**Returns:**

* ``bool``: Whether the enrichment was successful

**Usage:**

.. code-block:: python

   success = tracer.enrich_session(
       session_id="session-123",  # Optional
       metadata={
           "user_id": "user-456",
           "conversation_type": "support",
           "language": "en"
       },
       feedback={
           "rating": 5,
           "helpful": True,
           "feedback_text": "Very helpful response"
       },
       metrics={
           "total_tokens": 1500,
           "duration": 2.5,
           "api_calls": 3
       },
       config={
           "model": "gpt-4",
           "temperature": 0.7,
           "max_tokens": 500
       },
       user_properties={
           "subscription_tier": "premium",
           "region": "us-west"
       }
   )

**When to Use:**

.. list-table:: enrich_span vs enrich_session
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - enrich_span
     - enrich_session  
   * - **Scope**
     - Span-level enrichment
     - Session-level enrichment
   * - **Target**
     - OpenTelemetry spans
     - HoneyHive backend API
   * - **Usage Patterns**
     - Context manager + Direct calls
     - Direct method call only
   * - **Dependencies**
     - No session_id required
     - Requires active session_id
   * - **Data Persistence**
     - Local span attributes
     - Backend storage
   * - **Availability**
     - Exported via OTEL pipeline
     - Immediately in HoneyHive UI
   * - **Recommended For**
     - Most tracing scenarios
     - User feedback collection

Tracing Decorators
------------------

@trace (Recommended)
~~~~~~~~~~~~~~~~~~~~

The ``@trace`` decorator is the **preferred choice** for most tracing needs. It automatically detects whether your function is synchronous or asynchronous and applies the appropriate wrapper:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   # Sync function - automatically wrapped with sync wrapper
   @trace(event_type="model", event_name="text_generation")
   def generate_text(prompt: str) -> str:
       return "Generated text"

   # Async function - automatically wrapped with async wrapper  
   @trace(event_type="model", event_name="async_text_generation")
   async def generate_text_async(prompt: str) -> str:
       return "Generated text async"

   # Both work seamlessly with the same decorator!
   # No need to remember which decorator to use

@atrace (Async-Only)
~~~~~~~~~~~~~~~~~~~~

If you specifically want to ensure a function is treated as async:

.. code-block:: python

   from honeyhive.tracer.decorators import atrace

   @atrace(event_type="llm", event_name="gpt4_completion")
   async def call_gpt4(prompt: str) -> str:
       response = await openai_client.chat.completions.create(...)
       return response.choices[0].message.content

API Client
----------

HoneyHive
~~~~~~~~~

The main API client for interacting with HoneyHive services.

.. code-block:: python

   from honeyhive.api.client import HoneyHive

   client = HoneyHive(
       api_key="your-api-key",
       base_url="https://api.honeyhive.ai"
   )

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Configuration via environment variables.

.. list-table:: Environment Variables
   :header-rows: 1
   :widths: 20 40 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_API_KEY``
     - HoneyHive API key
     - None
     - Yes
   * - ``HH_API_URL``
     - API base URL
     - ``https://api.honeyhive.ai``
     - No
   * - ``HH_PROJECT``
     - Project name
     - ``default``
     - No
   * - ``HH_SOURCE``
     - Source environment
     - ``production``
     - No
   * - ``HH_TEST_MODE``
     - Enable test mode
     - ``false``
     - No
   * - ``HH_DISABLE_TRACING``
     - Disable tracing
     - ``false``
     - No
   * - ``HH_DISABLE_HTTP_TRACING``
     - Disable HTTP instrumentation
     - ``false``
     - No
   * - ``HH_OTLP_ENABLED``
     - Enable OTLP export
     - ``true``
     - No

Utilities
---------

Utility Functions
~~~~~~~~~~~~~~~~~

Various utility functions and helpers.

Connection Pool
~~~~~~~~~~~~~~~

HTTP connection pooling for efficient API communication.

Models
------

Data Models
~~~~~~~~~~~

Generated data models for API requests and responses.

Examples
--------

Usage Examples
~~~~~~~~~~~~~~

Basic usage examples and common patterns.
