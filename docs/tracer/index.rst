Tracing and OpenTelemetry
=========================

This section covers the tracing functionality and OpenTelemetry integration of the HoneyHive Python SDK.

Overview
--------

The HoneyHive tracer has been completely refactored to support a modern multi-instance architecture, allowing you to create multiple independent tracer instances within the same runtime. This provides greater flexibility for managing different workflows, environments, and tracing configurations.

Key Features
~~~~~~~~~~~~

* **Multi-Instance Support**: Create multiple tracers for different workflows
* **Dynamic Session Naming**: Automatic session naming based on initialization file
* **Smart TracerProvider Management**: Integrates with existing OpenTelemetry providers
* **Enhanced Decorator Support**: Explicit tracer instance support in decorators
* **Independent Lifecycle Management**: Each tracer manages its own resources

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

Multi-Instance Architecture
---------------------------

The new architecture supports creating multiple independent tracer instances:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

      # Create production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-key",
       project="production-app",
       source="prod"
   )
   
   # Create development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-key",
       project="development-app",
       source="dev"
   )
   
   # Create testing tracer
   test_tracer = HoneyHiveTracer.init(
       api_key="test-key",
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
----------------------

Sessions are automatically named based on the file where the tracer is initialized:

.. code-block:: python

   # In file: src/my_app/main.py
   tracer = HoneyHiveTracer.init(api_key="key", project="project", source="source")
   # Session name will be: "main"

   # In file: src/my_app/processors/data_processor.py  
   tracer = HoneyHiveTracer.init(api_key="key", project="project", source="source")
   # Session name will be: "data_processor"

   # In file: src/my_app/api/endpoints.py
   tracer = HoneyHiveTracer.init(api_key="key", project="project", source="source")
   # Session name will be: "endpoints"

This provides better organization and makes it easier to identify which component generated specific traces.

TracerProvider Integration
--------------------------

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

Usage Examples
--------------

**Recommended: Use @trace with explicit tracer instance**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `@trace` decorator now supports explicit tracer instances for better multi-instance usage:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   # Explicit tracer instance (recommended)
   @trace(tracer=my_tracer, event_type="model", event_name="text_generation")
   def generate_text(prompt: str) -> str:
       return "Generated text"

   # Async function with explicit tracer
   @trace(tracer=my_tracer, event_type="model", event_name="async_text_generation")
   async def generate_text_async(prompt: str) -> str:
       return "Generated text async"

**Legacy: Global tracer support (deprecated)**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For backward compatibility, the decorator still supports global tracer usage:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   # Uses global tracer (not recommended for new code)
   @trace(event_type="model", event_name="text_generation")
   def generate_text(prompt: str) -> str:
       return "Generated text"

**Advanced: Use @atrace for async-only functions**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you specifically want to ensure a function is treated as async:

.. code-block:: python

   from honeyhive.tracer.decorators import atrace

   @atrace(tracer=my_tracer, event_type="llm", event_name="gpt4_completion")
   async def call_gpt4(prompt: str) -> str:
       response = await openai_client.chat.completions.create(...)
       return response.choices[0].message.content

Basic Tracing
~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   
   # Initialize the tracer (creates new instance)
   tracer = HoneyHiveTracer.init(
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
   
   # Pass tracer instance explicitly (recommended)
   @trace(tracer=my_tracer)
   def my_function():
       # This function will be automatically traced
       pass

OpenTelemetry Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   from opentelemetry import trace
   
   # Create tracer instance
   tracer = HoneyHiveTracer.init(
       api_key="key",
       project="project",
       source="source"
   )
   
   # Use with OpenTelemetry
   with trace.get_tracer(__name__).start_as_current_span("span-name"):
       # Your traced operation
       pass

Lifecycle Management
--------------------

Each tracer instance manages its own lifecycle:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Create tracer
   tracer = HoneyHiveTracer.init(api_key="key", project="project", source="source")

   # Use tracer
   with tracer.start_span("operation") as span:
       # Your operation
       pass

   # Shutdown when done (optional - will be cleaned up automatically)
   tracer.shutdown()

   # Create another tracer
   another_tracer = HoneyHiveTracer.init(api_key="key2", project="project2", source="source2")



**Key Benefits of Multi-Instance Architecture:**

✅ **Multiple Workflows**: Support different tracing configurations for different parts of your application
✅ **Environment Isolation**: Separate production, development, and testing tracing
✅ **Independent Lifecycles**: Each tracer manages its own resources and shutdown
✅ **Better Testing**: Easier to test with isolated tracer instances
✅ **Flexible Configuration**: Different API keys, projects, and sources per tracer
✅ **Modern Design**: Follows current best practices for dependency injection

**Key Benefits of @trace with Explicit Tracer:**

✅ **Explicit Dependencies**: Clear which tracer instance is being used
✅ **Better Testing**: Easier to mock and test with specific tracer instances
✅ **Multi-Instance Support**: Works seamlessly with the new architecture
✅ **Performance**: No global state lookups
✅ **Type Safety**: Better IDE support and type checking
