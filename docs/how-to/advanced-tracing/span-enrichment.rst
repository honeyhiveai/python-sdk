Span Enrichment Patterns
========================

**Problem:** You need to add rich context, business metadata, and performance metrics to your traces to make them useful for debugging, analysis, and business intelligence.

**Solution:** Use these 5 proven span enrichment patterns to transform basic traces into powerful observability data.

This guide covers advanced enrichment techniques beyond the basics. For an introduction, see :doc:`/tutorials/03-enable-span-enrichment`.

Session-Level vs Span-Level Enrichment
---------------------------------------

HoneyHive provides two enrichment scopes: **session-level** and **span-level**.

**``enrich_session()`` - Apply metadata to all spans in a session:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(project="my-app")
   
   # Apply to ALL spans in this session
   tracer.enrich_session({
       "user_id": "user_456",
       "user_tier": "enterprise",
       "environment": "production",
       "deployment_region": "us-east-1"
   })
   
   # All subsequent operations inherit this metadata
   response1 = call_llm(...)
   response2 = call_llm(...)
   response3 = call_llm(...)
   # All 3 traces will have user_id, user_tier, environment, deployment_region

**Use ``enrich_session()`` for:**

- ✅ User identification (user_id, email, tier)
- ✅ Session context (session_type, workflow_name)
- ✅ Environment info (environment, region, version)
- ✅ Business context (customer_id, account_type, plan)
- ✅ Any metadata that applies to the entire user session

**``enrich_span()`` - Apply metadata to a single span:**

.. code-block:: python

   from honeyhive import enrich_span
   
   def process_query(query: str, use_cache: bool):
       # Apply to THIS specific span only
       enrich_span({
           "query_length": len(query),
           "cache_enabled": use_cache,
           "model": "gpt-4",
           "temperature": 0.7
       })
       
       return call_llm(query)

**Use ``enrich_span()`` for:**

- ✅ Per-call parameters (model, temperature, max_tokens)
- ✅ Call-specific metrics (input_length, cache_hit, latency)
- ✅ Dynamic metadata (intent_classification, confidence_score)
- ✅ Error details (error_type, retry_count)
- ✅ Any metadata that varies per LLM call

**Example combining both:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Session-level: Set once for the entire user session
   tracer = HoneyHiveTracer.init(
       project="customer-support",
       session_name="support-session-789"
   )
   
   tracer.enrich_session({
       "user_id": "user_456",
       "support_tier": "premium",
       "issue_category": "billing"
   })
   
   # Span-level: Varies per call
   def handle_query(query: str):
       intent = classify_intent(query)
       
       tracer.enrich_span({
           "query_intent": intent,
           "query_length": len(query),
           "model": "gpt-4" if intent == "complex" else "gpt-3.5-turbo"
       })
       
       return generate_response(query)
   
   # Each call has both session + span metadata
   handle_query("How do I change my billing address?")
   handle_query("What's my current balance?")
   handle_query("Can I upgrade my plan?")

**Decision Matrix:**

+------------------------------+-------------------------+-------------------------+
| **Metadata Type**            | **Scope**               | **Method**              |
+==============================+=========================+=========================+
| User ID, email               | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Model name, temperature      | Span (varies)           | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Environment (prod/dev)       | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Cache hit/miss               | Span (per-call)         | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Customer tier                | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Prompt token count           | Span (per-call)         | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+
| Deployment region            | Session (constant)      | ``enrich_session()``    |
+------------------------------+-------------------------+-------------------------+
| Error type/message           | Span (when it occurs)   | ``enrich_span()``       |
+------------------------------+-------------------------+-------------------------+

.. tip::
   **Rule of Thumb:**
   
   If the metadata is the same for all LLM calls in a user session, use ``enrich_session()``.
   If it changes per call, use ``enrich_span()``.

Understanding Enrichment Interfaces
-----------------------------------

``enrich_span()`` supports multiple invocation patterns. Choose the one that fits your use case:

Quick Reference Table
^^^^^^^^^^^^^^^^^^^^^

+----------------------------+----------------------------------+----------------------------------------------+
| Pattern                    | When to Use                      | Backend Namespace                            |
+============================+==================================+==============================================+
| Simple Dict                | Quick metadata                   | ``honeyhive_metadata.*``                     |
+----------------------------+----------------------------------+----------------------------------------------+
| Keyword Arguments          | Concise inline enrichment        | ``honeyhive_metadata.*``                     |
+----------------------------+----------------------------------+----------------------------------------------+
| Reserved Namespaces        | Structured organization          | ``honeyhive_<namespace>.*``                  |
+----------------------------+----------------------------------+----------------------------------------------+
| Mixed Usage                | Combine multiple patterns        | Multiple namespaces                          |
+----------------------------+----------------------------------+----------------------------------------------+

Simple Dict Pattern (New)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from honeyhive import enrich_span
   
   # Pass a dictionary - routes to metadata
   enrich_span({
       "user_id": "user_123",
       "feature": "chat",
       "session": "abc"
   })
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.session = "abc"

Keyword Arguments Pattern (New)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from honeyhive import enrich_span
   
   # Pass keyword arguments - also routes to metadata
   enrich_span(
       user_id="user_123",
       feature="chat",
       session="abc"
   )
   
   # Same backend storage as simple dict

Reserved Namespaces Pattern (Backwards Compatible)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use explicit namespace parameters for organized data:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Explicit namespaces for structured organization
   enrich_span(
       metadata={"user_id": "user_123", "session": "abc"},
       metrics={"latency_ms": 150, "score": 0.95},
       user_properties={"user_id": "user_123", "plan": "premium"},
       feedback={"rating": 5, "helpful": True},
       inputs={"query": "What is AI?"},
       outputs={"answer": "AI is artificial intelligence..."},
       config={"model": "gpt-4", "temperature": 0.7},
       error="Optional error message",
       event_id="evt_unique_identifier"
   )
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.session = "abc"
   # honeyhive_metrics.latency_ms = 150
   # honeyhive_metrics.score = 0.95
   # honeyhive_user_properties.user_id = "user_123"
   # honeyhive_user_properties.plan = "premium"
   # honeyhive_feedback.rating = 5
   # honeyhive_feedback.helpful = True
   # honeyhive_inputs.query = "What is AI?"
   # honeyhive_outputs.answer = "AI is artificial intelligence..."
   # honeyhive_config.model = "gpt-4"
   # honeyhive_config.temperature = 0.7
   # honeyhive_error = "Optional error message"
   # honeyhive_event_id = "evt_unique_identifier"

**Available Namespaces:**

- ``metadata``: Business context (user IDs, features, session info)
- ``metrics``: Numeric measurements (latencies, scores, counts)
- ``user_properties``: User-specific properties (user_id, plan, tier, etc.) - stored in dedicated namespace
- ``feedback``: User or system feedback (ratings, thumbs up/down)
- ``inputs``: Input data to the operation
- ``outputs``: Output data from the operation
- ``config``: Configuration parameters (model settings, hyperparams)
- ``error``: Error messages or exceptions (stored as direct attribute)
- ``event_id``: Unique event identifier (stored as direct attribute)

**Why use namespaces?**

- Organize different data types separately
- Easier to query specific categories in the backend
- Maintain backwards compatibility with existing code
- Clear semantic meaning for different attribute types

Mixed Usage Pattern
^^^^^^^^^^^^^^^^^^^

Combine multiple patterns - later values override earlier ones:

.. code-block:: python

   from honeyhive import enrich_span
   
   # Combine namespaces with kwargs
   enrich_span(
       metadata={"user_id": "user_123"},
       metrics={"score": 0.95, "latency_ms": 150},
       feature="chat",     # Adds to metadata
       priority="high",    # Also adds to metadata
       retries=3           # Also adds to metadata
   )
   
   # Backend storage:
   # honeyhive_metadata.user_id = "user_123"
   # honeyhive_metadata.feature = "chat"
   # honeyhive_metadata.priority = "high"
   # honeyhive_metadata.retries = 3
   # honeyhive_metrics.score = 0.95
   # honeyhive_metrics.latency_ms = 150

Using ``enrich_span_context()`` for Inline Span Creation
----------------------------------------------------------

**New in v1.0+:** When you need to create and enrich a named span without refactoring code into separate functions.

**When to use:**

- ✅ You want explicit named spans for specific code blocks
- ✅ It's hard or impractical to split code into separate functions
- ✅ You need to enrich spans with inputs/outputs immediately upon creation
- ✅ You want clear span boundaries without decorator overhead

**Problem:** Using ``@trace`` decorator requires refactoring code into separate functions:

.. code-block:: python

   # Without decorator - no span created
   def complex_workflow(data):
       # Step 1: Preprocessing
       cleaned = preprocess(data)
       
       # Step 2: Model inference
       result = model.predict(cleaned)
       
       # Step 3: Postprocessing
       final = postprocess(result)
       
       return final
   
   # With decorator - requires splitting into functions
   @trace(event_name="preprocess_step")
   def preprocess(data):
       # preprocessing logic
       pass
   
   @trace(event_name="inference_step")
   def predict(data):
       # inference logic
       pass
   
   @trace(event_name="postprocess_step")
   def postprocess(data):
       # postprocessing logic
       pass

**Solution:** Use ``enrich_span_context()`` to create named spans inline:

.. code-block:: python

   from honeyhive.tracer.processing.context import enrich_span_context
   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(project="my-app")
   
   def complex_workflow(data):
       """Workflow with inline named spans - no refactoring needed!"""
       
       # Step 1: Create span for preprocessing
       with enrich_span_context(
           event_name="preprocess_step",
           inputs={"raw_data_size": len(data)},
           metadata={"stage": "preprocessing"}
       ):
           cleaned = preprocess_data(data)
           tracer.enrich_span(outputs={"cleaned_size": len(cleaned)})
       
       # Step 2: Create span for model inference
       with enrich_span_context(
           event_name="inference_step",
           inputs={"input_shape": cleaned.shape},
           metadata={"model": "gpt-4", "temperature": 0.7}
       ):
           result = model.predict(cleaned)
           tracer.enrich_span(
               outputs={"prediction": result},
               metrics={"confidence": 0.95}
           )
       
       # Step 3: Create span for postprocessing
       with enrich_span_context(
           event_name="postprocess_step",
           inputs={"raw_result": result}
       ):
           final = postprocess(result)
           tracer.enrich_span(outputs={"final_result": final})
       
       return final

**What you get in HoneyHive:**

.. code-block:: text

   📊 complex_workflow [ROOT]
   ├── 🔧 preprocess_step
   │   └── inputs: {"raw_data_size": 1000}
   │   └── outputs: {"cleaned_size": 950}
   │   └── metadata: {"stage": "preprocessing"}
   ├── 🤖 inference_step
   │   └── inputs: {"input_shape": [950, 128]}
   │   └── outputs: {"prediction": "..."}
   │   └── metadata: {"model": "gpt-4", "temperature": 0.7}
   │   └── metrics: {"confidence": 0.95}
   └── ✨ postprocess_step
       └── inputs: {"raw_result": "..."}
       └── outputs: {"final_result": "..."}

**Advantages over decorator approach:**

+----------------------------+----------------------------------+----------------------------------+
| **Aspect**                 | **@trace decorator**             | **enrich_span_context()**        |
+============================+==================================+==================================+
| **Refactoring**            | Must split into functions        | No refactoring needed            |
+----------------------------+----------------------------------+----------------------------------+
| **Code Structure**         | Forces function boundaries       | Flexible inline usage            |
+----------------------------+----------------------------------+----------------------------------+
| **Enrichment Timing**      | After span creation              | On creation + during execution   |
+----------------------------+----------------------------------+----------------------------------+
| **Span Naming**            | Function name or explicit        | Always explicit                  |
+----------------------------+----------------------------------+----------------------------------+
| **Best for**               | Reusable functions               | Inline code blocks               |
+----------------------------+----------------------------------+----------------------------------+

**Real-world example: RAG Pipeline with inline spans**

.. code-block:: python

   from honeyhive.tracer.processing.context import enrich_span_context
   from honeyhive import HoneyHiveTracer, trace
   import openai
   
   tracer = HoneyHiveTracer.init(project="rag-app")
   
   @trace(event_type="chain", event_name="rag_query")
   def rag_query(query: str, context_docs: list) -> str:
       """RAG pipeline with explicit span boundaries."""
       
       # Span 1: Document retrieval
       with enrich_span_context(
           event_name="retrieve_documents",
           inputs={"query": query, "doc_count": len(context_docs)},
           metadata={"retrieval_method": "semantic_search"}
       ):
           relevant_docs = semantic_search(query, context_docs, top_k=5)
           tracer.enrich_span(
               outputs={"retrieved_count": len(relevant_docs)},
               metrics={"avg_relevance_score": 0.87}
           )
       
       # Span 2: Context building
       with enrich_span_context(
           event_name="build_context",
           inputs={"doc_count": len(relevant_docs)}
       ):
           context = "\n\n".join([doc.content for doc in relevant_docs])
           prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
           tracer.enrich_span(
               outputs={"context_length": len(context), "prompt_length": len(prompt)}
           )
       
       # Span 3: LLM generation (instrumentor creates child spans automatically)
       with enrich_span_context(
           event_name="generate_answer",
           inputs={"prompt_length": len(prompt)},
           metadata={"model": "gpt-4", "max_tokens": 500}
       ):
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-4",
               max_tokens=500,
               messages=[{"role": "user", "content": prompt}]
           )
           answer = response.choices[0].message.content
           tracer.enrich_span(
               outputs={"answer": answer},
               metrics={"completion_tokens": response.usage.completion_tokens}
           )
       
       return answer

**Key benefits:**

- **Clear span boundaries**: Each pipeline stage has an explicit named span
- **No refactoring**: Keep your logic in one function, add spans inline
- **Rich context**: Set inputs/outputs/metadata when creating the span
- **Flexible enrichment**: Can still call ``tracer.enrich_span()`` during execution
- **Works with instrumentors**: Auto-instrumented spans (e.g., OpenAI) become children

.. note::
   **When to use each approach:**
   
   - Use ``@trace`` decorator for **reusable functions** you call multiple times
   - Use ``enrich_span_context()`` for **inline code blocks** that are hard to extract into functions
   - Use ``tracer.enrich_span()`` for **adding metadata** to existing spans (decorator or instrumentor)
   - Use ``tracer.enrich_session()`` for **session-wide metadata** that applies to all spans

Advanced Techniques
-------------------

Conditional Enrichment
^^^^^^^^^^^^^^^^^^^^^^

Only enrich based on conditions:

.. code-block:: python

   def conditional_enrichment(user_tier: str, result: str):
       # Always enrich with tier
       enrich_span({"user_tier": user_tier})
       
       # Only enrich premium users with detailed info
       if user_tier == "premium":
           enrich_span({
               "result_length": len(result),
               "result_word_count": len(result.split()),
               "premium_features_used": True
           })

Structured Enrichment
^^^^^^^^^^^^^^^^^^^^^

Organize related metadata:

.. code-block:: python

   def structured_enrichment(user_data: dict, request_data: dict):
       # User namespace
       enrich_span({
           "user.id": user_data["id"],
           "user.tier": user_data["tier"],
           "user.region": user_data["region"]
       })
       
       # Request namespace
       enrich_span({
           "request.id": request_data["id"],
           "request.priority": request_data["priority"],
           "request.source": request_data["source"]
       })

Best Practices
--------------

**DO:**

- Use dot notation for hierarchical keys (``user.id``, ``request.priority``)
- Enrich early and often throughout function execution
- Include timing information for performance analysis
- Add error context in exception handlers
- Use consistent key naming conventions

**DON'T:**

- Include sensitive data (PII, credentials, API keys)
- Add extremely large values (>10KB per field)
- Use random/dynamic key names
- Over-enrich (100+ fields per span becomes noise)
- Duplicate data already captured by instrumentors

Troubleshooting
---------------

**Enrichment not appearing:**

- Ensure you're calling ``enrich_span()`` within a traced context
- Check that instrumentor is properly initialized
- Verify tracer is sending data to HoneyHive

**Performance impact:**

- Enrichment adds <1ms overhead per call
- Serialize complex objects before enriching
- Use sampling for high-frequency enrichment

Next Steps
----------

- :doc:`custom-spans` - Create custom spans for complex workflows
- :doc:`class-decorators` - Class-level tracing patterns
- :doc:`advanced-patterns` - Session enrichment and distributed tracing
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns

**Key Takeaway:** Span enrichment transforms basic traces into rich observability data that powers debugging, analysis, and business intelligence. Use these 5 patterns as building blocks for your tracing strategy. ✨

