from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .CreateDatapointResponseResult import CreateDatapointResponseResult

__all__ = ["CreateDatapointResponse"]


class CreateDatapointResponse(BaseModel):
    """
    CreateDatapointResponse model
        Response for POST /datapoints
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inserted: bool = Field(validation_alias="inserted")

    result: CreateDatapointResponseResult = Field(validation_alias="result")
