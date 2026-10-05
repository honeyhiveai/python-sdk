"""The ingestion operations the SDK exposes, and how to call each on an ingestion key.

The Data Plane OpenAPI spec declares which operations the ingestion endpoints
serve: those whose ``security`` names the ``IngestionApiKey`` scheme. The SDK
exposes some of them through ``HoneyHive`` wrappers, and each wrapper passes
the ingestion configuration. ``OPERATIONS`` is the one dictionary that ties the
two together: keyed by operationId, each value performs the operation through
the public wrapper on a client holding only an ingestion key and says how to
read the result back on the project key.

Two tests consume it. ``tests/unit/test_ingestion_operations_match_the_spec.py``
asserts its keys equal the wrapped ingestion operations (the spec's set,
intersected with the operations the shim calls a generated service function
for), so a new wrapper for an ingestion route fails until it has an entry. It
runs in the unit job, where the ``openapi/dataplane.yaml`` symlink resolves.
``tests/integration/test_ingestion_api_key_endpoints.py`` runs every entry
live. Operations the spec declares but the SDK does not wrap are unsupported
and have no entry.
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from honeyhive.api.client import HoneyHive
from honeyhive.models import PostEventBatchRequest, PostEventRequest, UpdateEventRequest

INGESTION_SCHEME = "IngestionApiKey"

# How long update_event_legacy waits for a created event to become durable
# before it updates the event. The value is far above the server flush
# interval, so a loaded CI runner does not shorten the wait into the race.
_CREATE_SETTLE_SECONDS = 5.0


def _named(events: List[Any], name: str) -> Optional[Any]:
    return next(
        (event for event in events if getattr(event, "event_name", None) == name),
        None,
    )


@dataclass(frozen=True)
class Outcome:
    """What an entry did, for the read-back on the project key.

    ``landed`` is checked over the session's events. None means the server's
    acceptance of the call was the whole proof.
    """

    session_id: str
    landed: Optional[Callable[[List[Any]], bool]] = None


# (client holding only an ingestion key, project, source) -> what to read back.
Entry = Callable[[HoneyHive, str, str], Outcome]


def _start_session(client: HoneyHive, project: str, source: str) -> str:
    started = client.sessions.start(
        {
            "session": {
                "project": project,
                "session_name": f"ingestion-key-{uuid.uuid4().hex[:8]}",
                "source": source,
            }
        }
    )
    assert started.session_id
    return started.session_id


def _event(project: str, source: str, session_id: str, name: str) -> Dict[str, Any]:
    return {
        "project": project,
        "source": source,
        "event_name": name,
        "event_type": "tool",
        "inputs": {"value": 21},
        "outputs": {"value": 42},
        "session_id": session_id,
        "duration": 1.0,
    }


def start_session_legacy(client: HoneyHive, project: str, source: str) -> Outcome:
    """``sessions.start``: the returned session id is the server's acceptance."""
    return Outcome(_start_session(client, project, source))


def create_event_legacy(client: HoneyHive, project: str, source: str) -> Outcome:
    """``events.create``: the event is found under its session afterwards."""
    session_id = _start_session(client, project, source)
    name = f"created-{uuid.uuid4().hex[:8]}"
    created = client.events.create(
        PostEventRequest(event=_event(project, source, session_id, name))
    )
    assert created.event_id
    return Outcome(session_id, lambda events: _named(events, name) is not None)


def update_event_legacy(client: HoneyHive, project: str, source: str) -> Outcome:
    """``events.update``: the metadata written by the update is read back."""
    session_id = _start_session(client, project, source)
    name = f"updated-{uuid.uuid4().hex[:8]}"
    created = client.events.create(
        PostEventRequest(event=_event(project, source, session_id, name))
    )
    # The create call returns before the event is durable. A create and an
    # update sent inside that window can be applied out of order, which drops
    # the update with no error. This test covers the update endpoint on an
    # ingestion key, not concurrent writes, so it waits instead of asserting
    # on the order.
    # TODO: delete this wait after the server orders a create and an update
    # to the same event.
    time.sleep(_CREATE_SETTLE_SECONDS)
    marker = uuid.uuid4().hex
    client.events.update(
        UpdateEventRequest(
            event_id=created.event_id, metadata={"ingestion_key_marker": marker}
        )
    )

    def landed(events: List[Any]) -> bool:
        event = _named(events, name)
        metadata = getattr(event, "metadata", None) or {}
        return event is not None and metadata.get("ingestion_key_marker") == marker

    return Outcome(session_id, landed)


def create_event_batch_legacy(client: HoneyHive, project: str, source: str) -> Outcome:
    """``events.create_batch``: every event in the batch is found afterwards."""
    session_id = _start_session(client, project, source)
    names = [f"batched-{uuid.uuid4().hex[:8]}-{index}" for index in range(2)]
    client.events.create_batch(
        PostEventBatchRequest(
            events=[_event(project, source, session_id, name) for name in names]
        )
    )
    return Outcome(
        session_id, lambda events: all(_named(events, n) is not None for n in names)
    )


# Keyed by operationId. A wrapped ingestion operation missing here fails the
# unit guard; an entry for an operation the shim does not wrap fails it too.
OPERATIONS: Dict[str, Entry] = {
    "startSessionLegacy": start_session_legacy,
    "createEventLegacy": create_event_legacy,
    "updateEventLegacy": update_event_legacy,
    "createEventBatchLegacy": create_event_batch_legacy,
}
