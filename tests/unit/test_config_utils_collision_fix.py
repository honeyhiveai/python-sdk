"""Unit tests for config collision fix in create_unified_config.

This module tests the fix for the field collision bug where SessionConfig and
EvaluationConfig values were not properly promoted to root level, causing
them to be hidden in nested namespaces.

Bug Reference: User reported session_id from SessionConfig not being used.
Root Cause: create_unified_config() didn't handle colliding fields between
TracerConfig and specialized configs (SessionConfig/EvaluationConfig).
"""

# pylint: disable=protected-access
# Justification: Testing requires verification of internal config structure

from honeyhive.config.models.tracer import (
    EvaluationConfig,
    SessionConfig,
    TracerConfig,
)
from honeyhive.config.utils import create_unified_config


class TestSessionConfigCollisionFix:
    """Test SessionConfig field collision fixes."""

    def test_session_id_collision_fix(self) -> None:
        """Test session_id from SessionConfig overrides TracerConfig at root.

        This is the originally reported bug - session_id from SessionConfig
        was hidden in config.session.session_id and not available at root.
        """
        tracer_config = TracerConfig(api_key="test", project="test")
        session_config = SessionConfig(
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        # Root level should have SessionConfig value
        assert unified.get("session_id") == "550e8400-e29b-41d4-a716-446655440000"
        # Nested level should also have it
        assert (
            unified.session.get("session_id") == "550e8400-e29b-41d4-a716-446655440000"
        )

    def test_api_key_collision_priority(self) -> None:
        """Test api_key from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="tracer_key", project="test")
        session_config = SessionConfig(api_key="session_key")

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        # SessionConfig should win
        assert unified.get("api_key") == "session_key"
        assert unified.session.get("api_key") == "session_key"

    def test_project_collision_priority(self) -> None:
        """Test project from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="tracer_project")
        session_config = SessionConfig(project="session_project")

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("project") == "session_project"
        assert unified.session.get("project") == "session_project"

    def test_inputs_collision_priority(self) -> None:
        """Test inputs from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(
            api_key="test", project="test", inputs={"tracer": "input"}
        )
        session_config = SessionConfig(inputs={"session": "input"})

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("inputs") == {"session": "input"}
        assert unified.session.get("inputs") == {"session": "input"}

    def test_link_carrier_collision_priority(self) -> None:
        """Test link_carrier from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(
            api_key="test", project="test", link_carrier={"tracer": "carrier"}
        )
        session_config = SessionConfig(link_carrier={"session": "carrier"})

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("link_carrier") == {"session": "carrier"}
        assert unified.session.get("link_carrier") == {"session": "carrier"}

    def test_test_mode_collision_priority(self) -> None:
        """Test test_mode from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="test", test_mode=False)
        session_config = SessionConfig(test_mode=True)

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("test_mode") is True
        assert unified.session.get("test_mode") is True

    def test_verbose_collision_priority(self) -> None:
        """Test verbose from SessionConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="test", verbose=False)
        session_config = SessionConfig(verbose=True)

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("verbose") is True
        assert unified.session.get("verbose") is True


class TestEvaluationConfigCollisionFix:
    """Test EvaluationConfig field collision fixes."""

    def test_is_evaluation_collision_priority(self) -> None:
        """Test is_evaluation from EvaluationConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(
            api_key="test", project="test", is_evaluation=False
        )
        eval_config = EvaluationConfig(is_evaluation=True)

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert unified.get("is_evaluation") is True
        assert unified.evaluation.get("is_evaluation") is True

    def test_run_id_collision_priority(self) -> None:
        """Test run_id from EvaluationConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="test", run_id=None)
        eval_config = EvaluationConfig(run_id="eval_run_123")

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert unified.get("run_id") == "eval_run_123"
        assert unified.evaluation.get("run_id") == "eval_run_123"

    def test_dataset_id_collision_priority(self) -> None:
        """Test dataset_id from EvaluationConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="test", dataset_id=None)
        eval_config = EvaluationConfig(dataset_id="dataset_456")

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert unified.get("dataset_id") == "dataset_456"
        assert unified.evaluation.get("dataset_id") == "dataset_456"

    def test_datapoint_id_collision_priority(self) -> None:
        """Test datapoint_id from EvaluationConfig overrides TracerConfig at root."""
        tracer_config = TracerConfig(api_key="test", project="test", datapoint_id=None)
        eval_config = EvaluationConfig(datapoint_id="datapoint_789")

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert unified.get("datapoint_id") == "datapoint_789"
        assert unified.evaluation.get("datapoint_id") == "datapoint_789"


class TestConfigPriorityOrder:
    """Test the complete priority order for colliding fields."""

    def test_session_config_overrides_tracer_config(self) -> None:
        """Test SessionConfig takes priority over TracerConfig."""
        tracer_config = TracerConfig(api_key="tracer_key", project="test")
        session_config = SessionConfig(api_key="session_key")

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert unified.get("api_key") == "session_key"

    def test_evaluation_config_overrides_tracer_config(self) -> None:
        """Test EvaluationConfig takes priority over TracerConfig."""
        tracer_config = TracerConfig(
            api_key="tracer_key", project="test", is_evaluation=False
        )
        eval_config = EvaluationConfig(api_key="eval_key", is_evaluation=True)

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert unified.get("api_key") == "eval_key"
        assert unified.get("is_evaluation") is True

    def test_session_config_overrides_evaluation_config(self) -> None:
        """Test SessionConfig takes priority over EvaluationConfig for shared fields."""
        tracer_config = TracerConfig(api_key="tracer_key", project="test")
        session_config = SessionConfig(api_key="session_key", verbose=True)
        eval_config = EvaluationConfig(api_key="eval_key", verbose=False)

        unified = create_unified_config(
            config=tracer_config,
            session_config=session_config,
            evaluation_config=eval_config,
        )

        # SessionConfig should win for shared fields
        assert unified.get("api_key") == "session_key"
        assert unified.get("verbose") is True

    def test_individual_params_override_all(self) -> None:
        """Test individual params have highest priority (backwards compatibility)."""
        tracer_config = TracerConfig(api_key="tracer_key", project="test")
        session_config = SessionConfig(api_key="session_key")

        unified = create_unified_config(
            config=tracer_config,
            session_config=session_config,
            api_key="individual_key",
        )

        # Individual param should override everything
        assert unified.get("api_key") == "individual_key"


class TestNoCollisionWhenConfigNotProvided:
    """Test that promotion only happens when specialized configs are provided."""

    def test_no_session_config_no_promotion(self) -> None:
        """Test that empty SessionConfig defaults don't override TracerConfig."""
        tracer_config = TracerConfig(api_key="tracer_key", project="test", verbose=True)

        # Don't provide session_config - should use tracer_config values
        unified = create_unified_config(config=tracer_config)

        assert unified.get("verbose") is True  # From TracerConfig
        assert unified.get("api_key") == "tracer_key"  # From TracerConfig

    def test_no_evaluation_config_no_promotion(self) -> None:
        """Test that empty EvaluationConfig defaults don't override TracerConfig."""
        tracer_config = TracerConfig(
            api_key="tracer_key", project="test", is_evaluation=True, verbose=True
        )

        # Don't provide evaluation_config - should use tracer_config values
        unified = create_unified_config(config=tracer_config)

        assert unified.get("is_evaluation") is True  # From TracerConfig
        assert unified.get("verbose") is True  # From TracerConfig


class TestNestedValuesAlwaysPresent:
    """Test that values are present in both root and nested locations."""

    def test_session_values_in_both_locations(self) -> None:
        """Test SessionConfig values accessible from both root and nested."""
        session_config = SessionConfig(
            session_id="550e8400-e29b-41d4-a716-446655440000", inputs={"user": "test"}
        )

        unified = create_unified_config(session_config=session_config)

        # Root level
        assert unified.get("session_id") == "550e8400-e29b-41d4-a716-446655440000"
        assert unified.get("inputs") == {"user": "test"}

        # Nested level
        assert (
            unified.session.get("session_id") == "550e8400-e29b-41d4-a716-446655440000"
        )
        assert unified.session.get("inputs") == {"user": "test"}

    def test_evaluation_values_in_both_locations(self) -> None:
        """Test EvaluationConfig values accessible from both root and nested."""
        eval_config = EvaluationConfig(
            is_evaluation=True, run_id="run_123", dataset_id="dataset_456"
        )

        unified = create_unified_config(evaluation_config=eval_config)

        # Root level
        assert unified.get("is_evaluation") is True
        assert unified.get("run_id") == "run_123"
        assert unified.get("dataset_id") == "dataset_456"

        # Nested level
        assert unified.evaluation.get("is_evaluation") is True
        assert unified.evaluation.get("run_id") == "run_123"
        assert unified.evaluation.get("dataset_id") == "dataset_456"
