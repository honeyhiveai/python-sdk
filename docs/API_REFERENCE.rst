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

The main tracer class providing OpenTelemetry integration and session management. Designed with minimal dependencies to prevent conflicts in customer environments while supporting comprehensive LLM agent observability.

Primary Initialization (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   HoneyHiveTracer.init(
       api_key: Optional[str] = None,
       project: Optional[str] = None,
       source: str = "dev",
       session_name: Optional[str] = None,
       server_url: Optional[str] = None,
       disable_http_tracing: bool = True
   )

**Parameters:**

* ``api_key``: HoneyHive API key (required if not in environment)
* ``project``: Project name (defaults to environment or "default")
* ``source``: Source environment (defaults to "dev" per official docs)
* ``session_name``: Custom session name (auto-generated if not provided)
* ``server_url``: Server URL for self-hosted deployments (optional)
* ``disable_http_tracing``: Whether to disable HTTP tracing (defaults to True)

**Dependency Philosophy:**

The ``instrumentors`` parameter follows our "bring your own instrumentor" approach. This prevents dependency conflicts by allowing you to choose exactly what gets instrumented rather than forcing specific LLM library versions.

**Example:**

.. code-block:: python

   # Official SDK pattern (recommended)
   HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # For self-hosted deployments
   HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       server_url="https://custom-honeyhive-server.com"
   )

   # With HTTP tracing enabled
   HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       disable_http_tracing=False
   )

Enhanced Initialization (All Features Available)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   HoneyHiveTracer.init(
       api_key: Optional[str] = None,
       project: Optional[str] = None,
       source: str = "dev",
       test_mode: bool = False,
       session_name: Optional[str] = None,
       server_url: Optional[str] = None,
       instrumentors: Optional[list] = None,
       disable_http_tracing: bool = True,
   )

**Parameters:**

* ``api_key``: HoneyHive API key (required if not in environment)
* ``project``: Project name (defaults to environment or "default")
* ``source``: Source environment (defaults to "dev")
* ``test_mode``: Enable test mode (defaults to False)
* ``session_name``: Custom session name (auto-generated if not provided)
* ``server_url``: Custom server URL for self-hosted deployments
* ``instrumentors``: List of OpenInference instrumentors to integrate
* ``disable_http_tracing``: Whether to disable HTTP tracing (defaults to True)

**Example:**

.. code-block:: python

   # Enhanced initialization with all features available
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       test_mode=True,  # Test mode support
       instrumentors=[OpenAIInstrumentor()],  # Auto-integration
       disable_http_tracing=True  # Performance control
   )

.. note::

   The ``init()`` method now supports ALL constructor features and is the recommended way to initialize the tracer. It follows the official HoneyHive SDK documentation pattern and provides the same functionality as the constructor.

Environment-Based Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use environment variables for configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   # Set environment variables
   os.environ["HH_API_KEY"] = "your-api-key"
   os.environ["HH_PROJECT"] = "my-project"
   os.environ["HH_SOURCE"] = "production"

   # Initialize tracer (automatically reads environment)
   tracer = HoneyHiveTracer.init()

Conditional Initialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Initialize based on environment or configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   def create_tracer():
       """Create tracer based on environment."""
       
       if os.getenv("ENVIRONMENT") == "production":
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="production"
           )
       else:
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="development",
               test_mode=True
           )

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
