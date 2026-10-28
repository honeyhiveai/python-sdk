from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultScatterDataPointsItem"]


class ChartResultScatterDataPointsItem(BaseModel):
    """
    ChartResultScatterDataPointsItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    key: str = Field(validation_alias="key")

    label: str = Field(validation_alias="label")

    dimensions: Dict[str, Any] = Field(validation_alias="dimensions")

    x: float = Field(validation_alias="x")

    y: float = Field(validation_alias="y")

    weight: float = Field(validation_alias="weight")
