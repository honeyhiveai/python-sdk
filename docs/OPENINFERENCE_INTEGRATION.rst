OpenInference Integration
=========================

Using the HoneyHive SDK with OpenInference instrumentors.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

OpenInference is a collection of instrumentors that automatically trace AI/ML operations across various frameworks and providers. When combined with the HoneyHive SDK, you get seamless observability into your LLM agent applications without modifying your existing code.

**Why This Approach?**

* **No Dependency Conflicts**: We don't force specific LLM library versions
* **Flexible Instrumentation**: Choose exactly what gets traced
* **LLM Agent Focus**: Built for multi-step conversations and agent workflows
* **Rapid Integration**: Add new LLM providers in minutes, not days

Key Benefits
~~~~~~~~~~~~

* **Zero Code Changes** - Automatic instrumentation of AI operations
* **Framework Agnostic** - Works with OpenAI, Anthropic, Google AI, and more
* **Session Context** - Automatic session tracking and correlation
* **Rich Metadata** - Detailed span attributes for AI operations
* **Performance Monitoring** - Built-in latency and token tracking

How It Works
~~~~~~~~~~~~

1. **Initialize HoneyHiveTracer** with OpenInference instrumentors
2. **Instrumentors automatically wrap** AI library calls
3. **Spans are created** for each AI operation
4. **HoneyHive enriches** spans with session context
5. **Data is exported** via OTLP to your backend

LLM Agent Workflows
~~~~~~~~~~~~~~~~~~~

Track multi-step conversations and agent state:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize with OpenAI instrumentation
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-agent-project",
       instrumentors=[OpenAIInstrumentor()]
   )

   # Multi-step agent conversation
   def agent_conversation(user_input: str):
       with tracer.start_span("agent.conversation") as conversation_span:
           conversation_span.set_attribute("agent.input", user_input)
           
           # Step 1: Analyze user intent
           intent_response = openai.ChatCompletion.create(
               model="gpt-4",
               messages=[{"role": "user", "content": f"Analyze intent: {user_input}"}]
           )
           # Automatically traced with conversation context
           
           # Step 2: Generate response
           response = openai.ChatCompletion.create(
               model="gpt-4",
               messages=[
                   {"role": "user", "content": user_input},
                   {"role": "assistant", "content": intent_response.choices[0].message.content}
               ]
           )
           # Also traced with full conversation context
           
           conversation_span.set_attribute("agent.response", response.choices[0].message.content)
           return response.choices[0].message.content

Quick Start
-----------

Basic Integration
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize tracer with OpenInference instrumentor
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production",
       instrumentors=[OpenAIInstrumentor()]
   )

   # OpenInference automatically traces OpenAI calls
   import openai
   response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

Multiple Instrumentors
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor

   # Initialize with multiple instrumentors
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production",
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor()
       ]
   )

Supported Instrumentors
-----------------------

OpenAI
~~~~~~

**Package**: ``openinference-instrumentation-openai``

.. code-block:: python

   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Basic instrumentation
   instrumentor = OpenAIInstrumentor()

   # Advanced configuration
   instrumentor = OpenAIInstrumentor(
       # Custom span names
       span_name_prefix="openai",
       # Custom attributes
       span_attributes={
           "llm.vendor": "openai",
           "llm.request.type": "chat"
       }
   )

Anthropic
~~~~~~~~~

**Package**: ``openinference-instrumentation-anthropic``

.. code-block:: python

   from openinference.instrumentation.anthropic import AnthropicInstrumentor

   # Basic instrumentation
   instrumentor = AnthropicInstrumentor()

   # With custom configuration
   instrumentor = AnthropicInstrumentor(
       span_name_prefix="anthropic",
       span_attributes={
           "llm.vendor": "anthropic"
       }
   )

Google AI
~~~~~~~~~

**Package**: ``openinference-instrumentation-google-generativeai``

.. code-block:: python

   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor

   # Basic instrumentation
   instrumentor = GoogleGenerativeAIInstrumentor()

Integration Patterns
--------------------

1. Application-Level Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate at the application startup:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   def setup_tracing():
       """Setup tracing for the application."""
       
       tracer = HoneyHiveTracer.init(
           api_key=os.environ["HH_API_KEY"],
           project="ai-chat-app",
           source="production",
           instrumentors=[OpenAIInstrumentor()]
       )
       
       return tracer

   # Call at startup
   tracer = setup_tracing()

2. Conditional Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable instrumentation based on environment:

.. code-block:: python

   def get_instrumentors():
       """Get instrumentors based on environment."""
       
       instrumentors = []
       
       if os.getenv("ENABLE_OPENAI_TRACING") == "true":
           from openinference.instrumentation.openai import OpenAIInstrumentor
           instrumentors.append(OpenAIInstrumentor())
       
       if os.getenv("ENABLE_ANTHROPIC_TRACING") == "true":
           from openinference.instrumentation.anthropic import AnthropicInstrumentor
           instrumentors.append(AnthropicInstrumentor())
       
       return instrumentors

   # Use conditionally
   tracer = HoneyHiveTracer.init(
       instrumentors=get_instrumentors()
   )

Advanced Configuration
----------------------

Custom Span Attributes
~~~~~~~~~~~~~~~~~~~~~~

Customize span attributes for better observability:

.. code-block:: python

   from openinference.instrumentation.openai import OpenAIInstrumentor

   class CustomOpenAIInstrumentor(OpenAIInstrumentor):
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           
           # Add custom attributes
           self.span_attributes.update({
               "llm.framework": "openai",
               "llm.version": "latest",
               "custom.tag": "ai-service"
           })

   # Use custom instrumentor
   instrumentor = CustomOpenAIInstrumentor()
   tracer = HoneyHiveTracer.init(
       instrumentors=[instrumentor]
   )

Span Filtering
~~~~~~~~~~~~~~

Filter spans based on custom criteria:

.. code-block:: python

   def should_trace_span(span):
       """Filter spans based on custom logic."""
       
       # Only trace spans with specific attributes
       if span.attributes.get("llm.request.type") == "chat":
           return True
       
       # Skip low-priority operations
       if span.attributes.get("llm.request.tokens", 0) < 10:
           return False
       
       return True

   # Apply filter
   instrumentor = OpenAIInstrumentor(
       span_filter=should_trace_span
   )

Examples
--------

Chat Application
~~~~~~~~~~~~~~~~

Complete chat application with tracing:

.. code-block:: python

   from fastapi import FastAPI
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai

   app = FastAPI()

   # Initialize tracing
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="chat-app",
       source="production",
       instrumentors=[OpenAIInstrumentor()]
   )

   @app.post("/chat")
   async def chat_endpoint(request: dict):
       """Chat endpoint with automatic tracing."""
       
       # OpenInference automatically traces this call
       response = openai.ChatCompletion.create(
           model="gpt-3.5-turbo",
           messages=request["messages"]
       )
       
       return {"response": response.choices[0].message.content}

AI Service
~~~~~~~~~~

Multi-provider AI service:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor

   class AIService:
       def __init__(self):
           # Initialize with multiple instrumentors
           self.tracer = HoneyHiveTracer.init(
               api_key="your-api-key",
               project="ai-service",
               source="production",
               instrumentors=[
                   OpenAIInstrumentor(),
                   AnthropicInstrumentor()
               ]
           )
       
       async def generate_with_openai(self, prompt: str):
           """Generate using OpenAI with automatic tracing."""
           import openai
           
           response = openai.ChatCompletion.create(
               model="gpt-4",
               messages=[{"role": "user", "content": prompt}]
           )
           return response.choices[0].message.content
       
       async def generate_with_anthropic(self, prompt: str):
           """Generate using Anthropic with automatic tracing."""
           import anthropic
           
           client = anthropic.Anthropic(api_key="your-key")
           response = client.messages.create(
               model="claude-3-sonnet-20240229",
               max_tokens=1000,
               messages=[{"role": "user", "content": prompt}]
           )
           return response.content[0].text

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Instrumentor Not Working**
   
   Check if the instrumentor is properly imported and added:
   
   .. code-block:: python
      
      # Make sure instrumentor is in the list
      tracer = HoneyHiveTracer.init(
          instrumentors=[OpenAIInstrumentor()]  # Must be in list
      )

2. **Spans Not Appearing**
   
   Verify OpenTelemetry is properly configured:
   
   .. code-block:: python
      
      # Check if OTLP is enabled
      print(os.environ.get("HH_OTLP_ENABLED"))
      
      # Check if tracing is disabled
      print(os.environ.get("HH_DISABLE_TRACING"))

3. **Missing Attributes**
   
   Ensure instrumentor is configured with proper attributes:
   
   .. code-block:: python
      
      instrumentor = OpenAIInstrumentor(
          span_attributes={
               "llm.vendor": "openai",
               "llm.request.type": "chat"
           }
      )

Debug Mode
~~~~~~~~~~

Enable debug mode for troubleshooting:

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Initialize with debug mode
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="debug-project",
       source="development",
       test_mode=True,  # Enable test mode for debugging
       instrumentors=[OpenAIInstrumentor()]
   )

For more examples, see the :doc:`examples/README` section.
