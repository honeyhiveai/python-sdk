"""Unit tests for generated models."""

import uuid

import pytest
from pydantic import ValidationError

from honeyhive.models.generated import (
    CallType,
    Configuration,
    EventType1,
    SessionStartRequest,
    UUIDType,
)


class TestGeneratedModels:
    """Test basic functionality of generated Pydantic models."""

    def test_session_start_request_creation(self):
        """Test creating a SessionStartRequest."""
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test"
        )

        assert session_request.project == "test-project"
        assert session_request.session_name == "test-session"
        assert session_request.source == "test"

    def test_session_start_request_validation(self):
        """Test SessionStartRequest validation."""
        with pytest.raises(ValidationError):
            SessionStartRequest(
                project="test-project"
                # Missing required fields
            )

    def test_configuration_model(self):
        """Test Configuration model."""
        config = Configuration(
            project="test-project",
            name="test-config",
            provider="openai",
            parameters={"call_type": "chat", "model": "gpt-4"},
            type="LLM",
        )

        assert config.project == "test-project"
        assert config.name == "test-config"
        assert config.provider == "openai"

    def test_call_type_enum(self):
        """Test CallType enum."""
        assert CallType.chat.value == "chat"
        assert CallType.completion.value == "completion"

    def test_event_type_enum(self):
        """Test EventType1 enum."""
        assert EventType1.model.value == "model"
        assert EventType1.tool.value == "tool"

    def test_uuid_type(self):
        """Test UUIDType functionality."""
        test_uuid = uuid.uuid4()
        uuid_obj = UUIDType(test_uuid)

        assert uuid_obj.root == test_uuid
        assert str(uuid_obj) == str(test_uuid)
        assert repr(uuid_obj) == f"UUIDType({test_uuid})"

    def test_model_serialization(self):
        """Test model serialization."""
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test"
        )

        serialized = session_request.model_dump(exclude_none=True)
        assert serialized["project"] == "test-project"
        assert serialized["session_name"] == "test-session"
        assert serialized["source"] == "test"
