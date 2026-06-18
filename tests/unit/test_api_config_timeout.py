"""Unit tests for the configurable APIConfig request timeout.

Verifies the new ``timeout`` field on APIConfig (defaulting to 5.0s, matching
httpx's own default). Env var / precedence resolution lives in the public client
(see test_client_timeout.py), not in APIConfig itself.
"""

from honeyhive._generated.api_config import APIConfig


class TestAPIConfigTimeoutField:
    """Test the APIConfig.timeout field defaults and overrides."""

    def test_default_timeout_is_five_seconds(self) -> None:
        """Default timeout should be 5.0 to match httpx's default."""
        assert APIConfig().timeout == 5.0

    def test_explicit_timeout_overrides_default(self) -> None:
        """An explicit timeout should be stored verbatim."""
        assert APIConfig(timeout=12.0).timeout == 12.0

    def test_explicit_none_disables_timeout(self) -> None:
        """Passing None explicitly disables timeouts (httpx semantics)."""
        assert APIConfig(timeout=None).timeout is None
