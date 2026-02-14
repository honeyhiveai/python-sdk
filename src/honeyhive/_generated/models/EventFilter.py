from typing import *

from pydantic import BaseModel, Field


class EventFilter(BaseModel):
    """
    EventFilter model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    field: Optional[str] = Field(validation_alias="field", default=None)

    value: Optional[str] = Field(validation_alias="value", default=None)

    operator: Optional[str] = Field(validation_alias="operator", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)
