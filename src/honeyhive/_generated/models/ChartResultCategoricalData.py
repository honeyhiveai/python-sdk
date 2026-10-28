from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultCategory import ChartResultCategory
from .ChartResultSeries import ChartResultSeries

__all__ = ["ChartResultCategoricalData"]


class ChartResultCategoricalData(BaseModel):
    """
    ChartResultCategoricalData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    categories: List[ChartResultCategory] = Field(validation_alias="categories")

    series: List[ChartResultSeries] = Field(validation_alias="series")
