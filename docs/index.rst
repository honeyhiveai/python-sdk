Welcome to HoneyHive Python SDK's documentation!
================================================

HoneyHive is a comprehensive Python SDK for AI observability, tracing, and evaluation. This SDK provides seamless integration with OpenTelemetry for distributed tracing, comprehensive API client libraries, and powerful evaluation tools.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   FEATURE_LIST
   API_REFERENCE
   IMPLEMENTATION_GUIDE
   OPENINFERENCE_INTEGRATION
   examples/README

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/index
   tracer/index
   evaluation/index
   utils/index

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   examples/BASIC_USAGE_PATTERNS
   examples/ADVANCED_PATTERNS
   examples/PRACTICAL_EXAMPLES

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Quick Start
===========

Install the SDK:

.. code-block:: bash

   pip install honeyhive

Basic usage:

.. code-block:: python

   from honeyhive import HoneyHive
   
   # Initialize the client
   client = HoneyHive(api_key="your-api-key")
   
   # Start a session
   session = client.sessions.start_session(
       project="my-project",
       session_name="my-session",
       source="my-app"
   )
   
   # Create an event
   event = client.events.create_event(
       project="my-project",
       source="my-app",
       event_name="user-interaction",
       event_type="tool",
       config={"model": "gpt-4"},
       inputs={"prompt": "Hello, world!"}
   )

**Tracing with @trace (Recommended)**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `@trace` decorator is the **preferred choice** for automatic tracing:

.. code-block:: python

   from honeyhive.tracer.decorators import trace
   
   @trace(event_type="model", event_name="text_generation")
   def generate_text(prompt: str) -> str:
       # This function is automatically traced
       return "Generated text"
   
   @trace(event_type="model", event_name="async_generation")
   async def generate_text_async(prompt: str) -> str:
       # Async functions work seamlessly too!
       return "Generated text async"

Features
========

* **OpenTelemetry Integration**: Full support for distributed tracing
* **Comprehensive API Client**: Complete coverage of HoneyHive API endpoints
* **Evaluation Framework**: Built-in tools for AI model evaluation
* **Smart Tracing**: **@trace decorator** automatically handles sync/async functions
* **Async Support**: Full asynchronous operation support
* **Type Safety**: Complete type hints and Pydantic model validation

For more information, see the :doc:`FEATURE_LIST` and :doc:`IMPLEMENTATION_GUIDE`.
