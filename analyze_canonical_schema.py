"""Analyze canonical HoneyHive schema from production events.

This script retrieves events from Deep Research Prod project and analyzes
the canonical schema structure across all event types.
"""

import os
import sys
import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from honeyhive import HoneyHive
from honeyhive.models.generated import EventFilter

# Initialize client
client = HoneyHive(
    api_key=os.getenv("HH_API_KEY")
)

# Project ID for Deep Research Prod
project_name = "Deep Research Prod"

print(f"Retrieving events from project: {project_name}")
print("=" * 80)

# Collect events by type
events_by_type = {
    "model": [],
    "chain": [],
    "tool": [],
    "session": []
}

# Fetch events with exact name filter
print(f"\nFetching 'Financial Research Agent Eval' events...")
print("(Target: 100+ per event type)")

# Use list_events API with EventFilter
try:
    # Create filter for "Financial Research Agent Eval" events
    event_name_filter = EventFilter(
        field="event_name",
        value="Financial Research Agent Eval",
        operator="is",
        type="string"
    )
    
    print(f"Fetching events with filter: event_name = 'Financial Research Agent Eval'")
    
    # List events with filter (limit 1000 to get as many as possible)
    events = client.events.list_events(
        event_filter=event_name_filter,
        limit=1000,
        project=project_name
    )
    
    print(f"\n✅ Retrieved {len(events)} total events")
    
    # First, inspect what event types we actually have
    actual_event_types = defaultdict(int)
    for event in events:
        if hasattr(event, 'model_dump'):
            event_dict = event.model_dump()
        elif hasattr(event, 'dict'):
            event_dict = event.dict()
        else:
            event_dict = event
        
        event_type = event_dict.get('event_type', 'unknown')
        # Convert enum to string if needed
        if hasattr(event_type, 'value'):
            event_type = event_type.value
        actual_event_types[event_type] += 1
    
    print(f"\nActual event_type distribution:")
    for et, count in actual_event_types.items():
        print(f"  {et}: {count}")
    
    # Process events by type
    total_events = 0
    for event in events:
        # Convert to dict if needed
        if hasattr(event, 'model_dump'):
            event_dict = event.model_dump()
        elif hasattr(event, 'dict'):
            event_dict = event.dict()
        else:
            event_dict = event
        
        event_type = event_dict.get('event_type', 'unknown')
        # Convert enum to string if needed
        if hasattr(event_type, 'value'):
            event_type = event_type.value
            event_dict['event_type'] = event_type  # Update dict with string value
        
        # Add to events_by_type if it doesn't exist
        if event_type not in events_by_type:
            events_by_type[event_type] = []
        
        if len(events_by_type[event_type]) < 100:
            events_by_type[event_type].append(event_dict)
            total_events += 1
    
    # Print progress for session events
    print(f"\nSession events collected: {len(events_by_type.get('session', []))}")
    
    # Now fetch child events (model, chain, tool) from these sessions
    print(f"\nFetching child events from sessions...")
    for session_event in events_by_type.get('session', [])[:20]:  # Limit to first 20 sessions
        session_id = session_event.get('session_id')
        if not session_id:
            continue
        
        try:
            # Fetch events for this session
            session_filter = EventFilter(
                field="session_id",
                value=session_id,
                operator="is",
                type="id"
            )
            
            child_events = client.events.list_events(
                event_filter=session_filter,
                limit=1000,
                project=project_name
            )
            
            # Process child events
            for child_event in child_events:
                # Convert to dict
                if hasattr(child_event, 'model_dump'):
                    child_dict = child_event.model_dump()
                elif hasattr(child_event, 'dict'):
                    child_dict = child_event.dict()
                else:
                    child_dict = child_event
                
                event_type = child_dict.get('event_type', 'unknown')
                # Convert enum to string
                if hasattr(event_type, 'value'):
                    event_type = event_type.value
                    child_dict['event_type'] = event_type
                
                # Skip session events (we already have those)
                if event_type == 'session':
                    continue
                
                # Add to events_by_type
                if event_type not in events_by_type:
                    events_by_type[event_type] = []
                
                if len(events_by_type[event_type]) < 100:
                    events_by_type[event_type].append(child_dict)
                    total_events += 1
            
            # Print progress every 5 sessions
            if (events_by_type.get('session', []).index(session_event) + 1) % 5 == 0:
                print(f"  Processed {events_by_type.get('session', []).index(session_event) + 1} sessions...")
                for et in ['model', 'chain', 'tool']:
                    print(f"    {et}: {len(events_by_type.get(et, []))}")
            
            # Check if we have enough
            model_ok = len(events_by_type.get('model', [])) >= 100
            chain_ok = len(events_by_type.get('chain', [])) >= 100
            tool_ok = len(events_by_type.get('tool', [])) >= 100
            
            if model_ok and chain_ok and tool_ok:
                print(f"\n✅ Collected 100+ samples for model, chain, and tool!")
                break
                
        except Exception as e:
            print(f"  Error fetching child events for session {session_id}: {e}")
            continue
    
    # Final progress
    print(f"\nFinal collection progress:")
    for et, evts in sorted(events_by_type.items()):
        status = "✅" if len(evts) >= 100 else "⏳"
        print(f"  {status} {et}: {len(evts)}")

except Exception as e:
    print(f"\n❌ Error in main fetch loop: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 80}")
print("COLLECTION SUMMARY")
print(f"{'=' * 80}")
for event_type, events in events_by_type.items():
    print(f"{event_type}: {len(events)} events")

# Save raw events
output_dir = "canonical_schema_analysis"
os.makedirs(output_dir, exist_ok=True)

for event_type, events in events_by_type.items():
    if events:
        output_file = f"{output_dir}/{event_type}_events.json"
        with open(output_file, 'w') as f:
            json.dump(events, f, indent=2)
        print(f"  Saved {len(events)} {event_type} events to {output_file}")

print(f"\n{'=' * 80}")
print("SCHEMA ANALYSIS")
print(f"{'=' * 80}")

# Analyze schema structure
def analyze_schema(events: List[Dict], event_type: str):
    """Analyze schema structure for event type."""
    print(f"\n--- {event_type.upper()} Events ({len(events)} samples) ---")
    
    if not events:
        print("  No events to analyze")
        return
    
    # Sample event
    sample = events[0]
    
    # Analyze top-level fields
    all_fields = set()
    for event in events:
        all_fields.update(event.keys())
    
    print(f"\nTop-level fields ({len(all_fields)}):")
    for field in sorted(all_fields):
        # Count how many events have this field
        count = sum(1 for e in events if field in e)
        percentage = (count / len(events)) * 100
        print(f"  {field}: {count}/{len(events)} ({percentage:.1f}%)")
    
    # Analyze the 4-section structure
    print(f"\nInputs structure:")
    if 'inputs' in sample and sample['inputs']:
        inputs = sample['inputs']
        if isinstance(inputs, dict):
            print(f"  Keys: {list(inputs.keys())}")
            print(f"  Sample: {json.dumps(inputs, indent=4)[:200]}...")
        else:
            print(f"  Type: {type(inputs).__name__}")
    
    print(f"\nOutputs structure:")
    if 'outputs' in sample and sample['outputs']:
        outputs = sample['outputs']
        if isinstance(outputs, dict):
            print(f"  Keys: {list(outputs.keys())}")
            print(f"  Sample: {json.dumps(outputs, indent=4)[:200]}...")
        else:
            print(f"  Type: {type(outputs).__name__}")
    
    print(f"\nConfig structure:")
    if 'config' in sample and sample['config']:
        config = sample['config']
        if isinstance(config, dict):
            print(f"  Keys: {list(config.keys())}")
    
    print(f"\nMetadata structure:")
    if 'metadata' in sample and sample['metadata']:
        metadata = sample['metadata']
        if isinstance(metadata, dict):
            print(f"  Keys: {list(metadata.keys())}")

# Analyze each event type
for event_type, events in events_by_type.items():
    analyze_schema(events, event_type)

# Cross-type analysis
print(f"\n{'=' * 80}")
print("CROSS-TYPE ANALYSIS")
print(f"{'=' * 80}")

# Find common patterns
all_events = []
for events in events_by_type.values():
    all_events.extend(events)

if all_events:
    # Analyze inputs patterns
    inputs_keys = defaultdict(int)
    outputs_keys = defaultdict(int)
    config_keys = defaultdict(int)
    metadata_keys = defaultdict(int)
    
    for event in all_events:
        if 'inputs' in event and isinstance(event['inputs'], dict):
            for key in event['inputs'].keys():
                inputs_keys[key] += 1
        if 'outputs' in event and isinstance(event['outputs'], dict):
            for key in event['outputs'].keys():
                outputs_keys[key] += 1
        if 'config' in event and isinstance(event['config'], dict):
            for key in event['config'].keys():
                config_keys[key] += 1
        if 'metadata' in event and isinstance(event['metadata'], dict):
            for key in event['metadata'].keys():
                metadata_keys[key] += 1
    
    print(f"\nMost common inputs keys:")
    for key, count in sorted(inputs_keys.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count} events")
    
    print(f"\nMost common outputs keys:")
    for key, count in sorted(outputs_keys.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count} events")
    
    print(f"\nMost common config keys:")
    for key, count in sorted(config_keys.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count} events")
    
    print(f"\nMost common metadata keys:")
    for key, count in sorted(metadata_keys.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count} events")

print(f"\n{'=' * 80}")
print("ANALYSIS COMPLETE")
print(f"{'=' * 80}")
print(f"\nResults saved to: {output_dir}/")

