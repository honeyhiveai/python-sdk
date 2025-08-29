Testing Guide
=============

Comprehensive guide to testing the HoneyHive Python SDK and applications that use it.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Testing is a crucial part of developing reliable applications with the HoneyHive Python SDK. This guide covers testing strategies, tools, and best practices for ensuring your tracing implementation works correctly.

Testing Strategy
----------------

Multi-Layer Testing
~~~~~~~~~~~~~~~~~~~

The SDK supports a multi-layered testing approach:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Performance Tests** - Test performance characteristics

Test Configuration
~~~~~~~~~~~~~~~~~~

Configure the SDK for testing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer

   # Test configuration
   tracer = HoneyHiveTracer.init(
       api_key="test-api-key",
       project="test-project",
       source="test",
       test_mode=True,  # Enable test mode
       disable_http_tracing=True  # Disable HTTP tracing in tests
   )

Unit Testing
------------

Testing Individual Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test individual SDK components:

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

Testing Decorators
~~~~~~~~~~~~~~~~~~

Test tracing decorators:

.. code-block:: python

   from honeyhive.tracer.decorators import trace

   @trace
   def traced_function():
       """Function to test tracing decorator."""
       return "traced result"

   def test_trace_decorator():
       """Test that the trace decorator works."""
       result = traced_function()
       assert result == "traced result"
       
       # Verify span was created (in test mode)
       # This would require access to the tracer instance

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

Test how components work together:

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

End-to-End Testing
------------------

Testing Complete Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test complete tracing workflows:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHiveTracer, trace

   @trace
   async def workflow_step_1():
       """First step in workflow."""
       await asyncio.sleep(0.1)
       return "step1_result"

   @trace
   async def workflow_step_2(input_data):
       """Second step in workflow."""
       await asyncio.sleep(0.1)
       return f"step2_result_{input_data}"

   @trace
   async def complete_workflow():
       """Complete workflow with multiple steps."""
       step1_result = await workflow_step_1()
       step2_result = await workflow_step_2(step1_result)
       return step2_result

   async def test_complete_workflow():
       """Test complete workflow execution."""
       tracer = HoneyHiveTracer(
           api_key="test-key",
           test_mode=True
       )
       
       result = await complete_workflow()
       assert result == "step2_result_step1_result"

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

   def assert_span_attributes(span, expected_attrs):
       """Assert that span has expected attributes."""
       for key, value in expected_attrs.items():
           assert span.get_attribute(key) == value, f"Attribute {key} mismatch"

   def assert_span_events(span, expected_events):
       """Assert that span has expected events."""
       event_names = [event.name for event in span.events]
       for event_name in expected_events:
           assert event_name in event_names, f"Event {event_name} not found"

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
           pytest tests/ -v --cov=honeyhive --cov-report=xml
       
       - name: Upload coverage
         uses: codecov/codecov-action@v3
         with:
           file: ./coverage.xml

Running Tests
-------------

Command Line
~~~~~~~~~~~~

Run tests from command line:

.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_tracer.py

   # Run with coverage
   pytest --cov=honeyhive --cov-report=html

   # Run with verbose output
   pytest -v

   # Run specific test
   pytest tests/test_tracer.py::TestTracerInitialization::test_basic_initialization

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
