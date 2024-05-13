import honeyhive
import os
import time
import uuid
from honeyhive.models import components, operations

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


def test_post_event():
    # Start session
    session_name = f"Python SDK Test {str(uuid.uuid4())}"
    res = sdk.session.start_session(
        request=operations.StartSessionRequestBody(
            session=components.SessionStartRequest(
                project=os.environ["HH_PROJECT"],
                session_name=session_name,
                source="SDK Test",
            )
        )
    )
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.session_id is not None

    # Get session
    time.sleep(5)
    session_id = res.object.session_id
    res = sdk.session.get_session(session_id=session_id)
    assert res.status_code == 200
    assert res.event is not None

    # Post event to session
    req = operations.CreateEventRequestBody(
        event=components.CreateEventRequest(
            project=os.environ["HH_PROJECT"],
            source="Python SDK Test",
            event_name="Python SDK Test Event",
            event_type=components.CreateEventRequestEventType.TOOL,
            config={},
            inputs=components.CreateEventRequestInputs(),
            duration=0,
        )
    )
    res = sdk.events.create_event(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.event_id is not None

    # Get event
    time.sleep(5)
    event_id = res.object.event_id
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
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

    # Update event
    random_string = str(uuid.uuid4())
    req = operations.UpdateEventRequestBody(
        event_id=event_id, metadata={"random_value": random_string}
    )
    res = sdk.events.update_event(request=req)
    assert res.status_code == 200

    # Get event
    time.sleep(5)
    req = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT_ID"],
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
    assert res.object.events[0].metadata.get("random_value") == random_string
