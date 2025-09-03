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

HoneyHive uses OpenInference instrumentors to automatically trace LLM calls from any provider. This approach provides:

- **Zero Code Changes**: Existing LLM calls are automatically traced
- **Provider Flexibility**: Use any LLM provider you want
- **Rich Observability**: Automatic span creation with detailed metadata
- **No Dependency Conflicts**: Use any library version

Quick Start
-----------

**1. Install Instrumentor**

.. code-block:: bash

   # For OpenAI
   pip install openinference-instrumentation-openai openai
   
   # For Anthropic
   pip install openinference-instrumentation-anthropic anthropic

**2. Initialize HoneyHive with Instrumentor**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

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

**OpenAI** - :doc:`openai`
   Use ``openinference-instrumentation-openai`` for OpenAI GPT models

**Anthropic** - :doc:`anthropic`
   Use ``openinference-instrumentation-anthropic`` for Claude models

**Google AI** - :doc:`google-ai`
   Use ``openinference-instrumentation-google-generativeai`` for Gemini models

**AWS Bedrock** - :doc:`aws-bedrock`
   Use ``openinference-instrumentation-bedrock`` for Bedrock model access

**Azure OpenAI** - :doc:`azure-openai`
   Use ``openinference-instrumentation-openai`` for Azure-hosted OpenAI

**MCP (Model Context Protocol)** - :doc:`mcp`
   Use ``openinference-instrumentation-mcp`` for agent tool orchestration

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
       project=os.getenv("HH_PROJECT"),
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

   pip install openinference-instrumentation-<provider> <provider-sdk>

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
