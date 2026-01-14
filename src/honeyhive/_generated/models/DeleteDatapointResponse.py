from typing import *

from pydantic import BaseModel, Field


class DeleteDatapointResponse(BaseModel):
    """
    DeleteDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    deleted: bool = Field(validation_alias="deleted")
