"""The live data plane key suite covers exactly the data plane operations the SDK exposes.

``OPERATIONS`` in ``tests/integration/_data_plane_operations`` is hand-written.
The spec says which operations take the data plane key, and the shim's source
says which of those the SDK wraps; their intersection must equal the
dictionary's keys. A new wrapper for a data plane route therefore fails here,
in the unit job, until it has a live entry. This runs as a unit test because
the spec is reached through a symlink that resolves only in a monorepo
checkout; the integration image cannot see it.
"""

from tests.integration import _data_plane_operations as data_plane
from tests.integration import _ingestion_operations as ingestion
from tests.integration._spec_operations import (
    require_spec,
    shim_operations,
    spec_operations_declaring,
)


def test_every_wrapped_data_plane_operation_has_a_live_entry() -> None:
    """OPERATIONS keys equal the spec's DataPlaneApiKey operations the shim wraps."""
    require_spec()
    declaring = spec_operations_declaring(data_plane.DATA_PLANE_SCHEME)
    assert declaring, "the spec declares no DataPlaneApiKey operations"
    wrapped = declaring & shim_operations()
    assert wrapped, "the shim wraps no data plane operation"
    assert set(data_plane.OPERATIONS) == wrapped, sorted(
        set(data_plane.OPERATIONS) ^ wrapped
    )


def test_no_operation_is_in_both_live_suites() -> None:
    """The data plane and ingestion suites cover disjoint operations.

    Each live suite runs its operations on a client holding only its own key,
    so a wrapper sending the other key's configuration fails there. That holds
    only while no operation sits in both suites, since no operation accepts
    both keys.
    """
    assert data_plane.OPERATIONS and ingestion.OPERATIONS
    assert set(data_plane.OPERATIONS).isdisjoint(ingestion.OPERATIONS), sorted(
        set(data_plane.OPERATIONS) & set(ingestion.OPERATIONS)
    )
