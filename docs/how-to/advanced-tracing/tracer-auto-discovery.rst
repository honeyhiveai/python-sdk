.. _tracer-auto-discovery:

Automatic Tracer Discovery
==========================

The HoneyHive Python SDK now supports automatic tracer discovery, which enables backward compatibility with existing ``@trace`` decorator usage while unlocking powerful multi-instance capabilities.

.. versionadded:: 0.2.0
   Automatic tracer discovery via OpenTelemetry baggage context (available in complete-refactor branch).

Overview
--------

.. important::
   This feature is currently available in the ``complete-refactor`` branch and represents a major enhancement to the HoneyHive Python SDK. It will be included in the next major release.

The automatic tracer discovery system uses OpenTelemetry baggage to propagate tracer context information, enabling the ``@trace`` and ``@atrace`` decorators to automatically find the appropriate tracer instance without explicit parameters.

**Key Benefits:**

- **100% Backward Compatibility**: All existing ``@trace`` usage continues to work
- **Zero Migration Required**: No code changes needed for existing projects  
- **Multi-Instance Support**: Multiple tracer instances work seamlessly
- **Context Awareness**: Automatic context-based tracer selection
- **Graceful Degradation**: Functions execute normally when no tracer is available

Priority System
---------------

The tracer discovery system uses a priority-based fallback chain:

1. **Explicit Tracer** (Highest Priority)
   
   .. code-block:: python
   
      @trace(tracer=my_tracer)  # Always uses my_tracer
      def my_function():
          pass

2. **Context Tracer** (Medium Priority)
   
   .. code-block:: python
   
      with tracer.start_span("operation"):
          @trace  # Auto-discovers tracer from context
          def my_function():
              pass

3. **Default Tracer** (Lowest Priority)
   
   .. code-block:: python
   
      set_default_tracer(global_tracer)
      
      @trace  # Uses global_tracer as fallback
      def my_function():
          pass

Basic Usage Patterns
--------------------

Explicit Tracer (Original Pattern)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The original explicit tracer pattern continues to work exactly as before:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, atrace
   from honeyhive.models import EventType
   
   tracer = HoneyHiveTracer()
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def process_data(data):
       return f"processed: {data}"
   
   @atrace(tracer=tracer, event_type=EventType.tool)  
   async def async_process_data(data):
       return f"async_processed: {data}"

Context-Based Auto-Discovery (Enhanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorators now automatically discover tracers from context when needed:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, atrace
   from honeyhive.models import EventType
   
   tracer = HoneyHiveTracer()
   
   @trace(event_type=EventType.tool)  # No tracer parameter needed!
   def process_data(data):
       return f"processed: {data}"
   
   @trace(event_type=EventType.chain)
   def analyze_data(data):
       return f"analyzed: {data}"
   
   # Use decorators as the primary pattern
   def main_workflow():
       # Context manager provides tracer context for decorators
       with tracer.start_span("data_processing"):
           result = process_data("sample_data")
           analysis = analyze_data(result)
           return analysis

Global Default Tracer (New Convenience)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set a global default tracer for application-wide convenience:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, set_default_tracer
   
   # Set up default tracer once
   default_tracer = HoneyHiveTracer()
   set_default_tracer(default_tracer)
   
   # Now @trace works everywhere without specification
   @trace(event_type=EventType.tool)
   def compute_metrics(data):
       return {"accuracy": 0.95}
   
   # Works automatically with default tracer
   result = compute_metrics({"sample": "data"})

Multi-Instance Patterns
-----------------------

Multiple Service Tracers
~~~~~~~~~~~~~~~~~~~~~~~~

Create independent tracers for different services using decorators as the primary pattern:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, set_default_tracer
   
   # Create service-specific tracers
   auth_tracer = HoneyHiveTracer()
   payment_tracer = HoneyHiveTracer()
   notification_tracer = HoneyHiveTracer()
   
   # Option 1: Use explicit tracer parameter (always works)
   @trace(tracer=auth_tracer, event_type=EventType.tool)
   def authenticate_user(credentials):
       return credentials == "valid_token"
   
   @trace(tracer=payment_tracer, event_type=EventType.tool)
   def process_payment(amount):
       return amount > 0
   
   @trace(tracer=notification_tracer, event_type=EventType.tool)
   def send_notification(message):
       return f"Sent: {message}"
   
   # Option 2: Use context switching with default tracer (more flexible)
   def process_user_registration():
       # Authenticate user
       set_default_tracer(auth_tracer)
       auth_result = authenticate_user("token")
       
       if auth_result:
           # Process payment
           set_default_tracer(payment_tracer)
           payment_result = process_payment(99.99)
           
           if payment_result:
               # Send notification
               set_default_tracer(notification_tracer)
               send_notification("Registration complete!")
   
   # Option 3: Context managers when you need fine-grained control
   def process_user_registration_with_context():
       with auth_tracer.start_span("user_registration"):
           auth_result = authenticate_user("token")
           
           with payment_tracer.start_span("payment_processing"):
               payment_result = process_payment(99.99)
               
               with notification_tracer.start_span("notification_sending"):
                   send_notification("Registration complete!")

Cross-Service Nested Calls
~~~~~~~~~~~~~~~~~~~~~~~~~~

Handle nested calls across different service boundaries with decorators:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, set_default_tracer
   
   # Create tracers for different layers
   api_tracer = HoneyHiveTracer()
   business_tracer = HoneyHiveTracer()
   data_tracer = HoneyHiveTracer()
   
   # Decorator-first approach with explicit tracers
   @trace(tracer=data_tracer, event_type=EventType.tool)
   def fetch_user_data(user_id):
       return {"id": user_id, "name": "John Doe"}
   
   @trace(tracer=business_tracer, event_type=EventType.chain)
   def process_user_request(user_id):
       # Decorated function automatically calls data layer
       return fetch_user_data(user_id)
   
   @trace(tracer=api_tracer, event_type=EventType.chain)
   def handle_user_request(user_id):
       # Decorated function automatically calls business layer
       return process_user_request(user_id)
   
   # Clean, declarative usage
   result = handle_user_request("user123")
   
   # Alternative: Use default tracer switching for workflow patterns
   def user_request_workflow(user_id):
       set_default_tracer(api_tracer)
       
       @trace(event_type=EventType.chain)
       def api_layer():
           set_default_tracer(business_tracer)
           return business_layer()
       
       @trace(event_type=EventType.chain)  
       def business_layer():
           set_default_tracer(data_tracer)
           return data_layer()
           
       @trace(event_type=EventType.tool)
       def data_layer():
           return {"id": user_id, "name": "John Doe"}
           
       return api_layer()
   
   # Context managers only when you need span-level control
   def handle_user_request_with_spans(user_id):
       with api_tracer.start_span("incoming_request"):
           with business_tracer.start_span("business_operation"):
               with data_tracer.start_span("database_query"):
                   return fetch_user_data(user_id)

Async Patterns
--------------

Async Function Auto-Discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Async functions work seamlessly with decorator-based tracing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, atrace, set_default_tracer
   import asyncio
   
   tracer = HoneyHiveTracer()
   set_default_tracer(tracer)
   
   @atrace(event_type=EventType.tool)
   async def fetch_async_data(source):
       await asyncio.sleep(0.1)  # Simulate async I/O
       return {"source": source, "data": [1, 2, 3]}
   
   @atrace(event_type=EventType.tool)  
   async def process_async_data(data):
       await asyncio.sleep(0.1)  # Simulate processing
       return {"processed": [x * 2 for x in data["data"]]}
   
   @atrace(event_type=EventType.chain)
   async def async_data_pipeline(source):
       # All functions use default tracer automatically
       raw_data = await fetch_async_data(source)
       processed = await process_async_data(raw_data)
       return processed
   
   # Clean, declarative async pipeline
   async def main():
       result = await async_data_pipeline("api")
       print(f"Pipeline result: {result}")
   
   # Run the async pipeline
   result = asyncio.run(main())
   
   # Alternative: Explicit tracer parameters (always works)
   @atrace(tracer=tracer, event_type=EventType.tool)
   async def explicit_async_function():
       return "explicitly traced"

Mixed Sync/Async Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine synchronous and asynchronous functions with decorator-based tracing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, atrace, set_default_tracer
   import asyncio
   
   tracer = HoneyHiveTracer()
   set_default_tracer(tracer)
   
   @trace(event_type=EventType.tool)
   def validate_input(data):
       return len(data) > 0 and data.isalnum()
   
   @atrace(event_type=EventType.tool)
   async def call_external_service(data):
       await asyncio.sleep(0.1)
       return f"response_for_{data}"
   
   @atrace(event_type=EventType.chain)
   async def mixed_workflow(input_data):
       # Sync validation within async function
       is_valid = validate_input(input_data)
       
       if is_valid:
           # Async external call
           return await call_external_service(input_data)
       else:
           return "invalid_input"
   
   @atrace(event_type=EventType.tool)
   async def process_batch(items):
       results = []
       for item in items:
           result = await mixed_workflow(item)
           results.append(result)
       return results
   
   # Clean async workflow execution
   async def main():
       items = ["test123", "sample456", "data789"]
       results = await process_batch(items)
       print(f"Processed {len(results)} items")
   
   result = asyncio.run(main())

Advanced Configuration
----------------------

Registry Management
~~~~~~~~~~~~~~~~~~~

Control the tracer registry for advanced use cases:

.. code-block:: python

   from honeyhive.tracer import clear_registry, get_registry_stats
   
   # Get registry statistics
   stats = get_registry_stats()
   print(f"Active tracers: {stats['active_tracers']}")
   print(f"Has default: {stats['has_default_tracer']}")
   
   # Clear registry (useful for testing)
   clear_registry()

Error Handling
~~~~~~~~~~~~~~

The system gracefully handles various error conditions:

.. code-block:: python

   from honeyhive import trace, set_default_tracer
   
   # Clear any default tracer
   set_default_tracer(None)
   
   @trace(event_type=EventType.tool)
   def function_without_tracer():
       # Executes normally without tracing
       return "success"
   
   # Function runs normally, just without tracing
   result = function_without_tracer()

Priority Override Demonstration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understand how the priority system works:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, set_default_tracer
   
   # Set up different tracers
   default_tracer = HoneyHiveTracer()
   context_tracer = HoneyHiveTracer()
   explicit_tracer = HoneyHiveTracer()
   
   set_default_tracer(default_tracer)
   
   @trace(event_type=EventType.tool)
   def flexible_function():
       return "uses_current_priority"
   
   @trace(tracer=explicit_tracer, event_type=EventType.tool)
   def explicit_function():
       return "always_explicit"
   
   # 1. Uses default tracer
   result1 = flexible_function()
   
   # 2. Uses context tracer (overrides default)
   with context_tracer.start_span("context"):
       result2 = flexible_function()
       
       # 3. Uses explicit tracer (overrides context)
       result3 = explicit_function()

Best Practices
--------------

Decorator-First Philosophy
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Decorators should be your primary tracing mechanism.** They provide clean, declarative tracing that's easy to read and maintain:

.. code-block:: python

   # ✅ PREFERRED: Decorator-based tracing
   @trace(event_type=EventType.chain)
   def process_user_request(user_id):
       return handle_request(user_id)
   
   @trace(event_type=EventType.tool)  
   def handle_request(user_id):
       return fetch_user_data(user_id)
   
   # ❌ AVOID: Unnecessary context managers
   def process_user_request_verbose(user_id):
       with tracer.start_span("user_action"):
           with tracer.start_span("data_access"):
               return fetch_user_data(user_id)

When to Use Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reserve context managers for specific scenarios where decorators aren't sufficient:

**1. Non-Function Operations**

.. code-block:: python

   # ✅ Context managers for non-function code blocks
   def complex_workflow():
       with tracer.start_span("setup_phase"):
           config = load_configuration()
           resources = allocate_resources(config)
       
       # Use decorators for functions
       result = process_data(resources)
       
       with tracer.start_span("cleanup_phase"):
           cleanup_resources(resources)

**2. Fine-Grained Timing Control**

.. code-block:: python

   @trace(event_type=EventType.tool)
   def process_batch(items):
       for i, item in enumerate(items):
           # Individual item timing
           with tracer.start_span(f"item_{i}"):
               process_item(item)

**3. Conditional Tracing Logic**

.. code-block:: python

   def adaptive_processing(data, enable_detailed_tracing=False):
       if enable_detailed_tracing:
           with tracer.start_span("detailed_analysis"):
               return detailed_process(data)
       else:
           return simple_process(data)

Recommended Patterns by Use Case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Simple Applications: Default Tracer + Decorators**

.. code-block:: python

   # Set once at startup
   set_default_tracer(HoneyHiveTracer())
   
   # Use everywhere without parameters
   @trace(event_type=EventType.chain)
   def my_function():
       pass

**2. Multi-Service Applications: Explicit Tracers**

.. code-block:: python

   # Create service-specific tracers
   auth_tracer = HoneyHiveTracer()
   data_tracer = HoneyHiveTracer()
   
   # Use explicit tracer parameters
   @trace(tracer=auth_tracer, event_type=EventType.tool)
   def authenticate():
       pass
   
   @trace(tracer=data_tracer, event_type=EventType.tool)
   def fetch_data():
       pass

**3. Complex Workflows: Mixed Approach**

.. code-block:: python

   # Use decorators for business functions
   @trace(tracer=workflow_tracer, event_type=EventType.tool)
   def execute_step(step_data):
       return process_step(step_data)
   
   # Use context managers for workflow orchestration
   def run_workflow(steps):
       with workflow_tracer.start_span("workflow_execution"):
           results = []
           for step in steps:
               result = execute_step(step)  # Decorated function
               results.append(result)
           return results

**4. Performance-Critical Code: Selective Tracing**

.. code-block:: python

   # Trace important business operations
   @trace(event_type=EventType.tool)
   def important_business_function():
       # Don't trace every utility call
       helper_result = utility_function()  # No decorator
       return process_result(helper_result)

**5. Legacy Integration: Gradual Adoption**

.. code-block:: python

   # Start with minimal decoration
   @trace(event_type=EventType.tool)
   def legacy_wrapper():
       # Existing code unchanged
       return existing_legacy_function()

Guidelines Summary
~~~~~~~~~~~~~~~~~~

1. **Start with Decorators**: Use ``@trace`` and ``@atrace`` as your primary patterns
2. **Context Managers for Orchestration**: Use ``start_span()`` only for non-function blocks
3. **Explicit Tracers for Multi-Service**: Use ``tracer=`` parameters for service isolation
4. **Default Tracer for Simplicity**: Use ``set_default_tracer()`` for single-service apps
5. **Performance Awareness**: Don't trace every function, focus on business operations

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``@trace`` decorator warns "No tracer available"

**Solution**: Either set a default tracer, use explicit tracer parameter, or ensure you're within a tracer context:

.. code-block:: python

   # Option 1: Set default tracer
   set_default_tracer(my_tracer)
   
   # Option 2: Use explicit tracer
   @trace(tracer=my_tracer)
   def my_function():
       pass
   
   # Option 3: Use context manager
   with my_tracer.start_span("operation"):
       my_function()  # Will auto-discover tracer

**Problem**: Wrong tracer being used in nested contexts

**Solution**: Verify the priority chain - explicit > context > default:

.. code-block:: python

   # Explicit tracer always wins
   @trace(tracer=specific_tracer)  # Uses specific_tracer
   def my_function():
       pass
   
   # Context and default follow priority
   with context_tracer.start_span("span"):
       my_function()  # Uses specific_tracer (explicit wins)

**Problem**: Memory leaks with many tracer instances

**Solution**: The registry uses weak references and automatically cleans up. For manual cleanup:

.. code-block:: python

   from honeyhive.tracer import clear_registry
   
   # Manual cleanup if needed
   clear_registry()

Migration Guide
---------------

Branch Information
~~~~~~~~~~~~~~~~~~

.. warning::
   This feature is currently in development on the ``complete-refactor`` branch. To use these features:
   
   1. Switch to the complete-refactor branch:
      
      .. code-block:: bash
      
         git checkout complete-refactor
   
   2. Install in development mode:
      
      .. code-block:: bash
      
         pip install -e .
   
   3. The changes will be merged to main and released in version 0.2.0

Migrating from Previous Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**No Changes Required**: All existing code continues to work exactly as before.

**Optional Enhancements**: Gradually adopt new patterns for improved convenience:

.. code-block:: python

   # Before (still works)
   @trace(tracer=my_tracer, event_type=EventType.tool)
   def old_pattern():
       pass
   
   # After (new convenience)
   set_default_tracer(my_tracer)
   
   @trace(event_type=EventType.tool)  # Simpler!
   def new_pattern():
       pass

**Multi-Instance Adoption**: For complex applications, gradually introduce service-specific tracers:

.. code-block:: python

   # Phase 1: Single tracer (existing)
   app_tracer = HoneyHiveTracer()
   
   # Phase 2: Service-specific tracers (new)
   auth_tracer = HoneyHiveTracer()
   user_tracer = HoneyHiveTracer()
   
   # Phase 3: Context-aware usage (enhanced)
   with auth_tracer.start_span("auth_flow"):
       @trace  # Auto-discovers auth_tracer
       def authenticate():
           pass

See Also
--------

- :doc:`../../development/testing/unit-testing` - Testing strategies with auto-discovery
- :doc:`../integrations/multi-provider` - Multi-provider tracing patterns  
- :doc:`../../reference/api/decorators` - Complete decorator API reference
- :doc:`../../explanation/architecture/overview` - Architecture deep dive
