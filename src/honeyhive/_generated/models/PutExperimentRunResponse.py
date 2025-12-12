from typing import *

from pydantic import BaseModel, Field


class PutExperimentRunResponse(BaseModel):
    """
    PutExperimentRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[Any] = Field(validation_alias="evaluation", default=None)

    warning: Optional[str] = Field(validation_alias="warning", default=None)
