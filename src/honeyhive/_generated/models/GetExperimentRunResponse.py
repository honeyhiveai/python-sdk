from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunResponse(BaseModel):
    """
    GetExperimentRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[Any] = Field(validation_alias="evaluation", default=None)
