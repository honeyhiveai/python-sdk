import honeyhive
import os
import time
import uuid
from honeyhive.models import components, operations

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)

test_event = components.CreateEventRequest(
    project=os.environ["HH_PROJECT"],
    source='SDK Test',
    event_name='Python SDK Test Event',
    event_type=components.CreateEventRequestEventType.TOOL,
    config={},
    inputs=components.CreateEventRequestInputs(),
    duration=0
)

test_model_event = components.CreateModelEvent(
    project=os.environ["HH_PROJECT"],
    model='gpt-4o',
    provider='openai',
    messages=[
        {
            'role': 'system',
            'content': 'Hello, world!',
        }
    ],
    response={
        'role': 'assistant',
        'content': 'Hello, world!',
    },
    duration=42,
    usage={
        'prompt_tokens': 10,
        'completion_tokens': 10,
        'total_tokens': 20,
    },
    cost=0.00008,
    error=None,
    source='playground',
    event_name='Model Completion',
    hyperparameters={
        'temperature': 0,
        'top_p': 1,
        'max_tokens': 1000,
        'presence_penalty': 0,
        'frequency_penalty': 0,
        'stop': '<value>',
        'n': 1,
    },
    template=[
        {
            'role': 'system',
            'content': 'Hello, {{ name }}!',
        }
    ],
    template_inputs={
        'name': 'world',
    },
    tools=[
        {
            'key': '<value>',
        }
    ],
    tool_choice='none',
    response_format={
        'type': 'text',
    },
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
        event=test_event
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

def test_valid_event_batch_post_request():
    # Create a batch of events
    batch = [test_event, test_event]

    # Send batch event request
    req = operations.CreateEventBatchRequestBody(
        events=batch
    )
    res = sdk.events.create_event_batch(req)

    # Validate response
    assert res.status_code == 200
    event_ids = res.object.event_ids
    assert isinstance(event_ids, list)
    assert len(event_ids) == 2

def test_valid_event_batch_post_request_single_session():
    # Create a batch of events
    batch = [test_event, test_event]

    # Send batch event request with single session flag
    req = operations.CreateEventBatchRequestBody(
        events=batch,
        is_single_session=True
    )
    res = sdk.events.create_event_batch(req)

    # Validate response
    assert res.status_code == 200
    event_ids = res.object.event_ids
    assert isinstance(event_ids, list)
    assert len(event_ids) == 2
    session_id = res.object.session_id
    assert isinstance(session_id, str)

def test_valid_openai_model_event_post_request():
    # Create and send model event request
    req = operations.CreateModelEventRequestBody(
        event=test_model_event
    )
    res = sdk.events.create_model_event(req)

    # Validate initial response
    assert res.status_code == 200
    time.sleep(WAIT_TIME)
    model_event_id = res.object.event_id

    # Create filters and parameters for fetching the event
    filters = [
        components.EventFilter(
            field="event_id",
            operator=components.Operator.IS,
            value=model_event_id
        )
    ]
    params = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=filters
    )

    # Fetch the event
    fetch_res = sdk.events.get_events(params)

    # Validate fetch response
    assert fetch_res.status_code == 200
    events = fetch_res.object.events
    assert isinstance(events, list)
    assert len(events) == 1

    # Validate event details
    event = events[0]
    assert event.duration == 42
    assert event.config["model"] == "gpt-4o"

def test_valid_event_model_batch_post_request():
    # Create a batch of model events
    batch = [test_model_event, test_model_event]

    # Send batch model event request
    req = operations.CreateModelEventBatchRequestBody(
        model_events=batch
    )
    res = sdk.events.create_model_event_batch(req)

    # Validate response
    assert res.status_code == 200
    event_ids = res.object.event_ids
    assert isinstance(event_ids, list)
    assert len(event_ids) == 2

    # fetch the events
    filters = [
        components.EventFilter(
            field="event_id",
            operator=components.Operator.IS,
            value=event_ids[0]
        )
    ]
    params = operations.GetEventsRequestBody(
        project=os.environ["HH_PROJECT"],
        filters=filters
    )

    # Fetch the event
    fetch_res = sdk.events.get_events(params)

    # Validate fetch response
    assert fetch_res.status_code == 200
    events = fetch_res.object.events
    assert isinstance(events, list)
    assert len(events) == 1
    event = events[0]
    assert event.duration == 42
