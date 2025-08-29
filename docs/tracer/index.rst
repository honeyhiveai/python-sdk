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

**Recommended: Use @trace for most cases**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `@trace` decorator is the **preferred choice** for most tracing needs. It automatically detects whether your function is synchronous or asynchronous and applies the appropriate wrapper:

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

**Advanced: Use @atrace for async-only functions**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you specifically want to ensure a function is treated as async:

.. code-block:: python

   from honeyhive.tracer.decorators import atrace

   @atrace(event_type="llm", event_name="gpt4_completion")
   async def call_gpt4(prompt: str) -> str:
       response = await openai_client.chat.completions.create(...)
       return response.choices[0].message.content

**Legacy: @dynamic_trace (not recommended)**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `@dynamic_trace` decorator is available for backward compatibility but is **not recommended** for new code. Use `@trace` instead as it provides the same functionality with better performance and cleaner code.

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

**Key Benefits of @trace:**

✅ **Single decorator** works for both sync and async  
✅ **Automatic detection** - no need to remember which decorator to use  
✅ **Consistent API** - same parameters and behavior for both  
✅ **Performance optimized** - no unnecessary async overhead for sync functions  
✅ **Error handling** - proper exception handling for both patterns  
✅ **Recommended approach** - preferred by the HoneyHive team
