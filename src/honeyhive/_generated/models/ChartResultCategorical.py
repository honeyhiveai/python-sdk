from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultCategoricalData import ChartResultCategoricalData
from .ChartResultCategoricalMeta import ChartResultCategoricalMeta

__all__ = ["ChartResultCategorical"]


class ChartResultCategorical(BaseModel):
    """
    ChartResultCategorical model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultCategoricalMeta = Field(validation_alias="meta")

    unit: str = Field(validation_alias="unit")

    format: str = Field(validation_alias="format")

    data: ChartResultCategoricalData = Field(validation_alias="data")
