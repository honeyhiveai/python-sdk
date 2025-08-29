HoneyHive Python SDK Documentation
==================================

Welcome to the HoneyHive Python SDK documentation. This SDK provides comprehensive observability and tracing capabilities for Python applications, with seamless integration with OpenTelemetry and OpenInference.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The HoneyHive Python SDK is designed to provide comprehensive observability into your Python applications. It combines the power of OpenTelemetry with HoneyHive's session management and AI operation tracing capabilities.

Design Philosophy
-----------------

**Minimal Dependencies**: We intentionally keep core dependencies minimal to prevent conflicts in customer environments. This ensures your existing LLM workflows continue working without dependency clashes.

**Bring Your Own Instrumentor**: Rather than hardcoding LLM integrations, we provide a flexible framework for you to choose what gets instrumented. This gives you full control over your observability stack.

**LLM Agent Focus**: Built specifically for comprehensive observability of LLM agent workflows and multi-step AI operations. Track conversations, state changes, and performance across your entire AI application.

**Zero Vendor Lock-in**: Use any combination of LLM providers, frameworks, and tools while maintaining consistent observability through OpenTelemetry standards.

**Multi-Instance Architecture**: Modern tracer design supporting multiple independent tracer instances within the same runtime for flexible session management.

Key Features
~~~~~~~~~~~~

* **LLM Agent Observability** - Track multi-step conversations and agent state
* **OpenTelemetry Integration** - Full OpenTelemetry compliance with minimal dependencies
* **Bring Your Own Instrumentor** - Choose exactly what gets traced without conflicts
* **Automatic Session Management** - Seamless session tracking across agent workflows
* **AI Operation Tracing** - OpenInference integration for any LLM provider
* **Performance Monitoring** - Built-in latency, token tracking, and cost monitoring
* **Framework Agnostic** - Works with any Python application and LLM framework
* **Zero Code Changes** - Automatic instrumentation where possible
* **Multi-Instance Support** - Create multiple independent tracers for different workflows
* **Dynamic Session Naming** - Automatic file-based session naming for better organization

Quick Start
-----------

1. Installation
~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install honeyhive

2. Basic Usage
~~~~~~~~~~~~~~

**Option 1: Official SDK Pattern (Recommended)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Official SDK pattern (recommended)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # Use the tracer directly
   with tracer.start_span("my-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       # Your operation here
       result = process_data()
       span.set_attribute("operation.result", result)

**Option 2: Direct Constructor (Alternative)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Direct constructor (creates a new instance)
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # Use the tracer directly
   with tracer.start_span("my-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       # Your operation here
       result = process_data()
       span.set_attribute("operation.result", result)

3. Multiple Tracers
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Create multiple tracers for different workflows
   production_tracer = HoneyHiveTracer(
       api_key="prod-key",
       project="production-app",
       source="prod"
   )
   
   development_tracer = HoneyHiveTracer(
       api_key="dev-key", 
       project="development-app",
       source="dev"
   )

   # Each tracer operates independently
   with production_tracer.start_span("prod-operation") as span:
       # Production tracing
       pass

4. LLM Agent Tracing
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize with LLM instrumentation
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production",
       instrumentors=[OpenAIInstrumentor()]  # Choose what to trace
   )

   # Your existing LLM code works unchanged
   import openai
   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   # Automatically traced with full context!

5. Automatic Tracing with Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   # Pass tracer instance explicitly (recommended)
   @trace(tracer=my_tracer)
   def my_function():
       """This function will be automatically traced."""
       return "Hello, World!"

   # Or use global tracer (legacy, deprecated)
   @trace
   def legacy_function():
       """Uses global tracer - not recommended for new code."""
       return "Hello, World!"

Documentation Sections
----------------------

API Reference
~~~~~~~~~~~~~

:doc:`API_REFERENCE`

Complete API reference for all classes, methods, and configuration options.

Implementation Guide
~~~~~~~~~~~~~~~~~~~~

:doc:`IMPLEMENTATION_GUIDE`

Technical implementation details, architecture overview, and design patterns.

Examples
~~~~~~~~

:doc:`examples/README`

Practical examples and usage patterns for various use cases.

OpenInference Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`OPENINFERENCE_INTEGRATION`

Guide to integrating OpenInference instrumentors for automatic AI operation tracing.

Recent Improvements
~~~~~~~~~~~~~~~~~~~

**Multi-Instance Architecture**: Modern multi-instance tracer design supporting multiple independent tracers within the same runtime.

**Dynamic Session Naming**: Automatic session naming based on the file where the tracer is initialized, improving organization and debugging.

**Enhanced Testing**: Comprehensive test coverage increased to 72.10% with a new 70% coverage threshold requirement.

**Improved Decorator Support**: Enhanced `@trace` and `@atrace` decorators with explicit tracer instance support for better multi-instance usage.

**TracerProvider Integration**: Smart OpenTelemetry provider management that integrates with existing providers or creates new ones as needed.

**Complete Integration Testing**: Full test suite covering multi-instance patterns, real API integration, and TracerProvider scenarios.

**Dependency Management**: Added `psutil` dependency for enhanced memory usage monitoring in evaluation framework.

**Enhanced Documentation**: All documentation has been converted from Markdown to reStructuredText for better Sphinx integration and cross-referencing.

**Complete Feature Coverage**: Documentation now accurately reflects all implemented features including `@trace_class` and `@evaluate` decorators.

**Dependency Philosophy**: Clear explanation of the minimal dependencies approach and "bring your own instrumentor" philosophy.

**LLM Agent Focus**: Comprehensive coverage of multi-step conversation tracking and agent state management.

Building the Documentation
--------------------------

To build the documentation locally:

.. code-block:: bash

   # Install dependencies
   pip install -r docs/requirements.txt

   # Build documentation
   cd docs
   make html

   # Serve locally
   python serve.py

The documentation will be available at http://localhost:8000

Getting Help
------------

* **Documentation**: This site contains comprehensive guides and examples
* **Examples**: See the examples section for practical implementations
* **API Reference**: Complete reference for all SDK components
* **GitHub**: Source code and issue tracking

Contributing
------------

We welcome contributions! Please see our contributing guidelines for more information.

* Report bugs and request features
* Submit pull requests
* Improve documentation
* Share examples and use cases

Testing Standards
-----------------

* **Coverage Requirement**: Minimum 70% test coverage required
* **Test Framework**: pytest with comprehensive unit and integration tests
* **Quality Tools**: Black (formatting), isort (imports), pylint (linting), mypy (type checking)
* **Multi-Instance Testing**: Full test coverage for new multi-tracer architecture
