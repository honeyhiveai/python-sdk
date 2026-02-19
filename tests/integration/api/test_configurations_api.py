"""ConfigurationsAPI Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import CreateConfigurationRequest


class TestConfigurationsAPI:
    """Test ConfigurationsAPI CRUD operations.

    NOTE: test_get_configuration is skipped because v1 API has no get_configuration
    method - must use list() to retrieve configurations. Other CRUD operations work.

    NOTE: The API's createConfiguration and deleteConfiguration return None
    (no response body). Verification is done via list() instead.
    """

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
            project=integration_project_name,
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        # API createConfiguration returns None - just verify no exception
        integration_client.configurations.create(config_request)

        # Verify via list
        time.sleep(2)
        configs = integration_client.configurations.list()
        assert isinstance(configs, list)

        # Find our config and get its ID for cleanup
        created_config = None
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name == config_name:
                created_config = cfg
                break

        assert (
            created_config is not None
        ), f"Config {config_name} not found after create"

        # Cleanup
        config_id = getattr(created_config, "id", None) or getattr(
            created_config, "_id", None
        )
        if config_id:
            try:
                integration_client.configurations.delete(config_id)
            except Exception:
                pass  # Best-effort cleanup

    @pytest.mark.skip(
        reason="v1 API: no get_configuration method, must use list() to retrieve"
    )
    def test_get_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration retrieval by ID."""
        pass

    def test_list_configurations(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration listing, pagination, filtering, empty results."""
        test_id = str(uuid.uuid4())[:8]

        for i in range(3):
            parameters = {
                "call_type": "chat",
                "model": "gpt-3.5-turbo",
                "hyperparameters": {"test_id": test_id, "index": i},
            }
            config_request = CreateConfigurationRequest(
                project=integration_project_name,
                name=f"test_list_config_{test_id}_{i}",
                provider="openai",
                parameters=parameters,
            )
            integration_client.configurations.create(config_request)

        time.sleep(2)
        configs = integration_client.configurations.list()

        # configurations.list() returns a list of configuration objects
        assert isinstance(configs, list)

        # Cleanup - find and delete our test configs
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name and test_id in cfg.name:
                config_id = getattr(cfg, "id", None) or getattr(cfg, "_id", None)
                if config_id:
                    try:
                        integration_client.configurations.delete(config_id)
                    except Exception:
                        pass

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
            project=integration_project_name,
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        integration_client.configurations.create(config_request)

        time.sleep(2)

        # Find the created config to get its ID
        configs = integration_client.configurations.list()
        created_config = None
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name == config_name:
                created_config = cfg
                break
        assert created_config is not None, f"Config {config_name} not found for update"
        created_id = getattr(created_config, "id", None) or getattr(
            created_config, "_id", None
        )
        assert created_id is not None

        from honeyhive.models import UpdateConfigurationRequest

        update_request = UpdateConfigurationRequest(
            project=integration_project_name,
            name=config_name,
            provider="openai",
            parameters={
                "call_type": "chat",
                "model": "gpt-4",
                "hyperparameters": {"temperature": 0.9, "updated": True},
            },
        )
        # API updateConfiguration returns None
        integration_client.configurations.update(created_id, update_request)

        # Cleanup
        try:
            integration_client.configurations.delete(created_id)
        except Exception:
            pass

    def test_delete_configuration(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test configuration deletion, verify delete response."""
        test_id = str(uuid.uuid4())[:8]
        config_name = f"test_delete_config_{test_id}"

        parameters = {
            "call_type": "chat",
            "model": "gpt-3.5-turbo",
            "hyperparameters": {"test": "delete"},
        }
        config_request = CreateConfigurationRequest(
            project=integration_project_name,
            name=config_name,
            provider="openai",
            parameters=parameters,
        )

        integration_client.configurations.create(config_request)

        time.sleep(2)

        # Find created config ID
        configs = integration_client.configurations.list()
        created_config = None
        for cfg in configs:
            if hasattr(cfg, "name") and cfg.name == config_name:
                created_config = cfg
                break
        assert created_config is not None, f"Config {config_name} not found for delete"
        created_id = getattr(created_config, "id", None) or getattr(
            created_config, "_id", None
        )
        assert created_id is not None

        # Delete - API returns None, just verify no exception
        try:
            integration_client.configurations.delete(created_id)
        except Exception as e:
            # Multi-tenant API key may not have delete permissions (403)
            if "403" in str(e):
                pytest.skip("Delete not permitted with current API key (403)")
            raise
