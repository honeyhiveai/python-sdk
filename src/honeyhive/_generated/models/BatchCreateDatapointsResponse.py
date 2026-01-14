from typing import *

from pydantic import BaseModel, Field


class BatchCreateDatapointsResponse(BaseModel):
    """
    BatchCreateDatapointsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: bool = Field(validation_alias="inserted")

    insertedIds: List[str] = Field(validation_alias="insertedIds")
