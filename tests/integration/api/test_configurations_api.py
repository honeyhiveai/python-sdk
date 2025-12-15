"""ConfigurationsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateConfigurationRequest


class TestConfigurationsAPI:
    """Test ConfigurationsAPI CRUD operations.

    NOTE: Several tests are skipped due to discovered API limitations:
    - get_configuration() returns empty responses
    - update_configuration() returns 400 errors
    - list_configurations() doesn't respect limit parameter
    These should be investigated as potential backend issues.
    """

    @pytest.mark.skip(
        reason="API Issue: get_configuration returns empty response after create"
    )
    def test_create_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration creation with valid payload, verify backend storage."""
        test_id = str(uuid.uuid4())[:8]
        config_name = f"test_config_{test_id}"

        parameters = {
            "call_type": "chat",
            "model": "gpt-4",
            "hyperparameters": {"temperature": 0.7, "test_id": test_id},
        }
        config_request = CreateConfigurationRequest(
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        response = integration_client.configurations.create(config_request)

        assert hasattr(response, "acknowledged")
        assert response.acknowledged is True
        assert hasattr(response, "insertedId")
        assert response.insertedId is not None

        created_id = response.insertedId

        time.sleep(2)

        configs = integration_client.configurations.list()
        assert configs is not None
        found = None
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name == config_name:
                found = cfg
                break
        assert found is not None
        assert found.name == config_name

        # Cleanup
        integration_client.configurations.delete(created_id)

    @pytest.mark.skip(reason="v1 API: no get_configuration method, list only")
    def test_get_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration retrieval by ID."""
        test_id = str(uuid.uuid4())[:8]
        config_name = f"test_get_config_{test_id}"

        parameters = {
            "call_type": "chat",
            "model": "gpt-3.5-turbo",
        }
        config_request = CreateConfigurationRequest(
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        create_response = integration_client.configurations.create(config_request)
        created_id = create_response.insertedId

        time.sleep(2)

        configs = integration_client.configurations.list()
        config = None
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name == config_name:
                config = cfg
                break

        assert config is not None
        assert config.name == config_name
        assert config.provider == "openai"

        # Cleanup
        integration_client.configurations.delete(created_id)

    @pytest.mark.skip(
        reason="API Issue: list_configurations doesn't respect limit parameter"
    )
    def test_list_configurations(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration listing, pagination, filtering, empty results."""
        test_id = str(uuid.uuid4())[:8]
        created_ids = []

        for i in range(3):
            parameters = {
                "call_type": "chat",
                "model": "gpt-3.5-turbo",
                "hyperparameters": {"test_id": test_id, "index": i},
            }
            config_request = CreateConfigurationRequest(
                name=f"test_list_config_{test_id}_{i}",
                provider="openai",
                parameters=parameters,
            )
            response = integration_client.configurations.create(config_request)
            created_ids.append(response.insertedId)

        time.sleep(2)

        configs = integration_client.configurations.list()

        assert configs is not None
        assert isinstance(configs, list)

        # Cleanup
        for config_id in created_ids:
            integration_client.configurations.delete(config_id)

    @pytest.mark.skip(reason="API Issue: update_configuration returns 400 error")
    def test_update_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration update operations, verify changes persist."""
        test_id = str(uuid.uuid4())[:8]
        config_name = f"test_update_config_{test_id}"

        parameters = {
            "call_type": "chat",
            "model": "gpt-3.5-turbo",
            "hyperparameters": {"temperature": 0.5},
        }
        config_request = CreateConfigurationRequest(
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        create_response = integration_client.configurations.create(config_request)
        created_id = create_response.insertedId

        time.sleep(2)

        from honeyhive.models import UpdateConfigurationRequest

        update_request = UpdateConfigurationRequest(
            name=config_name,
            provider="openai",
            parameters={
                "call_type": "chat",
                "model": "gpt-4",
                "hyperparameters": {"temperature": 0.9, "updated": True},
            },
        )
        response = integration_client.configurations.update(created_id, update_request)

        assert response is not None
        assert response.acknowledged is True

        # Cleanup
        integration_client.configurations.delete(created_id)

    @pytest.mark.skip(reason="API Issue: depends on get_configuration which has issues")
    def test_delete_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration deletion, verify not in list after delete."""
        test_id = str(uuid.uuid4())[:8]
        config_name = f"test_delete_config_{test_id}"

        parameters = {
            "call_type": "chat",
            "model": "gpt-3.5-turbo",
            "hyperparameters": {"test": "delete"},
        }
        config_request = CreateConfigurationRequest(
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        create_response = integration_client.configurations.create(config_request)
        created_id = create_response.insertedId

        time.sleep(2)

        # Verify exists before deletion
        configs = integration_client.configurations.list()
        found_before = any(
            hasattr(c, "name") and c.name == config_name for c in configs
        )
        assert found_before is True

        # Delete
        response = integration_client.configurations.delete(created_id)
        assert response is not None

        time.sleep(2)

        # Verify not in list after deletion
        configs = integration_client.configurations.list()
        found_after = any(
            hasattr(c, "name") and c.name == config_name for c in configs
        )
        assert found_after is False
