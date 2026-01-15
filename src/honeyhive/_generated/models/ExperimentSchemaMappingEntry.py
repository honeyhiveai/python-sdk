from typing import *

from pydantic import BaseModel, Field


class ExperimentSchemaMappingEntry(BaseModel):
    """
    ExperimentSchemaMappingEntry model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    field_name: str = Field(validation_alias="field_name")

    event_type: str = Field(validation_alias="event_type")
