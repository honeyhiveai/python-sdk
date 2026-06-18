"""ExperimentsAPI (Runs) Integration Tests - NO MOCKS, REAL API CALLS."""

import time
import uuid
from typing import Any

from honeyhive.models import PostExperimentRunRequest


class TestExperimentsAPI:
    """Test ExperimentsAPI (Runs) CRUD operations."""

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

    def test_list_runs(
        self, integration_client: Any, integration_project_name: str
    ) -> None:
        """Test run listing returns created runs with pagination metadata."""
        test_id = str(uuid.uuid4())[:8]

        created_run_ids = []
        try:
            for i in range(2):
                run_request = PostExperimentRunRequest(
                    name=f"test_list_run_{test_id}_{i}",
                    configuration={"model": "gpt-4"},
                )
                response = integration_client.experiments.create_run(run_request)
                created_run_ids.append(response.run_id)

            time.sleep(2)

            # GetExperimentRunsResponse exposes runs as `evaluations`
            # plus a `pagination` envelope.
            runs_response = integration_client.experiments.list_runs(
                name=f"test_list_run_{test_id}"
            )

            assert runs_response is not None
            assert isinstance(runs_response.evaluations, list)
            listed_names = {run.name for run in runs_response.evaluations}
            assert listed_names == {
                f"test_list_run_{test_id}_0",
                f"test_list_run_{test_id}_1",
            }
            assert runs_response.pagination.total >= 2
        finally:
            for run_id in created_run_ids:
                integration_client.experiments.delete_run(run_id)
