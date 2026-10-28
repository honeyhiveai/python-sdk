from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultScalarDataComparison import ChartResultScalarDataComparison
from .ChartResultScalarDataSparkline import ChartResultScalarDataSparkline

__all__ = ["ChartResultScalarData"]


class ChartResultScalarData(BaseModel):
    """
    ChartResultScalarData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    value: Union[float, None] = Field(validation_alias="value")

    comparison: Optional[ChartResultScalarDataComparison] = Field(
        validation_alias="comparison", default=None
    )

    sparkline: Optional[ChartResultScalarDataSparkline] = Field(
        validation_alias="sparkline", default=None
    )
