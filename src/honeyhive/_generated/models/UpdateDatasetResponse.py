from typing import *

from pydantic import BaseModel, Field

from .Dataset import Dataset


class UpdateDatasetResponse(BaseModel):
    """
    UpdateDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: Dataset = Field(validation_alias="result")
