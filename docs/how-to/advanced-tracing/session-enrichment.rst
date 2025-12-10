Session Enrichment
==================

**Problem:** You need to add metadata, metrics, and context to entire sessions (collections of related spans) for tracking user workflows, experiments, or multi-step operations.

**Solution:** Use ``enrich_session()`` to add session-level metadata that persists across all spans in a session and is stored in the HoneyHive backend.

This guide covers session enrichment patterns. For span-level enrichment, see :doc:`span-enrichment`.

Understanding Session Enrichment
--------------------------------

Session enrichment differs from span enrichment:

**Span Enrichment** (``enrich_span()``):

- Adds metadata to a **single span** (one operation)
- Stored in OpenTelemetry span attributes
- Local to the trace

**Session Enrichment** (``enrich_session()``):

- Adds metadata to an **entire session** (collection of spans)
- **Persisted to HoneyHive backend** via API
- Available for analysis across all spans in the session
- Supports complex nested data structures

Use Cases
---------

Session enrichment is ideal for:

- **User Workflows**: Track user journeys across multiple LLM calls
- **Experiments**: Add experiment parameters and results
- **A/B Testing**: Tag sessions with test variants
- **Business Context**: Add customer IDs, subscription tiers, feature flags
- **Performance Metrics**: Session-level latency, success rates, cost tracking

API Reference
-------------

Function Signature
~~~~~~~~~~~~~~~~~~

.. py:function:: enrich_session(session_id=None, *, metadata=None, inputs=None, outputs=None, config=None, feedback=None, metrics=None, user_properties=None, **kwargs)

   Add metadata and metrics to a session with backend persistence.
   
   .. note::
      **All parameters are optional**: You can call ``enrich_session()`` without any parameters. The function will work correctly as long as a valid session_id is available (either explicitly provided or detected from the active context). This is useful for ensuring a session exists or "touching" it even when you don't have enrichment data to add.
   
   **Parameters:**
   
   :param metadata: Business context data (user IDs, features, session info).
   :type metadata: Optional[Dict[str, Any]]
   
   :param inputs: Input data for the session (e.g., initial query, configuration).
   :type inputs: Optional[Dict[str, Any]]
   
   :param outputs: Output data from the session (e.g., final response, results).
   :type outputs: Optional[Dict[str, Any]]
   
   :param config: Configuration parameters for the session (model settings, hyperparameters).
   :type config: Optional[Dict[str, Any]]
   
   :param feedback: User or system feedback for the session (ratings, quality scores).
   :type feedback: Optional[Dict[str, Any]]
   
   :param metrics: Numeric measurements for the session (latency, cost, token counts).
   :type metrics: Optional[Dict[str, Any]]
   
   :param user_properties: User-specific properties (user_id, plan, etc.). Stored as a separate field in the backend, not merged into metadata.
   :type user_properties: Optional[Dict[str, Any]]

   :param session_id: Explicit session ID to enrich. If not provided, uses the active session from context.
   :type session_id: Optional[str]
   
   :param kwargs: Additional keyword arguments (passed through for extensibility).
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: None
   :returns: None (updates session in backend)
   
   **Raises:**
   
   - No exceptions raised - failures are logged and gracefully handled

**Key Differences from enrich_span:**

1. **Backend Persistence**: ``enrich_session()`` makes API calls to persist data, while ``enrich_span()`` only sets local span attributes
2. **Session Scope**: Affects the entire session, not just the current span
3. **Complex Data**: Supports nested dictionaries and lists
4. **Explicit Session ID**: Can target any session by ID, not just the active one

Basic Usage
-----------

Enrich Active Session
~~~~~~~~~~~~~~~~~~~~~

The simplest usage enriches the currently active session:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   import openai
   
   # Initialize tracer (creates a session automatically)
   tracer = HoneyHiveTracer.init(
       project="my-app",
       session_name="user-123-chat"
   )
   
   # Enrich the active session
   enrich_session(
       metadata={
           "user_id": "user_123",
           "subscription_tier": "premium",
           "feature": "chat_assistant"
       }
   )
   
   # All subsequent traces in this session will be associated with this metadata
   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

.. note::
   **Optional Parameters**: All parameters to ``enrich_session()`` are optional. You can call ``enrich_session()`` without any parameters to ensure the session exists or to "touch" it, even if you don't have enrichment data to add at that moment. The function will work correctly as long as a valid session_id is available (either explicitly provided or detected from the active context).

Enrich Specific Session
~~~~~~~~~~~~~~~~~~~~~~~

Target a specific session by providing its ID:

.. code-block:: python

   from honeyhive import enrich_session
   
   # Enrich a specific session (not necessarily the active one)
   enrich_session(
       session_id="sess_abc123xyz",
       metadata={
           "experiment": "variant_b",
           "completed": True
       },
       metrics={
           "total_tokens": 1500,
           "total_cost": 0.045,
           "duration_seconds": 12.5
       }
   )

Backwards Compatible Signatures
-------------------------------

The ``enrich_session()`` function maintains full backwards compatibility with previous versions:

Legacy Signature (Still Supported)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Old style: positional session_id
   enrich_session(
       "sess_abc123",  # session_id as first positional arg
       metadata={"user_id": "user_456"}
   )
   
  # Old style: user_properties parameter
  enrich_session(
      session_id="sess_abc123",
      user_properties={
          "tier": "premium",
          "region": "us-east"
      }
  )
  
  # Result: user_properties stored as a separate field in the backend
  # Backend receives:
  # {
  #   "user_properties": {
  #     "tier": "premium",
  #     "region": "us-east"
  #   }
  # }

Modern Signature (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # New style: keyword-only arguments
   enrich_session(
       session_id="sess_abc123",  # Optional, defaults to active session
       metadata={
           "user_id": "user_456",
           "tier": "premium",
           "region": "us-east"
       },
       metrics={
           "total_cost": 0.045
       }
   )

Common Patterns
---------------

Pattern 1: User Workflow Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track user journeys across multiple interactions:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   from datetime import datetime
   import openai
   
   def handle_user_workflow(user_id: str, workflow_name: str):
       """Handle a multi-step user workflow."""
       
       # Initialize session for this workflow
       tracer = HoneyHiveTracer.init(
           project="customer-support",
           session_name=f"{workflow_name}-{user_id}"
       )
       
       # Enrich with user context
       enrich_session(
           metadata={
               "user_id": user_id,
               "workflow": workflow_name,
               "started_at": datetime.now().isoformat()
           }
       )
       
       # Step 1: Initial query
       client = openai.OpenAI()
       response1 = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "How do I reset my password?"}]
       )
       
       # Update session with progress
       enrich_session(
           metadata={
               "step": "initial_query_complete"
           }
       )
       
       # Step 2: Follow-up
       response2 = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "user", "content": "How do I reset my password?"},
               {"role": "assistant", "content": response1.choices[0].message.content},
               {"role": "user", "content": "I didn't receive the email"}
           ]
       )
       
       # Final session enrichment
       enrich_session(
           metadata={
               "step": "workflow_complete",
               "completed_at": datetime.now().isoformat()
           },
           metrics={
               "total_interactions": 2,
               "resolution": "success"
           }
       )
       
       return response2.choices[0].message.content

Pattern 2: Experiment Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add experiment parameters and results to sessions:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   import openai
   import random
   import time
   
   def run_ab_test_experiment(query: str, user_id: str):
       """Run A/B test with different model configurations."""
       
       # Determine variant
       variant = "variant_a" if random.random() < 0.5 else "variant_b"
       
       # Initialize session
       tracer = HoneyHiveTracer.init(
           project="ab-testing",
           session_name=f"experiment-{user_id}"
       )
       
       # Enrich with experiment metadata
       enrich_session(
           metadata={
               "experiment": "prompt_optimization_v2",
               "variant": variant,
               "user_id": user_id
           },
           config={
               "model": "gpt-4" if variant == "variant_a" else "gpt-3.5-turbo",
               "temperature": 0.7 if variant == "variant_a" else 0.9
           }
       )
       
       # Run the experiment
       start_time = time.time()
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4" if variant == "variant_a" else "gpt-3.5-turbo",
           messages=[{"role": "user", "content": query}],
           temperature=0.7 if variant == "variant_a" else 0.9
       )
       duration = time.time() - start_time
       
       # Enrich with results
       enrich_session(
           metrics={
               "response_time": duration,
               "token_count": response.usage.total_tokens,
               "cost": calculate_cost(response.usage)
           },
           outputs={
               "response": response.choices[0].message.content
           }
       )
       
       return response.choices[0].message.content

Pattern 3: Session Feedback Collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add user feedback to sessions after completion:

.. code-block:: python

   from honeyhive import enrich_session
   from datetime import datetime
   
   def collect_session_feedback(session_id: str, rating: int, comments: str):
       """Add user feedback to a completed session."""
       
       # Enrich the session with feedback (can be called after session ends)
       enrich_session(
           session_id=session_id,
           feedback={
               "user_rating": rating,
               "user_comments": comments,
               "feedback_timestamp": datetime.now().isoformat(),
               "helpful": rating >= 4
           },
           metadata={
               "feedback_collected": True
           }
       )

Pattern 4: Cost and Performance Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track session-level costs and performance metrics:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   import openai
   
   class SessionCostTracker:
       """Track costs across a session."""
       
       def __init__(self, project: str, session_name: str):
           self.tracer = HoneyHiveTracer.init(
               project=project,
               session_name=session_name
           )
           self.total_tokens = 0
           self.total_cost = 0.0
           self.call_count = 0
       
       def make_llm_call(self, messages: list, model: str = "gpt-3.5-turbo"):
           """Make an LLM call and track costs."""
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model=model,
               messages=messages
           )
           
           # Update tracking
           self.call_count += 1
           self.total_tokens += response.usage.total_tokens
           self.total_cost += self.calculate_cost(response.usage, model)
           
           # Enrich session with updated metrics
           enrich_session(
               metrics={
                   "total_tokens": self.total_tokens,
                   "total_cost": self.total_cost,
                   "call_count": self.call_count,
                   "avg_tokens_per_call": self.total_tokens / self.call_count
               }
           )
           
           return response.choices[0].message.content
       
       def calculate_cost(self, usage, model):
           """Calculate cost based on token usage and model."""
           # Simplified cost calculation
           if "gpt-4" in model:
               return (usage.prompt_tokens * 0.00003 + 
                       usage.completion_tokens * 0.00006)
           else:
               return (usage.prompt_tokens * 0.000001 + 
                       usage.completion_tokens * 0.000002)
   
   # Usage
   tracker = SessionCostTracker("my-app", "cost-tracking-session")
   tracker.make_llm_call([{"role": "user", "content": "Hello!"}])
   tracker.make_llm_call([{"role": "user", "content": "Tell me more"}])

Pattern 5: Multi-Instance Session Enrichment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enrich sessions across multiple tracer instances:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   
   # Create multiple tracers for different workflows
   prod_tracer = HoneyHiveTracer.init(
       project="production",
       session_name="prod-session-1",
       source="production"
   )
   
   test_tracer = HoneyHiveTracer.init(
       project="testing",
       session_name="test-session-1",
       source="testing"
   )
   
   # Enrich production session
   enrich_session(
       metadata={
           "environment": "production",
           "user_id": "user_123"
       },
       tracer_instance=prod_tracer  # Specify which tracer's session to enrich
   )
   
   # Enrich test session
   enrich_session(
       metadata={
           "environment": "testing",
           "test_case": "scenario_1"
       },
       tracer_instance=test_tracer
   )

Advanced Usage
--------------

Session Lifecycle Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enrich sessions at different lifecycle stages:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, enrich_session
   from datetime import datetime
   import openai
   
   def managed_session_workflow(user_id: str, task: str):
       """Demonstrate session enrichment across lifecycle."""
       
       # Initialize session
       tracer = HoneyHiveTracer.init(
           project="managed-workflows",
           session_name=f"{task}-{user_id}"
       )
       
       # Start: Add initial metadata
       enrich_session(
           metadata={
               "user_id": user_id,
               "task": task,
               "status": "started",
               "started_at": datetime.now().isoformat()
           }
       )
       
       try:
           # In Progress: Update status
           enrich_session(
               metadata={
                   "status": "in_progress"
               }
           )
           
           # Do work
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": f"Help me with: {task}"}]
           )
           
           # Success: Add final metadata
           enrich_session(
               metadata={
                   "status": "completed",
                   "completed_at": datetime.now().isoformat()
               },
               outputs={
                   "result": response.choices[0].message.content
               },
               metrics={
                   "success": True
               }
           )
           
           return response.choices[0].message.content
           
       except Exception as e:
           # Error: Add error metadata
           enrich_session(
               metadata={
                   "status": "failed",
                   "failed_at": datetime.now().isoformat(),
                   "error_type": type(e).__name__,
                   "error_message": str(e)
               },
               metrics={
                   "success": False
               }
           )
           raise

Complex Data Structures
~~~~~~~~~~~~~~~~~~~~~~~

``enrich_session()`` supports nested dictionaries and lists:

.. code-block:: python

   from honeyhive import enrich_session
   
   # Complex nested structures
   enrich_session(
       metadata={
           "user": {
               "id": "user_123",
               "profile": {
                   "tier": "premium",
                   "features": ["chat", "analytics", "export"],
                   "settings": {
                       "notifications": True,
                       "language": "en"
                   }
               }
           }
       },
       config={
           "model_pipeline": [
               {"step": 1, "model": "gpt-4", "temperature": 0.7},
               {"step": 2, "model": "gpt-3.5-turbo", "temperature": 0.5}
           ],
           "fallback_strategy": {
               "enabled": True,
               "models": ["gpt-4", "gpt-3.5-turbo", "claude-2"]
           }
       }
   )

Best Practices
--------------

**DO:**

- Enrich sessions at key lifecycle points (start, progress, completion)
- Use consistent naming conventions for metadata keys
- Add business-relevant context (user IDs, feature flags, experiments)
- Include performance metrics (cost, latency, token counts)
- Collect and add user feedback to completed sessions

**DON'T:**

- Include sensitive data (passwords, API keys, PII)
- Add extremely large payloads (>100KB per enrichment)
- Call ``enrich_session()`` excessively (it makes API calls)
- Use inconsistent key names across sessions
- Forget to handle enrichment failures gracefully

Troubleshooting
---------------

**Session enrichment not appearing:**

- Verify tracer is initialized and session is active
- Check API key has proper permissions
- Ensure session_id is valid (if explicitly provided)
- Check network connectivity and API endpoint

**Performance impact:**

- ``enrich_session()`` makes API calls (expect ~50-200ms per call)
- Batch enrichment calls when possible (send all data at once)
- Don't call inside tight loops
- Consider async enrichment for high-throughput applications

**Backwards compatibility issues:**

- The function accepts both old and new signatures
- ``user_properties`` is stored as a separate field (not merged into metadata)
- ``session_id`` can be positional or keyword argument
- All enrichment data is gracefully merged

Comparison with enrich_span
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - enrich_span()
     - enrich_session()
   * - Scope
     - Single span
     - Entire session
   * - Storage
     - OpenTelemetry attributes
     - HoneyHive backend API
   * - Persistence
     - Local to trace
     - Backend persisted
   * - API Calls
     - No
     - Yes
   * - Complex Data
     - Limited (OTel constraints)
     - Full support
   * - Performance
     - Instant
     - ~50-200ms per call
   * - Use Case
     - Operation-level context
     - Workflow-level context

Next Steps
----------

- :doc:`span-enrichment` - Learn about span-level enrichment
- :doc:`custom-spans` - Create custom spans for complex workflows
- :doc:`advanced-patterns` - Advanced session and tracing patterns
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns

**Key Takeaway:** Use ``enrich_session()`` to add workflow-level context that persists across all spans in a session and is stored in the HoneyHive backend for comprehensive analysis. ✨

