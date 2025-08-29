# Testing & Quality Assurance

The HoneyHive Python SDK maintains high quality through comprehensive testing strategies and robust test infrastructure.

## 🎯 **Test Coverage Overview**

- **Current Coverage**: 70.89% (exceeds 60% requirement)
- **Total Tests**: 685 unit tests + 21 integration tests
- **Test Categories**: API clients, evaluation framework, tracing, utilities, decorators
- **Python Versions**: 3.11, 3.12, 3.13

## 🧪 **Test Structure**

### Unit Tests (`tests/unit/`)
- **API Tests**: Client functionality, endpoints, models
- **Evaluation Tests**: Framework, evaluators, threading, decorators
- **Tracer Tests**: OpenTelemetry integration, decorators, HTTP instrumentation
- **Utility Tests**: Caching, connection pooling, logging, configuration

### Integration Tests (`tests/integration/`)
- **API Workflows**: **REAL API integration testing** (no mocking)
- **Evaluation Framework**: Comprehensive evaluation scenarios with real API
- **Model Integration**: Real-world usage patterns
- **Tracer Integration**: Full tracing workflow testing

**Important**: Integration tests use **REAL HoneyHive API credentials** from your `.env` file to test actual API functionality. This ensures that:
- Tests validate real API behavior and responses
- Integration issues are caught early
- Tests run against your actual HoneyHive project
- No mock objects or fake responses

## �� **Running Tests**

### Using Tox (Recommended)
```bash
# Run all unit tests
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
```

### Direct Pytest
```bash
# Run unit tests with coverage
pytest tests/unit --cov=src/honeyhive --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_evaluation_evaluators.py -v

# Run with markers
pytest -m evaluation
pytest -m integration
```

## 🛡️ **Test Environment & Isolation**

### Environment Variables

#### Unit Tests
```bash
HH_TEST_MODE=true
HH_DEBUG_MODE=true
HH_DISABLE_TRACING=true
HH_DISABLE_HTTP_TRACING=true
HH_OTLP_ENABLED=false
```

#### Integration Tests (REAL API)
Integration tests use **real credentials** from your `.env` file:
```bash
# Loaded automatically from .env file
HH_API_KEY=hh_Dhi9z2EY0tmUtgKinW1mOkKCEYKqkQ8W
HH_API_URL=https://api.honeyhive.ai
HH_PROJECT="New Project"
HH_PROJECT_ID="64d69442f9fa4485aa1cc582"
HH_SOURCE="production"
HH_TEST_MODE=false  # Use real API mode
HH_DEBUG_MODE=true
HH_DISABLE_TRACING=false  # Enable real tracing
HH_DISABLE_HTTP_TRACING=false
HH_OTLP_ENABLED=false
```

**Note**: Integration tests will skip if no real credentials are found in the `.env` file.

### Test Fixtures
- **API Client**: Mocked HoneyHive client for testing
- **Tracer**: Isolated tracer instance per test
- **Environment**: Clean setup/teardown between tests
- **Mocking**: Comprehensive OpenTelemetry mocking

## 🔌 **I/O Error Prevention**

## 🌐 **Real API Integration vs Mocking**

### **Why Real API for Integration Tests?**

Integration tests use **real HoneyHive API credentials** instead of mocking because:

1. **Authentic Testing**: Tests real API behavior, responses, and error handling
2. **Integration Validation**: Catches actual integration issues between components
3. **API Changes**: Tests automatically adapt to API changes and new features
4. **Performance**: Real API performance characteristics are tested
5. **Data Persistence**: Tests create real evaluation runs in your project
6. **Error Scenarios**: Real API errors and edge cases are tested

### **Mocking Strategy**

- **Unit Tests**: Use comprehensive mocking for isolation and speed
- **Integration Tests**: Use real API for end-to-end validation
- **Test Isolation**: Each test runs in a clean environment with proper cleanup
- **Credential Management**: Real credentials loaded from `.env` file automatically

## 🔌 **I/O Error Prevention**

### OpenTelemetry Mocking
The test suite includes sophisticated mocking to prevent OpenTelemetry I/O errors:

```python
@pytest.fixture(autouse=True)
def disable_tracing_during_tests():
    """Disable tracing during tests to prevent I/O errors."""
    # Set environment variables to disable tracing
    os.environ["HH_DISABLE_TRACING"] = "true"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"
    
    # Mock the get_tracer function to return None during tests
    with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
        mock_get_tracer.return_value = None
        # Mock OpenTelemetry trace module to prevent span creation
        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            # Create a proper mock tracer that supports context manager protocol
            mock_tracer = Mock()
            mock_span = Mock()
            mock_span.__enter__ = Mock(return_value=mock_span)
            mock_span.__exit__ = Mock(return_value=None)
            mock_tracer.start_as_current_span.return_value = mock_span
            mock_trace.get_tracer.return_value = mock_tracer
            yield
```

### Benefits
- **No I/O Errors**: Prevents "Exception while exporting Span" errors
- **Context Manager Support**: Proper mock objects support `with` statements
- **Test Isolation**: Each test runs in a clean, isolated environment
- **Performance**: Tests run faster without actual tracing overhead

## 📊 **Coverage Analysis**

### High Coverage Areas
- **Evaluation Framework**: 84% coverage with comprehensive testing
- **API Evaluations**: 100% coverage for evaluation endpoints
- **Models**: 99% coverage for generated models
- **Core Utilities**: 98% coverage for caching, 86% for baggage dict

### Areas for Improvement
- **CLI Module**: 36% coverage (mostly untested edge cases)
- **HTTP Instrumentation**: 43% coverage (complex instrumentation logic)
- **Connection Pool**: 57% coverage (async operations and edge cases)

## 🔧 **Test Configuration**

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --asyncio-mode=auto
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, component interaction)
    evaluation: Evaluation framework tests
    slow: Slow running tests
    api: API-related tests
    tracer: Tracer functionality tests
```

### tox.ini
```ini
[testenv]
deps =
    pytest>=7.0.0
    pytest-asyncio>=0.21.0
    pytest-cov>=4.0.0
    httpx>=0.24.0
    opentelemetry-api>=1.20.0
    opentelemetry-sdk>=1.20.0
commands =
    pytest tests/unit --cov=src/honeyhive --cov-report=term-missing
```

## 🚨 **Common Test Issues & Solutions**

### OpenTelemetry Import Errors
```bash
# Solution: Use tox environments
tox -e py311  # Instead of direct pytest
```

### Coverage Failures
```bash
# Check current coverage
tox -e unit -- --cov=src/honeyhive --cov-report=term-missing

# Coverage is currently 70.89%, above the 60% requirement
```

### Test Isolation Issues
```bash
# Reset OpenTelemetry context between tests
pytest --tb=short  # For cleaner error output
```

## 📈 **Continuous Improvement**

### Regular Testing
- **Pre-commit**: Run tests before committing code
- **CI/CD**: Automated testing on all pull requests
- **Coverage Monitoring**: Track coverage trends over time
- **Performance Testing**: Monitor test execution time

### Test Maintenance
- **Mock Updates**: Keep mocks in sync with code changes
- **Fixture Optimization**: Optimize test fixtures for performance
- **Coverage Goals**: Aim to maintain >70% coverage
- **Integration Testing**: Expand integration test coverage

## 🔍 **Debugging Tests**

### Verbose Output
```bash
pytest -v --tb=long
```

### Specific Test Debugging
```bash
pytest tests/unit/test_evaluation_evaluators.py::TestThreadingFeatures::test_evaluate_with_evaluators_threading -v -s
```

### Coverage Debugging
```bash
# Generate HTML coverage report
pytest --cov=src/honeyhive --cov-report=html
# Open htmlcov/index.html in browser
```

## 📚 **Testing Best Practices**

### Writing Tests
- **Descriptive Names**: Use clear, descriptive test method names
- **Arrange-Act-Assert**: Follow AAA pattern for test structure
- **Mock External Dependencies**: Mock API calls and external services
- **Test Edge Cases**: Include boundary conditions and error scenarios

### Test Organization
- **Group Related Tests**: Use test classes to group related functionality
- **Consistent Naming**: Follow `test_<module>_<file>.py` pattern
- **Proper Markers**: Use appropriate pytest markers for categorization
- **Documentation**: Include docstrings explaining test purpose

### Performance Considerations
- **Fast Unit Tests**: Keep unit tests under 1 second each
- **Efficient Mocking**: Use lightweight mocks where possible
- **Resource Cleanup**: Ensure proper cleanup in test teardown
- **Parallel Execution**: Leverage pytest-xdist for parallel test execution
