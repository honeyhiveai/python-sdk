import os
import time
from honeyhive import HoneyHive
from honeyhive.models import components, operations


MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer


if __name__ == "__main__":
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        session_name="Session Name",
        source="source_identifier",
        server_url=HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )

    current_session_id = tracer.session_id

    # Set two or more of the following at once (this overwrites the previous individual calls)
    final_feedback = {'some_domain_expert': "Final feedback"}
    final_metrics = {"final_metric": 1.0}
    final_metadata = {"final_key": "final_value"}
    tracer.enrich_session(
        feedback=final_feedback,
        metrics=final_metrics,
        metadata=final_metadata
    )
    assert tracer.session_id is not None

    # Allow time for events to be processed
    time.sleep(5)

    # Initialize SDK and fetch events
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=HONEYHIVE_SERVER_URL
    )

    req = operations.GetEventsRequestBody(
        project=MY_HONEYHIVE_PROJECT_NAME,
        filters=[
            components.EventFilter(
                field="session_id",
                value=current_session_id,  # Use the session_id from the tracer
                operator=components.Operator.IS,
            )
        ],
    )

    res = sdk.events.get_events(request=req)

    # Assertions
    assert res.object is not None
    # Expecting at least 1 event: Session Start
    assert len(res.object.events) >= 1, f"Expected at least 1 event for session {current_session_id}, found {len(res.object.events)}"
    # Find the session start event
    session_event = next((e for e in res.object.events if e.event_type == 'session'), None)
    assert session_event is not None, "Session start event not found"
    # Verify the final feedback, metrics, and metadata
    assert session_event.feedback == final_feedback
    assert 'final_metric' in session_event.metrics
    assert 'final_key' in session_event.metadata