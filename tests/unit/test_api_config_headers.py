"""Unit tests for APIConfig.get_default_headers() and _get_sdk_version().

Verifies that:
- The hh-client-version, hh-client-language, and hh-client-package headers are present
- The header values are correct
- get_default_headers() includes all expected keys
- _get_sdk_version() returns a valid version string
"""

from honeyhive import __version__
from honeyhive._generated.api_config import APIConfig, _get_sdk_version


class TestGetDefaultHeaders:
    """Tests for APIConfig.get_default_headers()."""

    def test_includes_sdk_version_header(self) -> None:
        """get_default_headers() must include hh-client-version."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert "hh-client-version" in headers

    def test_sdk_version_matches_package_version(self) -> None:
        """hh-client-version value must equal honeyhive.__version__."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert headers["hh-client-version"] == __version__

    def test_includes_authorization_header(self) -> None:
        """get_default_headers() must include Authorization bearer token."""
        config = APIConfig(access_token="my-secret-key")
        headers = config.get_default_headers()
        assert headers["Authorization"] == "Bearer my-secret-key"

    def test_includes_content_type_and_accept(self) -> None:
        """get_default_headers() must include Content-Type and Accept."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_no_bearer_none_when_token_missing(self) -> None:
        """Authorization must not contain 'None' when access_token is unset."""
        config = APIConfig()
        headers = config.get_default_headers()
        assert "None" not in headers["Authorization"]

    def test_includes_sdk_language_header(self) -> None:
        """get_default_headers() must include hh-client-language set to 'python'."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert headers["hh-client-language"] == "python"

    def test_includes_sdk_package_header(self) -> None:
        """get_default_headers() must include hh-client-package set to 'honeyhive'."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert headers["hh-client-package"] == "honeyhive"


class TestGetSdkVersion:
    """Tests for the _get_sdk_version() helper."""

    def test_returns_version_string(self) -> None:
        """_get_sdk_version() must return the SDK version."""
        version = _get_sdk_version()
        assert version == __version__

    def test_version_is_non_empty_string(self) -> None:
        """_get_sdk_version() must return a non-empty string."""
        version = _get_sdk_version()
        assert isinstance(version, str)
        assert len(version) > 0
