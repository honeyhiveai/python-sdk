"""Unit tests for the HoneyHive client's data plane key.

Operations that name a project in their path take a fine-grained data plane
key; the client resolves it, checks it at construction, and a namespace with
wrappers for those operations sends it through ``_data_plane_api_config``. How
the key is resolved and checked is ``honeyhive.config.resolved``'s contract
and is tested there; this module covers only what the client adds on top.
"""

# pylint: disable=protected-access

import os
from unittest.mock import AsyncMock, patch

import pytest

from honeyhive import MissingApiKeyError
from honeyhive.api.client import ChartsAPI, HoneyHive, charts_svc, charts_svc_async
from honeyhive.models import ChartQueryRequest

DATA_PLANE_KEY = "hh_fgdp_" + "A" * 24 + "_" + "b" * 64
INGESTION_KEY = "hh_ingst_" + "C" * 24 + "_" + "d" * 64
PROJECT_KEY = "hh_" + "x" * 32


class TestClientResolution:
    """What the client holds after construction."""

    def test_keeps_the_resolved_key(self) -> None:
        """An explicit data plane key is resolved and exposed."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY, data_plane_api_key=DATA_PLANE_KEY)

        assert client.data_plane_api_key == DATA_PLANE_KEY
        assert client.api_key == PROJECT_KEY

    def test_reads_the_variable(self) -> None:
        """HH_DATA_PLANE_API_KEY supplies the key when no argument does."""
        with patch.dict(
            os.environ, {"HH_DATA_PLANE_API_KEY": DATA_PLANE_KEY}, clear=True
        ):
            client = HoneyHive(api_key=PROJECT_KEY)

        assert client.data_plane_api_key == DATA_PLANE_KEY

    def test_nothing_configured_is_empty(self) -> None:
        """Without a data plane key the property is empty, as ingestion_api_key is."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)

        assert client.data_plane_api_key == ""

    def test_constructs_with_a_data_plane_key_alone(self) -> None:
        """A process that holds only a data plane key can build a client.

        The data plane key never stands in for the project key, so an operation
        that takes the project key is refused, naming it.
        """
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(data_plane_api_key=DATA_PLANE_KEY)

        assert client.data_plane_api_key == DATA_PLANE_KEY
        with pytest.raises(MissingApiKeyError) as exc_info:
            _ = client.experiments._api_config
        assert exc_info.value.key_kind == "project"

    def test_a_malformed_key_raises_at_construction(self) -> None:
        """Another kind of key fails here, naming the parameter, without echoing it."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError,
                match="data_plane_api_key must be a fine-grained data plane API key",
            ) as exc_info:
                HoneyHive(api_key=PROJECT_KEY, data_plane_api_key=INGESTION_KEY)

        assert INGESTION_KEY not in str(exc_info.value)


class TestNamespaceConfiguration:
    """``_data_plane_api_config`` on a namespace handed the key."""

    def test_carries_the_data_plane_key(self) -> None:
        """A namespace given the key sends it; its other operations do not."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config, data_plane_api_key=DATA_PLANE_KEY)

        data_plane = charts._data_plane_api_config
        assert data_plane.access_token == DATA_PLANE_KEY
        assert data_plane.get_default_headers()["Authorization"] == (
            f"Bearer {DATA_PLANE_KEY}"
        )
        assert charts._api_config.access_token == PROJECT_KEY

    def test_the_project_key_never_stands_in(self) -> None:
        """With only the project key, the operation is refused, naming the data plane key."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config)

        with pytest.raises(MissingApiKeyError) as exc_info:
            _ = charts._data_plane_api_config
        assert exc_info.value.key_kind == "data_plane"

    def test_mutations_of_api_config_reach_it(self) -> None:
        """A value set on api_config after construction applies to it too."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config, data_plane_api_key=DATA_PLANE_KEY)

        client.server_url = "https://example.test"
        client.api_config.verify = "/etc/ssl/private-ca.pem"
        data_plane = charts._data_plane_api_config
        assert data_plane.base_path == "https://example.test"
        assert data_plane.verify == "/etc/ssl/private-ca.pem"
        assert data_plane.access_token == DATA_PLANE_KEY

    def test_neither_key_refuses_it_naming_the_data_plane_key(self) -> None:
        """With no key at all, the operation is refused before it is sent."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive()
        charts = ChartsAPI(client.api_config)

        with pytest.raises(
            MissingApiKeyError,
            match=(
                "Missing data plane API key: provide data_plane_api_key or set the "
                "HH_DATA_PLANE_API_KEY environment variable"
            ),
        ):
            _ = charts._data_plane_api_config


class TestChartQuery:
    """``charts.query`` sends the request with the data plane key only."""

    REQUEST = ChartQueryRequest.model_validate(
        {
            "date_range": {
                "start_time": "2026-01-01T00:00:00Z",
                "end_time": "2026-01-02T00:00:00Z",
            },
            "filters": [
                {
                    "field": "event_type",
                    "operator": "is",
                    "value": "model",
                    "type": "string",
                }
            ],
            "query": {"kind": "scalar", "measure": {"metric": "event_count"}},
        }
    )

    def test_sends_the_project_scoped_request(self) -> None:
        """The request names the project in its path and carries the data plane key."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config, data_plane_api_key=DATA_PLANE_KEY)

        with patch.object(charts_svc, "queryChart") as query_chart:
            result = charts.query(self.REQUEST, project_id="p1")

        assert result is query_chart.return_value
        (api_config,) = query_chart.call_args.args
        assert api_config.access_token == DATA_PLANE_KEY
        assert query_chart.call_args.kwargs == {
            "project_id": "p1",
            "data": self.REQUEST,
        }

    @pytest.mark.asyncio
    async def test_async_sends_the_project_scoped_request(self) -> None:
        """``query_async`` dispatches exactly as ``query`` does."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config, data_plane_api_key=DATA_PLANE_KEY)

        with patch.object(
            charts_svc_async, "queryChart", new_callable=AsyncMock
        ) as query_chart:
            result = await charts.query_async(self.REQUEST, project_id="p1")

        assert result is query_chart.return_value
        (api_config,) = query_chart.call_args.args
        assert api_config.access_token == DATA_PLANE_KEY
        assert query_chart.call_args.kwargs == {
            "project_id": "p1",
            "data": self.REQUEST,
        }

    def test_the_project_key_never_stands_in(self) -> None:
        """With only the project key, the query is refused before it is sent."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)
        charts = ChartsAPI(client.api_config)

        with patch.object(charts_svc, "queryChart") as query_chart:
            with pytest.raises(MissingApiKeyError):
                charts.query(self.REQUEST, project_id="p1")
        query_chart.assert_not_called()
