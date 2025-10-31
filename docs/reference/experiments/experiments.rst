Experiments Module
==================

**Complete API reference** for the HoneyHive experiments framework - evaluate LLM outputs, compare models, and analyze performance at scale.

.. note::
   The ``experiments`` module replaces the deprecated ``evaluation`` module with improved architecture, better tracer integration, and backend-powered aggregation.

Overview
--------

The experiments module provides a comprehensive framework for:

- **Automated Evaluation**: Run custom evaluators against LLM outputs
- **Dataset Management**: Support for both external and HoneyHive-managed datasets
- **Results Analysis**: Backend-aggregated metrics and comparison tools
- **A/B Testing**: Compare multiple experiment runs with detailed metrics

Quick Start
-----------

**Basic Experiment**

.. code-block:: python

   from honeyhive.experiments import evaluate, evaluator
   
   @evaluator
   def accuracy_check(outputs, inputs, ground_truth):
       """Check if output matches expected result."""
       return {
           "score": 1.0 if outputs == ground_truth else 0.0,
           "passed": outputs == ground_truth
       }
   
   # Run experiment
   result = evaluate(
       function=my_llm_function,
       dataset=[
           {"inputs": {"query": "What is 2+2?"}, "ground_truth": {"answer": "4"}},
           {"inputs": {"query": "What is 3+3?"}, "ground_truth": {"answer": "6"}},
       ],
       evaluators=[accuracy_check],
       api_key="your-api-key",
       project="your-project",
       name="accuracy-test"
   )
   
   print(f"Success: {result.success}")
   print(f"Passed: {result.passed}/{result.passed + result.failed}")

Module Contents
---------------

Core Functions
~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   core-functions

Primary functions for running experiments and managing execution.

Evaluators
~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   evaluators

Decorator-based evaluator system for defining custom quality checks.

Results
~~~~~~~

.. toctree::
   :maxdepth: 2

   results

Functions for retrieving and comparing experiment results.

Data Models
~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   models

Pydantic models for experiment runs, results, and comparisons.

Utilities
~~~~~~~~~

.. toctree::
   :maxdepth: 2

   utilities

Helper functions for dataset preparation and ID generation.

Key Concepts
------------

Experiments vs Traces
~~~~~~~~~~~~~~~~~~~~~

**Traces** capture what happened during execution (spans, events, timing).

**Experiments** evaluate how well it happened (quality, accuracy, performance).

They work together:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.experiments import evaluate, evaluator
   
   # Tracer captures execution details
   tracer = HoneyHiveTracer(api_key="key", project="project")
   
   # Evaluator assesses quality
   @evaluator
   def quality_check(outputs, inputs, ground_truth):
       return {"score": calculate_quality(outputs, ground_truth)}
   
   # evaluate() runs function with both tracing + evaluation
   result = evaluate(
       function=traced_llm_call,
       dataset=test_cases,
       evaluators=[quality_check],
       api_key="key",
       project="project"
   )

External vs Managed Datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**External Datasets** - Your own test data:

.. code-block:: python

   # SDK generates EXT- prefixed IDs
   result = evaluate(
       function=my_function,
       dataset=[
           {"inputs": {...}, "ground_truth": {...}},
           {"inputs": {...}, "ground_truth": {...}},
       ],
       # ... other params
   )

**Managed Datasets** - Stored in HoneyHive:

.. code-block:: python

   # Reference existing dataset by ID
   result = evaluate(
       function=my_function,
       dataset_id="dataset-abc-123",
       # ... other params
   )

Evaluator Architecture
~~~~~~~~~~~~~~~~~~~~~~

Modern decorator-based approach (not class inheritance):

.. code-block:: python

   @evaluator
   def sync_evaluator(outputs, inputs, ground_truth):
       """Synchronous evaluator."""
       return {"score": 0.9}
   
   @aevaluator
   async def async_evaluator(outputs, inputs, ground_truth):
       """Asynchronous evaluator."""
       result = await external_api_call(outputs)
       return {"score": result.score}

Aggregation & Comparison
~~~~~~~~~~~~~~~~~~~~~~~~

Backend handles aggregation automatically:

.. code-block:: python

   from honeyhive.experiments import get_run_result, compare_runs
   
   # Get aggregated results
   result = get_run_result(client, run_id="run-123")
   print(f"Average score: {result.metrics.get_metric('accuracy')}")
   
   # Compare two runs
   comparison = compare_runs(
       client=client,
       new_run_id="run-new",
       old_run_id="run-old"
   )
   
   print(f"Common datapoints: {comparison.common_datapoints}")
   print(f"Improved metrics: {comparison.list_improved_metrics()}")
   print(f"Degraded metrics: {comparison.list_degraded_metrics()}")

Migration from evaluation Module
--------------------------------

The ``evaluation`` module is deprecated. Migrate to ``experiments``:

**Import Changes**

.. code-block:: python

   # OLD
   from honeyhive.evaluation import evaluate, BaseEvaluator
   
   # NEW
   from honeyhive.experiments import evaluate, evaluator

**Evaluator Pattern Changes**

.. code-block:: python

   # OLD - Class-based
   class MyEvaluator(BaseEvaluator):
       def evaluate(self, inputs, outputs, ground_truth):
           return {"score": 0.9}
   
   # NEW - Decorator-based
   @evaluator
   def my_evaluator(outputs, inputs, ground_truth):
       return {"score": 0.9}

**Function Signature Changes**

.. code-block:: python

   # OLD
   evaluate(
       inputs=inputs,
       outputs=outputs,
       evaluators=[my_evaluator]
   )
   
   # NEW
   evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=[my_evaluator],
       api_key="key",
       project="project"
   )

See Also
--------

- :doc:`../../how-to/evaluation/index` - Learn experiments basics
- :doc:`../../how-to/evaluation/index` - Problem-solving guides
- :doc:`../evaluation/deprecation-notice` - Deprecation details
- :doc:`../../how-to/migration-compatibility/migration-guide` - Full migration guide

