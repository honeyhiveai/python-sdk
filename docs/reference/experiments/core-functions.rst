Core Functions
==============

Primary functions for running experiments and managing execution.

evaluate()
----------

.. py:function:: evaluate(function, dataset=None, dataset_id=None, evaluators=None, api_key=None, project=None, name=None, source=None, max_workers=1, aggregate_function="average", verbose=False)

   Run an experiment by executing a function against a dataset and evaluating outputs.

   This is the main entry point for the experiments framework. It handles:
   
   - Function execution with tracer integration
   - Evaluator orchestration (sync and async)
   - Session/event linking
   - Results aggregation via backend

   :param function: Function to test. Should accept ``Dict[str, Any]`` (datapoint) and return ``Dict[str, Any]`` (outputs).
   :type function: Callable[[Dict[str, Any]], Dict[str, Any]]
   
   :param dataset: List of test cases with ``inputs`` and optional ``ground_truth``. Mutually exclusive with ``dataset_id``.
   :type dataset: Optional[List[Dict[str, Any]]]
   
   :param dataset_id: ID of HoneyHive-managed dataset. Mutually exclusive with ``dataset``.
   :type dataset_id: Optional[str]
   
   :param evaluators: List of evaluator functions decorated with ``@evaluator`` or ``@aevaluator``.
   :type evaluators: Optional[List[Callable]]
   
   :param api_key: HoneyHive API key. Falls back to ``HH_API_KEY`` environment variable.
   :type api_key: Optional[str]
   
   :param project: HoneyHive project name. Falls back to ``HH_PROJECT`` environment variable.
   :type project: Optional[str]
   
   :param name: Human-readable name for this experiment run.
   :type name: Optional[str]
   
   :param source: Source identifier for this experiment (e.g., "ci-pipeline", "local-dev").
   :type source: Optional[str]
   
   :param max_workers: Maximum number of concurrent workers for parallel execution.
   :type max_workers: int
   
   :param aggregate_function: Aggregation method for metrics ("average", "sum", "min", "max").
   :type aggregate_function: str
   
   :param verbose: Enable detailed logging.
   :type verbose: bool
   
   :returns: Experiment result summary with aggregated metrics.
   :rtype: ExperimentResultSummary
   
   :raises ValueError: If neither ``dataset`` nor ``dataset_id`` provided, or if both provided.

   **Basic Usage**

   .. code-block:: python

      from honeyhive.experiments import evaluate, evaluator
      
      @evaluator
      def accuracy_evaluator(outputs, inputs, ground_truth):
          return {"score": 1.0 if outputs == ground_truth else 0.0}
      
      def my_llm_function(datapoint):
          inputs = datapoint["inputs"]
          # Your LLM logic here
          return {"answer": process(inputs["query"])}
      
      result = evaluate(
          function=my_llm_function,
          dataset=[
              {"inputs": {"query": "Q1"}, "ground_truth": {"answer": "A1"}},
              {"inputs": {"query": "Q2"}, "ground_truth": {"answer": "A2"}},
          ],
          evaluators=[accuracy_evaluator],
          api_key="your-api-key",
          project="your-project",
          name="accuracy-test-v1"
      )
      
      print(f"Success: {result.success}")
      print(f"Passed: {result.passed} / {result.passed + result.failed}")
      print(f"Avg accuracy: {result.metrics.get_metric('accuracy_evaluator')}")

   **External Dataset (Client-Side Data)**

   .. code-block:: python

      # SDK auto-generates EXT- prefixed IDs
      result = evaluate(
          function=my_function,
          dataset=[
              {"inputs": {"x": 1}, "ground_truth": {"y": 2}},
              {"inputs": {"x": 2}, "ground_truth": {"y": 4}},
          ],
          evaluators=[my_evaluator],
          api_key="key",
          project="project"
      )

   **Managed Dataset (HoneyHive-Stored)**

   .. code-block:: python

      # Use existing dataset by ID
      result = evaluate(
          function=my_function,
          dataset_id="dataset-abc-123",  # Pre-created in HoneyHive
          evaluators=[my_evaluator],
          api_key="key",
          project="project"
      )

   **Multiple Evaluators**

   .. code-block:: python

      @evaluator
      def accuracy(outputs, inputs, ground_truth):
          return {"score": calculate_accuracy(outputs, ground_truth)}
      
      @evaluator
      def relevance(outputs, inputs, ground_truth):
          return {"score": calculate_relevance(outputs, inputs)}
      
      @aevaluator
      async def external_check(outputs, inputs, ground_truth):
          result = await external_api.validate(outputs)
          return {"score": result.score}
      
      result = evaluate(
          function=my_function,
          dataset=test_data,
          evaluators=[accuracy, relevance, external_check],
          api_key="key",
          project="project",
          max_workers=4  # Parallel execution
      )

   **Accessing Results**

   .. code-block:: python

      result = evaluate(...)
      
      # Overall status
      print(f"Run ID: {result.run_id}")
      print(f"Status: {result.status}")
      print(f"Success: {result.success}")
      
      # Aggregated metrics
      accuracy_score = result.metrics.get_metric("accuracy")
      all_metrics = result.metrics.get_all_metrics()
      
      # Individual datapoints
      for datapoint in result.datapoints:
          print(f"Datapoint: {datapoint}")

run_experiment()
----------------

.. py:function:: run_experiment(function, dataset, datapoint_ids, experiment_context, api_key, max_workers=1, verbose=False)

   Low-level function to execute a function against a dataset with tracer integration.

   .. warning::
      This is a low-level API. Most users should use ``evaluate()`` instead,
      which provides a higher-level interface with evaluator support.

   :param function: Function to execute for each datapoint.
   :type function: Callable[[Dict[str, Any]], Dict[str, Any]]
   
   :param dataset: List of datapoints to process.
   :type dataset: List[Dict[str, Any]]
   
   :param datapoint_ids: List of datapoint IDs (must match dataset length).
   :type datapoint_ids: List[str]
   
   :param experiment_context: Context with run_id, dataset_id, project, source.
   :type experiment_context: ExperimentContext
   
   :param api_key: HoneyHive API key.
   :type api_key: str
   
   :param max_workers: Maximum concurrent workers.
   :type max_workers: int
   
   :param verbose: Enable detailed logging.
   :type verbose: bool
   
   :returns: List of execution results with outputs, errors, and session IDs.
   :rtype: List[Dict[str, Any]]

   **Usage Example**

   .. code-block:: python

      from honeyhive.experiments import run_experiment, ExperimentContext
      
      context = ExperimentContext(
          run_id="run-123",
          dataset_id="dataset-456",
          project="my-project",
          source="test"
      )
      
      results = run_experiment(
          function=my_function,
          dataset=test_data,
          datapoint_ids=["dp-1", "dp-2", "dp-3"],
          experiment_context=context,
          api_key="key",
          max_workers=2
      )
      
      for result in results:
          print(f"Datapoint: {result['datapoint_id']}")
          print(f"Status: {result['status']}")
          print(f"Outputs: {result['outputs']}")
          if result['error']:
              print(f"Error: {result['error']}")

ExperimentContext
-----------------

.. py:class:: ExperimentContext

   Context object storing experiment metadata for tracer integration.

   :param run_id: Unique experiment run identifier.
   :type run_id: str
   
   :param dataset_id: Dataset identifier (may be EXT- prefixed for external datasets).
   :type dataset_id: str
   
   :param project: HoneyHive project name.
   :type project: str
   
   :param source: Optional source identifier.
   :type source: Optional[str]

   **Methods**

   .. py:method:: to_tracer_config()

      Convert context to tracer configuration dictionary.
      
      :returns: Configuration dict for HoneyHiveTracer initialization.
      :rtype: Dict[str, Any]

   **Usage Example**

   .. code-block:: python

      from honeyhive.experiments import ExperimentContext
      
      context = ExperimentContext(
          run_id="run-abc-123",
          dataset_id="EXT-dataset-xyz",
          project="my-project",
          source="ci-pipeline"
      )
      
      # Convert to tracer config
      tracer_config = context.to_tracer_config()
      
      # Use with HoneyHiveTracer
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer(**tracer_config, api_key="key")

Best Practices
--------------

**1. Function Signatures**

Your function should accept a datapoint dict and return outputs dict:

.. code-block:: python

   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:

       Args:
           datapoint: Contains 'inputs' and optionally 'ground_truth'
       
       Returns:
           Dict with your outputs (e.g., {"answer": "...", "confidence": 0.9})

       inputs = datapoint["inputs"]
       # Process inputs
       return {"answer": process(inputs)}

**2. Error Handling**

Let exceptions bubble up - ``evaluate()`` catches and logs them:

.. code-block:: python

   def my_function(datapoint):
       try:
           result = risky_operation(datapoint["inputs"])
           return {"result": result}
       except SpecificError as e:
           # Log but don't suppress - let evaluate() handle it
           logger.warning(f"Operation failed: {e}")
           raise

**3. Parallel Execution**

Use ``max_workers`` for I/O-bound workloads:

.. code-block:: python

   # Good for API calls
   result = evaluate(
       function=api_heavy_function,
       dataset=large_dataset,
       evaluators=[...],
       max_workers=10,  # High concurrency for I/O
       api_key="key",
       project="project"
   )
   
   # For CPU-bound work, keep lower
   result = evaluate(
       function=cpu_intensive_function,
       dataset=dataset,
       max_workers=2,  # Lower for CPU work
       api_key="key",
       project="project"
   )

**4. Dataset Size Management**

For large datasets, use batching:

.. code-block:: python

   def run_large_experiment(full_dataset, batch_size=100):
       """Process large dataset in batches."""
       results = []
       
       for i in range(0, len(full_dataset), batch_size):
           batch = full_dataset[i:i+batch_size]
           
           result = evaluate(
               function=my_function,
               dataset=batch,
               evaluators=[my_evaluator],
               name=f"experiment-batch-{i//batch_size}",
               api_key="key",
               project="project"
           )
           
           results.append(result)
       
       return results

See Also
--------

- :doc:`evaluators` - Define custom evaluators
- :doc:`results` - Retrieve and compare results
- :doc:`models` - Result data models
- :doc:`../../../how-to/evaluation/index` - Experiments tutorial

