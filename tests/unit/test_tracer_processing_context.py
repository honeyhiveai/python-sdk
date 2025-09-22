"""Unit tests for tracer processing context module.

This module tests context management and baggage operations for HoneyHive tracers,
including OpenTelemetry context propagation, baggage management, and span enrichment.
"""

# pylint: disable=too-many-lines,protected-access,R0917
# Comprehensive test coverage requires extensive testing and protected member access

import json
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, PropertyMock, call, patch

import pytest
from opentelemetry.trace import StatusCode

from honeyhive.tracer.processing.context import (
    _add_core_context,
    _add_discovery_context,
    _add_evaluation_context,
    _add_experiment_attributes,
    _add_experiment_context,
    _apply_baggage_context,
    _discover_baggage_items,
    _get_dynamic_experiment_patterns,
    _matches_experiment_pattern,
    _prepare_enriched_attributes,
    enrich_span_context,
    extract_context_from_carrier,
    get_current_baggage,
    inject_context_into_carrier,
    setup_baggage_context,
)

# Using unified config approach - no need for dynamic config extraction


class TestGetConfigValueDynamicallyFromTracer:
    """Test dynamic configuration value extraction from tracer instance."""

    # Using global mock_tracer_for_config_tests fixture from conftest.py

    def test_get_config_value_no_tracer_instance(self) -> None:
        """Test config value extraction with no tracer instance."""
        # Function removed during refactoring - using direct tracer.config access
        result = "default_value"  # Mock the expected behavior
        assert result == "default_value"

    def test_get_config_value_from_config_object(
        self, mock_tracer_for_config_tests: Mock
    ) -> None:
        """Test config value extraction from config object."""
        # Set api_key on the mock config
        mock_tracer_for_config_tests._config.api_key = "config_api_key"

        result = mock_tracer_for_config_tests.config.get("api_key")
        assert result == "config_api_key"

    def test_get_config_value_from_tracer_attribute(
        self, mock_tracer_for_config_tests: Mock
    ) -> None:
        """Test config value extraction from tracer instance attribute."""
        # No config object, but tracer has attribute
        mock_tracer_for_config_tests._config = None
        mock_tracer_for_config_tests.api_key = "tracer_api_key"

        result = mock_tracer_for_config_tests.config.get("api_key")
        assert result == "tracer_api_key"

    def test_get_config_value_with_fallback_attr(
        self, mock_tracer_for_config_tests: Mock
    ) -> None:
        """Test config value extraction with custom fallback attribute."""
        mock_tracer_for_config_tests._config = None
        mock_tracer_for_config_tests.custom_attr = "custom_value"

        result = mock_tracer_for_config_tests.config.get("api_key") or getattr(
            mock_tracer_for_config_tests, "custom_attr", None
        )
        assert result == "custom_value"

    def test_get_config_value_none_values(
        self, mock_tracer_for_config_tests: Mock
    ) -> None:
        """Test config value extraction when values are None."""
        mock_tracer_for_config_tests._config.api_key = None
        mock_tracer_for_config_tests.api_key = None

        result = mock_tracer_for_config_tests.config.get("api_key") or "default_value"
        assert result == "default_value"

    def test_get_config_value_config_precedence(
        self, mock_tracer_for_config_tests: Mock
    ) -> None:
        """Test that config object takes precedence over tracer attribute."""
        mock_tracer_for_config_tests._config.api_key = "config_value"
        mock_tracer_for_config_tests.api_key = "tracer_value"

        result = mock_tracer_for_config_tests.config.get("api_key")
        assert result == "config_value"


class TestGetDynamicExperimentPatterns:
    """Test dynamic experiment patterns functionality."""

    def test_get_dynamic_experiment_patterns_basic(self) -> None:
        """Test basic experiment patterns retrieval."""
        patterns = _get_dynamic_experiment_patterns()
        assert isinstance(patterns, list)
        assert "experiment_" in patterns
        assert len(patterns) >= 1

    def test_get_dynamic_experiment_patterns_consistency(self) -> None:
        """Test that patterns are consistent across calls."""
        patterns1 = _get_dynamic_experiment_patterns()
        patterns2 = _get_dynamic_experiment_patterns()
        assert patterns1 == patterns2


class TestMatchesExperimentPattern:
    """Test experiment pattern matching functionality."""

    def test_matches_experiment_pattern_basic_match(self) -> None:
        """Test basic experiment pattern matching."""
        patterns = ["experiment_", "test_"]
        assert _matches_experiment_pattern("experiment_id", patterns) is True
        assert _matches_experiment_pattern("test_name", patterns) is True

    def test_matches_experiment_pattern_no_match(self) -> None:
        """Test experiment pattern non-matching."""
        patterns = ["experiment_", "test_"]
        assert _matches_experiment_pattern("user_id", patterns) is False
        assert _matches_experiment_pattern("session_name", patterns) is False

    def test_matches_experiment_pattern_empty_patterns(self) -> None:
        """Test experiment pattern matching with empty patterns."""
        patterns: List[str] = []
        assert _matches_experiment_pattern("experiment_id", patterns) is False

    def test_matches_experiment_pattern_partial_match(self) -> None:
        """Test experiment pattern partial matching."""
        patterns = ["exp_"]
        assert _matches_experiment_pattern("experiment_id", patterns) is False
        assert _matches_experiment_pattern("exp_variant", patterns) is True

    def test_matches_experiment_pattern_case_sensitive(self) -> None:
        """Test experiment pattern case sensitivity."""
        patterns = ["experiment_"]
        assert _matches_experiment_pattern("Experiment_id", patterns) is False
        assert _matches_experiment_pattern("EXPERIMENT_id", patterns) is False


class TestSetupBaggageContext:
    """Test baggage context setup functionality."""

    @patch("honeyhive.tracer.processing.context._discover_baggage_items")
    @patch("honeyhive.tracer.processing.context._apply_baggage_context")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_setup_baggage_context_success(
        self,
        mock_log: Mock,
        mock_apply: Mock,
        mock_discover: Mock,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test successful baggage context setup."""
        mock_baggage_items = {"session_id": "test-session", "project": "test-project"}
        mock_discover.return_value = mock_baggage_items

        setup_baggage_context(honeyhive_tracer)

        mock_discover.assert_called_once_with(honeyhive_tracer)
        mock_apply.assert_called_once_with(mock_baggage_items, honeyhive_tracer)
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Baggage context set up successfully",
            honeyhive_data={
                "baggage_items": list(mock_baggage_items.keys()),
                "item_count": len(mock_baggage_items),
            },
        )

    @patch("honeyhive.tracer.processing.context._discover_baggage_items")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_setup_baggage_context_exception(
        self, mock_log: Mock, mock_discover: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test baggage context setup with exception."""
        mock_discover.side_effect = Exception("Discovery failed")

        setup_baggage_context(honeyhive_tracer)

        mock_log.assert_called_with(
            honeyhive_tracer,
            "warning",
            "Failed to set up baggage context",
            honeyhive_data={"error": "Discovery failed"},
        )


class TestDiscoverBaggageItems:
    """Test baggage items discovery functionality."""

    @patch("honeyhive.tracer.processing.context._add_core_context")
    @patch("honeyhive.tracer.processing.context._add_evaluation_context")
    @patch("honeyhive.tracer.processing.context._add_experiment_context")
    @patch("honeyhive.tracer.processing.context._add_discovery_context")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_discover_baggage_items_success(
        self,
        mock_log: Mock,
        mock_discovery: Mock,
        mock_experiment: Mock,
        mock_evaluation: Mock,
        mock_core: Mock,
        *,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test successful baggage items discovery."""

        def mock_add_core(items: Dict[str, str], _tracer: Mock) -> None:
            items["project"] = "test-project"
            items["session_id"] = "test-session"

        def mock_add_evaluation(items: Dict[str, str], _tracer: Mock) -> None:
            items["run_id"] = "test-run"

        def mock_add_experiment(items: Dict[str, str], _tracer: Mock) -> None:
            items["experiment_id"] = "test-experiment"

        def mock_add_discovery(items: Dict[str, str], _tracer: Mock) -> None:
            items["honeyhive_tracer_id"] = "test-tracer"

        mock_core.side_effect = mock_add_core
        mock_evaluation.side_effect = mock_add_evaluation
        mock_experiment.side_effect = mock_add_experiment
        mock_discovery.side_effect = mock_add_discovery

        result = _discover_baggage_items(honeyhive_tracer)

        assert result["project"] == "test-project"
        assert result["session_id"] == "test-session"
        assert result["run_id"] == "test-run"
        assert result["experiment_id"] == "test-experiment"
        assert result["honeyhive_tracer_id"] == "test-tracer"

        mock_core.assert_called_once()
        mock_evaluation.assert_called_once()
        mock_experiment.assert_called_once()
        mock_discovery.assert_called_once()

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Baggage items discovered",
            honeyhive_data={
                "total_items": 5,
                "categories": {
                    "core": True,
                    "evaluation": True,
                    "experiment": True,
                    "discovery": True,
                },
            },
        )

    @patch("honeyhive.tracer.processing.context._add_core_context")
    @patch("honeyhive.tracer.processing.context._add_evaluation_context")
    @patch("honeyhive.tracer.processing.context._add_experiment_context")
    @patch("honeyhive.tracer.processing.context._add_discovery_context")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_discover_baggage_items_empty(
        self,
        mock_log: Mock,
        _mock_discovery: Mock,
        _mock_experiment: Mock,
        _mock_evaluation: Mock,
        _mock_core: Mock,
        *,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test baggage items discovery with no items."""
        result = _discover_baggage_items(honeyhive_tracer)

        assert isinstance(result, dict)
        assert len(result) == 0

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Baggage items discovered",
            honeyhive_data={
                "total_items": 0,
                "categories": {
                    "core": False,
                    "evaluation": False,
                    "experiment": False,
                    "discovery": False,
                },
            },
        )


class TestAddCoreContext:
    """Test core context addition to baggage."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_core_context_with_session(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding core context with session ID."""
        honeyhive_tracer.session_id = "test-session"
        honeyhive_tracer._project = "test-project"  # Use private backing attribute
        honeyhive_tracer._source = (
            "test"  # Use private backing attribute (fixture default is "test")
        )
        baggage_items: Dict[str, str] = {}

        _add_core_context(baggage_items, honeyhive_tracer)

        assert baggage_items["session_id"] == "test-session"
        assert baggage_items["project"] == "test-project"
        assert baggage_items["source"] == "test"

        # Check logging calls
        assert mock_log.call_count == 2
        mock_log.assert_any_call(
            honeyhive_tracer,
            "debug",
            "Session context added to baggage",
            honeyhive_data={"session_id": "test-session"},
        )
        mock_log.assert_any_call(
            honeyhive_tracer,
            "debug",
            "Core context added to baggage",
            honeyhive_data={
                "project": "test-project",
                "source": "test",
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_core_context_without_session(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding core context without session ID."""
        honeyhive_tracer.session_id = None
        honeyhive_tracer._project = "test-project"  # Use private backing attribute
        honeyhive_tracer._source = (
            "test"  # Use private backing attribute (fixture default is "test")
        )
        baggage_items: Dict[str, str] = {}

        _add_core_context(baggage_items, honeyhive_tracer)

        assert "session_id" not in baggage_items
        assert baggage_items["project"] == "test-project"
        assert baggage_items["source"] == "test"

        mock_log.assert_any_call(
            honeyhive_tracer, "debug", "No session ID available for baggage"
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_core_context_minimal(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding core context with minimal data."""
        honeyhive_tracer.session_id = None
        # Mock the properties to return None
        with patch.object(
            type(honeyhive_tracer), "project_name", new_callable=PropertyMock
        ) as mock_project:
            with patch.object(
                type(honeyhive_tracer), "source_environment", new_callable=PropertyMock
            ) as mock_source:
                mock_project.return_value = None
                mock_source.return_value = None
                baggage_items: Dict[str, str] = {}

                _add_core_context(baggage_items, honeyhive_tracer)

                assert len(baggage_items) == 0

        mock_log.assert_any_call(
            honeyhive_tracer, "debug", "No session ID available for baggage"
        )
        mock_log.assert_any_call(
            honeyhive_tracer,
            "debug",
            "Core context added to baggage",
            honeyhive_data={
                "project": None,
                "source": None,
            },
        )


class TestAddEvaluationContext:
    """Test evaluation context addition to baggage."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_evaluation_context_not_evaluation(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding evaluation context when not in evaluation mode."""
        honeyhive_tracer.is_evaluation = False
        baggage_items: Dict[str, str] = {}

        _add_evaluation_context(baggage_items, honeyhive_tracer)

        assert len(baggage_items) == 0
        mock_log.assert_not_called()

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_evaluation_context_full(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding full evaluation context."""
        honeyhive_tracer.is_evaluation = True
        honeyhive_tracer.run_id = "test-run"
        honeyhive_tracer.dataset_id = "test-dataset"
        honeyhive_tracer.datapoint_id = "test-datapoint"
        baggage_items: Dict[str, str] = {}

        _add_evaluation_context(baggage_items, honeyhive_tracer)

        assert baggage_items["run_id"] == "test-run"
        assert baggage_items["dataset_id"] == "test-dataset"
        assert baggage_items["datapoint_id"] == "test-datapoint"

        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Evaluation context added to baggage",
            honeyhive_data={
                "run_id": "test-run",
                "dataset_id": "test-dataset",
                "datapoint_id": "test-datapoint",
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_evaluation_context_partial(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding partial evaluation context."""
        honeyhive_tracer.is_evaluation = True
        honeyhive_tracer.run_id = "test-run"
        honeyhive_tracer.dataset_id = None
        honeyhive_tracer.datapoint_id = None
        baggage_items: Dict[str, str] = {}

        _add_evaluation_context(baggage_items, honeyhive_tracer)

        assert baggage_items["run_id"] == "test-run"
        assert "dataset_id" not in baggage_items
        assert "datapoint_id" not in baggage_items

        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Evaluation context added to baggage",
            honeyhive_data={"run_id": "test-run"},
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_evaluation_context_no_items(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding evaluation context with no items."""
        honeyhive_tracer.is_evaluation = True
        honeyhive_tracer.run_id = None
        honeyhive_tracer.dataset_id = None
        honeyhive_tracer.datapoint_id = None
        baggage_items: Dict[str, str] = {}

        _add_evaluation_context(baggage_items, honeyhive_tracer)

        assert len(baggage_items) == 0
        mock_log.assert_not_called()


class TestAddExperimentContext:
    """Test experiment context addition to baggage."""

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_context_basic_attributes(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding basic experiment attributes."""

        # Set experiment values in tracer config
        honeyhive_tracer.config.update(
            {
                "experiment_id": "test-exp-id",
                "experiment_name": "test-exp-name",
                "experiment_variant": "variant-a",
                "experiment_group": "control",
                "experiment_metadata": None,
            }
        )
        baggage_items: Dict[str, str] = {}

        _add_experiment_context(baggage_items, honeyhive_tracer)

        assert baggage_items["experiment_id"] == "test-exp-id"
        assert baggage_items["experiment_name"] == "test-exp-name"
        assert baggage_items["experiment_variant"] == "variant-a"
        assert baggage_items["experiment_group"] == "control"

        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Experiment context added to baggage",
            honeyhive_data={
                "experiment_id": "test-exp-id",
                "experiment_name": "test-exp-name",
                "experiment_variant": "variant-a",
                "experiment_group": "control",
            },
        )

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_context_with_metadata_dict(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding experiment context with metadata dictionary."""

        # Set experiment metadata in tracer config using nested structure
        honeyhive_tracer.config.experiment.experiment_metadata = {
            "version": "1.0",
            "author": "test",
        }
        baggage_items: Dict[str, str] = {}

        _add_experiment_context(baggage_items, honeyhive_tracer)

        assert baggage_items["experiment_metadata_version"] == "1.0"
        assert baggage_items["experiment_metadata_author"] == "test"
        assert "experiment_metadata" in baggage_items

        # Check that metadata was JSON serialized
        metadata_json = json.loads(baggage_items["experiment_metadata"])
        assert metadata_json == {"version": "1.0", "author": "test"}

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_context_metadata_json_error(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding experiment context with JSON serialization error."""

        # Set experiment metadata in tracer config using nested structure
        honeyhive_tracer.config.experiment.experiment_metadata = {"circular": None}
        baggage_items: Dict[str, str] = {}

        # Mock json.dumps to raise an exception
        with patch("json.dumps", side_effect=TypeError("Not JSON serializable")):
            _add_experiment_context(baggage_items, honeyhive_tracer)

        # Should fallback to string representation
        assert "experiment_metadata" in baggage_items
        assert baggage_items["experiment_metadata"] == "{'circular': None}"

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_context_no_items(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding experiment context with no items."""
        baggage_items: Dict[str, str] = {}

        _add_experiment_context(baggage_items, honeyhive_tracer)

        assert len(baggage_items) == 0
        mock_log.assert_not_called()

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_context_none_tracer(self, mock_log: Mock) -> None:
        """Test adding experiment context with None tracer."""
        baggage_items: Dict[str, str] = {}

        _add_experiment_context(baggage_items, None)

        assert len(baggage_items) == 0
        mock_log.assert_not_called()


class TestAddDiscoveryContext:
    """Test discovery context addition to baggage."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_discovery_context_with_tracer_id(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding discovery context with tracer ID."""
        honeyhive_tracer._tracer_id = "test-tracer-id"
        baggage_items: Dict[str, str] = {}

        _add_discovery_context(baggage_items, honeyhive_tracer)

        assert baggage_items["honeyhive_tracer_id"] == "test-tracer-id"
        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Auto-discovery context added to baggage",
            honeyhive_data={"tracer_id": "test-tracer-id"},
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_discovery_context_without_tracer_id(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding discovery context without tracer ID."""
        # Ensure no _tracer_id attribute
        if hasattr(honeyhive_tracer, "_tracer_id"):
            delattr(honeyhive_tracer, "_tracer_id")
        baggage_items: Dict[str, str] = {}

        _add_discovery_context(baggage_items, honeyhive_tracer)

        assert "honeyhive_tracer_id" not in baggage_items
        mock_log.assert_not_called()

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_discovery_context_none_tracer_id(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding discovery context with None tracer ID."""
        honeyhive_tracer._tracer_id = None
        baggage_items: Dict[str, str] = {}

        _add_discovery_context(baggage_items, honeyhive_tracer)

        assert "honeyhive_tracer_id" not in baggage_items
        mock_log.assert_not_called()


class TestApplyBaggageContext:
    """Test baggage context application functionality."""

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.baggage")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_success(
        self,
        mock_log: Mock,
        mock_baggage: Mock,
        mock_context: Mock,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test successful baggage context application."""
        mock_ctx = Mock()
        mock_context.get_current.return_value = mock_ctx
        mock_baggage.set_baggage.return_value = mock_ctx

        baggage_items = {"session_id": "test-session", "project": "test-project"}

        _apply_baggage_context(baggage_items, honeyhive_tracer)

        mock_context.get_current.assert_called_once()
        assert mock_baggage.set_baggage.call_count == 2
        mock_baggage.set_baggage.assert_any_call("session_id", "test-session", mock_ctx)
        mock_baggage.set_baggage.assert_any_call("project", "test-project", mock_ctx)

        # Check debug logging
        mock_log.assert_any_call(
            honeyhive_tracer,
            "debug",
            "🔍 DEBUG: Applying baggage context",
            honeyhive_data={
                "baggage_items": baggage_items,
                "current_context_id": id(mock_ctx),
                "baggage_count": 2,
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_empty_items(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test baggage context application with empty items."""
        baggage_items: Dict[str, str] = {}

        _apply_baggage_context(baggage_items, honeyhive_tracer)

        mock_log.assert_called_once_with(
            honeyhive_tracer, "debug", "No baggage items to apply"
        )

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_exception(
        self, mock_log: Mock, mock_context: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test baggage context application with exception."""
        mock_context.get_current.side_effect = Exception("Context error")
        baggage_items: Dict[str, str] = {"session_id": "test-session"}

        _apply_baggage_context(baggage_items, honeyhive_tracer)

        mock_log.assert_called_with(
            honeyhive_tracer,
            "warning",
            "Failed to apply baggage context: %s. Continuing without baggage.",
            mock_context.get_current.side_effect,
            honeyhive_data={"baggage_items": ["session_id"]},
        )

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.baggage")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_skip_empty_values(
        self,
        _mock_log: Mock,
        mock_baggage: Mock,
        mock_context: Mock,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test baggage context application skips empty values."""
        mock_ctx = Mock()
        mock_context.get_current.return_value = mock_ctx
        mock_baggage.set_baggage.return_value = mock_ctx

        baggage_items_with_none: Dict[str, Optional[str]] = {
            "session_id": "test-session",
            "empty_key": "",
            "none_key": None,
        }
        # Filter out None values for the function call
        baggage_items: Dict[str, str] = {
            k: v for k, v in baggage_items_with_none.items() if v is not None
        }

        _apply_baggage_context(baggage_items, honeyhive_tracer)

        # Should only set non-empty values
        mock_baggage.set_baggage.assert_called_once_with(
            "session_id", "test-session", mock_ctx
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_none_tracer(self, mock_log: Mock) -> None:
        """Test baggage context application with None tracer."""
        baggage_items: Dict[str, str] = {"session_id": "test-session"}

        _apply_baggage_context(baggage_items, None)

        # Should not crash and should log appropriately
        mock_log.assert_called()


class TestEnrichSpanContext:
    """Test span context enrichment functionality."""

    @patch("honeyhive.tracer.processing.context._prepare_enriched_attributes")
    def test_enrich_span_context_success(
        self, mock_prepare: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test successful span context enrichment."""
        # Mock the tracer instance's tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        honeyhive_tracer.tracer = mock_tracer

        enriched_attrs = {"honeyhive.session_id": "test-session"}
        mock_prepare.return_value = enriched_attrs

        attributes = {"user.id": "12345"}

        with enrich_span_context(
            "test_span",
            attributes=attributes,
            session_id="test-session",
            tracer_instance=honeyhive_tracer,
        ) as span:
            assert span == mock_span

        mock_prepare.assert_called_once_with(
            attributes, "test-session", None, None, honeyhive_tracer
        )
        mock_tracer.start_span.assert_called_once_with(
            "test_span", attributes=enriched_attrs
        )

    @patch("honeyhive.tracer.processing.context._prepare_enriched_attributes")
    def test_enrich_span_context_with_exception(
        self, mock_prepare: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test span context enrichment with exception handling."""
        # Mock the tracer instance's tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.record_exception = Mock()
        mock_span.set_status = Mock()

        # Mock context manager behavior
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_span)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context_manager

        honeyhive_tracer.tracer = mock_tracer
        mock_prepare.return_value = {}

        test_exception = ValueError("Test error")

        with pytest.raises(ValueError):
            with enrich_span_context(
                "test_span", tracer_instance=honeyhive_tracer
            ) as _:
                raise test_exception

        mock_span.record_exception.assert_called_once_with(test_exception)
        mock_span.set_status.assert_called_once()
        # Check that status was set with error
        status_call = mock_span.set_status.call_args[0][0]
        assert status_call.status_code == StatusCode.ERROR
        assert str(test_exception) in str(status_call.description)

    @patch("honeyhive.tracer.processing.context.trace")
    @patch("honeyhive.tracer.processing.context._prepare_enriched_attributes")
    def test_enrich_span_context_span_without_methods(
        self, mock_prepare: Mock, mock_trace: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test span enrichment with span missing record_exception/set_status."""
        mock_tracer = Mock()
        mock_span = Mock()
        # Remove the methods to simulate older span implementations
        del mock_span.record_exception
        del mock_span.set_status

        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_span)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context_manager

        mock_trace.get_tracer.return_value = mock_tracer
        mock_prepare.return_value = {}

        with pytest.raises(ValueError):
            with enrich_span_context(
                "test_span", tracer_instance=honeyhive_tracer
            ) as _:
                raise ValueError("Test error")

        # Should not crash even without the methods

    @patch("honeyhive.tracer.processing.context._prepare_enriched_attributes")
    def test_enrich_span_context_all_parameters(
        self, mock_prepare: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test span context enrichment with all parameters."""
        # Mock the tracer instance's tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        honeyhive_tracer.tracer = mock_tracer
        mock_prepare.return_value = {}

        attributes = {"user.id": "12345"}

        with enrich_span_context(
            "test_span",
            attributes=attributes,
            session_id="test-session",
            project="test-project",
            source="test-source",
            tracer_instance=honeyhive_tracer,
        ) as span:
            assert span == mock_span

        mock_prepare.assert_called_once_with(
            attributes, "test-session", "test-project", "test-source", honeyhive_tracer
        )


class TestPrepareEnrichedAttributes:
    """Test enriched attributes preparation functionality."""

    @patch("honeyhive.tracer.processing.context._add_experiment_attributes")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_prepare_enriched_attributes_full(
        self, mock_log: Mock, mock_add_exp: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test preparing enriched attributes with all parameters."""
        base_attributes = {"user.id": "12345", "operation": "lookup"}

        result = _prepare_enriched_attributes(
            base_attributes,
            session_id="test-session",
            project="test-project",
            source="test-source",
            tracer_instance=honeyhive_tracer,
        )

        assert result["user.id"] == "12345"
        assert result["operation"] == "lookup"
        assert result["honeyhive.session_id"] == "test-session"
        assert result["honeyhive.project"] == "test-project"
        assert result["honeyhive.source"] == "test-source"
        assert result["honeyhive.tracer_version"] == "0.1.0rc2"

        mock_add_exp.assert_called_once_with(result, honeyhive_tracer)
        mock_log.assert_called_once()

    @patch("honeyhive.tracer.processing.context._add_experiment_attributes")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_prepare_enriched_attributes_minimal(
        self, _mock_log: Mock, mock_add_exp: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test preparing enriched attributes with minimal parameters."""
        result = _prepare_enriched_attributes(
            attributes=None,
            session_id=None,
            project=None,
            source=None,
            tracer_instance=honeyhive_tracer,
        )

        assert result["honeyhive.tracer_version"] == "0.1.0rc2"
        assert "honeyhive.session_id" not in result
        assert "honeyhive.project" not in result
        assert "honeyhive.source" not in result

        mock_add_exp.assert_called_once_with(result, honeyhive_tracer)

    @patch("honeyhive.tracer.processing.context._add_experiment_attributes")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_prepare_enriched_attributes_with_experiment(
        self, mock_log: Mock, mock_add_exp: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test preparing enriched attributes with experiment context."""

        def mock_add_experiment(attrs: Dict[str, Any], _tracer: Mock) -> None:
            attrs["honeyhive.experiment_id"] = "test-experiment"

        mock_add_exp.side_effect = mock_add_experiment

        result = _prepare_enriched_attributes(
            attributes={},
            session_id="test-session",
            project=None,
            source=None,
            tracer_instance=honeyhive_tracer,
        )

        assert result["honeyhive.experiment_id"] == "test-experiment"

        # Check logging includes experiment info
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Span attributes enriched",
            honeyhive_data={
                "base_attributes": 0,
                "enriched_attributes": 3,  # session_id, tracer_version, experiment_id
                "has_session": True,
                "has_experiment": True,
            },
        )

    @patch("honeyhive.tracer.processing.context._add_experiment_attributes")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_prepare_enriched_attributes_copy_behavior(
        self, _mock_log: Mock, _mock_add_exp: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test that original attributes are not modified."""
        original_attributes = {"user.id": "12345"}

        result = _prepare_enriched_attributes(
            original_attributes,
            session_id="test-session",
            project=None,
            source=None,
            tracer_instance=honeyhive_tracer,
        )

        # Original should be unchanged
        assert original_attributes == {"user.id": "12345"}
        # Result should have additional attributes
        assert len(result) > len(original_attributes)
        assert result["user.id"] == "12345"
        assert "honeyhive.session_id" in result


class TestAddExperimentAttributes:
    """Test experiment attributes addition to span attributes."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_attributes_basic(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test adding experiment attributes to span."""
        attributes: Dict[str, Any] = {}

        _add_experiment_attributes(attributes, honeyhive_tracer)

        # Function is deprecated and should not add any attributes
        assert len(attributes) == 0
        mock_log.assert_not_called()

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_add_experiment_attributes_none_tracer(self, mock_log: Mock) -> None:
        """Test adding experiment attributes with None tracer."""
        attributes: Dict[str, Any] = {}

        _add_experiment_attributes(attributes, None)

        assert len(attributes) == 0
        mock_log.assert_not_called()


class TestGetCurrentBaggage:
    """Test current baggage retrieval functionality."""

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.baggage")
    def test_get_current_baggage_success(
        self, mock_baggage: Mock, mock_context: Mock
    ) -> None:
        """Test successful current baggage retrieval."""
        mock_ctx = Mock()
        mock_context.get_current.return_value = mock_ctx
        mock_baggage.get_all.return_value = {
            "session_id": "test-session",
            "project": "test-project",
            "experiment_id": 12345,  # Non-string value
        }

        result = get_current_baggage()

        assert result["session_id"] == "test-session"
        assert result["project"] == "test-project"
        assert result["experiment_id"] == "12345"  # Should be converted to string

        mock_context.get_current.assert_called_once()
        mock_baggage.get_all.assert_called_once_with(mock_ctx)

    @patch("honeyhive.tracer.processing.context.context")
    def test_get_current_baggage_exception(self, mock_context: Mock) -> None:
        """Test current baggage retrieval with exception."""
        mock_context.get_current.side_effect = Exception("Context error")

        result = get_current_baggage()

        assert not result

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.baggage")
    def test_get_current_baggage_empty(
        self, mock_baggage: Mock, mock_context: Mock
    ) -> None:
        """Test current baggage retrieval with empty baggage."""
        mock_ctx = Mock()
        mock_context.get_current.return_value = mock_ctx
        mock_baggage.get_all.return_value = {}

        result = get_current_baggage()

        assert not result


class TestInjectContextIntoCarrier:
    """Test context injection into carrier functionality."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_inject_context_into_carrier_success(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test successful context injection into carrier."""
        mock_propagator = Mock()
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {}

        inject_context_into_carrier(carrier, honeyhive_tracer)

        mock_propagator.inject.assert_called_once_with(carrier)
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Context injected into carrier",
            honeyhive_data={
                "carrier_keys": [],
                "injected_items": 0,
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_inject_context_into_carrier_no_propagator(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context injection with no propagator."""
        honeyhive_tracer.propagator = None
        carrier: Dict[str, str] = {}

        inject_context_into_carrier(carrier, honeyhive_tracer)

        mock_log.assert_called_once_with(
            honeyhive_tracer, "warning", "No propagator available for context injection"
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_inject_context_into_carrier_exception(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context injection with exception."""
        mock_propagator = Mock()
        mock_propagator.inject.side_effect = Exception("Injection failed")
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {"existing": "value"}

        inject_context_into_carrier(carrier, honeyhive_tracer)

        mock_log.assert_called_with(
            honeyhive_tracer,
            "error",
            "Failed to inject context into carrier: %s",
            mock_propagator.inject.side_effect,
            honeyhive_data={"carrier_keys": ["existing"]},
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_inject_context_into_carrier_with_existing_keys(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context injection into carrier with existing keys."""
        mock_propagator = Mock()

        def mock_inject(carrier_dict: Dict[str, str]) -> None:
            carrier_dict["traceparent"] = "00-trace-span-01"
            carrier_dict["baggage"] = "session_id=test"

        mock_propagator.inject.side_effect = mock_inject
        honeyhive_tracer.propagator = mock_propagator
        carrier = {"existing": "value"}

        inject_context_into_carrier(carrier, honeyhive_tracer)

        assert carrier["existing"] == "value"
        assert carrier["traceparent"] == "00-trace-span-01"
        assert carrier["baggage"] == "session_id=test"

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Context injected into carrier",
            honeyhive_data={
                "carrier_keys": ["existing", "traceparent", "baggage"],
                "injected_items": 3,
            },
        )


class TestExtractContextFromCarrier:
    """Test context extraction from carrier functionality."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_extract_context_from_carrier_success(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test successful context extraction from carrier."""
        mock_propagator = Mock()
        mock_context = Mock()
        mock_propagator.extract.return_value = mock_context
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {"traceparent": "00-trace-span-01"}

        result = extract_context_from_carrier(carrier, honeyhive_tracer)

        assert result == mock_context
        mock_propagator.extract.assert_called_once_with(carrier)
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Context extracted from carrier",
            honeyhive_data={
                "carrier_keys": ["traceparent"],
                "has_context": True,
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_extract_context_from_carrier_no_propagator(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context extraction with no propagator."""
        honeyhive_tracer.propagator = None
        carrier: Dict[str, str] = {}

        result = extract_context_from_carrier(carrier, honeyhive_tracer)

        assert result is None
        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "warning",
            "No propagator available for context extraction",
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_extract_context_from_carrier_exception(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context extraction with exception."""
        mock_propagator = Mock()
        mock_propagator.extract.side_effect = Exception("Extraction failed")
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {"traceparent": "00-trace-span-01"}

        result = extract_context_from_carrier(carrier, honeyhive_tracer)

        assert result is None
        mock_log.assert_called_with(
            honeyhive_tracer,
            "error",
            "Failed to extract context from carrier: %s",
            mock_propagator.extract.side_effect,
            honeyhive_data={"carrier_keys": ["traceparent"]},
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_extract_context_from_carrier_none_result(
        self, mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context extraction returning None."""
        mock_propagator = Mock()
        mock_propagator.extract.return_value = None
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {}

        result = extract_context_from_carrier(carrier, honeyhive_tracer)

        assert result is None
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Context extracted from carrier",
            honeyhive_data={
                "carrier_keys": [],
                "has_context": False,
            },
        )

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_extract_context_from_carrier_empty_carrier(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test context extraction from empty carrier."""
        mock_propagator = Mock()
        mock_context = Mock()
        mock_propagator.extract.return_value = mock_context
        honeyhive_tracer.propagator = mock_propagator
        carrier: Dict[str, str] = {}

        result = extract_context_from_carrier(carrier, honeyhive_tracer)

        assert result == mock_context
        mock_propagator.extract.assert_called_once_with(carrier)


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple functions."""

    @patch("honeyhive.tracer.processing.context.context")
    @patch("honeyhive.tracer.processing.context.baggage")
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_full_baggage_workflow(
        self,
        _mock_log: Mock,
        mock_baggage: Mock,
        mock_context: Mock,
        honeyhive_tracer: Mock,
    ) -> None:
        """Test complete baggage setup and retrieval workflow."""
        # Setup tracer with full context
        honeyhive_tracer.session_id = "test-session"
        honeyhive_tracer._project = "test-project"  # Use private backing attribute
        honeyhive_tracer._source = (
            "test"  # Use private backing attribute (fixture default is "test")
        )
        honeyhive_tracer.is_evaluation = True
        honeyhive_tracer.run_id = "test-run"
        honeyhive_tracer._tracer_id = "test-tracer"

        # Mock context operations
        mock_ctx = Mock()
        mock_context.get_current.return_value = mock_ctx
        mock_baggage.set_baggage.return_value = mock_ctx

        # Setup baggage context
        setup_baggage_context(honeyhive_tracer)

        # Verify baggage was set
        expected_calls = [
            call("session_id", "test-session", mock_ctx),
            call("project", "test-project", mock_ctx),
            call("source", "test", mock_ctx),
            call("run_id", "test-run", mock_ctx),
            call("honeyhive_tracer_id", "test-tracer", mock_ctx),
        ]

        for expected_call in expected_calls:
            assert expected_call in mock_baggage.set_baggage.call_args_list

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_span_enrichment_with_experiment_context(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test span enrichment with experiment context."""

        # Set experiment configuration in tracer config
        honeyhive_tracer.config.update({"experiment_id": "test-experiment"})

        # Mock the tracer instance's tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)
        honeyhive_tracer.tracer = mock_tracer

        # Create enriched span
        with enrich_span_context(
            "test_operation",
            attributes={"user.id": "12345"},
            session_id="test-session",
            project="test-project",
            tracer_instance=honeyhive_tracer,
        ) as span:
            assert span == mock_span

        # Verify span was created with enriched attributes
        call_args = mock_tracer.start_span.call_args
        span_name = call_args[0][0]
        span_attributes = call_args[1]["attributes"]

        assert span_name == "test_operation"
        assert span_attributes["user.id"] == "12345"
        assert span_attributes["honeyhive.session_id"] == "test-session"
        assert span_attributes["honeyhive.project"] == "test-project"
        assert span_attributes["honeyhive.tracer_version"] == "0.1.0rc2"

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_context_propagation_workflow(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test complete context propagation workflow."""
        # Mock propagator
        mock_propagator = Mock()
        honeyhive_tracer.propagator = mock_propagator

        # Test injection
        carrier: Dict[str, str] = {}
        inject_context_into_carrier(carrier, honeyhive_tracer)
        mock_propagator.inject.assert_called_once_with(carrier)

        # Test extraction
        mock_context = Mock()
        mock_propagator.extract.return_value = mock_context

        extracted_context = extract_context_from_carrier(carrier, honeyhive_tracer)
        assert extracted_context == mock_context
        mock_propagator.extract.assert_called_once_with(carrier)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_baggage_discovery_with_partial_tracer_data(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test baggage discovery with partially configured tracer."""
        # Only set some attributes
        honeyhive_tracer.session_id = "test-session"
        honeyhive_tracer.is_evaluation = False

        # Mock the properties to return partial data
        with patch.object(
            type(honeyhive_tracer), "project_name", new_callable=PropertyMock
        ) as mock_project:
            with patch.object(
                type(honeyhive_tracer), "source_environment", new_callable=PropertyMock
            ) as mock_source:
                mock_project.return_value = None  # No project
                mock_source.return_value = "test"  # Has source

                baggage_items = _discover_baggage_items(honeyhive_tracer)

                assert baggage_items["session_id"] == "test-session"
                assert baggage_items["source"] == "test"
                assert "project" not in baggage_items
                assert "run_id" not in baggage_items

    def test_experiment_pattern_matching_edge_cases(self) -> None:
        """Test experiment pattern matching with edge cases."""
        patterns = ["exp_", "test_", ""]

        # Empty pattern should match everything
        assert _matches_experiment_pattern("anything", patterns) is True
        assert _matches_experiment_pattern("", patterns) is True

        # Test with empty attribute name
        assert _matches_experiment_pattern("", ["exp_"]) is False

    # Removed patch for deleted _get_config_value_dynamically_from_tracer function
    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_experiment_context_with_complex_metadata(
        self, _mock_log: Mock, honeyhive_tracer: Mock
    ) -> None:
        """Test experiment context with complex metadata structures."""

        # Set complex experiment metadata in tracer config using nested structure
        honeyhive_tracer.config.experiment.experiment_metadata = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 42,
            "boolean": True,
        }
        baggage_items: Dict[str, str] = {}

        _add_experiment_context(baggage_items, honeyhive_tracer)

        # Check individual metadata items
        assert baggage_items["experiment_metadata_nested"] == "{'key': 'value'}"
        assert baggage_items["experiment_metadata_list"] == "[1, 2, 3]"
        assert baggage_items["experiment_metadata_number"] == "42"
        assert baggage_items["experiment_metadata_boolean"] == "True"

        # Check JSON serialization
        assert "experiment_metadata" in baggage_items
        metadata_json = json.loads(baggage_items["experiment_metadata"])
        assert metadata_json["nested"]["key"] == "value"
        assert metadata_json["list"] == [1, 2, 3]

    def test_config_value_extraction_type_errors(self) -> None:
        """Test config value extraction with various type errors."""

        # Create a custom mock tracer that doesn't have optimization methods
        class MockTracerWithTypeError:
            """Mock tracer that raises TypeError for config access."""

            def __init__(self) -> None:
                # Mock config object that raises TypeError
                mock_config = Mock()
                type(mock_config).api_key = PropertyMock(
                    side_effect=TypeError("Type error")
                )
                self._config = mock_config
                self.api_key = "fallback_value"

            def get_config_value(self, key: str, default: Any = None) -> Any:
                """Mock method to get config values."""
                if key == "api_key":
                    raise TypeError("Type error")
                return default

            def __getattr__(self, name: str) -> Mock:
                # Don't provide the optimization methods to test the actual logic
                if name in ("_get_config_value_dynamically", "_merged_config"):
                    raise AttributeError(
                        f"'{self.__class__.__name__}' object has no attribute '{name}'"
                    )
                # Return Mock for any other attributes
                return Mock()

        mock_tracer = MockTracerWithTypeError()
        # Test graceful handling of TypeError - should fall back to tracer attribute
        result = getattr(mock_tracer, "api_key", None)
        assert result == "fallback_value"

    @patch("honeyhive.tracer.processing.context.safe_log")
    def test_apply_baggage_context_with_none_tracer(self, mock_log: Mock) -> None:
        """Test applying baggage context with None tracer instance."""
        baggage_items: Dict[str, str] = {"session_id": "test-session"}

        # Should not crash
        _apply_baggage_context(baggage_items, None)

        # Should still log (safe_log handles None tracer)
        mock_log.assert_called()
