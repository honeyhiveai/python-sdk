# Phase 3: Integration Dependency Strategy

**🎯 Real Dependency Usage for Integration Tests**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Integration Dependency Strategy Prerequisites
- [ ] All shared analysis completed (Tasks 3.1-3.4) with evidence ✅/❌
- [ ] Integration test path selected and locked (no unit mixing) ✅/❌
- [ ] Dependency inventory complete ✅/❌
- [ ] Phase 3.4 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If unit path selected - cannot proceed with integration strategy

## 🛑 **INTEGRATION DEPENDENCY STRATEGY DEFINITION**

⚠️ MUST-COMPLETE: Define complete real dependency strategy based on analysis
📊 COUNT-AND-DOCUMENT: External dependencies to use (real): [NUMBER from analysis]
📊 COUNT-AND-DOCUMENT: Internal dependencies to validate: [NUMBER from analysis]
📊 COUNT-AND-DOCUMENT: Configuration dependencies to test: [NUMBER from analysis]

🛑 EXECUTE-NOW: Verify integration fixtures are available
```bash
# MANDATORY: Verify integration dependency infrastructure
echo "=== INTEGRATION DEPENDENCY VERIFICATION ==="
grep -n "honeyhive_tracer" tests/integration/conftest.py
grep -n "honeyhive_client" tests/integration/conftest.py
grep -n "verify_backend_event" tests/integration/conftest.py
echo "Integration dependency fixtures available: $(grep -c -E '(honeyhive_tracer|honeyhive_client|verify_backend_event)' tests/integration/conftest.py)"
```

🛑 PASTE-OUTPUT: Integration dependency fixture verification results below

## 📋 **INTEGRATION DEPENDENCY STRATEGY**

### **Real External Library Usage**
```python
# Based on external library analysis: Use real third-party dependencies
# NO MOCKING - Real OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

def test_real_otel_integration(
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
):
    # Use real OpenTelemetry tracer
    tracer = trace.get_tracer(__name__)
    
    # Real span creation and management
    with tracer.start_as_current_span("test-span") as span:
        span.set_status(Status(StatusCode.OK))
        
        # Execute real function with real dependencies
        result = function_under_test(honeyhive_tracer)
        
        # Verify real backend integration
        verify_backend_event(
            tracer=honeyhive_tracer,
            expected_event_type="span",
            expected_data={
                "span_name": "test-span",
                "status": "OK"
            }
        )
```

### **Real Internal Module Usage**
```python
# Based on internal module analysis: Use real HoneyHive components
from honeyhive.utils.logger import safe_log
from honeyhive.tracer.base import HoneyHiveTracer

def test_real_internal_integration(
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
):
    # Use real internal modules
    safe_log(honeyhive_tracer, "info", "Integration test message")
    
    # Real cross-module interactions
    result = honeyhive_tracer.initialize()
    
    # Verify real backend data flow
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="session",
        expected_data={
            "session_id": honeyhive_tracer.session_id,
            "initialized": True
        }
    )
```

### **Real Configuration Usage**
```python
# Based on configuration analysis: Use real environment variables
import os

def test_real_config_integration(
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
):
    # Use real environment configuration
    api_key = os.environ.get('HH_API_KEY')
    project_name = os.environ.get('HH_PROJECT', 'integration-test')
    
    # Configure tracer with real values
    honeyhive_tracer.config.api_key = api_key
    honeyhive_tracer.project_name = project_name
    
    # Test real configuration validation
    assert honeyhive_tracer.config.is_valid()
    
    # Verify real backend authentication
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="auth",
        expected_data={
            "api_key_valid": True,
            "project": project_name
        }
    )
```

### **Integration Fixtures Usage**
```python
# Use integration-specific fixtures (from Phase 1 analysis)
def test_with_integration_fixtures(
    honeyhive_tracer: HoneyHiveTracer,  # Real tracer
    honeyhive_client: HoneyHiveClient,  # Real client
    verify_backend_event  # Backend verification
):
    # Real end-to-end functionality testing
    # No mocking - full system integration
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 QUANTIFY-RESULTS: Real external usage strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Real internal usage strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Real configuration strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Integration fixture usage: [CONFIRMED with fixture verification]
⚠️ EVIDENCE-REQUIRED: Integration dependency strategy documented with specific validation points

## 🛑 **VALIDATION GATE: INTEGRATION DEPENDENCY STRATEGY COMPLETE**
🛑 VALIDATE-GATE: Integration Dependency Strategy Evidence
- [ ] All dependencies use real implementations (no mocks - count matches analysis) ✅/❌
- [ ] No mocking strategy defined (correct for integration) ✅/❌
- [ ] Backend verification integrated (fixtures verified) ✅/❌
- [ ] Real end-to-end validation achieved ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete integration dependency strategy
🛑 UPDATE-TABLE: Phase 3.6 → Integration dependency strategy complete with evidence
🎯 NEXT-MANDATORY: [evidence-collection-framework.md](evidence-collection-framework.md)
