"""Basic usage example for HoneyHive Python SDK."""

import asyncio
from honeyhive import HoneyHive, HoneyHiveTracer
from honeyhive.api.session import SessionStartRequest
from honeyhive.api.events import CreateEventRequest


def sync_example():
    """Synchronous usage example."""
    print("=== Synchronous Example ===")
    
    # Initialize client
    client = HoneyHive(api_key="your-api-key")
    
    # Start a session
    session_request = SessionStartRequest(
        project="Example Project",
        session_name="Basic Usage Session",
        source="example",
        inputs={"user_query": "What is the weather like?"}
    )
    
    response = client.session.start_session(session_request)
    session_id = response.session_id
    print(f"Session started: {session_id}")
    
    # Create an event
    event_request = CreateEventRequest(
        project="Example Project",
        source="example",
        event_name="model_call",
        event_type="model",
        session_id=session_id,
        inputs={"prompt": "What is the weather like?"},
        outputs={"response": "The weather is sunny today!"}
    )
    
    event_response = client.events.create_event(event_request)
    print(f"Event created: {event_response.event_id}")
    
    # Get session details
    session_data = client.session.get_session(session_id)
    print(f"Session retrieved: {session_data.event_name}")
    
    # Close client
    client.close()


async def async_example():
    """Asynchronous usage example."""
    print("\n=== Asynchronous Example ===")
    
    # Initialize client
    client = HoneyHive(api_key="your-api-key")
    
    # Start a session
    session_request = SessionStartRequest(
        project="Example Project",
        session_name="Async Usage Session",
        source="example",
        inputs={"user_query": "What is the weather like?"}
    )
    
    response = await client.session.start_session_async(session_request)
    session_id = response.session_id
    print(f"Session started: {session_id}")
    
    # Create an event
    event_request = CreateEventRequest(
        project="Example Project",
        source="example",
        event_name="model_call",
        event_type="model",
        session_id=session_id,
        inputs={"prompt": "What is the weather like?"},
        outputs={"response": "The weather is sunny today!"}
    )
    
    event_response = await client.events.create_event_async(event_request)
    print(f"Event created: {event_response.event_id}")
    
    # Get session details
    session_data = await client.session.get_session_async(session_id)
    print(f"Session retrieved: {session_data.event_name}")
    
    # Close client
    await client.aclose()


def tracing_example():
    """Tracing example."""
    print("\n=== Tracing Example ===")
    
    # Initialize tracer
    tracer = HoneyHiveTracer(
        api_key="your-api-key",
        project="Example Project",
        source="example"
    )
    
    # Use context manager for manual tracing
    with tracer.start_span("custom-operation", session_id="example-session"):
        print("Performing custom operation...")
        result = "Operation completed successfully"
        print(f"Result: {result}")
    
    # Set and get baggage
    tracer.set_baggage("user_id", "12345")
    user_id = tracer.get_baggage("user_id")
    print(f"User ID from baggage: {user_id}")
    
    # Enrich session
    success = tracer.enrich_session(
        session_id="example-session",
        metadata={"custom": "data"},
        feedback={"rating": 5},
        metrics={"accuracy": 0.95}
    )
    print(f"Session enrichment successful: {success}")


def verbose_example():
    """Verbose logging example for debugging API calls."""
    print("\n=== Verbose Logging Example ===")
    
    # Initialize client with verbose mode enabled
    client = HoneyHive(
        api_key="your-api-key",
        verbose=True  # Enable verbose logging for API debugging
    )
    
    print("Client initialized with verbose mode enabled.")
    print("All API requests and responses will be logged with detailed information.")
    
    # Start a session (this will show detailed request/response logs)
    session_request = SessionStartRequest(
        project="Verbose Example Project",
        session_name="Verbose Logging Session",
        source="example",
        inputs={"user_query": "Debug this API call"}
    )
    
    try:
        response = client.session.start_session(session_request)
        session_id = response.session_id
        print(f"Session started successfully: {session_id}")
    except Exception as e:
        print(f"Session creation failed: {e}")
        print("Check the verbose logs above for detailed error information.")
    
    # Close client
    client.close()
    print("Verbose example completed. Check the logs above for detailed API information.")


def main():
    """Run all examples."""
    # Synchronous example
    sync_example()
    
    # Asynchronous example
    asyncio.run(async_example())
    
    # Tracing example
    tracing_example()
    
    # Verbose example
    verbose_example()


if __name__ == "__main__":
    main()
