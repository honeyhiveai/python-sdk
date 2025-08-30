"""Verbose Debugging Example for HoneyHive Python SDK.

This example demonstrates how to use the verbose flag to debug API calls
and troubleshoot issues with the HoneyHive API.
"""

import os
import sys
from honeyhive import HoneyHive
from honeyhive.api.session import SessionStartRequest
from honeyhive.api.events import CreateEventRequest


def setup_verbose_logging():
    """Setup verbose logging through environment variables."""
    print("=== Setting up Verbose Logging ===")

    # Method 1: Set environment variable
    os.environ["HH_VERBOSE"] = "true"
    print("✓ Set HH_VERBOSE=true environment variable")

    # Method 2: You can also set other debugging environment variables
    os.environ["HH_DEBUG_MODE"] = "true"
    print("✓ Set HH_DEBUG_MODE=true environment variable")

    print("Environment variables configured for verbose logging.\n")


def verbose_client_example():
    """Example of using verbose flag in client initialization."""
    print("=== Verbose Client Example ===")

    # Initialize client with verbose mode enabled
    client = HoneyHive(
        api_key="your-api-key",  # Replace with your actual API key
        verbose=True,  # Enable verbose logging
        base_url="https://api.honeyhive.ai",  # Optional: specify custom base URL
    )

    print("✓ Client initialized with verbose mode enabled")
    print("✓ All API requests and responses will be logged with detailed information")
    print("✓ Error details will include request parameters and response information\n")

    return client


def debug_api_calls(client):
    """Demonstrate verbose logging during API calls."""
    print("=== Debugging API Calls ===")

    try:
        # This will generate verbose logs for the request
        print("Making API call to start session...")
        session_request = SessionStartRequest(
            project="Debug Example Project",
            session_name="Verbose Debugging Session",
            source="verbose_example",
            inputs={"debug_info": "This is a test call for debugging"},
        )

        response = client.session.start_session(session_request)
        session_id = response.session_id
        print(f"✓ Session started successfully: {session_id}")

        # This will generate verbose logs for another API call
        print("\nMaking API call to create event...")
        event_request = CreateEventRequest(
            project="Debug Example Project",
            source="verbose_example",
            event_name="debug_event",
            event_type="debug",
            session_id=session_id,
            inputs={"test_input": "Debug input data"},
            outputs={"test_output": "Debug output data"},
        )

        event_response = client.events.create_event(event_request)
        print(f"✓ Event created successfully: {event_response.event_id}")

    except Exception as e:
        print(f"✗ API call failed: {e}")
        print("Check the verbose logs above for detailed error information.")
        print("The logs will show:")
        print("  - Request details (method, URL, headers, body)")
        print("  - Response details (status code, headers, timing)")
        print("  - Error details (error type, message, context)")

    return client


def debug_with_environment_variables():
    """Example of using environment variables for verbose logging."""
    print("\n=== Environment Variable Configuration ===")

    # You can also configure verbose logging through environment variables
    # without modifying your code:

    print(
        "To enable verbose logging without code changes, set these environment variables:"
    )
    print("  export HH_VERBOSE=true")
    print("  export HH_DEBUG_MODE=true")
    print("  export HH_API_KEY=your-api-key")
    print("  export HH_PROJECT=your-project")
    print()

    print("Then initialize the client normally:")
    print("  client = HoneyHive()  # Will automatically use verbose mode")
    print()


def main():
    """Run the verbose debugging examples."""
    print("HoneyHive Verbose Debugging Example")
    print("=" * 50)

    # Setup environment variables
    setup_verbose_logging()

    # Initialize client with verbose mode
    client = verbose_client_example()

    # Demonstrate API call debugging
    client = debug_api_calls(client)

    # Show environment variable configuration
    debug_with_environment_variables()

    # Close client
    client.close()
    print("\n=== Example Completed ===")
    print("Check the logs above for detailed API request/response information.")
    print("This verbose logging is invaluable for debugging API issues!")


if __name__ == "__main__":
    main()
