"""Unit tests for honeyhive.config.models.tracer.

This module contains comprehensive unit tests for tracer configuration models
including TracerConfig, SessionConfig, and EvaluationConfig classes with
their field validation logic.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from honeyhive.config.models.tracer import (
    EvaluationConfig,
    SessionConfig,
    TracerConfig,
)


class TestTracerConfig:
    """Test suite for TracerConfig class."""

    def test_initialization_with_defaults(self) -> None:
        """Test TracerConfig initialization with default values."""
        # Clear any environment variables that might affect defaults
        with patch.dict("os.environ", {}, clear=True):
            config = TracerConfig()

            assert config.api_key is None
            assert config.project is None
            assert config.test_mode is False
            assert config.verbose is False
            assert config.session_name is None
            assert config.source == "dev"
            assert config.server_url == "https://api.honeyhive.ai"
            assert config.disable_http_tracing is True
            assert config.disable_batch is False
            assert config.disable_tracing is False
            assert config.cache_enabled is True
            assert config.cache_max_size is None
            assert config.cache_ttl is None
            assert config.cache_cleanup_interval is None
            assert config.session_id is None
            assert config.inputs is None
            assert config.link_carrier is None
            assert config.is_evaluation is False
            assert config.run_id is None
            assert config.dataset_id is None
            assert config.datapoint_id is None
            # Span limit defaults
            assert config.max_attributes == 1024
            assert config.max_events == 1024
            assert config.max_links == 128
            assert config.max_span_size == 10 * 1024 * 1024  # 10MB
            assert config.preserve_core_attributes is True  # Default enabled

    def test_initialization_with_values(self) -> None:
        """Test TracerConfig initialization with provided values."""
        config = TracerConfig(
            api_key="hh_test_key",
            project="test-project",
            session_name="test-session",
            source="production",
            server_url="https://api.honeyhive.ai",
            verbose=True,
            test_mode=True,
            disable_http_tracing=False,
            disable_batch=True,
            cache_enabled=False,
            cache_max_size=1000,
            cache_ttl=300.0,
            session_id="550e8400-e29b-41d4-a716-446655440000",
            inputs={"user_id": "123"},
            is_evaluation=True,
            run_id="eval-run-123",
            max_attributes=2048,
            max_events=256,
            max_links=256,
            max_span_size=20 * 1024 * 1024,  # 20MB
            preserve_core_attributes=False,  # Explicitly disable for testing
        )

        assert config.api_key == "hh_test_key"
        assert config.project == "test-project"
        assert config.session_name == "test-session"
        assert config.source == "production"
        assert config.server_url == "https://api.honeyhive.ai"
        assert config.verbose is True
        assert config.test_mode is True
        assert config.disable_http_tracing is False
        assert config.disable_batch is True
        assert config.cache_enabled is False
        assert config.cache_max_size == 1000
        assert config.cache_ttl == 300.0
        assert config.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert config.inputs == {"user_id": "123"}
        assert config.is_evaluation is True
        assert config.run_id == "eval-run-123"
        # Span limit custom values
        assert config.max_attributes == 2048
        assert config.max_events == 256
        assert config.max_links == 256
        assert config.max_span_size == 20 * 1024 * 1024  # 20MB
        assert config.preserve_core_attributes is False  # Custom value

    def test_validate_server_url_valid_https(self) -> None:
        """Test server URL validation with valid HTTPS URL."""
        config = TracerConfig(server_url="https://api.honeyhive.ai")
        assert config.server_url == "https://api.honeyhive.ai"

    def test_validate_server_url_valid_http(self) -> None:
        """Test server URL validation with valid HTTP URL."""
        config = TracerConfig(server_url="http://localhost:8080")
        assert config.server_url == "http://localhost:8080"

    @patch("honeyhive.config.models.base.logger")
    def test_validate_server_url_invalid_protocol(self, mock_logger: Mock) -> None:
        """Test server URL validation with invalid protocol falls back to default."""
        config = TracerConfig(server_url="ftp://invalid.com")

        assert config.server_url == "https://api.honeyhive.ai"
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert (
            "Invalid" in call_args[0][0] and "must be HTTP/HTTPS URL" in call_args[0][0]
        )

    @patch("honeyhive.config.models.base.logger")
    def test_validate_server_url_non_string(self, mock_logger: Mock) -> None:
        """Test server URL validation with non-string value falls back to default."""
        config = TracerConfig(server_url=12345)  # type: ignore[arg-type]

        assert config.server_url == "https://api.honeyhive.ai"
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert (
            "Invalid" in call_args[0][0]
            and "expected string" in call_args[0][0]
            and "got" in call_args[0][0]
        )

    def test_validate_server_url_none(self) -> None:
        """Test server URL validation with None value defaults to API URL."""
        config = TracerConfig(server_url=None)
        assert config.server_url == "https://api.honeyhive.ai"

    def test_validate_source_valid_string(self) -> None:
        """Test source validation with valid string."""
        config = TracerConfig(source="production")
        assert config.source == "production"

    @patch("honeyhive.config.models.base.logger")
    def test_validate_source_non_string(self, mock_logger: Mock) -> None:
        """Test source validation with non-string value."""
        config = TracerConfig(source=123)  # type: ignore[arg-type]

        assert config.source == "dev"
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert (
            "Invalid" in call_args[0][0]
            and "expected string" in call_args[0][0]
            and "got" in call_args[0][0]
        )

    @patch("honeyhive.config.models.base.logger")
    def test_validate_source_empty_string(self, mock_logger: Mock) -> None:
        """Test source validation with empty string."""
        config = TracerConfig(source="")

        assert config.source == "dev"
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "Empty" in call_args[0][0] and "provided" in call_args[0][0]

    def test_validate_session_id_valid_uuid(self) -> None:
        """Test session ID validation with valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        config = TracerConfig(session_id=valid_uuid)
        assert config.session_id == valid_uuid.lower()

    def test_validate_session_id_uppercase_uuid(self) -> None:
        """Test session ID validation normalizes uppercase UUID to lowercase."""
        uppercase_uuid = "550E8400-E29B-41D4-A716-446655440000"
        config = TracerConfig(session_id=uppercase_uuid)
        assert config.session_id == uppercase_uuid.lower()

    @patch("honeyhive.config.models.tracer.logger")
    def test_validate_session_id_invalid_uuid(self, mock_logger: Mock) -> None:
        """Test session ID validation with invalid UUID format."""
        config = TracerConfig(session_id="invalid-uuid")

        assert config.session_id is None
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "Invalid session_id: must be a valid UUID" in call_args[0][0]

    @patch("honeyhive.config.models.base.logger")
    def test_validate_session_id_non_string(self, mock_logger: Mock) -> None:
        """Test session ID validation with non-string value."""
        config = TracerConfig(session_id=12345)  # type: ignore[arg-type]

        assert config.session_id is None
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert (
            "Invalid" in call_args[0][0]
            and "expected string" in call_args[0][0]
            and "got" in call_args[0][0]
        )

    def test_validate_session_id_none(self) -> None:
        """Test session ID validation with None value."""
        config = TracerConfig(session_id=None)
        assert config.session_id is None

    def test_validate_ids_valid_strings(self) -> None:
        """Test ID field validation with valid strings."""
        config = TracerConfig(
            run_id="eval-run-123",
            dataset_id="dataset-456",
            datapoint_id="datapoint-789",
        )

        assert config.run_id == "eval-run-123"
        assert config.dataset_id == "dataset-456"
        assert config.datapoint_id == "datapoint-789"

    @patch("honeyhive.config.models.base.logger")
    def test_validate_ids_non_string_values(self, mock_logger: Mock) -> None:
        """Test ID field validation with non-string values."""
        config = TracerConfig(
            run_id=123,  # type: ignore[arg-type]
            dataset_id=456,  # type: ignore[arg-type]
            datapoint_id=789,  # type: ignore[arg-type]
        )

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None
        assert mock_logger.warning.call_count == 3

    @patch("honeyhive.config.models.base.logger")
    def test_validate_ids_empty_strings(self, mock_logger: Mock) -> None:
        """Test ID field validation with empty strings."""
        config = TracerConfig(run_id="", dataset_id="   ", datapoint_id="")

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None
        assert mock_logger.warning.call_count == 3

    def test_validate_ids_none_values(self) -> None:
        """Test ID field validation with None values."""
        config = TracerConfig(run_id=None, dataset_id=None, datapoint_id=None)

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None

    def test_environment_variable_loading(self) -> None:
        """Test configuration loading from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "HH_API_KEY": "env_api_key",
                "HH_PROJECT": "env_project",
                "HH_SOURCE": "env_source",
                "HH_API_URL": "https://env.honeyhive.ai",
                "HH_VERBOSE": "true",
                "HH_TEST_MODE": "true",
                "HH_DISABLE_HTTP_TRACING": "false",
                "HH_DISABLE_BATCH": "true",
                "HH_CACHE_ENABLED": "false",
                "HH_CACHE_MAX_SIZE": "2000",
                "HH_CACHE_TTL": "600.0",
                "HH_MAX_ATTRIBUTES": "5000",
                "HH_MAX_EVENTS": "512",
                "HH_MAX_LINKS": "256",
                "HH_MAX_SPAN_SIZE": "52428800",  # 50MB in bytes
                "HH_PRESERVE_CORE_ATTRIBUTES": "false",  # Disable via env var
            },
            clear=True,
        ):
            config = TracerConfig()

            assert config.api_key == "env_api_key"
            assert config.project == "env_project"
            assert config.source == "env_source"
            assert config.server_url == "https://env.honeyhive.ai"
            assert config.verbose is True
            assert config.test_mode is True
            assert config.disable_http_tracing is False
            assert config.disable_batch is True
            assert config.cache_enabled is False
            assert config.cache_max_size == 2000
            assert config.cache_ttl == 600.0
            # Span limit environment variables
            assert config.max_attributes == 5000
            assert config.max_events == 512
            assert config.max_links == 256
            assert config.max_span_size == 52428800  # 50MB
            assert config.preserve_core_attributes is False  # Disabled via env var

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden in configuration."""
        with pytest.raises(ValidationError) as exc_info:
            TracerConfig(invalid_field="should_fail")  # type: ignore[call-arg]

        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_complex_inputs_dict(self) -> None:
        """Test configuration with complex inputs dictionary."""
        complex_inputs = {
            "user_id": "user-123",
            "session_data": {
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"version": "1.0"},
            },
            "query": "test query",
        }

        config = TracerConfig(inputs=complex_inputs)
        assert config.inputs == complex_inputs

    def test_complex_link_carrier_dict(self) -> None:
        """Test configuration with complex link carrier dictionary."""
        link_carrier = {
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            "baggage": "userId=alice,serverNode=DF:28,isProduction=false",
            "custom_header": "custom_value",
        }

        config = TracerConfig(link_carrier=link_carrier)
        assert config.link_carrier == link_carrier


class TestSessionConfig:
    """Test suite for SessionConfig class."""

    def test_initialization_with_defaults(self) -> None:
        """Test SessionConfig initialization with default values."""
        with patch.dict("os.environ", {}, clear=True):
            config = SessionConfig()

            assert config.api_key is None
            assert config.project is None
            assert config.test_mode is False
            assert config.verbose is False
            assert config.session_id is None
            assert config.inputs is None
            assert config.link_carrier is None

    def test_initialization_with_values(self) -> None:
        """Test SessionConfig initialization with provided values."""
        config = SessionConfig(
            api_key="hh_session_key",
            project="session-project",
            session_id="550e8400-e29b-41d4-a716-446655440000",
            inputs={"user_id": "session-user"},
            link_carrier={"traceparent": "00-123"},
            verbose=True,
        )

        assert config.api_key == "hh_session_key"
        assert config.project == "session-project"
        assert config.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert config.inputs == {"user_id": "session-user"}
        assert config.link_carrier == {"traceparent": "00-123"}
        assert config.verbose is True

    def test_validate_session_id_valid_uuid(self) -> None:
        """Test session ID validation with valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        config = SessionConfig(session_id=valid_uuid)
        assert config.session_id == valid_uuid.lower()

    def test_validate_session_id_uppercase_uuid(self) -> None:
        """Test session ID validation normalizes uppercase UUID to lowercase."""
        uppercase_uuid = "550E8400-E29B-41D4-A716-446655440000"
        config = SessionConfig(session_id=uppercase_uuid)
        assert config.session_id == uppercase_uuid.lower()

    @patch("honeyhive.config.models.tracer.logger")
    def test_validate_session_id_invalid_uuid(self, mock_logger: Mock) -> None:
        """Test session ID validation with invalid UUID format."""
        config = SessionConfig(session_id="invalid-uuid")

        assert config.session_id is None
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "Invalid session_id: must be a valid UUID" in call_args[0][0]

    @patch("honeyhive.config.models.base.logger")
    def test_validate_session_id_non_string(self, mock_logger: Mock) -> None:
        """Test session ID validation with non-string value."""
        config = SessionConfig(session_id=12345)  # type: ignore[arg-type]

        assert config.session_id is None
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert (
            "Invalid" in call_args[0][0]
            and "expected string" in call_args[0][0]
            and "got" in call_args[0][0]
        )

    def test_validate_session_id_none(self) -> None:
        """Test session ID validation with None value."""
        config = SessionConfig(session_id=None)
        assert config.session_id is None

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden in session configuration."""
        with pytest.raises(ValidationError) as exc_info:
            SessionConfig(invalid_field="should_fail")  # type: ignore[call-arg]

        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_inheritance_from_base_config(self) -> None:
        """Test that SessionConfig properly inherits from BaseHoneyHiveConfig."""
        config = SessionConfig(
            api_key="hh_inherited_key",
            project="inherited-project",
            test_mode=True,
            verbose=True,
        )

        # Test inherited fields work correctly
        assert config.api_key == "hh_inherited_key"
        assert config.project == "inherited-project"
        assert config.test_mode is True
        assert config.verbose is True


class TestEvaluationConfig:
    """Test suite for EvaluationConfig class."""

    def test_initialization_with_defaults(self) -> None:
        """Test EvaluationConfig initialization with default values."""
        with patch.dict("os.environ", {}, clear=True):
            config = EvaluationConfig()

            assert config.api_key is None
            assert config.project is None
            assert config.test_mode is False
            assert config.verbose is False
            assert config.is_evaluation is False
            assert config.run_id is None
            assert config.dataset_id is None
            assert config.datapoint_id is None

    def test_initialization_with_values(self) -> None:
        """Test EvaluationConfig initialization with provided values."""
        config = EvaluationConfig(
            api_key="hh_eval_key",
            project="eval-project",
            is_evaluation=True,
            run_id="eval-run-456",
            dataset_id="eval-dataset-789",
            datapoint_id="eval-datapoint-123",
            verbose=True,
        )

        assert config.api_key == "hh_eval_key"
        assert config.project == "eval-project"
        assert config.is_evaluation is True
        assert config.run_id == "eval-run-456"
        assert config.dataset_id == "eval-dataset-789"
        assert config.datapoint_id == "eval-datapoint-123"
        assert config.verbose is True

    def test_validate_ids_valid_strings(self) -> None:
        """Test ID field validation with valid strings."""
        config = EvaluationConfig(
            run_id="eval-run-123",
            dataset_id="dataset-456",
            datapoint_id="datapoint-789",
        )

        assert config.run_id == "eval-run-123"
        assert config.dataset_id == "dataset-456"
        assert config.datapoint_id == "datapoint-789"

    @patch("honeyhive.config.models.base.logger")
    def test_validate_ids_non_string_values(self, mock_logger: Mock) -> None:
        """Test ID field validation with non-string values."""
        config = EvaluationConfig(
            run_id=123,  # type: ignore[arg-type]
            dataset_id=456,  # type: ignore[arg-type]
            datapoint_id=789,  # type: ignore[arg-type]
        )

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None
        assert mock_logger.warning.call_count == 3

    @patch("honeyhive.config.models.base.logger")
    def test_validate_ids_empty_strings(self, mock_logger: Mock) -> None:
        """Test ID field validation with empty strings."""
        config = EvaluationConfig(run_id="", dataset_id="   ", datapoint_id="")

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None
        assert mock_logger.warning.call_count == 3

    def test_validate_ids_none_values(self) -> None:
        """Test ID field validation with None values."""
        config = EvaluationConfig(run_id=None, dataset_id=None, datapoint_id=None)

        assert config.run_id is None
        assert config.dataset_id is None
        assert config.datapoint_id is None

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden in evaluation configuration."""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationConfig(invalid_field="should_fail")  # type: ignore[call-arg]

        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_inheritance_from_base_config(self) -> None:
        """Test that EvaluationConfig properly inherits from BaseHoneyHiveConfig."""
        config = EvaluationConfig(
            api_key="hh_inherited_key",
            project="inherited-project",
            test_mode=True,
            verbose=True,
        )

        # Test inherited fields work correctly
        assert config.api_key == "hh_inherited_key"
        assert config.project == "inherited-project"
        assert config.test_mode is True
        assert config.verbose is True

    def test_evaluation_mode_enabled(self) -> None:
        """Test evaluation mode configuration."""
        config = EvaluationConfig(
            is_evaluation=True,
            run_id="experiment-2024-01-15",
            dataset_id="qa-dataset-v2",
            datapoint_id="question-42",
        )

        assert config.is_evaluation is True
        assert config.run_id == "experiment-2024-01-15"
        assert config.dataset_id == "qa-dataset-v2"
        assert config.datapoint_id == "question-42"


class TestConfigModelIntegration:
    """Test suite for integration scenarios between config models."""

    def test_tracer_config_with_session_and_evaluation_fields(self) -> None:
        """Test TracerConfig with both session and evaluation fields."""
        config = TracerConfig(
            api_key="hh_integrated_key",
            project="integrated-project",
            # Session fields
            session_id="550e8400-e29b-41d4-a716-446655440000",
            inputs={"user_id": "integrated-user"},
            link_carrier={"traceparent": "00-integrated"},
            # Evaluation fields
            is_evaluation=True,
            run_id="integrated-run",
            dataset_id="integrated-dataset",
            datapoint_id="integrated-datapoint",
        )

        # Base config fields
        assert config.api_key == "hh_integrated_key"
        assert config.project == "integrated-project"

        # Session fields
        assert config.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert config.inputs == {"user_id": "integrated-user"}
        assert config.link_carrier == {"traceparent": "00-integrated"}

        # Evaluation fields
        assert config.is_evaluation is True
        assert config.run_id == "integrated-run"
        assert config.dataset_id == "integrated-dataset"
        assert config.datapoint_id == "integrated-datapoint"

    def test_config_model_field_types(self) -> None:
        """Test that all config models have correct field types."""
        # Test TracerConfig field types
        tracer_config = TracerConfig()
        assert isinstance(tracer_config.disable_http_tracing, bool)
        assert isinstance(tracer_config.disable_batch, bool)
        assert isinstance(tracer_config.cache_enabled, bool)

        # Test SessionConfig field types
        session_config = SessionConfig()
        assert session_config.session_id is None or isinstance(
            session_config.session_id, str
        )
        assert session_config.inputs is None or isinstance(session_config.inputs, dict)

        # Test EvaluationConfig field types
        eval_config = EvaluationConfig()
        assert isinstance(eval_config.is_evaluation, bool)
        assert eval_config.run_id is None or isinstance(eval_config.run_id, str)

    def test_config_model_validation_error_handling(self) -> None:
        """Test that config models handle validation errors gracefully."""
        # Test that invalid types are handled gracefully through validators
        # rather than raising ValidationError for basic type mismatches

        # These should not raise ValidationError due to graceful degradation
        tracer_config = TracerConfig(
            server_url=12345,  # type: ignore[arg-type]  # Invalid type
            source=None,  # type: ignore[arg-type]  # Invalid for source
            session_id="invalid-uuid",  # Invalid UUID, should become None
        )

        assert tracer_config.server_url == "https://api.honeyhive.ai"
        assert tracer_config.source == "dev"
        assert tracer_config.session_id is None

    @patch("honeyhive.config.models.tracer.uuid.UUID")
    def test_uuid_validation_exception_handling(self, mock_uuid: Mock) -> None:
        """Test UUID validation handles ValueError exceptions."""
        mock_uuid.side_effect = ValueError("Invalid UUID format")

        with patch("honeyhive.config.models.tracer.logger") as mock_logger:
            config = TracerConfig(session_id="test-uuid")

            assert config.session_id is None
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            assert "Invalid session_id: must be a valid UUID" in call_args[0][0]
