"""Unit tests for honeyhive.api.base.

This module contains comprehensive unit tests for the BaseAPI class,
covering initialization, error context creation, and dynamic data processing.
"""

# pylint: disable=too-many-lines,duplicate-code
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from typing import Any, Dict
from unittest.mock import Mock, patch

from honeyhive.api.base import BaseAPI
from honeyhive.utils.error_handler import ErrorContext


class TestBaseAPIInitialization:
    """Test suite for BaseAPI initialization."""

    def test_initialization_success(self, mock_client: Mock) -> None:
        """Test successful BaseAPI initialization.

        Verifies that BaseAPI initializes correctly with a client,
        sets up error handler, and stores client name.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            # Act
            base_api = BaseAPI(mock_client)

            # Assert
            assert base_api.client == mock_client
            assert base_api.error_handler == mock_error_handler
            assert base_api._client_name == "BaseAPI"
            mock_get_handler.assert_called_once()

    def test_initialization_with_different_client_types(
        self, mock_client: Mock
    ) -> None:
        """Test BaseAPI initialization with different client configurations.

        Verifies that BaseAPI works with various client configurations
        and properly stores the client reference.
        """
        # Arrange
        mock_client.server_url = "https://custom.api.com"
        mock_client.api_key = "test-key-123"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            # Act
            base_api = BaseAPI(mock_client)

            # Assert
            assert base_api.client.server_url == "https://custom.api.com"
            assert base_api.client.api_key == "test-key-123"
            assert base_api._client_name == "BaseAPI"

    def test_client_name_reflects_subclass(self, mock_client: Mock) -> None:
        """Test that _client_name reflects the actual subclass name.

        Verifies that when BaseAPI is subclassed, the _client_name
        attribute correctly reflects the subclass name.
        """

        # Arrange
        class TestAPISubclass(BaseAPI):
            """Test subclass of BaseAPI."""

            def test_method(self) -> str:
                """Test method to satisfy pylint."""
                return "test"

            def another_method(self) -> str:
                """Another method to satisfy pylint."""
                return "another"

        with patch("honeyhive.api.base.get_error_handler") as mock_get_handler:
            mock_error_handler = Mock()
            mock_get_handler.return_value = mock_error_handler

            # Act
            subclass_api = TestAPISubclass(mock_client)

            # Assert
            assert subclass_api._client_name == "TestAPISubclass"


class TestBaseAPICreateErrorContext:
    """Test suite for BaseAPI._create_error_context method."""

    def test_create_error_context_minimal_parameters(self, mock_client: Mock) -> None:
        """Test error context creation with minimal parameters.

        Verifies that error context is created correctly with just
        the operation parameter and default values for optional parameters.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            context = base_api._create_error_context("test_operation")

            # Assert
            assert isinstance(context, ErrorContext)
            assert context.operation == "test_operation"
            assert context.method is None
            assert context.url is None
            assert context.params is None
            assert context.json_data is None
            assert context.client_name == "BaseAPI"
            assert context.additional_context == {}

    def test_create_error_context_with_path(self, mock_client: Mock) -> None:
        """Test error context creation with path parameter.

        Verifies that when a path is provided, the URL is constructed
        correctly by combining client base_url and the path.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            context = base_api._create_error_context("create_event", path="/events")

            # Assert
            assert context.operation == "create_event"
            assert context.url == "https://api.honeyhive.ai/events"

    def test_create_error_context_with_all_parameters(self, mock_client: Mock) -> None:
        """Test error context creation with all parameters provided.

        Verifies that error context is created correctly when all
        optional parameters are provided with their expected values.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"
        test_params = {"limit": 10, "offset": 0}
        test_json_data = {"name": "test_event", "data": {"key": "value"}}
        additional_context = {"request_id": "req-123", "user_id": "user-456"}

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            context = base_api._create_error_context(
                operation="create_event",
                method="POST",
                path="/events",
                params=test_params,
                json_data=test_json_data,
                **additional_context,
            )

            # Assert
            assert context.operation == "create_event"
            assert context.method == "POST"
            assert context.url == "https://api.honeyhive.ai/events"
            assert context.params == test_params
            assert context.json_data == test_json_data
            assert context.client_name == "BaseAPI"
            assert context.additional_context == additional_context

    def test_create_error_context_without_path(self, mock_client: Mock) -> None:
        """Test error context creation without path parameter.

        Verifies that when no path is provided, the URL remains None
        and other parameters are handled correctly.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            context = base_api._create_error_context(
                operation="validate_config", method="GET"
            )

            # Assert
            assert context.operation == "validate_config"
            assert context.method == "GET"
            assert context.url is None

    def test_create_error_context_with_empty_additional_context(
        self, mock_client: Mock
    ) -> None:
        """Test error context creation with empty additional context.

        Verifies that when no additional context is provided,
        the additional_context field is an empty dictionary.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            context = base_api._create_error_context("test_operation")

            # Assert
            assert context.additional_context == {}


class TestBaseAPIProcessDataDynamically:
    """Test suite for BaseAPI._process_data_dynamically method."""

    def test_process_empty_data_list(self, mock_client: Mock) -> None:
        """Test processing empty data list.

        Verifies that when an empty list is provided,
        the method returns an empty list without processing.
        """
        # Arrange
        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Act
            result = base_api._process_data_dynamically([], Mock, "test_items")

            # Assert
            assert not result

    def test_process_small_dataset_success(self, mock_client: Mock) -> None:
        """Test processing small dataset successfully.

        Verifies that small datasets (≤100 items) are processed
        using the simple processing path with proper model instantiation.
        """
        # Arrange
        mock_model_class = Mock()
        mock_instance_1 = Mock()
        mock_instance_2 = Mock()
        mock_model_class.side_effect = [mock_instance_1, mock_instance_2]

        test_data = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 2
                assert result[0] == mock_instance_1
                assert result[1] == mock_instance_2

                # Verify model class was called with correct data
                assert mock_model_class.call_count == 2
                mock_model_class.assert_any_call(**test_data[0])
                mock_model_class.assert_any_call(**test_data[1])

                # Verify no debug logging for small datasets
                mock_log.assert_not_called()

    def test_process_small_dataset_with_validation_errors(
        self, mock_client: Mock
    ) -> None:
        """Test processing small dataset with validation errors.

        Verifies that validation errors in small datasets are logged
        and invalid items are skipped while valid items are processed.
        """
        # Arrange
        mock_model_class = Mock()
        mock_instance = Mock()
        mock_model_class.side_effect = [
            ValueError("Invalid data"),  # First item fails
            mock_instance,  # Second item succeeds
        ]

        test_data = [{"id": "invalid"}, {"id": 2, "name": "valid_item"}]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 1
                assert result[0] == mock_instance

                # Verify error was logged
                mock_log.assert_called_once()
                log_call = mock_log.call_args
                assert log_call[0][0] == "warning"
                assert "validation error" in log_call[0][1]

    def test_process_large_dataset_success(self, mock_client: Mock) -> None:
        """Test processing large dataset successfully.

        Verifies that large datasets (>100 items) use the optimized
        processing path with progress logging and performance monitoring.
        """
        # Arrange
        mock_model_class = Mock()
        mock_instances = [Mock() for _ in range(150)]
        mock_model_class.side_effect = mock_instances

        test_data = [{"id": i, "name": f"item{i}"} for i in range(150)]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 150
                assert all(instance in mock_instances for instance in result)

                # Verify debug logging for large dataset
                debug_calls = [
                    call for call in mock_log.call_args_list if call[0][0] == "debug"
                ]
                assert len(debug_calls) >= 2  # Initial + completion logs

                # Verify initial processing log
                initial_log = debug_calls[0]
                assert (
                    "Processing large test_items dataset: 150 items"
                    in initial_log[0][1]
                )

                # Verify completion log with success rate
                completion_log = debug_calls[-1]
                assert "processing complete" in completion_log[0][1]
                assert "150/150 items" in completion_log[0][1]
                assert "100.0% success rate" in completion_log[0][1]

    def test_process_large_dataset_with_progress_logging(
        self, mock_client: Mock
    ) -> None:
        """Test large dataset processing with progress logging.

        Verifies that very large datasets (>500 items) include
        progress logging every 100 items for monitoring.
        """
        # Arrange
        mock_model_class = Mock()
        mock_instances = [Mock() for _ in range(600)]
        mock_model_class.side_effect = mock_instances

        test_data = [{"id": i, "name": f"item{i}"} for i in range(600)]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 600

                # Verify progress logging occurred
                progress_calls = [
                    call
                    for call in mock_log.call_args_list
                    if call[0][0] == "debug" and "Processed" in call[0][1]
                ]
                assert (
                    len(progress_calls) >= 5
                )  # Should have progress logs at 100, 200, 300, 400, 500

    def test_process_large_dataset_early_termination(self, mock_client: Mock) -> None:
        """Test large dataset processing with early termination due to errors.

        Verifies that when error count exceeds max_errors (dataset_size // 10),
        processing stops early to prevent performance degradation.
        """
        # Arrange
        mock_model_class = Mock()
        # Create side effects: first 21 items fail (max_errors = 20 for 200 items),
        # rest would succeed
        side_effects = [ValueError("Validation error") for _ in range(21)]
        side_effects.extend([Mock() for _ in range(179)])
        mock_model_class.side_effect = side_effects

        test_data = [{"id": i, "name": f"item{i}"} for i in range(200)]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                # Processing should stop early due to high error rate
                assert len(result) < 200

                # Verify early termination warning was logged
                warning_calls = [
                    call
                    for call in mock_log.call_args_list
                    if call[0][0] == "warning"
                    and "Too many validation errors" in call[0][1]
                ]
                assert len(warning_calls) == 1

                termination_log = warning_calls[0]
                assert (
                    "Stopping processing to prevent performance degradation"
                    in termination_log[0][1]
                )

    def test_process_large_dataset_error_logging_suppression(
        self, mock_client: Mock
    ) -> None:
        """Test error logging suppression in large datasets.

        Verifies that after the first 3 validation errors,
        subsequent error logs are suppressed with a suppression message.
        """
        # Arrange
        mock_model_class = Mock()
        # First 5 items fail, rest succeed
        side_effects = [ValueError(f"Error {i}") for i in range(5)]
        side_effects.extend([Mock() for _ in range(150)])
        mock_model_class.side_effect = side_effects

        test_data = [{"id": i, "name": f"item{i}"} for i in range(155)]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 150  # 5 failed, 150 succeeded

                # Verify error suppression message was logged
                suppression_calls = [
                    call
                    for call in mock_log.call_args_list
                    if call[0][0] == "warning" and "Suppressing further" in call[0][1]
                ]
                assert len(suppression_calls) == 1

                suppression_log = suppression_calls[0]
                assert "test_items validation error logs" in suppression_log[0][1]

    def test_process_data_with_custom_data_type(self, mock_client: Mock) -> None:
        """Test processing data with custom data type parameter.

        Verifies that the data_type parameter is used correctly
        in logging messages and error reporting.
        """
        # Arrange
        mock_model_class = Mock()
        mock_instance = Mock()
        mock_model_class.return_value = mock_instance

        test_data = [{"id": 1, "name": "custom_item"}]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "custom_metrics"
                )

                # Assert
                assert len(result) == 1
                assert result[0] == mock_instance

                # No logging should occur for small successful datasets
                mock_log.assert_not_called()

    def test_process_data_zero_success_rate_calculation(
        self, mock_client: Mock
    ) -> None:
        """Test success rate calculation with zero items processed.

        Verifies that when no items are successfully processed,
        the success rate calculation handles division by zero correctly.
        """
        # Arrange
        mock_model_class = Mock()
        mock_model_class.side_effect = [
            ValueError("All items fail") for _ in range(150)
        ]

        test_data = [{"id": i, "invalid": True} for i in range(150)]

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            with patch.object(base_api.client, "_log") as mock_log:
                # Act
                result = base_api._process_data_dynamically(
                    test_data, mock_model_class, "test_items"
                )

                # Assert
                assert len(result) == 0

                # Verify completion log handles zero success rate
                completion_calls = [
                    call
                    for call in mock_log.call_args_list
                    if call[0][0] == "debug" and "processing complete" in call[0][1]
                ]
                assert len(completion_calls) == 1

                completion_log = completion_calls[0]
                assert "0/150 items" in completion_log[0][1]
                assert "0.0% success rate" in completion_log[0][1]


class TestBaseAPIIntegration:
    """Test suite for BaseAPI integration scenarios."""

    def test_error_context_integration_with_processing(self, mock_client: Mock) -> None:
        """Test integration between error context creation and data processing.

        Verifies that BaseAPI methods work together correctly
        in realistic usage scenarios.
        """
        # Arrange
        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            base_api = BaseAPI(mock_client)

            # Test error context creation
            context = base_api._create_error_context(
                "process_events", method="POST", path="/events/batch"
            )

            # Test data processing
            mock_model = Mock()
            mock_model.return_value = Mock()
            test_data = [{"event_id": 1}, {"event_id": 2}]

            with patch.object(base_api.client, "_log"):
                result = base_api._process_data_dynamically(
                    test_data, mock_model, "events"
                )

            # Assert
            assert context.operation == "process_events"
            assert context.url == "https://api.honeyhive.ai/events/batch"
            assert len(result) == 2

    def test_subclass_behavior_preservation(self, mock_client: Mock) -> None:
        """Test that BaseAPI behavior is preserved in subclasses.

        Verifies that when BaseAPI is subclassed, all functionality
        continues to work correctly with proper inheritance.
        """

        # Arrange
        class EventsAPI(BaseAPI):
            """Test subclass representing an Events API."""

            def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
                """Create an event using BaseAPI functionality."""
                context = self._create_error_context(
                    "create_event", method="POST", path="/events", json_data=event_data
                )
                return {"context": context, "data": event_data}

            def get_events(self) -> Dict[str, Any]:
                """Get events - additional method to satisfy pylint."""
                return {"events": []}

        mock_client.server_url = "https://api.honeyhive.ai"

        with patch("honeyhive.api.base.get_error_handler"):
            events_api = EventsAPI(mock_client)

            # Act
            event_data = {"name": "test_event", "type": "user_action"}
            result = events_api.create_event(event_data)

            # Assert
            assert events_api._client_name == "EventsAPI"
            assert result["context"].operation == "create_event"
            assert result["context"].json_data == event_data
            assert result["data"] == event_data
