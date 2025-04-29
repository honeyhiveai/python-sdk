import os
import honeyhive
from honeyhive.logger import start, log, update
import uuid
from honeyhive.models import components, operations
import time

def test_start_session():
    # Start a new session
    session_id = start(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        env="sdk_test",
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
        env="sdk_test",
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
        env="sdk_test",
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
        env="sdk_test",
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
        env="sdk_test",
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
        env="sdk_test",
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
    
if __name__ == "__main__":
    test_start_session()
    test_start_session_with_metadata()
    test_log_event()
    test_log_event_with_metrics()
    test_update_session()