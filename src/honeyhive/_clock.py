"""Monotonic-anchored wall clock and per-call timestamp capture.

The SDK emits a wall-clock ``hh-client-timestamp`` header on every REST
request so the backend can order requests from the same client correctly.
Two properties matter:

1. **Monotonicity within a process.** Successive requests must produce
   non-decreasing timestamps even if the system wall clock is adjusted
   (NTP slew, manual change). We anchor a wall-clock reading at module load
   and accumulate ``time.monotonic_ns()`` deltas from it. The result is
   wall-clock-comparable across processes but guaranteed non-decreasing
   within a single process.

2. **Stamped at the user-call boundary, not at wire-send time.** The
   timestamp reflects when the user invoked the SDK method, not when the
   HTTP bytes left the socket. The boundary value is held in a ContextVar
   that ``APIConfig.get_default_headers()`` reads from, so retries and any
   inner helper calls all emit the same value.
"""

from __future__ import annotations

import contextvars
import functools
import inspect
import time
from typing import Any, Callable, Optional

# Captured at module load. Together they let us compute a wall-clock-anchored
# nanosecond timestamp that is monotonic within the process.
_WALL_ANCHOR_NS: int = time.time_ns()
_MONO_ANCHOR_NS: int = time.monotonic_ns()


def _client_now_ns() -> int:
    """Return a wall-clock-anchored nanosecond timestamp.

    Equivalent to ``time.time_ns()`` at the moment this module was imported,
    plus the monotonic time elapsed since. Guaranteed non-decreasing within
    the process even if the system wall clock steps backwards.

    Note: cross-process comparability holds only at process start. If the
    host wall clock is adjusted (NTP step, manual change) after the anchor
    is captured, this function continues to emit
    ``original_wall_anchor + monotonic_delta`` and will diverge from a fresh
    ``time.time_ns()`` reading by the magnitude of the adjustment. Within
    a process, ordering is preserved -- which is what this header relies on.
    """
    return _WALL_ANCHOR_NS + (time.monotonic_ns() - _MONO_ANCHOR_NS)


# Holds the timestamp captured at the outermost SDK public method entry.
# When set, ``get_default_headers()`` reads from this so retries and inner
# helper calls all serialize the same "user intent" timestamp.
_call_time_ns: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "hh_call_time_ns", default=None
)


def _get_or_stamp_call_time_ns() -> int:
    """Return the captured call-entry timestamp, or ``_client_now_ns()`` if none.

    The fallback keeps direct callers of ``get_default_headers()`` working
    (e.g. ad-hoc httpx requests outside an SDK method).
    """
    captured = _call_time_ns.get()
    return captured if captured is not None else _client_now_ns()


def _stamp_call(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a public API method so its entry time is captured into the ContextVar.

    Re-entrant safe: if the ContextVar is already set (an outer stamped method
    is on the call stack), the wrapper is a no-op and the outer timestamp wins.
    This keeps backwards-compat aliases (``create_event`` -> ``create``) from
    overwriting the caller's stamp.

    Generator and async-generator functions are not supported: calling such a
    function returns the iterator without executing the body, so the wrapper
    would hit its ``finally`` and reset the ContextVar before the caller
    iterated. Raises ``TypeError`` to surface the misuse at class definition
    time rather than silently losing the stamp at runtime.
    """
    if inspect.isgeneratorfunction(fn) or inspect.isasyncgenfunction(fn):
        raise TypeError(
            f"_stamp_call does not support generator functions ({fn.__qualname__}); "
            "wrap the consumer that fully iterates the generator instead."
        )

    if inspect.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if _call_time_ns.get() is not None:
                return await fn(*args, **kwargs)
            token = _call_time_ns.set(_client_now_ns())
            try:
                return await fn(*args, **kwargs)
            finally:
                _call_time_ns.reset(token)

        return async_wrapper

    @functools.wraps(fn)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        if _call_time_ns.get() is not None:
            return fn(*args, **kwargs)
        token = _call_time_ns.set(_client_now_ns())
        try:
            return fn(*args, **kwargs)
        finally:
            _call_time_ns.reset(token)

    return sync_wrapper
