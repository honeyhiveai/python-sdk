from typing import *

from pydantic import BaseModel, Field


class ExperimentSchemaField(BaseModel):
    """
    ExperimentSchemaField model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    event_type: str = Field(validation_alias="event_type")
