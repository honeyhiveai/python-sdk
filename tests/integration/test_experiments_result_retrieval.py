"""Integration test — result retrieval via evaluations API.

Validates that ``evaluate()`` produces a ``run_id`` that the
evaluations API ``get_run_result`` endpoint can read back. The richer
``ExperimentResultSummary`` shape (typed models, print_table, etc.)
lives in ``test_experiments_result_models.py``.
"""

# pylint: disable=R0801

import os
import time
from typing import Any, Dict

import pytest

from honeyhive import HoneyHive
from honeyhive.experiments import evaluate


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsResultRetrieval:
    """Result retrieval integration."""

    def test_evaluate_result_retrieval(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """``evaluate()`` returns a run_id that get_run_result can fetch."""

        def simple_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
            inputs = datapoint.get("inputs", {})
            return {"output": inputs.get("input", "")}

        dataset = [
            {"inputs": {"input": "test1"}},
            {"inputs": {"input": "test2"}},
        ]
        run_name = f"result-retrieval-{int(time.time())}"

        result = evaluate(
            function=simple_function,
            dataset=dataset,
            api_key=real_api_key,
            project=real_project,
            name=run_name,
            verbose=False,
        )
        assert result is not None and result.run_id

        # get_run_result is best-effort here — the assertion is that the
        # endpoint accepts the run_id without raising. Empty/null
        # aggregates are acceptable.
        metrics_response = integration_client.evaluations.get_run_result(
            run_id=result.run_id, aggregate_function="average"
        )
        assert metrics_response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--real-api"])
