"""``ResolvedConfig``: one resolution of the project API key and the API URL.

The three entry points that send requests (the client, the tracer, the CLI)
resolve once from their own arguments and hand the result down, and a
configuration model built directly by a caller asks the resolver for the two
connection fields it was not given. So the precedence pinned here is the
precedence everywhere: explicit argument, then the preferred ``HH_`` variable,
then the undocumented alternates in order, with blanks treated as absent.
"""

import logging
import warnings
from typing import Iterator

import pytest
from pydantic import ValidationError

from honeyhive.config import resolved
from honeyhive.config.models.api_client import APIClientConfig
from honeyhive.config.models.tracer import EvaluationConfig, SessionConfig, TracerConfig
from honeyhive.config.resolved import (
    DEFAULT_API_URL,
    ResolvedConfig,
    check_ingestion_api_key,
)
from honeyhive.config.utils import create_unified_config

ALL_VARIABLES = (
    "HH_API_KEY",
    "HONEYHIVE_API_KEY",
    "HH_INGESTION_API_KEY",
    "HH_API_URL",
    "HH_SERVER_URL",
    "HONEYHIVE_SERVER_URL",
)

INGESTION_KEY = "hh_ingst_" + "A" * 24 + "_" + "b" * 64
OTHER_INGESTION_KEY = "hh_ingst_" + "B" * 24 + "_" + "c" * 64
PROJECT_KEY = "hh_" + "x" * 32
SECTIONS = ("session", "evaluation", "http", "otlp", "api", "experiment")


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Start every test with none of the variables set and no alternate yet warned."""
    for name in ALL_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    resolved._warned_alternates.clear()
    yield
    resolved._warned_alternates.clear()


class TestApiKeyPrecedence:
    """Explicit argument, then HH_API_KEY, then HONEYHIVE_API_KEY, then None."""

    def test_explicit_beats_every_variable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicit key wins even when both variables are set."""
        monkeypatch.setenv("HH_API_KEY", "hh_preferred")
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        assert ResolvedConfig.resolve(api_key="hh_explicit").api_key == "hh_explicit"

    def test_preferred_variable_beats_alternate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_API_KEY wins over HONEYHIVE_API_KEY."""
        monkeypatch.setenv("HH_API_KEY", "hh_preferred")
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        assert ResolvedConfig.resolve().api_key == "hh_preferred"

    def test_alternate_is_read_when_preferred_is_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HONEYHIVE_API_KEY still works, and says what to set instead."""
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        with pytest.warns(DeprecationWarning, match="HONEYHIVE_API_KEY.*HH_API_KEY"):
            assert ResolvedConfig.resolve().api_key == "hh_alternate"

    def test_nothing_set_is_none(self) -> None:
        """Absence is reported, not judged; the consumer decides if it is an error."""
        assert ResolvedConfig.resolve().api_key is None

    @pytest.mark.parametrize("blank", ["", "   ", "\t"])
    def test_blank_explicit_falls_through_to_the_environment(
        self, blank: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A blank explicit value counts as absent."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        assert ResolvedConfig.resolve(api_key=blank).api_key == "hh_from_env"

    def test_blank_variable_falls_through_to_the_alternate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A blank variable counts as unset."""
        monkeypatch.setenv("HH_API_KEY", "  ")
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        with pytest.warns(DeprecationWarning):
            assert ResolvedConfig.resolve().api_key == "hh_alternate"

    def test_value_is_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Surrounding whitespace, a common copy-paste artefact, is removed."""
        monkeypatch.setenv("HH_API_KEY", " hh_padded ")
        assert ResolvedConfig.resolve().api_key == "hh_padded"

    def test_non_string_explicit_raises(self) -> None:
        """A non-string key is malformed and has no default, so it raises."""
        with pytest.raises(TypeError, match="api_key must be a string"):
            ResolvedConfig.resolve(**{"api_key": 123})


class TestApiUrlPrecedence:
    """Explicit argument, then HH_API_URL, then the alternates, then the default."""

    def test_explicit_beats_every_variable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicit URL wins even when all three variables are set."""
        monkeypatch.setenv("HH_API_URL", "https://preferred.example.test")
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        monkeypatch.setenv("HONEYHIVE_SERVER_URL", "https://honeyhive.example.test")
        config = ResolvedConfig.resolve(api_url="https://explicit.example.test")
        assert config.api_url == "https://explicit.example.test"

    def test_preferred_variable_beats_both_alternates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_API_URL wins over HONEYHIVE_SERVER_URL and HH_SERVER_URL."""
        monkeypatch.setenv("HH_API_URL", "https://preferred.example.test")
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        monkeypatch.setenv("HONEYHIVE_SERVER_URL", "https://honeyhive.example.test")
        assert ResolvedConfig.resolve().api_url == "https://preferred.example.test"

    def test_alternates_keep_their_relative_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Between the alternates, HONEYHIVE_SERVER_URL comes before HH_SERVER_URL."""
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        monkeypatch.setenv("HONEYHIVE_SERVER_URL", "https://honeyhive.example.test")
        with pytest.warns(DeprecationWarning, match="HONEYHIVE_SERVER_URL.*HH_API_URL"):
            assert ResolvedConfig.resolve().api_url == "https://honeyhive.example.test"

    def test_hh_server_url_alone_is_read_with_a_warning(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_SERVER_URL still works and names HH_API_URL."""
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        with pytest.warns(DeprecationWarning, match="HH_SERVER_URL.*HH_API_URL"):
            assert ResolvedConfig.resolve().api_url == "https://server.example.test"

    def test_nothing_set_is_the_default(self) -> None:
        """The default URL is defined once, here."""
        assert ResolvedConfig.resolve().api_url == DEFAULT_API_URL

    @pytest.mark.parametrize("source", ["explicit", "HH_API_URL"])
    def test_trailing_slash_is_removed(
        self, source: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A trailing slash would double up when request paths are appended."""
        if source == "explicit":
            config = ResolvedConfig.resolve(api_url="https://example.test/")
        else:
            monkeypatch.setenv("HH_API_URL", "https://example.test/")
            config = ResolvedConfig.resolve()
        assert config.api_url == "https://example.test"

    @pytest.mark.parametrize("source", ["explicit", "HH_API_URL"])
    def test_malformed_url_warns_and_uses_the_default(
        self,
        source: str,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """A URL without an http(s) scheme is malformed; the setting has a default."""
        with caplog.at_level(logging.WARNING, logger="honeyhive.config.resolved"):
            if source == "explicit":
                config = ResolvedConfig.resolve(api_url="example.test:3000")
            else:
                monkeypatch.setenv("HH_API_URL", "example.test:3000")
                config = ResolvedConfig.resolve()
        assert config.api_url == DEFAULT_API_URL
        named = "api_url" if source == "explicit" else source
        assert any(named in record.getMessage() for record in caplog.records)
        assert not any(
            "example.test" in record.getMessage() for record in caplog.records
        )

    def test_blank_explicit_falls_through(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A blank explicit URL counts as absent."""
        monkeypatch.setenv("HH_API_URL", "https://example.test")
        assert ResolvedConfig.resolve(api_url="").api_url == "https://example.test"


class TestDeprecationWarnings:
    """An alternate warns once per process, however many times it is resolved."""

    def test_warns_once_per_alternate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The second resolution of the same alternate is silent."""
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        with pytest.warns(DeprecationWarning):
            ResolvedConfig.resolve()
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            ResolvedConfig.resolve()

    def test_each_alternate_warns_independently(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Warning about one alternate does not silence another."""
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        with pytest.warns(DeprecationWarning) as caught:
            ResolvedConfig.resolve()
        messages = [str(w.message) for w in caught]
        assert any("HONEYHIVE_API_KEY" in m for m in messages)
        assert any("HH_SERVER_URL" in m for m in messages)

    def test_preferred_variables_never_warn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Using the documented names is silent."""
        monkeypatch.setenv("HH_API_KEY", "hh_preferred")
        monkeypatch.setenv("HH_API_URL", "https://preferred.example.test")
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            ResolvedConfig.resolve()


class TestConfigModelsUseTheResolver:
    """A directly built model asks the resolver for api_key and server_url."""

    def test_models_read_the_preferred_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """HH_API_KEY and HH_API_URL reach the models, normalized."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        monkeypatch.setenv("HH_API_URL", "https://preferred.example.test/")
        for model in (TracerConfig, APIClientConfig):
            config = model()
            assert config.api_key == "hh_from_env"
            assert config.server_url == "https://preferred.example.test"

    def test_models_apply_the_same_precedence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A model built from the environment resolves exactly as the client would."""
        monkeypatch.setenv("HONEYHIVE_API_KEY", "hh_alternate")
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        monkeypatch.setenv("HH_API_URL", "https://preferred.example.test")
        with pytest.warns(DeprecationWarning):
            config = TracerConfig()
        assert config.api_key == "hh_alternate"
        assert config.server_url == "https://preferred.example.test"

    def test_env_source_does_not_read_the_fields_itself(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """With the resolver silenced, HH_API_KEY in the environment reaches nothing."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        monkeypatch.setenv("HH_SERVER_URL", "https://server.example.test")
        monkeypatch.setattr(
            resolved, "_from_environment", lambda setting: (None, "unused")
        )
        config = TracerConfig()
        assert config.api_key is None
        assert config.server_url == DEFAULT_API_URL

    def test_explicit_constructor_argument_still_wins(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Init kwargs outrank the resolver."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        assert TracerConfig(api_key="hh_explicit").api_key == "hh_explicit"

    def test_explicit_server_url_is_normalized_by_the_same_rule(self) -> None:
        """Config(server_url=...) bypasses the resolver but not the shape rule."""
        assert TracerConfig(server_url="https://example.test/").server_url == (
            "https://example.test"
        )
        assert TracerConfig(server_url="example.test").server_url == DEFAULT_API_URL


class TestTracerPropDrilling:
    """Every model a tracer builds carries the tracer's own key and URL."""

    def test_nested_models_take_the_tracers_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An override given to the tracer reaches every section, not only the root."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        monkeypatch.setenv("HH_API_URL", "https://env.example.test")
        unified = create_unified_config(
            api_key="hh_override", server_url="https://override.example.test"
        )
        for section in ("http", "otlp", "api", "experiment", "session", "evaluation"):
            assert unified[section]["api_key"] == "hh_override", section
            assert unified[section]["server_url"] == "https://override.example.test"

    def test_a_user_supplied_config_object_is_left_alone(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A model the caller constructed keeps the caller's values."""
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        unified = create_unified_config(config=TracerConfig(api_key="hh_theirs"))
        assert unified["api_key"] == "hh_theirs"
        assert unified["api"]["api_key"] == "hh_theirs"

    def test_caller_supplied_section_configs_take_the_root_connection(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A SessionConfig or EvaluationConfig built by the caller agrees with the root.

        Each resolved its own key from the environment at construction; the
        unified result replaces those two fields with the root's. A value the
        caller set on the section config explicitly is kept instead.
        """
        monkeypatch.setenv("HH_API_KEY", "hh_from_env")
        monkeypatch.setenv("HH_API_URL", "https://env.example.test")
        unified = create_unified_config(
            config=TracerConfig(
                api_key="hh_root", server_url="https://root.example.test"
            ),
            session_config=SessionConfig(),
            evaluation_config=EvaluationConfig(),
        )
        for section in ("session", "evaluation", "http", "otlp", "api", "experiment"):
            assert unified[section]["api_key"] == "hh_root", section
            assert unified[section]["server_url"] == "https://root.example.test"


class TestIngestionApiKeyShape:
    """The one shape check every reader of an ingestion key runs."""

    def test_accepts_a_well_formed_key(self) -> None:
        """A complete hh_ingst_ key passes through unchanged."""
        assert (
            check_ingestion_api_key(INGESTION_KEY, "HH_INGESTION_API_KEY")
            == INGESTION_KEY
        )

    def test_strips_surrounding_whitespace(self) -> None:
        """Whitespace around a key, a common copy-paste artefact, is removed."""
        assert check_ingestion_api_key(f"  {INGESTION_KEY}\n", "x") == INGESTION_KEY

    def test_rejects_a_project_key_and_names_the_source(self) -> None:
        """A different HoneyHive key kind is refused by name, without echoing it."""
        with pytest.raises(
            ValueError, match="HH_INGESTION_API_KEY must be an ingestion API key"
        ) as exc_info:
            check_ingestion_api_key(PROJECT_KEY, "HH_INGESTION_API_KEY")
        assert "different kind of HoneyHive API key" in str(exc_info.value)
        assert PROJECT_KEY not in str(exc_info.value)

    def test_rejects_a_value_that_is_not_a_honeyhive_key(self) -> None:
        """A value from another vendor is refused without echoing it."""
        with pytest.raises(ValueError, match="not a HoneyHive API key") as exc_info:
            check_ingestion_api_key("sk-not-ours", "ingestion_api_key")
        assert "sk-not-ours" not in str(exc_info.value)

    def test_rejects_a_truncated_ingestion_key(self) -> None:
        """The prefix alone is not enough; the id and secret lengths are fixed."""
        with pytest.raises(ValueError, match="not a complete key"):
            check_ingestion_api_key(INGESTION_KEY[:-1], "ingestion_api_key")


class TestIngestionApiKeyPrecedence:
    """Explicit argument, then HH_INGESTION_API_KEY, then None; no alternate."""

    def test_explicit_beats_the_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An explicit key wins over the variable."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", INGESTION_KEY)
        config = ResolvedConfig.resolve(ingestion_api_key=OTHER_INGESTION_KEY)
        assert config.ingestion_api_key == OTHER_INGESTION_KEY

    def test_variable_is_read(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """HH_INGESTION_API_KEY is the one variable."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", INGESTION_KEY)
        assert ResolvedConfig.resolve().ingestion_api_key == INGESTION_KEY

    def test_nothing_set_is_none(self) -> None:
        """Absence is reported, not judged: api_key then serves ingestion too."""
        assert ResolvedConfig.resolve().ingestion_api_key is None

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_counts_as_unset(
        self, blank: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A blank value, explicit or in the variable, counts as unset."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", blank)
        assert ResolvedConfig.resolve().ingestion_api_key is None
        assert ResolvedConfig.resolve(ingestion_api_key=blank).ingestion_api_key is None

    def test_wrong_kind_in_the_variable_raises_naming_it(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A project key in the variable fails at resolution and names the variable."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", PROJECT_KEY)
        with pytest.raises(
            ValueError, match="HH_INGESTION_API_KEY must be an ingestion API key"
        ) as exc_info:
            ResolvedConfig.resolve()
        assert PROJECT_KEY not in str(exc_info.value)

    def test_wrong_kind_in_the_argument_raises_naming_it(self) -> None:
        """A project key passed explicitly fails and names the parameter."""
        with pytest.raises(
            ValueError, match="ingestion_api_key must be an ingestion API key"
        ):
            ResolvedConfig.resolve(ingestion_api_key=PROJECT_KEY)

    def test_non_string_argument_raises(self) -> None:
        """A non-string is malformed with no default, so it raises."""
        with pytest.raises(TypeError, match="ingestion_api_key must be a string"):
            ResolvedConfig.resolve(**{"ingestion_api_key": 123})

    def test_an_ingestion_key_in_api_key_is_forwarded_unchanged(self) -> None:
        """api_key has no shape rule; the server decides."""
        assert ResolvedConfig.resolve(api_key=INGESTION_KEY).api_key == INGESTION_KEY


class TestIngestionApiKeyOnModels:
    """The models and the tracer's sections carry the same ingestion key."""

    def test_model_reads_the_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A directly built model asks the resolver for the ingestion key too."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", INGESTION_KEY)
        assert TracerConfig().ingestion_api_key == INGESTION_KEY

    def test_model_rejects_a_wrong_kind_constructed_explicitly(self) -> None:
        """An explicit constructor value bypasses the resolver, not the shape rule."""
        with pytest.raises(ValidationError, match="ingestion API key"):
            TracerConfig(ingestion_api_key=PROJECT_KEY)

    def test_model_rejects_a_non_string_as_a_validation_error(self) -> None:
        """The validator's own type branch: a ValidationError, not the resolver's TypeError."""
        with pytest.raises(ValidationError, match="must be a string"):
            TracerConfig(**{"ingestion_api_key": 123})

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_model_treats_a_blank_explicit_value_as_unset(self, blank: str) -> None:
        """The validator's blank branch, which has no resolver equivalent."""
        assert TracerConfig(ingestion_api_key=blank).ingestion_api_key is None

    def test_wrong_kind_in_the_variable_fails_model_construction(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The check runs when the model resolves from the environment as well."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", PROJECT_KEY)
        with pytest.raises(ValueError, match="HH_INGESTION_API_KEY"):
            TracerConfig()

    def test_nested_sections_carry_the_tracers_ingestion_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An override given to the tracer reaches every section."""
        monkeypatch.setenv("HH_INGESTION_API_KEY", INGESTION_KEY)
        unified = create_unified_config(ingestion_api_key=OTHER_INGESTION_KEY)
        assert unified["ingestion_api_key"] == OTHER_INGESTION_KEY
        for section in SECTIONS:
            assert unified[section]["ingestion_api_key"] == OTHER_INGESTION_KEY, section
