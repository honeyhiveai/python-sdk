Real API Integration Testing
=============================

This document describes the real API integration testing framework designed to catch bugs that mocked tests miss, such as the ProxyTracerProvider issue.

Overview
--------

The HoneyHive SDK now supports two types of testing:

1. **Mocked Tests** (default) - Fast unit tests with OpenTelemetry mocking
2. **Real API Tests** - Integration tests using real OpenTelemetry components and API calls

The real API tests are designed to catch bugs like:

- ProxyTracerProvider not being handled correctly
- Instrumentor integration failures
- Real OpenTelemetry behavior issues
- Actual API communication problems

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
