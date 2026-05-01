from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyEvent import LegacyEvent

__all__ = ["ExportEventsResponse"]


class ExportEventsResponse(BaseModel):
    """
    ExportEventsResponse model
        Response for POST /v1/events/search and POST /v1/events/export
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[LegacyEvent] = Field(validation_alias="events")

    count: float = Field(validation_alias="count")
