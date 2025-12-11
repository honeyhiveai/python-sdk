Running Experiments
===================

How do I run experiments to test my LLM application?
----------------------------------------------------

Use the ``evaluate()`` function to run your application across a dataset and track results.

What's the simplest way to run an experiment?
---------------------------------------------

**Three-Step Pattern**

.. versionchanged:: 1.0

   Function signature changed from ``(inputs, ground_truth)`` to ``(datapoint: Dict[str, Any])``.

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   
   # Step 1: Define your function
   def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Your application logic.
       
       Args:
           datapoint: Contains 'inputs' and 'ground_truth'
       
       Returns:
           Dictionary with your function's outputs
       """
       inputs = datapoint.get("inputs", {})
       result = call_llm(inputs["prompt"])
       return {"answer": result}
   
   
   # Step 2: Create dataset
   dataset = [
       {
           "inputs": {"prompt": "What is AI?"},
           "ground_truth": {"answer": "Artificial Intelligence..."}
       }
   ]
   
   
   # Step 3: Run experiment
   result = evaluate(
       function=my_llm_app,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project",
       name="My Experiment v1"
   )
   
   
   print(f"✅ Run ID: {result.run_id}")
   print(f"✅ Status: {result.status}")

.. important::
   **Think of Your Evaluation Function as a Scaffold**
   
   The evaluation function's job is to take datapoints from your dataset and convert them into the right format to invoke your main AI processing functions. It's a thin adapter layer that:
   
   - Extracts ``inputs`` from the datapoint
   - Calls your actual application logic (``call_llm``, ``process_query``, ``rag_pipeline``, etc.)
   - Returns the results in a format that evaluators can use
   
   Keep the evaluation function simple - the real logic lives in your application functions.

How should I structure my test data?
------------------------------------

**Use inputs + ground_truth Pattern**

Each datapoint in your dataset should have:

.. code-block:: python

   {
       "inputs": {
           # Parameters passed to your function
           "query": "user question",
           "context": "additional info",
           "model": "gpt-4"
       },
       "ground_truth": {
           # Expected outputs (optional but recommended)
           "answer": "expected response",
           "category": "classification",
           "score": 0.95
       }
   }

**Complete Example:**

.. code-block:: python

   dataset = [
       {
           "inputs": {
               "question": "What is the capital of France?",
               "language": "English"
           },
           "ground_truth": {
               "answer": "Paris",
               "confidence": "high"
           }
       },
       {
           "inputs": {
               "question": "What is 2+2?",
               "language": "English"
           },
           "ground_truth": {
               "answer": "4",
               "confidence": "absolute"
           }
       }
   ]

What signature must my function have?
-------------------------------------

**Accept datapoint Parameter (v1.0)**

.. versionchanged:: 1.0

   Function signature changed from ``(inputs, ground_truth)`` to ``(datapoint: Dict[str, Any])``.

Your function MUST accept a ``datapoint`` parameter, and can optionally accept a ``tracer`` parameter:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive import HoneyHiveTracer
   
   
   # Option 1: Basic signature (datapoint only)
   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Your evaluation function.
       
       Args:
           datapoint: Dictionary with 'inputs' and 'ground_truth' keys
       
       Returns:
           dict: Your function's output
       """
       # Extract inputs and ground_truth
       inputs = datapoint.get("inputs", {})
       ground_truth = datapoint.get("ground_truth", {})
       
       
       # Access input parameters
       user_query = inputs.get("question")
       language = inputs.get("language", "English")
       
       
       # ground_truth available but typically not used in function
       # (used by evaluators for scoring)
       
       
       # Your logic
       result = process_query(user_query, language)
       
       
       # Return dict
       return {"answer": result, "metadata": {...}}
   
   
   # Option 2: With tracer parameter (for advanced tracing)
   def my_function_with_tracer(
       datapoint: Dict[str, Any],
       tracer: HoneyHiveTracer  # Optional - auto-injected by evaluate()
   ) -> Dict[str, Any]:
       """Evaluation function with tracer access.
       
       Args:
           datapoint: Dictionary with 'inputs' and 'ground_truth' keys
           tracer: HoneyHiveTracer instance (optional, auto-provided)
       
       Returns:
           dict: Your function's output
       """
       inputs = datapoint.get("inputs", {})
       
       # Use tracer for enrichment
       tracer.enrich_session(metadata={"user_id": inputs.get("user_id")})
       
       result = process_query(inputs["question"])
       
       return {"answer": result}

.. important::
   **Required Parameters:**
   
   - Accept ``datapoint: Dict[str, Any]`` as first parameter (required)
   
   **Optional Parameters:**
   
   - Accept ``tracer: HoneyHiveTracer`` as second parameter (optional - auto-injected by evaluate())
   
   **Requirements:**
   
   - Extract ``inputs`` with ``datapoint.get("inputs", {})``
   - Extract ``ground_truth`` with ``datapoint.get("ground_truth", {})``
   - Return value should be a **dictionary**
   - **Type hints are strongly recommended**

**Backward Compatibility (Deprecated):**

.. deprecated:: 1.0

   The old ``(inputs, ground_truth)`` signature is deprecated but still supported
   for backward compatibility. It will be removed in v2.0.

.. code-block:: python

   # ⚠️ Deprecated: Old signature (still works in v1.0)
   def old_style_function(inputs, ground_truth):
       # This still works but will be removed in v2.0
       return {"output": inputs["query"]}
   
   
   # ✅ Recommended: New signature (v1.0+)
   def new_style_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       inputs = datapoint.get("inputs", {})
       return {"output": inputs["query"]}

Can I use async functions with evaluate()?
------------------------------------------

.. versionadded:: 1.0

   The ``evaluate()`` function now supports async functions.

**Yes! Async functions are fully supported.**

If your application uses async operations (like async LLM clients), you can pass an async function directly to ``evaluate()``. Async functions are automatically detected and executed correctly.

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   import asyncio
   
   
   # Option 1: Basic async function
   async def my_async_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Async evaluation function.
       
       Args:
           datapoint: Dictionary with 'inputs' and 'ground_truth' keys
       
       Returns:
           dict: Your function's output
       """
       inputs = datapoint.get("inputs", {})
       
       # Use async operations (e.g., async LLM client)
       result = await async_llm_call(inputs["prompt"])
       
       return {"answer": result}
   
   
   # Option 2: Async function with tracer parameter
   async def my_async_function_with_tracer(
       datapoint: Dict[str, Any],
       tracer: HoneyHiveTracer
   ) -> Dict[str, Any]:
       """Async evaluation function with tracer access.
       
       Args:
           datapoint: Dictionary with 'inputs' and 'ground_truth' keys
           tracer: HoneyHiveTracer instance (auto-injected)
       
       Returns:
           dict: Your function's output
       """
       inputs = datapoint.get("inputs", {})
       
       # Use tracer for enrichment
       tracer.enrich_session(metadata={"async": True})
       
       # Use async operations
       result = await async_llm_call(inputs["prompt"])
       
       return {"answer": result}
   
   
   # Run experiment with async function - works the same as sync!
   result = evaluate(
       function=my_async_function,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project",
       name="Async Experiment v1"
   )

.. note::
   **How it works:**
   
   - Async functions are automatically detected using ``asyncio.iscoroutinefunction()``
   - Each datapoint is processed in a separate thread using ``ThreadPoolExecutor``
   - Async functions are executed with ``asyncio.run()`` inside each worker thread
   - Both sync and async functions work seamlessly with the optional ``tracer`` parameter

**When to use async functions:**

- When using async LLM clients (e.g., ``openai.AsyncOpenAI``)
- When making concurrent API calls within your function
- When your existing application code is already async

How do I use ground_truth from datapoints in my experiments?
-------------------------------------------------------------

**Client-Side vs Server-Side Evaluators**

The ``ground_truth`` from your datapoints can be used by evaluators to measure quality. Choose between client-side or server-side evaluation based on your architecture.

**Client-Side Evaluators (Recommended)**

Pass data down to the evaluation function so it's available for client-side evaluators:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Evaluation function that passes through data for evaluators."""
       inputs = datapoint.get("inputs", {})
       ground_truth = datapoint.get("ground_truth", {})
       
       # Call your LLM
       result = call_llm(inputs["prompt"])
       
       # Return outputs AND pass through ground_truth for evaluators
       return {
           "answer": result,
           "ground_truth": ground_truth,  # Make available to evaluators
           "intermediate_steps": [...]    # Any other data for evaluation
       }
   
   # Your evaluator receives both the output and datapoint context
   def accuracy_evaluator(output: Dict[str, Any], datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Client-side evaluator with access to ground truth."""
       predicted = output["answer"]
       expected = output["ground_truth"]["answer"]  # From evaluation function output
       
       is_correct = predicted.lower() == expected.lower()
       return {
           "score": 1.0 if is_correct else 0.0,
           "metadata": {"predicted": predicted, "expected": expected}
       }
   
   # Run evaluation with client-side evaluator
   result = evaluate(
       function=my_llm_app,
       dataset=dataset,
       evaluators=[accuracy_evaluator],
       name="Accuracy Test"
   )

.. note::
   **When to Use Client-Side Evaluators**
   
   - Simple, self-contained evaluation logic
   - Evaluators that need access to intermediate steps
   - When you can easily pass data through the evaluation function
   - Faster feedback (no roundtrip to HoneyHive)

**Server-Side Evaluators**

For complex applications where it's hard to pass intermediate steps, use ``enrich_session()`` to bring data up to the session level:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive import HoneyHiveTracer
   from honeyhive.experiments import evaluate
   
   def complex_app(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
       """Complex app with hard-to-pass intermediate steps."""
       inputs = datapoint.get("inputs", {})
       
       # Step 1: Document retrieval (deep in call stack)
       docs = retrieve_documents(inputs["query"])
       
       # Step 2: LLM call (deep in another function)
       result = generate_answer(inputs["query"], docs)
       
       # Instead of threading data through complex call stacks,
       # use enrich_session to make it available at session level
       tracer.enrich_session(
           outputs={
               "answer": result,
               "retrieved_docs": docs,
               "doc_count": len(docs)
           },
           metadata={
               "ground_truth": datapoint.get("ground_truth", {}),
               "experiment_version": "v2"
           }
       )
       
       return {"answer": result}
   
   # Run evaluation - use server-side evaluators in HoneyHive dashboard
   result = evaluate(
       function=complex_app,
       dataset=dataset,
       name="Complex App Evaluation"
   )
   # Then configure server-side evaluators in HoneyHive to compare
   # session.outputs.answer against session.metadata.ground_truth.answer

.. note::
   **When to Use Server-Side Evaluators**
   
   - Complex, nested application architectures
   - Intermediate steps are hard to pass through function calls
   - Need to evaluate data from multiple spans/sessions together
   - Want centralized evaluation logic in HoneyHive dashboard

**Decision Matrix:**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Scenario
     - Use Client-Side
     - Use Server-Side
   * - Simple function
     - ✅ Easy to pass data
     - ❌ Overkill
   * - Complex nested calls
     - ❌ Hard to thread data
     - ✅ Use enrich_session
   * - Evaluation speed
     - ✅ Faster (local)
     - ⚠️ Slower (API roundtrip)
   * - Centralized logic
     - ❌ In code
     - ✅ In dashboard
   * - Team collaboration
     - ⚠️ Requires code changes
     - ✅ No code changes needed

How do I enrich sessions or spans during evaluation?
----------------------------------------------------

.. versionadded:: 1.0

   You can now receive a ``tracer`` parameter in your evaluation function.

**Use the tracer Parameter for Advanced Tracing**

If your function needs to enrich sessions or use the tracer instance,
add a ``tracer`` parameter to your function signature:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive import HoneyHiveTracer
   from honeyhive.experiments import evaluate
   
   
   def my_function(
       datapoint: Dict[str, Any],
       tracer: HoneyHiveTracer  # Optional tracer parameter
   ) -> Dict[str, Any]:
       """Function with tracer access.
       
       Args:
           datapoint: Test data with 'inputs' and 'ground_truth'
           tracer: HoneyHiveTracer instance (auto-injected)
       
       Returns:
           Function outputs
       """
       inputs = datapoint.get("inputs", {})
       
       
       # Enrich the session with metadata
       tracer.enrich_session(
           metadata={"experiment_version": "v2", "user_id": "test-123"}
       )
       
       
       # Call your application logic - enrich_span happens inside
       result = process_query(inputs["query"], tracer)
       
       
       return {"answer": result}
   
   
   def process_query(query: str, tracer: HoneyHiveTracer) -> str:
       """Application logic that enriches spans.
       
       Call enrich_span from within your actual processing functions,
       not directly in the evaluation function.
       """
       # Do some processing
       result = call_llm(query)
       
       # Enrich the span with metrics from within this function
       tracer.enrich_span(
           metrics={"processing_time": 0.5, "token_count": 150},
           metadata={"model": "gpt-4", "temperature": 0.7}
       )
       
       return result
   
   
   # The tracer is automatically provided by evaluate()
   result = evaluate(
       function=my_function,
       dataset=dataset,
       name="experiment-v1"
   )

.. important::
   - The ``tracer`` parameter is **optional** - only add it if needed
   - The tracer is **automatically injected** by ``evaluate()``
   - Use it to call ``enrich_session()`` or access the tracer instance
   - Each datapoint gets its own tracer instance (multi-instance architecture)

**Without tracer parameter (simpler):**

.. code-block:: python

   def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Function without tracer access."""
       inputs = datapoint.get("inputs", {})
       return {"answer": process_query(inputs["query"])}

How do I trace third-party library calls in my evaluation?
----------------------------------------------------------

.. versionadded:: 1.0

   The ``evaluate()`` function now supports the ``instrumentors`` parameter.

**Use the instrumentors Parameter for Automatic Tracing**

If your evaluation function uses third-party libraries (OpenAI, Anthropic, Google ADK, LangChain, etc.), you can automatically trace their calls by passing instrumentor factory functions:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   
   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Evaluation function using OpenAI."""
       inputs = datapoint.get("inputs", {})
       
       # OpenAI calls will be automatically traced
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": inputs["prompt"]}]
       )
       
       return {"answer": response.choices[0].message.content}
   
   
   # Pass instrumentor factories - each datapoint gets its own instance
   result = evaluate(
       function=my_function,
       dataset=dataset,
       instrumentors=[lambda: OpenAIInstrumentor()],  # Factory function
       name="openai-traced-experiment"
   )

.. important::
   **Why Factory Functions?**
   
   The ``instrumentors`` parameter accepts **factory functions** (callables that return instrumentor instances), not instrumentor instances directly. This ensures each datapoint gets its own isolated instrumentor instance, preventing trace routing issues in concurrent processing.
   
   - **Correct**: ``instrumentors=[lambda: OpenAIInstrumentor()]``
   - **Incorrect**: ``instrumentors=[OpenAIInstrumentor()]``

**Multiple Instrumentors:**

.. code-block:: python

   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.langchain import LangChainInstrumentor
   
   result = evaluate(
       function=my_function,
       dataset=dataset,
       instrumentors=[
           lambda: OpenAIInstrumentor(),
           lambda: LangChainInstrumentor(),
       ],
       name="multi-instrumented-experiment"
   )

**Google ADK Example:**

.. code-block:: python

   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   from google.adk.agents import Agent
   from google.adk.runners import Runner
   
   
   async def run_adk_agent(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Run Google ADK agent - calls are automatically traced."""
       inputs = datapoint.get("inputs", {})
       
       agent = Agent(name="my_agent", model="gemini-2.0-flash", ...)
       runner = Runner(agent=agent, ...)
       
       # ADK agent calls will be traced
       response = await runner.run_async(...)
       
       return {"response": response}
   
   
   result = evaluate(
       function=run_adk_agent,
       dataset=dataset,
       instrumentors=[lambda: GoogleADKInstrumentor()],
       name="adk-agent-evaluation"
   )

.. note::
   **How it works:**
   
   - Each datapoint gets its own tracer instance (multi-instance architecture)
   - For each datapoint, the SDK creates fresh instrumentor instances from your factories
   - Instrumentors are configured with the datapoint's tracer provider via ``instrumentor.instrument(tracer_provider=tracer.provider)``
   - This ensures all traces from that datapoint are routed to the correct session

**Supported Instrumentors:**

Any OpenInference-compatible instrumentor works with this pattern:

- ``openinference.instrumentation.openai.OpenAIInstrumentor``
- ``openinference.instrumentation.anthropic.AnthropicInstrumentor``
- ``openinference.instrumentation.google_adk.GoogleADKInstrumentor``
- ``openinference.instrumentation.langchain.LangChainInstrumentor``
- ``openinference.instrumentation.llama_index.LlamaIndexInstrumentor``
- And many more...

My experiments are too slow on large datasets
---------------------------------------------

**Use max_workers for Parallel Processing**

.. code-block:: python

   # Slow: Sequential processing (default)
   result = evaluate(
       function=my_function,
       dataset=large_dataset,  # 1000 items
       api_key="your-api-key",
       project="your-project"
   )
   # Takes: ~1000 seconds if each item takes 1 second
   
   
   # Fast: Parallel processing
   result = evaluate(
       function=my_function,
       dataset=large_dataset,  # 1000 items
       max_workers=20,  # Process 20 items simultaneously
       api_key="your-api-key",
       project="your-project"
   )
   # Takes: ~50 seconds (20x faster)

**Choosing max_workers:**

.. code-block:: python

   # Conservative (good for API rate limits)
   max_workers=5
   
   
   # Balanced (good for most cases)
   max_workers=10
   
   
   # Aggressive (fast but watch rate limits)
   max_workers=20

How do I avoid hardcoding credentials?
--------------------------------------

**Use Environment Variables**

.. code-block:: python

   import os
   
   
   # Set environment variables
   os.environ["HH_API_KEY"] = "your-api-key"
   os.environ["HH_PROJECT"] = "your-project"
   
   
   # Now you can omit api_key and project
   result = evaluate(
       function=my_function,
       dataset=dataset,
       name="Experiment v1"
   )

**Or use a .env file:**

.. code-block:: bash

   # .env file
   HH_API_KEY=your-api-key
   HH_PROJECT=your-project
   HH_SOURCE=dev  # Optional: environment identifier

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()
   
   
   # Credentials loaded automatically
   result = evaluate(
       function=my_function,
       dataset=dataset,
       name="Experiment v1"
   )

How should I name my experiments?
---------------------------------

**Use Descriptive, Versioned Names**

.. code-block:: python

   # ❌ Bad: Generic names
   name="test"
   name="experiment"
   name="run1"
   
   
   # ✅ Good: Descriptive names
   name="gpt-3.5-baseline-v1"
   name="improved-prompt-v2"
   name="rag-with-reranking-v1"
   name="production-candidate-2024-01-15"

**Naming Convention:**

.. code-block:: python

   # Format: {change-description}-{version}
   evaluate(
       function=baseline_function,
       dataset=dataset,
       name="gpt-3.5-baseline-v1",
       api_key="your-api-key",
       project="your-project"
   )
   
   
   evaluate(
       function=improved_function,
       dataset=dataset,
       name="gpt-4-improved-v1",  # Easy to compare
       api_key="your-api-key",
       project="your-project"
   )

How do I access experiment results in code?
-------------------------------------------

**Use the Returned EvaluationResult Object**

.. code-block:: python

   result = evaluate(
       function=my_function,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project"
   )
   
   
   # Access run information
   print(f"Run ID: {result.run_id}")
   print(f"Status: {result.status}")
   print(f"Dataset ID: {result.dataset_id}")
   
   
   # Access session IDs (one per datapoint)
   print(f"Session IDs: {result.session_ids}")
   
   
   # Access evaluation data
   print(f"Results: {result.data}")
   
   
   # Export to JSON
   result.to_json()  # Saves to {suite_name}.json

I want to see what's happening during evaluation
------------------------------------------------

**Enable Verbose Output**

.. code-block:: python

   result = evaluate(
       function=my_function,
       dataset=dataset,
       verbose=True,  # Show progress
       api_key="your-api-key",
       project="your-project"
   )
   
   
   # Output:
   # Processing datapoint 1/10...
   # Processing datapoint 2/10...
   # ...

Show me a complete real-world example
-------------------------------------

**Question Answering Pipeline (v1.0)**

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   import openai
   import os
   
   
   # Setup
   os.environ["HH_API_KEY"] = "your-honeyhive-key"
   os.environ["HH_PROJECT"] = "qa-system"
   openai.api_key = "your-openai-key"
   
   
   # Define function to test
   def qa_pipeline(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Answer questions using GPT-4.
       
       Args:
           datapoint: Contains 'inputs' and 'ground_truth'
       
       Returns:
           Dictionary with answer, model, and token count
       """
       client = openai.OpenAI()
       
       
       inputs = datapoint.get("inputs", {})
       question = inputs["question"]
       context = inputs.get("context", "")
       
       
       prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
       
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}],
           temperature=0.0
       )
       
       
       return {
           "answer": response.choices[0].message.content,
           "model": "gpt-4",
           "tokens": response.usage.total_tokens
       }
   
   
   # Create test dataset
   dataset = [
       {
           "inputs": {
               "question": "What is machine learning?",
               "context": "ML is a subset of AI"
           },
           "ground_truth": {
               "answer": "Machine learning is a subset of artificial intelligence..."
           }
       },
       {
           "inputs": {
               "question": "What is deep learning?",
               "context": "DL uses neural networks"
           },
           "ground_truth": {
               "answer": "Deep learning uses neural networks..."
           }
       }
   ]
   
   
   # Run experiment
   result = evaluate(
       function=qa_pipeline,
       dataset=dataset,
       name="qa-gpt4-baseline-v1",
       max_workers=5,
       verbose=True
   )
   
   
   print(f"✅ Experiment complete!")
   print(f"📊 Run ID: {result.run_id}")
   print(f"🔗 View in dashboard: https://app.honeyhive.ai/projects/qa-system")

See Also
--------

- :doc:`creating-evaluators` - Add metrics to your experiments
- :doc:`dataset-management` - Use datasets from HoneyHive UI
- :doc:`comparing-experiments` - Compare multiple experiment runs
- :doc:`../../reference/experiments/core-functions` - Complete evaluate() API reference

