"""Integration tests for model validation and serialization in HoneyHive."""

import uuid
from datetime import datetime

import pytest

from honeyhive.models import (
    CreateDatapointRequest,
    CreateEventRequest,
    CreateRunRequest,
    CreateToolRequest,
    PostConfigurationRequest,
    SessionStartRequest,
)
from honeyhive.models.generated import (
    CallType,
    EnvEnum,
    EventType1,
)
from honeyhive.models.generated import FunctionCallParams as GeneratedFunctionCallParams
from honeyhive.models.generated import (
    Parameters2,
    SelectedFunction,
    Type3,
    UUIDType,
)


@pytest.mark.integration
@pytest.mark.models
class TestModelIntegration:
    """Test model integration and end-to-end validation."""

    def test_model_serialization_integration(self):
        """Test complete model serialization workflow."""
        # Create a complex configuration request
        config_request = PostConfigurationRequest(
            project="integration-test-project",
            name="complex-config",
            provider="openai",
            parameters=Parameters2(
                call_type=CallType.chat,
                model="gpt-4",
                hyperparameters={"temperature": 0.7, "max_tokens": 1000, "top_p": 0.9},
                responseFormat={"type": "json_object"},
                selectedFunctions=[
                    SelectedFunction(
                        id="func-1",
                        name="extract_entities",
                        description="Extract named entities",
                        parameters={
                            "type": "object",
                            "properties": {
                                "entity_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            },
                        },
                    )
                ],
                functionCallParams=GeneratedFunctionCallParams.auto,
                forceFunction={"enabled": False},
            ),
            env=[EnvEnum.prod, EnvEnum.staging],
            user_properties={"team": "AI-Research", "project_lead": "Dr. Smith"},
        )

        # Serialize to dict
        config_dict = config_request.model_dump(exclude_none=True)

        # Verify serialization
        assert config_dict["project"] == "integration-test-project"
        assert config_dict["name"] == "complex-config"
        assert config_dict["provider"] == "openai"
        assert config_dict["parameters"]["model"] == "gpt-4"
        assert config_dict["parameters"]["hyperparameters"]["temperature"] == 0.7
        assert len(config_dict["parameters"]["selectedFunctions"]) == 1
        assert (
            config_dict["parameters"]["selectedFunctions"][0]["name"]
            == "extract_entities"
        )

        # Verify enum serialization
        assert config_dict["parameters"]["call_type"] == CallType.chat
        assert config_dict["env"] == [EnvEnum.prod, EnvEnum.staging]

    def test_model_validation_integration(self):
        """Test model validation with complex data."""
        # Test valid event creation
        event_request = CreateEventRequest(
            project="integration-test-project",
            source="production",
            event_name="validation-test-event",
            event_type=EventType1.model,
            config={
                "model": "gpt-4",
                "provider": "openai",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            inputs={
                "prompt": "Test prompt for validation",
                "user_id": "user-123",
                "session_id": "session-456",
            },
            duration=1500.0,
            metadata={
                "experiment_id": "exp-789",
                "quality_metrics": {"response_time": 1500, "token_usage": 150},
            },
        )

        # Verify model is valid
        assert event_request.project == "integration-test-project"
        assert event_request.event_type == EventType1.model
        assert event_request.duration == 1500.0
        assert event_request.metadata["experiment_id"] == "exp-789"

        # Test serialization preserves structure
        event_dict = event_request.model_dump(exclude_none=True)
        assert event_dict["config"]["temperature"] == 0.7
        assert event_dict["metadata"]["quality_metrics"]["response_time"] == 1500

    def test_model_workflow_integration(self):
        """Test complete model workflow from creation to API usage."""
        # Step 1: Create session request
        session_request = SessionStartRequest(
            project="integration-test-project",
            session_name="model-workflow-session",
            source="integration-test",
        )

        # Step 2: Create event request linked to session
        event_request = CreateEventRequest(
            project="integration-test-project",
            source="integration-test",
            event_name="model-workflow-event",
            event_type=EventType1.model,
            config={"model": "gpt-4", "provider": "openai"},
            inputs={"prompt": "Workflow test prompt"},
            duration=1000.0,
            session_id="session-123",  # Would come from session creation
        )

        # Step 3: Create datapoint request
        datapoint_request = CreateDatapointRequest(
            project="integration-test-project",
            inputs={"query": "What is AI?", "context": "Technology question"},
            linked_event="event-123",  # Would come from event creation
            metadata={"workflow_step": "datapoint_creation"},
        )

        # Step 4: Create tool request
        tool_request = CreateToolRequest(
            task="integration-test-project",
            name="workflow-tool",
            description="Tool for workflow testing",
            parameters={"test": True, "workflow": "integration"},
            type=Type3.function,
        )

        # Step 5: Create evaluation run request
        run_request = CreateRunRequest(
            project="integration-test-project",
            name="workflow-evaluation",
            event_ids=[UUIDType(str(uuid.uuid4()))],  # Use real UUID
            configuration={"metrics": ["accuracy", "precision"]},
        )

        # Verify all models are valid and can be serialized
        models = [
            session_request,
            event_request,
            datapoint_request,
            tool_request,
            run_request,
        ]

        for model in models:
            # Test serialization
            model_dict = model.model_dump(exclude_none=True)
            assert isinstance(model_dict, dict)

            # Test that required fields are present
            if hasattr(model, "project"):
                assert "project" in model_dict

    def test_model_edge_cases_integration(self):
        """Test model edge cases and boundary conditions."""
        # Test with minimal required fields
        minimal_event = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="minimal-event",
            event_type=EventType1.model,
            config={},
            inputs={},
            duration=0.0,
        )

        assert minimal_event.project == "test-project"
        assert minimal_event.config == {}
        assert minimal_event.inputs == {}

        # Test with complex nested structures
        complex_config = {
            "model": "gpt-4",
            "provider": "openai",
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "deep_value": "very_deep",
                            "array": [1, 2, 3, {"nested": True}],
                        }
                    }
                }
            },
            "arrays": [{"id": 1, "data": "test1"}, {"id": 2, "data": "test2"}],
        }

        complex_event = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="complex-event",
            event_type=EventType1.model,
            config=complex_config,
            inputs={"complex_input": complex_config},
            duration=100.0,
        )

        # Verify complex structures are preserved
        assert (
            complex_event.config["nested"]["level1"]["level2"]["level3"]["deep_value"]
            == "very_deep"
        )
        assert complex_event.config["arrays"][0]["data"] == "test1"
        assert complex_event.config["arrays"][1]["id"] == 2

    def test_model_error_handling_integration(self):
        """Test model error handling and validation."""
        # Test invalid enum values
        with pytest.raises(ValueError):
            CreateEventRequest(
                project="test-project",
                source="test",
                event_name="invalid-event",
                event_type="invalid_type",  # Should be EventType1 enum
                config={},
                inputs={},
                duration=0.0,
            )

        # Test missing required fields
        with pytest.raises(ValueError):
            CreateEventRequest(
                # Missing required fields
                config={},
                inputs={},
                duration=0.0,
            )

        # Test invalid parameter types
        with pytest.raises(ValueError):
            PostConfigurationRequest(
                project="test-project",
                name="invalid-config",
                provider="openai",
                parameters="invalid_parameters",  # Should be Parameters2
            )

    def test_model_performance_integration(self):
        """Test model performance with large data structures."""
        # Create large configuration
        large_hyperparameters = {}
        for i in range(100):
            large_hyperparameters[f"param_{i}"] = {
                "value": i,
                "description": f"Parameter {i} description",
                "nested": {"sub_value": i * 2, "sub_array": list(range(i))},
            }

        large_config = PostConfigurationRequest(
            project="integration-test-project",
            name="large-config",
            provider="openai",
            parameters=Parameters2(
                call_type=CallType.chat,
                model="gpt-4",
                hyperparameters=large_hyperparameters,
                responseFormat={"type": "text"},
                forceFunction={"enabled": False},
            ),
        )

        # Test serialization performance
        start_time = datetime.now()
        config_dict = large_config.model_dump(exclude_none=True)
        end_time = datetime.now()

        # Verify serialization completed
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "large-config"
        assert len(config_dict["parameters"]["hyperparameters"]) == 100

        # Verify reasonable performance (should complete in under 1 second)
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0
