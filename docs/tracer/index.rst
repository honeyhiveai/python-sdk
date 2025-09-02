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

Architecture
------------

The HoneyHive tracing system follows a layered architecture designed for flexibility, multi-instance support, and OpenTelemetry compatibility:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       subgraph "Application Layer"
           UA[User Code]
           DEC[Decorators]
           CTX[Context Managers]
       end
       
       subgraph "HoneyHive SDK"
           subgraph "Tracer Layer"
               T[Multi-Instance Tracers]
               ES[Span Enrichment]
               ESS[Session Enrichment]
           end
           
           subgraph "OpenTelemetry Layer"
               OT[OTEL Tracer]
               SP[Span Processor]
               HTTP[HTTP Instrumentation]
           end
           
           subgraph "Export Layer"
               TP[TracerProvider]
               BSP[Batch Processor]
               OTLP[OTLP Exporter]
           end
       end
       
       subgraph "HoneyHive Platform"
           API[API]
           DASH[Dashboard]
           STORE[Storage]
       end
       
       UA ==> T
       DEC ==> T
       CTX ==> T
       
       T ==> ES
       T ==> ESS
       T ==> OT
       
       ES ==> OT
       OT ==> TP
       HTTP ==> TP
       
       TP ==> SP
       TP ==> BSP
       BSP ==> OTLP
       
       OTLP ==> API
       ESS ==> API
       
       API ==> DASH
       API ==> STORE
       
       classDef userLayer fill:#1b5e20,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef tracerLayer fill:#1a237e,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef otelLayer fill:#e65100,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef exportLayer fill:#ad1457,stroke:#ffffff,stroke-width:4px,color:#ffffff
       classDef platformLayer fill:#4a148c,stroke:#ffffff,stroke-width:4px,color:#ffffff
       
       class UA,DEC,CTX userLayer
       class T,ES,ESS tracerLayer
       class OT,SP,HTTP otelLayer
       class TP,BSP,OTLP exportLayer
       class API,DASH,STORE platformLayer

**Key Architecture Components:**

* **Multi-Instance Tracers**: Independent tracer instances for different environments/workflows
* **Enrichment Layer**: Dual enrichment system for spans and sessions
* **HoneyHive Span Processor**: Enriches spans with HoneyHive-specific attributes and context
* **Standard OTLP Export**: Uses OpenTelemetry's OTLP exporter to send spans to HoneyHive API
* **Flexible Entry Points**: Decorators, context managers, and direct API calls
* **Data Flow**: User code → Span enrichment → OTLP export → HoneyHive platform

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

Span and Session Enrichment
----------------------------

The HoneyHive SDK provides powerful enrichment capabilities for adding metadata and context to your traces. For detailed enrichment architecture and implementation details, see the :doc:`../IMPLEMENTATION_GUIDE`.

**Quick Overview:**

1. **enrich_span**: Modern, unified span-level enrichment (recommended for most use cases)
2. **enrich_session**: Session-level enrichment for backend persistence

**Basic Usage Examples:**

.. code-block:: python

   # Span enrichment with context manager
   with enrich_span(
       event_type="llm_inference",
       metadata={"model": "gpt-4"},
       inputs={"prompt": "What is AI?"}
   ):
       response = llm_client.complete(prompt)
   
   # Session enrichment for backend persistence
   tracer.enrich_session(
       metadata={"user_id": "123"},
       metrics={"total_tokens": 1500}
   )

For complete enrichment documentation including all usage patterns, migration guides, and advanced features, see the :doc:`../IMPLEMENTATION_GUIDE`.
