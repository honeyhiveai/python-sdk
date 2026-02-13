from typing import *

from pydantic import BaseModel, Field


class ExperimentResultResponse(BaseModel):
    """
    ExperimentResultResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    status: Optional[str] = Field(validation_alias="status", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)

    passed: Optional[List[str]] = Field(validation_alias="passed", default=None)

    failed: Optional[List[str]] = Field(validation_alias="failed", default=None)

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    datapoints: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="datapoints", default=None
    )
