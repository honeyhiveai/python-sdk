"""Every twin pair a client offers reaches its project-scoped operation from Python.

A twin pair is one capability on two URLs: the flat operation, which carries
``x-twin``, and the scoped operation it names, which takes the project in its
path. The TypeScript SDK and the CLI generate one method and command per pair.
The Python methods are hand-written, so this checks the shim calls each pair's
scoped operation from a sync and an async service. It does not require the flat
operation, because a method's call without a project may reach an older
operation than the pair's flat arm. That a call carries the right key is the
live data plane suite's to check.
"""

from tests.integration._spec_operations import (
    require_spec,
    shim_operations,
    spec_client_facing_twins,
)


def test_every_twin_pair_has_sync_and_async_wrappers() -> None:
    """Each client-facing pair's scoped operation is called sync and async."""
    require_spec()
    scoped = set(spec_client_facing_twins().values())
    assert scoped, "the spec declares no client-facing twin pairs"

    missing_sync = scoped - shim_operations(asynchronous=False)
    missing_async = scoped - shim_operations(asynchronous=True)

    assert not missing_sync, f"no sync wrapper calls {sorted(missing_sync)}"
    assert not missing_async, f"no async wrapper calls {sorted(missing_async)}"
