HoneyHive Python SDK Documentation
==================================

**LLM Observability and Evaluation Platform**

The HoneyHive Python SDK provides comprehensive observability, tracing, and evaluation capabilities for LLM applications with OpenTelemetry integration and a "Bring Your Own Instrumentor" architecture.

.. note::
   **Project Configuration**: The ``project`` parameter is required when initializing the tracer. This identifies which HoneyHive project your traces belong to and must match your project name in the HoneyHive dashboard.

📦 **Installation**

.. code-block:: bash

   # Core SDK only (minimal dependencies)
   pip install honeyhive
   
   # With LLM provider support (recommended)
   pip install honeyhive[openinference-openai]      # OpenAI via OpenInference
   pip install honeyhive[openinference-anthropic]   # Anthropic via OpenInference
   pip install honeyhive[all-openinference]         # All OpenInference integrations

🔧 **Quick Example**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize with BYOI architecture
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Initialize instrumentor separately (correct pattern)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Use @trace for custom functions
   @trace(tracer=tracer)
   def analyze_sentiment(text: str) -> str:
       # OpenAI calls automatically traced via instrumentor
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": f"Analyze sentiment: {text}"}]
       )
       return response.choices[0].message.content
   
   # Both the function and the OpenAI call are traced!
   result = analyze_sentiment("I love this new feature!")

🔗 **External Links**

- `HoneyHive Platform <https://honeyhive.ai>`_
- `Python SDK on PyPI <https://pypi.org/project/honeyhive/>`_
- `GitHub Repository <https://github.com/honeyhiveai/python-sdk>`_
- `OpenInference Instrumentors <https://github.com/Arize-ai/openinference>`_ (supported instrumentor provider)
- `Traceloop Instrumentors <https://github.com/traceloop/openllmetry>`_ - Enhanced metrics and production optimizations

.. toctree::
   :maxdepth: 1

   reference/index

Indices and Tables
==================

* :ref:`genindex`
* :ref:`search`
