Result Analysis
===============

How do I access and analyze experiment results programmatically?
----------------------------------------------------------------

Use ``get_run_result()`` and ``get_run_metrics()`` functions.

How do I retrieve results for a specific run?
---------------------------------------------

**Use get_run_result()**

.. code-block:: python

   from honeyhive.experiments import evaluate, get_run_result
   from honeyhive import HoneyHive
   
   # Run experiment
   result = evaluate(
       function=my_function,
       dataset=dataset,
       evaluators=[my_evaluator],
       api_key="your-api-key",
       project="your-project"
   )
   
   run_id = result.run_id
   
   # Get detailed results later
   client = HoneyHive(api_key="your-api-key")
   detailed_result = get_run_result(
       client=client,
       run_id=run_id
   )
   
   print(detailed_result.status)
   print(detailed_result.metrics)

How do I get aggregated metrics for a run?
------------------------------------------

**Use get_run_metrics()**

.. code-block:: python

   from honeyhive.experiments import get_run_metrics
   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   metrics = get_run_metrics(
       client=client,
       run_id="run_abc123",
       aggregate_function="average"  # or "median", "mode"
   )
   
   print(f"Average accuracy: {metrics.get('accuracy')}")
   print(f"Average quality: {metrics.get('quality')}")

How do I export results to a file?
----------------------------------

**Use to_json() Method**

.. code-block:: python

   result = evaluate(
       function=my_function,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project",
       name="my-experiment"
   )
   
   # Exports to {name}.json
   result.to_json()  # Creates "my-experiment.json"

The JSON file contains all inputs, outputs, and metrics.

See Also
--------

- :doc:`running-experiments` - Run experiments
- :doc:`comparing-experiments` - Compare results
- :doc:`../../reference/experiments/results` - Complete API reference

