Utilities Reference
===================

Complete reference for utility classes and helper functions.

.. contents:: Table of Contents
   :local:
   :depth: 2

Caching
-------

Cache
~~~~~

.. autoclass:: honeyhive.utils.cache.Cache
   :members:
   :undoc-members:
   :show-inheritance:

FunctionCache
~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.cache.FunctionCache
   :members:
   :undoc-members:
   :show-inheritance:

AsyncFunctionCache
~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.cache.AsyncFunctionCache
   :members:
   :undoc-members:
   :show-inheritance:

CacheEntry
~~~~~~~~~~

.. autoclass:: honeyhive.utils.cache.CacheEntry
   :members:
   :undoc-members:
   :show-inheritance:

Connection Pooling
------------------

ConnectionPool
~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.connection_pool.ConnectionPool
   :members:
   :undoc-members:
   :show-inheritance:

PooledHTTPClient
~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.connection_pool.PooledHTTPClient
   :members:
   :undoc-members:
   :show-inheritance:

PooledAsyncHTTPClient
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.connection_pool.PooledAsyncHTTPClient
   :members:
   :undoc-members:
   :show-inheritance:

Data Structures
---------------

DotDict
~~~~~~~

.. autoclass:: honeyhive.utils.dotdict.DotDict
   :members:
   :undoc-members:
   :show-inheritance:

BaggageDict
~~~~~~~~~~~

.. autoclass:: honeyhive.utils.baggage_dict.BaggageDict
   :members:
   :undoc-members:
   :show-inheritance:

Retry Configuration
-------------------

RetryConfig
~~~~~~~~~~~

.. autoclass:: honeyhive.utils.retry.RetryConfig
   :members:
   :undoc-members:
   :show-inheritance:

Logging
-------

HoneyHiveLogger
~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.logger.HoneyHiveLogger
   :members:
   :undoc-members:
   :show-inheritance:

get_logger
~~~~~~~~~~

.. autofunction:: honeyhive.utils.logger.get_logger

Distributed Tracing (v1.0+)
----------------------------

Context Propagation Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These functions enable distributed tracing by propagating trace context across service boundaries via HTTP headers.

inject_context_into_carrier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: honeyhive.tracer.processing.context.inject_context_into_carrier

Adds OpenTelemetry trace context (trace ID, span ID, baggage) to a dictionary (typically HTTP headers) for propagation to downstream services.

**Example:**

.. code-block:: python

   from honeyhive.tracer.processing.context import inject_context_into_carrier
   import requests
   
   # Inject trace context into HTTP headers
   headers = {"Content-Type": "application/json"}
   inject_context_into_carrier(headers, tracer)
   
   # Send request with distributed trace context
   response = requests.post(
       "http://downstream-service/api/endpoint",
       json=data,
       headers=headers  # Trace context propagates here
   )

extract_context_from_carrier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: honeyhive.tracer.processing.context.extract_context_from_carrier

Extracts OpenTelemetry trace context from a dictionary (typically HTTP headers) received from an upstream service.

**Example:**

.. code-block:: python

   from flask import request
   from honeyhive.tracer.processing.context import extract_context_from_carrier
   from opentelemetry import context
   
   @app.route("/api/endpoint", methods=["POST"])
   def endpoint():
       # Extract trace context from incoming headers
       incoming_context = extract_context_from_carrier(dict(request.headers), tracer)
       
       # Attach context so spans become children of parent trace
       if incoming_context:
           token = context.attach(incoming_context)
       
       try:
           # Your business logic here
           result = do_work()
           return jsonify(result)
       finally:
           if incoming_context:
               context.detach(token)

with_distributed_trace_context (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: honeyhive.tracer.processing.context.with_distributed_trace_context

**New in v1.0+:** Simplified context manager for server-side distributed tracing that handles extraction, baggage parsing, and context attachment automatically.

**This is the recommended approach for modern Python applications.**

**Advantages:**

- ✅ **Concise**: 1 line vs 65 lines of boilerplate
- ✅ **Thread-safe**: Automatic context isolation per request
- ✅ **Automatic cleanup**: Context detached even on exceptions
- ✅ **Baggage handling**: Automatically extracts and preserves ``session_id``, ``project``, ``source``
- ✅ **Works with async**: Handles ``asyncio.run()`` edge cases

**Example:**

.. code-block:: python

   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer
   from honeyhive.tracer.processing.context import with_distributed_trace_context
   
   tracer = HoneyHiveTracer.init(
       project="distributed-app",
       source="api-service"
   )
   
   app = Flask(__name__)
   
   @app.route("/api/process", methods=["POST"])
   def process():
       """Server endpoint with simplified distributed tracing."""
       
       # Single line replaces ~65 lines of context management
       with with_distributed_trace_context(dict(request.headers), tracer):
           # All spans created here automatically:
           # - Use the client's session_id
           # - Become children of the parent trace
           # - Inherit the client's project and source
           
           with tracer.start_span("process_request") as span:
               data = request.get_json()
               result = process_data(data)
               return jsonify(result)

**Works seamlessly with the @trace decorator:**

.. code-block:: python

   from honeyhive import trace
   
   @app.route("/api/endpoint", methods=["POST"])
   def endpoint():
       with with_distributed_trace_context(dict(request.headers), tracer):
           return handle_request()
   
   @trace(event_type="chain")
   def handle_request():
       # Decorator automatically uses the distributed context
       return {"status": "success"}

.. note::
   The ``@trace`` decorator in v1.0+ preserves existing baggage from distributed traces, so you don't need to manually set ``session_id`` or other baggage items inside decorated functions.

**For async functions with asyncio.run():**

If you need to use ``asyncio.run()`` inside your handler, you'll need to re-attach the context in the async function since ``asyncio.run()`` creates a new event loop:

.. code-block:: python

   from opentelemetry import context
   
   @app.route("/api/async-endpoint", methods=["POST"])
   def async_endpoint():
       with with_distributed_trace_context(dict(request.headers), tracer) as ctx:
           async def process():
               # Re-attach context in new event loop
               token = context.attach(ctx)
               try:
                   # Your async code here
                   result = await async_operation()
                   return result
               finally:
                   context.detach(token)
           
           return jsonify(asyncio.run(process()))

See Also
--------

- :doc:`client-apis` - API client reference
- :doc:`/reference/configuration/config-options` - Configuration options
- :doc:`/tutorials/06-distributed-tracing` - Distributed tracing tutorial

