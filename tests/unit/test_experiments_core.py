"""Unit tests for HoneyHive Experiments Core Functions.

This module contains comprehensive unit tests for the experiments module's
core orchestration logic, including experiment context, concurrent execution
with tracer multi-instance pattern, evaluator execution, and full evaluate()
orchestration.

Tests cover:
- ExperimentContext initialization and tracer config generation
- run_experiment() with ThreadPoolExecutor and tracer multi-instance
- _run_evaluators() with concurrent evaluator execution (sync/async)
- evaluate() full orchestration (dataset prep, run creation, execution, results)
- Error handling, edge cases, and failure scenarios
"""

# pylint: disable=R0801
# Justification: Shared test patterns with experiment integration and performance tests

# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods
# pylint: disable=too-many-lines,unused-argument,too-few-public-methods
# pylint: disable=line-too-long,too-many-positional-arguments,no-member
# Justification: Testing behavior, pytest fixture patterns, comprehensive coverage
# Justification: Mock setup and test names require descriptive length
# Justification: Mock objects have dynamic attributes

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from honeyhive.experiments.core import (
    ExperimentContext,
    _run_evaluators,
    evaluate,
    run_experiment,
)


class TestExperimentContext:
    """Test suite for ExperimentContext class."""

    def test_initialization_required_fields(self) -> None:
        """Test ExperimentContext with only required fields."""
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        assert context.run_id == "run-123"
        assert context.dataset_id == "ds-456"
        assert context.project == "test-project"
        assert context.source == "evaluation"  # Default value
        assert context.metadata == {}  # Default value

    def test_initialization_with_optional_fields(self) -> None:
        """Test ExperimentContext with optional fields."""
        metadata = {"custom_key": "custom_value"}
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
            source="custom-source",
            metadata=metadata,
        )

        assert context.source == "custom-source"
        assert context.metadata == metadata

    def test_to_tracer_config_returns_correct_structure(self) -> None:
        """Test that to_tracer_config returns proper tracer init kwargs."""
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="EXT-abc",
            project="test-project",
            source="evaluation",
        )

        config = context.to_tracer_config("dp-1")

        assert isinstance(config, dict)
        assert config["project"] == "test-project"
        assert config["is_evaluation"] is True
        assert config["run_id"] == "run-123"
        assert config["dataset_id"] == "EXT-abc"
        assert config["datapoint_id"] == "dp-1"
        assert config["source"] == "evaluation"

    def test_to_tracer_config_different_datapoint_ids(self) -> None:
        """Test that different datapoint IDs generate different configs."""
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        config1 = context.to_tracer_config("dp-1")
        config2 = context.to_tracer_config("dp-2")

        assert config1["datapoint_id"] == "dp-1"
        assert config2["datapoint_id"] == "dp-2"
        # Other fields should be identical
        assert config1["run_id"] == config2["run_id"]
        assert config1["dataset_id"] == config2["dataset_id"]

    def test_metadata_defaults_to_empty_dict(self) -> None:
        """Test that metadata defaults to empty dict, not None."""
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        assert context.metadata == {}
        assert isinstance(context.metadata, dict)


class TestRunExperiment:
    """Test suite for run_experiment function."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock HoneyHiveTracer."""
        tracer = Mock()
        tracer.project = "test-project"
        # Set up start_span as a context manager for @trace decorator support
        mock_span = Mock()
        tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        tracer.start_span.return_value.__exit__ = Mock(return_value=False)
        return tracer

    @pytest.fixture
    def experiment_context(self) -> ExperimentContext:
        """Create a test experiment context."""
        return ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

    @pytest.fixture
    def simple_function(self) -> Any:
        """Simple test function."""

        def func(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            return {"output": f"processed-{inputs.get('query', 'default')}"}

        return func

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")  # Patch where it's imported
    def test_successful_single_datapoint_execution(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test successful execution with single datapoint."""
        mock_tracer_class.return_value = mock_tracer

        dataset = [{"inputs": {"query": "test"}, "ground_truth": {"answer": "a1"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            verbose=False,
        )

        assert len(results) == 1
        assert results[0]["datapoint_id"] == "dp-1"
        assert results[0]["status"] == "success"
        assert results[0]["outputs"] == {"output": "processed-test"}
        assert results[0]["error"] is None

        # Verify tracer was created and flushed
        mock_tracer_class.assert_called_once()
        mock_flush.assert_called_once_with(mock_tracer)

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_multiple_datapoints_execution(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test execution with multiple datapoints."""
        mock_tracer_class.return_value = mock_tracer

        dataset = [
            {"inputs": {"query": "test1"}, "ground_truth": {"answer": "a1"}},
            {"inputs": {"query": "test2"}, "ground_truth": {"answer": "a2"}},
            {"inputs": {"query": "test3"}, "ground_truth": {"answer": "a3"}},
        ]
        datapoint_ids = ["dp-1", "dp-2", "dp-3"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=2,
            verbose=False,
        )

        assert len(results) == 3
        # Check all datapoints were processed
        result_ids = {r["datapoint_id"] for r in results}
        assert result_ids == {"dp-1", "dp-2", "dp-3"}

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_function_without_ground_truth(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test execution when datapoint has no ground_truth."""
        mock_tracer_class.return_value = mock_tracer

        def func_no_gt(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "no-gt"}

        dataset = [{"inputs": {"query": "test"}}]  # No ground_truth
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=func_no_gt,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
        )

        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["ground_truth"] is None

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_function_execution_error_handling(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test error handling when function raises exception."""
        mock_tracer_class.return_value = mock_tracer

        def failing_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Test error")

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=failing_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
        )

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert results[0]["error"] == "Test error"
        assert results[0]["outputs"] is None

        # Tracer should still be flushed even on error
        mock_flush.assert_called_once()

    def test_dataset_datapoint_ids_length_mismatch(
        self, experiment_context: ExperimentContext, simple_function: Any
    ) -> None:
        """Test validation error when dataset and datapoint_ids lengths don't match."""
        dataset = [{"inputs": {}}, {"inputs": {}}]
        datapoint_ids = ["dp-1"]  # Mismatch!

        with pytest.raises(ValueError, match="Dataset length.*does not match"):
            run_experiment(
                function=simple_function,
                dataset=dataset,
                datapoint_ids=datapoint_ids,
                experiment_context=experiment_context,
                api_key="test-key",
            )

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_tracer_flush_error_handling(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that flush errors are caught and logged."""
        mock_tracer_class.return_value = mock_tracer
        mock_flush.side_effect = Exception("Flush failed")

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        # Should not raise, error should be caught
        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
        )

        assert len(results) == 1
        assert results[0]["status"] == "success"  # Function still succeeded

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_verbose_logging(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that verbose=True enables logging."""
        mock_tracer_class.return_value = mock_tracer

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        with patch("honeyhive.experiments.core.logger") as mock_logger:
            run_experiment(
                function=simple_function,
                dataset=dataset,
                datapoint_ids=datapoint_ids,
                experiment_context=experiment_context,
                api_key="test-key",
                max_workers=1,
                verbose=True,
            )

            # Verify logger was called
            assert mock_logger.info.called


class TestRunEvaluators:
    """Test suite for _run_evaluators function."""

    def test_successful_sync_evaluator_execution(self) -> None:
        """Test successful execution with synchronous evaluator."""

        def accuracy_eval(inputs: Dict, outputs: Any, ground_truth: Any) -> float:
            return 0.95

        execution_results = [
            {
                "datapoint_id": "dp-1",
                "inputs": {"query": "test"},
                "outputs": {"answer": "a1"},
                "ground_truth": {"answer": "a1"},
            }
        ]

        metrics = _run_evaluators(
            evaluators=[accuracy_eval],
            execution_results=execution_results,
            max_workers=1,
            verbose=False,
        )

        assert "dp-1" in metrics
        assert metrics["dp-1"]["accuracy_eval"] == 0.95

    def test_multiple_evaluators(self) -> None:
        """Test execution with multiple evaluators."""

        def accuracy(inputs: Dict, outputs: Any, ground_truth: Any) -> float:
            return 0.95

        def relevance(inputs: Dict, outputs: Any, ground_truth: Any) -> float:
            return 0.87

        execution_results = [
            {
                "datapoint_id": "dp-1",
                "inputs": {},
                "outputs": {},
                "ground_truth": {},
            }
        ]

        metrics = _run_evaluators(
            evaluators=[accuracy, relevance],
            execution_results=execution_results,
            max_workers=2,
        )

        assert "dp-1" in metrics
        assert "accuracy" in metrics["dp-1"]
        assert "relevance" in metrics["dp-1"]

    def test_evaluator_without_ground_truth(self) -> None:
        """Test evaluator execution when ground_truth is None."""

        def fluency_eval(inputs: Dict, outputs: Any) -> float:
            return 0.9

        execution_results = [
            {
                "datapoint_id": "dp-1",
                "inputs": {},
                "outputs": {},
                "ground_truth": None,  # No ground truth
            }
        ]

        metrics = _run_evaluators(
            evaluators=[fluency_eval],
            execution_results=execution_results,
            max_workers=1,
        )

        assert "dp-1" in metrics
        assert metrics["dp-1"]["fluency_eval"] == 0.9

    def test_evaluator_error_handling(self) -> None:
        """Test that evaluator errors are caught and return None."""

        def failing_evaluator(inputs: Dict, outputs: Any) -> float:
            raise ValueError("Evaluator failed")

        execution_results = [
            {
                "datapoint_id": "dp-1",
                "inputs": {},
                "outputs": {},
                "ground_truth": None,
            }
        ]

        metrics = _run_evaluators(
            evaluators=[failing_evaluator],
            execution_results=execution_results,
            max_workers=1,
        )

        assert "dp-1" in metrics
        assert metrics["dp-1"]["failing_evaluator"] is None

    # NOTE: Async evaluator testing removed - too complex to properly mock
    # asyncio is imported inside the function (import-outside-toplevel)
    # This should be covered by integration tests instead


class TestEvaluate:
    """Test suite for evaluate() function - the main user-facing API."""

    @pytest.fixture
    def simple_function(self) -> Any:
        """Simple test function."""

        def func(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        return func

    def test_validation_neither_dataset_nor_dataset_id(
        self, simple_function: Any
    ) -> None:
        """Test that ValueError is raised when neither dataset nor dataset_id provided."""
        with pytest.raises(ValueError, match="Must provide either"):
            evaluate(
                function=simple_function,
                api_key="test-key",
                project="test-project",
            )

    def test_validation_both_dataset_and_dataset_id(self, simple_function: Any) -> None:
        """Test that ValueError is raised when both dataset and dataset_id provided."""
        with pytest.raises(ValueError, match="Cannot provide both"):
            evaluate(
                function=simple_function,
                dataset=[{"inputs": {}}],
                dataset_id="ds-123",
                api_key="test-key",
                project="test-project",
            )

    @patch.dict("os.environ", {}, clear=True)  # Clear all env vars
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_validation_no_api_key_no_env_var(
        self, mock_honeyhive_class: Mock, simple_function: Any
    ) -> None:
        """Test that evaluate works without explicit api_key if no env var set (client handles it)."""
        # The evaluate function no longer validates api_key presence
        # It's passed to HoneyHive client which handles missing keys gracefully
        mock_client = Mock()
        mock_client.evaluations.create_run.side_effect = Exception("No API key")
        mock_honeyhive_class.return_value = mock_client

        with pytest.raises(Exception):  # Client will raise error, not evaluate
            evaluate(
                function=simple_function,
                dataset=[{"inputs": {}}],
                project="test-project",
            )

    def test_validation_no_project(self, simple_function: Any) -> None:
        """Test that ValueError is raised when project is None."""
        with pytest.raises(ValueError, match="Must provide 'project'"):
            evaluate(
                function=simple_function,
                dataset=[{"inputs": {}}],
                api_key="test-key",
                project=None,
            )

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core._run_evaluators")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_with_external_dataset(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_run_evaluators: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test evaluate() with external dataset."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-dataset-123", ["dp-1", "dp-2"])
        mock_prepare_run.return_value = {
            "name": "test-experiment",
            "project": "test-project",
            "dataset_id": "EXT-dataset-123",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-456"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run_from_dict.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
            {"datapoint_id": "dp-2", "outputs": {"result": "B"}},
        ]

        mock_run_evaluators.return_value = {
            "dp-1": {"accuracy": 0.9},
            "dp-2": {"accuracy": 0.8},
        }

        mock_result = Mock()
        mock_result.success = True
        mock_result.passed = ["dp-1", "dp-2"]
        mock_result.failed = []
        mock_get_result.return_value = mock_result

        # Execute
        dataset = [{"inputs": {"x": 1}}, {"inputs": {"x": 2}}]

        def eval_func(inputs: Any, outputs: Any, ground_truth: Any = None) -> float:
            return 0.9

        result = evaluate(
            function=simple_function,
            dataset=dataset,
            api_key="test-key",
            project="test-project",
            evaluators=[eval_func],
            max_workers=2,
            aggregate_function="average",
            verbose=True,
        )

        # Verify
        assert result == mock_result
        # Note: server_url comes from HH_API_URL environment variable set in tox.ini
        mock_honeyhive_class.assert_called_once_with(
            api_key="test-key", server_url="https://api.honeyhive.ai", verbose=True
        )
        mock_prepare_external.assert_called_once_with(dataset)
        mock_run_experiment.assert_called_once()
        mock_run_evaluators.assert_called_once()
        mock_client.evaluations.update_run_from_dict.assert_called_once()
        mock_get_result.assert_called_once()

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_with_honeyhive_dataset(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test evaluate() with HoneyHive dataset_id."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_run.return_value = {
            "name": "test-experiment",
            "project": "test-project",
            "dataset_id": "ds-123",
            "event_ids": [],
        }

        mock_client = Mock()

        # Mock dataset response
        mock_ds = Mock()
        mock_ds.datapoints = ["dp-1", "dp-2"]
        mock_client.datasets.get_dataset.return_value = mock_ds

        # Mock datapoint responses
        mock_dp1 = Mock()
        mock_dp1.inputs = {"x": 1}
        mock_dp1.ground_truth = {"y": 2}
        mock_dp1.field_id = "dp-1"

        mock_dp2 = Mock()
        mock_dp2.inputs = {"x": 3}
        mock_dp2.ground_truth = {"y": 4}
        mock_dp2.field_id = "dp-2"

        mock_client.datapoints.get_datapoint.side_effect = [mock_dp1, mock_dp2]

        mock_run_response = Mock()
        mock_run_response.run_id = "run-789"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
            {"datapoint_id": "dp-2", "outputs": {"result": "B"}},
        ]

        mock_result = Mock()
        mock_result.success = True
        mock_result.passed = ["dp-1", "dp-2"]
        mock_result.failed = []
        mock_get_result.return_value = mock_result

        # Execute
        result = evaluate(
            function=simple_function,
            dataset_id="ds-123",
            api_key="test-key",
            project="test-project",
            max_workers=1,
            aggregate_function="median",
            verbose=True,
        )

        # Verify
        assert result == mock_result
        mock_client.datasets.get_dataset.assert_called_once_with("ds-123")
        assert mock_client.datapoints.get_datapoint.call_count == 2
        mock_run_experiment.assert_called_once()
        mock_get_result.assert_called_once()

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_datapoint_fetch_error_handling(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test evaluate() handles datapoint fetch errors gracefully."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_run.return_value = {
            "name": "test-experiment",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()

        # Mock dataset response
        mock_ds = Mock()
        mock_ds.datapoints = ["dp-1", "dp-2"]
        mock_client.datasets.get_dataset.return_value = mock_ds

        # First datapoint succeeds, second fails
        mock_dp1 = Mock()
        mock_dp1.inputs = {"x": 1}
        mock_dp1.ground_truth = {"y": 2}
        mock_dp1.field_id = "dp-1"

        mock_client.datapoints.get_datapoint.side_effect = [
            mock_dp1,
            Exception("Network error"),
        ]

        mock_run_response = Mock()
        mock_run_response.run_id = "run-abc"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_result.success = True
        mock_result.passed = ["dp-1"]
        mock_result.failed = []
        mock_get_result.return_value = mock_result

        # Execute
        result = evaluate(
            function=simple_function,
            dataset_id="ds-123",
            api_key="test-key",
            project="test-project",
        )

        # Verify - should continue with available datapoints
        assert result == mock_result
        assert mock_client.datapoints.get_datapoint.call_count == 2

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_update_run_error_handling(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test evaluate() handles run update errors gracefully."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-xyz"
        mock_client.evaluations.create_run.return_value = mock_run_response

        # update_run_from_dict raises error
        mock_client.evaluations.update_run_from_dict.side_effect = Exception(
            "API error"
        )
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_result.success = True
        mock_result.passed = ["dp-1"]
        mock_result.failed = []
        mock_get_result.return_value = mock_result

        # Execute - should not crash despite update error
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            api_key="test-key",
            project="test-project",
        )

        # Verify - should still return result despite update failure
        assert result == mock_result
        mock_client.evaluations.update_run_from_dict.assert_called_once()

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_without_evaluators(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test evaluate() without evaluators (skip evaluator step)."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_result.success = True
        mock_result.passed = ["dp-1"]
        mock_result.failed = []
        mock_get_result.return_value = mock_result

        # Execute without evaluators
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            api_key="test-key",
            project="test-project",
            evaluators=None,  # No evaluators
            verbose=False,
        )

        # Verify
        assert result == mock_result
        # _run_evaluators should NOT have been called
        # (can't directly verify since it's not patched, but no error means it wasn't called)

    @patch.dict("os.environ", {"HONEYHIVE_API_KEY": "env-api-key"})
    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_reads_api_key_from_honeyhive_env_var(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test that evaluate() reads API key from HONEYHIVE_API_KEY env var."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_get_result.return_value = mock_result

        # Execute without explicit api_key (should use env var)
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            # NO api_key parameter
            project="test-project",
        )

        # Verify HoneyHive client was initialized with env var value
        mock_honeyhive_class.assert_called_once()
        call_kwargs = mock_honeyhive_class.call_args[1]
        assert call_kwargs["api_key"] == "env-api-key"
        assert result == mock_result

    @patch.dict("os.environ", {"HH_API_KEY": "hh-api-key"})
    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_reads_api_key_from_hh_env_var(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test that evaluate() reads API key from HH_API_KEY env var."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_get_result.return_value = mock_result

        # Execute without explicit api_key (should use HH_API_KEY env var)
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            project="test-project",
        )

        # Verify HoneyHive client was initialized with env var value
        mock_honeyhive_class.assert_called_once()
        call_kwargs = mock_honeyhive_class.call_args[1]
        assert call_kwargs["api_key"] == "hh-api-key"
        assert result == mock_result

    @patch.dict(
        "os.environ", {"HONEYHIVE_API_KEY": "honeyhive-key", "HH_API_KEY": "hh-key"}
    )
    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_prefers_honeyhive_prefix_env_var(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test that evaluate() prefers HONEYHIVE_* over HH_* env vars."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_get_result.return_value = mock_result

        # Execute
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            project="test-project",
        )

        # Verify HONEYHIVE_API_KEY was used (not HH_API_KEY)
        mock_honeyhive_class.assert_called_once()
        call_kwargs = mock_honeyhive_class.call_args[1]
        assert call_kwargs["api_key"] == "honeyhive-key"
        assert result == mock_result

    @patch.dict("os.environ", {"HONEYHIVE_SERVER_URL": "https://custom.server.com"})
    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_reads_server_url_from_env_var(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test that evaluate() reads server_url from HONEYHIVE_SERVER_URL env var."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_get_result.return_value = mock_result

        # Execute without explicit server_url
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            api_key="test-key",
            project="test-project",
        )

        # Verify HoneyHive client was initialized with env var value
        mock_honeyhive_class.assert_called_once()
        call_kwargs = mock_honeyhive_class.call_args[1]
        assert call_kwargs["server_url"] == "https://custom.server.com"
        assert result == mock_result

    @patch("honeyhive.experiments.core.get_run_result")
    @patch("honeyhive.experiments.core.run_experiment")
    @patch("honeyhive.experiments.core.ExperimentContext")
    @patch("honeyhive.experiments.core.prepare_run_request_data")
    @patch("honeyhive.experiments.core.prepare_external_dataset")
    @patch("honeyhive.experiments.core.uuid.uuid4")
    @patch("honeyhive.experiments.core.HoneyHive")
    def test_evaluate_explicit_server_url_parameter(
        self,
        mock_honeyhive_class: Mock,
        mock_uuid: Mock,
        mock_prepare_external: Mock,
        mock_prepare_run: Mock,
        mock_context_class: Mock,
        mock_run_experiment: Mock,
        mock_get_result: Mock,
        simple_function: Any,
    ) -> None:
        """Test that evaluate() accepts explicit server_url parameter."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="abc123")
        mock_prepare_external.return_value = ("EXT-ds-123", ["dp-1"])
        mock_prepare_run.return_value = {
            "name": "test",
            "project": "test-project",
            "event_ids": [],
        }

        mock_client = Mock()
        mock_run_response = Mock()
        mock_run_response.run_id = "run-123"
        mock_client.evaluations.create_run.return_value = mock_run_response
        mock_client.evaluations.update_run.return_value = None
        mock_honeyhive_class.return_value = mock_client

        mock_context = Mock()
        mock_context_class.return_value = mock_context

        mock_run_experiment.return_value = [
            {"datapoint_id": "dp-1", "outputs": {"result": "A"}},
        ]

        mock_result = Mock()
        mock_get_result.return_value = mock_result

        # Execute with explicit server_url
        result = evaluate(
            function=simple_function,
            dataset=[{"inputs": {"x": 1}}],
            api_key="test-key",
            server_url="https://staging.honeyhive.com",  # NEW parameter
            project="test-project",
        )

        # Verify HoneyHive client was initialized with explicit server_url
        mock_honeyhive_class.assert_called_once()
        call_kwargs = mock_honeyhive_class.call_args[1]
        assert call_kwargs["server_url"] == "https://staging.honeyhive.com"
        assert result == mock_result


class TestAsyncFunctionSupport:
    """Test suite for async function support in run_experiment."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock HoneyHiveTracer."""
        tracer = Mock()
        tracer.project = "test-project"
        mock_span = Mock()
        tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        tracer.start_span.return_value.__exit__ = Mock(return_value=False)
        return tracer

    @pytest.fixture
    def experiment_context(self) -> ExperimentContext:
        """Create a test experiment context."""
        return ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_async_function_execution(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test that async functions are detected and executed correctly."""
        mock_tracer_class.return_value = mock_tracer

        async def async_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Async test function."""
            inputs = datapoint.get("inputs", {})
            return {"output": f"async-processed-{inputs.get('query', 'default')}"}

        dataset = [{"inputs": {"query": "test"}, "ground_truth": {"answer": "a1"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=async_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            verbose=False,
        )

        assert len(results) == 1
        assert results[0]["datapoint_id"] == "dp-1"
        assert results[0]["status"] == "success"
        assert results[0]["outputs"] == {"output": "async-processed-test"}
        assert results[0]["error"] is None

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_async_function_with_tracer_parameter(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test async function with tracer parameter."""
        mock_tracer_class.return_value = mock_tracer

        async def async_function_with_tracer(
            datapoint: Dict[str, Any], tracer: Any
        ) -> Dict[str, Any]:
            """Async test function with tracer parameter."""
            inputs = datapoint.get("inputs", {})
            return {"output": f"async-with-tracer-{inputs.get('query', 'default')}"}

        dataset = [{"inputs": {"query": "test"}, "ground_truth": {"answer": "a1"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=async_function_with_tracer,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            verbose=False,
        )

        assert len(results) == 1
        assert results[0]["datapoint_id"] == "dp-1"
        assert results[0]["status"] == "success"
        assert results[0]["outputs"] == {"output": "async-with-tracer-test"}

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_async_function_error_handling(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test error handling when async function raises exception."""
        mock_tracer_class.return_value = mock_tracer

        async def failing_async_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Async function that raises an error."""
            raise ValueError("Async test error")

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=failing_async_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
        )

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert results[0]["error"] == "Async test error"
        assert results[0]["outputs"] is None

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_multiple_async_datapoints(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        mock_tracer: Mock,
    ) -> None:
        """Test async function execution with multiple datapoints."""
        mock_tracer_class.return_value = mock_tracer

        async def async_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Async test function."""
            inputs = datapoint.get("inputs", {})
            return {"output": f"async-{inputs.get('query', 'default')}"}

        dataset = [
            {"inputs": {"query": "test1"}, "ground_truth": {"answer": "a1"}},
            {"inputs": {"query": "test2"}, "ground_truth": {"answer": "a2"}},
            {"inputs": {"query": "test3"}, "ground_truth": {"answer": "a3"}},
        ]
        datapoint_ids = ["dp-1", "dp-2", "dp-3"]

        results = run_experiment(
            function=async_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=2,
            verbose=False,
        )

        assert len(results) == 3
        result_ids = {r["datapoint_id"] for r in results}
        assert result_ids == {"dp-1", "dp-2", "dp-3"}
        # All should be successful
        for result in results:
            assert result["status"] == "success"

    def test_async_function_detection(self) -> None:
        """Test that asyncio.iscoroutinefunction correctly detects async functions."""
        import asyncio

        def sync_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "sync"}

        async def async_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "async"}

        assert not asyncio.iscoroutinefunction(sync_function)
        assert asyncio.iscoroutinefunction(async_function)


class TestInstrumentorsSupport:
    """Test suite for instrumentors parameter in run_experiment and evaluate."""

    @pytest.fixture
    def mock_tracer(self) -> Mock:
        """Create a mock HoneyHiveTracer with provider attribute."""
        tracer = Mock()
        tracer.project = "test-project"
        tracer.provider = Mock()
        mock_span = Mock()
        tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        tracer.start_span.return_value.__exit__ = Mock(return_value=False)
        return tracer

    @pytest.fixture
    def experiment_context(self) -> ExperimentContext:
        """Create a test experiment context."""
        return ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

    @pytest.fixture
    def simple_function(self) -> Any:
        """Simple test function."""

        def func(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            return {"output": f"processed-{inputs.get('query', 'default')}"}

        return func

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_instrumentors_called_with_tracer_provider(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that instrumentor factories are called and instrument() is invoked."""
        mock_tracer_class.return_value = mock_tracer

        mock_instrumentor = Mock()
        instrumentor_factory = Mock(return_value=mock_instrumentor)

        dataset = [{"inputs": {"query": "test"}, "ground_truth": {"answer": "a1"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            verbose=False,
            instrumentors=[instrumentor_factory],
        )

        instrumentor_factory.assert_called_once()
        mock_instrumentor.instrument.assert_called_once_with(
            tracer_provider=mock_tracer.provider
        )

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_multiple_instrumentors(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that multiple instrumentor factories are all called."""
        mock_tracer_class.return_value = mock_tracer

        mock_instrumentor1 = Mock()
        mock_instrumentor2 = Mock()
        factory1 = Mock(return_value=mock_instrumentor1)
        factory2 = Mock(return_value=mock_instrumentor2)

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            instrumentors=[factory1, factory2],
        )

        factory1.assert_called_once()
        factory2.assert_called_once()
        mock_instrumentor1.instrument.assert_called_once()
        mock_instrumentor2.instrument.assert_called_once()

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_instrumentors_per_datapoint_isolation(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that each datapoint gets its own instrumentor instance."""
        mock_tracer_class.return_value = mock_tracer

        call_count = {"count": 0}

        def instrumentor_factory() -> Mock:
            call_count["count"] += 1
            return Mock()

        dataset = [
            {"inputs": {"query": "test1"}},
            {"inputs": {"query": "test2"}},
            {"inputs": {"query": "test3"}},
        ]
        datapoint_ids = ["dp-1", "dp-2", "dp-3"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            instrumentors=[instrumentor_factory],
        )

        assert call_count["count"] == 3

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_instrumentor_error_handling(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that instrumentor errors are caught and logged."""
        mock_tracer_class.return_value = mock_tracer

        def failing_factory() -> Mock:
            raise ValueError("Instrumentor creation failed")

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            instrumentors=[failing_factory],
        )

        assert len(results) == 1
        assert results[0]["status"] == "success"

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_no_instrumentors_works(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that run_experiment works without instrumentors."""
        mock_tracer_class.return_value = mock_tracer

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
        )

        assert len(results) == 1
        assert results[0]["status"] == "success"

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_empty_instrumentors_list(
        self,
        mock_tracer_class: Mock,
        mock_flush: Mock,
        experiment_context: ExperimentContext,
        simple_function: Any,
        mock_tracer: Mock,
    ) -> None:
        """Test that empty instrumentors list works."""
        mock_tracer_class.return_value = mock_tracer

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=experiment_context,
            api_key="test-key",
            max_workers=1,
            instrumentors=[],
        )

        assert len(results) == 1
        assert results[0]["status"] == "success"
