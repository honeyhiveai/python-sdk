from typing import *

from pydantic import BaseModel, Field


class UpdateDatasetRequest(BaseModel):
    """
    UpdateDatasetRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: str = Field(validation_alias="dataset_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)
