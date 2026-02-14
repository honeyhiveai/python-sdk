from typing import *

from pydantic import BaseModel, Field

from .EvaluationRun import EvaluationRun


class GetRunResponse(BaseModel):
    """
    GetRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[EvaluationRun] = Field(
        validation_alias="evaluation", default=None
    )
