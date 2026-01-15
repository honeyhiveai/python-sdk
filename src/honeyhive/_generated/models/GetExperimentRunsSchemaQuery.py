from typing import *

from pydantic import BaseModel, Field

from .AbsoluteDateRange import AbsoluteDateRange


class GetExperimentRunsSchemaQuery(BaseModel):
    """
    GetExperimentRunsSchemaQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[Union[str, AbsoluteDateRange]] = Field(validation_alias="dateRange", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
