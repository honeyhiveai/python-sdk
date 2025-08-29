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
   DYNAMIC_TRACE_DECORATOR
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

Features
========

* **OpenTelemetry Integration**: Full support for distributed tracing
* **Comprehensive API Client**: Complete coverage of HoneyHive API endpoints
* **Evaluation Framework**: Built-in tools for AI model evaluation
* **Dynamic Tracing**: Automatic instrumentation and tracing decorators
* **Async Support**: Full asynchronous operation support
* **Type Safety**: Complete type hints and Pydantic model validation

For more information, see the :doc:`FEATURE_LIST` and :doc:`IMPLEMENTATION_GUIDE`.
