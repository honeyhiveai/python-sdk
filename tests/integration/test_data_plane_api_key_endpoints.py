"""The data plane API key against every data plane operation the SDK exposes, live.

Each entry of ``OPERATIONS`` (see ``_data_plane_operations``) performs one
wrapped data plane operation through the public wrapper on a client holding
only a data plane key, and checks its effect with a client holding only the
project key. That the dictionary covers exactly the wrapped data plane
operations is asserted by
``tests/unit/test_data_plane_operations_match_the_spec.py``, which runs where
the spec is reachable; this module runs the entries where the server is.

The data plane key comes from ``HH_DATA_PLANE_API_KEY`` and the id of the
project it acts on from ``HH_PROJECT_ID``. Without either, the tests here skip.
"""

import pytest

from honeyhive.api.client import HoneyHive
from tests.integration._data_plane_operations import OPERATIONS
from tests.integration._spec_operations import data_plane_url

pytestmark = [pytest.mark.integration, pytest.mark.real_api, pytest.mark.slow]


@pytest.mark.parametrize("operation", sorted(OPERATIONS))
def test_operation_accepts_the_data_plane_key_alone(
    operation: str,
    real_api_key: str,
    real_data_plane_api_key: str,
    real_project_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The wrapper reaches the server on a data plane key with no project key in reach."""
    # Each client holds one key, so the data plane client's request can only
    # have travelled on the data plane key, and every check of its effect only
    # on the project key.
    with monkeypatch.context() as env:
        env.delenv("HH_API_KEY", raising=False)
        env.delenv("HONEYHIVE_API_KEY", raising=False)
        env.delenv("HH_DATA_PLANE_API_KEY", raising=False)
        data_plane = HoneyHive(
            data_plane_api_key=real_data_plane_api_key, base_url=data_plane_url()
        )
        project_client = HoneyHive(api_key=real_api_key, base_url=data_plane_url())
        assert data_plane.api_key == ""
        assert project_client.data_plane_api_key == ""

        OPERATIONS[operation](data_plane, project_client, real_project_id)
