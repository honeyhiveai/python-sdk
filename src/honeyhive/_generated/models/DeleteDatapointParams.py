from typing import *

from pydantic import BaseModel, Field


class DeleteDatapointParams(BaseModel):
    """
    DeleteDatapointParams model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoint_id: str = Field(validation_alias="datapoint_id")
