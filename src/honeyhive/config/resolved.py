"""The resolved HoneyHive connection settings: the API keys and the API URL.

Three parts of the SDK send requests to HoneyHive on their own: the ``HoneyHive``
client, the tracer (its OTLP export), and the CLI. Each is an entry point that
takes the keys and the URL as arguments and otherwise reads them from the
environment, and each used to do that reading itself, with its own variable
names in its own order, so one process could authenticate with one key in
``evaluate()`` and another in a tracer, or send runs to one host and spans to
another, with no error anywhere. Now each entry point calls
``ResolvedConfig.resolve`` once with the arguments it received, and everything
beneath it is handed the result; nothing below an entry point reads these
variables or resolves them again. The configuration models get their connection
fields from the ``environment_*`` functions here when a caller constructs one
directly, and from the tracer's resolved values when the tracer builds them.

Each setting has one preferred variable, ``HH_<SETTING>``. The alternates in
``_SETTINGS`` stay supported because shipped code read them and the changelog
of the release that added them names them. They are kept out of the README and
the docs site, reading one emits a ``DeprecationWarning`` once per process, and
removing one is a breaking change.

The ingestion API key is typed: a present value that is not an ``hh_ingst_`` key
raises here, at resolution, whether or not the run goes on to send anything with
it. The project API key has no shape rule and is forwarded as given.

This type holds HoneyHive's canonical connection settings and nothing else. A
new field is a deliberate decision about a canonical setting, never a
convenience for a caller.
"""

import logging
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Optional, Set, Tuple

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "https://api.dp1.us.honeyhive.ai"

INGESTION_API_KEY_PREFIX = "hh_ingst_"

# Every HoneyHive API key begins with this, so a value that does not is not a
# HoneyHive key of any kind.
_HONEYHIVE_KEY_PREFIX = "hh_"

# An ingestion key is the prefix, a 24-character id, and a 64-character secret.
# Both lengths are fixed properties of the key format, so a value of any other
# shape is a truncated or corrupted key, never a newer variant.
_INGESTION_API_KEY_PATTERN = re.compile(r"^hh_ingst_[A-Za-z0-9]{24}_[A-Za-z0-9_-]{64}$")

# Setting name -> (preferred variable, alternates in precedence order).
_SETTINGS: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "api_key": ("HH_API_KEY", ("HONEYHIVE_API_KEY",)),
    "ingestion_api_key": ("HH_INGESTION_API_KEY", ()),
    "api_url": ("HH_API_URL", ("HONEYHIVE_SERVER_URL", "HH_SERVER_URL")),
}

_warned_alternates: Set[str] = set()


def _present(value: Any, source: str) -> Optional[str]:
    """Return the stripped string, or None for None and blank values.

    A non-string raises rather than degrading to None. A tracer or client
    holding a wrong-typed credential cannot work, because the server rejects
    every request; treating the value as absent would let the tracer appear to
    run while every event is lost, with nothing but a log line to say so. The
    only choice is how the fault is reported, and an exception at the call site
    is the report the caller can act on.

    Raises:
        TypeError: ``value`` is neither None nor a string.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{source} must be a string, got {type(value).__name__}.")
    stripped = value.strip()
    return stripped or None


def _warn_alternate(alternate: str, preferred: str) -> None:
    """Say once per process that a deprecated variable name is in use.

    The DeprecationWarning serves test suites and developers who run with
    warnings enabled. Python's default filter hides one attributed to library
    code, and no ``stacklevel`` can point at user code because the variable
    belongs to the process, not to a call site, so the log line is what a user
    sees in normal output.
    """
    if alternate in _warned_alternates:
        return
    _warned_alternates.add(alternate)
    message = f"{alternate} is deprecated; set {preferred} instead."
    warnings.warn(message, DeprecationWarning)
    logger.warning(message, extra={"honeyhive_data": {"variable": alternate}})


def _from_environment(setting: str) -> Tuple[Optional[str], str]:
    """Read a setting from the environment.

    Returns:
        The value and the variable it came from; ``(None, preferred)`` when no
        variable is set.
    """
    preferred, alternates = _SETTINGS[setting]
    value = _present(os.environ.get(preferred), preferred)
    if value is not None:
        return value, preferred
    for alternate in alternates:
        value = _present(os.environ.get(alternate), alternate)
        if value is not None:
            _warn_alternate(alternate, preferred)
            return value, alternate
    return None, preferred


def normalize_api_url(value: str, source: str) -> str:
    """Apply the one shape rule for the API URL.

    A value that is not an HTTP or HTTPS URL is malformed; the setting has a
    default, so the default is used with a warning rather than raising. A
    trailing slash is removed so request paths join without a double slash.

    Args:
        value: A non-blank URL candidate.
        source: The parameter or variable it came from, named in the warning.
    """
    if not value.startswith(("http://", "https://")):
        logger.warning(
            "Invalid %s: must be an HTTP or HTTPS URL. Using the default.",
            source,
            extra={"honeyhive_data": {"field": source}},
        )
        return DEFAULT_API_URL
    return value.rstrip("/")


def check_ingestion_api_key(value: str, source: str) -> str:
    """Return ``value`` if it is a well-formed ingestion API key.

    Args:
        value: The candidate key, already known to be a non-blank string.
        source: Where the value came from, named in the error, for example
            ``"HH_INGESTION_API_KEY"`` or ``"ingestion_api_key"``.

    Returns:
        The key with surrounding whitespace removed.

    Raises:
        ValueError: ``value`` is not an ingestion API key. The message says what
            the value looks like instead and never echoes the value itself.
    """
    candidate = value.strip()
    if _INGESTION_API_KEY_PATTERN.fullmatch(candidate):
        return candidate

    expectation = (
        f"{source} must be an ingestion API key, a value beginning with "
        f"{INGESTION_API_KEY_PREFIX!r}"
    )
    if candidate.startswith(INGESTION_API_KEY_PREFIX):
        raise ValueError(
            f"{expectation}; the value provided begins with it but is not a "
            "complete key."
        )
    if candidate.startswith(_HONEYHIVE_KEY_PREFIX):
        raise ValueError(
            f"{expectation}; the value provided looks like a different kind of "
            "HoneyHive API key."
        )
    raise ValueError(f"{expectation}; the value provided is not a HoneyHive API key.")


def environment_api_key() -> Optional[str]:
    """The project API key from the environment alone, or None when unset."""
    value, _ = _from_environment("api_key")
    return value


def environment_ingestion_api_key() -> Optional[str]:
    """The ingestion API key from the environment alone, checked; None when unset.

    Raises:
        ValueError: The variable is set to something other than an ingestion key.
    """
    value, source = _from_environment("ingestion_api_key")
    if value is None:
        return None
    return check_ingestion_api_key(value, source)


def environment_api_url() -> str:
    """The API URL from the environment alone, normalized; the default when unset."""
    value, source = _from_environment("api_url")
    if value is None:
        return DEFAULT_API_URL
    return normalize_api_url(value, source)


@dataclass(frozen=True)
class ResolvedConfig:
    """The API keys and API URL after precedence has been applied.

    ``api_key`` and ``ingestion_api_key`` are None when nothing supplied them;
    whether that is an error is the consumer's decision, since a tracer can run
    on an ingestion key alone while a Data Plane call cannot.
    """

    api_key: Optional[str]
    ingestion_api_key: Optional[str]
    api_url: str

    @classmethod
    def resolve(
        cls,
        *,
        api_key: Optional[str] = None,
        ingestion_api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> "ResolvedConfig":
        """Merge an entry point's explicit arguments with the environment.

        For each setting: the explicit argument if it is set, else the preferred
        variable, else the alternates in order. None and blank strings count as
        unset at every step. A present ingestion key is checked for shape,
        whichever step supplied it.

        Raises:
            TypeError: An explicit argument is neither None nor a string.
            ValueError: The ingestion key, explicit or from the environment, is
                not an ingestion API key. The message names its source.
        """
        resolved_key = _present(api_key, "api_key")
        if resolved_key is None:
            resolved_key = environment_api_key()

        # The shape check runs for every caller, including one that will never
        # send this key (the CLI, a client used only for Data Plane reads): a
        # typed credential that is present and malformed is a deployment error,
        # and surfacing it from every entry point beats a user learning of it
        # only when the tracer path runs somewhere else.
        explicit_ingestion_key = _present(ingestion_api_key, "ingestion_api_key")
        if explicit_ingestion_key is not None:
            resolved_ingestion_key: Optional[str] = check_ingestion_api_key(
                explicit_ingestion_key, "ingestion_api_key"
            )
        else:
            resolved_ingestion_key = environment_ingestion_api_key()

        explicit_url = _present(api_url, "api_url")
        if explicit_url is not None:
            resolved_url = normalize_api_url(explicit_url, "api_url")
        else:
            resolved_url = environment_api_url()

        return cls(
            api_key=resolved_key,
            ingestion_api_key=resolved_ingestion_key,
            api_url=resolved_url,
        )


class EnvSettingsSourceWithout(EnvSettingsSource):
    """The built-in environment source, minus the fields the resolver owns.

    Without this, pydantic-settings would read ``HH_API_KEY`` and, through the
    prefix, ``HH_SERVER_URL`` on its own, and the latter would beat
    ``HH_API_URL`` instead of ranking below it.
    """

    def __init__(
        self, settings_cls: type[BaseSettings], excluded: FrozenSet[str]
    ) -> None:
        super().__init__(settings_cls)
        self._excluded = excluded

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        if field_name in self._excluded:
            return None, field_name, False
        return super().get_field_value(field, field_name)


def settings_sources(
    settings_cls: type[BaseSettings],
    init_settings: PydanticBaseSettingsSource,
    dotenv_settings: PydanticBaseSettingsSource,
    file_secret_settings: PydanticBaseSettingsSource,
    *,
    excluded: FrozenSet[str],
) -> Tuple[PydanticBaseSettingsSource, ...]:
    """The source order for every HoneyHive configuration model."""
    return (
        init_settings,
        EnvSettingsSourceWithout(settings_cls, excluded),
        dotenv_settings,
        file_secret_settings,
    )
