"""Unit tests for the HTTP requests ``experiments.list_runs`` sends.

With ``project_id`` the call goes to ``/v1/projects/{project_id}/runs`` with the
data plane key; without it, to ``/v1/runs`` with the project key.
"""

import os
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from honeyhive import HoneyHive

PROJECT_KEY = "hh_" + "x" * 32
DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64


def _response() -> Mock:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "evaluations": [],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 0,
            "total_unfiltered": 0,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
        },
        "metrics": [],
    }
    return response


def _client() -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)


def _sent(mock_client: MagicMock) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = mock_client.request.call_args.kwargs
    return {
        "path": str(mock_client.request.call_args.args[1]),
        "authorization": kwargs["headers"]["Authorization"],
        "params": dict(kwargs["params"]),
    }


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize(
    ("project_id", "path", "key"),
    [
        (None, "/v1/runs", PROJECT_KEY),
        ("p1", "/v1/projects/p1/runs", DATA_PLANE_KEY),
    ],
)
@patch("honeyhive._generated.services.Experiments_service.httpx.Client")
def test_list_runs_sends_the_arm_for_project_id(
    mock_client_cls: MagicMock, project_id: Any, path: str, key: str
) -> None:
    mock_client = MagicMock()
    mock_client.request.return_value = _response()
    mock_client_cls.return_value.__enter__.return_value = mock_client

    result = _client().experiments.list_runs(name="run-a", project_id=project_id)

    sent = _sent(mock_client)
    assert sent["path"] == path
    assert sent["authorization"] == f"Bearer {key}"
    assert sent["params"]["name"] == "run-a"
    assert result.evaluations == []


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize(
    ("project_id", "path", "key"),
    [
        (None, "/v1/runs", PROJECT_KEY),
        ("p1", "/v1/projects/p1/runs", DATA_PLANE_KEY),
    ],
)
@patch("honeyhive._generated.services.async_Experiments_service.httpx.AsyncClient")
async def test_list_runs_async_sends_the_arm_for_project_id(
    mock_client_cls: MagicMock, project_id: Any, path: str, key: str
) -> None:
    mock_client = MagicMock()
    mock_client.request = AsyncMock(return_value=_response())
    mock_client_cls.return_value.__aenter__.return_value = mock_client

    result = await _client().experiments.list_runs_async(
        name="run-a", project_id=project_id
    )

    sent = _sent(mock_client)
    assert sent["path"] == path
    assert sent["authorization"] == f"Bearer {key}"
    assert sent["params"]["name"] == "run-a"
    assert result.evaluations == []
