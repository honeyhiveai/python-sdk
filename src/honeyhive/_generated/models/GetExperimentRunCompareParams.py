from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunCompareParams(BaseModel):
    """
    GetExperimentRunCompareParams model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    new_run_id: str = Field(validation_alias="new_run_id")

    old_run_id: str = Field(validation_alias="old_run_id")
