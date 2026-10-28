from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultScalarDataComparisonSparkline"]


class ChartResultScalarDataComparisonSparkline(BaseModel):
    """
    ChartResultScalarDataComparisonSparkline model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    interval: str = Field(validation_alias="interval")

    buckets: List[str] = Field(validation_alias="buckets")

    values: List[Union[float, None]] = Field(validation_alias="values")
