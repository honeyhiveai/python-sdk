Evaluation Framework
====================

This section covers the evaluation functionality of the HoneyHive Python SDK.

Evaluators
----------

.. automodule:: honeyhive.evaluation.evaluators
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_strings
   
   # Evaluate two strings for similarity
   result = evaluate_strings(
       reference="Hello, world!",
       prediction="Hello world",
       metric="exact_match"
   )
   
   print(f"Score: {result.score}")
   print(f"Feedback: {result.feedback}")

Custom Evaluation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation.evaluators import EvaluationResult
   
   # Create a custom evaluation result
   result = EvaluationResult(
       score=0.85,
       feedback="Good response with minor formatting issues",
       metadata={"confidence": 0.9}
   )

Evaluation Metrics
~~~~~~~~~~~~~~~~~~

The SDK supports various evaluation metrics:

* **Exact Match**: Perfect string matching
* **Fuzzy Match**: Approximate string matching
* **Semantic Similarity**: Meaning-based comparison
* **Custom Metrics**: User-defined evaluation criteria
