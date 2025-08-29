Utilities
=========

This section covers the utility modules of the HoneyHive Python SDK.

Configuration
-------------

.. automodule:: honeyhive.utils.config
   :members:
   :undoc-members:
   :show-inheritance:

Logging
--------

.. automodule:: honeyhive.utils.logger
   :members:
   :undoc-members:
   :show-inheritance:

Caching
--------

.. automodule:: honeyhive.utils.cache
   :members:
   :undoc-members:
   :show-inheritance:

Connection Pooling
------------------

.. automodule:: honeyhive.utils.connection_pool
   :members:
   :undoc-members:
   :show-inheritance:

Baggage Management
------------------

.. automodule:: honeyhive.utils.baggage_dict
   :members:
   :undoc-members:
   :show-inheritance:

Dictionary Utilities
--------------------

.. automodule:: honeyhive.utils.dotdict
   :members:
   :undoc-members:
   :show-inheritance:

Retry Logic
-----------

.. automodule:: honeyhive.utils.retry
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.utils.config import config
   
   # Access configuration values
   api_key = config.api_key
   project = config.project
   debug_mode = config.debug_mode

Logging
~~~~~~~~

.. code-block:: python

   from honeyhive.utils.logger import get_logger
   
   logger = get_logger(__name__)
   logger.info("Application started")
   logger.error("An error occurred")

Caching
~~~~~~~~

.. code-block:: python

   from honeyhive.utils.cache import Cache
   
   cache = Cache()
   cache.set("key", "value", ttl=3600)
   value = cache.get("key")

Connection Pooling
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.utils.connection_pool import PooledHTTPClient
   
   client = PooledHTTPClient()
   response = client.request("GET", "https://api.example.com")
