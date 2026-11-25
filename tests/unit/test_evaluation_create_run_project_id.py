"""Unit tests for ``create_evaluation_run``'s choice of operation and key.

With ``project_id`` it sends the project-scoped run create with the data plane
key. Without it, it sends the older run create with the project key and warns.
When the key a branch needs is not configured, nothing is sent and it returns
None, because the function reports every failure that way.

Every warning is checked for the file it is attributed to, because Python's
default filter hides a ``DeprecationWarning`` that is attributed to the SDK.
"""

# pylint: disable=protected-access

import logging
import os
import warnings
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from honeyhive.api import client as client_module
from honeyhive.api.client import HoneyHive
from honeyhive.evaluation.evaluators import create_evaluation_run

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32
PROJECT_ID = "p1"

MISSING_PROJECT_ID_WARNING = (
    "Calling evaluation.evaluators.create_evaluation_run() without project_id is "
    "deprecated and will stop working in v2.0. Pass project_id, and configure a "
    "data plane API key with data_plane_api_key or the HH_DATA_PLANE_API_KEY "
    "environment variable."
)


def _client(**keys: str) -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(**keys)


def _assert_sent(mock: MagicMock, key: str, kwargs: Dict[str, Any]) -> None:
    """The mock was called once, with a configuration carrying ``key``."""
    mock.assert_called_once()
    (api_config,), sent_kwargs = mock.call_args
    assert api_config.access_token == key
    assert set(sent_kwargs) == {"data", *kwargs}
    for name, value in kwargs.items():
        assert sent_kwargs[name] == value


def test_project_id_sends_the_scoped_create_with_the_data_plane_key() -> None:
    """With project_id the scoped function is called, and nothing warns."""
    client = _client(data_plane_api_key=DATA_PLANE_KEY)
    with (
        patch.object(client_module.experiments_svc, "createRun") as scoped,
        patch.object(client_module.experiments_svc, "createRunLegacy") as legacy,
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = create_evaluation_run(
                "run", "project", [], client=client, project_id=PROJECT_ID
            )

    assert result is scoped.return_value
    _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": PROJECT_ID})
    legacy.assert_not_called()


def test_no_project_id_sends_the_older_create_and_warns() -> None:
    """Without project_id the call is today's, on the project key, and warns."""
    client = _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)
    with (
        patch.object(client_module.experiments_svc, "createRunLegacy") as legacy,
        patch.object(client_module.experiments_svc, "createRun") as scoped,
    ):
        with pytest.warns(DeprecationWarning) as caught:
            result = create_evaluation_run("run", "project", [], client=client)

    assert result is legacy.return_value
    _assert_sent(legacy, PROJECT_KEY, {})
    scoped.assert_not_called()
    [warning] = caught
    assert str(warning.message) == MISSING_PROJECT_ID_WARNING
    assert warning.filename == __file__


def test_project_id_without_a_data_plane_key_sends_nothing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The project key never stands in for the data plane key."""
    client = _client(api_key=PROJECT_KEY)
    with (
        patch.object(client_module.experiments_svc, "createRun") as scoped,
        patch.object(client_module.experiments_svc, "createRunLegacy") as legacy,
    ):
        with caplog.at_level(logging.ERROR, logger="honeyhive.evaluation.evaluators"):
            result = create_evaluation_run(
                "run", "project", [], client=client, project_id=PROJECT_ID
            )

    assert result is None
    scoped.assert_not_called()
    legacy.assert_not_called()
    assert "HH_DATA_PLANE_API_KEY" in caplog.text


def test_own_client_uses_a_data_plane_key_from_the_environment() -> None:
    """Without a client, a data plane key alone is enough when given project_id."""
    with (
        patch.dict(os.environ, {"HH_DATA_PLANE_API_KEY": DATA_PLANE_KEY}, clear=True),
        patch.object(client_module.experiments_svc, "createRun") as scoped,
    ):
        result = create_evaluation_run("run", "project", [], project_id=PROJECT_ID)

    assert result is scoped.return_value
    _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": PROJECT_ID})


def test_own_client_with_no_keys_sends_nothing() -> None:
    """Without a client or any configured key, it returns None unsent."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch.object(client_module.experiments_svc, "createRunLegacy") as legacy,
        patch.object(client_module.experiments_svc, "createRun") as scoped,
    ):
        with pytest.warns(DeprecationWarning) as caught:
            result = create_evaluation_run("run", "project", [])

    assert result is None
    legacy.assert_not_called()
    scoped.assert_not_called()
    [warning] = caught
    assert warning.filename == __file__
