from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EventSearchFiltersArray import EventSearchFiltersArray
from .SearchEventsRequestDateRange import SearchEventsRequestDateRange

__all__ = ["SearchEventsRequest"]


class SearchEventsRequest(BaseModel):
    """
    SearchEventsRequest model
        Request body for POST /v1/events/search
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    filters: Optional[EventSearchFiltersArray] = Field(
        validation_alias="filters", default=None
    )

    dateRange: Optional[SearchEventsRequestDateRange] = Field(
        validation_alias="dateRange", default=None
    )

    limit: Optional[int] = Field(validation_alias="limit", default=None)

    page: Optional[int] = Field(validation_alias="page", default=None)

    ignore_order: Optional[bool] = Field(validation_alias="ignore_order", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
