#!/usr/bin/env python3
"""
Example: Get tool call events for evaluation purposes.

This demonstrates the CORRECT way to filter events using get_events()
with multiple filters, which is more powerful than list_events().
"""

import os
from dotenv import load_dotenv
from honeyhive import HoneyHive
from honeyhive.api import EventsAPI
from honeyhive.models.generated import EventFilter, Operator, Type

load_dotenv()


def get_tool_calls_for_evaluation(
    project: str,
    session_id: str = None,
    limit: int = 100
):
    """
    Retrieve tool call events for evaluation.
    
    Args:
        project: Project name
        session_id: Optional session ID to filter by
        limit: Maximum number of events to return
        
    Returns:
        Dict with 'events' (List[Event]) and 'totalEvents' (int)
    """
    honeyhive = HoneyHive(
        api_key=os.environ["HH_API_KEY"],
        server_url=os.environ.get("HH_API_URL", "https://api.honeyhive.ai")
    )
    
    events_api = EventsAPI(honeyhive)
    
    # Build filters for tool calls
    filters = [
        EventFilter(
            field="event_type",
            value="tool",
            operator=Operator.is_,
            type=Type.string
        )
    ]
    
    # Add session filter if provided
    if session_id:
        filters.append(
            EventFilter(
                field="session_id",
                value=session_id,
                operator=Operator.is_,
                type=Type.id
            )
        )
    
    # Get events using the powerful get_events() method
    result = events_api.get_events(
        project=project,
        filters=filters,
        limit=limit
    )
    
    return result


def get_expensive_model_calls(
    project: str,
    min_cost: float = 0.01,
    limit: int = 100
):
    """
    Example: Get model events that cost more than a threshold.
    
    This demonstrates using multiple filters with different operators.
    """
    honeyhive = HoneyHive(
        api_key=os.environ["HH_API_KEY"],
        server_url=os.environ.get("HH_API_URL", "https://api.honeyhive.ai")
    )
    
    events_api = EventsAPI(honeyhive)
    
    filters = [
        EventFilter(
            field="event_type",
            value="model",
            operator=Operator.is_,
            type=Type.string
        ),
        EventFilter(
            field="metadata.cost",
            value=str(min_cost),
            operator=Operator.greater_than,
            type=Type.number
        )
    ]
    
    result = events_api.get_events(
        project=project,
        filters=filters,
        limit=limit
    )
    
    return result


def get_events_with_date_range(
    project: str,
    event_type: str,
    start_date: str,
    end_date: str,
    limit: int = 100
):
    """
    Example: Get events within a specific date range.
    
    Args:
        project: Project name
        event_type: Type of event (tool, model, chain, session)
        start_date: ISO format date string (e.g., "2024-01-01T00:00:00.000Z")
        end_date: ISO format date string
        limit: Maximum number of events
    """
    honeyhive = HoneyHive(
        api_key=os.environ["HH_API_KEY"],
        server_url=os.environ.get("HH_API_URL", "https://api.honeyhive.ai")
    )
    
    events_api = EventsAPI(honeyhive)
    
    filters = [
        EventFilter(
            field="event_type",
            value=event_type,
            operator=Operator.is_,
            type=Type.string
        )
    ]
    
    date_range = {
        "$gte": start_date,
        "$lte": end_date
    }
    
    result = events_api.get_events(
        project=project,
        filters=filters,
        date_range=date_range,
        limit=limit
    )
    
    return result


if __name__ == "__main__":
    project = os.environ["HH_PROJECT"]
    
    print("=" * 80)
    print("Example 1: Get all tool calls")
    print("=" * 80)
    result = get_tool_calls_for_evaluation(project=project, limit=10)
    print(f"Found {result['totalEvents']} total tool calls")
    print(f"Retrieved {len(result['events'])} events")
    
    if result['events']:
        print(f"\nFirst tool call:")
        first_event = result['events'][0]
        print(f"  - Event Name: {first_event.event_name}")
        print(f"  - Event Type: {first_event.event_type}")
        if hasattr(first_event, 'metadata'):
            print(f"  - Metadata: {first_event.metadata}")
    
    print("\n" + "=" * 80)
    print("Example 2: Get expensive model calls (cost > $0.01)")
    print("=" * 80)
    result = get_expensive_model_calls(project=project, min_cost=0.01, limit=10)
    print(f"Found {result['totalEvents']} expensive model calls")
    print(f"Retrieved {len(result['events'])} events")
    
    print("\n" + "=" * 80)
    print("Key Takeaways")
    print("=" * 80)
    print("""
    ✓ Use get_events() for multiple filters
    ✓ Returns both events list AND total count
    ✓ Supports date range filtering
    ✓ Better for pagination (page parameter)
    
    ✗ Avoid list_events() for complex filtering
    ✗ list_events() only supports single filter
    ✗ No metadata (like total count) returned
    """)

