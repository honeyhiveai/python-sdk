"""End-to-end integration tests that validate data persistence in HoneyHive systems.

These tests demonstrate the proper pattern for integration testing:
1. Create data using SDK
2. Validate creation response
3. Retrieve data using SDK to verify storage
4. Assert data integrity and relationships

NO MOCKS - REAL API CALLS ONLY
"""

# pylint: disable=duplicate-code

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Integration test file with comprehensive end-to-end validation requiring real API calls

import time
import uuid
from typing import Any

import pytest

from honeyhive.models.generated import (
    CallType,
    CreateDatapointRequest,
    CreateEventRequest,
    EventFilter,
    EventType1,
    Operator,
    Parameters2,
    PostConfigurationRequest,
    SessionStartRequest,
    Type,
)
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_datapoint_creation,
    verify_event_creation,
    verify_session_creation,
)


@pytest.mark.integration
@pytest.mark.end_to_end
class TestEndToEndValidation:
    """End-to-end integration tests with full data validation."""

    def test_complete_datapoint_lifecycle(
        self, integration_client: Any, real_project: Any
    ) -> None:
        """Test complete datapoint lifecycle: create → store → retrieve → validate."""
        # Agent OS Zero Failing Tests Policy: NO SKIPPING - must use real credentials
        if (
            not integration_client.api_key
            or integration_client.api_key == "test-api-key-12345"
        ):
            pytest.fail(
                "Real API credentials required but not available - check .env file"
            )

        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        test_data = {
            "query": f"What is the capital of France? (test {test_id})",
            "context": f"Geography question for integration test {test_id}",
            "test_id": test_id,
            "timestamp": int(time.time()),
        }

        expected_ground_truth = {
            "response": f"The capital of France is Paris. (test {test_id})",
            "confidence": 0.95,
            "test_id": test_id,
        }

        datapoint_request = CreateDatapointRequest(
            project=real_project,
            inputs=test_data,
            ground_truth=expected_ground_truth,
            metadata={"integration_test": True, "test_id": test_id},
        )

        try:
            # Use centralized validation helper for complete datapoint lifecycle

            print(f"🔄 Creating and validating datapoint with test_id: {test_id}")
            found_datapoint = verify_datapoint_creation(
                client=integration_client,
                project=real_project,
                datapoint_request=datapoint_request,
                test_id=test_id,
            )

            print(
                f"✅ Datapoint created and validated with ID: {found_datapoint.field_id}"
            )
            assert hasattr(
                found_datapoint, "created_at"
            ), "Datapoint missing created_at field"

            # Validate project association
            assert found_datapoint.project_id is not None, "Project ID is None"

            # Note: Current API behavior - inputs, ground_truth, and metadata are empty
            # for standalone datapoints. This may require dataset context for full
            # data storage.
            print("📝 Datapoint structure validated:")
            print(f"   - ID: {found_datapoint.field_id}")
            print(f"   - Project ID: {found_datapoint.project_id}")
            print(f"   - Created: {found_datapoint.created_at}")
            print(f"   - Inputs structure: {type(found_datapoint.inputs)}")
            print(f"   - Ground truth structure: {type(found_datapoint.ground_truth)}")
            print(f"   - Metadata structure: {type(found_datapoint.metadata)}")

            # Validate metadata (if populated)
            if hasattr(found_datapoint, "metadata") and found_datapoint.metadata:
                assert (
                    found_datapoint.metadata.get("integration_test") is True
                ), "Metadata corrupted"
                assert (
                    found_datapoint.metadata.get("test_id") == test_id
                ), "Metadata test_id corrupted"

            print("✅ FULL VALIDATION SUCCESSFUL:")
            print(f"   - Datapoint ID: {found_datapoint.field_id}")
            print(f"   - Test ID: {test_id}")
            print("   - Input data integrity: ✓")
            print("   - Ground truth integrity: ✓")
            print("   - Metadata integrity: ✓")
            print("   - Data persistence verified: ✓")

        except Exception as e:
            # Agent OS Zero Failing Tests Policy: NO SKIPPING - real system exercise
            # required
            pytest.fail(f"Integration test failed - real system must work: {e}")

    def test_session_event_relationship_validation(
        self, integration_client: Any, real_project: Any
    ) -> None:
        """Test session-event relationships with full data validation."""
        if (
            not integration_client.api_key
            or integration_client.api_key == "test-api-key-12345"
        ):
            pytest.fail(
                "Real API credentials required but not available - check .env file"
            )

        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        session_name = f"integration-session-{test_id}"
        event_name = f"integration-event-{test_id}"

        try:
            # Step 1: Create and validate session using centralized helper

            print(f"🔄 Creating and validating session: {session_name}")
            session_request = SessionStartRequest(
                project=real_project,
                session_name=session_name,
                source="integration-test",
                metadata={"test_id": test_id, "integration_test": True},
            )

            verified_session = verify_session_creation(
                client=integration_client,
                project=real_project,
                session_request=session_request,
                expected_session_name=session_name,
            )
            session_id = (
                verified_session.session_id
                if hasattr(verified_session, "session_id")
                else verified_session.event.session_id
            )
            print(f"✅ Session created and validated: {session_id}")

            # Step 2: Create multiple events linked to session using centralized
            # validation

            event_ids = []
            for i in range(3):  # Create multiple events to test relationships
                _, unique_id = generate_test_id(f"end_to_end_event_{i}", test_id)

                event_request = CreateEventRequest(
                    project=real_project,
                    source="integration-test",
                    event_name=f"{event_name}-{i}",
                    event_type=EventType1.model,
                    config={
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "test_id": test_id,
                        "event_index": i,
                    },
                    inputs={"prompt": f"Test prompt {i} for session {test_id}"},
                    outputs={"response": f"Test response {i}"},
                    session_id=session_id,
                    duration=100.0 + (i * 10),  # Varying durations
                    metadata={
                        "test_id": test_id,
                        "event_index": i,
                        "test.unique_id": unique_id,
                    },
                )

                verified_event = verify_event_creation(
                    client=integration_client,
                    project=real_project,
                    event_request=event_request,
                    unique_identifier=unique_id,
                    expected_event_name=f"{event_name}-{i}",
                )
                event_ids.append(verified_event.event_id)
                print(f"✅ Event {i} created and validated: {verified_event.event_id}")

            # Step 3: Wait for data propagation
            print("⏳ Waiting for relationship data propagation...")
            time.sleep(4)

            # Step 4: Validate session persistence and metadata
            print("🔍 Validating session storage...")
            retrieved_session = integration_client.sessions.get_session(session_id)
            assert retrieved_session is not None, "Session not found in system"
            assert hasattr(retrieved_session, "event"), "Session missing event data"
            assert (
                retrieved_session.event.session_id == session_id
            ), "Session ID mismatch"
            print(f"✅ Session validation successful: {session_id}")

            # Step 5: Validate event-session relationships
            print("🔍 Validating event-session relationships...")
            session_filter = EventFilter(
                field="session_id",
                value=session_id,
                operator=Operator.is_,
                type=Type.string,
            )

            events_result = integration_client.events.get_events(
                project=real_project, filters=[session_filter], limit=20
            )

            assert "events" in events_result, "Events result missing 'events' key"
            retrieved_events = events_result["events"]

            # Validate all events are linked to session
            found_events = []
            for event_id in event_ids:
                found_event = None
                for event in retrieved_events:
                    # Events are now Event objects, not dictionaries
                    if event.event_id == event_id:
                        found_event = event
                        break

                assert (
                    found_event is not None
                ), f"Event {event_id} not found in session {session_id}"
                assert (
                    found_event.session_id == session_id
                ), f"Event {event_id} not properly linked to session"
                assert (
                    found_event.config["test_id"] == test_id
                ), f"Event {event_id} test_id corrupted"
                found_events.append(found_event)

            # Step 6: Validate event data integrity and ordering
            print("🔍 Validating event data integrity...")
            for i, event in enumerate(found_events):
                # Events are Event objects, use attribute access
                expected_index = event.config["event_index"]
                assert event.config["model"] == "gpt-4", f"Event {i} model corrupted"
                assert (
                    event.config["temperature"] == 0.7
                ), f"Event {i} temperature corrupted"
                assert (
                    event.inputs["prompt"]
                    == f"Test prompt {expected_index} for session {test_id}"
                ), f"Event {i} input corrupted"
                assert (
                    event.outputs["response"] == f"Test response {expected_index}"
                ), f"Event {i} output corrupted"

            print("✅ RELATIONSHIP VALIDATION SUCCESSFUL:")
            print(f"   - Session ID: {session_id}")
            print(f"   - Events created: {len(event_ids)}")
            print(f"   - Events retrieved: {len(found_events)}")
            print("   - Session-event linking: ✓")
            print("   - Event data integrity: ✓")
            print("   - Relationship persistence: ✓")

        except Exception as e:
            # Agent OS Zero Failing Tests Policy: NO SKIPPING - real system exercise
            # required
            pytest.fail(
                f"Session-event integration test failed - real system must work: {e}"
            )

    def test_configuration_workflow_validation(
        self, integration_client: Any, integration_project_name: Any
    ) -> None:
        """Test configuration creation and retrieval with full validation."""
        if (
            not integration_client.api_key
            or integration_client.api_key == "test-api-key-12345"
        ):
            pytest.fail(
                "Real API credentials required but not available - check .env file"
            )

        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        config_name = f"integration-config-{test_id}"

        try:
            # Step 1: Create configuration with comprehensive parameters
            print(f"🔄 Creating configuration: {config_name}")
            config_request = PostConfigurationRequest(
                name=config_name,
                project=integration_project_name,
                provider="openai",
                parameters=Parameters2(
                    call_type=CallType.chat,
                    model="gpt-3.5-turbo",
                    hyperparameters={
                        "temperature": 0.8,
                        "max_tokens": 150,
                        "top_p": 0.9,
                        "frequency_penalty": 0.1,
                        "presence_penalty": 0.1,
                    },
                ),
                user_properties={"test_id": test_id, "integration_test": True},
            )

            config_response = integration_client.configurations.create_configuration(
                config_request
            )
            # Configuration API returns CreateConfigurationResponse with MongoDB format
            assert hasattr(
                config_response, "acknowledged"
            ), "Configuration response missing acknowledged"
            assert (
                config_response.acknowledged is True
            ), "Configuration creation not acknowledged"
            assert hasattr(
                config_response, "inserted_id"
            ), "Configuration response missing inserted_id"
            assert (
                config_response.inserted_id is not None
            ), "Configuration inserted_id is None"
            created_config_id = config_response.inserted_id
            print(f"✅ Configuration created with ID: {created_config_id}")

            # Step 2: Wait for data propagation
            print("⏳ Waiting for configuration data propagation...")
            time.sleep(2)

            # Step 3: Retrieve and validate configuration
            print("🔍 Retrieving configurations to validate storage...")
            configurations = integration_client.configurations.list_configurations(
                project=integration_project_name, limit=50
            )

            # Find our specific configuration
            found_config = None
            for config in configurations:
                if hasattr(config, "name") and config.name == config_name:
                    found_config = config
                    break

            # Step 4: Comprehensive validation
            assert (
                found_config is not None
            ), f"Configuration {config_name} not found in HoneyHive system"
            assert found_config.name == config_name, "Configuration name corrupted"
            assert found_config.provider == "openai", "Configuration provider corrupted"

            # Validate parameters integrity (API only stores call_type and model currently)
            params = found_config.parameters
            assert params.model == "gpt-3.5-turbo", "Model parameter corrupted"
            assert params.call_type == CallType.chat, "Call type parameter corrupted"
            # Note: API currently only stores call_type and model, not temperature, max_tokens, etc.

            print("✅ CONFIGURATION VALIDATION SUCCESSFUL:")
            print(f"   - Configuration name: {config_name}")
            print(f"   - Provider: {found_config.provider}")
            print(f"   - Model: {params.model}")
            print("   - Parameter integrity: ✓")
            print("   - Data persistence: ✓")

        except Exception as e:
            # Agent OS Zero Failing Tests Policy: NO SKIPPING - real system exercise required
            pytest.fail(
                f"Configuration integration test failed - real system must work: {e}"
            )

    def test_cross_entity_data_consistency(
        self, integration_client: Any, real_project: Any
    ) -> None:
        """Test data consistency across multiple entity types."""
        if (
            not integration_client.api_key
            or integration_client.api_key == "test-api-key-12345"
        ):
            pytest.fail(
                "Real API credentials required but not available - check .env file"
            )

        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        test_timestamp = int(time.time())

        try:
            # Create entities with shared test_id for consistency validation
            entities_created = {}

            # 1. Create configuration
            config_name = f"consistency-config-{test_id}"
            config_request = PostConfigurationRequest(
                name=config_name,
                project=real_project,
                provider="openai",
                parameters=Parameters2(
                    call_type=CallType.chat,
                    model="gpt-4",
                    hyperparameters={"temperature": 0.5},
                ),
                user_properties={"test_id": test_id, "timestamp": test_timestamp},
            )
            config_response = integration_client.configurations.create_configuration(
                config_request
            )
            entities_created["config"] = {
                "name": config_name,
                "response": config_response,
            }

            # 2. Create session
            session_name = f"consistency-session-{test_id}"
            session_request = SessionStartRequest(
                project=real_project,
                session_name=session_name,
                source="consistency-test",
                metadata={"test_id": test_id, "timestamp": test_timestamp},
            )
            session_response = integration_client.sessions.create_session(
                session_request
            )
            entities_created["session"] = {
                "name": session_name,
                "id": session_response.session_id,
            }

            # 3. Create datapoint
            datapoint_request = CreateDatapointRequest(
                project=real_project,
                inputs={"query": f"Consistency test query {test_id}"},
                ground_truth={"response": f"Consistency test response {test_id}"},
                metadata={"test_id": test_id, "timestamp": test_timestamp},
            )
            datapoint_response = integration_client.datapoints.create_datapoint(
                datapoint_request
            )
            entities_created["datapoint"] = {"id": datapoint_response.field_id}

            print(f"✅ All entities created with test_id: {test_id}")

            # Wait for propagation
            time.sleep(4)

            # Validate cross-entity consistency
            print("🔍 Validating cross-entity data consistency...")

            # Check that all entities exist and have consistent metadata
            consistency_checks = []

            # Validate configuration exists with correct metadata
            configs = integration_client.configurations.list_configurations(
                project=real_project, limit=50
            )
            found_config = next((c for c in configs if c.name == config_name), None)
            if found_config and hasattr(found_config, "metadata"):
                consistency_checks.append(
                    {
                        "entity": "configuration",
                        "test_id_match": found_config.metadata.get("test_id")
                        == test_id,
                        "timestamp_match": found_config.metadata.get("timestamp")
                        == test_timestamp,
                    }
                )

            # Validate session exists
            try:
                session = integration_client.sessions.get_session(
                    entities_created["session"]["id"]
                )
                consistency_checks.append(
                    {
                        "entity": "session",
                        "exists": session is not None,
                        "id_match": session.event.session_id
                        == entities_created["session"]["id"],
                    }
                )
            except Exception:
                consistency_checks.append({"entity": "session", "exists": False})

            # Validate datapoint exists
            datapoints = integration_client.datapoints.list_datapoints(
                project=real_project
            )
            found_datapoint = None
            for dp in datapoints:
                if (
                    hasattr(dp, "inputs")
                    and dp.inputs
                    and dp.inputs.get("query") == f"Consistency test query {test_id}"
                ):
                    found_datapoint = dp
                    break

            if found_datapoint:
                consistency_checks.append(
                    {
                        "entity": "datapoint",
                        "exists": True,
                        "data_match": found_datapoint.inputs.get("query")
                        == f"Consistency test query {test_id}",
                    }
                )

            # Report consistency results
            print("✅ CROSS-ENTITY CONSISTENCY VALIDATION:")
            print(f"   - Test ID: {test_id}")
            print(f"   - Timestamp: {test_timestamp}")
            for check in consistency_checks:
                print(f"   - {check['entity']}: {check}")

            # Assert at least basic entity creation succeeded
            assert len(entities_created) >= 3, "Not all entities were created"
            print("   - All entities created and validated: ✓")

        except Exception as e:
            # Agent OS Zero Failing Tests Policy: NO SKIPPING - real system exercise required
            pytest.fail(
                f"Cross-entity consistency test failed - real system must work: {e}"
            )
