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

All request and response models generated from the API schema.

.. automodule:: honeyhive.models.generated
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: model_config, model_fields, model_computed_fields

.. note::
   **Key Models Included:**
   
   **Request Models:**
   - ``CreateRunRequest`` - Create experiment runs
   - ``CreateDatasetRequest`` - Create datasets
   - ``CreateProjectRequest`` - Create projects
   - ``CreateToolRequest`` - Create tools
   - ``UpdateRunRequest``, ``UpdateProjectRequest``, ``UpdateToolRequest`` - Update operations
   
   **Response Models:**
   - ``CreateRunResponse`` - Run creation response
   - ``Dataset`` - Dataset information
   - ``DeleteRunResponse`` - Deletion confirmation
   - ``GetRunResponse``, ``GetRunsResponse`` - Run retrieval
   - ``NewRun``, ``OldRun`` - Run comparison models
   
   **Supporting Models:**
   - ``SessionStartRequest``, ``SessionPropertiesBatch`` - Session management
   - ``ExperimentComparisonResponse``, ``ExperimentResultResponse`` - Experiment results
   - ``FunctionCallParams``, ``SelectedFunction``, ``Parameters`` - Configuration
   - ``Metric1``, ``Metric2``, ``MetricEdit`` - Metrics
   - ``Threshold``, ``Operator`` - Evaluation criteria
   
   **Enums:**
   - ``CallType`` - LLM call types (chat, completion)
   - ``EnvEnum`` - Environments (dev, staging, prod)
   - ``PipelineType`` - Pipeline types (event, session)
   - ``ToolType``, ``ReturnType`` - Tool and return type specifications
   - ``Type1``, ``Type3``, ``Type4``, ``Type6`` - Type categorizations
   - ``UUIDType`` - UUID handling

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
