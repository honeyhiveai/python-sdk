# Backwards Compatibility Integration Tests

This directory contains integration tests that validate backwards compatibility between the `complete-refactor` branch and the `main` branch. These tests are designed to catch critical runtime issues that our previous testing approach missed.

## Test Categories

### 1. Runtime Environment Loading (`test_runtime_environment_loading.py`)

**Purpose**: Tests environment variables set AFTER SDK import (critical production pattern)

**What it catches**:
- Environment variables not being picked up when set at runtime
- Boolean environment variable parsing regressions  
- Configuration reload issues
- Environment variable precedence problems

**Why it's needed**: Our previous tests set environment variables at test setup time, missing the common production pattern where environment variables are set after the SDK is imported (Docker, Kubernetes, Lambda, etc.).

**Example regression it would have caught**: The HH_API_URL issue fixed in commit 2ebe473.

### 2. Production Patterns (`test_production_patterns.py`)

**Purpose**: Tests real-world deployment patterns used in production

**Deployment patterns covered**:
- Docker environment variable injection
- Kubernetes ConfigMap/Secret injection
- AWS Lambda environment variables
- Google Cloud Run configuration
- Azure Functions environment setup
- Development .env file patterns
- CI/CD pipeline environment variables

**Why it's needed**: Ensures the SDK works correctly across all major deployment scenarios that our users encounter.

### 3. Regression Detection (`test_regression_detection.py`)

**Purpose**: Automated detection of backwards compatibility regressions

**What it validates**:
- All main branch API patterns continue to work
- All main branch imports are available
- All 16 original parameters function correctly
- Context propagation methods work as expected
- Evaluation workflows maintain compatibility
- Session management remains functional

**Why it's needed**: Provides comprehensive validation that the complete-refactor branch maintains 100% backwards compatibility with main branch patterns.

## How These Tests Work

### Subprocess Execution
These tests run in subprocess to simulate real production behavior:

```python
# This simulates real user behavior
test_script = '''
import os

# Import SDK first (like real users do)
from honeyhive import HoneyHiveTracer

# THEN set environment variables (like real users do)
os.environ["HH_API_URL"] = "https://runtime.custom.url"

# Create tracer - should use runtime env vars
tracer = HoneyHiveTracer(test_mode=True)
assert tracer.client.base_url == "https://runtime.custom.url"
'''

result = subprocess.run([sys.executable, "-c", test_script], ...)
```

### Integration with Tox

These tests run as part of the `tox -e integration` environment:

```bash
# Run all integration tests (includes backwards compatibility)
tox -e integration

# Run specific backwards compatibility tests
tox -e integration -- tests/integration/backwards_compatibility/

# Run specific test
tox -e integration -- tests/integration/backwards_compatibility/test_runtime_environment_loading.py::TestRuntimeEnvironmentBehavior::test_environment_variables_set_after_import
```

## Test Environment

These tests run in the integration environment with:
- `HH_TEST_MODE = false` (to test real behavior)
- `HH_DEBUG_MODE = true` (for detailed logging)
- Real OpenTelemetry components (no mocking)
- Subprocess execution for fresh Python environments

## Monitoring Script

The `scripts/backwards_compatibility_monitor.py` script provides quick validation:

```bash
# Quick compatibility check
python scripts/backwards_compatibility_monitor.py

# Verbose output
python scripts/backwards_compatibility_monitor.py --verbose

# JSON output for automation
python scripts/backwards_compatibility_monitor.py --json
```

## Why This Approach

### Previous Testing Gaps

Our previous testing approach had critical blind spots:

1. **Static vs Runtime**: Tests set environment variables at setup time, missing runtime changes
2. **Mock-Heavy**: Heavy mocking hid real behavior issues
3. **No Production Patterns**: Didn't test real deployment scenarios
4. **Import-Time Loading**: Didn't catch environment variable loading after import

### New Testing Benefits

1. **Runtime Validation**: Tests environment variables set after import
2. **Real Behavior**: Minimal mocking, tests actual SDK behavior
3. **Production Coverage**: Tests all major deployment patterns
4. **Regression Prevention**: Automated detection of backwards compatibility issues

## Integration with CI/CD

These tests run automatically as part of the integration test suite in CI/CD, ensuring that any backwards compatibility regressions are caught before they reach production.

The tests are designed to be fast, reliable, and comprehensive, providing confidence that the complete-refactor branch maintains full backwards compatibility with the main branch.
