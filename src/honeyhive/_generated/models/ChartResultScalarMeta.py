from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultWarning import ChartResultWarning

__all__ = ["ChartResultScalarMeta"]


class ChartResultScalarMeta(BaseModel):
    """
    ChartResultScalarMeta model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    matched_event_count: float = Field(validation_alias="matched_event_count")

    warnings: List[ChartResultWarning] = Field(validation_alias="warnings")
