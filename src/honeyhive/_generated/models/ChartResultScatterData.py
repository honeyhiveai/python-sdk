from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultScatterDataPointsItem import ChartResultScatterDataPointsItem

__all__ = ["ChartResultScatterData"]


class ChartResultScatterData(BaseModel):
    """
    ChartResultScatterData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    points: List[ChartResultScatterDataPointsItem] = Field(validation_alias="points")
