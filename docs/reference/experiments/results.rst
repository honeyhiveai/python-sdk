Results Retrieval
=================

Functions for retrieving and comparing experiment results from the backend.

get_run_result()
----------------

.. py:function:: get_run_result(client, run_id, aggregate_function="average")

   Retrieve aggregated results for an experiment run from the backend.

   The backend computes aggregated metrics across all datapoints using the specified aggregation function.

   :param client: HoneyHive API client instance
   :type client: HoneyHive
   
   :param run_id: Experiment run ID
   :type run_id: str
   
   :param aggregate_function: Aggregation method ("average", "sum", "min", "max")
   :type aggregate_function: str
   
   :returns: Experiment result summary with aggregated metrics
   :rtype: ExperimentResultSummary

   **Usage:**

   .. code-block:: python

      from honeyhive import HoneyHive as Client
      from honeyhive.experiments import get_run_result
      
      client = honeyhive.HoneyHive(api_key="your-key")
      
      result = get_run_result(client, run_id="run-abc-123")
      
      print(f"Status: {result.status}")
      print(f"Success: {result.success}")
      print(f"Passed: {len(result.passed)}")
      print(f"Failed: {len(result.failed)}")
      
      # Access aggregated metrics
      accuracy = result.metrics.get_metric("accuracy_evaluator")
      print(f"Average accuracy: {accuracy}")

   **Custom Aggregation:**

   .. code-block:: python

      # Use median instead of average
      result = get_run_result(
          client,
          run_id="run-123",
          aggregate_function="median"
      )

get_run_metrics()
-----------------

.. py:function:: get_run_metrics(client, run_id)

   Retrieve raw (non-aggregated) metrics for an experiment run.

   Returns the full metrics data from the backend without aggregation,
   useful for detailed analysis or custom aggregation.

   :param client: HoneyHive API client instance
   :type client: HoneyHive
   
   :param run_id: Experiment run ID
   :type run_id: str
   
   :returns: Dictionary containing raw metrics data
   :rtype: Dict[str, Any]

   **Usage:**

   .. code-block:: python

      from honeyhive import HoneyHive as Client
      from honeyhive.experiments import get_run_metrics
      
      client = honeyhive.HoneyHive(api_key="your-key")
      
      metrics = get_run_metrics(client, run_id="run-abc-123")
      
      # Raw metrics include per-datapoint data
      print(f"Raw metrics: {metrics}")

compare_runs()
--------------

.. py:function:: compare_runs(client, new_run_id, old_run_id, aggregate_function="average")

   Compare two experiment runs using backend aggregated comparison.

   The backend identifies common datapoints between runs, computes metric deltas,
   and classifies changes as improvements or degradations.

   :param client: HoneyHive API client instance
   :type client: HoneyHive
   
   :param new_run_id: ID of the new (more recent) run
   :type new_id: str
   
   :param old_run_id: ID of the old (baseline) run
   :type old_run_id: str
   
   :param aggregate_function: Aggregation method ("average", "sum", "min", "max")
   :type aggregate_function: str
   
   :returns: Comparison result with metric deltas and improvement analysis
   :rtype: RunComparisonResult

   **Basic Comparison:**

   .. code-block:: python

      from honeyhive import HoneyHive as Client
      from honeyhive.experiments import compare_runs
      
      client = honeyhive.HoneyHive(api_key="your-key")
      
      comparison = compare_runs(
          client=client,
          new_run_id="run-v2",
          old_run_id="run-v1"
      )
      
      print(f"Common datapoints: {comparison.common_datapoints}")
      print(f"Improved metrics: {comparison.list_improved_metrics()}")
      print(f"Degraded metrics: {comparison.list_degraded_metrics()}")

   **Detailed Metric Analysis:**

   .. code-block:: python

      comparison = compare_runs(client, "run-new", "run-old")
      
      # Check specific metric
      accuracy_delta = comparison.get_metric_delta("accuracy")
      
      if accuracy_delta:
          print(f"Old accuracy: {accuracy_delta['old_aggregate']}")
          print(f"New accuracy: {accuracy_delta['new_aggregate']}")
          print(f"Improved on {accuracy_delta['improved_count']} datapoints")
          print(f"Degraded on {accuracy_delta['degraded_count']} datapoints")
          
          # Get specific datapoint IDs
          print(f"Improved: {accuracy_delta['improved']}")
          print(f"Degraded: {accuracy_delta['degraded']}")

   **A/B Testing Pattern:**

   .. code-block:: python

      # Run baseline
      baseline = evaluate(
          function=model_a,
          dataset=test_data,
          evaluators=[accuracy, latency],
          name="baseline-model-a",
          api_key="key",
          project="project"
      )
      
      # Run variant
      variant = evaluate(
          function=model_b,
          dataset=test_data,
          evaluators=[accuracy, latency],
          name="variant-model-b",
          api_key="key",
          project="project"
      )
      
      # Compare
      comparison = compare_runs(
          client,
          new_run_id=variant.run_id,
          old_run_id=baseline.run_id
      )
      
      # Decision logic
      improved = comparison.list_improved_metrics()
      degraded = comparison.list_degraded_metrics()
      
      if "accuracy" in improved and "latency" not in degraded:
          print("✅ Model B is better - deploy it!")
      else:
          print("❌ Model A is still better - keep baseline")

Best Practices
--------------

**1. Use Consistent Datasets for Comparison**

.. code-block:: python

   # GOOD - Same dataset for both runs
   dataset = load_test_dataset()
   
   run1 = evaluate(function=model_v1, dataset=dataset, ...)
   run2 = evaluate(function=model_v2, dataset=dataset, ...)
   
   comparison = compare_runs(client, run2.run_id, run1.run_id)

**2. Cache Results for Analysis**

.. code-block:: python

   # Retrieve once, analyze many times
   result = get_run_result(client, run_id)
   
   # Multiple analyses without re-fetching
   accuracy = result.metrics.get_metric("accuracy")
   latency = result.metrics.get_metric("latency")
   cost = result.metrics.get_metric("cost")

**3. Handle Missing Metrics Gracefully**

.. code-block:: python

   comparison = compare_runs(client, new_id, old_id)
   
   # Some metrics might not exist in both runs
   accuracy_delta = comparison.get_metric_delta("accuracy")
   
   if accuracy_delta:
       print(f"Accuracy changed: {accuracy_delta['new_aggregate'] - accuracy_delta['old_aggregate']}")
   else:
       print("Accuracy metric not found in both runs")

**4. Use Appropriate Aggregation**

.. code-block:: python

   # For accuracy/pass rates - use average
   result = get_run_result(client, run_id, aggregate_function="average")
   
   # For total cost - use sum
   result = get_run_result(client, run_id, aggregate_function="sum")
   
   # For worst-case analysis - use min/max
   result = get_run_result(client, run_id, aggregate_function="min")

See Also
--------

- :doc:`core-functions` - Run experiments
- :doc:`models` - Result data models
- :doc:`../../../how-to/evaluation/index` - Evaluation patterns

