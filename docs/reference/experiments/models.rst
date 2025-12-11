Data Models
===========

Pydantic models for experiment runs, results, and comparisons.

ExperimentRunStatus
-------------------

.. py:class:: ExperimentRunStatus

   Enum representing the status of an experiment run.

   **Values:**

   - ``PENDING`` - Run created but not started
   - ``RUNNING`` - Currently executing
   - ``COMPLETED`` - Finished successfully
   - ``FAILED`` - Execution failed
   - ``CANCELLED`` - Manually cancelled

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import ExperimentRunStatus
      
      if result.status == ExperimentRunStatus.COMPLETED:
          print("Experiment finished!")

MetricDatapoints
----------------

.. py:class:: MetricDatapoints

   Model for tracking passed/failed datapoint IDs per metric.

   **Attributes:**

   - ``passed`` (List[str]) - List of datapoint IDs that passed this metric
   - ``failed`` (List[str]) - List of datapoint IDs that failed this metric

MetricDetail
------------

.. py:class:: MetricDetail

   Detailed information about a single metric result.

   **Attributes:**

   - ``metric_name`` (str) - Name of the metric
   - ``metric_type`` (Optional[str]) - Type of metric ("numeric", "boolean", etc.)
   - ``event_name`` (Optional[str]) - Name of the event that generated this metric
   - ``event_type`` (Optional[str]) - Type of event ("model", "tool", etc.)
   - ``aggregate`` (Optional[Union[float, int, bool, str]]) - Aggregated value across all datapoints
   - ``values`` (Optional[List[Any]]) - Individual values per datapoint
   - ``datapoints`` (Optional[MetricDatapoints]) - Passed/failed datapoint tracking

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import get_run_result
      
      result = get_run_result(client, "run-123")
      
      # Get a specific metric detail
      accuracy = result.metrics.get_metric("accuracy_evaluator")
      if accuracy:
          print(f"Aggregate: {accuracy.aggregate}")
          print(f"Type: {accuracy.metric_type}")

DatapointMetric
---------------

.. py:class:: DatapointMetric

   Individual metric value for a single datapoint.

   **Attributes:**

   - ``name`` (str) - Name of the metric
   - ``event_name`` (Optional[str]) - Name of the event
   - ``event_type`` (Optional[str]) - Type of event
   - ``value`` (Optional[Union[float, int, bool, str]]) - Metric value for this datapoint
   - ``passed`` (Optional[bool]) - Whether this metric passed for this datapoint

DatapointResult
---------------

.. py:class:: DatapointResult

   Result for a single datapoint in an experiment run.

   **Attributes:**

   - ``datapoint_id`` (Optional[str]) - Unique identifier for the datapoint
   - ``session_id`` (Optional[str]) - Session ID associated with this datapoint
   - ``passed`` (Optional[bool]) - Whether all metrics passed for this datapoint
   - ``metrics`` (Optional[List[DatapointMetric]]) - Individual metric results

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import get_run_result
      
      result = get_run_result(client, "run-123")
      
      for datapoint in result.datapoints:
          print(f"Datapoint: {datapoint.datapoint_id}")
          print(f"Passed: {datapoint.passed}")
          if datapoint.metrics:
              for metric in datapoint.metrics:
                  print(f"  {metric.name}: {metric.value}")

AggregatedMetrics
-----------------

.. py:class:: AggregatedMetrics

   Aggregated experiment metrics with support for both new ``details`` array format
   and legacy ``model_extra`` format for backward compatibility.

   **Attributes:**

   - ``aggregation_function`` (Optional[str]) - Aggregation method used ("average", "sum", etc.)
   - ``details`` (List[MetricDetail]) - List of metric details from backend (new format)

   **Methods:**

   .. py:method:: get_metric(metric_name: str) -> Optional[Union[MetricDetail, Dict[str, Any]]]

      Get value for a specific metric. Supports both new ``details`` array format
      (returns ``MetricDetail``) and legacy ``model_extra`` format (returns dict).

      :param metric_name: Name of the metric
      :returns: MetricDetail object, dict, or None if not found

   .. py:method:: list_metrics() -> List[str]

      List all available metric names.

      :returns: List of metric names from ``details`` array or ``model_extra`` keys

   .. py:method:: get_all_metrics() -> Dict[str, Union[MetricDetail, Dict[str, Any]]]

      Get all metrics as a dictionary.

      :returns: Dictionary mapping metric names to MetricDetail objects or dicts

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import get_run_result
      
      result = get_run_result(client, "run-123")
      metrics = result.metrics
      
      # Get specific metric (returns MetricDetail with new format)
      accuracy = metrics.get_metric("accuracy_evaluator")
      if accuracy:
          # Access typed attributes
          print(f"Aggregate: {accuracy.aggregate}")
          print(f"Type: {accuracy.metric_type}")
      
      # List all metrics
      metric_names = metrics.list_metrics()
      
      # Get all as dict
      all_metrics = metrics.get_all_metrics()

ExperimentResultSummary
-----------------------

.. py:class:: ExperimentResultSummary

   Complete summary of an experiment run with aggregated results.

   **Attributes:**

   - ``run_id`` (str) - Unique run identifier
   - ``status`` (ExperimentRunStatus) - Current run status
   - ``success`` (bool) - Whether run completed successfully
   - ``passed`` (List[str]) - List of passed datapoint IDs
   - ``failed`` (List[str]) - List of failed datapoint IDs
   - ``metrics`` (AggregatedMetrics) - Aggregated evaluation metrics
   - ``datapoints`` (List[Any]) - Individual datapoint results

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import evaluate, evaluator
      
      @evaluator
      def my_evaluator(outputs, inputs, ground_truth):
          return {"score": 0.9}
      
      result = evaluate(
          function=my_function,
          dataset=test_data,
          evaluators=[my_evaluator],
          api_key="key",
          project="project"
      )
      
      # Access summary fields
      print(f"Run ID: {result.run_id}")
      print(f"Status: {result.status}")
      print(f"Success: {result.success}")
      print(f"Passed: {len(result.passed)}")
      print(f"Failed: {len(result.failed)}")
      
      # Access metrics
      avg_score = result.metrics.get_metric("my_evaluator")
      print(f"Average score: {avg_score}")

RunComparisonResult
-------------------

.. py:class:: RunComparisonResult

   Result of comparing two experiment runs.

   **Attributes:**

   - ``new_run_id`` (str) - ID of the new run
   - ``old_run_id`` (str) - ID of the old run
   - ``common_datapoints`` (int) - Count of datapoints in both runs
   - ``new_only_datapoints`` (int) - Count of datapoints only in new run
   - ``old_only_datapoints`` (int) - Count of datapoints only in old run
   - ``metric_deltas`` (Dict[str, Any]) - Per-metric comparison data

   **Methods:**

   .. py:method:: get_metric_delta(metric_name: str) -> Optional[Dict[str, Any]]

      Get comparison data for a specific metric.

      :param metric_name: Name of the metric
      :returns: Dict with delta information or None

      Returns dict with keys:
      
      - ``old_aggregate`` - Old run's aggregated value
      - ``new_aggregate`` - New run's aggregated value
      - ``improved_count`` - Number of improved datapoints
      - ``degraded_count`` - Number of degraded datapoints
      - ``improved`` - List of improved datapoint IDs
      - ``degraded`` - List of degraded datapoint IDs

   .. py:method:: list_improved_metrics() -> List[str]

      List metrics that improved in the new run.

      :returns: List of metric names with improved_count > 0

   .. py:method:: list_degraded_metrics() -> List[str]

      List metrics that degraded in the new run.

      :returns: List of metric names with degraded_count > 0

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import compare_runs
      
      comparison = compare_runs(
          client=client,
          new_run_id="run-new",
          old_run_id="run-old"
      )
      
      # Overview
      print(f"Common datapoints: {comparison.common_datapoints}")
      print(f"New datapoints: {comparison.new_only_datapoints}")
      print(f"Old datapoints: {comparison.old_only_datapoints}")
      
      # Metric analysis
      improved = comparison.list_improved_metrics()
      degraded = comparison.list_degraded_metrics()
      
      print(f"Improved: {improved}")
      print(f"Degraded: {degraded}")
      
      # Detailed metric delta
      accuracy_delta = comparison.get_metric_delta("accuracy")
      if accuracy_delta:
          print(f"Old: {accuracy_delta['old_aggregate']}")
          print(f"New: {accuracy_delta['new_aggregate']}")
          print(f"Improved datapoints: {len(accuracy_delta['improved'])}")

See Also
--------

- :doc:`core-functions` - Functions that return these models
- :doc:`results` - Retrieve and compare results
- :doc:`../../../how-to/evaluation/index` - Tutorial
