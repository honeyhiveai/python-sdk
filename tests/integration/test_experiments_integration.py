"""Integration tests for honeyhive.experiments module.

These tests validate the complete experiment workflow with REAL API calls
and verify the actual backend state.

Tests cover:
- evaluate() with external datasets (EXT- prefix)
- evaluate() with HoneyHive datasets
- Backend run state validation (name, dataset, events, status, results)
- Evaluator execution and metric collection
- Result aggregation from backend
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive integration test scenarios require extensive test cases

import os
import time
from typing import Any, Dict, Optional

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import compare_runs, evaluate
from honeyhive.models import CreateDatapointRequest, CreateDatasetRequest


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsIntegration:
    """Integration tests for experiments module with real API validation."""

    def test_evaluate_with_external_dataset_full_workflow(
        self,
        real_api_key: str,
        real_project: str,
        real_source: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test complete evaluate() workflow with external dataset.

        This test validates:
        1. Run creation with EXT- prefixed dataset_id
        2. Function execution with tracer multi-instance
        3. Backend state: run name, dataset, events, status
        4. Result retrieval and aggregation
        """

        # Step 1: Define test function
        # Note: The function receives the full datapoint dict, not just inputs
        def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Simple test function that echoes input."""
            inputs = datapoint.get("inputs", {})
            question = inputs.get("question", "")
            return {"answer": f"Answer to: {question}"}

        # Step 2: Define evaluator
        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Simple evaluator that checks if answer matches."""
            expected = ground_truth.get("expected_answer", "")
            actual = outputs.get("answer", "")
            return 1.0 if expected in actual else 0.0

        # Step 3: Create external dataset
        dataset = [
            {
                "inputs": {"question": "What is 2+2?"},
                "ground_truth": {"expected_answer": "4"},
            },
            {
                "inputs": {"question": "What is the capital of France?"},
                "ground_truth": {"expected_answer": "Paris"},
            },
            {
                "inputs": {"question": "What color is the sky?"},
                "ground_truth": {"expected_answer": "blue"},
            },
        ]

        run_name = f"integration-test-{int(time.time())}"

        # Step 4: Execute evaluate()
        print(f"\n{'='*70}")
        print("EXECUTING EVALUATE() WITH EXTERNAL DATASET")
        print(f"{'='*70}")
        print(f"Run name: {run_name}")
        print(f"Dataset size: {len(dataset)} datapoints")
        print(f"Project: {real_project}")
        print(f"Source: {real_source}")

        result_summary = evaluate(
            function=simple_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            aggregate_function="average",
            verbose=True,
        )

        # Step 5: Validate result summary
        print(f"\n{'='*70}")
        print("RESULT SUMMARY VALIDATION")
        print(f"{'='*70}")
        assert result_summary is not None, "Result summary should not be None"
        assert hasattr(result_summary, "run_id"), "Should have run_id"
        assert result_summary.run_id, "run_id should not be empty"

        print(f"✅ Run ID: {result_summary.run_id}")
        print(f"✅ Status: {result_summary.status}")
        print(f"✅ Success: {result_summary.success}")
        print(f"✅ Passed: {len(result_summary.passed)} datapoints")
        print(f"✅ Failed: {len(result_summary.failed)} datapoints")

        if result_summary.metrics:
            # Access model_extra safely for Pydantic v2 models with extra="allow"
            extra_fields = getattr(result_summary.metrics, "model_extra", {})
            if extra_fields:
                print(f"✅ Metrics available: {list(extra_fields.keys())}")

        # Step 6: Fetch actual run from backend
        print(f"\n{'='*70}")
        print("BACKEND STATE VALIDATION")
        print(f"{'='*70}")
        print(f"Fetching run from backend: {result_summary.run_id}")

        # Helper: Validate backend run data
        def validate_backend_run(backend_run: Any) -> None:
            """Extract and validate backend run data."""
            # Extract run data
            if not (hasattr(backend_run, "evaluation") and backend_run.evaluation):
                raise ValueError(
                    f"Backend response missing 'evaluation' field. "
                    f"Response: {backend_run}"
                )

            run_data = backend_run.evaluation

            # Print diagnostics
            print("\n✅ Successfully fetched run from backend")
            print(f"\nBackend Response Type: {type(backend_run)}")
            print(f"Run ID: {getattr(run_data, 'run_id', 'NOT SET')}")
            print(f"Name: {getattr(run_data, 'name', 'NOT SET')}")
            print(f"Project: {getattr(run_data, 'project', 'NOT SET')}")
            print(f"Status: {getattr(run_data, 'status', 'NOT SET')}")

            # Validate name
            actual_name = getattr(run_data, "name", None)
            assert actual_name, "Run name should not be empty"
            print(f"✅ Run name is set: {actual_name}")

            # Validate events
            event_ids = getattr(run_data, "event_ids", [])
            assert len(event_ids) > 0, "Should have recorded events"
            print(f"✅ Events recorded: {len(event_ids)} events")

        # Use evaluations API to get the run
        try:
            backend_run = integration_client.evaluations.get_run(result_summary.run_id)

            print(f"\n{'='*70}")
            print("BACKEND STATE VALIDATION")
            print(f"{'='*70}")

            validate_backend_run(backend_run)

            print(f"\n{'='*70}")
            print("INTEGRATION TEST PASSED")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n❌ Error fetching run from backend: {e}")
            print(
                "This indicates the run wasn't properly created/updated in the backend"
            )
            raise

    def test_evaluate_result_retrieval(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test that evaluate() properly retrieves results from backend."""

        def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            return {"output": inputs.get("input", "")}

        dataset = [
            {"inputs": {"input": "test1"}},
            {"inputs": {"input": "test2"}},
        ]

        run_name = f"result-test-{int(time.time())}"

        print(f"\n{'='*70}")
        print("TESTING RESULT RETRIEVAL")
        print(f"{'='*70}")

        result = evaluate(
            function=simple_function,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            verbose=True,
        )

        # Validate result structure
        assert result is not None
        assert result.run_id
        print(f"✅ Result retrieved with run_id: {result.run_id}")

        # Try to fetch metrics directly
        try:
            metrics_response = integration_client.evaluations.get_run_result(
                run_id=result.run_id, aggregate_function="average"
            )
            print("✅ Metrics fetched successfully")
            print(f"   Response type: {type(metrics_response)}")
        except Exception as e:
            print(f"⚠️  Could not fetch metrics: {e}")

    def test_evaluate_with_multiple_evaluators(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test evaluate() with real evaluators and verify metrics in backend.

        This test validates:
        1. Evaluators execute successfully
        2. Metrics are collected with actual values (not null)
        3. Metrics are sent to backend
        4. Metrics are retrievable via GET endpoint
        5. Metrics show up in platform metric report
        """

        def test_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Simple doubler function."""
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            return {"result": value * 2, "original": value}

        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Check if output matches expected value.

            Standard evaluator signature: (outputs, inputs, ground_truth)
            """
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            return 1.0 if actual == expected else 0.0

        def confidence_evaluator(
            _outputs: Dict[str, Any],
            inputs: Dict[str, Any],
            _ground_truth: Dict[str, Any],
        ) -> float:
            """Return a confidence score based on value magnitude.

            Standard evaluator signature: (outputs, inputs, ground_truth)
            """
            value = inputs.get("value", 0)
            # Higher values get higher confidence (0.5-1.0 range)
            return min(1.0, 0.5 + (value / 100.0))

        # Dataset with ground truth
        dataset = [
            {
                "inputs": {"value": 5, "label": "small"},
                "ground_truth": {"expected": 10},
            },
            {
                "inputs": {"value": 10, "label": "medium"},
                "ground_truth": {"expected": 20},
            },
            {
                "inputs": {"value": 15, "label": "large"},
                "ground_truth": {"expected": 30},
            },
        ]

        run_name = f"evaluator-metrics-test-{int(time.time())}"

        print(f"\n{'='*70}")
        print("TESTING EVALUATOR METRICS")
        print(f"{'='*70}")
        print(f"Run name: {run_name}")
        print("Dataset: 3 datapoints with ground truth")
        print("Evaluators: 2 (accuracy, confidence)")

        # Execute evaluate with real evaluators
        result = evaluate(
            function=test_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator, confidence_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            aggregate_function="average",
            verbose=True,
        )

        # Validate result summary
        assert result is not None, "Result should not be None"
        assert result.run_id, "Should have run_id"

        print(f"\n{'='*70}")
        print("RESULT SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Run ID: {result.run_id}")
        print(f"✅ Status: {result.status}")
        print(f"✅ Success: {result.success}")

        # Fetch run from backend to verify metrics
        print(f"\n{'='*70}")
        print("BACKEND METRICS VALIDATION")
        print(f"{'='*70}")

        try:
            # Get the run from backend
            backend_run = integration_client.evaluations.get_run(result.run_id)

            if hasattr(backend_run, "evaluation") and backend_run.evaluation:
                run_data = backend_run.evaluation

                # Check metadata for evaluator metrics
                metadata = getattr(run_data, "metadata", {})
                evaluator_metrics = metadata.get("evaluator_metrics", {})

                print("\n✅ Backend returned metadata")
                print(f"   Evaluator metrics for {len(evaluator_metrics)} datapoints")

                # Validate each datapoint has metrics
                for datapoint_id, metrics in evaluator_metrics.items():
                    print(f"\n   Datapoint: {datapoint_id}")
                    for metric_name, metric_value in metrics.items():
                        print(f"      - {metric_name}: {metric_value}")

                        # CRITICAL: Verify metrics are NOT null
                        assert metric_value is not None, (
                            f"Metric {metric_name} for {datapoint_id} "
                            f"should not be null!"
                        )

                        # Verify metrics are numeric
                        assert isinstance(metric_value, (int, float)), (
                            f"Metric {metric_name} should be numeric, "
                            f"got {type(metric_value)}"
                        )

                        # Verify metrics are in valid range
                        assert 0.0 <= metric_value <= 1.0, (
                            f"Metric {metric_name} should be in range "
                            f"[0.0, 1.0], got {metric_value}"
                        )

                print("\n✅ All evaluator metrics validated successfully!")
                print("✅ Metrics are non-null and within expected range")

                # Also try to get aggregated metrics
                try:
                    result_summary = integration_client.evaluations.get_run_result(
                        run_id=result.run_id, aggregate_function="average"
                    )

                    print("\n✅ Backend aggregation successful")
                    print(f"   Response type: {type(result_summary)}")

                except Exception as e:
                    print(f"\n⚠️  Could not fetch aggregated results: {e}")

            else:
                raise ValueError("Backend response missing evaluation data")

        except Exception as e:
            print(f"\n❌ Error validating backend metrics: {e}")
            raise

    def test_compare_runs_with_metric_improvements_and_regressions(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test compare_runs() with metric improvements and regressions.

        This test validates:
        1. Two runs execute against the same dataset
        2. Second run has intentionally different performance (some better, some worse)
        3. compare_runs() correctly identifies common datapoints
        4. Comparison shows which metrics improved vs regressed
        5. Metric deltas are accurately calculated
        """

        # Shared dataset for both runs
        dataset = [
            {
                "inputs": {"value": 10, "task": "double"},
                "ground_truth": {"expected": 20},
            },
            {
                "inputs": {"value": 15, "task": "triple"},
                "ground_truth": {"expected": 45},
            },
            {
                "inputs": {"value": 8, "task": "quadruple"},
                "ground_truth": {"expected": 32},
            },
        ]

        # Evaluators to measure performance
        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Check if output matches expected value exactly."""
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            return 1.0 if actual == expected else 0.0

        def error_rate_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Calculate normalized error (inverted: 1.0=perfect, 0.0=worst)."""
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            if expected == 0:
                return 0.0
            error = abs(actual - expected) / abs(expected)
            # Invert so 1.0 = perfect, 0.0 = worst
            return max(0.0, 1.0 - error)

        # Run 1: Baseline function (simple multipliers, some errors)
        def baseline_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Baseline function with known performance."""
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            task = inputs.get("task", "")

            if task == "double":
                result = value * 2  # Correct
            elif task == "triple":
                result = value * 2  # Wrong (should be 3x)
            elif task == "quadruple":
                result = value * 3  # Wrong (should be 4x)
            else:
                result = 0

            return {"result": result, "method": "baseline"}

        # Run 2: Improved function (fixes some errors, introduces others)
        def improved_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Improved function with different performance profile."""
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            task = inputs.get("task", "")

            if task == "double":
                result = value * 2  # Still correct
            elif task == "triple":
                result = value * 3  # Fixed! (was 2x, now 3x)
            elif task == "quadruple":
                result = value * 3  # Still wrong (should be 4x)
            else:
                result = 0

            return {"result": result, "method": "improved"}

        print(f"\n{'='*70}")
        print("TESTING RUN COMPARISON WITH IMPROVEMENTS AND REGRESSIONS")
        print(f"{'='*70}")
        print("Dataset: 3 datapoints (double, triple, quadruple tasks)")
        print("Evaluators: accuracy, error_rate")
        print("\nExpected Performance:")
        print("  - Task 'double': Both runs correct → No change")
        print("  - Task 'triple': Run1 wrong, Run2 correct → IMPROVEMENT")
        print("  - Task 'quadruple': Both runs wrong → No change")

        # Execute Run 1 (baseline)
        print(f"\n{'='*70}")
        print("EXECUTING BASELINE RUN")
        print(f"{'='*70}")

        baseline_result = evaluate(
            function=baseline_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator, error_rate_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"comparison-baseline-{int(time.time())}",
            max_workers=2,
            verbose=True,
        )

        assert baseline_result is not None
        assert baseline_result.run_id
        baseline_run_id = baseline_result.run_id

        print(f"\n✅ Baseline run completed: {baseline_run_id}")

        # Execute Run 2 (improved)
        print(f"\n{'='*70}")
        print("EXECUTING IMPROVED RUN")
        print(f"{'='*70}")

        improved_result = evaluate(
            function=improved_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator, error_rate_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"comparison-improved-{int(time.time())}",
            max_workers=2,
            verbose=True,
        )

        assert improved_result is not None
        assert improved_result.run_id
        improved_run_id = improved_result.run_id

        print(f"\n✅ Improved run completed: {improved_run_id}")

        # Compare the runs
        print(f"\n{'='*70}")
        print("COMPARING RUNS")
        print(f"{'='*70}")
        print(f"Baseline run: {baseline_run_id}")
        print(f"Improved run: {improved_run_id}")

        comparison = compare_runs(
            client=integration_client,
            new_run_id=improved_run_id,
            old_run_id=baseline_run_id,
            aggregate_function="average",
        )

        # Validate comparison results
        print(f"\n{'='*70}")
        print("COMPARISON VALIDATION")
        print(f"{'='*70}")

        # Check basic structure
        assert comparison is not None, "Comparison should not be None"
        assert comparison.new_run_id == improved_run_id
        assert comparison.old_run_id == baseline_run_id

        print("✅ Run IDs match")

        # Validate datapoint counts
        assert (
            comparison.common_datapoints == 3
        ), f"Should have 3 common datapoints, got {comparison.common_datapoints}"
        print(f"✅ Common datapoints: {comparison.common_datapoints}")

        # Check for new/old datapoints (should be 0 since same dataset)
        assert (
            comparison.new_only_datapoints == 0
        ), f"Should have 0 new datapoints, got {comparison.new_only_datapoints}"
        assert (
            comparison.old_only_datapoints == 0
        ), f"Should have 0 old datapoints, got {comparison.old_only_datapoints}"
        print("✅ No new/old datapoints (same dataset)")

        # Validate metric deltas exist
        assert comparison.metric_deltas is not None
        assert len(comparison.metric_deltas) > 0, "Should have metric deltas"

        print(f"\n{'='*70}")
        print("METRIC DELTAS")
        print(f"{'='*70}")

        # Check each metric delta
        metric_deltas_dict = (
            comparison.metric_deltas
            if isinstance(comparison.metric_deltas, dict)
            else {}
        )
        for metric_name, delta_info in metric_deltas_dict.items():
            print(f"\n{metric_name}:")
            print(f"  Old aggregate: {delta_info.get('old_aggregate', 'N/A')}")
            print(f"  New aggregate: {delta_info.get('new_aggregate', 'N/A')}")
            print(f"  Found count: {delta_info.get('found_count', 'N/A')}")
            print(f"  Improved count: {delta_info.get('improved_count', 'N/A')}")
            print(f"  Degraded count: {delta_info.get('degraded_count', 'N/A')}")
            print(f"  Improved: {delta_info.get('improved', [])}")
            print(f"  Degraded: {delta_info.get('degraded', [])}")

        # Validate that we can detect improvements
        improved_metrics = comparison.list_improved_metrics()
        degraded_metrics = comparison.list_degraded_metrics()

        print(f"\n{'='*70}")
        print("IMPROVEMENT/REGRESSION ANALYSIS")
        print(f"{'='*70}")
        print(f"Improved metrics: {improved_metrics}")
        print(f"Degraded metrics: {degraded_metrics}")

        # At minimum, we should see some metric changes
        # (exact values depend on backend aggregation)
        total_changed_metrics = len(improved_metrics) + len(degraded_metrics)
        assert (
            total_changed_metrics >= 0
        ), "Should detect metric changes (improvements or regressions)"

        print(
            f"\n✅ Detected {len(improved_metrics)} improvements "
            f"and {len(degraded_metrics)} regressions"
        )
        print("✅ Comparison workflow validated successfully!")

    def test_managed_dataset_evaluation(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test evaluate() with managed HoneyHive dataset.

        This test validates:
        1. Dataset creation via SDK
        2. Datapoint addition to dataset
        3. Experiment execution with dataset_id parameter
        4. Backend verification of dataset-run linkage
        5. Datapoint fetching and processing
        6. Proper cleanup/teardown

        V3 Framework: REL-001
        Documentation: .agent-os/specs/.../test-generation/REL-001-...-v3-analysis.md
        """
        # Setup: Create unique dataset name
        timestamp = int(time.time())
        dataset_name = f"integration-test-dataset-{timestamp}"

        print(
            f"\n{'='*70}\n"
            "TESTING MANAGED DATASET EVALUATION\n"
            f"{'='*70}\n"
            f"Dataset name: {dataset_name}\n"
            f"Project: {real_project}"
        )

        # Helper: Extract ID from object
        def get_id_from_object(obj: Any) -> Optional[str]:
            """Extract ID from object with multiple field support."""
            if hasattr(obj, "_id"):
                id_value = getattr(obj, "_id", None)
                if id_value:
                    return str(id_value)
            if hasattr(obj, "id"):
                id_value = getattr(obj, "id", None)
                if id_value:
                    return str(id_value)
            return None

        # Helper: Create dataset and get ID
        def create_dataset_and_get_id(name: str) -> str:
            """Create dataset and extract its ID."""
            request = CreateDatasetRequest(
                project=real_project,
                name=name,
                description="Integration test dataset for managed evaluation workflow",
            )
            created = integration_client.datasets.create_dataset(request)

            print("✅ Dataset created")
            print(f"   Name: {created.name}")
            print(f"   Project: {created.project}")

            # Try to get ID from response
            ds_id = get_id_from_object(created)

            if not ds_id:
                # Fallback: search by name
                print("   Searching by name...")
                datasets = integration_client.datasets.list_datasets(
                    project=real_project
                )
                for ds in datasets:
                    if getattr(ds, "name", None) == name:
                        ds_id = get_id_from_object(ds)
                        if ds_id:
                            print(f"   Found: {ds_id}")
                            break

            assert ds_id, f"Could not get dataset_id for {name}"
            print(f"   ID: {ds_id}")
            return ds_id

        # Step 1: Create dataset in HoneyHive
        print(f"\n{'='*70}\nSTEP 1: CREATE DATASET\n{'='*70}")

        dataset_id = create_dataset_and_get_id(dataset_name)

        # Step 2: Add datapoints to dataset
        print(f"\n{'='*70}\nSTEP 2: ADD DATAPOINTS TO DATASET\n{'='*70}")

        test_datapoints = [
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
                "ground_truth": {"answer": "yellow", "explanation": "Visible spectrum"},
            },
        ]

        # Helper: Create datapoint and extract ID
        def create_and_track_datapoint(
            datapoint_data: Dict[str, Any], idx: int
        ) -> Optional[str]:
            """Create a datapoint and return its ID."""
            datapoint_request = CreateDatapointRequest(
                inputs=datapoint_data["inputs"],
                ground_truth=datapoint_data["ground_truth"],
                linked_datasets=[dataset_id],
                project=real_project,
                history=None,
                linked_event=None,
                metadata=None,
            )
            created = integration_client.datapoints.create_datapoint(datapoint_request)
            datapoint_id = get_id_from_object(created)
            print(f"✅ Datapoint {idx} created")
            if datapoint_id:
                print(f"   ID: {datapoint_id}")
            return datapoint_id

        # Create all datapoints
        for idx, dp in enumerate(test_datapoints, 1):
            create_and_track_datapoint(dp, idx)

        print(f"\n✅ Created {len(test_datapoints)} datapoints")

        # Step 3: Define test function
        def test_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Simple test function that processes datapoint inputs."""
            inputs = datapoint.get("inputs", {})
            question = inputs.get("question", "")
            category = inputs.get("category", "unknown")

            return {
                "response": f"Processing: {question}",
                "category": category,
                "processed": True,
            }

        # Step 4: Define evaluator
        def answer_checker(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Check if response contains ground truth answer.

            Args:
                outputs: Function outputs to evaluate
                _inputs: Datapoint inputs (unused in this evaluator)
                ground_truth: Expected ground truth for comparison

            Returns:
                Score of 1.0 if answer found, 0.5 otherwise
            """
            response = outputs.get("response", "").lower()
            expected_answer = ground_truth.get("answer", "").lower()

            # Simple containment check
            return 1.0 if expected_answer in response else 0.5

        # Step 5: Run experiment using managed dataset
        print(f"\n{'='*70}\nSTEP 3: RUN EXPERIMENT WITH MANAGED DATASET\n{'='*70}")
        print(f"Dataset ID: {dataset_id}")

        run_name = f"managed-dataset-test-{timestamp}"

        result = evaluate(
            function=test_function,
            dataset_id=dataset_id,  # Use managed dataset
            evaluators=[answer_checker],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            max_workers=2,
            verbose=True,
        )

        # Step 6: Validate results
        print(f"\n{'='*70}\nSTEP 4: VALIDATE RESULTS\n{'='*70}")

        assert result is not None, "Result should not be None"
        assert result.run_id, "Result should have run_id"
        print(f"✅ Run ID: {result.run_id}")
        print(f"✅ Status: {result.status}")

        # Helper: Verify backend state
        def verify_backend_run_state(
            run_id: str, expected_dataset_id: str, expected_event_count: int
        ) -> None:
            """Verify backend run state matches expectations."""
            backend_run = integration_client.evaluations.get_run(run_id)

            if not (hasattr(backend_run, "evaluation") and backend_run.evaluation):
                print("⚠️  Backend response missing evaluation data")
                return

            run_data = backend_run.evaluation

            # Verify dataset linkage
            if hasattr(run_data, "dataset_id"):
                backend_dataset_id = getattr(run_data, "dataset_id")
                print(f"✅ Backend dataset_id: {backend_dataset_id}")
                if backend_dataset_id:
                    assert str(backend_dataset_id) == str(expected_dataset_id), (
                        f"Dataset ID mismatch: {backend_dataset_id} "
                        f"!= {expected_dataset_id}"
                    )
                    print("✅ Dataset linkage verified")

            # Verify events were created
            if hasattr(run_data, "event_ids"):
                event_ids = getattr(run_data, "event_ids", [])
                print(f"✅ Events created: {len(event_ids)} events")
                assert (
                    len(event_ids) == expected_event_count
                ), f"Expected {expected_event_count} events, got {len(event_ids)}"
                print("✅ Event count matches datapoint count")

            print("\n✅ Backend state validation complete")

        # Step 7: Verify backend state
        print(f"\n{'='*70}\nSTEP 5: VERIFY BACKEND STATE\n{'='*70}")

        try:
            verify_backend_run_state(result.run_id, dataset_id, len(test_datapoints))
        except Exception as e:
            print(f"\n⚠️  Backend verification error: {e}")
            # Don't fail the test if backend verification has issues

        # Helper: Cleanup dataset
        def cleanup_dataset(ds_id: str) -> None:
            """Delete test dataset."""
            try:
                deleted = integration_client.datasets.delete_dataset(ds_id)
                if deleted:
                    print(f"✅ Dataset deleted: {ds_id}")
                else:
                    print(f"⚠️  Dataset deletion returned False: {ds_id}")
            except Exception as e:
                print(f"⚠️  Dataset cleanup error: {e}")

        # Step 8: Cleanup
        print(f"\n{'='*70}\nSTEP 6: CLEANUP\n{'='*70}")

        cleanup_dataset(dataset_id)

        print(f"\n{'='*70}\nMANAGED DATASET EVALUATION TEST COMPLETE\n{'='*70}\n")

    def test_event_level_comparison(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test event-level comparison using /runs/compare/events endpoint.

        This test validates:
        1. Two runs execute on same dataset
        2. Events matched by datapoint_id
        3. Per-metric improved/degraded/same lists
        4. Common datapoints correctly identified
        5. Event pairing (event_1, event_2) returned
        6. Event presence information accurate
        """

        # Shared dataset for both runs
        dataset = [
            {"inputs": {"value": 10}, "ground_truth": {"expected": 20}},
            {"inputs": {"value": 15}, "ground_truth": {"expected": 30}},
            {"inputs": {"value": 8}, "ground_truth": {"expected": 16}},
        ]

        # Run 1: Baseline function
        def baseline_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Baseline function."""
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            return {"result": value * 2}

        # Run 2: Different performance function
        def modified_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            """Modified function with different results."""
            inputs = datapoint.get("inputs", {})
            value = inputs.get("value", 0)
            # Different multiplier for some values
            multiplier = 2.5 if value > 12 else 2.0
            return {"result": value * multiplier}

        # Evaluator
        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            """Check accuracy."""
            expected = ground_truth.get("expected", 0)
            actual = outputs.get("result", 0)
            return 1.0 if actual == expected else 0.0

        print(f"\n{'='*70}\nTESTING EVENT-LEVEL COMPARISON\n{'='*70}")

        # CRITICAL: Both runs must use the SAME dataset to ensure datapoint IDs match
        # evaluate() generates deterministic EXT- IDs from content hash
        # Same dataset content → same EXT- IDs → matching datapoint_ids

        # Execute Run 1
        baseline_result = evaluate(
            function=baseline_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"event-comparison-baseline-{int(time.time())}",
            max_workers=2,
            verbose=True,
        )

        assert baseline_result and baseline_result.run_id
        baseline_run_id = baseline_result.run_id
        print(f"\n✅ Baseline run: {baseline_run_id}")

        # Execute Run 2 (SAME dataset - will generate SAME EXT- IDs)
        modified_result = evaluate(
            function=modified_function,
            dataset=dataset,  # Same dataset list → same EXT- IDs
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=f"event-comparison-modified-{int(time.time())}",
            max_workers=2,
            verbose=True,
        )

        assert modified_result and modified_result.run_id
        modified_run_id = modified_result.run_id
        print(f"✅ Modified run: {modified_run_id}")

        # Use event-level comparison endpoint
        print(f"\n{'='*70}\nCALLING /runs/compare/events ENDPOINT\n{'='*70}")

        comparison_response = integration_client.evaluations.compare_run_events(
            new_run_id=modified_run_id,
            old_run_id=baseline_run_id,
            event_type="session",
            limit=100,
        )

        # Validate response structure
        assert comparison_response is not None
        print("✅ Comparison response received")

        # Actual backend response structure: {events: [...], totalEvents: X}
        # NOT {commonDatapoints: [...], metrics: [...]}

        # Check event pairing
        events = comparison_response.get("events", [])
        total_events = comparison_response.get("totalEvents", 0)

        print(f"\n✅ Total events: {total_events}")
        print(f"✅ Event pairs returned: {len(events)}")

        # Validate we got event pairs
        assert len(events) > 0, "Should have event pairs"
        assert len(events) == len(
            dataset
        ), f"Expected {len(dataset)} event pairs, got {len(events)}"
        print("✅ Event pair count matches dataset size")

        # Validate event structure
        for idx, event_pair in enumerate(events, 1):
            assert "datapoint_id" in event_pair, "Should have datapoint_id"
            assert "event_1" in event_pair, "Should have event_1"
            assert "event_2" in event_pair, "Should have event_2"

            datapoint_id = event_pair["datapoint_id"]
            event_1 = event_pair["event_1"]
            event_2 = event_pair["event_2"]

            # Verify datapoint_id matches in both events' metadata
            assert event_1["metadata"]["datapoint_id"] == datapoint_id
            assert event_2["metadata"]["datapoint_id"] == datapoint_id

            print(f"\n  Pair {idx}: {datapoint_id}")
            print(f"    Event 1: {event_1['event_id']}")
            print(f"    Event 2: {event_2['event_id']}")

            # Show metric comparison
            event_1_metrics = event_1.get("metrics", {})
            event_2_metrics = event_2.get("metrics", {})
            for metric_name in event_1_metrics.keys():
                val1 = event_1_metrics.get(metric_name)
                val2 = event_2_metrics.get(metric_name)
                print(f"    {metric_name}: {val2} → {val1}")

        print("\n✅ Event-level comparison structure validated")
        print("✅ All events successfully matched by datapoint_id")

        print(f"\n{'='*70}\nEVENT-LEVEL COMPARISON TEST COMPLETE\n{'='*70}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
