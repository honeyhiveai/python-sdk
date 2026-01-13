from typing import *

from pydantic import BaseModel, Field


class GetEventsLegacyRequest(BaseModel):
    """
    GetEventsLegacyRequest model
        Request body for GET /events legacy endpoint
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    filters: List[Dict[str, Any]] = Field(validation_alias="filters")

    dateRange: Optional[Dict[str, Any]] = Field(
        validation_alias="dateRange", default=None
    )

    projections: Optional[List[str]] = Field(
        validation_alias="projections", default=None
    )

    limit: Optional[float] = Field(validation_alias="limit", default=None)

    page: Optional[float] = Field(validation_alias="page", default=None)
