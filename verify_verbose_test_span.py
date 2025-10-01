#!/usr/bin/env python3
"""
Verify the verbose test span appears in HoneyHive backend.
"""

import os
import sys
import time

def verify_verbose_test_span():
    """Verify the verbose test span made it to the backend."""
    
    print("🔍 Verifying verbose test span in HoneyHive backend...")
    
    # Check for required environment variables
    api_key = os.getenv('HH_API_KEY')
    if not api_key:
        print("❌ ERROR: HH_API_KEY environment variable not set!")
        sys.exit(1)
    
    try:
        from honeyhive import HoneyHive
        from honeyhive.models.generated import EventFilter
        
        # Initialize HoneyHive client
        client = HoneyHive(api_key=api_key)
        
        print(f"✅ HoneyHive client initialized")
        
        project = "New Project"
        session_id = "4dc9365e-937e-4109-ae0e-ce0cb4ade94a"  # NEW session from verbose test
        expected_span = "verbose-debug-test-span"
        
        print(f"   Project: {project}")
        print(f"   Session ID: {session_id}")
        print(f"   Expected Span: {expected_span}")
        
        # Query events by session_id
        print(f"\n📊 Querying events for verbose test session...")
        try:
            session_filter = EventFilter(
                field="session_id",
                value=session_id,
                operator="is",
                type="string"
            )
            
            events = client.events.list_events(
                event_filter=session_filter,
                limit=100,
                project=project
            )
            
            # Handle response format
            events_list = []
            if isinstance(events, list):
                events_list = events
            elif hasattr(events, 'events'):
                events_list = events.events
            elif isinstance(events, dict) and 'events' in events:
                events_list = events['events']
            
            print(f"✅ Found {len(events_list)} events for session {session_id}")
            
            if events_list:
                verbose_test_span_found = False
                
                for i, event in enumerate(events_list):
                    # Handle both dict and object formats
                    if isinstance(event, dict):
                        event_name = event.get('event_name', 'N/A')
                        event_type = event.get('event_type', 'N/A')
                        event_id = event.get('event_id', 'N/A')
                        created_at = event.get('created_at', 'N/A')
                        inputs = event.get('inputs')
                        outputs = event.get('outputs')
                        config = event.get('config')
                    else:
                        event_name = getattr(event, 'event_name', 'N/A')
                        event_type = getattr(event, 'event_type', 'N/A')
                        event_id = getattr(event, 'event_id', 'N/A')
                        created_at = getattr(event, 'created_at', 'N/A')
                        inputs = getattr(event, 'inputs', None)
                        outputs = getattr(event, 'outputs', None)
                        config = getattr(event, 'config', None)
                    
                    print(f"\n📝 Event {i+1}:")
                    print(f"   ID: {event_id}")
                    print(f"   Event Type: {event_type}")
                    print(f"   Event Name: {event_name}")
                    print(f"   Created At: {created_at}")
                    
                    # Check if this is our verbose test span
                    if event_name == expected_span:
                        verbose_test_span_found = True
                        print(f"   🎯 ← THIS IS OUR VERBOSE TEST SPAN!")
                        
                        if inputs:
                            print(f"   Inputs: {inputs}")
                        if outputs:
                            print(f"   Outputs: {outputs}")
                        if config:
                            print(f"   Config: {config}")
                    elif event_name == "initialization":
                        print(f"   🔍 ← Session initialization event")
                    else:
                        print(f"   📄 ← Other event")
                
                # Final result
                print(f"\n🎯 VERIFICATION RESULT:")
                if verbose_test_span_found:
                    print(f"✅ SUCCESS! Verbose test span '{expected_span}' found in backend!")
                    print(f"   🚀 OTLP export pipeline is working correctly!")
                    print(f"   🎉 Spans are successfully reaching HoneyHive UI!")
                else:
                    print(f"❌ Verbose test span '{expected_span}' NOT found")
                    print(f"   ⏳ May need to wait longer for backend processing")
                    
            else:
                print("❌ No events found for this session")
                print("   ⏳ Span may still be processing - try again in a few seconds")
                
        except Exception as e:
            print(f"❌ Error querying events: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"\n🔍 Also check HoneyHive UI directly:")
        print(f"   1. Go to https://app.honeyhive.ai")
        print(f"   2. Navigate to project: {project}")
        print(f"   3. Look for session: {session_id}")
        print(f"   4. Verify span: {expected_span}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_verbose_test_span()
