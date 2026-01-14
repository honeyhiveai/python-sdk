from typing import *

from pydantic import BaseModel, Field


class UpdateDatasetResponse(BaseModel):
    """
    UpdateDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: Dict[str, Any] = Field(validation_alias="result")
