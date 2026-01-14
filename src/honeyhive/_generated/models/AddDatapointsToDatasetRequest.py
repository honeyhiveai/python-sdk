from typing import *

from pydantic import BaseModel, Field


class AddDatapointsToDatasetRequest(BaseModel):
    """
    AddDatapointsToDatasetRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    data: List[Dict[str, Any]] = Field(validation_alias="data")

    mapping: Dict[str, Any] = Field(validation_alias="mapping")
