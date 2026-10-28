from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryDateRange import ChartQueryDateRange
from .ChartResultScalarDataComparisonSparkline import (
    ChartResultScalarDataComparisonSparkline,
)

__all__ = ["ChartResultScalarDataComparison"]


class ChartResultScalarDataComparison(BaseModel):
    """
    ChartResultScalarDataComparison model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    value: Union[float, None] = Field(validation_alias="value")

    date_range: ChartQueryDateRange = Field(validation_alias="date_range")

    sparkline: Optional[ChartResultScalarDataComparisonSparkline] = Field(
        validation_alias="sparkline", default=None
    )
