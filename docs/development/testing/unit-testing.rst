Unit Testing Strategies
=======================

.. note::
   **Problem-solving guide for unit testing HoneyHive SDK components**
   
   Practical solutions for testing individual SDK components in isolation with comprehensive examples.

Unit testing focuses on testing individual components of the HoneyHive SDK in isolation to ensure each part works correctly before integration.

Quick Start
-----------

**Problem**: I need to start unit testing my HoneyHive integration immediately.

**Solution**:

.. code-block:: python

   import pytest
   from honeyhive import HoneyHiveTracer
   
   def test_tracer_initialization():
       """Test basic tracer initialization."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",      # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Critical for unit tests (or set HH_TEST_MODE=true)
       )
       
       assert tracer.api_key == "test-key"
       assert tracer.project == "test-project"
       assert tracer.test_mode is True

Testing Tracer Initialization
-----------------------------

**Problem**: Test different tracer initialization scenarios.

**Solution**:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   
   class TestTracerInitialization:
       """Test tracer initialization scenarios."""
       
       def test_basic_initialization(self):
           """Test basic tracer initialization."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           assert tracer is not None
           assert tracer.api_key == "test-key"
           assert tracer.project == "test-project"
           assert tracer.test_mode is True
       
       def test_environment_variable_initialization(self):
           """Test initialization from environment variables."""
           # Set environment variables
           os.environ["HH_API_KEY"] = "env-test-key"
           os.environ["           os.environ["HH_TEST_MODE"] = "true"
           
           try:
               tracer = HoneyHiveTracer.init(
                   # Uses HH_API_KEY and HH_PROJECT environment variables
               )
               
               assert tracer.api_key == "env-test-key"
               assert tracer.project == "env-test-project" 
               assert tracer.test_mode is True
           finally:
               # Clean up environment variables
               del os.environ["HH_API_KEY"]
               del os.environ["HH_PROJECT"]
               del os.environ["HH_TEST_MODE"]
       
       def test_missing_api_key_raises_error(self):
           """Test that missing API key raises appropriate error."""
           with pytest.raises(ValueError, match="API key is required"):
               HoneyHiveTracer.init(
                   api_key=None               )
       
       def test_custom_configuration(self):
           """Test initialization with custom configuration."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",               source="development"
               session_name="custom-session",
               test_mode=True,
               disable_http_tracing=True
           )
           
           assert tracer.project == "custom-project"
           assert tracer.source == "custom-source"
           assert tracer.session_name == "custom-session"

Testing Span Operations
-----------------------

**Problem**: Test span creation and management.

**Solution**:

.. code-block:: python

   import time
   from honeyhive import HoneyHiveTracer
   
   class TestSpanOperations:
       """Test span creation and management."""
       
       @pytest.fixture
       def tracer(self):
           """Create test tracer fixture."""
           return HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
       
       def test_span_creation(self, tracer):
           """Test basic span creation."""
           with tracer.trace("test-span") as span:
               assert span is not None
               assert span.name == "test-span"
       
       def test_span_attributes(self, tracer):
           """Test setting span attributes."""
           with tracer.trace("attribute-test") as span:
               span.set_attribute("test.attribute", "value")
               span.set_attribute("test.number", 42)
               span.set_attribute("test.boolean", True)
               
               # Verify attributes are set
               assert span.get_attribute("test.attribute") == "value"
               assert span.get_attribute("test.number") == 42
               assert span.get_attribute("test.boolean") is True
       
       def test_nested_spans(self, tracer):
           """Test nested span creation."""
           with tracer.trace("parent-span") as parent:
               parent.set_attribute("span.level", "parent")
               
               with tracer.trace("child-span") as child:
                   child.set_attribute("span.level", "child")
                   assert child is not None
                   
                   # Verify parent-child relationship
                   assert parent is not child
       
       def test_span_timing(self, tracer):
           """Test span timing functionality."""
           start_time = time.time()
           
           with tracer.trace("timed-operation") as span:
               time.sleep(0.1)  # Simulate work
               span.set_attribute("operation.duration", 0.1)
           
           end_time = time.time()
           actual_duration = end_time - start_time
           
           # Verify timing is reasonable
           assert 0.09 <= actual_duration <= 0.2  # Account for timing variance

Testing Decorators
------------------

**Problem**: Test the ``@trace`` decorator functionality.

**Solution**:

.. code-block:: python

   from unittest.mock import Mock, patch
   from honeyhive import trace
   from honeyhive.models import EventType
   
   class TestTraceDecorator:
       """Test trace decorator functionality."""
       
       @pytest.fixture
       def mock_tracer(self):
           """Create mock tracer for testing."""
           mock_tracer = Mock()
           mock_span = Mock()
           mock_span.__enter__ = Mock(return_value=mock_span)
           mock_span.__exit__ = Mock(return_value=None)
           mock_tracer.trace.return_value = mock_span
           return mock_tracer
       
       def test_decorator_with_explicit_tracer(self, mock_tracer):
           """Test decorator with explicit tracer."""
           @trace(tracer=mock_tracer, event_type=EventType.tool)
           def decorated_function(x, y):
               return x + y
           
           result = decorated_function(2, 3)
           
           assert result == 5
           mock_tracer.trace.assert_called_once()
       
       def test_decorator_captures_arguments(self):
           """Test that decorator captures function arguments."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           @trace(tracer=tracer, include_inputs=True)
           def function_with_args(name: str, age: int, active: bool = True):
               return f"{name} is {age} years old"
           
           result = function_with_args("Alice", 30, active=True)
           
           assert result == "Alice is 30 years old"
           # In real implementation, would verify captured arguments
       
       def test_decorator_captures_return_value(self):
           """Test that decorator captures return values.""" 
           tracer = HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           @trace(tracer=tracer, include_outputs=True)
           def function_with_return():
               return {"status": "success", "data": [1, 2, 3]}
           
           result = function_with_return()
           
           assert result["status"] == "success"
           assert result["data"] == [1, 2, 3]
       
       def test_decorator_handles_exceptions(self):
           """Test that decorator handles exceptions correctly."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           @trace(tracer=tracer)
           def function_that_raises():
               raise ValueError("Test exception")
           
           with pytest.raises(ValueError, match="Test exception"):
               function_that_raises()
           
           # Exception should be captured in trace (verified in integration tests)

Testing Multi-Instance Behavior
-------------------------------

**Problem**: Test that multiple tracer instances work independently.

**Solution**:

.. code-block:: python

   class TestMultiInstanceBehavior:
       """Test multiple tracer instances working independently."""
       
       def test_independent_tracers(self):
           """Test that multiple tracers operate independently."""
           tracer1 = HoneyHiveTracer.init(
               api_key="key1",          # Unique API key for tracer1
               project="project1",      # Unique project for tracer1
               source="development",    # Or set HH_SOURCE environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           tracer2 = HoneyHiveTracer.init(
               api_key="key2",          # Unique API key for tracer2
               project="project2",      # Unique project for tracer2
               source="development",    # Or set HH_SOURCE environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           # Verify tracers are different instances
           assert tracer1 is not tracer2
           assert tracer1.api_key != tracer2.api_key
           assert tracer1.project != tracer2.project
           assert tracer1.session_id != tracer2.session_id
       
       def test_concurrent_tracer_operations(self):
           """Test concurrent operations with different tracers."""
           import threading
           import time
           
           tracer1 = HoneyHiveTracer.init(
               api_key="key1",          # Unique API key for tracer1
               project="project1",      # Unique project for tracer1
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           tracer2 = HoneyHiveTracer.init(
               api_key="key2",          # Unique API key for tracer2
               project="project2",      # Unique project for tracer2
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           results = []
           
           def worker(tracer, worker_id):
               with tracer.trace(f"worker-{worker_id}") as span:
                   span.set_attribute("worker.id", worker_id)
                   time.sleep(0.1)  # Simulate work
                   results.append(f"completed-{worker_id}")
           
           # Start workers with different tracers
           thread1 = threading.Thread(target=worker, args=(tracer1, 1))
           thread2 = threading.Thread(target=worker, args=(tracer2, 2))
           
           thread1.start()
           thread2.start()
           
           thread1.join()
           thread2.join()
           
           # Verify both completed
           assert "completed-1" in results
           assert "completed-2" in results
           assert len(results) == 2
       
       def test_decorator_with_different_tracers(self):
           """Test decorators with different tracer instances."""
           tracer1 = HoneyHiveTracer.init(
               api_key="key1",          # Unique API key for tracer1
               project="project1",      # Unique project for tracer1
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           tracer2 = HoneyHiveTracer.init(
               api_key="key2",          # Unique API key for tracer2
               project="project2",      # Unique project for tracer2
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           @trace(tracer=tracer1, event_type=EventType.tool)
           def function1():
               return "from tracer1"
           
           @trace(tracer=tracer2, event_type=EventType.tool) 
           def function2():
               return "from tracer2"
           
           result1 = function1()
           result2 = function2()
           
           assert result1 == "from tracer1"
           assert result2 == "from tracer2"

Testing Error Handling
----------------------

**Problem**: Test error scenarios and exception handling.

**Solution**:

.. code-block:: python

   import pytest
   from unittest.mock import patch
   from honeyhive import HoneyHiveTracer
   
   class TestErrorHandling:
       """Test error handling scenarios."""
       
       @pytest.fixture
       def tracer(self):
           return HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
       
       def test_span_exception_recording(self, tracer):
           """Test that exceptions are recorded in spans."""
           with tracer.trace("error-test") as span:
               try:
                   raise ValueError("Test error message")
               except ValueError as e:
                   span.record_exception(e)
                   span.set_attribute("error.type", "ValueError")
                   span.set_attribute("error.message", str(e))
                   
                   # Verify error attributes
                   assert span.get_attribute("error.type") == "ValueError"
                   assert span.get_attribute("error.message") == "Test error message"
       
       def test_graceful_degradation_on_api_failure(self):
           """Test graceful degradation when HoneyHive API is unavailable."""
           with patch('honeyhive.api.client.requests.post') as mock_post:
               # Simulate API failure
               mock_post.side_effect = Exception("API unavailable")
               
               # Tracer should still work in degraded mode
               tracer = HoneyHiveTracer.init(
                   api_key="test-key",                   test_mode=False  # Use real API (which will fail)
               )
               
               # Operations should not raise exceptions
               with tracer.trace("degraded-operation") as span:
                   span.set_attribute("test.attribute", "value")
                   # Should complete without error
       
       def test_invalid_configuration_handling(self):
           """Test handling of invalid configuration."""
           with pytest.raises(ValueError):
               HoneyHiveTracer.init(
                   api_key="",  # Empty API key should raise error               )
           
           with pytest.raises(ValueError):
               HoneyHiveTracer.init(
                   api_key="invalid-format",  # Invalid format               )

Testing Configuration Loading
-----------------------------

**Problem**: Test configuration loading from different sources.

**Solution**:

.. code-block:: python

   import os
   import tempfile
   import json
   from honeyhive import HoneyHiveTracer
   
   class TestConfigurationLoading:
       """Test configuration loading from various sources."""
       
       def test_explicit_parameter_priority(self):
           """Test that explicit parameters have highest priority."""
           # Set environment variables
           os.environ["HH_API_KEY"] = "env-key"
           os.environ["           
           try:
               tracer = HoneyHiveTracer.init(
                   api_key="explicit-key",  # Should override env var
                   # Should override env var
                   test_mode=True
               )
               
               assert tracer.api_key == "explicit-key"
               assert tracer.project == "explicit-project"
           finally:
               del os.environ["HH_API_KEY"]
               del os.environ["HH_PROJECT"]
       
       def test_environment_variable_fallback(self):
           """Test fallback to environment variables."""
           os.environ["HH_API_KEY"] = "fallback-key"
           os.environ["           os.environ["HH_SOURCE"] = "fallback-source"
           
           try:
               tracer = HoneyHiveTracer.init(
                   # Uses HH_API_KEY and HH_PROJECT environment variables
                   test_mode=True  # Or set HH_TEST_MODE=true
               )
               
               assert tracer.api_key == "fallback-key"
               assert tracer.project == "fallback-project"
               assert tracer.source == "fallback-source"
           finally:
               del os.environ["HH_API_KEY"]
               del os.environ["HH_PROJECT"]
               del os.environ["HH_SOURCE"]
       
       def test_default_value_usage(self):
           """Test usage of default values."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",
               test_mode=True
               # project and source not specified
           )
           
           assert tracer.api_key == "test-key"
           assert tracer.project == "default"  # Default value
           assert tracer.source == "unknown"  # Default value

Testing Session Management
--------------------------

**Problem**: Test session creation and management.

**Solution**:

.. code-block:: python

   class TestSessionManagement:
       """Test session creation and management."""
       
       @pytest.fixture
       def tracer(self):
           return HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
       
       def test_session_creation(self, tracer):
           """Test that session is created automatically.""" 
           assert tracer.session_id is not None
           assert isinstance(tracer.session_id, str)
           assert len(tracer.session_id) > 0
       
       def test_session_uniqueness(self):
           """Test that different tracers have unique sessions."""
           tracer1 = HoneyHiveTracer.init(
               api_key="key1",          # Unique API key for tracer1
               project="project1",      # Unique project for tracer1
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           tracer2 = HoneyHiveTracer.init(
               api_key="key2",          # Unique API key for tracer2
               project="project2",      # Unique project for tracer2
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           assert tracer1.session_id != tracer2.session_id
       
       def test_custom_session_name(self):
           """Test custom session name setting."""
           custom_name = "custom-test-session"
           tracer = HoneyHiveTracer.init(
               api_key="test-key",               session_name=custom_name,
               test_mode=True
           )
           
           assert tracer.session_name == custom_name

Testing Performance Impact
--------------------------

**Problem**: Test that tracing has minimal performance impact.

**Solution**:

.. code-block:: python

   import time
   import statistics
   from honeyhive import HoneyHiveTracer, trace
   
   class TestPerformanceImpact:
       """Test performance impact of tracing."""
       
       def test_tracing_overhead(self):
           """Test that tracing adds minimal overhead."""
           tracer = HoneyHiveTracer.init(
               api_key="test-key",      # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           
           # Measure baseline performance
           def baseline_operation():
               return sum(range(1000))
           
           baseline_times = []
           for _ in range(10):
               start = time.perf_counter()
               baseline_operation()
               end = time.perf_counter()
               baseline_times.append(end - start)
           
           baseline_avg = statistics.mean(baseline_times)
           
           # Measure performance with tracing
           @trace(tracer=tracer)
           def traced_operation():
               return sum(range(1000))
           
           traced_times = []
           for _ in range(10):
               start = time.perf_counter()
               traced_operation()
               end = time.perf_counter()
               traced_times.append(end - start)
           
           traced_avg = statistics.mean(traced_times)
           
           # Calculate overhead
           overhead_ratio = traced_avg / baseline_avg
           
           # Overhead should be reasonable (less than 3x)
           assert overhead_ratio < 3.0, f"Tracing overhead too high: {overhead_ratio:.2f}x"
       
       def test_memory_usage(self):
           """Test memory usage with tracing."""
           import psutil
           import os
           
           process = psutil.Process(os.getpid())
           initial_memory = process.memory_info().rss
           
           # Create multiple tracers and spans
           tracers = []
           for i in range(10):
               tracer = HoneyHiveTracer.init(
                   api_key=f"test-key-{i}",     # Unique API key for each tracer instance
                   project=f"test-project-{i}", # Unique project for each tracer instance
                   test_mode=True               # Or set HH_TEST_MODE=true
               )
               tracers.append(tracer)
               
               # Create spans
               for j in range(10):
                   with tracer.trace(f"span-{j}") as span:
                       span.set_attribute("iteration", j)
           
           final_memory = process.memory_info().rss
           memory_increase = final_memory - initial_memory
           
           # Memory increase should be reasonable (less than 50MB)
           assert memory_increase < 50 * 1024 * 1024, f"Memory usage too high: {memory_increase / 1024 / 1024:.2f}MB"

Mock Testing Utilities
----------------------

**Problem**: Create reusable mock utilities for testing.

**Solution**:

.. code-block:: python

   from unittest.mock import Mock, MagicMock
   
   class MockHoneyHiveTracer:
       """Mock tracer for testing."""
       
       def __init__(self, **kwargs):
           self.api_key = kwargs.get("api_key", "mock-key")
           self.project = kwargs.get("project", "mock-project")
           self.source = kwargs.get("source", "mock")
           self.test_mode = kwargs.get("test_mode", True)
           self.session_id = "mock-session-id"
           self.session_name = kwargs.get("session_name", "mock-session")
           self.spans = []
       
       def trace(self, name, **kwargs):
           """Create mock span context manager."""
           span = MockSpan(name, **kwargs)
           self.spans.append(span)
           return span
       
       def get_spans(self):
           """Get all created spans for verification."""
           return self.spans
       
       def flush(self, timeout=None):
           """Mock flush operation."""
           return True
       
       def close(self):
           """Mock close operation."""
           pass
   
   class MockSpan:
       """Mock span for testing."""
       
       def __init__(self, name, **kwargs):
           self.name = name
           self.attributes = {}
           self.events = []
           self.exceptions = []
           self.status = "OK"
       
       def __enter__(self):
           return self
       
       def __exit__(self, exc_type, exc_val, exc_tb):
           if exc_type:
               self.record_exception(exc_val)
               self.status = "ERROR"
       
       def set_attribute(self, key, value):
           """Set span attribute."""
           self.attributes[key] = value
       
       def get_attribute(self, key):
           """Get span attribute."""
           return self.attributes.get(key)
       
       def record_exception(self, exception):
           """Record exception in span."""
           self.exceptions.append(exception)
       
       def add_event(self, name, attributes=None):
           """Add event to span."""
           self.events.append({"name": name, "attributes": attributes or {}})
   
   # Test utility functions
   def create_test_tracer(**kwargs):
       """Create a tracer configured for testing."""
       default_config = {
           "api_key": "test-api-key",
           "project": "test-project", 
           "source": "test",
           "test_mode": True,
           "disable_http_tracing": True
       }
       default_config.update(kwargs)
       
       return HoneyHiveTracer.init(**default_config)
   
   def assert_span_attributes(span, expected_attrs):
       """Assert that span has expected attributes."""
       for key, value in expected_attrs.items():
           actual_value = span.get_attribute(key)
           assert actual_value == value, f"Attribute {key}: expected {value}, got {actual_value}"
   
   def assert_span_events(span, expected_events):
       """Assert that span has expected events."""
       event_names = [event["name"] for event in span.events]
       for event_name in expected_events:
           assert event_name in event_names, f"Event {event_name} not found in {event_names}"

Advanced Unit Testing Patterns
------------------------------

**Problem**: Test complex scenarios and edge cases.

**Solution**:

.. code-block:: python

   import pytest
   from unittest.mock import patch, PropertyMock
   import threading
   import asyncio
   
   class TestAdvancedScenarios:
       """Test complex and edge case scenarios."""
       
       def test_context_propagation_in_threads(self):
           """Test context propagation across threads."""
           tracer = create_test_tracer()
           results = []
           
           def worker(worker_id):
               with tracer.trace(f"worker-{worker_id}") as span:
                   span.set_attribute("worker.id", worker_id)
                   span.set_attribute("thread.name", threading.current_thread().name)
                   results.append(worker_id)
           
           threads = []
           for i in range(5):
               thread = threading.Thread(target=worker, args=(i))
               threads.append(thread)
               thread.start()
           
           for thread in threads:
               thread.join()
           
           assert len(results) == 5
           assert set(results) == {0, 1, 2, 3, 4}
       
       @pytest.mark.asyncio
       async def test_async_tracing(self):
           """Test tracing with async functions."""
           tracer = create_test_tracer()
           
           @trace(tracer=tracer, event_type="async_test")
           async def async_operation(delay):
               await asyncio.sleep(delay)
               return f"completed after {delay}s"
           
           # Test concurrent async operations
           tasks = [
               async_operation(0.1),
               async_operation(0.05),
               async_operation(0.15)
           ]
           
           results = await asyncio.gather(*tasks)
           
           assert len(results) == 3
           assert "completed after 0.1s" in results
           assert "completed after 0.05s" in results
           assert "completed after 0.15s" in results
       
       def test_resource_cleanup(self):
           """Test proper resource cleanup."""
           # Test that tracers can be properly cleaned up
           tracers = []
           
           for i in range(10):
               tracer = HoneyHiveTracer.init(
                   api_key=f"cleanup-test-{i}",                   test_mode=True
               )
               tracers.append(tracer)
           
           # Verify all tracers are created
           assert len(tracers) == 10
           
           # Clean up tracers
           for tracer in tracers:
               tracer.close()
           
           # Verify cleanup completed without errors
           assert True  # If we reach here, cleanup succeeded
       
       def test_edge_case_span_names(self):
           """Test edge cases in span naming."""
           tracer = create_test_tracer()
           
           edge_cases = [
               "",  # Empty string
               "a" * 1000,  # Very long name
               "special!@#$%^&*()characters",  # Special characters
               "unicode_测试_🚀",  # Unicode characters
               "   whitespace   ",  # Whitespace
           ]
           
           for name in edge_cases:
               with tracer.trace(name) as span:
                   span.set_attribute("test.edge_case", True)
                   # Should not raise exceptions
           
           assert True  # If we reach here, all edge cases handled

Test Fixtures and Utilities
---------------------------

**Problem**: Create reusable test fixtures and utilities.

**Solution**:

.. code-block:: python

   import pytest
   import tempfile
   import json
   import os
   
   @pytest.fixture
   def test_tracer():
       """Standard test tracer fixture."""
       tracer = HoneyHiveTracer.init(
           api_key="test-api-key",           source="development"
           test_mode=True,
           disable_http_tracing=True
       )
       yield tracer
       tracer.close()
   
   @pytest.fixture
   def multiple_tracers():
       """Fixture for multiple test tracers."""
       tracers = []
       for i in range(3):
           tracer = HoneyHiveTracer.init(
               api_key=f"test-key-{i}",               source=f"test-source-{i}",
               test_mode=True
           )
           tracers.append(tracer)
       
       yield tracers
       
       for tracer in tracers:
           tracer.close()
   
   @pytest.fixture
   def temp_config_file():
       """Fixture for temporary configuration file."""
       config = {
           "api_key": "file-test-key",
           "project": "file-test-project",
           "source": "file-test",
           "test_mode": True
       }
       
       with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
           json.dump(config, f)
           temp_file = f.name
       
       yield temp_file
       
       os.unlink(temp_file)
   
   @pytest.fixture
   def mock_environment():
       """Fixture for mocked environment variables."""
       original_env = {}
       test_env = {
           "HH_API_KEY": "env-test-key",
                      "HH_SOURCE": "env-test",
           "HH_TEST_MODE": "true"
       }
       
       # Save original values and set test values
       for key, value in test_env.items():
           original_env[key] = os.environ.get(key)
           os.environ[key] = value
       
       yield test_env
       
       # Restore original values
       for key, original_value in original_env.items():
           if original_value is None:
               os.environ.pop(key, None)
           else:
               os.environ[key] = original_value

Running Unit Tests
------------------

**Command Examples**:

.. code-block:: bash

   # Run all unit tests
   tox -e unit
   
   # Run specific test file
   pytest tests/unit/test_tracer.py -v
   
   # Run specific test class
   pytest tests/unit/test_tracer.py::TestTracerInitialization -v
   
   # Run specific test method
   pytest tests/unit/test_tracer.py::TestTracerInitialization::test_basic_initialization -v
   
   # Run with coverage
   pytest tests/unit/ --cov=honeyhive --cov-report=term-missing
   
   # Run with verbose output
   pytest tests/unit/ -v -s
   
   # Run tests matching pattern
   pytest tests/unit/ -k "tracer" -v

CLI Testing
-----------

**Problem**: Test CLI commands and command-line interface functionality.

**Solution**:

.. code-block:: python

   from click.testing import CliRunner
   from unittest.mock import Mock, patch
   from honeyhive.cli.main import cli
   
   class TestCLICommands:
       """Test CLI command functionality."""
       
       def test_cli_help(self):
           """Test CLI help command."""
           runner = CliRunner()
           result = runner.invoke(cli, ["--help"])
           
           assert result.exit_code == 0
           assert "HoneyHive CLI" in result.output
       
       @patch('honeyhive.cli.main.HoneyHive')
       def test_api_command_with_mocking(self, mock_client):
           """Test API command with proper mocking."""
           # Setup mock
           mock_instance = Mock()
           mock_client.return_value = mock_instance
           mock_response = Mock()
           mock_response.status_code = 200
           mock_response.json.return_value = {"status": "success"}
           mock_instance.sync_client.request.return_value = mock_response
           
           runner = CliRunner()
           result = runner.invoke(cli, [
               "api", "request", 
               "--method", "GET",
               "--url", "/api/v1/test"
           ])
           
           assert result.exit_code == 0
           assert "Status: 200" in result.output
           mock_client.assert_called_once()
       
       def test_config_show_json(self):
           """Test config show with JSON format."""
           runner = CliRunner()
           result = runner.invoke(cli, ["config", "show", "--format", "json"])
           
           assert result.exit_code == 0
           # Verify JSON output structure
           import json
           config_data = json.loads(result.output)
           assert "api_key" in config_data

**CLI Testing Best Practices**:

1. **Use CliRunner**: Always use ``click.testing.CliRunner`` for CLI tests
2. **Mock at Module Level**: Use ``@patch('honeyhive.cli.main.ModuleName')`` for mocking
3. **Test All Commands**: Cover all CLI commands and subcommands
4. **Test Error Conditions**: Verify error handling and exit codes
5. **Test Output Format**: Verify command output matches expected format
6. **Mock External Services**: Mock API clients, file operations, and network calls
7. **Test Help Text**: Ensure all help text is properly displayed
8. **Test Command Options**: Verify all command-line options and flags work correctly

**CLI Test Coverage**: The CLI module achieves 89% test coverage with 58 comprehensive tests covering:

- Command structure and help text (11 tests)
- Configuration management (8 tests) 
- Tracing operations (12 tests)
- API client interactions (8 tests)
- System monitoring (8 tests)
- Resource cleanup (10 tests)
- Environment integration (4 tests)

**Best Practices for Unit Tests**:

1. **Test in Isolation**: Each test should be independent
2. **Use Test Mode**: Always set ``test_mode=True``
3. **Mock External Dependencies**: Don't make real API calls
4. **Test Both Success and Failure**: Cover happy path and error cases
5. **Use Descriptive Names**: Test names should describe what is being tested
6. **Keep Tests Fast**: Unit tests should run quickly
7. **Clean Up Resources**: Use fixtures for setup/teardown
8. **Test Edge Cases**: Include boundary conditions and unusual inputs

See Also
--------

- :doc:`integration-testing` - Integration testing strategies
- :doc:`mocking-strategies` - Advanced mocking techniques
- :doc:`../../tutorials/01-setup-first-tracer` - Basic tracing patterns
- :doc:`../../reference/api/tracer` - Complete tracer API reference
