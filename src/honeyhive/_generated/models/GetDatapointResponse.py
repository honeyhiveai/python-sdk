from typing import *

from pydantic import BaseModel, Field


class GetDatapointResponse(BaseModel):
    """
    GetDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoint: List[Dict[str, Any]] = Field(validation_alias="datapoint")
