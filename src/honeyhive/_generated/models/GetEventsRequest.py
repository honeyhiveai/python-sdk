from typing import *

from pydantic import BaseModel, Field

from .EventFilter import EventFilter


class GetEventsRequest(BaseModel):
    """
    GetEventsRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    filters: List[EventFilter] = Field(validation_alias="filters")

    dateRange: Optional[Dict[str, Any]] = Field(
        validation_alias="dateRange", default=None
    )

    projections: Optional[List[str]] = Field(
        validation_alias="projections", default=None
    )

    limit: Optional[float] = Field(validation_alias="limit", default=None)

    page: Optional[float] = Field(validation_alias="page", default=None)
