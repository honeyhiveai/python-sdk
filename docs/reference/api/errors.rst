Error Handling Reference
========================

Complete reference for error classes and error handling utilities.

.. contents:: Table of Contents
   :local:
   :depth: 2

Error Classes
-------------

APIError
~~~~~~~~

Base error class for all API errors.

.. autoclass:: honeyhive.utils.error_handler.APIError
   :members:
   :undoc-members:
   :show-inheritance:

AuthenticationError
~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.AuthenticationError
   :members:
   :undoc-members:
   :show-inheritance:

ValidationError
~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.ValidationError
   :members:
   :undoc-members:
   :show-inheritance:

RateLimitError
~~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.RateLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Error Handler
-------------

ErrorHandler
~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.ErrorHandler
   :members:
   :undoc-members:
   :show-inheritance:

ErrorContext
~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.ErrorContext
   :members:
   :undoc-members:
   :show-inheritance:

ErrorResponse
~~~~~~~~~~~~~

.. autoclass:: honeyhive.utils.error_handler.ErrorResponse
   :members:
   :undoc-members:
   :show-inheritance:

Tracer Integration Errors
--------------------------

InitializationError
~~~~~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.integration.error_handling.InitializationError
   :members:
   :undoc-members:
   :show-inheritance:

ExportError
~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.integration.error_handling.ExportError
   :members:
   :undoc-members:
   :show-inheritance:

ErrorSeverity
~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.integration.error_handling.ErrorSeverity
   :members:
   :undoc-members:
   :show-inheritance:

ResilienceLevel
~~~~~~~~~~~~~~~

.. autoclass:: honeyhive.tracer.integration.error_handling.ResilienceLevel
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`client-apis` - API client reference
- :doc:`tracer` - Tracer API

