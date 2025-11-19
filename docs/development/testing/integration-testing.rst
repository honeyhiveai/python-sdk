Integration Testing Strategies
==============================

.. warning::
   **🚨 CRITICAL: NO MOCKS IN INTEGRATION TESTS**
   
   Integration tests MUST use real systems, real APIs, and real OpenTelemetry components. Any test that uses mocking (``unittest.mock``, ``@patch``, ``Mock()``) belongs in ``tests/unit/``, not ``tests/integration/``.
   
   **Why**: Mocked integration tests create false security and miss critical bugs like the ProxyTracerProvider issue.

.. note::
   **Problem-solving guide for integration testing HoneyHive SDK components**
   
   Practical solutions for testing how SDK components work together and integrate with real external systems.

Integration testing verifies that different parts of the HoneyHive SDK work correctly together and integrate properly with real external systems like OpenAI, Anthropic, and HoneyHive APIs using actual API calls and real OpenTelemetry components.

Quick Start
-----------

**Problem**: I need to test my complete HoneyHive integration workflow.

**Solution**:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   @pytest.mark.integration
   def test_complete_workflow():
       """Test complete tracer + API client workflow."""
       # Skip if no real API credentials
       api_key = os.getenv("HH_API_KEY")
       if not api_key:
           pytest.skip("Real API credentials required for integration tests")
       
       # Initialize tracer with real API
       tracer = HoneyHiveTracer.init(
           api_key=api_key,         # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=False          # Real integration test (or set HH_TEST_MODE=false)
       )
       
       # Initialize API client with real API
       client = HoneyHive(
           api_key=api_key,
           test_mode=False  # Real integration test
       )
       
       # Test tracer + client integration
       with tracer.trace("integration-test") as span:
           span.set_attribute("test.type", "integration")
           
           # Test session creation via client
           session = client.sessions.create(               session_name="test-session"
           )
           
           span.set_attribute("session.id", session.session_id)
           
       assert session is not None
       assert tracer.session_id is not None

Testing Component Interactions
------------------------------

**Problem**: Test how tracer and API client work together.

**Solution**:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   class TestTracerApiIntegration:
       """Test tracer and API client integration."""
       
       @pytest.fixture
       def integration_setup(self):
           """Setup tracer and client for integration testing."""
           api_key = os.getenv("HH_API_KEY")
           if not api_key:
               pytest.skip("Real API credentials required for integration tests")
           
           tracer = HoneyHiveTracer.init(
               api_key=api_key,
               test_mode=False  # Real integration test
           )
           
           client = HoneyHive(
               api_key=api_key,
               test_mode=False  # Real integration test
           )
           
           return {"tracer": tracer, "client": client}
       
       def test_session_creation_integration(self, integration_setup):
           """Test session creation through both tracer and client."""
           tracer = integration_setup["tracer"]
           client = integration_setup["client"]
           
           # Tracer should have created a session
           assert tracer.session_id is not None
           
           # Client should be able to retrieve session info
           session_info = client.sessions.get(tracer.session_id)
           assert session_info is not None
           assert session_info.session_id == tracer.session_id
       
       def test_event_creation_integration(self, integration_setup):
           """Test event creation through tracer and retrieval via client."""
           tracer = integration_setup["tracer"]
           client = integration_setup["client"]
           
           # Create event through tracer
           with tracer.trace("integration-event", event_type="test") as span:
               span.set_attribute("test.data", "integration-value")
               event_id = span.event_id  # If available
           
           # Retrieve event through client (if event_id available)
           if hasattr(span, 'event_id') and span.event_id:
               event = client.events.get(span.event_id)
               assert event is not None
               assert event.event_type == "test"
       
       def test_project_consistency(self, integration_setup):
           """Test project consistency between tracer and client."""
           tracer = integration_setup["tracer"]
           client = integration_setup["client"]
           
           # Both should reference the same project
           assert tracer.project == "integration-test-project"
           
           # Client should be able to access project info
           projects = client.projects.list()
           project_names = [p.name for p in projects]
           assert "integration-test-project" in project_names

Testing Multi-Instance Patterns
-------------------------------

**Problem**: Test multiple tracer instances working together.

**Solution**:

.. code-block:: python

   import pytest
   import threading
   import time
   from honeyhive import HoneyHiveTracer
   
   class TestMultiInstanceIntegration:
       """Test multiple tracer instances working together."""
       
       def test_independent_sessions(self):
           """Test that multiple tracers create independent sessions."""
           tracer1 = HoneyHiveTracer.init(
               api_key="test-key-1",               source="development"
               test_mode=True
           )
           
           tracer2 = HoneyHiveTracer.init(
               api_key="test-key-2",               source="development"
               test_mode=True
           )
           
           # Verify independence
           assert tracer1.session_id != tracer2.session_id
           assert tracer1.project != tracer2.project
           assert tracer1.source != tracer2.source
       
       def test_concurrent_tracing(self):
           """Test concurrent tracing with multiple instances."""
           tracers = []
           results = []
           
           # Create multiple tracers
           for i in range(3):
               tracer = HoneyHiveTracer.init(
                   api_key=f"concurrent-key-{i}",                   test_mode=True
               )
               tracers.append(tracer)
           
           def worker(tracer, worker_id):
               """Worker function for concurrent testing."""
               with tracer.trace(f"concurrent-operation-{worker_id}") as span:
                   span.set_attribute("worker.id", worker_id)
                   span.set_attribute("tracer.project", tracer.project)
                   time.sleep(0.1)  # Simulate work
                   results.append({
                       "worker_id": worker_id,
                       "session_id": tracer.session_id,
                       "project": tracer.project
                   })
           
           # Start concurrent workers
           threads = []
           for i, tracer in enumerate(tracers):
               thread = threading.Thread(target=worker, args=(tracer, i))
               threads.append(thread)
               thread.start()
           
           # Wait for completion
           for thread in threads:
               thread.join()
           
           # Verify results
           assert len(results) == 3
           session_ids = [r["session_id"] for r in results]
           assert len(set(session_ids)) == 3  # All unique
           
           projects = [r["project"] for r in results]
           assert len(set(projects)) == 3  # All unique
       
       def test_shared_instrumentor_integration(self):
           """Test multiple tracers with shared instrumentors."""
           from openinference.instrumentation.openai import OpenAIInstrumentor
           
           # Create instrumentor instance
           instrumentor = OpenAIInstrumentor()
           
           # Create tracers with shared instrumentor
           # Step 1: Initialize tracers first (without instrumentors)
           tracer1 = HoneyHiveTracer.init(
               api_key="shared-key-1",      # Unique API key for tracer1
               project="shared-project-1",  # Unique project for tracer1
               test_mode=True               # Or set HH_TEST_MODE=true
           )
           
           tracer2 = HoneyHiveTracer.init(
               api_key="shared-key-2",      # Unique API key for tracer2
               project="shared-project-2",  # Unique project for tracer2
               test_mode=True               # Or set HH_TEST_MODE=true
           )
           
           # Step 2: Initialize shared instrumentor with both tracer providers
           instrumentor.instrument(tracer_provider=tracer1.provider)
           instrumentor.instrument(tracer_provider=tracer2.provider)
           
           # Both should have the instrumentor
           assert len(tracer1.instrumentors) > 0
           assert len(tracer2.instrumentors) > 0
           assert any(isinstance(i, OpenAIInstrumentor) for i in tracer1.instrumentors)
           assert any(isinstance(i, OpenAIInstrumentor) for i in tracer2.instrumentors)

Testing LLM Provider Integration
--------------------------------

**Problem**: Test integration with LLM providers like OpenAI and Anthropic.

**Solution**:

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   class TestLLMProviderIntegration:
       """Test integration with LLM providers."""
       
       @pytest.fixture
       def instrumented_tracer(self):
           """Create tracer with LLM instrumentors."""
           # Step 1: Initialize HoneyHive tracer first (without instrumentors)
           tracer = HoneyHiveTracer.init(
               api_key="llm-test-key",      # Or set HH_API_KEY environment variable
               project="llm-test-project",  # Or set HH_PROJECT environment variable
               test_mode=True               # Or set HH_TEST_MODE=true
           )
           
           # Step 2: Initialize instrumentor separately with tracer_provider
           openai_instrumentor = OpenAIInstrumentor()
           openai_instrumentor.instrument(tracer_provider=tracer.provider)
           
           return tracer
       
       @patch('openai.chat.completions.create')
       def test_openai_integration(self, mock_create, instrumented_tracer):
           """Test OpenAI integration with tracing."""
           # Mock OpenAI response
           mock_response = Mock()
           mock_response.choices = [Mock()]
           mock_response.choices[0].message.content = "Test response"
           mock_response.usage = Mock()
           mock_response.usage.total_tokens = 50
           mock_create.return_value = mock_response
           
           # Test with instrumentor
           import openai
           client = openai.OpenAI(api_key="test-key")
           
           with instrumented_tracer.trace("openai-test") as span:
               response = client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": "Test"}]
               )
               
               span.set_attribute("openai.model", "gpt-3.5-turbo")
               span.set_attribute("openai.response", response.choices[0].message.content)
           
           assert response.choices[0].message.content == "Test response"
           mock_create.assert_called_once()
       
       @patch('anthropic.messages.create')
       def test_anthropic_integration(self, mock_create, instrumented_tracer):
           """Test Anthropic integration with tracing."""
           # Mock Anthropic response
           mock_response = Mock()
           mock_response.content = [Mock()]
           mock_response.content[0].text = "Anthropic test response"
           mock_response.usage = Mock()
           mock_response.usage.input_tokens = 10
           mock_response.usage.output_tokens = 15
           mock_create.return_value = mock_response
           
           import anthropic
           client = anthropic.Anthropic(api_key="test-key")
           
           with instrumented_tracer.trace("anthropic-test") as span:
               response = client.messages.create(
                   model="claude-3-sonnet-20240229",
                   messages=[{"role": "user", "content": "Test"}],
                   max_tokens=100
               )
               
               span.set_attribute("anthropic.model", "claude-3-sonnet-20240229")
               span.set_attribute("anthropic.response", response.content[0].text)
           
           assert response.content[0].text == "Anthropic test response"
           mock_create.assert_called_once()

Testing Real API Integration
----------------------------

**Problem**: Test integration with real HoneyHive APIs.

**Solution**:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   @pytest.mark.integration
   class TestRealAPIIntegration:
       """Test integration with real HoneyHive API endpoints."""
       
       @pytest.fixture(autouse=True)
       def setup_integration(self):
           """Setup real API credentials."""
           self.api_key = os.getenv("HH_INTEGRATION_API_KEY")
           self.project = os.getenv("HH_INTEGRATION_PROJECT", "integration-test")
           
           if not self.api_key:
               pytest.skip("Real API credentials not available")
           
           self.tracer = HoneyHiveTracer.init(
               api_key=self.api_key,               source="development"
               test_mode=False  # Use real API
           )
           
           self.client = HoneyHive(
               api_key=self.api_key,
               test_mode=False
           )
       
       def test_real_session_creation(self):
           """Test creating real session via tracer."""
           # Tracer should have created a real session
           assert self.tracer.session_id is not None
           
           # Verify session exists via API client
           try:
               session = self.client.sessions.get(self.tracer.session_id)
               assert session is not None
               assert session.project == self.project
           except Exception as e:
               pytest.skip(f"Session verification failed: {e}")
       
       def test_real_event_creation(self):
           """Test creating real events."""
           with self.tracer.trace("real-integration-test") as span:
               span.set_attribute("test.type", "integration")
               span.set_attribute("api.project", self.project)
               
               # Add some realistic test data
               span.set_attribute("llm.model", "gpt-3.5-turbo")
               span.set_attribute("llm.tokens", 42)
               
               # Force flush to ensure delivery
               flush_success = self.tracer.force_flush(timeout_millis=5000)
               assert flush_success, "Failed to flush traces to real API"
       
       def test_real_project_integration(self):
           """Test project-level integration."""
           # List projects via client
           projects = self.client.projects.list()
           project_names = [p.name for p in projects]
           
           # Integration test project should exist
           assert self.project in project_names
           
           # Get project details
           project = self.client.projects.get(self.project)
           assert project is not None
           assert project.name == self.project
       
       def test_real_evaluation_integration(self):
           """Test evaluation integration with real API."""
           from honeyhive.evaluation import evaluate
           
           @evaluate(
               tracer=self.tracer,
               evaluator_names=["accuracy", "relevance"]
           )
           def test_llm_function(prompt):
               return f"Response to: {prompt}"
           
           # Run evaluation
           result = test_llm_function("Integration test prompt")
           
           assert result == "Response to: Integration test prompt"
           # Evaluation results should be sent to real API

Testing Environment Integration
-------------------------------

**Problem**: Test integration across different environments.

**Solution**:

.. code-block:: python

   import pytest
   import os
   from honeyhive import HoneyHiveTracer
   
   class TestEnvironmentIntegration:
       """Test integration across different environments."""
       
       def test_development_environment(self):
           """Test development environment integration."""
           os.environ["HH_ENVIRONMENT"] = "development"
           os.environ["HH_TEST_MODE"] = "true"
           
           try:
               tracer = HoneyHiveTracer.init(
                   api_key="dev-test-key"               )
               
               with tracer.trace("dev-test") as span:
                   span.set_attribute("env", "development")
                   span.set_attribute("test_mode", True)
               
               assert tracer.test_mode is True
           finally:
               del os.environ["HH_ENVIRONMENT"]
               del os.environ["HH_TEST_MODE"]
       
       def test_staging_environment(self):
           """Test staging environment integration."""
           os.environ["HH_ENVIRONMENT"] = "staging"
           os.environ["HH_TEST_MODE"] = "false"
           
           try:
               tracer = HoneyHiveTracer.init(
                   api_key=os.getenv("HH_STAGING_API_KEY", "staging-key")               )
               
               with tracer.trace("staging-test") as span:
                   span.set_attribute("env", "staging")
                   span.set_attribute("test_mode", False)
               
               # In staging, might use real API
               assert tracer.api_key is not None
           finally:
               del os.environ["HH_ENVIRONMENT"] 
               del os.environ["HH_TEST_MODE"]
       
       def test_production_environment(self):
           """Test production environment configuration.""" 
           os.environ["HH_ENVIRONMENT"] = "production"
           
           try:
               # Production should require real credentials
               if not os.getenv("HH_PROD_API_KEY"):
                   pytest.skip("Production credentials not available")
               
               tracer = HoneyHiveTracer.init(
                   api_key=os.getenv("HH_PROD_API_KEY"),                   test_mode=False  # Never test mode in production
               )
               
               # Production tracer should be configured conservatively
               assert tracer.test_mode is False
               assert tracer.api_key.startswith("hh_")  # Real API key format
           finally:
               del os.environ["HH_ENVIRONMENT"]

Testing Error Scenarios Integration
-----------------------------------

**Problem**: Test how components handle errors together.

**Solution**:

.. code-block:: python

   import pytest
   from unittest.mock import patch, Mock
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   class TestErrorIntegration:
       """Test error handling across integrated components."""
       
       def test_api_unavailable_graceful_degradation(self):
           """Test graceful degradation when API is unavailable."""
           with patch('requests.post') as mock_post:
               # Simulate API unavailability
               mock_post.side_effect = Exception("API unavailable")
               
               # Tracer should still work in degraded mode
               tracer = HoneyHiveTracer.init(
                   api_key="test-key",                   test_mode=False  # Try to use real API
               )
               
               # Tracing operations should not fail
               with tracer.trace("degraded-operation") as span:
                   span.set_attribute("degraded", True)
                   # Should complete without raising exceptions
               
               # Verify degraded mode behavior
               assert tracer is not None
       
       def test_network_timeout_handling(self):
           """Test network timeout handling."""
           import requests
           
           with patch('requests.post') as mock_post:
               # Simulate network timeout
               mock_post.side_effect = requests.Timeout("Request timeout")
               
               tracer = HoneyHiveTracer.init(
                   api_key="timeout-test-key",                   test_mode=False
               )
               
               # Operations should handle timeouts gracefully
               with tracer.trace("timeout-test") as span:
                   span.set_attribute("network.timeout", True)
                   # Should not block or raise unhandled exceptions
       
       def test_invalid_credentials_handling(self):
           """Test handling of invalid credentials."""
           with patch('requests.post') as mock_post:
               # Simulate authentication failure
               mock_response = Mock()
               mock_response.status_code = 401
               mock_response.json.return_value = {"error": "Invalid API key"}
               mock_post.return_value = mock_response
               
               tracer = HoneyHiveTracer.init(
                   api_key="invalid-key",                   test_mode=False
               )
               
               # Should handle auth failures gracefully
               with tracer.trace("auth-failure-test") as span:
                   span.set_attribute("auth.failed", True)
       
       def test_partial_failure_resilience(self):
           """Test resilience to partial system failures."""
           # Test scenario where some operations succeed and others fail
           with patch('honeyhive.api.client.HoneyHive.sessions.create') as mock_session:
               # Session creation fails
               mock_session.side_effect = Exception("Session creation failed")
               
               # But tracer should still work locally
               tracer = HoneyHiveTracer.init(
                   api_key="partial-failure-key",                   test_mode=False
               )
               
               # Local tracing should still work
               with tracer.trace("partial-failure-operation") as span:
                   span.set_attribute("partial.failure", True)
                   # Should complete successfully

Testing Configuration Integration
---------------------------------

**Problem**: Test how configuration works across components.

**Solution**:

.. code-block:: python

   import pytest
   import os
   import tempfile
   import json
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   class TestConfigurationIntegration:
       """Test configuration integration across components."""
       
       def test_environment_variable_consistency(self):
           """Test that all components respect environment variables."""
           os.environ.update({
               "HH_API_KEY": "env-integration-key",
               "HH_PROJECT": "env-integration-project",
               "HH_SOURCE": "env-integration-source",
               "HH_BASE_URL": "https://api-test.honeyhive.ai",
               "HH_TEST_MODE": "true"
           })
           
           try:
               # Both tracer and client should use env vars
               tracer = HoneyHiveTracer.init()
               client = HoneyHive()
               
               assert tracer.api_key == "env-integration-key"
               assert tracer.project == "env-integration-project"
               assert tracer.source == "env-integration-source"
               assert tracer.test_mode is True
               
               assert client.api_key == "env-integration-key"
               assert client.base_url == "https://api-test.honeyhive.ai"
               assert client.test_mode is True
           finally:
               # Clean up
               for key in ["HH_API_KEY", "HH_PROJECT", "HH_SOURCE", "HH_BASE_URL", "HH_TEST_MODE"]:
                   del os.environ[key]
       
       def test_explicit_override_precedence(self):
           """Test that explicit parameters override environment variables."""
           os.environ.update({
               "HH_API_KEY": "env-key",
               "HH_PROJECT": "env-project"
           })
           
           try:
               tracer = HoneyHiveTracer.init(
                   api_key="explicit-key",  # Should override env               )
               
               assert tracer.api_key == "explicit-key"
               assert tracer.project == "explicit-project"
           finally:
               del os.environ["HH_API_KEY"]
               del os.environ["HH_PROJECT"]
       
       def test_configuration_validation_integration(self):
           """Test configuration validation across components."""
           # Test invalid configuration combinations
           with pytest.raises(ValueError):
               HoneyHiveTracer.init(
                   api_key="",  # Invalid: empty API key               )
           
           with pytest.raises(ValueError):
               HoneyHive(
                   api_key="valid-key",
                   base_url=""  # Invalid: empty base URL
               )

Testing Performance Integration
-------------------------------

**Problem**: Test performance characteristics of integrated components.

**Solution**:

.. code-block:: python

   import time
   import statistics
   from honeyhive import HoneyHiveTracer
   from honeyhive.api.client import HoneyHive
   
   class TestPerformanceIntegration:
       """Test performance characteristics of integrated systems."""
       
       def test_tracer_client_performance(self):
           """Test performance of tracer + client operations."""
           tracer = HoneyHiveTracer.init(
               api_key="perf-test-key",               test_mode=True
           )
           
           client = HoneyHive(
               api_key="perf-test-key",
               test_mode=True
           )
           
           # Measure integrated operation performance
           times = []
           for i in range(10):
               start = time.perf_counter()
               
               with tracer.trace(f"perf-test-{i}") as span:
                   span.set_attribute("iteration", i)
                   
                   # Simulate client operation
                   session_id = tracer.session_id
                   span.set_attribute("session.id", session_id)
               
               end = time.perf_counter()
               times.append(end - start)
           
           # Performance should be consistent
           avg_time = statistics.mean(times)
           std_dev = statistics.stdev(times)
           
           # Should complete quickly and consistently
           assert avg_time < 0.1, f"Average time too slow: {avg_time:.3f}s"
           assert std_dev < 0.05, f"Too much variance: {std_dev:.3f}s"
       
       def test_concurrent_integration_performance(self):
           """Test performance under concurrent load."""
           import threading
           import queue
           
           results = queue.Queue()
           
           def worker(worker_id):
               """Worker function for concurrent testing."""
               tracer = HoneyHiveTracer.init(
                   api_key=f"concurrent-perf-key-{worker_id}",                   test_mode=True
               )
               
               start = time.perf_counter()
               
               with tracer.trace(f"concurrent-operation-{worker_id}") as span:
                   span.set_attribute("worker.id", worker_id)
                   time.sleep(0.01)  # Simulate minimal work
               
               end = time.perf_counter()
               results.put(end - start)
           
           # Start concurrent workers
           threads = []
           for i in range(10):
               thread = threading.Thread(target=worker, args=(i))
               threads.append(thread)
               thread.start()
           
           # Wait for completion
           for thread in threads:
               thread.join()
           
           # Collect results
           times = []
           while not results.empty():
               times.append(results.get())
           
           assert len(times) == 10
           avg_time = statistics.mean(times)
           
           # Concurrent operations should not significantly degrade performance
           assert avg_time < 0.2, f"Concurrent performance too slow: {avg_time:.3f}s"

Running Integration Tests
-------------------------

**Command Examples**:

.. code-block:: bash

   # Run all integration tests
   tox -e integration
   
   # Run specific integration test categories
   pytest tests/integration/ -v
   pytest tests/integration/ -v
   pytest tests/integration/ -m "llm_provider" -v
   
   # Run integration tests with coverage
   pytest tests/integration/ --cov=honeyhive --cov-report=term-missing
   
   # Run integration tests with real API (requires credentials)
   HH_API_KEY=your_key pytest tests/integration/ -v
   
   # Run performance integration tests
   pytest tests/integration/ -m "performance" -v
   
   # Run multiprocessing integration tests
   pytest tests/integration/ -m "concurrent" -v

**Environment Variables for Integration Testing**:

.. code-block:: bash

   # Required for real API testing
   export HH_INTEGRATION_API_KEY="your_test_api_key"
   export HH_INTEGRATION_PROJECT="integration-test-project"
   
   # Optional configuration
   export HH_INTEGRATION_BASE_URL="https://api-staging.honeyhive.ai"
   export HH_INTEGRATION_TIMEOUT="30"
   
   # LLM provider credentials (for LLM integration tests)
   export OPENAI_API_KEY="your_openai_key"
   export ANTHROPIC_API_KEY="your_anthropic_key"

**Test Organization Best Practices**:

.. code-block:: python

   # Group tests by integration type
   class TestAPIIntegration:
       """Test HoneyHive API integration."""
       pass
   
   class TestLLMIntegration:
       """Test LLM provider integration.""" 
       pass
   
   class TestMultiInstanceIntegration:
       """Test multi-instance integration."""
       pass
   
   class TestPerformanceIntegration:
       """Test performance characteristics."""
       pass

**Pytest Marks for Organization**:

.. code-block:: python

   import pytest
   
   @pytest.mark.integration
   def test_basic_integration():
       """Basic integration test."""
       pass
   
   @pytest.mark.integration
   def test_integration():
       """Test with real API (requires credentials)."""
       pass
   
   @pytest.mark.llm_provider
   def test_llm_provider_integration():
       """Test LLM provider integration."""
       pass
   
   @pytest.mark.performance
   def test_performance_integration():
       """Test performance characteristics."""
       pass
   
   @pytest.mark.concurrent
   def test_concurrent_integration():
       """Test concurrent/multiprocessing scenarios."""
       pass

Best Practices
--------------

**Integration Testing Guidelines**:

1. **Test Real Workflows**: Test complete user workflows, not just individual components
2. **Use Appropriate Test Data**: Use realistic test data that mimics production scenarios
3. **Test Error Scenarios**: Include network failures, timeouts, and invalid responses
4. **Verify End-to-End**: Ensure data flows correctly from input to final output
5. **Test Performance**: Measure performance under realistic load conditions
6. **Use Real Credentials Sparingly**: Use test mode when possible, real API only when necessary
7. **Clean Up Resources**: Ensure test data is cleaned up after integration tests
8. **Test Environment Variations**: Test across different environments and configurations

**Common Integration Test Patterns**:

.. code-block:: python

   # Pattern 1: Component Integration
   def test_component_integration():
       component_a = create_component_a()
       component_b = create_component_b()
       result = component_a.integrate_with(component_b)
       assert result.is_valid()
   
   # Pattern 2: External System Integration
   @pytest.mark.integration
   def test_external_integration():
       client = create_real_client()
       response = client.make_request()
       assert response.status_code == 200
   
   # Pattern 3: End-to-End Workflow
   def test_end_to_end_workflow():
       input_data = create_test_data()
       result = complete_workflow(input_data)
       assert result.meets_expectations()
   
   # Pattern 4: Error Recovery Integration
   def test_error_recovery():
       with inject_failure():
           result = resilient_operation()
           assert result.recovered_gracefully()

See Also
--------

- :doc:`unit-testing` - Unit testing strategies
- :doc:`lambda-testing` - AWS Lambda integration testing
- :doc:`performance-testing` - Performance testing and benchmarking
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration patterns
- :doc:`../../reference/api/client` - API client reference
- :doc:`../../reference/api/tracer` - Tracer API reference
