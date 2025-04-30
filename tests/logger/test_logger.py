import os
import honeyhive
from honeyhive.logger import start, log, update, _retry_with_backoff
import uuid
from honeyhive.models import components, operations
import time
import urllib.error
import socket

def test_start_session():
    # Start a new session
    session_id = start(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session",
        server_url=os.environ["HH_API_URL"]
    )
    
    # Verify session_id is a valid UUID
    assert session_id is not None
    try:
        uuid.UUID(session_id)
    except ValueError:
        assert False, "session_id is not a valid UUID"
    
    # Update session with metadata
    update(
        event_id=session_id,
        metadata={"test": "value"},
    )
    
    # Wait for update to be processed
    time.sleep(5)
    
    # Verify session exists in API
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.session_id == session_id
    assert res.event.project_id is not None
    assert res.event.source == "sdk_test"
    assert res.event.metadata.get("test") == "value"

def test_start_session_with_metadata():
    # Test starting session with additional metadata
    metadata = {
        "test_key": "test_value",
        "version": "1.0.0"
    }
    
    session_id = start(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session_with_metadata",
        metadata=metadata,
        server_url=os.environ["HH_API_URL"]
    )
    
    # Wait for session to be processed
    time.sleep(5)
    
    # Verify session exists and metadata is correct
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.metadata is not None
    assert res.event.metadata.get("test_key") == "test_value"
    assert res.event.metadata.get("version") == "1.0.0"

def test_log_event():
    # First start a session
    session_id = start(
        source="sdk_test",
        session_name="test_log_event"
    )
    
    # Log an event
    event_name = "test_event"
    inputs = {"query": "test query"}
    outputs = {"result": "test result"}
    metadata = {"test_meta": "test_value"}
    
    event_id = log(
        session_id=session_id,
        event_name=event_name,
        event_type="model",
        config={"model": "test-model"},
        inputs=inputs,
        outputs=outputs,
        metadata=metadata,
        duration_ms=100
    )
    
    # Update event with feedback
    update(
        event_id=event_id,
        feedback={"rating": 5, "comment": "Great result!"}
    )
    
    # Wait for event to be processed
    time.sleep(10)
    
    # Verify event was logged correctly
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="event_id",
                value=event_id,
                operator=components.Operator.IS,
            )
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1
    event = res.object.events[0]
    assert event.event_name == event_name
    assert event.inputs.get("query") == inputs["query"]
    assert event.outputs.get("result") == outputs["result"]
    assert event.metadata.get("test_meta") == metadata["test_meta"]
    assert event.session_id == session_id
    assert event.feedback.get("rating") == 5
    assert event.feedback.get("comment") == "Great result!"

def test_log_event_with_metrics():
    # Start a session
    session_id = start(
        source="sdk_test",
        session_name="test_log_event_with_metrics"
    )
    
    # Log an event
    event_id = log(
        session_id=session_id,
        event_name="test_event_with_metrics",
        event_type="model",
        config={"model": "test-model"},
    )
    
    # Update event with metrics
    update(
        event_id=event_id,
        metrics={
            "latency": 0.5,
            "tokens_used": 100
        },
        verbose=True  # Enable verbose logging
    )
    
    # Wait for event to be processed - increased from 10 to 20 seconds
    print("Waiting for event to be processed...")
    time.sleep(20)
    
    # Verify event and metrics were logged correctly
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=[
            components.EventFilter(
                field="event_id",
                value=event_id,
                operator=components.Operator.IS,
            )
        ],
    )
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1
    assert res.object.events[0].metrics is not None, "Metrics should not be None"
    print(f"Actual metrics: {res.object.events[0].metrics}")
    print(f"Event ID: {event_id}")
    print(f"Session ID: {session_id}")
    assert res.object.events[0].metrics.get("latency") == 0.5, f"Expected latency 0.5, got {res.object.events[0].metrics.get('latency')}"
    assert res.object.events[0].metrics.get("tokens_used") == 100, f"Expected tokens_used 100, got {res.object.events[0].metrics.get('tokens_used')}"

def test_update_with_session_id():
    # Start a new session
    session_id = start(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session",
        server_url=os.environ["HH_API_URL"]
    )
    
    # Update using session_id
    update(
        event_id=session_id,
        metadata={"test": "value"},
    )
    
    # Wait for update to be processed
    time.sleep(5)
    
    # Verify update was successful
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.metadata is not None
    assert res.event.metadata.get("test") == "value"

def test_update_session():
    # Start a new session
    session_id = start(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session",
        server_url=os.environ["HH_API_URL"]
    )
    
    # Update session with metadata
    update(
        event_id=session_id,
        metadata={"test": "value"},
    )
    
    # Wait for update to be processed
    time.sleep(5)
    
    # Verify session exists in API with updated metadata
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.session_id == session_id
    assert res.event.metadata.get("test") == "value"

def test_retry_with_backoff_time_constraint():
    """Test that retry_with_backoff never exceeds 5 seconds total"""
    import time
    
    def fail_until_timeout():
        time.sleep(0.05)  # Reduced sleep time
        raise urllib.error.URLError("Connection failed")
    
    start_time = time.time()
    try:
        _retry_with_backoff(
            fail_until_timeout,
            max_retries=8,      # Reduced retries
            base_delay=0.05,    # Reduced base delay
            max_delay=0.2,      # Reduced max delay
            timeout=0.5         # Reduced timeout
        )
        assert False, "Should have raised an exception"
    except urllib.error.URLError:
        total_time = time.time() - start_time
        assert total_time < 5.0, f"Total time {total_time:.2f}s exceeded 5 second limit"

def test_retry_with_backoff_success():
    """Test that retry_with_backoff succeeds on first attempt"""
    def success_func():
        return "success"
    
    result = _retry_with_backoff(
        success_func,
        max_retries=3,
        base_delay=0.1,
        max_delay=0.5,
        timeout=1.0
    )
    assert result == "success"

def test_retry_with_backoff_retries():
    """Test that retry_with_backoff retries on failure and eventually succeeds"""
    attempts = 0
    
    def fail_then_succeed():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise urllib.error.URLError("Connection failed")
        return "success"
    
    result = _retry_with_backoff(
        fail_then_succeed,
        max_retries=3,
        base_delay=0.1,
        max_delay=0.5,
        timeout=1.0
    )
    assert result == "success"
    assert attempts == 3

def test_retry_with_backoff_max_retries():
    """Test that retry_with_backoff gives up after max retries"""
    attempts = 0
    
    def always_fail():
        nonlocal attempts
        attempts += 1
        raise urllib.error.URLError("Connection failed")
    
    try:
        _retry_with_backoff(
            always_fail,
            max_retries=2,
            base_delay=0.1,
            max_delay=0.5,
            timeout=1.0
        )
        assert False, "Should have raised an exception"
    except urllib.error.URLError:
        assert attempts == 3  # Initial attempt + 2 retries

def test_retry_with_backoff_non_retryable_error():
    """Test that retry_with_backoff immediately raises non-retryable errors"""
    attempts = 0
    
    def raise_value_error():
        nonlocal attempts
        attempts += 1
        raise ValueError("Non-retryable error")
    
    try:
        _retry_with_backoff(
            raise_value_error,
            max_retries=3,
            base_delay=0.1,
            max_delay=0.5,
            timeout=1.0
        )
        assert False, "Should have raised an exception"
    except ValueError:
        assert attempts == 1  # Should not retry for non-retryable errors

def test_retry_with_backoff_timeout():
    """Test that retry_with_backoff handles socket timeouts"""
    attempts = 0
    
    def timeout_then_succeed():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise socket.timeout("Connection timed out")
        return "success"
    
    result = _retry_with_backoff(
        timeout_then_succeed,
        max_retries=3,
        base_delay=0.1,
        max_delay=0.5,
        timeout=1.0
    )
    assert result == "success"
    assert attempts == 2

if __name__ == "__main__":
    test_start_session()
    test_start_session_with_metadata()
    test_log_event()
    test_log_event_with_metrics()
    test_update_session()
    test_retry_with_backoff_success()
    test_retry_with_backoff_retries()
    test_retry_with_backoff_max_retries()
    test_retry_with_backoff_non_retryable_error()
    test_retry_with_backoff_timeout()
    test_retry_with_backoff_time_constraint()