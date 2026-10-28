from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQuery import ChartQuery
from .ChartQueryDateRange import ChartQueryDateRange
from .ChartQueryProductFilters import ChartQueryProductFilters
from .EventSearchFilter import EventSearchFilter

__all__ = ["ChartQueryRequest"]


class ChartQueryRequest(BaseModel):
    """
    ChartQueryRequest model
        Request body for POST /v1/charts/query
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    date_range: ChartQueryDateRange = Field(validation_alias="date_range")

    filters: Optional[List[Optional[EventSearchFilter]]] = Field(
        validation_alias="filters", default=None
    )

    product_filters: Optional[ChartQueryProductFilters] = Field(
        validation_alias="product_filters", default=None
    )

    query: ChartQuery = Field(validation_alias="query")
