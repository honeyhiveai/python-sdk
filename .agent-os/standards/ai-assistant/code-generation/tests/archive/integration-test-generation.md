# Integration Test Generation Framework

## 🎯 **INTEGRATION TEST SPECIFIC REQUIREMENTS**

**Purpose**: Generate end-to-end tests that validate real API interactions and component integration.

---

## 📋 **INTEGRATION TEST NAMING STANDARDS**

### **✅ CORRECT NAMING PATTERN**
```
tests/integration/test_[feature]_[integration_type].py
```

**Examples:**
- `test_tracer_instrumentor_integration.py` - Tracer + instrumentor integration
- `test_api_client_real_endpoints.py` - Real API endpoint testing
- `test_otel_honeyhive_integration.py` - OpenTelemetry + HoneyHive integration

### **❌ FORBIDDEN PATTERNS**
- `test_models_integration.py` - Too vague, what integration?
- `test_unit_integration.py` - Contradictory naming
- `test_[single_module].py` - Should be unit test, not integration

---

## 🚨 **INTEGRATION TEST SCOPE REQUIREMENTS**

### **✅ VALID INTEGRATION TEST TARGETS**
- **API Client + Real Endpoints** - Test actual HTTP calls
- **Tracer + Instrumentor Integration** - Test OpenTelemetry integration
- **Multi-Component Workflows** - Test complete user journeys
- **External Service Integration** - Test third-party service connections

### **❌ INVALID INTEGRATION TEST TARGETS**
- **Single module testing** - Should be unit tests
- **Mock-heavy tests** - Should be unit tests with mocks
- **Configuration-only tests** - Should be unit tests

---

## 🔗 **INTEGRATION WITH TESTING STANDARDS**

**MANDATORY: Follow existing integration testing standards:**

### **Integration Test Standards**
- **Reference**: [Integration Testing Standards](../../testing/integration-testing-standards.md)
- **Real APIs**: Use actual endpoints, not mocks
- **Environment**: Use `.env` file for credentials
- **Backend Validation**: Verify backend systems are working
- **Cleanup**: Ensure proper resource cleanup

### **🚨 MANDATORY FILE HEADER TEMPLATE**
```python
"""Integration tests for [FUNCTIONALITY].

This module contains comprehensive integration tests for [DESCRIPTION].
"""
# pylint: disable=too-many-lines
# Justification: Comprehensive integration test workflows require extensive test cases

import pytest
import os
from honeyhive import HoneyHive, HoneyHiveTracer
# ... other imports
```

**🚨 CRITICAL**: ALL integration test files MUST start with the pre-approved pylint disable to prevent line length violations.

**NOTE**: Integration tests do NOT need `redefined-outer-name` or `protected-access` disables as they should minimize fixture usage and avoid private method testing.

### **No Mocks Policy**
- **Reference**: Agent OS testing standards
- **Rule**: Integration tests MUST NOT use mocks
- **Validation**: Pre-commit hook enforces no mocks in integration tests

### **🛠️ Proven Backend Verification Fixtures**
**MANDATORY: Use existing proven fixtures for backend validation:**

```python
# ✅ IMPORT PROVEN FIXTURES
from tests.utils import (
    verify_backend_event,      # Core backend verification with retry logic
    verify_tracer_span,        # Complete workflow: create → export → verify
    verify_span_export,        # Standardized span export verification
    generate_test_id,          # Unique test identifiers for parallel execution
)

# ✅ STANDARD INTEGRATION TEST PATTERN
def test_integration_workflow(integration_tracer, integration_client, real_project) -> None:
    """Test integration workflow with backend verification."""
    _, unique_id = generate_test_id("integration", "workflow")
    
    # Use proven verification pattern - creates span AND verifies backend
    verified_event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name="integration_workflow_test",
        unique_identifier=unique_id,
        span_attributes={
            "test.integration_type": "end_to_end",
            "test.backend_verification": "true",
            "integration.component": "api_client",
        },
    )
    
    # Verify backend actually processed the integration
    assert verified_event.event_id is not None
    assert verified_event.session_id == integration_tracer.session_id
```

**Why Use These Fixtures:**
- **Proven Reliability**: Used across 20+ integration tests
- **Built-in Retry Logic**: Handles backend processing delays
- **Dynamic Relationship Analysis**: Finds related spans intelligently
- **Comprehensive Validation**: Verifies event properties, metadata, timing

---

## 🚀 **INTEGRATION TEST GENERATION WORKFLOW**

### **Phase 0C: Integration Target Validation**
```bash
# 1. Validate integration scope (not single module)
echo "[TARGET_DESCRIPTION]" | grep -E "integration|api|endpoint|workflow"

# 2. Ensure real API usage (no mocks)
grep -r "Mock\|patch\|@mock" "tests/integration/test_[TARGET].py" || echo "No mocks found - GOOD"

# 3. Verify environment setup
test -f ".env" || test -f "env.integration.example" && echo "Environment config available"

# 4. Check for cleanup patterns
grep -E "teardown|cleanup|finally" "tests/integration/test_[TARGET].py" | wc -l
```

---

## 📊 **INTEGRATION TEST QUALITY TARGETS**

| Metric | Target | Enforcement |
|--------|--------|-------------|
| **Pass Rate** | 100% | Phase 8 mandatory |
| **Real API Usage** | 100% | Pre-commit hook |
| **No Mocks** | 0 mocks | Pre-commit hook |
| **Environment Setup** | Required | Phase 0C validation |
| **Resource Cleanup** | Required | Phase 8 validation |

---

**🎯 Key Principle**: Integration tests validate real interactions between components and external services without mocks.
