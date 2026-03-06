Evaluation Framework API Reference
==================================

.. deprecated::

   The ``honeyhive.evaluation`` module is deprecated. Use the decorator-based
   evaluators in :doc:`../experiments/evaluators` instead (``@evaluator``,
   ``@aevaluator``). The classes below are retained for backwards compatibility.

.. currentmodule:: honeyhive.evaluation

The HoneyHive evaluation framework provides built-in evaluators for assessing
LLM outputs. All evaluators follow a standard interface: they accept ``inputs``,
``outputs``, and an optional ``ground_truth`` dict, and return a metrics dict.

**Available built-in evaluators:**

.. code-block:: python

   from honeyhive.evaluation import (
       ExactMatchEvaluator,
       F1ScoreEvaluator,
       LengthEvaluator,
       SemanticSimilarityEvaluator,
       BaseEvaluator,
   )

   # Built-in evaluator keys (for use with evaluate_batch)
   # "exact_match", "f1_score", "length", "semantic_similarity"

Base Classes
------------

BaseEvaluator
~~~~~~~~~~~~~

.. note::

   The ``BaseEvaluator`` class has been deprecated in favor of the decorator-based
   approach. Please use the ``@evaluator`` decorator instead. See
   :doc:`../experiments/evaluators` for details.

The abstract base class for all evaluators.

**Abstract Methods:**

.. py:method:: evaluate(inputs: dict, outputs: dict, ground_truth: Optional[dict] = None, **kwargs) -> dict

   Evaluate outputs given inputs and optional ground truth.

   **Parameters:**

   :param inputs: Input data (e.g. ``{"expected": "...", "prompt": "..."}``)
   :type inputs: dict

   :param outputs: Output data (e.g. ``{"response": "..."}``)
   :type outputs: dict

   :param ground_truth: Optional ground truth data
   :type ground_truth: Optional[dict]

   **Returns:**

   :rtype: dict
   :returns: Metrics dict (varies by evaluator)

**Custom Evaluator Example:**

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator

   class MyEvaluator(BaseEvaluator):
       def __init__(self, **kwargs):
           super().__init__("my_evaluator", **kwargs)

       def evaluate(self, inputs, outputs, ground_truth=None, **kwargs):
           expected = inputs.get("expected", "")
           actual = outputs.get("response", "")
           score = float(expected.strip().lower() == actual.strip().lower())
           return {"score": score, "passed": score >= 0.7}

Built-in Evaluators
-------------------

ExactMatchEvaluator
~~~~~~~~~~~~~~~~~~~

Evaluates whether the output exactly matches the expected value (case-insensitive,
whitespace-trimmed).

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import ExactMatchEvaluator

   evaluator = ExactMatchEvaluator()

**Expected input format:**

- ``inputs["expected"]`` — the expected string
- ``outputs["response"]`` — the actual output string

**Returns:**

.. code-block:: python

   {
       "exact_match": 1.0,   # 1.0 if match, 0.0 if not
       "expected": "...",
       "actual": "..."
   }

**Usage Example:**

.. code-block:: python

   result = evaluator.evaluate(
       inputs={"expected": "Paris"},
       outputs={"response": "paris"},
   )
   print(result["exact_match"])  # 1.0

F1ScoreEvaluator
~~~~~~~~~~~~~~~~

Computes the token-level F1 score between the output and expected value. Useful for
extractive QA and information retrieval tasks.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import F1ScoreEvaluator

   evaluator = F1ScoreEvaluator()

**Expected input format:**

- ``inputs["expected"]`` — the expected string
- ``outputs["response"]`` — the actual output string

**Returns:**

.. code-block:: python

   {"f1_score": 0.85}

**Usage Example:**

.. code-block:: python

   result = evaluator.evaluate(
       inputs={"expected": "The quick brown fox"},
       outputs={"response": "A quick brown dog"},
   )
   print(result["f1_score"])  # ~0.67

LengthEvaluator
~~~~~~~~~~~~~~~

.. note::

   The ``LengthEvaluator`` class has been deprecated in favor of the decorator-based
   approach. Please implement custom length evaluators using the ``@evaluator``
   decorator.

Evaluates response length characteristics. Returns character, word, and line counts;
does not apply pass/fail thresholds.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import LengthEvaluator

   evaluator = LengthEvaluator()

**Expected input format:**

- ``outputs["response"]`` — the output string to measure

**Returns:**

.. code-block:: python

   {
       "char_count": 142,
       "word_count": 27,
       "line_count": 3
   }

**Usage Example:**

.. code-block:: python

   result = evaluator.evaluate(
       inputs={},
       outputs={"response": "This is a sample response."},
   )
   print(result["word_count"])  # 5

SemanticSimilarityEvaluator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evaluates semantic similarity between the output and expected value using word-overlap
and sentence-structure heuristics.

**Initialization:**

.. code-block:: python

   from honeyhive.evaluation import SemanticSimilarityEvaluator

   evaluator = SemanticSimilarityEvaluator()

**Expected input format:**

- ``inputs["expected"]`` — the reference string
- ``outputs["response"]`` — the actual output string

**Returns:**

.. code-block:: python

   {"semantic_similarity": 0.72}  # 0.0-1.0

**Usage Example:**

.. code-block:: python

   result = evaluator.evaluate(
       inputs={"expected": "Photosynthesis converts sunlight into energy."},
       outputs={"response": "Plants use sunlight to produce energy via photosynthesis."},
   )
   print(result["semantic_similarity"])  # e.g. 0.65

Batch Evaluation
----------------

``evaluate_batch()`` runs a list of evaluators over a dataset concurrently.

.. code-block:: python

   from honeyhive.evaluation.evaluators import evaluate_batch, ExactMatchEvaluator, F1ScoreEvaluator

   dataset = [
       {"inputs": {"expected": "Paris"}, "outputs": {"response": "paris"}},
       {"inputs": {"expected": "London"}, "outputs": {"response": "Paris"}},
   ]

   results = evaluate_batch(
       evaluators=[ExactMatchEvaluator(), F1ScoreEvaluator()],
       dataset=dataset,
       max_workers=4,
   )

Integration Patterns
--------------------

With Decorators
~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import trace, evaluate
   from honeyhive.evaluation import SemanticSimilarityEvaluator

   quality_eval = SemanticSimilarityEvaluator()

   @trace(tracer=tracer, event_type="content_generation")
   @evaluate(evaluator=quality_eval)
   def generate_response(query: str) -> str:
       return create_response(query)

With Manual Evaluation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.evaluation import ExactMatchEvaluator, F1ScoreEvaluator, LengthEvaluator

   evaluators = {
       "exact_match": ExactMatchEvaluator(),
       "f1": F1ScoreEvaluator(),
       "length": LengthEvaluator(),
   }

   inputs = {"expected": "The Eiffel Tower is in Paris."}
   outputs = {"response": "The Eiffel Tower is located in Paris, France."}

   results = {name: ev.evaluate(inputs, outputs) for name, ev in evaluators.items()}
   for name, result in results.items():
       print(f"{name}: {result}")

Migrating to Decorator-Based Evaluators
----------------------------------------

The preferred approach for new code is the ``@evaluator`` decorator:

.. code-block:: python

   # OLD (deprecated)
   from honeyhive.evaluation import ExactMatchEvaluator
   evaluator = ExactMatchEvaluator()
   result = evaluator.evaluate(inputs, outputs)

   # NEW (preferred)
   from honeyhive.experiments import evaluator

   @evaluator
   def exact_match(outputs, inputs, ground_truth=None):
       expected = inputs.get("expected", "")
       actual = outputs.get("response", "")
       return {"exact_match": float(expected.strip().lower() == actual.strip().lower())}

See :doc:`../experiments/evaluators` for the full decorator-based API.

See Also
--------

- :doc:`../api/decorators` - ``@evaluate`` decorator reference
- :doc:`../experiments/evaluators` - Decorator-based evaluators (preferred)
- :doc:`../../how-to/evaluation/index` - Evaluation guides
- :doc:`../../explanation/concepts/llm-observability` - LLM observability concepts
