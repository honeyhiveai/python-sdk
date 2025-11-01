Enable Span Enrichment
======================

**Problem:** You have traces in HoneyHive but want to add custom business context, user IDs, or metadata to make them more useful for debugging and analysis.

**Solution:** Use ``enrich_span()`` to add custom key-value metadata to any trace, giving you rich context for every LLM call.

This guide shows you the basics of span enrichment. For advanced patterns, see :doc:`/how-to/advanced-tracing/span-enrichment`.

What is Span Enrichment?
------------------------

Span enrichment lets you add custom metadata to traces:

**Without enrichment:**

- Model: ``gpt-3.5-turbo``
- Latency: 1.2s
- Tokens: 150

**With enrichment:**

- Model: ``gpt-3.5-turbo``
- Latency: 1.2s
- Tokens: 150
- **user_id**: ``user_12345``
- **feature**: ``chat_support``
- **intent**: ``question_answering``
- **priority**: ``high``

This context makes it easy to:

- Filter traces by user, feature, or intent
- Debug issues for specific customers
- Analyze performance by use case
- Track business metrics alongside technical metrics

Prerequisites
-------------

- HoneyHive tracer initialized (see :doc:`01-setup-first-tracer`)
- Basic understanding of Python decorators
- An instrumented LLM application

Basic Enrichment
----------------

The simplest way to enrich spans is with ``enrich_span()``:

.. code-block:: python

   from honeyhive import enrich_span
   import openai
   
   client = openai.OpenAI()
   
   # Add metadata to the current span
   enrich_span({
       "user_id": "user_12345",
       "feature": "chat_support",
       "environment": "production"
   })
   
   # Make LLM call (metadata is automatically attached)
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

**Result:** The trace includes your custom metadata.

.. note::
   The simple dict pattern shown above automatically routes your metadata to the ``honeyhive_metadata`` namespace in the backend.

Enrichment Interfaces
---------------------

``enrich_span()`` supports multiple invocation patterns to fit your needs:

Pattern 1: Simple Dictionary (New)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass a single dictionary for quick metadata enrichment:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Simple dict - routes to metadata namespace
   enrich_span({
       "user_id": "user_12345",
       "feature": "chat",
       "session": "abc123"
   })

Pattern 2: Keyword Arguments (New)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass arbitrary keyword arguments - perfect for concise enrichment:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Arbitrary kwargs - also route to metadata namespace
   enrich_span(
       user_id="user_12345",
       feature="chat",
       session="abc123"
   )

Pattern 3: Reserved Namespaces (Backwards Compatible)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use explicit namespace parameters for structured data organization:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Reserved namespaces provide structured organization
   enrich_span(
       metadata={"user_id": "user_12345", "session": "abc123"},
       metrics={"latency_ms": 150, "tokens": 50, "score": 0.95},
       feedback={"rating": 5, "helpful": True},
       inputs={"query": "What is AI?"},
       outputs={"answer": "AI is..."},
       config={"model": "gpt-4", "temperature": 0.7},
       error="Rate limit exceeded",  # Optional error string
       event_id="evt_unique_123"     # Optional event identifier
   )





**Available namespaces:**

- ``metadata``: Custom business context (user IDs, features, etc.)
- ``metrics``: Numeric measurements (scores, latencies, counts)
- ``feedback``: User or system feedback (ratings, flags)
- ``inputs``: Input data to the operation
- ``outputs``: Output data from the operation  
- ``config``: Configuration parameters (model settings, etc.)
- ``error``: Error messages or exceptions (string)
- ``event_id``: Unique event identifier (string)

Each namespace (except ``error`` and ``event_id``) creates nested attributes in the backend:

- ``metadata`` → ``honeyhive_metadata.*``
- ``metrics`` → ``honeyhive_metrics.*``
- ``feedback`` → ``honeyhive_feedback.*``
- ``inputs`` → ``honeyhive_inputs.*``
- ``outputs`` → ``honeyhive_outputs.*``
- ``config`` → ``honeyhive_config.*``
- ``error`` → ``honeyhive_error`` (direct attribute)
- ``event_id`` → ``honeyhive_event_id`` (direct attribute)


**When to use namespaces:**

- Organize different types of data separately
- Make it easier to query specific data categories in the backend
- Maintain backwards compatibility with existing code

Pattern 4: Mixed Usage
^^^^^^^^^^^^^^^^^^^^^^

You can combine patterns - later values override earlier ones:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Combine namespaces with kwargs
   enrich_span(
       metadata={"user_id": "user_12345"},
       metrics={"score": 0.95},
       feature="chat",        # Adds to metadata
       priority="high"        # Also adds to metadata
   )
   
   # Result in backend:
   # honeyhive_metadata.user_id = "user_12345"
   # honeyhive_metadata.feature = "chat"  
   # honeyhive_metadata.priority = "high"
   # honeyhive_metrics.score = 0.95

Enrichment in Functions
-----------------------

Add enrichment inside your application functions:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(project="my-app")
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   def process_customer_query(user_id: str, query: str, priority: str):
       """Process a customer support query."""
       
       # Enrich with business context
       enrich_span({
           "user_id": user_id,
           "query_type": "customer_support",
           "priority": priority,
           "query_length": len(query)
       })
       
       # Make LLM call
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a helpful support agent."},
               {"role": "user", "content": query}
           ]
       )
       
       return response.choices[0].message.content
   
   # Usage
   answer = process_customer_query(
       user_id="user_12345",
       query="How do I reset my password?",
       priority="high"
   )

Common Enrichment Patterns
--------------------------

Pattern 1: User Context
^^^^^^^^^^^^^^^^^^^^^^^

Track which users are making which calls:

.. code-block:: python


   def generate_response(user_id: str, message: str):
       enrich_span({
           "user_id": user_id,
           "user_type": get_user_type(user_id),  # e.g., "free", "pro", "enterprise"
           "session_id": get_current_session()
       })

       

       
       
       # LLM call...





Pattern 2: Feature Tracking
^^^^^^^^^^^^^^^^^^^^^^^^^^^


Identify which feature generated each trace:


.. code-block:: python


   def summarize_document(document: str, feature: str):
       enrich_span({
           "feature": feature,  # e.g., "document_summary", "email_draft"
           "document_length": len(document),
           "word_count": len(document.split())
       })

       

       
       
       # LLM call...





Pattern 3: Request Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^


Add HTTP request context in web applications:


.. code-block:: python


   from flask import request
   
   
   @app.route("/api/chat", methods=["POST"])
   def chat_endpoint():
       enrich_span({
           "request_id": request.headers.get("X-Request-ID"),
           "user_agent": request.user_agent.string,
           "ip_address": request.remote_addr,
           "endpoint": "/api/chat"
       })

       

       
       
       # Process chat request...





Pattern 4: Business Metrics
^^^^^^^^^^^^^^^^^^^^^^^^^^^


Track business-relevant information:


.. code-block:: python


   def generate_recommendation(product_id: str, user_id: str):
       enrich_span({
           "product_id": product_id,
           "recommendation_type": "ai_powered",
           "user_segment": get_user_segment(user_id),
           "ab_test_variant": "variant_b"
       })

       

       
       
       # LLM call...





Enrichment Data Types
---------------------


You can enrich with various data types:


.. code-block:: python


   enrich_span({
       # Strings
       "user_id": "user_12345",
       "feature": "chat",

       

       
       
       # Numbers
       "priority_score": 8.5,
       "retry_count": 3,

       

       
       
       # Booleans
       "is_premium_user": True,
       "cache_hit": False,

       

       
       
       # Lists (converted to JSON)
       "tags": ["support", "billing", "urgent"],
       "model_fallback_order": ["gpt-4", "gpt-3.5-turbo"],

       

       
       
       # Nested dicts (converted to JSON)
       "user_metadata": {
           "tier": "pro",
           "region": "us-east"
       }
   })





.. note::
   Complex objects are automatically serialized to JSON strings for storage.





Timing Enrichment
-----------------


Add timing information to understand performance:


.. code-block:: python


   import time
   from honeyhive import enrich_span

   

   
   
   def process_with_timing(data: str):
       start_time = time.time()

       

       
       
       # Preprocessing
       preprocessed = preprocess(data)
       preprocess_time = time.time() - start_time

       

       
       
       # LLM call
       llm_start = time.time()
       result = make_llm_call(preprocessed)
       llm_time = time.time() - llm_start

       

       
       
       # Postprocessing
       postprocess_start = time.time()
       final_result = postprocess(result)
       postprocess_time = time.time() - postprocess_start

       

       
       
       # Enrich with timing breakdown
       enrich_span({
           "preprocess_time_ms": round(preprocess_time * 1000, 2),
           "llm_time_ms": round(llm_time * 1000, 2),
           "postprocess_time_ms": round(postprocess_time * 1000, 2),
           "total_time_ms": round((time.time() - start_time) * 1000, 2)
       })

       

       
       
       return final_result





Error Context Enrichment
------------------------


Add error context when things go wrong:


.. code-block:: python


   from honeyhive import enrich_span
   import openai

   

   
   
   def make_llm_call_with_error_handling(prompt: str):
       try:
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": prompt}]
           )

           

           
           
           # Success enrichment
           enrich_span({
               "status": "success",
               "response_length": len(response.choices[0].message.content)
           })

           

           
           
           return response.choices[0].message.content

           

           
           
       except openai.RateLimitError as e:
           # Error enrichment
           enrich_span({
               "status": "error",
               "error_type": "rate_limit",
               "error_message": str(e),
               "retry_after": e.response.headers.get("Retry-After")
           })
           raise

           

           
           
       except openai.APIError as e:
           enrich_span({
               "status": "error",
               "error_type": "api_error",
               "error_message": str(e),
               "status_code": e.status_code
           })
           raise





Best Practices
--------------


**DO:**


- Use consistent key names across your application
- Add user/session IDs for debugging
- Include feature/endpoint identifiers
- Enrich with business-relevant context
- Use descriptive key names (``user_id`` not ``uid``)


**DON'T:**


- Include sensitive data (passwords, API keys, PII)
- Add massive data (>1KB per field)
- Use random/generated key names
- Duplicate data already captured by instrumentors


Viewing Enriched Data
---------------------


In the HoneyHive dashboard:


1. Go to your project's Traces view
2. Click on any trace
3. Look for the "Metadata" or "Attributes" section
4. Your enriched data appears as key-value pairs


You can also:


- Filter traces by enriched metadata
- Create dashboards using enriched fields
- Set up alerts based on custom metadata


Complete Example
----------------


Here's a complete application with enrichment:


.. code-block:: python


   """
   enriched_app.py - Application with span enrichment







   from honeyhive import HoneyHiveTracer, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import time

   

   
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="enriched-app"
   )
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   

   
   
   def analyze_sentiment(text: str, user_id: str, feature: str):
       """Analyze sentiment with rich tracing context."""
       start_time = time.time()

       

       
       
       # Enrich with business context
       enrich_span({
           "user_id": user_id,
           "feature": feature,
           "input_length": len(text),
           "word_count": len(text.split()),
           "timestamp": time.time()
       })

       

       
       
       try:
           # Make LLM call
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "system", "content": "Analyze sentiment: positive, negative, or neutral"},
                   {"role": "user", "content": text}
               ]
           )

           

           
           
           result = response.choices[0].message.content

           

           
           
           # Enrich with success metrics
           enrich_span({
               "status": "success",
               "sentiment": result.lower(),
               "processing_time_ms": round((time.time() - start_time) * 1000, 2)
           })

           

           
           
           return result

           

           
           
       except Exception as e:
           # Enrich with error context
           enrich_span({
               "status": "error",
               "error_type": type(e).__name__,
               "error_message": str(e)
           })
           raise

   

   
   
   if __name__ == "__main__":
       result = analyze_sentiment(
           text="This product is amazing!",
           user_id="user_789",
           feature="product_reviews"
       )
       print(f"Sentiment: {result}")





Next Steps
----------


You now know the basics of span enrichment. For more advanced patterns:


- :doc:`/how-to/advanced-tracing/span-enrichment` - 5+ advanced enrichment patterns
- :doc:`/how-to/advanced-tracing/custom-spans` - Create custom spans with decorators
- :doc:`/how-to/advanced-tracing/class-decorators` - Class-level tracing patterns
- :doc:`04-configure-multi-instance` - Multiple tracers for different use cases


**Quick start:** Add ``enrich_span()`` calls in your existing functions to start adding context to your traces immediately! ✨




