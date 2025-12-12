from typing import *

from pydantic import BaseModel, Field


class PostExperimentRunResponse(BaseModel):
    """
    PostExperimentRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[Any] = Field(validation_alias="evaluation", default=None)

    run_id: str = Field(validation_alias="run_id")
