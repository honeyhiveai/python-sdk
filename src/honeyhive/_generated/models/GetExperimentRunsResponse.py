from typing import *

from pydantic import BaseModel, Field

from .Pagination import Pagination


class GetExperimentRunsResponse(BaseModel):
    """
    GetExperimentRunsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluations: List[Any] = Field(validation_alias="evaluations")

    pagination: Pagination = Field(validation_alias="pagination")

    metrics: List[str] = Field(validation_alias="metrics")
