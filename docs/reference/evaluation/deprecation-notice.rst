Deprecation Notice
==================

.. warning::
   **The ``evaluation`` module is deprecated and will be removed in version 2.0.0.**
   
   Please migrate to the ``experiments`` module for new features, better architecture,
   and continued support.

Overview
--------

The ``honeyhive.evaluation`` module has been superseded by ``honeyhive.experiments`` which provides:

- **Improved Architecture**: Decorator-based evaluators instead of class inheritance
- **Backend Aggregation**: Server-side metric aggregation for better performance
- **Enhanced Tracer Integration**: Seamless integration with the multi-instance tracer
- **Better Type Safety**: Pydantic v2 models with full validation
- **Cleaner API**: Simpler, more intuitive function signatures

Deprecation Timeline
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Version
     - Status
   * - 0.2.x (Current)
     - ``evaluation`` module works with deprecation warnings
   * - 1.x
     - ``evaluation`` module continues to work with warnings
   * - 2.0.0 (Future)
     - ``evaluation`` module removed, must use ``experiments``

Migration Guide
---------------

Quick Migration Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Update imports: ``honeyhive.evaluation`` → ``honeyhive.experiments``
2. Replace class-based evaluators with ``@evaluator`` decorator
3. Update ``evaluate()`` function signature
4. Update result handling to use new models

Detailed Migration Steps
~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1: Update Imports**

.. code-block:: python

   # OLD
   from honeyhive.evaluation import evaluate, BaseEvaluator, EvaluationResult
   
   # NEW
   from honeyhive.experiments import evaluate, evaluator, ExperimentResultSummary

**Step 2: Convert Class-Based Evaluators to Decorators**

.. code-block:: python

   # OLD - Class inheritance
   from honeyhive.evaluation import BaseEvaluator
   
   class AccuracyEvaluator(BaseEvaluator):
       def __init__(self, threshold=0.8):
           super().__init__("accuracy")
           self.threshold = threshold
       
       def evaluate(self, inputs, outputs, ground_truth):
           score = calculate_accuracy(outputs, ground_truth)
           return {
               "score": score,
               "passed": score >= self.threshold
           }
   
   # NEW - Decorator-based
   from honeyhive.experiments import evaluator
   
   @evaluator
   def accuracy_evaluator(outputs, inputs, ground_truth):
       """Note: outputs is first parameter in new signature."""
       score = calculate_accuracy(outputs, ground_truth)
       threshold = 0.8  # Can use closures or default args
       return {
           "score": score,
           "passed": score >= threshold
       }

**Step 3: Update evaluate() Function Calls**

.. code-block:: python

   # OLD
   from honeyhive.evaluation import evaluate
   
   result = evaluate(
       inputs=test_inputs,
       outputs=test_outputs,
       evaluators=[AccuracyEvaluator(), F1Evaluator()],
       ground_truth=expected_outputs
   )
   
   # NEW
   from honeyhive.experiments import evaluate
   
   result = evaluate(
       function=my_llm_function,  # Your function to test
       dataset=[
           {"inputs": {...}, "ground_truth": {...}},
           {"inputs": {...}, "ground_truth": {...}},
       ],
       evaluators=[accuracy_evaluator, f1_evaluator],  # Function refs
       api_key="your-key",
       project="your-project",
       name="experiment-v1"
   )

**Step 4: Update Result Handling**

.. code-block:: python

   # OLD
   from honeyhive.evaluation import EvaluationResult
   
   result = evaluate(...)
   
   # Access results (old structure)
   overall_score = result.score
   metrics = result.metrics
   
   # NEW
   from honeyhive.experiments import ExperimentResultSummary
   
   result = evaluate(...)
   
   # Access results (new structure)
   print(f"Run ID: {result.run_id}")
   print(f"Status: {result.status}")
   print(f"Success: {result.success}")
   print(f"Passed: {len(result.passed)}")
   print(f"Failed: {len(result.failed)}")
   
   # Aggregated metrics
   accuracy = result.metrics.get_metric("accuracy_evaluator")
   all_metrics = result.metrics.get_all_metrics()

**Step 5: Update Async Evaluators**

.. code-block:: python

   # OLD - Async class method
   class AsyncEvaluator(BaseEvaluator):
       async def evaluate(self, inputs, outputs, ground_truth):
           result = await external_api_call(outputs)
           return {"score": result.score}
   
   # NEW - @aevaluator decorator
   from honeyhive.experiments import aevaluator
   
   @aevaluator
   async def async_evaluator(outputs, inputs, ground_truth):
       result = await external_api_call(outputs)
       return {"score": result.score}

Common Patterns
~~~~~~~~~~~~~~~

**Pattern 1: Built-in Evaluators**

.. code-block:: python

   # OLD
   from honeyhive.evaluation.evaluators import (
       ExactMatchEvaluator,
       LengthEvaluator,
       FactualAccuracyEvaluator
   )
   
   evaluators = [
       ExactMatchEvaluator(),
       LengthEvaluator(min_length=10, max_length=100),
       FactualAccuracyEvaluator()
   ]
   
   # NEW - Implement as decorator-based evaluators
   from honeyhive.experiments import evaluator
   
   @evaluator
   def exact_match(outputs, inputs, ground_truth):
       return {"score": 1.0 if outputs == ground_truth else 0.0}
   
   @evaluator
   def length_check(outputs, inputs, ground_truth):
       length = len(str(outputs))
       in_range = 10 <= length <= 100
       return {"score": 1.0 if in_range else 0.0}
   
   # Use external APIs for factual accuracy
   @aevaluator
   async def factual_accuracy(outputs, inputs, ground_truth):
       result = await fact_check_api(outputs, ground_truth)
       return {"score": result.accuracy}
   
   evaluators = [exact_match, length_check, factual_accuracy]

**Pattern 2: Evaluator with State**

.. code-block:: python

   # OLD
   class StatefulEvaluator(BaseEvaluator):
       def __init__(self, model):
           super().__init__("stateful")
           self.model = model  # Store state
       
       def evaluate(self, inputs, outputs, ground_truth):
           score = self.model.predict(outputs)
           return {"score": score}
   
   # NEW - Use closures or class methods with decorator
   from honeyhive.experiments import evaluator
   
   # Option 1: Closure
   def create_stateful_evaluator(model):
       @evaluator
       def stateful_evaluator(outputs, inputs, ground_truth):
           score = model.predict(outputs)
           return {"score": score}
       return stateful_evaluator
   
   model = load_model()
   my_evaluator = create_stateful_evaluator(model)
   
   # Option 2: Class with __call__
   class StatefulEvaluator:
       def __init__(self, model):
           self.model = model
       
       @evaluator
       def __call__(self, outputs, inputs, ground_truth):
           score = self.model.predict(outputs)
           return {"score": score}
   
   my_evaluator = StatefulEvaluator(load_model())

**Pattern 3: Batch Evaluation**

.. code-block:: python

   # OLD
   from honeyhive.evaluation import evaluate_batch
   
   results = evaluate_batch(
       inputs_list=batch_inputs,
       outputs_list=batch_outputs,
       evaluators=[evaluator1, evaluator2],
       max_workers=4
   )
   
   # NEW - Use evaluate() with dataset
   from honeyhive.experiments import evaluate
   
   result = evaluate(
       function=my_function,
       dataset=test_dataset,
       evaluators=[evaluator1, evaluator2],
       max_workers=4,
       api_key="key",
       project="project"
   )

Backward Compatibility Layer
----------------------------

The old ``evaluation`` module still works through a compatibility layer:

.. code-block:: python

   # This still works but shows deprecation warnings
   from honeyhive.evaluation import evaluate, evaluator
   
   # Internally redirects to honeyhive.experiments
   result = evaluate(...)

**Deprecation Warnings:**

When you use the old module, you'll see warnings like:

.. code-block:: text

   DeprecationWarning: honeyhive.evaluation.evaluate is deprecated.
   Please use honeyhive.experiments.evaluate instead.
   The evaluation module will be removed in version 2.0.0.

Breaking Changes
----------------

**Parameter Order Change**

Evaluator function signature changed:

.. code-block:: python

   # OLD
   def evaluator(inputs, outputs, ground_truth):
       pass
   
   # NEW - outputs comes first
   def evaluator(outputs, inputs, ground_truth):
       pass

**evaluate() Signature Change**

The main evaluate function has a completely new signature:

.. code-block:: python

   # OLD
   evaluate(inputs, outputs, evaluators, ground_truth=None)
   
   # NEW
   evaluate(
       function,          # NEW: function to test
       dataset,           # NEW: combined inputs + ground_truth
       evaluators,
       api_key,           # NEW: required
       project,           # NEW: required
       name=None,
       max_workers=1,
       aggregate_function="average",
       verbose=False
   )

**Return Type Change**

.. code-block:: python

   # OLD
   result: EvaluationResult = evaluate(...)
   result.score           # Overall score
   result.metrics         # Dict of metrics
   result.passed          # Bool
   
   # NEW
   result: ExperimentResultSummary = evaluate(...)
   result.run_id          # Unique run ID
   result.status          # ExperimentRunStatus enum
   result.success         # Bool
   result.passed          # List[str] of passed datapoint IDs
   result.failed          # List[str] of failed datapoint IDs
   result.metrics         # AggregatedMetrics object

Support & Help
--------------

**Documentation:**

- :doc:`../experiments/experiments` - Experiments module overview
- :doc:`../../how-to/evaluation/index` - Updated tutorial
- :doc:`../../how-to/migration-compatibility/migration-guide` - Complete migration guide

**Common Issues:**

1. **Import Error**: Make sure you've updated imports to ``honeyhive.experiments``
2. **Parameter Order**: Remember ``outputs`` comes first in new evaluators
3. **Missing api_key/project**: These are now required for ``evaluate()``
4. **Result Structure**: Use new ``ExperimentResultSummary`` structure

**Getting Help:**

- GitHub Issues: https://github.com/honeyhive/python-sdk/issues
- Documentation: https://docs.honeyhive.ai
- Community: https://discord.gg/honeyhive

See Also
--------

- :doc:`../experiments/experiments` - New experiments module
- :doc:`../experiments/evaluators` - Decorator-based evaluators
- :doc:`../../how-to/migration-compatibility/migration-guide` - Migration guide

