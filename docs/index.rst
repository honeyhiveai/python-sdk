HoneyHive Python SDK Documentation
==================================

Welcome to the comprehensive documentation for the HoneyHive Python SDK. This SDK provides LLM observability, evaluation, and tracing capabilities with OpenTelemetry integration.

🔄 **Major Architectural Refactor: Bring Your Own Instrumentor (BYOI)**
------------------------------------------------------------------------

This version represents a **major architectural refactor** designed to solve dependency conflicts and embrace a "bring your own instrumentor" approach for maximum flexibility and compatibility.

**Key Improvements:**

- **Dependency Conflict Resolution**: Eliminates conflicts with existing OpenTelemetry and instrumentation setups
- **BYOI Architecture**: Use any OpenTelemetry instrumentor with HoneyHive tracing (OpenInference, custom instrumentors, etc.)
- **Multi-Instance Tracer Support**: Create independent tracer instances for different environments and workflows
- **Cleaner Integration**: Works seamlessly with existing OpenTelemetry infrastructure
- **Reduced Footprint**: Lighter SDK that doesn't force specific instrumentation choices

**Design Philosophy:**

- **Minimal Dependencies**: Intentionally minimal core dependencies to prevent conflicts in customer environments
- **Zero Vendor Lock-in**: Use any combination of LLM providers, frameworks, and tools while maintaining consistent observability
- **LLM Agent Focus**: Built specifically for comprehensive observability of LLM agent workflows and multi-step AI operations

**Migration Benefits:**

- **No More Version Conflicts**: Compatible with any OpenTelemetry setup
- **Flexible Instrumentation**: Choose any OpenTelemetry-compatible instrumentor based on your needs
- **Better Testing**: Isolated tracer instances improve test reliability
- **Production Ready**: Designed for complex production environments with multiple services

**Quick Start with BYOI:**

.. code-block:: python

   # Install any OpenTelemetry-compatible instrumentor
   # Examples:
   # pip install openinference-instrumentation-openai      # OpenInference
   # pip install opentelemetry-instrumentation-requests    # Standard OTEL
   # pip install your-custom-instrumentor                  # Custom instrumentors
   
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   # from opentelemetry.instrumentation.requests import RequestsInstrumentor
   # from your_custom_instrumentor import CustomInstrumentor
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Bring your own instrumentor - any OpenTelemetry-compatible instrumentor works
   OpenAIInstrumentor().instrument()
   # RequestsInstrumentor().instrument()
   # CustomInstrumentor().instrument()
   
   # All instrumented calls are now automatically traced to HoneyHive

🧪 **Quality & Reliability**
-----------------------------

The SDK maintains high quality through comprehensive testing with **72.95% coverage** (exceeds 70% requirement) and **881 tests** with 100% success rate. See the :doc:`TESTING` guide for detailed testing information.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   FEATURE_LIST
   IMPLEMENTATION_GUIDE
   BRING_YOUR_INSTRUMENTOR
   examples/README
   tracer/index
   evaluation/index
   CLI_REFERENCE
   API_REFERENCE
   TESTING

Getting Help
============

* **Documentation**: This site contains comprehensive guides and examples
* **Examples**: See the :doc:`examples/README` section for practical implementations  
* **API Reference**: Complete reference in :doc:`API_REFERENCE`
* **GitHub**: `Source code and issue tracking <https://github.com/honeyhiveai/python-sdk>`_

Contributing
============

We welcome contributions! Here's how you can help:

**Reporting Issues**
- Report bugs and request features on GitHub
- Provide detailed reproduction steps
- Include environment information (Python version, OS, etc.)

**Development**
- Submit pull requests with clear descriptions
- Follow the existing code style and testing patterns
- Add tests for new functionality
- Update documentation for changes

**Documentation**
- Improve existing documentation
- Add examples and use cases
- Fix typos and clarify explanations

**Building Documentation Locally**

To build and serve the documentation locally:

.. code-block:: bash

   # Install dependencies
   pip install -e .
   
   # Build documentation
   cd docs
   make html
   
   # Serve locally (optional)
   python serve.py

The documentation will be available at http://localhost:8000

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
