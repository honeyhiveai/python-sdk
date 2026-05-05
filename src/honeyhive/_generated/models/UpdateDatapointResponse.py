from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .UpdateDatapointResponseResult import UpdateDatapointResponseResult

__all__ = ["UpdateDatapointResponse"]


class UpdateDatapointResponse(BaseModel):
    """
    UpdateDatapointResponse model
        Response for PUT /datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    updated: bool = Field(validation_alias="updated")

    result: UpdateDatapointResponseResult = Field(validation_alias="result")
