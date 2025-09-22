# HoneyHive Integration Test Fixture Standards

> **📚 COMPREHENSIVE STANDARDS**: This document provides quick reference for integration test fixtures. For complete testing standards, see **[`.agent-os/standards/development/testing-standards.md`](../.agent-os/standards/development/testing-standards.md)**

## 🔒 **MANDATORY: Skip-Proof Test Generation Framework**

**⛔ BEFORE writing ANY tests, AI assistants MUST follow the skip-proof framework:**

- **📋 Framework**: [`.agent-os/standards/ai-assistant/code-generation/comprehensive-analysis-skip-proof.md`](../.agent-os/standards/ai-assistant/code-generation/comprehensive-analysis-skip-proof.md)
- **🛡️ Enforcement**: [`.agent-os/standards/ai-assistant/code-generation/skip-proof-enforcement-card.md`](../.agent-os/standards/ai-assistant/code-generation/skip-proof-enforcement-card.md)
- **🚨 Trigger**: [`.agent-os/standards/ai-assistant/TEST_GENERATION_MANDATORY_FRAMEWORK.md`](../.agent-os/standards/ai-assistant/TEST_GENERATION_MANDATORY_FRAMEWORK.md)

**🎯 Required**: Complete ALL 5 checkpoint gates with evidence before writing tests

## 🚨 MANDATORY: Use Standard Fixtures & Validation

**ALL integration tests MUST use:**
1. **Standardized fixtures** from `tests/conftest.py`
2. **Centralized validation** from `tests/utils/validation_helpers.py`
3. **Backend verification** for all span-creating tests

### ✅ CORRECT Usage

```python
def test_my_integration(integration_tracer, integration_client, real_project):
    """Use standard fixtures AND validation."""
    from tests.utils.validation_helpers import verify_tracer_span
    from tests.utils.unique_id import generate_test_id
    
    # Generate unique identifier for backend verification
    _, unique_id = generate_test_id("my_test", "integration")
    
    # Use centralized validation helper
    verified_event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name="my_test_span",
        unique_identifier=unique_id,
        span_attributes={"test.type": "integration"}
    )
    
    # Assert on verified backend data
    assert verified_event.event_name == "my_test_span"
```

### ❌ INCORRECT Usage

```python
def test_my_integration(real_api_key, real_project, real_source):
    """DON'T create tracers directly OR use manual validation."""
    # WRONG: Direct tracer creation
    tracer = HoneyHiveTracer(
        api_key=real_api_key,
        project=real_project,
        source=real_source,
        # Missing critical parameters!
    )
    
    # WRONG: Manual validation instead of centralized helpers
    with tracer.start_span("test") as span:
        span.set_attribute("test", "value")
    
    # WRONG: Manual backend verification
    events = client.events.list_events(project=real_project)
    # Manual search logic...
```

## 📋 Standard Fixture Configuration

The `integration_tracer` fixture provides:

- ✅ **Unique session names** (prevents conflicts in parallel tests)
- ✅ **OTLP export enabled** (spans reach backend for verification)
- ✅ **Immediate mode** (`disable_batch=True` for test reliability)
- ✅ **Proper cleanup** (prevents resource leaks)
- ✅ **Test isolation** (clean state between tests)

## 🔧 Available Fixtures

### Primary Fixtures
- `integration_tracer` - Standard tracer for most integration tests
- `tracer_factory` - Factory for creating multiple tracers in one test
- `integration_client` - HoneyHive API client for validation
- `real_api_key`, `real_project`, `real_source` - Credentials (use with fixtures only)

### Specialized Fixtures
- `clean_otel_state` - OpenTelemetry state cleanup
- `integration_test_config` - Test configuration settings

## 🔍 Centralized Validation Helpers

**ALL integration tests MUST use centralized validation from `tests/utils/validation_helpers.py`:**

### Span Validation (Most Common)
```python
from tests.utils.validation_helpers import verify_tracer_span

verified_event = verify_tracer_span(
    tracer=integration_tracer,
    client=integration_client,
    project=real_project,
    span_name="operation_name",
    unique_identifier=unique_id,
)
```

### Datapoint Validation
```python
from tests.utils.validation_helpers import verify_datapoint_creation

verified_datapoint = verify_datapoint_creation(
    client=integration_client,
    project=real_project,
    datapoint_request=datapoint_request,
    test_id=test_id,
)
```

### Session Validation
```python
from tests.utils.validation_helpers import verify_session_creation

verified_session = verify_session_creation(
    client=integration_client,
    project=real_project,
    session_request=session_request,
    expected_session_name="test_session",
)
```

### Configuration Validation
```python
from tests.utils.validation_helpers import verify_configuration_creation

verified_config = verify_configuration_creation(
    client=integration_client,
    project=real_project,
    config_request=config_request,
    expected_config_name="test_config",
)
```

### Event Validation
```python
from tests.utils.validation_helpers import verify_event_creation

verified_event = verify_event_creation(
    client=integration_client,
    project=real_project,
    event_request=event_request,
    unique_identifier=unique_id,
    expected_event_name="test_event",
)
```

## 🚨 Validation Standardization Required

**The following test files need backend verification added:**

### ❌ Missing Backend Verification (11 files):
1. `test_multi_instance_tracer_integration.py` - No backend verification
2. `test_real_api_multi_tracer.py` - No backend verification  
3. `test_tracer_integration.py` - No backend verification
4. `test_end_to_end_validation.py` - Manual validation instead of centralized
5. `test_tracer_performance.py` - No backend verification
6. `test_real_instrumentor_integration.py` - No backend verification
7. `test_real_instrumentor_integration_comprehensive.py` - No backend verification
8. `test_api_client_performance_regression.py` - No validation
9. `test_batch_configuration.py` - No validation
10. `test_model_integration.py` - No validation
11. `test_simple_integration.py` - Manual validation

### ✅ Already Using Backend Verification (12 files):
- All `test_otel_*_integration.py` files use `verify_backend_event` consistently

## 📝 Standardization Steps

1. **Add backend verification** to all span-creating tests
2. **Replace manual validation** with centralized helpers
3. **Use standard fixtures** (`integration_tracer`, `integration_client`)
4. **Import validation helpers** from `tests.utils.validation_helpers`
5. **Test the changes** to ensure end-to-end validation works

## 🎯 Benefits

- **Consistent OTLP configuration** across all tests
- **Reliable backend verification** (no more 5-minute hangs)
- **Better test isolation** (no cross-test contamination)
- **Faster test execution** (proper cleanup and timeouts)
- **Easier maintenance** (centralized configuration)

## 📚 Documentation

This standardization addresses the root cause of inconsistent test behavior and ensures the rule "every HoneyHiveTracer must have HoneyHiveSpanProcessor AND HoneyHiveOTLPExporter" is consistently applied.
