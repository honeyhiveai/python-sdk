from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultHistogramData import ChartResultHistogramData
from .ChartResultHistogramMeta import ChartResultHistogramMeta

__all__ = ["ChartResultHistogram"]


class ChartResultHistogram(BaseModel):
    """
    ChartResultHistogram model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultHistogramMeta = Field(validation_alias="meta")

    unit: str = Field(validation_alias="unit")

    format: str = Field(validation_alias="format")

    data: ChartResultHistogramData = Field(validation_alias="data")
