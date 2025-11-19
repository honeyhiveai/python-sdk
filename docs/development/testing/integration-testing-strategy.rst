Integration Testing Strategy for HoneyHive SDK
==============================================

This document outlines our comprehensive integration testing strategy, particularly focusing on preventing bugs like the ProxyTracerProvider issue that slipped through our initial testing.

Overview
--------

Our testing strategy uses a multi-layered approach:

1. **Unit Tests** - Fast, isolated, heavily mocked
2. **Integration Tests** - Real components, real scenarios  
3. **End-to-End Tests** - Full user workflows
4. **Real Environment Tests** - Subprocess-based testing

The ProxyTracerProvider Bug: Lessons Learned
--------------------------------------------

**What Happened**
~~~~~~~~~~~~~~~~~

A critical bug existed where HoneyHive failed to handle OpenTelemetry's default ``ProxyTracerProvider``, causing instrumentor integration to fail silently.

**Why It Wasn't Caught**
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Over-Mocking**: Our test suite completely mocked OpenTelemetry components
2. **Missing Real Scenarios**: No tests covered "fresh Python environment + instrumentor" scenarios  
3. **Documentation Gap**: Examples didn't follow documented best practices
4. **Integration Test Gaps**: Tests didn't validate real TracerProvider behavior

**The Fix**
~~~~~~~~~~~

.. code-block:: python

   # Fixed: Properly detect and handle ProxyTracerProvider
   is_noop_provider = (
       existing_provider is None
       or str(type(existing_provider).__name__) == "NoOpTracerProvider"
       or str(type(existing_provider).__name__) == "ProxyTracerProvider"  # ← Added this
       or "NoOp" in str(type(existing_provider).__name__)
       or "Proxy" in str(type(existing_provider).__name__)  # ← Added this
   )

Testing Strategy Updates
------------------------

Real Environment Testing
~~~~~~~~~~~~~~~~~~~~~~~~

We now use subprocess-based tests to validate real-world scenarios:

.. code-block:: python

   def test_fresh_environment_proxy_tracer_provider_bug(self):
       """Test ProxyTracerProvider handling in fresh environment."""
       test_script = '''
       from opentelemetry import trace
       from honeyhive.tracer.otel_tracer import HoneyHiveTracer
       
       # Verify we start with ProxyTracerProvider
       initial_provider = trace.get_tracer_provider()
       assert "Proxy" in type(initial_provider).__name__
       
       # Initialize HoneyHive - should handle ProxyTracerProvider
       tracer = HoneyHiveTracer(api_key="test", project="test")
       
       # Should now have real TracerProvider
       final_provider = trace.get_tracer_provider()
       assert "Proxy" not in type(final_provider).__name__

       
       # Run in subprocess for fresh environment
       result = subprocess.run([sys.executable, script_path], ...)

**Benefits:**

- Tests real OpenTelemetry behavior
- Catches environment-specific bugs  
- Validates actual user experience
- No mocking interference

Instrumentor Integration Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

New tests specifically validate instrumentor integration patterns:

.. code-block:: python

   @pytest.mark.real_instrumentor
   def test_real_openai_instrumentor_integration(self):
       """Test with actual OpenInference instrumentor."""
       # Test both initialization patterns:
       # 1. HoneyHive first, then instrumentor (recommended)
       # 2. Instrumentor passed to HoneyHive.init() (legacy)

**Coverage Areas:**

- Fresh environment scenarios
- Multiple TracerProvider types
- Real instrumentor libraries
- Initialization order variations
- Span processor integration

Test Categories and When to Use
-------------------------------

Unit Tests (Fast, Isolated)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use for:**
- Individual function logic
- Error handling paths
- Configuration validation
- Mock-friendly scenarios

**Characteristics:**
- Heavy mocking
- Fast execution (< 1s each)
- No external dependencies
- Isolated components

Integration Tests (Real Components)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use for:**
- Component interaction
- Real API integration  
- TracerProvider scenarios
- Multi-instance behavior

**Characteristics:**
- Minimal mocking
- Real OpenTelemetry components
- Moderate execution time
- External service integration

Real Environment Tests (Subprocess)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use for:**
- Fresh environment scenarios
- Instrumentor integration
- Environment-specific bugs
- User experience validation

**Characteristics:**
- No mocking
- Subprocess execution
- Real library behavior
- Slower but comprehensive

Test Execution Strategy
-----------------------

Local Development
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fast feedback loop
   tox -e unit                    # Unit tests only
   
   # Before committing  
   tox -e integration            # Integration tests
   
   # Full validation
   tox -e unit -e integration    # Complete test suite

CI/CD Pipeline
~~~~~~~~~~~~~~

.. code-block:: yaml

   # GitHub Actions workflow
   - name: Unit Tests
     run: tox -e unit
     
   - name: Integration Tests  
     run: tox -e integration
     
   - name: Real Environment Tests
     run: tox -e real_env
     if: github.event_name == 'pull_request'

**Test Execution Order:**

1. Unit tests (fast feedback)
2. Integration tests (component validation)  
3. Real environment tests (comprehensive validation)
4. End-to-end tests (user workflows)

Preventing Future Bugs
----------------------

Mandatory Test Coverage
~~~~~~~~~~~~~~~~~~~~~~~

**New Features Must Include:**

1. **Unit Tests** - Core logic validation
2. **Integration Tests** - Component interaction  
3. **Real Environment Tests** - User scenario validation
4. **Documentation Examples** - Working code samples

**Quality Gates:**

- All tests must pass
- Coverage >= 80% for new code
- Real environment tests for instrumentor features
- Documentation examples must be tested

Test Review Checklist
~~~~~~~~~~~~~~~~~~~~~

**For New Tests:**

- [ ] Tests real user scenarios?
- [ ] Covers error conditions?  
- [ ] Validates integration points?
- [ ] Uses appropriate test category?
- [ ] Includes cleanup/teardown?

**For Bug Fixes:**

- [ ] Reproduces the original bug?
- [ ] Tests the fix in isolation?
- [ ] Validates fix in real environment?
- [ ] Prevents regression?

Monitoring and Metrics
----------------------

Test Health Metrics
~~~~~~~~~~~~~~~~~~~

**Track:**
- Test execution time trends
- Flaky test identification  
- Coverage percentage changes
- Real environment test success rates

**Alerts:**
- Integration test failures
- Coverage drops below threshold
- Real environment test timeouts
- Instrumentor compatibility issues

**Review Schedule:**
- Weekly: Test health review
- Monthly: Strategy effectiveness assessment
- Quarterly: Coverage and quality analysis

Tools and Infrastructure
------------------------

Testing Tools
~~~~~~~~~~~~~

**Core Testing:**
- pytest (test framework)
- tox (environment management)
- coverage.py (coverage tracking)

**Integration Testing:**
- Real OpenTelemetry components
- Subprocess execution
- Temporary file management

**CI/CD Integration:**
- GitHub Actions workflows
- Automated test execution
- Coverage reporting

Environment Management
~~~~~~~~~~~~~~~~~~~~~~

**Test Environments:**
- Unit: Heavily mocked, fast
- Integration: Real components, moderate
- Real Environment: Subprocess, comprehensive
- Staging: Full user workflows

**Dependency Management:**
- Isolated test dependencies
- Version compatibility testing
- Optional dependency handling

Conclusion
----------

The ProxyTracerProvider bug taught us that comprehensive testing requires:

1. **Multiple Test Layers** - Unit, integration, and real environment
2. **Real Scenario Coverage** - Test actual user workflows
3. **Minimal Mocking** - Use real components when possible  
4. **Subprocess Testing** - Validate fresh environment behavior

This strategy ensures we catch integration bugs early while maintaining fast feedback loops for development.

**Key Takeaway:** *Test the user experience, not just the code.*
