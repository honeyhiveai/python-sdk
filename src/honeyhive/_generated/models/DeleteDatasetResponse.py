from typing import *

from pydantic import BaseModel, Field

from .DeleteResult import DeleteResult


class DeleteDatasetResponse(BaseModel):
    """
    DeleteDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: DeleteResult = Field(validation_alias="result")
