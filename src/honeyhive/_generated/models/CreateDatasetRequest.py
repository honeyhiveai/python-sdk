from typing import *

from pydantic import BaseModel, Field


class CreateDatasetRequest(BaseModel):
    """
    CreateDatasetRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)
