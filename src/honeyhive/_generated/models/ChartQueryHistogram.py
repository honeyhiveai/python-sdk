from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryHistogramBins import ChartQueryHistogramBins

__all__ = ["ChartQueryHistogram"]


class ChartQueryHistogram(BaseModel):
    """
    ChartQueryHistogram model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    metric: str = Field(validation_alias="metric")

    bins: Optional[ChartQueryHistogramBins] = Field(
        validation_alias="bins", default=None
    )

    markers: Optional[List[str]] = Field(validation_alias="markers", default=None)
