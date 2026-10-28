from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultWarning import ChartResultWarning

__all__ = ["ChartResultCategoricalMeta"]


class ChartResultCategoricalMeta(BaseModel):
    """
    ChartResultCategoricalMeta model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    warnings: List[ChartResultWarning] = Field(validation_alias="warnings")
