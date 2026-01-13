Data Models Reference
=====================

Complete reference for all data models, request/response classes, and enums.

.. contents:: Table of Contents
   :local:
   :depth: 2

Core Models
-----------

This section documents all data models used throughout the HoneyHive SDK.

Public Models
~~~~~~~~~~~~~

All request and response models are re-exported from ``honeyhive.models``.

.. automodule:: honeyhive.models
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: model_config, model_fields, model_computed_fields

.. note::
   **Key Models Included:**
   
   **Request Models:**
   
   - ``CreateConfigurationRequest`` - Create configurations
   - ``CreateDatasetRequest`` - Create datasets
   - ``CreateDatapointRequest`` - Create datapoints
   - ``CreateMetricRequest`` - Create metrics
   - ``CreateToolRequest`` - Create tools
   - ``PostEventRequest`` - Post events
   - ``PostSessionRequest`` - Create sessions
   - ``PostExperimentRunRequest`` - Create experiment runs
   - ``UpdateConfigurationRequest``, ``UpdateDatasetRequest``, ``UpdateDatapointRequest`` - Update operations
   
   **Response Models:**
   
   - ``CreateConfigurationResponse`` - Configuration creation response
   - ``CreateDatasetResponse`` - Dataset creation response
   - ``CreateDatapointResponse`` - Datapoint creation response
   - ``GetEventsResponse`` - Events retrieval
   - ``GetSessionResponse`` - Session retrieval
   - ``GetExperimentRunsResponse`` - Experiment runs retrieval
   - ``PostSessionStartResponse`` - Session start response
   
   **Query Parameters:**
   
   - ``GetEventsQuery`` - Query parameters for fetching events
   - ``GetDatasetsQuery`` - Query parameters for fetching datasets
   - ``GetDatapointsQuery`` - Query parameters for fetching datapoints
   
   **Enums:**
   
   - ``EventType`` - Event types (model, tool, chain, session, generic)

Configuration Models
--------------------

ServerURLMixin
~~~~~~~~~~~~~~

.. autoclass:: honeyhive.config.models.base.ServerURLMixin
   :members:
   :undoc-members:
   :show-inheritance:

Experiment Models
-----------------

ExperimentRunStatus
~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.experiments.models.ExperimentRunStatus
   :members:
   :undoc-members:
   :show-inheritance:

RunComparisonResult
~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.experiments.models.RunComparisonResult
   :members:
   :undoc-members:
   :show-inheritance:

ExperimentContext
~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.experiments.core.ExperimentContext
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`client-apis` - API client classes
- :doc:`/reference/experiments/experiments` - Experiments API
- :doc:`/how-to/evaluation/index` - Evaluation guides
