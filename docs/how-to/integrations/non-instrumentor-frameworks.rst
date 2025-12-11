Non-Instrumentor Framework Integration
======================================

Learn how to integrate HoneyHive with frameworks that use OpenTelemetry directly, without relying on auto-instrumentation libraries.

.. contents::
   :local:
   :depth: 2

Overview
--------

Non-instrumentor frameworks are AI/ML frameworks that:

- Use OpenTelemetry directly for tracing
- Don't rely on auto-instrumentation libraries
- May set up their own ``TracerProvider``
- Require careful integration order with HoneyHive

Examples include:

- AWS Strands
- Custom AI frameworks
- Direct OpenTelemetry implementations
- Frameworks with manual span creation

Integration Strategies
----------------------

HoneyHive automatically detects the integration strategy based on the current OpenTelemetry setup:

Main Provider Strategy
~~~~~~~~~~~~~~~~~~~~~~

**When to use**: Framework hasn't set up a ``TracerProvider`` yet, or uses a ``ProxyTracerProvider``

**How it works**: HoneyHive becomes the main ``TracerProvider``

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from your_framework import YourFramework

   # Initialize HoneyHive first
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="your-app"
   )

   # Framework will use HoneyHive's provider
   framework = YourFramework()
   framework.initialize()

Secondary Provider Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**When to use**: Framework has already set up a real ``TracerProvider``

**How it works**: HoneyHive adds its span processor to the existing provider

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from your_framework import YourFramework

   # Framework sets up its TracerProvider first
   framework = YourFramework()

   # HoneyHive integrates with existing provider
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="your-app"
   )

Initialization Order Independence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HoneyHive is designed to work regardless of initialization order:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from your_framework import YourFramework

   # Option 1: "HoneyHive first"
   tracer = HoneyHiveTracer.init(api_key="your-key", project="my-project")
   framework = YourFramework()

   # Option 2: "Framework first"
   framework = YourFramework()
   tracer = HoneyHiveTracer.init(api_key="your-key", project="my-project")

   # Both work correctly!

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Required
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_PROJECT="my-project"

   # Optional
   export HH_SOURCE="my-application"
   export HH_OTLP_ENABLED="true"  # Enable OTLP export (default: true)
   export HH_OTLP_PROTOCOL="http/json"  # Use JSON format (default: http/protobuf)

Code Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",        # Required for OTLP tracing
       source="my-application",     # Optional, defaults to filename
       test_mode=False,            # Set to True for testing
       verbose=True                # Enable debug logging
   )

Best Practices
--------------

1. **Initialize Early**

   Initialize HoneyHive as early as possible in your application:

   .. code-block:: python

      # At the top of your main module
      from honeyhive import HoneyHiveTracer

      tracer = HoneyHiveTracer.init(
          api_key="your-api-key",
          project="my-project"
      )

2. **Use Environment Variables**

   Store configuration in environment variables for security:

   .. code-block:: python

      import os
      from honeyhive import HoneyHiveTracer

      tracer = HoneyHiveTracer.init(
          api_key=os.getenv("HH_API_KEY"),
          project=os.getenv("HH_PROJECT", "default"),
          source=os.getenv("HH_SOURCE", "my-app")
      )

3. **Handle Initialization Errors**

   Gracefully handle initialization failures:

   .. code-block:: python

      try:
          tracer = HoneyHiveTracer.init(
              api_key=os.getenv("HH_API_KEY"),
              project=os.getenv("HH_PROJECT")
          )
      except Exception as e:
          print(f"HoneyHive initialization failed: {e}")
          # Continue without tracing or use fallback

4. **Test Integration**

   Use test mode during development:

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key="test-key",
          project="test-project",
          test_mode=True  # Disables API calls
      )

Common Integration Patterns
---------------------------

Pattern 1: Framework with Delayed Provider Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some frameworks delay TracerProvider setup:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from delayed_framework import DelayedFramework

   # Initialize HoneyHive first
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   # Framework will use HoneyHive's provider
   framework = DelayedFramework()
   framework.initialize()  # Sets up tracing

Pattern 2: Multiple Framework Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate multiple frameworks with a single HoneyHive tracer:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from framework_a import FrameworkA
   from framework_b import FrameworkB

   # Single HoneyHive tracer for all frameworks
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key", 
       project="multi-framework-project"
   )

   # All frameworks share the same tracing context
   framework_a = FrameworkA()
   framework_b = FrameworkB()

Pattern 3: Context Propagation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure context propagation between framework operations:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry import trace

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key", 
       project="my-project"
   )

   # Create parent span for workflow
   otel_tracer = trace.get_tracer("my-app")
   with otel_tracer.start_as_current_span("workflow") as span:
       # Framework operations inherit this context
       result_a = framework_a.process(data)
       result_b = framework_b.analyze(result_a)

Troubleshooting
---------------

Provider Detection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

If HoneyHive doesn't detect your framework's provider correctly:

.. code-block:: python

   from honeyhive.tracer.provider_detector import ProviderDetector

   detector = ProviderDetector()
   provider_info = detector.detect_provider()
   print(f"Detected provider: {provider_info}")

Integration Strategy Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check which integration strategy is being used:

.. code-block:: python

   from honeyhive.tracer.provider_detector import ProviderDetector

   detector = ProviderDetector()
   provider_info = detector.detect_provider()
   strategy = detector.determine_integration_strategy(provider_info)
   print(f"Integration strategy: {strategy}")

Span Processing Issues
~~~~~~~~~~~~~~~~~~~~~~

Enable verbose logging to debug span processing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       verbose=True  # Enable debug output
   )

Missing Spans
~~~~~~~~~~~~~

If spans aren't appearing in HoneyHive:

1. **Check API Key**: Ensure ``HH_API_KEY`` is set correctly
2. **Check Project**: Ensure ``HH_PROJECT`` is set (required for OTLP)
3. **Check OTLP**: Ensure ``HH_OTLP_ENABLED`` is not set to "false"
4. **Check Test Mode**: Ensure ``test_mode=False`` in production

Advanced Topics
---------------

Custom Attributes
~~~~~~~~~~~~~~~~~

Add custom attributes to all spans:

.. code-block:: python

   from opentelemetry import trace

   # Get the tracer after HoneyHive initialization
   otel_tracer = trace.get_tracer("my-app")

   with otel_tracer.start_as_current_span("custom-operation") as span:
       span.set_attribute("custom.attribute", "value")
       span.set_attribute("framework.version", "1.0.0")
       
       # Your framework operation here
       result = framework.process(data)

Error Handling
~~~~~~~~~~~~~~

Handle framework integration errors gracefully:

.. code-block:: python

   from honeyhive.tracer.processor_integrator import ProviderIncompatibleError

   try:
       tracer = HoneyHiveTracer.init(
           api_key="your-api-key",
           project="my-project"
       )
   except ProviderIncompatibleError as e:
       print(f"Provider incompatible: {e}")
       # Use fallback tracing or continue without HoneyHive
   except Exception as e:
       print(f"Unexpected error: {e}")

Session Management
~~~~~~~~~~~~~~~~~~

Manage tracing sessions explicitly:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key", 
       project="my-project"
   )

   # Session ID is automatically generated
   session_id = tracer.session_id
   print(f"Tracing session: {session_id}")

   # All framework operations will be associated with this session

See Also
--------

- :doc:`../../reference/api/tracer` - HoneyHive Tracer API reference
- :doc:`../../explanation/index` - Understanding HoneyHive concepts
- :doc:`../../development/testing/integration-testing` - Testing with real APIs
- `OpenTelemetry Python Documentation <https://opentelemetry-python.readthedocs.io/>`_
