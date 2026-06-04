from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .FiltersArray import FiltersArray

__all__ = ["MetricVersionContentRequestFilters"]


class MetricVersionContentRequestFilters(BaseModel):
    """
    MetricVersionContentRequestFilters model
        ETL filter narrowing which events this metric applies to. Defaults to `{ filterArray: [] }` (no filtering).
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    filterArray: FiltersArray = Field(validation_alias="filterArray")
