from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyEvent import LegacyEvent

__all__ = ["AddSessionTracesRequest"]


class AddSessionTracesRequest(BaseModel):
    """
    AddSessionTracesRequest model
        Request body for POST /session/{session_id}/traces (deprecated — use POST /v1/sessions/{session_id}/events/batch). Exactly one of `logs` (deprecated) or `events` must be present.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    logs: Optional[List[Optional[LegacyEvent]]] = Field(
        validation_alias="logs", default=None
    )

    events: Optional[List[Optional[LegacyEvent]]] = Field(
        validation_alias="events", default=None
    )
