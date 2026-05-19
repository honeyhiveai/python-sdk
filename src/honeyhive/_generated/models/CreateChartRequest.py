from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .AbsoluteDateRange import AbsoluteDateRange
from .QueryFilter import QueryFilter
from .RelativeDateRange import RelativeDateRange

__all__ = ["CreateChartRequest"]


class CreateChartRequest(BaseModel):
    """
    CreateChartRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    metric: str = Field(validation_alias="metric")

    func: Optional[str] = Field(validation_alias="func", default=None)

    groupBy: Optional[str] = Field(validation_alias="groupBy", default=None)

    bucketing: Optional[str] = Field(validation_alias="bucketing", default=None)

    dateRange: Optional[Union[RelativeDateRange, AbsoluteDateRange]] = Field(
        validation_alias="dateRange", default=None
    )

    query: Optional[List[Optional[QueryFilter]]] = Field(
        validation_alias="query", default=None
    )

    owner_id: Optional[str] = Field(validation_alias="owner_id", default=None)
