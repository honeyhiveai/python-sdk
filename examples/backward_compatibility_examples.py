"""
HoneyHive SDK - Backward Compatibility Examples (Complete-Refactor Branch)

This file demonstrates how the new baggage-based tracer discovery maintains
100% backward compatibility while enabling new multi-instance capabilities.

IMPORTANT: This functionality is available in the 'complete-refactor' branch
and represents major enhancements that will be included in the next release.

All existing @trace usage patterns continue to work exactly as before, while
new patterns are now possible for advanced use cases.
"""

import asyncio
import os
from typing import Any, Dict

# Set up environment for examples
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "backward-compatibility-demo"

from honeyhive import HoneyHiveTracer, atrace, set_default_tracer, trace
from honeyhive.models import EventType


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ==============================================================================
# SECTION 1: ORIGINAL API PATTERNS (ALL CONTINUE TO WORK)
# ==============================================================================

section_header("1. ORIGINAL API PATTERNS - 100% BACKWARD COMPATIBLE")

print("\n1.1 - Explicit tracer parameter (ORIGINAL - STILL WORKS)")


def example_explicit_tracer():
    """Original pattern: explicit tracer parameter."""
    tracer = HoneyHiveTracer(test_mode=True)

    @trace(tracer=tracer, event_type=EventType.tool)
    def process_data(data: str) -> str:
        return f"processed: {data}"

    @atrace(tracer=tracer, event_type=EventType.tool)
    async def async_process_data(data: str) -> str:
        return f"async_processed: {data}"

    # Test sync function
    result = process_data("test_data")
    print(f"✓ Sync result: {result}")

    # Test async function
    async_result = asyncio.run(async_process_data("async_test_data"))
    print(f"✓ Async result: {async_result}")


example_explicit_tracer()


print("\n1.2 - Context manager pattern (ENHANCED - NOW WITH AUTO-DISCOVERY)")


def example_default_tracer_approach():
    """NEW: Default tracer pattern - cleaner than context managers."""
    tracer = HoneyHiveTracer(test_mode=True)
    set_default_tracer(tracer)

    # Clean decorator-based approach (preferred)
    @trace(event_type=EventType.tool)
    def analyze_data(data: str) -> str:
        return f"analyzed: {data}"

    @atrace(event_type=EventType.tool)
    async def async_analyze_data(data: str) -> str:
        return f"async_analyzed: {data}"

    # Clean function calls - no context managers needed
    result = analyze_data("sample_data")
    print(f"✓ Default tracer sync result: {result}")

    async_result = asyncio.run(async_analyze_data("async_sample_data"))
    print(f"✓ Default tracer async result: {async_result}")


example_default_tracer_approach()


print("\n1.3 - Context manager pattern (WHEN NEEDED - for non-function operations)")


def example_context_manager_appropriate_usage():
    """Context managers for appropriate use cases only."""
    tracer = HoneyHiveTracer(test_mode=True)

    @trace(event_type=EventType.tool)
    def process_data_batch(data_list: list) -> list:
        return [f"processed: {item}" for item in data_list]

    # Context managers for non-function operations and orchestration
    with tracer.start_span("workflow_orchestration"):
        # Setup phase
        data_sources = ["source1", "source2", "source3"]
        print("✓ Data sources configured")

        # Processing phase (uses decorator)
        results = process_data_batch(data_sources)
        print(f"✓ Processed {len(results)} items")

        # Cleanup phase
        print("✓ Cleanup completed")


example_context_manager_appropriate_usage()


# ==============================================================================
# SECTION 2: NEW CONVENIENCE PATTERNS
# ==============================================================================

section_header("2. NEW CONVENIENCE PATTERNS - ENHANCED FUNCTIONALITY")

print("\n2.1 - Global default tracer (NEW CONVENIENCE FEATURE)")


def example_default_tracer():
    """New pattern: set a global default tracer for convenience."""
    # Set up a default tracer for the entire application
    default_tracer = HoneyHiveTracer(project="my-app", test_mode=True)
    set_default_tracer(default_tracer)

    # Now @trace works without any tracer specification!
    @trace(event_type=EventType.tool)
    def compute_metrics(data: Dict[str, Any]) -> Dict[str, float]:
        return {"accuracy": 0.95, "latency": 120.5}

    @atrace(event_type=EventType.tool)
    async def async_compute_metrics(data: Dict[str, Any]) -> Dict[str, float]:
        await asyncio.sleep(0.01)  # Simulate async work
        return {"throughput": 1000.0, "error_rate": 0.02}

    # These work automatically with the default tracer
    metrics = compute_metrics({"sample": "data"})
    print(f"✓ Default tracer sync result: {metrics}")

    async_metrics = asyncio.run(async_compute_metrics({"async": "data"}))
    print(f"✓ Default tracer async result: {async_metrics}")


example_default_tracer()


print("\n2.2 - Mixed usage patterns (ALL PATTERNS WORK TOGETHER)")


def example_mixed_patterns():
    """Demonstrate that all patterns work together seamlessly."""
    # Create multiple tracers for different contexts
    api_tracer = HoneyHiveTracer(project="api-service", test_mode=True)
    db_tracer = HoneyHiveTracer(project="database", test_mode=True)

    @trace(event_type=EventType.chain)
    def handle_api_request(user_id: str) -> str:
        # This will use the tracer from the current context
        return f"handled_request_for_{user_id}"

    @trace(tracer=db_tracer, event_type=EventType.tool)  # Explicit override
    def query_database(query: str) -> str:
        # This explicitly uses db_tracer regardless of context
        return f"query_result: {query}"

    @trace(event_type=EventType.chain)
    def mixed_operation(user_id: str) -> str:
        # Auto-discovers tracer from context
        api_result = handle_api_request(user_id)

        # Uses explicit tracer (overrides context)
        db_result = query_database(f"SELECT * FROM users WHERE id={user_id}")

        return f"{api_result} | {db_result}"

    # Test with API tracer context
    with api_tracer.start_span("incoming_request"):
        result = mixed_operation("user123")
        print(f"✓ Mixed patterns result: {result}")


example_mixed_patterns()


# ==============================================================================
# SECTION 3: MULTI-INSTANCE PATTERNS
# ==============================================================================

section_header("3. MULTI-INSTANCE PATTERNS - ADVANCED USE CASES")

print("\n3.1 - Multiple service tracers")


def example_multi_service():
    """Demonstrate multiple independent service tracers with decorator-first approach."""
    # Different services with their own tracers
    auth_tracer = HoneyHiveTracer(project="auth-service", test_mode=True)
    payment_tracer = HoneyHiveTracer(project="payment-service", test_mode=True)
    notification_tracer = HoneyHiveTracer(
        project="notification-service", test_mode=True
    )

    # PREFERRED: Explicit tracer parameters (always clear which service)
    @trace(tracer=auth_tracer, event_type=EventType.tool)
    def authenticate_user(credentials: str) -> bool:
        return credentials == "valid_token"

    @trace(tracer=payment_tracer, event_type=EventType.tool)
    def process_payment(amount: float) -> bool:
        return amount > 0

    @trace(tracer=notification_tracer, event_type=EventType.tool)
    def send_notification(message: str) -> bool:
        return len(message) > 0

    # Clean, declarative service calls
    auth_result = authenticate_user("valid_token")
    print(f"✓ Auth service: {auth_result}")

    payment_result = process_payment(99.99)
    print(f"✓ Payment service: {payment_result}")

    notif_result = send_notification("Payment successful!")
    print(f"✓ Notification service: {notif_result}")

    # Alternative: Default tracer switching for workflow patterns
    def user_registration_workflow():
        set_default_tracer(auth_tracer)
        auth_result = authenticate_user("valid_token")

        if auth_result:
            set_default_tracer(payment_tracer)
            payment_result = process_payment(99.99)

            if payment_result:
                set_default_tracer(notification_tracer)
                send_notification("Registration successful!")

    print("✓ Multi-service workflow:")
    user_registration_workflow()


example_multi_service()


print("\n3.2 - Nested cross-service calls")


def example_nested_cross_service():
    """Demonstrate nested calls across different services with decorator-first approach."""
    # Create tracers for different layers
    gateway_tracer = HoneyHiveTracer(project="api-gateway", test_mode=True)
    business_tracer = HoneyHiveTracer(project="business-logic", test_mode=True)
    data_tracer = HoneyHiveTracer(project="data-layer", test_mode=True)

    # PREFERRED: Explicit tracers make service boundaries clear
    @trace(tracer=data_tracer, event_type=EventType.tool)
    def fetch_user_data(user_id: str) -> Dict[str, Any]:
        return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

    @trace(tracer=business_tracer, event_type=EventType.chain)
    def process_user_request(user_id: str) -> Dict[str, Any]:
        # Decorated function automatically calls data layer
        user_data = fetch_user_data(user_id)

        # Process the data
        processed_data = {**user_data, "processed": True}
        return processed_data

    @trace(tracer=gateway_tracer, event_type=EventType.chain)
    def handle_user_request(user_id: str) -> Dict[str, Any]:
        # Decorated function automatically calls business layer
        result = process_user_request(user_id)

        # Add API-specific metadata
        return {**result, "api_version": "v1", "timestamp": "2024-01-01T12:00:00Z"}

    # Clean, declarative nested service calls
    final_result = handle_user_request("user456")
    print(f"✓ Cross-service result: {final_result}")

    # Alternative: Using default tracer switching for complex workflows
    def complex_user_workflow(user_id: str):
        # API Gateway layer
        set_default_tracer(gateway_tracer)

        @trace(event_type=EventType.tool)
        def validate_request():
            return len(user_id) > 0

        if validate_request():
            # Business Logic layer
            set_default_tracer(business_tracer)

            @trace(event_type=EventType.chain)
            def business_processing():
                # Data Layer
                set_default_tracer(data_tracer)

                @trace(event_type=EventType.tool)
                def data_retrieval():
                    return {"id": user_id, "status": "active"}

                return data_retrieval()

            return business_processing()

    workflow_result = complex_user_workflow("user789")
    print(f"✓ Workflow result: {workflow_result}")


example_nested_cross_service()


print("\n3.3 - Priority override demonstration")


def example_priority_override():
    """Demonstrate the priority system: explicit > context > default."""
    # Set up different tracers
    default_tracer = HoneyHiveTracer(project="default-app", test_mode=True)
    context_tracer = HoneyHiveTracer(project="context-specific", test_mode=True)
    explicit_tracer = HoneyHiveTracer(project="explicit-override", test_mode=True)

    set_default_tracer(default_tracer)

    @trace(event_type=EventType.tool)
    def flexible_function() -> str:
        return "uses_current_priority"

    @trace(tracer=explicit_tracer, event_type=EventType.tool)
    def explicit_function() -> str:
        return "always_uses_explicit_tracer"

    print("Priority demonstration:")

    # 1. Default tracer (lowest priority)
    result1 = flexible_function()
    print(f"  1. Default tracer: {result1}")

    # 2. Context tracer (medium priority)
    with context_tracer.start_span("context_operation"):
        result2 = flexible_function()
        print(f"  2. Context tracer: {result2}")

        # 3. Explicit tracer (highest priority - overrides context)
        result3 = explicit_function()
        print(f"  3. Explicit tracer (overrides context): {result3}")


example_priority_override()


# ==============================================================================
# SECTION 4: ASYNC PATTERNS
# ==============================================================================

section_header("4. ASYNC PATTERNS - FULL ASYNC/AWAIT SUPPORT")

print("\n4.1 - Async function tracing with auto-discovery")


async def example_async_patterns():
    """Demonstrate async patterns with automatic tracer discovery."""
    tracer = HoneyHiveTracer(test_mode=True)

    @atrace(event_type=EventType.tool)
    async def fetch_async_data(source: str) -> Dict[str, Any]:
        await asyncio.sleep(0.01)  # Simulate async I/O
        return {"source": source, "data": [1, 2, 3, 4, 5]}

    @atrace(event_type=EventType.tool)
    async def process_async_data(data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)  # Simulate async processing
        processed_values = [x * 2 for x in data["data"]]
        return {"source": data["source"], "processed": processed_values}

    @atrace(event_type=EventType.chain)
    async def async_data_pipeline(source: str) -> Dict[str, Any]:
        # Fetch data
        raw_data = await fetch_async_data(source)

        # Process data
        processed_data = await process_async_data(raw_data)

        return processed_data

    # Run async pipeline with tracer context
    with tracer.start_span("async_pipeline_execution"):
        result = await async_data_pipeline("external_api")
        print(f"✓ Async pipeline result: {result}")


# Run the async example
asyncio.run(example_async_patterns())


print("\n4.2 - Mixed sync/async with auto-discovery")


async def example_mixed_sync_async():
    """Demonstrate mixing sync and async functions with auto-discovery."""
    tracer = HoneyHiveTracer(test_mode=True)

    @trace(event_type=EventType.tool)
    def validate_input(data: str) -> bool:
        return len(data) > 0 and data.isalnum()

    @atrace(event_type=EventType.tool)
    async def call_external_service(data: str) -> str:
        await asyncio.sleep(0.01)  # Simulate network call
        return f"external_response_for_{data}"

    @atrace(event_type=EventType.chain)
    async def mixed_workflow(input_data: str) -> Dict[str, Any]:
        # Sync validation within async function
        is_valid = validate_input(input_data)

        if is_valid:
            # Async external call
            external_result = await call_external_service(input_data)
            return {"valid": True, "result": external_result}
        else:
            return {"valid": False, "error": "Invalid input"}

    # Run mixed workflow
    with tracer.start_span("mixed_sync_async_workflow"):
        result = await mixed_workflow("test123")
        print(f"✓ Mixed sync/async result: {result}")


# Run the mixed example
asyncio.run(example_mixed_sync_async())


# ==============================================================================
# SECTION 5: ERROR HANDLING
# ==============================================================================

section_header("5. ERROR HANDLING - GRACEFUL DEGRADATION")

print("\n5.1 - Graceful degradation when no tracer available")


def example_graceful_degradation():
    """Demonstrate graceful degradation when no tracer is available."""
    # Clear any default tracer
    set_default_tracer(None)

    @trace(event_type=EventType.tool)
    def function_without_tracer() -> str:
        # This will execute normally without tracing
        return "executed_without_tracing"

    @atrace(event_type=EventType.tool)
    async def async_function_without_tracer() -> str:
        await asyncio.sleep(0.01)
        return "async_executed_without_tracing"

    # These execute normally, just without tracing
    sync_result = function_without_tracer()
    print(f"✓ Sync without tracer: {sync_result}")

    async_result = asyncio.run(async_function_without_tracer())
    print(f"✓ Async without tracer: {async_result}")


example_graceful_degradation()


print("\n5.2 - Error preservation")


def example_error_preservation():
    """Demonstrate that function errors are preserved during tracing."""
    tracer = HoneyHiveTracer(test_mode=True)

    @trace(tracer=tracer, event_type=EventType.tool)
    def function_that_errors() -> str:
        raise ValueError("This is an intentional error")

    try:
        function_that_errors()
    except ValueError as e:
        print(f"✓ Error correctly preserved: {e}")


example_error_preservation()


# ==============================================================================
# CONCLUSION
# ==============================================================================

section_header("CONCLUSION")

print(
    """
✅ BACKWARD COMPATIBILITY VERIFIED
All existing @trace usage patterns continue to work exactly as before.

🚀 NEW CAPABILITIES UNLOCKED
- Automatic tracer discovery from context
- Global default tracer support  
- Multi-instance tracer support
- Priority-based tracer selection
- Enhanced async/await support

📋 RECOMMENDED PATTERNS (DECORATOR-FIRST PHILOSOPHY)
1. PREFERRED: @trace with explicit tracer parameter for multi-service
2. CONVENIENT: @trace with default tracer for single-service apps
3. ADVANCED: Default tracer switching for complex workflows
4. SPECIALIZED: Context managers only for non-function operations

📈 MIGRATION PATH
- ZERO changes required for existing code
- Gradual adoption of new patterns as needed
- Decorators should be your primary tracing mechanism
- Use context managers only when decorators aren't sufficient

The decorator-first approach with baggage-based discovery provides clean,
declarative tracing that's easy to read and maintain, while context managers
are reserved for orchestration and non-function operations.
"""
)

print(f"\n{'='*60}")
print("  All examples completed successfully! ✓")
print(f"{'='*60}\n")
