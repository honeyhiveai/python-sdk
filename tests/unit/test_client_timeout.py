"""Unit tests for HoneyHive client request-timeout configuration.

Verifies that the ``timeout`` constructor arg and the HH_API_TIMEOUT env var are
threaded into the underlying APIConfig, while preserving the 5.0s default when
nothing is configured.
"""

from unittest.mock import patch

from honeyhive.api.client import HoneyHive, _resolve_api_timeout


class TestClientTimeoutThreading:
    """HoneyHive() threads the timeout into APIConfig."""

    def test_default_timeout_preserved(self) -> None:
        """With no timeout configured, APIConfig keeps its 5.0s default."""
        with patch.dict("os.environ", {}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.api_config.timeout == 5.0

    def test_explicit_timeout_is_used(self) -> None:
        """An explicit timeout arg is threaded into APIConfig."""
        with patch.dict("os.environ", {}, clear=True):
            client = HoneyHive(api_key="k", timeout=20.0)
        assert client.api_config.timeout == 20.0

    def test_explicit_none_keeps_default(self) -> None:
        """timeout=None means "unset" at the client layer, keeping the default.

        This is a deliberate asymmetry: HoneyHive(timeout=None) preserves the
        5.0s default, whereas APIConfig(timeout=None) disables timeouts.
        """
        with patch.dict("os.environ", {}, clear=True):
            client = HoneyHive(api_key="k", timeout=None)
        assert client.api_config.timeout == 5.0


class TestClientTimeoutEnvVar:
    """HH_API_TIMEOUT resolution at the client layer."""

    def test_env_var_is_used(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "45"}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.api_config.timeout == 45.0

    def test_explicit_arg_beats_env_var(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "45"}, clear=True):
            client = HoneyHive(api_key="k", timeout=10.0)
        assert client.api_config.timeout == 10.0

    def test_invalid_env_var_falls_back_to_default(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "nope"}, clear=True):
            client = HoneyHive(api_key="k")
        assert client.api_config.timeout == 5.0

    def test_non_positive_arg_falls_back_to_default(self) -> None:
        """timeout=0 / negative would break httpx; fall back to the default."""
        with patch.dict("os.environ", {}, clear=True):
            assert HoneyHive(api_key="k", timeout=0).api_config.timeout == 5.0
            assert HoneyHive(api_key="k", timeout=-5).api_config.timeout == 5.0

    def test_non_positive_env_var_falls_back_to_default(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "0"}, clear=True):
            assert HoneyHive(api_key="k").api_config.timeout == 5.0


class TestResolveApiTimeout:
    """Direct coverage of the _resolve_api_timeout helper."""

    def test_explicit_wins(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "45"}, clear=True):
            assert _resolve_api_timeout(3.0) == 3.0

    def test_env_used_when_no_explicit(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "45"}, clear=True):
            assert _resolve_api_timeout(None) == 45.0

    def test_returns_none_when_unset(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert _resolve_api_timeout(None) is None

    def test_invalid_env_warns_and_returns_none(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "bad"}, clear=True):
            with patch("honeyhive.api.client.logger") as mock_logger:
                assert _resolve_api_timeout(None) is None
                mock_logger.warning.assert_called_once()

    def test_non_positive_explicit_warns_and_returns_none(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with patch("honeyhive.api.client.logger") as mock_logger:
                assert _resolve_api_timeout(0) is None
                assert _resolve_api_timeout(-1.0) is None
                assert mock_logger.warning.call_count == 2

    def test_non_positive_env_warns_and_returns_none(self) -> None:
        with patch.dict("os.environ", {"HH_API_TIMEOUT": "-3"}, clear=True):
            with patch("honeyhive.api.client.logger") as mock_logger:
                assert _resolve_api_timeout(None) is None
                mock_logger.warning.assert_called_once()
