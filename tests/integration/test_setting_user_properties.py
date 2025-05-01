import os
import time
from honeyhive import HoneyHive
from honeyhive.models import components, operations

MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

from honeyhive import HoneyHiveTracer, enrich_session

if __name__ == "__main__":

    # Store the tracer instance to access session_id later
    tracer = HoneyHiveTracer.init(
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        server_url=HONEYHIVE_SERVER_URL # Optional / Required for self-hosted or dedicated deployments
    )

    current_session_id = tracer.session_id

    user_props = {
        "user_id": "12345",
        "user_email": "user@example.com",
        "user_properties": {
            "is_premium": True,
            "subscription_plan": "pro",
            "last_login": "2024-01-01T12:00:00Z"
        }
    }

    enrich_session(user_properties=user_props)

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
    assert session_event.user_properties is not None, "User properties not found in session start event"

    # Verify the user properties
    assert session_event.user_properties == user_props