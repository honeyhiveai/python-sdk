"""Unit tests for HoneyHive models integration.

This module tests the integration and functionality of HoneyHive models,
including model instantiation, validation, and integration patterns.

Test Coverage:
- Model import/export functionality
- Pydantic model instantiation and validation
- UUIDType class methods and functionality
- TracingParams validation logic

# pylint: disable=duplicate-code  # Unit tests share common patterns
- Field validation and error handling
- Integration patterns used across the codebase

Following Agent OS testing standards with proper fixtures and isolation.
Generated using enhanced comprehensive analysis framework for 90%+ coverage.
"""

# pylint: disable=too-many-lines,line-too-long,redefined-outer-name,no-member
# Reason: Comprehensive testing file requires extensive test coverage for 90%+ target
# Line length disabled for test readability and comprehensive assertions
# Redefined outer name disabled for pytest fixture usage pattern

from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from honeyhive import models
from honeyhive.models import (
    Configuration,
    CreateEventRequest,
    EventFilter,
    EventType,
    Metric,
    SessionStartRequest,
    Tool,
    TracingParams,
    UUIDType,
)
from honeyhive.models.generated import (
    CallType,
)
from honeyhive.models.generated import EventType as GeneratedEventType
from honeyhive.models.generated import (
    EventType1,
    Operator,
    Parameters,
    ReturnType,
    ToolType,
    Type,
    Type1,
)


class TestModelsIntegration:
    """Test models integration and import functionality."""

    def test_models_import_availability(self) -> None:
        """Test that all models are properly imported and available."""
        # Test that all major model classes are importable
        assert CreateEventRequest is not None
        assert SessionStartRequest is not None
        assert TracingParams is not None
        assert UUIDType is not None
        assert EventType is not None
        assert Configuration is not None
        assert Tool is not None
        assert Metric is not None

    def test_models_module_exports(self) -> None:
        """Test that models module exports all expected classes."""
        # models imported via honeyhive.models at top level

        # Test that __all__ exports are accessible
        expected_exports = [
            "SessionStartRequest",
            "CreateEventRequest",
            "TracingParams",
            "EventType",
            "Configuration",
            "Tool",
            "Metric",
            "UUIDType",
        ]

        for export_name in expected_exports:
            assert hasattr(models, export_name), f"Missing export: {export_name}"
            assert getattr(models, export_name) is not None


class TestSessionStartRequest:
    """Test SessionStartRequest model functionality."""

    @pytest.fixture
    def valid_session_data(self) -> Dict[str, Any]:
        """Provide valid session data for testing."""
        return {
            "project": "test-project",
            "session_name": "test-session",
            "source": "test-source",
        }

    def test_session_start_request_creation(
        self, valid_session_data: Dict[str, Any]
    ) -> None:
        """Test creating a SessionStartRequest with valid data."""
        session = SessionStartRequest(**valid_session_data)

        assert session.project == "test-project"
        assert session.session_name == "test-session"
        assert session.source == "test-source"
        assert session.session_id is None  # Optional field
        assert session.children_ids is None  # Optional field

    def test_session_start_request_with_optional_fields(
        self, valid_session_data: Dict[str, Any]
    ) -> None:
        """Test SessionStartRequest with optional fields."""
        session_data = {
            **valid_session_data,
            "session_id": "test-session-123",
            "children_ids": ["child-1", "child-2"],
            "config": {"model": "gpt-4"},
            "inputs": {"prompt": "test prompt"},
            "outputs": {"response": "test response"},
            "error": None,
            "duration": 1500.0,
            "user_properties": {"user_id": "user-123"},
            "metrics": {"accuracy": 0.95},
            "feedback": {"rating": 5},
            "metadata": {"version": "1.0"},
            "start_time": 1234567890000.0,
            "end_time": 1234567891500,
        }

        session = SessionStartRequest(**session_data)

        assert session.session_id == "test-session-123"
        assert session.children_ids == ["child-1", "child-2"]
        assert session.config == {"model": "gpt-4"}
        assert session.inputs == {"prompt": "test prompt"}
        assert session.outputs == {"response": "test response"}
        assert session.duration == 1500.0
        assert session.user_properties == {"user_id": "user-123"}
        assert session.metrics == {"accuracy": 0.95}
        assert session.feedback == {"rating": 5}
        assert session.metadata == {"version": "1.0"}
        assert session.start_time == 1234567890000.0
        assert session.end_time == 1234567891500

    def test_session_start_request_validation_errors(self) -> None:
        """Test SessionStartRequest validation with invalid data."""
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            SessionStartRequest()  # type: ignore[call-arg]

        error_dict = exc_info.value.errors()
        required_fields = {"project", "session_name", "source"}
        error_fields = {error["loc"][0] for error in error_dict}

        assert required_fields.issubset(error_fields)

    def test_session_start_request_partial_data(
        self, valid_session_data: Dict[str, Any]
    ) -> None:
        """Test SessionStartRequest with minimal required data."""
        session = SessionStartRequest(**valid_session_data)

        # Test that optional fields default to None
        assert session.session_id is None
        assert session.children_ids is None
        assert session.config is None
        assert session.inputs is None
        assert session.outputs is None
        assert session.error is None
        assert session.duration is None
        assert session.user_properties is None
        assert session.metrics is None
        assert session.feedback is None
        assert session.metadata is None
        assert session.start_time is None
        assert session.end_time is None


class TestCreateEventRequest:
    """Test CreateEventRequest model functionality."""

    @pytest.fixture
    def valid_event_data(self) -> Dict[str, Any]:
        """Provide valid event data for testing."""
        return {
            "project": "test-project",
            "source": "test-source",
            "event_name": "test-event",
            "event_type": "model",
            "config": {"model": "gpt-4"},
            "inputs": {"prompt": "test prompt"},
            "duration": 1000.0,
        }

    def test_create_event_request_creation(
        self, valid_event_data: Dict[str, Any]
    ) -> None:
        """Test creating a CreateEventRequest with valid data."""
        event = CreateEventRequest(**valid_event_data)

        assert event.project == "test-project"
        assert event.source == "test-source"
        assert event.event_name == "test-event"
        assert event.event_type.value == "model"
        assert event.event_id is None  # Optional field
        assert event.session_id is None  # Optional field

    def test_create_event_request_with_optional_fields(
        self, valid_event_data: Dict[str, Any]
    ) -> None:
        """Test CreateEventRequest with optional fields."""
        event_data = {
            **valid_event_data,
            "event_id": "event-123",
            "session_id": "session-456",
            "parent_id": "parent-789",
            "children_ids": ["child-1", "child-2"],
            "config": {"temperature": 0.7},
            "inputs": {"prompt": "test prompt"},
            "outputs": {"response": "test response"},
            "error": None,
            "start_time": 1234567890000.0,
            "end_time": 1234567891000.0,
            "duration": 1000.0,
            "metadata": {"model": "gpt-4"},
            "feedback": {"helpful": True},
            "metrics": {"latency": 1.5},
            "user_properties": {"user_id": "user-123"},
        }

        event = CreateEventRequest(**event_data)

        assert event.event_id == "event-123"
        assert event.session_id == "session-456"
        assert event.parent_id == "parent-789"
        assert event.children_ids == ["child-1", "child-2"]
        assert event.config == {"temperature": 0.7}
        assert event.inputs == {"prompt": "test prompt"}
        assert event.outputs == {"response": "test response"}
        assert event.start_time == 1234567890000.0
        assert event.end_time == 1234567891000.0
        assert event.duration == 1000.0
        assert event.metadata == {"model": "gpt-4"}
        assert event.feedback == {"helpful": True}
        assert event.metrics == {"latency": 1.5}
        assert event.user_properties == {"user_id": "user-123"}

    def test_create_event_request_validation_errors(self) -> None:
        """Test CreateEventRequest validation with invalid data."""
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            CreateEventRequest()  # type: ignore[call-arg]

        error_dict = exc_info.value.errors()
        required_fields = {
            "project",
            "source",
            "event_name",
            "event_type",
            "config",
            "inputs",
            "duration",
        }
        error_fields = {error["loc"][0] for error in error_dict}

        assert required_fields.issubset(error_fields)

    def test_create_event_request_event_type_validation(
        self, valid_event_data: Dict[str, Any]
    ) -> None:
        """Test CreateEventRequest with different event types."""
        valid_event_types = [
            "model",
            "tool",
            "chain",
        ]  # Only these are valid for CreateEventRequest

        for event_type in valid_event_types:
            event_data = {**valid_event_data, "event_type": event_type}
            event = CreateEventRequest(**event_data)
            assert event.event_type.value == event_type


class TestUUIDType:
    """Test UUIDType class functionality."""

    @pytest.fixture
    def sample_uuid(self) -> UUID:
        """Provide a sample UUID for testing."""
        return uuid4()

    def test_uuid_type_creation(self, sample_uuid: UUID) -> None:
        """Test UUIDType creation with valid UUID."""
        uuid_type = UUIDType(sample_uuid)
        assert (
            uuid_type.root == sample_uuid
        )  # Use public property instead of protected _value

    def test_uuid_type_root_property(self, sample_uuid: UUID) -> None:
        """Test UUIDType root property returns the UUID value."""
        uuid_type = UUIDType(sample_uuid)
        assert uuid_type.root == sample_uuid

    def test_uuid_type_str_method(self, sample_uuid: UUID) -> None:
        """Test UUIDType __str__ method returns string representation."""
        uuid_type = UUIDType(sample_uuid)
        assert str(uuid_type) == str(sample_uuid)
        assert isinstance(str(uuid_type), str)

    def test_uuid_type_repr_method(self, sample_uuid: UUID) -> None:
        """Test UUIDType __repr__ method returns proper representation."""
        uuid_type = UUIDType(sample_uuid)
        expected_repr = f"UUIDType({sample_uuid})"
        assert repr(uuid_type) == expected_repr

    def test_uuid_type_with_string_uuid(self) -> None:
        """Test UUIDType creation with string UUID."""
        uuid_string = "12345678-1234-5678-9012-123456789012"
        uuid_obj = UUID(uuid_string)
        uuid_type = UUIDType(uuid_obj)

        assert str(uuid_type) == uuid_string
        assert uuid_type.root == uuid_obj


class TestTracingParams:
    """Test TracingParams model functionality."""

    @pytest.fixture
    def valid_tracing_data(self) -> Dict[str, Any]:
        """Provide valid tracing parameters for testing."""
        return {
            "event_type": "model",
            "event_name": "test-event",
            "project": "test-project",
            "source": "test-source",
        }

    def test_tracing_params_creation(self, valid_tracing_data: Dict[str, Any]) -> None:
        """Test creating TracingParams with valid data."""
        params = TracingParams(**valid_tracing_data)

        assert params.event_type == "model"
        assert params.event_name == "test-event"
        assert params.project == "test-project"
        assert params.source == "test-source"

    def test_tracing_params_with_all_fields(self) -> None:
        """Test TracingParams with all optional fields."""
        test_exception = Exception("test error")
        params_data: Dict[str, Any] = {
            "event_type": "tool",
            "event_name": "test-tool",
            "event_id": "event-123",
            "source": "test-source",
            "project": "test-project",
            "session_id": "session-456",
            "user_id": "user-789",
            "session_name": "test-session",
            "inputs": {"input": "test"},
            "outputs": {"output": "result"},
            "metadata": {"version": "1.0"},
            "config": {"temperature": 0.7},
            "metrics": {"accuracy": 0.95},
            "feedback": {"rating": 5},
            "error": test_exception,
            "tracer": "mock-tracer",
        }

        params = TracingParams(**params_data)

        assert params.event_type == "tool"
        assert params.event_name == "test-tool"
        assert params.event_id == "event-123"
        assert params.source == "test-source"
        assert params.project == "test-project"
        assert params.session_id == "session-456"
        assert params.user_id == "user-789"
        assert params.session_name == "test-session"
        assert params.inputs == {"input": "test"}
        assert params.outputs == {"output": "result"}
        assert params.metadata == {"version": "1.0"}
        assert params.config == {"temperature": 0.7}
        assert params.metrics == {"accuracy": 0.95}
        assert params.feedback == {"rating": 5}
        assert isinstance(params.error, Exception)
        assert params.tracer == "mock-tracer"

    def test_tracing_params_event_type_validation_with_string(self) -> None:
        """Test TracingParams event_type validation with valid strings."""
        valid_event_types = ["model", "tool", "chain", "session"]

        for event_type in valid_event_types:
            params = TracingParams(event_type=event_type)
            assert params.event_type == event_type

    def test_tracing_params_event_type_validation_with_enum(self) -> None:
        """Test TracingParams event_type validation with EventType enum."""
        params = TracingParams(event_type=GeneratedEventType.model)
        assert params.event_type == GeneratedEventType.model

    def test_tracing_params_event_type_validation_with_none(self) -> None:
        """Test TracingParams event_type validation with None value."""
        params = TracingParams(event_type=None)
        assert params.event_type is None

    def test_tracing_params_event_type_validation_error_invalid_string(self) -> None:
        """Test TracingParams event_type validation with invalid string."""
        with pytest.raises(ValidationError) as exc_info:
            TracingParams(event_type="invalid_type")

        error = exc_info.value.errors()[0]
        assert "Invalid event_type 'invalid_type'" in str(error["ctx"])
        assert "Must be one of:" in str(error["ctx"])

    def test_tracing_params_event_type_validation_error_invalid_type(self) -> None:
        """Test TracingParams event_type validation with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            TracingParams(event_type=123)  # type: ignore[arg-type]  # Invalid type

        error = exc_info.value.errors()[0]
        # The error message varies, just check that validation failed appropriately
        assert error["type"] == "enum" or "event_type" in str(error)

    def test_tracing_params_default_values(self) -> None:
        """Test TracingParams with default values."""
        params = TracingParams()

        assert params.event_type is None
        assert params.event_name is None
        assert params.event_id is None
        assert params.source is None
        assert params.project is None
        assert params.session_id is None
        assert params.user_id is None
        assert params.session_name is None
        assert params.inputs is None
        assert params.outputs is None
        assert params.metadata is None
        assert params.config is None
        assert params.metrics is None
        assert params.feedback is None
        assert params.error is None
        assert params.tracer is None


class TestModelValidation:
    """Test general model validation functionality."""

    def test_configuration_model_creation(self) -> None:
        """Test Configuration model creation."""
        # Parameters and CallType imported at top level

        parameters = Parameters(
            call_type=CallType.chat,
            model="gpt-4",
        )

        config_data: Dict[str, Any] = {
            "project": "test-project",
            "name": "test-config",
            "provider": "openai",
            "parameters": parameters,
        }

        config = Configuration(**config_data)
        assert config.project == "test-project"
        assert config.name == "test-config"
        assert config.provider == "openai"
        assert config.parameters.model == "gpt-4"
        assert config.parameters.call_type.value == "chat"

    def test_tool_model_creation(self) -> None:
        """Test Tool model creation."""
        # ToolType imported at top level

        tool_data: Dict[str, Any] = {
            "task": "test-task",
            "name": "test-tool",
            "description": "A test tool",
            "parameters": {"param1": "value1"},
            "tool_type": ToolType.function,
        }

        tool = Tool(**tool_data)
        assert tool.name == "test-tool"
        assert tool.description == "A test tool"
        assert tool.task == "test-task"
        assert tool.parameters == {"param1": "value1"}
        assert tool.tool_type.value == "function"

    def test_metric_model_creation(self) -> None:
        """Test Metric model creation."""
        # Type1 and ReturnType imported at top level

        metric_data: Dict[str, Any] = {
            "name": "test-metric",
            "type": Type1.PYTHON,
            "criteria": "def evaluate(output): return 1.0",
            "description": "A test metric",
            "return_type": ReturnType.float,
        }

        metric = Metric(**metric_data)
        assert metric.name == "test-metric"
        assert metric.type == Type1.PYTHON
        assert metric.description == "A test metric"

    def test_event_filter_model_creation(self) -> None:
        """Test EventFilter model creation."""
        # Operator and Type imported at top level

        filter_data: Dict[str, Any] = {
            "field": "metadata.cost",
            "value": "0.01",
            "operator": Operator.greater_than,
            "type": Type.number,
        }

        event_filter = EventFilter(**filter_data)
        assert event_filter.field == "metadata.cost"
        assert event_filter.value == "0.01"
        assert event_filter.operator is not None
        assert event_filter.operator.value == "greater than"
        assert event_filter.type is not None
        assert event_filter.type.value == "number"


class TestModelIntegrationPatterns:
    """Test integration patterns used across the codebase."""

    def test_create_event_request_integration_pattern(self) -> None:
        """Test CreateEventRequest integration pattern used in API classes."""
        # EventType1 imported at top level

        # This tests the common pattern found in API usage
        event_data: Dict[str, Any] = {
            "project": "test-project",
            "source": "production",
            "event_name": "llm_call",
            "event_type": EventType1.model,
            "config": {"model": "gpt-4", "temperature": 0.7},
            "inputs": {"prompt": "Hello, world!"},
            "outputs": {"response": "Hello! How can I help you today?"},
            "duration": 1500.0,
            "metadata": {"user_id": "user-123", "session_id": "session-456"},
        }

        event = CreateEventRequest(**event_data)

        # Test that the model can be serialized (common API pattern)
        event_dict = event.model_dump()
        assert event_dict["project"] == "test-project"
        assert (
            event_dict["event_type"].value == "model"
        )  # Enum objects in serialized dict
        assert event_dict["config"]["model"] == "gpt-4"

    def test_session_start_request_integration_pattern(self) -> None:
        """Test SessionStartRequest integration pattern used in session API."""
        session_data: Dict[str, Any] = {
            "project": "test-project",
            "session_name": "user_conversation",
            "source": "production",
            "config": {"model": "gpt-4"},
            "inputs": {"initial_prompt": "Start conversation"},
            "user_properties": {"user_id": "user-123", "plan": "premium"},
        }

        session = SessionStartRequest(**session_data)

        # Test serialization pattern
        session_dict = session.model_dump()
        assert session_dict["project"] == "test-project"
        assert session_dict["session_name"] == "user_conversation"
        user_props = session_dict.get("user_properties")
        assert user_props is not None
        assert user_props["plan"] == "premium"

    def test_tracing_params_decorator_pattern(self) -> None:
        """Test TracingParams pattern used in tracer decorators."""
        # This tests the pattern used in tracer decorators
        params = TracingParams(
            event_type="model",
            event_name="llm_completion",
            project="test-project",
            inputs={"prompt": "test"},
            metadata={"model": "gpt-4"},
        )

        # Test that params can be used in decorator context
        assert params.event_type == "model"
        assert params.event_name == "llm_completion"
        inputs = params.inputs
        assert inputs is not None
        assert inputs["prompt"] == "test"  # pylint: disable=unsubscriptable-object
        metadata = params.metadata
        assert metadata is not None
        assert metadata["model"] == "gpt-4"  # pylint: disable=unsubscriptable-object

    def test_batch_event_creation_pattern(self) -> None:
        """Test batch event creation pattern used in API classes."""
        # EventType1 imported at top level

        # Test creating multiple events (common batch pattern)
        events_data: list[Dict[str, Any]] = [
            {
                "project": "test-project",
                "source": "test",
                "event_name": f"event-{i}",
                "event_type": EventType1.model,
                "config": {"model": "gpt-4"},
                "inputs": {"prompt": f"prompt-{i}"},
                "duration": 1000.0,
            }
            for i in range(3)
        ]

        events = [CreateEventRequest(**data) for data in events_data]

        assert len(events) == 3
        for i, event in enumerate(events):
            assert event.event_name == f"event-{i}"
            assert event.inputs["prompt"] == f"prompt-{i}"

    def test_model_validation_error_handling(self) -> None:
        """Test model validation error handling patterns."""
        # Test that validation errors are properly raised and handled
        with pytest.raises(ValidationError) as exc_info:
            CreateEventRequest(  # type: ignore[call-arg]
                project="test",
                source="test",
                # Missing required event_name and event_type
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # At least event_name and event_type missing

        # Test that error messages are informative
        error_fields = {error["loc"][0] for error in errors}
        assert "event_name" in error_fields
        assert "event_type" in error_fields

    def test_model_field_access_patterns(self) -> None:
        """Test common field access patterns used across the codebase."""
        # EventType1 imported at top level

        event = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"temperature": 0.7},
            inputs={"prompt": "test"},
            duration=1000.0,
            metadata={"user_id": "user-123"},
        )

        # Test common field access patterns
        assert event.project == "test-project"
        config = event.config
        assert config is not None
        assert config["temperature"] == 0.7  # type: ignore[index]
        metadata = event.metadata
        assert metadata is not None
        assert metadata["user_id"] == "user-123"  # type: ignore[index]
        assert "max_tokens" not in config  # Non-existent key

        # Test optional field handling
        assert event.error is None
        assert event.duration == 1000.0  # Duration is required and set
        assert event.feedback is None


class TestEventTypeEnum:
    """Test EventType enum functionality."""

    def test_event_type_enum_values(self) -> None:
        """Test EventType enum has expected values."""
        # Test that EventType enum has the expected values
        expected_values = {"session", "model", "tool", "chain"}
        actual_values = {e.value for e in GeneratedEventType}

        assert expected_values.issubset(actual_values)

    def test_event_type_enum_usage(self) -> None:
        """Test EventType enum usage in models."""
        # EventType1 imported at top level

        # Test using enum values directly
        event = CreateEventRequest(
            project="test",
            source="test",
            event_name="test",
            event_type=EventType1.model,
            config={"model": "gpt-4"},
            inputs={"prompt": "test"},
            duration=1000.0,
        )

        assert event.event_type.value == "model"

    def test_event_type_enum_in_tracing_params(self) -> None:
        """Test EventType enum usage in TracingParams."""
        params = TracingParams(event_type=GeneratedEventType.tool)
        assert params.event_type == GeneratedEventType.tool


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_create_event_request_serialization(self) -> None:
        """Test CreateEventRequest serialization to dict."""
        # EventType1 imported at top level

        event = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="test-event",
            event_type=EventType1.model,
            config={"temperature": 0.7},
            inputs={"prompt": "test"},
            outputs={"response": "result"},
            duration=1000.0,
        )

        event_dict = event.model_dump()

        assert event_dict["project"] == "test-project"
        assert (
            event_dict["event_type"].value == "model"
        )  # Enum objects in serialized dict
        assert event_dict["config"]["temperature"] == 0.7
        assert event_dict["inputs"]["prompt"] == "test"
        assert event_dict["outputs"]["response"] == "result"

    def test_session_start_request_serialization(self) -> None:
        """Test SessionStartRequest serialization to dict."""
        session = SessionStartRequest(
            project="test-project",
            session_name="test-session",
            source="test",
            config={"model": "gpt-4"},
            user_properties={"user_id": "user-123"},
        )

        session_dict = session.model_dump()

        assert session_dict["project"] == "test-project"
        assert session_dict["session_name"] == "test-session"
        assert session_dict["config"]["model"] == "gpt-4"
        assert session_dict["user_properties"]["user_id"] == "user-123"

    def test_tracing_params_serialization(self) -> None:
        """Test TracingParams serialization to dict."""
        params = TracingParams(
            event_type="model",
            event_name="test",
            project="test-project",
            inputs={"prompt": "test"},
            metadata={"version": "1.0"},
        )

        params_dict = params.model_dump()

        assert params_dict["event_type"] == "model"
        assert params_dict["event_name"] == "test"
        assert params_dict["project"] == "test-project"
        assert params_dict["inputs"]["prompt"] == "test"
        assert params_dict["metadata"]["version"] == "1.0"
