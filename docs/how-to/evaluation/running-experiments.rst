Running Experiments
===================

How do I run experiments to test my LLM application?
------------------------------------------------------

Use the ``evaluate()`` function to run your application across a dataset and track results.

What's the simplest way to run an experiment?
----------------------------------------------

**Three-Step Pattern**

.. code-block:: python

   from honeyhive.experiments import evaluate
   
   # Step 1: Define your function
   def my_llm_app(inputs, ground_truths):
       # Your application logic
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
-------------------------------------

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
--------------------------------------

**Accept (inputs, ground_truths) Parameters**

Your function MUST accept these parameters in this order:

.. code-block:: python

   def my_function(inputs, ground_truths):
       """
       Args:
           inputs (dict): From datapoint["inputs"]
           ground_truths (dict): From datapoint["ground_truths"]
       
       Returns:
           dict: Your function's output
       """
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
   - Parameters are **positional** - order matters!
   - ``inputs`` is required
   - ``ground_truths`` is optional (can ignore if not needed)
   - Return value should be a **dictionary**

My experiments are too slow on large datasets
----------------------------------------------

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
---------------------------------------

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
----------------------------------

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
--------------------------------------------

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
-------------------------------------------------

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
--------------------------------------

**Question Answering Pipeline**

.. code-block:: python

   from honeyhive.experiments import evaluate
   import openai
   import os
   
   # Setup
   os.environ["HH_API_KEY"] = "your-honeyhive-key"
   os.environ["HH_PROJECT"] = "qa-system"
   openai.api_key = "your-openai-key"
   
   # Define function to test
   def qa_pipeline(inputs, ground_truths):
       """Answer questions using GPT-4."""
       client = openai.OpenAI()
       
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
