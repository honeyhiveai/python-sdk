#!/usr/bin/env python3
"""
Example demonstrating dataclass alternatives to Pydantic models.
This shows how you could implement the same functionality using standard library dataclasses.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import json
from enum import Enum


# ============================================================================
# Dataclass Implementation Examples
# ============================================================================

@dataclass
class SessionStartRequest:
    """Dataclass equivalent of the Pydantic SessionStartRequest model."""
    project: str
    session_name: str
    source: str
    session_id: Optional[str] = None
    children_ids: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    user_properties: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    start_time: Optional[float] = None
    end_time: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionStartRequest':
        """Create instance from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionStartRequest':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class EventType(Enum):
    """Event type enumeration."""
    session = 'session'
    model = 'model'
    tool = 'tool'
    chain = 'chain'


@dataclass
class Event:
    """Dataclass equivalent of the Pydantic Event model."""
    project_id: Optional[str] = None
    source: Optional[str] = None
    event_name: Optional[str] = None
    event_type: Optional[EventType] = None
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[int] = None
    duration: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    user_properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Handle enum serialization
        if result.get('event_type'):
            result['event_type'] = result['event_type'].value
        return {k: v for k, v in result.items() if v is not None}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create instance from dictionary."""
        # Handle enum deserialization
        if 'event_type' in data and data['event_type']:
            data['event_type'] = EventType(data['event_type'])
        return cls(**data)


@dataclass
class Threshold:
    """Dataclass equivalent of the Pydantic Threshold model."""
    min: Optional[float] = None
    max: Optional[float] = None
    
    def is_valid(self, value: float) -> bool:
        """Check if a value is within the threshold."""
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.max:
            return False
        return True


@dataclass
class Metric:
    """Dataclass equivalent of the Pydantic Metric model."""
    name: str
    task: str
    type: str
    description: str
    return_type: str
    criteria: Optional[str] = None
    code_snippet: Optional[str] = None
    prompt: Optional[str] = None
    enabled_in_prod: Optional[bool] = None
    needs_ground_truth: Optional[bool] = None
    threshold: Optional[Threshold] = None
    pass_when: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Handle nested objects
        if result.get('threshold'):
            result['threshold'] = asdict(result['threshold'])
        return {k: v for k, v in result.items() if v is not None}


# ============================================================================
# Validation and Serialization Utilities
# ============================================================================

class DataclassValidator:
    """Utility class for validating dataclass instances."""
    
    @staticmethod
    def validate_required_fields(instance: Any) -> List[str]:
        """Validate that required fields are not None."""
        errors = []
        for field_name, field_value in instance.__dict__.items():
            field_info = instance.__class__.__dataclass_fields__[field_name]
            if not field_info.default and not field_info.default_factory and field_value is None:
                errors.append(f"Field '{field_name}' is required but is None")
        return errors
    
    @staticmethod
    def validate_types(instance: Any) -> List[str]:
        """Basic type validation for dataclass instances."""
        errors = []
        for field_name, field_value in instance.__dict__.items():
            field_info = instance.__class__.__dataclass_fields__[field_name]
            expected_type = field_info.type
            
            # Handle Optional types
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:
                if type(None) in expected_type.__args__:
                    # This is Optional[T], check if it's None or the expected type
                    if field_value is not None:
                        expected_type = next(t for t in expected_type.__args__ if t is not type(None))
                    else:
                        continue
            
            if field_value is not None and not isinstance(field_value, expected_type):
                errors.append(f"Field '{field_name}' expected {expected_type}, got {type(field_value)}")
        
        return errors


# ============================================================================
# Usage Examples
# ============================================================================

def demonstrate_dataclass_usage():
    """Demonstrate how to use the dataclass models."""
    
    print("=== Dataclass Model Usage Examples ===\n")
    
    # Create a session request
    session = SessionStartRequest(
        project="my-project",
        session_name="test-session",
        source="production",
        config={"model": "gpt-4", "temperature": 0.7}
    )
    
    print("1. Session Request:")
    print(f"   Project: {session.project}")
    print(f"   Session Name: {session.session_name}")
    print(f"   Config: {session.config}")
    print()
    
    # Convert to JSON
    json_data = session.to_json()
    print("2. JSON Serialization:")
    print(json_data)
    print()
    
    # Create from JSON
    recreated_session = SessionStartRequest.from_json(json_data)
    print("3. Deserialization:")
    print(f"   Recreated project: {recreated_session.project}")
    print(f"   Recreated config: {recreated_session.config}")
    print()
    
    # Create an event
    event = Event(
        project_id="proj-123",
        event_name="model-completion",
        event_type=EventType.model,
        config={"model": "gpt-4"},
        inputs={"prompt": "Hello, world!"},
        outputs={"completion": "Hi there!"},
        duration=1500.0
    )
    
    print("4. Event Creation:")
    print(f"   Event Type: {event.event_type}")
    print(f"   Duration: {event.duration}ms")
    print()
    
    # Validation
    validator = DataclassValidator()
    type_errors = validator.validate_types(event)
    required_errors = validator.validate_required_fields(event)
    
    print("5. Validation Results:")
    if type_errors:
        print(f"   Type errors: {type_errors}")
    if required_errors:
        print(f"   Required field errors: {required_errors}")
    if not type_errors and not required_errors:
        print("   All validations passed!")
    print()
    
    # Threshold example
    threshold = Threshold(min=0.0, max=1.0)
    test_values = [0.5, -0.1, 1.5]
    
    print("6. Threshold Validation:")
    for value in test_values:
        is_valid = threshold.is_valid(value)
        print(f"   Value {value}: {'✓' if is_valid else '✗'}")


def compare_with_pydantic():
    """Show the differences between dataclass and Pydantic approaches."""
    
    print("=== Comparison with Pydantic ===\n")
    
    print("Dataclass Approach:")
    print("  ✓ Standard library (no dependencies)")
    print("  ✓ Better performance for simple cases")
    print("  ✓ Lower memory footprint")
    print("  ✓ Cleaner syntax")
    print("  ✗ No runtime validation")
    print("  ✗ Manual serialization")
    print("  ✗ No built-in field types")
    print("  ✗ Manual OpenAPI integration")
    print()
    
    print("Pydantic Approach:")
    print("  ✓ Runtime validation")
    print("  ✓ Built-in serialization")
    print("  ✓ Rich field types")
    print("  ✓ OpenAPI integration")
    print("  ✓ Better error handling")
    print("  ✗ Additional dependency")
    print("  ✗ Higher memory usage")
    print("  ✗ Validation overhead")
    print()


if __name__ == "__main__":
    demonstrate_dataclass_usage()
    print("\n" + "="*50 + "\n")
    compare_with_pydantic()
