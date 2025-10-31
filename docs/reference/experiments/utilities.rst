Utility Functions
=================

Helper functions for dataset preparation and ID generation.

generate_external_dataset_id()
------------------------------

.. py:function:: generate_external_dataset_id(datapoints, custom_id=None)

   Generate a unique EXT- prefixed dataset ID for client-side datasets.

   :param datapoints: List of datapoints
   :type datapoints: List[Dict[str, Any]]
   
   :param custom_id: Optional custom suffix for the ID
   :type custom_id: Optional[str]
   
   :returns: EXT- prefixed dataset ID
   :rtype: str

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import generate_external_dataset_id
      
      dataset = [
          {"inputs": {"x": 1}, "ground_truth": {"y": 2}},
          {"inputs": {"x": 2}, "ground_truth": {"y": 4}},
      ]
      
      dataset_id = generate_external_dataset_id(dataset)
      print(dataset_id)  # e.g., "EXT-a1b2c3d4e5f6"

   **With Custom ID:**

   .. code-block:: python

      dataset_id = generate_external_dataset_id(dataset, custom_id="my-test")
      print(dataset_id)  # e.g., "EXT-my-test-a1b2c3d4"

generate_external_datapoint_id()
--------------------------------

.. py:function:: generate_external_datapoint_id(datapoint, index, custom_id=None)

   Generate a unique EXT- prefixed datapoint ID.

   :param datapoint: Datapoint dictionary
   :type datapoint: Dict[str, Any]
   
   :param index: Index of datapoint in dataset
   :type index: int
   
   :param custom_id: Optional custom suffix
   :type custom_id: Optional[str]
   
   :returns: EXT- prefixed datapoint ID
   :rtype: str

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import generate_external_datapoint_id
      
      datapoint = {"inputs": {"x": 1}, "ground_truth": {"y": 2}}
      
      dp_id = generate_external_datapoint_id(datapoint, index=0)
      print(dp_id)  # e.g., "EXT-d1e2f3a4b5c6"

prepare_external_dataset()
--------------------------

.. py:function:: prepare_external_dataset(datapoints, custom_dataset_id=None)

   Prepare a list of datapoints for an external dataset.
   
   Ensures all datapoints have EXT- prefixed IDs and generates
   a dataset ID if not provided.

   :param datapoints: List of datapoints
   :type datapoints: List[Dict[str, Any]]
   
   :param custom_dataset_id: Optional custom dataset ID
   :type custom_dataset_id: Optional[str]
   
   :returns: Tuple of (dataset_id, list of datapoint_ids)
   :rtype: Tuple[str, List[str]]

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import prepare_external_dataset
      
      dataset = [
          {"inputs": {"query": "Q1"}, "ground_truth": {"answer": "A1"}},
          {"inputs": {"query": "Q2"}, "ground_truth": {"answer": "A2"}},
      ]
      
      dataset_id, datapoint_ids = prepare_external_dataset(dataset)
      
      print(f"Dataset ID: {dataset_id}")
      print(f"Datapoint IDs: {datapoint_ids}")
      
      # Output:
      # Dataset ID: EXT-abc123def456
      # Datapoint IDs: ['EXT-dp1hash', 'EXT-dp2hash']

prepare_run_request_data()
--------------------------

.. py:function:: prepare_run_request_data(run_data, datapoint_ids=None)

   Prepare experiment run request data for backend submission.
   
   Transforms EXT- prefixed dataset_id to metadata.offline_dataset_id
   as required by the backend.

   :param run_data: Run data dictionary
   :type run_data: Dict[str, Any]
   
   :param datapoint_ids: Optional list of datapoint IDs
   :type datapoint_ids: Optional[List[str]]
   
   :returns: Transformed run data ready for backend
   :rtype: Dict[str, Any]

   .. note::
      This is typically used internally by ``evaluate()``.
      Most users don't need to call this directly.

   **Usage:**

   .. code-block:: python

      from honeyhive.experiments import prepare_run_request_data
      
      run_data = {
          "name": "my-experiment",
          "project": "my-project",
          "dataset_id": "EXT-abc123",
          "event_ids": []
      }
      
      prepared = prepare_run_request_data(run_data)
      
      # EXT- dataset_id moved to metadata
      print(prepared["dataset_id"])  # None
      print(prepared["metadata"]["offline_dataset_id"])  # "EXT-abc123"

See Also
--------

- :doc:`core-functions` - Use these utilities via evaluate()
- :doc:`../../../how-to/evaluation/index` - Tutorial
