from typing import *

from pydantic import BaseModel, Field


class DatapointResult(BaseModel):
    """
    DatapointResult model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoint_id: Optional[str] = Field(validation_alias="datapoint_id", default=None)

    session_id: str = Field(validation_alias="session_id")

    passed: bool = Field(validation_alias="passed")

    metrics: Optional[List[Any]] = Field(validation_alias="metrics", default=None)
