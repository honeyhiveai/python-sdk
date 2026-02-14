from typing import *

from pydantic import BaseModel, Field


class CreateDatasetResponse(BaseModel):
    """
    CreateDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: Optional[bool] = Field(validation_alias="inserted", default=None)

    result: Optional[Dict[str, Any]] = Field(validation_alias="result", default=None)
