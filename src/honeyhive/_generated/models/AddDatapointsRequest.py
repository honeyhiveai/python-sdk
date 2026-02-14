from typing import *

from pydantic import BaseModel, Field


class AddDatapointsRequest(BaseModel):
    """
    AddDatapointsRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    data: List[Dict[str, Any]] = Field(validation_alias="data")

    mapping: Dict[str, Any] = Field(validation_alias="mapping")
