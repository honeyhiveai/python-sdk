"""Integration test — ``ExperimentResultSummary`` typed-model contract.

Asserts that ``evaluate()`` returns the typed Pydantic models that
``honeyhive.experiments.models`` defines, against a real backend
response. Catches drift between the OpenAPI-generated models and the
``get_run_result`` response shape.
"""

# pylint: disable=R0801

import os
import time
from typing import Any, Dict

import pytest

from honeyhive.experiments import evaluate
from honeyhive.experiments.models import (
    AggregatedMetrics,
    DatapointResult,
    MetricDetail,
)


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsResultModels:
    """Typed-model shape contract from a real ``evaluate()`` run."""

    def test_experiment_result_models_match_real_api_response(
        self,
        real_api_key: str,
        real_project: str,
    ) -> None:
        """``ExperimentResultSummary`` deserializes correctly with real data."""

        def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            return {"result": inputs.get("value", 0) * 2}

        def accuracy_evaluator(
            outputs: Dict[str, Any],
            _inputs: Dict[str, Any],
            ground_truth: Dict[str, Any],
        ) -> float:
            return 1.0 if outputs["result"] == ground_truth["expected"] else 0.0

        dataset = [
            {"inputs": {"value": 5}, "ground_truth": {"expected": 10}},
            {"inputs": {"value": 10}, "ground_truth": {"expected": 20}},
        ]
        run_name = f"typed-models-{int(time.time())}"

        result = evaluate(
            function=simple_function,
            dataset=dataset,
            evaluators=[accuracy_evaluator],
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            aggregate_function="average",
            verbose=False,
        )
        assert result is not None and result.run_id
        assert isinstance(result.run_id, str)
        assert isinstance(result.status, str)
        assert isinstance(result.success, bool)

        # AggregatedMetrics shape — no `Any`, every detail is a MetricDetail.
        assert isinstance(
            result.metrics, AggregatedMetrics
        ), f"metrics should be AggregatedMetrics, got {type(result.metrics)}"
        # pylint: disable=no-member  # pydantic field access
        details = result.metrics.details
        if details:
            for detail in details:
                assert isinstance(
                    detail, MetricDetail
                ), f"detail should be MetricDetail, got {type(detail)}"
                assert isinstance(detail.metric_name, str)
                if detail.aggregate is not None:
                    assert isinstance(detail.aggregate, (float, int, bool))

        metric_names = result.metrics.list_metrics()
        assert isinstance(metric_names, list)
        for name in metric_names:
            assert isinstance(name, str)

        if metric_names:
            first_metric = result.metrics.get_metric(metric_names[0])
            assert first_metric is None or isinstance(first_metric, MetricDetail)

        # DatapointResult shape — explicit nullability per field.
        # pylint: disable=not-an-iterable
        for dp in result.datapoints or []:
            assert isinstance(
                dp, DatapointResult
            ), f"datapoint should be DatapointResult, got {type(dp)}"
            if dp.datapoint_id is not None:
                assert isinstance(dp.datapoint_id, str)
            if dp.session_id is not None:
                assert isinstance(dp.session_id, str)
            if dp.passed is not None:
                assert isinstance(dp.passed, bool)

        # print_table is documented as side-effect-free; assert it doesn't raise.
        result.print_table(run_name=run_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
