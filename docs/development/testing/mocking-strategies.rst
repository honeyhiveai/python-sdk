Mocking Strategies & Test Doubles
=================================

.. note::
   **Problem-solving guide for mocking HoneyHive SDK components**
   
   Practical solutions for creating test doubles, mocks, and stubs to isolate your code under test and control external dependencies.

Mocking allows you to test your code in isolation by replacing external dependencies with controlled test doubles. This is essential for reliable, fast unit tests.

Quick Start
-----------

**Problem**: I need to mock HoneyHive SDK to test my application without making real API calls.

**Solution**:

.. code-block:: python

   from unittest.mock import Mock, patch
   import pytest
   
   def test_with_mocked_honeyhive():
       """Quick example of mocking HoneyHive SDK."""
       with patch('honeyhive.HoneyHiveTracer') as mock_tracer_class:
           # Configure mock
           mock_tracer = Mock()
           mock_span = Mock()
           mock_span.__enter__ = Mock(return_value=mock_span)
           mock_span.__exit__ = Mock(return_value=None)
           
           mock_tracer.trace.return_value = mock_span
           mock_tracer_class.init.return_value = mock_tracer
           
           # Import and use your code that uses HoneyHive
           from your_app import function_that_uses_honeyhive
           
           result = function_that_uses_honeyhive("test_input")
           
           # Verify interactions
           mock_tracer_class.init.assert_called_once()
           mock_tracer.trace.assert_called()
           assert result is not None

Mock Tracer Creation
--------------------

**Problem**: Create a comprehensive mock tracer for testing.

**Solution - Mock Tracer Class**:

.. code-block:: python

   """Comprehensive mock tracer for HoneyHive SDK testing."""
   
   from unittest.mock import Mock, MagicMock
   from typing import Dict, Any, List, Optional
   import time
   import threading
   
   class MockHoneyHiveTracer:
       """Mock implementation of HoneyHiveTracer for testing."""
       
       def __init__(self, **kwargs):
           self.api_key = kwargs.get("api_key", "mock-api-key")
           self.project = kwargs.get("project", "mock-project")
           self.source = kwargs.get("source", "mock-source")
           self.session_name = kwargs.get("session_name", "mock-session")
           self.test_mode = kwargs.get("test_mode", True)
           self.session_id = f"mock-session-{int(time.time())}"
           
           # Track all created spans
           self.spans = []
           self.events = []
           self.flush_calls = []
           self.close_calls = []
           
           # Threading support
           self._lock = threading.Lock()
       
       def trace(self, name: str, **kwargs) -> 'MockSpan':
           """Create a mock span."""
           span = MockSpan(name, tracer=self, **kwargs)
           with self._lock:
               self.spans.append(span)
           return span
       
       def start_span(self, name: str, **kwargs) -> 'MockSpan':
           """Start a mock span (alias for trace)."""
           return self.trace(name, **kwargs)
       
       def enrich_current_span(self, **kwargs):
           """Mock span enrichment."""
           if self.spans:
               current_span = self.spans[-1]
               current_span.enrich(**kwargs)
       
       def force_flush(self, timeout_millis: int = 5000) -> bool:
           """Mock force flush operation."""
           with self._lock:
               self.flush_calls.append({
                   "timeout_millis": timeout_millis,
                   "timestamp": time.time()
               })
           return True  # Always successful in mock
       
       def close(self):
           """Mock close operation."""
           with self._lock:
               self.close_calls.append({"timestamp": time.time()})
       
       # Test utilities
       def get_spans(self) -> List['MockSpan']:
           """Get all created spans for verification."""
           with self._lock:
               return self.spans.copy()
       
       def get_span_by_name(self, name: str) -> Optional['MockSpan']:
           """Get span by name for verification."""
           for span in self.spans:
               if span.name == name:
                   return span
           return None
       
       def clear_spans(self):
           """Clear all recorded spans."""
           with self._lock:
               self.spans.clear()
               self.events.clear()
       
       def assert_span_created(self, name: str):
           """Assert that a span with given name was created."""
           span = self.get_span_by_name(name)
           assert span is not None, f"No span found with name: {name}"
           return span
       
       def assert_attribute_set(self, span_name: str, key: str, value: Any):
           """Assert that an attribute was set on a span."""
           span = self.assert_span_created(span_name)
           assert key in span.attributes, f"Attribute '{key}' not found in span '{span_name}'"
           assert span.attributes[key] == value, f"Attribute '{key}' has value {span.attributes[key]}, expected {value}"
   
   class MockSpan:
       """Mock implementation of a tracing span."""
       
       def __init__(self, name: str, tracer: MockHoneyHiveTracer = None, **kwargs):
           self.name = name
           self.tracer = tracer
           self.attributes = {}
           self.events = []
           self.exceptions = []
           self.status = "OK"
           self.start_time = time.time()
           self.end_time = None
           self.is_active = False
           
           # Extract kwargs
           self.event_type = kwargs.get("event_type")
           self.event_name = kwargs.get("event_name")
       
       def __enter__(self):
           """Context manager entry."""
           self.is_active = True
           return self
       
       def __exit__(self, exc_type, exc_val, exc_tb):
           """Context manager exit."""
           self.is_active = False
           self.end_time = time.time()
           
           if exc_type:
               self.record_exception(exc_val)
               self.status = "ERROR"
           
           return False  # Don't suppress exceptions
       
       def set_attribute(self, key: str, value: Any):
           """Set span attribute."""
           self.attributes[key] = value
       
       def get_attribute(self, key: str) -> Any:
           """Get span attribute."""
           return self.attributes.get(key)
       
       def record_exception(self, exception: Exception):
           """Record exception in span."""
           self.exceptions.append({
               "exception": exception,
               "timestamp": time.time()
           })
           self.set_attribute("error.type", type(exception).__name__)
           self.set_attribute("error.message", str(exception))
       
       def add_event(self, name: str, attributes: Dict[str, Any] = None):
           """Add event to span."""
           event = {
               "name": name,
               "attributes": attributes or {},
               "timestamp": time.time()
           }
           self.events.append(event)
           
           if self.tracer:
               self.tracer.events.append(event)
       
       def enrich(self, **kwargs):
           """Enrich span with additional data."""
           for key, value in kwargs.items():
               if key == "metadata" and isinstance(value, dict):
                   for meta_key, meta_value in value.items():
                       self.set_attribute(f"metadata.{meta_key}", meta_value)
               elif key == "outputs" and isinstance(value, dict):
                   for output_key, output_value in value.items():
                       self.set_attribute(f"output.{output_key}", output_value)
               else:
                   self.set_attribute(key, value)
       
       def duration_ms(self) -> float:
           """Get span duration in milliseconds."""
           if self.end_time:
               return (self.end_time - self.start_time) * 1000
           return (time.time() - self.start_time) * 1000

**Using Mock Tracer**:

.. code-block:: python

   def test_with_mock_tracer():
       """Example of using MockHoneyHiveTracer."""
       # Create mock tracer
       mock_tracer = MockHoneyHiveTracer(
           api_key="test-key"       )
       
       # Use mock tracer in your code
       with mock_tracer.trace("test-operation") as span:
           span.set_attribute("test.value", "mock-test")
           span.add_event("test-event", {"event_data": "test"})
       
       # Verify interactions
       mock_tracer.assert_span_created("test-operation")
       mock_tracer.assert_attribute_set("test-operation", "test.value", "mock-test")
       
       # Check events
       spans = mock_tracer.get_spans()
       assert len(spans) == 1
       assert len(spans[0].events) == 1
       assert spans[0].events[0]["name"] == "test-event"

Patching Strategies
-------------------

**Problem**: Mock HoneyHive SDK at different levels of your application.

**Solution - Comprehensive Patching Strategies**:

.. code-block:: python

   """Different strategies for patching HoneyHive SDK."""
   
   import pytest
   from unittest.mock import patch, Mock, MagicMock
   
   # Strategy 1: Patch at module level
   @patch('honeyhive.HoneyHiveTracer')
   def test_module_level_patching(mock_tracer_class):
       """Patch the entire tracer class."""
       mock_tracer = Mock()
       mock_tracer_class.init.return_value = mock_tracer
       
       # Your code that imports and uses HoneyHive
       from your_app import initialize_tracing
       
       tracer = initialize_tracing()
       mock_tracer_class.init.assert_called_once()
   
   # Strategy 2: Patch at import level
   def test_import_level_patching():
       """Patch HoneyHive at import time."""
       with patch.dict('sys.modules', {'honeyhive': Mock()}):
           # Re-import your module with mocked honeyhive
           import importlib
           import your_app
           importlib.reload(your_app)
           
           # Test your app with mocked honeyhive
           result = your_app.some_function()
           assert result is not None
   
   # Strategy 3: Patch specific methods
   @patch('honeyhive.HoneyHiveTracer.init')
   @patch('honeyhive.HoneyHiveTracer.trace')
   def test_method_level_patching(mock_trace, mock_init):
       """Patch specific tracer methods."""
       mock_tracer = Mock()
       mock_init.return_value = mock_tracer
       
       mock_span = Mock()
       mock_span.__enter__ = Mock(return_value=mock_span)
       mock_span.__exit__ = Mock(return_value=None)
       mock_trace.return_value = mock_span
       
       # Your code
       from honeyhive import HoneyHiveTracer
       tracer = HoneyHiveTracer.init(
           api_key="test",          # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       
       with tracer.trace("test") as span:
           span.set_attribute("key", "value")
       
       mock_init.assert_called_once()
       mock_trace.assert_called_once_with("test")
   
   # Strategy 4: Context manager patching
   def test_context_manager_patching():
       """Use patch as context manager for fine control."""
       with patch('honeyhive.HoneyHiveTracer') as mock_class:
           mock_tracer = MockHoneyHiveTracer()
           mock_class.init.return_value = mock_tracer
           
           # Test specific behavior
           result = your_function_that_uses_honeyhive()
           
           # Verify specific interactions
           assert mock_tracer.spans
           assert result is not None
   
   # Strategy 5: Decorator-based patching
   class TestWithPatching:
       """Test class with decorator-based patching."""
       
       @patch('honeyhive.HoneyHiveTracer')
       def test_method1(self, mock_tracer):
           """Test with mocked tracer."""
           mock_tracer.init.return_value = Mock()
           # Test code here
       
       @patch.object('honeyhive.HoneyHiveTracer', 'init')
       def test_method2(self, mock_init):
           """Test with mocked init method."""
           mock_init.return_value = MockHoneyHiveTracer()
           # Test code here

Fixture-Based Mocking
---------------------

**Problem**: Create reusable mock fixtures for consistent testing.

**Solution - PyTest Fixtures**:

.. code-block:: python

   """PyTest fixtures for HoneyHive mocking."""
   
   import pytest
   from unittest.mock import Mock, patch
   
   @pytest.fixture
   def mock_tracer():
       """Fixture providing a mock HoneyHive tracer."""
       return MockHoneyHiveTracer(
           api_key="fixture-test-key",           test_mode=True
       )
   
   @pytest.fixture
   def mock_honeyhive_class():
       """Fixture that patches HoneyHiveTracer class."""
       with patch('honeyhive.HoneyHiveTracer') as mock_class:
           mock_tracer = MockHoneyHiveTracer()
           mock_class.init.return_value = mock_tracer
           mock_class.return_value = mock_tracer
           yield mock_class
   
   @pytest.fixture
   def mock_honeyhive_init():
       """Fixture that patches HoneyHiveTracer.init method."""
       with patch('honeyhive.HoneyHiveTracer.init') as mock_init:
           mock_tracer = MockHoneyHiveTracer()
           mock_init.return_value = mock_tracer
           yield mock_tracer
   
   @pytest.fixture
   def mock_honeyhive_trace_method():
       """Fixture that patches the trace method specifically."""
       with patch('honeyhive.HoneyHiveTracer.trace') as mock_trace:
           mock_span = MockSpan("mocked-span")
           mock_trace.return_value = mock_span
           yield mock_trace
   
   @pytest.fixture
   def mock_honeyhive_decorators():
       """Fixture that patches HoneyHive decorators."""
       with patch('honeyhive.trace') as mock_trace_decorator:
           def trace_wrapper(func):
               """Mock trace decorator that just calls the function."""
               def wrapper(*args, **kwargs):
                   return func(*args, **kwargs)
               return wrapper
           
           mock_trace_decorator.side_effect = trace_wrapper
           yield mock_trace_decorator
   
   @pytest.fixture
   def isolated_honeyhive():
       """Fixture that completely isolates HoneyHive imports."""
       with patch.dict('sys.modules', {
           'honeyhive': Mock(),
           'honeyhive.tracer': Mock(),
           'honeyhive.api': Mock(),
           'honeyhive.evaluation': Mock()
       }):
           yield

**Using Mock Fixtures**:

.. code-block:: python

   def test_with_mock_tracer_fixture(mock_tracer):
       """Test using mock tracer fixture."""
       # Use the mock tracer directly
       with mock_tracer.trace("fixture-test") as span:
           span.set_attribute("test.fixture", True)
       
       # Verify using mock tracer utilities
       mock_tracer.assert_span_created("fixture-test")
       mock_tracer.assert_attribute_set("fixture-test", "test.fixture", True)
   
   def test_with_mocked_class(mock_honeyhive_class):
       """Test with completely mocked HoneyHive class."""
       from honeyhive import HoneyHiveTracer
       
       tracer = HoneyHiveTracer.init(
           api_key="test",          # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       mock_honeyhive_class.init.assert_called_once_with(api_key="test")
   
   def test_with_isolated_honeyhive(isolated_honeyhive):
       """Test with completely isolated HoneyHive."""
       # HoneyHive is completely mocked, won't interfere with test
       result = some_function_that_imports_honeyhive()
       assert result is not None

Mocking External Dependencies
-----------------------------

**Problem**: Mock external services that HoneyHive might interact with.

**Solution - External Dependency Mocking**:

.. code-block:: python

   """Mocking external dependencies for HoneyHive testing."""
   
   import pytest
   from unittest.mock import Mock, patch, MagicMock
   import requests
   
   class MockHoneyHiveAPI:
       """Mock implementation of HoneyHive API."""
       
       def __init__(self):
           self.sessions = []
           self.events = []
           self.projects = []
           self.call_log = []
       
       def create_session(self, project: str, session_name: str = None):
           """Mock session creation."""
           session = {
               "session_id": f"mock-session-{len(self.sessions)}",
               "project": project,
               "session_name": session_name or f"session-{len(self.sessions)}",
               "created_at": "2024-01-01T00:00:00Z"
           }
           self.sessions.append(session)
           self.call_log.append(("create_session", session))
           return session
       
       def create_event(self, session_id: str, event_data: dict):
           """Mock event creation."""
           event = {
               "event_id": f"mock-event-{len(self.events)}",
               "session_id": session_id,
               **event_data,
               "created_at": "2024-01-01T00:00:00Z"
           }
           self.events.append(event)
           self.call_log.append(("create_event", event))
           return event
       
       def get_session(self, session_id: str):
           """Mock session retrieval."""
           for session in self.sessions:
               if session["session_id"] == session_id:
                   self.call_log.append(("get_session", session_id))
                   return session
           return None
   
   @pytest.fixture
   def mock_api():
       """Fixture providing mock HoneyHive API."""
       return MockHoneyHiveAPI()
   
   @pytest.fixture
   def mock_requests():
       """Fixture that mocks HTTP requests."""
       with patch('requests.post') as mock_post:
           mock_response = Mock()
           mock_response.status_code = 200
           mock_response.json.return_value = {"status": "success"}
           mock_post.return_value = mock_response
           yield mock_post
   
   @pytest.fixture
   def mock_network_failure():
       """Fixture that simulates network failures."""
       with patch('requests.post') as mock_post:
           mock_post.side_effect = requests.ConnectionError("Network error")
           yield mock_post
   
   def test_with_mocked_api(mock_api, mock_requests):
       """Test with mocked API and network calls."""
       # Configure requests mock to return API responses
       def mock_post_response(url, **kwargs):
           if "sessions" in url:
               return Mock(
                   status_code=200,
                   json=lambda: mock_api.create_session("test-project")
               )
           elif "events" in url:
               return Mock(
                   status_code=200,
                   json=lambda: mock_api.create_event("session-1", kwargs.get("json", {}))
               )
           return Mock(status_code=200, json=lambda: {})
       
       mock_requests.side_effect = mock_post_response
       
       # Test your code that uses HoneyHive API
       from honeyhive import HoneyHiveTracer
       tracer = HoneyHiveTracer.init(
           api_key="test-key",           test_mode=False  # Use "real" API (which is mocked)
       )
       
       with tracer.trace("api-test") as span:
           span.set_attribute("test.api", True)
       
       # Verify API calls were made
       assert len(mock_api.call_log) > 0
   
   def test_network_failure_handling(mock_network_failure):
       """Test handling of network failures."""
       from honeyhive import HoneyHiveTracer
       
       # Should not raise exception even with network failure
       tracer = HoneyHiveTracer.init(
           api_key="test-key",           test_mode=False
       )
       
       # Should handle gracefully
       with tracer.trace("network-failure-test") as span:
           span.set_attribute("test.network_failure", True)
       
       # Verify network call was attempted
       mock_network_failure.assert_called()

Mocking Async Operations
------------------------

**Problem**: Mock async operations in HoneyHive SDK.

**Solution - Async Mocking**:

.. code-block:: python

   """Mocking async operations for HoneyHive SDK."""
   
   import asyncio
   import pytest
   from unittest.mock import AsyncMock, Mock, patch
   
   class MockAsyncHoneyHiveTracer:
       """Mock async tracer for testing."""
       
       def __init__(self, **kwargs):
           self.api_key = kwargs.get("api_key", "mock-key")
           self.project = kwargs.get("project", "mock-project")
           self.spans = []
       
       async def atrace(self, name: str, **kwargs):
           """Mock async trace method."""
           span = MockSpan(name)
           self.spans.append(span)
           return span
       
       async def force_flush(self, timeout_millis: int = 5000) -> bool:
           """Mock async flush operation."""
           await asyncio.sleep(0.01)  # Simulate async work
           return True
       
       async def close(self):
           """Mock async close operation."""
           await asyncio.sleep(0.01)  # Simulate cleanup
   
   @pytest.fixture
   def mock_async_tracer():
       """Fixture providing mock async tracer."""
       return MockAsyncHoneyHiveTracer()
   
   @pytest.fixture
   def mock_async_honeyhive():
       """Fixture that patches async HoneyHive operations."""
       with patch('honeyhive.atrace') as mock_atrace:
           async_mock = AsyncMock()
           mock_atrace.return_value = async_mock
           yield mock_atrace
   
   @pytest.mark.asyncio
   async def test_async_operations(mock_async_tracer):
       """Test async operations with mock tracer."""
       # Test async trace
       span = await mock_async_tracer.atrace("async-test")
       assert span.name == "async-test"
       
       # Test async flush
       flush_result = await mock_async_tracer.force_flush()
       assert flush_result is True
       
       # Test async close
       await mock_async_tracer.close()
   
   @pytest.mark.asyncio
   async def test_with_async_mock_decorator(mock_async_honeyhive):
       """Test with async decorator mocking."""
       from honeyhive import atrace
       
       @atrace(event_type="async_test")
       async def async_function():
           await asyncio.sleep(0.01)
           return "async_result"
       
       result = await async_function()
       assert result == "async_result"
       mock_async_honeyhive.assert_called()

Advanced Mocking Patterns
-------------------------

**Problem**: Implement sophisticated mocking patterns for complex scenarios.

**Solution - Advanced Patterns**:

.. code-block:: python

   """Advanced mocking patterns for complex testing scenarios."""
   
   from unittest.mock import Mock, MagicMock, PropertyMock, call
   from contextlib import contextmanager
   import time
   
   class StatefulMockTracer:
       """Mock tracer that maintains state across calls."""
       
       def __init__(self):
           self.state = "initialized"
           self.spans = []
           self.call_count = 0
           self.errors = []
       
       def trace(self, name: str, **kwargs):
           """Stateful trace method."""
           self.call_count += 1
           
           if self.state == "error_mode":
               raise Exception(f"Simulated error for span: {name}")
           
           span = MockSpan(name)
           self.spans.append(span)
           
           # Simulate state changes
           if self.call_count > 10:
               self.state = "rate_limited"
           
           return span
       
       def set_error_mode(self, enabled: bool = True):
           """Set tracer to error mode for testing error handling."""
           self.state = "error_mode" if enabled else "normal"
       
       def reset(self):
           """Reset tracer state."""
           self.state = "initialized"
           self.spans.clear()
           self.call_count = 0
           self.errors.clear()
   
   class ConditionalMockTracer:
       """Mock tracer with conditional behavior."""
       
       def __init__(self):
           self.conditions = {}
           self.default_behavior = lambda name, **kwargs: MockSpan(name)
       
       def add_condition(self, span_name: str, behavior):
           """Add conditional behavior for specific span names."""
           self.conditions[span_name] = behavior
       
       def trace(self, name: str, **kwargs):
           """Trace with conditional behavior."""
           if name in self.conditions:
               return self.conditions[name](name, **kwargs)
           return self.default_behavior(name, **kwargs)
   
   def test_stateful_mocking():
       """Test with stateful mock tracer."""
       mock_tracer = StatefulMockTracer()
       
       # Normal operation
       span1 = mock_tracer.trace("test-1")
       assert span1.name == "test-1"
       assert mock_tracer.state == "initialized"
       
       # Set error mode
       mock_tracer.set_error_mode(True)
       
       with pytest.raises(Exception, match="Simulated error"):
           mock_tracer.trace("test-error")
       
       # Reset and continue
       mock_tracer.reset()
       span2 = mock_tracer.trace("test-2")
       assert span2.name == "test-2"
   
   def test_conditional_mocking():
       """Test with conditional mock behavior."""
       mock_tracer = ConditionalMockTracer()
       
       # Add specific behavior for certain spans
       def slow_span_behavior(name, **kwargs):
           span = MockSpan(name)
           span.set_attribute("performance.slow", True)
           return span
       
       def error_span_behavior(name, **kwargs):
           raise Exception(f"Error in {name}")
       
       mock_tracer.add_condition("slow-operation", slow_span_behavior)
       mock_tracer.add_condition("error-operation", error_span_behavior)
       
       # Test normal span
       normal_span = mock_tracer.trace("normal-operation")
       assert normal_span.name == "normal-operation"
       
       # Test slow span
       slow_span = mock_tracer.trace("slow-operation")
       assert slow_span.get_attribute("performance.slow") is True
       
       # Test error span
       with pytest.raises(Exception, match="Error in error-operation"):
           mock_tracer.trace("error-operation")
   
   class MockTracerBuilder:
       """Builder pattern for creating configured mock tracers."""
       
       def __init__(self):
           self.mock_tracer = Mock()
           self.spans_config = {}
           self.global_config = {}
       
       def with_span(self, name: str, attributes: dict = None, should_error: bool = False):
           """Configure a specific span."""
           self.spans_config[name] = {
               "attributes": attributes or {},
               "should_error": should_error
           }
           return self
       
       def with_global_config(self, **kwargs):
           """Configure global tracer behavior."""
           self.global_config.update(kwargs)
           return self
       
       def build(self):
           """Build the configured mock tracer."""
           def mock_trace(name, **kwargs):
               if name in self.spans_config:
                   config = self.spans_config[name]
                   if config["should_error"]:
                       raise Exception(f"Configured error for {name}")
                   
                   span = MockSpan(name)
                   for key, value in config["attributes"].items():
                       span.set_attribute(key, value)
                   return span
               
               return MockSpan(name)
           
           self.mock_tracer.trace = mock_trace
           
           # Configure global properties
           for key, value in self.global_config.items():
               setattr(self.mock_tracer, key, value)
           
           return self.mock_tracer
   
   def test_builder_pattern():
       """Test mock tracer builder pattern."""
       mock_tracer = (MockTracerBuilder()
                      .with_span("db-query", {"db.table": "users"})
                      .with_span("api-call", {"http.status": 200})
                      .with_span("error-operation", should_error=True)
                      .with_global_config(api_key="test-key")
                      .build())
       
       # Test configured spans
       db_span = mock_tracer.trace("db-query")
       assert db_span.get_attribute("db.table") == "users"
       
       api_span = mock_tracer.trace("api-call")
       assert api_span.get_attribute("http.status") == 200
       
       # Test error span
       with pytest.raises(Exception, match="Configured error"):
           mock_tracer.trace("error-operation")
       
       # Test global config
       assert mock_tracer.api_key == "test-key"
       assert mock_tracer.project == "test"

Mock Validation Utilities
-------------------------

**Problem**: Create utilities to validate mock interactions.

**Solution - Validation Framework**:

.. code-block:: python

   """Utilities for validating mock interactions."""
   
   from typing import List, Dict, Any, Optional
   import re
   
   class MockValidator:
       """Utilities for validating mock tracer interactions."""
       
       def __init__(self, mock_tracer):
           self.mock_tracer = mock_tracer
       
       def assert_span_count(self, expected_count: int):
           """Assert expected number of spans were created."""
           actual_count = len(self.mock_tracer.spans)
           assert actual_count == expected_count, f"Expected {expected_count} spans, got {actual_count}"
       
       def assert_span_names(self, expected_names: List[str]):
           """Assert specific span names were created."""
           actual_names = [span.name for span in self.mock_tracer.spans]
           assert actual_names == expected_names, f"Expected {expected_names}, got {actual_names}"
       
       def assert_span_attributes(self, span_name: str, expected_attributes: Dict[str, Any]):
           """Assert span has expected attributes."""
           span = self.mock_tracer.get_span_by_name(span_name)
           assert span is not None, f"Span '{span_name}' not found"
           
           for key, expected_value in expected_attributes.items():
               actual_value = span.get_attribute(key)
               assert actual_value == expected_value, f"Span '{span_name}' attribute '{key}': expected {expected_value}, got {actual_value}"
       
       def assert_span_pattern(self, pattern: str):
           """Assert span names match a pattern."""
           regex = re.compile(pattern)
           for span in self.mock_tracer.spans:
               assert regex.match(span.name), f"Span name '{span.name}' doesn't match pattern '{pattern}'"
       
       def assert_flush_called(self, times: int = None):
           """Assert force_flush was called."""
           flush_calls = len(self.mock_tracer.flush_calls)
           if times is not None:
               assert flush_calls == times, f"Expected {times} flush calls, got {flush_calls}"
           else:
               assert flush_calls > 0, "Expected at least one flush call"
       
       def assert_no_errors(self):
           """Assert no spans recorded errors."""
           for span in self.mock_tracer.spans:
               assert span.status != "ERROR", f"Span '{span.name}' has error status"
               assert not span.exceptions, f"Span '{span.name}' recorded exceptions: {span.exceptions}"
       
       def assert_span_hierarchy(self, expected_hierarchy: Dict[str, List[str]]):
           """Assert span parent-child relationships."""
           # This would need more sophisticated implementation
           # based on how span hierarchy is tracked in your mock
           pass
       
       def get_interaction_summary(self) -> Dict[str, Any]:
           """Get summary of all mock interactions."""
           return {
               "total_spans": len(self.mock_tracer.spans),
               "span_names": [span.name for span in self.mock_tracer.spans],
               "total_attributes": sum(len(span.attributes) for span in self.mock_tracer.spans),
               "total_events": sum(len(span.events) for span in self.mock_tracer.spans),
               "error_spans": [span.name for span in self.mock_tracer.spans if span.status == "ERROR"],
               "flush_calls": len(self.mock_tracer.flush_calls),
               "close_calls": len(self.mock_tracer.close_calls)
           }
   
   def test_with_validation():
       """Example of using mock validation utilities."""
       mock_tracer = MockHoneyHiveTracer()
       validator = MockValidator(mock_tracer)
       
       # Run code under test
       with mock_tracer.trace("operation-1") as span:
           span.set_attribute("step", 1)
       
       with mock_tracer.trace("operation-2") as span:
           span.set_attribute("step", 2)
       
       mock_tracer.force_flush()
       
       # Validate interactions
       validator.assert_span_count(2)
       validator.assert_span_names(["operation-1", "operation-2"])
       validator.assert_span_attributes("operation-1", {"step": 1})
       validator.assert_span_attributes("operation-2", {"step": 2})
       validator.assert_flush_called(times=1)
       validator.assert_no_errors()
       
       # Get summary
       summary = validator.get_interaction_summary()
       print(f"Test summary: {summary}")

Best Practices for Mocking
--------------------------

**Mocking Guidelines**:

1. **Mock at the Right Level**: Mock at the boundary of your code, not deep internals
2. **Use Realistic Mocks**: Make mocks behave like the real system
3. **Verify Interactions**: Check that your code calls mocks as expected
4. **Test Error Scenarios**: Mock failures to test error handling
5. **Keep Mocks Simple**: Don't make mocks more complex than necessary
6. **Reset Between Tests**: Ensure mocks are clean for each test
7. **Document Mock Behavior**: Make it clear what the mock represents

**Common Patterns**:

.. code-block:: python

   # Pattern 1: Mock with side effects
   mock_tracer.trace.side_effect = [
       MockSpan("span1"), 
       MockSpan("span2"),
       Exception("Third call fails")
   ]
   
   # Pattern 2: Mock with return values based on arguments
   def trace_side_effect(name, **kwargs):
       if "error" in name:
           raise Exception(f"Error in {name}")
       return MockSpan(name)
   
   mock_tracer.trace.side_effect = trace_side_effect
   
   # Pattern 3: Partial mocking
   real_tracer = HoneyHiveTracer.init(api_key="test", test_mode=True)
   real_tracer.trace = Mock(side_effect=real_tracer.trace)
   
   # Pattern 4: Property mocking
   with patch.object(HoneyHiveTracer, 'session_id', new_callable=PropertyMock) as mock_session_id:
       mock_session_id.return_value = "mock-session-123"

See Also
--------

- :doc:`unit-testing` - Unit testing strategies using mocks
- :doc:`integration-testing` - When to use mocks vs real integrations
- :doc:`troubleshooting-tests` - Debugging issues with mocks
- :doc:`../../reference/api/tracer` - Real tracer API for accurate mocking
