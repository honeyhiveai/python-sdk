HoneyHive Client API Reference
==============================

.. note::
   **Complete API documentation for the HoneyHive client classes**
   
   Direct API clients for interacting with HoneyHive services without tracing middleware.

.. currentmodule:: honeyhive

The HoneyHive SDK provides several client classes for direct interaction with HoneyHive services. These clients are used internally by tracers but can also be used directly for advanced use cases.

HoneyHive Client
----------------

.. autoclass:: HoneyHive
   :members:
   :undoc-members:
   :show-inheritance:

The main client class for interacting with HoneyHive's core services.

**Key Features:**

- Direct API access to HoneyHive services
- Session and event management
- Project and configuration management
- Synchronous and asynchronous operations
- Built-in retry logic and error handling
- Rate limiting and throttling support

Initialization
~~~~~~~~~~~~~~

.. py:method:: __init__(api_key: Optional[str] = None, base_url: Optional[str] = None, cp_base_url: Optional[str] = None, server_url: Optional[str] = None, timeout: Optional[float] = None, rate_limit_calls: Optional[int] = None, rate_limit_window: Optional[float] = None, max_connections: Optional[int] = None, max_keepalive: Optional[int] = None, test_mode: bool = False, verbose: bool = False, tracer_instance: Optional[Any] = None, **kwargs)

   Initialize a HoneyHive client instance.

   **Parameters:**

   :param api_key: HoneyHive API key. If not provided, reads from ``HH_API_KEY`` environment variable.
   :type api_key: Optional[str]

   :param base_url: Base URL for the HoneyHive API. Defaults to ``"https://api.honeyhive.ai"``.
   :type base_url: Optional[str]

   :param cp_base_url: Base URL for the HoneyHive control-plane API. Used for project and configuration endpoints when separate from the data-plane.
   :type cp_base_url: Optional[str]

   :param server_url: Legacy alias for ``base_url``. Accepted for backwards compatibility.
   :type server_url: Optional[str]

   :param timeout: Request timeout in seconds. Accepted for backwards compatibility; not actively enforced by all transports.
   :type timeout: Optional[float]

   :param rate_limit_calls: Maximum API calls allowed per ``rate_limit_window`` seconds.
   :type rate_limit_calls: Optional[int]

   :param rate_limit_window: Window duration (seconds) for the rate limiter.
   :type rate_limit_window: Optional[float]

   :param max_connections: Maximum size of the HTTP connection pool.
   :type max_connections: Optional[int]

   :param max_keepalive: Maximum number of keep-alive connections in the pool.
   :type max_keepalive: Optional[int]

   :param test_mode: Enable test mode (requests are validated but not sent to the server). Default: ``False``
   :type test_mode: bool

   :param verbose: Enable verbose logging of requests and responses. Default: ``False``
   :type verbose: bool

   :param tracer_instance: Optional tracer instance to associate with this client for correlated tracing.
   :type tracer_instance: Optional[Any]

   **Example:**

   .. code-block:: python

      from honeyhive import HoneyHive

      # Basic initialization (api_key falls back to HH_API_KEY env var)
      client = HoneyHive(api_key="hh_your_api_key_here")

      # With custom configuration
      client = HoneyHive(
          api_key="hh_your_api_key_here",
          base_url="https://api.honeyhive.ai",
          rate_limit_calls=100,
          rate_limit_window=60.0,   # 100 calls per minute
          max_connections=50,
          max_keepalive=10,
      )

      # Test mode for development
      client = HoneyHive(
          api_key="hh_test_key",
          test_mode=True            # Or set HH_TEST_MODE=true environment variable
      )

Session Management
~~~~~~~~~~~~~~~~~~

Sessions are accessed via ``client.sessions``.

client.sessions.start()
^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.sessions.start(data: dict) -> StartSessionResponse

   Start (create) a new session for grouping related events.

   :param data: Session creation payload. Common keys:

      - ``session_name`` (*str*) — Human-readable name for the session.
      - ``project`` (*str*) — Project this session belongs to.
      - ``source`` (*str*) — Source environment (e.g. ``"production"``, ``"staging"``).
      - ``inputs`` (*dict*) — Initial inputs for the session.
      - ``user_properties`` (*dict*) — User-level metadata.

   :type data: dict
   :returns: A ``StartSessionResponse`` object. The session ID is at ``response.session_id``.

   .. code-block:: python

      from honeyhive import HoneyHive

      client = HoneyHive(api_key="hh_...")

      response = client.sessions.start({
          "session_name": "user-onboarding-flow",
          "project": "my-project",
          "source": "production",
          "inputs": {"user_id": "u123"},
      })

      session_id = response.session_id
      print(f"Created session: {session_id}")

   .. note::

      Backwards-compatibility aliases ``client.sessions.create_session()`` and
      ``client.sessions.start_session()`` also exist and behave identically.

client.sessions.get()
^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.sessions.get(session_id: str) -> Event

   Retrieve a session (returned as an ``Event`` object) by its ID.

   :param session_id: Unique session identifier.
   :type session_id: str
   :returns: An ``Event`` object containing session details.

   .. code-block:: python

      event = client.sessions.get("session_abc123")

      print(f"Session name: {event.event_name}")
      print(f"Inputs: {event.inputs}")

   .. note::

      A backwards-compatibility alias ``client.sessions.get_session()`` is also available.

Event Management
~~~~~~~~~~~~~~~~

Events are accessed via ``client.events``.

client.events.create()
^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.events.create(request: PostEventRequest) -> None

   Create a new event within a session. Accepts a ``PostEventRequest`` model object.

   .. code-block:: python

      from honeyhive import HoneyHive
      from honeyhive.models import PostEventRequest

      client = HoneyHive(api_key="hh_...")

      client.events.create(PostEventRequest(
          project="my-project",
          event_name="openai_completion",
          event_type="model",
          session_id="session_abc123",
          inputs={
              "model": "gpt-4",
              "messages": [{"role": "user", "content": "Hello!"}],
          },
          outputs={
              "response": "Hello! How can I help you today?",
          },
          metadata={"duration_ms": 1500},
      ))

client.events.update()
^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.events.update(data: dict) -> None

   Update an existing event (e.g. to add feedback or outputs after the fact).

   :param data: Update payload. Common keys: ``event_id``, ``feedback``, ``outputs``, ``metadata``, ``metrics``.
   :type data: dict

   .. code-block:: python

      client.events.update({
          "event_id": "event_xyz789",
          "feedback": {"rating": 5, "comment": "Great response"},
          "metadata": {"reviewed": True},
      })

client.events.get_by_session_id()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.events.get_by_session_id(session_id: str) -> GetEventsResponse

   Retrieve all events belonging to a session.

   :param session_id: Unique session identifier.
   :type session_id: str
   :returns: A ``GetEventsResponse`` containing a list of events.

   .. code-block:: python

      response = client.events.get_by_session_id("session_abc123")

      for event in response.events:
          print(f"Event: {event.event_name} ({event.event_type})")

client.events.list()
^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.events.list(query: dict) -> GetEventsResponse

   List events matching a query object.

   :param query: Query parameters (project name, filters, date ranges, etc.).
   :type query: dict

   .. code-block:: python

      response = client.events.list({
          "project": "my-project",
          "filters": [{"field": "event_type", "value": "model", "operator": "is"}],
      })

      for event in response.events:
          print(event.event_name)

client.events.create_batch()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.events.create_batch(data: dict) -> None

   Create multiple events in a single API call.

   :param data: Batch payload with an ``"events"`` list.
   :type data: dict

   .. code-block:: python

      events_batch = [
          {
              "project": "my-project",
              "session_id": session_id,
              "event_type": "chain",
              "event_name": f"process_item_{i}",
              "inputs": {"item_id": i},
              "outputs": {"result": f"processed_{i}"},
          }
          for i in range(100)
      ]

      client.events.create_batch({"events": events_batch})

Project Management
~~~~~~~~~~~~~~~~~~

Projects are accessed via ``client.projects``.

client.projects.list()
^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.projects.list() -> GetProjectsResponse

   List all accessible projects.

   :returns: A ``GetProjectsResponse`` containing a list of projects.

   .. code-block:: python

      response = client.projects.list()

      for project in response.projects:
          print(f"Project: {project.name}")

client.projects.create()
^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.projects.create(data: dict) -> CreateProjectResponse

   Create a new project.

   :param data: Project creation payload. Common keys: ``"name"``, ``"description"``.
   :type data: dict

   .. code-block:: python

      response = client.projects.create({
          "name": "customer-support-bot",
          "description": "AI-powered customer support chatbot",
      })

client.projects.update()
^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.projects.update(data: dict) -> None

   Update an existing project's metadata.

   :param data: Update payload including ``"name"`` (current name) and fields to update.
   :type data: dict

   .. code-block:: python

      client.projects.update({
          "name": "customer-support-bot",
          "description": "Updated description",
      })

client.projects.delete()
^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.projects.delete(name: str) -> None

   Delete a project by name.

   :param name: Name of the project to delete.
   :type name: str

   .. code-block:: python

      client.projects.delete("customer-support-bot")

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

Configurations are accessed via ``client.configurations``.

client.configurations.list()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.configurations.list(project: str) -> GetConfigurationsResponse

   List all configurations for a project.

   :param project: Project name to filter by.
   :type project: str
   :returns: A ``GetConfigurationsResponse`` containing a list of configurations.

   .. code-block:: python

      response = client.configurations.list(project="my-project")

      for config in response.configurations:
          print(f"Config: {config.name} (active: {config.is_active})")

client.configurations.create()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.configurations.create(request: CreateConfigurationRequest) -> None

   Create a new configuration for a project.

   :param request: A ``CreateConfigurationRequest`` model object.

   .. code-block:: python

      from honeyhive.models import CreateConfigurationRequest

      client.configurations.create(CreateConfigurationRequest(
          project="my-project",
          name="v1-config",
          provider="openai",
          parameters={"model": "gpt-4", "temperature": 0.7},
      ))

client.configurations.update()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.configurations.update(request: UpdateConfigurationRequest) -> None

   Update an existing configuration.

   :param request: An ``UpdateConfigurationRequest`` model object containing the configuration ID and updated fields.

   .. code-block:: python

      from honeyhive.models import UpdateConfigurationRequest

      client.configurations.update(UpdateConfigurationRequest(
          configuration_id="cfg_abc123",
          parameters={"model": "gpt-4-turbo", "temperature": 0.5},
      ))

client.configurations.delete()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: client.configurations.delete(id: str) -> None

   Delete a configuration by ID.

   :param id: Configuration ID to delete.
   :type id: str

   .. code-block:: python

      client.configurations.delete("cfg_abc123")

Async Operations
----------------

There is no separate async client class. Every method on every API namespace
exposes an async variant via the ``_async`` suffix. Use these from within
``async`` functions or event loops.

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHive

   client = HoneyHive(api_key="hh_...")

   async def main():
       # Async session start
       response = await client.sessions.start_async({
           "session_name": "async-session",
           "project": "my-project",
           "source": "production",
       })
       session_id = response.session_id

       # Async event creation
       await client.events.create_async(PostEventRequest(
           project="my-project",
           session_id=session_id,
           event_type="model",
           event_name="async_completion",
           inputs={"prompt": "Hello async world!"},
           outputs={"response": "Hello back!"},
       ))

   asyncio.run(main())

The ``_async`` suffix is available on all methods across all namespaces:

.. list-table::
   :header-rows: 1
   :widths: 40 40

   * - Sync method
     - Async equivalent
   * - ``client.sessions.start(data)``
     - ``await client.sessions.start_async(data)``
   * - ``client.sessions.get(session_id)``
     - ``await client.sessions.get_async(session_id)``
   * - ``client.events.create(request)``
     - ``await client.events.create_async(request)``
   * - ``client.events.update(data)``
     - ``await client.events.update_async(data)``
   * - ``client.events.get_by_session_id(id)``
     - ``await client.events.get_by_session_id_async(id)``
   * - ``client.events.list(query)``
     - ``await client.events.list_async(query)``
   * - ``client.events.create_batch(data)``
     - ``await client.events.create_batch_async(data)``
   * - ``client.projects.list()``
     - ``await client.projects.list_async()``
   * - ``client.projects.create(data)``
     - ``await client.projects.create_async(data)``
   * - ``client.configurations.list(project)``
     - ``await client.configurations.list_async(project)``
   * - ``client.configurations.create(request)``
     - ``await client.configurations.create_async(request)``

Concurrent Async Example
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHive
   from honeyhive.models import PostEventRequest

   client = HoneyHive(api_key="hh_...")

   async def process_batch():
       response = await client.sessions.start_async({
           "session_name": "batch-session",
           "project": "my-project",
       })
       session_id = response.session_id

       # Fire off multiple event creations concurrently
       tasks = [
           client.events.create_async(PostEventRequest(
               project="my-project",
               session_id=session_id,
               event_type="tool",
               event_name=f"task_{i}",
               inputs={"task_id": i},
               outputs={"result": f"completed_{i}"},
           ))
           for i in range(10)
       ]
       await asyncio.gather(*tasks)
       print("Created 10 events concurrently")

   asyncio.run(process_batch())

Batch Operations
----------------

For high-throughput scenarios, use ``client.events.create_batch()``:

Batch Event Creation
~~~~~~~~~~~~~~~~~~~~

.. py:method:: client.events.create_batch(data: dict) -> None

   Create multiple events in a single API call.

   :param data: Dict with an ``"events"`` key containing a list of event dicts.
   :type data: dict

   .. code-block:: python

      from honeyhive import HoneyHive

      client = HoneyHive(api_key="hh_key")

      # Prepare batch of events
      events_batch = [
          {
              "project": "my-project",
              "session_id": session_id,
              "event_type": "chain",
              "event_name": f"process_item_{i}",
              "inputs": {"item_id": i, "data": f"item_data_{i}"},
              "outputs": {"result": f"processed_{i}"},
              "metadata": {"batch_id": "batch_001", "item_index": i},
          }
          for i in range(100)
      ]

      # Create all events in one API call
      client.events.create_batch({"events": events_batch})

Error Handling
--------------

Both clients provide comprehensive error handling:

Exception Types
~~~~~~~~~~~~~~~

.. py:exception:: HoneyHiveError

   Base exception for all HoneyHive client errors.

.. py:exception:: APIError

   API-related errors (4xx, 5xx HTTP responses). Imported from ``honeyhive.utils``.

   **Attributes:**

   - ``status_code``: HTTP status code
   - ``message``: Error message

.. py:exception:: HoneyHiveConnectionError

   Connection-related errors (network failures, timeouts). Imported from ``honeyhive.utils``.

.. py:exception:: AuthenticationError

   Authentication failures (invalid or missing API key). Imported from ``honeyhive.utils``.

.. py:exception:: RateLimitError

   Rate limiting errors (HTTP 429). Imported from ``honeyhive.utils``.

   **Attributes:**

   - ``retry_after``: Recommended retry delay in seconds (may be ``None``)

Error Handling Examples
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.utils import HoneyHiveError, APIError, RateLimitError, HoneyHiveConnectionError
   import time

   client = HoneyHive(api_key="hh_your_key")  # Or set HH_API_KEY environment variable

   def robust_api_call():
       max_retries = 3
       for attempt in range(max_retries):
           try:
               response = client.sessions.start({
                   "session_name": "my-session",
                   "project": "my-project",
               })
               return response.session_id

           except RateLimitError as e:
               if attempt < max_retries - 1:
                   wait_time = e.retry_after or (2 ** attempt)
                   print(f"Rate limited, waiting {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise

           except APIError as e:
               if e.status_code >= 500 and attempt < max_retries - 1:
                   # Retry on server errors
                   wait_time = 2 ** attempt
                   print(f"Server error {e.status_code}, retrying in {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise

           except HoneyHiveConnectionError as e:
               if attempt < max_retries - 1:
                   wait_time = 2 ** attempt
                   print(f"Connection error, retrying in {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise

Client Configuration
--------------------

Advanced Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive

   # Production configuration
   client = HoneyHive(
       api_key="hh_prod_key",               # Or set HH_API_KEY environment variable
       base_url="https://api.honeyhive.ai", # Or set HH_API_URL environment variable

       # Rate limiting
       rate_limit_calls=100,
       rate_limit_window=60.0,              # 100 calls per minute

       # Connection pooling
       max_connections=50,
       max_keepalive=10,

       # Verbose logging
       verbose=True,
   )

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from honeyhive import HoneyHive

   def create_client_from_env() -> HoneyHive:
       """Create client with environment-based configuration."""
       return HoneyHive(
           api_key=os.getenv("HH_API_KEY"),
           base_url=os.getenv("HH_API_URL", "https://api.honeyhive.ai"),
           test_mode=os.getenv("HH_TEST_MODE", "false").lower() == "true",
       )

   # Usage
   client = create_client_from_env()

Integration Patterns
--------------------

Context Manager Usage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import PostEventRequest

   # HoneyHive supports use as a context manager for resource cleanup
   with HoneyHive(api_key="hh_key") as client:  # Or set HH_API_KEY environment variable
       response = client.sessions.start({
           "session_name": "my-session",
           "project": "my-project",
           "source": "production",
       })
       session_id = response.session_id

       # Multiple operations
       for i in range(10):
           client.events.create(PostEventRequest(
               project="my-project",
               session_id=session_id,
               event_type="tool",
               event_name=f"iteration_{i}",
               inputs={"iteration": i},
               outputs={"result": i * 2},
           ))
   # Client automatically closed and cleaned up

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive

   class MyService:
       def __init__(self, honeyhive_client: HoneyHive):
           self.client = honeyhive_client

       def process_user_request(self, user_id: str, request_data: dict) -> str:
           # Create session for this request
           response = self.client.sessions.start({
               "session_name": "process-request",
               "project": "my-project",
               "source": "development",
               "inputs": {"user_id": user_id},
           })
           return response.session_id

   # Dependency injection
   client = HoneyHive(api_key="hh_key")  # Or set HH_API_KEY environment variable
   service = MyService(honeyhive_client=client)

Factory Pattern
~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from honeyhive import HoneyHive

   class HoneyHiveClientFactory:
       """Factory for creating configured HoneyHive clients."""

       @staticmethod
       def create_production_client(api_key: str) -> HoneyHive:
           return HoneyHive(
               api_key=api_key,
               rate_limit_calls=200,
               rate_limit_window=60.0,  # 200 calls per minute
               max_connections=50,
               max_keepalive=10,
           )

       @staticmethod
       def create_development_client(api_key: str) -> HoneyHive:
           return HoneyHive(
               api_key=api_key,
               verbose=True,
           )

       @staticmethod
       def create_testing_client() -> HoneyHive:
           return HoneyHive(
               api_key="test_key",
               test_mode=True,  # Or set HH_TEST_MODE=true environment variable
           )

   # Usage
   env = os.getenv("ENVIRONMENT", "development")
   if env == "production":
       client = HoneyHiveClientFactory.create_production_client(
           api_key=os.getenv("HH_API_KEY")
       )
   elif env == "development":
       client = HoneyHiveClientFactory.create_development_client(
           api_key=os.getenv("HH_DEV_API_KEY")
       )
   else:
       client = HoneyHiveClientFactory.create_testing_client()

Performance Optimization
------------------------

Connection Pooling
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive

   # Configure connection pooling for high-throughput applications
   client = HoneyHive(
       api_key="hh_key",        # Or set HH_API_KEY environment variable
       max_connections=100,     # Total connection pool size
       max_keepalive=20,        # Persistent keep-alive connections
   )

Request Batching
~~~~~~~~~~~~~~~~

Use ``client.events.create_batch()`` to send many events in a single API call,
or ``create_batch_async()`` from async code:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHive

   client = HoneyHive(api_key="hh_key")

   async def batch_events_efficiently():
       response = await client.sessions.start_async({
           "session_name": "batch-session",
           "project": "my-project",
           "source": "production",
       })
       session_id = response.session_id

       # Create events in batches for better performance
       batch_size = 50
       for batch_start in range(0, 1000, batch_size):
           batch_events = [
               {
                   "project": "my-project",
                   "session_id": session_id,
                   "event_type": "chain",
                   "event_name": f"item_{i}",
                   "inputs": {"item_id": i},
                   "outputs": {"processed": True},
               }
               for i in range(batch_start, min(batch_start + batch_size, 1000))
           ]

           await client.events.create_batch_async({"events": batch_events})
           print(f"Processed batch {batch_start // batch_size + 1}")

   asyncio.run(batch_events_efficiently())

See Also
--------

- :doc:`tracer` - HoneyHiveTracer API reference
- :doc:`decorators` - Decorator-based APIs
- :doc:`../../tutorials/01-setup-first-tracer` - Getting started tutorial
- :doc:`../../how-to/index` - Client troubleshooting (see Troubleshooting section)
- :doc:`../../explanation/architecture/overview` - Architecture overview
