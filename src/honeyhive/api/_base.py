"""Base classes for HoneyHive API client.

This module provides base functionality that can be extended for features like:
- Automatic retries with exponential backoff
- Request/response logging
- Rate limiting
- Custom error handling
"""

from typing import Any, Dict, Literal

from honeyhive._clock import _stamp_call
from honeyhive._generated.api_config import APIConfig

ApiKeyKind = Literal["project", "ingestion", "data_plane"]

_MISSING_API_KEY_MESSAGES: Dict[ApiKeyKind, str] = {
    "project": (
        "Missing project API key: provide api_key or set the HH_API_KEY "
        "environment variable"
    ),
    "ingestion": (
        "Missing ingestion API key: provide ingestion_api_key or set the "
        "HH_INGESTION_API_KEY environment variable"
    ),
    "data_plane": (
        "Missing data plane API key: provide data_plane_api_key or set the "
        "HH_DATA_PLANE_API_KEY environment variable"
    ),
}


class MissingApiKeyError(ValueError):
    """Raised by an operation when no key it can use is configured.

    It is raised before anything is sent. An ingestion operation uses the
    project API key when no ingestion key is configured, so it names the
    ingestion key only when neither is. An operation that takes the data plane
    key accepts no other key, so it names the data plane key whenever that key
    is absent.

    Attributes:
        key_kind: The kind of key the operation requires.
    """

    def __init__(self, key_kind: ApiKeyKind) -> None:
        super().__init__(_MISSING_API_KEY_MESSAGES[key_kind])
        self.key_kind = key_kind


class BaseAPI:
    """Base class for API resource namespaces.

    Provides shared configuration and extensibility hooks for all API resources.

    Public methods on subclasses are automatically wrapped so that the entry
    time of each SDK call is captured into a ContextVar that
    ``APIConfig.get_default_headers()`` reads from when emitting the
    ``hh-client-timestamp`` header. Stamping at call entry rather than at
    wire-send time keeps the header value stable across retries and any
    inner helper calls, so requests from the same client carry consistent
    timing metadata. The re-entrant guard inside ``_stamp_call`` ensures
    backwards-compat alias methods preserve the outer caller's timestamp.
    """

    def __init__(
        self,
        api_config: APIConfig,
        ingestion_api_key: str = "",
        data_plane_api_key: str = "",
    ) -> None:
        self._config = api_config
        # Each is empty when that key is not configured. Only the namespaces
        # with wrappers for a typed key's operations are given that key; the
        # rest never read it.
        self._ingestion_api_key = ingestion_api_key
        self._data_plane_api_key = data_plane_api_key

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Walk only the methods defined directly on this subclass (vars(cls)
        # excludes inherited members). Inherited methods are already wrapped
        # on the parent; overrides defined here get freshly wrapped.
        for name, attr in list(vars(cls).items()):
            # Skip private/dunder names: helper functions don't need stamping
            # and __init__/__init_subclass__ would break if wrapped.
            if name.startswith("_"):
                continue
            # callable(attr) excludes property and functools.cached_property
            # (neither is directly callable). It includes functools.lru_cache
            # wrappers, which would interact awkwardly with arg passthrough --
            # avoid @lru_cache on public BaseAPI subclass methods.
            if not callable(attr) or isinstance(attr, (staticmethod, classmethod)):
                continue
            # Wrapping is one-shot at class definition time; methods patched
            # onto the class after definition (e.g. test monkeypatching) will
            # not be auto-stamped.
            setattr(cls, name, _stamp_call(attr))

    @property
    def _api_config(self) -> APIConfig:
        """The configuration an operation that takes the project key is sent with.

        A wrapper reads it when it is called, so the check runs before the
        request is sent.

        Raises:
            MissingApiKeyError: No project API key is configured.
        """
        if not self._config.access_token:
            raise MissingApiKeyError("project")
        return self._config

    def _typed_api_config(self, key: str, key_kind: ApiKeyKind) -> APIConfig:
        """The configuration carrying a typed key.

        It is derived from the Data Plane configuration at call time, so a
        value a caller sets on ``api_config`` after construction (``verify``
        for a private CA, ``base_path``, ``timeout``) reaches these requests
        too.

        Raises:
            MissingApiKeyError: The typed key is not configured. It names the
                typed key.
        """
        if not key:
            raise MissingApiKeyError(key_kind)
        return self._config.model_copy(update={"access_token": key})

    @property
    def _ingestion_api_config(self) -> APIConfig:
        """The configuration an ingestion operation is sent with.

        A wrapper for an operation the ingestion endpoints serve (creating
        sessions, writing events) passes this; every other wrapper passes
        ``_api_config`` or ``_data_plane_api_config``. Which operations those
        are is declared by the published OpenAPI spec, and the live
        ingestion-key suite checks every wrapper against it. The ingestion
        endpoints accept the project API key in place of an ingestion key, so
        without an ingestion key this is the project configuration itself, the
        same object.

        Raises:
            MissingApiKeyError: Neither key is configured. It names the
                ingestion key.
        """
        if not self._ingestion_api_key and self._config.access_token:
            return self._config
        return self._typed_api_config(self._ingestion_api_key, "ingestion")

    @property
    def _data_plane_api_config(self) -> APIConfig:
        """The configuration an operation that takes the data plane key is sent with.

        A wrapper for an operation that names a project in its path passes
        this. The project API key never stands in for the data plane key,
        because those operations refuse it at the API.

        Raises:
            MissingApiKeyError: No data plane key is configured, whatever other
                key is.
        """
        return self._typed_api_config(self._data_plane_api_key, "data_plane")

    @property
    def api_config(self) -> APIConfig:
        """Access the API configuration."""
        return self._config
