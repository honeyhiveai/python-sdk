Testing Applications with HoneyHive
===================================

**Problem:** You need to test your LLM application with HoneyHive tracing enabled, write unit tests for traced functions, and verify that traces are captured correctly without relying on mocks.

**Solution:** Use pytest with real HoneyHive tracers in test mode, validate trace outputs programmatically, and follow testing best practices for LLM applications.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Testing Philosophy
------------------

**Key Principles:**

1. **Test with Real Tracers**: Don't mock HoneyHive - test with actual tracing
2. **Validate Trace Structure**: Ensure spans contain expected attributes
3. **Separate Test Projects**: Use dedicated test projects in HoneyHive
4. **Fixture-Based Setup**: Reusable tracer fixtures for consistency

**Why Test with Real Tracing?**

- ✅ Catches integration issues early
- ✅ Validates span enrichment logic
- ✅ Ensures production-like behavior
- ❌ Mocking hides real-world failures

Setup for Testing
-----------------

Test Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.test file
   HH_API_KEY=hh_test_your_test_api_key
   HH_PROJECT=test-project
   HH_SOURCE=pytest
   
   # Use separate API key and project for testing
   # DO NOT use production credentials in tests

Pytest Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # conftest.py - Shared test fixtures
   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   from dotenv import load_dotenv
   
   # Load test environment
   load_dotenv('.env.test')
   
   @pytest.fixture(scope="session")
   def test_tracer():
       """Provide a HoneyHive tracer for testing."""
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),
           project=os.getenv("HH_PROJECT", "test-project"),
           source="pytest"
       )
       
       yield tracer
       
       # Cleanup after all tests
       # HoneyHive automatically flushes on process exit
   
   @pytest.fixture
   def clean_tracer():
       """Provide a fresh tracer for each test."""
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),
           project=f"test-{pytest.current_test_name}",
           source="pytest"
       )
       
       yield tracer
       
       # Test-specific cleanup if needed

Unit Testing Traced Functions
-----------------------------

Basic Function Testing
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # test_traced_functions.py
   from honeyhive import trace, enrich_span
   from honeyhive.models import EventType
   import pytest
   
   # Function under test
   @trace(event_type=EventType.tool)
   def process_data(data: dict) -> dict:
       """Process data with tracing."""
       enrich_span({
           "input.size": len(data),
           "process.type": "transformation"
       })
       
       result = {"processed": True, **data}
       enrich_span({"output.size": len(result)})
       
       return result
   
   # Test the function
   def test_process_data(test_tracer):
       """Test data processing with real tracing."""
       # Arrange
       input_data = {"key": "value", "count": 10}
       
       # Act
       result = process_data(input_data)
       
       # Assert
       assert result["processed"] is True
       assert result["key"] == "value"
       assert result["count"] == 10
       
       # Trace is captured automatically in test project

Testing with Span Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from opentelemetry import trace as otel_trace
   from opentelemetry.sdk.trace import ReadableSpan
   from opentelemetry.sdk.trace.export import SimpleSpanProcessor
   from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
   
   @pytest.fixture
   def span_capture(test_tracer):
       """Capture spans for validation in tests."""
       exporter = InMemorySpanExporter()
       processor = SimpleSpanProcessor(exporter)
       test_tracer.provider.add_span_processor(processor)
       
       yield exporter
       
       exporter.clear()
   
   def test_span_enrichment(test_tracer, span_capture):
       """Validate that span enrichment works correctly."""
       # Act
       result = process_data({"key": "value"})
       
       # Assert
       spans = span_capture.get_finished_spans()
       assert len(spans) > 0
       
       span = spans[0]
       attributes = dict(span.attributes)
       
       # Validate expected attributes
       assert attributes.get("input.size") == 1
       assert attributes.get("process.type") == "transformation"
       assert attributes.get("output.size") == 2

Testing Error Handling
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @trace(event_type=EventType.tool)
   def risky_operation(value: int) -> int:
       """Operation that may fail."""
       enrich_span({"input.value": value})
       
       if value < 0:
           enrich_span({"error.type": "ValueError"})
           raise ValueError("Value must be non-negative")
       
       result = value * 2
       enrich_span({"output.value": result})
       return result
   
   def test_risky_operation_success(test_tracer):
       """Test successful execution."""
       result = risky_operation(5)
       assert result == 10
   
   def test_risky_operation_failure(test_tracer, span_capture):
       """Test error handling with trace validation."""
       with pytest.raises(ValueError, match="Value must be non-negative"):
           risky_operation(-1)
       
       # Validate error was captured in span
       spans = span_capture.get_finished_spans()
       assert len(spans) > 0
       
       span = spans[0]
       attributes = dict(span.attributes)
       assert attributes.get("error.type") == "ValueError"

Integration Testing
-------------------

Testing LLM Workflows
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # test_llm_workflow.py
   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType
   import openai
   import pytest
   
   @trace(event_type=EventType.chain)
   def llm_workflow(query: str) -> str:
       """Complete LLM workflow."""
       from honeyhive import enrich_span
       
       enrich_span({"workflow.query": query, "workflow.type": "rag"})
       
       # Step 1: Retrieve context
       context = retrieve_context(query)
       
       # Step 2: Generate response
       response = generate_response(query, context)
       
       enrich_span({"workflow.success": True})
       return response
   
   @trace(event_type=EventType.tool)
   def retrieve_context(query: str) -> list:
       """Retrieve relevant context."""
       from honeyhive import enrich_span
       enrich_span({"retrieval.query": query})
       
       # Mock retrieval for testing
       context = ["doc1", "doc2"]
       enrich_span({"retrieval.found": len(context)})
       return context
   
   @trace(event_type=EventType.model)
   def generate_response(query: str, context: list) -> str:
       """Generate LLM response."""
       from honeyhive import enrich_span
       enrich_span({
           "llm.provider": "openai",
           "llm.model": "gpt-4",
           "llm.context_size": len(context)
       })
       
       # For testing, use a mock or test-safe LLM call
       response = f"Response to: {query} (with {len(context)} docs)"
       enrich_span({"llm.response_length": len(response)})
       return response
   
   def test_llm_workflow_integration(test_tracer):
       """Test complete LLM workflow with tracing."""
       query = "What is machine learning?"
       
       result = llm_workflow(query)
       
       assert "Response to:" in result
       assert "machine learning" in result
       # Trace automatically captured with 3 spans (chain + tool + model)

Testing Multi-Provider Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @trace(event_type=EventType.chain)
   def multi_provider_call(prompt: str) -> str:
       """Try multiple LLM providers with fallback."""
       from honeyhive import enrich_span
       
       providers = ["openai", "anthropic"]
       enrich_span({"providers.available": len(providers)})
       
       for i, provider in enumerate(providers):
           try:
               result = call_provider(provider, prompt)
               enrich_span({
                   "providers.used": provider,
                   "providers.attempts": i + 1
               })
               return result
           except Exception as e:
               enrich_span({f"providers.{provider}_failed": str(e)})
               if i == len(providers) - 1:
                   raise
       
       return ""
   
   @trace(event_type=EventType.model)
   def call_provider(provider: str, prompt: str) -> str:
       """Call specific LLM provider."""
       from honeyhive import enrich_span
       enrich_span({"provider.name": provider, "provider.prompt_length": len(prompt)})
       
       # Mock for testing
       if provider == "openai":
           return "OpenAI response"
       elif provider == "anthropic":
           return "Anthropic response"
       else:
           raise ValueError(f"Unknown provider: {provider}")
   
   def test_multi_provider_fallback(test_tracer):
       """Test provider fallback logic."""
       result = multi_provider_call("Test prompt")
       assert result in ["OpenAI response", "Anthropic response"]

Evaluation Testing
------------------

Testing with Evaluation Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # test_evaluation.py
   from honeyhive import HoneyHiveTracer
   import pytest
   
   def test_llm_output_quality(test_tracer):
       """Test LLM output meets quality thresholds."""
       query = "Explain Python decorators"
       response = generate_response(query, [])
       
       # Quality checks
       assert len(response) > 50, "Response too short"
       assert "decorator" in response.lower(), "Key term missing"
       assert not any(word in response.lower() for word in ["sorry", "cannot", "unable"]), \
           "Negative response detected"
       
       # Trace captured automatically for review in HoneyHive dashboard
   
   def test_latency_requirements(test_tracer):
       """Test that operations meet latency requirements."""
       import time
       
       start = time.time()
       result = llm_workflow("Simple query")
       duration = time.time() - start
       
       assert duration < 5.0, f"Operation took {duration:.2f}s, expected < 5s"
       assert result is not None

For comprehensive evaluation testing, see :doc:`evaluation/index`.

Best Practices
--------------

**1. Use Separate Test Projects**

.. code-block:: python

   # ✅ Good: Dedicated test project
   @pytest.fixture
   def test_tracer():
       return HoneyHiveTracer.init(
           api_key=os.getenv("HH_TEST_API_KEY"),
           project="test-project",  # Separate from production
           source="pytest"
       )
   
   # ❌ Bad: Using production project
   # project="production-app"  # DON'T do this

**2. Clean Fixture Management**

.. code-block:: python

   # conftest.py
   @pytest.fixture(scope="session")
   def session_tracer():
       """One tracer for entire test session."""
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_TEST_API_KEY"),
           project="test-project",
           source="pytest-session"
       )
       yield tracer
   
   @pytest.fixture
   def function_tracer():
       """Fresh tracer for each test function."""
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_TEST_API_KEY"),
           project=f"test-{pytest.current_test_name}",
           source="pytest-function"
       )
       yield tracer

**3. Environment-Based Configuration**

.. code-block:: python

   # tests/conftest.py
   import os
   import pytest
   from dotenv import load_dotenv
   
   def pytest_configure(config):
       """Load test environment before tests run."""
       load_dotenv('.env.test')
       
       # Verify test configuration
       if not os.getenv("HH_API_KEY"):
           pytest.exit("HH_API_KEY not set in test environment")
       
       if os.getenv("HH_PROJECT") == "production":
           pytest.exit("Cannot use production project in tests")

**4. Parametrized Testing**

.. code-block:: python

   @pytest.mark.parametrize("input_value,expected_output", [
       (5, 10),
       (0, 0),
       (100, 200),
   ])
   def test_risky_operation_parametrized(test_tracer, input_value, expected_output):
       """Test multiple scenarios with tracing."""
       result = risky_operation(input_value)
       assert result == expected_output

Common Testing Patterns
-----------------------

Pattern 1: Test Helper with Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # test_helpers.py
   from contextlib import contextmanager
   from honeyhive import enrich_span
   import time
   
   @contextmanager
   def assert_trace_timing(max_duration_ms: float):
       """Context manager to validate operation timing."""
       start = time.time()
       
       yield
       
       duration_ms = (time.time() - start) * 1000
       enrich_span({"test.duration_ms": duration_ms})
       
       assert duration_ms < max_duration_ms, \
           f"Operation took {duration_ms:.2f}ms, expected < {max_duration_ms}ms"
   
   # Usage
   def test_with_timing(test_tracer):
       with assert_trace_timing(max_duration_ms=500):
           result = process_data({"key": "value"})

Pattern 2: Trace Assertion Helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def assert_span_has_attributes(span, expected_attrs: dict):
       """Assert span contains expected attributes."""
       actual_attrs = dict(span.attributes)
       
       for key, expected_value in expected_attrs.items():
           actual_value = actual_attrs.get(key)
           assert actual_value == expected_value, \
               f"Attribute {key}: expected {expected_value}, got {actual_value}"
   
   # Usage
   def test_span_attributes(test_tracer, span_capture):
       process_data({"key": "value"})
       
       spans = span_capture.get_finished_spans()
       assert_span_has_attributes(spans[0], {
           "input.size": 1,
           "process.type": "transformation"
       })

Running Tests
-------------

**Basic Test Execution:**

.. code-block:: bash

   # Run all tests with test environment
   pytest tests/ --env-file=.env.test
   
   # Run specific test file
   pytest tests/test_traced_functions.py -v
   
   # Run with coverage
   pytest tests/ --cov=src --cov-report=html

**Test Selection:**

.. code-block:: bash

   # Run only integration tests
   pytest tests/ -m integration
   
   # Run only unit tests
   pytest tests/ -m unit
   
   # Skip slow tests
   pytest tests/ -m "not slow"

**Pytest Markers:**

.. code-block:: python

   import pytest
   
   @pytest.mark.unit
   def test_unit_function(test_tracer):
       """Unit test with tracing."""
       pass
   
   @pytest.mark.integration
   def test_integration_workflow(test_tracer):
       """Integration test with tracing."""
       pass
   
   @pytest.mark.slow
   def test_heavy_processing(test_tracer):
       """Slow test that may be skipped."""
       pass

Next Steps
----------

- :doc:`evaluation/index` - Comprehensive evaluation testing strategies
- :doc:`deployment/production` - Production testing and monitoring
- :doc:`../development/index` - SDK development testing (for contributors)

**Key Takeaway:** Test with real HoneyHive tracing enabled to catch integration issues early. Use pytest fixtures for consistent tracer setup, validate trace attributes programmatically, and maintain separate test projects to avoid polluting production data. ✨

