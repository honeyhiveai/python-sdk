from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .Datapoint import Datapoint

__all__ = ["GetDatapointsResponse"]


class GetDatapointsResponse(BaseModel):
    """
    GetDatapointsResponse model
        Response for GET /datapoints
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoints: List[Datapoint] = Field(validation_alias="datapoints")
