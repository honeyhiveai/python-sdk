from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyUpdateMetricRequestCategoriesItem"]


class LegacyUpdateMetricRequestCategoriesItem(BaseModel):
    """
    LegacyUpdateMetricRequestCategoriesItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    category: str = Field(validation_alias="category")

    score: Optional[float] = Field(validation_alias="score")
