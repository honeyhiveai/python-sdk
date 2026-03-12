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
   datasets = client.datasets.list(project="your-project")
   metrics = client.metrics.list(project="your-project")


BaseAPI
-------

Base class for all API endpoint clients. All API classes (``DatasetsAPI``, ``EventsAPI``, etc.) inherit from ``BaseAPI``.

DatasetsAPI
-----------

API client for dataset operations.

.. autoclass:: honeyhive.api.client.DatasetsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.create_dataset

create_async
^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.create_async

list_datasets
^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.list_datasets

get_dataset
^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.get_dataset

update_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.update_dataset

delete_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.DatasetsAPI.delete_dataset


Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateDatasetRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a dataset
   dataset = client.datasets.create_dataset(
       CreateDatasetRequest(
           project="your-project",
           name="test-dataset",
           description="Test dataset for evaluation"
       )
   )
   
   # List datasets
   datasets = client.datasets.list_datasets(project="your-project")
   
   # Get a specific dataset response by ID
   dataset_response = client.datasets.get_dataset("dataset-id")

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
   datapoint = client.datapoints.create_datapoint(
       CreateDatapointRequest(
           inputs={"query": "What is machine learning?"},
           ground_truth="Machine learning is a subset of AI...",
           linked_datasets=["dataset-id"]
       )
   )
   
   # List datapoints for a project
   datapoints = client.datapoints.list(project="your-project")
   
   # Get specific datapoint
   datapoint = client.datapoints.get("datapoint-id")

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
   
   # List metrics for a project
   metrics = client.metrics.list(project="your-project")


ProjectsAPI
-----------

API client for project operations.

.. autoclass:: honeyhive.api.client.ProjectsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ProjectsAPI.create_project

list_projects
^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ProjectsAPI.list_projects

get_project
^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ProjectsAPI.get_project

update_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ProjectsAPI.update_project

delete_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ProjectsAPI.delete_project

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateProjectRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a project
   project = client.projects.create(
       CreateProjectRequest(
           name="my-llm-project",
           description="Production LLM application"
       )
   )
   
   # List all projects
   projects = client.projects.list_projects()

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
   
   client = HoneyHive(api_key="your-api-key")
   
   from honeyhive.models import StartSessionRequestBody, SessionStartRequest
   
   # Start a session
   session = client.sessions.start(
       StartSessionRequestBody(
           session=SessionStartRequest(
               project="your-project",
               session_name="user-interaction"
           )
       )
   )
   
   # Get a session by ID
   event = client.sessions.get(session.session_id)

ToolsAPI
--------

API client for tool operations.

.. autoclass:: honeyhive.api.client.ToolsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ToolsAPI.create_tool

list_tools
^^^^^^^^^^

.. automethod:: honeyhive.api.client.ToolsAPI.list_tools

get_tool
^^^^^^^^

.. automethod:: honeyhive.api.client.ToolsAPI.get_tool

update_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ToolsAPI.update_tool

delete_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.client.ToolsAPI.delete_tool

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import CreateToolRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Create a tool
   tool = client.tools.create_tool(
       CreateToolRequest(
           project="your-project",
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

ExperimentsAPI
--------------

API client for experiment run operations. Also accessible as ``client.evaluations`` (backwards compatibility alias).

.. autoclass:: honeyhive.api.client.ExperimentsAPI
   :members:
   :undoc-members:
   :show-inheritance:

.. note::
   ``client.evaluations`` is an alias to ``client.experiments`` for backwards compatibility.
   Neither exposes a top-level ``evaluate()`` method — use ``honeyhive.experiments.evaluate()``
   to run experiments. See :doc:`/reference/experiments/core-functions`.

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # List experiment runs
   runs = client.experiments.list_runs(project="your-project")
   
   # Get a specific run
   run = client.experiments.get_run(run_id="run-123")
   
   # Compare two runs
   comparison = client.experiments.compare_runs(
       new_run_id="run-123",
       old_run_id="run-456",
       project_id="your-project"
   )

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
   
   client = HoneyHive(api_key="your-api-key")
   
   from honeyhive.models import PostEventRequest
   
   # Create an event
   response = client.events.create(
       PostEventRequest(
           project="your-project",
           event_type="model",
           event_name="gpt-4-call",
           inputs={"prompt": "Hello"},
           outputs={"completion": "Hi there!"},
           metrics={"latency": 250}
       )
   )

See Also
--------

- :doc:`models-complete` - Request and response models
- :doc:`errors` - Error handling
- :doc:`tracer` - Tracer API



