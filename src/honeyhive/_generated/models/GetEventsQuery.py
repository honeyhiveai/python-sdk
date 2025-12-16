from typing import *

from pydantic import BaseModel, Field


class GetEventsQuery(BaseModel):
    """
    GetEventsQuery model
        Query parameters for GET /events
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[Union[Dict[str, Any], str]] = Field(
        validation_alias="dateRange", default=None
    )

    filters: Optional[Union[List[Dict[str, Any]], str, List[str]]] = Field(
        validation_alias="filters", default=None
    )

    projections: Optional[Union[List[str], str]] = Field(
        validation_alias="projections", default=None
    )

    ignore_order: Optional[Union[bool, str]] = Field(
        validation_alias="ignore_order", default=None
    )

    limit: Optional[Union[float, str]] = Field(validation_alias="limit", default=None)

    page: Optional[Union[float, str]] = Field(validation_alias="page", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
