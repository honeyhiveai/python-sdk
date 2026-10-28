from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultHistogramDataBinsItem import ChartResultHistogramDataBinsItem

__all__ = ["ChartResultHistogramData"]


class ChartResultHistogramData(BaseModel):
    """
    ChartResultHistogramData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    bins: List[ChartResultHistogramDataBinsItem] = Field(validation_alias="bins")

    markers: Dict[str, Any] = Field(validation_alias="markers")
