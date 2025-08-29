Examples
========

Comprehensive examples and usage patterns for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

This section contains practical examples and usage patterns for the HoneyHive Python SDK. Each example demonstrates real-world scenarios and best practices for implementing observability in your applications.

Available Examples
------------------

Basic Usage Patterns
~~~~~~~~~~~~~~~~~~~~

:doc:`BASIC_USAGE_PATTERNS`

Getting started with the SDK, including initialization patterns, basic tracing, and common usage scenarios.

Advanced Patterns
~~~~~~~~~~~~~~~~~

:doc:`ADVANCED_PATTERNS`

Complex use cases, custom instrumentors, advanced span management, and performance optimization techniques.

Practical Examples
~~~~~~~~~~~~~~~~~~

:doc:`PRACTICAL_EXAMPLES`

Real-world implementation examples including web applications, data processing pipelines, AI services, and microservices.

OpenInference Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

   :doc:`../OPENINFERENCE_INTEGRATION`

Complete guide to integrating OpenInference instrumentors with the HoneyHive SDK for automatic AI operation tracing.

Quick Start
-----------

1. Basic Initialization
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

2. Basic Tracing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   @trace
   def my_function():
       """This function will be automatically traced."""
       return "Hello, World!"

3. Manual Span Management
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.get_instance()

   with tracer.start_span("custom-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       # Your operation here
       result = process_data()
       span.set_attribute("operation.result", result)

Integration Examples
--------------------

Web Frameworks
~~~~~~~~~~~~~~

FastAPI, Flask, and Django integration examples with automatic HTTP request tracing.

AI/ML Operations
~~~~~~~~~~~~~~~~

OpenAI, Anthropic, and Google AI integration with automatic operation tracing via OpenInference.

Data Processing
~~~~~~~~~~~~~~~

ETL pipelines, batch processing, and data transformation workflows with comprehensive tracing.

Microservices
~~~~~~~~~~~~~

Distributed tracing across multiple services with context propagation and correlation.

Best Practices
--------------

1. Initialization
~~~~~~~~~~~~~~~~~

* Use ``HoneyHiveTracer.init()`` for production code
* Set environment variables for configuration
* Enable test mode for development

2. Tracing
~~~~~~~~~~

* Use ``@trace`` decorator for automatic tracing
* Add meaningful span names and attributes
* Handle errors properly in spans

3. Performance
~~~~~~~~~~~~~~

* Use conditional tracing for high-throughput operations
* Implement sampling for large applications
* Monitor span volume and performance impact

4. Testing
~~~~~~~~~~

* Use test mode for development
* Mock tracer for unit tests
* Test error scenarios and edge cases

Getting Help
------------

For more detailed examples and advanced usage patterns, see the individual example files in this section.

For API reference and implementation details, see:

* :doc:`../API_REFERENCE` - Complete API reference
* :doc:`../IMPLEMENTATION_GUIDE` - Technical implementation details
* :doc:`../OPENINFERENCE_INTEGRATION` - OpenInference integration guide
