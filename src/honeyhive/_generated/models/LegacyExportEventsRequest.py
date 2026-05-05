from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .FiltersArray import FiltersArray
from .LegacyExportEventsRequestDateRange import LegacyExportEventsRequestDateRange

__all__ = ["LegacyExportEventsRequest"]


class LegacyExportEventsRequest(BaseModel):
    """
    LegacyExportEventsRequest model
        Request body for POST /v1/events/export
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    filters: Optional[FiltersArray] = Field(validation_alias="filters", default=None)

    dateRange: Optional[LegacyExportEventsRequestDateRange] = Field(
        validation_alias="dateRange", default=None
    )

    projections: Optional[List[str]] = Field(
        validation_alias="projections", default=None
    )

    limit: Optional[float] = Field(validation_alias="limit", default=None)

    page: Optional[float] = Field(validation_alias="page", default=None)

    ignore_order: Optional[bool] = Field(validation_alias="ignore_order", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
