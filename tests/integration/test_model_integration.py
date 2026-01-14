"""Integration tests for model validation and serialization in HoneyHive."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

# v1 API imports - only models that exist in the new API
from honeyhive.models import (
    CreateConfigurationRequest,
    CreateDatapointRequest,
    CreateToolRequest,
    PostExperimentRunRequest,
)

# v0 models - these don't exist in v1, tests need to be migrated
# from honeyhive.models import (
#     CreateEventRequest,  # No longer exists in v1
#     SessionStartRequest,  # No longer exists in v1
# )
# from honeyhive.models.generated import FunctionCallParams as GeneratedFunctionCallParams
# from honeyhive.models.generated import Parameters2, SelectedFunction, UUIDType  # No longer exist in v1


@pytest.mark.integration
@pytest.mark.models
class TestModelIntegration:
    """Test model integration and end-to-end validation."""

    def test_model_serialization_integration(self):
        """Test complete model serialization workflow."""
        # v1 API: Create a configuration request with simplified structure
        config_request = CreateConfigurationRequest(
            name="complex-config",
            provider="openai",
            parameters={
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9,
            },
            env=["prod", "staging"],
            user_properties={"team": "AI-Research", "project_lead": "Dr. Smith"},
        )

        # Serialize to dict
        config_dict = config_request.model_dump(exclude_none=True)

        # Verify serialization
        assert config_dict["name"] == "complex-config"
        assert config_dict["provider"] == "openai"
        assert config_dict["parameters"]["model"] == "gpt-4"
        assert config_dict["parameters"]["temperature"] == 0.7
        assert config_dict["env"] == ["prod", "staging"]

        # v0 API test - commented out as these models don't exist in v1
        # config_request = PostConfigurationRequest(
        #     project="integration-test-project",
        #     name="complex-config",
        #     provider="openai",
        #     parameters=Parameters2(
        #         call_type="chat",
        #         model="gpt-4",
        #         hyperparameters={"temperature": 0.7, "max_tokens": 1000, "top_p": 0.9},
        #         responseFormat={"type": "json_object"},
        #         selectedFunctions=[
        #             SelectedFunction(
        #                 id="func-1",
        #                 name="extract_entities",
        #                 description="Extract named entities",
        #                 parameters={
        #                     "type": "object",
        #                     "properties": {
        #                         "entity_types": {
        #                             "type": "array",
        #                             "items": {"type": "string"},
        #                         }
        #                     },
        #                 },
        #             )
        #         ],
        #         functionCallParams=GeneratedFunctionCallParams.auto,
        #         forceFunction={"enabled": False},
        #     ),
        #     env=["prod", "staging"],
        #     user_properties={"team": "AI-Research", "project_lead": "Dr. Smith"},
        # )

    def test_model_validation_integration(self):
        """Test model validation with complex data."""
        # v1 API: Test datapoint creation instead (events API changed)
        datapoint_request = CreateDatapointRequest(
            inputs={
                "prompt": "Test prompt for validation",
                "user_id": "user-123",
                "session_id": "session-456",
            },
            metadata={
                "experiment_id": "exp-789",
                "quality_metrics": {"response_time": 1500, "token_usage": 150},
            },
        )

        # Verify model is valid
        assert datapoint_request.inputs["prompt"] == "Test prompt for validation"
        assert datapoint_request.metadata["experiment_id"] == "exp-789"

        # Test serialization preserves structure
        datapoint_dict = datapoint_request.model_dump(exclude_none=True)
        assert datapoint_dict["inputs"]["prompt"] == "Test prompt for validation"
        assert datapoint_dict["metadata"]["quality_metrics"]["response_time"] == 1500

        # v0 API test - commented out as CreateEventRequest doesn't exist in v1
        # event_request = CreateEventRequest(
        #     project="integration-test-project",
        #     source="production",
        #     event_name="validation-test-event",
        #     event_type="model",
        #     config={
        #         "model": "gpt-4",
        #         "provider": "openai",
        #         "temperature": 0.7,
        #         "max_tokens": 1000,
        #     },
        #     inputs={
        #         "prompt": "Test prompt for validation",
        #         "user_id": "user-123",
        #         "session_id": "session-456",
        #     },
        #     duration=1500.0,
        #     metadata={
        #         "experiment_id": "exp-789",
        #         "quality_metrics": {"response_time": 1500, "token_usage": 150},
        #     },
        # )

    def test_model_workflow_integration(self):
        """Test complete model workflow from creation to API usage."""
        # v1 API: Simplified workflow with models that exist

        # Step 1: Create datapoint request
        datapoint_request = CreateDatapointRequest(
            inputs={"query": "What is AI?", "context": "Technology question"},
            metadata={"workflow_step": "datapoint_creation"},
        )

        # Step 2: Create tool request
        tool_request = CreateToolRequest(
            task="integration-test-project",
            name="workflow-tool",
            description="Tool for workflow testing",
            parameters={"test": True, "workflow": "integration"},
            type="function",
        )

        # Step 3: Create experiment run request (replaces CreateRunRequest)
        run_request = PostExperimentRunRequest(
            name="workflow-evaluation",
            event_ids=[str(uuid.uuid4())],  # Use real UUID string
            configuration={"metrics": ["accuracy", "precision"]},
        )

        # Step 4: Create configuration request
        config_request = CreateConfigurationRequest(
            name="workflow-config",
            provider="openai",
            parameters={"model": "gpt-4", "temperature": 0.7},
        )

        # Verify all models are valid and can be serialized
        models = [
            datapoint_request,
            tool_request,
            run_request,
            config_request,
        ]

        for model in models:
            # Test serialization
            model_dict = model.model_dump(exclude_none=True)
            assert isinstance(model_dict, dict)

            # Test that name field is present where applicable
            if hasattr(model, "name") and model.name is not None:
                assert "name" in model_dict

        # v0 API test - commented out as these models don't exist in v1
        # session_request = SessionStartRequest(
        #     project="integration-test-project",
        #     session_name="model-workflow-session",
        #     source="integration-test",
        # )
        # event_request = CreateEventRequest(
        #     project="integration-test-project",
        #     source="integration-test",
        #     event_name="model-workflow-event",
        #     event_type="model",
        #     config={"model": "gpt-4", "provider": "openai"},
        #     inputs={"prompt": "Workflow test prompt"},
        #     duration=1000.0,
        #     session_id="session-123",
        # )

    def test_model_edge_cases_integration(self):
        """Test model edge cases and boundary conditions."""
        # v1 API: Test with minimal required fields using datapoint
        minimal_datapoint = CreateDatapointRequest(
            inputs={},
        )

        assert minimal_datapoint.inputs == {}

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

        complex_datapoint = CreateDatapointRequest(
            inputs={"complex_input": complex_config},
            metadata={"config": complex_config},
        )

        # Verify complex structures are preserved
        assert (
            complex_datapoint.metadata["config"]["nested"]["level1"]["level2"][
                "level3"
            ]["deep_value"]
            == "very_deep"
        )
        assert complex_datapoint.metadata["config"]["arrays"][0]["data"] == "test1"
        assert complex_datapoint.metadata["config"]["arrays"][1]["id"] == 2

        # v0 API test - commented out as CreateEventRequest doesn't exist in v1
        # minimal_event = CreateEventRequest(
        #     project="test-project",
        #     source="test",
        #     event_name="minimal-event",
        #     event_type="model",
        #     config={},
        #     inputs={},
        #     duration=0.0,
        # )
        # complex_event = CreateEventRequest(
        #     project="test-project",
        #     source="test",
        #     event_name="complex-event",
        #     event_type="model",
        #     config=complex_config,
        #     inputs={"complex_input": complex_config},
        #     duration=100.0,
        # )

    def test_model_error_handling_integration(self):
        """Test model error handling and validation."""
        # v1 API: Test missing required fields with configuration
        with pytest.raises(ValidationError):
            CreateConfigurationRequest(
                # Missing required 'name', 'provider', and 'parameters' fields
            )

        # Test invalid parameter types with configuration
        with pytest.raises(ValidationError):
            CreateConfigurationRequest(
                name="invalid-config",
                provider="openai",
                parameters="invalid_parameters",  # Should be a dict
            )

        # Test invalid provider type
        with pytest.raises(ValidationError):
            CreateConfigurationRequest(
                name="test-config",
                provider=123,  # Should be a string
                parameters={"model": "gpt-4"},
            )

        # v0 API test - commented out as these models don't exist in v1
        # with pytest.raises(ValueError):
        #     CreateEventRequest(
        #         project="test-project",
        #         source="test",
        #         event_name="invalid-event",
        #         event_type="invalid_type",
        #         config={},
        #         inputs={},
        #         duration=0.0,
        #     )
        # with pytest.raises(ValueError):
        #     PostConfigurationRequest(
        #         project="test-project",
        #         name="invalid-config",
        #         provider="openai",
        #         parameters="invalid_parameters",
        #     )

    def test_model_performance_integration(self):
        """Test model performance with large data structures."""
        # v1 API: Create large configuration with simplified structure
        large_parameters = {}
        for i in range(100):
            large_parameters[f"param_{i}"] = {
                "value": i,
                "description": f"Parameter {i} description",
                "nested": {"sub_value": i * 2, "sub_array": list(range(i))},
            }

        large_config = CreateConfigurationRequest(
            name="large-config",
            provider="openai",
            parameters=large_parameters,
        )

        # Test serialization performance
        start_time = datetime.now()
        config_dict = large_config.model_dump(exclude_none=True)
        end_time = datetime.now()

        # Verify serialization completed
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "large-config"
        assert len(config_dict["parameters"]) == 100

        # Verify reasonable performance (should complete in under 1 second)
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0

        # v0 API test - commented out as Parameters2 doesn't exist in v1
        # large_config = PostConfigurationRequest(
        #     project="integration-test-project",
        #     name="large-config",
        #     provider="openai",
        #     parameters=Parameters2(
        #         call_type="chat",
        #         model="gpt-4",
        #         hyperparameters=large_hyperparameters,
        #         responseFormat={"type": "text"},
        #         forceFunction={"enabled": False},
        #     ),
        # )
