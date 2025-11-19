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

.. py:method:: __init__(api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3, test_mode: bool = False, **kwargs)

   Initialize a HoneyHive client instance.
   
   **Parameters:**
   
   :param api_key: HoneyHive API key. If not provided, reads from ``HH_API_KEY`` environment variable.
   :type api_key: Optional[str]
   
   :param base_url: Base URL for HoneyHive API. Defaults to "https://api.honeyhive.ai".
   :type base_url: Optional[str]
   
   :param timeout: Request timeout in seconds. Default: 30.0
   :type timeout: float
   
   :param max_retries: Maximum number of retry attempts for failed requests. Default: 3
   :type max_retries: int
   
   :param test_mode: Enable test mode (requests are validated but not processed). Default: False
   :type test_mode: bool
   
   :param kwargs: Additional configuration options
   :type kwargs: Any
   
   **Example:**
   
   .. code-block:: python
   
      from honeyhive import HoneyHive
      from honeyhive.models import EventType
      
      # Basic initialization
      client = HoneyHive(api_key="hh_your_api_key_here")  # Or set HH_API_KEY environment variable
      
      # With custom configuration
      client = HoneyHive(
          api_key="hh_your_api_key_here",  # Or set HH_API_KEY environment variable
          base_url="https://api.honeyhive.ai",  # Or set HH_API_URL environment variable
          timeout=60.0,
          max_retries=5
      )
      
      # Test mode for development
      client = HoneyHive(
          api_key="hh_test_key",           # Or set HH_API_KEY environment variable
          test_mode=True                   # Or set HH_TEST_MODE=true environment variable
      )

Session Management
~~~~~~~~~~~~~~~~~~

create_session()
^^^^^^^^^^^^^^^^

.. py:method:: create_session(project: str, source: Optional[str] = None, session_name: Optional[str] = None, **kwargs) -> dict

   Create a new session for grouping related events.
   
   **Parameters:**
   
   :param project: Project name for the session
   :type project: str
   
   :param source: Source identifier (e.g., "production", "staging")
   :type source: Optional[str]
   
   :param session_name: Custom session name
   :type session_name: Optional[str]
   
   :param kwargs: Additional session metadata
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: dict
   :returns: Session information including session_id
   
   **Example:**
   
   .. code-block:: python
   
      # Create a basic session
      session = client.create_session(
          source="development",
          session_name="user-onboarding-flow"
      )
      
      print(f"Created session: {session['session_id']}")
      
      # Create session with metadata
      session = client.create_session(
          source="development",
          user_id="user_123",
          conversation_type="customer_support",
          priority="high"
      )

get_session()
^^^^^^^^^^^^^

.. py:method:: get_session(session_id: str) -> dict

   Retrieve session information by ID.
   
   **Parameters:**
   
   :param session_id: Unique session identifier
   :type session_id: str
   
   **Returns:**
   
   :rtype: dict
   :returns: Session details and metadata
   
   **Example:**
   
   .. code-block:: python
   
      session_info = client.get_session("session_abc123")
      
      print(f"Session project: {session_info['project']}")
      print(f"Session created: {session_info['created_at']}")
      print(f"Event count: {session_info['event_count']}")

list_sessions()
^^^^^^^^^^^^^^^

.. py:method:: list_sessions(project: Optional[str] = None, source: Optional[str] = None, limit: int = 100, offset: int = 0, **filters) -> dict

   List sessions with optional filtering.
   
   **Parameters:**
   
   :param project: Filter by project name
   :type project: Optional[str]
   
   :param source: Filter by source identifier
   :type source: Optional[str]
   
   :param limit: Maximum number of sessions to return
   :type limit: int
   
   :param offset: Number of sessions to skip (for pagination)
   :type offset: int
   
   :param filters: Additional filter criteria
   :type filters: Any
   
   **Returns:**
   
   :rtype: dict
   :returns: List of sessions and pagination info
   
   **Example:**
   
   .. code-block:: python
   
      # List all sessions for a project
      sessions = client.list_sessions(limit=50)
      
      for session in sessions['sessions']:
          print(f"Session {session['session_id']}: {session['session_name']}")
      
      # List with filters
      recent_sessions = client.list_sessions(
          source="development",
          created_after="2024-01-01T00:00:00Z",
          limit=20
      )

Event Management
~~~~~~~~~~~~~~~~

create_event()
^^^^^^^^^^^^^^

.. py:method:: create_event(session_id: str, event_type: str, event_name: str, inputs: Optional[dict] = None, outputs: Optional[dict] = None, metadata: Optional[dict] = None, **kwargs) -> dict

   Create a new event within a session.
   
   **Parameters:**
   
   :param session_id: Session ID to associate the event with
   :type session_id: str
   
   :param event_type: Type of event. Must be one of: ``"model"``, ``"tool"``, or ``"chain"``
   :type event_type: str
   
   :param event_name: Descriptive name for the event
   :type event_name: str
   
   :param inputs: Input data for the event
   :type inputs: Optional[dict]
   
   :param outputs: Output data from the event
   :type outputs: Optional[dict]
   
   :param metadata: Additional event metadata
   :type metadata: Optional[dict]
   
   :param kwargs: Additional event attributes
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: dict
   :returns: Created event information
   
   **Example:**
   
   .. code-block:: python
   
      # Create an LLM call event
      event = client.create_event(
          session_id="session_abc123",
          event_type=EventType.model,
          event_name="openai_completion",
          inputs={
              "model": "gpt-4",
              "messages": [{"role": "user", "content": "Hello!"}],
              "temperature": 0.7
          },
          outputs={
              "response": "Hello! How can I help you today?",
              "usage": {
                  "prompt_tokens": 10,
                  "completion_tokens": 12,
                  "total_tokens": 22
              }
          },
          metadata={
              "duration_ms": 1500,
              "model_version": "gpt-4-0613"
          }
      )
      
      print(f"Created event: {event['event_id']}")

get_event()
^^^^^^^^^^^

.. py:method:: get_event(event_id: str) -> dict

   Retrieve event information by ID.
   
   **Parameters:**
   
   :param event_id: Unique event identifier
   :type event_id: str
   
   **Returns:**
   
   :rtype: dict
   :returns: Event details and data
   
   **Example:**
   
   .. code-block:: python
   
      event = client.get_event("event_xyz789")
      
      print(f"Event type: {event['event_type']}")
      print(f"Event name: {event['event_name']}")
      print(f"Duration: {event['metadata']['duration_ms']}ms")

list_events()
^^^^^^^^^^^^^

.. py:method:: list_events(session_id: Optional[str] = None, project: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100, offset: int = 0, **filters) -> dict

   List events with optional filtering.
   
   **Parameters:**
   
   :param session_id: Filter by session ID
   :type session_id: Optional[str]
   
   :param project: Filter by project name
   :type project: Optional[str]
   
   :param event_type: Filter by event type
   :type event_type: Optional[str]
   
   :param limit: Maximum number of events to return
   :type limit: int
   
   :param offset: Number of events to skip (for pagination)
   :type offset: int
   
   :param filters: Additional filter criteria
   :type filters: Any
   
   **Returns:**
   
   :rtype: dict
   :returns: List of events and pagination info
   
   **Example:**
   
   .. code-block:: python
   
      # List events for a session
      events = client.list_events(session_id="session_abc123")
      
      for event in events['events']:
          print(f"Event: {event['event_name']} ({event['event_type']})")
      
      # List LLM call events across all sessions
      llm_events = client.list_events(
          event_type=EventType.model,
          limit=50
      )

Project Management
~~~~~~~~~~~~~~~~~~

create_project()
^^^^^^^^^^^^^^^^

.. py:method:: create_project(name: str, description: Optional[str] = None, **kwargs) -> dict

   Create a new project.
   
   **Parameters:**
   
   :param name: Project name
   :type name: str
   
   :param description: Project description
   :type description: Optional[str]
   
   :param kwargs: Additional project configuration
   :type kwargs: Any
   
   **Returns:**
   
   :rtype: dict
   :returns: Created project information
   
   **Example:**
   
   .. code-block:: python
   
      project = client.create_project(
          name="customer-support-bot",
          description="AI-powered customer support chatbot",
          team="engineering",
          environment="production"
      )

get_project()
^^^^^^^^^^^^^

.. py:method:: get_project(project_name: str) -> dict

   Retrieve project information.
   
   **Parameters:**
   
   :param project_name: Name of the project
   :type project_name: str
   
   **Returns:**
   
   :rtype: dict
   :returns: Project details and configuration
   
   **Example:**
   
   .. code-block:: python
   
      project_info = client.get_project("customer-support-bot")
      
      print(f"Project: {project_info['name']}")
      print(f"Created: {project_info['created_at']}")
      print(f"Total events: {project_info['event_count']}")

list_projects()
^^^^^^^^^^^^^^^

.. py:method:: list_projects(limit: int = 100, offset: int = 0) -> dict

   List all accessible projects.
   
   **Parameters:**
   
   :param limit: Maximum number of projects to return
   :type limit: int
   
   :param offset: Number of projects to skip (for pagination)
   :type offset: int
   
   **Returns:**
   
   :rtype: dict
   :returns: List of projects and pagination info
   
   **Example:**
   
   .. code-block:: python
   
      projects = client.list_projects()
      
      for project in projects['projects']:
          print(f"Project: {project['name']} - {project['description']}")

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

get_configuration()
^^^^^^^^^^^^^^^^^^^

.. py:method:: get_configuration(project: str) -> dict

   Get project configuration settings.
   
   **Parameters:**
   
   :param project: Project name
   :type project: str
   
   **Returns:**
   
   :rtype: dict
   :returns: Project configuration
   
   **Example:**
   
   .. code-block:: python
   
      config = client.get_configuration("my-app")
      
      print(f"Sampling rate: {config['sampling_rate']}")
      print(f"Retention days: {config['retention_days']}")

update_configuration()
^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: update_configuration(project: str, configuration: dict) -> dict

   Update project configuration settings.
   
   **Parameters:**
   
   :param project: Project name
   :type project: str
   
   :param configuration: Configuration updates
   :type configuration: dict
   
   **Returns:**
   
   :rtype: dict
   :returns: Updated configuration
   
   **Example:**
   
   .. code-block:: python
   
      updated_config = client.update_configuration(
          configuration={
              "sampling_rate": 0.1,  # 10% sampling
              "retention_days": 30,
              "alert_thresholds": {
                  "error_rate": 0.05,
                  "latency_p95": 5000
              }
          }
      )

Async Client
------------

**AsyncHoneyHive**

Asynchronous version of the HoneyHive client for non-blocking operations.

**Key Features:**

- Non-blocking API calls
- Context manager support 
- Concurrent request handling
- Same interface as sync client

**Example Usage:**

.. code-block:: python

   import asyncio
   from honeyhive import AsyncHoneyHive

   async def async_example():
       async with AsyncHoneyHive(api_key="your-key") as client:  # Or set HH_API_KEY environment variable
           session = await client.create_session(
               session_name="async-session"
           )
           
           event = await client.create_event(
               session_id=session['session_id'],
               event_type=EventType.model,
               event_name="async_completion"
           )

Asynchronous version of the HoneyHive client for use in async applications.

**Key Features:**

- All methods are async/await compatible
- Built-in connection pooling
- Concurrent request handling
- Async context manager support

Initialization
~~~~~~~~~~~~~~

.. py:method:: __init__(api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3, max_connections: int = 100, test_mode: bool = False, **kwargs)
   :no-index:

   Initialize an async HoneyHive client.
   
   **Parameters:**
   
   :param api_key: HoneyHive API key
   :type api_key: Optional[str]
   
   :param base_url: Base URL for HoneyHive API
   :type base_url: Optional[str]
   
   :param timeout: Request timeout in seconds
   :type timeout: float
   
   :param max_retries: Maximum retry attempts
   :type max_retries: int
   
   :param max_connections: Maximum concurrent connections
   :type max_connections: int
   
   :param test_mode: Enable test mode
   :type test_mode: bool
   
   :param kwargs: Additional configuration
   :type kwargs: Any
   
   **Example:**
   
   .. code-block:: python
   
      import asyncio
      from honeyhive import AsyncHoneyHive
      
      async def main():
          async with AsyncHoneyHive(api_key="hh_your_key") as client:  # Or set HH_API_KEY environment variable
              # Use async client
              session = await client.create_session(
                  source="production"
              )
              
              event = await client.create_event(
                  session_id=session['session_id'],
                  event_type=EventType.model,
                  event_name="async_completion",
                  inputs={"prompt": "Hello async world!"},
                  outputs={"response": "Hello back!"}
              )
      
      asyncio.run(main())

Async Session Management
~~~~~~~~~~~~~~~~~~~~~~~~

All session management methods have async equivalents:

.. code-block:: python

   async def manage_sessions():
       async with AsyncHoneyHive(api_key="hh_key") as client:  # Or set HH_API_KEY environment variable
           # Create session
           session = await client.create_session(
               source="production"
           )
           
           # Get session info
           session_info = await client.get_session(session['session_id'])
           
           # List sessions
           sessions = await client.list_sessions(
               limit=10
           )

Async Event Management
~~~~~~~~~~~~~~~~~~~~~~

All event management methods have async equivalents:

.. code-block:: python

   async def manage_events():
       async with AsyncHoneyHive(api_key="hh_key") as client:  # Or set HH_API_KEY environment variable
           session = await client.create_session(
               source="production"
           )
           
           # Create multiple events concurrently
           tasks = []
           for i in range(10):
               task = client.create_event(
                   session_id=session['session_id'],
                   event_type=EventType.tool,
                   event_name=f"task_{i}",
                   inputs={"task_id": i},
                   outputs={"result": f"completed_{i}"}
               )
               tasks.append(task)
           
           # Wait for all events to be created
           events = await asyncio.gather(*tasks)
           print(f"Created {len(events)} events concurrently")

Batch Operations
----------------

For high-throughput scenarios, both clients support batch operations:

Batch Event Creation
~~~~~~~~~~~~~~~~~~~~

.. py:method:: create_events_batch(events: List[dict]) -> dict

   Create multiple events in a single API call.
   
   **Parameters:**
   
   :param events: List of event dictionaries
   :type events: List[dict]
   
   **Returns:**
   
   :rtype: dict
   :returns: Batch creation results
   
   **Example:**
   
   .. code-block:: python
   
      # Prepare batch of events
      events_batch = []
      for i in range(100):
          events_batch.append({
              "session_id": session_id,
              "event_type": "chain",
              "event_name": f"process_item_{i}",
              "inputs": {"item_id": i, "data": f"item_data_{i}"},
              "outputs": {"result": f"processed_{i}"},
              "metadata": {"batch_id": "batch_001", "item_index": i}
          })
      
      # Create all events in one API call
      result = client.create_events_batch(events_batch)
      
      print(f"Created {result['created_count']} events")
      print(f"Failed: {result['failed_count']} events")

Error Handling
--------------

Both clients provide comprehensive error handling:

Exception Types
~~~~~~~~~~~~~~~

.. py:exception:: HoneyHiveError

   Base exception for all HoneyHive client errors.

.. py:exception:: HoneyHiveAPIError

   API-related errors (4xx, 5xx HTTP responses).
   
   **Attributes:**
   
   - ``status_code``: HTTP status code
   - ``response``: Raw API response
   - ``message``: Error message

.. py:exception:: HoneyHiveConnectionError

   Connection-related errors (network, timeout).

.. py:exception:: HoneyHiveAuthenticationError

   Authentication failures (invalid API key).

.. py:exception:: HoneyHiveRateLimitError

   Rate limiting errors.
   
   **Attributes:**
   
   - ``retry_after``: Recommended retry delay in seconds

Error Handling Examples
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive, HoneyHiveAPIError, HoneyHiveRateLimitError
   import time
   
   client = HoneyHive(api_key="hh_your_key")  # Or set HH_API_KEY environment variable
   
   def robust_api_call():
       max_retries = 3
       for attempt in range(max_retries):
           try:
               session = client.create_session(
                   source="production"
               )
               return session
               
           except HoneyHiveRateLimitError as e:
               if attempt < max_retries - 1:
                   wait_time = e.retry_after or (2 ** attempt)
                   print(f"Rate limited, waiting {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise
                   
           except HoneyHiveAPIError as e:
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
       timeout=30.0,
       max_retries=3,
       
       # Custom headers
       headers={
           "User-Agent": "MyApp/1.0",
           "X-Custom-Header": "custom-value"
       },
       
       # SSL configuration
       verify_ssl=True,
       ssl_cert_path="/path/to/cert.pem",
       
       # Proxy configuration
       proxy_url="http://proxy.company.com:8080",
       
       # Rate limiting
       rate_limit_calls=100,
       rate_limit_period=60,  # 100 calls per minute
       
       # Connection pooling
       max_connections=50,
       max_keepalive_connections=10,
       keepalive_expiry=30.0,
       
       # Retry configuration
       retry_backoff_factor=1.0,
       retry_backoff_max=60.0,
       retry_on_status_codes=[429, 502, 503, 504],
       
       # Debug mode
       debug=True,
       log_requests=True,
       log_responses=True
   )

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from honeyhive import HoneyHive
   
   def create_client_from_env():
       """Create client with environment-based configuration."""
       
       config = {
           "api_key": os.getenv("HH_API_KEY"),
           "base_url": os.getenv("HH_BASE_URL", "https://api.honeyhive.ai"),
           "timeout": float(os.getenv("HH_TIMEOUT", "30.0")),
           "max_retries": int(os.getenv("HH_MAX_RETRIES", "3")),
           "test_mode": os.getenv("HH_TEST_MODE", "false").lower() == "true"
       }
       
       # Optional proxy configuration
       if proxy_url := os.getenv("HH_PROXY_URL"):
           config["proxy_url"] = proxy_url
       
       # Optional SSL configuration
       if cert_path := os.getenv("HH_SSL_CERT_PATH"):
           config["ssl_cert_path"] = cert_path
       
       return HoneyHive(**config)
   
   # Usage
   client = create_client_from_env()

Integration Patterns
--------------------

Context Manager Usage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Automatic resource cleanup
   with HoneyHive(api_key="hh_key") as client:  # Or set HH_API_KEY environment variable
       session = client.create_session(
           source="production"
       )
       
       # Multiple operations
       for i in range(10):
           client.create_event(
               session_id=session['session_id'],
               event_type=EventType.tool,
               event_name=f"iteration_{i}",
               inputs={"iteration": i},
               outputs={"result": i * 2}
           )
   # Client automatically closed and cleaned up

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import Protocol
   
   class HoneyHiveClientProtocol(Protocol):
       def create_session(self, project: str, **kwargs) -> dict: ...
       def create_event(self, session_id: str, **kwargs) -> dict: ...
   
   class MyService:
       def __init__(self, honeyhive_client: HoneyHiveClientProtocol):
           self.client = honeyhive_client
       
       def process_user_request(self, user_id: str, request_data: dict):
           # Create session for this request
           session = self.client.create_session(
               source="development",
               user_id=user_id
           )
           
           # Process and log events
           event = self.client.create_event(
               session_id=session['session_id'],
               event_type=EventType.session,
               event_name="process_request",
               inputs={"user_id": user_id, "request": request_data},
               outputs={"result": "processed"}
           )
           
           return event
   
   # Dependency injection
   client = HoneyHive(api_key="hh_key")  # Or set HH_API_KEY environment variable
   service = MyService(honeyhive_client=client)

Factory Pattern
~~~~~~~~~~~~~~~

.. code-block:: python

   class HoneyHiveClientFactory:
       """Factory for creating configured HoneyHive clients."""
       
       @staticmethod
       def create_production_client(api_key: str) -> HoneyHive:
           return HoneyHive(
               api_key=api_key,  # Or set HH_API_KEY environment variable
               timeout=60.0,
               max_retries=5,
               rate_limit_calls=200,
               rate_limit_period=60
           )
       
       @staticmethod
       def create_development_client(api_key: str) -> HoneyHive:
           return HoneyHive(
               api_key=api_key,      # Or set HH_API_KEY environment variable
               test_mode=True,       # Or set HH_TEST_MODE=true environment variable
               timeout=10.0,
               max_retries=1,
               debug=True,
               log_requests=True
           )
       
       @staticmethod
       def create_testing_client() -> HoneyHive:
           return HoneyHive(
               api_key="test_key",   # Or set HH_API_KEY environment variable
               test_mode=True,       # Or set HH_TEST_MODE=true environment variable
               timeout=5.0,
               max_retries=0
           )
   
   # Usage
   if os.getenv("ENVIRONMENT") == "production":
       client = HoneyHiveClientFactory.create_production_client(
           api_key=os.getenv("HH_API_KEY")
       )
   elif os.getenv("ENVIRONMENT") == "development":
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

   # Configure connection pooling for high-throughput applications
   client = HoneyHive(
       api_key="hh_key",             # Or set HH_API_KEY environment variable
       max_connections=100,          # Total connection pool size
       max_keepalive_connections=20, # Persistent connections
       keepalive_expiry=60.0,        # Connection lifetime
       connection_timeout=10.0,      # Time to establish connection
       read_timeout=30.0,           # Time to read response
       write_timeout=10.0           # Time to send request
   )

Request Batching
~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from honeyhive import AsyncHoneyHive
   
   async def batch_events_efficiently():
       async with AsyncHoneyHive(api_key="hh_key") as client:  # Or set HH_API_KEY environment variable
           session = await client.create_session(
               source="production"
           )
           
           # Create events in batches for better performance
           batch_size = 50
           all_events = []
           
           for batch_start in range(0, 1000, batch_size):
               batch_events = []
               
               for i in range(batch_start, min(batch_start + batch_size, 1000)):
                   batch_events.append({
                       "session_id": session['session_id'],
                       "event_type": "batch_item",
                       "event_name": f"item_{i}",
                       "inputs": {"item_id": i},
                       "outputs": {"processed": True}
                   })
               
               # Send batch
               result = await client.create_events_batch(batch_events)
               all_events.extend(result['events'])
               
               print(f"Processed batch {batch_start//batch_size + 1}")
           
           return all_events

See Also
--------

- :doc:`tracer` - HoneyHiveTracer API reference
- :doc:`decorators` - Decorator-based APIs
- :doc:`../../tutorials/01-setup-first-tracer` - Getting started tutorial
- :doc:`../../how-to/index` - Client troubleshooting (see Troubleshooting section)
- :doc:`../../explanation/architecture/overview` - Architecture overview
