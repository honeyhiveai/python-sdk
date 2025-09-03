SDK Testing Best Practices
===========================

.. note::
   **For HoneyHive SDK Developers and Contributors**
   
   This guide covers testing practices for developing the HoneyHive Python SDK itself, not for testing applications that use the SDK.

This section provides testing standards, practices, and tools used in HoneyHive Python SDK development. All contributors must follow these testing practices to maintain code quality and reliability.

SDK Development Testing Setup
------------------------------

**Setup**: Configure your development environment for SDK testing.

**Required Setup**:

.. code-block:: bash

   # 1. Set up development environment (required first step)
   ./scripts/setup-dev.sh
   
   # 2. Verify setup with basic tests
   tox -e unit
   
   # 3. Run integration tests
   tox -e integration
   
   # 4. Check code coverage (minimum 60% required)
   tox -e unit -- --cov=honeyhive --cov-report=html --cov-fail-under=60

.. toctree::
   :maxdepth: 2
   
   unit-testing
   integration-testing
   lambda-testing
   performance-testing
   mocking-strategies
   ci-cd-integration
   troubleshooting-tests

Testing Overview
----------------

**Current Test Infrastructure**:

- **Total Tests**: 881+ tests (100% success rate)
- **Test Coverage**: 72.95% (above 70% requirement ✅)
- **Test Types**: Unit, Integration, Lambda, Performance, Real API
- **CI/CD Integration**: GitHub Actions with automated quality gates
- **Lambda Testing**: AWS Lambda compatibility and performance validation

**Testing Strategy**:

The HoneyHive SDK employs a **three-tier testing strategy**:

1. **Continuous Testing** (Every PR/Push) - Docker simulation, unit/integration tests
2. **Daily Scheduled Testing** - Real AWS Lambda deployment validation  
3. **Release Candidate Testing** - Full comprehensive validation

Quick Solutions
---------------

**Problem: Test SDK Integration**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   def test_basic_integration():
       tracer = HoneyHiveTracer.init(
           api_key="test-key",
           project="test-project",
           test_mode=True  # Important: enables test mode
       )
       
       with tracer.trace("test-operation") as span:
           span.set_attribute("test.type", "integration")
           assert span is not None

**Problem: Mock HoneyHive for Testing**

.. code-block:: python

   from unittest.mock import Mock, patch
   
   def test_with_mock_tracer():
       with patch('honeyhive.HoneyHiveTracer') as mock_tracer:
           mock_tracer.init.return_value = Mock()
           
           # Your application code here
           result = your_function_that_uses_honeyhive()
           
           # Verify tracer was used
           mock_tracer.init.assert_called_once()

**Problem: Test Lambda Performance**

.. code-block:: bash

   # Navigate to Lambda testing
   cd tests/lambda
   
   # Build test containers
   make build
   
   # Run performance tests
   make test-performance

**Problem: Test Multi-Instance Tracers**

.. code-block:: python

   def test_multiple_tracers():
       tracer1 = HoneyHiveTracer.init(
           api_key="key1", project="project1", test_mode=True
       )
       tracer2 = HoneyHiveTracer.init(
           api_key="key2", project="project2", test_mode=True
       )
       
       # Verify independence
       assert tracer1.session_id != tracer2.session_id
       assert tracer1.project != tracer2.project

Code Quality Requirements
-------------------------

**⚠️ MANDATORY Development Setup**:

.. code-block:: bash

   # Required one-time setup for all developers
   ./scripts/setup-dev.sh

**Pre-Commit Verification** (required before every commit):

.. code-block:: bash

   # Mandatory verification
   tox -e format && tox -e lint

**Automated Quality Enforcement**:

- **Black formatting**: 88-character lines, applied automatically
- **Import sorting**: isort with black profile
- **Static analysis**: pylint + mypy type checking
- **YAML validation**: yamllint with 120-character lines
- **Documentation verification**: Sphinx build and synchronization checks

Testing Commands
----------------

**Run Specific Test Types**:

.. code-block:: bash

   # Unit tests only
   tox -e unit
   
   # Integration tests only
   tox -e integration
   
   # Lambda compatibility tests
   cd tests/lambda && make test-lambda
   
   # Performance tests
   cd tests/lambda && make test-performance
   
   # Real API tests (requires credentials)
   pytest -m real_api -v
   
   # Specific test file
   pytest tests/test_tracer.py -v
   
   # With coverage
   pytest --cov=honeyhive --cov-report=term-missing

**Quality Gates**:

.. code-block:: bash

   # Format verification
   tox -e format
   
   # Lint verification
   tox -e lint
   
   # Documentation build
   tox -e docs

Test Environment Setup
----------------------

**Basic Test Configuration**:

.. code-block:: python

   # Test configuration
   test_tracer = HoneyHiveTracer.init(
       api_key="test-api-key",
       project="test-project",
       source="development"
       test_mode=True,  # Enable test mode
       disable_http_tracing=True  # Optimize for testing
   )

**Environment Variables for Testing**:

.. code-block:: bash

   # Set test environment variables
   export HH_API_KEY="test-key"
   export HH_PROJECT="test-project" 
   export HH_SOURCE="test"
   export HH_TEST_MODE="true"

**Multi-Environment Testing**:

.. code-block:: python

   def create_test_tracer(environment="test"):
       config = {
           "test": {
               "api_key": "test-key",
               "project": "test-project",
               "test_mode": True
           },
           "integration": {
               "api_key": os.getenv("HH_INTEGRATION_KEY"),
               "project": "integration-project", 
               "test_mode": False
           }
       }
       
       return HoneyHiveTracer.init(**config[environment])

Performance Testing
-------------------

**Lambda Performance Validation**:

- **Cold Start Target**: < 500ms (actual: ~281ms ✅)
- **Warm Start Target**: < 100ms (actual: ~52ms ✅)
- **Memory Overhead**: < 50MB (actual: <50MB ✅)
- **Success Rate**: > 95% (actual: >95% ✅)

**Local Performance Testing**:

.. code-block:: python

   import time
   
   def test_tracing_overhead():
       # Measure baseline performance
       start = time.time()
       for _ in range(1000):
           simple_operation()
       baseline = time.time() - start
       
       # Measure with tracing
       @trace(tracer=test_tracer)
       def traced_operation():
           return simple_operation()
       
       start = time.time()
       for _ in range(1000):
           traced_operation()
       traced_time = time.time() - start
       
       # Verify minimal overhead
       overhead_ratio = traced_time / baseline
       assert overhead_ratio < 2.0  # Less than 2x overhead

Best Practices
--------------

**Testing Guidelines**:

1. **Always Use Test Mode**: Set ``test_mode=True`` for testing
2. **Mock External Dependencies**: Mock API calls and external services
3. **Test Error Scenarios**: Test both success and failure cases
4. **Verify Span Attributes**: Check that spans have correct attributes
5. **Test Performance Impact**: Ensure tracing doesn't significantly impact performance
6. **Clean Up Resources**: Clean up test resources after each test
7. **Test Multi-Instance Patterns**: Verify multiple tracers work independently
8. **Maintain Coverage**: Keep test coverage above 70% threshold

**Test Organization**:

.. code-block:: python

   class TestTracerFunctionality:
       """Group related tracer tests."""
       
       def test_initialization(self):
           """Test basic initialization."""
           pass
       
       def test_span_creation(self):
           """Test span creation and management."""
           pass
       
       def test_error_handling(self):
           """Test error scenarios."""
           pass

**Naming Conventions**:

- Test files: ``test_<module>_<file>.py``
- Test classes: ``TestModuleFunctionality``
- Test methods: ``test_specific_behavior``

See Also
--------

- :doc:`unit-testing` - Unit testing strategies and examples
- :doc:`integration-testing` - Integration testing patterns
- :doc:`lambda-testing` - AWS Lambda testing guide
- :doc:`performance-testing` - Performance testing and benchmarking
- :doc:`../../tutorials/advanced-setup` - Advanced testing configurations
- :doc:`../../reference/configuration/environment-vars` - Test environment configuration
