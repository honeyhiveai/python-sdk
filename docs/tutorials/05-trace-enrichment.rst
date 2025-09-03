Trace Enrichment
================

.. note::
   **Tutorial Goal**: Learn how to enrich traces with metrics, feedback, user properties, and custom metadata using ``enrich_session`` and ``enrich_span``.

In this tutorial, you'll learn how to add rich context to your traces to improve observability, analysis, and debugging of your LLM applications.

What You'll Learn
-----------------

- How to use ``enrich_session`` for root-level context
- How to use ``enrich_span`` for event-specific details  
- Adding user feedback and annotations
- Including metrics, scores, and evaluations
- Attaching configuration and metadata
- Best practices for trace enrichment

Prerequisites
-------------

- Complete :doc:`02-basic-tracing` tutorial
- Understanding of decorators and context managers
- HoneyHive SDK installed and configured

Overview of Trace Enrichment
-----------------------------

Trace enrichment allows you to add valuable context to your observability data after the initial trace creation. This is particularly useful for:

- **Real-time feedback**: Adding user ratings or corrections
- **Post-processing metrics**: Evaluation scores calculated after execution
- **Dynamic metadata**: Context that emerges during execution
- **User tracking**: Session-level user properties

.. important::
   **Session vs Span Enrichment**:
   
   - **``enrich_session``**: Adds data to the root session (affects entire trace)
   - **``enrich_span``**: Adds data to the current active span (event-specific)

Setup and Basic Example
------------------------

Let's start with a complete example showing both session and span enrichment:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_session, enrich_span, set_default_tracer
   from honeyhive.models import EventType
   import time
   import random

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       
   )
   set_default_tracer(tracer)

   @trace(event_type=EventType.chain, event_name="chat_completion")
   def complete_chat(user_message: str, user_id: str) -> dict:
       """Process a chat completion with enrichment."""
       
       # Enrich session with user context
       enrich_session({
           "user_properties": {
               "user_id": user_id,
               "subscription_tier": "premium",
               "region": "us-west-2"
           },
           "config": {
               "model": "gpt-4",
               "temperature": 0.7,
               "max_tokens": 500
           }
       })
       
       # Simulate processing
       response = process_message(user_message)
       
       # Add evaluation metrics after processing
       quality_score = evaluate_response(response)
       
       # Enrich the current span with results
       enrich_span({
           "outputs": {"response": response},
           "metrics": {
               "quality_score": quality_score,
               "response_length": len(response),
               "processing_time_ms": time.time() * 1000
           }
       })
       
       return {"response": response, "quality": quality_score}

   @trace(event_type=EventType.tool, event_name="message_processing")
   def process_message(message: str) -> str:
       """Process the user message."""
       # Enrich with input analysis
       enrich_span({
           "inputs": {"message": message},
           "metadata": {
               "message_length": len(message),
               "language": "en",
               "detected_intent": "question"
           }
       })
       
       # Simulate LLM call
       time.sleep(0.1)
       response = f"I understand you're asking: {message}. Here's my response..."
       
       return response

   @trace(event_type=EventType.tool, event_name="response_evaluation")
   def evaluate_response(response: str) -> float:
       """Evaluate response quality."""
       # Simulate evaluation
       score = random.uniform(0.7, 1.0)
       
       enrich_span({
           "inputs": {"response": response},
           "outputs": {"score": score},
           "metrics": {
               "evaluation_method": "llm_judge",
               "confidence": 0.95
           }
       })
       
       return score

   # Example usage
   if __name__ == "__main__":
       result = complete_chat(
           user_message="What is machine learning?",
           user_id="user_123"
       )
       print(f"Result: {result}")

Session-Level Enrichment
------------------------

Use ``enrich_session`` to add context that applies to the entire trace:

.. code-block:: python

   @trace(event_type=EventType.chain, event_name="user_workflow")
   def handle_user_request(user_id: str, request_data: dict):
       """Handle a user request with session context."""
       
       # Add user and session context
       enrich_session({
           "user_properties": {
               "user_id": user_id,
               "account_type": "enterprise",
               "region": "eu-west-1",
               "session_start": time.time()
           },
           "config": {
               "feature_flags": {
                   "new_ui": True,
                   "advanced_analytics": True
               },
               "environment": "production",
               "version": "2.1.0"
           },
           "metadata": {
               "request_source": "web_app",
               "experiment_group": "control"
           }
       })
       
       # Process the request
       return process_workflow(request_data)

   @trace(event_type=EventType.tool, event_name="workflow_step")
   def process_workflow(data: dict):
       """Process workflow step."""
       # This inherits the session context automatically
       return {"status": "completed", "data": data}

Span-Level Enrichment
---------------------

Use ``enrich_span`` to add event-specific context:

.. code-block:: python

   @trace(event_type=EventType.model, event_name="llm_generation")
   def generate_text(prompt: str, model_params: dict) -> str:
       """Generate text with detailed span enrichment."""
       
       # Enrich with input context
       enrich_span({
           "inputs": {
               "prompt": prompt,
               "prompt_length": len(prompt),
               "model_params": model_params
           },
           "config": {
               "provider": "openai",
               "model": model_params.get("model", "gpt-4"),
               "temperature": model_params.get("temperature", 0.7)
           }
       })
       
       # Simulate generation
       start_time = time.time()
       generated_text = f"Generated response for: {prompt[:50]}..."
       duration = time.time() - start_time
       
       # Enrich with output and performance metrics
       enrich_span({
           "outputs": {
               "generated_text": generated_text,
               "text_length": len(generated_text)
           },
           "metrics": {
               "generation_time_ms": duration * 1000,
               "tokens_generated": len(generated_text.split()),
               "cost_estimate": 0.002
           }
       })
       
       return generated_text

Adding User Feedback
--------------------

Enrich traces with user feedback for continuous improvement:

.. code-block:: python

   @trace(event_type=EventType.chain, event_name="recommendation")
   def get_recommendations(user_id: str, query: str) -> list:
       """Get recommendations and collect feedback."""
       
       recommendations = generate_recommendations(query)
       
       # Initial enrichment
       enrich_span({
           "outputs": {"recommendations": recommendations},
           "metadata": {"recommendation_count": len(recommendations)}
       })
       
       return recommendations

   def collect_user_feedback(trace_id: str, feedback_data: dict):
       """Collect and add user feedback to existing trace."""
       
       # This would typically be called from a separate feedback endpoint
       # For tutorial purposes, we'll show the enrichment structure
       feedback_enrichment = {
           "feedback": {
               "user_rating": feedback_data.get("rating"),  # 1-5 stars
               "user_comment": feedback_data.get("comment"),
               "helpful_items": feedback_data.get("helpful_items", []),
               "feedback_timestamp": time.time(),
               "feedback_source": "web_ui"
           },
           "metrics": {
               "user_satisfaction": feedback_data.get("rating", 0) / 5.0,
               "engagement_score": len(feedback_data.get("helpful_items", []))
           }
       }
       
       # In practice, you'd use the HoneyHive API to update the trace
       # This shows the structure of feedback enrichment
       return feedback_enrichment

Error Handling and Enrichment
------------------------------

Enrich traces with error context for better debugging:

.. code-block:: python

   @trace(event_type=EventType.tool, event_name="api_call")
   def call_external_api(endpoint: str, payload: dict) -> dict:
       """Call external API with error enrichment."""
       
       enrich_span({
           "inputs": {
               "endpoint": endpoint,
               "payload_size": len(str(payload))
           },
           "config": {
               "timeout": 30,
               "retry_count": 3
           }
       })
       
       try:
           # Simulate API call
           if random.random() < 0.1:  # 10% chance of failure
               raise Exception("API rate limit exceeded")
           
           result = {"status": "success", "data": "api_response"}
           
           enrich_span({
               "outputs": result,
               "metrics": {
                   "success": True,
                   "response_time_ms": 150
               }
           })
           
           return result
           
       except Exception as e:
           # Enrich with error details
           enrich_span({
               "error": str(e),
               "metadata": {
                   "error_type": type(e).__name__,
                   "error_code": "RATE_LIMIT",
                   "retry_suggested": True
               },
               "metrics": {
                   "success": False,
                   "error_count": 1
               }
           })
           
           raise

Advanced Enrichment Patterns
-----------------------------

**1. Conditional Enrichment**

.. code-block:: python

   @trace(event_type=EventType.tool, event_name="data_processing")
   def process_data(data: list, include_debug: bool = False) -> dict:
       """Process data with conditional enrichment."""
       
       result = {"processed_items": len(data)}
       
       # Always enrich with basic metrics
       enrich_span({
           "inputs": {"item_count": len(data)},
           "outputs": result,
           "metrics": {"processing_efficiency": len(data) / 10.0}
       })
       
       # Conditionally add debug information
       if include_debug:
           enrich_span({
               "metadata": {
                   "debug_mode": True,
                   "detailed_stats": {
                       "memory_usage": "45MB",
                       "cpu_time": "2.3s"
                   }
               }
           })
       
       return result

**2. Dynamic Enrichment Based on Results**

.. code-block:: python

   @trace(event_type=EventType.model, event_name="content_generation")
   def generate_content(topic: str, style: str) -> dict:
       """Generate content with dynamic enrichment."""
       
       content = f"Generated content about {topic} in {style} style"
       word_count = len(content.split())
       
       # Base enrichment
       enrichment = {
           "inputs": {"topic": topic, "style": style},
           "outputs": {"content": content},
           "metrics": {"word_count": word_count}
       }
       
       # Dynamic enrichment based on content length
       if word_count > 100:
           enrichment["metadata"] = {
               "content_category": "long_form",
               "reading_time_minutes": word_count / 200
           }
       elif word_count < 20:
           enrichment["metadata"] = {
               "content_category": "snippet",
               "format": "brief"
           }
       
       enrich_span(enrichment)
       return {"content": content, "stats": {"words": word_count}}

Enrichment Schema Reference
---------------------------

Here's the complete schema for enrichment data:

.. list-table:: Enrichment Attributes
   :header-rows: 1
   :widths: 20 15 50 15

   * - Attribute
     - Type
     - Description
     - Available In
   * - ``config``
     - Object
     - Configuration details, model parameters, feature flags
     - Session & Span
   * - ``feedback``
     - Object
     - User feedback, ratings, annotations
     - Session & Span
   * - ``metrics``
     - Object
     - Performance metrics, scores, evaluations
     - Session & Span
   * - ``metadata``
     - Object
     - Arbitrary metadata, tags, custom fields
     - Session & Span
   * - ``outputs``
     - Object
     - Output data from functions or events
     - Session & Span
   * - ``user_properties``
     - Object
     - User-specific attributes, IDs, subscription info
     - Session Only
   * - ``event_type``
     - String
     - Override the event type (model, tool, chain, session)
     - Span Only
   * - ``inputs``
     - Object
     - Input data for functions or events
     - Span Only
   * - ``error``
     - String
     - Error information and context
     - Span Only

Best Practices
--------------

**1. Structured Data**

.. code-block:: python

   # Good: Structured, queryable data
   enrich_span({
       "metrics": {
           "latency_ms": 245,
           "token_count": 150,
           "cost_usd": 0.003
       },
       "metadata": {
           "model_version": "gpt-4-1106",
           "provider": "openai",
           "region": "us-east-1"
       }
   })
   
   # Avoid: Unstructured strings
   enrich_span({
       "metadata": {
           "info": "latency: 245ms, tokens: 150, cost: $0.003"
       }
   })

**2. Consistent Naming**

.. code-block:: python

   # Use consistent naming conventions
   STANDARD_METRICS = {
       "latency_ms": lambda start, end: (end - start) * 1000,
       "token_count": lambda text: len(text.split()),
       "success_rate": lambda success, total: success / total
   }

**3. Avoid Sensitive Data**

.. code-block:: python

   # Good: Hash or omit sensitive data
   enrich_span({
       "inputs": {
           "user_id_hash": hash_user_id(user_id),
           "query_length": len(query)
       }
   })
   
   # Avoid: Including raw sensitive data
   enrich_span({
       "inputs": {
           "user_email": "user@example.com",
           "api_key": "sk-..."
       }
   })

Common Use Cases
----------------

**1. A/B Testing**

.. code-block:: python

   @trace(event_type=EventType.chain, event_name="recommendation_engine")
   def recommend(user_id: str, algorithm_version: str):
       """Recommendation with A/B test tracking."""
       
       enrich_session({
           "metadata": {
               "experiment": "recommendation_v2",
               "variant": algorithm_version,
               "test_group": hash(user_id) % 2
           }
       })
       
       recommendations = get_recommendations(user_id, algorithm_version)
       
       enrich_span({
           "metrics": {
               "recommendation_count": len(recommendations),
               "algorithm_version": algorithm_version
           }
       })
       
       return recommendations

**2. Performance Monitoring**

.. code-block:: python

   @trace(event_type=EventType.model, event_name="model_inference")
   def run_inference(model_name: str, input_data: dict):
       """Model inference with performance tracking."""
       
       start_time = time.time()
       start_memory = get_memory_usage()
       
       result = execute_model(model_name, input_data)
       
       end_time = time.time()
       end_memory = get_memory_usage()
       
       enrich_span({
           "metrics": {
               "inference_time_ms": (end_time - start_time) * 1000,
               "memory_delta_mb": end_memory - start_memory,
               "throughput_items_per_sec": 1 / (end_time - start_time)
           },
           "config": {
               "model_name": model_name,
               "batch_size": len(input_data.get("items", []))
           }
       })
       
       return result

What's Next?
------------

You've learned how to enrich traces with valuable context! Next steps:

- :doc:`../how-to/advanced-tracing/index` - Advanced tracing patterns
- :doc:`../how-to/evaluation/index` - Setting up automated evaluations
- :doc:`../how-to/monitoring/index` - Monitoring and alerting on enriched data

Key Takeaways
-------------

- **Use enrich_session** for user context and configuration that applies to the entire trace
- **Use enrich_span** for event-specific metrics, outputs, and metadata
- **Structure your data** for better querying and analysis
- **Add enrichment progressively** as you learn what data is most valuable
- **Consider privacy** when enriching with user data
- **Use consistent schemas** across your application for better analytics

Trace enrichment transforms basic observability into powerful insights that drive continuous improvement of your LLM applications!
