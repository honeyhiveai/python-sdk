#!/usr/bin/env python3
"""
Script to query chat completion events from 'Deep Research Prod' project
to analyze proper span JSON mapping structure.

This script will extract multiple chat completion events to understand
the proper layout for span processor mapping.
"""

import json
import os
import sys
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from honeyhive import HoneyHive
from honeyhive.models.generated import EventFilter, Operator, Type, EventType1


def load_credentials() -> Dict[str, str]:
    """Load credentials from environment variables (sourced from .env file)."""
    api_key = os.getenv('HH_API_KEY')
    if not api_key:
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'HH_' in key or 'API' in key:
                print(f"  {key}={value[:20]}..." if len(value) > 20 else f"  {key}={value}")
        raise ValueError("HH_API_KEY environment variable is required. Please source .env file first.")
    
    return {
        'api_key': api_key,
        'server_url': os.getenv('HH_API_URL', 'https://api.honeyhive.ai')
    }


def query_chat_completion_events(client: HoneyHive, project: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Query chat completion events from the specified project.
    
    Args:
        client: HoneyHive client instance
        project: Project name to query from
        limit: Maximum number of events to retrieve
        
    Returns:
        List of event dictionaries
    """
    print(f"Querying events from project: {project}")
    
    # Create filters to find chat completion events
    filters = [
        EventFilter(
            field="event_type",
            value="model",
            operator=Operator.is_,
            type=Type.string
        )
    ]
    
    try:
        # Use the get_events method which returns both events and count
        result = client.events.get_events(
            project=project,
            filters=filters,
            limit=limit
        )
        
        events = result.get('events', [])
        total_count = result.get('totalEvents', 0)
        
        print(f"Found {len(events)} events out of {total_count} total events")
        return [event.model_dump() if hasattr(event, 'model_dump') else event for event in events]
        
    except Exception as e:
        print(f"Error querying events: {e}")
        
        # Try alternative approach with broader filter
        try:
            print("Trying alternative query approach...")
            result = client.events.get_events(
                project=project,
                filters=[],  # No filters - get all events
                limit=limit
            )
            
            events = result.get('events', [])
            print(f"Found {len(events)} events with no filters")
            return [event.model_dump() if hasattr(event, 'model_dump') else event for event in events]
            
        except Exception as e2:
            print(f"Alternative query also failed: {e2}")
            return []


def analyze_event_structure(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the structure of events to understand span mapping.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        Analysis results
    """
    if not events:
        return {"error": "No events to analyze"}
    
    analysis = {
        "total_events": len(events),
        "event_types": set(),
        "common_fields": set(),
        "metadata_fields": set(),
        "config_fields": set(),
        "input_fields": set(),
        "output_fields": set(),
        "sample_events": []
    }
    
    # Analyze first few events in detail
    for i, event in enumerate(events[:5]):
        analysis["sample_events"].append({
            "index": i,
            "event_id": event.get("event_id", "unknown"),
            "event_type": event.get("event_type", "unknown"),
            "event_name": event.get("event_name", "unknown"),
            "has_metadata": bool(event.get("metadata")),
            "has_config": bool(event.get("config")),
            "has_inputs": bool(event.get("inputs")),
            "has_outputs": bool(event.get("outputs")),
            "structure": {
                "top_level_keys": list(event.keys()),
                "metadata_keys": list(event.get("metadata", {}).keys()) if event.get("metadata") else [],
                "config_keys": list(event.get("config", {}).keys()) if event.get("config") else [],
                "input_keys": list(event.get("inputs", {}).keys()) if event.get("inputs") else [],
                "output_keys": list(event.get("outputs", {}).keys()) if event.get("outputs") else []
            }
        })
    
    # Collect field statistics across all events
    for event in events:
        if "event_type" in event:
            analysis["event_types"].add(event["event_type"])
        
        analysis["common_fields"].update(event.keys())
        
        if event.get("metadata"):
            analysis["metadata_fields"].update(event["metadata"].keys())
        
        if event.get("config"):
            analysis["config_fields"].update(event["config"].keys())
        
        if event.get("inputs"):
            analysis["input_fields"].update(event["inputs"].keys())
        
        if event.get("outputs"):
            analysis["output_fields"].update(event["outputs"].keys())
    
    # Convert sets to lists for JSON serialization
    analysis["event_types"] = list(analysis["event_types"])
    analysis["common_fields"] = list(analysis["common_fields"])
    analysis["metadata_fields"] = list(analysis["metadata_fields"])
    analysis["config_fields"] = list(analysis["config_fields"])
    analysis["input_fields"] = list(analysis["input_fields"])
    analysis["output_fields"] = list(analysis["output_fields"])
    
    return analysis


def save_analysis_results(events: List[Dict[str, Any]], analysis: Dict[str, Any], output_dir: str = "event_analysis"):
    """Save analysis results to files.
    
    Args:
        events: Raw event data
        analysis: Analysis results
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw events
    with open(f"{output_dir}/raw_events.json", "w") as f:
        json.dump(events, f, indent=2, default=str)
    
    # Save analysis
    with open(f"{output_dir}/analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # Save sample events for detailed inspection
    if analysis.get("sample_events"):
        with open(f"{output_dir}/sample_events_detailed.json", "w") as f:
            json.dump(analysis["sample_events"], f, indent=2, default=str)
    
    # Save first complete event as example
    if events:
        with open(f"{output_dir}/first_event_complete.json", "w") as f:
            json.dump(events[0], f, indent=2, default=str)
    
    print(f"Analysis results saved to {output_dir}/")


def main():
    """Main function to run the analysis."""
    print("=== HoneyHive Event Analysis for Span Processor Mapping ===")
    
    try:
        # Load credentials
        creds = load_credentials()
        print(f"Using API URL: {creds['server_url']}")
        
        # Initialize client
        client = HoneyHive(
            api_key=creds['api_key'],
            server_url=creds['server_url'],
            verbose=True  # Enable verbose logging for debugging
        )
        
        # Query events from Deep Research Prod project
        project_name = "Deep Research Prod"
        events = query_chat_completion_events(client, project_name, limit=100)
        
        if not events:
            print("No events found. Exiting.")
            return
        
        print(f"\n=== Successfully retrieved {len(events)} events ===")
        
        # Analyze event structure
        analysis = analyze_event_structure(events)
        
        # Save results
        save_analysis_results(events, analysis)
        
        # Print summary
        print(f"\n=== Analysis Summary ===")
        print(f"Total events analyzed: {analysis['total_events']}")
        print(f"Event types found: {analysis['event_types']}")
        print(f"Common top-level fields: {analysis['common_fields']}")
        print(f"Metadata fields: {analysis['metadata_fields']}")
        print(f"Config fields: {analysis['config_fields']}")
        print(f"Input fields: {analysis['input_fields']}")
        print(f"Output fields: {analysis['output_fields']}")
        
        if analysis.get("sample_events"):
            print(f"\n=== Sample Event Structure ===")
            first_sample = analysis["sample_events"][0]
            print(f"Event ID: {first_sample['event_id']}")
            print(f"Event Type: {first_sample['event_type']}")
            print(f"Event Name: {first_sample['event_name']}")
            print(f"Top-level keys: {first_sample['structure']['top_level_keys']}")
            
            if first_sample['structure']['metadata_keys']:
                print(f"Metadata keys: {first_sample['structure']['metadata_keys']}")
            if first_sample['structure']['config_keys']:
                print(f"Config keys: {first_sample['structure']['config_keys']}")
            if first_sample['structure']['input_keys']:
                print(f"Input keys: {first_sample['structure']['input_keys']}")
            if first_sample['structure']['output_keys']:
                print(f"Output keys: {first_sample['structure']['output_keys']}")
        
        print(f"\n=== Next Steps ===")
        print("1. Review the saved JSON files in event_analysis/ directory")
        print("2. Compare with current span processor implementation")
        print("3. Update span processor mapping based on findings")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
