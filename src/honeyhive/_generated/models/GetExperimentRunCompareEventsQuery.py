from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetExperimentRunCompareEventsQuery"]


class GetExperimentRunCompareEventsQuery(BaseModel):
    """
    GetExperimentRunCompareEventsQuery model
        Query parameters for GET /runs/{new_run_id}/compare/{old_run_id}/events
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    filter: Optional[Union[str, Dict[str, Any]]] = Field(
        validation_alias="filter", default=None
    )

    limit: Optional[int] = Field(validation_alias="limit", default=None)

    page: Optional[int] = Field(validation_alias="page", default=None)
