Basic Usage Patterns
====================

Getting started and common usage patterns for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Initialization Patterns
-----------------------

1. Primary Pattern (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the official SDK pattern for production code:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Official SDK pattern (recommended)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # Use the tracer instance directly
   with tracer.start_span("my-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       # Your operation here

   # With HTTP tracing enabled
   tracer = HoneyHiveTracer(
       api_key="your-api-key",
       project="my-project",
       source="production",
       disable_http_tracing=False
   )

1.1. Multiple Tracers Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create multiple tracers for different workflows:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-api-key",
       project="production-app",
       source="prod"
   )
   
   # Development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-api-key",
       project="development-app",
       source="dev"
   )
   
   # Testing tracer
   test_tracer = HoneyHiveTracer.init(
       api_key="test-api-key",
       project="testing-app",
       source="test"
   )
   
   # Each tracer operates independently
   with prod_tracer.start_span("prod-operation") as span:
       # Production tracing
       pass
   
   with dev_tracer.start_span("dev-operation") as span:
       # Development tracing
       pass

1.2. Enhanced Pattern with Instrumentors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced use cases with additional options:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Enhanced initialization with all features available
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       test_mode=True,  # Test mode support
       instrumentors=[OpenAIInstrumentor()],  # Auto-integration
       disable_http_tracing=True  # Performance control
   )

.. note::

   The new multi-instance pattern provides better flexibility and follows modern Python best practices. Each tracer instance is independent and can be configured differently for various use cases.

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use environment variables for configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   # Set environment variables
   os.environ["HH_API_KEY"] = "your-api-key"
   os.environ["HH_PROJECT"] = "my-project"
   os.environ["HH_SOURCE"] = "production"

   # Initialize tracer (automatically reads environment)
   tracer = HoneyHiveTracer.init()

Conditional Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialize based on environment or configuration:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   def create_tracer():
       """Create tracer based on environment."""
       
       if os.getenv("ENVIRONMENT") == "production":
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="production"
           )
       else:
           return HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=os.getenv("HH_PROJECT"),
               source="development",
               test_mode=True
           )

Tracing Patterns
----------------

**Decorator Recommendations:**

* **Use `@trace` for new code** - Automatically detects sync/async functions
* **`@atrace` is legacy support** - Only use for existing code that requires it
* **`@trace_class` for class-wide tracing** - Traces all methods automatically

1. Basic Tracing
~~~~~~~~~~~~~~~~

Simple function tracing:

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
       return f"Generated: {prompt}"

2. Async Function Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic async detection:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   @trace
   async def async_function():
       """This async function will be automatically traced."""
       await asyncio.sleep(1)
       return "Async result"

   # With custom attributes
   @trace(event_type="llm", event_name="gpt4_completion")
   async def call_gpt4(prompt: str) -> str:
       """Call GPT-4 with custom tracing attributes."""
       response = await openai_client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content

3. Context Manager Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Manual span management:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   with tracer.start_span("custom-operation") as span:
       span.set_attribute("operation.type", "data_processing")
       span.set_attribute("operation.size", 1000)
       
       # Your operation here
       result = process_data()
       
       span.set_attribute("operation.result", result)

Manual Span Management
----------------------

Create and manage spans manually:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   # Start a span
   span = tracer.start_span("manual-operation")
   
   try:
       # Set attributes
       span.set_attribute("operation.type", "manual")
       span.set_attribute("operation.start_time", time.time())
       
       # Your operation here
       result = perform_operation()
       
       # Set result attributes
       span.set_attribute("operation.result", result)
       span.set_attribute("operation.success", True)
       
   except Exception as e:
       # Set error attributes
       span.set_attribute("operation.success", False)
       span.set_attribute("operation.error", str(e))
       span.record_exception(e)
       raise
   
   finally:
       # End the span
       span.end()

Span and Session Enrichment
----------------------------

The HoneyHive SDK provides two powerful approaches for enriching your traces with additional context and metadata.

1. enrich_span - Modern Span Enrichment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The new unified ``enrich_span`` function is the **recommended approach** for most tracing scenarios. It provides flexible usage patterns and rich attribute support.

**Basic Context Manager Pattern:**

.. code-block:: python

   from honeyhive.tracer import enrich_span, HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   # Basic enrichment (backwards compatible)
   with enrich_span("user_session", {"user_id": "123", "action": "query"}):
       process_user_request()

   # Enhanced enrichment with rich attributes including outputs and error handling
   with enrich_span(
       event_type="llm_inference",
       event_name="gpt4_completion",
       inputs={"prompt": "What is AI?", "temperature": 0.7},
       outputs={"response": "AI is artificial intelligence...", "tokens": 145},
       metadata={"model": "gpt-4", "version": "2024-03"},
       metrics={"expected_tokens": 150, "actual_tokens": 145},
       error=None  # Will capture any exceptions that occur
   ):
       try:
           response = llm_client.complete(prompt)
       except Exception as e:
           # Error is automatically captured in span attributes
           raise

**Tracer Instance Methods:**

.. code-block:: python

   # Context manager pattern (backwards compatible with basic_usage.py)
   with tracer.enrich_span("operation_name", {"step": "preprocessing"}):
       preprocess_data()
   
   # Direct method call with outputs and error support
   success = tracer.enrich_span(
       metadata={"stage": "postprocessing"},
       metrics={"latency": 0.1, "tokens": 150},
       outputs={"result": "processed", "quality_score": 0.95},
       error=None  # Set to Exception instance if error occurred
   )

**Global Function with Tracer Parameter:**

.. code-block:: python

   from honeyhive.tracer.otel_tracer import enrich_span

   # Direct call with explicit tracer, outputs and error support
   success = enrich_span(
       metadata={"operation": "batch_processing"},
       metrics={"items_processed": 1000},
       outputs={"success_count": 950, "error_count": 50},
       error=None,  # Set to Exception if batch processing failed
       tracer=my_tracer
   )

**Experiment and A/B Testing Support:**

.. code-block:: python

   with enrich_span(
       event_type="ab_test",
       inputs={"prompt": "Compare these models", "test_data": "sample_input"},
       outputs={"model_a_score": 0.85, "model_b_score": 0.92, "winner": "model_b"},
       config_data={
           "experiment_id": "exp-789",
           "experiment_name": "model_comparison",
           "experiment_variant": "gpt4_turbo",
           "experiment_group": "B",
           "experiment_metadata": {
               "version": "1.2",
               "feature_flags": ["new_prompt", "enhanced_context"]
           }
       },
       error=None  # Captures any experiment execution errors
   ):
       # Automatically sets honeyhive_experiment_* attributes
       try:
           result = run_experiment()
       except Exception as e:
           # Error automatically captured in span attributes
           raise

2. enrich_session - Backend Session Enrichment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``enrich_session`` when you need to store session-level data directly in the HoneyHive backend for immediate availability in the UI.

**Session Data Collection:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   # Enrich session with comprehensive data
   success = tracer.enrich_session(
       session_id="session-123",  # Optional - uses tracer's session if not provided
       metadata={
           "user_id": "user-456",
           "conversation_type": "support",
           "language": "en"
       },
       feedback={
           "rating": 5,
           "helpful": True,
           "feedback_text": "Very helpful response"
       },
       metrics={
           "total_tokens": 1500,
           "duration": 2.5,
           "api_calls": 3
       },
       config={
           "model": "gpt-4",
           "temperature": 0.7,
           "max_tokens": 500
       },
       user_properties={
           "subscription_tier": "premium",
           "region": "us-west"
       }
   )

**User Feedback Collection:**

.. code-block:: python

   # Collect user feedback after conversation
   def collect_feedback(rating: int, helpful: bool, comments: str):
       """Collect and store user feedback."""
       success = tracer.enrich_session(
           feedback={
               "rating": rating,
               "helpful": helpful,
               "comments": comments,
               "timestamp": time.time()
           },
           metrics={
               "feedback_collected": True,
               "feedback_delay": calculate_delay()
           }
       )
       return success

3. Combined Usage Pattern (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use both approaches together for comprehensive observability:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.tracer import enrich_span

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   # Session-level data (persisted to backend)
   tracer.enrich_session(
       metadata={"user_id": "123", "session_type": "chat"},
       config={"model": "gpt-4", "temperature": 0.7}
   )

   # Span-level data (rich context for operations)
   with enrich_span(
       event_type="llm_query",
       inputs={"prompt": "What is AI?"},
       metadata={"step": "preprocessing"}
   ):
       preprocess_query()

   with enrich_span(
       event_type="llm_inference",
       config_data={"model": "gpt-4", "tokens": 150},
       metrics={"latency": 0.8}
   ):
       generate_response()

   # Collect user feedback at session level
   tracer.enrich_session(
       feedback={"rating": 5, "helpful": True}
   )

**When to Use Which:**

.. code-block:: python

   # Use enrich_span for:
   # ✅ Span-level context and attributes
   # ✅ OpenTelemetry-native enrichment
   # ✅ Experiment and A/B testing data
   # ✅ Flexible context manager patterns
   # ✅ Local span enrichment

   # Use enrich_session for:
   # ✅ Backend persistence of session data
   # ✅ User feedback and ratings
   # ✅ Session-scoped metrics
   # ✅ Data immediately available in HoneyHive UI
   # ✅ Cross-span session context

Session Management
------------------

1. Automatic Session Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sessions are created automatically:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Session is created automatically
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production"
   )

   # Session ID is available
   print(f"Session ID: {tracer.session_id}")

2. Custom Session Names
~~~~~~~~~~~~~~~~~~~~~~~

Specify custom session names:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project",
       source="production",
       session_name="user-interaction-123"
   )

   print(f"Custom Session: {tracer.session_name}")

3. Session Context
~~~~~~~~~~~~~~~~~~

Use session context in spans:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   with tracer.start_span("user-action") as span:
       # Session context is automatically included
       span.set_attribute("user.action", "button_click")
       span.set_attribute("user.session", tracer.session_id)

Error Handling
--------------

1. Basic Error Handling
~~~~~~~~~~~~~~~~~~~~~~~

Automatic error tracking:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   @trace
   def function_with_errors():
       """Function that may raise errors."""
       try:
           # Risky operation
           result = risky_operation()
           return result
       except Exception as e:
           # Error is automatically recorded in span
           raise

2. Custom Error Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add custom error information:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-project"
   )

   with tracer.start_span("error-prone-operation") as span:
       try:
           result = risky_operation()
           span.set_attribute("operation.success", True)
           return result
       except ValueError as e:
           span.set_attribute("operation.success", False)
           span.set_attribute("operation.error_type", "ValueError")
           span.set_attribute("operation.error_message", str(e))
           span.record_exception(e)
           raise
       except Exception as e:
           span.set_attribute("operation.success", False)
           span.set_attribute("operation.error_type", type(e).__name__)
           span.set_attribute("operation.error_message", str(e))
           span.record_exception(e)
           raise

Configuration Patterns
----------------------

1. Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use environment variables:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   # Configuration from environment
   config = {
       "api_key": os.environ.get("HH_API_KEY"),
       "project": os.environ.get("HH_PROJECT", "default"),
       "source": os.environ.get("HH_SOURCE", "production"),
       "test_mode": os.environ.get("HH_TEST_MODE", "false").lower() == "true"
   }

   tracer = HoneyHiveTracer.init(**config)

2. Configuration File
~~~~~~~~~~~~~~~~~~~~~

Load from configuration file:

.. code-block:: python

   import yaml
   from honeyhive import HoneyHiveTracer

   def load_config(config_path: str):
       """Load configuration from YAML file."""
       with open(config_path, 'r') as f:
           return yaml.safe_load(f)

   # Load configuration
   config = load_config("honeyhive_config.yml")
   tracer = HoneyHiveTracer.init(**config)

Performance Patterns
--------------------

1. Conditional Tracing
~~~~~~~~~~~~~~~~~~~~~~

Enable tracing based on conditions:

.. code-block:: python

   import os
   from honeyhive.tracer.decorators import trace

   def should_trace():
       """Determine if tracing should be enabled."""
       return os.getenv("ENABLE_TRACING", "true").lower() == "true"

   @trace(enabled=should_trace)
   def conditional_traced_function():
       """This function is only traced when tracing is enabled."""
       return "Conditional result"

2. Sampling
~~~~~~~~~~~

Control tracing volume:

.. code-block:: python

   import random
   from honeyhive.tracer.decorators import trace

   def sampling_function():
       """Sample 10% of operations."""
       return random.random() < 0.1

   @trace(sampled=sampling_function)
   def sampled_function():
       """This function is traced based on sampling."""
       return "Sampled result"

LLM Agent Patterns
------------------

1. Multi-Step Agent Conversations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track complex agent workflows with multiple LLM calls:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize with OpenAI instrumentation
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="my-agent-project",
       instrumentors=[OpenAIInstrumentor()]
   )

   def agent_workflow(user_query: str):
       """Multi-step agent workflow with full tracing."""
       
       with tracer.start_span("agent.workflow") as workflow_span:
           workflow_span.set_attribute("agent.query", user_query)
           
           # Step 1: Intent Analysis
           with tracer.start_span("agent.intent_analysis") as intent_span:
               intent_response = openai.ChatCompletion.create(
                   model="gpt-4",
                   messages=[{"role": "user", "content": f"Analyze intent: {user_query}"}]
               )
               intent_span.set_attribute("agent.intent", intent_response.choices[0].message.content)
           
           # Step 2: Context Retrieval
           with tracer.start_span("agent.context_retrieval") as context_span:
               # Your context retrieval logic here
               context = retrieve_relevant_context(user_query)
               context_span.set_attribute("agent.context_size", len(context))
           
           # Step 3: Response Generation
           with tracer.start_span("agent.response_generation") as response_span:
               final_response = openai.ChatCompletion.create(
                   model="gpt-4",
                   messages=[
                       {"role": "system", "content": f"Context: {context}"},
                       {"role": "user", "content": user_query}
                   ]
               )
               response_span.set_attribute("agent.response_length", len(final_response.choices[0].message.content))
           
           workflow_span.set_attribute("agent.steps_completed", 3)
           return final_response.choices[0].message.content

2. Agent State Management
~~~~~~~~~~~~~~~~~~~~~~~~~

Track agent state across multiple operations:

.. code-block:: python

   class AgentState:
       def __init__(self, tracer):
           self.tracer = tracer
           self.conversation_history = []
           self.current_context = {}
       
       def add_message(self, role: str, content: str):
           """Add message to conversation history with tracing."""
           with self.tracer.start_span("agent.add_message") as span:
               self.conversation_history.append({"role": role, "content": content})
               span.set_attribute("agent.message_count", len(self.conversation_history))
               span.set_attribute("agent.role", role)
               span.set_attribute("agent.content_length", len(content))
       
       def get_context(self):
           """Get current context with tracing."""
           with self.tracer.start_span("agent.get_context") as span:
               span.set_attribute("agent.context_keys", list(self.current_context.keys()))
               return self.current_context.copy()

Evaluation Patterns
-------------------

1. Basic Evaluation
~~~~~~~~~~~~~~~~~~~

Use the `@evaluate` decorator for automatic evaluation:

.. code-block:: python

   from honeyhive.evaluation import evaluate_decorator, ExactMatchEvaluator

   @evaluate_decorator(evaluators=["exact_match", "length"])
   def generate_response(prompt: str) -> str:
       """Generate a response that will be automatically evaluated."""
       return f"Response to: {prompt}"

   # Function is automatically evaluated when called
   result = generate_response("Hello, world!")
   # Evaluation results are automatically captured and stored

2. Custom Evaluators
~~~~~~~~~~~~~~~~~~~~

Create custom evaluation metrics:

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator

   class SentimentEvaluator(BaseEvaluator):
       def evaluate(self, prediction: str, reference: str = None) -> dict:
           """Evaluate sentiment of the prediction."""
           # Your custom evaluation logic here
           sentiment_score = analyze_sentiment(prediction)
           return {"sentiment_score": sentiment_score}

   @evaluate_decorator(evaluators=[SentimentEvaluator()])
   def analyze_text(text: str) -> str:
       return "Positive analysis"

Testing Patterns
----------------

1. Test Configuration
~~~~~~~~~~~~~~~~~~~~~

Configure for testing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   def create_test_tracer():
       """Create tracer configured for testing."""
       return HoneyHiveTracer.init(
           api_key="test-api-key",
           project="test-project",
           source="test",
           test_mode=True,  # Enable test mode
           disable_http_tracing=True  # Disable HTTP tracing in tests
       )

2. Mock Tracer
~~~~~~~~~~~~~~

Use mock tracer for unit tests:

.. code-block:: python

   from unittest.mock import Mock
   from honeyhive.tracer import HoneyHiveTracer

   class MockTracer:
       def __init__(self):
           self.spans = []
       
       def start_span(self, name):
           span = Mock()
           span.name = name
           span.attributes = {}
           self.spans.append(span)
           return span

   # Use in tests
   def test_function():
       tracer = MockTracer()
       # Test with mock tracer
       pass

Best Practices
--------------

1. Initialization
~~~~~~~~~~~~~~~~~

* Use ``HoneyHiveTracer.init()`` for production code
* Set environment variables for configuration
* Enable test mode for development

2. Tracing
~~~~~~~~~~

* Use ``@trace`` decorator for automatic tracing
* Add meaningful span names and attributes
* Handle errors properly in spans

3. Performance
~~~~~~~~~~~~~~

* Use conditional tracing for high-throughput operations
* Implement sampling for large applications
* Monitor span volume and performance impact

4. Testing
~~~~~~~~~~

* Use test mode for development
* Mock tracer for unit tests
* Test error scenarios and edge cases
