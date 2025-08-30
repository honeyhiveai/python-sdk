Bring Your Own Instrumentor
============================

HoneyHive's flexible instrumentor pattern lets you integrate any LLM provider with automatic tracing using OpenInference instrumentors. This approach gives you zero-code-change observability for your AI applications.

.. contents:: Table of Contents
   :local:
   :depth: 2

Why This Approach?
------------------

**Simple Integration**
  Add tracing to existing code without modifications

**No Dependency Conflicts**
  Use any LLM library version you want

**Provider Flexibility**
  Switch between OpenAI, Anthropic, Google, Bedrock easily

**Rich Observability**
  Automatic span creation with detailed metadata through instrumentors

Quick Start
-----------

The pattern is simple: initialize HoneyHive with your chosen instrumentors.

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize tracer with instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       instrumentors=[OpenAIInstrumentor()]
   )

   # Your existing code works unchanged
   import openai
   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   # Automatically traced through OpenInference instrumentor! ✨

How It Works
------------

**OpenInference Instrumentors vs HTTP Tracing**

HoneyHive uses OpenInference instrumentors to trace LLM calls, not HTTP interception:

- **OpenInference Instrumentors**: Trace specific LLM library calls (OpenAI, Anthropic, etc.)
- **HTTP Tracing**: Traces all HTTP requests (disabled by default to reduce noise)

.. code-block:: python

   # This works - LLM calls traced via OpenInference
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="my-project",
       instrumentors=[OpenAIInstrumentor()]  # Enables OpenAI tracing
   )

   # This call is traced by the OpenAI instrumentor
   response = openai_client.chat.completions.create(...)

**Enabling HTTP Tracing (Optional)**

If you need to trace all HTTP requests, set ``disable_http_tracing=False``:

.. code-block:: python

   # Enable HTTP tracing for all requests
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="my-project",
       disable_http_tracing=False,  # Enable HTTP tracing
       instrumentors=[OpenAIInstrumentor()]
   )

.. warning::
   Enabling HTTP tracing will capture ALL HTTP requests in your application, 
   which may create noise. Use instrumentors for targeted LLM tracing instead.

Provider Examples
-----------------

Anthropic
~~~~~~~~~

**Installation:**

.. code-block:: bash

   pip install openinference-instrumentation-anthropic anthropic

**Simple Example:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic

   # Setup
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="anthropic-project",
       instrumentors=[AnthropicInstrumentor()]
   )

   # Use Anthropic normally - automatically traced
   client = anthropic.Anthropic(api_key="your-anthropic-key")
   response = client.messages.create(
       model="claude-3-haiku-20240307",
       max_tokens=100,
       messages=[{
           "role": "user",
           "content": "Explain machine learning in simple terms"
       }]
   )

   print(response.content[0].text)

**Streaming Example:**

.. code-block:: python

   # Streaming responses are also automatically traced
   with client.messages.stream(
       model="claude-3-haiku-20240307",
       max_tokens=100,
       messages=[{"role": "user", "content": "Count from 1 to 10"}]
   ) as stream:
       for text in stream.text_stream:
           print(text, end="", flush=True)

AWS Bedrock
~~~~~~~~~~~

**Installation:**

.. code-block:: bash

   pip install openinference-instrumentation-bedrock boto3

**Simple Example:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.bedrock import BedrockInstrumentor
   import boto3
   import json

   # Setup
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="bedrock-project",
       instrumentors=[BedrockInstrumentor()]
   )

   # Use Bedrock normally - automatically traced
   client = boto3.client("bedrock-runtime", region_name="us-east-1")

   # Claude via Bedrock
   request = {
       "prompt": "\n\nHuman: What is cloud computing?\n\nAssistant:",
       "max_tokens_to_sample": 100,
       "temperature": 0.1
   }

   response = client.invoke_model(
       modelId="anthropic.claude-v2",
       body=json.dumps(request),
       contentType="application/json"
   )

   result = json.loads(response["body"].read())
   print(result["completion"])

**Multiple Models:**

.. code-block:: python

   # Amazon Titan
   titan_request = {
       "inputText": "Explain quantum computing briefly.",
       "textGenerationConfig": {
           "maxTokenCount": 100,
           "temperature": 0.1
       }
   }

   titan_response = client.invoke_model(
       modelId="amazon.titan-text-express-v1",
       body=json.dumps(titan_request),
       contentType="application/json"
   )

   titan_result = json.loads(titan_response["body"].read())
   print(titan_result["results"][0]["outputText"])

Google AI (Gemini)
~~~~~~~~~~~~~~~~~~

**Installation:**

.. code-block:: bash

   pip install openinference-instrumentation-google-generativeai google-generativeai

**Simple Example:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai as genai

   # Setup
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="google-project",
       instrumentors=[GoogleGenerativeAIInstrumentor()]
   )

   # Configure and use Google AI - automatically traced
   genai.configure(api_key="your-google-key")
   model = genai.GenerativeModel('gemini-pro')

   response = model.generate_content("What are the benefits of renewable energy?")
   print(response.text)

**Chat Session:**

.. code-block:: python

   # Chat sessions are automatically traced
   chat = model.start_chat(history=[])
   
   response1 = chat.send_message("Hello! I'm learning about AI.")
   print("AI:", response1.text)
   
   response2 = chat.send_message("What should I learn first?")
   print("AI:", response2.text)

OpenAI
~~~~~~

**Installation:**

.. code-block:: bash

   pip install openinference-instrumentation-openai openai

**Simple Example:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai

   # Setup
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="openai-project",
       instrumentors=[OpenAIInstrumentor()]
   )

   # Use OpenAI normally - automatically traced
   client = openai.OpenAI(api_key="your-openai-key")
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "What is Python?"}]
   )

   print(response.choices[0].message.content)

**Chat Conversation:**

.. code-block:: python

   # Multi-turn conversation - each call automatically traced
   messages = [{"role": "user", "content": "Hello!"}]
   
   for i in range(3):
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=messages
       )
       
       # Add response to conversation
       messages.append({
           "role": "assistant", 
           "content": response.choices[0].message.content
       })
       messages.append({
           "role": "user", 
           "content": f"Tell me more about that. (Turn {i+2})"
       })

Multiple Providers
------------------

Use multiple providers in the same application:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize with multiple instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="multi-provider-project",
       instrumentors=[
           AnthropicInstrumentor(),
           GoogleGenerativeAIInstrumentor(),
           OpenAIInstrumentor()
       ]
   )

   # Now all three providers are automatically traced
   import anthropic
   import google.generativeai as genai
   import openai

   # Anthropic call
   anthropic_client = anthropic.Anthropic()
   anthropic_response = anthropic_client.messages.create(
       model="claude-3-haiku-20240307",
       max_tokens=50,
       messages=[{"role": "user", "content": "Hello from Anthropic!"}]
   )

   # Google AI call
   genai.configure(api_key="your-google-key")
   google_model = genai.GenerativeModel('gemini-pro')
   google_response = google_model.generate_content("Hello from Google!")

   # OpenAI call
   openai_client = openai.OpenAI()
   openai_response = openai_client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello from OpenAI!"}]
   )

Adding Custom Context
---------------------

Enrich your traces with custom spans and metadata:

.. code-block:: python

   # Add custom span around your AI workflow
   with tracer.start_span("ai_workflow") as span:
       span.set_attribute("workflow.type", "content_generation")
       span.set_attribute("user.id", "user123")
       
       # AI calls inside this span inherit the context
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Generate a blog post"}]
       )
       
       span.set_attribute("content.length", len(response.choices[0].message.content))

**Session-Level Metadata:**

.. code-block:: python

   # Enrich the entire session
   tracer.enrich_session(
       metadata={"user_id": "user123", "feature": "content_gen"},
       feedback={"rating": 5},
       metrics={"total_tokens": 150}
   )

Environment Configuration
-------------------------

Set up environment variables for easy configuration:

.. code-block:: bash

   # .env file
   HH_API_KEY=your-honeyhive-api-key
   HH_PROJECT=my-ai-project
   HH_SOURCE=production
   
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Load from environment
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT"),
       source=os.getenv("HH_SOURCE", "development"),
       instrumentors=[OpenAIInstrumentor()]
   )

Error Handling
--------------

Instrumentors automatically capture errors:

.. code-block:: python

   try:
       # This will be traced, including the error
       response = client.chat.completions.create(
           model="invalid-model",  # This will fail
           messages=[{"role": "user", "content": "Hello"}]
       )
   except Exception as e:
       print(f"Error captured in trace: {e}")
       # Error details are automatically added to the span

Best Practices
--------------

**1. Initialize Once**

.. code-block:: python

   # Do this at application startup
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="my-project",
       instrumentors=[OpenAIInstrumentor()]
   )

**2. Use Environment Variables**

.. code-block:: python

   # Keep secrets in environment, not code
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT"),
       instrumentors=[OpenAIInstrumentor()]
   )

**3. Add Context to Important Operations**

.. code-block:: python

   # Wrap important workflows
   with tracer.start_span("user_query_processing") as span:
       span.set_attribute("query.type", "technical_support")
       
       # AI calls here get the context
       response = process_user_query(user_input)

**4. Handle Multiple Environments**

.. code-block:: python

   # Different instrumentors for different environments
   instrumentors = []
   
   if os.getenv("ENABLE_OPENAI"):
       instrumentors.append(OpenAIInstrumentor())
   
   if os.getenv("ENABLE_ANTHROPIC"):
       instrumentors.append(AnthropicInstrumentor())
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT"),
       instrumentors=instrumentors
   )

Usage Patterns
--------------

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use environment variables for flexible configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Set environment variables
   os.environ["HH_API_KEY"] = "your-api-key"
   os.environ["HH_PROJECT"] = "my-project"
   os.environ["HH_SOURCE"] = "production"

   # Initialize tracer (automatically reads environment)
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )

Conditional Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialize based on environment or configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   def create_tracer():
       """Create tracer based on environment."""
       
       instrumentors = [OpenAIInstrumentor()]
       
       if os.getenv("ENVIRONMENT") == "production":
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="production",
               instrumentors=instrumentors
           )
       else:
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="development",
               test_mode=True,
               instrumentors=instrumentors
           )

Multiple Tracers Pattern
~~~~~~~~~~~~~~~~~~~~~~~~

Create multiple tracers for different workflows:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-api-key",
       project="production-app",
       source="prod",
       instrumentors=[OpenAIInstrumentor()]
   )
   
   # Development tracer with different provider
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-api-key",
       project="development-app",
       source="dev",
       instrumentors=[AnthropicInstrumentor()]
   )

Advanced Tracing Patterns
-------------------------

Decorator Tracing
~~~~~~~~~~~~~~~~~

Add custom tracing to your functions:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   @trace
   def simple_function():
       """This function will be automatically traced."""
       return "Hello, World!"

   # With custom attributes
   @trace(event_type="model", event_name="text_generation")
   def generate_text(prompt: str) -> str:
       """Generate text with custom tracing attributes."""
       # Your LLM call here - automatically traced by instrumentor
       response = openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content

   # Async functions work automatically
   @trace(event_type="llm", event_name="gpt4_completion")
   async def call_gpt4(prompt: str) -> str:
       """Call GPT-4 with custom tracing attributes."""
       response = await openai_client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content

Manual Span Management
~~~~~~~~~~~~~~~~~~~~~~

Create and manage spans manually for complex operations:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       instrumentors=[OpenAIInstrumentor()]
   )

   with tracer.start_span("custom-operation") as span:
       span.set_attribute("operation.type", "ai_workflow")
       span.set_attribute("operation.model", "gpt-4")
       
       # Your LLM operations here - automatically traced
       result = openai_client.chat.completions.create(...)
       
       span.set_attribute("operation.result_length", len(result.choices[0].message.content))

Multi-Provider Agent Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate multiple LLM providers in a single agent:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor

   # Initialize with multiple instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="multi-provider-agent",
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor()
       ]
   )

   def multi_provider_agent(user_query: str):
       """Agent that uses multiple LLM providers."""
       
       with tracer.start_span("agent.multi_provider_workflow") as workflow_span:
           workflow_span.set_attribute("agent.query", user_query)
           
           # Use OpenAI for analysis - automatically traced
           analysis = openai_client.chat.completions.create(
               model="gpt-4",
               messages=[{"role": "user", "content": f"Analyze: {user_query}"}]
           )
           
           # Use Anthropic for generation - automatically traced
           response = anthropic_client.messages.create(
               model="claude-3-sonnet-20240229",
               messages=[{"role": "user", "content": user_query}]
           )
           
           workflow_span.set_attribute("agent.providers_used", ["openai", "anthropic"])
           return response.content[0].text

Troubleshooting
---------------

**No Traces Appearing?**

1. **Check your instrumentors**: Ensure the instrumentor for your LLM provider is in the list
2. **Verify API key and project settings**: Make sure HoneyHive credentials are correct
3. **Confirm you're making actual API calls**: Instrumentors only trace real LLM API calls

.. code-block:: python

   # Debug mode with detailed logging
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="debug-project",
       test_mode=True,  # Enable for debugging
       instrumentors=[OpenAIInstrumentor()]  # Must include instrumentor
   )

**Common Issues:**

- **Missing instrumentor**: LLM calls won't be traced without the appropriate instrumentor
- **Wrong provider**: Using OpenAI instrumentor but making Anthropic calls won't work

**Import Errors?**

Install the required packages:

.. code-block:: bash

   # For OpenAI
   pip install openinference-instrumentation-openai openai
   
   # For Anthropic  
   pip install openinference-instrumentation-anthropic anthropic
   
   # For Google AI
   pip install openinference-instrumentation-google-generativeai google-generativeai
   
   # For AWS Bedrock
   pip install openinference-instrumentation-bedrock boto3

Next Steps
----------

- Check the :doc:`examples/README` for more complete applications
- See :doc:`API_REFERENCE` for advanced configuration options  
- Visit the `HoneyHive Dashboard <https://app.honeyhive.ai>`_ to view your traces
