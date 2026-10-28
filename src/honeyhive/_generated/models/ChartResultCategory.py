from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultCategory"]


class ChartResultCategory(BaseModel):
    """
    ChartResultCategory model
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

    is_other: Optional[bool] = Field(validation_alias="is_other", default=None)
