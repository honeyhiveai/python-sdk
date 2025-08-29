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

Span and Session Enrichment
============================

The HoneyHive SDK provides two powerful enrichment approaches for adding metadata and context to your traces:

1. **enrich_span**: Modern, unified span-level enrichment (recommended for most use cases)
2. **enrich_session**: Session-level enrichment for backend persistence

enrich_span - Unified Span Enrichment
--------------------------------------

The new ``enrich_span`` function provides a unified, flexible approach to span enrichment with multiple usage patterns and full backwards compatibility.

**Key Features:**

* ✅ **Unified API**: Single function supporting multiple usage patterns
* ✅ **OpenTelemetry Native**: Works with standard OTEL infrastructure  
* ✅ **Context Manager Support**: Rich context manager pattern
* ✅ **Backwards Compatible**: Supports all existing usage patterns
* ✅ **No Dependencies**: No session_id or API connection required
* ✅ **Rich Attributes**: Supports experiments, complex data structures
* ✅ **Multiple Import Paths**: Consistent across all modules

**Usage Patterns:**

Context Manager Pattern (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the context manager pattern for automatic span enrichment within a code block:

.. code-block:: python

   from honeyhive.tracer import enrich_span
   
   # Enhanced pattern with rich attributes including outputs and error handling
   with enrich_span(
       event_type="llm_inference",
       event_name="gpt4_completion", 
       inputs={"prompt": "What is AI?", "temperature": 0.7},
       outputs={"response": "AI is...", "tokens_used": 145},
       metadata={"model": "gpt-4", "version": "2024-03"},
       metrics={"expected_tokens": 150, "actual_tokens": 145},
       config_data={
           "experiment_id": "exp-123",
           "experiment_name": "temperature_test",
           "experiment_variant": "control"
       },
       error=None  # Can be set to an Exception if an error occurs
   ):
       # Your code here - span is automatically enriched
       try:
           response = llm_client.complete(prompt)
       except Exception as e:
           # Error will be captured automatically in span attributes
           raise

   # Basic pattern (backwards compatible with basic_usage.py)
   with enrich_span("user_session", {"user_id": "123", "action": "query"}):
       process_user_request()

Tracer Instance Method (Direct Calls)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use direct method calls on tracer instances for immediate enrichment:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   
   # Context manager pattern (backwards compatible)
   with tracer.enrich_span("operation_name", {"step": "preprocessing"}):
       preprocess_data()
   
   # Direct method call with outputs and error support
   success = tracer.enrich_span(
       metadata={"stage": "postprocessing"},
       metrics={"latency": 0.1, "tokens": 150},
       outputs={"result": "processed_data", "format": "json"},
       error=None  # Set to Exception instance if error occurred
   )

Global Function (Multi-Instance Support)  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the global function with explicit tracer parameter for multi-instance scenarios:

.. code-block:: python

   from honeyhive.tracer.otel_tracer import enrich_span
   
   # Direct call with tracer parameter and outputs/error support
   success = enrich_span(
       metadata={"operation": "batch_processing"},
       metrics={"items_processed": 1000},
       outputs={"processed_count": 1000, "failed_count": 0},
       error=None,  # Set to Exception if processing failed
       tracer=my_tracer
   )
   
   # Context manager with tracer parameter and error handling
   with enrich_span(
       event_type="batch_job",
       metadata={"job_id": "job-456"},
       outputs={"status": "starting"},
       error=None,
       tracer=my_tracer
   ):
       try:
           process_batch()
       except Exception as e:
           # Exception will be captured in span attributes
           raise

**Import Compatibility:**

All import paths work consistently:

.. code-block:: python

   # All of these are equivalent:
   from honeyhive.tracer import enrich_span                    # Public API (recommended)
   from honeyhive.tracer.otel_tracer import enrich_span        # Main implementation
   from honeyhive.tracer.decorators import enrich_span         # Delegates to main

**Experiment Support:**

Rich experiment data support with automatic attribute setting:

.. code-block:: python

   with enrich_span(
       event_type="ab_test",
       config_data={
           "experiment_id": "exp-789",
           "experiment_name": "model_comparison", 
           "experiment_variant": "gpt4_turbo",
           "experiment_group": "B",
           "experiment_metadata": {
               "version": "1.2",
               "feature_flags": ["new_prompt", "enhanced_context"]
           }
       }
   ):
       # Automatically sets:
       # honeyhive_experiment_id = "exp-789"
       # honeyhive_experiment_name = "model_comparison"
       # honeyhive_experiment_variant = "gpt4_turbo" 
       # honeyhive_experiment_group = "B"
       # honeyhive_experiment_metadata_version = "1.2"
       # honeyhive_experiment_metadata_feature_flags = [...]
       run_experiment()

enrich_session - Session-Level Enrichment  
------------------------------------------

Use ``enrich_session`` for backend persistence of session-level data that needs to be stored in the HoneyHive platform.

**Key Features:**

* ✅ **Backend Integration**: Direct API calls to HoneyHive backend
* ✅ **Rich Data Types**: metadata, feedback, metrics, config, inputs, outputs, user_properties
* ✅ **Immediate Persistence**: Data stored in HoneyHive backend immediately
* ✅ **Session Scoped**: Updates entire session context
* ❌ **Session Dependency**: Requires active session_id
* ❌ **API Dependency**: Requires HoneyHive API connection

**Usage:**

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(api_key="key", project="project")
   
   # Enrich session with comprehensive data
   success = tracer.enrich_session(
       session_id="session-123",  # Optional - uses tracer's session if not provided
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

When to Use Which?
------------------

**Use enrich_span when:**

* ✅ Working within **span context** (most tracing scenarios)
* ✅ Need **OpenTelemetry-native** span enrichment
* ✅ Want **flexible usage patterns** (context managers)
* ✅ Need **rich attribute support** with experiment data
* ✅ Want **backwards compatibility** with existing code
* ✅ Working with **local span enrichment**

**Use enrich_session when:**

* ✅ Need **backend persistence** of session-level data
* ✅ Want to **update existing sessions** in HoneyHive
* ✅ Working with **session-scoped metrics/feedback**
* ✅ Need data **immediately available** in HoneyHive UI
* ✅ Collecting **user feedback and ratings**

**Combined Usage (Recommended):**

Use both for comprehensive observability:

.. code-block:: python

   # Session-level data (persisted to backend)
   tracer.enrich_session(
       metadata={"user_id": "123", "session_type": "chat"},
       config={"model": "gpt-4", "temperature": 0.7}
   )
   
   # Span-level data (rich context for current operation)  
   with enrich_span(
       event_type="llm_query",
       inputs={"prompt": "What is AI?"},
       metadata={"step": "preprocessing"}
   ):
       preprocess_query()
   
   with enrich_span(
       event_type="llm_inference",
       config_data={"model": "gpt-4", "tokens": 150},
       metrics={"latency": 0.8}
   ):
       generate_response()

Migration Guide
---------------

**From Legacy enrich_span Usage:**

The new unified approach is **fully backwards compatible**:

.. code-block:: python

   # ✅ Legacy patterns continue to work unchanged:
   
   # Basic usage pattern (basic_usage.py)
   with tracer.enrich_span("session_enrichment", {"enrichment_type": "session_data"}):
       pass
   
   # Enhanced tracing pattern (enhanced_tracing_demo.py)  
   with enrich_span(
       event_type="enrichment_demo",
       event_name="attribute_enrichment",
       metadata={"enrichment_type": "context_manager"}
   ):
       pass
   
   # Direct method calls
   success = tracer.enrich_span(metadata={"key": "value"})

**Architecture Benefits:**

* ✅ **Single Implementation**: No more duplicate code across modules
* ✅ **No Circular Imports**: Clean dependency flow
* ✅ **Consistent API**: Same behavior across all import paths
* ✅ **Better Testing**: Comprehensive unit and integration test coverage
* ✅ **Type Safety**: Full type annotations and IDE support
