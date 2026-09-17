"""The ``HoneyHive`` constructor: deprecated parameters warn, live ones apply.

The constructor is one of the three entry points that resolve the API key and
URL, so the cases that reach the resolver are pinned here as well: nothing
given, the environment, and the two URL spellings together.
"""

import warnings

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.config import resolved
from honeyhive.utils.retry import RetryConfig

DEPRECATED = [
    ("project", "my-project"),
    ("cp_base_url", "https://cp.example.test"),
    ("rate_limit_calls", 10),
    ("rate_limit_window", 1.5),
    ("max_connections", 4),
    ("max_keepalive", 2),
    ("tracer_instance", object()),
]


class TestDeprecatedParameters:
    """Deprecated parameters are accepted, named in a warning, and ignored."""

    @pytest.mark.parametrize(("name", "value"), DEPRECATED)
    def test_each_deprecated_parameter_warns_by_name(
        self, name: str, value: object
    ) -> None:
        """The warning names the parameter so the caller knows what to remove."""
        with pytest.warns(DeprecationWarning, match=name):
            client = HoneyHive(api_key="test-key", **{name: value})
        assert client.api_key == "test-key"

    def test_legacy_positional_project_still_constructs(self) -> None:
        """The reserved second positional slot still binds to project."""
        with pytest.warns(DeprecationWarning, match="project"):
            client = HoneyHive("test-key", "my-project")
        assert client.api_key == "test-key"

    def test_live_parameters_do_not_warn(self) -> None:
        """Passing only parameters still in use emits no warning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            HoneyHive(
                api_key="test-key",
                base_url="https://api.example.test",
                timeout=2.5,
                retry_config=RetryConfig(max_retries=1),
                test_mode=True,
                verbose=True,
            )


class TestLiveParameters:
    """Parameters still in use reach the client through the internal initializer."""

    def test_values_reach_the_client(self) -> None:
        """Each live parameter is observable on the constructed client."""
        client = HoneyHive(
            api_key="test-key",
            base_url="https://api.example.test",
            timeout=2.5,
            retry_config=RetryConfig(max_retries=1),
            test_mode=True,
            verbose=True,
        )
        assert client.api_key == "test-key"
        assert client.server_url == "https://api.example.test"
        assert client.timeout == 2.5
        assert client.retry_config.max_retries == 1
        assert client.test_mode is True
        assert client.verbose is True
        assert client.api_config.access_token == "test-key"

    def test_server_url_is_the_legacy_spelling_of_base_url(self) -> None:
        """server_url still sets the base URL when base_url is not given."""
        client = HoneyHive(api_key="test-key", server_url="https://legacy.example.test")
        assert client.server_url == "https://legacy.example.test"

    def test_base_url_wins_over_server_url(self) -> None:
        """When both spellings are given, base_url is the one used."""
        client = HoneyHive(
            api_key="test-key",
            base_url="https://base.example.test",
            server_url="https://legacy.example.test",
        )
        assert client.server_url == "https://base.example.test"


class TestEnvironmentResolution:
    """Without explicit arguments the constructor resolves from the environment."""

    @pytest.fixture(autouse=True)
    def clean_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Start with none of the resolver's variables set."""
        for preferred, alternates in resolved._SETTINGS.values():
            for variable in (preferred, *alternates):
                monkeypatch.delenv(variable, raising=False)

    def test_key_and_url_come_from_the_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_API_KEY and HH_API_URL reach the client and its request config."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        monkeypatch.setenv("HH_API_URL", "https://env.example.test/")
        client = HoneyHive()
        assert client.api_key == "hh_from_env"
        assert client.api_config.access_token == "hh_from_env"
        assert client.server_url == "https://env.example.test"

    def test_absent_key_is_the_empty_string(self) -> None:
        """Nothing set anywhere gives an empty key, which callers test for."""
        client = HoneyHive()
        assert client.api_key == ""
        assert client.api_config.access_token == ""
