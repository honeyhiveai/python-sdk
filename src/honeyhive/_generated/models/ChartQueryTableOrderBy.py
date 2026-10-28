from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryTableOrderBy"]


class ChartQueryTableOrderBy(BaseModel):
    """
    ChartQueryTableOrderBy model
        Default: first measure, descending
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    field: str = Field(validation_alias="field")

    direction: Optional[str] = Field(validation_alias="direction", default=None)
