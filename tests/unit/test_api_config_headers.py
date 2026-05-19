"""Unit tests for APIConfig.get_default_headers(), the SDK clock module, and
the BaseAPI auto-wrap mechanism that captures call-entry timestamps."""

import asyncio

import honeyhive._clock as clock
from honeyhive import __version__
from honeyhive._clock import (
    _call_time_ns,
    _client_now_ns,
    _get_or_stamp_call_time_ns,
    _stamp_call,
)
from honeyhive._generated.api_config import APIConfig, _get_sdk_version
from honeyhive.api._base import BaseAPI


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

    def test_includes_client_timestamp_header(self) -> None:
        """get_default_headers() must include hh-client-timestamp."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        assert "hh-client-timestamp" in headers

    def test_client_timestamp_is_decimal_string(self) -> None:
        """hh-client-timestamp must be a decimal-digit string."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        ts = headers["hh-client-timestamp"]
        assert ts.isdigit(), f"expected all digits, got {ts!r}"

    def test_client_timestamp_is_nanosecond_range(self) -> None:
        """hh-client-timestamp must be > 1e18 (nanoseconds after 2001-09-09)."""
        config = APIConfig(access_token="test-token")
        headers = config.get_default_headers()
        ts_ns = int(headers["hh-client-timestamp"])
        assert ts_ns > 1_000_000_000_000_000_000, f"timestamp {ts_ns} looks too small"

    def test_client_timestamp_recomputed_when_no_context(self, monkeypatch) -> None:
        """Without an enclosing stamped call, each get_default_headers() reads
        a fresh value from _client_now_ns()."""
        values = iter([1_700_000_000_000_000_000, 1_700_000_000_000_000_500])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))
        config = APIConfig(access_token="test-token")
        ts1 = config.get_default_headers()["hh-client-timestamp"]
        ts2 = config.get_default_headers()["hh-client-timestamp"]
        assert ts1 != ts2


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


class TestClientNowNs:
    """Tests for _client_now_ns() — the monotonic-anchored wall clock."""

    def test_returns_int(self) -> None:
        """_client_now_ns() must return an int."""
        assert isinstance(_client_now_ns(), int)

    def test_is_non_decreasing(self) -> None:
        """Successive calls must never go backwards, even back-to-back."""
        samples = [_client_now_ns() for _ in range(1000)]
        for a, b in zip(samples, samples[1:]):
            assert b >= a, f"clock went backwards: {a} -> {b}"

    def test_in_wall_clock_range(self) -> None:
        """Anchored to wall clock — value should be in the modern epoch range."""
        assert _client_now_ns() > 1_000_000_000_000_000_000


class TestGetOrStampCallTime:
    """Tests for _get_or_stamp_call_time_ns()."""

    def test_falls_back_to_now_when_context_unset(self, monkeypatch) -> None:
        """When the ContextVar is unset, returns _client_now_ns()."""
        monkeypatch.setattr(clock, "_client_now_ns", lambda: 42)
        assert _call_time_ns.get() is None
        assert _get_or_stamp_call_time_ns() == 42

    def test_returns_captured_when_context_set(self) -> None:
        """When the ContextVar is set, returns the captured value (not now)."""
        token = _call_time_ns.set(12345)
        try:
            assert _get_or_stamp_call_time_ns() == 12345
        finally:
            _call_time_ns.reset(token)


class TestStampCallDecorator:
    """Tests for _stamp_call()."""

    def test_sync_captures_entry_time_into_context(self, monkeypatch) -> None:
        """The sync wrapper sets the ContextVar to the entry-time value."""
        monkeypatch.setattr(clock, "_client_now_ns", lambda: 9001)

        observed = {}

        @_stamp_call
        def fn() -> None:
            observed["ts"] = _call_time_ns.get()

        fn()
        assert observed["ts"] == 9001

    def test_async_captures_entry_time_into_context(self, monkeypatch) -> None:
        """The async wrapper sets the ContextVar to the entry-time value."""
        monkeypatch.setattr(clock, "_client_now_ns", lambda: 12345)

        observed = {}

        @_stamp_call
        async def fn() -> None:
            observed["ts"] = _call_time_ns.get()

        asyncio.run(fn())
        assert observed["ts"] == 12345

    def test_context_var_cleared_after_sync_call(self, monkeypatch) -> None:
        """After the wrapped sync function returns, the ContextVar is reset."""
        monkeypatch.setattr(clock, "_client_now_ns", lambda: 1)

        @_stamp_call
        def fn() -> None:
            pass

        fn()
        assert _call_time_ns.get() is None

    def test_context_var_cleared_after_exception(self, monkeypatch) -> None:
        """ContextVar must be reset even when the wrapped function raises."""
        monkeypatch.setattr(clock, "_client_now_ns", lambda: 1)

        @_stamp_call
        def fn() -> None:
            raise ValueError("boom")

        try:
            fn()
        except ValueError:
            pass
        assert _call_time_ns.get() is None

    def test_reentrant_sync_outer_wins(self, monkeypatch) -> None:
        """When a stamped method calls another stamped method, the outer
        timestamp survives — inner's entry doesn't overwrite it."""
        values = iter([100, 200])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))

        observed = {}

        @_stamp_call
        def inner() -> None:
            observed["inner"] = _call_time_ns.get()

        @_stamp_call
        def outer() -> None:
            observed["outer_before"] = _call_time_ns.get()
            inner()
            observed["outer_after"] = _call_time_ns.get()

        outer()
        assert observed["outer_before"] == 100
        assert observed["inner"] == 100  # outer wins; second next() never consumed
        assert observed["outer_after"] == 100

    def test_reentrant_async_outer_wins(self, monkeypatch) -> None:
        """Re-entrancy guard works for async wrappers too."""
        values = iter([500, 600])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))

        observed = {}

        @_stamp_call
        async def inner() -> None:
            observed["inner"] = _call_time_ns.get()

        @_stamp_call
        async def outer() -> None:
            await inner()
            observed["outer"] = _call_time_ns.get()

        asyncio.run(outer())
        assert observed["outer"] == 500
        assert observed["inner"] == 500

    def test_rejects_sync_generator_function(self) -> None:
        """Generator functions silently lose their stamp; wrapping must raise."""

        def gen():
            yield 1

        try:
            _stamp_call(gen)
        except TypeError as exc:
            assert "generator" in str(exc)
        else:
            raise AssertionError("expected TypeError for generator function")

    def test_rejects_async_generator_function(self) -> None:
        """Async-generator functions are rejected for the same reason."""

        async def agen():
            yield 1

        try:
            _stamp_call(agen)
        except TypeError as exc:
            assert "generator" in str(exc)
        else:
            raise AssertionError("expected TypeError for async generator function")


class TestBaseAPIAutoWrap:
    """Tests for BaseAPI.__init_subclass__ — auto-wrapping public methods."""

    def test_public_method_is_wrapped(self) -> None:
        """A public method on a BaseAPI subclass picks up _stamp_call wrapping."""

        class FakeAPI(BaseAPI):
            def do_thing(self) -> int:
                return 7

        api = FakeAPI(APIConfig(access_token="x"))
        # Wrapped function has __wrapped__ via functools.wraps
        assert hasattr(FakeAPI.do_thing, "__wrapped__")
        assert api.do_thing() == 7

    def test_private_method_is_not_wrapped(self) -> None:
        """Underscore-prefixed methods are skipped by the wrapper."""

        class FakeAPI(BaseAPI):
            def _internal(self) -> int:
                return 9

        assert not hasattr(FakeAPI._internal, "__wrapped__")

    def test_staticmethod_is_not_wrapped(self) -> None:
        """Static methods aren't wrapped (the wrapper would mishandle them)."""

        class FakeAPI(BaseAPI):
            @staticmethod
            def helper() -> int:
                return 1

        # vars(cls)[name] for a staticmethod is the staticmethod descriptor.
        attr = vars(FakeAPI)["helper"]
        assert isinstance(attr, staticmethod)

    def test_header_uses_entry_timestamp_during_call(self, monkeypatch) -> None:
        """End-to-end: a wrapped API method's get_default_headers() call
        inside the method body returns the entry-time timestamp, not the
        wire-send time."""
        values = iter([10_000, 99_999])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))

        captured = {}

        class FakeAPI(BaseAPI):
            def do_thing(self) -> None:
                captured.update(self._api_config.get_default_headers())

        api = FakeAPI(APIConfig(access_token="test"))
        api.do_thing()
        # 10_000 was consumed at entry; the second next() (99_999) is NOT
        # consumed because get_default_headers() reads from the ContextVar.
        assert captured["hh-client-timestamp"] == "10000"

    def test_header_uses_entry_timestamp_async(self, monkeypatch) -> None:
        """Same end-to-end guarantee for async methods."""
        values = iter([2_000, 3_000])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))

        captured = {}

        class FakeAsyncAPI(BaseAPI):
            async def do_thing_async(self) -> None:
                captured.update(self._api_config.get_default_headers())

        api = FakeAsyncAPI(APIConfig(access_token="test"))
        asyncio.run(api.do_thing_async())
        assert captured["hh-client-timestamp"] == "2000"

    def test_alias_method_preserves_outer_stamp(self, monkeypatch) -> None:
        """Backwards-compat alias -> real method -> header chain: the alias's
        entry timestamp survives all the way into the header, even though the
        real method is also stamped."""
        values = iter([100, 200])
        monkeypatch.setattr(clock, "_client_now_ns", lambda: next(values))

        captured = []

        class FakeAPI(BaseAPI):
            def create(self, x: int) -> None:
                captured.append(
                    self._api_config.get_default_headers()["hh-client-timestamp"]
                )

            def create_event(self, x: int) -> None:
                # Backwards-compat alias delegates to the canonical method.
                self.create(x)

        api = FakeAPI(APIConfig(access_token="t"))
        api.create_event(1)
        # Outer alias captured 100; inner create() saw the ContextVar already
        # set and short-circuited, so the second next() (200) was never used.
        assert captured == ["100"]
