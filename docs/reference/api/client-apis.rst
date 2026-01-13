API Client Classes
==================

This section documents all API client classes for interacting with the HoneyHive platform.

.. note::
   **For tracing and observability**, use :doc:`tracer` (``HoneyHiveTracer``). This page documents the ``HoneyHive`` API client for managing platform resources (datasets, projects, etc.) - typically used in scripts and automation.

.. contents:: Table of Contents
   :local:
   :depth: 2

HoneyHive Client
----------------

The main client class for interacting with the HoneyHive API.

.. autoclass:: honeyhive.api.client.HoneyHive
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :no-index:

Usage Example
~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   # Initialize the client
   client = HoneyHive(api_key="your-api-key")
   
   # Access API endpoints
   datasets = client.datasets.list()
   projects = client.projects.list()


DatasetsAPI
-----------

API client for dataset operations.

.. autoclass:: honeyhive.api.client.DatasetsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateDatasetRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a dataset
   dataset = client.datasets.create(
       CreateDatasetRequest(
           project="your-project",
           name="test-dataset",
           description="Test dataset for evaluation"
       )
   )
   
   # List datasets
   datasets = client.datasets.list()
   
   # Delete a dataset
   client.datasets.delete(id="dataset-id")


DatapointsAPI
-------------

API client for datapoint operations. Datapoints are individual records within datasets.

.. autoclass:: honeyhive.api.client.DatapointsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateDatapointRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a datapoint
   datapoint = client.datapoints.create(
       CreateDatapointRequest(
           inputs={"query": "What is machine learning?"},
           ground_truth="Machine learning is a subset of AI...",
           linked_datasets=["dataset-id"]
       )
   )
   
   # List datapoints for a dataset
   datapoints = client.datapoints.list(dataset_id="dataset-id")
   
   # Get specific datapoint
   datapoint = client.datapoints.get(id="datapoint-id")


ConfigurationsAPI
-----------------

API client for configuration operations.

.. autoclass:: honeyhive.api.client.ConfigurationsAPI
   :members:
   :undoc-members:
   :show-inheritance:


MetricsAPI
----------

API client for metrics operations.

.. autoclass:: honeyhive.api.client.MetricsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # List metrics
   metrics = client.metrics.list()
   
   # Run a metric
   result = client.metrics.run(metric_id="metric-id", event_id="event-id")


ProjectsAPI
-----------

API client for project operations.

.. autoclass:: honeyhive.api.client.ProjectsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import PostProjectRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a project
   project = client.projects.create(
       PostProjectRequest(
           name="my-llm-project",
           type="evaluation"
       )
   )
   
   # List all projects
   projects = client.projects.list()


SessionsAPI
-----------

API client for session operations.

.. autoclass:: honeyhive.api.client.SessionsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import PostSessionRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Start a session
   session = client.sessions.start(
       PostSessionRequest(
           project="your-project",
           session_name="user-interaction"
       )
   )
   
   print(f"Session ID: {session.session_id}")


ToolsAPI
--------

API client for tool operations.

.. autoclass:: honeyhive.api.client.ToolsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateToolRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a tool
   tool = client.tools.create(
       CreateToolRequest(
           name="calculator",
           description="Performs mathematical calculations",
           parameters={
               "type": "object",
               "properties": {
                   "operation": {"type": "string"},
                   "a": {"type": "number"},
                   "b": {"type": "number"}
               }
           }
       )
   )
   
   # List all tools
   tools = client.tools.list()


ExperimentsAPI
--------------

API client for experiment/evaluation operations.

.. autoclass:: honeyhive.api.client.ExperimentsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # List experiment runs
   runs = client.experiments.list_runs()
   
   # Get experiment result
   result = client.experiments.get_result(run_id="run-id")


EventsAPI
---------

API client for event operations.

.. autoclass:: honeyhive.api.client.EventsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import PostEventRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Post an event
   response = client.events.post(
       PostEventRequest(
           project="your-project",
           event_type="model",
           model="gpt-4",
           inputs={"prompt": "Hello"},
           outputs={"response": "Hi there!"}
       )
   )


See Also
--------

- :doc:`models-complete` - Request and response models
- :doc:`errors` - Error handling
- :doc:`tracer` - Tracer API
