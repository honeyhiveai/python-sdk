"""
Unit tests for the 5 immediate ship requirements (v1.0 release).

Tests cover:
1. Session naming with experiment name
2. Tracer parameter (backward compatible)
3. Ground truths in feedback
4. Auto-inputs on nested spans
5. Session linking
"""

# pylint: disable=R0801
# Justification: Shared test patterns with experiment integration tests
import inspect
from typing import Any, Dict
from unittest.mock import Mock, patch

from honeyhive.experiments.core import (
    ExperimentContext,
    _enrich_session_with_results,
    run_experiment,
)
from honeyhive.tracer.instrumentation.decorators import _capture_function_inputs


class TestSessionNaming:
    """Test TASK 1: Session naming uses experiment name."""

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_session_name_uses_run_name(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that session_name is set to run_name in tracer config."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        mock_tracer.session_id = "test-session-123"

        run_name = "my-experiment-2025-10-30"

        def simple_function(_datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
            run_name=run_name,  # TASK 1: Pass run_name
        )

        dataset = [{"inputs": {"query": "test"}, "ground_truth": {"answer": "a1"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Verify tracer was initialized with session_name = run_name
        tracer_call_kwargs = mock_tracer_class.call_args[1]
        assert "session_name" in tracer_call_kwargs
        assert tracer_call_kwargs["session_name"] == run_name

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_session_name_none_when_run_name_not_provided(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that session_name is None when run_name is not provided."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        mock_tracer.session_id = "test-session-456"

        def simple_function(_datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        # Context without run_name
        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
            # No run_name specified
        )

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Verify session_name was not set (should use default)
        tracer_call_kwargs = mock_tracer_class.call_args[1]
        # When run_name is None, session_name should not be explicitly set
        # (will fall back to default tracer behavior)
        assert tracer_call_kwargs.get("session_name") is None


class TestTracerParameter:
    """Test TASK 2: Tracer parameter with backward compatibility."""

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_function_with_tracer_parameter(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that function receives tracer parameter when signature includes it."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        mock_tracer.session_id = "test-session-123"
        # Set up start_span as a context manager for @trace decorator support
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=False)

        # Track if tracer was passed
        tracer_received = []

        def function_with_tracer(
            _datapoint: Dict[str, Any], tracer: Any
        ) -> Dict[str, Any]:
            tracer_received.append(tracer)
            return {"output": "test"}

        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=function_with_tracer,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Verify tracer was passed
        assert len(tracer_received) == 1
        assert tracer_received[0] is mock_tracer

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_function_without_tracer_parameter_backward_compatible(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that function without tracer parameter still works (backward compat)."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        mock_tracer.session_id = "test-session-123"
        # Set up start_span as a context manager for @trace decorator support
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=False)

        def function_without_tracer(_datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        # Verify function doesn't have tracer parameter
        sig = inspect.signature(function_without_tracer)
        assert "tracer" not in sig.parameters

        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=function_without_tracer,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Should complete successfully without tracer parameter
        assert len(results) == 1
        assert results[0]["status"] == "success"


class TestGroundTruthsInFeedback:
    """Test TASK 3: Ground truths in feedback."""

    @patch("honeyhive.experiments.core.logger")
    def test_ground_truth_added_to_feedback(self, _mock_logger: Mock) -> None:
        """Test that ground_truth are added to feedback field."""
        mock_client = Mock()
        mock_update_event = Mock()
        mock_client.events.update_event = mock_update_event

        ground_truth_data = {"answer": "expected answer", "score": 0.95}

        _enrich_session_with_results(
            session_id="session-123",
            datapoint_id="dp-1",
            outputs={"result": "test"},
            ground_truth=ground_truth_data,  # TASK 3: Pass ground_truth
            evaluator_metrics={},
            client=mock_client,
            verbose=False,
        )

        # Verify update_event was called
        assert mock_update_event.called
        update_request = mock_update_event.call_args[0][0]

        # Verify feedback contains ground_truth
        assert hasattr(update_request, "feedback")
        assert update_request.feedback is not None
        assert "ground_truth" in update_request.feedback
        assert update_request.feedback["ground_truth"] == ground_truth_data

    @patch("honeyhive.experiments.core.logger")
    def test_no_ground_truth_no_feedback(self, _mock_logger: Mock) -> None:
        """Test that feedback is not added when ground_truth is None."""
        mock_client = Mock()
        mock_update_event = Mock()
        mock_client.events.update_event = mock_update_event

        _enrich_session_with_results(
            session_id="session-123",
            datapoint_id="dp-1",
            outputs={"result": "test"},
            ground_truth=None,  # No ground truths
            evaluator_metrics={},
            client=mock_client,
            verbose=False,
        )

        # Verify update_event was called
        assert mock_update_event.called
        update_request = mock_update_event.call_args[0][0]

        # Verify feedback is None when no ground_truth
        feedback = getattr(update_request, "feedback", None)
        assert feedback is None


class TestAutoInputCapture:
    """Test TASK 4: Auto-capture of function inputs."""

    def test_capture_function_inputs_basic(self) -> None:
        """Test basic input capture for simple function arguments."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()

        def test_function(arg1: str, arg2: int, arg3: bool) -> None:
            del arg1, arg2, arg3  # Parameters exist for signature inspection

        args = ("test_string", 42, True)
        kwargs = {}

        _capture_function_inputs(mock_span, test_function, args, kwargs)

        # Verify attributes were set
        calls = mock_span.set_attribute.call_args_list
        assert len(calls) == 3

        # Check each argument was captured
        captured = {call[0][0]: call[0][1] for call in calls}
        assert captured["honeyhive_inputs.arg1"] == "test_string"
        assert captured["honeyhive_inputs.arg2"] == 42
        assert captured["honeyhive_inputs.arg3"] is True

    def test_capture_function_inputs_with_kwargs(self) -> None:
        """Test input capture with keyword arguments."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()

        def test_function(required: str, optional: str = "default") -> None:
            del required, optional  # Parameters exist for signature inspection

        args = ("required_value",)
        kwargs = {"optional": "custom_value"}

        _capture_function_inputs(mock_span, test_function, args, kwargs)

        # Verify both args were captured
        calls = mock_span.set_attribute.call_args_list
        captured = {call[0][0]: call[0][1] for call in calls}
        assert captured["honeyhive_inputs.required"] == "required_value"
        assert captured["honeyhive_inputs.optional"] == "custom_value"

    def test_capture_function_inputs_skips_self_and_tracer(self) -> None:
        """Test that self, cls, and tracer parameters are skipped."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()

        def test_function(self: Any, arg1: str, tracer: Any) -> None:
            del self, arg1, tracer  # Parameters exist for signature inspection

        args = (Mock(), "test_value", Mock())
        kwargs = {}

        _capture_function_inputs(mock_span, test_function, args, kwargs)

        # Verify only arg1 was captured (not self or tracer)
        calls = mock_span.set_attribute.call_args_list
        assert len(calls) == 1
        assert calls[0][0][0] == "honeyhive_inputs.arg1"
        assert calls[0][0][1] == "test_value"

    def test_capture_function_inputs_dict_serialization(self) -> None:
        """Test that dict inputs are serialized to JSON."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()

        def test_function(config: Dict[str, Any]) -> None:
            del config  # Parameter exists for signature inspection

        args = ()
        kwargs = {"config": {"key": "value", "nested": {"data": 123}}}

        _capture_function_inputs(mock_span, test_function, args, kwargs)

        # Verify dict was serialized
        calls = mock_span.set_attribute.call_args_list
        assert len(calls) == 1
        assert calls[0][0][0] == "honeyhive_inputs.config"
        # Should be JSON string
        assert isinstance(calls[0][0][1], str)
        assert "key" in calls[0][0][1]
        assert "value" in calls[0][0][1]


class TestSessionLinking:
    """Test TASK 5: Session linking."""

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_session_id_captured_in_results(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that session_id is captured in execution results."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        expected_session_id = "session-abc-123"
        mock_tracer.session_id = expected_session_id

        def simple_function(_datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        context = ExperimentContext(
            run_id="run-123",
            dataset_id="ds-456",
            project="test-project",
        )

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        results = run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Verify session_id was captured in results
        assert len(results) == 1
        assert "session_id" in results[0]
        assert results[0]["session_id"] == expected_session_id

    @patch("honeyhive.experiments.core.force_flush_tracer")
    @patch("honeyhive.experiments.core.HoneyHiveTracer")
    def test_run_id_in_tracer_config(
        self, mock_tracer_class: Mock, _mock_flush: Mock
    ) -> None:
        """Test that run_id is included in tracer config for linking."""
        mock_tracer = Mock()
        mock_tracer_class.return_value = mock_tracer
        mock_tracer.session_id = "session-123"

        run_id = "run-xyz-789"

        def simple_function(_datapoint: Dict[str, Any]) -> Dict[str, Any]:
            return {"output": "test"}

        context = ExperimentContext(
            run_id=run_id,
            dataset_id="ds-456",
            project="test-project",
        )

        dataset = [{"inputs": {"query": "test"}}]
        datapoint_ids = ["dp-1"]

        run_experiment(
            function=simple_function,
            dataset=dataset,
            datapoint_ids=datapoint_ids,
            experiment_context=context,
            api_key="test-key",
            max_workers=1,
        )

        # Verify tracer was initialized with run_id directly in kwargs
        tracer_call_kwargs = mock_tracer_class.call_args[1]
        assert "run_id" in tracer_call_kwargs
        assert tracer_call_kwargs["run_id"] == run_id
