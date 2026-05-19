from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetExperimentRunSummaryQuery"]


class GetExperimentRunSummaryQuery(BaseModel):
    """
    GetExperimentRunSummaryQuery model
        Query parameters for GET /runs/{run_id}/summary
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    aggregate_function: Optional[str] = Field(
        validation_alias="aggregate_function", default=None
    )

    filters: Optional[Union[str, List[Any]]] = Field(
        validation_alias="filters", default=None
    )
