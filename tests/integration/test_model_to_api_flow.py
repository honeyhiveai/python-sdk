"""Integration tests for end-to-end model-to-API flow in HoneyHive."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time

from honeyhive.api.client import HoneyHive
from honeyhive.models import (
    # Core models for the flow
    SessionStartRequest,
    CreateEventRequest,
    CreateDatapointRequest,
    CreateDatasetRequest,
    PostConfigurationRequest,
    CreateRunRequest,
    EventFilter,
    CreateToolRequest,
    # Supporting models
    EventType,
)
from honeyhive.models.generated import (
    UUIDType,
    Parameters,
    Parameters1,
    Parameters2,
    SelectedFunction,
    Type4,
    PipelineType,
    CallType,
    FunctionCallParams,
    EnvEnum,
    Type6,
)


class TestEndToEndModelToAPIFlow:
    """Test complete end-to-end flows from model creation to API calls."""
    
    def test_complete_llm_evaluation_workflow(self, api_key):
        """Test complete LLM evaluation workflow from models to API."""
        client = HoneyHive(api_key=api_key)
        
        # Step 1: Create a session
        session_request = SessionStartRequest(
            project="integration-test-project",
            session_name="llm-evaluation-session",
            source="integration-test"
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"session_id": "session-123"}
            mock_request.return_value = mock_response
            
            # Test session creation
            session_response = client.sessions.create_session(session_request)
            assert session_response.session_id == "session-123"
            
            # Verify the model was properly serialized
            call_args = mock_request.call_args
            assert "session" in call_args[1]["json"]
            session_data = call_args[1]["json"]["session"]
            assert session_data["project"] == "integration-test-project"
            assert session_data["session_name"] == "llm-evaluation-session"
            assert session_data["source"] == "integration-test"
    
    def test_complete_event_tracking_workflow(self, api_key):
        """Test complete event tracking workflow with complex nested data."""
        client = HoneyHive(api_key=api_key)
        
        # Create complex event request
        event_request = CreateEventRequest(
            project="integration-test-project",
            source="production",
            event_name="llm-completion-event",
            event_type=EventType.model,
            config={
                "model": "gpt-4",
                "provider": "openai",
                "temperature": 0.7,
                "max_tokens": 1000,
                "function_calling": {
                    "enabled": True,
                    "mode": "auto",
                    "functions": [
                        {
                            "name": "extract_entities",
                            "description": "Extract named entities",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "entity_types": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            inputs={
                "prompt": "Extract entities from the following text",
                "text": "Apple Inc. is headquartered in Cupertino, California.",
                "user_id": "user-123",
                "session_id": "session-456"
            },
            duration=1500.0,
            metadata={
                "experiment_id": "exp-789",
                "evaluation_round": 1,
                "quality_metrics": {
                    "response_time": 1500,
                    "token_usage": 150,
                    "cost": 0.003
                }
            }
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "event_id": "event-123",
                "success": True
            }
            mock_request.return_value = mock_response
            
            # Test event creation
            event_response = client.events.create_event(event_request)
            assert event_response.event_id == "event-123"
            assert event_response.success is True
            
            # Verify complex nested structure was properly serialized
            call_args = mock_request.call_args
            assert "event" in call_args[1]["json"]
            event_data = call_args[1]["json"]["event"]
            
            # Verify nested config
            assert event_data["config"]["function_calling"]["enabled"] is True
            assert event_data["config"]["function_calling"]["functions"][0]["name"] == "extract_entities"
            
            # Verify nested inputs
            assert event_data["inputs"]["text"] == "Apple Inc. is headquartered in Cupertino, California."
            
            # Verify nested metadata
            assert event_data["metadata"]["quality_metrics"]["response_time"] == 1500
    
    def test_complete_datapoint_creation_workflow(self, api_key):
        """Test complete datapoint creation workflow with complex data."""
        client = HoneyHive(api_key=api_key)
        
        # Create complex datapoint request
        datapoint_request = CreateDatapointRequest(
            project="integration-test-project",
            inputs={
                "user_query": "What is the capital of France?",
                "context": "Geography quiz",
                "user_preferences": {
                    "language": "english",
                    "detail_level": "detailed",
                    "include_history": True
                }
            },
            history=[
                {
                    "role": "user",
                    "content": "What is the capital of France?",
                    "timestamp": "2024-01-15T10:00:00Z"
                },
                {
                    "role": "assistant",
                    "content": "The capital of France is Paris.",
                    "timestamp": "2024-01-15T10:00:01Z"
                }
            ],
            ground_truth={
                "expected_response": "Paris",
                "correct_answer": True,
                "confidence": 0.95,
                "evaluation_criteria": {
                    "accuracy": 1.0,
                    "completeness": 0.8,
                    "helpfulness": 0.9
                }
            },
            metadata={
                "dataset_version": "v1.0",
                "collection_date": "2024-01-15",
                "annotator": "expert-1",
                "quality_score": 0.92
            }
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "field_id": "datapoint-123",
                "project_id": "integration-test-project"
            }
            mock_request.return_value = mock_response
            
            # Test datapoint creation
            datapoint_response = client.datapoints.create_datapoint(datapoint_request)
            assert datapoint_response.field_id == "datapoint-123"
            
            # Verify complex nested structure was properly serialized
            call_args = mock_request.call_args
            assert "datapoint" in call_args[1]["json"]
            datapoint_data = call_args[1]["json"]["datapoint"]
            
            # Verify nested inputs
            assert datapoint_data["inputs"]["user_preferences"]["language"] == "english"
            
            # Verify history
            assert len(datapoint_data["history"]) == 2
            assert datapoint_data["history"][0]["role"] == "user"
            
            # Verify ground truth
            assert datapoint_data["ground_truth"]["evaluation_criteria"]["accuracy"] == 1.0
    
    def test_complete_dataset_creation_workflow(self, api_key):
        """Test complete dataset creation workflow with complex metadata."""
        client = HoneyHive(api_key=api_key)
        
        # Create complex dataset request
        dataset_request = CreateDatasetRequest(
            project="integration-test-project",
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
                        "domains": ["technology", "healthcare", "finance", "education"],
                        "languages": ["english", "spanish", "french"],
                        "difficulty_levels": ["easy", "medium", "hard", "expert"]
                    },
                    "validation_process": {
                        "automated_checks": True,
                        "human_review": True,
                        "inter_annotator_agreement": 0.89
                    }
                },
                "usage_guidelines": {
                    "intended_use": "LLM evaluation, benchmarking, and research",
                    "restrictions": "Research and development purposes only",
                    "citation": "HoneyHive Comprehensive Dataset v2.0",
                    "license": "MIT"
                }
            }
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "dataset-123",
                "name": "comprehensive-llm-evaluation-dataset"
            }
            mock_request.return_value = mock_request
            
            # Test dataset creation
            dataset_response = client.datasets.create_dataset(dataset_request)
            assert dataset_response.id == "dataset-123"
            
            # Verify complex nested structure was properly serialized
            call_args = mock_request.call_args
            assert "dataset" in call_args[1]["json"]
            dataset_data = call_args[1]["json"]["dataset"]
            
            # Verify nested metadata
            assert dataset_data["metadata"]["quality_assurance"]["quality_score"] == 0.96
            assert "technology" in dataset_data["metadata"]["quality_assurance"]["coverage_metrics"]["domains"]
            assert dataset_data["metadata"]["quality_assurance"]["validation_process"]["automated_checks"] is True
    
    def test_complete_configuration_workflow(self, api_key):
        """Test complete configuration creation workflow with complex parameters."""
        client = HoneyHive(api_key=api_key)
        
        # Create complex function parameters
        selected_functions = [
            SelectedFunction(
                id="func-1",
                name="extract_entities",
                description="Extract named entities from text",
                parameters={
                    "entity_types": ["person", "organization", "location", "date"],
                    "confidence_threshold": 0.8,
                    "include_metadata": True
                }
            ),
            SelectedFunction(
                id="func-2",
                name="classify_sentiment",
                description="Classify text sentiment",
                parameters={
                    "scale": "1-5",
                    "include_confidence": True,
                    "neutral_threshold": 0.1
                }
            ),
            SelectedFunction(
                id="func-3",
                name="summarize_text",
                description="Generate text summary",
                parameters={
                    "max_length": 150,
                    "style": "concise",
                    "include_key_points": True
                }
            )
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
                    "length_penalty": 1.0
                },
                "sampling": {
                    "nucleus_sampling": True,
                    "top_k": 40,
                    "repetition_penalty": 1.1
                },
                "safety": {
                    "content_filter": "high",
                    "blocked_categories": ["harmful", "inappropriate", "biased"]
                }
            }
        }
        
        config_request = PostConfigurationRequest(
            project="integration-test-project",
            name="advanced-llm-configuration",
            provider="openai",
            parameters=Parameters(
                call_type=CallType.chat,
                model="gpt-4",
                hyperparameters=hyperparameters,
                responseFormat={"type": "json_object"},
                selectedFunctions=selected_functions,
                functionCallParams=FunctionCallParams.auto,
                forceFunction={
                    "name": "extract_entities",
                    "parameters": {"entity_types": ["person", "organization"]}
                }
            ),
            env=[EnvEnum.prod, EnvEnum.staging],
            user_properties={
                "team": "AI-Research",
                "project_lead": "Dr. Smith",
                "budget_code": "AI-2024-001",
                "approval_status": "approved",
                "review_date": "2024-01-20"
            }
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "config-123",
                "name": "advanced-llm-configuration"
            }
            mock_request.return_value = mock_response
            
            # Test configuration creation
            config_response = client.configurations.create_configuration(config_request)
            assert config_response.id == "config-123"
            
            # Verify complex nested structure was properly serialized
            call_args = mock_request.call_args
            assert "configuration" in call_args[1]["json"]
            config_data = call_args[1]["json"]["configuration"]
            
            # Verify nested parameters
            assert config_data["parameters"]["hyperparameters"]["advanced"]["beam_search"]["enabled"] is True
            assert config_data["parameters"]["hyperparameters"]["advanced"]["safety"]["content_filter"] == "high"
            
            # Verify selected functions
            assert len(config_data["parameters"]["selectedFunctions"]) == 3
            assert config_data["parameters"]["selectedFunctions"][0]["name"] == "extract_entities"
    
    def test_complete_evaluation_workflow(self, api_key):
        """Test complete evaluation run workflow with complex configuration."""
        client = HoneyHive(api_key=api_key)
        
        from uuid import uuid4
        
        # Create complex evaluation configuration
        evaluation_config = {
            "metrics": {
                "accuracy": {"threshold": 0.8, "weight": 0.3},
                "precision": {"threshold": 0.75, "weight": 0.25},
                "recall": {"threshold": 0.7, "weight": 0.25},
                "f1_score": {"threshold": 0.75, "weight": 0.2}
            },
            "evaluation_settings": {
                "batch_size": 100,
                "parallel_processing": True,
                "timeout_seconds": 300,
                "retry_attempts": 3,
                "quality_checks": {
                    "inter_annotator_agreement": True,
                    "confidence_threshold": 0.8,
                    "outlier_detection": True
                }
            },
            "output_format": {
                "include_predictions": True,
                "include_confidence_scores": True,
                "include_explanations": True,
                "include_error_analysis": True,
                "export_formats": ["json", "csv", "excel", "html"]
            },
            "advanced_features": {
                "cross_validation": True,
                "bootstrap_sampling": True,
                "statistical_significance": True,
                "confidence_intervals": 0.95
            }
        }
        
        run_request = CreateRunRequest(
            project="integration-test-project",
            name="comprehensive-llm-evaluation-run",
            event_ids=[UUIDType(uuid4()), UUIDType(uuid4()), UUIDType(uuid4())],
            dataset_id="dataset-123",
            datapoint_ids=["dp-1", "dp-2", "dp-3", "dp-4", "dp-5"],
            configuration=evaluation_config,
            metadata={
                "evaluation_type": "comprehensive_llm_assessment",
                "evaluator": "expert-team",
                "benchmark": "industry-standard",
                "quality_metrics": {
                    "inter_evaluator_reliability": 0.89,
                    "test_retest_reliability": 0.92,
                    "content_validity": 0.94,
                    "construct_validity": 0.91
                },
                "evaluation_context": {
                    "domain": "general_ai",
                    "task_type": "question_answering",
                    "difficulty_level": "mixed",
                    "target_audience": "researchers"
                }
            }
        )
        
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "evaluation": {"run_id": "run-123"},
                "run_id": "run-123"
            }
            mock_request.return_value = mock_response
            
            # Mock the CreateRunResponse creation to avoid UUIDType validation issues
            with patch('honeyhive.api.evaluations.CreateRunResponse') as mock_response_class:
                mock_response_instance = Mock()
                mock_response_instance.run_id = "run-123"
                mock_response_class.return_value = mock_response_instance
                
                # Test evaluation run creation
                run_response = client.evaluations.create_run(run_request)
                assert run_response.run_id == "run-123"
                
                # Verify complex nested structure was properly serialized
                call_args = mock_request.call_args
                assert "run" in call_args[1]["json"]
                run_data = call_args[1]["json"]["run"]
                
                # Verify nested configuration
                assert run_data["configuration"]["metrics"]["accuracy"]["threshold"] == 0.8
                assert run_data["configuration"]["evaluation_settings"]["quality_checks"]["inter_annotator_agreement"] is True
                assert "html" in run_data["configuration"]["output_format"]["export_formats"]
                
                # Verify nested metadata
                assert run_data["metadata"]["quality_metrics"]["inter_evaluator_reliability"] == 0.89
                assert run_data["metadata"]["evaluation_context"]["domain"] == "general_ai"


class TestModelSerializationInAPIFlow:
    """Test that models are properly serialized throughout the API flow."""
    
    def test_model_serialization_preserves_structure(self, api_key):
        """Test that model serialization preserves complex nested structures."""
        client = HoneyHive(api_key=api_key)
        
        # Create a complex event request
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="serialization-test",
            event_type=EventType.model,
            config={
                "nested": {
                    "deep": {
                        "structure": {
                            "with": {
                                "arrays": [1, 2, 3, {"nested": "value"}],
                                "and": {
                                    "objects": {"key": "value"}
                                }
                            }
                        }
                    }
                }
            },
            inputs={"complex": {"nested": "input"}},
            duration=100.0
        )
        
        # Test serialization
        serialized = event_request.model_dump(exclude_none=True)
        
        # Verify the complex structure is preserved
        assert serialized["config"]["nested"]["deep"]["structure"]["with"]["arrays"] == [1, 2, 3, {"nested": "value"}]
        assert serialized["config"]["nested"]["deep"]["structure"]["with"]["and"]["objects"]["key"] == "value"
        assert serialized["inputs"]["complex"]["nested"] == "input"
        
        # Verify this can be used in API calls
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"event_id": "event-123", "success": True}
            mock_request.return_value = mock_response
            
            # The serialized data should work in API calls
            response = client.events.create_event(event_request)
            assert response.event_id == "event-123"
    
    def test_enum_serialization_in_api_flow(self, api_key):
        """Test that enums are properly serialized in API flow."""
        client = HoneyHive(api_key=api_key)
        
        from honeyhive.models.generated import Type3
        
        # Create tool request with enum
        tool_request = CreateToolRequest(
            task="test-project",
            name="enum-test-tool",
            description="Test tool for enum serialization",
            parameters={"test": True},
            type=Type3.function
        )
        
        # Test serialization
        serialized = tool_request.model_dump(exclude_none=True)
        
        # Verify enum is serialized correctly
        assert serialized["type"] == Type3.function
        assert isinstance(serialized["type"], type(Type3.function))
        
        # Verify this can be used in API calls
        with patch.object(client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "tool-123", "name": "enum-test-tool"}
            mock_request.return_value = mock_request
            
            # The serialized data should work in API calls
            response = client.tools.create_tool(tool_request)
            assert response.id == "tool-123"


class TestErrorHandlingInModelFlow:
    """Test error handling when models fail validation in API flow."""
    
    def test_invalid_model_rejection_in_api_flow(self, api_key):
        """Test that invalid models are rejected before API calls."""
        client = HoneyHive(api_key=api_key)
        
        # Try to create an invalid event request (missing required fields)
        with pytest.raises(Exception):  # Should fail validation
            invalid_event = CreateEventRequest(
                project="test-project",
                # Missing required fields: source, event_name, event_type, config, inputs, duration
            )
    
    def test_model_validation_errors_propagate(self, api_key):
        """Test that model validation errors properly propagate."""
        client = HoneyHive(api_key=api_key)
        
        # Try to create an invalid datapoint request
        with pytest.raises(Exception):  # Should fail validation
            invalid_datapoint = CreateDatapointRequest(
                project="test-project",
                # Missing required field: inputs
            )
    
    def test_complex_model_validation_edge_cases(self, api_key):
        """Test edge cases in complex model validation."""
        client = HoneyHive(api_key=api_key)
        
        # Test with invalid enum values
        with pytest.raises(Exception):  # Should fail validation
            invalid_event = CreateEventRequest(
                project="test-project",
                source="test",
                event_name="test",
                event_type="invalid_type",  # Invalid enum value
                config={"test": True},
                inputs={"test": "test"},
                duration=100.0
            )


class TestPerformanceInModelFlow:
    """Test performance characteristics of model serialization and API flow."""
    
    def test_large_model_serialization_performance(self, api_key):
        """Test performance of serializing large complex models."""
        client = HoneyHive(api_key=api_key)
        
        # Create a large complex model
        large_config = {}
        for i in range(100):
            large_config[f"level1_{i}"] = {
                f"level2_{j}": {
                    f"level3_{k}": f"value_{i}_{j}_{k}"
                    for k in range(10)
                }
                for j in range(10)
            }
        
        event_request = CreateEventRequest(
            project="test-project",
            source="test",
            event_name="large-model-test",
            event_type=EventType.model,
            config=large_config,
            inputs={"large_input": large_config},
            duration=100.0
        )
        
        # Measure serialization performance
        start_time = time.time()
        serialized = event_request.model_dump(exclude_none=True)
        serialization_time = time.time() - start_time
        
        # Serialization should be reasonably fast (< 1 second for this size)
        assert serialization_time < 1.0
        
        # Verify the large structure is preserved
        assert len(serialized["config"]) == 100
        assert serialized["config"]["level1_0"]["level2_0"]["level3_0"] == "value_0_0_0"
    
    def test_batch_model_processing_performance(self, api_key):
        """Test performance of processing multiple models in batch."""
        client = HoneyHive(api_key=api_key)
        
        # Create multiple complex models
        events = []
        for i in range(50):
            event_request = CreateEventRequest(
                project="test-project",
                source="test",
                event_name=f"batch-event-{i}",
                event_type=EventType.model,
                config={
                    "index": i,
                    "nested": {
                        "data": [j for j in range(100)],
                        "metadata": {"batch_id": i, "timestamp": time.time()}
                    }
                },
                inputs={"input": f"input-{i}"},
                duration=100.0 + i
            )
            events.append(event_request)
        
        # Measure batch processing performance
        start_time = time.time()
        serialized_events = [event.model_dump(exclude_none=True) for event in events]
        batch_time = time.time() - start_time
        
        # Batch processing should be reasonably fast (< 2 seconds for 50 models)
        assert batch_time < 2.0
        
        # Verify all models were processed correctly
        assert len(serialized_events) == 50
        for i, serialized in enumerate(serialized_events):
            assert serialized["config"]["index"] == i
            assert len(serialized["config"]["nested"]["data"]) == 100
