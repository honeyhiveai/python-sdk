from typing import *

from pydantic import BaseModel, Field


class CreateDatapointResponse(BaseModel):
    """
    CreateDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: Optional[Dict[str, Any]] = Field(validation_alias="result", default=None)
