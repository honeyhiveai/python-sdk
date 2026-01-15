from typing import *

from pydantic import BaseModel, Field

from .Datapoint import Datapoint


class GetDatapointResponse(BaseModel):
    """
    GetDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoint: List[Datapoint] = Field(validation_alias="datapoint")
