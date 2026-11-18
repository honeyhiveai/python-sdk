"""Unit tests for the configurations list methods' choice of operation and key.

``configurations.list``, its async form and its aliases take ``project_id``.
With it they send the project-scoped list with the data plane key. Without it
they send the older list with the project key and warn. Each branch is refused
before sending, naming its key, when that key is not configured.

These are the checks ``tests/unit/test_api_client_twins.py`` runs for each
row of its table. The list methods are not a row there, because they take a
deprecated positional ``project`` and return the list their response wraps,
and the table models neither.

Every warning is checked for the file it is attributed to, because Python's
default filter hides a ``DeprecationWarning`` that is attributed to the SDK.
"""

# pylint: disable=protected-access

import os
import warnings
from typing import Any, Dict, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from honeyhive import MissingApiKeyError
from honeyhive.api import client as client_module
from honeyhive.api.client import HoneyHive

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32

# Each sync method that lists configurations, with the arguments it needs.
SYNC_LISTS = [
    pytest.param("list", (), id="list"),
    pytest.param("list_configurations", (), id="list_configurations"),
    pytest.param("get_configuration", ("c1",), id="get_configuration"),
]

# The sync methods that take the deprecated ``project`` argument.
SYNC_LISTS_WITH_PROJECT = ["list", "list_configurations"]


def missing_project_id_warning(method: str) -> str:
    """The warning ``configurations.<method>()`` gives without project_id."""
    return (
        f"Calling configurations.{method}() without project_id is deprecated and "
        "will stop working in v2.0. Pass project_id, and configure a data plane "
        "API key with data_plane_api_key or the HH_DATA_PLANE_API_KEY "
        "environment variable."
    )


PROJECT_ARGUMENT_WARNING = (
    "The 'project' parameter is ignored. It is deprecated and will be removed "
    "in v2.0. Name the project with project_id, which takes the project's ID."
)


def _client(**keys: str) -> HoneyHive:
    with patch.dict(os.environ, {}, clear=True):
        return HoneyHive(**keys)


def _both_keys() -> HoneyHive:
    return _client(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)


def _assert_sent(mock: MagicMock, key: str, kwargs: Dict[str, Any]) -> None:
    """The mock was called once, with a configuration carrying ``key``."""
    mock.assert_called_once()
    (api_config,), sent_kwargs = mock.call_args
    assert api_config.access_token == key
    assert sent_kwargs == kwargs


class TestSync:
    """``list`` and its aliases."""

    @pytest.mark.parametrize("method, args", SYNC_LISTS)
    def test_project_id_sends_the_scoped_list_with_the_data_plane_key(
        self, method: str, args: Tuple[Any, ...]
    ) -> None:
        """With project_id the scoped function is called, and nothing warns."""
        client = _both_keys()
        with patch.object(client_module.configs_svc, "getConfigurations") as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = getattr(client.configurations, method)(*args, project_id="p1")

        assert result is scoped.return_value.configurations
        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1"})

    @pytest.mark.parametrize("method, args", SYNC_LISTS)
    def test_no_project_id_sends_the_older_list_and_warns_in_its_own_name(
        self, method: str, args: Tuple[Any, ...]
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc, "getConfigurationsLegacy"
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = getattr(client.configurations, method)(*args)

        assert result is legacy.return_value.configurations
        _assert_sent(legacy, PROJECT_KEY, {})
        [warning] = caught
        assert str(warning.message) == missing_project_id_warning(method)
        assert warning.filename == __file__

    @pytest.mark.parametrize("method, args", SYNC_LISTS)
    def test_project_id_without_a_data_plane_key_sends_nothing(
        self, method: str, args: Tuple[Any, ...]
    ) -> None:
        """The project key never stands in for the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(client_module.configs_svc, "getConfigurations") as scoped:
            with pytest.raises(MissingApiKeyError) as exc_info:
                getattr(client.configurations, method)(*args, project_id="p1")

        assert exc_info.value.key_kind == "data_plane"
        scoped.assert_not_called()

    @pytest.mark.parametrize("method, args", SYNC_LISTS)
    def test_no_project_id_without_a_project_key_sends_nothing(
        self, method: str, args: Tuple[Any, ...]
    ) -> None:
        """The data plane key never stands in for the project key."""
        client = _client(data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.configs_svc, "getConfigurationsLegacy"
        ) as legacy:
            with pytest.raises(MissingApiKeyError) as exc_info:
                getattr(client.configurations, method)(*args)

        assert exc_info.value.key_kind == "project"
        legacy.assert_not_called()

    @pytest.mark.parametrize(
        "method, args",
        [
            ("list", (None, "p1")),
            ("list_configurations", (None, "p1")),
            ("get_configuration", ("c1", "p1")),
        ],
    )
    def test_project_id_is_keyword_only(
        self, method: str, args: Tuple[Any, ...]
    ) -> None:
        """A positional argument after the method's own is not project_id."""
        client = _both_keys()

        with pytest.raises(TypeError):
            getattr(client.configurations, method)(*args)

    @pytest.mark.parametrize("method", SYNC_LISTS_WITH_PROJECT)
    def test_project_argument_warns_and_is_not_sent(self, method: str) -> None:
        """``project`` beside project_id gives one warning, to the caller."""
        client = _both_keys()
        with patch.object(client_module.configs_svc, "getConfigurations") as scoped:
            with pytest.warns(DeprecationWarning) as caught:
                getattr(client.configurations, method)("my-project", project_id="p1")

        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1"})
        [warning] = caught
        assert str(warning.message) == PROJECT_ARGUMENT_WARNING
        assert warning.filename == __file__

    def test_core_sends_the_older_list_without_warning(self) -> None:
        """The core takes the older branch silently, for SDK code with no project_id."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc, "getConfigurationsLegacy"
        ) as legacy:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = client.configurations._list()

        assert result is legacy.return_value.configurations
        _assert_sent(legacy, PROJECT_KEY, {})


class TestAsync:
    """``list_async``, which dispatches exactly as ``list`` does."""

    @pytest.mark.asyncio
    async def test_project_id_sends_the_scoped_list_with_the_data_plane_key(
        self,
    ) -> None:
        """With project_id the scoped function is awaited, and nothing warns."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc_async, "getConfigurations", new_callable=AsyncMock
        ) as scoped:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await client.configurations.list_async(project_id="p1")

        assert result is scoped.return_value.configurations
        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1"})

    @pytest.mark.asyncio
    async def test_no_project_id_sends_the_older_list_and_warns_in_its_own_name(
        self,
    ) -> None:
        """Without project_id the call is today's, on the project key, and warns."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc_async,
            "getConfigurationsLegacy",
            new_callable=AsyncMock,
        ) as legacy:
            with pytest.warns(DeprecationWarning) as caught:
                result = await client.configurations.list_async()

        assert result is legacy.return_value.configurations
        _assert_sent(legacy, PROJECT_KEY, {})
        [warning] = caught
        assert str(warning.message) == missing_project_id_warning("list_async")
        assert warning.filename == __file__

    @pytest.mark.asyncio
    async def test_project_id_without_a_data_plane_key_sends_nothing(self) -> None:
        """The project key never stands in for the data plane key."""
        client = _client(api_key=PROJECT_KEY)
        with patch.object(
            client_module.configs_svc_async, "getConfigurations", new_callable=AsyncMock
        ) as scoped:
            with pytest.raises(MissingApiKeyError) as exc_info:
                await client.configurations.list_async(project_id="p1")

        assert exc_info.value.key_kind == "data_plane"
        scoped.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_project_id_without_a_project_key_sends_nothing(self) -> None:
        """The data plane key never stands in for the project key."""
        client = _client(data_plane_api_key=DATA_PLANE_KEY)
        with patch.object(
            client_module.configs_svc_async,
            "getConfigurationsLegacy",
            new_callable=AsyncMock,
        ) as legacy:
            with pytest.raises(MissingApiKeyError) as exc_info:
                await client.configurations.list_async()

        assert exc_info.value.key_kind == "project"
        legacy.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_id_is_keyword_only(self) -> None:
        """A positional argument after ``project`` is not project_id."""
        client = _both_keys()

        with pytest.raises(TypeError):
            await getattr(client.configurations, "list_async")(None, "p1")

    @pytest.mark.asyncio
    async def test_project_argument_warns_and_is_not_sent(
        self,
    ) -> None:
        """``project`` beside project_id gives one warning, to the caller."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc_async, "getConfigurations", new_callable=AsyncMock
        ) as scoped:
            with pytest.warns(DeprecationWarning) as caught:
                await client.configurations.list_async("my-project", project_id="p1")

        _assert_sent(scoped, DATA_PLANE_KEY, {"project_id": "p1"})
        [warning] = caught
        assert str(warning.message) == PROJECT_ARGUMENT_WARNING
        assert warning.filename == __file__

    @pytest.mark.asyncio
    async def test_core_sends_the_older_list_without_warning(self) -> None:
        """The async core takes the older branch silently."""
        client = _both_keys()
        with patch.object(
            client_module.configs_svc_async,
            "getConfigurationsLegacy",
            new_callable=AsyncMock,
        ) as legacy:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                result = await client.configurations._list_async()

        assert result is legacy.return_value.configurations
        _assert_sent(legacy, PROJECT_KEY, {})
