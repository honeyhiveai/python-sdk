Add LLM Tracing in 5 Minutes
============================

**Problem:** You have an existing LLM application and want to add HoneyHive tracing with minimal code changes.

**Solution:** Add 5 lines of code to initialize tracing, and your existing LLM calls will be automatically traced.

This guide shows you how to integrate HoneyHive into an existing application in under 5 minutes with minimal disruption to your code.

Before You Start
----------------

**You have:**

- An existing application using OpenAI, Anthropic, or another LLM provider
- Python 3.11+ 
- 5 minutes of time

**You need:**

- HoneyHive API key from https://app.honeyhive.ai
- Your LLM provider's SDK already installed

Quick Integration (3 Steps)
---------------------------

Step 1: Install HoneyHive
^^^^^^^^^^^^^^^^^^^^^^^^^

Add HoneyHive with your provider's instrumentor:

.. code-block:: bash

   # For OpenAI
   pip install honeyhive[openinference-openai]
   
   # For Anthropic  
   pip install honeyhive[openinference-anthropic]

Step 2: Add 5 Lines of Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^

At the top of your main application file, add the tracer initialization:

.. code-block:: python

   # Add these 5 lines at the top of your file
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="your-project")
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Your existing code continues unchanged below...

.. important::
   **Order Matters!** 
   
   The tracer **must** be initialized **before** calling ``instrumentor.instrument()``.
   The instrumentor needs the tracer provider to route traces correctly.
   
   ✅ **Correct:**
   
   .. code-block:: python
   
      tracer = HoneyHiveTracer.init(...)       # 1. Initialize tracer first
      instrumentor.instrument(tracer_provider=tracer.provider)  # 2. Then instrument
   
   ❌ **Wrong:**
   
   .. code-block:: python
   
      instrumentor.instrument()  # This won't work - no tracer provider!
      tracer = HoneyHiveTracer.init(...)  # Too late

Step 3: Run Your Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

That's it! Your existing LLM calls are now automatically traced.

.. code-block:: bash

   python your_app.py

Check https://app.honeyhive.ai to see your traces.

Before & After Examples
-----------------------

Example 1: Simple Chatbot
^^^^^^^^^^^^^^^^^^^^^^^^^

**Before** (no tracing):

.. code-block:: python

   import openai
   
   client = openai.OpenAI()
   
   def chat(message):
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": message}]
       )
       return response.choices[0].message.content
   
   if __name__ == "__main__":
       result = chat("Hello, how are you?")
       print(result)

**After** (with tracing):

.. code-block:: python

   import openai
   # ✨ Add these 5 lines
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="chatbot")
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   # End of changes ✨
   
   client = openai.OpenAI()
   
   def chat(message):
       # This function is unchanged - automatic tracing!
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": message}]
       )
       return response.choices[0].message.content
   
   if __name__ == "__main__":
       result = chat("Hello, how are you?")
       print(result)

**Changes made:** 5 lines added at the top. Zero changes to existing logic.

Example 2: RAG Pipeline
^^^^^^^^^^^^^^^^^^^^^^^

**Before** (no tracing):

.. code-block:: python

   import anthropic
   
   def rag_query(question, context_docs):
       """RAG pipeline with Anthropic Claude."""
       client = anthropic.Anthropic()
       
       # Build context from documents
       context = "\n\n".join(context_docs)
       prompt = f"Context:\n{context}\n\nQuestion: {question}"
       
       # Generate answer
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=1000,
           messages=[{"role": "user", "content": prompt}]
       )
       
       return response.content[0].text

**After** (with tracing):

.. code-block:: python

   import anthropic
   # ✨ Add tracing
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   
   tracer = HoneyHiveTracer.init(api_key="your-key", project="rag-system")
   instrumentor = AnthropicInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   # End of changes ✨
   
   def rag_query(question, context_docs):
       """RAG pipeline with Anthropic Claude - now traced!"""
       client = anthropic.Anthropic()
       
       # Build context from documents (traced automatically)
       context = "\n\n".join(context_docs)
       prompt = f"Context:\n{context}\n\nQuestion: {question}"
       
       # Generate answer (traced automatically)
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=1000,
           messages=[{"role": "user", "content": prompt}]
       )
       
       return response.content[0].text

**Changes made:** 5 lines added. RAG logic unchanged.

Using Environment Variables (Production)
----------------------------------------

For production deployments, use environment variables instead of hardcoded keys:

**1. Create .env file:**

.. code-block:: bash

   HH_API_KEY=your-honeyhive-key
   HH_PROJECT=production-app
   HH_SOURCE=production
   OPENAI_API_KEY=your-openai-key

**2. Update your code:**

.. code-block:: python

   import openai
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from dotenv import load_dotenv
   
   # Load environment variables
   load_dotenv()
   
   # Initialize tracer (reads HH_API_KEY, HH_PROJECT, HH_SOURCE from env)
   tracer = HoneyHiveTracer.init()
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Your existing code...

**3. Install python-dotenv:**

.. code-block:: bash

   pip install python-dotenv

What Gets Traced Automatically?
-------------------------------

Once the instrumentor is initialized, these are traced automatically:

**OpenAI:**

- ``client.chat.completions.create()``
- ``client.completions.create()``
- ``client.embeddings.create()``
- Streaming calls
- Function calling
- Vision API calls

**Anthropic:**

- ``client.messages.create()``
- Streaming responses
- Tool use / function calling

**Google AI:**

- ``model.generate_content()``
- Multi-turn conversations
- Streaming

See :doc:`/how-to/integrations/openai` for provider-specific details.

Alternative: Using @trace Decorator (Non-Instrumentor Pattern)
---------------------------------------------------------------

If you prefer more control or your framework isn't supported by instrumentors, use the ``@trace`` decorator instead:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import openai
   
   # Initialize tracer (no instrumentor needed)
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="your-project"
   )
   
   # Manually trace specific functions with @trace decorator
   @trace(event_type="tool", event_name="chat_completion", tracer=tracer)
   def chat_with_llm(message: str) -> str:
       """Manually traced LLM call."""
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": message}]
       )
       return response.choices[0].message.content
   
   # Use it normally
   result = chat_with_llm("Hello!")
   print(result)

**When to use @trace decorator:**

- ✅ You want fine-grained control over what gets traced
- ✅ Your framework/library doesn't have an instrumentor
- ✅ You're building custom integrations
- ✅ You need to trace non-LLM functions (business logic, tool calls, etc.)

**When to use instrumentors:**

- ✅ You want automatic tracing with zero code changes to LLM calls
- ✅ Your provider has an instrumentor (OpenAI, Anthropic, Google, Bedrock, etc.)
- ✅ You want to trace all LLM calls without manually decorating functions

.. note::
   **You can use both together!** Instrumentors for automatic LLM tracing + ``@trace`` for custom logic.
   
   See :doc:`/reference/api/decorators` for more details on the ``@trace`` decorator.

Multiple Providers in One Application
-------------------------------------

If you use multiple LLM providers, initialize multiple instrumentors:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   
   # Initialize tracer once
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="multi-provider-app"
   )
   
   # Initialize all instrumentors with same tracer
   openai_instrumentor = OpenAIInstrumentor()
   anthropic_instrumentor = AnthropicInstrumentor()
   
   openai_instrumentor.instrument(tracer_provider=tracer.provider)
   anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Now both OpenAI and Anthropic calls are traced!

Verifying Traces
----------------

After adding tracing, verify it's working:

**1. Run your application normally**

.. code-block:: bash

   python your_app.py

**2. Check HoneyHive dashboard**

- Go to https://app.honeyhive.ai
- Select your project
- Click "Traces"
- You should see traces appearing within 1-2 seconds

**3. Check trace details**

Each trace should show:

- Model used (e.g., ``gpt-3.5-turbo``)
- Input prompts/messages
- Output responses
- Token counts
- Latency
- Cost (if using instrumentors that support cost tracking)

Performance Impact
------------------

Tracing overhead is minimal:

- **Latency**: <5ms added per LLM call
- **Memory**: <1MB per trace
- **Network**: Async batch export (no blocking)

Traces are exported in batches asynchronously, so they don't block your application.

Common Patterns
---------------

**Pattern 1: Conditional Tracing**

Only trace in certain environments:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Only trace in production/staging
   if os.getenv("ENABLE_TRACING", "false") == "true":
       tracer = HoneyHiveTracer.init()
       instrumentor = OpenAIInstrumentor()
       instrumentor.instrument(tracer_provider=tracer.provider)
       print("✅ Tracing enabled")

**Pattern 2: Multiple Projects**

Route different parts of your app to different projects:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Main app tracer
   main_tracer = HoneyHiveTracer.init(project="main-app")
   
   # Experimental features tracer  
   experimental_tracer = HoneyHiveTracer.init(project="experiments")
   
   # Initialize instrumentor (will capture all OpenAI calls)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=main_tracer.provider)
   
   # Use @trace decorator to route to specific projects
   @trace(tracer=main_tracer)
   def main_feature(prompt: str):
       client = openai.OpenAI()
       return client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}]
       )
   
   @trace(tracer=experimental_tracer)
   def experimental_feature(prompt: str):
       client = openai.OpenAI()
       return client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )

.. note::
   For more details on multi-instance patterns, see :doc:`04-configure-multi-instance`.

Troubleshooting
---------------

**Traces not appearing:**

- Check ``HH_API_KEY`` is set correctly
- Verify project name matches
- Wait 2-3 seconds for processing
- Check for error messages in console

**Import errors:**

.. code-block:: bash

   # Make sure you installed the right extra
   pip install honeyhive[openinference-openai]

**Performance issues:**

- Traces are batched and async - they shouldn't block
- If you see slowness, check your network connection
- Contact support if latency is >10ms per call

Next Steps
----------

Now that tracing is integrated:

- :doc:`03-enable-span-enrichment` - Add custom metadata to traces
- :doc:`/how-to/advanced-tracing/span-enrichment` - Advanced enrichment patterns
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns
- :doc:`/how-to/deployment/production` - Production deployment best practices

**Time to integrate:** 5 minutes ⏱️  
**Time to value:** Immediate visibility into LLM calls ✨

