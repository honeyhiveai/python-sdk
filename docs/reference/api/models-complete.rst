Data Models Reference
=====================

Complete reference for all data models, request/response classes, and enums.

.. contents:: Table of Contents
   :local:
   :depth: 2

Core Models
-----------

This section documents all data models used throughout the HoneyHive SDK.

Generated Models
~~~~~~~~~~~~~~~~

Request and response models re-exported from ``honeyhive.models``.

.. automodule:: honeyhive.models
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: model_config, model_fields, model_computed_fields

.. note::
   **Key Models Included:**
   
   **Request Models:**
   - ``PostExperimentRunRequest`` - Create experiment runs
   - ``CreateDatasetRequest`` - Create datasets
   - ``CreateProjectRequest`` - Create projects
   - ``CreateToolRequest`` - Create tools
   - ``PutExperimentRunRequest``, ``UpdateProjectRequest``, ``UpdateToolRequest`` - Update operations
   
   **Response Models:**
   - ``PostExperimentRunResponse`` - Run creation response
   - ``Dataset`` - Dataset information
   - ``DeleteExperimentRunResponse`` - Deletion confirmation
   - ``GetExperimentRunResponse``, ``GetRunsResponse`` - Run retrieval
   - ``ExperimentComparisonResponse`` - Run comparison payload
   
   **Supporting Models:**
   - ``SessionStartRequest``, ``SessionPropertiesBatch`` - Session management
   - ``ExperimentComparisonResponse``, ``ExperimentResultResponse`` - Experiment results
   - ``Configuration`` - Saved configuration payloads
   - ``Metric`` / ``CreateMetricRequest`` - Metrics
   - ``EventType`` - Tracing decorator event type enum
   
   **Enums:**
   - ``EventType`` - Event categories for traced operations

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
