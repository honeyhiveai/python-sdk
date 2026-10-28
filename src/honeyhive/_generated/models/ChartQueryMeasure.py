from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryAggregation import ChartQueryAggregation

__all__ = ["ChartQueryMeasure"]


class ChartQueryMeasure(BaseModel):
    """
    ChartQueryMeasure model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: Optional[str] = Field(validation_alias="id", default=None)

    metric: str = Field(validation_alias="metric")

    aggregation: Optional[ChartQueryAggregation] = Field(
        validation_alias="aggregation", default=None
    )
