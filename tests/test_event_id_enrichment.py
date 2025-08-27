from honeyhive.tracer import HoneyHiveTracer
from honeyhive import trace, enrich_span
import honeyhive
from honeyhive.models import components, operations
import os
import uuid
import time


# Set up SDK client for event validation
sdk = honeyhive.HoneyHive(
    bearer_auth=os.getenv("HH_API_KEY"),
    server_url=os.getenv("HH_API_URL")
)

def start_conversation():
    conversation_id = str(uuid.uuid4())
    print("Starting conversation with ID:", conversation_id)

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_id=conversation_id
    )
    # all future spans in this call stack will have conversation_id as session_id

    turn_id = new_turn("hi")
    print("Turn response:", turn_id)
    
    return conversation_id, turn_id

@trace
def new_turn(message: str):
    turn_id = str(uuid.uuid4())
    print("Starting new turn with ID:", turn_id)
    enrich_span(event_id=turn_id)
    return turn_id

def test_event_id_enrichment():
    conversation_id, turn_id = start_conversation()
    
    # Wait for events to be processed and indexed
    print("Waiting for events to be processed...")
    time.sleep(10)
    
    # Query events to validate that the turn_id was set as event_id
    req = operations.GetEventsRequestBody(
        project=os.getenv("HH_PROJECT"),
        filters=[
            components.EventFilter(
                field="session_id",
                value=conversation_id,
                operator=components.Operator.IS,
            ),
            components.EventFilter(
                field="event_name",
                value="new_turn",
                operator=components.Operator.IS,
            ),
        ],
    )
    
    res = sdk.events.get_events(request=req)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.events) == 1
    
    # Validate that the event_id matches the turn_id we set
    event = res.object.events[0]
    print(f"Event ID from response: {event.event_id}")
    print(f"Expected turn ID: {turn_id}")
    
    assert event.event_id == turn_id, f"Expected event_id to be {turn_id}, but got {event.event_id}"
    
    print("✅ Test passed: turn_id was correctly set as event_id")

if __name__ == "__main__":
    test_event_id_enrichment()
