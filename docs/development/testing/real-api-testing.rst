Real API Integration Testing
=============================

This document describes the comprehensive real API integration testing framework designed to validate HoneyHive SDK integration with real services and catch bugs that mocked tests miss, including ProxyTracerProvider issues and non-instrumentor integration patterns.

Overview
--------

The HoneyHive SDK now supports comprehensive real API integration testing:

1. **Mocked Tests** (default) - Fast unit tests with OpenTelemetry mocking
2. **Real API Tests** - Integration tests using real OpenTelemetry components and API calls
3. **Non-Instrumentor Integration Tests** - Tests for frameworks that use OpenTelemetry directly (e.g., AWS Strands)

The real API tests are designed to catch bugs like:

- ProxyTracerProvider not being handled correctly
- Instrumentor integration failures
- Real OpenTelemetry behavior issues
- Actual API communication problems
- Provider detection and replacement issues
- Initialization order dependencies
- Multi-agent session continuity problems

Configuration
-------------

Local Development
~~~~~~~~~~~~~~~~~

For local development, create a ``.env.integration`` file in the project root:

.. code-block:: bash

   # Required: HoneyHive API credentials
   HH_API_KEY=your_honeyhive_api_key_here
   # Note: HH_PROJECT is deprecated - project is now derived from API key
   
   # Optional: HoneyHive configuration
   HH_SOURCE=pytest-integration
   HH_API_URL=https://api.honeyhive.ai
   
   # Optional: LLM Provider API Keys for Real Instrumentor Testing
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

CI/CD Environment
~~~~~~~~~~~~~~~~~

In CI/CD environments, set these as environment variables:

.. code-block:: yaml

   # GitHub Actions example
   env:
     HH_API_KEY: ${{ secrets.HH_API_KEY }}
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
     ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

Running Tests
-------------

Unit Tests (Mocked)
~~~~~~~~~~~~~~~~~~~

Default behavior - uses mocking to prevent real API calls:

.. code-block:: bash

   # Run all unit tests with mocking
   tox -e unit
   
   # Run specific unit test
   pytest tests/unit/test_tracer.py

Integration Tests (Real API)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses real API credentials and OpenTelemetry components:

.. code-block:: bash

   # Run all integration tests
   tox -e integration
   
   # Run only real API tests
   tox -e real-api
   
   # Run specific real API test
   pytest tests/integration/test_real_instrumentor_integration_comprehensive.py -m real_api

Test Markers
------------

The testing framework uses pytest markers to control test behavior:

- ``@pytest.mark.real_api`` - Requires real HoneyHive API credentials
- ``@pytest.mark.real_instrumentor`` - Tests real instrumentor integration
- ``@pytest.mark.openai_required`` - Requires OpenAI API key
- ``@pytest.mark.anthropic_required`` - Requires Anthropic API key

Example:

.. code-block:: python

   @pytest.mark.real_api
   @pytest.mark.openai_required
   def test_real_openai_integration(real_honeyhive_tracer, provider_api_keys):
       # This test will be skipped if HH_API_KEY or OPENAI_API_KEY is missing
       pass

Test Fixtures
-------------

Real API Fixtures
~~~~~~~~~~~~~~~~~

- ``real_api_credentials`` - Loads credentials from .env or environment
- ``real_honeyhive_tracer`` - Creates tracer with real OpenTelemetry (no mocking)
- ``fresh_tracer_environment`` - Fresh tracer with reset OpenTelemetry state
- ``provider_api_keys`` - Dictionary of LLM provider API keys
- ``no_mocking_context`` - Ensures no OpenTelemetry mocking is active

Conditional Mocking
~~~~~~~~~~~~~~~~~~~

The ``conditional_disable_tracing`` fixture automatically:

- **Enables mocking** for regular unit tests (fast, no I/O)
- **Disables mocking** for tests marked with ``@pytest.mark.real_api``

This ensures real API tests use actual OpenTelemetry behavior.

Key Test Scenarios
------------------

ProxyTracerProvider Bug Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests that reproduce the exact bug scenario:

.. code-block:: python

   def test_proxy_tracer_provider_bug_detection(fresh_tracer_environment):
       """Test that we properly handle ProxyTracerProvider in fresh environments."""
       tracer = fresh_tracer_environment
       
       # Verify we have a real TracerProvider, not ProxyTracerProvider
       provider_type = type(tracer.provider).__name__
       assert "TracerProvider" in provider_type
       assert "Proxy" not in provider_type

Subprocess Testing
~~~~~~~~~~~~~~~~~~

Tests in completely fresh Python environments:

.. code-block:: python

   def test_subprocess_fresh_environment_integration(real_api_credentials):
       """Test instrumentor integration in a completely fresh subprocess."""
       # Creates and runs a test script in subprocess
       # Catches issues that persist even with fixture cleanup

Real Instrumentor Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests with actual LLM API calls:

.. code-block:: python

   @pytest.mark.openai_required
   def test_real_openai_instrumentor_integration(fresh_tracer_environment, provider_api_keys):
       """Test real OpenAI instrumentor integration with actual API calls."""
       # Makes real OpenAI API call with instrumentor
       # Verifies traces are captured correctly

Benefits
--------

This testing approach provides:

1. **Bug Detection** - Catches real-world integration issues
2. **Confidence** - Tests actual behavior, not mocked behavior  
3. **Flexibility** - Supports both local development and CI/CD
4. **Efficiency** - Mocked tests remain fast, real tests run when needed
5. **Comprehensive** - Tests complete workflows end-to-end

Troubleshooting
---------------

Test Skipping
~~~~~~~~~~~~~

If tests are being skipped:

.. code-block:: bash

   # Check if credentials are available
   echo $HH_API_KEY
   
   # Run with verbose output to see skip reasons
   pytest tests/integration -v -s

Missing Dependencies
~~~~~~~~~~~~~~~~~~~~

If instrumentor tests fail:

.. code-block:: bash

   # Install instrumentor dependencies
   pip install openinference-instrumentation-openai
   pip install openinference-instrumentation-anthropic
   
   # Or use the real-api tox environment
   tox -e real-api

API Rate Limits
~~~~~~~~~~~~~~~

Real API tests may hit rate limits:

- Use test-specific API keys with higher limits
- Run tests sequentially: ``pytest -n 1``
- Add delays between tests if needed

Best Practices
--------------

1. **Use Real Tests Sparingly** - Only for integration scenarios that need real behavior
2. **Mock by Default** - Keep unit tests fast with mocking
3. **Secure Credentials** - Never commit API keys to version control
4. **Test Isolation** - Use fresh fixtures to prevent test pollution
5. **Clear Markers** - Mark tests clearly with required dependencies

This framework ensures that bugs like the ProxyTracerProvider issue are caught early while maintaining fast unit test performance.

Non-Instrumentor Integration Testing
====================================

The non-instrumentor integration tests validate frameworks that use OpenTelemetry directly (rather than through traditional instrumentors) with real API calls to both HoneyHive and the target services. AWS Strands serves as the primary example and prototype for this integration pattern.

Prerequisites
-------------

Non-Instrumentor Framework Testing Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Required: HoneyHive API credentials
   export HH_API_KEY="your_honeyhive_api_key"
   export HH_PROJECT="your_project_name"  # Required for OTLP tracing
   
   # Install framework dependencies (example: AWS Strands)
   pip install strands-agents  # For AWS Strands integration tests
   
   # Install test dependencies
   pip install pytest pytest-timeout

Optional Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # For custom API endpoints
   export HH_API_URL="https://api.honeyhive.ai"
   
   # For debugging
   export HH_DEBUG_MODE=true
   
   # For OTLP configuration
   export HH_OTLP_ENABLED=true

Running Non-Instrumentor Integration Tests
-------------------------------------------

Quick Start
~~~~~~~~~~~

.. code-block:: bash

   # Run all non-instrumentor integration tests
   pytest tests/integration/ -m real_api -k "non_instrumentor" -v
   
   # Run specific framework tests (example: AWS Strands)
   pytest tests/integration/test_non_instrumentor_real_api_integration.py --real-api -v

Manual Test Execution
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test initialization order scenarios (example with AWS Strands)
   pytest tests/integration/test_non_instrumentor_real_api_integration.py::TestNonInstrumentorRealAPIIntegration::test_honeyhive_first_strands_second_real_api -v --real-api
   
   # Test concurrent initialization
   pytest tests/integration/test_non_instrumentor_real_api_integration.py::TestNonInstrumentorRealAPIIntegration::test_concurrent_initialization_real_api -v --real-api
   
   # Test multi-instance scenarios
   pytest tests/integration/test_non_instrumentor_real_api_integration.py::TestNonInstrumentorRealAPIIntegration::test_multi_agent_session_real_api -v --real-api
   
   # Run all non-instrumentor integration tests
   pytest tests/integration/ -m real_api -k "non_instrumentor or strands" -v

Test Scenarios
--------------

1. HoneyHive First, Framework Second
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Initializes HoneyHive tracer first (becomes main provider)
- Creates framework instance (e.g., AWS Strands agent) using existing provider
- Executes real API call through framework
- Validates spans are traced to HoneyHive

2. Framework First, HoneyHive Second
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Initializes framework first (may set ProxyTracerProvider)
- Initializes HoneyHive tracer (detects and integrates)
- Executes real API call through framework with HoneyHive tracing
- Validates integration strategy based on framework's provider type

3. Concurrent Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Starts HoneyHive and framework initialization in separate threads
- Validates thread-safe integration
- Ensures no race conditions or conflicts

4. Multi-Instance Session
~~~~~~~~~~~~~~~~~~~~~~~~~

- Creates multiple framework instances in single HoneyHive session
- Executes different types of operations
- Validates session continuity across instances
- Confirms unified tracing

5. Error Handling
~~~~~~~~~~~~~~~~~

- Tests various error scenarios (empty input, long input, special characters)
- Validates graceful degradation
- Ensures tracer remains functional after errors

6. Performance Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

- Measures initialization overhead
- Times multiple API operations
- Validates performance requirements are met
- Confirms minimal integration overhead

Expected Behavior
-----------------

Provider Detection Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario A: HoneyHive First**

.. code-block:: text

   🔧 Provider Detection: NoOpTracerProvider -> main_provider
   🔧 Creating new TracerProvider as main provider
   ✅ Added HoneyHive span processor to new provider

**Scenario B: Framework First (Proxy)**

.. code-block:: text

   🔧 Provider Detection: ProxyTracerProvider -> main_provider  
   🔧 Creating new TracerProvider as main provider (replaced placeholder)
   ✅ Added HoneyHive span processor to new provider

**Scenario C: Framework First (Real Provider)**

.. code-block:: text

   🔧 Provider Detection: TracerProvider -> secondary_provider
   🔧 Using existing TracerProvider: TracerProvider
   ✅ Successfully integrated with existing provider

Integration Success Indicators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ✅ **Provider Detection**: Correct strategy selected based on existing provider
- ✅ **Span Processor Integration**: HoneyHive processor added without errors
- ✅ **API Call Success**: Real API calls complete successfully
- ✅ **Trace Export**: Spans exported to HoneyHive backend
- ✅ **Performance**: Initialization < 5s, operations < 30s average
- ✅ **Error Resilience**: Graceful handling of API failures

Troubleshooting Non-Instrumentor Integration Tests
---------------------------------------------------

Common Issues
~~~~~~~~~~~~~

**API Key Issues**

.. code-block:: text

   Error: 401 Unauthorized

**Solution**: Verify ``HH_API_KEY`` is set and valid

**Framework Installation Issues**

.. code-block:: text

   ImportError: No module named 'strands'  # or other framework

**Solution**: Install framework dependencies (e.g., ``pip install strands-agents`` for AWS Strands)

**Network/Timeout Issues**

.. code-block:: text

   TimeoutError: API call timed out

**Solution**: Check network connectivity, increase timeout in test config

**Rate Limiting**

.. code-block:: text

   Error: 429 Too Many Requests

**Solution**: Add delays between tests, use different API keys for parallel testing

Debug Mode
~~~~~~~~~~

Enable debug logging for detailed integration information:

.. code-block:: bash

   export HH_DEBUG_MODE=true
   pytest tests/integration/test_non_instrumentor_real_api_integration.py -v -s

Test Configuration
~~~~~~~~~~~~~~~~~~

Modify test timeouts and retry behavior in ``conftest.py``:

.. code-block:: python

   @pytest.fixture
   def integration_test_config():
       return {
           "timeout": 60,      # Increase for slow networks
           "retry_count": 5,   # More retries for flaky connections
           "test_project": "your-test-project",
           "test_source": "your-test-environment",
       }

CI/CD Integration
-----------------

Real API tests should be integrated into the main testing workflow, not run as separate jobs. This ensures comprehensive validation of all integration patterns.

GitHub Actions Integration Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Integration Tests
   
   on:
     schedule:
       - cron: '0 6 * * *'  # Daily at 6 AM
     workflow_dispatch:
     pull_request:
       paths:
         - 'src/**'
         - 'tests/integration/**'
   
   jobs:
     integration-tests:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             pip install -e .
             pip install pytest pytest-timeout
             # Install optional integration dependencies
             pip install strands-agents || echo "Strands not available"
             pip install openinference-instrumentation-openai || echo "OpenInference not available"
         - name: Run All Integration Tests
           env:
             HH_API_KEY: ${{ secrets.HH_API_KEY }}
             HH_PROJECT: ${{ secrets.HH_PROJECT }}
             OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
             ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
           run: |
             # Run all real API integration tests
             pytest tests/integration/ -m real_api -v --tb=short
             # Run specific non-instrumentor integration tests
             pytest tests/integration/test_*_real_api_integration.py -v --tb=short

Local Development
~~~~~~~~~~~~~~~~~

For local development, create a ``.env`` file:

.. code-block:: bash

   # .env (add to .gitignore)
   HH_API_KEY=your_api_key_here
   HH_PROJECT=your_project_name
   HH_DEBUG_MODE=true
   
   # Optional: LLM provider keys for comprehensive testing
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key

Load and run all integration tests:

.. code-block:: bash

   source .env
   
   # Run all real API integration tests
   pytest tests/integration/ -m real_api -v
   
   # Run specific integration test categories
   pytest tests/integration/ -m "real_api and not slow" -v
   
   # Run with comprehensive logging
   pytest tests/integration/ -m real_api -v -s --tb=short

Contributing to Real API Integration Tests
--------------------------------------------

When adding new real API integration tests (including non-instrumentor frameworks like AWS Strands):

1. **Mark with ``@pytest.mark.real_api``** decorator
2. **Check for API key availability** in ``setup_method()``
3. **Handle API failures gracefully** - don't fail tests due to network issues
4. **Validate integration success** even if API calls fail
5. **Include performance assertions** for timing requirements
6. **Add comprehensive logging** for debugging

Test Template
~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.integration
   @pytest.mark.real_api
   def test_new_integration_scenario_real_api(self):
       """Test description for any real API integration."""
       # Check prerequisites
       if not self.api_key:
           pytest.skip("API key required")
       
       # Initialize components
       tracer = HoneyHiveTracer.init(
           api_key=self.api_key,
           project=self.project,
           test_mode=False
       )
       
       # Execute real API operations (example with optional framework)
       try:
           # Example: AWS Strands
           from strands import Agent
           agent = Agent(system_prompt="You are a helpful assistant")
           result = asyncio.run(agent.invoke_async("Test query"))
           
           # Example: OpenAI
           # import openai
           # client = openai.OpenAI()
           # result = client.chat.completions.create(...)
           
           # Validate result
           assert result is not None
       except ImportError:
           pytest.skip("Optional integration framework not available")
       except Exception as e:
           # Handle gracefully - still validate integration
           print(f"⚠️  API call failed: {e}")
       
       # Validate integration regardless of API success
       assert tracer.provider is not None
       assert tracer.span_processor is not None

Support
-------

For issues with real API integration tests:

1. **Check Prerequisites**: API keys, framework installations, network connectivity
2. **Review Logs**: Enable debug mode for detailed information
3. **Validate Separately**: Test HoneyHive and external services independently
4. **Check Documentation**: Refer to HoneyHive and third-party framework documentation
5. **Report Issues**: Include full logs, environment details, and framework versions

Common Integration Frameworks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **AWS Strands**: Non-instrumentor AI framework integration
- **OpenAI**: Direct API integration with instrumentors
- **Anthropic**: Claude API integration with instrumentors
- **Custom Frameworks**: Any framework using OpenTelemetry directly
