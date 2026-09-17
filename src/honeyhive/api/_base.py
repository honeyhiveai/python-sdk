"""Base classes for HoneyHive API client.

This module provides base functionality that can be extended for features like:
- Automatic retries with exponential backoff
- Request/response logging
- Rate limiting
- Custom error handling
"""

from typing import Any

from honeyhive._clock import _stamp_call
from honeyhive._generated.api_config import APIConfig


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

    def __init__(self, api_config: APIConfig, ingestion_api_key: str = "") -> None:
        self._api_config = api_config
        # Empty when the project API key serves ingestion requests too. Only
        # the namespaces with ingestion wrappers are given a key; the rest
        # never read it.
        self._ingestion_api_key = ingestion_api_key

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
    def _ingestion_api_config(self) -> APIConfig:
        """The configuration an ingestion operation is sent with.

        A wrapper for an operation the ingestion endpoints serve (creating
        sessions, writing events) passes this; every other wrapper passes
        ``_api_config`` and is unaffected by the ingestion key. Which
        operations those are is declared by the published OpenAPI spec, and
        the live ingestion-key suite checks every wrapper against it.

        It is derived from the Data Plane configuration at call time, so a
        value a caller sets on ``api_config`` after construction (``verify``
        for a private CA, ``base_path``, ``timeout``) reaches ingestion
        requests too. Without an ingestion key it is the Data Plane
        configuration itself, the same object, so the project API key serves
        ingestion requests as before.
        """
        if not self._ingestion_api_key:
            return self._api_config
        return self._api_config.model_copy(
            update={"access_token": self._ingestion_api_key}
        )

    @property
    def api_config(self) -> APIConfig:
        """Access the API configuration."""
        return self._api_config
