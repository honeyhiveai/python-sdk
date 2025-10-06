"""Backward Compatibility Tests for honeyhive.evaluation Module.

This module validates 100% backward compatibility with the deprecated
honeyhive.evaluation module, ensuring existing code continues to work
while new code migrates to honeyhive.experiments.

Tests cover:
- All old imports work without changes
- Deprecation warnings are logged correctly
- No functional changes (old calls new implementation)
- Warning messages guide users to migration path
"""

# pylint: disable=protected-access,redefined-outer-name
# pylint: disable=deprecated-module,no-member,import-outside-toplevel
# pylint: disable=unused-argument,too-few-public-methods
# Justification: Testing deprecated module and warning behavior
# Justification: Mock objects have dynamic attributes
# Justification: Testing imports at various points for compat validation
# Justification: Test classes need minimal methods

import warnings
from typing import Any, Dict
from unittest.mock import Mock, patch

# Test that old imports still work
from honeyhive.evaluation import (
    BaseEvaluator,
    EvalResult,
    EvalSettings,
    EvaluationContext,
    EvaluationResult,
    EvaluationRun,
    EvaluatorSettings,
    aevaluator,
    compare_runs,
    evaluate,
    evaluator,
    get_run_metrics,
    get_run_result,
    run_experiment,
)


class TestBackwardCompatibleImports:
    """Test that all old imports continue to work."""

    def test_evaluate_import(self) -> None:
        """Test that evaluate function is importable."""
        assert callable(evaluate)
        assert evaluate.__name__ in ["evaluate", "wrapper"]

    def test_evaluator_decorator_import(self) -> None:
        """Test that evaluator decorator is importable."""
        assert callable(evaluator)

    def test_aevaluator_decorator_import(self) -> None:
        """Test that aevaluator decorator is importable."""
        assert callable(aevaluator)

    def test_run_experiment_import(self) -> None:
        """Test that run_experiment function is importable."""
        assert callable(run_experiment)

    def test_get_run_result_import(self) -> None:
        """Test that get_run_result function is importable."""
        assert callable(get_run_result)

    def test_get_run_metrics_import(self) -> None:
        """Test that get_run_metrics function is importable."""
        assert callable(get_run_metrics)

    def test_compare_runs_import(self) -> None:
        """Test that compare_runs function is importable."""
        assert callable(compare_runs)

    def test_evaluation_context_import(self) -> None:
        """Test that EvaluationContext type alias exists."""
        assert EvaluationContext is not None

    def test_evaluation_result_import(self) -> None:
        """Test that EvaluationResult type alias exists."""
        assert EvaluationResult is not None

    def test_evaluation_run_import(self) -> None:
        """Test that EvaluationRun type alias exists."""
        assert EvaluationRun is not None

    def test_eval_result_import(self) -> None:
        """Test that EvalResult type alias exists."""
        assert EvalResult is not None

    def test_eval_settings_import(self) -> None:
        """Test that EvalSettings type alias exists."""
        assert EvalSettings is not None

    def test_evaluator_settings_import(self) -> None:
        """Test that EvaluatorSettings type alias exists."""
        assert EvaluatorSettings is not None

    def test_base_evaluator_import(self) -> None:
        """Test that BaseEvaluator class exists."""
        assert BaseEvaluator is not None


class TestDeprecationWarnings:
    """Test that deprecation warnings are logged correctly."""

    def test_evaluate_deprecation_warning(self) -> None:
        """Test that evaluate() logs deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Call deprecated evaluate (will fail but we just want the warning)
            try:
                evaluate(
                    function=lambda x: x,
                    dataset=[{"inputs": {}}],
                    api_key="test",
                    project="test",
                )
            except Exception:
                pass  # Expected to fail, we're testing the warning

            # Verify deprecation warning was raised
            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "honeyhive.evaluation" in str(w[0].message)
            assert "honeyhive.experiments" in str(w[0].message)

    def test_evaluator_deprecation_warning(self) -> None:
        """Test that @evaluator logs deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            @evaluator
            def test_eval(inputs: Dict, outputs: Any) -> float:
                return 1.0

            # Verify deprecation warning was raised
            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "evaluator" in str(w[0].message).lower()

    def test_aevaluator_deprecation_warning(self) -> None:
        """Test that @aevaluator logs deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            @aevaluator
            async def test_eval(inputs: Dict, outputs: Any) -> float:
                return 1.0

            # Verify deprecation warning was raised
            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "aevaluator" in str(w[0].message).lower()

    def test_run_experiment_deprecation_warning(self) -> None:
        """Test that run_experiment() logs deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                run_experiment(
                    function=lambda x: x,
                    dataset=[],
                    datapoint_ids=[],
                    experiment_context=None,
                    api_key="test",
                )
            except Exception:
                pass

            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_get_run_result_deprecation_warning(self) -> None:
        """Test that get_run_result() logs deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                get_run_result(client=Mock(), run_id="test")
            except Exception:
                pass

            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_deprecation_warning_message_format(self) -> None:
        """Test that deprecation warning messages follow proper format."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                evaluate(
                    function=lambda x: x,
                    dataset=[{"inputs": {}}],
                    api_key="test",
                    project="test",
                )
            except Exception:
                pass

            assert len(w) >= 1
            message = str(w[0].message)

            # Verify message contains migration guidance
            assert "OLD:" in message or "NEW:" in message
            assert "honeyhive.evaluation" in message
            assert "honeyhive.experiments" in message
            assert "deprecated" in message.lower() or "deprecation" in message.lower()


class TestFunctionalEquivalence:
    """Test that old interface produces same results as new interface."""

    @patch("honeyhive.evaluation._compat._evaluate")
    def test_evaluate_calls_new_implementation(self, mock_new_evaluate: Mock) -> None:
        """Test that old evaluate() calls new experiments.evaluate()."""
        mock_new_evaluate.return_value = Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore deprecation for this test

            try:
                evaluate(
                    function=lambda x: x,
                    dataset=[{"inputs": {}}],
                    api_key="test",
                    project="test",
                )
            except Exception:
                pass

        # Verify new implementation was called
        mock_new_evaluate.assert_called_once()

    @patch("honeyhive.evaluation._compat._run_experiment")
    def test_run_experiment_calls_new_implementation(
        self, mock_new_run_experiment: Mock
    ) -> None:
        """Test that old run_experiment() calls new implementation."""
        mock_new_run_experiment.return_value = []

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            try:
                run_experiment(
                    function=lambda x: x,
                    dataset=[],
                    datapoint_ids=[],
                    experiment_context=None,
                    api_key="test",
                )
            except Exception:
                pass

        mock_new_run_experiment.assert_called_once()

    def test_type_aliases_point_to_new_types(self) -> None:
        """Test that old type aliases point to new experiment types."""
        from honeyhive.experiments import ExperimentContext as NewContext
        from honeyhive.experiments import ExperimentResultSummary as NewSummary

        # These should be the same objects
        assert EvaluationContext is NewContext
        assert EvaluationResult is NewSummary


class TestBaseEvaluatorBackwardCompat:
    """Test BaseEvaluator class for backward compatibility."""

    def test_base_evaluator_instantiation_warning(self) -> None:
        """Test that BaseEvaluator instantiation logs warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            BaseEvaluator()

            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "BaseEvaluator" in str(w[0].message)
            assert "@evaluator" in str(w[0].message)


class TestEvaluatorsSubmodule:
    """Test that evaluators submodule is accessible for backward compat."""

    def test_evaluators_submodule_importable(self) -> None:
        """Test that honeyhive.evaluation.evaluators can be imported."""
        from honeyhive.evaluation import evaluators

        assert evaluators is not None

    def test_evaluators_submodule_has_expected_content(self) -> None:
        """Test that evaluators submodule contains expected exports."""
        from honeyhive.evaluation import evaluators

        # Should have access to evaluator decorators and settings
        assert hasattr(evaluators, "evaluator")
        assert hasattr(evaluators, "aevaluator")


class TestDecoratorWithArguments:
    """Test evaluator and aevaluator decorators with arguments."""

    def test_evaluator_with_arguments(self) -> None:
        """Test @evaluator(...) decorator with arguments."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            @evaluator(name="test_eval")
            def test_func(inputs: Dict, outputs: Any) -> float:
                return 1.0

            assert callable(test_func)

    def test_aevaluator_with_arguments(self) -> None:
        """Test @aevaluator(...) decorator with arguments."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            @aevaluator(name="test_async_eval")
            async def test_func(inputs: Dict, outputs: Any) -> float:
                return 1.0

            assert callable(test_func)


class TestAdditionalFunctions:
    """Test remaining wrapper functions for coverage."""

    @patch("honeyhive.evaluation._compat._get_run_metrics")
    def test_get_run_metrics_wrapper(self, mock_get_metrics: Mock) -> None:
        """Test get_run_metrics wrapper calls new implementation."""
        mock_get_metrics.return_value = {"accuracy": 0.9}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            result = get_run_metrics(client=Mock(), run_id="test-123")

            mock_get_metrics.assert_called_once()
            assert result == {"accuracy": 0.9}

    @patch("honeyhive.evaluation._compat._compare_runs")
    def test_compare_runs_wrapper(self, mock_compare: Mock) -> None:
        """Test compare_runs wrapper calls new implementation."""
        mock_compare.return_value = Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            result = compare_runs(
                client=Mock(), new_run_id="new-123", old_run_id="old-456"
            )

            mock_compare.assert_called_once()
            assert result is not None
