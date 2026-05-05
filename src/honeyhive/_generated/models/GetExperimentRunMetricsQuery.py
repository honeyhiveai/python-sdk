from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetExperimentRunMetricsQuery"]


class GetExperimentRunMetricsQuery(BaseModel):
    """
    GetExperimentRunMetricsQuery model
        Query parameters for GET /runs/{run_id}/metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dateRange: Optional[str] = Field(validation_alias="dateRange", default=None)

    filters: Optional[Union[str, List[Any]]] = Field(
        validation_alias="filters", default=None
    )
