from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ExperimentRunObject import ExperimentRunObject
from .Pagination import Pagination

__all__ = ["GetExperimentRunsResponse"]


class GetExperimentRunsResponse(BaseModel):
    """
    GetExperimentRunsResponse model
        Response for GET /runs
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    evaluations: List[ExperimentRunObject] = Field(validation_alias="evaluations")

    pagination: Pagination = Field(validation_alias="pagination")

    metrics: List[str] = Field(validation_alias="metrics")
