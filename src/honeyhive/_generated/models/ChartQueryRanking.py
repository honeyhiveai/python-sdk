from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryRanking"]


class ChartQueryRanking(BaseModel):
    """
    ChartQueryRanking model
        Caps the split_by dimension
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    limit: Optional[int] = Field(validation_alias="limit", default=None)

    direction: Optional[str] = Field(validation_alias="direction", default=None)

    include_other: Optional[bool] = Field(
        validation_alias="include_other", default=None
    )
