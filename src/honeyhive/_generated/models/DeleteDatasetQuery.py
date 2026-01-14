from typing import *

from pydantic import BaseModel, Field


class DeleteDatasetQuery(BaseModel):
    """
    DeleteDatasetQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: str = Field(validation_alias="dataset_id")
