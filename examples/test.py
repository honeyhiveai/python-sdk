import time

from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHive, HoneyHiveTracer, trace
from honeyhive.models import EventFilter

# Initialize tracer
tracer = HoneyHiveTracer.init(
    verbose=True,
)

# Initialize instrumentor - auto-traces OpenAI calls
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)


# Trace any function in your code using @trace() decorator
@trace()
def call_openai():
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What is the meaning of life?"}],
    )
    print(completion.choices[0].message.content)


call_openai()

# Flush the tracer to ensure all spans are exported
tracer.force_flush()

# Wait for events to be processed
print("\nWaiting 10 seconds for events to be processed...")
time.sleep(10)

# Fetch events for this session using the SDK client
session_id = tracer.session_id
project_name = tracer.project_name

print(f"\nFetching events for session: {session_id}")
print(f"Project: {project_name}")

try:
    # Use the HoneyHive API client to export events
    client = HoneyHive()

    # Export events using the new export() method with EventFilter
    response = client.events.export(
        project=project_name,
        filters=[
            EventFilter(
                field="session_id",
                operator="is",
                value=session_id,
                type="string",
            )
        ],
        limit=100,
    )

    print(f"\nFound {len(response.events)} events (total: {response.total_events}):")
    for event in response.events:
        print(f"  - {event.get('event_name', 'N/A')} (type: {event.get('event_type', 'N/A')})")

    # Alternative: Use backwards-compatible list_events() alias
    # response = client.events.list_events(
    #     project=project_name,
    #     filters=[{"field": "session_id", "operator": "is", "value": session_id, "type": "string"}],
    #     limit=100,
    # )
except Exception as e:
    print(f"\nError fetching events: {e}")
