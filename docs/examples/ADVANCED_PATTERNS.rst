Advanced Patterns
=================

Complex use cases and best practices for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Custom Instrumentors
--------------------

Custom OpenInference Instrumentor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from openinference.instrumentation.base import BaseInstrumentor
   from opentelemetry import trace

   class CustomAIInstrumentor(BaseInstrumentor):
       def __init__(self, service_name="custom-ai"):
           self.service_name = service_name
           self._is_instrumented = False
       
       def instrument(self, **kwargs):
           if self._is_instrumented:
               return
           
           # Custom instrumentation logic
           self._instrument_custom_ai()
           self._is_instrumented = True
       
       def _instrument_custom_ai(self):
           """Instrument custom AI operations."""
           # Implementation details
           pass

   # Usage
   tracer = HoneyHiveTracer.init(
       instrumentors=[CustomAIInstrumentor("my-ai-service")]
   )

Conditional Instrumentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class ConditionalInstrumentor:
       def __init__(self, condition_func):
           self.condition_func = condition_func
           self.instrumentors = []
       
       def add_instrumentor(self, instrumentor):
           self.instrumentors.append(instrumentor)
       
       def instrument(self):
           if self.condition_func():
               for instrumentor in self.instrumentors:
                   instrumentor.instrument()

   # Usage
   def should_instrument():
       return os.getenv("ENVIRONMENT") == "production"

   conditional = ConditionalInstrumentor(should_instrument)
   conditional.add_instrumentor(OpenAIInstrumentor())
   conditional.instrument()

Advanced Span Management
------------------------

Span Context Propagation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from opentelemetry import context, trace

   def propagate_context_to_thread():
       """Propagate span context to a new thread."""
       
       with tracer.start_span("parent-operation") as parent_span:
           # Get current context
           ctx = context.get_current()
           
           def worker_function():
               # Attach context to new thread
               context.attach(ctx)
               
               with tracer.start_span("worker-operation") as worker_span:
                   worker_span.set_attribute("thread.id", threading.get_ident())
                   # Worker logic here
                   pass
           
           # Start worker thread
           thread = threading.Thread(target=worker_function)
           thread.start()
           thread.join()

Span Batching
~~~~~~~~~~~~~

.. code-block:: python

   from opentelemetry.sdk.trace.export import BatchSpanProcessor

   def setup_batch_processing():
       """Setup batch span processing for performance."""
       
       # Create batch processor
       batch_processor = BatchSpanProcessor(
           exporter=your_exporter,
           max_queue_size=1000,
           max_export_batch_size=100,
           schedule_delay_millis=5000
       )
       
       # Add to provider
       provider.add_span_processor(batch_processor)

Performance Optimization
------------------------

Span Batching
~~~~~~~~~~~~~

Efficient span processing:

.. code-block:: python

   def optimize_span_processing():
       """Optimize span processing for high-throughput applications."""
       
       # Configure batch processing
       batch_config = {
           "max_queue_size": 10000,
           "max_export_batch_size": 500,
           "schedule_delay_millis": 1000
       }
       
       # Create optimized processor
       processor = BatchSpanProcessor(
           exporter=otlp_exporter,
           **batch_config
       )
       
       return processor

Memory Management
~~~~~~~~~~~~~~~~~

Efficient memory usage:

.. code-block:: python

   def optimize_memory_usage():
       """Optimize memory usage for long-running applications."""
       
       # Limit span storage
       max_spans = 1000
       
       # Configure sampling
       sampler = ParentBased(
           root=AlwaysOnSampler(),
           remote_parent_sampled=AlwaysOnSampler(),
           local_parent_sampled=AlwaysOnSampler(),
           remote_parent_not_sampled=AlwaysOffSampler(),
           local_parent_not_sampled=AlwaysOffSampler()
       )
       
       return sampler

Advanced LLM Agent Patterns
----------------------------

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
           
           # Use OpenAI for analysis
           analysis = openai.ChatCompletion.create(
               model="gpt-4",
               messages=[{"role": "user", "content": f"Analyze: {user_query}"}]
           )
           
           # Use Anthropic for generation
           response = anthropic.messages.create(
               model="claude-3-sonnet",
               messages=[{"role": "user", "content": user_query}]
           )
           
           workflow_span.set_attribute("agent.providers_used", ["openai", "anthropic"])
           return response.content[0].text

Advanced Session Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom session handling for complex workflows:

.. code-block:: python

   class AdvancedAgentSession:
       def __init__(self, tracer, session_name: str):
           self.tracer = tracer
           self.session_name = session_name
           self.conversation_history = []
           self.context = {}
       
       def start_conversation(self, user_input: str):
           """Start a new conversation with context."""
           with self.tracer.start_span("session.conversation_start") as span:
               span.set_attribute("session.name", self.session_name)
               span.set_attribute("session.input", user_input)
               
               # Initialize conversation context
               self.context["start_time"] = time.time()
               self.context["user_input"] = user_input
               
               return self.context
       
       def add_interaction(self, role: str, content: str, metadata: dict = None):
           """Add an interaction to the conversation."""
           with self.tracer.start_span("session.add_interaction") as span:
               interaction = {
                   "role": role,
                   "content": content,
                   "timestamp": time.time(),
                   "metadata": metadata or {}
               }
               
               self.conversation_history.append(interaction)
               span.set_attribute("session.interaction_count", len(self.conversation_history))
               span.set_attribute("session.role", role)
               
               return interaction
