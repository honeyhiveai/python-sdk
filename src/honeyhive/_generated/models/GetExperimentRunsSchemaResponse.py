from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunsSchemaResponse(BaseModel):
    """
    GetExperimentRunsSchemaResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    fields: List[Dict[str, Any]] = Field(validation_alias="fields")

    datasets: List[str] = Field(validation_alias="datasets")

    mappings: Dict[str, Any] = Field(validation_alias="mappings")
