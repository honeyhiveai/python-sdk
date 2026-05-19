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

    def __init__(self, api_config: APIConfig) -> None:
        self._api_config = api_config

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
    def api_config(self) -> APIConfig:
        """Access the API configuration."""
        return self._api_config
