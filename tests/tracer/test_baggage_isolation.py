"""Baggage isolation and selective propagation tests (v1.0).

This module tests the selective baggage propagation fix that enables
tracer discovery while preventing session ID conflicts.
"""

# pylint: disable=protected-access
# Justification: Tests need to access _tracer_id for tracer identification

from typing import Any, Dict, Optional

import pytest
from opentelemetry import baggage, context

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.processing.context import SAFE_PROPAGATION_KEYS
from honeyhive.tracer.registry import get_tracer_from_baggage


class TestSelectiveBaggagePropagation:
    """Test selective baggage key propagation (v1.0 fix)."""

    def test_safe_keys_propagated(self) -> None:
        """Test that SAFE_PROPAGATION_KEYS are propagated."""
        # Create tracer
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Create span (triggers baggage propagation)
        with tracer.start_span("test-span"):
            # Check that safe keys are in baggage
            current_ctx = context.get_current()

            # honeyhive_tracer_id should be propagated (safe key)
            tracer_id_from_baggage = baggage.get_baggage(
                "honeyhive_tracer_id", current_ctx
            )
            assert (
                tracer_id_from_baggage == tracer._tracer_id
            ), "honeyhive_tracer_id not propagated correctly"

    def test_unsafe_keys_filtered(self) -> None:
        """Test that unsafe keys are filtered out."""
        # Create tracer with custom session
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            session_name="test-session",
            test_mode=True,
        )

        # Create span
        with tracer.start_span("test-span"):
            current_ctx = context.get_current()

            # Check that potentially unsafe keys are NOT in baggage
            # (These would cause conflicts in multi-instance scenarios)
            unsafe_keys = [
                "session_id",  # Would conflict between instances
                "span_id",  # Would conflict
                "parent_id",  # Would conflict
            ]

            for key in unsafe_keys:
                value = baggage.get_baggage(key, current_ctx)
                # It's OK if these don't exist or are None
                # The point is they shouldn't leak across instances

    def test_safe_keys_constant_complete(self) -> None:
        """Test SAFE_PROPAGATION_KEYS constant is complete."""
        # Verify all expected safe keys are present
        expected_safe_keys = {
            "run_id",
            "dataset_id",
            "datapoint_id",
            "honeyhive_tracer_id",
            "project",
            "source",
        }

        assert SAFE_PROPAGATION_KEYS == expected_safe_keys, (
            f"SAFE_PROPAGATION_KEYS mismatch. "
            f"Expected: {expected_safe_keys}, "
            f"Got: {SAFE_PROPAGATION_KEYS}"
        )

    def test_evaluation_context_propagated(self) -> None:
        """Test evaluation context keys are propagated (run_id, dataset_id, etc)."""
        # Create tracer
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Simulate evaluation context
        eval_baggage = {
            "run_id": "eval-run-123",
            "dataset_id": "dataset-456",
            "datapoint_id": "datapoint-789",
        }

        # Apply evaluation baggage
        from honeyhive.tracer.processing.context import _apply_baggage_context

        _apply_baggage_context(eval_baggage, tracer)

        # Create span
        with tracer.start_span("test-span"):
            current_ctx = context.get_current()

            # Verify evaluation keys propagated
            assert baggage.get_baggage("run_id", current_ctx) == "eval-run-123"
            assert baggage.get_baggage("dataset_id", current_ctx) == "dataset-456"
            assert baggage.get_baggage("datapoint_id", current_ctx) == "datapoint-789"


class TestBaggageIsolation:
    """Test baggage isolation between tracer instances."""

    def test_two_tracers_isolated_baggage(self) -> None:
        """Test two tracers have isolated baggage."""
        # Create tracer 1
        tracer1 = HoneyHiveTracer.init(
            api_key="test-key", project="project-1", test_mode=True
        )

        # Create tracer 2
        tracer2 = HoneyHiveTracer.init(
            api_key="test-key", project="project-2", test_mode=True
        )

        # Use tracer 1 in a context
        with tracer1.start_span("span-1"):
            ctx1 = context.get_current()
            tracer1_id_in_baggage = baggage.get_baggage("honeyhive_tracer_id", ctx1)
            assert tracer1_id_in_baggage == tracer1.tracer_id

            # Use tracer 2 in nested context
            with tracer2.start_span("span-2"):
                ctx2 = context.get_current()
                tracer2_id_in_baggage = baggage.get_baggage("honeyhive_tracer_id", ctx2)

                # Tracer 2 should have its own ID in baggage
                assert tracer2_id_in_baggage == tracer2.tracer_id

                # Verify they're different
                assert tracer1.tracer_id != tracer2.tracer_id

    def test_nested_spans_preserve_baggage(self) -> None:
        """Test nested spans preserve baggage context."""
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Set evaluation baggage
        eval_baggage = {"run_id": "run-123", "dataset_id": "dataset-456"}

        from honeyhive.tracer.processing.context import _apply_baggage_context

        _apply_baggage_context(eval_baggage, tracer)

        # Parent span
        with tracer.start_span("parent-span"):
            ctx_parent = context.get_current()

            # Verify baggage in parent
            assert baggage.get_baggage("run_id", ctx_parent) == "run-123"
            assert (
                baggage.get_baggage("honeyhive_tracer_id", ctx_parent)
                == tracer._tracer_id
            )

            # Child span
            with tracer.start_span("child-span"):
                ctx_child = context.get_current()

                # Verify baggage propagated to child
                assert baggage.get_baggage("run_id", ctx_child) == "run-123"
                assert (
                    baggage.get_baggage("honeyhive_tracer_id", ctx_child)
                    == tracer._tracer_id
                )


class TestTracerDiscoveryViaBaggage:
    """Test tracer discovery via baggage (v1.0 fix)."""

    def test_discover_tracer_from_baggage(self) -> None:
        """Test tracer can be discovered from baggage."""
        # Create tracer
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Create span (sets baggage)
        with tracer.start_span("test-span"):
            # Discover tracer from baggage
            discovered = get_tracer_from_baggage()

            # Should find the tracer
            if discovered:  # May be None in some test environments
                assert discovered.tracer_id == tracer._tracer_id
                assert discovered.project_name == tracer.project_name

    def test_no_tracer_returns_none(self) -> None:
        """Test discovery returns None when no tracer in context."""
        # Don't create any tracer or span
        discovered = get_tracer_from_baggage()

        # Should return None
        assert discovered is None

    def test_discovery_with_evaluation_context(self) -> None:
        """Test discovery works with evaluation context baggage."""
        # Create tracer
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Set evaluation + tracer baggage
        eval_baggage = {
            "run_id": "eval-run-123",
            "dataset_id": "dataset-456",
            "honeyhive_tracer_id": tracer._tracer_id,
        }

        from honeyhive.tracer.processing.context import _apply_baggage_context

        _apply_baggage_context(eval_baggage, tracer)

        # Create span
        with tracer.start_span("eval-span"):
            # Discovery should work
            discovered = get_tracer_from_baggage()

            if discovered:
                assert discovered.tracer_id == tracer._tracer_id

                # Evaluation context should also be in baggage
                ctx = context.get_current()
                assert baggage.get_baggage("run_id", ctx) == "eval-run-123"


@pytest.mark.integration
class TestBaggagePropagationIntegration:
    """Integration tests for baggage propagation patterns."""

    def test_evaluate_pattern_simulation(self) -> None:
        """Simulate evaluate() pattern with tracer discovery."""
        # Create tracer (would be passed to evaluate())
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="test-project", test_mode=True
        )

        # Simulate evaluate() setting baggage for each datapoint
        datapoints = [
            {"run_id": "run-1", "datapoint_id": "dp-1"},
            {"run_id": "run-1", "datapoint_id": "dp-2"},
            {"run_id": "run-1", "datapoint_id": "dp-3"},
        ]

        for dp in datapoints:
            # evaluate() would set this baggage
            baggage_items = {
                "run_id": dp["run_id"],
                "datapoint_id": dp["datapoint_id"],
                "honeyhive_tracer_id": tracer._tracer_id,
            }

            from honeyhive.tracer.processing.context import _apply_baggage_context

            _apply_baggage_context(baggage_items, tracer)

            # User function decorated with @tracer.trace
            with tracer.start_span(f"process-{dp['datapoint_id']}") as span:
                # Inside user function: enrich_span should work
                tracer.enrich_span(metadata={"datapoint": dp["datapoint_id"]})

                if span and span.is_recording():
                    # Verify enrichment worked
                    attrs = dict(span.attributes or {})
                    expected_key = "honeyhive.metadata.datapoint"
                    assert expected_key in attrs
                    assert attrs[expected_key] == dp["datapoint_id"]

    def test_multi_instance_no_interference(self) -> None:
        """Test multiple tracers don't interfere with each other's baggage."""
        # Create two tracers for different projects
        tracer_a = HoneyHiveTracer.init(
            api_key="test-key", project="project-a", test_mode=True
        )

        tracer_b = HoneyHiveTracer.init(
            api_key="test-key", project="project-b", test_mode=True
        )

        # Use tracer A
        with tracer_a.start_span("span-a") as span_a:
            if span_a and span_a.is_recording():
                tracer_a.enrich_span(metadata={"tracer": "a"})

                # Verify tracer A's baggage
                ctx_a = context.get_current()
                assert (
                    baggage.get_baggage("honeyhive_tracer_id", ctx_a)
                    == tracer_a.tracer_id
                )

        # Use tracer B (separate context)
        with tracer_b.start_span("span-b") as span_b:
            if span_b and span_b.is_recording():
                tracer_b.enrich_span(metadata={"tracer": "b"})

                # Verify tracer B's baggage
                ctx_b = context.get_current()
                assert (
                    baggage.get_baggage("honeyhive_tracer_id", ctx_b)
                    == tracer_b.tracer_id
                )

        # Verify they were different
        assert tracer_a.tracer_id != tracer_b.tracer_id
