from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultHistogramDataBinsItem"]


class ChartResultHistogramDataBinsItem(BaseModel):
    """
    ChartResultHistogramDataBinsItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    start: float = Field(validation_alias="start")

    end: Union[float, None] = Field(validation_alias="end")

    count: float = Field(validation_alias="count")
