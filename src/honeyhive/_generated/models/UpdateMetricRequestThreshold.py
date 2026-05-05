from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateMetricRequestThreshold"]


class UpdateMetricRequestThreshold(BaseModel):
    """
    UpdateMetricRequestThreshold model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    min: Optional[float] = Field(validation_alias="min", default=None)

    max: Optional[float] = Field(validation_alias="max", default=None)

    pass_when: Optional[Union[bool, float]] = Field(
        validation_alias="pass_when", default=None
    )

    passing_categories: Optional[List[str]] = Field(
        validation_alias="passing_categories", default=None
    )
