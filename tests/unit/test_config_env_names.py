"""Environment variable names of the configuration models.

Every field that has an ``HH_`` variable reads ``HH_<FIELD NAME>``. ``api_key``
and ``server_url`` get theirs through ``honeyhive.config.resolved`` (which also
honours the older ``HH_API_URL`` spelling, with precedence over
``HH_SERVER_URL``); every other such field reads through pydantic-settings'
``env_prefix``. A bare field name is not read, so an unrelated ``VERBOSE`` or
``API_KEY`` in the host environment cannot reconfigure the SDK. Two kinds of
field are exceptions and are listed explicitly: the standard variables that
``HTTPClientConfig`` and ``ExperimentConfig`` read on purpose in their own
``__init__`` (``INTENTIONAL_BARE_READS``), and the fields that never had an
``HH_`` variable and keep reading their bare name as they always have
(``BARE_NAME_FIELDS``).
"""

import types
import uuid
from typing import Any, List, Optional, Tuple, Type, Union, get_args, get_origin

import pytest
from pydantic import ValidationError
from pydantic.fields import FieldInfo

from honeyhive.config import resolved
from honeyhive.config.models.api_client import APIClientConfig
from honeyhive.config.models.base import BaseHoneyHiveConfig
from honeyhive.config.models.experiment import ExperimentConfig
from honeyhive.config.models.http_client import HTTPClientConfig
from honeyhive.config.models.otlp import OTLPConfig
from honeyhive.config.models.tracer import EvaluationConfig, SessionConfig, TracerConfig

SETTINGS_MODELS: List[Type[BaseHoneyHiveConfig]] = [
    BaseHoneyHiveConfig,
    TracerConfig,
    SessionConfig,
    EvaluationConfig,
    OTLPConfig,
    HTTPClientConfig,
    ExperimentConfig,
    APIClientConfig,
]


# Fields whose bare name is a standard variable that the model's own __init__
# reads on purpose (HTTP_PROXY, VERIFY_SSL, EXPERIMENT_ID, ...).
INTENTIONAL_BARE_READS = {
    (HTTPClientConfig, "http_proxy"),
    (HTTPClientConfig, "https_proxy"),
    (HTTPClientConfig, "no_proxy"),
    (HTTPClientConfig, "verify_ssl"),
    (HTTPClientConfig, "follow_redirects"),
    (ExperimentConfig, "experiment_id"),
    (ExperimentConfig, "experiment_name"),
    (ExperimentConfig, "experiment_variant"),
    (ExperimentConfig, "experiment_group"),
}

# String fields whose validator accepts only a URL.
URL_FIELDS = {"server_url", "otlp_endpoint", "http_proxy", "https_proxy"}

# String fields whose validator accepts only a well-formed ingestion API key.
INGESTION_KEY_FIELDS = {"ingestion_api_key"}
INGESTION_KEY = "hh_ingst_" + "A" * 24 + "_" + "b" * 64

# Fields that never had an HH_ variable and keep reading their bare name
# (RUN_ID, not HH_RUN_ID). Each declares validation_alias equal to its own name
# so env_prefix does not apply. A new field belongs here only if it is meant to
# read a bare name; otherwise it reads HH_<FIELD NAME> with no declaration.
BARE_NAME_FIELDS = {
    (TracerConfig, "session_name"),
    (TracerConfig, "span_name_filters"),
    (TracerConfig, "requests_session"),
    (TracerConfig, "session_id"),
    (TracerConfig, "inputs"),
    (TracerConfig, "link_carrier"),
    (TracerConfig, "is_evaluation"),
    (TracerConfig, "run_id"),
    (TracerConfig, "dataset_id"),
    (TracerConfig, "datapoint_id"),
    (SessionConfig, "session_id"),
    (SessionConfig, "skip_backend_session_creation"),
    (SessionConfig, "inputs"),
    (SessionConfig, "link_carrier"),
    (EvaluationConfig, "is_evaluation"),
    (EvaluationConfig, "run_id"),
    (EvaluationConfig, "dataset_id"),
    (EvaluationConfig, "datapoint_id"),
    (APIClientConfig, "http_config"),
}


def _all_subclasses(cls: type) -> set:
    """Every transitive subclass of ``cls``."""
    found = set()
    for sub in cls.__subclasses__():
        found.add(sub)
        found |= _all_subclasses(sub)
    return found


def _scalar_type(field: FieldInfo) -> Optional[type]:
    """The field's type when it is str, int, float or bool, possibly Optional."""
    annotation = field.annotation
    if get_origin(annotation) in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) != 1:
            return None
        annotation = args[0]
    return annotation if annotation in (str, int, float, bool) else None


def _env_case(name: str, field: FieldInfo) -> Optional[Tuple[str, Any]]:
    """The environment string to set for ``name`` and the value it must land as."""
    scalar = _scalar_type(field)
    if scalar is bool:
        return ("false", False) if field.default is True else ("true", True)
    if scalar is int:
        return ("7", 7)
    if scalar is float:
        return ("2.5", 2.5)
    if scalar is str:
        if name in INGESTION_KEY_FIELDS:
            value = INGESTION_KEY
        elif name in URL_FIELDS:
            value = "https://env.example.test"
        else:
            value = str(uuid.uuid4())
        return (value, value)
    return None


SCALAR_FIELDS = [
    pytest.param(model, name, id=f"{model.__name__}.{name}")
    for model in SETTINGS_MODELS
    for name, field in model.model_fields.items()
    if _scalar_type(field) is not None
]


def _clear_hh_variables(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset every variable that could populate ``name``.

    The resolver's names are cleared whatever the field, so an ambient
    HONEYHIVE_SERVER_URL or a developer .env cannot outrank the variable a
    test sets.
    """
    monkeypatch.delenv(f"HH_{name.upper()}", raising=False)
    for preferred, alternates in resolved._SETTINGS.values():
        for variable in (preferred, *alternates):
            monkeypatch.delenv(variable, raising=False)


class TestEnvironmentVariableNames:
    """The HH_ prefix rule, pinned structurally and behaviourally."""

    def test_every_settings_model_is_listed(self) -> None:
        """A new settings model must be added to SETTINGS_MODELS to be checked.

        ``__subclasses__`` is process-wide and other tests define throwaway
        subclasses, so only classes from the package's own modules count.
        """
        production = {
            sub
            for sub in _all_subclasses(BaseHoneyHiveConfig)
            if sub.__module__.startswith("honeyhive.config.models.")
        }
        assert production == set(SETTINGS_MODELS[1:])

    @pytest.mark.parametrize("model", SETTINGS_MODELS)
    def test_env_prefix(self, model: Type[BaseHoneyHiveConfig]) -> None:
        """Every model inherits the prefix from the base class."""
        assert model.model_config["env_prefix"] == "HH_"

    @pytest.mark.parametrize("model", SETTINGS_MODELS)
    def test_fields_declare_no_alias(self, model: Type[BaseHoneyHiveConfig]) -> None:
        """No field declares an alias other than its own name.

        The variable a field reads comes from env_prefix, or from the resolver
        for api_key and server_url; a second spelling belongs in the resolver's
        table, never in an alias. A BARE_NAME_FIELDS entry declares its own
        name, which keeps the bare variable and adds no second spelling.
        """
        for name, field in model.model_fields.items():
            if (model, name) in BARE_NAME_FIELDS:
                assert field.validation_alias == name
                continue
            assert field.validation_alias is None, (
                f"{model.__name__}.{name} declares alias {field.validation_alias!r}; "
                "the environment variable is HH_<FIELD NAME>"
            )

    def test_bare_name_fields_are_exactly_those_declaring_their_own_name(
        self,
    ) -> None:
        """Declaring the own name as alias and being listed here go together."""
        declared = {
            (model, name)
            for model in SETTINGS_MODELS
            for name, field in model.model_fields.items()
            if field.validation_alias == name
        }
        assert declared == BARE_NAME_FIELDS

    @pytest.mark.parametrize(("model", "name"), SCALAR_FIELDS)
    def test_hh_prefixed_variable_lands_on_every_scalar_field(
        self,
        model: Type[BaseHoneyHiveConfig],
        name: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """HH_<FIELD NAME> sets the field, whichever layer reads the environment.

        The exceptions are the BARE_NAME_FIELDS, which read the bare name
        instead and stay at their default here.
        """
        case = _env_case(name, model.model_fields[name])
        assert case is not None
        raw, expected = case
        _clear_hh_variables(name, monkeypatch)
        monkeypatch.delenv(name.upper(), raising=False)
        monkeypatch.setenv(f"HH_{name.upper()}", raw)

        if (model, name) in BARE_NAME_FIELDS:
            expected = model.model_fields[name].get_default(call_default_factory=True)
        assert getattr(model(), name) == expected

    @pytest.mark.parametrize(("model", "name"), SCALAR_FIELDS)
    def test_bare_field_name_is_not_read_unless_intentional(
        self,
        model: Type[BaseHoneyHiveConfig],
        name: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A bare field name leaves the field at its default.

        The exceptions set their field: the standard variables listed in
        INTENTIONAL_BARE_READS, and the BARE_NAME_FIELDS, which have always
        read their bare name.
        """
        case = _env_case(name, model.model_fields[name])
        assert case is not None
        raw, landed = case
        _clear_hh_variables(name, monkeypatch)
        monkeypatch.setenv(name.upper(), raw)

        if (model, name) in INTENTIONAL_BARE_READS | BARE_NAME_FIELDS:
            expected = landed
        else:
            expected = model.model_fields[name].get_default(call_default_factory=True)
        assert getattr(model(), name) == expected

    def test_server_url_prefers_hh_api_url_over_hh_server_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_SERVER_URL is the prefix spelling; HH_API_URL is the documented one."""
        _clear_hh_variables("server_url", monkeypatch)
        monkeypatch.setenv("HH_SERVER_URL", "https://prefixed.example.test")
        assert TracerConfig().server_url == "https://prefixed.example.test"
        assert APIClientConfig().server_url == "https://prefixed.example.test"

        monkeypatch.setenv("HH_API_URL", "https://documented.example.test")
        assert TracerConfig().server_url == "https://documented.example.test"
        assert APIClientConfig().server_url == "https://documented.example.test"

    def test_otel_exporter_protocol_variable_is_read(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The OpenTelemetry variable stays honoured, and HH_OTLP_PROTOCOL wins."""
        monkeypatch.delenv("HH_OTLP_PROTOCOL", raising=False)
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
        assert OTLPConfig().otlp_protocol == "http/protobuf"

        monkeypatch.setenv("HH_OTLP_PROTOCOL", "http/json")
        assert OTLPConfig().otlp_protocol == "http/json"


class TestValidationErrorsOmitTheInput:
    """Fields hold credentials, so an error never echoes the value."""

    SECRET = "hh_value_that_must_not_appear"

    def test_unknown_field_name(self) -> None:
        """A mistyped field name does not print the value it carried."""
        with pytest.raises(ValidationError) as excinfo:
            TracerConfig(**{"apikey": self.SECRET})
        assert self.SECRET not in str(excinfo.value)

    def test_wrong_type(self) -> None:
        """A value of the wrong type is not printed either."""
        with pytest.raises(ValidationError) as excinfo:
            TracerConfig(**{"max_attributes": self.SECRET})
        assert self.SECRET not in str(excinfo.value)
