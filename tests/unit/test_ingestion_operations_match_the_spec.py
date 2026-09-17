"""The live ingestion-key suite covers exactly the ingestion operations the SDK exposes.

``OPERATIONS`` in ``tests/integration/_ingestion_operations`` is hand-written.
The spec says which operations the ingestion endpoints serve, and the shim's
source says which of those the SDK wraps; their intersection must equal the
dictionary's keys. A new wrapper for an ingestion route therefore fails here,
in the unit job, until it has a live entry. This runs as a unit test because
the spec is reached through a symlink that resolves only in a monorepo
checkout; the integration image cannot see it.
"""

from tests.integration._ingestion_operations import (
    OPERATIONS,
    require_spec,
    shim_operations,
    spec_ingestion_operations,
)


def test_every_wrapped_ingestion_operation_has_a_live_entry() -> None:
    """OPERATIONS keys equal the spec's IngestionApiKey operations the shim wraps."""
    require_spec()
    ingestion = spec_ingestion_operations()
    assert ingestion, "the spec declares no IngestionApiKey operations"
    wrapped = ingestion & shim_operations()
    assert wrapped, "the shim wraps no ingestion operation"
    assert set(OPERATIONS) == wrapped, sorted(set(OPERATIONS) ^ wrapped)
