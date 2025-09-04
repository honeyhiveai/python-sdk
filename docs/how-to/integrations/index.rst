Integrate with LLM Providers
============================

Learn how to integrate HoneyHive with different LLM providers using the BYOI (Bring Your Own Instrumentor) architecture.

.. toctree::
   :maxdepth: 2

   openai
   anthropic
   google-ai
   google-adk
   aws-bedrock
   azure-openai
   mcp
   multi-provider

Overview
--------

HoneyHive supports both OpenInference and OpenLLMetry instrumentors to automatically trace LLM calls from any provider. This approach provides:

- **Zero Code Changes**: Existing LLM calls are automatically traced
- **Instrumentor Choice**: Choose between OpenInference (lightweight) or OpenLLMetry (enhanced metrics)
- **Provider Flexibility**: Use any LLM provider you want
- **Rich Observability**: Automatic span creation with detailed metadata
- **No Dependency Conflicts**: Use any library version

**Choose Your Instrumentor:**
- **OpenInference**: Lightweight, open-source, perfect for getting started
- **OpenLLMetry**: Enhanced LLM metrics, cost tracking, production optimizations

Quick Start
-----------

**1. Choose and Install Your Instrumentor**

**Option A: OpenInference (Lightweight)**

.. code-block:: bash

   # For OpenAI (includes instrumentor + SDK)
   pip install honeyhive[openinference-openai]
   
   # For Anthropic (includes instrumentor + SDK)  
   pip install honeyhive[openinference-anthropic]
   
   # For Google AI (includes instrumentor + SDK)
   pip install honeyhive[openinference-google-ai]

**Option B: OpenLLMetry (Enhanced Metrics)**

.. code-block:: bash

   # For OpenAI (includes instrumentor + SDK)
   pip install honeyhive[traceloop-openai]
   
   # For Anthropic (includes instrumentor + SDK)  
   pip install honeyhive[traceloop-anthropic]
   
   # For Google AI (includes instrumentor + SDK)
   pip install honeyhive[traceloop-google-ai]

**2. Initialize HoneyHive with Your Chosen Instrumentor**

**Using OpenInference:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[OpenAIInstrumentor()]
   )

**Using OpenLLMetry:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[OpenAIInstrumentor()]
   )

**3. Use LLM Normally**

.. code-block:: python

   import openai
   
   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   # Automatically traced! ✨

Available Providers
-------------------

Each provider supports both OpenInference and OpenLLMetry instrumentors (where available):

**OpenAI** - :doc:`openai`
   - OpenInference: ``openinference-instrumentation-openai``
   - OpenLLMetry: ``opentelemetry-instrumentation-openai``

**Anthropic** - :doc:`anthropic`
   - OpenInference: ``openinference-instrumentation-anthropic``
   - OpenLLMetry: ``opentelemetry-instrumentation-anthropic``

**Google AI** - :doc:`google-ai`
   - OpenInference: ``openinference-instrumentation-google-generativeai``
   - OpenLLMetry: ``opentelemetry-instrumentation-google-generativeai``

**Google ADK** - :doc:`google-adk`
   - OpenInference: ``openinference-instrumentation-google-adk``
   - OpenLLMetry: *Not available*

**AWS Bedrock** - :doc:`aws-bedrock`
   - OpenInference: ``openinference-instrumentation-bedrock``
   - OpenLLMetry: ``opentelemetry-instrumentation-bedrock``

**Azure OpenAI** - :doc:`azure-openai`
   - OpenInference: ``openinference-instrumentation-openai``
   - OpenLLMetry: ``opentelemetry-instrumentation-openai``

**MCP (Model Context Protocol)** - :doc:`mcp`
   - OpenInference: ``openinference-instrumentation-mcp``
   - OpenLLMetry: ``opentelemetry-instrumentation-mcp``

**Multiple Providers** - :doc:`multi-provider`
   Combine multiple instrumentors in one application

.. _OpenInference Docs: https://github.com/Arize-ai/openinference

Best Practices
--------------

**1. Initialize Once**

.. code-block:: python

   # Good: Initialize at application startup
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       instrumentors=[OpenAIInstrumentor()]
   )

**2. Use Environment Variables**

.. code-block:: python

   # Good: Keep secrets in environment
   import os
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       instrumentors=[OpenAIInstrumentor()]
   )

**3. Add Business Context**

.. code-block:: python

   # Good: Add relevant business context
   with tracer.start_span("customer_support") as span:
       span.set_attribute("customer.tier", "premium")
       span.set_attribute("support.category", "technical")
       
       # LLM call inherits this context
       response = client.chat.completions.create(...)

Common Issues
-------------

**No Traces Appearing?**

1. Check that you've included the instrumentor for your LLM provider
2. Verify your HoneyHive API key and project settings
3. Ensure you're making actual LLM API calls (not mocked calls)

**Import Errors?**

Install the required packages:

.. code-block:: bash

   # Recommended: Use integration groups
   pip install honeyhive[openinference-<provider>]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-<provider> <provider-sdk>

**Multiple Providers Not Working?**

Make sure you've included instrumentors for all providers you're using:

.. code-block:: python

   tracer = HoneyHiveTracer.init(
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor()  # Don't forget this!
       ]
   )

Next Steps
----------

- :doc:`openai` - Detailed OpenAI integration guide
- :doc:`anthropic` - Detailed Anthropic integration guide  
- :doc:`multi-provider` - Using multiple providers together
- :doc:`../advanced-tracing/custom-spans` - Adding custom tracing
