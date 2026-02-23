from typing import *

from pydantic import BaseModel, Field

from .EvaluationRun import EvaluationRun


class PostExperimentRunResponse(BaseModel):
    """
    PostExperimentRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[EvaluationRun] = Field(
        validation_alias="evaluation", default=None
    )

    run_id: Optional[str] = Field(validation_alias="run_id", default=None)
