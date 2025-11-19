Evaluators Reference
====================

Complete reference for all evaluation classes and functions in HoneyHive.

.. contents:: Table of Contents
   :local:
   :depth: 2

Base Classes
------------

BaseEvaluator
~~~~~~~~~~~~~

Base class for all custom evaluators.

.. autoclass:: honeyhive.evaluation.evaluators.BaseEvaluator
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __call__

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator
   
   class CustomEvaluator(BaseEvaluator):
       def __init__(self, threshold=0.5, **kwargs):
           super().__init__("custom_evaluator", **kwargs)
           self.threshold = threshold
       
       def evaluate(self, inputs, outputs, ground_truth=None, **kwargs):
           # Custom evaluation logic
           score = self._compute_score(outputs)
           return {
               "score": score,
               "passed": score >= self.threshold
           }

Built-in Evaluators
-------------------

ExactMatchEvaluator
~~~~~~~~~~~~~~~~~~~

Evaluates exact string matching between expected and actual outputs.

.. autoclass:: honeyhive.evaluation.evaluators.ExactMatchEvaluator
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Description
^^^^^^^^^^^

The ExactMatchEvaluator checks if the actual output exactly matches the expected output.
String comparisons are case-insensitive and whitespace is stripped.

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import ExactMatchEvaluator
   
   evaluator = ExactMatchEvaluator()
   
   result = evaluator.evaluate(
       inputs={"expected": "The answer is 42"},
       outputs={"response": "The answer is 42"}
   )
   # Returns: {"exact_match": 1.0, "expected": "...", "actual": "..."}
   
   # Case-insensitive matching
   result = evaluator.evaluate(
       inputs={"expected": "hello"},
       outputs={"response": "HELLO"}
   )
   # Returns: {"exact_match": 1.0, ...}

F1ScoreEvaluator
~~~~~~~~~~~~~~~~

Evaluates F1 score for text similarity.

.. autoclass:: honeyhive.evaluation.evaluators.F1ScoreEvaluator
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Description
^^^^^^^^^^^

The F1ScoreEvaluator computes the F1 score between predicted and ground truth text
based on word-level token overlap. It calculates precision and recall and combines
them into an F1 score.

Formula
^^^^^^^

.. code-block:: text

   precision = |predicted_words ∩ ground_truth_words| / |predicted_words|
   recall = |predicted_words ∩ ground_truth_words| / |ground_truth_words|
   f1_score = 2 * (precision * recall) / (precision + recall)

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import F1ScoreEvaluator
   
   evaluator = F1ScoreEvaluator()
   
   result = evaluator.evaluate(
       inputs={"expected": "the quick brown fox"},
       outputs={"response": "the fast brown fox"}
   )
   # Returns: {"f1_score": 0.75}  # 3 out of 4 words match

SemanticSimilarityEvaluator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evaluates semantic similarity using embeddings.

.. autoclass:: honeyhive.evaluation.evaluators.SemanticSimilarityEvaluator
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Description
^^^^^^^^^^^

The SemanticSimilarityEvaluator uses embeddings to compute semantic similarity
between texts. This is more sophisticated than exact match or F1 score as it
understands meaning rather than just token overlap.

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import SemanticSimilarityEvaluator
   
   evaluator = SemanticSimilarityEvaluator(
       embedding_model="text-embedding-ada-002",
       threshold=0.8
   )
   
   result = evaluator.evaluate(
       inputs={"expected": "The weather is nice today"},
       outputs={"response": "It's a beautiful day outside"}
   )
   # Returns: {"similarity": 0.85, "passed": True}

Evaluation Decorators
---------------------

evaluator
~~~~~~~~~

Decorator for defining synchronous evaluators.

.. autofunction:: honeyhive.evaluation.evaluators.evaluator

Description
^^^^^^^^^^^

The ``evaluator`` decorator converts a regular function into an evaluator that can be
used with the HoneyHive evaluation system.

Example
^^^^^^^

.. code-block:: python

   from honeyhive import evaluator
   
   @evaluator
   def length_check(inputs, outputs, ground_truth=None, min_length=10):
       """Check if output meets minimum length requirement."""
       text = outputs.get("response", "")
       length = len(text)
       
       return {
           "length": length,
           "meets_minimum": length >= min_length,
           "score": 1.0 if length >= min_length else 0.0
       }
   
   # Use in evaluation
   from honeyhive import evaluate
   
   results = evaluate(
       data=[{"input": "test"}],
       task=lambda x: {"response": "short"},
       evaluators=[length_check]
   )

aevaluator
~~~~~~~~~~

Decorator for defining asynchronous evaluators.

.. autofunction:: honeyhive.evaluation.evaluators.aevaluator

EvaluatorMeta
~~~~~~~~~~~~~

Metaclass for evaluator type handling.

.. autoclass:: honeyhive.experiments.evaluators.EvaluatorMeta
   :members:
   :undoc-members:
   :show-inheritance:

TerminalColors
~~~~~~~~~~~~~~

Terminal color constants for formatted output.

.. autoclass:: honeyhive.experiments.evaluators.TerminalColors
   :members:
   :undoc-members:
   :show-inheritance:

Description
^^^^^^^^^^^

The ``aevaluator`` decorator is used for async evaluators that need to make
asynchronous calls (e.g., API calls for LLM-based evaluation).

Example
^^^^^^^

.. code-block:: python

   from honeyhive import aevaluator
   import aiohttp
   
   @aevaluator
   async def llm_grader(inputs, outputs, ground_truth=None):
       """Use an LLM to grade the output."""
       async with aiohttp.ClientSession() as session:
           async with session.post(
               "https://api.openai.com/v1/chat/completions",
               json={
                   "model": "gpt-4",
                   "messages": [{
                       "role": "user",
                       "content": f"Grade this output: {outputs['response']}"
                   }]
               }
           ) as response:
               result = await response.json()
               grade = parse_grade(result)
               
               return {
                   "grade": grade,
                   "score": grade / 100.0
               }

Data Models
-----------

EvaluationResult
~~~~~~~~~~~~~~~~

Result model for evaluation outputs.

.. autoclass:: honeyhive.evaluation.evaluators.EvaluationResult
   :members:
   :undoc-members:
   :show-inheritance:

Fields
^^^^^^

- **score** (float): Numeric score from evaluation
- **metrics** (Dict[str, Any]): Additional metrics
- **feedback** (Optional[str]): Text feedback
- **metadata** (Optional[Dict[str, Any]]): Additional metadata
- **evaluation_id** (str): Unique ID for this evaluation
- **timestamp** (Optional[str]): Timestamp of evaluation

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import EvaluationResult
   
   result = EvaluationResult(
       score=0.85,
       metrics={"accuracy": 0.9, "latency": 250},
       feedback="Good response, minor improvements possible",
       metadata={"model": "gpt-4", "version": "1.0"}
   )

EvaluationContext
~~~~~~~~~~~~~~~~~

Context information for evaluation runs.

.. autoclass:: honeyhive.evaluation.evaluators.EvaluationContext
   :members:
   :undoc-members:
   :show-inheritance:

Fields
^^^^^^

- **project** (str): Project name
- **source** (str): Source of evaluation
- **session_id** (Optional[str]): Session identifier
- **metadata** (Optional[Dict[str, Any]]): Additional context

Example
^^^^^^^

.. code-block:: python

   from honeyhive.evaluation import EvaluationContext
   
   context = EvaluationContext(
       project="my-llm-app",
       source="production",
       session_id="session-123",
       metadata={"user_id": "user-456"}
   )

Evaluation Functions
--------------------

evaluate
~~~~~~~~

Main function for running evaluations.

.. autofunction:: honeyhive.evaluation.evaluators.evaluate

Description
^^^^^^^^^^^

The ``evaluate`` function runs a set of evaluators on your task outputs,
collecting metrics and results for analysis.

Parameters
^^^^^^^^^^

- **data** (List[Dict]): Input data for evaluation
- **task** (Callable): Function that produces outputs
- **evaluators** (List): List of evaluator functions or objects
- **project** (str, optional): Project name
- **run_name** (str, optional): Name for this evaluation run
- **metadata** (Dict, optional): Additional metadata

Returns
^^^^^^^

Dict containing:
- **results**: List of evaluation results
- **metrics**: Aggregated metrics
- **summary**: Summary statistics

Example
^^^^^^^

.. code-block:: python

   from honeyhive import evaluate, evaluator
   
   @evaluator
   def check_length(inputs, outputs, min_words=5):
       words = len(outputs["response"].split())
       return {
           "word_count": words,
           "meets_minimum": words >= min_words,
           "score": 1.0 if words >= min_words else 0.0
       }
   
   # Define your task
   def my_task(input_data):
       # Your LLM logic here
       return {"response": "Generated response"}
   
   # Run evaluation
   results = evaluate(
       data=[
           {"prompt": "What is AI?"},
           {"prompt": "Explain ML"},
       ],
       task=my_task,
       evaluators=[check_length],
       project="my-project",
       run_name="baseline-eval"
   )
   
   print(f"Average score: {results['metrics']['average_score']}")
   print(f"Pass rate: {results['metrics']['pass_rate']}")

See Also
--------

- :doc:`/reference/experiments/experiments` - Experiments API
- :doc:`/tutorials/05-run-first-experiment` - Evaluation tutorial
- :doc:`/how-to/evaluation/creating-evaluators` - Creating custom evaluators
- :doc:`/how-to/evaluation/best-practices` - Evaluation best practices

