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
