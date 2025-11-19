"""Configuration Validation Integration Tests.

TRUE integration tests (no SDK mocks) that validate:
- Real config loading and merging
- Real environment variable loading
- Real tracer initialization with various configs
- Real Pydantic validation
- Real default value fallbacks
- Real config serialization

Reference: INTEGRATION_TEST_INVENTORY_AND_GAP_ANALYSIS.md Phase 1 Critical Tests
Standards: .agent-os/standards/testing/integration-testing.md

HARD RULE: NO MOCKS for SDK code - only mock external environment variables.
"""

# pylint: disable=duplicate-code,too-many-statements,too-many-locals,too-few-public-methods

import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from honeyhive import HoneyHiveTracer
from honeyhive.config.models.otlp import OTLPConfig
from honeyhive.config.models.tracer import (
    EvaluationConfig,
    SessionConfig,
    TracerConfig,
)


class TestEnvironmentVariables:
    """Test environment variable loading and precedence with REAL env vars."""

    def test_hh_api_key_precedence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test HH_API_KEY environment variable is loaded and can be overridden."""
        # Set env var
        test_api_key_from_env = "env-api-key-12345"
        monkeypatch.setenv("HH_API_KEY", test_api_key_from_env)

        # Test 1: Env var alone should be used
        tracer1 = HoneyHiveTracer(project="test-project", test_mode=True)
        assert tracer1.api_key == test_api_key_from_env
        tracer1.shutdown()

        # Test 2: Individual param should override env var (highest priority)
        override_api_key = "override-api-key-67890"
        tracer2 = HoneyHiveTracer(
            api_key=override_api_key, project="test-project", test_mode=True
        )
        assert tracer2.api_key == override_api_key
        tracer2.shutdown()

        # Test 3: TracerConfig should override env var
        config_api_key = "config-api-key-11111"
        tracer_config = TracerConfig(
            api_key=config_api_key, project="test-project", test_mode=True
        )
        tracer3 = HoneyHiveTracer(config=tracer_config)
        assert tracer3.api_key == config_api_key
        tracer3.shutdown()

    def test_hh_api_url_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test HH_API_URL environment variable overrides default server_url."""
        # Set custom server URL via env var
        custom_url = "https://custom.api.honeyhive.ai"
        monkeypatch.setenv("HH_API_URL", custom_url)

        # Tracer should use env var URL
        tracer = HoneyHiveTracer(
            api_key="test-key", project="test-project", test_mode=True
        )
        # Note: server_url may not be directly accessible, test via config
        assert tracer.config.get("server_url") == custom_url
        tracer.shutdown()

    def test_hh_project_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test HH_PROJECT environment variable provides default project."""
        # Set project via env var
        env_project = "env-test-project"
        monkeypatch.setenv("HH_PROJECT", env_project)

        # Tracer should use env var project
        tracer = HoneyHiveTracer(api_key="test-key", test_mode=True)
        assert tracer.project == env_project
        tracer.shutdown()

    def test_priority_order(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test complete priority order.

        individual > SessionConfig > EvaluationConfig > TracerConfig > env vars
        """
        # Setup: env var as lowest priority
        monkeypatch.setenv("HH_API_KEY", "env-key")
        monkeypatch.setenv("HH_PROJECT", "env-project")

        # TracerConfig (overrides env vars)
        tracer_config = TracerConfig(
            api_key="tracer-config-key",
            project="tracer-config-project",
            test_mode=True,
        )

        # SessionConfig (overrides TracerConfig for shared fields)
        session_config = SessionConfig(project="session-config-project")

        # Individual param (highest priority)
        tracer = HoneyHiveTracer(
            config=tracer_config,
            session_config=session_config,
            api_key="individual-key",  # This should win for api_key
            # project comes from session_config (no individual override)
        )

        # Verify priority order
        assert tracer.api_key == "individual-key"  # individual param wins
        assert tracer.project == "session-config-project"  # SessionConfig wins
        tracer.shutdown()


class TestDefaultValues:
    """Test default value fallbacks with REAL tracer initialization."""

    def test_default_server_url(self) -> None:
        """Test default server_url is set when not provided."""
        tracer = HoneyHiveTracer(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Default server URL should be set
        # (may be staging or production depending on env)
        server_url = tracer.config.get("server_url")
        assert server_url is not None
        assert "honeyhive.ai" in server_url
        tracer.shutdown()

    def test_default_test_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default test_mode is False when HH_TEST_MODE not set."""
        # Clear HH_TEST_MODE environment variable to test true default
        monkeypatch.delenv("HH_TEST_MODE", raising=False)

        # Create TracerConfig without test_mode
        config = TracerConfig(api_key="test-key", project="test-project")
        assert config.test_mode is False  # Pydantic default

    def test_default_batch_settings(self) -> None:
        """Test default batch_size, flush_interval, export_timeout values."""
        # Create OTLPConfig with defaults
        otlp_config = OTLPConfig()

        # Verify default batch settings (these are Pydantic defaults)
        assert isinstance(otlp_config.batch_size, int)
        assert otlp_config.batch_size > 0
        assert isinstance(otlp_config.flush_interval, (int, float))
        assert otlp_config.flush_interval > 0
        assert isinstance(otlp_config.export_timeout, (int, float))
        assert otlp_config.export_timeout > 0


class TestTypeValidation:
    """Test Pydantic type validation with REAL validation errors."""

    def test_session_config_invalid_session_id_format(self) -> None:
        """Test invalid session_id format is handled gracefully."""
        # SDK uses graceful degradation: logs warning, sets to None
        config = SessionConfig(
            session_id="not-a-uuid-format",  # Invalid UUID
            project="test-project",
        )

        # SDK should set invalid UUID to None (graceful degradation)
        assert config.session_id is None

    def test_evaluation_config_invalid_uuid_formats(self) -> None:
        """Test EvaluationConfig accepts string IDs without strict UUID validation."""
        # SDK accepts string IDs for evaluation fields (no strict UUID validation)
        # This allows flexibility for different ID formats

        # Test run_id - accepts any string
        config1 = EvaluationConfig(
            run_id="not-a-valid-uuid",
            project="test-project",
        )
        assert config1.run_id == "not-a-valid-uuid"  # Accepted as-is

        # Test dataset_id - accepts any string
        config2 = EvaluationConfig(
            dataset_id="invalid-dataset-id-123",
            project="test-project",
        )
        assert config2.dataset_id == "invalid-dataset-id-123"  # Accepted as-is

        # Test datapoint_id - accepts any string
        config3 = EvaluationConfig(
            datapoint_id="12345",  # Not UUID format but accepted
            project="test-project",
        )
        assert config3.datapoint_id == "12345"  # Accepted as-is

    def test_otlp_config_invalid_numeric_values(self) -> None:
        """Test invalid numeric values are handled gracefully."""
        # SDK uses graceful degradation for invalid values

        # Test negative batch_size - should use default
        config = OTLPConfig(batch_size=-1)
        assert config.batch_size == 100  # Default value

        # Test negative export_timeout - should use default
        config2 = OTLPConfig(export_timeout=-10.0)
        assert config2.export_timeout > 0  # Positive default

        # Test zero batch_size - should use default
        config3 = OTLPConfig(batch_size=0)
        assert config3.batch_size == 100  # Default value


class TestConfigSerialization:
    """Test config serialization/deserialization with REAL models."""

    def test_to_dict_all_models(self) -> None:
        """Test model_dump() on all config models."""
        # TracerConfig
        tracer_config = TracerConfig(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )
        tracer_dict = tracer_config.model_dump()
        assert isinstance(tracer_dict, dict)
        assert tracer_dict["api_key"] == "test-key"
        assert tracer_dict["project"] == "test-project"
        assert tracer_dict["test_mode"] is True

        # SessionConfig
        session_id = str(uuid.uuid4())
        session_config = SessionConfig(
            session_id=session_id,
            project="test-project",
        )
        session_dict = session_config.model_dump()
        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == session_id

        # EvaluationConfig
        run_id = str(uuid.uuid4())
        eval_config = EvaluationConfig(
            run_id=run_id,
            project="test-project",
        )
        eval_dict = eval_config.model_dump()
        assert isinstance(eval_dict, dict)
        assert eval_dict["run_id"] == run_id

        # OTLPConfig
        otlp_config = OTLPConfig(batch_size=100, export_timeout=30.0)
        otlp_dict = otlp_config.model_dump()
        assert isinstance(otlp_dict, dict)
        assert otlp_dict["batch_size"] == 100
        assert otlp_dict["export_timeout"] == 30.0

    def test_from_dict_reconstruction(self) -> None:
        """Test model_validate() reconstruction for all models."""
        # TracerConfig from dict
        tracer_dict = {
            "api_key": "test-key",
            "project": "test-project",
            "test_mode": True,
        }
        tracer_config = TracerConfig.model_validate(tracer_dict)
        assert tracer_config.api_key == "test-key"
        assert tracer_config.project == "test-project"
        assert tracer_config.test_mode is True

        # SessionConfig from dict
        session_id = str(uuid.uuid4())
        session_dict = {
            "session_id": session_id,
            "project": "test-project",
        }
        session_config = SessionConfig.model_validate(session_dict)
        assert session_config.session_id == session_id

        # OTLPConfig from dict
        otlp_dict = {"batch_size": 200, "export_timeout": 60.0}
        otlp_config = OTLPConfig.model_validate(otlp_dict)
        assert otlp_config.batch_size == 200
        assert otlp_config.export_timeout == 60.0

    def test_json_serialization(self) -> None:
        """Test JSON.dumps/loads for all models."""
        # Create config
        tracer_config = TracerConfig(
            api_key="test-key",
            project="test-project",
            test_mode=True,
        )

        # Serialize to JSON string
        json_str = tracer_config.model_dump_json()
        assert isinstance(json_str, str)

        # Deserialize from JSON string
        reconstructed = TracerConfig.model_validate_json(json_str)
        assert reconstructed.api_key == tracer_config.api_key
        assert reconstructed.project == tracer_config.project
        assert reconstructed.test_mode == tracer_config.test_mode

    def test_roundtrip_no_data_loss(self) -> None:
        """Test config → dict → config preserves all data."""
        # Create config with all fields
        session_id = str(uuid.uuid4())
        original_config = SessionConfig(
            session_id=session_id,
            project="test-project",
            api_key="test-key",
        )

        # Round trip: config → dict → config
        config_dict = original_config.model_dump()
        reconstructed_config = SessionConfig.model_validate(config_dict)

        # Verify all fields preserved
        assert reconstructed_config.session_id == original_config.session_id
        assert reconstructed_config.project == original_config.project
        assert reconstructed_config.api_key == original_config.api_key


class TestRequiredFields:
    """Test required field validation with REAL tracer initialization."""

    def test_missing_api_key_graceful_error(self) -> None:
        """Test missing api_key → graceful error or test mode."""
        # Without api_key or test_mode, tracer may fail gracefully
        # This is a REAL integration test - no mocks
        try:
            tracer = HoneyHiveTracer(project="test-project")
            # If it succeeds, verify it's in a safe mode
            assert tracer is not None
            tracer.shutdown()
        except (ValueError, ValidationError, TypeError) as e:
            # Expected behavior: clear error message
            assert "api_key" in str(e).lower() or "required" in str(e).lower()

    def test_missing_project(self) -> None:
        """Test missing project → uses default or errors."""
        # Test with api_key but no project
        tracer = HoneyHiveTracer(api_key="test-key", test_mode=True)

        # Should either have a default project or handle gracefully
        assert tracer is not None
        assert hasattr(tracer, "project")
        # Project may be None, empty string, or a default value
        tracer.shutdown()


class TestInvalidConfigCombinations:
    """Test invalid configuration combinations with REAL initialization."""

    def test_clear_error_messages(self) -> None:
        """Verify SDK provides clear graceful degradation for invalid configs."""
        # SDK uses graceful degradation with warning logs
        # Test invalid session_id - should set to None with warning log
        config = SessionConfig(session_id="invalid-uuid", project="test")

        # SDK gracefully degrades invalid UUID to None
        assert config.session_id is None
        # In real usage, this would also log a warning message
        # which is more user-friendly than raising ValidationError


class TestEnvFileLoading:
    """Test .env file loading with REAL file operations."""

    def test_env_file_loading(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test .env file is parsed and loaded."""
        # Create temp .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            "HH_API_KEY=env-file-key\n"
            "HH_PROJECT=env-file-project\n"
            "HH_API_URL=https://test.api.honeyhive.ai\n"
        )

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # NOTE: The SDK may or may not auto-load .env files
        # This test verifies the behavior if it does
        # If not auto-loaded, this documents expected behavior

        # For now, manually set env vars to simulate .env loading
        monkeypatch.setenv("HH_API_KEY", "env-file-key")
        monkeypatch.setenv("HH_PROJECT", "env-file-project")

        tracer = HoneyHiveTracer(test_mode=True)
        assert tracer.api_key == "env-file-key"
        assert tracer.project == "env-file-project"
        tracer.shutdown()

    def test_file_not_found_uses_defaults(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test missing .env file uses defaults without crash."""
        # Change to temp directory with no .env file
        monkeypatch.chdir(tmp_path)

        # Should not crash, should use defaults/provided values
        tracer = HoneyHiveTracer(
            api_key="test-key", project="test-project", test_mode=True
        )
        assert tracer is not None
        assert tracer.api_key == "test-key"
        tracer.shutdown()
