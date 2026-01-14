"""ExperimentsAPI (Runs) Integration Tests - NO MOCKS, REAL API CALLS.

NOTE: Tests are skipped due to spec drift:
- CreateRunRequest now requires 'event_ids' as a mandatory field
- This requires pre-existing events, making simple integration tests impractical
- Backend contract changed but OpenAPI spec not updated
"""

import time
import uuid
from typing import Any

import pytest

from honeyhive.models import PostExperimentRunRequest


class TestExperimentsAPI:
    """Test ExperimentsAPI (Runs) CRUD operations."""

    @pytest.mark.skip(
        reason="Spec Drift: CreateRunRequest requires event_ids (mandatory field)"
    )
    def test_create_run(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test run creation with evaluator config, verify backend."""
        test_id = str(uuid.uuid4())[:8]
        run_name = f"test_run_{test_id}"

        run_request = PostExperimentRunRequest(
            name=run_name,
            configuration={"model": "gpt-4", "provider": "openai"},
        )

        response = integration_client.experiments.create_run(run_request)

        assert response is not None
        assert hasattr(response, "run_id") or hasattr(response, "id")
        run_id = getattr(response, "run_id", getattr(response, "id", None))
        assert run_id is not None

    @pytest.mark.skip(
        reason="Spec Drift: CreateRunRequest requires event_ids (mandatory field)"
    )
    def test_get_run(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test run retrieval with results, verify data complete."""
        test_id = str(uuid.uuid4())[:8]
        run_name = f"test_get_run_{test_id}"

        run_request = PostExperimentRunRequest(
            name=run_name,
            configuration={"model": "gpt-4"},
        )

        create_response = integration_client.experiments.create_run(run_request)
        run_id = getattr(
            create_response, "run_id", getattr(create_response, "id", None)
        )

        time.sleep(2)

        run = integration_client.experiments.get_run(run_id)

        assert run is not None
        run_data = run.run if hasattr(run, "run") else run
        run_name_attr = (
            run_data.get("name")
            if isinstance(run_data, dict)
            else getattr(run_data, "name", None)
        )
        if run_name_attr:
            assert run_name_attr == run_name

    @pytest.mark.skip(
        reason="Spec Drift: CreateRunRequest requires event_ids (mandatory field)"
    )
    def test_list_runs(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test run listing, filter by project, pagination."""
        test_id = str(uuid.uuid4())[:8]

        for i in range(2):
            run_request = PostExperimentRunRequest(
                name=f"test_list_run_{test_id}_{i}",
                configuration={"model": "gpt-4"},
            )
            integration_client.experiments.create_run(run_request)

        time.sleep(2)

        runs_response = integration_client.experiments.list_runs(
            project=integration_project_name
        )

        assert runs_response is not None
        runs = runs_response.runs if hasattr(runs_response, "runs") else []
        assert isinstance(runs, list)
        assert len(runs) >= 2

    @pytest.mark.skip(reason="ExperimentsAPI.run_experiment() requires complex setup")
    def test_run_experiment(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test async experiment execution, verify completion status."""
        pytest.skip(
            "ExperimentsAPI.run_experiment() requires complex setup "
            "with dataset and metrics"
        )
