GitHub Actions CI/CD Testing
============================

.. note::
   **Internal HoneyHive SDK Development - GitHub Actions Workflows**
   
   Best practices and workflows for HoneyHive SDK testing in our GitHub Actions CI/CD pipeline. For SDK contributors and maintainers.

This guide covers our internal GitHub Actions workflows for automated testing of the HoneyHive Python SDK. All contributors must understand these workflows to maintain code quality.

Our GitHub Actions Workflows
----------------------------

**HoneyHive SDK uses a comprehensive GitHub Actions CI/CD pipeline with multiple workflows:**

**Primary Workflows**:

1. **`.github/workflows/tox-full-suite.yml`** - Comprehensive testing pipeline (tox environments)
2. **`.github/workflows/lambda-tests.yml`** - AWS Lambda compatibility testing  
3. **`.github/workflows/release-candidate.yml`** - Release automation and validation
4. **`.github/workflows/docs-*.yml`** - Documentation building, validation, and deployment

**Key Testing Commands Used in CI**:

.. code-block:: bash

   # Our standard testing commands (used in GHA)
   tox -e unit              # Unit tests (fast)
   tox -e integration       # Integration tests  
   tox -e lint             # Code quality (pylint + mypy)
   tox -e format           # Code formatting (black + isort)
   tox -e py311,py312,py313 # Multi-Python testing

Tox Full Suite Workflow
-----------------------

**Our `.github/workflows/tox-full-suite.yml` - Comprehensive Testing**:

This workflow runs our complete tox-based testing suite across multiple Python versions:

.. code-block:: yaml

   # Simplified version of our actual workflow
   name: Tox Full Test Suite
   
   on:
     workflow_dispatch:  # Manual trigger
     workflow_call:      # Called by other workflows
     
   jobs:
     test-matrix:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: ['3.11', '3.12', '3.13']
           tox-env: ['unit', 'integration', 'lint', 'format']
       
       steps:
       - uses: actions/checkout@v4
       - uses: actions/setup-python@v4
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install tox
         run: pip install tox
       
       - name: Run tox environment
         run: tox -e ${{ matrix.tox-env }}

AWS Lambda Testing Workflow
---------------------------

**Our `.github/workflows/lambda-tests.yml` - Lambda Compatibility**:

This workflow specifically tests AWS Lambda compatibility and runs on every PR:

.. code-block:: yaml

   # Key aspects of our Lambda testing workflow
   name: AWS Lambda Compatibility Tests
   
   on:
     pull_request:    # Run on all PRs
     push:
       branches: [main]  # Run on main branch pushes
     schedule:
       - cron: '0 6 * * *'  # Daily Lambda validation
   
   jobs:
     lambda-compatibility:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v4
       - name: Run Lambda tests
         run: |
           # Our Lambda-specific testing commands
           tox -e lambda
           python -m pytest tests/lambda/ -v

Internal Development Best Practices
-----------------------------------

**For HoneyHive SDK Contributors**:

**Pre-Commit Requirements**:

.. code-block:: bash

   # Before every commit, run these locally:
   tox -e format    # Code formatting (black + isort)
   tox -e lint      # Code quality (pylint + mypy)  
   tox -e unit      # Fast unit tests
   
   # For major changes, also run:
   tox -e integration  # Integration tests
   tox -e py311,py312,py313  # Multi-Python testing

**GitHub Actions Integration Points**:

1. **PR Validation**: Every PR triggers tox-full-suite + lambda-tests
2. **Main Branch Protection**: All tests must pass before merge
3. **Daily Validation**: Scheduled runs catch environment drift
4. **Release Validation**: Release candidate workflow runs full test suite

Environment Variables in CI
---------------------------

**Required Secrets in GitHub Actions**:

.. code-block:: bash

   # Repository secrets (configured in GitHub)
   HH_API_KEY          # HoneyHive API key for testing
   HH_TEST_API_KEY     # Dedicated test environment key
   AWS_ACCESS_KEY_ID   # For Lambda testing (optional)
   AWS_SECRET_ACCESS_KEY  # For Lambda testing (optional)

**Environment Variables Set in Workflows**:

.. code-block:: bash

   # Standard test environment configuration
   HH_TEST_MODE=true
   HH_PROJECT=honeyhive-sdk-ci
   HH_SOURCE=github-actions
   HH_DISABLE_HTTP_TRACING=true  # Performance optimization

Troubleshooting CI Failures
---------------------------

**Common Issues and Solutions**:

**1. Tox Environment Failures**:

.. code-block:: bash

   # Check tox configuration
   tox --listenvs
   
   # Run specific environment locally
   tox -e unit -v

**2. Lambda Test Failures**:

.. code-block:: bash

   # Check Lambda-specific logs
   python -m pytest tests/lambda/ -v -s
   
   # Verify Docker setup
   docker --version

**3. Integration Test Timeouts**:

.. code-block:: bash

   # Run with extended timeout
   HH_TIMEOUT=30000 tox -e integration

**4. Coverage Failures**:

.. code-block:: bash

   # Generate local coverage report
   tox -e unit -- --cov=honeyhive --cov-report=html
   open htmlcov/index.html

Workflow Monitoring and Debugging
---------------------------------

**Monitoring CI Health**:

1. **GitHub Actions Dashboard**: Monitor workflow runs and success rates
2. **Tox Environment Status**: Check which environments are failing
3. **Coverage Trends**: Track coverage changes over time
4. **Lambda Performance**: Monitor Lambda test execution times

**Debugging Failed Workflows**:

.. code-block:: bash

   # Download workflow logs locally
   gh run download <run-id>
   
   # Re-run specific workflow
   gh workflow run tox-full-suite.yml
   
   # Check workflow status
   gh run list --workflow=tox-full-suite.yml

**Performance Optimization**:

- **Parallel Execution**: Matrix strategy runs tests in parallel
- **Caching**: Dependencies cached between runs
- **Selective Testing**: Only run affected test suites when possible
- **Resource Limits**: Appropriate memory/CPU allocation for each job

See Also
--------

- :doc:`lambda-testing` - Lambda-specific CI/CD testing
- :doc:`performance-testing` - Performance testing in pipelines
- :doc:`integration-testing` - Integration testing strategies
- :doc:`../../tutorials/advanced-setup` - Advanced CI/CD configuration
- :doc:`../../reference/configuration/environment-vars` - CI/CD environment settings