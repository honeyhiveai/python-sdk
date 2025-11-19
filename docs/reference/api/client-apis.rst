API Client Classes
==================

This section documents all API client classes for interacting with the HoneyHive platform.

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

   from honeyhive import HoneyHive as Client
   
   # Initialize the client
   client = honeyhive.HoneyHive(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Access API endpoints
   datasets = client.datasets.list_datasets(project="your-project")
   metrics = client.metrics.get_metrics(project="your-project")


RateLimiter
-----------

Rate limiting for API calls to prevent exceeding rate limits.

.. autoclass:: honeyhive.api.client.RateLimiter
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Example
~~~~~~~

.. code-block:: python

   from honeyhive.api.client import RateLimiter
   
   # Create rate limiter (100 calls per 60 seconds)
   limiter = RateLimiter(max_calls=100, time_window=60.0)
   
   # Check if call is allowed
   if limiter.can_call():
       # Make API call
       pass
   
   # Or wait automatically
   limiter.wait_if_needed()
   # Make API call

BaseAPI
-------

Base class for all API endpoint clients.

.. autoclass:: honeyhive.api.base.BaseAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

DatasetsAPI
-----------

API client for dataset operations.

**Recent Updates**: Enhanced filtering capabilities for ``list_datasets()`` including name and include_datapoints parameters. See method documentation below for details.

.. autoclass:: honeyhive.api.datasets.DatasetsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.create_dataset

create_dataset_async
^^^^^^^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.create_dataset_async

list_datasets
^^^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.list_datasets

get_dataset
^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.get_dataset

update_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.update_dataset

delete_dataset
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.datasets.DatasetsAPI.delete_dataset


Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   from honeyhive.models import CreateDatasetRequest
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
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
   
   # Get specific dataset
   dataset = client.datasets.get_dataset(dataset_id="dataset-id")

MetricsAPI
----------

API client for metrics operations.

.. autoclass:: honeyhive.api.metrics.MetricsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
   # Get metrics for a project
   metrics = client.metrics.get_metrics(
       project="your-project",
       start_time="2024-01-01T00:00:00Z",
       end_time="2024-01-31T23:59:59Z"
   )


ProjectsAPI
-----------

API client for project operations.

.. autoclass:: honeyhive.api.projects.ProjectsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.projects.ProjectsAPI.create_project

list_projects
^^^^^^^^^^^^^

.. automethod:: honeyhive.api.projects.ProjectsAPI.list_projects

get_project
^^^^^^^^^^^

.. automethod:: honeyhive.api.projects.ProjectsAPI.get_project

update_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.projects.ProjectsAPI.update_project

delete_project
^^^^^^^^^^^^^^

.. automethod:: honeyhive.api.projects.ProjectsAPI.delete_project

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   from honeyhive.models import CreateProjectRequest
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
   # Create a project
   project = client.projects.create_project(
       CreateProjectRequest(
           name="my-llm-project",
           description="Production LLM application"
       )
   )
   
   # List all projects
   projects = client.projects.list_projects()

SessionAPI
----------

API client for session operations.

.. autoclass:: honeyhive.api.session.SessionAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

SessionResponse
~~~~~~~~~~~~~~~

Response model for session operations.

.. autoclass:: honeyhive.api.session.SessionResponse
   :members:
   :undoc-members:
   :show-inheritance:

SessionStartResponse
~~~~~~~~~~~~~~~~~~~~

Response model for session start operations.

.. autoclass:: honeyhive.api.session.SessionStartResponse
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
   # Start a session
   session = client.session.start_session(
       project="your-project",
       session_name="user-interaction",
       metadata={"user_id": "123"}
   )
   
   # End the session
   client.session.end_session(
       session_id=session.session_id,
       status="completed"
   )

ToolsAPI
--------

API client for tool operations.

.. autoclass:: honeyhive.api.tools.ToolsAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Methods
~~~~~~~

create_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.tools.ToolsAPI.create_tool

list_tools
^^^^^^^^^^

.. automethod:: honeyhive.api.tools.ToolsAPI.list_tools

get_tool
^^^^^^^^

.. automethod:: honeyhive.api.tools.ToolsAPI.get_tool

update_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.tools.ToolsAPI.update_tool

delete_tool
^^^^^^^^^^^

.. automethod:: honeyhive.api.tools.ToolsAPI.delete_tool

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   from honeyhive.models import CreateToolRequest
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
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

EvaluationsAPI
--------------

API client for evaluation operations.

.. autoclass:: honeyhive.api.evaluations.EvaluationsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
   # Run evaluation
   result = client.evaluations.evaluate(
       project="your-project",
       inputs={"query": "What is AI?"},
       ground_truth="Artificial Intelligence is...",
       evaluators=["exact_match", "semantic_similarity"]
   )

EventsAPI
---------

API client for event operations.

.. autoclass:: honeyhive.api.events.EventsAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example
~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive as Client
   
   client = honeyhive.HoneyHive(api_key="your-api-key")
   
   # Send event
   client.events.send_event(
       project="your-project",
       event_type="llm_call",
       event_data={
           "model": "gpt-4",
           "input": "Hello",
           "output": "Hi there!",
           "latency": 250
       }
   )

See Also
--------

- :doc:`models-complete` - Request and response models
- :doc:`errors` - Error handling
- :doc:`tracer` - Tracer API




