"""Simplified tests for Pydantic model usage in HoneyHive API client."""

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import (
    CreateDatapointRequest,
    CreateEventRequest,
    CreateProjectRequest,
    CreateRunRequest,
    CreateToolRequest,
    PostConfigurationRequest,
    SessionStartRequest,
)


class TestModelImportAndUsage:
    """Test that Pydantic models can be imported and used."""

    def test_models_can_be_imported(self):
        """Test that all required models can be imported."""
        # This test just verifies that imports work
        assert SessionStartRequest is not None
        assert CreateEventRequest is not None
        assert CreateDatapointRequest is not None
        assert CreateProjectRequest is not None
        assert CreateToolRequest is not None
        assert PostConfigurationRequest is not None
        assert CreateRunRequest is not None

    def test_session_start_request_creation(self):
        """Test creating a SessionStartRequest with minimal required fields."""
        try:
            session_request = SessionStartRequest(
                project="test-project", session_name="test-session", source="test"
            )
            assert session_request.project == "test-project"
            assert session_request.session_name == "test-session"
            assert session_request.source == "test"
        except Exception as e:
            pytest.fail(f"Failed to create SessionStartRequest: {e}")

    def test_create_project_request_creation(self):
        """Test creating a CreateProjectRequest with minimal required fields."""
        try:
            project_request = CreateProjectRequest(
                name="test-project", description="A test project"
            )
            assert project_request.name == "test-project"
            assert project_request.description == "A test project"
        except Exception as e:
            pytest.fail(f"Failed to create CreateProjectRequest: {e}")

    def test_create_tool_request_creation(self):
        """Test creating a CreateToolRequest with minimal required fields."""
        try:
            from honeyhive.models.generated import Type3

            tool_request = CreateToolRequest(
                task="test-project",
                name="test-tool",
                description="A test tool",
                parameters={"param1": "value1"},
                type=Type3.function,
            )
            assert tool_request.task == "test-project"
            assert tool_request.name == "test-tool"
            assert tool_request.description == "A test tool"
            assert tool_request.parameters == {"param1": "value1"}
            assert tool_request.type == Type3.function
        except Exception as e:
            pytest.fail(f"Failed to create CreateToolRequest: {e}")

    def test_create_tool_request_creation_with_enum(self):
        """Test creating a CreateToolRequest using the correct enum type."""
        try:
            from honeyhive.models.generated import Type3

            tool_request = CreateToolRequest(
                task="test-project",
                name="test-tool",
                description="A test tool",
                parameters={"param1": "value1"},
                type=Type3.function,
            )
            assert tool_request.task == "test-project"
            assert tool_request.name == "test-tool"
            assert tool_request.description == "A test tool"
            assert tool_request.parameters == {"param1": "value1"}
            assert tool_request.type == Type3.function
        except Exception as e:
            pytest.fail(f"Failed to create CreateToolRequest with enum: {e}")


class TestAPIClientModelSupport:
    """Test that the API client supports model-based methods."""

    def test_api_client_has_model_methods(self, api_key):
        """Test that the API client has the new model-based methods."""
        client = HoneyHive(api_key=api_key)

        # Check that model-based methods exist
        assert hasattr(client.sessions, "create_session")
        assert hasattr(client.events, "create_event")
        assert hasattr(client.datapoints, "create_datapoint")
        assert hasattr(client.datasets, "create_dataset")
        assert hasattr(client.projects, "create_project")
        assert hasattr(client.tools, "create_tool")
        assert hasattr(client.configurations, "create_configuration")
        assert hasattr(client.evaluations, "create_run")

    def test_api_client_has_legacy_methods(self, api_key):
        """Test that the API client maintains legacy methods."""
        client = HoneyHive(api_key=api_key)

        # Check that legacy methods exist
        assert hasattr(client.sessions, "create_session_from_dict")
        assert hasattr(client.events, "create_event_from_dict")
        assert hasattr(client.datapoints, "create_datapoint_from_dict")
        assert hasattr(client.datasets, "create_dataset_from_dict")
        assert hasattr(client.projects, "create_project_from_dict")
        assert hasattr(client.tools, "create_tool_from_dict")
        assert hasattr(client.configurations, "create_configuration_from_dict")
        assert hasattr(client.evaluations, "create_run_from_dict")


class TestModelSerialization:
    """Test that models can be properly serialized."""

    def test_session_request_serialization(self):
        """Test that SessionStartRequest can be serialized."""
        session_request = SessionStartRequest(
            project="test-project", session_name="test-session", source="test"
        )

        # Test model_dump method
        serialized = session_request.model_dump(exclude_none=True)
        assert serialized["project"] == "test-project"
        assert serialized["session_name"] == "test-session"
        assert serialized["source"] == "test"

        # Test that optional fields are excluded when None
        assert "config" not in serialized
        assert "metadata" not in serialized

    def test_project_request_serialization(self):
        """Test that CreateProjectRequest can be serialized."""
        project_request = CreateProjectRequest(
            name="test-project", description="A test project"
        )

        serialized = project_request.model_dump(exclude_none=True)
        assert serialized["name"] == "test-project"
        assert serialized["description"] == "A test project"

    def test_tool_request_serialization(self):
        """Test that CreateToolRequest can be serialized."""
        from honeyhive.models.generated import Type3

        tool_request = CreateToolRequest(
            task="test-project",
            name="test-tool",
            description="A test tool",
            parameters={"param1": "value1"},
            type=Type3.function,
        )

        serialized = tool_request.model_dump(exclude_none=True)
        assert serialized["task"] == "test-project"
        assert serialized["name"] == "test-tool"
        assert serialized["description"] == "A test tool"
        assert serialized["parameters"] == {"param1": "value1"}
        # The enum value is serialized as the enum object itself
        assert serialized["type"] == Type3.function


class TestBackwardCompatibility:
    """Test that legacy functionality is maintained."""

    def test_legacy_methods_work_with_dicts(self, api_key):
        """Test that legacy methods can accept dictionary parameters."""
        client = HoneyHive(api_key=api_key)

        # Test that legacy methods exist and can be called
        # We're not testing the actual API calls, just the method existence
        assert callable(client.sessions.create_session_from_dict)
        assert callable(client.events.create_event_from_dict)
        assert callable(client.datapoints.create_datapoint_from_dict)
        assert callable(client.datasets.create_dataset_from_dict)
        assert callable(client.projects.create_project_from_dict)
        assert callable(client.tools.create_tool_from_dict)
        assert callable(client.configurations.create_configuration_from_dict)
        assert callable(client.evaluations.create_run_from_dict)


class TestModelValidation:
    """Test that model validation works correctly."""

    def test_invalid_session_request_raises_error(self):
        """Test that invalid SessionStartRequest raises validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SessionStartRequest(
                # Missing required fields
                project="test-project"
                # Missing session_name and source
            )

    def test_invalid_project_request_raises_error(self):
        """Test that invalid CreateProjectRequest raises validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateProjectRequest(
                # Missing required name field
                description="A test project"
            )

    def test_invalid_tool_request_raises_error(self):
        """Test that invalid CreateToolRequest raises validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateToolRequest(
                # Missing required fields
                description="A test tool"
            )


class TestComplexModelScenarios:
    """Test complex nested model structures one model at a time."""

    def test_create_event_request_with_nested_config(self):
        """Test creating CreateEventRequest with complex nested configuration."""
        try:
            from honeyhive.models.generated import EventType1

            # Create a complex event with nested configuration
            event_request = CreateEventRequest(
                project="test-project",
                source="production",
                event_name="complex-llm-evaluation",
                event_type=EventType1.model,
                event_id="event-123",
                session_id="session-456",
                parent_id=None,
                children_ids=None,
                config={
                    "model": "gpt-4",
                    "provider": "openai",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "nested": {
                        "function_calling": {
                            "enabled": True,
                            "mode": "auto",
                            "functions": [
                                {
                                    "name": "extract_data",
                                    "description": "Extract structured data",
                                }
                            ],
                        },
                        "safety": {
                            "content_filter": "high",
                            "blocked_categories": ["harmful", "inappropriate"],
                        },
                    },
                },
                inputs={
                    "prompt": "Analyze the following text and extract key information",
                    "context": "This is a complex analysis task",
                    "metadata": {
                        "task_type": "information_extraction",
                        "difficulty": "high",
                        "expected_output": "structured_data",
                    },
                },
                outputs=None,
                error=None,
                start_time=None,
                end_time=None,
                duration=2500.0,
                metadata={
                    "experiment_id": "exp-123",
                    "user_id": "user-456",
                    "session_context": {
                        "conversation_id": "conv-789",
                        "turn_number": 5,
                        "previous_events": ["event-1", "event-2"],
                    },
                },
                feedback=None,
                metrics=None,
                user_properties=None,
            )

            # Verify the complex structure is valid
            assert event_request.config["nested"]["function_calling"]["enabled"] is True
            assert event_request.config["nested"]["safety"]["content_filter"] == "high"
            assert (
                event_request.inputs["metadata"]["task_type"]
                == "information_extraction"
            )
            assert event_request.metadata["session_context"]["turn_number"] == 5

            # Test serialization
            serialized = event_request.model_dump(exclude_none=True)
            assert serialized["config"]["nested"]["function_calling"]["enabled"] is True
            assert serialized["config"]["nested"]["safety"]["content_filter"] == "high"
            assert (
                serialized["inputs"]["metadata"]["task_type"]
                == "information_extraction"
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex CreateEventRequest: {e}")

    def test_create_datapoint_request_with_nested_history(self):
        """Test creating CreateDatapointRequest with complex conversation history."""
        try:
            # Create complex conversation history
            conversation_history = [
                {
                    "role": "user",
                    "content": "What is the weather like today?",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "metadata": {"user_id": "user-123", "session_id": "sess-456"},
                },
                {
                    "role": "assistant",
                    "content": "I don't have access to real-time weather data.",
                    "timestamp": "2024-01-15T10:00:01Z",
                    "metadata": {"model": "gpt-4", "confidence": 0.95},
                },
                {
                    "role": "user",
                    "content": "Can you help me find a weather API?",
                    "timestamp": "2024-01-15T10:00:02Z",
                    "metadata": {"user_id": "user-123", "session_id": "sess-456"},
                },
            ]

            # Create complex ground truth
            ground_truth = {
                "expected_response": "Provide information about weather APIs",
                "quality_score": 0.9,
                "evaluation_criteria": {
                    "relevance": 0.95,
                    "helpfulness": 0.88,
                    "accuracy": 0.92,
                },
            }

            datapoint_request = CreateDatapointRequest(
                project="test-project",
                inputs={
                    "user_query": "What is the weather like today?",
                    "context": "User is asking about weather information",
                    "user_preferences": {
                        "location": "San Francisco",
                        "units": "fahrenheit",
                        "detailed": True,
                    },
                },
                history=conversation_history,
                ground_truth=ground_truth,
                metadata={
                    "dataset_version": "v2.1",
                    "collection_date": "2024-01-15",
                    "annotator": "expert-1",
                    "quality_metrics": {
                        "inter_annotator_agreement": 0.87,
                        "confidence": 0.92,
                    },
                },
            )

            # Verify complex nested structures
            assert len(datapoint_request.history) == 3
            assert datapoint_request.history[0]["role"] == "user"
            assert (
                datapoint_request.ground_truth["evaluation_criteria"]["relevance"]
                == 0.95
            )
            assert (
                datapoint_request.inputs["user_preferences"]["location"]
                == "San Francisco"
            )

            # Test serialization
            serialized = datapoint_request.model_dump(exclude_none=True)
            assert len(serialized["history"]) == 3
            assert serialized["history"][0]["role"] == "user"
            assert (
                serialized["ground_truth"]["evaluation_criteria"]["relevance"] == 0.95
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex CreateDatapointRequest: {e}")

    def test_post_configuration_request_with_nested_parameters(self):
        """Test creating PostConfigurationRequest with complex nested parameters."""
        try:
            from honeyhive.models.generated import (
                CallType,
                EnvEnum,
                FunctionCallParams,
                Parameters2,
                SelectedFunction,
            )

            # Create complex function parameters
            selected_functions = [
                SelectedFunction(
                    id="func-1",
                    name="extract_entities",
                    description="Extract named entities from text",
                    parameters={
                        "entity_types": ["person", "organization", "location"],
                        "confidence_threshold": 0.8,
                        "include_metadata": True,
                    },
                ),
                SelectedFunction(
                    id="func-2",
                    name="classify_sentiment",
                    description="Classify text sentiment",
                    parameters={
                        "scale": "1-5",
                        "include_confidence": True,
                        "neutral_threshold": 0.1,
                    },
                ),
            ]

            # Create complex hyperparameters
            hyperparameters = {
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
                "advanced": {
                    "beam_search": {
                        "enabled": True,
                        "beam_size": 5,
                        "length_penalty": 1.0,
                    },
                    "sampling": {
                        "nucleus_sampling": True,
                        "top_k": 40,
                        "repetition_penalty": 1.1,
                    },
                },
            }

            config_request = PostConfigurationRequest(
                project="test-project",
                name="complex-llm-config",
                provider="openai",
                parameters=Parameters2(
                    call_type=CallType.chat,
                    model="gpt-4",
                    hyperparameters=hyperparameters,
                    responseFormat={"type": "json_object"},
                    selectedFunctions=selected_functions,
                    functionCallParams=FunctionCallParams.auto,
                    forceFunction={
                        "name": "extract_entities",
                        "parameters": {"entity_types": ["person", "organization"]},
                    },
                ),
                env=[EnvEnum.prod, EnvEnum.staging],
                user_properties={
                    "team": "AI-Research",
                    "project_lead": "Dr. Smith",
                    "budget_code": "AI-2024-001",
                    "approval_status": "approved",
                },
            )

            # Verify complex nested structures
            assert config_request.parameters.call_type == CallType.chat
            assert config_request.parameters.model == "gpt-4"
            assert (
                config_request.parameters.hyperparameters["advanced"]["beam_search"][
                    "enabled"
                ]
                is True
            )
            assert len(config_request.parameters.selectedFunctions) == 2
            assert (
                config_request.parameters.selectedFunctions[0].name
                == "extract_entities"
            )
            assert EnvEnum.prod in config_request.env
            assert config_request.user_properties["team"] == "AI-Research"

            # Test serialization
            serialized = config_request.model_dump(exclude_none=True)
            assert (
                serialized["parameters"]["hyperparameters"]["advanced"]["beam_search"][
                    "enabled"
                ]
                is True
            )
            assert (
                serialized["parameters"]["selectedFunctions"][0]["name"]
                == "extract_entities"
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex PostConfigurationRequest: {e}")

    def test_create_run_request_with_complex_evaluation_config(self):
        """Test creating CreateRunRequest with complex evaluation configuration."""
        try:
            pass

            from honeyhive.models.generated import UUIDType

            # Create complex evaluation configuration
            evaluation_config = {
                "metrics": {
                    "accuracy": {"threshold": 0.8, "weight": 0.4},
                    "precision": {"threshold": 0.75, "weight": 0.3},
                    "recall": {"threshold": 0.7, "weight": 0.3},
                },
                "evaluation_settings": {
                    "batch_size": 100,
                    "parallel_processing": True,
                    "timeout_seconds": 300,
                    "retry_attempts": 3,
                },
                "output_format": {
                    "include_predictions": True,
                    "include_confidence_scores": True,
                    "include_explanations": True,
                    "export_formats": ["json", "csv", "excel"],
                },
            }

            run_request = CreateRunRequest(
                project="test-project",
                name="complex-evaluation-run",
                event_ids=[
                    UUIDType("event-1"),
                    UUIDType("event-2"),
                    UUIDType("event-3"),
                ],
                dataset_id="dataset-123",
                datapoint_ids=["dp-1", "dp-2", "dp-3"],
                configuration=evaluation_config,
                metadata={
                    "evaluation_type": "comprehensive_llm_assessment",
                    "evaluator": "expert-team",
                    "benchmark": "industry-standard",
                    "quality_metrics": {
                        "inter_evaluator_reliability": 0.89,
                        "test_retest_reliability": 0.92,
                        "content_validity": 0.94,
                    },
                },
            )

            # Verify complex nested structures
            assert run_request.configuration["metrics"]["accuracy"]["threshold"] == 0.8
            assert (
                run_request.configuration["evaluation_settings"]["parallel_processing"]
                is True
            )
            assert (
                "json" in run_request.configuration["output_format"]["export_formats"]
            )
            assert (
                run_request.metadata["quality_metrics"]["inter_evaluator_reliability"]
                == 0.89
            )

            # Test serialization
            serialized = run_request.model_dump(exclude_none=True)
            assert (
                serialized["configuration"]["metrics"]["accuracy"]["threshold"] == 0.8
            )
            assert (
                serialized["configuration"]["evaluation_settings"][
                    "parallel_processing"
                ]
                is True
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex CreateRunRequest: {e}")

    def test_update_tool_request_with_complex_changes(self):
        """Test creating UpdateToolRequest with complex nested changes."""
        try:
            from honeyhive.models import UpdateToolRequest

            update_request = UpdateToolRequest(
                id="tool-123",
                name="updated-complex-tool",
                description="Enhanced text processing tool with new capabilities",
                parameters={
                    "new_capabilities": {
                        "sentiment_analysis": True,
                        "entity_recognition": True,
                        "text_summarization": True,
                    },
                    "enhanced_parameters": {
                        "input_schema": {
                            "additional_fields": ["context", "user_preferences"],
                            "validation_rules": ["non_empty", "max_length_check"],
                        }
                    },
                },
            )

            # Verify complex nested structures
            assert (
                update_request.parameters["new_capabilities"]["sentiment_analysis"]
                is True
            )
            assert (
                update_request.parameters["new_capabilities"]["entity_recognition"]
                is True
            )
            assert (
                "context"
                in update_request.parameters["enhanced_parameters"]["input_schema"][
                    "additional_fields"
                ]
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert (
                serialized["parameters"]["new_capabilities"]["sentiment_analysis"]
                is True
            )
            assert serialized["parameters"]["enhanced_parameters"]["input_schema"][
                "additional_fields"
            ] == ["context", "user_preferences"]

        except Exception as e:
            pytest.fail(f"Failed to create complex UpdateToolRequest: {e}")

    def test_update_datapoint_request_with_complex_changes(self):
        """Test creating UpdateDatapointRequest with complex nested changes."""
        try:
            from honeyhive.models import UpdateDatapointRequest

            update_request = UpdateDatapointRequest(
                field_id="datapoint-123",
                inputs={
                    "updated_query": "What is the weather like in Paris?",
                    "enhanced_context": "User is planning a trip to Paris",
                    "user_preferences": {
                        "location": "Paris, France",
                        "units": "celsius",
                        "detailed": True,
                        "include_forecast": True,
                    },
                },
                metadata={
                    "last_updated": "2024-01-25",
                    "update_reason": "Enhanced user preferences and context",
                    "quality_improvements": {
                        "additional_annotations": True,
                        "cross_references": ["dp-456", "dp-789"],
                        "validation_status": "reviewed",
                    },
                },
            )

            # Verify complex nested structures
            assert (
                update_request.inputs["user_preferences"]["location"] == "Paris, France"
            )
            assert update_request.inputs["user_preferences"]["include_forecast"] is True
            assert (
                update_request.metadata["quality_improvements"]["validation_status"]
                == "reviewed"
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert (
                serialized["inputs"]["user_preferences"]["location"] == "Paris, France"
            )
            assert (
                serialized["metadata"]["quality_improvements"]["validation_status"]
                == "reviewed"
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex UpdateDatapointRequest: {e}")

    def test_event_filter_with_complex_queries(self):
        """Test EventFilter with complex query structures."""
        try:
            from honeyhive.models import EventFilter

            # Test complex filter scenarios
            complex_filters = [
                EventFilter(field="metadata.experiment_id", value="exp-123"),
                EventFilter(field="config.model", value="gpt-4"),
                EventFilter(
                    field="inputs.metadata.task_type", value="information_extraction"
                ),
                EventFilter(
                    field="metadata.session_context.conversation_id", value="conv-789"
                ),
            ]

            for event_filter in complex_filters:
                assert event_filter.field is not None
                assert event_filter.value is not None
                # Verify the filter can be used in API calls
                assert isinstance(event_filter.field, str)
                assert isinstance(event_filter.value, str)

            # Test serialization
            serialized_filters = [
                filter_obj.model_dump(exclude_none=True)
                for filter_obj in complex_filters
            ]
            assert len(serialized_filters) == 4
            assert serialized_filters[0]["field"] == "metadata.experiment_id"
            assert serialized_filters[0]["value"] == "exp-123"

        except Exception as e:
            pytest.fail(f"Failed to create complex EventFilter: {e}")

    def test_update_project_request_with_complex_changes(self):
        """Test creating UpdateProjectRequest with complex nested changes."""
        try:
            from honeyhive.models import UpdateProjectRequest

            update_request = UpdateProjectRequest(
                project_id="project-123",
                name="updated-complex-project",
                description="Enhanced project with new capabilities and metadata",
            )

            # Verify basic fields
            assert update_request.project_id == "project-123"
            assert update_request.name == "updated-complex-project"
            assert (
                update_request.description
                == "Enhanced project with new capabilities and metadata"
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert serialized["project_id"] == "project-123"
            assert serialized["name"] == "updated-complex-project"
            assert (
                serialized["description"]
                == "Enhanced project with new capabilities and metadata"
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex UpdateProjectRequest: {e}")

    def test_update_run_request_with_complex_changes(self):
        """Test creating UpdateRunRequest with complex nested changes."""
        try:
            from honeyhive.models import UpdateRunRequest

            update_request = UpdateRunRequest(
                name="updated-complex-evaluation",
                metadata={
                    "last_updated": "2024-01-25",
                    "update_reason": "Enhanced evaluation criteria and metrics",
                    "changes": {
                        "new_metrics": ["f1_score", "auc_roc"],
                        "updated_thresholds": {
                            "accuracy": 0.85,
                            "precision": 0.8,
                            "recall": 0.75,
                        },
                        "quality_improvements": {
                            "additional_evaluators": ["evaluator-3", "evaluator-4"],
                            "enhanced_guidelines": True,
                            "automated_validation": True,
                        },
                    },
                },
            )

            # Verify complex nested structures
            assert update_request.metadata["changes"]["new_metrics"] == [
                "f1_score",
                "auc_roc",
            ]
            assert (
                update_request.metadata["changes"]["updated_thresholds"]["accuracy"]
                == 0.85
            )
            assert (
                update_request.metadata["changes"]["quality_improvements"][
                    "enhanced_guidelines"
                ]
                is True
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert serialized["metadata"]["changes"]["new_metrics"] == [
                "f1_score",
                "auc_roc",
            ]
            assert (
                serialized["metadata"]["changes"]["updated_thresholds"]["accuracy"]
                == 0.85
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex UpdateRunRequest: {e}")

    def test_put_configuration_request_with_complex_changes(self):
        """Test creating PutConfigurationRequest with complex nested changes."""
        try:
            from honeyhive.models import PutConfigurationRequest
            from honeyhive.models.generated import (
                CallType,
                EnvEnum,
                Parameters1,
                Type6,
            )

            update_request = PutConfigurationRequest(
                project="test-project",
                name="updated-complex-config",
                provider="anthropic",
                parameters=Parameters1(
                    call_type=CallType.completion,
                    model="claude-3-sonnet",
                    hyperparameters={
                        "temperature": 0.8,
                        "max_tokens": 2000,
                        "advanced": {
                            "anthropic_specific": {
                                "system_prompt": "You are a helpful AI assistant",
                                "max_input_tokens": 100000,
                            }
                        },
                    },
                ),
                env=[EnvEnum.dev, EnvEnum.staging],
                type=Type6.LLM,
                user_properties={
                    "updated_by": "Dr. Johnson",
                    "update_date": "2024-01-25",
                    "change_log": [
                        "Switched from OpenAI to Anthropic",
                        "Updated model to Claude 3 Sonnet",
                        "Enhanced hyperparameter tuning",
                    ],
                },
            )

            # Verify complex nested structures
            assert update_request.provider == "anthropic"
            assert update_request.parameters.model == "claude-3-sonnet"
            assert (
                update_request.parameters.hyperparameters["advanced"][
                    "anthropic_specific"
                ]["system_prompt"]
                == "You are a helpful AI assistant"
            )
            assert update_request.type == Type6.LLM
            assert (
                "Switched from OpenAI to Anthropic"
                in update_request.user_properties["change_log"]
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert serialized["provider"] == "anthropic"
            assert serialized["parameters"]["model"] == "claude-3-sonnet"

        except Exception as e:
            pytest.fail(f"Failed to create complex PutConfigurationRequest: {e}")

    def test_validation_edge_cases(self):
        """Test validation edge cases and error handling."""
        try:
            from pydantic import ValidationError

            from honeyhive.models import CreateEventRequest
            from honeyhive.models.generated import EventType1

            # Test with invalid enum values
            with pytest.raises(ValidationError):
                invalid_event = CreateEventRequest(
                    project="test-project",
                    source="test",
                    event_name="test",
                    event_type="invalid_type",  # Invalid enum value
                    config={"test": True},
                    inputs={"test": "test"},
                    duration=100.0,
                )

            # Test with missing required fields
            with pytest.raises(ValidationError):
                invalid_event = CreateEventRequest(
                    project="test-project",
                    # Missing required fields: source, event_name, event_type, config, inputs, duration
                )

            # Test with invalid data types
            with pytest.raises(ValidationError):
                invalid_event = CreateEventRequest(
                    project="test-project",
                    source="test",
                    event_name="test",
                    event_type=EventType1.model,
                    config="not_a_dict",  # Should be dict
                    inputs={"test": "test"},
                    duration="not_a_number",  # Should be float
                )

            # Test that valid models pass validation
            valid_event = CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test",
                event_type=EventType1.model,
                config={"test": True},
                inputs={"test": "test"},
                duration=100.0,
            )
            assert valid_event.project == "test-project"
            assert valid_event.event_type == EventType1.model

        except Exception as e:
            pytest.fail(f"Failed to test validation edge cases: {e}")

    def test_create_dataset_request_with_complex_metadata(self):
        """Test creating CreateDatasetRequest with complex metadata structure."""
        try:
            from honeyhive.models import CreateDatasetRequest
            from honeyhive.models.generated import PipelineType, Type4

            dataset_request = CreateDatasetRequest(
                project="test-project",
                name="comprehensive-llm-evaluation-dataset",
                description="A comprehensive dataset for evaluating LLM performance across multiple domains",
                type=Type4.evaluation,
                pipeline_type=PipelineType.event,
                datapoints=["dp-1", "dp-2", "dp-3", "dp-4", "dp-5"],
                linked_evals=["eval-1", "eval-2"],
                metadata={
                    "version": "2.0.0",
                    "creation_date": "2024-01-15",
                    "curator": "expert-team",
                    "quality_assurance": {
                        "reviewed_by": ["reviewer-1", "reviewer-2", "reviewer-3"],
                        "review_date": "2024-01-20",
                        "quality_score": 0.96,
                        "coverage_metrics": {
                            "domains": [
                                "technology",
                                "healthcare",
                                "finance",
                                "education",
                            ],
                            "languages": ["english", "spanish", "french"],
                            "difficulty_levels": ["easy", "medium", "hard", "expert"],
                        },
                        "validation_process": {
                            "automated_checks": True,
                            "human_review": True,
                            "inter_annotator_agreement": 0.89,
                        },
                    },
                    "usage_guidelines": {
                        "intended_use": "LLM evaluation, benchmarking, and research",
                        "restrictions": "Research and development purposes only",
                        "citation": "HoneyHive Comprehensive Dataset v2.0",
                        "license": "MIT",
                    },
                },
            )

            # Verify complex nested structures
            assert dataset_request.type == Type4.evaluation
            assert dataset_request.pipeline_type == PipelineType.event
            assert (
                dataset_request.metadata["quality_assurance"]["quality_score"] == 0.96
            )
            assert (
                "technology"
                in dataset_request.metadata["quality_assurance"]["coverage_metrics"][
                    "domains"
                ]
            )
            assert (
                dataset_request.metadata["quality_assurance"]["validation_process"][
                    "automated_checks"
                ]
                is True
            )

            # Test serialization
            serialized = dataset_request.model_dump(exclude_none=True)
            assert serialized["metadata"]["quality_assurance"]["quality_score"] == 0.96
            assert (
                "technology"
                in serialized["metadata"]["quality_assurance"]["coverage_metrics"][
                    "domains"
                ]
            )

        except Exception as e:
            pytest.fail(f"Failed to create complex CreateDatasetRequest: {e}")

    def test_dataset_update_with_nested_changes(self):
        """Test creating DatasetUpdate with complex nested changes."""
        try:
            from honeyhive.models.generated import DatasetUpdate

            update_request = DatasetUpdate(
                dataset_id="dataset-123",
                name="updated-complex-dataset",
                description="Updated comprehensive dataset",
                metadata={
                    "last_updated": "2024-01-25",
                    "update_reason": "Added new domains and improved quality",
                    "changes": {
                        "added_domains": ["education", "environment"],
                        "removed_domains": ["outdated-tech"],
                        "quality_improvements": {
                            "new_annotators": ["annotator-3", "annotator-4"],
                            "improved_guidelines": True,
                            "validation_enhancements": [
                                "automated_checks",
                                "human_review",
                            ],
                        },
                    },
                },
            )

            # Verify complex nested structures
            assert update_request.dataset_id == "dataset-123"
            assert update_request.name == "updated-complex-dataset"
            assert "education" in update_request.metadata["changes"]["added_domains"]
            assert (
                update_request.metadata["changes"]["quality_improvements"][
                    "improved_guidelines"
                ]
                is True
            )
            assert (
                "automated_checks"
                in update_request.metadata["changes"]["quality_improvements"][
                    "validation_enhancements"
                ]
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert serialized["dataset_id"] == "dataset-123"
            assert "education" in serialized["metadata"]["changes"]["added_domains"]

        except Exception as e:
            pytest.fail(f"Failed to create complex DatasetUpdate: {e}")

    def test_metric_edit_with_complex_changes(self):
        """Test creating MetricEdit with complex nested changes."""
        try:
            from honeyhive.models.generated import MetricEdit

            update_request = MetricEdit(
                metric_id="metric-123",
                name="updated-comprehensive-metric",
                event_name="enhanced-llm-evaluation",
                criteria="Enhanced evaluation criteria with new dimensions and weights",
            )

            # Verify basic fields
            assert update_request.metric_id == "metric-123"
            assert update_request.name == "updated-comprehensive-metric"
            assert update_request.event_name == "enhanced-llm-evaluation"
            assert (
                update_request.criteria
                == "Enhanced evaluation criteria with new dimensions and weights"
            )

            # Test serialization
            serialized = update_request.model_dump(exclude_none=True)
            assert serialized["metric_id"] == "metric-123"
            assert serialized["name"] == "updated-comprehensive-metric"

        except Exception as e:
            pytest.fail(f"Failed to create complex MetricEdit: {e}")

    def test_update_run_response_parsing(self):
        """Test parsing UpdateRunResponse with complex data."""
        try:
            from honeyhive.models.generated import UpdateRunResponse

            response_data = {
                "evaluation": {
                    "run_id": "run-123",
                    "status": "completed",
                    "results": {
                        "accuracy": 0.87,
                        "precision": 0.82,
                        "recall": 0.79,
                        "f1_score": 0.80,
                    },
                    "metadata": {
                        "completion_time": "2024-01-25T15:30:00Z",
                        "evaluator": "expert-team",
                        "quality_score": 0.92,
                    },
                },
                "run_id": "run-123",
            }

            # Test that the response can be parsed
            response = UpdateRunResponse(**response_data)

            # Verify the response structure
            assert response.evaluation["run_id"] == "run-123"
            assert response.evaluation["status"] == "completed"
            assert response.evaluation["results"]["accuracy"] == 0.87
            assert response.evaluation["metadata"]["quality_score"] == 0.92

            # Test serialization
            serialized = response.model_dump(exclude_none=True)
            assert serialized["evaluation"]["results"]["accuracy"] == 0.87

        except Exception as e:
            pytest.fail(f"Failed to parse UpdateRunResponse: {e}")

    def test_create_run_response_parsing(self):
        """Test parsing CreateRunResponse with complex data."""
        try:
            from honeyhive.models.generated import CreateRunResponse, Status, UUIDType

            response_data = {
                "evaluation": {
                    "run_id": UUIDType("run-456"),
                    "status": Status.pending,
                    "created_at": "2024-01-25T10:00:00Z",
                    "configuration": {
                        "metrics": ["accuracy", "precision", "recall"],
                        "batch_size": 100,
                        "timeout": 300,
                    },
                },
                "run_id": UUIDType("run-456"),
            }

            # Test that the response can be parsed
            response = CreateRunResponse(**response_data)

            # Verify the response structure
            assert response.run_id == UUIDType("run-456")
            assert response.evaluation.run_id == UUIDType("run-456")
            assert response.evaluation.status == Status.pending
            assert "accuracy" in response.evaluation.configuration["metrics"]
            assert response.evaluation.configuration["batch_size"] == 100

            # Test that the model was created successfully
            assert response is not None
            assert hasattr(response, "run_id")
            assert hasattr(response, "evaluation")

        except Exception as e:
            pytest.fail(f"Failed to parse CreateRunResponse: {e}")

    def test_get_runs_response_parsing(self):
        """Test parsing GetRunsResponse with complex data."""
        try:
            from honeyhive.models.generated import GetRunsResponse, Status, UUIDType

            response_data = {
                "evaluations": [
                    {
                        "run_id": UUIDType("run-1"),
                        "status": Status.completed,
                        "name": "Evaluation Run 1",
                        "created_at": "2024-01-25T10:00:00Z",
                    },
                    {
                        "run_id": UUIDType("run-2"),
                        "status": Status.pending,
                        "name": "Evaluation Run 2",
                        "created_at": "2024-01-25T11:00:00Z",
                    },
                ]
            }

            # Test that the response can be parsed
            response = GetRunsResponse(**response_data)

            # Verify the response structure
            assert len(response.evaluations) == 2
            assert response.evaluations[0].run_id == UUIDType("run-1")
            assert response.evaluations[0].status == Status.completed
            assert response.evaluations[0].name == "Evaluation Run 1"
            assert response.evaluations[1].run_id == UUIDType("run-2")
            assert response.evaluations[1].status == Status.pending

            # Test that the model was created successfully
            assert response is not None
            assert hasattr(response, "evaluations")

        except Exception as e:
            pytest.fail(f"Failed to parse GetRunsResponse: {e}")

    def test_get_run_response_parsing(self):
        """Test parsing GetRunResponse with complex data."""
        try:
            from honeyhive.models.generated import GetRunResponse, Status, UUIDType

            response_data = {
                "evaluation": {
                    "run_id": UUIDType("run-789"),
                    "status": Status.completed,
                    "name": "Comprehensive LLM Evaluation",
                    "created_at": "2024-01-25T12:00:00Z",
                    "results": {
                        "overall_score": 0.87,
                        "metrics": {
                            "accuracy": 0.89,
                            "precision": 0.85,
                            "recall": 0.82,
                            "f1_score": 0.83,
                        },
                    },
                }
            }

            # Test that the response can be parsed
            response = GetRunResponse(**response_data)

            # Verify the response structure
            assert response.evaluation.run_id == UUIDType("run-789")
            assert response.evaluation.status == Status.completed
            assert response.evaluation.name == "Comprehensive LLM Evaluation"
            assert response.evaluation.results["overall_score"] == 0.87
            assert response.evaluation.results["metrics"]["accuracy"] == 0.89

            # Test that the model was created successfully
            assert response is not None
            assert hasattr(response, "evaluation")

        except Exception as e:
            pytest.fail(f"Failed to parse GetRunResponse: {e}")

    def test_delete_run_response_parsing(self):
        """Test parsing DeleteRunResponse with complex data."""
        try:
            from honeyhive.models.generated import DeleteRunResponse, UUIDType

            response_data = {"id": UUIDType("run-999"), "deleted": True}

            # Test that the response can be parsed
            response = DeleteRunResponse(**response_data)

            # Verify the response structure
            assert response.id == UUIDType("run-999")
            assert response.deleted is True

            # Test that the model was created successfully
            assert response is not None
            assert hasattr(response, "id")
            assert hasattr(response, "deleted")

        except Exception as e:
            pytest.fail(f"Failed to parse DeleteRunResponse: {e}")

    def test_uuid_type_methods_coverage(self):
        """Test UUIDType methods to achieve 100% coverage."""
        try:
            from honeyhive.models.generated import UUIDType

            # Test UUIDType instantiation and methods
            uuid_obj = UUIDType("test-uuid-123")

            # Test the root property (line 718)
            assert uuid_obj.root == "test-uuid-123"

            # Test the __str__ method (line 721)
            assert str(uuid_obj) == "test-uuid-123"

            # Test the __repr__ method
            assert repr(uuid_obj) == "UUIDType(test-uuid-123)"

        except Exception as e:
            pytest.fail(f"Failed to test UUIDType methods: {e}")
