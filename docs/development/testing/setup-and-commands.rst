Testing Setup and Commands
==========================

This guide covers the essential setup and commands for SDK testing.

## Development Environment Setup

### Initial Setup

**Required one-time setup** for all SDK developers:

.. code-block:: bash

   # Set up development environment (required first step)
   ./scripts/setup-dev.sh

This script installs:
- Pre-commit hooks for code quality
- Development dependencies (tox, pytest, etc.)
- Code formatting tools (black, isort)
- Static analysis tools (pylint, mypy)

### Verification

**Verify your setup** with basic tests:

.. code-block:: bash

   # 1. Run unit tests to verify setup
   tox -e unit
   
   # 2. Run integration tests
   tox -e integration
   
   # 3. Check code coverage (minimum 80% required)
   tox -e unit -- --cov=honeyhive --cov-report=html --cov-fail-under=80

## Testing Commands Reference

### Core Test Commands

**Run specific test types**:

.. code-block:: bash

   # Unit tests only (fast, isolated tests)
   tox -e unit
   
   # Integration tests only (end-to-end functionality)
   tox -e integration
   
   # All tests (unit + integration)
   tox -e unit -e integration

### Specialized Testing

.. code-block:: bash

   # CLI tests specifically
   pytest tests/unit/test_cli_main.py -v
   
   # CLI tests with coverage
   pytest tests/unit/test_cli_main.py --cov=src/honeyhive/cli/main --cov-report=term-missing
   
   # Lambda compatibility tests
   cd tests/lambda && make test-lambda
   
   # Performance tests
   cd tests/lambda && make test-performance
   
   # Integration tests (requires real API credentials)
   tox -e integration

### Coverage and Quality

.. code-block:: bash

   # Coverage report (HTML format)
   pytest --cov=honeyhive --cov-report=html
   
   # Coverage report (terminal)
   pytest --cov=honeyhive --cov-report=term-missing
   
   # Specific test file with coverage
   pytest tests/test_tracer.py --cov=honeyhive --cov-report=term-missing

### Quality Gates

**Required before every commit**:

.. code-block:: bash

   # Format verification (black, isort)
   tox -e format
   
   # Lint verification (pylint, mypy)
   tox -e lint
   
   # Documentation build
   tox -e docs
   
   # Combined quality check
   tox -e format && tox -e lint

### Python Version Testing

.. code-block:: bash

   # Test specific Python versions
   tox -e py311    # Python 3.11
   tox -e py312    # Python 3.12
   tox -e py313    # Python 3.13
   
   # Test all supported versions
   tox -e py311 -e py312 -e py313

## Test Environment Configuration

### Basic Test Configuration

.. code-block:: python

   # Test configuration
   test_tracer = HoneyHiveTracer.init(
       api_key="test-api-key",  # Or set HH_API_KEY environment variable
       project="test-project",  # Or set HH_PROJECT environment variable
       source="development",    # Or set HH_SOURCE environment variable
       test_mode=True,          # Enable test mode (or set HH_TEST_MODE=true)
       disable_http_tracing=True  # Optimize for testing
   )

### Environment Variables for Testing

.. code-block:: bash

   # Set test environment variables
   export HH_API_KEY="test-key"
   export HH_SOURCE="test"
   export HH_TEST_MODE="true"

### Multi-Environment Testing

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

## Quick Testing Examples

### Basic Integration Test

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   def test_basic_integration():
       tracer = HoneyHiveTracer.init(
           api_key="test-key",      # Or set HH_API_KEY environment variable
           project="test-project",  # Or set HH_PROJECT environment variable
           test_mode=True           # Important: enables test mode (or set HH_TEST_MODE=true)
       )
       
       with tracer.trace("test-operation") as span:
           span.set_attribute("test.type", "integration")
           assert span is not None

### Mock HoneyHive for Testing

.. code-block:: python

   from unittest.mock import Mock, patch
   
   def test_with_mock_tracer():
       with patch('honeyhive.HoneyHiveTracer') as mock_tracer:
           mock_tracer.init.return_value = Mock()
           
           # Your application code here
           result = your_function_that_uses_honeyhive()
           
           # Verify tracer was used
           mock_tracer.init.assert_called_once()

### Test Multi-Instance Tracers

.. code-block:: python

   def test_multiple_tracers():
       tracer1 = HoneyHiveTracer.init(
           api_key="key1",          # Unique API key for project1
           project="project1",      # Unique project identifier
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       tracer2 = HoneyHiveTracer.init(
           api_key="key2",          # Unique API key for project2
           project="project2",      # Unique project identifier
           test_mode=True           # Or set HH_TEST_MODE=true
       )
       
       # Verify independence
       assert tracer1.session_id != tracer2.session_id
       assert tracer1.project != tracer2.project

### CLI Testing

.. code-block:: python

   from click.testing import CliRunner
   from unittest.mock import Mock, patch
   from honeyhive.cli.main import cli
   
   def test_cli_command():
       """Test CLI commands using Click's CliRunner."""
       runner = CliRunner()
       
       # Test basic command
       result = runner.invoke(cli, ["--help"])
       assert result.exit_code == 0
       assert "HoneyHive CLI" in result.output
   
   @patch('honeyhive.cli.main.HoneyHive')
   def test_cli_with_mocking(mock_client):
       """Test CLI commands with proper mocking."""
       mock_client.return_value = Mock()
       
       runner = CliRunner()
       result = runner.invoke(cli, ["api", "request", "--method", "GET", "--url", "/test"])
       
       assert result.exit_code == 0
       mock_client.assert_called_once()

## Troubleshooting Setup Issues

### Common Setup Problems

**Problem**: `tox` command not found
**Solution**: Install tox in your virtual environment:

.. code-block:: bash

   pip install tox

**Problem**: Tests fail with import errors
**Solution**: Install SDK in development mode:

.. code-block:: bash

   pip install -e .

**Problem**: Pre-commit hooks not running
**Solution**: Reinstall pre-commit hooks:

.. code-block:: bash

   pre-commit install

### Performance Issues

**Problem**: Tests are slow
**Solution**: Run unit tests only for faster feedback:

.. code-block:: bash

   # Fast unit tests only
   tox -e unit
   
   # Skip integration tests during development
   pytest tests/unit/ -v

**Problem**: Coverage calculation is slow
**Solution**: Use faster coverage options:

.. code-block:: bash

   # Skip HTML report for faster results
   pytest --cov=honeyhive --cov-report=term

## See Also

- :doc:`unit-testing` - Unit testing strategies and patterns
- :doc:`integration-testing` - Integration testing best practices
- :doc:`troubleshooting-tests` - Detailed troubleshooting guide
- :doc:`ci-cd-integration` - CI/CD testing workflows
