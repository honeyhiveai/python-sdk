#!/usr/bin/env python3
"""
Verbose Logging Example

This example demonstrates how to use verbose logging for debugging
HoneyHive API calls and troubleshooting issues. It combines the best
of both verbose examples into a single working demonstration.

Key features demonstrated:
1. Enabling verbose mode via constructor and environment variables
2. Real verbose output during API operations
3. Debugging failed API calls with detailed logs
4. Practical debugging scenarios
"""

import os
import time
from typing import Dict, Any
from honeyhive import HoneyHive, HoneyHiveTracer

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "demo-api-key-for-testing"
os.environ["HH_PROJECT"] = "verbose-demo"
os.environ["HH_SOURCE"] = "development"


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")


def demonstrate_verbose_constructor():
    """Demonstrate verbose mode via constructor parameter."""
    print("1. Verbose Mode via Constructor")
    print("-" * 35)

    # Method 1: Enable verbose mode via constructor
    client = HoneyHive(
        api_key="demo-api-key",  # This will fail, but we'll see verbose logs
        verbose=True,
        test_mode=True,  # Use test mode to avoid real API calls
    )

    print(f"✓ Client created with verbose={client.verbose}")
    print("✓ All API requests will show detailed information")
    print("✓ Error details will include request parameters and response info")

    return client


def demonstrate_verbose_environment():
    """Demonstrate verbose mode via environment variables."""
    print("\n2. Verbose Mode via Environment Variables")
    print("-" * 45)

    # Method 2: Enable verbose mode via environment variable
    os.environ["HH_VERBOSE"] = "true"
    os.environ["HH_DEBUG_MODE"] = "true"

    print("✓ Set HH_VERBOSE=true environment variable")
    print("✓ Set HH_DEBUG_MODE=true environment variable")

    # Create client that will automatically use verbose mode
    client = HoneyHive(api_key="demo-api-key", test_mode=True)

    print(f"✓ Client automatically uses verbose mode: {client.verbose}")
    print("✓ Environment variables override constructor defaults")

    return client


def demonstrate_tracer_verbose():
    """Demonstrate verbose logging with HoneyHiveTracer."""
    print("\n3. Verbose Tracing")
    print("-" * 18)

    # Initialize tracer with verbose logging
    tracer = HoneyHiveTracer.init(
        api_key="demo-api-key",
        project="verbose-demo-project",  # Required for OTLP tracing
        source="development",
        test_mode=True,  # Use test mode
    )

    print("✓ Tracer initialized with verbose session creation")
    print(f"✓ Project: {tracer.project}")
    print(f"✓ Session ID: {tracer.session_id}")

    # Create some traced operations
    with tracer.start_span("verbose_demo_operation") as span:
        span.set_attribute("demo.type", "verbose_logging")
        span.set_attribute("demo.purpose", "show_detailed_logs")
        print("✓ Created span with verbose attribute logging")
        time.sleep(0.1)  # Simulate work

    print("✓ Span completed - check logs for detailed tracing info")

    return tracer


def demonstrate_api_debugging():
    """Demonstrate debugging API calls with verbose logging."""
    print("\n4. API Call Debugging")
    print("-" * 22)

    # Create client with verbose mode for debugging
    client = HoneyHive(
        api_key="invalid-api-key-for-demo",  # Intentionally invalid
        verbose=True,
        test_mode=False,  # Disable test mode to see real API errors
    )

    print("✓ Client created with invalid API key (for demonstration)")
    print("✓ Verbose mode will show detailed error information")

    # Attempt API operations that will fail (for demonstration)
    try:
        print("\nAttempting API call with invalid credentials...")

        # This will fail and show verbose error logs
        # Note: We're using a simple HTTP request to demonstrate verbose logging
        response = client.sync_client.get("/sessions")  # This will fail
        print(f"✓ Unexpected success: {response.status_code}")

    except Exception as e:
        print(f"✗ Expected API failure: {type(e).__name__}")
        print("✓ Check the verbose logs above for detailed error information")
        print("  The logs show:")
        print("  - Request details (method, URL, headers)")
        print("  - Response details (status code, error message)")
        print("  - Timing information")
        print("  - Full error context")

    return client


def demonstrate_configuration_debugging():
    """Demonstrate configuration debugging with verbose mode."""
    print("\n5. Configuration Debugging")
    print("-" * 27)

    # Show current configuration
    from honeyhive.utils.config import config

    print("Current configuration (with verbose details):")
    print(f"  API Key: {'✓ Set' if config.api_key else '✗ Not set'}")
    print(f"  Project: {config.project}")
    print(f"  Source: {config.source}")
    print(f"  Debug Mode: {config.debug_mode}")
    print(f"  Verbose Mode: {config.verbose}")
    print(f"  Test Mode: {config.test_mode}")

    # Show environment variables that affect verbose logging
    print("\nEnvironment variables affecting verbose logging:")
    verbose_env_vars = [
        "HH_VERBOSE",
        "HH_DEBUG_MODE",
        "HH_API_KEY",
        "HH_PROJECT",
        "HH_SOURCE",
        "HH_TEST_MODE",
    ]

    for var in verbose_env_vars:
        value = os.environ.get(var, "Not set")
        print(f"  {var}: {value}")


def demonstrate_practical_debugging():
    """Demonstrate practical debugging scenarios."""
    print("\n6. Practical Debugging Scenarios")
    print("-" * 33)

    print("Common debugging scenarios where verbose logging helps:")
    print()

    print("Scenario 1: Authentication Issues")
    print("  Problem: API calls return 401 Unauthorized")
    print("  Solution: Verbose logs show exact request headers and API key format")
    print("  Command: client = HoneyHive(api_key='your-key', verbose=True)")
    print()

    print("Scenario 2: Network Connectivity")
    print("  Problem: API calls timeout or fail to connect")
    print("  Solution: Verbose logs show connection attempts and timing")
    print("  Command: export HH_VERBOSE=true && python your_script.py")
    print()

    print("Scenario 3: Request Format Issues")
    print("  Problem: API returns 400 Bad Request")
    print("  Solution: Verbose logs show exact request body and validation errors")
    print("  Command: client = HoneyHive(verbose=True, debug=True)")
    print()

    print("Scenario 4: Performance Analysis")
    print("  Problem: API calls are slow")
    print("  Solution: Verbose logs show request/response timing")
    print("  Command: export HH_DEBUG_MODE=true && run your application")


def main():
    """Main function demonstrating comprehensive verbose logging."""

    print("🚀 HoneyHive Verbose Logging - Comprehensive Example")
    print("This example shows how to use verbose logging for debugging")
    print("API calls, troubleshooting issues, and understanding SDK behavior.")

    # Demonstrate different ways to enable verbose logging
    client1 = demonstrate_verbose_constructor()
    client2 = demonstrate_verbose_environment()
    tracer = demonstrate_tracer_verbose()

    # Demonstrate debugging scenarios
    client3 = demonstrate_api_debugging()
    demonstrate_configuration_debugging()
    demonstrate_practical_debugging()

    # Cleanup
    try:
        client1.close()
        client2.close()
        client3.close()
    except:
        pass  # Ignore cleanup errors in demo

    section_header("Summary")
    print("🎉 Verbose logging example completed!")
    print()
    print("Key takeaways:")
    print("✅ Use verbose=True in constructor for immediate debugging")
    print("✅ Use HH_VERBOSE=true environment variable for persistent debugging")
    print("✅ Verbose logs show detailed request/response information")
    print("✅ Error messages include full context for troubleshooting")
    print("✅ Timing information helps identify performance issues")
    print("✅ Configuration debugging helps verify setup")
    print()
    print("For production use:")
    print("• Only enable verbose mode when debugging issues")
    print("• Verbose logs may contain sensitive information")
    print("• Use environment variables for easier on/off control")
    print("• Consider log rotation for long-running applications")


if __name__ == "__main__":
    main()
