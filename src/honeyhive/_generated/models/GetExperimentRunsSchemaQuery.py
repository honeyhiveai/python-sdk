from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunsSchemaQuery(BaseModel):
    """
    GetExperimentRunsSchemaQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[Union[str, Dict[str, Any]]] = Field(
        validation_alias="dateRange", default=None
    )

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
