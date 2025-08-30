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

force_flush
~~~~~~~~~~~

**Force immediate flushing of all pending spans and telemetry data.**

The ``force_flush`` method ensures that all buffered spans and telemetry data are immediately sent to their destinations, rather than waiting for automatic batching.

**Function Signature:**

.. code-block:: python

   def force_flush(self, timeout_millis: float = 30000) -> bool

**Parameters:**

* ``timeout_millis``: Maximum time to wait for flush completion in milliseconds (default: 30000ms/30 seconds)

**Returns:**

* ``bool``: True if flush completed successfully within timeout, False otherwise

**Usage Examples:**

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="your-project")
   
   # Flush with default timeout (30 seconds)
   success = tracer.force_flush()
   if success:
       print("All spans flushed successfully")
   else:
       print("Flush timeout or error occurred")
   
   # Flush with custom timeout (5 seconds)
   success = tracer.force_flush(timeout_millis=5000)
   
   # Use before critical operations
   with tracer.start_span("critical_operation"):
       perform_work()
   
   # Ensure spans are sent before continuing
   tracer.force_flush()

**Integration with OpenTelemetry:**

The ``force_flush`` method integrates with:

* **TracerProvider**: Calls the provider's ``force_flush`` if available
* **Span Processors**: Flushes all attached span processors including batch processors
* **HoneyHive Processor**: Validates processor state and ensures consistency

**Best Practices:**

* Use ``force_flush`` before application shutdown
* Call before critical checkpoints where you need guaranteed span delivery
* Consider timeout values based on your network conditions
* Monitor return values to detect flush failures

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

API Configuration
~~~~~~~~~~~~~~~~~

.. list-table:: API Configuration
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_API_KEY``
     - HoneyHive API key
     - None
     - **Yes**
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

Tracing Configuration
~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Tracing Configuration
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_DISABLE_TRACING``
     - Disable tracing
     - ``false``
     - No
   * - ``HH_DISABLE_HTTP_TRACING``
     - Disable HTTP instrumentation
     - ``false``
     - No
   * - ``HH_TEST_MODE``
     - Enable test mode
     - ``false``
     - No
   * - ``HH_DEBUG_MODE``
     - Enable debug mode
     - ``false``
     - No

OTLP Configuration
~~~~~~~~~~~~~~~~~~

.. list-table:: OTLP Configuration
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_OTLP_ENABLED``
     - Enable OTLP export
     - ``true``
     - No
   * - ``HH_OTLP_ENDPOINT``
     - Custom OTLP endpoint
     - Auto-detected
     - No
   * - ``HH_OTLP_HEADERS``
     - OTLP headers (JSON format)
     - None
     - No

HTTP Client Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Connection Pool Settings
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_MAX_CONNECTIONS``
     - Maximum connections in pool
     - ``10``
     - No
   * - ``HH_MAX_KEEPALIVE_CONNECTIONS``
     - Maximum keepalive connections
     - ``20``
     - No
   * - ``HH_KEEPALIVE_EXPIRY``
     - Keepalive expiry time (seconds)
     - ``30.0``
     - No
   * - ``HH_POOL_TIMEOUT``
     - Pool timeout (seconds)
     - ``10.0``
     - No

.. list-table:: Rate Limiting
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_RATE_LIMIT_CALLS``
     - Maximum calls per time window
     - ``100``
     - No
   * - ``HH_RATE_LIMIT_WINDOW``
     - Rate limit time window (seconds)
     - ``60.0``
     - No

.. list-table:: Proxy Settings
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_HTTP_PROXY``
     - HTTP proxy URL
     - None
     - No
   * - ``HH_HTTPS_PROXY``
     - HTTPS proxy URL
     - None
     - No
   * - ``HH_NO_PROXY``
     - Hosts to bypass proxy (comma-separated)
     - None
     - No

.. list-table:: SSL and Redirects
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_VERIFY_SSL``
     - Verify SSL certificates
     - ``true``
     - No
   * - ``HH_FOLLOW_REDIRECTS``
     - Follow HTTP redirects
     - ``true``
     - No

Experiment Harness Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Experiment Configuration
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_EXPERIMENT_ID``
     - Unique experiment identifier
     - None
     - No
   * - ``HH_EXPERIMENT_NAME``
     - Experiment name
     - None
     - No
   * - ``HH_EXPERIMENT_VARIANT``
     - Experiment variant/treatment
     - None
     - No
   * - ``HH_EXPERIMENT_GROUP``
     - Experiment group/cohort
     - None
     - No
   * - ``HH_EXPERIMENT_METADATA``
     - Experiment metadata/tags (JSON)
     - None
     - No

SDK Configuration
~~~~~~~~~~~~~~~~~

.. list-table:: SDK Configuration
   :header-rows: 1
   :widths: 25 35 20 20

   * - Variable
     - Description
     - Default
     - Required
   * - ``HH_TIMEOUT``
     - Request timeout in seconds
     - ``30.0``
     - No
   * - ``HH_MAX_RETRIES``
     - Maximum retry attempts
     - ``3``
     - No

Standard Environment Variable Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK also supports standard environment variable names for better integration with existing infrastructure:

.. list-table:: Standard Alternatives
   :header-rows: 1
   :widths: 25 50 25

   * - HoneyHive Variable
     - Standard Alternatives
     - Category
   * - ``HH_HTTP_PROXY``
     - ``HTTP_PROXY``, ``http_proxy``
     - Proxy
   * - ``HH_HTTPS_PROXY``
     - ``HTTPS_PROXY``, ``https_proxy``
     - Proxy
   * - ``HH_NO_PROXY``
     - ``NO_PROXY``, ``no_proxy``
     - Proxy
   * - ``HH_EXPERIMENT_ID``
     - ``EXPERIMENT_ID``, ``MLFLOW_EXPERIMENT_ID``, ``WANDB_RUN_ID``
     - Experiment
   * - ``HH_EXPERIMENT_NAME``
     - ``EXPERIMENT_NAME``, ``MLFLOW_EXPERIMENT_NAME``, ``WANDB_PROJECT``
     - Experiment
   * - ``HH_OTLP_ENDPOINT``
     - ``OTEL_EXPORTER_OTLP_ENDPOINT``
     - OTLP
   * - ``HH_OTLP_HEADERS``
     - ``OTEL_EXPORTER_OTLP_HEADERS``
     - OTLP

Configuration Precedence
~~~~~~~~~~~~~~~~~~~~~~~~

Configuration values are resolved in the following order (highest to lowest priority):

1. **Constructor parameters** (highest priority)
2. **HoneyHive-specific environment variables** (``HH_*``)
3. **Standard environment variables** (e.g., ``HTTP_*``, ``EXPERIMENT_*``)
4. **Default values** (lowest priority)

Usage Notes
~~~~~~~~~~~

- Boolean environment variables accept: ``true``, ``false``, ``1``, ``0``, ``yes``, ``no``, ``on``, ``off``
- Numeric environment variables are automatically converted to appropriate types
- JSON environment variables (like ``HH_EXPERIMENT_METADATA``) support multiple formats
- The SDK gracefully handles invalid environment variable values by falling back to defaults

Evaluation Framework
--------------------

The evaluation framework provides comprehensive tools for evaluating LLM outputs with built-in and custom evaluators.

**Key Features:**

- Built-in evaluators (exact match, F1 score, length, semantic similarity)
- Custom evaluator support with ``BaseEvaluator`` class
- Threading and parallel processing capabilities
- Decorator pattern for easy integration
- API integration for storing evaluation results
- Batch processing for large datasets

**Environment Variables:**

- ``HH_EVALUATION_MAX_WORKERS`` - Maximum parallel workers (default: 4)
- ``HH_EVALUATION_TIMEOUT`` - Evaluation timeout in seconds (default: 30)
- ``HH_EVALUATION_BATCH_SIZE`` - Default batch size (default: 100)

**API Reference:**

.. automodule:: honeyhive.evaluation.evaluators
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Tracing and OpenTelemetry
-------------------------

The tracing system provides multi-instance tracer support, OpenTelemetry integration, and comprehensive span enrichment capabilities.

**Key Features:**

- Multi-instance tracer architecture for environment isolation
- Dynamic session naming based on initialization file
- Smart TracerProvider management with existing OTEL providers
- Enhanced decorator support with explicit tracer instances
- Dual enrichment system (span-level and session-level)
- HTTP instrumentation for automatic request tracing

**API Reference:**

OpenTelemetry Tracer
~~~~~~~~~~~~~~~~~~~~

.. automodule:: honeyhive.tracer.otel_tracer
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Tracing Decorators
~~~~~~~~~~~~~~~~~~

.. automodule:: honeyhive.tracer.decorators
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Span Processor
~~~~~~~~~~~~~~

.. automodule:: honeyhive.tracer.span_processor
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

HTTP Instrumentation
~~~~~~~~~~~~~~~~~~~~

.. automodule:: honeyhive.tracer.http_instrumentation
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Additional Resources
--------------------

Utilities
~~~~~~~~~

The SDK includes several utility classes for advanced use cases:

- **BaggageDict** - OpenTelemetry baggage management
- **DotDict** - Dictionary with dot notation access  
- **Cache** - Configurable caching system
- **ConnectionPool** - HTTP connection pooling
- **Logger** - Structured logging with HoneyHive formatting
- **RetryConfig** - Configurable retry strategies

For detailed utility documentation, see the source code in ``src/honeyhive/utils/``.

Data Models
~~~~~~~~~~~

The SDK provides 50+ auto-generated data models for API interactions, including:

- **Session Models** - ``SessionStartRequest``, ``SessionPropertiesBatch``
- **Event Models** - ``Event``, ``CreateEventRequest``, ``EventFilter``
- **Metric Models** - ``Metric``, ``MetricEdit``, ``Threshold``
- **Dataset Models** - ``Dataset``, ``CreateDatasetRequest``, ``Datapoint``
- **Project Models** - ``Project``, ``CreateProjectRequest``
- **Experiment Models** - ``EvaluationRun``, ``CreateRunRequest``

All models are available from ``honeyhive.models`` and include full type hints and validation.

Examples
~~~~~~~~

The ``examples/`` directory contains 12+ practical examples:

- **Basic Usage** - ``basic_usage.py``, ``tracing_decorators.py``
- **Provider Integration** - ``simple_openai_integration.py``, ``simple_anthropic_integration.py``
- **Advanced Patterns** - ``advanced_usage.py``
- **Evaluation** - ``evaluation_example.py`` (comprehensive)

See the `examples documentation <examples/README.html>`_ for detailed usage patterns.
