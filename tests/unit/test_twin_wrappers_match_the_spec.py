"""Every twin pair a client offers reaches its project-scoped operation from Python.

A twin pair is one capability on two URLs: the flat operation, which carries
``x-twin``, and the scoped operation it names, which takes the project in its
path. The TypeScript SDK and the CLI generate one method and command per pair.
The Python methods are hand-written, so this checks the shim calls each pair's
scoped operation from a sync and an async service, except the pairs in
``UNWRAPPED``. It does not require the flat operation, because a method's call
without a project may reach an older operation than the pair's flat arm. That a
call carries the right key is the live data plane suite's to check.
"""

from typing import Dict

from tests.integration._spec_operations import (
    require_spec,
    shim_operations,
    spec_client_facing_twins,
)

# Scoped operations no wrapper calls, each with the reason the SDK offers no
# project-scoped form of the capability.
UNWRAPPED: Dict[str, str] = {
    "searchEvents": (
        "its methods take no project and post to an older operation that "
        "accepts requests the scoped operation refuses"
    ),
    "getEvent": "the SDK wraps neither operation of the pair",
}


def test_every_twin_pair_has_sync_and_async_wrappers() -> None:
    """Each client-facing pair's scoped operation is called sync and async."""
    require_spec()
    twins = set(spec_client_facing_twins().values())
    assert twins, "the spec declares no client-facing twin pairs"
    unwrapped = set(UNWRAPPED)
    assert unwrapped <= twins, sorted(unwrapped - twins)
    scoped = twins - unwrapped

    missing_sync = scoped - shim_operations(asynchronous=False)
    missing_async = scoped - shim_operations(asynchronous=True)

    assert not missing_sync, f"no sync wrapper calls {sorted(missing_sync)}"
    assert not missing_async, f"no async wrapper calls {sorted(missing_async)}"


def test_unwrapped_twins_have_no_wrapper() -> None:
    """A scoped operation listed in UNWRAPPED is called by no wrapper."""
    require_spec()
    wrapped = shim_operations(asynchronous=False) | shim_operations(asynchronous=True)
    unwrapped = set(UNWRAPPED)
    assert not unwrapped & wrapped, sorted(unwrapped & wrapped)
