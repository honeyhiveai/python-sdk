from typing import *

from pydantic import BaseModel, Field


class EventComparisonDetail(BaseModel):
    """
    EventComparisonDetail model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_name: str = Field(validation_alias="event_name")

    event_type: str = Field(validation_alias="event_type")

    presence: str = Field(validation_alias="presence")
