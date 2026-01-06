"""Example: Query traces from HoneyHive.

This example demonstrates how to programmatically query and export trace data
using the HoneyHive SDK.

Tested and verified working on 2026-01-06.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from honeyhive.api.client import HoneyHive
from honeyhive.models import EventFilter
from honeyhive.models.generated import Operator, Type

# Initialize client
client = HoneyHive(api_key=os.environ["HH_API_KEY"])
project_name = os.environ.get("HH_PROJECT", "test-project")

print(f"Querying traces from project: {project_name}\n")

# =============================================================================
# Example 1: Query model events
# =============================================================================
print("1. Query model events:")
result = client.events.get_events(
    project=project_name,
    filters=[
        EventFilter(
            field="event_type",
            value="model",
            operator=Operator.is_,
            type=Type.string,
        )
    ],
    limit=5,
)
print(f"   Total: {result['totalEvents']}, Returned: {len(result['events'])}")

# =============================================================================
# Example 2: Query all events in a specific session
# =============================================================================
print("\n2. Query events in a session:")
if result["events"]:
    session_id = result["events"][0].session_id
    session_result = client.events.get_events(
        project=project_name,
        filters=[
            EventFilter(
                field="session_id",
                value=session_id,
                operator=Operator.is_,
                type=Type.string,
            )
        ],
    )
    print(f"   Session {session_id[:8]}... has {len(session_result['events'])} events")

# =============================================================================
# Example 3: Query sessions only
# =============================================================================
print("\n3. Query sessions:")
sessions = client.events.get_events(
    project=project_name,
    filters=[
        EventFilter(
            field="event_type",
            value="session",
            operator=Operator.is_,
            type=Type.string,
        )
    ],
    limit=5,
)
print(f"   Total sessions: {sessions['totalEvents']}")

# =============================================================================
# Example 4: Query with multiple filters (e.g., model events with feedback)
# =============================================================================
print("\n4. Query with multiple filters:")
filtered = client.events.get_events(
    project=project_name,
    filters=[
        EventFilter(
            field="event_type",
            value="model",
            operator=Operator.is_,
            type=Type.string,
        ),
        # Add more filters as needed:
        # EventFilter(
        #     field="feedback.rating",
        #     value="5",
        #     operator=Operator.is_,
        #     type=Type.number,
        # ),
    ],
    limit=10,
)
print(f"   Found: {filtered['totalEvents']} events")

print("\nDone!")
