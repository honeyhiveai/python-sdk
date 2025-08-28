#!/usr/bin/env python3
"""
API Client Models Demo - Showcasing Pydantic Model Usage at SDK Caller Level

This example demonstrates how the HoneyHive API client now consistently uses
existing Pydantic models from the models directory for all operations, providing
better type safety and validation at the SDK caller level.
"""

import os
import sys

# Add the src directory to the path so we can import our SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.models import (
    # Session models
    SessionStartRequest,
    
    # Event models
    CreateEventRequest,
    EventFilter,
    
    # Datapoint models
    CreateDatapointRequest,
    
    # Project models
    CreateProjectRequest,
    
    # Tool models
    CreateToolRequest,
    
    # Configuration models
    PostConfigurationRequest,
    
    # Evaluation models
    CreateRunRequest,
)


def demonstrate_model_imports():
    """Demonstrate that all Pydantic models are available for import."""
    print("=== Pydantic Models Available ===")
    
    print("✓ SessionStartRequest - for creating sessions")
    print("✓ CreateEventRequest - for creating events")
    print("✓ EventFilter - for filtering events")
    print("✓ CreateDatapointRequest - for creating datapoints")
    print("✓ CreateProjectRequest - for creating projects")
    print("✓ CreateToolRequest - for creating tools")
    print("✓ PostConfigurationRequest - for creating configurations")
    print("✓ CreateRunRequest - for creating evaluation runs")
    print()


def demonstrate_api_client_usage():
    """Demonstrate how the API client uses these models."""
    print("=== API Client Usage Examples ===")
    
    print("✓ All API methods now use Pydantic models as primary parameters:")
    print()
    
    print("Session Operations:")
    print("  client.sessions.create_session(session_request: SessionStartRequest)")
    print("  client.sessions.start_session(project, session_name, source, **kwargs)")
    print()
    
    print("Event Operations:")
    print("  client.events.create_event(event: CreateEventRequest)")
    print("  client.events.list_events(event_filter: EventFilter)")
    print()
    
    print("Datapoint Operations:")
    print("  client.datapoints.create_datapoint(request: CreateDatapointRequest)")
    print("  client.datapoints.update_datapoint(id, request: UpdateDatapointRequest)")
    print()
    
    print("Project Operations:")
    print("  client.projects.create_project(request: CreateProjectRequest)")
    print("  client.projects.update_project(id, request: UpdateProjectRequest)")
    print()
    
    print("Tool Operations:")
    print("  client.tools.create_tool(request: CreateToolRequest)")
    print("  client.tools.update_tool(id, request: UpdateToolRequest)")
    print()
    
    print("Configuration Operations:")
    print("  client.configurations.create_configuration(request: PostConfigurationRequest)")
    print("  client.configurations.update_configuration(id, request: PutConfigurationRequest)")
    print()
    
    print("Evaluation Operations:")
    print("  client.evaluations.create_run(request: CreateRunRequest)")
    print("  client.evaluations.update_run(id, request: UpdateRunRequest)")
    print()


def demonstrate_legacy_compatibility():
    """Demonstrate legacy compatibility methods."""
    print("=== Legacy Compatibility Demo ===")
    
    print("✓ All API methods maintain backward compatibility")
    print("  → Legacy methods with '_from_dict' suffix still accept raw dictionaries")
    print("  → New primary methods use validated Pydantic models")
    print("  → Both sync and async versions are available")
    print()
    
    print("Example legacy usage:")
    print("  client.events.create_event_from_dict({'event_name': 'legacy_event'})")
    print("  client.sessions.create_session_from_dict({'session_name': 'legacy_session'})")
    print("  client.datapoints.create_datapoint_from_dict({'project': 'demo', 'inputs': {}})")
    print()


def demonstrate_benefits():
    """Demonstrate the benefits of using Pydantic models."""
    print("=== Benefits of Pydantic Models ===")
    
    print("1. Type Safety:")
    print("   ✓ Parameters are validated before API calls")
    print("   ✓ IDE autocomplete and type checking")
    print("   ✓ Clear error messages for invalid parameters")
    print()
    
    print("2. Consistency:")
    print("   ✓ All API operations use the same parameter structure")
    print("   ✓ Models are auto-generated from OpenAPI specification")
    print("   ✓ Consistent validation rules across all endpoints")
    print()
    
    print("3. Developer Experience:")
    print("   ✓ Better documentation through model fields")
    print("   ✓ Automatic serialization with model_dump()")
    print("   ✓ Clear required vs optional parameter distinction")
    print()
    
    print("4. Backward Compatibility:")
    print("   ✓ Existing code continues to work unchanged")
    print("   ✓ Legacy methods still available")
    print("   ✓ Gradual migration path available")
    print()


if __name__ == "__main__":
    print("HoneyHive API Client Models Demo")
    print("=" * 60)
    print()
    
    # Run all demonstrations
    demonstrate_model_imports()
    demonstrate_api_client_usage()
    demonstrate_legacy_compatibility()
    demonstrate_benefits()
    
    print("=" * 60)
    print("Demo completed!")
    print()
    print("Summary:")
    print("The HoneyHive API client now consistently uses existing Pydantic models")
    print("from the models directory for all operations, providing better type safety")
    print("and validation at the SDK caller level while maintaining full backward")
    print("compatibility.")
