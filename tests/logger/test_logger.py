import os
import honeyhive
from honeyhive.tracer import start_session, log
import uuid
from honeyhive.models import components, operations
import time

def test_start_session():
    # Start a new session
    session_id = start_session(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session",
        server_url=os.environ["HH_API_URL"],
        verbose=True
    )
    
    # Verify session_id is a valid UUID
    assert session_id is not None
    try:
        uuid.UUID(session_id)
    except ValueError:
        assert False, "session_id is not a valid UUID"
    
    # Verify session exists in API
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.session_id == session_id
    assert res.event.project_id is not None
    assert res.event.source == "sdk_test"

def test_start_session_with_metadata():
    # Test starting session with additional metadata
    metadata = {
        "test_key": "test_value",
        "version": "1.0.0"
    }
    
    session_id = start_session(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_session_with_metadata",
        metadata=metadata,
        server_url=os.environ["HH_API_URL"]
    )
    
    # Verify session exists and metadata is correct
    sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
    res = sdk.session.get_session(session_id=session_id)
    assert res.event is not None
    assert res.event.metadata is not None
    assert res.event.metadata.get("test_key") == "test_value"
    assert res.event.metadata.get("version") == "1.0.0"

def test_log_event():
    # First start a session
    session_id = start_session(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_log_event"
    )
    
    # Log an event
    event_name = "test_event"
    inputs = {"query": "test query"}
    outputs = {"result": "test result"}
    metadata = {"test_meta": "test_value"}
    
    event_id = log(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        session_id=session_id,
        event_name=event_name,
        inputs=inputs,
        outputs=outputs,
        metadata=metadata,
        server_url=os.environ["HH_API_URL"],
        verbose=True
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

def test_log_event_with_feedback():
    # Start a session
    session_id = start_session(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_log_event_with_feedback"
    )
    
    # Log an event with feedback
    feedback = {
        "rating": 5,
        "comment": "Great result!"
    }
    
    event_id = log(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        session_id=session_id,
        event_name="test_event_with_feedback",
        feedback=feedback,
        server_url=os.environ["HH_API_URL"]
    )
    
    # Wait for event to be processed
    time.sleep(5)
    
    # Verify event and feedback were logged correctly
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
    assert res.object.events[0].feedback is not None
    assert res.object.events[0].feedback.get("rating") == feedback["rating"]
    assert res.object.events[0].feedback.get("comment") == feedback["comment"]

def test_log_event_with_metrics():
    # Start a session
    session_id = start_session(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        source="sdk_test",
        session_name="test_log_event_with_metrics"
    )
    
    # Log an event with metrics
    metrics = {
        "latency": 0.5,
        "tokens_used": 100
    }
    
    event_id = log(
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        session_id=session_id,
        event_name="test_event_with_metrics",
        metrics=metrics,
        server_url=os.environ["HH_API_URL"]
    )
    
    # Wait for event to be processed
    time.sleep(5)
    
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
    assert res.object.events[0].metrics is not None
    assert res.object.events[0].metrics.get("latency") == metrics["latency"]
    assert res.object.events[0].metrics.get("tokens_used") == metrics["tokens_used"]

if __name__ == "__main__":
    test_start_session()
    test_start_session_with_metadata()
    test_log_event()
    test_log_event_with_feedback()
    test_log_event_with_metrics()