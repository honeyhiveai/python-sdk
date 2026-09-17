"""Unit tests for the HoneyHive client's two credentials.

Requests that create sessions or write events carry the ingestion key when one
is configured; every other request carries the project key. A project key alone
serves everything, as it did before the ingestion key existed. How the keys are
resolved and checked is ``honeyhive.config.resolved``'s contract and is tested
there; this module covers only what the client adds on top.
"""

# pylint: disable=protected-access

import os
from unittest.mock import patch

from honeyhive.api.client import HoneyHive

INGESTION_KEY = "hh_ingst_" + "A" * 24 + "_" + "b" * 64
PROJECT_KEY = "hh_" + "x" * 32


class TestCredentialRouting:
    """Which key each kind of operation is sent with."""

    def test_both_keys_split_by_operation(self) -> None:
        """Ingestion wrappers carry the ingestion key; the rest the project key."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY, ingestion_api_key=INGESTION_KEY)

        ingestion = client.sessions._ingestion_api_config
        plane = client.experiments._api_config
        assert ingestion.access_token == INGESTION_KEY
        assert plane.access_token == PROJECT_KEY
        assert ingestion.get_default_headers()["Authorization"] == (
            f"Bearer {INGESTION_KEY}"
        )
        assert plane.get_default_headers()["Authorization"] == f"Bearer {PROJECT_KEY}"
        assert client.api_key == PROJECT_KEY
        assert client.ingestion_api_key == INGESTION_KEY

    def test_project_key_alone_serves_everything(self) -> None:
        """Without an ingestion key nothing changes, down to object identity."""
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY)

        assert client.sessions._ingestion_api_config.access_token == PROJECT_KEY
        assert client.experiments._api_config.access_token == PROJECT_KEY
        assert client.ingestion_api_key == ""
        # The same configuration object, not an equal copy: mutating
        # `client.api_config` must keep reaching every request, as before.
        assert client.sessions._ingestion_api_config is client.api_config

    def test_ingestion_key_alone_serves_ingestion_only(self) -> None:
        """An ingestion-only client carries the key on ingestion requests and nothing else.

        Every other namespace is exactly a client with no key: the ingestion
        key changes nothing about how they behave.
        """
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(ingestion_api_key=INGESTION_KEY)

        assert client.sessions._ingestion_api_config.access_token == INGESTION_KEY
        assert client.events._ingestion_api_config.access_token == INGESTION_KEY
        assert client.experiments._api_config.access_token == ""
        assert client.experiments._ingestion_api_key == ""

    def test_mutations_of_api_config_reach_ingestion_requests(self) -> None:
        """A value set on api_config after construction applies to both credentials.

        verify is the case that matters: the constructor takes no such
        parameter, so a private CA can only be configured this way.
        """
        with patch.dict(os.environ, {}, clear=True):
            client = HoneyHive(api_key=PROJECT_KEY, ingestion_api_key=INGESTION_KEY)

        client.server_url = "https://example.test"
        client.api_config.verify = "/etc/ssl/private-ca.pem"
        ingestion = client.sessions._ingestion_api_config
        assert ingestion.base_path == "https://example.test"
        assert ingestion.verify == "/etc/ssl/private-ca.pem"
        assert ingestion.access_token == INGESTION_KEY
        assert client.experiments._api_config.base_path == "https://example.test"
        assert client.experiments._api_config.verify == "/etc/ssl/private-ca.pem"
