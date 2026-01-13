from typing import *

from pydantic import BaseModel, Field


class GetEventsQuery(BaseModel):
    """
    GetEventsQuery model
        Query parameters for GET /events
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[Union[Dict[str, Any], Dict[str, Any]]] = Field(
        validation_alias="dateRange", default=None
    )

    filters: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="filters", default=None
    )

    projections: Optional[List[str]] = Field(
        validation_alias="projections", default=None
    )

    ignore_order: Optional[bool] = Field(validation_alias="ignore_order", default=None)

    limit: Optional[float] = Field(validation_alias="limit", default=None)

    page: Optional[float] = Field(validation_alias="page", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
