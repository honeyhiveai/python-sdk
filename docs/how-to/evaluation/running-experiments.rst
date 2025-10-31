Running Experiments
===================


How do I run experiments to test my LLM application?
----------------------------------------------------


Use the ``evaluate()`` function to run your application across a dataset and track results.


What's the simplest way to run an experiment?
---------------------------------------------


**Three-Step Pattern**


.. versionchanged:: 1.0


   Function signature changed from ``(inputs, ground_truths)`` to ``(datapoint: Dict[str, Any])``.


.. code-block:: python


   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   
   # Step 1: Define your function
   def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Your application logic.
       
       Args:
           datapoint: Contains 'inputs' and 'ground_truths'
       
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
           "ground_truths": {"answer": "Artificial Intelligence..."}
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


How should I structure my test data?
------------------------------------


**Use inputs + ground_truths Pattern**


Each datapoint in your dataset should have:


.. code-block:: python


   {
       "inputs": {
           # Parameters passed to your function
           "query": "user question",
           "context": "additional info",
           "model": "gpt-4"
       },
       "ground_truths": {
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
           "ground_truths": {
               "answer": "Paris",
               "confidence": "high"
           }
       },
       {
           "inputs": {
               "question": "What is 2+2?",
               "language": "English"
           },
           "ground_truths": {
               "answer": "4",
               "confidence": "absolute"
           }
       }
   ]


What signature must my function have?
-------------------------------------


**Accept datapoint Parameter (v1.0)**


.. versionchanged:: 1.0


   Function signature changed from ``(inputs, ground_truths)`` to ``(datapoint: Dict[str, Any])``.


Your function MUST accept a ``datapoint`` parameter:


.. code-block:: python


   from typing import Any, Dict
   
   
   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Your evaluation function.
       
       Args:
           datapoint: Dictionary with 'inputs' and 'ground_truths' keys
       
       Returns:
           dict: Your function's output
       """
       # Extract inputs and ground_truths
       inputs = datapoint.get("inputs", {})
       ground_truths = datapoint.get("ground_truths", {})
       
       
       # Access input parameters
       user_query = inputs.get("question")
       language = inputs.get("language", "English")
       
       
       # ground_truths available but typically not used in function
       # (used by evaluators for scoring)
       
       
       # Your logic
       result = process_query(user_query, language)
       
       
       # Return dict
       return {"answer": result, "metadata": {...}}


.. important::
   - Accept **one parameter**: ``datapoint: Dict[str, Any]``
   - Extract ``inputs`` with ``datapoint.get("inputs", {})``
   - Extract ``ground_truths`` with ``datapoint.get("ground_truths", {})``
   - Return value should be a **dictionary**
   - **Type hints are strongly recommended**


**Backward Compatibility (Deprecated):**


.. deprecated:: 1.0


   The old ``(inputs, ground_truths)`` signature is deprecated but still supported
   for backward compatibility. It will be removed in v2.0.


.. code-block:: python


   # ⚠️ Deprecated: Old signature (still works in v1.0)
   def old_style_function(inputs, ground_truths):
       # This still works but will be removed in v2.0
       return {"output": inputs["query"]}
   
   
   # ✅ Recommended: New signature (v1.0+)
   def new_style_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       inputs = datapoint.get("inputs", {})
       return {"output": inputs["query"]}


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
   from honeyhive.sdk.utils import enrich_span, enrich_session
   
   
   def my_function(
       datapoint: Dict[str, Any],
       tracer: HoneyHiveTracer  # Optional tracer parameter
   ) -> Dict[str, Any]:
       """Function with tracer access.
       
       Args:
           datapoint: Test data with 'inputs' and 'ground_truths'
           tracer: HoneyHiveTracer instance (auto-injected)
       
       Returns:
           Function outputs
       """
       inputs = datapoint.get("inputs", {})
       
       
       # Enrich the session with metadata
       enrich_session(
           tracer=tracer,
           metadata={"experiment_version": "v2", "user_id": "test-123"}
       )
       
       
       # Your logic
       result = process_query(inputs["query"])
       
       
       # Enrich spans with metrics
       enrich_span(
           metrics={"processing_time": 0.5},
           metadata={"model": "gpt-4"}
       )
       
       
       return {"answer": result}
   
   
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
           datapoint: Contains 'inputs' and 'ground_truths'
       
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
           "ground_truths": {
               "answer": "Machine learning is a subset of artificial intelligence..."
           }
       },
       {
           "inputs": {
               "question": "What is deep learning?",
               "context": "DL uses neural networks"
           },
           "ground_truths": {
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

