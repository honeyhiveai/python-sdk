"""Unit tests for HoneyHive config utilities functionality.

This module tests the configuration utility functions including config merging,
parameter handling, and configuration transformation utilities.

Test Coverage:
- merge_configs_with_params function with all parameter combinations
- create_unified_config function with nested structure creation
- Edge cases, error handling, and backwards compatibility

Following Agent OS testing standards with proper fixtures and isolation.
Generated using enhanced comprehensive analysis framework for 90%+ coverage.
"""

# pylint: disable=too-many-lines,line-too-long,redefined-outer-name,unused-variable
# Reason: Comprehensive testing file requires extensive test coverage for 90%+ target
# Line length disabled for test readability and comprehensive assertions
# Redefined outer name disabled for pytest fixture usage pattern
# Unused variable disabled for tuple unpacking in test assertions

import os
from unittest.mock import patch

from honeyhive.config.models.tracer import (
    EvaluationConfig,
    SessionConfig,
    TracerConfig,
)
from honeyhive.config.utils import create_unified_config, merge_configs_with_params
from honeyhive.utils.dotdict import DotDict


class TestMergeConfigsWithParams:
    """Test the merge_configs_with_params utility function."""

    def test_merge_with_no_config_only_params(self) -> None:
        """Test merging when only parameters are provided (no config object)."""
        params = {
            "api_key": "param_api_key",
            "project": "param_project",
            "source": "param_source",
            "verbose": True,
        }

        tracer_config, session_config, eval_config = merge_configs_with_params(
            None, **params
        )

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.api_key == "param_api_key"
        assert tracer_config.project == "param_project"
        assert tracer_config.source == "param_source"
        assert tracer_config.verbose is True
        assert isinstance(session_config, SessionConfig)
        assert isinstance(eval_config, EvaluationConfig)

    def test_merge_with_config_only_no_params(self) -> None:
        """Test merging when only config object is provided (no parameters)."""
        config = TracerConfig(
            api_key="config_api_key",
            project="config_project",
            source="config_source",
            verbose=False,
        )

        tracer_config, session_config, eval_config = merge_configs_with_params(config)

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.api_key == "config_api_key"
        assert tracer_config.project == "config_project"
        assert tracer_config.source == "config_source"
        assert tracer_config.verbose is False
        assert isinstance(session_config, SessionConfig)
        assert isinstance(eval_config, EvaluationConfig)

    def test_merge_with_config_and_params_override(self) -> None:
        """Test merging where parameters override config values."""
        config = TracerConfig(
            api_key="config_api_key",
            project="config_project",
            source="config_source",
            verbose=False,
        )

        params = {
            "api_key": "param_api_key",  # Should override config
            "verbose": True,  # Should override config
            "session_name": "param_session",  # Should be added
        }

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **params
        )

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.api_key == "param_api_key"  # Overridden
        assert tracer_config.project == "config_project"  # From config
        assert tracer_config.source == "config_source"  # From config
        assert tracer_config.verbose is True  # Overridden
        assert tracer_config.session_name == "param_session"  # Added

    def test_merge_with_config_and_params_addition(self) -> None:
        """Test merging where parameters add new fields to config."""
        config = TracerConfig(api_key="config_api_key", project="config_project")

        params = {
            "source": "param_source",
            "session_name": "param_session",
            "disable_batch": True,
        }

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **params
        )

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.api_key == "config_api_key"  # From config
        assert tracer_config.project == "config_project"  # From config
        assert tracer_config.source == "param_source"  # Added
        assert tracer_config.session_name == "param_session"  # Added
        assert tracer_config.disable_batch is True  # Added

    def test_merge_preserves_config_defaults(self) -> None:
        """Test that merging preserves config default values."""
        # Clear environment to ensure clean defaults
        with patch.dict(os.environ, {}, clear=True):
            config = TracerConfig(
                api_key="config_api_key",
                project="config_project",
                # Other fields should have defaults
            )

            params = {"verbose": True}  # Only override one field

            tracer_config, session_config, eval_config = merge_configs_with_params(
                config, **params
            )

            assert isinstance(tracer_config, TracerConfig)
            assert tracer_config.api_key == "config_api_key"
            assert tracer_config.project == "config_project"
            assert tracer_config.verbose is True  # Overridden
            assert tracer_config.source == "dev"  # Default preserved
            assert tracer_config.disable_http_tracing is True  # Default preserved
            assert tracer_config.disable_batch is False  # Default preserved

    def test_merge_with_empty_params(self) -> None:
        """Test merging with empty parameters dictionary."""
        config = TracerConfig(
            api_key="config_api_key", project="config_project", verbose=True
        )

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **{}
        )

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.api_key == "config_api_key"
        assert tracer_config.project == "config_project"
        assert tracer_config.verbose is True
        # Should be identical to original config

    def test_merge_with_session_config_provided(self) -> None:
        """Test merging when session_config is provided."""
        tracer_config = TracerConfig(api_key="api_key", project="project")
        session_config = SessionConfig(
            api_key="session_api_key", project="session_project"
        )

        result_tracer, result_session, result_eval = merge_configs_with_params(
            config=tracer_config, session_config=session_config
        )

        assert isinstance(result_tracer, TracerConfig)
        assert isinstance(result_session, SessionConfig)
        assert isinstance(result_eval, EvaluationConfig)
        assert result_session.api_key == "session_api_key"
        assert result_session.project == "session_project"

    def test_merge_with_evaluation_config_provided(self) -> None:
        """Test merging when evaluation_config is provided."""
        tracer_config = TracerConfig(api_key="api_key", project="project")
        eval_config = EvaluationConfig(api_key="eval_api_key", project="eval_project")

        result_tracer, result_session, result_eval = merge_configs_with_params(
            config=tracer_config, evaluation_config=eval_config
        )

        assert isinstance(result_tracer, TracerConfig)
        assert isinstance(result_session, SessionConfig)
        assert isinstance(result_eval, EvaluationConfig)
        assert result_eval.api_key == "eval_api_key"
        assert result_eval.project == "eval_project"

    def test_merge_with_all_configs_provided(self) -> None:
        """Test merging when all config objects are provided."""
        tracer_config = TracerConfig(api_key="tracer_key", project="tracer_project")
        session_config = SessionConfig(api_key="session_key", project="session_project")
        eval_config = EvaluationConfig(api_key="eval_key", project="eval_project")

        result_tracer, result_session, result_eval = merge_configs_with_params(
            config=tracer_config,
            session_config=session_config,
            evaluation_config=eval_config,
        )

        assert result_tracer.api_key == "tracer_key"
        assert result_session.api_key == "session_key"
        assert result_eval.api_key == "eval_key"

    def test_merge_with_session_params_override(self) -> None:
        """Test merging where session parameters override session config."""
        session_config = SessionConfig(api_key="session_key", project="session_project")

        # Session-specific parameters
        params = {
            "api_key": "override_key",  # Should override session config
            "inputs": {"user": "test_user"},  # Session-specific field
        }

        result_tracer, result_session, result_eval = merge_configs_with_params(
            session_config=session_config, **params
        )

        # Tracer config should get the override
        assert result_tracer.api_key == "override_key"
        # Session config should also get the override
        assert result_session.api_key == "override_key"
        assert result_session.inputs == {"user": "test_user"}

    def test_merge_with_evaluation_params_override(self) -> None:
        """Test merging where evaluation parameters override evaluation config."""
        eval_config = EvaluationConfig(api_key="eval_key", project="eval_project")

        # Evaluation-specific parameters would go here if they existed
        # For now, test with common parameters
        params = {
            "api_key": "override_key",
            "project": "override_project",
        }

        result_tracer, result_session, result_eval = merge_configs_with_params(
            evaluation_config=eval_config, **params
        )

        assert result_tracer.api_key == "override_key"
        assert result_eval.api_key == "override_key"
        assert result_eval.project == "override_project"

    def test_merge_parameter_precedence_order(self) -> None:
        """Test that parameter precedence follows expected order."""
        config = TracerConfig(
            api_key="config_api_key",
            project="config_project",
            source="config_source",
            verbose=False,
        )

        # Parameters should have highest precedence
        params = {"api_key": "param_api_key", "source": "param_source", "verbose": True}

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **params
        )

        # All parameters should override config values
        assert tracer_config.api_key == "param_api_key"
        assert tracer_config.source == "param_source"
        assert tracer_config.verbose is True
        # Non-overridden config value should remain
        assert tracer_config.project == "config_project"

    def test_merge_with_boolean_values(self) -> None:
        """Test merging handles boolean values correctly."""
        config = TracerConfig(api_key="config_api_key", project="config_project")

        # Test actual boolean values (not string conversion)
        boolean_params = [
            ({"verbose": True}, True),
            ({"verbose": False}, False),
            ({"test_mode": True}, True),
            ({"test_mode": False}, False),
        ]

        for params, expected_value in boolean_params:
            tracer_config, session_config, eval_config = merge_configs_with_params(
                config, **params
            )

            if "verbose" in params:
                assert tracer_config.verbose == expected_value
            if "test_mode" in params:
                assert tracer_config.test_mode == expected_value

    def test_merge_with_none_config_and_minimal_params(self) -> None:
        """Test merging with None config and minimal valid parameters."""
        # Clear environment to ensure clean defaults
        with patch.dict(os.environ, {}, clear=True):
            minimal_params = {
                "api_key": "minimal_api_key",
                "project": "minimal_project",
            }

            tracer_config, session_config, eval_config = merge_configs_with_params(
                None, **minimal_params
            )

            assert isinstance(tracer_config, TracerConfig)
            assert tracer_config.api_key == "minimal_api_key"
            assert tracer_config.project == "minimal_project"
            # Other fields should have defaults
            assert tracer_config.source == "dev"  # Default value
            assert tracer_config.verbose is False  # Default value

    def test_merge_idempotency(self) -> None:
        """Test that merging is idempotent when no changes are made."""
        config = TracerConfig(
            api_key="test_api_key",
            project="test_project",
            source="test_source",
            verbose=True,
        )

        # Merge with same values
        same_params = {
            "api_key": "test_api_key",
            "project": "test_project",
            "source": "test_source",
            "verbose": True,
        }

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **same_params
        )

        # Result should have same values
        assert tracer_config.api_key == config.api_key
        assert tracer_config.project == config.project
        assert tracer_config.source == config.source
        assert tracer_config.verbose == config.verbose

    def test_merge_with_unknown_params_ignored(self) -> None:
        """Test merging behavior with unknown/extra parameters."""
        config = TracerConfig(api_key="config_api_key", project="config_project")

        # Include unknown parameter
        params_with_unknown = {
            "source": "valid_source",
            "unknown_param": "should_be_ignored",  # This gets ignored
        }

        # Unknown parameters are ignored by the merge function
        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **params_with_unknown
        )
        assert tracer_config.source == "valid_source"
        assert not hasattr(tracer_config, "unknown_param")

    def test_merge_with_complex_data_types(self) -> None:
        """Test merging with complex data types in parameters."""
        config = TracerConfig(api_key="config_api_key", project="config_project")

        # Test with complex session data
        params = {
            "source": "complex_source",
            "verbose": True,
            "inputs": {"nested": {"key": "value"}},  # Complex data for session
        }

        tracer_config, session_config, eval_config = merge_configs_with_params(
            config, **params
        )

        assert isinstance(tracer_config, TracerConfig)
        assert tracer_config.source == "complex_source"
        assert tracer_config.verbose is True
        # inputs should go to session config
        assert session_config.inputs == {"nested": {"key": "value"}}


class TestCreateUnifiedConfig:
    """Test the create_unified_config utility function."""

    def test_create_unified_config_with_tracer_config_only(self) -> None:
        """Test creating unified config with only tracer config."""
        config = TracerConfig(
            api_key="test_api_key",
            project="test_project",
            source="test_source",
            verbose=True,
        )

        unified = create_unified_config(config=config)

        assert isinstance(unified, DotDict)
        # TracerConfig fields at root level
        assert unified.api_key == "test_api_key"
        assert unified.project == "test_project"
        assert unified.source == "test_source"
        assert unified.verbose is True

        # Nested configs should exist
        assert isinstance(unified.http, DotDict)
        assert isinstance(unified.otlp, DotDict)
        assert isinstance(unified.api, DotDict)
        assert isinstance(unified.experiment, DotDict)
        assert isinstance(unified.session, DotDict)
        assert isinstance(unified.evaluation, DotDict)

    def test_create_unified_config_with_session_config(self) -> None:
        """Test creating unified config with session config.

        SessionConfig values should override TracerConfig at root level for colliding fields.
        This is the correct behavior after the field collision fix.
        """
        tracer_config = TracerConfig(api_key="tracer_key", project="tracer_project")
        session_config = SessionConfig(
            api_key="session_key",
            project="session_project",
            inputs={"user": "test_user"},
        )

        unified = create_unified_config(
            config=tracer_config, session_config=session_config
        )

        assert isinstance(unified, DotDict)
        # Root level should have SESSION config values (more specific wins)
        assert unified.api_key == "session_key"
        assert unified.project == "session_project"

        # Session config should also be in nested location
        assert unified.session.api_key == "session_key"
        assert unified.session.project == "session_project"
        assert unified.session.inputs == {"user": "test_user"}

    def test_create_unified_config_with_evaluation_config(self) -> None:
        """Test creating unified config with evaluation config.

        EvaluationConfig values should override TracerConfig at root level for colliding fields.
        """
        tracer_config = TracerConfig(api_key="tracer_key", project="tracer_project")
        eval_config = EvaluationConfig(api_key="eval_key", project="eval_project")

        unified = create_unified_config(
            config=tracer_config, evaluation_config=eval_config
        )

        assert isinstance(unified, DotDict)
        # Root level should have EVALUATION config values (more specific wins)
        assert unified.api_key == "eval_key"
        assert unified.project == "eval_project"

        # Evaluation config should also be in nested location
        assert unified.evaluation.api_key == "eval_key"
        assert unified.evaluation.project == "eval_project"

    def test_create_unified_config_with_all_configs(self) -> None:
        """Test creating unified config with all config types.

        Priority order: SessionConfig > EvaluationConfig > TracerConfig for colliding fields.
        """
        tracer_config = TracerConfig(api_key="tracer_key", project="tracer_project")
        session_config = SessionConfig(api_key="session_key", inputs={"user": "test"})
        eval_config = EvaluationConfig(api_key="eval_key")

        unified = create_unified_config(
            config=tracer_config,
            session_config=session_config,
            evaluation_config=eval_config,
        )

        assert isinstance(unified, DotDict)
        # Root level should have SESSION config api_key (highest priority for shared fields)
        assert unified.api_key == "session_key"
        # Values should also exist in nested locations
        assert unified.session.api_key == "session_key"
        assert unified.session.inputs == {"user": "test"}
        assert unified.evaluation.api_key == "eval_key"

    def test_create_unified_config_with_individual_params(self) -> None:
        """Test creating unified config with individual parameters."""
        params = {
            "api_key": "param_key",
            "project": "param_project",
            "verbose": True,
            "inputs": {"user": "param_user"},  # Should go to session
        }

        unified = create_unified_config(**params)

        assert isinstance(unified, DotDict)
        # Root level tracer params
        assert unified.api_key == "param_key"
        assert unified.project == "param_project"
        assert unified.verbose is True

        # Session params should be nested
        assert unified.session.inputs == {"user": "param_user"}

    def test_create_unified_config_parameter_routing(self) -> None:
        """Test that parameters are routed to correct nested configs."""
        # Test parameters that should go to different config sections
        params = {
            # TracerConfig params (should go to root)
            "api_key": "root_key",
            "project": "root_project",
            "verbose": True,
            # SessionConfig params (should go to session)
            "inputs": {"session": "data"},
            # Unknown params (should go to root)
            "unknown_param": "unknown_value",
        }

        unified = create_unified_config(**params)

        # Root level
        assert unified.api_key == "root_key"
        assert unified.project == "root_project"
        assert unified.verbose is True
        assert unified.unknown_param == "unknown_value"

        # Session level
        assert unified.session.inputs == {"session": "data"}

    def test_create_unified_config_dot_notation_access(self) -> None:
        """Test that unified config supports dot notation access."""
        config = TracerConfig(api_key="test_key", project="test_project")

        unified = create_unified_config(config=config)

        # Test dot notation access
        assert unified.api_key == "test_key"
        assert unified.project == "test_project"
        assert unified.http.timeout is not None  # Default HTTP config
        assert unified.otlp.batch_size is not None  # Default OTLP config

        # Test nested access
        assert hasattr(unified.session, "api_key")
        assert hasattr(unified.evaluation, "api_key")

    def test_create_unified_config_dictionary_access(self) -> None:
        """Test that unified config supports dictionary-style access."""
        config = TracerConfig(api_key="test_key", project="test_project")

        unified = create_unified_config(config=config)

        # Test dictionary access
        assert unified["api_key"] == "test_key"
        assert unified["project"] == "test_project"
        assert unified["http"]["timeout"] is not None
        # Session config should have default values
        assert "api_key" in unified["session"]

    def test_create_unified_config_empty_inputs(self) -> None:
        """Test creating unified config with no inputs."""
        unified = create_unified_config()

        assert isinstance(unified, DotDict)
        # Should have default structure
        assert isinstance(unified.http, DotDict)
        assert isinstance(unified.otlp, DotDict)
        assert isinstance(unified.api, DotDict)
        assert isinstance(unified.experiment, DotDict)
        assert isinstance(unified.session, DotDict)
        assert isinstance(unified.evaluation, DotDict)

    def test_create_unified_config_none_configs(self) -> None:
        """Test creating unified config with None config objects."""
        unified = create_unified_config(
            config=None, session_config=None, evaluation_config=None
        )

        assert isinstance(unified, DotDict)
        # Should still have nested structure
        assert isinstance(unified.session, DotDict)
        assert isinstance(unified.evaluation, DotDict)

    def test_create_unified_config_override_precedence(self) -> None:
        """Test that individual params override config objects."""
        config = TracerConfig(api_key="config_key", project="config_project")
        session_config = SessionConfig(api_key="session_key")

        # Individual params should override
        params = {
            "api_key": "override_key",
            "inputs": {"override": "data"},
        }

        unified = create_unified_config(
            config=config, session_config=session_config, **params
        )

        # Root level should have override
        assert unified.api_key == "override_key"
        assert unified.project == "config_project"  # Not overridden

        # Session should have override
        assert unified.session.inputs == {"override": "data"}

    def test_create_unified_config_nested_structure_integrity(self) -> None:
        """Test that nested structure maintains integrity."""
        unified = create_unified_config(
            api_key="test_key",
            inputs={"session": "data"},
        )

        # Verify nested structures are independent
        unified.session.new_field = "session_value"
        unified.http.new_field = "http_value"

        assert unified.session.new_field == "session_value"
        assert unified.http.new_field == "http_value"
        assert not hasattr(unified.otlp, "new_field")

    def test_create_unified_config_complex_nested_data(self) -> None:
        """Test unified config with complex nested data structures."""
        complex_params = {
            "api_key": "complex_key",
            "inputs": {"nested": {"deep": {"structure": "value"}}},
        }

        unified = create_unified_config(**complex_params)

        assert unified.api_key == "complex_key"
        assert unified.session.inputs["nested"]["deep"]["structure"] == "value"

        # Test dot notation access to nested data
        assert unified.session.inputs.nested.deep.structure == "value"

    def test_create_unified_config_all_default_configs_present(self) -> None:
        """Test that all expected default config sections are present."""
        unified = create_unified_config()

        # Verify all expected sections exist
        expected_sections = [
            "http",
            "otlp",
            "api",
            "experiment",
            "session",
            "evaluation",
        ]

        for section in expected_sections:
            assert hasattr(unified, section)
            assert isinstance(getattr(unified, section), DotDict)

    def test_create_unified_config_maintains_type_information(self) -> None:
        """Test that unified config maintains proper type information."""
        config = TracerConfig(
            api_key="test_key",
            project="test_project",
            verbose=True,
            disable_batch=False,
        )

        unified = create_unified_config(config=config)

        # Verify types are maintained
        assert isinstance(unified.api_key, str)
        assert isinstance(unified.project, str)
        assert isinstance(unified.verbose, bool)
        assert isinstance(unified.disable_batch, bool)
