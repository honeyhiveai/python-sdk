Examples
========

Comprehensive examples and usage patterns for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

This section contains practical examples and usage patterns for the HoneyHive Python SDK. The examples focus on the **Bring Your Own Instrumentor (BYOI)** approach, demonstrating how to achieve automatic AI/LLM observability with minimal code changes by leveraging existing OpenTelemetry instrumentors.

Available Examples
------------------

Bring Your Own Instrumentor
~~~~~~~~~~~~~~~~~~~~~~~~~~~

   :doc:`../BRING_YOUR_INSTRUMENTOR`

Complete guide to using the "Bring Your Own Instrumentor" pattern with the HoneyHive SDK for automatic AI operation tracing.

Quick Start: BYOI Pattern
-------------------------

The core BYOI pattern requires just two steps: initialize HoneyHive tracer and bring your instrumentor.

1. Basic BYOI Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Step 1: Install your instrumentor
   # pip install openinference-instrumentation-openai
   
   # Step 2: Initialize HoneyHive and instrument
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )
   
   # Bring your instrumentor
   OpenAIInstrumentor().instrument()
   
   # That's it! All OpenAI calls are now automatically traced

2. Multiple Tracers
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Create tracers for different environments
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-key",
       project="production-app",
       source="prod"
   )
   
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-key",
       project="development-app",
       source="dev"
   )

3. Basic Tracing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   # Pass tracer instance explicitly (recommended)
   @trace(tracer=my_tracer)
   def my_function():
       """This function will be automatically traced."""
       return "Hello, World!"

4. Manual Span Management
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   with tracer.start_span("custom-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       # Your operation here
       result = process_data()
       span.set_attribute("operation.result", result)

BYOI Integration Examples
-------------------------

The following examples demonstrate the BYOI pattern with different instrumentors and use cases:

AI/ML Providers (Automatic Tracing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **OpenAI**: `simple_openai_integration.py` - GPT models with OpenInference instrumentor
* **Anthropic**: `simple_anthropic_integration.py` - Claude models with OpenInference instrumentor  
* **Google AI**: `simple_google_ai_integration.py` - Gemini models with OpenInference instrumentor
* **AWS Bedrock**: `simple_bedrock_integration.py` - Bedrock models with OpenInference instrumentor

Standard Libraries (Automatic Tracing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **HTTP Requests**: Using `opentelemetry-instrumentation-requests` for automatic HTTP tracing
* **Database Operations**: Using `opentelemetry-instrumentation-sqlalchemy` for database tracing
* **Web Frameworks**: Using framework-specific instrumentors (FastAPI, Flask, Django)

Advanced Patterns
~~~~~~~~~~~~~~~~~

* **Multi-Provider Workflows**: `advanced_usage.py` - Multiple AI providers in one application
* **Multi-Instance Tracers**: Different tracers for different environments/workflows
* **Custom Instrumentors**: Building and integrating custom OpenTelemetry instrumentors

Manual Tracing (When Needed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Custom Operations**: `basic_usage.py` - Manual span management for custom logic
* **Decorator Tracing**: `tracing_decorators.py` - Function-level tracing with decorators
* **Span Enrichment**: Adding custom metadata and context to traces

Best Practices
--------------

1. BYOI Pattern
~~~~~~~~~~~~~~~

* **Start with instrumentors**: Use existing OpenTelemetry instrumentors before manual tracing
* **One tracer per application**: Initialize HoneyHive tracer once, let instrumentors handle the rest
* **Instrument early**: Set up instrumentors during application startup
* **Test instrumentor compatibility**: Verify instrumentors work with your dependencies

2. Multi-Instance Usage
~~~~~~~~~~~~~~~~~~~~~~~~

* **Environment separation**: Use different tracers for prod/dev/test environments
* **Component isolation**: Separate tracers for different services or workflows
* **Independent lifecycles**: Each tracer manages its own configuration and resources
* **Explicit tracer passing**: Pass tracer instances to decorators when using manual tracing

3. Instrumentor Selection
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Provider-specific**: Use OpenInference instrumentors for AI/ML providers (OpenAI, Anthropic, etc.)
* **Standard libraries**: Use official OpenTelemetry instrumentors for HTTP, databases, frameworks
* **Custom needs**: Build custom instrumentors for proprietary systems
* **Compatibility**: Ensure instrumentor versions are compatible with your dependencies

4. Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Sampling**: Configure sampling rates for high-volume applications
* **Selective instrumentation**: Only instrument critical paths in performance-sensitive code
* **Batch processing**: Use OTLP exporter's built-in batching for efficiency
* **Monitor overhead**: Track instrumentation impact on application performance

5. Development & Testing
~~~~~~~~~~~~~~~~~~~~~~~~

* **Test mode**: Use `test_mode=True` for development and testing
* **Mock instrumentors**: Disable instrumentation in unit tests when not needed
* **Environment variables**: Use environment variables for configuration flexibility
* **Gradual rollout**: Start with manual tracing, then add instrumentors incrementally

Getting Help
------------

For more detailed examples and advanced usage patterns, see the individual example files in this section.

For API reference and implementation details, see:

* :doc:`../API_REFERENCE` - Complete API reference
* :doc:`../IMPLEMENTATION_GUIDE` - Technical implementation details
* :doc:`../BRING_YOUR_INSTRUMENTOR` - Bring Your Own Instrumentor guide
