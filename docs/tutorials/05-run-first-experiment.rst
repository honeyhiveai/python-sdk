Tutorial 5: Run Your First Experiment
=====================================

.. note::
   **Tutorial** (15-20 minutes)
   
   
   This is a hands-on tutorial that takes you step-by-step through running
   your first experiment with HoneyHive. You'll create a working example
   and see results in the dashboard.









What You'll Learn
-----------------

By the end of this tutorial, you'll know how to:

- Run an experiment with ``evaluate()``
- Structure test data with inputs and ground truths
- **Create evaluators to automatically score outputs**
- **View metrics and scores in HoneyHive dashboard**
- Compare different versions of your function

What You'll Build
-----------------

A complete question-answering experiment with automated evaluation. You'll:

1. Create a baseline QA function
2. Test it against a dataset
3. **Add evaluators to automatically score outputs**
4. **Compare baseline vs improved version using metrics**
5. View results and metrics in HoneyHive dashboard

Prerequisites
-------------

Before starting this tutorial, you should:

- Complete :doc:`01-setup-first-tracer`
- Have Python 3.11 or higher installed
- Have a HoneyHive API key
- Basic familiarity with Python dictionaries

If you haven't set up the SDK yet, go back to Tutorial 1.

Step 1: Install and Setup
-------------------------

First, create a new Python file for this tutorial:

.. code-block:: bash

   touch my_first_experiment.py

Add the necessary imports and setup:

.. code-block:: python

   # my_first_experiment.py
   import os
   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   # Set your API key
   os.environ["HH_API_KEY"] = "your-api-key-here"
   os.environ["HH_PROJECT"] = "experiments-tutorial"

.. tip::
   Store your API key in a ``.env`` file instead of hardcoding it.
   See :doc:`../how-to/deployment/production` for production best practices.

Step 2: Define Your Function
----------------------------

Create a simple function that answers questions. This will be the function
we test in our experiment:

.. code-block:: python

   def answer_question(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Answer a trivia question.
       
       This is the function we'll test in our experiment.
       
       Args:
           datapoint: Contains 'inputs' with the question
       
       Returns:
           Dictionary with the answer
       
       Note:
           The evaluation function can also accept a 'tracer' parameter if you need
           to access the tracer instance within your function for manual tracing:
           
           def answer_question(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
               # Use tracer for custom spans, enrichment, etc.
               pass
       """
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "")
       
       # Simple logic: check for keywords
       # (In real use, you'd call an LLM here)
       if "capital" in question.lower() and "france" in question.lower():
           answer = "Paris"
       elif "2+2" in question:
           answer = "4"
       elif "color" in question.lower() and "sky" in question.lower():
           answer = "blue"
       else:
           answer = "I don't know"
       
       return {
           "answer": answer,
           "confidence": "high" if answer != "I don't know" else "low"
       }

.. note::
   This example uses simple logic for demonstration. In a real experiment,
   you'd call an LLM API (OpenAI, Anthropic, etc.) inside this function.









Step 3: Create Your Test Dataset
--------------------------------

Define a dataset with questions and expected answers:

.. code-block:: python

   dataset = [
       {
           "inputs": {
               "question": "What is the capital of France?"
           },
           "ground_truth": {
               "answer": "Paris",
               "category": "geography"
           }
       },
       {
           "inputs": {
               "question": "What is 2+2?"
           },
           "ground_truth": {
               "answer": "4",
               "category": "math"
           }
       },
       {
           "inputs": {
               "question": "What color is the sky?"
           },
           "ground_truth": {
               "answer": "blue",
               "category": "science"
           }
       }
   ]





**Understanding the Structure:**


- ``inputs``: What your function receives
- ``ground_truth``: The expected correct answers (used for evaluation)

Step 4: Run Your Experiment
---------------------------

Now run the experiment:

.. code-block:: python

   result = evaluate(
       function=answer_question,
       dataset=dataset,
       name="qa-baseline-v1",
       verbose=True  # Show progress
   )

   

   
   
   print(f"\n✅ Experiment complete!")
   print(f"📊 Run ID: {result.run_id}")
   print(f"📈 Status: {result.status}")





**Run it:**


.. code-block:: bash


   python my_first_experiment.py


**Expected Output:**


.. code-block:: text


   Processing datapoint 1/3...
   Processing datapoint 2/3...
   Processing datapoint 3/3...
   
   ✅ Experiment complete!
   📊 Run ID: run_abc123...
   📈 Status: completed





Step 5: View Results in Dashboard
---------------------------------


1. Go to `HoneyHive Experiments Dashboard <https://app.honeyhive.ai/evaluate>`_
2. Navigate to your project: ``experiments-tutorial``
3. Find your run: ``qa-baseline-v1``


5. Click to view:
   - Session traces for each question
   - Function outputs
   - Ground truths
   - Session metadata





**What You'll See:**

- 3 sessions (one per datapoint)
- Each session shows inputs and outputs
- Ground truths displayed for comparison
- Session names include your experiment name

Step 6: Add Evaluators for Automated Scoring
--------------------------------------------

Viewing results manually is helpful, but let's add **evaluators** to automatically
score our function's outputs:

.. code-block:: python

   def exact_match_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truth: Dict[str, Any]
   ) -> float:
       """Check if answer exactly matches ground truth.
       
       Args:
           outputs: Function's output (from answer_question)
           inputs: Original inputs (not used here)
           ground_truth: Expected outputs
       
       Returns:
           1.0 if exact match, 0.0 otherwise
       """


       actual_answer = outputs.get("answer", "").lower().strip()
       expected_answer = ground_truth.get("answer", "").lower().strip()

       

       
       
       return 1.0 if actual_answer == expected_answer else 0.0





   def confidence_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truth: Dict[str, Any]
   ) -> float:
       """Check if confidence is appropriate.
       
       Returns:
           1.0 if high confidence, 0.5 if low confidence







       confidence = outputs.get("confidence", "low")
       return 1.0 if confidence == "high" else 0.5





**Understanding Evaluators:**


- **Input**: Receives ``(outputs, inputs, ground_truth)``
- **Output**: Returns a score (typically 0.0 to 1.0)
- **Purpose**: Automated quality assessment
- **Runs**: After function executes, for each datapoint


Step 7: Run Experiment with Evaluators
--------------------------------------


Now run the experiment with evaluators:


.. code-block:: python


   result = evaluate(
       function=answer_question,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],  # Added!
       name="qa-baseline-with-metrics-v1",
       verbose=True
   )

   

   
   
   print(f"\n✅ Experiment complete!")
   print(f"📊 Run ID: {result.run_id}")
   print(f"📈 Status: {result.status}")

   

   
   
   # Access metrics
   if result.metrics:
       print(f"\n📊 Aggregated Metrics:")
       # Metrics stored in model_extra for Pydantic v2
       extra_fields = getattr(result.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")





**Expected Output:**


.. code-block:: text


   Processing datapoint 1/3...
   Processing datapoint 2/3...
   Processing datapoint 3/3...
   Running evaluators...

   

   
   
   ✅ Experiment complete!
   📊 Run ID: run_xyz789...
   📈 Status: completed

   

   
   
   📊 Aggregated Metrics:
      exact_match_evaluator: 1.00
      confidence_evaluator: 1.00





Step 8: View Metrics in Dashboard
---------------------------------


Go back to the HoneyHive dashboard:


1. Find your new run: ``qa-baseline-with-metrics-v1``
2. Click to view details


3. You'll now see:
   - **Metrics tab**: Aggregated scores
   - **Per-datapoint metrics**: Individual scores
   - **Metric trends**: Compare across runs





**What You'll See:**


- Exact match score: 100% (3/3 correct)
- Confidence score: 100% (all high confidence)
- Metrics visualized as charts
- Per-session metrics in session details


Step 9: Test an Improvement
---------------------------


Let's test an improved version WITH evaluators:


.. code-block:: python


   def answer_question_improved(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Improved version with better logic."""
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "").lower()
       
       # More sophisticated keyword matching
       answers = {
           "capital of france": "Paris",
           "2+2": "4", 
           "color of the sky": "blue",
           "color is the sky": "blue"
       }

       

       
       
       # Check each pattern
       for pattern, ans in answers.items():
           if all(word in question for word in pattern.split()):
               return {"answer": ans, "confidence": "high"}

       

       
       
       return {"answer": "I don't know", "confidence": "low"}

   

   
   
   # Run improved version WITH EVALUATORS
   result_v2 = evaluate(
       function=answer_question_improved,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],  # Same evaluators!
       name="qa-improved-with-metrics-v1",
       verbose=True
   )

   

   
   
   print(f"\n✅ Improved version complete!")
   print(f"📊 Run ID: {result_v2.run_id}")

   

   
   
   # Compare metrics
   if result_v2.metrics:
       print(f"\n📊 Metrics:")
       extra_fields = getattr(result_v2.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")





Now you have TWO runs to compare!


**Compare in the Dashboard OR via API:**


.. code-block:: python


   # Option 1: View comparison in HoneyHive dashboard (visual)
   # Go to: https://app.honeyhive.ai/evaluate → Select runs → Click Compare

   

   
   
   # Option 2: Programmatic comparison via API
   from honeyhive.experiments import compare_runs
   from honeyhive import HoneyHive

   

   
   
   client = HoneyHive(api_key=os.environ["HH_API_KEY"])
   comparison = compare_runs(
       client=client,
       new_run_id=result_v2.run_id,
       old_run_id=result.run_id
   )

   

   
   
   print(f"\nProgrammatic Comparison:")
   print(f"Common datapoints: {comparison.common_datapoints}")
   print(f"Improved metrics: {comparison.list_improved_metrics()}")
   print(f"Degraded metrics: {comparison.list_degraded_metrics()}")

   

   
   
   # Access detailed metric deltas
   for metric_name, delta in comparison.metric_deltas.items():
       old_val = delta.get("old_aggregate", 0)
       new_val = delta.get("new_aggregate", 0)
       change = new_val - old_val
       print(f"{metric_name}: {old_val:.2f} → {new_val:.2f} ({change:+.2f})")





.. tip::
   **Use both approaches:**
   
   
   - **Dashboard** for visual exploration and sharing with team
   - **API** for automated decision-making and CI/CD pipelines





What You've Learned
-------------------


Congratulations! You've:


✅ Created your first evaluation function  
✅ Structured test data with inputs and ground truths  
✅ **Created evaluators to automatically score outputs**  
✅ Run experiments with ``evaluate()`` and evaluators  
✅ Viewed results and metrics in HoneyHive dashboard  
✅ **Compared runs using both dashboard and API**  


**Key Concepts:**


- **Evaluation Function**: Your application logic under test
- **Dataset**: Test cases with inputs and ground truths
- **Evaluators**: Automated scoring functions
- **Metrics**: Quantitative measurements of quality
- **Comparison**: Compare runs via dashboard (visual) or API (programmatic)


Next Steps
----------


Now that you understand the basics:


- :doc:`../how-to/evaluation/creating-evaluators` - Add automated scoring
- :doc:`../how-to/evaluation/comparing-experiments` - Compare runs statistically
- :doc:`../how-to/evaluation/dataset-management` - Use datasets from HoneyHive UI
- :doc:`../how-to/evaluation/best-practices` - Production experiment patterns


Complete Code
-------------


Here's the complete code from this tutorial:


.. code-block:: python


   # my_first_experiment.py
   import os
   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   
   os.environ["HH_API_KEY"] = "your-api-key-here"
   os.environ["HH_PROJECT"] = "experiments-tutorial"
   
   
   def answer_question(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Answer a trivia question."""
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "")
       
       
       if "capital" in question.lower() and "france" in question.lower():
           answer = "Paris"
       elif "2+2" in question:
           answer = "4"
       elif "color" in question.lower() and "sky" in question.lower():
           answer = "blue"
       else:
           answer = "I don't know"
       
       
       return {"answer": answer, "confidence": "high" if answer != "I don't know" else "low"}
   
   
   dataset = [
       {
           "inputs": {"question": "What is the capital of France?"},
           "ground_truth": {"answer": "Paris"}
       },
       {
           "inputs": {"question": "What is 2+2?"},
           "ground_truth": {"answer": "4"}
       },
       {
           "inputs": {"question": "What color is the sky?"},
           "ground_truth": {"answer": "blue"}
       }
   ]
   
   
   # Define evaluators
   def exact_match_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truth: Dict[str, Any]
   ) -> float:
       """Check if answer exactly matches ground truth."""
       actual = outputs.get("answer", "").lower().strip()
       expected = ground_truth.get("answer", "").lower().strip()
       return 1.0 if actual == expected else 0.0
   
   
   def confidence_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truth: Dict[str, Any]
   ) -> float:
       """Check if confidence is appropriate."""
       confidence = outputs.get("confidence", "low")
       return 1.0 if confidence == "high" else 0.5
   
   
   # Run experiment with evaluators
   result = evaluate(
       function=answer_question,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],
       name="qa-baseline-with-metrics-v1",
       verbose=True
   )
   
   
   print(f"\n✅ Experiment complete! Run ID: {result.run_id}")
   
   
   # Print metrics
   if result.metrics:
       print(f"\n📊 Metrics:")
       extra_fields = getattr(result.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")

