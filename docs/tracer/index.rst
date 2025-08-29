Tracing and OpenTelemetry
=========================

This section covers the tracing functionality and OpenTelemetry integration of the HoneyHive Python SDK.

OpenTelemetry Tracer
--------------------

.. automodule:: honeyhive.tracer.otel_tracer
   :members:
   :undoc-members:
   :show-inheritance:

Tracing Decorators
------------------

.. automodule:: honeyhive.tracer.decorators
   :members:
   :undoc-members:
   :show-inheritance:

Span Processor
--------------

.. automodule:: honeyhive.tracer.span_processor
   :members:
   :undoc-members:
   :show-inheritance:

HTTP Instrumentation
--------------------

.. automodule:: honeyhive.tracer.http_instrumentation
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Tracing
~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   
   # Initialize the tracer
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="my-app"
   )
   
   # Start a span
   with tracer.start_span("operation-name") as span:
       span.set_attribute("key", "value")
       # Your operation here

Decorator-based Tracing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.decorators import trace
   
   @trace
   def my_function():
       # This function will be automatically traced
       pass

OpenTelemetry Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   from opentelemetry import trace
   
   # Get the global tracer
   tracer = HoneyHiveTracer.get_instance()
   
   # Use with OpenTelemetry
   with trace.get_tracer(__name__).start_as_current_span("span-name"):
       # Your traced operation
       pass
