from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultMeasure import ChartResultMeasure
from .ChartResultScatterData import ChartResultScatterData
from .ChartResultScatterMeta import ChartResultScatterMeta

__all__ = ["ChartResultScatter"]


class ChartResultScatter(BaseModel):
    """
    ChartResultScatter model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultScatterMeta = Field(validation_alias="meta")

    measures: List[ChartResultMeasure] = Field(validation_alias="measures")

    data: ChartResultScatterData = Field(validation_alias="data")
