"""Integration tests — managed dataset × client-side evaluators (Cell 3).

Same inline ``enrich_span(metrics=…)`` attachment path as Cell 1, but
the dataset is a HoneyHive-managed dataset (created via the SDK's
datasets API + linked datapoints) instead of an inline external list.

This cell exercises the ``dataset_id=`` branch of ``evaluate()`` —
``client.datasets.list(dataset_id=…)`` is hit, datapoints are fetched
one-by-one via ``client.datapoints.get_datapoint(...)``, and the
``EXT-`` prefix never appears in either the dataset_id or the
datapoint_ids. The chain-span metric-attachment guarantees still hold.
"""

# pylint: disable=R0801
# Justification: integration setup fixtures are intentionally similar
# across cells.

import os
import time
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import evaluate
from tests.integration._experiments_helpers import (
    assert_run_metadata_on_all_child_events,
    assert_standard_suite_attached_to_chain_spans,
    chain_events_for_function,
    create_managed_dataset,
    event_field,
    event_metrics,
    export_events_for_run_polling,
    safe_delete_dataset,
    standard_evaluator_suite,
)


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsManagedClientSide:
    """managed dataset × client-side evaluators."""

    def test_basic_managed_dataset_evaluation(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Smoke test: dataset linkage, event count, run state for managed path.

        This is the historical 'managed dataset' integration test — it
        validates the SDK's managed-dataset wiring (dataset creation,
        datapoint linkage, evaluate(dataset_id=…), backend dataset_id on
        the run, event count = datapoint count). The richer chain-span
        metric assertions live in
        ``test_inline_chain_span_attachment`` below.
        """
        timestamp = int(time.time())
        dataset_name = f"managed-client-basic-{timestamp}"
        run_name = f"managed-client-basic-run-{timestamp}"

        datapoints = [
            {
                "inputs": {"question": "What is 5 + 3?", "category": "math"},
                "ground_truth": {"answer": "8", "explanation": "Simple addition"},
            },
            {
                "inputs": {
                    "question": "What is the capital of Japan?",
                    "category": "geography",
                },
                "ground_truth": {"answer": "Tokyo", "explanation": "Capital city"},
            },
            {
                "inputs": {"question": "What color is the sun?", "category": "science"},
                "ground_truth": {
                    "answer": "yellow",
                    "explanation": "Visible spectrum",
                },
            },
        ]

        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        try:

            def test_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
                inputs = datapoint.get("inputs", {})
                question = inputs.get("question", "")
                category = inputs.get("category", "unknown")
                return {
                    "response": f"Processing: {question}",
                    "category": category,
                    "processed": True,
                }

            def answer_checker(
                outputs: Dict[str, Any],
                _inputs: Dict[str, Any],
                ground_truth: Dict[str, Any],
            ) -> float:
                # Containment check — "Tokyo" appears in "Processing: What is
                # the capital of Japan?" only when ground truth happens to
                # match a substring; the value here is "ran cleanly", not
                # the score itself.
                response = outputs.get("response", "").lower()
                expected_answer = ground_truth.get("answer", "").lower()
                return 1.0 if expected_answer in response else 0.5

            result = evaluate(
                function=test_function,
                dataset_id=dataset_id,
                evaluators=[answer_checker],
                api_key=real_api_key,
                project=real_project,
                name=run_name,
                max_workers=2,
                verbose=False,
            )
            assert result is not None and result.run_id

            backend_run = integration_client.evaluations.get_run(result.run_id)
            assert hasattr(backend_run, "evaluation") and backend_run.evaluation, (
                f"Backend response missing 'evaluation' field: {backend_run}"
            )
            run_data = backend_run.evaluation

            assert str(getattr(run_data, "dataset_id", "")) == str(dataset_id), (
                f"Backend dataset_id {getattr(run_data, 'dataset_id', None)!r} "
                f"!= created dataset_id {dataset_id!r}"
            )
            event_ids = getattr(run_data, "event_ids", []) or []
            assert len(event_ids) == len(datapoints), (
                f"Expected {len(datapoints)} session events, got {len(event_ids)}"
            )

        finally:
            safe_delete_dataset(integration_client, dataset_id)

    def test_inline_chain_span_attachment(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Rich chain-span metric attachment when the dataset is managed.

        Mirrors the assertions of
        ``TestExperimentsExternalClientSide.test_inline_chain_span_attachment_sync``
        but the dataset is a real HoneyHive-managed dataset (created via
        the SDK and referenced by ``dataset_id=…``).

        Asserts:
        * Every child event carries
          ``metadata.{run_id, dataset_id, datapoint_id}`` and
          ``dataset_id`` matches the created managed dataset (no ``EXT-``
          prefix).
        * All four standard evaluator return shapes (scalar float, scalar
          bool, dict-with-explanation, dict-with-extras) survive
          end-to-end onto the chain span.
        """
        timestamp = int(time.time())
        dataset_name = f"managed-client-rich-{timestamp}"
        run_name = f"managed-client-rich-run-{timestamp}"

        # Same passing+failing two-datapoint shape as Cell 1 so the
        # standard-suite assertions can compare branches consistently.
        datapoints = [
            {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},  # pass
            {"inputs": {"value": 8}, "ground_truth": {"expected": 99}},  # fail
        ]

        dataset_id = create_managed_dataset(
            integration_client, real_project, dataset_name, datapoints
        )

        try:

            def double_value_function(
                datapoint: Dict[str, Any],
            ) -> Dict[str, Any]:
                # Locally defined (rather than imported from helpers) so
                # the chain span name reads ``double_value_function``
                # exactly the same as Cell 1 — assertions reuse the
                # same standard-suite helper.
                return {"result": datapoint["inputs"]["value"] * 2}

            result = evaluate(
                function=double_value_function,
                dataset_id=dataset_id,
                evaluators=standard_evaluator_suite(),
                api_key=real_api_key,
                project=real_project,
                name=run_name,
                max_workers=2,
                verbose=False,
            )
            assert result is not None and result.run_id

            events = export_events_for_run_polling(
                integration_client,
                result.run_id,
                function_name="double_value_function",
                expected_chain_span_count=len(datapoints),
            )
            assert events, f"No events returned for run {result.run_id}"

            assert_run_metadata_on_all_child_events(events, result.run_id)

            # Managed dataset: dataset_id on every child event must equal
            # the dataset we just created (no ``EXT-`` synthetic prefix).
            for ev in events:
                if event_field(ev, "event_type") in ("chain", "tool", "model"):
                    md = event_field(ev, "metadata") or {}
                    md_ds = (
                        str(md.get("dataset_id", "")) if isinstance(md, dict) else ""
                    )
                    assert md_ds == str(dataset_id), (
                        f"event {event_field(ev, 'event_id')} dataset_id "
                        f"{md_ds!r} != managed dataset_id {dataset_id!r}; "
                        f"metadata={md}"
                    )
                    assert not md_ds.startswith("EXT-"), (
                        f"managed-dataset cell unexpectedly produced EXT- "
                        f"dataset_id {md_ds!r}"
                    )

            assert_standard_suite_attached_to_chain_spans(
                events,
                function_name="double_value_function",
                expected_dataset_size=len(datapoints),
            )

            # Sanity: chain spans came through as expected (one per dp).
            chains = chain_events_for_function(events, "double_value_function")
            assert len(chains) == len(datapoints)
            for ev in chains:
                # Each chain span carries every standard-suite key.
                m = event_metrics(ev)
                assert "chain_eval" in m and "is_positive" in m
                assert "confidence_eval" in m and "judge_eval" in m

        finally:
            safe_delete_dataset(integration_client, dataset_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
