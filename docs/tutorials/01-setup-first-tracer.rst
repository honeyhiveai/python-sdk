Set Up Your First Tracer
========================

**Problem:** You need to integrate HoneyHive tracing into your LLM application quickly to start monitoring calls and performance.

**Solution:** Initialize a HoneyHive tracer with minimal configuration and verify it's working in under 5 minutes.

This guide walks you through setting up your first tracer, making a traced LLM call, and verifying the trace appears in your HoneyHive dashboard.

Prerequisites
-------------

- Python 3.11+ installed
- HoneyHive API key (get one at https://app.honeyhive.ai)
- A HoneyHive project created (or we'll create one for you)

Installation
------------

Install the HoneyHive SDK:

.. code-block:: bash

   pip install honeyhive

For LLM provider integrations, install with the provider extra:

.. code-block:: bash

   # For OpenAI
   pip install honeyhive[openinference-openai]
   
   # For Anthropic
   pip install honeyhive[openinference-anthropic]
   
   # For multiple providers
   pip install honeyhive[openinference-openai,openinference-anthropic]





Step 1: Set Up Environment Variables
------------------------------------

Create a ``.env`` file in your project root:

.. code-block:: bash

   # HoneyHive configuration
   HH_API_KEY=your-honeyhive-api-key
   HH_PROJECT=my-first-project
   HH_SOURCE=development
   
   # Your LLM provider API key
   OPENAI_API_KEY=your-openai-api-key





Step 2: Initialize Your First Tracer
------------------------------------

Create a simple Python script to initialize the tracer:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os
   
   # Step 1: Initialize HoneyHive tracer (loads config from environment)
   tracer = HoneyHiveTracer.init(
       project="my-first-project",  # Or use HH_PROJECT env var
       source="development"          # Or use HH_SOURCE env var
   )  # API key loaded from HH_API_KEY
   
   # Step 2: Initialize instrumentor with tracer provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   print("✅ Tracer initialized successfully!")

**What's happening here:**

1. ``HoneyHiveTracer.init()`` creates a tracer instance configured for your project
2. ``OpenAIInstrumentor`` automatically captures OpenAI SDK calls
3. ``instrumentor.instrument(tracer_provider=tracer.provider)`` connects the instrumentor to HoneyHive

Step 3: Make Your First Traced Call
-----------------------------------

Add a simple LLM call to test tracing:

.. code-block:: python

   # Make a traced OpenAI call
   client = openai.OpenAI()  # Uses OPENAI_API_KEY from environment
   
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Hello! This is my first traced call."}
       ]
   )
   
   print(f"Response: {response.choices[0].message.content}")
   print("✅ Trace sent to HoneyHive!")

**Automatic tracing:** Because the instrumentor is active, this call is automatically traced without any decorators or manual span creation.

Step 4: Verify in HoneyHive Dashboard
-------------------------------------

1. Go to https://app.honeyhive.ai
2. Navigate to your project (``my-first-project``)
3. Click "Traces" in the left sidebar

4. You should see your trace with:
   - Model: ``gpt-3.5-turbo``
   - Input message: "Hello! This is my first traced call."
   - Response from the model
   - Timing information
   - Token counts

.. tip::
   Traces typically appear within 1-2 seconds. If you don't see your trace:
   
   - Check that ``HH_API_KEY`` is set correctly
   - Verify your project name matches
   - Look for error messages in your Python output





Complete Example
----------------

Here's the complete working script:

.. code-block:: python

   """
   first_tracer.py - Your first HoneyHive traced application
   
   Run: python first_tracer.py
   """
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os
   from dotenv import load_dotenv
   
   # Load environment variables
   load_dotenv()
   
   def main():
       # Initialize tracer
       tracer = HoneyHiveTracer.init(
           project="my-first-project",
           source="development"
       )
       
       # Initialize instrumentor
       instrumentor = OpenAIInstrumentor()
       instrumentor.instrument(tracer_provider=tracer.provider)
       
       print("✅ Tracer initialized!")
       
       # Make traced call
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a helpful assistant."},
               {"role": "user", "content": "Hello! This is my first traced call."}
           ]
       )
       
       print(f"\n📝 Response: {response.choices[0].message.content}")
       print("\n✅ Trace sent to HoneyHive!")
       print("👉 View at: https://app.honeyhive.ai")
   
   if __name__ == "__main__":
       main()

Running the Example
-------------------

.. code-block:: bash

   # Install dependencies
   pip install honeyhive[openinference-openai] python-dotenv
   
   # Run the script
   python first_tracer.py

Expected output:

.. code-block:: text

   ✅ Tracer initialized!
   
   
   📝 Response: Hello! I'm happy to help you with your first traced call...
   
   ✅ Trace sent to HoneyHive!
   👉 View at: https://app.honeyhive.ai





Troubleshooting
---------------

**Tracer initialization fails:**

- Verify ``HH_API_KEY`` is set correctly (check ``.env`` file)
- Ensure you have network connectivity to HoneyHive servers
- Check API key is valid at https://app.honeyhive.ai/settings/api-keys

**No traces appearing:**

- Wait 2-3 seconds for traces to process
- Check project name matches in code and dashboard
- Look for error messages in Python console
- Verify instrumentor was initialized correctly

**Import errors:**

.. code-block:: bash

   # Install the correct extras
   pip install honeyhive[openinference-openai]
   
   # Or install instrumentor directly
   pip install honeyhive openinference-instrumentation-openai openai





Next Steps
----------

Now that your tracer is working:

- :doc:`02-add-llm-tracing-5min` - Add tracing to existing applications
- :doc:`03-enable-span-enrichment` - Add custom metadata to traces
- :doc:`/how-to/integrations/openai` - Deep dive into OpenAI integration
- :doc:`advanced-configuration` - Advanced configuration options

**Completion time:** ~5 minutes from installation to first trace ✨
