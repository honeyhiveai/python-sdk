from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .Datapoint import Datapoint

__all__ = ["GetDatapointResponse"]


class GetDatapointResponse(BaseModel):
    """
    GetDatapointResponse model
        Response for GET /datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint: List[Datapoint] = Field(validation_alias="datapoint")
