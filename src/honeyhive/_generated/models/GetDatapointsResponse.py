from typing import *

from pydantic import BaseModel, Field

from .Datapoint import Datapoint


class GetDatapointsResponse(BaseModel):
    """
    GetDatapointsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoints: List[Datapoint] = Field(validation_alias="datapoints")
