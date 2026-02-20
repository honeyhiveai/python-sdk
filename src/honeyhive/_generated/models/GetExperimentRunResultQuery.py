from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunResultQuery(BaseModel):
    """
    GetExperimentRunResultQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    aggregate_function: Optional[str] = Field(
        validation_alias="aggregate_function", default=None
    )

    filters: Optional[Union[str, List[Any]]] = Field(
        validation_alias="filters", default=None
    )
