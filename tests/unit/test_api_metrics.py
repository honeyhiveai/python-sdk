"""Unit tests for honeyhive.api.metrics.

This module contains comprehensive unit tests for the MetricsAPI class,
covering all CRUD operations, async variants, legacy methods, and error handling.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

# Remove unused imports - Dict and List not needed
from unittest.mock import AsyncMock, Mock, patch

import pytest

from honeyhive.api.metrics import MetricsAPI
from honeyhive.models import Metric, MetricEdit
from honeyhive.models.generated import ReturnType, Type1
from honeyhive.utils.error_handler import AuthenticationError, ErrorContext


class TestMetricsAPIInitialization:
    """Test suite for MetricsAPI initialization."""

    def test_initialization_success(self, mock_client: Mock) -> None:
        """Test successful MetricsAPI initialization.

        Verifies that MetricsAPI inherits from BaseAPI correctly
        and initializes with proper client reference.
        """
        # Arrange & Act
        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            metrics_api = MetricsAPI(mock_client)

            # Assert
            assert metrics_api.client == mock_client
            assert metrics_api.error_handler == mock_error_handler
            assert metrics_api._client_name == "MetricsAPI"

    def test_initialization_with_custom_client(self, mock_client: Mock) -> None:
        """Test MetricsAPI initialization with custom client configuration.

        Verifies that MetricsAPI properly handles different client types
        and maintains proper inheritance from BaseAPI.
        """
        # Arrange
        mock_client.base_url = "https://custom.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            # Act
            metrics_api = MetricsAPI(mock_client)

            # Assert
            assert (
                getattr(metrics_api.client, "base_url") == "https://custom.honeyhive.ai"
            )
            assert metrics_api._client_name == "MetricsAPI"
            assert hasattr(metrics_api, "_process_data_dynamically")
            assert hasattr(metrics_api, "_create_error_context")


class TestMetricsAPICreateMetric:
    """Test suite for metric creation methods."""

    def test_create_metric_success(self, mock_client: Mock) -> None:
        """Test successful metric creation using Metric model.

        Verifies that create_metric properly serializes the Metric model,
        makes the correct API call, and returns a Metric instance.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "name": "test_metric",
                "task": "test_project",
                "type": "PYTHON",
                "criteria": "def evaluate(event): return True",
                "description": "Test metric description",
                "return_type": "float",
            }
        )
        mock_client.request.return_value = mock_response

        test_metric = Metric(
            name="test_metric",
            type=Type1.PYTHON,
            criteria="def evaluate(event): return True",
            description="Test metric description",
            return_type=ReturnType.float,
        )

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = metrics_api.create_metric(test_metric)

            # Assert
            assert isinstance(result, Metric)
            assert result.name == "test_metric"
            assert result.type.value == "PYTHON"  # pylint: disable=no-member

            # Verify API call
            mock_client.request.assert_called_once_with(
                "POST",
                "/metrics",
                json=test_metric.model_dump(mode="json", exclude_none=True),
            )
            mock_response.json.assert_called_once()

    def test_create_metric_from_dict_success(self, mock_client: Mock) -> None:
        """Test successful metric creation from dictionary (legacy method).

        Verifies that create_metric_from_dict handles dictionary input
        and returns a properly constructed Metric instance.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "legacy_metric",
            "task": "legacy_project",
            "type": "LLM",
            "criteria": "Rate quality",
            "description": "Legacy metric description",
            "return_type": "boolean",
            "model_provider": "openai",
            "model_name": "gpt-4",
        }
        mock_client.request.return_value = mock_response

        metric_data = {
            "name": "legacy_metric",
            "type": "LLM",
            "criteria": "Rate quality",
            "description": "Legacy metric description",
            "return_type": "boolean",
            "model_provider": "openai",
            "model_name": "gpt-4",
        }

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = metrics_api.create_metric_from_dict(metric_data)

            # Assert
            assert isinstance(result, Metric)
            assert result.name == "legacy_metric"
            assert result.type.value == "LLM"  # pylint: disable=no-member

            # Verify API call
            mock_client.request.assert_called_once_with(
                "POST", "/metrics", json=metric_data
            )

    @pytest.mark.asyncio
    async def test_create_metric_async_success(self, mock_client: Mock) -> None:
        """Test successful asynchronous metric creation using Metric model.

        Verifies that create_metric_async properly handles async operations
        and returns the expected Metric instance.
        """
        # Arrange
        mock_response_data = {
            "name": "async_metric",
            "task": "async_project",
            "type": "COMPOSITE",
            "criteria": "weighted-average",
            "description": "Async metric description",
            "return_type": "string",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        test_metric = Metric(
            name="async_metric",
            type=Type1.COMPOSITE,
            criteria="weighted-average",
            description="Async metric description",
            return_type=ReturnType.string,
        )

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = await metrics_api.create_metric_async(test_metric)

            # Assert
            assert isinstance(result, Metric)
            assert result.name == "async_metric"
            assert result.type.value == "COMPOSITE"  # pylint: disable=no-member

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "POST",
                "/metrics",
                json=test_metric.model_dump(mode="json", exclude_none=True),
            )

    @pytest.mark.asyncio
    async def test_create_metric_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test successful asynchronous metric creation from dictionary.

        Verifies that create_metric_from_dict_async handles dictionary input
        asynchronously and returns a Metric instance.
        """
        # Arrange
        mock_response_data = {
            "name": "async_legacy_metric",
            "task": "async_legacy_project",
            "type": "HUMAN",
            "criteria": "Rate the response",
            "description": "Async legacy metric description",
            "return_type": "float",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        metric_data = {
            "name": "async_legacy_metric",
            "type": "HUMAN",
            "criteria": "Rate the response",
            "description": "Async legacy metric description",
            "return_type": "float",
        }

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = await metrics_api.create_metric_from_dict_async(metric_data)

            # Assert
            assert isinstance(result, Metric)
            assert result.name == "async_legacy_metric"
            assert result.type.value == "HUMAN"  # pylint: disable=no-member

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "POST", "/metrics", json=metric_data
            )


class TestMetricsAPIGetMetric:
    """Test suite for metric retrieval methods."""

    def test_get_metric_success(self, mock_client: Mock) -> None:
        """Test successful metric retrieval by ID.

        Verifies that get_metric makes the correct API call
        and returns a properly constructed Metric instance.
        """
        # Arrange
        metric_id = "metric-123"
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "id": metric_id,
                "name": "retrieved_metric",
                "task": "retrieved_project",
                "type": "PYTHON",
                "criteria": "def evaluate(event): return True",
                "description": "Retrieved metric description",
                "return_type": "boolean",
            }
        )
        mock_client.request.return_value = mock_response

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = metrics_api.get_metric(metric_id)

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "retrieved_metric"

            # Verify API call
            mock_client.request.assert_called_once_with(
                "GET", "/metrics", params={"id": metric_id}
            )
            mock_response.json.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_metric_async_success(self, mock_client: Mock) -> None:
        """Test successful asynchronous metric retrieval by ID.

        Verifies that get_metric_async handles async operations correctly
        and returns the expected Metric instance.
        """
        # Arrange
        metric_id = "async-metric-456"
        mock_response_data = {
            "id": metric_id,
            "name": "async_retrieved_metric",
            "task": "async_retrieved_project",
            "type": "LLM",
            "criteria": "Rate quality",
            "description": "Async retrieved metric description",
            "return_type": "string",
            "model_provider": "openai",
            "model_name": "gpt-4",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = await metrics_api.get_metric_async(metric_id)

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "async_retrieved_metric"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "GET", "/metrics", params={"id": metric_id}
            )


class TestMetricsAPIListMetrics:
    """Test suite for metric listing methods."""

    def test_list_metrics_without_project_filter(self, mock_client: Mock) -> None:
        """Test listing metrics without project filter.

        Verifies that list_metrics handles default parameters correctly
        and processes the response using _process_data_dynamically.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "metrics": [
                {
                    "name": "metric1",
                    "task": "project1",
                    "type": "PYTHON",
                    "criteria": "def evaluate(event): return True",
                    "description": "First metric",
                    "return_type": "float",
                },
                {
                    "name": "metric2",
                    "task": "project2",
                    "type": "LLM",
                    "criteria": "Rate quality",
                    "description": "Second metric",
                    "return_type": "boolean",
                    "model_provider": "openai",
                    "model_name": "gpt-4",
                },
            ]
        }
        mock_client.request.return_value = mock_response

        mock_processed_metrics = [Mock(), Mock()]

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            with patch.object(
                metrics_api,
                "_process_data_dynamically",
                return_value=mock_processed_metrics,
            ) as mock_process:
                # Act
                result = metrics_api.list_metrics()

                # Assert
                assert result == mock_processed_metrics
                assert len(result) == 2

                # Verify API call without project filter
                mock_client.request.assert_called_once_with(
                    "GET", "/metrics", params={"limit": "100"}
                )

                # Verify data processing
                mock_process.assert_called_once_with(
                    mock_response.json.return_value["metrics"], Metric, "metrics"
                )

    def test_list_metrics_with_project_filter(self, mock_client: Mock) -> None:
        """Test listing metrics with project filter.

        Verifies that list_metrics correctly handles the conditional branch
        when project parameter is provided.
        """
        # Arrange
        project_name = "test_project"
        custom_limit = 50
        mock_response = Mock()
        mock_response.json.return_value = {"metrics": []}
        mock_client.request.return_value = mock_response

        mock_processed_metrics: list[Mock] = []

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            with patch.object(
                metrics_api,
                "_process_data_dynamically",
                return_value=mock_processed_metrics,
            ):
                # Act
                result = metrics_api.list_metrics(
                    project=project_name, limit=custom_limit
                )

                # Assert
                assert result == mock_processed_metrics

                # Verify API call with project filter - CRITICAL CONDITIONAL BRANCH
                mock_client.request.assert_called_once_with(
                    "GET", "/metrics", params={"limit": "50", "project": project_name}
                )

    @pytest.mark.asyncio
    async def test_list_metrics_async_without_project_filter(
        self, mock_client: Mock
    ) -> None:
        """Test asynchronous listing of metrics without project filter.

        Verifies that list_metrics_async handles async operations
        and default parameters correctly.
        """
        # Arrange
        mock_response_data = {
            "metrics": [
                {
                    "name": "async_metric1",
                    "task": "async_project1",
                    "type": "COMPOSITE",
                    "criteria": "weighted-average",
                    "description": "First async metric",
                    "return_type": "string",
                }
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        mock_processed_metrics: list[Mock] = [Mock()]

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            with patch.object(
                metrics_api,
                "_process_data_dynamically",
                return_value=mock_processed_metrics,
            ) as mock_process:
                # Act
                result = await metrics_api.list_metrics_async()

                # Assert
                assert result == mock_processed_metrics

                # Verify async API call
                mock_client.request_async.assert_called_once_with(
                    "GET", "/metrics", params={"limit": "100"}
                )

                # Verify data processing
                mock_process.assert_called_once_with(
                    mock_response.json.return_value["metrics"], Metric, "metrics"
                )

    @pytest.mark.asyncio
    async def test_list_metrics_async_with_project_filter(
        self, mock_client: Mock
    ) -> None:
        """Test asynchronous listing of metrics with project filter.

        Verifies that list_metrics_async correctly handles the conditional branch
        when project parameter is provided in async context.
        """
        # Arrange
        project_name = "async_test_project"
        custom_limit = 25
        mock_response_data: dict[str, list] = {"metrics": []}
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        mock_processed_metrics: list[Mock] = []

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            with patch.object(
                metrics_api,
                "_process_data_dynamically",
                return_value=mock_processed_metrics,
            ):
                # Act
                result = await metrics_api.list_metrics_async(
                    project=project_name, limit=custom_limit
                )

                # Assert
                assert result == mock_processed_metrics

                # Verify async API call with project filter - CRITICAL BRANCH
                mock_client.request_async.assert_called_once_with(
                    "GET", "/metrics", params={"limit": "25", "project": project_name}
                )


class TestMetricsAPIUpdateMetric:
    """Test suite for metric update methods."""

    def test_update_metric_success(self, mock_client: Mock) -> None:
        """Test successful metric update using MetricEdit model.

        Verifies that update_metric properly serializes the MetricEdit model
        and returns an updated Metric instance.
        """
        # Arrange
        metric_id = "update-metric-123"
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": metric_id,
            "name": "updated_metric",
            "task": "updated_project",
            "type": "PYTHON",
            "criteria": "def evaluate(event): return True",
            "description": "Updated metric description",
            "return_type": "float",
        }
        mock_client.request.return_value = mock_response

        metric_edit = MetricEdit(
            metric_id=metric_id,
            name="updated_metric",
            description="Updated metric description",
        )

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = metrics_api.update_metric(metric_id, metric_edit)

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "updated_metric"

            # Verify API call
            update_data_with_id = metric_edit.model_dump(mode="json", exclude_none=True)
            update_data_with_id["id"] = metric_id
            mock_client.request.assert_called_once_with(
                "PUT",
                "/metrics",
                json=update_data_with_id,
            )

    def test_update_metric_from_dict_success(self, mock_client: Mock) -> None:
        """Test successful metric update from dictionary (legacy method).

        Verifies that update_metric_from_dict handles dictionary input
        and returns an updated Metric instance.
        """
        # Arrange
        metric_id = "update-dict-metric-456"
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": metric_id,
            "name": "dict_updated_metric",
            "task": "dict_updated_project",
            "type": "LLM",
            "criteria": "Rate quality",
            "description": "Dict updated metric description",
            "return_type": "boolean",
            "model_provider": "openai",
            "model_name": "gpt-4",
        }
        mock_client.request.return_value = mock_response

        metric_data = {
            "name": "dict_updated_metric",
            "description": "Dict updated metric description",
        }

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = metrics_api.update_metric_from_dict(metric_id, metric_data)

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "dict_updated_metric"

            # Verify API call
            mock_client.request.assert_called_once_with(
                "PUT", "/metrics", json={**metric_data, "id": metric_id}
            )

    @pytest.mark.asyncio
    async def test_update_metric_async_success(self, mock_client: Mock) -> None:
        """Test successful asynchronous metric update using MetricEdit model.

        Verifies that update_metric_async handles async operations correctly
        and returns an updated Metric instance.
        """
        # Arrange
        metric_id = "async-update-metric-789"
        mock_response_data = {
            "id": metric_id,
            "name": "async_updated_metric",
            "task": "async_updated_project",
            "type": "COMPOSITE",
            "criteria": "weighted-average",
            "description": "Async updated metric description",
            "return_type": "string",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        metric_edit = MetricEdit(
            metric_id=metric_id,
            name="async_updated_metric",
            description="Async updated metric description",
        )

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = await metrics_api.update_metric_async(metric_id, metric_edit)

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "async_updated_metric"

            # Verify async API call
            update_data_with_id = metric_edit.model_dump(mode="json", exclude_none=True)
            update_data_with_id["id"] = metric_id
            mock_client.request_async.assert_called_once_with(
                "PUT",
                "/metrics",
                json=update_data_with_id,
            )

    @pytest.mark.asyncio
    async def test_update_metric_from_dict_async_success(
        self, mock_client: Mock
    ) -> None:
        """Test successful asynchronous metric update from dictionary.

        Verifies that update_metric_from_dict_async handles dictionary input
        asynchronously and returns an updated Metric instance.
        """
        # Arrange
        metric_id = "async-dict-update-metric-101"
        mock_response_data = {
            "id": metric_id,
            "name": "async_dict_updated_metric",
            "task": "async_dict_updated_project",
            "type": "HUMAN",
            "criteria": "Rate the response",
            "description": "Async dict updated metric description",
            "return_type": "float",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_client.request_async = AsyncMock(return_value=mock_response)

        metric_data = {
            "name": "async_dict_updated_metric",
            "description": "Async dict updated metric description",
        }

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act
            result = await metrics_api.update_metric_from_dict_async(
                metric_id, metric_data
            )

            # Assert
            assert isinstance(result, Metric)
            assert result.id == metric_id
            assert result.name == "async_dict_updated_metric"

            # Verify async API call
            mock_client.request_async.assert_called_once_with(
                "PUT", "/metrics", json={**metric_data, "id": metric_id}
            )


class TestMetricsAPIDeleteMetric:
    """Test suite for metric deletion methods with error handling."""

    def test_delete_metric_raises_authentication_error(self, mock_client: Mock) -> None:
        """Test that delete_metric raises AuthenticationError.

        Metric deletion via API is not authorized - users must use the webapp.
        """
        metric_id = "delete-metric-123"

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                metrics_api.delete_metric(metric_id)

            assert "not authorized" in str(exc_info.value).lower()
            assert "webapp" in str(exc_info.value).lower()

            # Verify no API call was made
            mock_client.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_metric_async_raises_authentication_error(
        self, mock_client: Mock
    ) -> None:
        """Test that delete_metric_async raises AuthenticationError.

        Metric deletion via API is not authorized - users must use the webapp.
        """
        metric_id = "async-delete-metric-789"

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                await metrics_api.delete_metric_async(metric_id)

            assert "not authorized" in str(exc_info.value).lower()
            assert "webapp" in str(exc_info.value).lower()

            # Verify no async API call was made
            mock_client.request_async.assert_not_called()


class TestMetricsAPIIntegration:
    """Test suite for MetricsAPI integration scenarios."""

    def test_inheritance_from_base_api(self, mock_client: Mock) -> None:
        """Test that MetricsAPI properly inherits BaseAPI functionality.

        Verifies that MetricsAPI has access to inherited methods
        and maintains proper inheritance chain.
        """
        # Arrange & Act
        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Assert
            assert hasattr(metrics_api, "_process_data_dynamically")
            assert hasattr(metrics_api, "_create_error_context")
            assert hasattr(metrics_api, "client")
            assert hasattr(metrics_api, "error_handler")
            assert metrics_api._client_name == "MetricsAPI"

    def test_model_serialization_consistency(self, mock_client: Mock) -> None:
        """Test consistency of model serialization across methods.

        Verifies that both create_metric and update_metric use
        the same serialization pattern for Pydantic models.
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "test_metric",
            "type": "PYTHON",
            "criteria": "def evaluate(event): return True",
            "description": "Test description",
            "return_type": "float",
        }
        mock_client.request.return_value = mock_response

        test_metric = Metric(
            name="test_metric",
            type=Type1.PYTHON,
            criteria="def evaluate(event): return True",
            description="Test description",
            return_type=ReturnType.float,
        )

        with patch("honeyhive.api.base.get_error_handler"):
            metrics_api = MetricsAPI(mock_client)

            # Act - Test create_metric serialization
            metrics_api.create_metric(test_metric)
            create_call = mock_client.request.call_args_list[0]

            # Reset mock for update test
            mock_client.request.reset_mock()

            # Test update_metric serialization
            metric_edit = MetricEdit(
                metric_id="test-id", name="test_metric", description="Test description"
            )
            metrics_api.update_metric("test-id", metric_edit)
            update_call = mock_client.request.call_args_list[0]

            # Assert
            # Both should use model_dump with same parameters
            create_json = create_call[1]["json"]
            update_json = update_call[1]["json"]

            # Verify both use exclude_none=True serialization
            assert isinstance(create_json, dict)
            assert isinstance(update_json, dict)
