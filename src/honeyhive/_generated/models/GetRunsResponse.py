from typing import *

from pydantic import BaseModel, Field

from .EvaluationRun import EvaluationRun


class GetRunsResponse(BaseModel):
    """
    GetRunsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluations: Optional[List[Optional[EvaluationRun]]] = Field(
        validation_alias="evaluations", default=None
    )
