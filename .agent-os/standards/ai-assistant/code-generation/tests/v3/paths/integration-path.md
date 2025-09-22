# Integration Test Path - REAL API Strategy

## 🎯 **INTEGRATION TEST PHILOSOPHY: END-TO-END VALIDATION**

🛑 VALIDATE-GATE: Integration Path Entry Requirements
- [ ] Real API strategy commitment confirmed ✅/❌
- [ ] Unit vs integration separation understood ✅/❌
- [ ] End-to-end validation objective acknowledged ✅/❌

🚨 FRAMEWORK-VIOLATION: If using mocks in integration tests or mixing with unit strategies

**Core Principle**: Use REAL APIs and services for authentic end-to-end testing  
**Success Metric**: 80%+ pass rate through real system integration  
**Complementary**: Unit tests mock external dependencies, integration tests use real systems  
**V3 Strategy**: Clear separation between unit (mock) and integration (real) approaches  

---

## 🛑 **MANDATORY REAL API STRATEGY EXECUTION**

⚠️ MUST-READ: Integration tests MUST use real systems - no mocking allowed

### **✅ USE REAL SYSTEMS CHECKLIST**

**🔗 REAL EXTERNAL APIS (100% Real Rate)**
```python
# Use REAL HoneyHive API with test credentials
client = HoneyHive(api_key=os.getenv("HH_TEST_API_KEY"))
session_api = SessionAPI(client)

# REAL API calls for authentic testing
response = client.events.create_event(event_data)
session = session_api.create_session(session_data)

# Verify REAL responses
assert response.event_id is not None
assert session.session_id is not None
```

**🔗 REAL CONFIGURATION (Test Environment)**
```python
# Use REAL configuration with test environment
config = TracerConfig(
    api_key=os.getenv("HH_TEST_API_KEY"),
    project="integration-test-project",
    server_url="https://api.honeyhive.ai",  # Real endpoint
    verbose=True
)

tracer = HoneyHiveTracer(config=config)
```

**🔗 REAL LOGGING (Actual Output)**
```python
# Use REAL logging to verify actual output
import logging
logging.basicConfig(level=logging.DEBUG)

# Verify real log messages appear
with self.assertLogs('honeyhive', level='INFO') as log:
    tracer.create_event(event_data)
    self.assertIn('Event created successfully', log.output[0])
```

**🔗 REAL FILE SYSTEM (Test Directories)**
```python
# Use REAL file operations in test directories
test_dir = tempfile.mkdtemp()
config_file = os.path.join(test_dir, "test_config.json")

# Real file operations
with open(config_file, 'w') as f:
    json.dump(config_data, f)

# Cleanup after test
shutil.rmtree(test_dir)
```

---

## 🔗 **INTEGRATION TEST PATTERNS**

### **🌐 End-to-End Flow Testing**
```python
@pytest.mark.integration
def test_complete_tracing_flow():
    """Test complete flow with real APIs."""
    # Real tracer initialization
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_TEST_API_KEY"),
        project="integration-test"
    )
    
    # Real span creation
    with tracer.start_span("integration_test") as span:
        span.set_attribute("test_type", "integration")
        
        # Real event creation
        event_id = tracer.create_event(
            event_name="test_event",
            event_type="tool",
            inputs={"input": "test_data"},
            outputs={"output": "test_result"}
        )
        
        span.set_attribute("event_id", event_id)
    
    # Real flush to ensure data sent
    tracer.flush()
    
    # Verify real API responses
    assert event_id is not None
    assert len(event_id) > 0
```

### **🔧 Real Configuration Testing**
```python
@pytest.mark.integration
def test_real_configuration_loading():
    """Test configuration with real environment."""
    # Real environment variables
    test_api_key = os.getenv("HH_TEST_API_KEY")
    assert test_api_key is not None, "HH_TEST_API_KEY required for integration tests"
    
    # Real configuration creation
    config = TracerConfig(
        api_key=test_api_key,
        project="integration-test-project",
        verbose=True
    )
    
    # Real tracer initialization
    tracer = HoneyHiveTracer(config=config)
    
    # Verify real initialization
    assert tracer.project_name == "integration-test-project"
    assert tracer.api_key == test_api_key
    assert tracer._initialized is True
```

### **🌊 Real API Error Handling**
```python
@pytest.mark.integration
def test_real_api_error_handling():
    """Test error handling with real API failures."""
    # Real tracer with invalid credentials
    tracer = HoneyHiveTracer(
        api_key="invalid-api-key",
        project="integration-test"
    )
    
    # Real API call that will fail
    with pytest.raises(Exception) as exc_info:
        tracer.create_event(
            event_name="test_event",
            event_type="tool",
            inputs={"input": "test"}
        )
    
    # Verify real error response
    assert "authentication" in str(exc_info.value).lower()
```

---

## 🚨 **INTEGRATION TEST REQUIREMENTS**

### **🌐 REAL SYSTEM DEPENDENCIES**
```python
# REQUIRED: Real test environment setup
@pytest.fixture(scope="session")
def integration_environment():
    """Setup real test environment."""
    # Verify real API key available
    api_key = os.getenv("HH_TEST_API_KEY")
    if not api_key:
        pytest.skip("HH_TEST_API_KEY required for integration tests")
    
    # Verify real API connectivity
    client = HoneyHive(api_key=api_key)
    try:
        # Real API health check
        response = client.projects.list()
        assert response is not None
    except Exception as e:
        pytest.skip(f"HoneyHive API not accessible: {e}")
    
    return {
        "api_key": api_key,
        "client": client,
        "test_project": "integration-test-project"
    }
```

### **🧹 Real Resource Cleanup**
```python
@pytest.fixture
def cleanup_real_resources():
    """Cleanup real resources after tests."""
    created_resources = []
    
    yield created_resources
    
    # Cleanup real API resources
    for resource in created_resources:
        try:
            if hasattr(resource, 'delete'):
                resource.delete()
        except Exception as e:
            print(f"Warning: Failed to cleanup {resource}: {e}")
```

---

## 🏗️ **INTEGRATION TEST FUNCTIONALITY VERIFICATION**

### **🎯 Functionality Verification Targets**
- **API Functionality**: 100% (all API endpoints work correctly)
- **End-to-End Workflows**: 90%+ (complete user scenarios work)
- **Error Handling**: 80%+ (real error conditions handled properly)
- **Configuration Options**: 100% (all config options function correctly)
- **Backend Verification**: 100% (all events verified in HoneyHive backend using `verify_backend_event`)

### **🚨 NOT CONCERNED WITH CODE COVERAGE**
Integration tests focus on **functionality verification** and **SDK + backend system vetting**, not code coverage metrics. Code coverage is handled by unit tests.

### **🔍 Backend Verification with `verify_backend_event`**
All integration tests MUST verify that events appear correctly in the HoneyHive backend:

```python
from tests.utils.backend_verification import verify_backend_event
from tests.utils import generate_test_id

@pytest.mark.integration
def test_tracer_backend_verification():
    """Test that tracer events are properly stored in backend."""
    # Generate unique identifier for this test
    unique_id = generate_test_id()
    
    # Initialize tracer with real API
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_TEST_API_KEY"),
        project="integration-test"
    )
    
    # Create event with unique identifier
    with tracer.start_span("test-operation") as span:
        span.set_attribute("test.unique_id", unique_id)
        span.set_attribute("test.type", "integration")
        
        # Perform real operation
        result = some_real_operation()
        span.set_attribute("operation.result", result)
    
    # CRITICAL: Verify event appears in backend
    verified_event = verify_backend_event(
        client=tracer.client,  # Use tracer's client
        project="integration-test",
        unique_identifier=unique_id,
        expected_event_name="test-operation",
        debug_content=True  # Enable debugging for troubleshooting
    )
    
    # Verify event content matches expectations
    assert verified_event.event_name == "test-operation"
    assert verified_event.metadata["test"]["unique_id"] == unique_id
    assert verified_event.metadata["test"]["type"] == "integration"
```

### **🏗️ Backend Verification Features**
- **Dynamic Relationship Analysis**: Finds related spans using parent-child relationships
- **Retry Logic**: Built-in retry with exponential backoff for backend processing delays  
- **Multiple Search Strategies**: Event name, metadata, parent-child relationships
- **Debug Support**: Detailed logging for troubleshooting backend issues
- **Error Handling**: Clear error messages when backend verification fails

### **🌟 Real-World Scenarios**
```python
@pytest.mark.integration
def test_multi_instance_real_scenario():
    """Test multiple tracer instances with real APIs."""
    # Real scenario: Multiple projects
    tracer1 = HoneyHiveTracer(
        api_key=os.getenv("HH_TEST_API_KEY"),
        project="project-1"
    )
    
    tracer2 = HoneyHiveTracer(
        api_key=os.getenv("HH_TEST_API_KEY"), 
        project="project-2"
    )
    
    # Real concurrent operations
    with tracer1.start_span("operation-1") as span1:
        with tracer2.start_span("operation-2") as span2:
            # Real event creation in parallel
            event1 = tracer1.create_event(
                event_name="event-1",
                event_type="tool"
            )
            event2 = tracer2.create_event(
                event_name="event-2", 
                event_type="tool"
            )
    
    # Verify real isolation
    assert event1 != event2
    assert tracer1.project_name != tracer2.project_name
```

---

## 🛡️ **INTEGRATION TEST QUALITY GATES**

### **🚨 Pre-Generation Validation**
Before generating integration tests, verify:
- [ ] Real API credentials available
- [ ] Test environment configured
- [ ] Real API endpoints accessible
- [ ] Test project/resources available
- [ ] Cleanup procedures defined

### **📋 Post-Generation Validation**
After generating integration tests, verify:
- [ ] All tests use real APIs (no mocks for core functionality)
- [ ] Real error scenarios tested
- [ ] End-to-end flows validated
- [ ] Resource cleanup implemented
- [ ] Test isolation maintained

---

## 🔄 **INTEGRATION PATH PHASE INTEGRATION**

### **Phase 1: Method Verification → Real API Testing**
- Use function analysis to identify API integration points
- Test real function calls with actual parameters
- Validate real return values and responses

### **Phase 2: Logging Analysis → Real Logging**
- Test actual log output with real loggers
- Verify log levels and messages in real environment
- Test log aggregation and filtering

### **Phase 3: Dependency Analysis → Real Dependencies**
- Use real external APIs and services
- Test actual dependency integration
- Validate real error handling

### **Phase 4: Usage Patterns → Real Usage**
- Test actual usage patterns with real data
- Validate real-world scenarios
- Test performance with real systems

---

## ⚖️ **INTEGRATION VS UNIT STRATEGY**

### **🧪 UNIT TESTS (Mock Everything)**
```python
# Unit: Mock all external dependencies
@patch('requests.post')
@patch('honeyhive.api.client.HoneyHive')
def test_unit_event_creation(mock_client, mock_requests):
    # Complete isolation testing
    pass
```

### **🔗 INTEGRATION TESTS (Real Everything)**
```python
# Integration: Use real systems
@pytest.mark.integration
def test_integration_event_creation():
    # Real API testing
    client = HoneyHive(api_key=os.getenv("HH_TEST_API_KEY"))
    response = client.events.create_event(real_event_data)
    assert response.event_id is not None
```

---

## 🚀 **INTEGRATION TEST EXECUTION - NO COVERAGE**

### **🎯 Tox Configuration for Integration Tests**
```bash
# Run integration tests (NO COVERAGE - functionality verification focus)
tox -e integration

# Per tox.ini configuration:
# Line 24-25: "Integration tests WITHOUT coverage (behavior focus)"
# Command: "pytest tests/integration -v --asyncio-mode=auto --tb=short"
# 
# Key differences from unit tests:
# ❌ NO --cov flags (no coverage collection)
# ❌ NO --cov-report (no coverage reporting)  
# ❌ NO --cov-fail-under (no coverage thresholds)
# ✅ Real API credentials passed through (HH_TEST_API_KEY, etc.)
# ✅ Focus on functionality verification and backend vetting
```

### **🔍 Integration Test Environment**
```bash
# Required environment variables for integration tests:
export HH_TEST_API_KEY="your-test-api-key"
export HH_TEST_PROJECT="integration-test-project"
export HH_API_URL="https://api.honeyhive.ai"

# Optional LLM provider keys for instrumentor testing:
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Run with real backend verification
tox -e integration
```

---

## ✅ **INTEGRATION TEST SUCCESS CRITERIA**

**Integration tests are successful when:**
1. ✅ All API endpoints tested with real calls
2. ✅ End-to-end flows validated with `verify_backend_event`
3. ✅ Real error scenarios handled and verified in backend
4. ✅ Multi-instance scenarios tested with real isolation
5. ✅ Backend system vetting completed (all events verified)
6. ✅ Resource cleanup implemented
7. ✅ Test environment isolation maintained
8. ✅ SDK + backend integration functionality confirmed

**Integration test failure indicators:**
- Mocked core functionality (should be real)
- Missing real API connectivity
- No end-to-end flow validation
- Missing error scenario testing
- Resource leaks or cleanup failures

---

## 🎯 **INTEGRATION PATH ENFORCEMENT**

**When integration path is chosen:**
- Core functionality MUST use real APIs
- End-to-end flows MUST be validated
- Real error scenarios MUST be tested
- Resource cleanup MUST be implemented
- Test environment MUST be configured

**Path violation detection:**
- Core APIs mocked → VIOLATION (should be real)
- No end-to-end validation → VIOLATION
- Missing error scenarios → VIOLATION
- No resource cleanup → VIOLATION

**Success metric**: 80%+ first-run pass rate through comprehensive real API testing.
