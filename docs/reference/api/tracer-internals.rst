Tracer Internals Reference
==========================

Reference for internal tracer components and advanced functionality.

.. contents:: Table of Contents
   :local:
   :depth: 2

.. warning::
   This section documents internal APIs that are primarily for SDK maintainers and advanced use cases.
   For standard usage, see :doc:`tracer` instead.

Core Components
---------------

Base Classes
~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.core.base.HoneyHiveTracerBase
   :members:
   :undoc-members:
   :show-inheritance:

NoOpSpan
~~~~~~~~

.. autoclass:: honeyhive.tracer.core.base.NoOpSpan
   :members:
   :undoc-members:
   :show-inheritance:

Processing
----------

Environment Profile
~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.processing.otlp_profiles.EnvironmentProfile
   :members:
   :undoc-members:
   :show-inheritance:

OTLP Exporters
~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.processing.otlp_exporter.HoneyHiveOTLPExporter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: honeyhive.tracer.processing.otlp_exporter.OTLPJSONExporter
   :members:
   :undoc-members:
   :show-inheritance:

Infrastructure
--------------

Environment Detector
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.infra.environment.EnvironmentDetector
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`tracer` - Main tracer API
- :doc:`tracer-architecture` - Architecture overview
