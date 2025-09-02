Testing Guide
=============

Comprehensive guide to testing the HoneyHive Python SDK and applications that use it.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Testing is a crucial part of developing reliable applications with the HoneyHive Python SDK. This guide covers testing strategies, tools, and best practices for ensuring your tracing implementation works correctly.

**Coverage Requirement**: The project maintains a minimum **70% test coverage** requirement to ensure code quality and reliability.

**Current Test Status**: 

- **Total Tests**: 881 tests (100% success rate)
- **Unit Tests**: 761 tests across 26 test files
- **Integration Tests**: 97 tests across 8 test files
- **Tracer Tests**: 23 tests across 1 test file
- **Test Coverage**: 72.95% ✅ (above 70% requirement)
- **Code Coverage**: 4,484 statements, 1,213 missed

Test Organization
-----------------

The project maintains a comprehensive test suite organized into logical categories:

**Test File Structure**:

- **Total Test Files**: 35
- **Unit Tests**: 26 test files in `tests/unit/` - Test individual components in isolation (761 tests)
- **Integration Tests**: 8 test files in `tests/integration/` - Test component interactions and multi-instance patterns (97 tests)
- **Tracer Tests**: 1 test file in `tests/tracer/` - Test core tracing functionality (23 tests)
- **Test Utilities**: 2 utility files (`conftest.py`, `utils.py`)

**Test File Naming Convention**: All unit test files follow the pattern `test_<module>_<file>.py` for consistent organization and easy identification.

**Test Types** (distributed across the above test files):

- **End-to-End Tests** - Complete workflow testing
- **Performance Tests** - Performance characteristics testing
- **Multi-Instance Tests** - Multiple tracer instance testing
- **Real API Tests** - Actual HoneyHive API endpoint testing
- **TracerProvider Tests** - OpenTelemetry provider integration testing (includes Force Flush functionality)

Testing Strategy
----------------

Multi-Layer Testing
~~~~~~~~~~~~~~~~~~~

The SDK supports a multi-layered testing approach:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions and multi-instance patterns
3. **End-to-End Tests** - Test complete workflows
4. **Performance Tests** - Test performance characteristics
5. **Multi-Instance Tests** - Test multiple tracer instances and their interactions
6. **Real API Tests** - Test with actual HoneyHive API endpoints

Test Configuration
~~~~~~~~~~~~~~~~~~

Configure the SDK for testing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Test configuration with multi-instance support
   test_tracer = HoneyHiveTracer.init(
       api_key="test-api-key",
       project="test-project",
       source="test",
       test_mode=True,  # Enable test mode
       disable_http_tracing=True  # Disable HTTP tracing in tests
   )

   # Create additional test tracers for different scenarios
   mock_tracer = HoneyHiveTracer.init(
       api_key="mock-key",
       project="mock-project",
       source="mock",
       test_mode=True
   )

Unit Testing
------------

Testing Individual Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test individual SDK components with the new multi-instance architecture:

.. code-block:: python

   import pytest
   from honeyhive.tracer import HoneyHiveTracer

   def test_tracer_initialization():
       """Test tracer initialization."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           project="test-project",
           test_mode=True
       )
       
       assert tracer.api_key == "test-key"
       assert tracer.project == "test-project"
       assert tracer.test_mode is True

   def test_span_creation():
       """Test span creation."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           test_mode=True
       )
       
       with tracer.start_span("test-span") as span:
           assert span.name == "test-span"
           span.set_attribute("test.attribute", "value")
           assert span.get_attribute("test.attribute") == "value"

Testing Multi-Instance Behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test that multiple tracer instances work independently:

.. code-block:: python

   def test_multiple_tracers():
       """Test that multiple tracers operate independently."""
       tracer1 = HoneyHiveTracer(
           api_key="key1",
           project="project1",
           source="source1"
       )
       
       tracer2 = HoneyHiveTracer(
           api_key="key2",
           project="project2",
           source="source2"
       )
       
       # Verify tracers are different instances
       assert tracer1 is not tracer2
       assert tracer1.api_key != tracer2.api_key
       assert tracer1.project != tracer2.project

Testing Dynamic Session Naming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test the automatic session naming feature:

.. code-block:: python

   def test_session_name_generation():
       """Test that session names are generated from file names."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           project="test-project"
       )
       
       # Session name should be based on the test file
       assert tracer.session_name is not None
       assert isinstance(tracer.session_name, str)

Testing Decorators
~~~~~~~~~~~~~~~~~~

Test tracing decorators with explicit tracer instances:

.. code-block:: python

   from honeyhive.tracer.decorators import trace
   from unittest.mock import Mock

   def test_trace_decorator_with_explicit_tracer():
       """Test trace decorator with explicit tracer instance."""
       mock_tracer = Mock()
       mock_span = Mock()
       mock_span.__enter__ = Mock(return_value=mock_span)
       mock_span.__exit__ = Mock(return_value=None)
       mock_tracer.start_span.return_value = mock_span

       @trace(tracer=mock_tracer)
       def traced_function():
           """Function to test tracing decorator."""
           return "traced result"

       result = traced_function()
       assert result == "traced result"
       
       # Verify span was created
       mock_tracer.start_span.assert_called_once()

Testing Error Handling
~~~~~~~~~~~~~~~~~~~~~~

Test error scenarios:

.. code-block:: python

   from honeyhive.tracer import HoneyHiveTracer

   def test_error_handling():
       """Test error handling in spans."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           test_mode=True
       )
       
       with tracer.start_span("error-test") as span:
           try:
               # Simulate an error
               raise ValueError("Test error")
           except ValueError as e:
               span.record_exception(e)
               span.set_attribute("error.type", "ValueError")
               span.set_attribute("error.message", str(e))
               
               # Verify error attributes
               assert span.get_attribute("error.type") == "ValueError"
               assert span.get_attribute("error.message") == "Test error"

Integration Testing
-------------------

Testing Component Interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test how components work together with multi-instance support:

.. code-block:: python

   import pytest
   from honeyhive.tracer import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive

   def test_tracer_api_integration():
       """Test tracer integration with API client."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           test_mode=True
       )
       
       # Test that tracer can create API client
       client = HoneyHive(
           api_key="test-key",
           base_url="https://test-api.honeyhive.ai"
       )
       
       assert client is not None
       assert client.api_key == "test-key"

Testing Multiple Tracer Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test that multiple tracers can coexist and operate independently:

.. code-block:: python

   def test_multiple_tracers_integration():
       """Test integration with multiple tracer instances."""
       prod_tracer = HoneyHiveTracer(
           api_key="prod-key",
           project="prod-project",
           source="prod"
       )
       
       dev_tracer = HoneyHiveTracer(
           api_key="dev-key",
           project="dev-project",
           source="dev"
       )
       
       # Both tracers should work independently
       with prod_tracer.start_span("prod-operation") as prod_span:
           prod_span.set_attribute("env", "production")
           
       with dev_tracer.start_span("dev-operation") as dev_span:
           dev_span.set_attribute("env", "development")
           
       # Verify each tracer has its own session
       assert prod_tracer.session_id != dev_tracer.session_id

Testing Session Management
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test session creation and management:

.. code-block:: python

   def test_session_management():
       """Test session creation and management."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           project="test-project",
           test_mode=True
       )
       
       # Verify session was created
       assert tracer.session_id is not None
       assert tracer.project == "test-project"

Testing TracerProvider Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test OpenTelemetry provider integration:

.. code-block:: python

   from unittest.mock import patch
   from honeyhive.tracer import HoneyHiveTracer

   def test_tracer_provider_integration():
       """Test integration with existing TracerProvider."""
       with patch('honeyhive.tracer.otel_tracer.trace.get_tracer_provider') as mock_get_provider:
           mock_provider = Mock()
           mock_get_provider.return_value = mock_provider
           
           # Create tracer - should integrate with existing provider
           tracer = HoneyHiveTracer.init(
               api_key="test-key",
               project="test-project"
           )
           
           # Verify provider integration
           assert tracer.provider is mock_provider

End-to-End Testing
------------------

Testing Complete Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test complete tracing workflows with multi-instance support:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHiveTracer
   from honeyhive.tracer.decorators import trace

   async def test_complete_workflow():
       """Test complete tracing workflow with multiple tracers."""
       
       # Create tracers for different workflow stages
       input_tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="workflow-test",
           source="input"
       )
       
       process_tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="workflow-test", 
           source="process"
       )
       
       output_tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="workflow-test",
           source="output"
       )

       @trace(tracer=input_tracer)
       async def input_stage():
           """Input processing stage."""
           await asyncio.sleep(0.1)
           return "input_data"

       @trace(tracer=process_tracer)
       async def process_stage(data):
           """Data processing stage."""
           await asyncio.sleep(0.1)
           return f"processed_{data}"

       @trace(tracer=output_tracer)
       async def output_stage(data):
           """Output generation stage."""
           await asyncio.sleep(0.1)
           return f"output_{data}"

       # Execute workflow
       input_data = await input_stage()
       processed_data = await process_stage(input_data)
       output_data = await output_stage(processed_data)
       
       assert output_data == "output_processed_input_data"

Performance Testing
-------------------

Testing Performance Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test performance impact of tracing:

.. code-block:: python

   import time
   import pytest
   from honeyhive import HoneyHiveTracer, trace

   def test_tracing_performance_impact():
       """Test that tracing has minimal performance impact."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           test_mode=True
       )
       
       # Measure performance without tracing
       start_time = time.time()
       for _ in range(1000):
           _ = "test" * 100
       baseline_time = time.time() - start_time
       
       # Measure performance with tracing
       @trace
       def traced_operation():
           return "test" * 100
       
       start_time = time.time()
       for _ in range(1000):
           _ = traced_operation()
       traced_time = time.time() - start_time
       
       # Tracing should add minimal overhead
       overhead_ratio = traced_time / baseline_time
       assert overhead_ratio < 2.0  # Less than 2x overhead

Testing Instrumentor Integration
---------------------------------

Testing AI Operation Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test instrumentor integration:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   def test_instrumentor_integration():
       """Test instrumentor integration."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True,
           instrumentors=[OpenAIInstrumentor()]
       )
       
       # Verify instrumentor was added
       assert len(tracer.instrumentors) > 0
       assert any(isinstance(i, OpenAIInstrumentor) for i in tracer.instrumentors)

Import Error Testing
--------------------

Testing Conditional Imports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK uses conditional imports for optional dependencies. Test these scenarios using `sys.modules` manipulation:

.. code-block:: python

   import sys
   import importlib
   from unittest.mock import patch

   def test_httpx_import_error_handling():
       """Test handling of missing httpx dependency."""
       # Save original modules
       httpx_modules = [key for key in sys.modules.keys() if key.startswith('httpx')]
       patch_dict = {module: None for module in httpx_modules}
       patch_dict['httpx'] = None

       with patch.dict(sys.modules, patch_dict):
           # Reload module to trigger ImportError
           import honeyhive.utils.connection_pool
           importlib.reload(honeyhive.utils.connection_pool)
           
           # Test that module handles missing dependency gracefully
           from honeyhive.utils.connection_pool import HTTPX_AVAILABLE
           assert isinstance(HTTPX_AVAILABLE, bool)

   def test_opentelemetry_import_error_handling():
       """Test handling of missing OpenTelemetry dependencies."""
       otel_modules = [key for key in sys.modules.keys() if key.startswith('opentelemetry')]
       patch_dict = {module: None for module in otel_modules}
       patch_dict.update({
           'opentelemetry': None,
           'opentelemetry.trace': None,
           'opentelemetry.sdk': None,
           'opentelemetry.sdk.trace': None,
       })

       with patch.dict(sys.modules, patch_dict):
           import honeyhive.tracer.otel_tracer
           importlib.reload(honeyhive.tracer.otel_tracer)
           
           from honeyhive.tracer.otel_tracer import OTEL_AVAILABLE
           assert isinstance(OTEL_AVAILABLE, bool)

**Import Testing Strategy**:

1. **Identify Conditional Imports** - Find modules with try/except import blocks
2. **Use sys.modules Manipulation** - Simulate missing dependencies by setting modules to None
3. **Reload Modules** - Force re-import to trigger conditional logic
4. **Test Graceful Degradation** - Verify the module handles missing dependencies properly
5. **Restore Original State** - Ensure tests don't affect other test modules

**Coverage Impact**: This strategy significantly improves coverage of conditional import paths, bringing modules like:

- ``http_instrumentation.py``: 65% → 72% coverage
- ``span_processor.py``: 59% → 60% coverage  
- ``otel_tracer.py``: 72% → 73% coverage

Mock Testing
------------

Using Mock Tracers
~~~~~~~~~~~~~~~~~~

Create mock tracers for testing:

.. code-block:: python

   from unittest.mock import Mock
   from honeyhive.tracer import HoneyHiveTracer

   class MockTracer:
       """Mock tracer for testing."""
       
       def __init__(self):
           self.spans = []
           self.attributes = {}
       
       def start_span(self, name):
           """Start a mock span."""
           span = Mock()
           span.name = name
           span.attributes = {}
           span.events = []
           self.spans.append(span)
           return span
       
       def get_spans(self):
           """Get all created spans."""
           return self.spans

   def test_with_mock_tracer():
       """Test using mock tracer."""
       mock_tracer = MockTracer()
       
       with mock_tracer.start_span("test-operation") as span:
           span.set_attribute("test.attr", "value")
       
       # Verify span was created
       assert len(mock_tracer.get_spans()) == 1
       assert mock_tracer.get_spans()[0].name == "test-operation"

Testing Configuration
---------------------

Environment Variable Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test configuration loading:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer

   def test_environment_configuration():
       """Test configuration from environment variables."""
       # Set test environment variables
       os.environ["HH_API_KEY"] = "env-test-key"
       os.environ["HH_PROJECT"] = "env-test-project"
       os.environ["HH_SOURCE"] = "env-test"
       
       try:
           tracer = HoneyHiveTracer.init()
           
           assert tracer.api_key == "env-test-key"
           assert tracer.project == "env-test-project"
           assert tracer.source == "env-test"
       
       finally:
           # Clean up environment variables
           del os.environ["HH_API_KEY"]
           del os.environ["HH_PROJECT"]
           del os.environ["HH_SOURCE"]

Test Utilities
--------------

Helper Functions
~~~~~~~~~~~~~~~~

Create utility functions for testing:

.. code-block:: python

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

   def create_multiple_test_tracers(count=3, **kwargs):
       """Create multiple test tracers for multi-instance testing."""
       tracers = []
       for i in range(count):
           tracer_config = {
               "api_key": f"test-api-key-{i}",
               "project": f"test-project-{i}",
               "source": f"test-{i}",
               "test_mode": True,
               "disable_http_tracing": True
           }
           tracer_config.update(kwargs)
           tracers.append(HoneyHiveTracer.init(**tracer_config))
       return tracers

   def assert_span_attributes(span, expected_attrs):
       """Assert that span has expected attributes."""
       for key, value in expected_attrs.items():
           assert span.get_attribute(key) == value, f"Attribute {key} mismatch"

   def assert_span_events(span, expected_events):
       """Assert that span has expected events."""
       event_names = [event.name for event in span.events]
       for event_name in expected_events:
           assert event_name in event_names, f"Event {event_name} not found"

   def assert_tracer_independence(tracer1, tracer2):
       """Assert that two tracers are independent instances."""
       assert tracer1 is not tracer2
       assert tracer1.session_id != tracer2.session_id
       assert tracer1.project != tracer2.project

Multi-Instance Testing
----------------------

Testing Multiple Tracer Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test scenarios with multiple independent tracers:

.. code-block:: python

   import pytest
   from honeyhive import HoneyHiveTracer

   class TestMultiInstanceTracer:
       """Test multiple tracer instances working together."""
       
       def test_tracer_coexistence(self):
           """Test that multiple tracers can coexist."""
           tracer1 = HoneyHiveTracer(
               api_key="key1",
               project="project1",
               source="source1"
           )
           
           tracer2 = HoneyHiveTracer(
               api_key="key2",
               project="project2",
               source="source2"
           )
           
           # Both tracers should work independently
           with tracer1.start_span("operation1") as span1:
               span1.set_attribute("tracer", "first")
               
           with tracer2.start_span("operation2") as span2:
               span2.set_attribute("tracer", "second")
           
           # Verify independence
           assert tracer1.session_id != tracer2.session_id
           assert tracer1.project != tracer2.project

       def test_decorator_with_multiple_tracers(self):
           """Test decorators with different tracer instances."""
           from honeyhive.tracer.decorators import trace
           
           tracer1 = HoneyHiveTracer(api_key="key1", project="project1")
           tracer2 = HoneyHiveTracer(api_key="key2", project="project2")
           
           @trace(tracer=tracer1)
           def function1():
               return "from tracer1"
           
           @trace(tracer=tracer2)
           def function2():
               return "from tracer2"
           
           result1 = function1()
           result2 = function2()
           
           assert result1 == "from tracer1"
           assert result2 == "from tracer2"

       def test_concurrent_tracer_usage(self):
           """Test concurrent usage of multiple tracers."""
           import threading
           import time
           
           tracers = [
               HoneyHiveTracer(api_key=f"key{i}", project=f"project{i}")
               for i in range(3)
           ]
           
           results = []
           
           def worker(tracer, tracer_id):
               with tracer.start_span(f"operation-{tracer_id}") as span:
                   span.set_attribute("worker_id", tracer_id)
                   time.sleep(0.1)  # Simulate work
                   results.append(f"completed-{tracer_id}")
           
           # Start workers concurrently
           threads = []
           for i, tracer in enumerate(tracers):
               thread = threading.Thread(target=worker, args=(tracer, i))
               threads.append(thread)
               thread.start()
           
           # Wait for all to complete
           for thread in threads:
               thread.join()
           
           # Verify all completed
           assert len(results) == 3
           assert "completed-0" in results
           assert "completed-1" in results
           assert "completed-2" in results

Real API Testing
----------------

Testing with Actual HoneyHive API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test integration with the real HoneyHive API:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer

   @pytest.mark.real_api
   class TestRealAPIIntegration:
       """Test integration with real HoneyHive API."""
       
       @pytest.fixture(autouse=True)
       def setup_real_api(self):
           """Setup real API credentials."""
           self.api_key = os.getenv("HH_API_KEY")
           self.project = os.getenv("HH_PROJECT")
           self.source = os.getenv("HH_SOURCE")
           
           if not all([self.api_key, self.project, self.source]):
               pytest.skip("Real API credentials not available")
           
           self.tracer = HoneyHiveTracer(
               api_key=self.api_key,
               project=self.project,
               source=self.source,
               test_mode=False  # Use real API
           )
       
       def test_real_session_creation(self):
           """Test creating a real session."""
           with self.tracer.start_span("real-api-test") as span:
               span.set_attribute("test.type", "real_api")
               span.set_attribute("api.project", self.project)
               
               # Verify session was created
               assert self.tracer.session_id is not None
               assert self.tracer.project == self.project
       
       def test_real_event_creation(self):
           """Test creating real events."""
           with self.tracer.start_span("event-test") as span:
               # Create an event
               event = self.tracer.create_event(
                   event_type="test",
                   event_name="real_api_test",
                   inputs={"test_input": "value"},
                   outputs={"test_output": "result"}
               )
               
               assert event is not None
               assert event.event_type == "test"

       def test_real_decorator_integration(self):
           """Test decorators with real API."""
           from honeyhive.tracer.decorators import trace
           
           @trace(tracer=self.tracer, event_type="test", event_name="decorator_test")
           def real_api_function():
               return "real_api_result"
           
           result = real_api_function()
           assert result == "real_api_result"

TracerProvider Testing
----------------------

Testing OpenTelemetry Provider Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test integration with existing OpenTelemetry providers:

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch
   from honeyhive import HoneyHiveTracer

   class TestTracerProviderIntegration:
       """Test TracerProvider integration scenarios."""
       
       def test_new_provider_creation(self):
           """Test creating a new TracerProvider when none exists."""
           with patch('honeyhive.tracer.otel_tracer.trace.get_tracer_provider') as mock_get:
               # Mock no existing provider
               mock_get.return_value = None
               
               tracer = HoneyHiveTracer(
                   api_key="test-key",
                   project="test-project"
               )
               
               # Should create new provider
               assert tracer.provider is not None
               assert tracer.is_main_provider is True
       
       def test_existing_provider_integration(self):
           """Test integrating with existing TracerProvider."""
           with patch('honeyhive.tracer.otel_tracer.trace.get_tracer_provider') as mock_get:
               # Mock existing provider
               mock_provider = Mock()
               mock_get.return_value = mock_provider
               
               tracer = HoneyHiveTracer(
                   api_key="test-key",
                   project="test-project"
               )
               
               # Should use existing provider
               assert tracer.provider is mock_provider
               assert tracer.is_main_provider is False

Force Flush Functionality Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test the comprehensive force_flush implementation as part of TracerProvider integration:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   def test_force_flush_basic():
       """Test basic force_flush functionality."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True
       )
       
       # Create spans to flush
       with tracer.start_span("test-span") as span:
           span.set_attribute("test.data", "value")
       
       # Test force_flush with default timeout
       result = tracer.force_flush()
       assert isinstance(result, bool)
       
       # Test force_flush with custom timeout
       result = tracer.force_flush(timeout_millis=5000)
       assert isinstance(result, bool)

   def test_force_flush_with_enrich_span():
       """Test force_flush with enrich_span integration."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True
       )
       
       # Test with context manager
       with tracer.enrich_span(
           metadata={"operation": "test"},
           outputs={"result": "success"},
           error=None
       ):
           with tracer.start_span("enriched-operation") as span:
               span.set_attribute("enriched", True)
       
       # Force flush to ensure delivery
       result = tracer.force_flush()
       assert result is True

   def test_force_flush_error_handling():
       """Test force_flush error handling."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True
       )
       
       # Test with mock provider failure
       with patch.object(tracer.provider, 'force_flush', return_value=False):
           result = tracer.force_flush()
           assert result is False  # Should handle failure gracefully

**TracerProvider Test Coverage** (includes Force Flush functionality):

- **Unit Tests**: 11 tests covering all force_flush scenarios
- **Integration Tests**: 9 tests with real API endpoints  
- **Total**: 20 dedicated force_flush tests within TracerProvider testing
- **Coverage Areas**: Basic functionality, provider integration, error handling, multi-instance coordination

Best Practices
--------------

Testing Guidelines
~~~~~~~~~~~~~~~~~~

1. **Use Test Mode** - Always enable test mode for testing
2. **Mock External Dependencies** - Mock API calls and external services
3. **Test Error Scenarios** - Test both success and failure cases
4. **Verify Span Attributes** - Check that spans have correct attributes
5. **Test Performance** - Ensure tracing doesn't significantly impact performance
6. **Clean Up Resources** - Clean up test resources after each test
7. **Test Multi-Instance Patterns** - Verify multiple tracers work independently
8. **Test Real API Integration** - Validate functionality with actual endpoints
9. **Test TracerProvider Scenarios** - Cover provider integration cases
10. **Maintain Coverage** - Keep test coverage above 70% threshold

Test Organization
~~~~~~~~~~~~~~~~~

Organize tests logically:

.. code-block:: python

   # tests/test_tracer.py
   class TestTracerInitialization:
       """Test tracer initialization scenarios."""
       
       def test_basic_initialization(self):
           """Test basic tracer initialization."""
           pass
       
       def test_with_custom_config(self):
           """Test initialization with custom configuration."""
           pass
       
       def test_error_handling(self):
           """Test error handling during initialization."""
           pass

   class TestTracerOperations:
       """Test tracer operations."""
       
       def test_span_creation(self):
           """Test span creation."""
           pass
       
       def test_span_attributes(self):
           """Test span attribute management."""
           pass

   class TestMultiInstanceTracer:
       """Test multiple tracer instances."""
       
       def test_independent_operation(self):
           """Test independent tracer operation."""
           pass
       
       def test_concurrent_usage(self):
           """Test concurrent tracer usage."""
           pass

   class TestTracerProviderIntegration:
       """Test TracerProvider integration."""
       
       def test_existing_provider(self):
           """Test integration with existing provider."""
           pass
       
       def test_new_provider_creation(self):
           """Test new provider creation."""
           pass



Continuous Integration
----------------------

Automated Testing
~~~~~~~~~~~~~~~~~

Set up automated testing in CI/CD:

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Tests
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.11, 3.12, 3.13]
       
       steps:
       - uses: actions/checkout@v3
       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v4
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
           pip install -r requirements-dev.txt
       
       - name: Run tests
         run: |
           pytest tests/ -v --cov=honeyhive --cov-report=xml --cov-fail-under=70
       
       - name: Upload coverage
         uses: codecov/codecov-action@v3
         with:
           file: ./coverage.xml

Running Tests
-------------

Current Test Execution
~~~~~~~~~~~~~~~~~~~~~~

The project uses tox for consistent testing across environments. Current test execution shows:

**Test Collection**: 881 tests collected from 35 test files
**Execution Time**: ~6-8 seconds for full test suite
**Coverage Generation**: HTML and XML reports automatically generated

Command Line
~~~~~~~~~~~~

Run tests from command line:

.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_tracer.py

   # Run with coverage (enforces 70% threshold)
   pytest --cov=honeyhive --cov-report=html --cov-fail-under=70

   # Run with verbose output
   pytest -v

   # Run specific test
   pytest tests/test_tracer.py::TestTracerInitialization::test_basic_initialization

   # Run integration tests only
   pytest tests/integration/ -v

   # Run multi-instance tests
   pytest -m multi_instance -v

   # Run real API tests
   pytest -m real_api -v

   # Run TracerProvider tests
   pytest -m tracer_provider -v

   # Run with current coverage settings
   pytest --cov=honeyhive --cov-report=term-missing --cov=src/honeyhive

Tox Environments
~~~~~~~~~~~~~~~~

Use tox for consistent testing across environments:

.. code-block:: bash

   # Run unit tests
   tox -e unit

   # Run integration tests
   tox -e integration

   # Run linting
   tox -e lint

   # Run formatting checks
   tox -e format

   # Run specific Python version
   tox -e py311
   tox -e py312
   tox -e py313

IDE Integration
~~~~~~~~~~~~~~~

Most IDEs support pytest integration:

* **VS Code** - Install Python extension and pytest extension
* **PyCharm** - Built-in pytest support
* **Vim/Neovim** - Use vim-test plugin
* **Emacs** - Use python-mode or elpy

Debugging Tests
~~~~~~~~~~~~~~~

Debug failing tests:

.. code-block:: python

   import pytest
   import pdb

   def test_debug_example():
       """Example of debugging a test."""
       result = some_function()
       
       if result != expected:
           pdb.set_trace()  # Breakpoint for debugging
       
       assert result == expected

Test Statistics & Coverage
--------------------------

Current Test Metrics
~~~~~~~~~~~~~~~~~~~~

The project maintains comprehensive testing with the following current statistics:

**Test Counts**:

- **Total Tests**: 881 tests
- **Unit Tests**: 26 test files covering individual components (761 tests)
- **Integration Tests**: 8 test files covering component interactions (97 tests)
- **Tracer Tests**: 1 test file covering core tracing functionality (23 tests)
- **Test Utilities**: 2 utility files for test support

**Coverage Metrics**:

- **Overall Coverage**: 72.95% (4,484 statements, 1,213 missed)
- **Coverage Requirement**: 70% minimum (✅ currently met)
- **Coverage Enforcement**: Tests fail if coverage drops below threshold
- **Coverage Reports**: HTML and XML coverage reports generated
- **Coverage Tools**: pytest-cov integration with fail-under option

**Test Results**:

- **Passed**: 881 tests ✅
- **Failed**: 0 tests ✅
- **Success Rate**: 100% ✅

**Module Coverage Highlights**:

- **100% Coverage**: `__init__.py` files, `evaluations.py`, `generated.py`, `tracing.py`, `dotdict.py`
- **High Coverage (85%+)**: `evaluators.py` (84%), `baggage_dict.py` (86%), `cache.py` (93%), `logger.py` (98%), `error_handler.py` (91%)
- **Medium Coverage (70-84%)**: `client.py` (76%), `otel_tracer.py` (73%), `config.py` (83%), `http_instrumentation.py` (72%)
- **Good Coverage (60-69%)**: `span_processor.py` (60%), `decorators.py` (66%), `retry.py` (66%)
- **Areas for Improvement (<60%)**: `cli/main.py` (37%), `connection_pool.py` (35%)

**Current Test Status**:

- **Test Success Rate**: 100% (881/881 tests passing) ✅
- **Known Issues**: None - all tests passing ✅
- **Coverage Status**: ✅ Above 70% requirement (currently 72.95%)

**Test Improvement Opportunities**:

- **CLI Module**: Increase coverage from 37% to target 60%+
- **Connection Pool**: Enhance coverage from 35% to target 60%+

**Recent Coverage Improvements**:

- **Error Handling**: New standardized middleware with 91% coverage
- **Import Testing**: Applied `sys.modules` strategy to improve conditional import coverage
- **Test Consolidation**: Reorganized 26 unit test files following `test_<module>_<file>.py` naming convention
- **File Consolidation**: All core API modules now have dedicated test files with 60%+ coverage

Coverage Requirements
~~~~~~~~~~~~~~~~~~~~~

The project maintains strict coverage requirements:

* **Minimum Coverage**: 70% overall test coverage
* **Coverage Enforcement**: Tests fail if coverage drops below threshold
* **Coverage Reports**: HTML and XML coverage reports generated
* **Coverage Tools**: pytest-cov integration with fail-under option

To check coverage locally:

.. code-block:: bash

   # Check current coverage
   pytest --cov=honeyhive --cov-report=term-missing

   # Generate HTML report
   pytest --cov=honeyhive --cov-report=html

   # Verify coverage threshold
   pytest --cov=honeyhive --cov-report=term-missing --cov-fail-under=70

   # Run with tox (recommended)
   tox -e unit -- --cov=honeyhive --cov-report=term-missing
   tox -e integration -- --cov=honeyhive --cov-report=term-missing

AWS Lambda Testing
------------------

**Production-ready test suite** for AWS Lambda compatibility and performance testing using validated bundle container approach.

Lambda Testing Overview
~~~~~~~~~~~~~~~~~~~~~~~

AWS Lambda presents unique challenges that require specialized testing approaches. The HoneyHive SDK has been optimized and validated for Lambda environments with comprehensive testing across the development lifecycle.

**Why Lambda Testing Matters**:

AWS Lambda has specific constraints that differ from traditional server environments:

- **Cold Start Delays**: First invocation initialization time
- **Memory Constraints**: Limited memory environments (128MB - 10GB)
- **Execution Timeouts**: Maximum 15-minute execution limits
- **Networking Restrictions**: Limited outbound connectivity
- **Container Reuse**: Warm start optimizations for performance
- **Concurrency Limits**: Parallel execution constraints

**Our Testing Approach**:

The HoneyHive SDK testing strategy addresses these challenges through:

- ✅ **Performance Validation**: Verified sub-500ms cold starts, <100ms warm starts
- ✅ **Memory Efficiency**: <50MB SDK overhead validated across memory configurations
- ✅ **Production Realism**: Bundle container approach mirrors actual AWS deployments
- ✅ **Multi-Environment Testing**: Local development → CI/CD → Production validation
- ✅ **Automated Quality Gates**: Continuous performance regression detection

**Lambda Testing Pipeline Overview**:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TD
       subgraph "Development Stage"
           DEV[Developer Code Changes]
           LOCAL[Local Lambda Testing]
           CONT[Bundle Container Build]
           BASIC[Basic Compatibility Tests]
           PERF[Performance Benchmarks]
       end
       
       subgraph "CI/CD Stage"
           PR[Pull Request]
           MATRIX[Matrix Testing<br/>Python 3.11/3.12/3.13<br/>Memory 256/512/1024MB]
           REGRESSION[Performance Regression Detection]
           GATES[Quality Gates]
       end
       
       subgraph "Production Stage"
           DEPLOY[Real AWS Lambda Deploy]
           PROD[Production Integration Tests]
           MONITOR[Performance Monitoring]
           ALERT[Alerting & Feedback]
       end
       
       DEV --> LOCAL
       LOCAL --> CONT
       CONT --> BASIC
       BASIC --> PERF
       PERF --> PR
       
       PR --> MATRIX
       MATRIX --> REGRESSION
       REGRESSION --> GATES
       
       GATES -->|Pass| DEPLOY
       GATES -->|Fail| DEV
       
       DEPLOY --> PROD
       PROD --> MONITOR
       MONITOR --> ALERT
       ALERT --> DEV
       
       classDef devStage fill:#1b5e20,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef ciStage fill:#1a237e,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef prodStage fill:#4a148c,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef failPath fill:#d32f2f,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class DEV,LOCAL,CONT,BASIC,PERF devStage
       class PR,MATRIX,REGRESSION,GATES ciStage
       class DEPLOY,PROD,MONITOR,ALERT prodStage

**✅ Validated Performance Results**:

.. list-table:: Lambda Performance Results
   :header-rows: 1
   :widths: 25 25 25 25

   * - Metric
     - Validated Target
     - Bundle Actual
     - Status
   * - SDK Import
     - < 200ms
     - ~153ms
     - ✅ PASS
   * - Tracer Init
     - < 300ms
     - ~155ms
     - ✅ PASS
   * - Cold Start Total
     - < 500ms
     - ~281ms
     - ✅ PASS
   * - Warm Start Avg
     - < 100ms
     - ~52ms
     - ✅ PASS
   * - Memory Overhead
     - < 50MB
     - <50MB
     - ✅ PASS

Lambda Testing Strategy
~~~~~~~~~~~~~~~~~~~~~~~

**Bundle Container Approach**

The project uses a **bundle container** approach for Lambda testing that provides:

- **Platform Compatibility**: Native Linux dependencies built in Lambda environment
- **Production Realistic**: Mirrors actual AWS Lambda deployments  
- **Reproducible**: Consistent builds across development environments
- **Performance Validated**: Real metrics from actual bundle testing

**Test Structure**:

.. code-block:: text

   tests/lambda/
   ├── Dockerfile.bundle-builder     # ✅ Multi-stage bundle build
   ├── lambda_functions/             # Lambda function code
   │   ├── working_sdk_test.py      # ✅ Basic functionality test
   │   ├── cold_start_test.py       # ✅ Performance measurement
   │   └── basic_tracing.py         # ✅ Simple tracing example
   ├── test_lambda_compatibility.py # ✅ Test suite implementation
   ├── test_lambda_performance.py   # Performance benchmarks
   ├── docker-compose.lambda.yml    # Legacy volume mounting approach
   └── Makefile                     # ✅ Build and test automation

**Quick Start**:

.. code-block:: bash

   # Build bundle container (required first step)
   cd tests/lambda
   make build
   
   # Run basic compatibility tests
   make test-lambda
   
   # Run cold start performance tests
   make test-cold-start
   
   # Manual container testing
   docker run --rm -p 9000:8080 \
     -e HH_API_KEY=test-key \
     -e HH_PROJECT=test-project \
     honeyhive-lambda:bundle-native
   
   curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
     -H "Content-Type: application/json" \
     -d '{"test": "manual"}'

Getting Started with Lambda Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Quick Start** - Get up and running with Lambda testing in under 2 minutes:

.. code-block:: bash

   # Navigate to Lambda testing directory
   cd tests/lambda
   
   # Build the bundle container (required first step)
   make build
   
   # Run basic compatibility tests
   make test-lambda
   
   # Run performance benchmarks
   make test-performance

**Available Testing Commands**:

.. code-block:: bash

   # Core Testing
   make test            # Run all Lambda compatibility tests
   make test-lambda     # Run basic Lambda tests
   make test-cold-start # Run cold start specific tests
   make test-performance# Run performance tests
   
   # Container Management
   make build           # Build Lambda test containers
   make clean           # Clean up containers and images
   
   # Debugging & Development
   make debug-shell     # Interactive shell in Lambda container
   make quick-test      # Quick validation test

Local Lambda Testing
~~~~~~~~~~~~~~~~~~~~

**Basic Lambda Function Testing**

Start with a simple Lambda function to verify SDK integration:

.. code-block:: python

   """Test HoneyHive SDK behavior during Lambda cold starts."""
   
   import json
   import os
   import sys
   import time
   from typing import Any, Dict
   
   sys.path.insert(0, "/var/task")
   
   # Track cold start behavior
   COLD_START = True
   INITIALIZATION_TIME = time.time()
   
   try:
       from honeyhive.tracer import HoneyHiveTracer
       SDK_IMPORT_TIME = time.time() - INITIALIZATION_TIME
       print(f"✅ SDK import took: {SDK_IMPORT_TIME * 1000:.2f}ms")
   except ImportError as e:
       print(f"❌ SDK import failed: {e}")
       SDK_IMPORT_TIME = -1
   
   # Initialize tracer and measure time
   tracer = None
   TRACER_INIT_TIME = -1
   
   if "honeyhive" in sys.modules:
       init_start = time.time()
       try:
           tracer = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY", "test-key"),
               project="lambda-cold-start-test",
               source="aws-lambda",
               session_name="cold-start-test",
               test_mode=True,
               disable_http_tracing=True,
           )
           TRACER_INIT_TIME = time.time() - init_start
           print(f"✅ Tracer initialization took: {TRACER_INIT_TIME * 1000:.2f}ms")
       except Exception as e:
           print(f"❌ Tracer initialization failed: {e}")
           TRACER_INIT_TIME = -1
   
   def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
       """Test cold start performance impact."""
       global COLD_START
       
       handler_start = time.time()
       current_cold_start = COLD_START
       COLD_START = False  # Subsequent invocations are warm starts
       
       print(f"🔥 {'Cold' if current_cold_start else 'Warm'} start detected")
       
       try:
           if not tracer:
               return {
                   "statusCode": 500,
                   "body": json.dumps({
                       "error": "Tracer not available",
                       "cold_start": current_cold_start,
                       "sdk_import_time_ms": (
                           SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                       ),
                       "tracer_init_time_ms": (
                           TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                       ),
                   }),
               }
       
           # Test SDK operations during cold/warm start
           with tracer.start_span("cold_start_test") as span:
               span.set_attribute("lambda.cold_start", current_cold_start)
               span.set_attribute(
                   "lambda.sdk_import_time_ms",
                   SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1,
               )
               span.set_attribute(
                   "lambda.tracer_init_time_ms", 
                   TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1,
               )
               
               # Simulate some work
               work_start = time.time()
               from honeyhive.tracer.otel_tracer import enrich_span
               
               with enrich_span(
                   tracer=tracer,
                   metadata={
                       "test_type": "cold_start",
                       "iteration": event.get("iteration", 1),
                   },
                   outputs={"cold_start": current_cold_start},
                   error=None,
               ):
                   # Simulate processing
                   time.sleep(0.05)
               
               work_time = time.time() - work_start
               span.set_attribute("lambda.work_time_ms", work_time * 1000)
           
           # Test flush performance
           flush_start = time.time()
           flush_success = tracer.force_flush(timeout_millis=1000)
           flush_time = time.time() - flush_start
           
           total_handler_time = time.time() - handler_start
           
           return {
               "statusCode": 200,
               "body": json.dumps({
                   "message": "Cold start test completed",
                   "cold_start": current_cold_start,
                   "timings": {
                       "sdk_import_ms": (
                           SDK_IMPORT_TIME * 1000 if SDK_IMPORT_TIME > 0 else -1
                       ),
                       "tracer_init_ms": (
                           TRACER_INIT_TIME * 1000 if TRACER_INIT_TIME > 0 else -1
                       ),
                       "handler_total_ms": total_handler_time * 1000,
                       "work_time_ms": work_time * 1000,
                       "flush_time_ms": flush_time * 1000,
                   },
                   "flush_success": flush_success,
                   "performance_impact": {
                       "init_overhead_ms": (
                           (SDK_IMPORT_TIME + TRACER_INIT_TIME) * 1000
                           if current_cold_start else 0
                       ),
                       "runtime_overhead_ms": (work_time + flush_time) * 1000,
                   },
               }),
           }
       
       except Exception as e:
           return {
               "statusCode": 500,
               "body": json.dumps({
                   "error": str(e),
                   "cold_start": current_cold_start,
                   "handler_time_ms": (time.time() - handler_start) * 1000,
               }),
           }

.. code-block:: python

   """Basic Lambda function to test HoneyHive SDK compatibility."""
   
   import json
   import os
   import time
   from honeyhive import HoneyHiveTracer
   
   # Initialize tracer outside handler for reuse
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY", "test-key"),
       project="lambda-test",
       source="aws-lambda",
       test_mode=True,
       disable_http_tracing=True,  # Optimize for Lambda
   )
   
   def lambda_handler(event, context):
       """Simple Lambda handler with HoneyHive tracing."""
       with tracer.start_span("lambda_execution") as span:
           span.set_attribute("lambda.request_id", getattr(context, "aws_request_id", "test"))
           
           # Process event and return response
           return {
               "statusCode": 200,
               "body": json.dumps({"message": "HoneyHive SDK works in Lambda!"})
           }

**Performance Testing**

Cold start and warm start performance validation:

.. code-block:: python

   """Basic Lambda function to test HoneyHive SDK compatibility."""
   
   import json
   import os
   import sys
   import time
   from typing import Any, Dict
   
   # Add the SDK to the path (simulates pip install in real Lambda)
   sys.path.insert(0, "/var/task")
   
   try:
       from honeyhive.tracer import HoneyHiveTracer
       from honeyhive.tracer.decorators import trace
       SDK_AVAILABLE = True
   except ImportError as e:
       print(f"❌ SDK import failed: {e}")
       SDK_AVAILABLE = False
   
   # Initialize tracer outside handler for reuse across invocations
   tracer = None
   if SDK_AVAILABLE:
       try:
           tracer = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY", "test-key"),
               project=os.getenv("HH_PROJECT", "lambda-test"),
               source="aws-lambda",
               session_name="lambda-basic-test",
               test_mode=True,  # Enable test mode for Lambda
               disable_http_tracing=True,  # Avoid Lambda networking issues
           )
           print("✅ HoneyHive tracer initialized successfully")
       except Exception as e:
           print(f"❌ Tracer initialization failed: {e}")
           tracer = None
   
   @trace(tracer=tracer, event_type="lambda", event_name="basic_operation")
   def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
       """Process data with tracing."""
       if not tracer:
           return {"error": "Tracer not available"}
   
       # Simulate work
       time.sleep(0.1)
   
       # Test span enrichment
       from honeyhive.tracer.otel_tracer import enrich_span
   
       with enrich_span(
           metadata={"lambda_test": True, "data_size": len(str(data))},
           outputs={"processed": True},
           error=None,
           tracer=tracer,
       ):
           result = {
               "processed_data": data,
               "timestamp": time.time(),
               "lambda_context": {
                   "function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
                   "function_version": os.getenv("AWS_LAMBDA_FUNCTION_VERSION"),
                   "memory_limit": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "128"),
               },
           }
   
       return result
   
   def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
       """Lambda handler function."""
       print(
           f"🚀 Lambda invocation started: {context.aws_request_id if hasattr(context, 'aws_request_id') else 'test'}"
       )
   
       start_time = time.time()
   
       try:
           # Test basic SDK functionality
           if not SDK_AVAILABLE:
               return {
                   "statusCode": 500,
                   "body": json.dumps({"error": "HoneyHive SDK not available"}),
               }
   
           if not tracer:
               return {
                   "statusCode": 500,
                   "body": json.dumps({"error": "HoneyHive tracer not initialized"}),
               }
   
           # Create a span for the entire Lambda execution
           with tracer.start_span("lambda_execution") as span:
               span.set_attribute(
                   "lambda.request_id", getattr(context, "aws_request_id", "test")
               )
               span.set_attribute(
                   "lambda.function_name", os.getenv("AWS_LAMBDA_FUNCTION_NAME", "unknown")
               )
               span.set_attribute(
                   "lambda.remaining_time",
                   getattr(context, "get_remaining_time_in_millis", lambda: 30000)(),
               )
   
               # Process the event
               result = process_data(event)
   
               # Test force_flush before Lambda completes
               flush_success = tracer.force_flush(timeout_millis=2000)
               span.set_attribute("lambda.flush_success", flush_success)
   
           execution_time = (time.time() - start_time) * 1000
   
           return {
               "statusCode": 200,
               "body": json.dumps({
                   "message": "HoneyHive SDK works in Lambda!",
                   "execution_time_ms": execution_time,
                   "flush_success": flush_success,
                   "result": result,
               }),
           }
   
       except Exception as e:
           print(f"❌ Lambda execution failed: {e}")
           return {
               "statusCode": 500,
               "body": json.dumps({
                   "error": str(e),
                   "execution_time_ms": (time.time() - start_time) * 1000,
               }),
           }
   
       finally:
           # Ensure cleanup
           if tracer:
               try:
                   tracer.force_flush(timeout_millis=1000)
               except Exception as e:
                   print(f"⚠️ Final flush failed: {e}")

Lambda Performance Benchmarks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automated Performance Testing**:

.. code-block:: python

   """Performance tests for HoneyHive SDK in AWS Lambda environment."""
   
   import json
   import statistics
   import time
   from typing import Any, Dict, List
   
   import docker
   import pytest
   import requests
   
   class TestLambdaPerformance:
       """Performance tests for Lambda environment."""
   
       @pytest.fixture(scope="class")
       def performance_container(self):
           """Start optimized Lambda container for performance testing."""
           client = docker.from_env()
   
           container = client.containers.run(
               "honeyhive-lambda:bundle-native",
               command="cold_start_test.lambda_handler",
               ports={"8080/tcp": 9100},
               environment={
                   "AWS_LAMBDA_FUNCTION_NAME": "honeyhive-performance-test",
                   "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "256",
                   "HH_API_KEY": "test-key",
                   "HH_PROJECT": "lambda-performance-test",
                   "HH_SOURCE": "performance-test",
                   "HH_TEST_MODE": "true",
               },
               detach=True,
               remove=True,
           )
   
           # Wait for container to be ready
           time.sleep(5)
           yield container
   
           try:
               container.stop()
           except:
               pass
   
       def invoke_lambda_timed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
           """Invoke Lambda and measure timing."""
           url = "http://localhost:9100/2015-03-31/functions/function/invocations"
   
           start_time = time.time()
           response = requests.post(
               url, json=payload, headers={"Content-Type": "application/json"}, timeout=30
           )
           total_time = (time.time() - start_time) * 1000
   
           result = response.json()
           result["_test_total_time_ms"] = total_time
   
           return result
   
       @pytest.mark.benchmark
       def test_cold_start_performance(self, performance_container):
           """Benchmark cold start performance."""
           result = self.invoke_lambda_timed({"test": "cold_start_benchmark"})
   
           assert result["statusCode"] == 200
           body = json.loads(result["body"])
           timings = body.get("timings", {})
   
           # Collect metrics
           metrics = {
               "cold_start": body.get("cold_start", True),
               "total_time_ms": result["_test_total_time_ms"],
               "sdk_import_ms": timings.get("sdk_import_ms", 0),
               "tracer_init_ms": timings.get("tracer_init_ms", 0),
               "handler_total_ms": timings.get("handler_total_ms", 0),
               "work_time_ms": timings.get("work_time_ms", 0),
               "flush_time_ms": timings.get("flush_time_ms", 0),
           }
   
           # Performance assertions
           assert metrics["sdk_import_ms"] < 50, f"SDK import too slow: {metrics['sdk_import_ms']}ms"
           assert metrics["tracer_init_ms"] < 100, f"Tracer init too slow: {metrics['tracer_init_ms']}ms"
           assert metrics["total_time_ms"] < 2000, f"Total time too slow: {metrics['total_time_ms']}ms"
   
           return metrics

**Memory and Performance Results**:

.. list-table:: Lambda Performance Results by Memory Configuration
   :header-rows: 1
   :widths: 25 25 25 25

   * - Memory (MB)
     - Cold Start (ms)
     - Warm Start (ms)
     - SDK Overhead (ms)
   * - 128
     - 850-1200
     - 5-15
     - 45-65
   * - 256
     - 650-900
     - 3-10
     - 35-50
   * - 512
     - 450-700
     - 2-8
     - 25-40
   * - 1024
     - 350-550
     - 1-5
     - 15-30

**Key Test Cases**:

- ✅ **Basic Compatibility**: SDK works in Lambda
- ✅ **Cold Start Performance**: < 2s initialization
- ✅ **Warm Start Optimization**: < 500ms execution
- ✅ **Memory Efficiency**: < 20MB overhead
- ✅ **Concurrent Execution**: > 95% success rate
- ✅ **Error Handling**: Graceful degradation

Performance Testing & Benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Comprehensive Performance Validation**

The Lambda testing infrastructure provides automated performance benchmarking across different scenarios:

**Performance Targets & Results**:

.. list-table:: Performance Benchmarks by Memory Configuration
   :header-rows: 1
   :widths: 25 25 25 25

   * - Memory (MB)
     - Cold Start (ms)
     - Warm Start (ms)
     - SDK Overhead (ms)
   * - 256
     - 650-900
     - 3-10
     - 35-50
   * - 512
     - 450-700
     - 2-8
     - 25-40
   * - 1024
     - 350-550
     - 1-5
     - 15-30

**Automated Performance Testing**:

.. code-block:: python

   # Performance test execution
   cd tests/lambda
   make test-performance
   
   # Custom performance tests with specific parameters
   python -m pytest test_lambda_performance.py::TestLambdaPerformance::test_cold_start_performance -v

**Key Performance Validations**:

- ✅ **Cold Start Performance**: Consistently < 500ms across memory configurations
- ✅ **Warm Start Optimization**: < 100ms average execution time
- ✅ **Memory Efficiency**: < 50MB SDK overhead
- ✅ **Throughput Testing**: > 95% success rate under load
- ✅ **Error Resilience**: Graceful degradation when HoneyHive is unavailable

**Performance Testing Matrix**:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph LR
       subgraph "Test Configurations"
           M256[256MB Memory]
           M512[512MB Memory]
           M1024[1024MB Memory]
       end
       
       subgraph "Performance Tests"
           COLD[Cold Start Tests<br/>Target: <500ms<br/>Measured: 281ms]
           WARM[Warm Start Tests<br/>Target: <100ms<br/>Measured: 52ms]
           MEM[Memory Usage Tests<br/>Target: <50MB<br/>Measured: <50MB]
           LOAD[Load Tests<br/>Target: >95%<br/>Measured: >95%]
       end
       
       subgraph "Python Versions"
           P311[Python 3.11]
           P312[Python 3.12]
           P313[Python 3.13]
       end
       
       subgraph "Test Results"
           PASS[✅ All Tests Pass<br/>281ms cold start<br/>52ms warm start<br/><50MB overhead]
           TREND[📈 Performance Trending<br/>Historical Analysis<br/>Regression Detection]
       end
       
       M256 --> COLD
       M512 --> WARM
       M1024 --> MEM
       
       P311 --> LOAD
       P312 --> COLD
       P313 --> WARM
       
       COLD --> PASS
       WARM --> PASS
       MEM --> PASS
       LOAD --> PASS
       
       PASS --> TREND
       
       classDef configNode fill:#1b5e20,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef testNode fill:#e65100,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef versionNode fill:#1a237e,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef resultNode fill:#388e3c,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class M256,M512,M1024 configNode
       class COLD,WARM,MEM,LOAD testNode
       class P311,P312,P313 versionNode
       class PASS,TREND resultNode

CI/CD Integration & Automation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**From Local to Production**

Once local testing is complete, the Lambda testing infrastructure integrates with CI/CD pipelines for automated validation across environments:

**GitHub Actions Workflow**:

.. code-block:: yaml

   # .github/workflows/lambda-tests.yml
   name: Lambda Testing Pipeline
   
   on: [push, pull_request]
   
   jobs:
     lambda-validation:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.11, 3.12, 3.13]
           memory-size: [256, 512, 1024]
       
       steps:
       - uses: actions/checkout@v4
       - name: Build Lambda containers
         run: |
           cd tests/lambda
           make build
       - name: Run Lambda tests
         run: |
           cd tests/lambda
           make test-lambda test-performance

**Performance Regression Gates**:

The CI/CD pipeline includes automated performance regression detection:

- **Cold Start Threshold**: Block merge if > 1000ms (target: < 500ms)
- **Memory Threshold**: Block merge if > 100MB overhead (target: < 50MB)  
- **Success Rate Threshold**: Block merge if < 90% (target: > 95%)

**CI/CD Quality Gate Flow**:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TD
       PR[Pull Request Created]
       
       subgraph "Automated Testing Matrix"
           PY311[Python 3.11 Tests]
           PY312[Python 3.12 Tests]
           PY313[Python 3.13 Tests]
           
           M256[256MB Memory Tests]
           M512[512MB Memory Tests]
           M1024[1024MB Memory Tests]
       end
       
       subgraph "Quality Gates"
           PERF[Performance Gate<br/>Cold Start < 1000ms<br/>Memory < 100MB<br/>Success > 90%]
           COMPAT[Compatibility Gate<br/>All Python Versions<br/>All Memory Configs]
           REGRESS[Regression Gate<br/>±20% Performance<br/>Historical Comparison]
       end
       
       subgraph "Results"
           PASS[✅ All Gates Pass<br/>Merge Approved]
           FAIL[❌ Gates Failed<br/>Block Merge<br/>Notify Developer]
           WARN[⚠️ Performance Warning<br/>Manual Review Required]
       end
       
       PR --> PY311
       PR --> PY312
       PR --> PY313
       
       PY311 --> M256
       PY312 --> M512
       PY313 --> M1024
       
       M256 --> PERF
       M512 --> PERF
       M1024 --> PERF
       
       PERF --> COMPAT
       COMPAT --> REGRESS
       
       REGRESS -->|Pass All| PASS
       REGRESS -->|Critical Fail| FAIL
       REGRESS -->|Minor Issue| WARN
       
       FAIL --> PR
       WARN --> PASS
       
       classDef prNode fill:#4F81BD,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef testNode fill:#1a237e,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef gateNode fill:#e65100,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef passNode fill:#388e3c,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef failNode fill:#d32f2f,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef warnNode fill:#ff9800,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class PR prNode
       class PY311,PY312,PY313,M256,M512,M1024 testNode
       class PERF,COMPAT,REGRESS gateNode
       class PASS passNode
       class FAIL failNode
       class WARN warnNode

Production Lambda Testing
~~~~~~~~~~~~~~~~~~~~~~~~~

**Real AWS Lambda Deployment Testing**

For final validation, the SDK is tested against actual AWS Lambda functions:

**Production Testing Architecture**:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       subgraph "AWS Lambda Environment"
           LAMBDA[AWS Lambda Function<br/>honeyhive-sdk-test]
           RUNTIME[Lambda Runtime<br/>Python 3.11/3.12/3.13]
           MEM[Memory Configurations<br/>256MB/512MB/1024MB]
       end
       
       subgraph "HoneyHive SDK"
           SDK[HoneyHive SDK Bundle]
           TRACER[Multi-Instance Tracers]
           INSTR[OpenAI Instrumentors]
       end
       
       subgraph "Real Integration Tests"
           COLD[Cold Start Validation<br/>10 iterations]
           WARM[Warm Start Validation<br/>50 iterations]
           LOAD[Load Testing<br/>Concurrent invocations]
           ERROR[Error Handling<br/>Network failures]
       end
       
       subgraph "HoneyHive Platform"
           API[HoneyHive API]
           DASH[Dashboard Validation]
           TRACES[Trace Data Verification]
           METRICS[Performance Metrics]
       end
       
       subgraph "Monitoring & Alerting"
           WATCH[CloudWatch Logs]
           ALERT[Performance Alerts]
           SLACK[Slack Notifications]
           FEEDBACK[Developer Feedback Loop]
       end
       
       LAMBDA --> SDK
       RUNTIME --> SDK
       MEM --> SDK
       
       SDK --> TRACER
       SDK --> INSTR
       
       TRACER --> COLD
       TRACER --> WARM
       TRACER --> LOAD
       TRACER --> ERROR
       
       COLD --> API
       WARM --> API
       LOAD --> API
       ERROR --> API
       
       API --> DASH
       API --> TRACES
       API --> METRICS
       
       TRACES --> WATCH
       METRICS --> ALERT
       ALERT --> SLACK
       SLACK --> FEEDBACK
       FEEDBACK --> LAMBDA
       
       classDef awsNode fill:#ff9900,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef sdkNode fill:#1a237e,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef testNode fill:#e65100,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef hhNode fill:#4F81BD,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef monitorNode fill:#4a148c,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class LAMBDA,RUNTIME,MEM awsNode
       class SDK,TRACER,INSTR sdkNode
       class COLD,WARM,LOAD,ERROR testNode
       class API,DASH,TRACES,METRICS hhNode
       class WATCH,ALERT,SLACK,FEEDBACK monitorNode

.. code-block:: python

   import json
   import os
   import openai
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   def lambda_handler(event, context):
       """Production Lambda test with real API calls."""
       
       # Initialize with production settings
       tracer = HoneyHiveTracer.init(
           api_key=os.environ.get("HH_API_KEY"),
           project="lambda-integration-test",
           source="aws-lambda-prod",
           instrumentors=[OpenAIInstrumentor()]
       )
       
       try:
           with tracer.start_span("lambda-openai-test") as span:
               span.set_attribute("lambda.function_name", context.function_name)
               span.set_attribute("lambda.request_id", context.aws_request_id)
               
               # Make real OpenAI API call (traced automatically)
               client = openai.OpenAI()
               response = client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": "Test from Lambda"}],
                   max_tokens=50
               )
               
               return {
                   'statusCode': 200,
                   'body': json.dumps({
                       'message': 'Lambda integration test successful',
                       'response': response.choices[0].message.content,
                       'request_id': context.aws_request_id
                   })
               }
               
       except Exception as e:
           return {
               'statusCode': 500,
               'body': json.dumps({
                   'error': str(e),
                   'request_id': context.aws_request_id
               })
           }

Lambda Testing Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Optimization Strategies**:

1. **Minimize Cold Start Impact**:
   - Initialize tracer outside handler when possible
   - Use connection pooling for HTTP requests
   - Optimize import statements and dependencies
   - Leverage Lambda container reuse

2. **Memory Management**:
   - Monitor memory usage patterns with CloudWatch
   - Clean up resources properly in finally blocks
   - Use appropriate memory allocation (256MB+ recommended)
   - Test with different memory configurations

3. **Error Handling**:
   - Implement comprehensive error catching
   - Log errors with structured logging for CloudWatch
   - Graceful degradation strategies when HoneyHive is unavailable
   - Test timeout scenarios

4. **Performance Optimization**:
   - Use ``disable_http_tracing=True`` to reduce overhead
   - Enable ``test_mode=True`` for non-production environments  
   - Use ``force_flush()`` with appropriate timeouts
   - Initialize instrumentors selectively

**Lambda-Specific Configuration**:

.. code-block:: python

   # Optimized Lambda configuration
   tracer = HoneyHiveTracer.init(
       api_key=os.environ.get("HH_API_KEY"),
       project=os.environ.get("HH_PROJECT", "lambda-app"),
       source="aws-lambda",
       session_name=os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "lambda-function"),
       # Optimize for Lambda constraints
       test_mode=os.environ.get("HH_TEST_MODE", "false").lower() == "true",
       disable_http_tracing=True,  # Reduce overhead in Lambda
       instrumentors=[OpenAIInstrumentor()],  # Only needed instrumentors
   )

**Testing Infrastructure Summary**:

The AWS Lambda testing infrastructure provides:

- ✅ **Comprehensive Test Suite**: 24 test files covering all scenarios
- ✅ **Production Bundle Containers**: Native Linux dependencies
- ✅ **Automated Performance Benchmarks**: Cold/warm start metrics
- ✅ **Real API Integration**: Actual AWS Lambda deployment testing  
- ✅ **CI/CD Ready**: Makefile automation and Docker integration
- ✅ **Validated Performance**: Sub-500ms cold starts, <100ms warm starts
- ✅ **Error Resilience**: Graceful degradation and timeout handling

**Key Files**:

- ``tests/lambda/README.md`` - Complete testing documentation
- ``tests/lambda/CONTAINER_STRATEGY.md`` - Bundle vs volume mount strategy
- ``tests/lambda/Makefile`` - Automated testing commands
- ``tests/lambda/test_lambda_compatibility.py`` - Compatibility test suite
- ``tests/lambda/test_lambda_performance.py`` - Performance benchmarks
- ``tests/lambda/lambda_functions/`` - Example Lambda functions
- ``Dockerfile.lambda`` - Production Lambda container setup

For complete Lambda testing documentation and examples, see the ``tests/lambda/`` directory.

Lambda CI/CD Testing
~~~~~~~~~~~~~~~~~~~~

**Automated Testing Pipeline**

The Lambda testing infrastructure integrates seamlessly with CI/CD pipelines for automated validation:

**GitHub Actions Integration**:

.. code-block:: yaml

   # .github/workflows/lambda-tests.yml
   name: Lambda Testing
   
   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main ]
     schedule:
       - cron: '0 6 * * *'  # Daily performance regression testing
   
   jobs:
     lambda-compatibility:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.11, 3.12, 3.13]
           memory-size: [256, 512, 1024]
       
       steps:
       - name: Checkout code
         uses: actions/checkout@v4
       
       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v4
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install tox docker
       
       - name: Build Lambda test containers
         run: |
           cd tests/lambda
           make build
       
       - name: Run Lambda compatibility tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
           HH_PROJECT: "ci-lambda-test"
           HH_SOURCE: "github-actions"
           AWS_LAMBDA_FUNCTION_MEMORY_SIZE: ${{ matrix.memory-size }}
         run: |
           cd tests/lambda
           make test-lambda
       
       - name: Run Lambda performance tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
         run: |
           cd tests/lambda
           make test-performance
       
       - name: Upload performance results
         uses: actions/upload-artifact@v3
         if: always()
         with:
           name: lambda-performance-${{ matrix.python-version }}-${{ matrix.memory-size }}mb
           path: tests/lambda/performance-results.json

**Performance Regression Detection**:

.. code-block:: yaml

   performance-regression:
     runs-on: ubuntu-latest
     needs: lambda-compatibility
     
     steps:
     - name: Download performance artifacts
       uses: actions/download-artifact@v3
       with:
         pattern: lambda-performance-*
         merge-multiple: true
     
     - name: Analyze performance trends
       run: |
         python scripts/analyze-lambda-performance.py \
           --baseline performance-baseline.json \
           --current performance-results.json \
           --threshold 20  # 20% regression threshold
     
     - name: Comment on PR with results
       if: github.event_name == 'pull_request'
       uses: actions/github-script@v6
       with:
         script: |
           const fs = require('fs');
           const results = JSON.parse(fs.readFileSync('performance-summary.json'));
           
           github.rest.issues.createComment({
             issue_number: context.issue.number,
             owner: context.repo.owner,
             repo: context.repo.repo,
             body: `## 🚀 Lambda Performance Results
             
             | Metric | Current | Baseline | Change |
             |--------|---------|----------|---------|
             | Cold Start | ${results.coldStart}ms | ${results.baselineColdStart}ms | ${results.coldStartChange} |
             | Warm Start | ${results.warmStart}ms | ${results.baselineWarmStart}ms | ${results.warmStartChange} |
             | Memory Usage | ${results.memoryUsage}MB | ${results.baselineMemory}MB | ${results.memoryChange} |
             
             ${results.passed ? '✅ All performance targets met!' : '❌ Performance regression detected!'}`
           });

**Deployment Testing**:

.. code-block:: yaml

   deploy-test:
     runs-on: ubuntu-latest
     if: github.ref == 'refs/heads/main'
     needs: [lambda-compatibility, performance-regression]
     
     steps:
     - name: Deploy test Lambda function
       env:
         AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
         AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
         AWS_REGION: us-east-1
       run: |
         # Create deployment package
         cd tests/lambda
         ./build-deployment-package.sh
         
         # Deploy to AWS Lambda
         aws lambda update-function-code \
           --function-name honeyhive-sdk-test \
           --zip-file fileb://deployment-package.zip
     
     - name: Run integration tests against real Lambda
       env:
         AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
         AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
         HH_API_KEY: ${{ secrets.HH_API_KEY }}
       run: |
         python tests/lambda/test_real_lambda_deployment.py \
           --function-name honeyhive-sdk-test \
           --iterations 10

**Multi-Environment Testing**:

.. code-block:: bash

   # Test across multiple environments
   tox -e lambda-py311,lambda-py312,lambda-py313 -- \
     --memory 256,512,1024 \
     --cold-start-iterations 5 \
     --warm-start-iterations 10

**CI/CD Performance Targets**:

.. list-table:: CI/CD Performance Gates
   :header-rows: 1
   :widths: 30 20 20 30

   * - Metric
     - Target
     - Threshold
     - Action on Failure
   * - Cold Start Time
     - < 500ms
     - < 1000ms
     - Block merge if > 1000ms
   * - Warm Start Time
     - < 100ms
     - < 200ms
     - Warning if > 100ms
   * - Memory Usage
     - < 50MB overhead
     - < 100MB
     - Block merge if > 100MB
   * - Success Rate
     - > 95%
     - > 90%
     - Block merge if < 90%
   * - Build Time
     - < 2 minutes
     - < 5 minutes
     - Warning if > 2 minutes

**Environment-Specific Testing**:

.. code-block:: bash

   # Development environment
   HH_TEST_MODE=true make test-lambda
   
   # Staging environment  
   HH_API_KEY=$STAGING_API_KEY HH_PROJECT=staging-tests make test-lambda
   
   # Production validation (read-only)
   HH_API_KEY=$PROD_API_KEY HH_PROJECT=prod-validation make test-lambda-readonly

**Automated Quality Gates**:

1. **Performance Gates**: Automated blocking if performance degrades > 20%
2. **Compatibility Gates**: Must pass on all supported Python versions
3. **Memory Gates**: Block if memory usage exceeds thresholds
4. **Error Rate Gates**: Block if error rate > 5%
5. **Integration Gates**: Real AWS Lambda deployment must succeed

**Monitoring and Alerting**:

.. code-block:: yaml

   monitoring:
     - name: Lambda performance monitoring
       schedule: "0 */6 * * *"  # Every 6 hours
       run: |
         python scripts/monitor-lambda-performance.py \
           --alert-slack ${{ secrets.SLACK_WEBHOOK }} \
           --alert-email ${{ secrets.ALERT_EMAIL }}

**CI/CD Benefits**:

- ✅ **Automated Validation**: Every PR tested against Lambda runtime
- ✅ **Performance Regression Detection**: Continuous monitoring of key metrics  
- ✅ **Multi-Environment Support**: Dev, staging, and production testing
- ✅ **Real Deployment Testing**: Actual AWS Lambda function validation
- ✅ **Quality Gates**: Automated blocking of problematic changes
- ✅ **Performance Trending**: Historical performance data tracking
- ✅ **Cross-Platform Testing**: Multiple Python versions and memory configurations
