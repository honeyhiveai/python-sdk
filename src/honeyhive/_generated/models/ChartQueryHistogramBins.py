from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryHistogramBins"]


class ChartQueryHistogramBins(BaseModel):
    """
    ChartQueryHistogramBins model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    mode: str = Field(validation_alias="mode")

    count: Optional[int] = Field(validation_alias="count", default=None)

    min: Optional[float] = Field(validation_alias="min", default=None)

    max: Optional[float] = Field(validation_alias="max", default=None)
