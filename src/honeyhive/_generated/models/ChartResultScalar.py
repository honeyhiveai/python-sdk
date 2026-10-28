from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultMeasure import ChartResultMeasure
from .ChartResultScalarData import ChartResultScalarData
from .ChartResultScalarMeta import ChartResultScalarMeta

__all__ = ["ChartResultScalar"]


class ChartResultScalar(BaseModel):
    """
    ChartResultScalar model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultScalarMeta = Field(validation_alias="meta")

    measures: List[ChartResultMeasure] = Field(validation_alias="measures")

    data: ChartResultScalarData = Field(validation_alias="data")
