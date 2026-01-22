import os
import time
from datetime import datetime, timedelta, timezone
import httpx

from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer, trace

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
print("\nWaiting 5 seconds for events to be processed...")
time.sleep(10)

# Fetch events for this session using direct httpx request
session_id = tracer.session_id
project_name = tracer.project_name
api_url = os.environ.get("HH_API_URL", "http://localhost:3000")
api_key = os.environ.get("HH_API_KEY", "")

print(f"\nFetching events for session: {session_id}")
print(f"Project: {project_name}")

try:
    # Build dateRange (required for ClickHouse query)
    now = datetime.now(timezone.utc)
    ten_minutes_ago = now - timedelta(minutes=10)
    ten_minutes_later = now + timedelta(minutes=10)

    response = httpx.post(
        f"{api_url}/v1/events/export",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "project": project_name,
            "filters": [
                {
                    "field": "session_id",
                    "operator": "is",
                    "value": session_id,
                    "type": "string",
                }
            ],
            "limit": 100,
        },
    )
    response.raise_for_status()
    data = response.json()
    events = data.get("events", [])
    total = data.get("count", 0)
    print(f"\nFound {len(events)} events (total: {total}):")
    for event in events:
        print(f"  - {event.get('event_name', 'N/A')} (type: {event.get('event_type', 'N/A')})")
except Exception as e:
    print(f"\nError fetching events: {e}")
