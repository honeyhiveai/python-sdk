from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultSeries import ChartResultSeries

__all__ = ["ChartResultTimeSeriesData"]


class ChartResultTimeSeriesData(BaseModel):
    """
    ChartResultTimeSeriesData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    buckets: List[str] = Field(validation_alias="buckets")

    series: List[ChartResultSeries] = Field(validation_alias="series")
