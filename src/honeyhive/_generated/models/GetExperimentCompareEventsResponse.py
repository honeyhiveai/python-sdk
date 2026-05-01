from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ComparableEvent import ComparableEvent

__all__ = ["GetExperimentCompareEventsResponse"]


class GetExperimentCompareEventsResponse(BaseModel):
    """
    GetExperimentCompareEventsResponse model
        Response for GET /runs/compare/events
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[ComparableEvent] = Field(validation_alias="events")

    totalEvents: int = Field(validation_alias="totalEvents")
