from typing import *

from pydantic import BaseModel, Field


class MetricComparison(BaseModel):
    """
    MetricComparison model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metric_name: str = Field(validation_alias="metric_name")

    metric_type: Optional[str] = Field(validation_alias="metric_type", default=None)

    old_aggregate: Optional[float] = Field(validation_alias="old_aggregate", default=None)

    new_aggregate: Optional[float] = Field(validation_alias="new_aggregate", default=None)

    difference: Optional[float] = Field(validation_alias="difference", default=None)

    percentage_change: Optional[float] = Field(validation_alias="percentage_change", default=None)
