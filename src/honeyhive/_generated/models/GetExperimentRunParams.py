from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunParams(BaseModel):
    """
    GetExperimentRunParams model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    run_id: str = Field(validation_alias="run_id")
