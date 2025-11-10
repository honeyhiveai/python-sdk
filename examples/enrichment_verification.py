#!/usr/bin/env python3
"""
Enrichment Verification Example

This example demonstrates and verifies that enrichment works correctly:
1. Tests enrich_span with user_properties and metrics (should go to correct namespaces)
2. Tests enrich_session with user_properties (should go to User Properties, not metadata)
3. Fetches the events and verifies the enrichment data is correctly stored

This addresses the customer-reported issue where:
- tracer.enrich_span() was adding user_properties and metrics to metadata
- tracer.enrich_session() was not working as expected
"""

import os
import time
from typing import Any, Dict, Optional

from honeyhive import HoneyHive, HoneyHiveTracer, trace


def verify_enrichment_data(
    event_data: Dict[str, Any],
    expected_user_properties: Optional[Dict[str, Any]] = None,
    expected_metrics: Optional[Dict[str, Any]] = None,
    expected_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, bool]:
    """Verify that enrichment data is stored correctly in the event.

    Args:
        event_data: Event data from API
        expected_user_properties: Expected user properties (should be in user_properties field)
        expected_metrics: Expected metrics (should be in metrics field or honeyhive_metrics.*)
        expected_metadata: Expected metadata (should be in metadata field or honeyhive_metadata.*)

    Returns:
        Dict with verification results
    """
    results = {
        "user_properties_correct": False,
        "metrics_correct": False,
        "metadata_correct": False,
    }

    # Check user_properties
    if expected_user_properties:
        event_user_props = event_data.get("user_properties", {})
        if isinstance(event_user_props, dict):
            results["user_properties_correct"] = all(
                event_user_props.get(k) == v for k, v in expected_user_properties.items()
            )
        print(f"  User Properties: {event_user_props}")
        print(f"  Expected: {expected_user_properties}")
        print(f"  ✓ User Properties Correct: {results['user_properties_correct']}")

    # Check metrics
    if expected_metrics:
        event_metrics = event_data.get("metrics", {})
        if isinstance(event_metrics, dict):
            results["metrics_correct"] = all(
                event_metrics.get(k) == v for k, v in expected_metrics.items()
            )
        print(f"  Metrics: {event_metrics}")
        print(f"  Expected: {expected_metrics}")
        print(f"  ✓ Metrics Correct: {results['metrics_correct']}")

    # Check metadata
    if expected_metadata:
        event_metadata = event_data.get("metadata", {})
        if isinstance(event_metadata, dict):
            # Check both direct metadata and honeyhive_metadata.* attributes
            results["metadata_correct"] = all(
                event_metadata.get(k) == v for k, v in expected_metadata.items()
            )
        print(f"  Metadata: {event_metadata}")
        print(f"  Expected: {expected_metadata}")
        print(f"  ✓ Metadata Correct: {results['metadata_correct']}")

    return results


def main():
    """Main function demonstrating enrichment verification."""
    print("🔍 HoneyHive Enrichment Verification Example")
    print("=" * 60)
    print("This example verifies that enrichment works correctly:\n")
    print("1. enrich_span() with user_properties and metrics")
    print("2. enrich_session() with user_properties")
    print("3. Event fetching and verification\n")

    # Get API key from environment
    api_key = os.environ.get("HH_API_KEY")
    if not api_key:
        print("⚠️  Warning: HH_API_KEY not set. Using test mode.")
        print("   Set HH_API_KEY environment variable to test with real API.\n")
        api_key = "test-key"

    project = os.environ.get("HH_PROJECT", "enrichment-verification")
    source = os.environ.get("HH_SOURCE", "examples")

    # Initialize tracer
    print("📝 Step 1: Initialize Tracer")
    print("-" * 40)
    tracer = HoneyHiveTracer.init(
        api_key=api_key,
        project=project,
        source=source,
        verbose=True,
    )
    print(f"✓ Tracer initialized for project: {tracer.project_name}\n")

    # Initialize API client for fetching events
    client = HoneyHive(api_key=api_key) if api_key != "test-key" else None

    # ========================================================================
    # Test 1: enrich_span with user_properties and metrics
    # ========================================================================
    print("📝 Step 2: Test enrich_span() with user_properties and metrics")
    print("-" * 60)

    @trace(tracer=tracer, event_type="tool", event_name="enrich_span_test")
    def test_enrich_span():
        """Test function that enriches span with user_properties and metrics."""
        print("  📝 Enriching span with user_properties and metrics...")

        # Test the suggested pattern: tracer.enrich_span()
        # user_properties should go to User Properties namespace
        # metrics should go to Automated Evaluations (metrics) namespace
        tracer.enrich_span(
            user_properties={"user_id": "test-user-123", "plan": "premium"},
            metrics={"score": 0.95, "latency_ms": 150},
            metadata={"feature": "enrichment_test", "test_id": "span_test_1"},
        )
        print("  ✓ Span enriched\n")

    # Execute test
    test_enrich_span()

    # Wait for span to be exported
    print("  ⏳ Waiting for span to be exported...")
    time.sleep(2)

    # ========================================================================
    # Test 2: enrich_session with user_properties
    # ========================================================================
    print("\n📝 Step 3: Test enrich_session() with user_properties")
    print("-" * 55)

    # Start a session
    session_id = tracer.session_start()
    if session_id:
        print(f"  ✓ Session started: {session_id}")

        # Enrich session with user_properties
        # user_properties should go to User Properties field, NOT metadata
        print("  📝 Enriching session with user_properties...")
        tracer.enrich_session(
            user_properties={"user_id": "test-user-456", "tier": "enterprise"},
            metadata={"source": "enrichment_test", "test_id": "session_test_1"},
            metrics={"session_duration_ms": 500},
        )
        print("  ✓ Session enriched\n")

        # Wait for session update to be processed
        print("  ⏳ Waiting for session update to be processed...")
        time.sleep(2)

        # Fetch and verify session
        if client:
            try:
                print("\n  📥 Fetching session from API...")
                session_response = client.sessions.get_session(session_id)
                event_data = session_response.event.model_dump() if hasattr(session_response, "event") else session_response.event.dict() if hasattr(session_response.event, "dict") else {}

                print("\n  🔍 Verifying Session Enrichment:")
                print("-" * 40)
                results = verify_enrichment_data(
                    event_data,
                    expected_user_properties={"user_id": "test-user-456", "tier": "enterprise"},
                    expected_metrics={"session_duration_ms": 500},
                    expected_metadata={"source": "enrichment_test", "test_id": "session_test_1"},
                )

                print("\n  📊 Session Verification Results:")
                print(f"    User Properties Correct: {results['user_properties_correct']}")
                print(f"    Metrics Correct: {results['metrics_correct']}")
                print(f"    Metadata Correct: {results['metadata_correct']}")

                if all(results.values()):
                    print("\n  ✅ All session enrichment checks passed!")
                else:
                    print("\n  ⚠️  Some session enrichment checks failed!")
                    print("     This indicates a bug in enrich_session()")

            except Exception as e:
                print(f"\n  ⚠️  Could not fetch session: {e}")
                print("     This is expected if HH_API_KEY is not set or API is unavailable")
    else:
        print("  ⚠️  Could not start session")

    # ========================================================================
    # Test 3: List recent events and verify span enrichment
    # ========================================================================
    if client:
        print("\n📝 Step 4: Fetch and verify span enrichment")
        print("-" * 45)
        try:
            print("  📥 Fetching recent events...")
            # Wait a bit more for OTLP export to complete
            time.sleep(3)
            
            # Use a simpler approach - list events by session_id
            # The span should be associated with the session
            if session_id:
                try:
                    # Try to get events for the session
                    from honeyhive.models.generated import EventFilter, Operator
                    
                    # Create a simple filter for session_id
                    filters = [
                        EventFilter(
                            field="session_id",
                            operator=Operator.is_,  # Use enum value
                            value=session_id,
                        )
                    ]

                    events_result = client.events.get_events(
                        project=project,
                        filters=filters,
                        limit=10,
                    )

                    events = events_result.get("events", [])
                    if events:
                        print(f"  ✓ Found {len(events)} event(s) for session")
                        
                        # Find the span event (event_type="tool", event_name="enrich_span_test")
                        span_event = None
                        for event in events:
                            event_dict = event.model_dump() if hasattr(event, "model_dump") else event.dict() if hasattr(event, "dict") else dict(event)
                            if event_dict.get("event_name") == "enrich_span_test":
                                span_event = event_dict
                                break
                        
                        if span_event:
                            print("\n  🔍 Verifying Span Enrichment from Backend:")
                            print("-" * 50)
                            print(f"  Event ID: {span_event.get('event_id', 'N/A')}")
                            print(f"  Event Name: {span_event.get('event_name', 'N/A')}")
                            print(f"  Event Type: {span_event.get('event_type', 'N/A')}")

                            # Check metrics
                            event_metrics = span_event.get("metrics", {})
                            print(f"\n  📊 Metrics in backend event:")
                            print(f"     {event_metrics}")
                            if event_metrics.get("score") == 0.95 and event_metrics.get("latency_ms") == 150:
                                print("     ✅ Metrics correctly stored!")
                            else:
                                print("     ⚠️  Metrics mismatch!")

                            # Check metadata
                            event_metadata = span_event.get("metadata", {})
                            print(f"\n  📝 Metadata in backend event:")
                            print(f"     {event_metadata}")
                            if event_metadata.get("feature") == "enrichment_test":
                                print("     ✅ Metadata correctly stored!")
                            else:
                                print("     ⚠️  Metadata mismatch!")

                            # Check user_properties
                            event_user_props = span_event.get("user_properties", {})
                            print(f"\n  👤 User Properties in backend event:")
                            print(f"     {event_user_props}")
                            if event_user_props.get("user_id") == "test-user-123" and event_user_props.get("plan") == "premium":
                                print("     ✅ User Properties correctly stored!")
                            else:
                                print("     ⚠️  User Properties mismatch!")
                                print("     Note: For spans, user_properties may be in attributes/honeyhive_user_properties.*")
                        else:
                            print("  ⚠️  Could not find span event 'enrich_span_test'")
                            print("     This may be because:")
                            print("     - OTLP export hasn't completed yet")
                            print("     - Event name doesn't match")
                    else:
                        print("  ⚠️  No events found for session")
                        print("     This may be because OTLP export hasn't completed yet")
                except Exception as e:
                    print(f"  ⚠️  Error fetching events: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("  ⚠️  No session_id available to fetch events")

        except Exception as e:
            print(f"\n  ⚠️  Could not fetch events: {e}")
            import traceback
            traceback.print_exc()
            print("     This is expected if HH_API_KEY is not set or API is unavailable")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print("\n✅ Enrichment tests completed!")
    print("\nExpected Behavior:")
    print("  1. enrich_span(user_properties={...}) → Should go to User Properties namespace")
    print("  2. enrich_span(metrics={...}) → Should go to Automated Evaluations (metrics) namespace")
    print("  3. enrich_session(user_properties={...}) → Should go to User Properties field (not metadata)")
    print("\nIf verification shows incorrect behavior, there may be a bug in:")
    print("  - enrich_span() routing user_properties/metrics to metadata")
    print("  - enrich_session() merging user_properties into metadata instead of separate field")
    print("\nSee the code comments and verification output above for details.")


if __name__ == "__main__":
    main()

