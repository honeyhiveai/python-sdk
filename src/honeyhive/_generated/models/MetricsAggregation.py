from typing import *

from pydantic import BaseModel, Field

from .MetricDetail import MetricDetail


class MetricsAggregation(BaseModel):
    """
    MetricsAggregation model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    aggregation_function: Optional[str] = Field(validation_alias="aggregation_function", default=None)

    details: Optional[List[Optional[MetricDetail]]] = Field(validation_alias="details", default=None)
