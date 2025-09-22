# Integration Testing Standards - Advanced Reference

**🎯 Advanced integration testing requirements and real-world scenarios for the HoneyHive Python SDK**

## 🚨 **MANDATORY: Use Test Generation Framework First**

**⛔ BEFORE using these standards, AI assistants MUST follow the comprehensive framework:**

- **📋 Framework Hub**: [Test Generation Framework](../ai-assistant/code-generation/tests/README.md)
- **🚀 Integration Test Path**: Framework → Setup → Integration Test Analysis → Integration Test Generation → Integration Test Quality
- **🎯 Embedded Standards**: Framework includes no-mocks policy, backend verification, and proven fixtures

**🚨 RULE**: This document provides **real-world scenarios** that complement the framework's embedded integration test standards

---

## 🚨 **Advanced No-Mocks Examples**

### **Complex Real API Integration**
```python
def test_multi_service_integration() -> None:
    """Test integration across multiple real services."""
    # Real environment setup
    load_dotenv()
    
    # Real clients - no mocks
    honeyhive_client = HoneyHive(api_key=os.getenv("HH_API_KEY"))
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Real tracer with real OTLP export
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="integration-test",
        session_name=f"multi-service-{int(time.time())}"
    )
    
    # Real workflow
    with tracer.start_session() as session:
        # Real OpenAI call
        with tracer.start_span("openai-call", event_type="model") as span:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test integration"}],
                max_tokens=10
            )
            span.set_attribute("model.response", response.choices[0].message.content)
        
        # Real data processing
        with tracer.start_span("data-processing", event_type="tool") as span:
            processed_data = process_openai_response(response)
            span.set_attribute("processing.result", processed_data)
    
    # Real backend verification - no mocks
    time.sleep(2)  # Allow async processing
    events = honeyhive_client.events.list_events(
        project="integration-test",
        session_id=session.session_id
    )
    
    # Verify real data flow
    assert len(events) >= 2
    event_types = [e.event_type for e in events]
    assert "model" in event_types
    assert "tool" in event_types
```

### **Real Error Handling Integration**
```python
def test_real_error_recovery_integration() -> None:
    """Test error recovery with real service failures."""
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="error-integration-test"
    )
    
    # Test with real invalid API key scenario
    invalid_client = HoneyHive(api_key="invalid-key-12345")
    
    with tracer.start_session() as session:
        # This will cause real API error
        try:
            with tracer.start_span("failing-operation") as span:
                # Real API call that will fail
                invalid_client.events.create_event({
                    "event_type": "model",
                    "inputs": {"test": "data"}
                })
        except Exception as e:
            # Real error handling
            span.record_exception(e)
            span.set_status("ERROR", str(e))
    
    # Verify real error was captured in backend
    time.sleep(2)
    events = tracer.client.events.list_events(
        project="error-integration-test",
        session_id=session.session_id
    )
    
    error_events = [e for e in events if e.get("status") == "ERROR"]
    assert len(error_events) > 0
    assert "invalid" in error_events[0].get("error", "").lower()
```

---

## 🎯 **Advanced Real-World Scenarios**

### **Production-Like Workflow Testing**
```python
def test_production_like_llm_application() -> None:
    """Test complete production-like LLM application workflow."""
    # Real production-like setup
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="prod-like-integration",
        session_name=f"user-session-{uuid.uuid4()}"
    )
    
    # Simulate real user conversation
    conversation_history = []
    
    with tracer.start_session() as session:
        # User input processing (real)
        with tracer.start_span("input-validation", event_type="tool") as span:
            user_input = "What are the benefits of machine learning?"
            validated_input = validate_and_sanitize_input(user_input)
            span.set_attribute("input.original", user_input)
            span.set_attribute("input.validated", validated_input)
        
        # Context retrieval (real database/vector store)
        with tracer.start_span("context-retrieval", event_type="tool") as span:
            relevant_context = retrieve_relevant_context(validated_input)
            span.set_attribute("context.documents_found", len(relevant_context))
            span.set_attribute("context.relevance_score", calculate_relevance_score(relevant_context))
        
        # LLM call with context (real OpenAI API)
        with tracer.start_span("llm-generation", event_type="model") as span:
            prompt = build_prompt_with_context(validated_input, relevant_context, conversation_history)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            span.set_attribute("model.name", "gpt-4")
            span.set_attribute("model.temperature", 0.7)
            span.set_attribute("model.max_tokens", 500)
            span.set_attribute("model.prompt_tokens", response.usage.prompt_tokens)
            span.set_attribute("model.completion_tokens", response.usage.completion_tokens)
        
        # Response processing (real)
        with tracer.start_span("response-processing", event_type="tool") as span:
            processed_response = process_and_format_response(response.choices[0].message.content)
            conversation_history.append({"user": user_input, "assistant": processed_response})
            span.set_attribute("response.length", len(processed_response))
            span.set_attribute("response.formatted", True)
        
        # Analytics and logging (real)
        with tracer.start_span("analytics", event_type="tool") as span:
            analytics_data = calculate_conversation_analytics(conversation_history)
            log_conversation_metrics(analytics_data)
            span.set_attribute("analytics.conversation_length", len(conversation_history))
            span.set_attribute("analytics.total_tokens", analytics_data["total_tokens"])
    
    # Verify complete workflow in backend
    time.sleep(3)  # Allow processing
    
    events = tracer.client.events.list_events(
        project="prod-like-integration",
        session_id=session.session_id
    )
    
    # Verify all workflow steps captured
    expected_spans = ["input-validation", "context-retrieval", "llm-generation", "response-processing", "analytics"]
    captured_spans = [e.event_name for e in events]
    
    for expected_span in expected_spans:
        assert expected_span in captured_spans, f"Missing span: {expected_span}"
    
    # Verify model event has proper attributes
    model_events = [e for e in events if e.event_type == "model"]
    assert len(model_events) == 1
    model_event = model_events[0]
    assert model_event.metadata.get("model.name") == "gpt-4"
    assert model_event.metadata.get("model.prompt_tokens") > 0
    assert model_event.metadata.get("model.completion_tokens") > 0
```

### **Multi-Tenant Integration Testing**
```python
def test_multi_tenant_isolation() -> None:
    """Test multi-tenant isolation with real projects."""
    # Create tracers for different tenants
    tenant_a_tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="tenant-a-integration",
        session_name=f"tenant-a-{int(time.time())}"
    )
    
    tenant_b_tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="tenant-b-integration",
        session_name=f"tenant-b-{int(time.time())}"
    )
    
    # Parallel operations for different tenants
    with tenant_a_tracer.start_session() as session_a:
        with tenant_a_tracer.start_span("tenant-a-operation") as span:
            span.set_attribute("tenant.id", "tenant-a")
            span.set_attribute("operation.type", "data-processing")
    
    with tenant_b_tracer.start_session() as session_b:
        with tenant_b_tracer.start_span("tenant-b-operation") as span:
            span.set_attribute("tenant.id", "tenant-b")
            span.set_attribute("operation.type", "model-inference")
    
    # Verify tenant isolation in backend
    time.sleep(2)
    
    tenant_a_events = tenant_a_tracer.client.events.list_events(
        project="tenant-a-integration",
        session_id=session_a.session_id
    )
    
    tenant_b_events = tenant_b_tracer.client.events.list_events(
        project="tenant-b-integration", 
        session_id=session_b.session_id
    )
    
    # Verify isolation
    assert len(tenant_a_events) > 0
    assert len(tenant_b_events) > 0
    
    # Verify no cross-contamination
    for event in tenant_a_events:
        assert event.project == "tenant-a-integration"
        assert event.metadata.get("tenant.id") == "tenant-a"
    
    for event in tenant_b_events:
        assert event.project == "tenant-b-integration"
        assert event.metadata.get("tenant.id") == "tenant-b"
```

---

## 🚀 **Advanced Performance Integration**

### **High-Throughput Testing**
```python
def test_high_throughput_integration() -> None:
    """Test high-throughput scenarios with real backend."""
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="throughput-integration",
        batch_size=50,  # Real batching
        flush_interval=1.0  # Real timing
    )
    
    start_time = time.time()
    
    with tracer.start_session() as session:
        # Generate high volume of real spans
        for i in range(100):
            with tracer.start_span(f"high-throughput-span-{i}") as span:
                span.set_attribute("span.index", i)
                span.set_attribute("batch.test", "throughput")
                
                # Simulate real processing
                time.sleep(0.01)  # 10ms processing time
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Force flush and wait for backend processing
    tracer.flush()
    time.sleep(5)
    
    # Verify all spans reached backend
    events = tracer.client.events.list_events(
        project="throughput-integration",
        session_id=session.session_id
    )
    
    assert len(events) == 100, f"Expected 100 events, got {len(events)}"
    
    # Verify performance characteristics
    assert processing_time < 10.0, f"Processing took too long: {processing_time}s"
    
    # Verify batching worked (check timestamps)
    timestamps = [e.created_at for e in events]
    timestamp_spread = max(timestamps) - min(timestamps)
    assert timestamp_spread < 60, "Events should be processed within 60 seconds"
```

### **Resource Cleanup Integration**
```python
def test_resource_cleanup_integration() -> None:
    """Test proper resource cleanup in real environment."""
    created_sessions = []
    
    try:
        # Create multiple real sessions
        for i in range(3):
            tracer = HoneyHiveTracer(
                api_key=os.getenv("HH_API_KEY"),
                project="cleanup-integration",
                session_name=f"cleanup-test-{i}-{int(time.time())}"
            )
            
            with tracer.start_session() as session:
                created_sessions.append(session.session_id)
                
                # Create some real spans
                with tracer.start_span(f"cleanup-span-{i}") as span:
                    span.set_attribute("cleanup.test", True)
                    span.set_attribute("session.index", i)
        
        # Verify sessions were created
        time.sleep(2)
        
        for session_id in created_sessions:
            events = tracer.client.events.list_events(
                project="cleanup-integration",
                session_id=session_id
            )
            assert len(events) > 0, f"No events found for session {session_id}"
    
    finally:
        # Real cleanup - delete test sessions
        for session_id in created_sessions:
            try:
                tracer.client.sessions.delete_session(session_id)
            except Exception as e:
                # Log but don't fail test
                print(f"Cleanup warning: Could not delete session {session_id}: {e}")
```

---

## 📊 **Advanced Validation Patterns**

### **End-to-End Data Flow Validation**
```python
def test_end_to_end_data_flow() -> None:
    """Test complete data flow from input to backend storage."""
    unique_id = f"e2e-test-{uuid.uuid4()}"
    
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project="e2e-data-flow",
        session_name=f"e2e-session-{unique_id}"
    )
    
    test_data = {
        "unique_id": unique_id,
        "test_type": "end_to_end",
        "input_data": "test input for e2e validation",
        "expected_output": "processed test output"
    }
    
    with tracer.start_session() as session:
        # Step 1: Input processing
        with tracer.start_span("input-processing", event_type="tool") as span:
            span.set_attribute("input.unique_id", unique_id)
            span.set_attribute("input.data", test_data["input_data"])
            processed_input = process_input(test_data["input_data"])
        
        # Step 2: Model processing
        with tracer.start_span("model-processing", event_type="model") as span:
            span.set_attribute("model.unique_id", unique_id)
            span.set_attribute("model.input", processed_input)
            model_output = simulate_model_processing(processed_input)
            span.set_attribute("model.output", model_output)
        
        # Step 3: Output processing
        with tracer.start_span("output-processing", event_type="tool") as span:
            span.set_attribute("output.unique_id", unique_id)
            span.set_attribute("output.raw", model_output)
            final_output = process_output(model_output)
            span.set_attribute("output.final", final_output)
    
    # Comprehensive backend validation
    time.sleep(3)
    
    # Validate session exists
    session_data = tracer.client.sessions.get_session(session.session_id)
    assert session_data.session_id == session.session_id
    assert unique_id in session_data.session_name
    
    # Validate all events exist
    events = tracer.client.events.list_events(
        project="e2e-data-flow",
        session_id=session.session_id
    )
    
    assert len(events) == 3, f"Expected 3 events, got {len(events)}"
    
    # Validate data flow continuity
    events_by_name = {e.event_name: e for e in events}
    
    input_event = events_by_name["input-processing"]
    model_event = events_by_name["model-processing"]
    output_event = events_by_name["output-processing"]
    
    # Validate unique_id propagation
    assert input_event.metadata.get("input.unique_id") == unique_id
    assert model_event.metadata.get("model.unique_id") == unique_id
    assert output_event.metadata.get("output.unique_id") == unique_id
    
    # Validate data transformation chain
    assert input_event.metadata.get("input.data") == test_data["input_data"]
    assert model_event.metadata.get("model.input") == process_input(test_data["input_data"])
    assert output_event.metadata.get("output.final") is not None
```

---

## 💡 **Best Practices Summary**

### **Real Environment Testing**
- **Use actual credentials** - test with real API keys in secure environment
- **Test real workflows** - mirror production usage patterns exactly
- **Validate backend state** - verify data actually reaches and is processed by backend
- **Handle real errors** - test actual service failures and recovery

### **Performance Considerations**
- **Account for latency** - real APIs have network delays
- **Test batching** - verify batch processing works with real backend
- **Resource management** - proper cleanup of real resources
- **Parallel safety** - ensure tests work in parallel execution

### **Data Validation**
- **End-to-end verification** - trace data from input to backend storage
- **Unique identifiers** - use UUIDs to avoid test interference
- **Comprehensive assertions** - verify both success and error scenarios
- **Backend consistency** - ensure data integrity across service boundaries

---

**💡 Key Principle**: These advanced integration scenarios demonstrate real-world testing techniques that complement the framework's embedded standards for complex, production-like testing scenarios.