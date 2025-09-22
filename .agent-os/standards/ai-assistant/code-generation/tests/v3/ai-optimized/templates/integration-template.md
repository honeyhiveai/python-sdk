# Integration Test Template - Real API Strategy

**🎯 AI Template for Generating Integration Tests with Real Backend Validation**

⚠️ MUST-READ: Complete integration template before test generation
🛑 VALIDATE-GATE: Integration Template Understanding
- [ ] Real API strategy comprehended (no mocking allowed) ✅/❌
- [ ] Backend verification requirements understood ✅/❌
- [ ] Integration fixtures identified and understood ✅/❌
- [ ] End-to-end validation principles accepted ✅/❌

🚨 FRAMEWORK-VIOLATION: If attempting to use mocks in integration tests

## 📋 **INTEGRATION TEST PRINCIPLES**

### **Real API Strategy**
- **No Mocking**: Use real HoneyHive APIs and backend services
- **End-to-End Validation**: Test complete functionality flows
- **Backend Vetting**: Verify data appears correctly in HoneyHive backend
- **Real Environment**: Test against actual API endpoints

## 🔧 **STANDARD FIXTURES (from conftest.py)**

### **Required Fixtures**
```python
# Use these fixtures from tests/integration/conftest.py
def test_function(
    self,
    honeyhive_tracer: HoneyHiveTracer,    # Real tracer instance
    verify_backend_event,                 # Backend verification utility
    cleanup_session                       # Session cleanup
) -> None:
```

### **Fixture Usage Patterns**
```python
# Real tracer configuration
honeyhive_tracer.project_name = "integration-test-project"
honeyhive_tracer.test_mode = True  # Use test environment

# Backend verification setup
event_data = {
    "event_type": "model",
    "inputs": {"prompt": "test input"},
    "outputs": {"response": "test output"}
}
```

## 🏗️ **TEST CLASS TEMPLATE**

```python
"""Integration tests for [MODULE_NAME].

This module tests [MODULE_PURPOSE] with real API calls and backend verification.
Tests validate end-to-end functionality and ensure data appears correctly in HoneyHive.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive integration test coverage requires extensive test cases, testing private 
# methods requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and real API integration patterns create unavoidable long lines.

import pytest
from honeyhive.tracer import HoneyHiveTracer

from src.module.under.test import function_to_test


class Test[FunctionName]Integration:
    """Integration test suite for [function_name] with real APIs."""

    def test_[scenario]_end_to_end(
        self,
        honeyhive_tracer: HoneyHiveTracer,
        verify_backend_event,
        cleanup_session
    ) -> None:
        """Test [scenario] with real API and backend verification."""
        # Execute function with real tracer
        result = function_to_test(honeyhive_tracer)
        
        # Verify function behavior
        assert result is not None
        assert honeyhive_tracer._initialized is True
        
        # Verify backend data (critical for integration tests)
        verify_backend_event(
            tracer=honeyhive_tracer,
            expected_event_type="model",  # or appropriate type
            expected_data={
                "project": honeyhive_tracer.project_name,
                "session_id": honeyhive_tracer.session_id
            },
            timeout=30  # Allow time for backend processing
        )

    def test_[scenario]_with_real_session_management(
        self,
        honeyhive_tracer: HoneyHiveTracer,
        verify_backend_event
    ) -> None:
        """Test [scenario] with real session creation and management."""
        # Test real session functionality
        original_session = honeyhive_tracer.session_id
        
        # Execute function that may create/modify sessions
        result = function_to_test(honeyhive_tracer)
        
        # Verify session handling
        assert honeyhive_tracer.session_id is not None
        if result.creates_new_session:
            assert honeyhive_tracer.session_id != original_session
        
        # Verify session exists in backend
        verify_backend_event(
            tracer=honeyhive_tracer,
            expected_event_type="session",
            expected_data={"session_id": honeyhive_tracer.session_id}
        )
```

## 🎯 **BACKEND VERIFICATION PATTERNS**

### **Event Verification**
```python
# Verify specific event appears in backend
verify_backend_event(
    tracer=honeyhive_tracer,
    expected_event_type="model",
    expected_data={
        "inputs": {"prompt": "expected input"},
        "outputs": {"response": "expected output"},
        "metadata": {"source": "integration_test"}
    },
    timeout=30
)
```

### **Session Verification**
```python
# Verify session created in backend
verify_backend_event(
    tracer=honeyhive_tracer,
    expected_event_type="session",
    expected_data={
        "project": "integration-test-project",
        "session_id": honeyhive_tracer.session_id,
        "source": "test"
    }
)
```

### **Configuration Verification**
```python
# Verify configuration applied correctly
assert honeyhive_tracer.config.server_url == "https://api.honeyhive.ai"
assert honeyhive_tracer.config.api_key is not None
assert honeyhive_tracer.test_mode is True
```

## 🧹 **CLEANUP PATTERNS**

### **Session Cleanup**
```python
def test_with_cleanup(
    self,
    honeyhive_tracer: HoneyHiveTracer,
    cleanup_session
):
    """Test with automatic session cleanup."""
    # Test creates session/events
    result = function_to_test(honeyhive_tracer)
    
    # Cleanup handled automatically by fixture
    # No manual cleanup needed
```

### **Resource Management**
```python
# For tests that create persistent resources
def test_with_resource_cleanup(self, honeyhive_tracer):
    created_resources = []
    try:
        # Test execution
        result = function_to_test(honeyhive_tracer)
        created_resources.append(result.resource_id)
        
        # Verify functionality
        assert result.success is True
        
    finally:
        # Clean up any created resources
        for resource_id in created_resources:
            cleanup_resource(resource_id)
```

## 🛑 **MANDATORY TEMPLATE COMPLIANCE**

🛑 VALIDATE-GATE: Integration Template Application
- [ ] Real API strategy applied (no mocks used) ✅/❌
- [ ] Backend verification included (verify_backend_event used) ✅/❌
- [ ] Integration fixtures properly used ✅/❌
- [ ] End-to-end validation implemented ✅/❌
- [ ] Cleanup patterns applied ✅/❌

## 🚨 **CRITICAL REQUIREMENTS**

### **Must Use Real APIs**
🛑 EXECUTE-NOW: Verify real API usage in generated tests
- ✅ Use real HoneyHive tracer instances
- ✅ Make actual API calls to backend
- ✅ Verify data appears in HoneyHive backend
- ❌ Never use mocks or fake responses
🚨 FRAMEWORK-VIOLATION: If any mocks found in integration tests

### **Must Verify Backend State**
📊 COUNT-AND-DOCUMENT: Backend verification points: [NUMBER]
- ✅ Use verify_backend_event for all data validation
- ✅ Check that events/sessions appear correctly
- ✅ Validate data integrity and completeness
- ❌ Never assume API calls succeeded without verification
⚠️ EVIDENCE-REQUIRED: All API calls must have backend verification

### **Must Handle Real Environment**
🛑 VALIDATE-GATE: Real Environment Handling
- ✅ Use test_mode=True for safe testing
- ✅ Handle real network latency and timing
- ✅ Clean up created resources appropriately
- ❌ Never impact production data or systems

🛑 UPDATE-TABLE: Integration template applied with compliance validation
🎯 NEXT-MANDATORY: Generate integration tests using this template only

---

**🎯 This template ensures generated integration tests use real APIs, verify backend state, and validate complete end-to-end functionality with mandatory compliance validation.**
