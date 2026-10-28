from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultMeasure"]


class ChartResultMeasure(BaseModel):
    """
    ChartResultMeasure model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    label: str = Field(validation_alias="label")

    unit: str = Field(validation_alias="unit")

    format: str = Field(validation_alias="format")
