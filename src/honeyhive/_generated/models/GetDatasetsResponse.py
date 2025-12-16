from typing import *

from pydantic import BaseModel, Field


class GetDatasetsResponse(BaseModel):
    """
    GetDatasetsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoints: List[Dict[str, Any]] = Field(validation_alias="datapoints")
