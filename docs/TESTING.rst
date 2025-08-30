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
- **Total Tests**: 859 tests
- **Test Coverage**: 72.76% ✅ (above 70% requirement)
- **Test Results**: 859 passed, 0 failed ✅
- **Code Coverage**: 4,270 total statements, 1,163 missed

Test Organization
-----------------

The project maintains a comprehensive test suite organized into logical categories:

**Test File Structure**:
- **Total Test Files**: 37
- **Unit Tests**: 21 test files in `tests/unit/` (739 tests)
- **Integration Tests**: 8 test files in `tests/integration/` (97 tests)
- **Tracer Tests**: 1 test file in `tests/tracer/` (23 tests)
- **Test Utilities**: 2 utility files (`conftest.py`, `utils.py`)

**Test Categories**:
1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions and multi-instance patterns
3. **End-to-End Tests** - Test complete workflows
4. **Performance Tests** - Test performance characteristics
5. **Multi-Instance Tests** - Test multiple tracer instances and their interactions
6. **Real API Tests** - Test with actual HoneyHive API endpoints
7. **TracerProvider Tests** - Test OpenTelemetry provider integration
8. **Force Flush Tests** - Test comprehensive force_flush functionality (20 tests)

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

Testing OpenInference Integration
---------------------------------

Testing AI Operation Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test OpenInference instrumentor integration:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor

   def test_openinference_integration():
       """Test OpenInference instrumentor integration."""
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True,
           instrumentors=[OpenAIInstrumentor()]
       )
       
       # Verify instrumentor was added
       assert len(tracer.instrumentors) > 0
       assert any(isinstance(i, OpenAIInstrumentor) for i in tracer.instrumentors)

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
       
       def test_provider_shutdown_behavior(self):
           """Test provider shutdown behavior."""
           tracer = HoneyHiveTracer(
               api_key="test-key",
               project="test-project"
           )
           
           # Set as main provider
           tracer.is_main_provider = True
           
           # Mock provider shutdown
           with patch.object(tracer.provider, 'shutdown') as mock_shutdown:
               tracer.shutdown()
               mock_shutdown.assert_called_once()

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

Force Flush Testing
-------------------

Testing Force Flush Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test the comprehensive force_flush implementation:

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

**Force Flush Test Coverage**:

- **Unit Tests**: 11 tests covering all force_flush scenarios
- **Integration Tests**: 9 tests with real API endpoints
- **Total**: 20 dedicated force_flush tests
- **Coverage Areas**: Basic functionality, provider integration, error handling, multi-instance coordination

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

**Test Collection**: 859 tests collected from 37 test files
**Execution Time**: ~14-16 seconds for full test suite
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
- **Total Tests**: 859 tests
- **Unit Tests**: 21 test files covering individual components (739 tests)
- **Integration Tests**: 8 test files covering component interactions (97 tests)
- **Tracer Tests**: 1 test file covering core tracing functionality (23 tests)
- **Test Utilities**: 2 utility files for test support

**Coverage Metrics**:
- **Overall Coverage**: 72.76% (4,270 statements, 1,163 missed)
- **Coverage Requirement**: 70% minimum (✅ currently met)
- **Coverage Enforcement**: Tests fail if coverage drops below threshold
- **Coverage Reports**: HTML and XML coverage reports generated
- **Coverage Tools**: pytest-cov integration with fail-under option

**Test Results**:
- **Passed**: 859 tests ✅
- **Failed**: 0 tests ✅
- **Success Rate**: 100% ✅

**Module Coverage Highlights**:
- **100% Coverage**: `__init__.py` files, `evaluations.py`, `generated.py`, `tracing.py`, `dotdict.py`
- **High Coverage (85%+)**: `evaluators.py` (85%), `baggage_dict.py` (86%), `cache.py` (98%), `logger.py` (98%)
- **Medium Coverage (70-84%)**: `client.py` (74%), `otel_tracer.py` (72%), `config.py` (84%)
- **Lower Coverage Areas**: `cli/main.py` (37%), `metrics.py` (30%), `connection_pool.py` (57%)

**Current Test Status**:
- **Test Success Rate**: 100% (859/859 tests passing) ✅
- **Known Issues**: None - all tests passing ✅
- **Coverage Status**: ✅ Above 70% requirement (currently 72.76%)

**Test Improvement Opportunities**:
- **CLI Module**: Increase coverage from 37% to target 70%+
- **Metrics API**: Improve coverage from 30% to target 70%+
- **Connection Pool**: Enhance coverage from 57% to target 70%+
- **Tracer Decorators**: Boost coverage from 53% to target 70%+
- **HTTP Instrumentation**: Improve coverage from 63% to target 70%+

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
