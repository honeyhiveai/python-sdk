from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunMetricsQuery(BaseModel):
    """
    GetExperimentRunMetricsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[str] = Field(validation_alias="dateRange", default=None)

    filters: Optional[Union[str, List[Any]]] = Field(
        validation_alias="filters", default=None
    )
