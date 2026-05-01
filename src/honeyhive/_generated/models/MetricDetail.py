from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricDatapoints import MetricDatapoints
from .PassingRange import PassingRange

__all__ = ["MetricDetail"]


class MetricDetail(BaseModel):
    """
    MetricDetail model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_name: str = Field(validation_alias="metric_name")

    metric_type: Optional[str] = Field(validation_alias="metric_type", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    aggregate: Optional[float] = Field(validation_alias="aggregate", default=None)

    values: Optional[List[float]] = Field(validation_alias="values", default=None)

    passing_range: Optional[PassingRange] = Field(
        validation_alias="passing_range", default=None
    )

    datapoints: Optional[MetricDatapoints] = Field(
        validation_alias="datapoints", default=None
    )
