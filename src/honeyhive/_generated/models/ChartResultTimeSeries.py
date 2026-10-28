from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultMeasure import ChartResultMeasure
from .ChartResultTimeSeriesData import ChartResultTimeSeriesData
from .ChartResultTimeSeriesMeta import ChartResultTimeSeriesMeta

__all__ = ["ChartResultTimeSeries"]


class ChartResultTimeSeries(BaseModel):
    """
    ChartResultTimeSeries model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultTimeSeriesMeta = Field(validation_alias="meta")

    measures: List[ChartResultMeasure] = Field(validation_alias="measures")

    data: ChartResultTimeSeriesData = Field(validation_alias="data")
