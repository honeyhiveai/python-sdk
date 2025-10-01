#!/usr/bin/env python3
"""
Deep Research Prod Event Analysis Script

This script gathers a comprehensive dataset of events from the Deep Research Prod project
to analyze JSON schema layouts for different event types (chain, model, tool).

Requirements:
- At least 100 events of each event_type: chain, model, tool
- Comprehensive JSON schema analysis
- Export organized data for further analysis
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime

from honeyhive import HoneyHive
from honeyhive.models import EventFilter
from honeyhive.models.generated import Operator, Type as FilterType

# Configure logging [[memory:8830238]]
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeepResearchEventAnalyzer:
    """Comprehensive event analyzer for Deep Research Prod project."""
    
    def __init__(self):
        """Initialize the analyzer with HoneyHive client."""
        # Load credentials from environment [[memory:8805742]]
        api_key = os.getenv('HH_API_KEY')
        api_url = os.getenv('HH_API_URL', 'https://api.staging.honeyhive.ai')
        project = os.getenv('HH_PROJECT', 'Deep Research Prod')
        
        if not api_key:
            raise ValueError("HH_API_KEY environment variable is required")
        
        logger.info(f"Initializing HoneyHive client for project: {project}")
        logger.info(f"API URL: {api_url}")
        
        self.client = HoneyHive(
            api_key=api_key,
            server_url=api_url,
            verbose=True
        )
        self.project = project
        
        # Data storage
        self.events_by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.schema_analysis: Dict[str, Dict[str, Any]] = {}
        self.total_events_collected = 0
        
    def create_event_type_filter(self, event_type: str) -> EventFilter:
        """Create an EventFilter for a specific event_type."""
        return EventFilter(
            field="event_type",
            value=event_type,
            operator=Operator.is_,
            type=FilterType.string
        )
    
    def gather_events_by_type(self, event_type: str, target_count: int = 100) -> List[Dict[str, Any]]:
        """Gather events of a specific type."""
        logger.info(f"Gathering {target_count} events of type: {event_type}")
        
        events = []
        page = 1
        limit = min(target_count, 1000)  # API limit is 1000 per request
        
        try:
            while len(events) < target_count:
                logger.info(f"Fetching page {page} for {event_type} events...")
                
                # Create filter for this event type
                event_filter = self.create_event_type_filter(event_type)
                
                # Get events using the proper API method
                response = self.client.events.get_events(
                    project=self.project,
                    filters=[event_filter],
                    limit=limit,
                    page=page
                )
                
                page_events = response.get('events', [])
                
                if not page_events:
                    logger.warning(f"No more {event_type} events found. Total collected: {len(events)}")
                    break
                
                # Convert Event objects to dictionaries for JSON serialization
                for event in page_events:
                    if hasattr(event, 'model_dump'):
                        event_dict = event.model_dump(mode='json', exclude_none=True)
                    elif hasattr(event, 'dict'):
                        event_dict = event.dict()
                    else:
                        event_dict = dict(event) if hasattr(event, '__dict__') else event
                    
                    events.append(event_dict)
                
                logger.info(f"Collected {len(page_events)} {event_type} events from page {page}")
                page += 1
                
                # Stop if we have enough events
                if len(events) >= target_count:
                    events = events[:target_count]
                    break
                    
        except Exception as e:
            logger.error(f"Error gathering {event_type} events: {str(e)}")
            logger.info(f"Collected {len(events)} {event_type} events before error")
        
        logger.info(f"Final count for {event_type}: {len(events)} events")
        return events
    
    def gather_all_events_comprehensive(self, target_count: int = 100) -> None:
        """Gather comprehensive event dataset."""
        logger.info(f"Starting comprehensive event gathering - target: {target_count} per type")
        
        # Event types to analyze (all four HoneyHive event types)
        event_types = ['session', 'chain', 'model', 'tool']
        
        for event_type in event_types:
            logger.info(f"\n{'='*50}")
            logger.info(f"GATHERING {event_type.upper()} EVENTS")
            logger.info(f"{'='*50}")
            
            events = self.gather_events_by_type(event_type, target_count)
            self.events_by_type[event_type] = events
            self.total_events_collected += len(events)
            
            logger.info(f"✓ Collected {len(events)} {event_type} events")
        
        logger.info(f"\n{'='*50}")
        logger.info(f"COLLECTION SUMMARY")
        logger.info(f"{'='*50}")
        for event_type, events in self.events_by_type.items():
            logger.info(f"{event_type}: {len(events)} events")
        logger.info(f"Total events collected: {self.total_events_collected}")
    
    def analyze_json_schemas(self) -> None:
        """Analyze JSON schemas for each event type."""
        logger.info("\n" + "="*50)
        logger.info("ANALYZING JSON SCHEMAS")
        logger.info("="*50)
        
        for event_type, events in self.events_by_type.items():
            if not events:
                logger.warning(f"No events to analyze for type: {event_type}")
                continue
                
            logger.info(f"\nAnalyzing {event_type} events...")
            
            # Collect all field paths and their types
            field_analysis = defaultdict(lambda: {'types': Counter(), 'examples': [], 'null_count': 0})
            
            for event in events:
                self._analyze_event_fields(event, field_analysis, "")
            
            # Process analysis results
            schema_info = {
                'event_count': len(events),
                'fields': {},
                'common_patterns': {},
                'sample_events': events[:3] if len(events) >= 3 else events
            }
            
            for field_path, analysis in field_analysis.items():
                total_occurrences = sum(analysis['types'].values()) + analysis['null_count']
                field_info = {
                    'total_occurrences': total_occurrences,
                    'null_count': analysis['null_count'],
                    'null_percentage': (analysis['null_count'] / len(events)) * 100,
                    'types': dict(analysis['types']),
                    'examples': analysis['examples'][:5]  # Keep first 5 examples
                }
                schema_info['fields'][field_path] = field_info
            
            self.schema_analysis[event_type] = schema_info
            
            logger.info(f"✓ Analyzed {len(events)} {event_type} events")
            logger.info(f"  - Found {len(field_analysis)} unique fields")
            logger.info(f"  - Sample fields: {list(field_analysis.keys())[:5]}")
    
    def _analyze_event_fields(self, obj: Any, field_analysis: Dict, path: str) -> None:
        """Recursively analyze fields in an event object."""
        if obj is None:
            field_analysis[path]['null_count'] += 1
            return
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._analyze_event_fields(value, field_analysis, new_path)
        elif isinstance(obj, list):
            field_analysis[path]['types'][f'list[{len(obj)}]'] += 1
            if obj:  # Analyze first item if list is not empty
                self._analyze_event_fields(obj[0], field_analysis, f"{path}[0]")
        else:
            obj_type = type(obj).__name__
            field_analysis[path]['types'][obj_type] += 1
            if len(field_analysis[path]['examples']) < 5:
                field_analysis[path]['examples'].append(obj)
    
    def export_analysis_results(self) -> None:
        """Export comprehensive analysis results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = f"deep_research_analysis_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"\nExporting analysis results to: {output_dir}")
        
        # Export raw events by type
        for event_type, events in self.events_by_type.items():
            filename = f"{output_dir}/raw_events_{event_type}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, default=str)
            logger.info(f"✓ Exported {len(events)} {event_type} events to {filename}")
        
        # Export schema analysis
        schema_filename = f"{output_dir}/schema_analysis.json"
        with open(schema_filename, 'w', encoding='utf-8') as f:
            json.dump(self.schema_analysis, f, indent=2, default=str)
        logger.info(f"✓ Exported schema analysis to {schema_filename}")
        
        # Export summary report
        summary_filename = f"{output_dir}/analysis_summary.md"
        self._generate_summary_report(summary_filename)
        logger.info(f"✓ Generated summary report: {summary_filename}")
        
        # Export consolidated dataset
        consolidated_filename = f"{output_dir}/consolidated_events.json"
        consolidated_data = {
            'metadata': {
                'project': self.project,
                'collection_timestamp': timestamp,
                'total_events': self.total_events_collected,
                'events_by_type': {k: len(v) for k, v in self.events_by_type.items()}
            },
            'events_by_type': self.events_by_type,
            'schema_analysis': self.schema_analysis
        }
        
        with open(consolidated_filename, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, default=str)
        logger.info(f"✓ Exported consolidated dataset to {consolidated_filename}")
        
        return output_dir
    
    def _generate_summary_report(self, filename: str) -> None:
        """Generate a comprehensive summary report in Markdown format."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Deep Research Prod - Event Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Project:** {self.project}\n")
            f.write(f"**Total Events Collected:** {self.total_events_collected}\n\n")
            
            f.write("## Event Collection Summary\n\n")
            f.write("| Event Type | Count | Target | Status |\n")
            f.write("|------------|-------|--------|---------|\n")
            
            for event_type, events in self.events_by_type.items():
                count = len(events)
                status = "✓ Complete" if count >= 100 else f"⚠️ Partial ({count}/100)"
                f.write(f"| {event_type} | {count} | 100 | {status} |\n")
            
            f.write("\n## Schema Analysis Overview\n\n")
            
            for event_type, analysis in self.schema_analysis.items():
                f.write(f"### {event_type.title()} Events\n\n")
                f.write(f"- **Event Count:** {analysis['event_count']}\n")
                f.write(f"- **Unique Fields:** {len(analysis['fields'])}\n\n")
                
                f.write("**Top 10 Most Common Fields:**\n\n")
                # Sort fields by occurrence
                sorted_fields = sorted(
                    analysis['fields'].items(),
                    key=lambda x: x[1]['total_occurrences'],
                    reverse=True
                )
                
                for field_name, field_info in sorted_fields[:10]:
                    occurrence_rate = (field_info['total_occurrences'] / analysis['event_count']) * 100
                    f.write(f"- `{field_name}`: {occurrence_rate:.1f}% occurrence\n")
                
                f.write("\n")
            
            f.write("## Key Findings\n\n")
            f.write("- Successfully collected events from Deep Research Prod project\n")
            f.write("- Analyzed JSON schema patterns across event types\n")
            f.write("- Identified common and unique fields for each event type\n")
            f.write("- Generated comprehensive dataset for further analysis\n\n")
            
            f.write("## Files Generated\n\n")
            f.write("- `raw_events_*.json`: Raw event data by type\n")
            f.write("- `schema_analysis.json`: Detailed schema analysis\n")
            f.write("- `consolidated_events.json`: Complete dataset\n")
            f.write("- `analysis_summary.md`: This summary report\n")

def main():
    """Main execution function."""
    logger.info("Starting Deep Research Prod Event Analysis")
    logger.info("="*60)
    
    try:
        # Initialize analyzer
        analyzer = DeepResearchEventAnalyzer()
        
        # Gather comprehensive event dataset
        analyzer.gather_all_events_comprehensive(target_count=100)
        
        # Analyze JSON schemas
        analyzer.analyze_json_schemas()
        
        # Export results
        output_dir = analyzer.export_analysis_results()
        
        logger.info("\n" + "="*60)
        logger.info("ANALYSIS COMPLETE!")
        logger.info("="*60)
        logger.info(f"Results exported to: {output_dir}")
        logger.info(f"Total events analyzed: {analyzer.total_events_collected}")
        
        # Print summary
        logger.info("\nCollection Summary:")
        for event_type, events in analyzer.events_by_type.items():
            logger.info(f"  {event_type}: {len(events)} events")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
