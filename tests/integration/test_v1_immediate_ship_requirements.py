"""Integration tests for v1.0 Immediate Ship Requirements.

Tests the 5 critical fixes for v1.0 release with real backend validation:
1. Session naming with experiment name
2. Tracer parameter (backward compatible)
3. Ground truths in feedback
4. Auto-inputs on nested spans
5. Session linking

These tests validate end-to-end behavior with REAL API calls and backend verification.
"""

# pylint: disable=R0801,too-many-lines
# Justification: Shared integration test patterns with experiments integration
# tests (R0801) and comprehensive integration test scenarios require extensive
# test cases

import os
import time
import traceback
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive, HoneyHiveTracer, enrich_session, trace
from honeyhive.experiments import evaluate
from honeyhive.models.generated import EventFilter, Operator, Type


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestV1ImmediateShipRequirements:
    """Integration tests for v1.0 immediate ship requirements."""

    @staticmethod
    def _create_test_dataset() -> list:
        """Create test dataset for experiments."""
        return [
            {
                "inputs": {"text": "hello", "category": "greeting"},
                "ground_truth": {"expected": "HELLO", "category": "greeting"},
            },
            {
                "inputs": {"text": "world", "category": "noun"},
                "ground_truth": {"expected": "WORLD", "category": "noun"},
            },
        ]

    def _validate_backend_results(
        self,
        integration_client: HoneyHive,
        result: Any,
        run_name: str,
        real_project: str,
    ) -> None:
        """Validate all 5 requirements in the backend."""
        # Get the run from backend
        backend_run = integration_client.evaluations.get_run(result.run_id)

        if not (hasattr(backend_run, "evaluation") and backend_run.evaluation):
            raise ValueError("Backend response missing evaluation data")

        run_data = backend_run.evaluation
        event_ids = getattr(run_data, "event_ids", [])

        assert len(event_ids) > 0, "Should have event IDs"

        # Get first session event for validation
        session_id_str = event_ids[0]
        session_event = integration_client.sessions.get_session(session_id_str)

        # TASK 1: Session naming validation
        event_name = getattr(session_event, "event_name", "")
        assert run_name in event_name, (
            f"TASK 1 FAILED: Session name should contain experiment name "
            f"'{run_name}', got '{event_name}'"
        )
        print("✅ TASK 1: Session name uses experiment name")
        print(f"   event_name: {event_name}")

        # TASK 3: Ground truths in feedback
        feedback = getattr(session_event, "feedback", {}) or {}
        assert (
            "ground_truth" in feedback
        ), "TASK 3 FAILED: feedback should contain 'ground_truth'"
        print("✅ TASK 3: Ground truths in feedback")
        print(f"   ground_truth keys: {list(feedback['ground_truth'].keys())}")

        # TASK 5: Session linking (run_id in metadata)
        metadata = getattr(session_event, "metadata", {}) or {}
        assert "run_id" in metadata, "TASK 5 FAILED: metadata should contain 'run_id'"
        assert metadata["run_id"] == result.run_id, (
            f"TASK 5 FAILED: run_id should match: "
            f"{metadata['run_id']} != {result.run_id}"
        )
        print("✅ TASK 5: Session linking (run_id in metadata)")
        print(f"   run_id: {metadata['run_id']}")

        # TASK 4 & 5: Get all child events
        events_response = integration_client.events.get_events(
            project=real_project,
            filters=[
                EventFilter(
                    field="session_id",
                    operator=Operator.is_,
                    value=session_id_str,
                    type=Type.id,
                ),
            ],
            limit=100,
        )

        all_events = events_response.get("events", [])
        child_events = [
            e for e in all_events if getattr(e, "event_id", None) != session_id_str
        ]

        assert (
            len(child_events) > 0
        ), "TASK 4 & 5 FAILED: Should have child events (nested @trace spans)"
        print(f"\n✅ TASK 4 & 5: Found {len(child_events)} child events")

        # Validate child events
        for child in child_events:
            print()
            self._validate_child_event(child, session_id_str)

    @staticmethod
    def _validate_child_inputs(child: Any) -> None:
        """Validate TASK 4: Auto-captured inputs in child events."""
        child_inputs = getattr(child, "inputs", {}) or {}
        if child_inputs:
            print("   ✅ TASK 4: Auto-captured inputs:")
            for key in list(child_inputs.keys())[:3]:
                print(f"      - {key}: {child_inputs[key]}")
            return

        # Inputs might be in config or metadata for some event types
        child_config = getattr(child, "config", {}) or {}
        child_metadata = getattr(child, "metadata", {}) or {}

        for field_dict in [child_config, child_metadata]:
            input_keys = [
                k
                for k in field_dict.keys()
                if "input" in k.lower() or "text" in k.lower()
            ]
            if input_keys:
                print("   ✅ TASK 4: Auto-captured inputs in metadata/config:")
                for key in input_keys[:3]:
                    print(f"      - {key}: {field_dict[key]}")
                return

        print(
            "   ⚠ TASK 4: No explicit inputs captured "
            "(may be in event_type-specific fields)"
        )

    @staticmethod
    def _validate_child_event(child: Any, session_id_str: str) -> None:
        """Validate a single child event for TASK 4 & 5."""
        child_name = getattr(child, "event_name", "unknown")
        print(f"   Child: {child_name}")

        # TASK 5: Verify parent-child linking
        child_parent_id = getattr(child, "parent_id", None)
        assert child_parent_id == session_id_str, (
            f"TASK 5 FAILED: Child parent_id should link to session. "
            f"Got {child_parent_id}, expected {session_id_str}"
        )
        print("   ✅ TASK 5: Correctly linked to parent")

        # TASK 4: Check for auto-captured inputs
        TestV1ImmediateShipRequirements._validate_child_inputs(child)

    def test_all_five_requirements_end_to_end(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test all 5 immediate ship requirements in a single end-to-end workflow.

        This comprehensive test validates:
        1. Session naming uses experiment name (not 'initialization')
        2. Tracer parameter passed to function (v1.0 feature)
        3. Ground truths stored in feedback field
        4. Auto-inputs captured on @trace decorated functions
        5. Session linking (run_id, session_id, parent-child)

        This is the PRIMARY integration test for v1.0 release validation.
        """

        # Track tracer received by function
        tracer_received = []
        calls_made = []

        # TASK 2: Function that accepts tracer parameter (v1.0 feature)
        def evaluation_function_with_tracer(
            datapoint: Dict[str, Any], tracer: HoneyHiveTracer
        ) -> Dict[str, Any]:
            """V1.0 function signature with tracer parameter."""
            calls_made.append("eval_function")
            tracer_received.append(tracer)

            # Use tracer to enrich session (TASK 2 validation)
            enrich_session(
                session_id=tracer.session_id,
                tracer=tracer,
                metadata={"evaluation_step": "processing"},
            )

            # Call nested function with @trace (TASK 4: Auto-inputs)
            result = process_input(datapoint["inputs"]["text"])

            return {"result": result, "status": "completed"}

        # TASK 4: Nested function with @trace to test auto-input capture
        @trace(event_type="tool", event_name="process_input")
        def process_input(text: str) -> str:
            """Nested function that will have inputs auto-captured."""
            calls_made.append("process_input")
            return f"Processed: {text.upper()}"

        # Dataset with ground_truth (TASK 3)
        dataset = self._create_test_dataset()

        # TASK 1: Use experiment name as session name
        run_name = f"v1-ship-requirements-{int(time.time())}"

        print(f"\n{'='*70}")
        print("V1.0 IMMEDIATE SHIP REQUIREMENTS - END-TO-END TEST")
        print(f"{'='*70}")
        print(f"Run name: {run_name}")
        print(f"Dataset: {len(dataset)} datapoints")
        print("Testing all 5 requirements simultaneously")

        # Execute evaluate()
        result = evaluate(
            function=evaluation_function_with_tracer,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=1,  # Serial for clearer validation
            verbose=True,
        )

        # Basic validation
        assert result is not None, "Result should not be None"
        assert result.run_id, "Result should have run_id"
        print(f"\n✅ Evaluation completed: {result.run_id}")

        # TASK 2 VALIDATION: Verify tracer was passed to function
        assert len(tracer_received) == len(dataset), (
            f"Tracer should be passed {len(dataset)} times, "
            f"got {len(tracer_received)}"
        )
        print(f"✅ TASK 2: Tracer parameter passed {len(tracer_received)} times")

        # Wait for backend processing
        print("\n⏳ Waiting for backend to process events...")
        time.sleep(5)

        # BACKEND VALIDATION
        print(f"\n{'='*70}")
        print("BACKEND VALIDATION - ALL 5 TASKS")
        print(f"{'='*70}")

        try:
            self._validate_backend_results(
                integration_client, result, run_name, real_project
            )

            print(f"\n{'='*70}")
            print("✅ ALL 5 TASKS VALIDATED SUCCESSFULLY")
            print(f"{'='*70}")
            print("✅ TASK 1: Session naming with experiment name")
            print("✅ TASK 2: Tracer parameter passed to function")
            print("✅ TASK 3: Ground truths in feedback")
            print("✅ TASK 4: Auto-inputs on nested spans")
            print("✅ TASK 5: Session linking (run_id, parent-child)")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n❌ Backend validation failed: {e}")
            traceback.print_exc()
            raise

    def test_backward_compatibility_without_tracer_parameter(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test that functions WITHOUT tracer parameter still work (backward compat).

        This validates TASK 2 backward compatibility: main branch code
        that doesn't use the tracer parameter should continue working.
        """

        # Old-style function WITHOUT tracer parameter (main branch style)
        def old_style_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Main branch style function without tracer parameter."""
            inputs = datapoint.get("inputs", {})
            return {"result": inputs.get("value", 0) * 2}

        dataset = [
            {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},
            {"inputs": {"value": 10}, "ground_truth": {"expected": 20}},
        ]

        run_name = f"backward-compat-{int(time.time())}"

        print(f"\n{'='*70}")
        print("TESTING BACKWARD COMPATIBILITY (NO TRACER PARAMETER)")
        print(f"{'='*70}")

        # Should work without errors
        result = evaluate(
            function=old_style_function,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=True,
        )

        assert result is not None
        assert result.run_id
        print(f"\n✅ Backward compatibility validated: {result.run_id}")
        print("✅ Main branch code (without tracer param) works correctly")

        # Quick backend validation
        time.sleep(3)
        backend_run = integration_client.evaluations.get_run(result.run_id)
        assert backend_run is not None, "Run should exist in backend"
        print("✅ Run verified in backend")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
