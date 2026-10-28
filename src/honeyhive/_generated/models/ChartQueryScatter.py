from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryMeasure import ChartQueryMeasure

__all__ = ["ChartQueryScatter"]


class ChartQueryScatter(BaseModel):
    """
    ChartQueryScatter model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    group_by: str = Field(validation_alias="group_by")

    x: ChartQueryMeasure = Field(validation_alias="x")

    y: ChartQueryMeasure = Field(validation_alias="y")

    limit: Optional[int] = Field(validation_alias="limit", default=None)
